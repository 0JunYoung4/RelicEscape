"""Interactive B1 rehearsal with a repeating claw and jump attack loop."""

from bisect import bisect_right
from itertools import accumulate
from math import sin
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from pico2d import pico2d as pico

from health import Health
from player import Animation, WORLD_MARGIN
from tools.b1_combat_tree import Attack, B1CombatTree, Status
from tools.b1_combat_terrain import GATE_LEFT, LEDGES
from tools.b1_roar_game_stage import B1RoarStage
from tools.b1_room_art import ROOM_SIZE, WORLD_PER_ART_PIXEL, _draw_plate, _green_grade, rgba_texture
from tools.preview_b1_intro import (APPROACH_LIMIT, ART, GROUND, INTERACT_DISTANCE, LAST_TREMOR,
                                   SHELL_X, SIZE, Preview, camera_box, ceiling_particles,
                                   clamp, dust_tile, lerp, smoothstep)
from tools.render_b1_roar_preview import rgba


SCALE = WORLD_PER_ART_PIXEL
SPAWN = (2235 * SCALE, 0, 0)
ROCK_RELEASE, ROCK_IMPACT = 2.15, 2.70
GATE_DURATION = .44
CLAW_HOLD = .64
CLAW_RECOVERY = .85
CLAW_OFFSET = 260 * SCALE
CLAW_HALF_WIDTH = 54 * SCALE
CLAW_HEIGHT = 116 * SCALE
CLAW_DAMAGE = 25
APPROACH_SPEED = 840
APPROACH_MAX_TIME = .75
JUMP_WAIT, JUMP_TELL, JUMP_RECOVERY = 1.4, .80, 1.10
JUMP_HALF_WIDTH = 120 * SCALE
JUMP_HEIGHT = 80 * SCALE
JUMP_WALL_MARGIN = 60 * SCALE
JUMP_DAMAGE = 25
COMBAT_WIDTH = 1264


class _Pose:
    def __init__(self, image, anchor, scale=SCALE):
        left, top, right, bottom = image.getbbox()
        self.image = rgba_texture(image.crop((left, top, right, bottom)))
        self.dx = ((left + right) / 2 - anchor[0]) * scale
        self.dy = (anchor[1] - (top + bottom) / 2) * scale
        self.scale = scale

    def draw(self, camera, x, y=0, facing=1):
        center = camera.world_to_screen(x + facing * self.dx, y + self.dy)
        scale = self.scale * camera.zoom
        self.image.composite_draw(0, "h" if facing < 0 else "", *center,
                                  self.image.w * scale, self.image.h * scale)


class _Motion:
    def __init__(self, filename, anchor, hold_frame, hold_time):
        frames, durations = [], []
        with Image.open(ART.parent / filename) as source:
            for index in range(source.n_frames):
                source.seek(index)
                frame = source.convert("RGBA")
                frames.append(_Pose(frame, anchor) if frame.getbbox() else None)
                durations.append(source.info["duration"] / 1000)
        durations[hold_frame] = hold_time
        self.frames = frames
        self.ends = tuple(accumulate(durations))

    def draw(self, camera, x, facing, elapsed):
        index = min(bisect_right(self.ends, elapsed), len(self.frames) - 1)
        frame = self.frames[index]
        if frame is not None:
            frame.draw(camera, x, facing=facing)


class _Claw(_Motion):
    def __init__(self):
        # Frame 22 holds the raised claw; frame 31 is the first contact.
        super().__init__("claw-approach-slam-animation-v2.webp", (310, 505), 22, CLAW_HOLD)
        self.tell = self.ends[21]
        self.impact = self.ends[30]


class _Jump(_Motion):
    def __init__(self):
        # Hold the authored empty frame for the wait plus the ground warning.
        super().__init__("boss-jump-animation-v4.webp", (296, 504), 47, JUMP_WAIT + JUMP_TELL)
        self.offscreen = self.ends[46]
        self.tell = self.offscreen + JUMP_WAIT
        self.drop = self.ends[47]
        self.impact = self.ends[70]


def _scuttle():
    frames = [{
        "x": (index % 8) * 616, "y": (index // 8) * 410,
        "width": 616, "height": 410,
    } for index in range(32)]
    return Animation(ART.parent / "boss-scuttle-poses-v1.png", frames, (308, 382), SCALE, 50)


def _label(font, text):
    left, top, right, bottom = font.getbbox(text)
    height = bottom - top
    image = Image.new("RGBA", (right - left + 24, height + 14))
    pen = ImageDraw.Draw(image)
    pen.rounded_rectangle((0, 0, image.width - 1, image.height - 1), 7,
                          fill=(12, 25, 28, 236), outline=(118, 114, 82, 235))
    pen.text((12 - left, 7 - top), text, font=font, fill=(245, 229, 186, 255))
    return rgba_texture(image)


def _labels():
    malgun = Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts" / "malgun.ttf"
    if malgun.is_file():
        font = ImageFont.truetype(str(malgun), 16)
        words = ("E  조사", "A/D 이동 · Shift 달리기 · Space 점프 · R 다시",
                 "쓰러졌습니다 · R 재도전")
    else:
        font = ImageFont.load_default(size=16)
        words = ("E  Inspect", "A/D Move | Shift Run | Space Jump | R Reset",
                 "Defeated | R Retry")
    return tuple(_label(font, word) for word in words)


def _attack_marker(half_width, height):
    image = Image.new("RGBA", (2 * half_width // SCALE, height))
    pen = ImageDraw.Draw(image)
    bounds = (0, 0, image.width - 1, image.height - 1)
    pen.ellipse(bounds, fill=(121, 63, 38, 158), outline=(217, 151, 85, 239), width=2)
    pen.line((image.width // 2 - 8, height // 2, image.width // 2 + 8, height // 2),
             fill=(239, 169, 100, 218), width=2)
    return rgba_texture(image)


def _approach_view(preview):
    left, top, right, bottom = camera_box(preview)
    near_shell = smoothstep((SHELL_X + INTERACT_DISTANCE + 180 - preview.x) / 180)
    before_widening = 1 - smoothstep((preview.elapsed or 0) / .60)
    offset = min(0, SHELL_X - 268 - (preview.x - 411)) * near_shell * before_widening
    return left + offset, top, right + offset, bottom


class B1EncounterStage(B1RoarStage):
    def __init__(self):
        super().__init__(gate_closed=False)
        self.gate = rgba_texture(_green_grade(rgba(ART / "right-passage-gate.png"),
                                              (7, 17, 21), (150, 169, 151), .25))
        self.ledges = tuple((x * SCALE, (GROUND - bottom) * SCALE, (x + width) * SCALE,
                             (GROUND - top) * SCALE) for _, x, top, width, bottom in LEDGES)
        shell = rgba(ART.parent / "assembled-retracted-v6.png")
        self.shell = _Pose(shell, (shell.width / 2, shell.getbbox()[3]), .55 * SCALE)
        rock = rgba(ART.parent / "ceiling-rock-v2/debris-v1/shard-large-01.png")
        self.rock = rgba_texture(rock.crop(rock.getbbox()))
        self.dust = rgba_texture(dust_tile(17))
        self.particles = ceiling_particles()
        self.claw = _Claw()
        self.jump = _Jump()
        self.scuttle = _scuttle()
        self.claw_marker = _attack_marker(CLAW_HALF_WIDTH, 19)
        self.jump_marker = _attack_marker(JUMP_HALF_WIDTH, 27)
        self.labels = _labels()
        self.combat = B1CombatTree()
        self.reset()

    def reset(self):
        self.state = "waiting"
        self.age = self.time = 0.0
        self.boss_x = SHELL_X * SCALE
        self.boss_facing = 1
        self.gate_progress = 0.0
        self.player.world_left = APPROACH_LIMIT * SCALE - WORLD_MARGIN
        self.player.terrain = self.ledges
        self.player.recover_at(*SPAWN)
        self.player.facing = -1
        self.health = Health(SPAWN)
        self.intro_camera = None
        self.combat_left = 0.0
        self.hit_landed = None
        self.jump_target = None
        self.combat.reset()

    @property
    def can_inspect(self):
        return (self.state == "waiting" and self.player.grounded and self.player.y == 0
                and APPROACH_LIMIT * SCALE <= self.player.x <= (SHELL_X + INTERACT_DISTANCE) * SCALE)

    @property
    def claw_center(self):
        return self.boss_x + CLAW_OFFSET * self.boss_facing

    @property
    def player_in_claw_range(self):
        return (abs(self.player.x - self.boss_x) <= CLAW_OFFSET + CLAW_HALF_WIDTH
                and self.player.y < CLAW_HEIGHT)

    @property
    def airborne(self):
        return self.state == "jump" and self.jump.offscreen <= self.age < self.jump.impact

    def _enter(self, state):
        self.state = state
        self.age = 0.0

    def advance(self, dt, direction=0, *, running=False, crouching=False, jump_pressed=False,
                jump_held=False, inspect_pressed=False, attack_pressed=False):
        self.time += dt
        if inspect_pressed and self.can_inspect:
            self.player.recover_at(self.player.x, 0, 0)
            self.intro_camera = Preview(x=self.player.x / SCALE, elapsed=0.0)
            self._enter("tremor")
            return
        if self.state not in ("tremor", "roar") and self.health.current > 0:
            self.player.update(direction, running, dt, jump_pressed, crouching,
                               attack_pressed=attack_pressed, jump_held=jump_held)
        if self.state == "tremor":
            self.age += dt
            self.gate_progress = clamp((self.age - ROCK_IMPACT) / GATE_DURATION, 0, 1)
            if self.age >= LAST_TREMOR:
                self.intro_camera.elapsed = LAST_TREMOR
                self.combat_left = camera_box(self.intro_camera)[0]
                self._enter("roar")
        elif self.state == "roar":
            self.age += dt
            if self.age * 1000 >= self.duration_ms:
                self.player.recover_at(self.player.x, 0, 0)
                self.player.world_left = 0
                # The closed gate fills the opening, with solid rock above it.
                gate_wall = (GATE_LEFT * SCALE, 0, (GATE_LEFT + self.gate.w) * SCALE, GROUND * SCALE)
                self.player.terrain = (*self.ledges, gate_wall)
                self._enter("ready")
                self.combat.tick(self, 0)
            else:
                self._brace_player(self.age * 1000)
        elif self.state != "waiting":
            self.combat.tick(self, dt)
            self._track_combat(dt)

    def start_attack(self, attack):
        self.hit_landed = None
        self.jump_target = None
        self.boss_facing = 1 if self.player.x >= self.boss_x else -1
        self._enter("approach" if attack is Attack.CLAW else "jump")

    def advance_attack(self, dt):
        before = self.age
        self.age += dt
        if self.state == "approach":
            distance = self.player.x - self.boss_x
            self.boss_facing = 1 if distance >= 0 else -1
            closing = max(0, abs(distance) - CLAW_OFFSET)
            self.boss_x += self.boss_facing * min(closing, APPROACH_SPEED * dt)
            if closing <= APPROACH_SPEED * dt or self.age >= APPROACH_MAX_TIME:
                self._enter("claw")
        elif self.state == "claw":
            if before < self.claw.impact <= self.age:
                self._strike(self.claw_center - CLAW_HALF_WIDTH, self.claw_center + CLAW_HALF_WIDTH,
                             CLAW_HEIGHT, CLAW_DAMAGE)
            if self.age >= self.claw.impact + CLAW_RECOVERY:
                self._enter("ready")
                return Status.SUCCESS
        elif self.state == "jump":
            if before < self.jump.tell <= self.age:
                self.jump_target = clamp(self.player.x, JUMP_WALL_MARGIN, GATE_LEFT * SCALE - JUMP_WALL_MARGIN)
            if self.age >= self.jump.drop:
                self.boss_x = self.jump_target
            if before < self.jump.impact <= self.age:
                self._strike(*self._jump_bounds(), JUMP_HEIGHT, JUMP_DAMAGE)
            if self.age >= self.jump.impact + JUMP_RECOVERY:
                self._enter("ready")
                return Status.SUCCESS
        return Status.RUNNING

    def end_combat(self):
        if self.state != "defeated":
            self._enter("defeated")

    def _track_combat(self, dt):
        player_x = self.player.x / SCALE
        if self.airborne:
            focus = player_x if self.jump_target is None else (self.player.x + self.jump_target) / (2 * SCALE)
        else:
            focus = (self.player.x + self.boss_x) / (2 * SCALE)
        left = lerp(self.combat_left, focus - 615, min(1, 3 * dt))
        self.combat_left = clamp(left, player_x - COMBAT_WIDTH + 120, player_x - 120)

    def _jump_bounds(self):
        return (max(0, self.jump_target - JUMP_HALF_WIDTH),
                min(GATE_LEFT * SCALE, self.jump_target + JUMP_HALF_WIDTH))

    def _strike(self, strike_left, strike_right, height, damage):
        left, bottom, right, top = self.player.get_hitbox()
        self.hit_landed = False
        if left < strike_right and right > strike_left and bottom < height and top > 0:
            self.hit_landed = self.health.take_enemy_hit((self.player.x, (bottom + top) / 2),
                                                        self.time, damage)

    def _view(self):
        if self.state == "waiting":
            return _approach_view(Preview(x=self.player.x / SCALE))
        if self.state == "tremor":
            self.intro_camera.elapsed = self.age
            return _approach_view(self.intro_camera)
        if self.state == "roar":
            return camera_box(self.intro_camera)
        width, top = COMBAT_WIDTH, 35
        if self.state in ("claw", "jump"):
            impact = self.claw.impact if self.state == "claw" else self.jump.impact
            since_impact = self.age - impact
            if 0 <= since_impact < .20:
                strength = 4 if self.state == "claw" else 8
                top += strength * sin(since_impact * 110) * (1 - since_impact / .20)
        left = clamp(self.combat_left, 0, ROOM_SIZE[0] - width)
        return left, top, left + width, top + width * SIZE[1] / SIZE[0]

    def _draw_gate(self):
        height = round(self.gate.h * smoothstep(self.gate_progress))
        if height == 0:
            return
        top = GROUND - self.gate.h
        x = (GATE_LEFT + self.gate.w / 2) * SCALE
        y = (GROUND - top - height / 2) * SCALE
        scale = self.camera.zoom * SCALE
        self.gate.clip_draw(0, 0, self.gate.w, height, *self.camera.world_to_screen(x, y),
                            self.gate.w * scale, height * scale)

    def _draw_tremor(self):
        for particle in self.particles:
            age = self.age - particle.birth
            if not 0 <= age < particle.lifetime:
                continue
            x = particle.x + particle.drift * age
            gravity = 480 if particle.is_stone else 212
            y = particle.y + (particle.speed + (0 if particle.is_stone else 44)) * age + gravity * age * age / 2
            if y >= GROUND:
                continue
            image = self.rock if particle.is_stone else self.dust
            radius = particle.radius + (0 if particle.is_stone else age * 7)
            strength = (1 - age / particle.lifetime) ** .65
            pico.SDL_SetTextureAlphaMod(image.texture, round(255 * strength))
            _draw_plate(self.camera, image, x - radius, y - radius, size=(2 * radius, 2 * radius))
        for image in (self.rock, self.dust):
            pico.SDL_SetTextureAlphaMod(image.texture, 255)
        if ROCK_RELEASE <= self.age < ROCK_IMPACT:
            fall = (self.age - ROCK_RELEASE) / (ROCK_IMPACT - ROCK_RELEASE)
            x = lerp(SHELL_X - 124, SHELL_X, fall)
            y = lerp(87, 535, fall ** 2)
            _draw_plate(self.camera, self.rock, x - 35, y - 31, size=(70, 62))
        elif ROCK_IMPACT <= self.age < ROCK_IMPACT + .26:
            self._draw_dust(SHELL_X, 483, self.age - ROCK_IMPACT)

    def _draw_dust(self, center, top, age):
        pico.SDL_SetTextureAlphaMod(self.dust.texture, round(255 * (1 - age / .26)))
        for sign in (-1, 1):
            x = center + sign * (10 + age * 165)
            _draw_plate(self.camera, self.dust, x - 30, top, size=(60 + 90 * age, 28))
        pico.SDL_SetTextureAlphaMod(self.dust.texture, 255)
        for sign, speed, rise, size in ((-1, 190, 104, 7), (-1, 80, 140, 5),
                                       (1, 120, 121, 8), (1, 225, 81, 6)):
            x = center + sign * (8 + age * speed)
            y = top + 24 - rise * age + 225 * age ** 2
            _draw_plate(self.camera, self.rock, x, y, size=(size, size))

    def draw(self):
        self._set_camera(0, self._view())
        self._draw_room(self.time * 1000, airborne=self.airborne)
        self._draw_gate()
        if self.state == "waiting":
            self.shell.draw(self.camera, self.boss_x)
        elif self.state == "tremor":
            if self.age < ROCK_IMPACT:
                self.shell.draw(self.camera, self.boss_x)
            else:
                self.boss.draw(self.boss_x, 0, 1, 0, self.camera)
            self._draw_tremor()
        elif self.state == "roar":
            self._draw_roar(self.age * 1000)
        elif self.state == "approach":
            # Both directions have their own frames in the scuttle atlas.
            index = int(self.age * 50) % 16 + (16 if self.boss_facing < 0 else 0)
            self.scuttle.draw(self.boss_x, 0, 1, 0, self.camera, frame_index=index)
        elif self.state == "claw":
            self._draw_claw()
        elif self.state == "jump":
            self._draw_jump()
        else:
            self.claw.draw(self.camera, self.boss_x, self.boss_facing, self.claw.ends[-1])
        self.player.draw(self.camera, tint=self.health.hit_tint(self.time))
        self.health.draw_hit(self.camera, self.time)
        self.room_art.draw_in_front(self.camera)
        self.health.draw_hud(SIZE[1], self.time)
        self._draw_ui()

    def _draw_claw(self):
        center = self.claw_center / SCALE
        if self.claw.tell <= self.age < self.claw.impact:
            _draw_plate(self.camera, self.claw_marker, center - self.claw_marker.w / 2, GROUND - 9)
        self.claw.draw(self.camera, self.boss_x, self.boss_facing, self.age)
        since_impact = self.age - self.claw.impact
        if 0 <= since_impact < .26:
            self._draw_dust(center, GROUND - 31, since_impact)

    def _draw_jump(self):
        if self.jump.tell <= self.age < self.jump.impact:
            left, right = self._jump_bounds()
            width = (right - left) / SCALE
            _draw_plate(self.camera, self.jump_marker, left / SCALE, GROUND - 13, size=(width, 27))
            age = self.age - self.jump.tell
            for fraction, delay, size in ((.28, .10, 9), (.55, .27, 7), (.74, .42, 12)):
                flight = (age - delay) / .34
                if 0 <= flight < 1:
                    x = left / SCALE + width * fraction
                    y = GROUND - size - 105 * (1 - flight ** 2)
                    _draw_plate(self.camera, self.rock, x, y, size=(size, size))
        self.jump.draw(self.camera, self.boss_x, self.boss_facing, self.age)
        since_impact = self.age - self.jump.impact
        if 0 <= since_impact < .26:
            self._draw_dust(self.boss_x / SCALE, GROUND - 32, since_impact)

    def _draw_ui(self):
        prompt, controls, retry = self.labels
        if self.state == "waiting":
            controls.draw(SIZE[0] / 2, 26)
            if self.can_inspect:
                x, y = self.camera.world_to_screen(self.player.x, self.player.get_hitbox()[3] + 42)
                prompt.draw(x, y)
        elif self.state == "defeated":
            retry.draw(SIZE[0] / 2, 26)

    def close(self):
        self.gate = self.shell = self.rock = self.dust = self.claw = self.jump = self.scuttle = None
        self.claw_marker = self.jump_marker = self.labels = None
        super().close()

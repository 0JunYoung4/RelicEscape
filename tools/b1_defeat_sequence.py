"""World-space defeat effects shared by the playable B1 encounter."""

from ctypes import byref
from math import atan2, cos, hypot, sin, tau

from PIL import Image
from pico2d import pico2d as pico

from player import ASSET_ROOT
from tools.b1_room_art import rgba_texture
from tools.render_b1_defeat_preview import (
    BEAMS, BEAM_END, BEAM_SWELL_END, BEAM_TRAVEL, BEAM_WIDTH_SCALE, BLUE_LIGHT,
    BURST, CLAW_FALL, FLOOR, HITSTOP, LIGHT_END, OUTPUT, REVEAL, ROOM_SPREAD_END, SHAKE_END, STILL,
    SWAP_POSE, WHITE_PEAK, WHITE_RELEASE, WHITE_START,
    glow, progress, shiver_offset,
)


DURATION = 4.0
HITSTOP_SECONDS = HITSTOP / 1000
PREVIEW_TO_WORLD = 2 * 1264 / 960
POSE_SCALE = (387 / 1459) * PREVIEW_TO_WORLD
ORB_SIZE = 171
ORB_CELL = 128
ORB_FRAME_MS = 75
ORB_HALO_SIZE = 330
ORB_HALO_ALPHA = .58
ORB_TRAIL_MS = 144
ORB_FLIGHT_EXPONENT = 1.85
ORB_START, ORB_RISE_START, ORB_GATHER_END = 2500, 2580, 2720
ORB_LAUNCH, ORB_EXIT, ORB_END = 3400, 3920, 3980
ORB_RISE_HEIGHT = 210
CORE_COLOR = (219, 247, 255)
ENERGY_COLOR = (89, 181, 242)
CRACK_X, CRACK_Y = (579 - 480) * PREVIEW_TO_WORLD, (FLOOR - 366) * PREVIEW_TO_WORLD


def _light_texture(color):
    image = Image.new("RGBA", (96, 96))
    glow(image, 48, 48, 47, color, 210)
    return rgba_texture(image)


def _sprite(path):
    with Image.open(path) as source:
        box = source.getchannel("A").point(lambda a: 255 if a > 8 else 0).getbbox()
        texture = rgba_texture(source.crop(box))
        offset = ((box[0] + box[2]) / 2 - source.width / 2) * POSE_SCALE
    return texture, offset


class B1DefeatSequence:
    def __init__(self):
        self.before = _sprite(OUTPUT / "before-flash.png")
        self.after = _sprite(OUTPUT / "after-flash.png")
        self.ray = pico.load_image(str(OUTPUT / "defeat-beam-source.png"))
        self.orb = pico.load_image(str(OUTPUT.with_name("defeat-orb-v3") / "energy-orb-sheet.png"))
        self.halo = _light_texture(ENERGY_COLOR)
        self.burst = _light_texture(BLUE_LIGHT)
        self.spark = _light_texture(CORE_COLOR)
        self.dust = _light_texture((170, 186, 172))
        self.release_sound = (pico.load_wav(str(ASSET_ROOT / "audio/b1-energy-release-v1.wav"))
                              if pico.audio_on else None)

    def play_release(self):
        if self.release_sound is not None:
            self.release_sound.play()

    @staticmethod
    def shake(elapsed):
        t = elapsed * 1000
        if HITSTOP <= t < STILL:
            strength = 1.1 + 2.6 * progress(t, HITSTOP, STILL)
        elif BURST <= t < SHAKE_END:
            strength = 6 * (1 - progress(t, BURST, SHAKE_END))
        else:
            return 0, 0
        return sin(t * .083) * strength, sin(t * .061) * strength * .46

    def draw_boss(self, camera, boss_x, facing, elapsed=DURATION):
        t = elapsed * 1000
        texture, offset = self.before if t < SWAP_POSE else self.after
        shiver = shiver_offset(t) * PREVIEW_TO_WORLD
        if t < SWAP_POSE:
            drop = progress(t, HITSTOP, CLAW_FALL)
            stretch = 1.02 - .05 * drop
            lift = 4 * (1 - drop) * PREVIEW_TO_WORLD
        else:
            stretch = 1 - .025 * (1 - progress(t, SWAP_POSE, 2100))
            lift = 0
        height = texture.h * POSE_SCALE * stretch
        center = camera.world_to_screen(boss_x + facing * offset + shiver, height / 2 + lift)
        texture.composite_draw(0, "h" if facing < 0 else "", *center,
                               texture.w * POSE_SCALE * camera.zoom, height * camera.zoom)

    @staticmethod
    def _draw_light(texture, camera, x, y, size, alpha, *, aspect=1.0):
        texture.opacify(alpha)
        width = size * camera.zoom
        texture.draw(*camera.world_to_screen(x, y), width, width * aspect)
        texture.opacify(1)

    def draw_lighting(self, camera, boss_x, facing, elapsed):
        t = elapsed * 1000
        if BURST <= t < LIGHT_END:
            expand = progress(t, BURST, ROOM_SPREAD_END)
            fade = 1 - progress(t, SWAP_POSE, LIGHT_END)
            self._draw_light(self.burst, camera, boss_x, 252, 340 + 2350 * expand, .83 * fade)
            self._draw_light(self.burst, camera, boss_x, 22, 850 + 490 * expand,
                             .49 * fade, aspect=.21)
        if ORB_START < t < ORB_END:
            x, y, strength = self._orb_pose(camera, boss_x, facing, t)
            self._draw_light(self.halo, camera, x, y, ORB_HALO_SIZE, ORB_HALO_ALPHA * strength)
            spill = max(0, 1 - y / 700)
            self._draw_light(self.halo, camera, x, 15, ORB_HALO_SIZE * 1.35,
                             .38 * spill * strength, aspect=.20)

    def _draw_rays(self, camera, boss_x, facing, t):
        width, height = pico.get_canvas_width(), pico.get_canvas_height()
        swell = progress(t, BURST, BEAM_SWELL_END) ** 1.7
        remaining = 1 - progress(t, WHITE_PEAK, BEAM_END)
        screen_scale = PREVIEW_TO_WORLD * camera.zoom
        for start, (x, y), (end_x, end_y), half in BEAMS:
            reach = progress(t, start, start + BEAM_TRAVEL)
            if reach == 0:
                continue
            dx, dy = (end_x - x) * facing, y - end_y
            direction_length = hypot(dx, dy)
            ux, uy = dx / direction_length, dy / direction_length
            world_x = boss_x + (facing * (x - 480) + shiver_offset(t)) * PREVIEW_TO_WORLD
            sx, sy = camera.world_to_screen(world_x, (FLOOR - y) * PREVIEW_TO_WORLD)
            border = min(((width if ux > 0 else 0) - sx) / ux,
                         ((height if uy > 0 else 0) - sy) / uy)
            length = max(24, border + 60) * reach
            half_width = half * screen_scale * BEAM_WIDTH_SCALE * (.40 + .60 * reach) * (1 + 7 * swell)
            self.ray.opacify((.43 + .45 * reach + .12 * swell) * remaining)
            self.ray.composite_draw(atan2(uy, ux), "", sx + ux * length / 2, sy + uy * length / 2,
                                    length, 2 * half_width)
        self.ray.opacify(1)

    @staticmethod
    def _orb_pose(camera, boss_x, facing, t):
        origin_x = boss_x + facing * CRACK_X
        rise = progress(t, ORB_RISE_START, ORB_LAUNCH)
        lift = rise * rise * (3 - 2 * rise)
        flight = progress(t, ORB_LAUNCH, ORB_EXIT)
        distance = flight ** ORB_FLIGHT_EXPONENT
        end_x = camera.x + camera.view_width + ORB_SIZE
        return (origin_x + (end_x - origin_x) * distance, CRACK_Y + ORB_RISE_HEIGHT * lift,
                progress(t, ORB_START, ORB_GATHER_END))

    def _draw_orb(self, camera, boss_x, facing, t):
        x, y, strength = self._orb_pose(camera, boss_x, facing, t)
        if t < ORB_GATHER_END:
            radius = 102 * (1 - strength)
            for index in range(5):
                angle = tau * (index / 5 + .20 * strength)
                self._draw_light(self.spark, camera, x + radius * cos(angle),
                                 y + radius * sin(angle) * .72, 15,
                                 .70 * sin(strength * tau / 2))
        trail_fade = 1 - progress(t, ORB_EXIT, ORB_END)
        for delay in range(ORB_TRAIL_MS, 0, -24):
            sample = t - delay
            if sample <= ORB_LAUNCH:
                continue
            tail_x, tail_y, _ = self._orb_pose(camera, boss_x, facing, sample)
            remaining = 1 - delay / (ORB_TRAIL_MS + 24)
            speed = progress(sample, ORB_LAUNCH, ORB_EXIT) ** .85
            self._draw_light(self.halo, camera, tail_x, tail_y, 48 + 32 * remaining,
                             .58 * speed * remaining * trail_fade, aspect=.48)
            self._draw_light(self.spark, camera, tail_x, tail_y + 17 * sin(sample * .074),
                             7 + 12 * remaining, .64 * speed * remaining * trail_fade)
        current = int((t - ORB_START) / ORB_FRAME_MS) % 16
        row, col = divmod(current, 4)
        size = ORB_SIZE * camera.zoom * (.43 + .57 * strength)
        self.orb.opacify(strength)
        self.orb.clip_draw(col * ORB_CELL, (3 - row) * ORB_CELL, ORB_CELL, ORB_CELL,
                           *camera.world_to_screen(x, y), size, size)
        self.orb.opacify(1)

    def draw_energy(self, camera, boss_x, facing, elapsed):
        t = elapsed * 1000
        if BEAMS[0][0] < t < BEAM_END:
            self._draw_rays(camera, boss_x, facing, t)
        for start, life, spread in ((CLAW_FALL, .32, 205), (BURST, .64, 735)):
            age = (t - start) / 1000
            if 0 <= age < life:
                distance = age / life
                for side in (-1, 1):
                    self._draw_light(self.dust, camera, boss_x + side * (220 + spread * distance),
                                     13 + 34 * distance, 180 + 310 * distance,
                                     .70 * (1 - distance), aspect=.25)
        if ORB_START < t < ORB_END:
            self._draw_orb(camera, boss_x, facing, t)

    @staticmethod
    def draw_flash(elapsed):
        t = elapsed * 1000
        flash = progress(t, WHITE_START, WHITE_PEAK) * (1 - progress(t, WHITE_RELEASE, REVEAL))
        if flash:
            previous = pico.SDL_BlendMode()
            pico.SDL_GetRenderDrawBlendMode(pico.renderer, byref(previous))
            pico.SDL_SetRenderDrawBlendMode(pico.renderer, pico.SDL_BLENDMODE_BLEND)
            try:
                pico.SDL_SetRenderDrawColor(pico.renderer, 255, 255, 255, round(flash * 255))
                pico.SDL_RenderFillRect(pico.renderer, None)
            finally:
                pico.SDL_SetRenderDrawBlendMode(pico.renderer, previous)

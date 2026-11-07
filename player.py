"""Player movement, jumping, crouching, and the approved character artwork."""

import json
from bisect import bisect_right
from itertools import accumulate
from math import sqrt
from pathlib import Path

from pico2d import draw_rectangle, load_image

from slash_effect import SLASH_DURATION, draw_slash


ASSET_ROOT = Path(__file__).resolve().parent / "assets"
IDLE_FLOURISH_DELAY = 5.0
WALK_SPEED = 300.0
RUN_SPEED = 525.0
CROUCH_SPEED = 90.0
CROUCH_DURATION = 0.15
WORLD_MARGIN = 64
JUMP_SPEED = 900.0
GRAVITY = 2000.0
MEDIUM_JUMP_HOLD = 0.09
LONG_JUMP_HOLD = 0.18
SHORT_JUMP_HEIGHT = 90.0
MEDIUM_JUMP_HEIGHT = 145.0
TAKEOFF_FRAME_DURATION = 0.06
LAND_DURATION = 0.12
JUMP_BUFFER_DURATION = 0.10
ATTACK_BUFFER_WINDOW = 0.05
STANDING_HITBOX_WIDTH = 40.0
STANDING_HITBOX_HEIGHT = 140.0
CROUCH_HITBOX_WIDTH = 100.0
CROUCH_HITBOX_HEIGHT = 80.0
WALL_SLIDE_SPEED = 120.0
WALL_JUMP_SPEED_X = 480.0
WALL_JUMP_SPEED_Y = 820.0
WALL_JUMP_PUSH_TIME = 0.18
CONTACT_EPSILON = 0.000001


class Animation:
    def __init__(self, image_path, frames, foot_anchor, scale, fps, frame_durations_ms=()):
        self.image = load_image(str(image_path))
        self.frames = frames
        self.foot_anchor = foot_anchor
        self.scale = scale
        self.fps = fps
        self.frame_ends_ms = tuple(accumulate(frame_durations_ms))
        self.duration = len(frames) / fps if fps else float("inf")
        if self.frame_ends_ms:
            self.duration = self.frame_ends_ms[-1] / 1000

    def frame_at(self, elapsed):
        if self.frame_ends_ms:
            return min(bisect_right(self.frame_ends_ms, elapsed * 1000), len(self.frames) - 1)
        return int(elapsed * self.fps) % len(self.frames)

    def draw(self, x, y, facing, elapsed, camera, frame_index=None):
        if frame_index is None:
            frame_index = self.frame_at(elapsed)
        frame = self.frames[frame_index]
        width, height = frame["width"], frame["height"]
        anchor_x, anchor_y = frame.get("foot_anchor", self.foot_anchor)
        # Anchor ground contact or the projected foot position of an airborne pose.
        center_x = x + facing * (width / 2 - anchor_x) * self.scale
        center_y = y + (anchor_y - height / 2) * self.scale
        screen_x, screen_y = camera.world_to_screen(center_x, center_y)
        display_scale = self.scale * camera.zoom
        # Asset metadata uses top-left coordinates; pico2D clips from bottom-left.
        self.image.clip_composite_draw(
            frame["x"], self.image.h - frame["y"] - height,
            width, height, 0, "h" if facing < 0 else "",
            screen_x, screen_y, width * display_scale, height * display_scale,
        )


class Player:
    def __init__(self, x, ground_y, world_width, terrain=()):
        self.x = x
        self.y = ground_y
        self.ground_y = ground_y
        self.vertical_speed = 0.0
        self.world_width = world_width
        self.facing = 1
        self.state = "idle"
        self.animation_time = 0.0
        self.attack_time = None
        self.buffered_attack_down = None
        self.attack_animation_key = "attack"
        self.attack_facing = self.facing
        self.slash_starts = {}
        self.slash = None
        self.crouch_time = 0.0
        self.look_down_held = False
        self.terrain = tuple(terrain)
        self.grounded = True
        self.wall_direction = 0
        self.jump_buffer_remaining = 0.0
        self.jump_origin_y = None
        self.wall_jump_remaining = 0.0
        self.wall_jump_speed = 0.0

        # Use the approved source directly, rather than the old 64x64 export.
        idle_frame = {"x": 472, "y": 202, "width": 355, "height": 1011}
        self.animations = {
            "idle": Animation(
                ASSET_ROOT / "concepts/player-sd-idle-right-source-v3.png",
                [idle_frame], (178, 1011), 140 / 1011, 0,
            ),
        }
        for state, filename, scale in (
            ("idle_sword_dust", "idle-sword-dust-right-draft-v3", 140 / 288),
            ("walk", "walk-right-v1", 1.5),
            ("run", "run-right-v1", 0.5),
            ("jump", "jump-right-draft-v1", 140 / 388),
            ("crouch", "crouch-right-fast-v1", 140 / 411),
            ("crawl", "crawl-right-draft-v2", 0.29),
            ("wall_slide", "wall-slide-right-draft-v4", 140 / 665),
            ("attack", "attack-right-draft-v2", 140 / 582),
            ("air_attack", "air-attack-right-draft-v3", 140 / 582),
            ("air_down_attack", "air-down-attack-right-draft-v4", 140 / 620),
        ):
            metadata_path = ASSET_ROOT / "sprites/player" / f"{filename}.json"
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            self.animations[state] = Animation(
                metadata_path.parent / metadata["image"], metadata["frames"],
                metadata["foot_anchor"], scale, metadata["fps"],
                metadata.get("frame_durations_ms", ()),
            )
            if "look_down_image" in metadata:
                self.animations["jump_look_down"] = Animation(
                    metadata_path.parent / metadata["look_down_image"], metadata["frames"],
                    metadata["foot_anchor"], scale, metadata["fps"],
                )
            if "slash_frame" in metadata:
                windup = metadata["frame_durations_ms"][:metadata["slash_frame"]]
                self.slash_starts[state] = sum(windup) / 1000

    def update(
        self, direction, running, delta_time, jump_pressed=False, crouch_held=False,
        *, attack_pressed=False, jump_held=True,
    ):
        next_state = "idle"
        previous_x = self.x
        self.look_down_held = crouch_held
        attack_down = crouch_held
        self.grounded = self.vertical_speed <= 0 and self._has_support()
        self.wall_direction = 0 if self.grounded else self._touching_wall()

        if self.slash is not None:
            age, facing, downward = self.slash
            age += delta_time
            self.slash = (age, facing, downward) if age < SLASH_DURATION else None

        if self.attack_time is not None:
            attack = self.animations[self.attack_animation_key]
            previous_attack_time = self.attack_time
            self.attack_time += delta_time
            slash_start = self.slash_starts.get(self.attack_animation_key)
            if slash_start is not None and previous_attack_time < slash_start <= self.attack_time:
                slash_age = self.attack_time - slash_start
                if slash_age < SLASH_DURATION:
                    downward = self.attack_animation_key == "air_down_attack"
                    self.slash = (slash_age, self.attack_facing, downward)
            if self.attack_time >= attack.duration:
                self.attack_time = None
                if not attack_pressed and self.buffered_attack_down is not None:
                    attack_pressed = True
                    attack_down = self.buffered_attack_down
                self.buffered_attack_down = None
            else:
                if attack_pressed and attack.duration - self.attack_time <= ATTACK_BUFFER_WINDOW:
                    self.buffered_attack_down = attack_down
                attack_pressed = False

        if jump_pressed:
            self.jump_buffer_remaining = JUMP_BUFFER_DURATION

        if self.jump_buffer_remaining > 0:
            if self.grounded:
                self._start_jump()
            elif jump_pressed and self.wall_direction:
                self.wall_jump_speed = -self.wall_direction * WALL_JUMP_SPEED_X
                self.wall_jump_remaining = WALL_JUMP_PUSH_TIME
                self.facing = -self.wall_direction
                self._start_jump(from_wall=True)
        self.jump_buffer_remaining = max(0.0, self.jump_buffer_remaining - delta_time)

        crouching = self.state not in ("jump", "land", "wall_slide") and (crouch_held or self.crouch_time > 0)
        speed = CROUCH_SPEED if crouching else (RUN_SPEED if running else WALK_SPEED)
        horizontal_delta = direction * speed * delta_time
        if direction:
            self.facing = direction
            next_state = "run" if running else "walk"
        if self.wall_jump_remaining > 0:
            push_time = min(delta_time, self.wall_jump_remaining)
            horizontal_delta = self.wall_jump_speed * push_time + direction * speed * (delta_time - push_time)
            self.wall_jump_remaining = max(0.0, self.wall_jump_remaining - delta_time)
            self.facing = 1 if self.wall_jump_speed > 0 else -1
        self._move_horizontal(horizontal_delta)
        self.grounded = self.vertical_speed <= 0 and self._has_support()
        self.wall_direction = 0 if self.grounded else self._touching_wall()
        if (
            attack_pressed and self.crouch_time == 0 and self.state != "wall_slide"
            and not (self.grounded and crouch_held)
        ):
            # Keep the swing pose and direction fixed while movement and gravity continue.
            self.attack_time = 0.0
            if self.grounded:
                self.attack_animation_key = "attack"
            else:
                self.attack_animation_key = "air_down_attack" if attack_down else "air_attack"
            self.attack_facing = self.facing

        if not self.grounded and self.state not in ("jump", "wall_slide"):
            # Walking off a platform begins falling immediately, without jump anticipation.
            self.state = "jump"
            self.animation_time = TAKEOFF_FRAME_DURATION
        if self.state in ("jump", "wall_slide"):
            self._advance_air(delta_time, direction, jump_held)
            if self.state == "wall_slide":
                self.attack_time = None
                self.buffered_attack_down = None
            return

        if self.state == "land":
            self.animation_time += delta_time
            if self.animation_time < LAND_DURATION:
                return

        # Preserve transition progress when the key is released or pressed again.
        previous_crouch_time = self.crouch_time
        self.crouch_time = max(0.0, min(
            CROUCH_DURATION, self.crouch_time + (delta_time if crouch_held else -delta_time),
        ))
        if self._overlaps_terrain():
            self.crouch_time = previous_crouch_time
        if crouch_held or self.crouch_time > 0:
            self.attack_time = None
            self.buffered_attack_down = None
            # Keep the transition/hold pose unless the body is fully lowered and moving.
            next_crouch_state = "crouch"
            if crouch_held and self.crouch_time >= CROUCH_DURATION and self.x != previous_x:
                next_crouch_state = "crawl"
            if self.state != next_crouch_state:
                self.animation_time = 0.0
            elif next_crouch_state == "crawl":
                self.animation_time += delta_time
            self.state = next_crouch_state
            return

        if self.state != next_state or (next_state == "idle" and self.attack_time is not None):
            self.state = next_state
            self.animation_time = 0.0
        else:
            self.animation_time += delta_time

        if self.state == "idle":
            idle_cycle = IDLE_FLOURISH_DELAY + self.animations["idle_sword_dust"].duration
            if self.animation_time >= idle_cycle:
                self.animation_time = 0.0

    def _has_support(self):
        left, bottom, right, _ = self.get_hitbox()
        if abs(bottom - self.ground_y) <= CONTACT_EPSILON:
            return True
        return any(
            abs(bottom - top) <= CONTACT_EPSILON
            and right > x1 + CONTACT_EPSILON and left < x2 - CONTACT_EPSILON
            for x1, _, x2, top in self.terrain
        )

    def _touching_wall(self):
        left, bottom, right, top = self.get_hitbox()
        for x1, y1, x2, y2 in self.terrain:
            if bottom >= y2 - CONTACT_EPSILON or top <= y1 + CONTACT_EPSILON:
                continue
            if abs(right - x1) <= CONTACT_EPSILON:
                return 1
            if abs(left - x2) <= CONTACT_EPSILON:
                return -1
        return 0

    def _overlaps_terrain(self):
        left, bottom, right, top = self.get_hitbox()
        return any(
            left < x2 - CONTACT_EPSILON and right > x1 + CONTACT_EPSILON
            and bottom < y2 - CONTACT_EPSILON and top > y1 + CONTACT_EPSILON
            for x1, y1, x2, y2 in self.terrain
        )

    def _can_wall_slide(self, direction):
        if self.crouch_time > 0 or not direction or self.wall_direction != direction:
            return False
        left, bottom, right, _ = self.get_hitbox()
        # The raised hand and the lower foot both need solid wall behind them.
        return any(
            bottom >= y1 - CONTACT_EPSILON
            and bottom + STANDING_HITBOX_HEIGHT <= y2 + CONTACT_EPSILON
            and abs((right - x1) if direction > 0 else (left - x2)) <= CONTACT_EPSILON
            for x1, y1, x2, y2 in self.terrain
        )

    def _move_horizontal(self, distance):
        left, bottom, right, top = self.get_hitbox()
        for x1, y1, x2, y2 in self.terrain:
            if bottom >= y2 - CONTACT_EPSILON or top <= y1 + CONTACT_EPSILON:
                continue
            # Check crossed faces, not just final overlap, to avoid tunneling.
            if distance > 0 and right <= x1 + CONTACT_EPSILON and right + distance >= x1:
                distance = min(distance, x1 - right)
            elif distance < 0 and left >= x2 - CONTACT_EPSILON and left + distance <= x2:
                distance = max(distance, x2 - left)
        self.x = max(WORLD_MARGIN, min(self.world_width - WORLD_MARGIN, self.x + distance))

    def _move_vertical(self, distance):
        left, bottom, right, top = self.get_hitbox()
        landed = False
        if distance <= 0:
            destination = self.y + distance
            if destination <= self.ground_y:
                destination = self.ground_y
                landed = True
            for x1, _, x2, y2 in self.terrain:
                if right <= x1 + CONTACT_EPSILON or left >= x2 - CONTACT_EPSILON:
                    continue
                if bottom >= y2 - CONTACT_EPSILON and self.y + distance <= y2:
                    destination = max(destination, y2)
                    landed = True
            self.y = destination
            if landed:
                self.vertical_speed = 0.0
        else:
            for x1, y1, x2, _ in self.terrain:
                if right <= x1 + CONTACT_EPSILON or left >= x2 - CONTACT_EPSILON:
                    continue
                if top <= y1 + CONTACT_EPSILON and top + distance >= y1:
                    distance = min(distance, y1 - top)
                    self.vertical_speed = 0.0
            self.y += distance
        self.grounded = landed
        return landed

    def _start_jump(self, *, from_wall=False):
        if self.crouch_time > 0:
            self._try_stand()
        self.state = "jump"
        self.animation_time = 0.0
        self.vertical_speed = WALL_JUMP_SPEED_Y if from_wall else JUMP_SPEED
        self.jump_origin_y = None if from_wall else self.y
        self.grounded = False
        self.jump_buffer_remaining = 0.0

    def _try_stand(self):
        previous_crouch_time = self.crouch_time
        self.crouch_time = 0.0
        if self._overlaps_terrain():
            self.crouch_time = previous_crouch_time

    def _advance_air(self, delta_time, direction, jump_held):
        if self.crouch_time > 0:
            self._try_stand()
            self.wall_direction = 0 if self.grounded else self._touching_wall()
        if self.jump_origin_y is not None:
            if self.vertical_speed <= 0 or self.animation_time >= LONG_JUMP_HOLD:
                self.jump_origin_y = None
            elif not jump_held:
                # Match the chosen apex even when Space is released later within the same tier.
                height = SHORT_JUMP_HEIGHT if self.animation_time < MEDIUM_JUMP_HOLD else MEDIUM_JUMP_HEIGHT
                remaining_height = max(0.0, self.jump_origin_y + height - self.y)
                self.vertical_speed = min(self.vertical_speed, sqrt(2 * GRAVITY * remaining_height))
                self.jump_origin_y = None
        self.animation_time += delta_time
        if delta_time <= 0:
            return

        sliding = self._can_wall_slide(direction) and self.vertical_speed <= 0
        if sliding:
            self.vertical_speed = max(self.vertical_speed, -WALL_SLIDE_SPEED)
            acceleration_time = min(delta_time, (self.vertical_speed + WALL_SLIDE_SPEED) / GRAVITY)
            distance = self.vertical_speed * acceleration_time - 0.5 * GRAVITY * acceleration_time ** 2
            distance -= WALL_SLIDE_SPEED * (delta_time - acceleration_time)
            self.vertical_speed = max(-WALL_SLIDE_SPEED, self.vertical_speed - GRAVITY * delta_time)
        else:
            distance = self.vertical_speed * delta_time - 0.5 * GRAVITY * delta_time ** 2
            self.vertical_speed -= GRAVITY * delta_time
        if self._move_vertical(distance):
            self.wall_direction = 0
            self.wall_jump_remaining = 0.0
            if self.jump_buffer_remaining > 0:
                self._start_jump()
            else:
                self.state = "land"
                self.animation_time = 0.0
                self.jump_buffer_remaining = 0.0
            return
        self.wall_direction = self._touching_wall()
        if self._can_wall_slide(direction) and self.vertical_speed <= 0:
            if self.state != "wall_slide":
                self.animation_time = 0.0
            self.state = "wall_slide"
            self.vertical_speed = max(self.vertical_speed, -WALL_SLIDE_SPEED)
            self.facing = self.wall_direction
        else:
            if self.state == "wall_slide":
                # Leaving the wall resumes falling, without ground takeoff frames.
                self.animation_time = TAKEOFF_FRAME_DURATION
            self.state = "jump"

    def get_jump_frame(self):
        if self.state == "land":
            return 6 if self.animation_time < 0.08 else 7
        if self.animation_time < TAKEOFF_FRAME_DURATION:
            return 1
        if self.vertical_speed > JUMP_SPEED * 0.25:
            return 2
        if self.vertical_speed > -JUMP_SPEED * 0.15:
            return 3
        if self.vertical_speed > -JUMP_SPEED * 0.65:
            return 4
        return 5

    def get_wall_slide_frame(self):
        animation = self.animations["wall_slide"]
        return min(len(animation.frames) - 1, int(self.animation_time * animation.fps))

    def get_crouch_frame(self):
        last_frame = len(self.animations["crouch"].frames) - 1
        return min(last_frame, int(self.crouch_time / CROUCH_DURATION * last_frame))

    def get_hitbox(self):
        # Use body dimensions, independent of the weapon and animation frame.
        crouch_ratio = self.crouch_time / CROUCH_DURATION
        width = STANDING_HITBOX_WIDTH + (CROUCH_HITBOX_WIDTH - STANDING_HITBOX_WIDTH) * crouch_ratio
        height = STANDING_HITBOX_HEIGHT + (CROUCH_HITBOX_HEIGHT - STANDING_HITBOX_HEIGHT) * crouch_ratio
        return self.x - width / 2, self.y, self.x + width / 2, self.y + height

    def draw_hitbox(self, camera):
        left, bottom, right, top = self.get_hitbox()
        screen_left, screen_bottom = camera.world_to_screen(left, bottom)
        screen_right, screen_top = camera.world_to_screen(right, top)
        draw_rectangle(screen_left, screen_bottom, screen_right, screen_top, 255, 96, 80)

    def draw(self, camera):
        if self.slash is not None:
            age, facing, downward = self.slash
            draw_slash(self.x, self.y, facing, age, camera, downward=downward)

        if self.attack_time is not None:
            attack = self.animations[self.attack_animation_key]
            frame_index = attack.frame_at(self.attack_time)
            if self.state == "idle" or not attack.frames[frame_index].get("movement_pose"):
                attack.draw(
                    self.x, self.y, self.attack_facing, self.attack_time, camera, frame_index,
                )
                return

        jumping = self.state in ("jump", "land")
        animation = self.animations["jump" if jumping else self.state]
        elapsed = self.animation_time
        if self.state == "idle" and elapsed >= IDLE_FLOURISH_DELAY:
            animation = self.animations["idle_sword_dust"]
            elapsed -= IDLE_FLOURISH_DELAY
        frame_index = self.get_jump_frame() if jumping else None
        if self.state == "jump" and (self.look_down_held or self.vertical_speed < 0):
            animation = self.animations.get("jump_look_down", animation)
        if self.state == "wall_slide":
            frame_index = self.get_wall_slide_frame()
        elif self.state == "crouch" or (self.state == "land" and self.crouch_time > 0):
            animation = self.animations["crouch"]
            frame_index = self.get_crouch_frame()
        facing = self.facing if self.attack_time is None else self.attack_facing
        animation.draw(
            self.x, self.y, facing, elapsed, camera,
            frame_index,
        )

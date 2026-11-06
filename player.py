"""Player movement, jumping, crouching, and the approved character artwork."""

import json
from pathlib import Path

from pico2d import draw_rectangle, load_image


ASSET_ROOT = Path(__file__).resolve().parent / "assets"
WALK_SPEED = 300.0
RUN_SPEED = 525.0
CROUCH_SPEED = 90.0
CROUCH_DURATION = 0.15
WORLD_MARGIN = 64
JUMP_SPEED = 900.0
GRAVITY = 2000.0
TAKEOFF_DURATION = 0.06
LAND_DURATION = 0.12
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
    def __init__(self, image_path, frames, foot_anchor, scale, fps):
        self.image = load_image(str(image_path))
        self.frames = frames
        self.foot_anchor = foot_anchor
        self.scale = scale
        self.fps = fps

    def draw(self, x, y, facing, elapsed, camera, frame_index=None):
        if frame_index is None:
            frame_index = int(elapsed * self.fps) % len(self.frames)
        frame = self.frames[frame_index]
        width, height = frame["width"], frame["height"]
        anchor_x, anchor_y = frame.get("foot_anchor", self.foot_anchor)
        # Keep the feet at the same world position across differently sized art.
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
        self.crouch_time = 0.0
        self.terrain = tuple(terrain)
        self.grounded = True
        self.wall_direction = 0
        self.takeoff_remaining = 0.0
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
            ("walk", "walk-right-v1", 1.5),
            ("run", "run-right-v1", 0.5),
            ("jump", "jump-right-draft-v1", 140 / 388),
            ("crouch", "crouch-right-fast-v1", 140 / 411),
            ("crawl", "crawl-right-draft-v2", 140 / 466),
            ("wall_slide", "wall-slide-right-draft-v4", 140 / 665),
        ):
            metadata_path = ASSET_ROOT / "sprites/player" / f"{filename}.json"
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            self.animations[state] = Animation(
                metadata_path.parent / metadata["image"], metadata["frames"],
                metadata["foot_anchor"], scale, metadata["fps"],
            )

    def update(self, direction, running, delta_time, jump_pressed=False, crouch_held=False):
        next_state = "idle"
        previous_x = self.x
        self.grounded = self.vertical_speed <= 0 and self._has_support()
        self.wall_direction = 0 if self.grounded else self._touching_wall()
        crouching = self.state not in ("jump", "land", "wall_slide") and (crouch_held or self.crouch_time > 0)

        if jump_pressed and not crouching:
            if self.grounded and self.state not in ("jump", "land"):
                self.state = "jump"
                self.animation_time = 0.0
                self.takeoff_remaining = TAKEOFF_DURATION
            elif not self.grounded and self.wall_direction:
                self.vertical_speed = WALL_JUMP_SPEED_Y
                self.wall_jump_speed = -self.wall_direction * WALL_JUMP_SPEED_X
                self.wall_jump_remaining = WALL_JUMP_PUSH_TIME
                self.takeoff_remaining = 0.0
                self.facing = -self.wall_direction
                self.state = "jump"
                self.animation_time = TAKEOFF_DURATION

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

        if not self.grounded and self.state not in ("jump", "wall_slide"):
            # Walking off a platform begins falling immediately, without jump anticipation.
            self.state = "jump"
            self.animation_time = TAKEOFF_DURATION + 0.06
            self.takeoff_remaining = 0.0
        if self.state in ("jump", "wall_slide"):
            self._advance_air(delta_time, direction)
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

        if self.state != next_state:
            self.state = next_state
            self.animation_time = 0.0
        else:
            self.animation_time += delta_time

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
        if not direction or self.wall_direction != direction:
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

    def _advance_air(self, delta_time, direction):
        if self.crouch_time > 0:
            previous_crouch_time = self.crouch_time
            self.crouch_time = 0.0
            if self._overlaps_terrain():
                self.crouch_time = previous_crouch_time
            self.wall_direction = 0 if self.grounded else self._touching_wall()
        self.animation_time += delta_time
        air_delta = delta_time
        if self.takeoff_remaining > 0:
            if self.grounded:
                preparation = min(delta_time, self.takeoff_remaining)
                self.takeoff_remaining -= preparation
                air_delta -= preparation
            else:
                self.takeoff_remaining = 0.0
            if self.takeoff_remaining <= CONTACT_EPSILON:
                self.takeoff_remaining = 0.0
                self.vertical_speed = JUMP_SPEED
                self.grounded = False
        if air_delta <= 0:
            return

        sliding = self._can_wall_slide(direction) and self.vertical_speed <= 0
        if sliding:
            self.vertical_speed = max(self.vertical_speed, -WALL_SLIDE_SPEED)
            acceleration_time = min(air_delta, (self.vertical_speed + WALL_SLIDE_SPEED) / GRAVITY)
            distance = self.vertical_speed * acceleration_time - 0.5 * GRAVITY * acceleration_time ** 2
            distance -= WALL_SLIDE_SPEED * (air_delta - acceleration_time)
            self.vertical_speed = max(-WALL_SLIDE_SPEED, self.vertical_speed - GRAVITY * air_delta)
        else:
            distance = self.vertical_speed * air_delta - 0.5 * GRAVITY * air_delta ** 2
            self.vertical_speed -= GRAVITY * air_delta
        if self._move_vertical(distance):
            self.state = "land"
            self.animation_time = 0.0
            self.wall_direction = 0
            self.wall_jump_remaining = 0.0
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
                self.animation_time = TAKEOFF_DURATION + 0.06
            self.state = "jump"

    def get_jump_frame(self):
        if self.state == "land":
            return 6 if self.animation_time < 0.08 else 7
        if self.animation_time < TAKEOFF_DURATION:
            return 0
        if self.animation_time < TAKEOFF_DURATION + 0.06:
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
        jumping = self.state in ("jump", "land")
        animation = self.animations["jump" if jumping else self.state]
        frame_index = self.get_jump_frame() if jumping else None
        if self.state == "wall_slide":
            frame_index = self.get_wall_slide_frame()
        elif self.state == "crouch":
            frame_index = self.get_crouch_frame()
        if (jumping or self.state == "wall_slide") and self.crouch_time > 0:
            animation = self.animations["crouch"]
            frame_index = self.get_crouch_frame()
        animation.draw(
            self.x, self.y, self.facing, self.animation_time, camera,
            frame_index,
        )

"""Player movement and the existing idle, walk, and run artwork."""

import json
from pathlib import Path

from pico2d import load_image


ASSET_ROOT = Path(__file__).resolve().parent / "assets"
WALK_SPEED = 180.0
RUN_SPEED = 320.0
WORLD_MARGIN = 64


class Animation:
    def __init__(self, image_path, frames, foot_anchor, scale, fps):
        self.image = load_image(str(image_path))
        self.frames = frames
        self.foot_anchor = foot_anchor
        self.scale = scale
        self.fps = fps

    def draw(self, x, y, facing, elapsed, camera):
        frame = self.frames[int(elapsed * self.fps) % len(self.frames)]
        width, height = frame["width"], frame["height"]
        anchor_x, anchor_y = self.foot_anchor
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
    def __init__(self, x, ground_y, world_width):
        self.x = x
        self.y = ground_y
        self.world_width = world_width
        self.facing = 1
        self.state = "idle"
        self.animation_time = 0.0

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
        ):
            metadata_path = ASSET_ROOT / "sprites/player" / f"{filename}.json"
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            self.animations[state] = Animation(
                metadata_path.parent / metadata["image"], metadata["frames"],
                metadata["foot_anchor"], scale, metadata["fps"],
            )

    def update(self, direction, running, delta_time):
        next_state = "idle"
        if direction:
            self.facing = direction
            next_state = "run" if running else "walk"
            speed = RUN_SPEED if running else WALK_SPEED
            self.x += direction * speed * delta_time
            self.x = max(WORLD_MARGIN, min(self.world_width - WORLD_MARGIN, self.x))

        if self.state != next_state:
            self.state = next_state
            self.animation_time = 0.0
        else:
            self.animation_time += delta_time

    def draw(self, camera):
        self.animations[self.state].draw(
            self.x, self.y, self.facing, self.animation_time, camera,
        )

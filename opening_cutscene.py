"""Automatic, weaponless approach to the cave sigil after investigation."""

from bisect import bisect_right
from itertools import accumulate
import json

from opening_cave import END_WALL_X, GROUND_Y
from player import ASSET_ROOT, Animation, STANDING_HITBOX_HEIGHT, STANDING_HITBOX_WIDTH


INTERACTION_DISTANCE = 420
OBSERVE_DURATION = 0.55
APPROACH_SPEED = 90
TOUCH_X = END_WALL_X - STANDING_HITBOX_WIDTH / 2
ANIMATION_DATA = ASSET_ROOT / "sprites/player/opening-investigate-unarmed-right-v3.json"


class SigilApproach:
    def __init__(self):
        metadata = json.loads(ANIMATION_DATA.read_text(encoding="utf-8"))
        self.art = Animation(
            ANIMATION_DATA.parent / metadata["image"], metadata["frames"],
            metadata["foot_anchor"], STANDING_HITBOX_HEIGHT / metadata["reference_height"], 0,
        )
        self.walk_frames = metadata["walk_frames"]
        self.walk_fps = metadata["walk_fps"]
        self.reach_frames = metadata["reach_frames"]
        self.reach_ends = tuple(accumulate(t / 1000 for t in metadata["reach_frame_durations_ms"]))
        self.reset()

    def reset(self):
        self.phase = "idle"
        self.phase_time = 0.0

    @property
    def active(self):
        return self.phase != "idle"

    @property
    def frame_index(self):
        if self.phase == "observe":
            return self.reach_frames[0]
        if self.phase == "walk":
            return self.walk_frames[int(self.phase_time * self.walk_fps) % len(self.walk_frames)]
        if self.phase == "reach":
            index = min(bisect_right(self.reach_ends, self.phase_time), len(self.reach_frames) - 1)
            return self.reach_frames[index]
        return self.reach_frames[-1]

    def can_start(self, player):
        return (
            not self.active and player.grounded and abs(player.y - GROUND_Y) < 0.001
            and 0 <= TOUCH_X - player.x <= INTERACTION_DISTANCE
        )

    def start(self, player):
        if not self.can_start(player) or not player.recover_at(player.x, GROUND_Y, 0.0):
            return False
        player.facing = 1
        self.phase = "observe"
        self.phase_time = 0.0
        return True

    def _enter(self, phase):
        self.phase = phase
        self.phase_time = 0.0

    def update(self, player, delta_time):
        remaining = max(0.0, delta_time)
        while remaining > 0 and self.active:
            if self.phase == "observe":
                step = min(remaining, max(0, OBSERVE_DURATION - self.phase_time))
                self.phase_time += step
                remaining -= step
                if self.phase_time >= OBSERVE_DURATION - 1e-9:
                    self._enter("walk")
                else:
                    break
            elif self.phase == "walk":
                distance = max(0, TOUCH_X - player.x)
                step = min(remaining, distance / APPROACH_SPEED)
                player.x = min(TOUCH_X, player.x + APPROACH_SPEED * step)
                self.phase_time += step
                remaining -= step
                if TOUCH_X - player.x < 1e-6:
                    player.x = TOUCH_X
                    self._enter("reach")
                else:
                    break
            elif self.phase == "reach":
                step = min(remaining, max(0, self.reach_ends[-1] - self.phase_time))
                self.phase_time += step
                remaining -= step
                if self.phase_time >= self.reach_ends[-1] - 1e-9:
                    self._enter("touch")
                else:
                    break
            else:
                # Hold contact while the later light, collapse and fall are authored.
                break

    def draw(self, player, camera):
        if not self.active:
            return False
        self.art.draw(player.x, player.y, 1, 0, camera, self.frame_index)
        return True

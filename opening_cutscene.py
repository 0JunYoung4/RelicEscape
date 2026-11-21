"""Automatic, weaponless approach to the cave sigil after investigation."""

from bisect import bisect_right
from itertools import accumulate
from math import inf, pi, sin
import json

from opening_cave import BROKEN_TERRAIN, END_WALL_X, GROUND_Y, SHAFT_FLOOR, SHAFT_TOP, TERRAIN
from player import ASSET_ROOT, Animation, STANDING_HITBOX_HEIGHT, STANDING_HITBOX_WIDTH


INTERACTION_DISTANCE = 420
OBSERVE_DURATION = 0.55
APPROACH_SPEED = 90
TOUCH_X = END_WALL_X - STANDING_HITBOX_WIDTH / 2
ANIMATION_DATA = ASSET_ROOT / "sprites/player/opening-investigate-unarmed-right-v3.json"
RECOIL_DATA = ASSET_ROOT / "sprites/player/opening-recoil-right-v1.json"
RETREAT_DISTANCE = 190
TREMORS = (0.85, 1.95, 3.05)
QUAKE_START = 4.15
COLLAPSE_START = 4.55
COLLAPSE_DURATION = ((GROUND_Y - SHAFT_TOP) / 720) ** 0.5
DESCENT_DURATION = 3.8
FLAIL_FPS = 10
SEAT_REBOUND_START = 0.10
SEAT_SETTLE = 0.38
GET_UP_START = SEAT_SETTLE + 0.55


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
        recoil = json.loads(RECOIL_DATA.read_text(encoding="utf-8"))
        self.recoil = Animation(
            RECOIL_DATA.parent / recoil["image"], recoil["frames"], (0, 0),
            STANDING_HITBOX_HEIGHT / recoil["reference_height"], recoil["fps"],
        )
        fall_data = RECOIL_DATA.with_name("opening-shaft-flail-seated.json")
        fall = json.loads(fall_data.read_text(encoding="utf-8"))
        self.fall = Animation(fall_data.parent / fall["image"], fall["frames"], (0, 0),
                              STANDING_HITBOX_HEIGHT / fall["reference_height"], 0)
        rise_data = RECOIL_DATA.with_name("opening-stand-up.json")
        rise = json.loads(rise_data.read_text(encoding="utf-8"))
        self.rise = Animation(rise_data.parent / rise["image"], rise["frames"], (0, 0),
                              STANDING_HITBOX_HEIGHT / rise["reference_height"], 0,
                              rise["frame_durations_ms"])
        self.reset()

    def reset(self, player=None):
        self.phase = "idle"
        self.phase_time = 0.0
        if player is not None:
            player.terrain = TERRAIN
            player.ground_y = GROUND_Y

    @property
    def active(self):
        return self.phase != "idle"

    @property
    def stood_up(self):
        return self.phase == "impact" and self.phase_time >= GET_UP_START + self.rise.duration

    @property
    def frame_index(self):
        if self.phase == "impact":
            if self.phase_time >= GET_UP_START:
                return self.rise.frame_at(self.phase_time - GET_UP_START)
            return 9 + bisect_right((SEAT_REBOUND_START, SEAT_SETTLE), self.phase_time)
        if self.phase in ("collapse", "descent"):
            elapsed = self.phase_time
            if self.phase == "descent":
                if elapsed >= DESCENT_DURATION - 0.18:
                    return 8  # Heels forward just before the seat hits the floor.
                elapsed += COLLAPSE_DURATION
            return int(elapsed * FLAIL_FPS) % 8
        if self.phase == "braced":
            return len(self.recoil.frames) - 1
        if self.phase == "recoil":
            return min(int(self.phase_time * self.recoil.fps), len(self.recoil.frames) - 1)
        if self.phase == "observe":
            return self.reach_frames[0]
        if self.phase == "walk":
            return self.walk_frames[int(self.phase_time * self.walk_fps) % len(self.walk_frames)]
        if self.phase == "reach":
            index = min(bisect_right(self.reach_ends, self.phase_time), len(self.reach_frames) - 1)
            return self.reach_frames[index]
        return self.reach_frames[-1]

    @property
    def contact_time(self):
        if self.phase == "collapse":
            return COLLAPSE_START + self.phase_time
        if self.phase == "reach":
            return max(0.0, self.phase_time - self.reach_ends[-2])
        if self.phase in ("recoil", "braced"):
            elapsed = self.phase_time
            if self.phase == "braced":
                elapsed += self.recoil.duration
            return self.reach_ends[-1] - self.reach_ends[-2] + elapsed
        return 0.0

    @property
    def sigil_light(self):
        t = self.contact_time
        base = 0.80 * min(t / 0.32, 1.0)
        return base + sum(gain * max(0, min(1, (t - start) / 0.28))
                          for start, gain in zip(TREMORS, (0.62, 0.84, 1.08)))

    @property
    def collapse_time(self):
        return self.phase_time if self.phase == "collapse" else None

    def shake(self):
        t = self.contact_time
        strength = 0.0
        for i, start in enumerate(TREMORS):
            beat = (t - start) / 0.68
            if 0 < beat < 1:
                strength = (0.7 + 0.35 * i) * sin(pi * beat)
        if t >= QUAKE_START:
            attack = min(1.0, (t - QUAKE_START) / 0.14)
            decay = max(0, min(1, (COLLAPSE_START + 1.6 - t) / 0.8))
            strength = 2.15 * attack * decay
        # Pixel offsets. Bias horizontal shake inward at the world's right edge.
        return (3.5 * strength * (sin(51*t) - 1),
                strength * (3.5 * sin(62*t) + 1.2 * sin(39*t)))

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
                    self._enter("recoil")
                else:
                    break
            elif self.phase == "recoil":
                step = min(remaining, self.recoil.duration - self.phase_time)
                self.phase_time += step
                remaining -= step
                # Feet push back in two steps, after the initial stationary flinch.
                frame = self.phase_time * self.recoil.fps
                first = max(0.0, min(1.0, (frame - 3) / 4))
                second = max(0.0, min(1.0, (frame - 8) / 5))
                player.x = TOUCH_X - RETREAT_DISTANCE * (
                    0.48 * first * first * (3 - 2 * first)
                    + 0.52 * second * second * (3 - 2 * second)
                )
                if self.phase_time >= self.recoil.duration - 1e-9:
                    self._enter("braced")
            elif self.phase == "braced":
                step = min(remaining, max(0.0, COLLAPSE_START - self.contact_time))
                self.phase_time += step
                remaining -= step
                if self.contact_time >= COLLAPSE_START - 1e-9:
                    self._enter("collapse")
                    player.terrain = BROKEN_TERRAIN
                    player.ground_y = -inf
                    player.grounded = False
            elif self.phase == "collapse":
                step = min(remaining, COLLAPSE_DURATION - self.phase_time)
                self.phase_time += step
                remaining -= step
                player.y = GROUND_Y - 720 * self.phase_time ** 2
                if self.phase_time >= COLLAPSE_DURATION - 1e-9:
                    self._enter("descent")
            elif self.phase == "descent":
                step = min(remaining, DESCENT_DURATION - self.phase_time)
                self.phase_time += step
                remaining -= step
                t = self.phase_time / DESCENT_DURATION
                player.y = SHAFT_TOP + (SHAFT_FLOOR - SHAFT_TOP) * t * (0.82 + 0.18 * t)
                if self.phase_time >= DESCENT_DURATION:
                    player.y = player.ground_y = SHAFT_FLOOR
                    player.grounded = True
                    self._enter("impact")
            else:
                self.phase_time = min(GET_UP_START + self.rise.duration, self.phase_time + remaining)
                break

    def draw(self, player, camera):
        if not self.active:
            return False
        y = player.y
        if self.phase == "impact" and self.phase_time >= GET_UP_START:
            art = self.rise
        elif self.phase in ("collapse", "descent", "impact"):
            art = self.fall
            if self.phase == "impact" and SEAT_REBOUND_START < self.phase_time < SEAT_SETTLE:
                t = (self.phase_time - SEAT_REBOUND_START) / (SEAT_SETTLE - SEAT_REBOUND_START)
                y += 4 * 13 * t * (1 - t)
        elif self.phase in ("recoil", "braced"):
            art = self.recoil
        else:
            art = self.art
        art.draw(player.x, y, 1, 0, camera, self.frame_index)
        return True

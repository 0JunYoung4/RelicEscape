"""Separate crystal artwork, ballistic flight, and swept impact collision."""

from dataclasses import dataclass
from math import atan2, ceil, sqrt


GRAVITY = 1000.0
ARC_RISE = 160.0
RADIUS = 8.0
DISPLAY_LENGTH = 76.0
MAX_AGE = 5.0
DAMAGE = 10


def segment_box_hit(start, end, box):
    """Return the first fraction along a segment inside an axis-aligned box."""
    entry, exit = 0.0, 1.0
    for origin, destination, low, high in zip(start, end, box[:2], box[2:]):
        delta = destination - origin
        if abs(delta) < 1e-12:
            if origin < low or origin > high:
                return None
            continue
        near, far = sorted(((low - origin) / delta, (high - origin) / delta))
        entry, exit = max(entry, near), min(exit, far)
        if entry > exit:
            return None
    return entry


@dataclass
class CrystalProjectile:
    x: float
    y: float
    vx: float
    vy: float
    age: float = 0.0
    active: bool = True

    @classmethod
    def aimed(cls, origin, target):
        x, y = origin
        target_x, target_y = target
        apex = max(y, target_y) + ARC_RISE
        vy = sqrt(2 * GRAVITY * (apex - y))
        flight_time = vy / GRAVITY + sqrt(2 * (apex - target_y) / GRAVITY)
        return cls(x, y, (target_x - x) / flight_time, vy)

    def update(self, dt, terrain, world_width, player_box=None, *, ground_y=0):
        if not self.active or dt <= 0:
            return None
        # Subdivide the curve, then sweep each segment so fast shards cannot tunnel.
        steps = max(1, ceil(dt * 120))
        step = dt / steps
        for _ in range(steps):
            start = self.x, self.y
            end = self.x + self.vx * step, self.y + self.vy * step - GRAVITY * step ** 2 / 2
            first, impact = 1.0, None
            for box in (*terrain, (-RADIUS, ground_y - 1000, world_width + RADIUS, ground_y)):
                expanded = box[0] - RADIUS, box[1] - RADIUS, box[2] + RADIUS, box[3] + RADIUS
                hit = segment_box_hit(start, end, expanded)
                if hit is not None and (impact is None or hit < first):
                    first, impact = hit, "terrain"
            if player_box is not None:
                left, bottom, right, top = player_box
                hit = segment_box_hit(start, end, (left - RADIUS, bottom - RADIUS,
                                                   right + RADIUS, top + RADIUS))
                if hit is not None and (impact is None or hit < first):
                    first, impact = hit, "player"
            self.x = start[0] + (end[0] - start[0]) * first
            self.y = start[1] + (end[1] - start[1]) * first
            self.vy -= GRAVITY * step * first
            self.age += step * first
            if impact is not None:
                self.active = False
                return impact
            if self.age >= MAX_AGE or not -RADIUS <= self.x <= world_width + RADIUS:
                self.active = False
                break
        return None

    def draw(self, image, camera):
        if self.active:
            length = DISPLAY_LENGTH * camera.zoom
            image.composite_draw(atan2(self.vy, self.vx), "", *camera.world_to_screen(self.x, self.y),
                                 length, length * image.h / image.w)

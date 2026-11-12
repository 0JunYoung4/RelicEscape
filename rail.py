"""Connect straight and quarter-turn rail pieces and move their carriage."""

from dataclasses import dataclass
from math import atan2, cos, hypot, pi, sin, tau


RAIL_MOUNT_RADIUS = 90
RAIL_TRAVEL_SPEED = 660
RAIL_ART_SCALE = 3  # World units per pixel at the authored size.
BEND_ART_RADIUS = 72


@dataclass(frozen=True)
class RailSegment:
    start: tuple[float, float]
    end: tuple[float, float]
    center: tuple[float, float] | None = None

    @property
    def length(self):
        if self.center is None:
            return hypot(self.end[0] - self.start[0], self.end[1] - self.start[1])
        return self.radius * pi / 2

    @property
    def radius(self):
        return hypot(self.start[0] - self.center[0], self.start[1] - self.center[1])

    def point_at(self, fraction):
        start_x, start_y = self.start
        end_x, end_y = self.end
        if self.center is None:
            return start_x + (end_x - start_x) * fraction, start_y + (end_y - start_y) * fraction
        cx, cy = self.center
        start_angle = atan2(start_y - cy, start_x - cx)
        end_angle = atan2(end_y - cy, end_x - cx)
        turn = (end_angle - start_angle + pi) % tau - pi
        angle = start_angle + turn * fraction
        return cx + self.radius * cos(angle), cy + self.radius * sin(angle)


class RailCarriage:
    def __init__(self, segments, width, height):
        self.segments = segments
        self.length = sum(segment.length for segment in segments)
        self.distance = 0.0
        self.half_width = width / 2
        self.half_height = height / 2
        self.direction = 0
        self.relic_mounted = False
        self.hit_by_swing = False

    @property
    def position(self):
        remaining = self.distance
        for segment in self.segments:
            length = segment.length
            if remaining < length:
                return segment.point_at(remaining / length)
            remaining -= length
        return self.segments[-1].end

    def can_mount(self, player, relic_placed):
        if relic_placed or self.relic_mounted:
            return False
        x, y = self.position
        _, bottom, _, top = player.get_hitbox()
        return hypot(x - player.x, y - (bottom + top) / 2) <= RAIL_MOUNT_RADIUS

    def check_attack(self, player):
        hitbox = player.get_attack_hitbox()
        if hitbox is None:
            self.hit_by_swing = False
            return
        if self.hit_by_swing:
            return
        x, y = self.position
        left, bottom, right, top = hitbox
        if (
            left < x + self.half_width and right > x - self.half_width
            and bottom < y + self.half_height and top > y - self.half_height
        ):
            self.direction = player.attack_facing
            self.hit_by_swing = True

    def move(self, delta_time):
        if self.direction == 0:
            return
        destination = self.length if self.direction > 0 else 0.0
        self.distance += self.direction * RAIL_TRAVEL_SPEED * delta_time
        self.distance = max(0.0, min(self.length, self.distance))
        if self.distance == destination:
            self.direction = 0


def draw_rail(straight_image, bend_image, camera, segments):
    for index, segment in enumerate(segments):
        if segment.center is None:
            _draw_straight(straight_image, camera, segment, index, len(segments))
        else:
            _draw_bend(bend_image, camera, segment)


def _draw_straight(image, camera, segment, index, segment_count):
    x1, y1 = map(round, camera.world_to_screen(*segment.start))
    x2, y2 = map(round, camera.world_to_screen(*segment.end))
    width = round(hypot(x2 - x1, y2 - y1))
    if width == 0:
        return
    source_width = min(image.w, max(1, round(segment.length / RAIL_ART_SCALE)))
    # Only the two exposed ends use the rounded tips of the straight artwork.
    source_left = 0
    if index == segment_count - 1:
        source_left = image.w - source_width
    elif index > 0:
        source_left = (image.w - source_width) // 2
    angle = atan2(y2 - y1, x2 - x1)
    height = round(image.h * RAIL_ART_SCALE * camera.zoom)
    image.clip_composite_draw(
        source_left, 0, source_width, image.h, angle, "",
        (x1 + x2) / 2, (y1 + y2) / 2, width, height,
    )


def _draw_bend(image, camera, segment):
    cx, cy = segment.center
    flip_x = min(segment.start[0], segment.end[0]) < cx
    flip_y = max(segment.start[1], segment.end[1]) > cy
    flip = ("h" if flip_x else "") + ("v" if flip_y else "")
    width = segment.radius * image.w / BEND_ART_RADIUS
    height = segment.radius * image.h / BEND_ART_RADIUS
    left = cx - width if flip_x else cx
    bottom = cy if flip_y else cy - height
    x1, y1 = map(round, camera.world_to_screen(left, bottom))
    x2, y2 = map(round, camera.world_to_screen(left + width, bottom + height))
    image.composite_draw(0, flip, (x1 + x2) / 2, (y1 + y2) / 2, x2 - x1, y2 - y1)

"""Connect straight and quarter-turn rail pieces and move their carriage."""

from ctypes import c_int
from dataclasses import dataclass
from math import atan2, cos, hypot, pi, sin, tau
from pathlib import Path

from pico2d import pico2d as pico


RAIL_MOUNT_RADIUS = 90
RAIL_TRAVEL_SPEED = 660
RAIL_ART_SCALE = 3  # World units per pixel at the authored size.
BEND_ART_RADIUS = 72
RAIL_ASSETS = Path(__file__).resolve().parent / "assets/sprites/rail"
RAIL_IMAGE = RAIL_ASSETS / "relic-track-blue-v4.png"
RAIL_BEND_IMAGE = RAIL_ASSETS / "relic-track-bend-v2.png"
RAIL_CARRIAGE_IMAGE = RAIL_ASSETS / "relic-carriage-v2.png"
BEND_STEPS = 16
BEND_DIRECTIONS = tuple(
    (cos(step * pi / (2 * BEND_STEPS)), sin(step * pi / (2 * BEND_STEPS)))
    for step in range(BEND_STEPS + 1)
)
BEND_TRIANGLES = (c_int * (6 * BEND_STEPS))(*(
    index for start in range(0, 2 * BEND_STEPS, 2)
    for index in (start, start + 1, start + 2, start + 1, start + 3, start + 2)
))


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
    thickness = round(straight_image.h * RAIL_ART_SCALE * camera.zoom)
    for index, segment in enumerate(segments):
        if segment.center is None:
            _draw_straight(straight_image, camera, segment, index, len(segments), thickness)
        else:
            _draw_bend(bend_image, camera, segment, thickness)


def _draw_straight(image, camera, segment, index, segment_count, thickness):
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
    image.clip_composite_draw(
        source_left, 0, source_width, image.h, angle, "",
        (x1 + x2) / 2, (y1 + y2) / 2, width, thickness,
    )


def _draw_bend(image, camera, segment, thickness):
    cx, cy = segment.center
    sx, sy = map(round, camera.world_to_screen(cx, cy))
    sign_x = -1 if min(segment.start[0], segment.end[0]) < cx else 1
    sign_y = 1 if max(segment.start[1], segment.end[1]) > cy else -1
    # Snap the centerline's endpoints the same way as the adjoining straights.
    end_x, end_y = map(round, camera.world_to_screen(
        cx + sign_x * segment.radius, cy + sign_y * segment.radius,
    ))
    radius_x = abs(end_x - sx)
    radius_y = abs(end_y - sy)
    half_width = thickness / 2
    art_half_width = image.w - BEND_ART_RADIUS
    vertices = []
    # Map the bend's inner and outer edges separately so only the radius changes.
    for dx, dy in BEND_DIRECTIONS:
        for edge in (-1, 1):
            offset = edge * half_width
            art_radius = BEND_ART_RADIUS + edge * art_half_width
            vertices.append(pico.SDL_Vertex(
                (sx + sign_x * (radius_x + offset) * dx,
                 pico.canvas_height - (sy + sign_y * (radius_y + offset) * dy)),
                (255, 255, 255, 255),
                (art_radius * dx / image.w, art_radius * dy / image.h),
            ))
    geometry = (pico.SDL_Vertex * len(vertices))(*vertices)
    pico.SDL_RenderGeometry(pico.renderer, image.texture, geometry, len(vertices),
                            BEND_TRIANGLES, len(BEND_TRIANGLES))

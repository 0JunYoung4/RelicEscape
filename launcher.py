"""Aim a mounted crossbow and trace the relic's ballistic path."""

from dataclasses import dataclass
from math import atan2, ceil, cos, degrees, hypot, radians, sin

from pico2d import pico2d as pico

from player import STANDING_HITBOX_HEIGHT, STANDING_HITBOX_WIDTH, WORLD_MARGIN


AIM_RADIUS = 90
MAX_ELEVATION = radians(55)
LAUNCH_SPEED = 1500
FLIGHT_GRAVITY = 950
FLIGHT_RADIUS = STANDING_HITBOX_WIDTH / 2
# The neutral socket sits at standing torso height. Coordinates are in the source crops.
ART_SCALE = STANDING_HITBOX_HEIGHT / (2 * 462)
BASE_WIDTH, BASE_HEIGHT = 873, 310
BASE_PIVOT_X, BASE_PIVOT_Y = 436, -14
BODY_WIDTH, BODY_HEIGHT = 807, 512
BODY_PIVOT_X, BODY_PIVOT_Y = 338, 404
SOCKET = (83, 266)
MUZZLE = (771, 266)


@dataclass
class RelicFlight:
    x: float
    y: float
    vx: float
    vy: float
    landed: bool = False

    @property
    def position(self):
        return self.x, self.y

    def return_pose(self, ground_y):
        offset = FLIGHT_RADIUS if self.landed else STANDING_HITBOX_HEIGHT / 2
        return self.x, max(ground_y, self.y - offset), 0.0

    def update(self, delta_time, terrain, ground_y, world_width):
        # Small steps keep the two-axis collision checks stable at low frame rates.
        steps = max(1, ceil(delta_time * 120))
        step = delta_time / steps
        for _ in range(steps):
            if self.landed:
                break
            self._move(step, terrain, ground_y, world_width)

    def _move(self, time, terrain, ground_y, world_width):
        next_y = self.y + self.vy * time - FLIGHT_GRAVITY * time ** 2 / 2
        self.vy -= FLIGHT_GRAVITY * time
        target_x = self.x + self.vx * time
        next_x = max(WORLD_MARGIN, min(world_width - WORLD_MARGIN, target_x))
        for left, bottom, right, top in terrain:
            if self.y + FLIGHT_RADIUS <= bottom or self.y - FLIGHT_RADIUS >= top:
                continue
            if self.vx > 0 and self.x <= left - FLIGHT_RADIUS <= next_x:
                next_x = left - FLIGHT_RADIUS
            elif self.vx < 0 and next_x <= right + FLIGHT_RADIUS <= self.x:
                next_x = right + FLIGHT_RADIUS
        if next_x != target_x:
            self.vx = 0.0
        self.x = next_x

        if next_y <= self.y:
            floor = ground_y + FLIGHT_RADIUS
            for left, _, right, top in terrain:
                if left < self.x + FLIGHT_RADIUS and self.x - FLIGHT_RADIUS < right:
                    if next_y <= top + FLIGHT_RADIUS <= self.y:
                        floor = max(floor, top + FLIGHT_RADIUS)
            if next_y <= floor:
                self.y = floor
                self.vx = self.vy = 0.0
                self.landed = True
                return
        else:
            for left, bottom, right, _ in terrain:
                if left < self.x + FLIGHT_RADIUS and self.x - FLIGHT_RADIUS < right:
                    if self.y <= bottom - FLIGHT_RADIUS <= next_y:
                        next_y = bottom - FLIGHT_RADIUS
                        self.vy = 0.0
        self.y = next_y


class Crossbow:
    def __init__(self, x, ground_y, base_image, body_image):
        self.x = x
        self.ground_y = ground_y
        self.y = ground_y + (BASE_HEIGHT - BASE_PIVOT_Y) * ART_SCALE
        self.base_image = base_image
        self.body_image = body_image
        self.angle = 0.0
        self.facing = 1
        self.aiming = False
        self.flight = None

    def _body_point(self, point):
        dx = (point[0] - BODY_PIVOT_X) * ART_SCALE
        dy = (BODY_PIVOT_Y - point[1]) * ART_SCALE
        sine, cosine = sin(self.angle), cos(self.angle)
        return self.x + self.facing * (dx * cosine - dy * sine), self.y + dx * sine + dy * cosine

    @property
    def socket_position(self):
        return self._body_point(SOCKET)

    @property
    def relic_position(self):
        if self.aiming:
            return self.socket_position
        return self.flight.position if self.flight is not None else None

    def can_aim(self, player):
        x, y = self.socket_position
        _, bottom, _, top = player.get_hitbox()
        return player.grounded and hypot(x - player.x, y - (bottom + top) / 2) <= AIM_RADIUS

    def aim_toward(self, x, y):
        dx = x - self.x
        if dx:
            self.facing = 1 if dx > 0 else -1
        self.angle = max(0.0, min(MAX_ELEVATION, atan2(y - self.y, abs(dx))))

    def _new_flight(self):
        x, y = self._body_point(MUZZLE)
        return RelicFlight(x, y, self.facing * LAUNCH_SPEED * cos(self.angle), LAUNCH_SPEED * sin(self.angle))

    def fire(self):
        self.flight = self._new_flight()
        self.aiming = False

    def trajectory(self, terrain, world_width):
        preview = self._new_flight()
        for _ in range(34):
            preview.update(0.085, terrain, self.ground_y, world_width)
            yield preview.position
            if preview.landed:
                break

    def draw(self, camera, screen_height):
        x, ground = camera.world_to_screen(self.x, self.ground_y)
        scale = ART_SCALE * camera.zoom
        self.base_image.draw_to_origin(x - BASE_PIVOT_X * scale, ground, BASE_WIDTH * scale, BASE_HEIGHT * scale)

        x, y = camera.world_to_screen(self.x, self.y)
        pivot_x = BODY_PIVOT_X if self.facing > 0 else BODY_WIDTH - BODY_PIVOT_X
        pivot = pico.SDL_FPoint(pivot_x * scale, BODY_PIVOT_Y * scale)
        bounds = pico.SDL_FRect(x - pivot.x, screen_height - y - pivot.y, BODY_WIDTH * scale, BODY_HEIGHT * scale)
        flip = pico.SDL_FLIP_NONE if self.facing > 0 else pico.SDL_FLIP_HORIZONTAL
        pico.SDL_RenderCopyExF(
            pico.renderer, self.body_image.texture, None, bounds,
            -self.facing * degrees(self.angle), pivot, flip,
        )

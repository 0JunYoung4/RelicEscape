"""The chamber beneath the combat room, with the recessed relic lift."""

from math import exp, hypot

from pico2d import pico2d as pico

from lower_route_a_art import LowerRouteAArt
from pillbug import Pillbug
from player import ASSET_ROOT, STANDING_HITBOX_HEIGHT, TAKEOFF_FRAME_DURATION
from rail import (RAIL_ART_SCALE, RAIL_BEND_IMAGE, RAIL_CARRIAGE_IMAGE, RAIL_IMAGE,
                  RailCarriage, RailSegment, draw_rail)


ART_ZOOM = .4
ART_WIDTH, ART_HEIGHT = 2172, 724
WIDTH, HEIGHT = ART_WIDTH / ART_ZOOM, ART_HEIGHT / ART_ZOOM
HOLE_PIXEL = (1950, 90)
SHADOW_BOUNDS = (1808, -8, 480, 300)


def world(x, y):
    """Convert the authored panorama's top-left pixels to world coordinates."""
    return x / ART_ZOOM, (ART_HEIGHT - y) / ART_ZOOM


def solid(left, top, right, bottom):
    return left / ART_ZOOM, world(0, bottom)[1], right / ART_ZOOM, world(0, top)[1]


GROUND_Y = world(0, 624)[1]
EXIT_LEDGE = solid(0, 369, 851, 437)
ENTRY_LEDGE = solid(1554, 407, ART_WIDTH, 624)
ENTRY_STEP = solid(1467, 462, 1554, 624)
RECESS_BACK = solid(0, 437, 507, 624)
# Set the rock undersides back in layers so none becomes a foothold.
OVERHANG = (solid(495, 437, 640, 452), solid(670, 437, 805, 466))
CEILING_LIPS = (solid(0, 0, 1908, 120), solid(2000, 0, ART_WIDTH, 120))
TERRAIN = (EXIT_LEDGE, ENTRY_LEDGE, ENTRY_STEP, RECESS_BACK, *OVERHANG, *CEILING_LIPS)
ENTRY_X, ENTRY_Y = world(1950, 63)
BUTTON_LEFT, BUTTON_RIGHT = 1103 / ART_ZOOM, 1170 / ART_ZOOM
BUTTON_CENTER = world(1137, 616)
BUTTON_PILLBUGS = ((1000 / ART_ZOOM, 1), (1285 / ART_ZOOM, -1))
RECOVERY = world(1434, 572)
RECOVERY_RADIUS = 108
LOWER_DOCK = world(725, 594)
UPPER_DOCK = world(605, 329)
RAIL_X = 975 / ART_ZOOM
LIFT_BEND_RADIUS = 72
SEAL_GATE = solid(414, 120, 488, 369)
SEAL_LOWER_PLATE = (935 / ART_ZOOM, GROUND_Y)
SEAL_UPPER_PLATE = (753 / ART_ZOOM, EXIT_LEDGE[3])
SEAL_PLATE_HALF_WIDTH = 64
SEAL_WINDOW = 3.0
SEAL_OPEN_DURATION = .52
SEAL_DIM = (73, 144, 151)
SEAL_LIT = (130, 246, 222)


def lift_path():
    left, bottom = LOWER_DOCK
    exit_x, top = UPPER_DOCK
    radius = LIFT_BEND_RADIUS
    lower_center = RAIL_X - radius, bottom + radius
    upper_center = RAIL_X - radius, top - radius
    return (
        RailSegment((left, bottom), (lower_center[0], bottom)),
        RailSegment((lower_center[0], bottom), (RAIL_X, lower_center[1]), lower_center),
        RailSegment((RAIL_X, lower_center[1]), (RAIL_X, upper_center[1])),
        RailSegment((RAIL_X, upper_center[1]), (upper_center[0], top), upper_center),
        RailSegment((upper_center[0], top), (exit_x, top)),
    )


class LowerRouteA:
    def __init__(self, origin=(0, 0), *, seal_open=False):
        self.origin = origin
        self.world_width = origin[0] + WIDTH
        self.camera_bottom, self.camera_top = origin[1], origin[1] + HEIGHT
        self.ground_y = GROUND_Y + origin[1]
        self.terrain = tuple(self.bounds(box) for box in TERRAIN)
        self.scenery = LowerRouteAArt(origin)
        self.shadow = pico.load_image(str(ASSET_ROOT / "terrain/lower-route-a-ceiling-shadow-v2.png"))
        self.seal_stone = pico.load_image(str(ASSET_ROOT / "terrain/moss-combat-door-blocker-v1.png"))
        self.rail = pico.load_image(str(RAIL_IMAGE))
        self.bend = pico.load_image(str(RAIL_BEND_IMAGE))
        self.mount = pico.load_image(str(RAIL_CARRIAGE_IMAGE))
        self.path = tuple(
            RailSegment(self.point(*segment.start), self.point(*segment.end),
                        self.point(*segment.center) if segment.center is not None else None)
            for segment in lift_path()
        )
        self.carriage = RailCarriage(self.path, self.mount.w * RAIL_ART_SCALE, self.mount.h * RAIL_ART_SCALE)
        self.pillbug = Pillbug.on_platform(self.bounds(solid(1615, 407, 1850, 624)))
        self.button_pillbugs = ()
        self.powered = False
        self.shadow_opacity = 1.0
        self.seal_deadline = 0.0
        self.seal_remaining = 0.0
        self.seal_lower_pressed = False
        self.seal_opened_at = None
        self.seal_height = 0 if seal_open else SEAL_GATE[3] - SEAL_GATE[1]

    def point(self, x, y):
        return x + self.origin[0], y + self.origin[1]

    def bounds(self, box):
        left, bottom, right, top = box
        return (*self.point(left, bottom), *self.point(right, top))

    @property
    def seal_unlocked(self):
        return self.seal_opened_at is not None or self.seal_height == 0

    @property
    def seal_barrier(self):
        if self.seal_height > 0:
            left, bottom, right, _ = SEAL_GATE
            return self.bounds((left, bottom, right, bottom + self.seal_height))
        return None

    @property
    def enemies(self):
        return (self.pillbug, *self.button_pillbugs)

    @property
    def mounted_carriage(self):
        return self.carriage if self.carriage.relic_mounted else None

    def enter(self, player, *, shaft_offset=None):
        player.world_width = self.world_width
        player.terrain = self.terrain
        player.ground_y = self.ground_y
        if shaft_offset is None:
            player.recover_at(*self.point(ENTRY_X, ENTRY_LEDGE[3]), 0)
        else:
            fall_speed = player.vertical_speed
            player.recover_at(*self.point(ENTRY_X + shaft_offset, ENTRY_Y), 0)
            player.vertical_speed = min(0, fall_speed)
            player.state = "jump"
            player.animation_time = TAKEOFF_FRAME_DURATION
        player.facing = -1

    def follow_camera(self, player, camera, screen_height):
        camera.follow(player.x)
        camera.y = self.camera_y(player.y, screen_height / camera.zoom)

    def camera_y(self, player_y, view_height):
        target = player_y - view_height * .24
        return max(self.camera_bottom, min(self.camera_top - view_height, target))

    def can_reset(self, player):
        return (player.grounded and player.y == self.ground_y
                and abs(player.x - self.point(*RECOVERY)[0]) <= RECOVERY_RADIUS
                and (self.carriage.distance > 0 or self.carriage.relic_mounted))

    def can_mount(self, player, relic_placed):
        return self.powered and self.carriage.can_mount(player, relic_placed)

    def prompt(self, player, relic_placed):
        if self.can_reset(player):
            return self.point(*RECOVERY), False
        carriage = self.carriage
        if self.can_mount(player, relic_placed):
            return carriage.position, False
        if carriage.relic_mounted:
            if carriage.distance == 0 and abs(player.x - carriage.position[0]) <= 160:
                return carriage.position, True
            return (player.x, player.y + STANDING_HITBOX_HEIGHT), False
        if not self.seal_unlocked and not relic_placed and self.on_seal_plate(player, SEAL_UPPER_PLATE):
            x, y = self.point(*SEAL_UPPER_PLATE)
            return (x, y + STANDING_HITBOX_HEIGHT), False
        return None

    def on_seal_plate(self, player, plate):
        x, y = self.point(*plate)
        return player.grounded and player.y == y and abs(player.x - x) <= SEAL_PLATE_HALF_WIDTH

    def update_seal(self, player, now):
        """Return whether the shared collision needs to follow the moving door."""
        if self.seal_height == 0:
            return False
        if self.seal_opened_at is not None:
            previous_height = self.seal_height
            fraction = min(1.0, (now - self.seal_opened_at) / SEAL_OPEN_DURATION)
            self.seal_height = (SEAL_GATE[3] - SEAL_GATE[1]) * (1 - fraction)
            return self.seal_height != previous_height

        on_lower = self.on_seal_plate(player, SEAL_LOWER_PLATE)
        if on_lower and not self.seal_lower_pressed and now >= self.seal_deadline:
            self.seal_deadline = now + SEAL_WINDOW
        self.seal_lower_pressed = on_lower
        self.seal_remaining = max(0.0, self.seal_deadline - now)
        if self.seal_remaining and self.on_seal_plate(player, SEAL_UPPER_PLATE):
            self.seal_opened_at = now
            self.seal_remaining = 0.0
        return False

    def use_relic(self, player, *, relic_placed):
        """Return (handled, destination), deferring the normal anchor when appropriate."""
        carriage = self.carriage
        if self.can_reset(player):
            carriage.direction = 0
            carriage.distance = 0
            carriage.relic_mounted = False
            return True, None
        if carriage.relic_mounted:
            x, y = carriage.position
            return True, (x, y - STANDING_HITBOX_HEIGHT / 2, 0.0)
        if self.can_mount(player, relic_placed):
            carriage.relic_mounted = True
            return True, None
        return False, None

    def update(self, player, dt):
        left, bottom, right, _ = player.get_hitbox()
        if (not self.powered and player.grounded and bottom == self.ground_y
                and right > BUTTON_LEFT + self.origin[0] and left < BUTTON_RIGHT + self.origin[0]):
            self.powered = True
            pit = self.bounds((RECESS_BACK[2], 0, ENTRY_STEP[0], GROUND_Y))
            bugs = []
            for x, direction in BUTTON_PILLBUGS:
                bug = Pillbug.on_platform(pit)
                bug.x, bug.direction = x + self.origin[0], direction
                bug.begin_emergence()
                bugs.append(bug)
            self.button_pillbugs = tuple(bugs)
        if self.carriage.relic_mounted:
            self.carriage.check_attack(player)
        # An empty carriage can finish an already-started trip after an early teleport.
        self.carriage.move(dt)

    def update_shadow(self, player, dt):
        self.scenery.time += dt
        x, y = self.point(*world(*HOLE_PIXEL))
        distance = hypot(player.x - x, player.y + STANDING_HITBOX_HEIGHT / 2 - y) * ART_ZOOM
        proximity = min(1.0, max(0.0, (distance - 293) / 118))
        target = proximity * proximity * (3 - 2 * proximity)
        self.shadow_opacity += (target - self.shadow_opacity) * (1 - exp(-14 * dt))

    def draw(self, camera):
        self.scenery.draw_background(camera)
        self.scenery.draw_terrain(camera)
        self.draw_seal(camera)
        self.scenery.draw_gate_collar(camera)
        if self.powered:
            x, y = camera.world_to_screen(*self.point(*BUTTON_CENTER))
            pico.draw_line(x - 29 * camera.zoom, y, x + 29 * camera.zoom, y, 91, 215, 222)
        rail_tint = (214, 238, 241) if self.powered else (79, 91, 99)
        for piece in (self.rail, self.bend):
            pico.SDL_SetTextureColorMod(piece.texture, *rail_tint)
        try:
            draw_rail(self.rail, self.bend, camera, self.path)
        finally:
            for piece in (self.rail, self.bend):
                pico.SDL_SetTextureColorMod(piece.texture, 255, 255, 255)
        scale = RAIL_ART_SCALE * camera.zoom
        self.mount.draw(*camera.world_to_screen(*self.carriage.position),
                        self.mount.w * scale, self.mount.h * scale)

    def draw_seal(self, camera):
        left, bottom, right, top = SEAL_GATE
        x, y = camera.world_to_screen(*self.point(left, bottom))
        zoom = camera.zoom
        width = (right - left) * zoom
        lintel_y = y + (top - bottom) * zoom
        housing_height = HEIGHT - top
        active = self.seal_remaining > 0
        color = SEAL_LIT if active or self.seal_unlocked else SEAL_DIM
        image = self.seal_stone
        housing_rows = round(image.h * housing_height / (top - bottom))
        image.clip_draw_to_origin(0, 0, image.w, housing_rows, x - 5, lintel_y,
                                  width + 10, housing_height * zoom)
        if self.seal_height > 0:
            visible = max(1, round(image.h * self.seal_height / (top - bottom)))
            image.clip_draw_to_origin(0, image.h - visible, image.w, visible, x, y,
                                      width, max(1, self.seal_height * zoom))
        # Inlaid lintel and threshold keep the gate's position readable after it sinks.
        for edge in (y, lintel_y):
            pico.draw_rectangle(x - 5, edge - 3, x + width + 5, edge + 3, 28, 50, 53, filled=True)
            pico.draw_line(x, edge, x + width, edge, *color)

        for number, plate in enumerate((SEAL_LOWER_PLATE, SEAL_UPPER_PLATE), start=1):
            x, y = camera.world_to_screen(*self.point(*plate))
            half_width = SEAL_PLATE_HALF_WIDTH * zoom
            pico.draw_rectangle(x - half_width, y - 2, x + half_width, y + 4, 25, 42, 45, filled=True)
            pico.draw_rectangle(x - half_width + 4, y + 1, x + half_width - 4, y + 7, 43, 69, 71, filled=True)
            pico.draw_line(x - half_width + 4, y + 7, x + half_width - 4, y + 7, *color)
            for index in range(number):
                lamp_x = x + (index - (number - 1) / 2) * 12
                pico.draw_rectangle(lamp_x - 2, y + 2, lamp_x + 2, y + 5, *color, filled=True)

        if active:
            x, y = camera.world_to_screen(*self.point(*SEAL_LOWER_PLATE))
            y += (STANDING_HITBOX_HEIGHT + 55) * zoom
            for index in range(3):
                left = x - 27 + index * 19
                pico.draw_rectangle(left, y, left + 16, y + 4, 24, 56, 61, filled=True)
                fraction = min(1.0, self.seal_remaining - index)
                if fraction > 0:
                    pico.draw_rectangle(left, y, left + 16 * fraction, y + 4, *SEAL_LIT, filled=True)

    def draw_foreground(self, camera):
        self.scenery.draw_foreground(camera)
        x, y, width, height = SHADOW_BOUNDS
        pico.SDL_SetTextureAlphaMod(self.shadow.texture, round(255 * self.shadow_opacity))
        self.shadow.draw_to_origin(*camera.world_to_screen(*self.point(*world(x, y + height))),
                                   width / ART_ZOOM * camera.zoom, height / ART_ZOOM * camera.zoom)

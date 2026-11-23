"""The chamber beneath the combat room, with the recessed relic lift."""

from math import exp, hypot

from pico2d import pico2d as pico

from pillbug import Pillbug
from player import ASSET_ROOT, STANDING_HITBOX_HEIGHT, TAKEOFF_FRAME_DURATION
from rail import (BEND_ART_RADIUS, RAIL_ART_SCALE, RAIL_BEND_IMAGE, RAIL_CARRIAGE_IMAGE,
                  RAIL_IMAGE, RailCarriage, RailSegment, draw_rail)


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


def lift_path():
    left, bottom = LOWER_DOCK
    exit_x, top = UPPER_DOCK
    radius = BEND_ART_RADIUS
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
    def __init__(self):
        self.plate = pico.load_image(str(ASSET_ROOT / "concepts/map1-lower-route-a-v3-plate.png"))
        self.shadow = pico.load_image(str(ASSET_ROOT / "terrain/lower-route-a-ceiling-shadow-v2.png"))
        self.rail = pico.load_image(str(RAIL_IMAGE))
        self.bend = pico.load_image(str(RAIL_BEND_IMAGE))
        self.mount = pico.load_image(str(RAIL_CARRIAGE_IMAGE))
        self.path = lift_path()
        self.carriage = RailCarriage(self.path, self.mount.w * RAIL_ART_SCALE, self.mount.h * RAIL_ART_SCALE)
        self.pillbug = Pillbug.on_platform(solid(1615, 407, 1850, 624))
        self.button_pillbugs = ()
        self.powered = False
        self.shadow_opacity = 1.0

    @property
    def enemies(self):
        return (self.pillbug, *self.button_pillbugs)

    def enter(self, player, *, shaft_offset=None):
        player.world_width = WIDTH
        player.terrain = TERRAIN
        player.ground_y = GROUND_Y
        if shaft_offset is None:
            player.recover_at(ENTRY_X, ENTRY_LEDGE[3], 0)
        else:
            fall_speed = player.vertical_speed
            player.recover_at(ENTRY_X + shaft_offset, ENTRY_Y, 0)
            player.vertical_speed = min(0, fall_speed)
            player.state = "jump"
            player.animation_time = TAKEOFF_FRAME_DURATION
        player.facing = -1

    def follow_camera(self, player, camera, screen_height):
        camera.follow(player.x)
        view_height = screen_height / camera.zoom
        target = player.y - view_height * .24
        camera.y = max(0, min(max(0, HEIGHT - view_height), target))

    def can_reset(self, player):
        return (player.grounded and player.y == GROUND_Y
                and abs(player.x - RECOVERY[0]) <= RECOVERY_RADIUS
                and (self.carriage.distance > 0 or self.carriage.relic_mounted))

    def can_mount(self, player, relic_placed):
        return self.powered and self.carriage.can_mount(player, relic_placed)

    def prompt(self, player, relic_placed):
        if self.can_reset(player):
            return RECOVERY, False
        carriage = self.carriage
        if self.can_mount(player, relic_placed):
            return carriage.position, False
        if carriage.relic_mounted:
            if carriage.distance == 0 and abs(player.x - LOWER_DOCK[0]) <= 160:
                return LOWER_DOCK, True
            return (player.x, player.y + STANDING_HITBOX_HEIGHT), False
        return None

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
        if (not self.powered and player.grounded and bottom == GROUND_Y
                and right > BUTTON_LEFT and left < BUTTON_RIGHT):
            self.powered = True
            pit = (RECESS_BACK[2], 0, ENTRY_STEP[0], GROUND_Y)
            bugs = []
            for x, direction in BUTTON_PILLBUGS:
                bug = Pillbug.on_platform(pit)
                bug.x, bug.direction = x, direction
                bug.begin_emergence()
                bugs.append(bug)
            self.button_pillbugs = tuple(bugs)
        if self.carriage.relic_mounted:
            self.carriage.check_attack(player)
        # An empty carriage can finish an already-started trip after an early teleport.
        self.carriage.move(dt)

    def update_shadow(self, player, dt):
        x, y = world(*HOLE_PIXEL)
        distance = hypot(player.x - x, player.y + STANDING_HITBOX_HEIGHT / 2 - y) * ART_ZOOM
        proximity = min(1.0, max(0.0, (distance - 293) / 118))
        target = proximity * proximity * (3 - 2 * proximity)
        self.shadow_opacity += (target - self.shadow_opacity) * (1 - exp(-14 * dt))

    def draw(self, camera):
        self.plate.draw_to_origin(*camera.world_to_screen(0, 0), WIDTH * camera.zoom, HEIGHT * camera.zoom)
        if self.powered:
            x, y = camera.world_to_screen(*BUTTON_CENTER)
            pico.draw_line(x - 29 * camera.zoom, y, x + 29 * camera.zoom, y, 91, 215, 222)
        if not self.powered:
            for piece in (self.rail, self.bend):
                pico.SDL_SetTextureColorMod(piece.texture, 79, 91, 99)
        try:
            draw_rail(self.rail, self.bend, camera, self.path)
        finally:
            if not self.powered:
                for piece in (self.rail, self.bend):
                    pico.SDL_SetTextureColorMod(piece.texture, 255, 255, 255)
        scale = RAIL_ART_SCALE * camera.zoom
        self.mount.draw(*camera.world_to_screen(*self.carriage.position),
                        self.mount.w * scale, self.mount.h * scale)

    def draw_foreground(self, camera):
        x, y, width, height = SHADOW_BOUNDS
        pico.SDL_SetTextureAlphaMod(self.shadow.texture, round(255 * self.shadow_opacity))
        self.shadow.draw_to_origin(*camera.world_to_screen(*world(x, y + height)),
                                   width / ART_ZOOM * camera.zoom, height / ART_ZOOM * camera.zoom)

"""The spike gorge, two curved relic rails, and three combat ledges."""

from math import hypot

from pico2d import pico2d as pico

from health import SpikeBed
from lower_route_b_art import LowerRouteBArt
from lower_route_b_layout import (A_ENTRY, BOTTOM, C_APPROACH_LEDGE, C_PASSAGE, PILLBUG_LEDGE, RAIL_ONE, RAIL_TWO,
                                  RIGHT_WALL, SECRET_FLOOR, SECRET_FLOOR_Y, SECRET_LEFT_WALL, SECRET_PASSAGE,
                                  SECRET_RAIL_DISTANCE, SECRET_RAIL_DOCK, SECRET_RELIC_X, SHIELD_LEDGE,
                                  STONE_SHELVES, STONE_SURFACE, TERRAIN, THORN_WALL_CROP, THORN_WALL_PROFILE,
                                  THORN_WALLS, TOP, WIDTH)
from pillbug import Pillbug
from player import STANDING_HITBOX_HEIGHT
from rail import (RAIL_ART_SCALE, RAIL_BEND_IMAGE, RAIL_CARRIAGE_IMAGE, RAIL_IMAGE, RAIL_MOUNT_RADIUS,
                  RailCarriage, draw_rail)
from shield_soldier import BASH_DAMAGE, ShieldSoldier
from route_camera import B_CAMERA_HEADROOM, camera_y


SPAWN = (4780, A_ENTRY[3], 0)


def _thorn_wall_spikes(bounds, hanging):
    left, bottom, right, top = bounds
    profile = THORN_WALL_PROFILE
    source_width = THORN_WALL_CROP[2] - THORN_WALL_CROP[0]
    scale_x = (right - left) / source_width
    height = (top - bottom) / len(profile)
    for index, (edge_left, edge_right) in enumerate(profile):
        if hanging:
            edge_left, edge_right = source_width - edge_right, source_width - edge_left
        row = index if hanging else len(profile) - 1 - index
        base = bottom + row * height
        visible_base = max(base, STONE_SURFACE)
        yield SpikeBed(left + edge_left * scale_x, left + edge_right * scale_x,
                       visible_base, height=base + height - visible_base)


SPIKES = tuple(spikes for wall, hanging in THORN_WALLS for spikes in _thorn_wall_spikes(wall, hanging))
# Keep the painted shelf cores solid and join the top of the hanging wall to the roof.
PLAY_TERRAIN = (*TERRAIN, *STONE_SHELVES, SECRET_FLOOR, SECRET_LEFT_WALL,
                (18, 360, 1110, 500), (1000, 140, 1315, 495),
                (2265, 332, 2860, 495), (4475, -45, WIDTH, 90),
                (3085, -16, 3615, 85), (3160, -145, 3525, -16),
                (3165, -350, 3520, -145),
                (RIGHT_WALL[0], RIGHT_WALL[3], RIGHT_WALL[2] + 50, 1270),
                (0, 1270, WIDTH, TOP))
SAFE_POSES = (
    (A_ENTRY, SPAWN),
    (PILLBUG_LEDGE, (3450, PILLBUG_LEDGE[3], 0)),
    (SHIELD_LEDGE, (2775, SHIELD_LEDGE[3], 0)),
    (C_APPROACH_LEDGE, (1160, C_APPROACH_LEDGE[3], 0)),
    (C_PASSAGE, (480, C_PASSAGE[3], 0)),
)


class LowerRouteB:
    camera_bottom, camera_top = BOTTOM, TOP + B_CAMERA_HEADROOM
    camera_right = WIDTH

    def __init__(self):
        self.art = LowerRouteBArt()
        self.rail = pico.load_image(str(RAIL_IMAGE))
        self.bend = pico.load_image(str(RAIL_BEND_IMAGE))
        self.mount = pico.load_image(str(RAIL_CARRIAGE_IMAGE))
        self.carriages = tuple(RailCarriage(path, self.mount.w * RAIL_ART_SCALE, self.mount.h * RAIL_ART_SCALE)
                               for path in (RAIL_ONE, RAIL_TWO))
        for carriage in self.carriages:
            self.reset_carriage(carriage)
        self.rail_attempt = None
        self.return_docks_open = False
        self.safe_pose = SPAWN
        self.secret_revealed = False
        self.secret_relic_collected = False
        # Leave the right edge of each ledge open for landing.
        self.pillbug = Pillbug.on_platform((3060, 85, 3380, PILLBUG_LEDGE[3]))
        self.pillbug.x = 3265
        self.shield = ShieldSoldier(2500, SHIELD_LEDGE[3], 2420, 2600,
                                   support_edges=(SHIELD_LEDGE[0], SHIELD_LEDGE[2]))
        self.fights = (
            (self.pillbug, 3060, 3410),
            (self.shield, 2350, 2670),
        )
        self.awake = set()

    @property
    def enemies(self):
        return tuple(enemy for enemy, _, _ in self.fights if enemy in self.awake)

    @property
    def mounted_carriage(self):
        if self.rail_attempt is not None and self.rail_attempt.relic_mounted:
            return self.rail_attempt
        return None

    @staticmethod
    def reset_carriage(carriage):
        carriage.distance = carriage.length
        carriage.direction = 0
        carriage.relic_mounted = False
        carriage.hit_by_swing = False

    def enter(self, player):
        player.world_width = WIDTH
        player.terrain = PLAY_TERRAIN
        player.ground_y = BOTTOM
        player.recover_at(*SPAWN)
        player.facing = -1

    def follow_camera(self, player, camera, screen_height, dt=None):
        camera.follow_route(player, screen_height, (self.camera_bottom, self.camera_top), dt)

    @staticmethod
    def camera_y(player_y, view_height):
        return camera_y(player_y, view_height, LowerRouteB.camera_bottom, LowerRouteB.camera_top)

    def nearby_dock(self, player, relic_placed):
        if relic_placed or not player.grounded:
            return None
        if player.y == SECRET_FLOOR_Y and abs(player.x - SECRET_RAIL_DOCK[0]) <= 64:
            return self.carriages[1], SECRET_RAIL_DISTANCE, SECRET_RAIL_DOCK
        _, bottom, _, top = player.get_hitbox()
        for carriage in self.carriages:
            x, y = carriage.segments[-1].end
            if hypot(player.x - x, (bottom + top) / 2 - y) <= RAIL_MOUNT_RADIUS:
                return carriage, carriage.length, (x, y)
            if self.return_docks_open:
                x, y = carriage.segments[0].start
                if hypot(player.x - x, (bottom + top) / 2 - y) <= RAIL_MOUNT_RADIUS:
                    return carriage, 0, (x, y)
        return None

    def use_relic(self, player, *, relic_placed):
        if self.mounted_carriage is not None:
            x, y = self.mounted_carriage.position
            return True, (x, y - STANDING_HITBOX_HEIGHT / 2, 0.0)
        dock = self.nearby_dock(player, relic_placed)
        if dock is None:
            return False, None
        carriage, distance, _ = dock
        self.reset_carriage(carriage)
        carriage.distance = distance
        carriage.relic_mounted = True
        self.rail_attempt = carriage
        return True, None

    def prompt(self, player, relic_placed):
        carriage = self.mounted_carriage
        if carriage is not None:
            x, y = carriage.segments[-1].end
            if carriage.distance == carriage.length and abs(player.x - x) <= 160:
                return (x, y), True
            if self.return_docks_open and carriage.distance == 0:
                x, y = carriage.segments[0].start
                if abs(player.x - x) <= 160:
                    return (x, y), True
            return (player.x, player.y + STANDING_HITBOX_HEIGHT), False
        dock = self.nearby_dock(player, relic_placed)
        if dock is not None:
            return dock[2], False
        return None

    def update(self, player, dt):
        mounted = self.mounted_carriage
        if mounted is not None:
            mounted.check_attack(player)
        for carriage in self.carriages:
            carriage.move(dt)
        if player.grounded and player.y == SECRET_FLOOR_Y and SECRET_PASSAGE[0] < player.x < SECRET_PASSAGE[2]:
            self.secret_revealed = True
            if abs(player.x - SECRET_RELIC_X) <= 45:
                self.secret_relic_collected = True

    def check_spikes(self, player, health, now):
        if player.grounded and not health.recovering(now):
            for (left, _, right, top), pose in SAFE_POSES:
                if player.y == top and left <= player.x < right:
                    self.safe_pose = pose
                    if self.mounted_carriage is None:
                        self.rail_attempt = None
                    break
        hit = health.check_spikes(player, SPIKES, now)
        health.safe_pose = self.safe_pose
        if hit and self.rail_attempt is not None:
            self.reset_carriage(self.rail_attempt)
            self.rail_attempt = None
        return hit

    def enemy_target(self, enemy, player):
        for actor, left, right in self.fights:
            if actor is enemy and left <= player.x < right and actor.floor_y <= player.y < actor.floor_y + 235:
                return player.get_hitbox()
        # A rolling pillbug still needs a box to test against while it finishes its attack.
        return (-2000, BOTTOM, -1900, BOTTOM + 140) if enemy is self.pillbug else ()

    def activate_enemies(self, player):
        if player.grounded:
            for enemy, left, right in self.fights:
                if left <= player.x < right and player.y == enemy.floor_y:
                    self.awake.add(enemy)

    def check_enemy_attack(self, player, health, now):
        target = self.enemy_target(self.shield, player)
        if self.shield in self.awake and target:
            hit = self.shield.bash_contact(target)
            if hit is not None:
                health.take_enemy_hit(hit, now, BASH_DAMAGE)

    def draw(self, camera, screen_height, *, passage_left=C_PASSAGE[0], backdrop_right=WIDTH, draw_entry=True,
             draw_depth=True):
        self.art.draw(camera, screen_height, passage_left=passage_left, secret_revealed=self.secret_revealed,
                      secret_relic_collected=self.secret_relic_collected, backdrop_right=backdrop_right,
                      draw_entry=draw_entry, draw_depth=draw_depth)
        scale = RAIL_ART_SCALE * camera.zoom
        for piece in (self.rail, self.bend):
            pico.SDL_SetTextureColorMod(piece.texture, 214, 238, 241)
        try:
            for carriage in self.carriages:
                draw_rail(self.rail, self.bend, camera, carriage.segments)
                self.mount.draw(*camera.world_to_screen(*carriage.position),
                                self.mount.w * scale, self.mount.h * scale)
        finally:
            for piece in (self.rail, self.bend):
                pico.SDL_SetTextureColorMod(piece.texture, 255, 255, 255)

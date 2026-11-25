"""The spike gorge, two curved relic rails, and three combat ledges."""

from math import hypot

from pico2d import pico2d as pico

from health import SpikeBed
from lower_route_b_art import LowerRouteBArt
from lower_route_b_layout import (A_ENTRY, BOTTOM, C_APPROACH_LEDGE, C_PASSAGE, PILLBUG_LEDGE,
                                  HIDDEN_DOCK, HIDDEN_DOCK_DISTANCE, HIDDEN_LEDGE, RAIL_ONE, RAIL_TWO,
                                  RIGHT_WALL, SHIELD_LEDGE, SPIKE_SHELVES, TERRAIN, THORN_WALL_CROP,
                                  THORN_WALL_PROFILE, THORN_WALLS, TOP, WIDTH)
from pillbug import Pillbug
from player import STANDING_HITBOX_HEIGHT
from rail import (RAIL_ART_SCALE, RAIL_BEND_IMAGE, RAIL_CARRIAGE_IMAGE, RAIL_IMAGE, RAIL_MOUNT_RADIUS,
                  RailCarriage, draw_rail)
from shield_soldier import BASH_DAMAGE, ShieldSoldier


SPAWN = (4780, A_ENTRY[3], 0)
HIDDEN_DOCK_PAUSE = 1.25
HIDDEN_RELIC_PICKUP_RADIUS = 50


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
        yield SpikeBed(left + edge_left * scale_x, left + edge_right * scale_x,
                       bottom + row * height, height=height)


SPIKES = (
    *(SpikeBed(left, right, top) for left, _, right, top in SPIKE_SHELVES),
    *(spikes for wall, hanging in THORN_WALLS for spikes in _thorn_wall_spikes(wall, hanging)),
    SpikeBed(0, WIDTH, BOTTOM),
)
# Keep the painted shelf cores solid and join the top of the hanging wall to the roof.
PLAY_TERRAIN = (*TERRAIN, *SPIKE_SHELVES, HIDDEN_LEDGE, (18, 360, 1110, 500), (1000, 140, 1315, 495),
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
    camera_bottom, camera_top = BOTTOM, TOP
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
        self.safe_pose = SPAWN
        self.dock_pause = 0.0
        self.hidden_relic_collected = False
        # Leave the right edge of each ledge open for landing.
        self.pillbug = Pillbug.on_platform((3060, 85, 3380, PILLBUG_LEDGE[3]))
        self.pillbug.x = 3265
        self.shield = ShieldSoldier(2500, SHIELD_LEDGE[3], 2420, 2600)
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

    def follow_camera(self, player, camera, screen_height):
        camera.follow(player.x)
        camera.y = self.camera_y(player.y, screen_height / camera.zoom)

    @staticmethod
    def camera_y(player_y, view_height):
        target = player_y - view_height * .46
        return max(BOTTOM, min(TOP - view_height, target))

    def nearby_carriage(self, player, relic_placed):
        if relic_placed or not player.grounded:
            return None
        if self.on_hidden_ledge(player):
            return self.carriages[1] if abs(player.x - HIDDEN_DOCK[0]) <= RAIL_MOUNT_RADIUS else None
        _, bottom, _, top = player.get_hitbox()
        for carriage in self.carriages:
            x, y = carriage.segments[-1].end
            if hypot(player.x - x, (bottom + top) / 2 - y) <= RAIL_MOUNT_RADIUS:
                return carriage
        return None

    @staticmethod
    def on_hidden_ledge(player):
        left, _, right, top = HIDDEN_LEDGE
        return player.grounded and player.y == top and left <= player.x < right

    def use_relic(self, player, *, relic_placed):
        if self.mounted_carriage is not None:
            x, y = self.mounted_carriage.position
            return True, (x, y - STANDING_HITBOX_HEIGHT / 2, 0.0)
        carriage = self.nearby_carriage(player, relic_placed)
        if carriage is None:
            return False, None
        self.reset_carriage(carriage)
        if carriage is self.carriages[1]:
            self.dock_pause = 0.0
            if self.on_hidden_ledge(player):
                carriage.distance = HIDDEN_DOCK_DISTANCE
        carriage.relic_mounted = True
        self.rail_attempt = carriage
        return True, None

    def prompt(self, player, relic_placed):
        carriage = self.mounted_carriage
        if carriage is not None:
            if carriage is self.carriages[1] and self.dock_pause > 0:
                return HIDDEN_DOCK, False
            x, y = carriage.segments[-1].end
            if carriage.distance == carriage.length and abs(player.x - x) <= 160:
                return (x, y), True
            return (player.x, player.y + STANDING_HITBOX_HEIGHT), False
        carriage = self.nearby_carriage(player, relic_placed)
        if carriage is not None:
            return (HIDDEN_DOCK if self.on_hidden_ledge(player) else carriage.segments[-1].end), False
        return None

    def update(self, player, dt):
        if self.mounted_carriage is not None:
            self.mounted_carriage.check_attack(player)
        first, second = self.carriages
        first.move(dt)
        if self.dock_pause > 0:
            wait = min(dt, self.dock_pause)
            self.dock_pause -= wait
            if self.dock_pause > 0:
                return
            if second.relic_mounted:
                second.direction = -1
            dt -= wait
        previous = second.distance
        second.move(dt)
        if second.relic_mounted and previous > HIDDEN_DOCK_DISTANCE >= second.distance:
            second.distance = HIDDEN_DOCK_DISTANCE
            second.direction = 0
            self.dock_pause = HIDDEN_DOCK_PAUSE

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
            if self.rail_attempt is self.carriages[1]:
                self.dock_pause = 0.0
            self.reset_carriage(self.rail_attempt)
            self.rail_attempt = None
        if not hit and not health.recovering(now) and self.on_hidden_ledge(player):
            if abs(player.x - HIDDEN_DOCK[0]) <= HIDDEN_RELIC_PICKUP_RADIUS:
                self.hidden_relic_collected = True
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

    def draw(self, camera, screen_height):
        self.art.draw(camera, screen_height)
        scale = RAIL_ART_SCALE * camera.zoom
        for carriage in self.carriages:
            draw_rail(self.rail, self.bend, camera, carriage.segments)
            self.mount.draw(*camera.world_to_screen(*carriage.position),
                            self.mount.w * scale, self.mount.h * scale)
        self.art.draw_hidden_relic(camera, screen_height, self.hidden_relic_collected)

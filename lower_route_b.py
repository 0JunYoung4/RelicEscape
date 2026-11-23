"""The spike gorge, two curved relic rails, and three combat ledges."""

from math import hypot

from pico2d import pico2d as pico

from crystal_golem import CrystalGolem
from health import SPIKE_HEIGHT, SpikeBed
from lower_route_b_art import LowerRouteBArt
from lower_route_b_layout import (A_ENTRY, BOTTOM, C_PASSAGE, GOLEM_LEDGE, PILLBUG_LEDGE,
                                  RAIL_ONE, RAIL_TWO, RIGHT_WALL, SHIELD_LEDGE,
                                  SPIKE_TIP_Y, TERRAIN, TOP, WIDTH)
from pillbug import Pillbug
from player import STANDING_HITBOX_HEIGHT
from rail import (RAIL_ART_SCALE, RAIL_BEND_IMAGE, RAIL_CARRIAGE_IMAGE, RAIL_IMAGE, RAIL_MOUNT_RADIUS,
                  RailCarriage, draw_rail)
from shield_soldier import BASH_DAMAGE, ShieldSoldier


SPAWN = (4780, A_ENTRY[3], 0)
SPIKES = (SpikeBed(0, WIDTH, SPIKE_TIP_Y - SPIKE_HEIGHT),)
# Keep the painted shelf cores solid and join the top of the hanging wall to the roof.
PLAY_TERRAIN = (*TERRAIN, (18, 360, 1110, 500), (1000, 140, 1315, 495),
                (2265, 332, 2860, 495), (4475, -45, WIDTH, 90),
                (3085, -16, 3615, 85), (3160, -145, 3525, -16),
                (3165, BOTTOM, 3520, -145),
                (RIGHT_WALL[0], RIGHT_WALL[3], RIGHT_WALL[2] + 50, 1270),
                (0, 1270, WIDTH, TOP))
SAFE_POSES = (
    (A_ENTRY, SPAWN),
    (PILLBUG_LEDGE, (3450, PILLBUG_LEDGE[3], 0)),
    (SHIELD_LEDGE, (2775, SHIELD_LEDGE[3], 0)),
    (GOLEM_LEDGE, (1160, GOLEM_LEDGE[3], 0)),
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
        # Leave the right edge of each ledge open for landing.
        self.pillbug = Pillbug.on_platform((3060, 85, 3380, PILLBUG_LEDGE[3]))
        self.pillbug.x = 3265
        self.shield = ShieldSoldier(2500, SHIELD_LEDGE[3], 2420, 2600)
        self.golem = CrystalGolem.on_platform((710, 495, 1070, GOLEM_LEDGE[3]), direction=1)
        self.golem.x = 885
        self.fights = (
            (self.pillbug, 3060, 3410),
            (self.shield, 2350, 2670),
            (self.golem, 680, 1100),
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
        player.ground_y = SPIKES[0].y
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
        _, bottom, _, top = player.get_hitbox()
        for carriage in self.carriages:
            x, y = carriage.segments[-1].end
            if hypot(player.x - x, (bottom + top) / 2 - y) <= RAIL_MOUNT_RADIUS:
                return carriage
        return None

    def use_relic(self, player, *, relic_placed):
        if self.mounted_carriage is not None:
            x, y = self.mounted_carriage.position
            return True, (x, y - STANDING_HITBOX_HEIGHT / 2, 0.0)
        carriage = self.nearby_carriage(player, relic_placed)
        if carriage is None:
            return False, None
        self.reset_carriage(carriage)
        carriage.relic_mounted = True
        self.rail_attempt = carriage
        return True, None

    def prompt(self, player, relic_placed):
        carriage = self.mounted_carriage
        if carriage is not None:
            x, y = carriage.segments[-1].end
            if carriage.distance == carriage.length and abs(player.x - x) <= 160:
                return (x, y), True
            return (player.x, player.y + STANDING_HITBOX_HEIGHT), False
        carriage = self.nearby_carriage(player, relic_placed)
        return (carriage.segments[-1].end, False) if carriage is not None else None

    def update(self, player, dt):
        if self.mounted_carriage is not None:
            self.mounted_carriage.check_attack(player)
        for carriage in self.carriages:
            carriage.move(dt)

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

    def draw(self, camera, screen_height):
        self.art.draw(camera, screen_height)
        scale = RAIL_ART_SCALE * camera.zoom
        for carriage in self.carriages:
            draw_rail(self.rail, self.bend, camera, carriage.segments)
            self.mount.draw(*camera.world_to_screen(*carriage.position),
                            self.mount.w * scale, self.mount.h * scale)

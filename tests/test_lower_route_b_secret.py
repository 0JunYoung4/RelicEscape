"""Verify the secret route is optional and can rejoin the second rail."""

import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("SDL_RENDER_DRIVER", "software")

from pico2d import pico2d as pico

from health import Health, MAX_HEALTH
from lower_route_b import LowerRouteB, SPAWN
from lower_route_b_layout import (RAIL_TWO, SECRET_CEILING_Y, SECRET_FLOOR_Y, SECRET_RAIL_DOCK,
                                  SECRET_RELIC_X, SHIELD_LEDGE, WIDTH)
from player import Player, STANDING_HITBOX_HEIGHT


class LowerRouteBSecretTests(unittest.TestCase):
    def setUp(self):
        pico.open_canvas(960, 540)
        self.addCleanup(pico.close_canvas)

    def test_drops_from_moving_rail_walks_left_for_relic_and_returns(self):
        route = LowerRouteB()
        player = Player(*SPAWN[:2], WIDTH)
        route.enter(player)
        health = Health(SPAWN)
        dt = 1 / 60

        def step(direction=0, attack=False):
            player.update(direction, True, dt, attack_pressed=attack)
            route.update(player, dt)
            self.assertFalse(route.check_spikes(player, health, 1))

        def walk_to(target, direction):
            for _ in range(260):
                if direction * (target - player.x) <= 0:
                    return
                step(direction)
            self.fail(f"Stopped at {player.x}, {player.y} on the way to {target}")

        self.assertEqual(SECRET_CEILING_Y - SECRET_FLOOR_Y, STANDING_HITBOX_HEIGHT + 25)
        self.assertTrue(player.recover_at(RAIL_TWO[-1].end[0], SHIELD_LEDGE[3], 0))
        self.assertEqual(route.use_relic(player, relic_placed=False), (True, None))
        carriage = route.carriages[1]
        step(-1, attack=True)
        for _ in range(300):
            if carriage.position[1] == SECRET_RAIL_DOCK[1] and carriage.position[0] <= SECRET_RAIL_DOCK[0]:
                break
            step()
        self.assertEqual(carriage.direction, -1)
        self.assertAlmostEqual(carriage.position[1], SECRET_RAIL_DOCK[1])

        handled, pose = route.use_relic(player, relic_placed=False)
        self.assertTrue(handled)
        self.assertTrue(player.teleport_to(*pose))
        carriage.relic_mounted = False
        for _ in range(35):
            step()
        self.assertTrue(player.grounded)
        self.assertEqual(player.y, SECRET_FLOOR_Y)
        self.assertFalse(route.secret_revealed)

        walk_to(SECRET_RELIC_X + 15, -1)
        self.assertEqual(player.y, SECRET_FLOOR_Y)
        self.assertEqual(player.crouch_time, 0)
        self.assertTrue(route.secret_revealed)
        self.assertTrue(route.secret_relic_collected)
        self.assertEqual(health.current, MAX_HEALTH)

        walk_to(SECRET_RAIL_DOCK[0] + 14, 1)
        self.assertEqual(route.prompt(player, False), (SECRET_RAIL_DOCK, False))
        self.assertEqual(route.use_relic(player, relic_placed=False), (True, None))
        step(-1, attack=True)
        for _ in range(300):
            if carriage.distance == 0:
                break
            step()
        self.assertEqual(carriage.position, RAIL_TWO[0].start)
        self.assertTrue(route.secret_relic_collected)
        handled, pose = route.use_relic(player, relic_placed=False)
        self.assertTrue(handled)
        self.assertTrue(player.teleport_to(*pose))
        for _ in range(20):
            step()
        self.assertTrue(player.grounded)

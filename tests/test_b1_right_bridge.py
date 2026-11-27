"""Exercise the main game's right bridge before and after B1 is cleared."""

import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("SDL_RENDER_DRIVER", "software")

from pico2d import pico2d as pico

import main
import right_bridge
from lower_caves import ENTRY_LEDGE, LowerCaves
from lower_route_a import ENTRY_STEP
from lower_route_b import SPIKES
from lower_route_c import BOSS_RETURN
from opening_cave import OpeningCave
from player import Player, WORLD_MARGIN


DT = 1 / 60


class B1RightBridgeTests(unittest.TestCase):
    def setUp(self):
        pico.open_canvas(main.SCREEN_WIDTH, main.SCREEN_HEIGHT)
        self.addCleanup(pico.close_canvas)
        self.rooms = LowerCaves(OpeningCave(main.SCREEN_WIDTH, main.SCREEN_HEIGHT))
        self.player = Player(75, 0, main.WORLD_WIDTH)
        self.camera = main.Camera(main.SCREEN_WIDTH, main.WORLD_WIDTH)
        self.rooms.room, self.rooms.has_relic = "route_a", True
        self.rooms.enter(self.player, self.camera, seal_open=True)

    def step(self, direction=0, *, jump_pressed=False, attack_pressed=False):
        self.rooms.update(self.player, self.camera, DT, interact=False, direction=direction,
                          running=True, jump_pressed=jump_pressed, jump_held=True,
                          crouching=False, attack_pressed=attack_pressed)
        self.rooms.update_effects(DT, self.player)

    def enter_from_a(self):
        self.assertEqual(self.rooms.room, "route_a")
        route = self.rooms.route_a
        floor_y = route.point(0, ENTRY_LEDGE[3])[1]
        self.assertTrue(self.player.recover_at(route.world_width - WORLD_MARGIN, floor_y, 0))
        self.step(1)
        self.assertEqual(self.rooms.room, "right_bridge")
        self.assertEqual((self.player.x, self.player.y), right_bridge.ENTRY_SPAWN[:2])

    def walk_until(self, condition, direction):
        for _ in range(720):
            if condition():
                return
            self.step(direction)
        self.fail(f"Bridge movement timed out in {self.rooms.room} at {(self.player.x, self.player.y)}")

    def draw_bridge(self):
        pico.SDL_ClearError()
        self.rooms.draw(self.camera)
        self.rooms.draw_foreground(self.camera)
        self.assertFalse(pico.SDL_GetError())

    def test_returns_from_b1_exit_to_open_bridge_with_existing_controls(self):
        rooms, player = self.rooms, self.player
        rooms.leave_b1(player, self.camera)
        self.assertEqual((player.x, player.y), BOSS_RETURN[:2])
        second, first = reversed(rooms.route_b.carriages)
        near_left_dock = second.segments[0].start[0] - 57
        self.walk_until(lambda: player.x >= near_left_dock and player.grounded, 1)
        self.assertIsNone(rooms.route_b.nearby_dock(player, relic_placed=False))

        rooms.b1_cleared = True
        rooms.leave_b1(player, self.camera)
        travel = main.RelicTravel()
        for carriage in (second, first):
            start_x, _ = carriage.segments[0].start
            self.walk_until(lambda: player.x >= start_x - 57 and player.grounded, 1)
            self.assertEqual(rooms.route.use_relic(player, relic_placed=False), (True, None))
            self.assertIs(rooms.route_b.mounted_carriage, carriage)
            self.assertEqual(carriage.distance, 0)
            self.step(attack_pressed=True)
            self.walk_until(lambda: carriage.distance == carriage.length, 0)
            handled, destination = rooms.route.use_relic(player, relic_placed=False)
            self.assertTrue(handled)
            self.assertTrue(travel.teleport(player, self.camera, destination, 1, reclaim=True))
            carriage.relic_mounted = False
            self.assertFalse(any(spike.overlaps(player.get_hitbox()) for spike in SPIKES))

        route = rooms.route_a
        step_left, _, _, step_top = route.bounds(ENTRY_STEP)
        ledge_left = route.bounds(ENTRY_LEDGE)[0]
        jumped = False
        for _ in range(1100):
            if rooms.room == "right_bridge":
                break
            ground_jump = player.grounded and (
                (not jumped and player.x >= step_left - 115)
                or (jumped and abs(player.y - step_top) < .1 and player.x >= ledge_left - 115)
            )
            wall_jump = (not player.grounded and player.wall_direction == 1 and player.wall_jump_remaining == 0
                         and player.x >= step_left - 125)
            jumped = jumped or ground_jump or wall_jump
            self.step(1, jump_pressed=ground_jump or wall_jump)
        self.assertEqual(rooms.room, "right_bridge",
                         (player.x, player.y, player.wall_direction, player.grounded))
        self.assertNotIn(right_bridge.BARRIER, player.terrain)
        self.walk_until(lambda: player.get_hitbox()[0] > right_bridge.BARRIER[2], 1)
        self.assertIsNotNone(rooms.bridge_release_age)

    def test_b1_clear_opens_the_bridge_and_plays_one_residual_effect(self):
        rooms, player = self.rooms, self.player
        self.enter_from_a()
        self.assertIn(right_bridge.BARRIER, player.terrain)
        self.walk_until(lambda: rooms.bridge_contact_age is not None, 1)
        self.assertAlmostEqual(player.get_hitbox()[2], right_bridge.BARRIER[0])
        self.draw_bridge()
        contact_x = player.x
        self.step()
        self.assertLess(player.x, contact_x)
        for tick in range(100):
            self.step(1, jump_pressed=tick % 28 == 0)
            self.assertLessEqual(player.get_hitbox()[2], right_bridge.BARRIER[0])
        right_destination = right_bridge.BARRIER[2] + 120, player.ground_y, 0
        self.assertFalse(rooms.allows_relic_destination(right_destination))
        self.assertTrue(rooms.allows_relic_destination(right_bridge.ENTRY_SPAWN))
        self.assertIsNone(rooms.bridge_release_age)
        self.assertFalse(rooms.bridge_release_seen)

        self.walk_until(lambda: rooms.room == "route_a", -1)
        rooms.b1_cleared = True
        self.enter_from_a()
        self.assertNotIn(right_bridge.BARRIER, player.terrain)
        self.assertTrue(rooms.allows_relic_destination(right_destination))
        self.assertIsNone(rooms.bridge_release_age)
        self.walk_until(lambda: rooms.bridge_release_seen, 1)
        self.assertGreaterEqual(player.x, right_bridge.RELEASE_APPROACH_X)
        self.assertEqual(rooms.bridge_release_age, 0)
        self.assertIsNone(rooms.bridge_contact_age)
        self.draw_bridge()
        self.walk_until(lambda: player.get_hitbox()[0] > right_bridge.BARRIER[2], 1)
        self.assertIsNotNone(rooms.bridge_release_age)
        self.walk_until(lambda: rooms.bridge_release_age is None, 0)

        self.walk_until(lambda: rooms.room == "route_a", -1)
        self.enter_from_a()
        self.walk_until(lambda: player.get_hitbox()[0] > right_bridge.BARRIER[2], 1)
        self.assertTrue(rooms.b1_cleared and rooms.bridge_release_seen)
        self.assertIsNone(rooms.bridge_release_age)
        self.assertIsNone(rooms.bridge_contact_age)

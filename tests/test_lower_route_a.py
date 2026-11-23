"""Verify the connected chamber's puzzle, jump constraints, and real key flow."""

import gc
from itertools import count
import os
from types import SimpleNamespace
import unittest
from unittest.mock import patch

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("SDL_RENDER_DRIVER", "software")

from pico2d import pico2d as pico

import main
from lower_caves import LowerCaves
from lower_route_a import (BUTTON_CENTER, ENTRY_LEDGE, ENTRY_STEP, EXIT_LEDGE, GROUND_Y,
                           LOWER_DOCK, RECOVERY, RECESS_BACK, UPPER_DOCK, WIDTH, LowerRouteA)
from player import Player, STANDING_HITBOX_HEIGHT, WORLD_MARGIN


def keydown(key):
    event = pico.Event(pico.SDL_KEYDOWN)
    event.key = key
    return event


class LowerRouteATests(unittest.TestCase):
    def setUp(self):
        pico.open_canvas(960, 540)
        self.player = Player(100, 0, WIDTH)
        self.camera = main.Camera(960, WIDTH)
        self.route = LowerRouteA()
        self.route.enter(self.player)

    def tearDown(self):
        del self.route, self.player
        gc.collect()
        pico.close_canvas()

    def tick(self, direction=0, *, jump=False, attack=False):
        self.player.update(direction, True, 1 / 60, jump_pressed=jump, attack_pressed=attack)
        self.route.update(self.player, 1 / 60)

    def test_walk_from_the_entry_powers_the_button_and_reaches_the_dock(self):
        for _ in range(450):
            if self.player.x <= LOWER_DOCK[0] - 60:
                break
            self.tick(-1)
        self.assertTrue(self.route.powered)
        self.assertEqual(self.player.y, GROUND_Y)
        self.assertTrue(self.route.can_mount(self.player, False))
        self.assertFalse(self.route.can_mount(self.player, True))
        self.assertEqual(self.route.use_relic(self.player, relic_placed=False), (True, None))
        self.player.facing = 1
        self.tick(attack=True)
        for _ in range(40):
            self.tick()
        self.assertGreater(self.route.carriage.distance, 0)
        self.assertLess(self.route.carriage.distance, self.route.carriage.length)
        handled, destination = self.route.use_relic(self.player, relic_placed=False)
        self.assertTrue(handled)
        self.assertTrue(self.player.teleport_to(*destination))
        self.route.carriage.relic_mounted = False  # Commit the successful recall.
        for _ in range(120):
            self.tick()
        self.assertEqual(self.player.y, GROUND_Y)
        self.assertTrue(self.player.recover_at(RECOVERY[0], GROUND_Y, 0))
        self.assertEqual(self.route.use_relic(self.player, relic_placed=False), (True, None))
        self.assertEqual(self.route.carriage.position, LOWER_DOCK)
        self.assertTrue(self.route.powered)

    def test_rail_never_places_the_player_inside_terrain(self):
        for segment in self.route.path:
            for i in range(51):
                x, y = segment.point_at(i / 50)
                self.assertTrue(self.player.teleport_to(x, y - STANDING_HITBOX_HEIGHT / 2, 0))

    def test_jumping_does_not_reach_the_exit_from_the_pit_or_right_ledge(self):
        for x, y, direction in (
            (EXIT_LEDGE[2] + 22, GROUND_Y, -1),
            ((EXIT_LEDGE[2] + ENTRY_STEP[0]) / 2, GROUND_Y, -1),
            (ENTRY_LEDGE[0] + 40, ENTRY_LEDGE[3], -1),
            (RECESS_BACK[2] + 22, GROUND_Y, -1),
        ):
            with self.subTest(x=x, y=y):
                self.assertTrue(self.player.recover_at(x, y, 0))
                for frame in range(200):
                    self.tick(direction, jump=frame % 12 == 0)
                    self.assertFalse(self.player.x < EXIT_LEDGE[2] and self.player.y >= EXIT_LEDGE[3])
        self.assertTrue(self.player.recover_at(RECESS_BACK[2] + 20,
                                              EXIT_LEDGE[1] - STANDING_HITBOX_HEIGHT - 2, 0))
        for frame in range(100):
            self.tick(1, jump=frame % 12 == 0)
            self.assertLess(self.player.y, EXIT_LEDGE[3])

    def test_opening_loop_mounts_launches_recalls_and_walks_to_the_exit(self):
        frame = count()
        state = SimpleNamespace(room=None, player=None, launched=False, recalled=False, mounted=False)

        def start(room, player, camera):
            room.room, room.has_relic = "route_a", True
            room.enter(player, camera)
            state.room, state.player = room, player
            player.recover_at(BUTTON_CENTER[0], GROUND_Y, 0)
            room.route_a.update(player, 0)
            player.recover_at(LOWER_DOCK[0] - 75, GROUND_Y, 0)
            player.facing = 1

        def events():
            index = next(frame)
            carriage = state.room.route_a.carriage
            if index == 0:
                return [keydown(pico.SDLK_e)]
            if index == 1:
                state.mounted = carriage.relic_mounted
                return [keydown(pico.SDLK_x)]
            if carriage.position == UPPER_DOCK and not state.recalled:
                state.launched = carriage.relic_mounted
                state.recalled = True
                return [keydown(pico.SDLK_e)]
            if state.player.x == WORLD_MARGIN or index > 450:
                return [pico.Event(pico.SDL_QUIT)]
            return []

        def movement():
            if state.recalled and state.player.grounded:
                return -1, True, False
            return 0, False, False

        with patch.object(LowerCaves, "start_after_relic", new=start), \
                patch.object(pico, "get_events", side_effect=events), \
                patch.object(pico, "SDL_GetKeyboardFocus", return_value=True), \
                patch.object(main, "read_movement", side_effect=movement), \
                patch.object(main, "perf_counter", side_effect=count(step=1 / 60)), \
                patch.object(main, "sleep"), patch.object(pico, "update_canvas"):
            main.run_opening_cave(False, after_relic=True)
        self.assertTrue(state.mounted and state.launched and state.recalled)
        self.assertFalse(state.room.route_a.carriage.relic_mounted)
        self.assertEqual((state.player.x, state.player.y), (WORLD_MARGIN, EXIT_LEDGE[3]))

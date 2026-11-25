"""Exercise the seamless B/C crossing and the antechamber checkpoint."""

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
from health import SPIKE_DAMAGE
from lower_caves import LowerCaves
from lower_route_b import SPIKES, LowerRouteB
from lower_route_c import CHECKPOINT, ENTRANCE_WIDTH, ENTRANCE_X, FLOOR, LEFT
from pillbug import Pillbug
from player import Player, STANDING_HITBOX_WIDTH


def keydown(key):
    event = pico.Event(pico.SDL_KEYDOWN)
    event.key = key
    return [event]


class LowerRouteCTests(unittest.TestCase):
    def setUp(self):
        pico.open_canvas(main.SCREEN_WIDTH, main.SCREEN_HEIGHT)
        self.addCleanup(pico.close_canvas)

    def test_entry_floor_and_sealed_boss_boundary(self):
        cave = SimpleNamespace(width=960, height=540, shaft=SimpleNamespace(w=4096))
        rooms = LowerCaves(cave)
        player = Player(0, 0, main.WORLD_WIDTH)
        camera = main.Camera(960, main.WORLD_WIDTH)
        rooms.room = "route_b"
        rooms.enter(player, camera)
        self.assertTrue(player.recover_at(80, FLOOR, 0))
        for _ in range(250):
            player.update(-1, True, 1 / 60)
            rooms.follow_camera(player, camera)
            self.assertTrue(player.grounded)
            self.assertEqual(player.y, FLOOR)
        self.assertEqual(rooms.room, "route_c")
        self.assertIsNone(rooms.route)
        self.assertEqual(rooms.restart_room, "route_c")
        self.assertAlmostEqual(player.x, ENTRANCE_X + (ENTRANCE_WIDTH + STANDING_HITBOX_WIDTH) / 2)
        self.assertEqual(camera.x, LEFT)

    def test_two_pillbugs_replace_the_golem_near_c_and_can_be_hit(self):
        cave = SimpleNamespace(width=960, height=540, shaft=SimpleNamespace(w=4096))
        rooms = LowerCaves(cave)
        player = Player(0, 0, main.WORLD_WIDTH)
        camera = main.Camera(960, main.WORLD_WIDTH)
        rooms.room = "route_b"
        rooms.enter(player, camera)
        self.assertTrue(player.recover_at(885, FLOOR, 0))
        rooms.update_enemies(player, 0)
        self.assertEqual(rooms.route_b.enemies, ())

        bugs = rooms.route_c.enemies
        self.assertEqual(len(bugs), 2)
        for swing, bug in enumerate(bugs, start=1):
            self.assertIsInstance(bug, Pillbug)
            self.assertGreater(bug.support_edges[0], CHECKPOINT[0])
            self.assertTrue(player.recover_at(bug.x + 96, FLOOR, 0))
            rooms.follow_camera(player, camera)
            self.assertEqual(rooms.room, "route_c")
            player.slash, player.swing_id = (0.04, -1, "attack"), swing
            hp = bug.hp
            rooms.update_enemies(player, 0)
            self.assertEqual(bug.hp, hp - player.attack_power)

    def test_relic_can_cross_the_seam_and_defeat_restarts_at_the_lantern(self):
        state = SimpleNamespace(step="to_c", direction=0)
        clock = count(step=1 / 120)
        frames = count()
        check_spikes = LowerRouteB.check_spikes

        def start(room, player, camera):
            state.room, state.player = room, player
            room.room, room.has_relic = "route_b", True
            room.enter(player, camera)
            self.assertTrue(player.recover_at(260, FLOOR, 0))
            room.follow_camera(player, camera)
            state.original_b = room.route_b

        def record(room, camera):
            state.room, state.camera = room, camera

        def near_fatal_spikes(route, player, health, now):
            if state.step == "hit_spikes":
                health.current = SPIKE_DAMAGE
                state.step = "restart"
            return check_spikes(route, player, health, now)

        def events():
            if next(frames) > 1000:
                self.fail(f"Did not finish C traversal at step {state.step}")
            room, player = state.room, state.player
            state.direction = 0
            if state.step == "to_c":
                if room.route_c.checkpoint_reached:
                    self.assertEqual(room.room, "route_c")
                    self.assertTrue(player.grounded)
                    state.anchor_x = player.x
                    state.step = "to_b"
                    return keydown(pico.SDLK_e)
                state.direction = -1
            elif state.step == "to_b":
                if room.room == "route_b" and player.x > 80:
                    self.assertIs(room.route_b, state.original_b)
                    state.step = "recall"
                    return keydown(pico.SDLK_e)
                state.direction = 1
            elif state.step == "recall":
                self.assertEqual(room.room, "route_c")
                self.assertAlmostEqual(player.x, state.anchor_x)
                self.assertLess(state.camera.x, 0)
                self.assertTrue(player.recover_at(4050, SPIKES[0].y, 0))
                room.follow_camera(player, state.camera)
                self.assertEqual(room.restart_room, "route_c")
                state.step = "hit_spikes"
            elif state.step == "restart" and room.route_b is not state.original_b:
                self.assertEqual(room.room, "route_c")
                self.assertEqual((player.x, player.y), CHECKPOINT[:2])
                self.assertTrue(room.has_relic and room.route_c.checkpoint_reached)
                self.assertTrue(player.grounded)
                state.step = "done"
                return [pico.Event(pico.SDL_QUIT)]
            return []

        with patch.object(LowerCaves, "start_after_relic", new=start), \
                patch.object(LowerCaves, "draw", new=record), \
                patch.object(LowerRouteB, "check_spikes", new=near_fatal_spikes), \
                patch.object(pico, "get_events", side_effect=events), \
                patch.object(pico, "SDL_GetKeyboardFocus", return_value=True), \
                patch.object(main, "read_movement", side_effect=lambda: (state.direction, True, False)), \
                patch.object(main, "perf_counter", side_effect=lambda: next(clock)), \
                patch.object(main, "sleep"), patch.object(pico, "update_canvas"):
            main.run_opening_cave(False, after_relic=True)
        self.assertEqual(state.step, "done")

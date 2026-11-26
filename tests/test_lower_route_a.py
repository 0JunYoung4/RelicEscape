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

from PIL import Image
from pico2d import pico2d as pico

import main
from health import Health
from lower_caves import LowerCaves
from lower_route_a import (BUTTON_CENTER, ENTRY_LEDGE, ENTRY_STEP, EXIT_LEDGE, GROUND_Y,
                           LOWER_DOCK, OVERHANG, RECOVERY, RECESS_BACK, SEAL_LOWER_PLATE,
                           SEAL_OPEN_DURATION, SEAL_PLATE_HALF_WIDTH, SEAL_UPPER_PLATE,
                           SEAL_WINDOW, UPPER_DOCK, WIDTH, LowerRouteA)
from lower_route_connection import (A_ORIGIN, PASSAGE_ART_FLOOR_ROW, PASSAGE_ART_SCALE_X,
                                    PASSAGE_ART_SCALE_Y, PASSAGE_ART_X, PASSAGE_FLOOR,
                                    PASSAGE_LEFT, PASSAGE_RIGHT)
from lower_route_b_layout import A_ENTRY
from lower_route_passage_art import PASSAGE_ART
from player import ASSET_ROOT, Player, STANDING_HITBOX_HEIGHT
from pillbug import EMERGE_DURATION


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

    def test_connected_cliff_has_an_opaque_collision_core_and_a_clear_exterior(self):
        with Image.open(PASSAGE_ART / "terrain.png") as plate:
            alpha = plate.getchannel("A")
        left = round((A_ENTRY[0] + 12 - PASSAGE_ART_X) / PASSAGE_ART_SCALE_X)
        right = round((PASSAGE_LEFT + 12 - PASSAGE_ART_X) / PASSAGE_ART_SCALE_X)
        bottom = PASSAGE_ART_FLOOR_ROW + round((A_ENTRY[3] - A_ENTRY[1]) / PASSAGE_ART_SCALE_Y)
        self.assertEqual(alpha.crop((left, PASSAGE_ART_FLOOR_ROW, right, bottom)).getextrema(), (255, 255))
        self.assertEqual(alpha.crop((0, 0, left, PASSAGE_ART_FLOOR_ROW - 8)).getextrema(), (0, 0))

    def test_layered_passage_preserves_the_visible_ground_pixels(self):
        with (
            Image.open(ASSET_ROOT / "terrain/lower-route-ab-passage-joined-v2.png") as original,
            Image.open(PASSAGE_ART / "terrain.png") as terrain,
        ):
            self.assertEqual(terrain.size, original.size)
            ground = (0, PASSAGE_ART_FLOOR_ROW, original.width, original.height)
            self.assertEqual(terrain.crop(ground).convert("RGBa").tobytes(),
                             original.crop(ground).convert("RGBa").tobytes())

    def test_ground_button_emerges_two_pillbugs_once_and_powers_the_rail(self):
        room = LowerCaves(SimpleNamespace(width=960, height=540, shaft=SimpleNamespace(w=4096)))
        room.room, room.route_a = "route_a", self.route
        button_x = BUTTON_CENTER[0]
        self.assertTrue(self.player.recover_at(button_x, GROUND_Y + 60, 0))
        self.tick()
        self.assertFalse(self.route.powered)
        self.assertEqual(room.enemies, (self.route.pillbug,))

        self.assertTrue(self.player.recover_at(button_x, GROUND_Y, 0))
        self.tick()
        left, right = self.route.button_pillbugs
        self.assertTrue(self.route.powered)
        self.assertEqual(room.enemies, (self.route.pillbug, left, right))
        self.assertLess(left.x, button_x)
        self.assertGreater(right.x, button_x)
        self.assertEqual((left.direction, right.direction), (1, -1))
        self.assertEqual((left.phase, right.phase), ("emerge", "emerge"))
        self.assertEqual((left.floor_y, right.floor_y), (GROUND_Y, GROUND_Y))
        health = Health((button_x, GROUND_Y, 0))
        self.assertTrue(self.player.recover_at(left.x, GROUND_Y, 0))
        self.assertFalse(health.check_contact(self.player, room.enemies, 1))
        room.update_enemies(self.player, EMERGE_DURATION)
        self.assertTrue(health.check_contact(self.player, room.enemies, 2))

        self.assertTrue(self.player.recover_at(button_x, GROUND_Y, 0))
        self.tick()
        self.assertEqual(self.route.button_pillbugs, (left, right))
        self.assertEqual((left.phase, right.phase), ("crawl", "crawl"))

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
                                              OVERHANG[0][1] - STANDING_HITBOX_HEIGHT - 2, 0))
        for frame in range(100):
            self.tick(1, jump=frame % 12 == 0)
            self.assertLess(self.player.y, EXIT_LEDGE[3])

    def test_timed_seal_expires_and_rearms_on_a_new_press(self):
        cave = SimpleNamespace(width=960, height=540, shaft=SimpleNamespace(w=4096))
        room = LowerCaves(cave)
        room.room = "route_a"
        room.enter(self.player, self.camera)
        route = room.route_a
        lower_x, lower_y = route.point(*SEAL_LOWER_PLATE)
        upper_x, upper_y = route.point(*SEAL_UPPER_PLATE)
        closed_barrier = route.seal_barrier
        self.assertIn(closed_barrier, self.player.terrain)
        gate_x = (closed_barrier[0] + closed_barrier[2]) / 2
        self.assertFalse(self.player.teleport_to(gate_x, upper_y, 0))

        self.assertTrue(self.player.recover_at(upper_x, upper_y, 0))
        room.update_relic_seal(self.player, 0)
        self.assertFalse(route.seal_unlocked)
        self.assertTrue(self.player.recover_at(lower_x, lower_y + 30, 0))
        room.update_relic_seal(self.player, .5)
        self.assertEqual(route.seal_remaining, 0)

        self.assertTrue(self.player.recover_at(lower_x, lower_y, 0))
        room.update_relic_seal(self.player, 1)
        self.assertEqual(route.seal_remaining, SEAL_WINDOW)
        room.update_relic_seal(self.player, 1 + SEAL_WINDOW)
        room.update_relic_seal(self.player, 2 + SEAL_WINDOW)
        self.assertEqual(route.seal_remaining, 0)
        self.assertTrue(self.player.recover_at(upper_x, upper_y, 0))
        room.update_relic_seal(self.player, 2 + SEAL_WINDOW)
        self.assertFalse(route.seal_unlocked)

        self.assertTrue(self.player.recover_at(lower_x, lower_y, 0))
        room.update_relic_seal(self.player, 6)
        self.assertEqual(route.seal_remaining, SEAL_WINDOW)
        self.assertTrue(self.player.recover_at(upper_x, upper_y, 0))
        room.update_relic_seal(self.player, 8.95)
        self.assertTrue(route.seal_unlocked)
        room.update_relic_seal(self.player, 8.95 + SEAL_OPEN_DURATION / 2)
        self.assertNotIn(closed_barrier, self.player.terrain)
        self.assertIn(route.seal_barrier, self.player.terrain)
        room.update_relic_seal(self.player, 10)
        self.assertTrue(self.player.teleport_to(gate_x, upper_y, 0))
        self.assertIsNone(route.seal_barrier)

        restarted = LowerCaves(cave)
        restarted.room = "route_b"
        restarted.enter(self.player, self.camera, seal_open=route.seal_unlocked)
        self.assertNotIn(closed_barrier, self.player.terrain)
        self.assertTrue(restarted.route_a.seal_unlocked)

    def test_opening_loop_solves_the_seal_and_walks_to_b_without_a_camera_cut(self):
        frame = count()
        state = SimpleNamespace(room=None, player=None, launched=False, recalled=False, mounted=False,
                                seal_step="upper")
        keys = [0] * pico.SDL_NUM_SCANCODES
        moving_views = []
        dock_views = []
        passage_views = []
        dock_frames = 0
        anchor_point = None
        travel = None
        draw = LowerCaves.draw
        place_or_recall = main.RelicTravel.place_or_recall

        def start(room, player, camera):
            room.room, room.has_relic = "route_a", True
            room.enter(player, camera)
            state.room, state.player = room, player
            route = room.route_a
            player.recover_at(*route.point(BUTTON_CENTER[0], GROUND_Y), 0)
            room.route_a.update(player, 0)
            player.recover_at(*route.point(LOWER_DOCK[0] - 75, GROUND_Y), 0)
            player.facing = 1

        def events():
            nonlocal dock_frames, anchor_point
            index = next(frame)
            if state.player.x < PASSAGE_LEFT - 100 or index > 800:
                return [pico.Event(pico.SDL_QUIT)]
            route = state.room.route_a
            carriage = route.carriage
            keys[pico.SDL_SCANCODE_C] = 0
            if index == 0:
                return [keydown(pico.SDLK_e)]
            if index == 1:
                state.mounted = carriage.relic_mounted
                return [keydown(pico.SDLK_x)]
            if index == 12:
                # From the far side of the pit, the upper dock is entirely off-screen.
                self.assertTrue(state.player.recover_at(*route.point(RECOVERY[0] - 230, GROUND_Y), 0))
            if 12 <= index < 36 or (not state.recalled and carriage.position[1] > 600 + A_ORIGIN[1]):
                keys[pico.SDL_SCANCODE_C] = 1
            if carriage.position == route.point(*UPPER_DOCK) and not state.recalled:
                dock_frames += 1
                keys[pico.SDL_SCANCODE_C] = dock_frames % 2
                if dock_frames < 5:
                    return []
                state.launched = carriage.relic_mounted
                state.recalled = True
                return [keydown(pico.SDLK_e)]
            if state.recalled and state.seal_step == "upper":
                if route.on_seal_plate(state.player, SEAL_UPPER_PLATE):
                    state.seal_step = "lower"
                    return [keydown(pico.SDLK_e)]
            elif state.seal_step == "lower" and route.seal_remaining:
                self.assertTrue(route.on_seal_plate(state.player, SEAL_LOWER_PLATE))
                state.seal_step = "exit"
                return [keydown(pico.SDLK_e)]
            if state.seal_step == "exit" and state.player.x < PASSAGE_RIGHT + 150 and anchor_point is None:
                anchor_point = state.player.x
                return [keydown(pico.SDLK_e)]
            return []

        def movement():
            if not state.recalled:
                return 0, False, False
            if state.seal_step == "exit":
                return -1, True, False
            plate = SEAL_UPPER_PLATE if state.seal_step == "upper" else SEAL_LOWER_PLATE
            x, _ = state.room.route_a.point(*plate)
            if state.player.x < x - SEAL_PLATE_HALF_WIDTH / 4:
                return 1, True, False
            return 0, False, False

        def record(room, camera):
            route = room.route_a
            carriage = route.carriage
            viewing_join = state.recalled and state.player.x < PASSAGE_RIGHT + 180
            if viewing_join:
                passage_views.append((state.player.x, state.player.y, camera.x, camera.y))
            if carriage.relic_mounted and carriage.position == route.point(*UPPER_DOCK):
                dock_views.append(camera.world_to_screen(*carriage.position)[0])
            elif carriage.relic_mounted and carriage.direction and keys[pico.SDL_SCANCODE_C]:
                moving_views.append((camera.x, camera.y, camera.world_to_screen(*carriage.position)))
            elif state.recalled and keys[pico.SDL_SCANCODE_C]:
                self.assertAlmostEqual(camera.x, camera._clamp_x(state.player.x - camera.view_width / 2))
            if viewing_join:
                pico.SDL_ClearError()
            draw(room, camera)
            if viewing_join:
                self.assertFalse(pico.SDL_GetError())

        def remember_anchor(relic_travel, player, now):
            nonlocal travel
            travel = relic_travel
            return place_or_recall(relic_travel, player, now)

        with patch.object(LowerCaves, "start_after_relic", new=start), \
                patch.object(LowerCaves, "draw", new=record), \
                patch.object(main.RelicTravel, "place_or_recall", new=remember_anchor), \
                patch.object(main, "poll_events", side_effect=events), \
                patch.object(pico, "SDL_GetKeyboardFocus", return_value=True), \
                patch.object(pico, "SDL_GetKeyboardState", return_value=keys), \
                patch.object(main, "read_movement", side_effect=movement), \
                patch.object(main, "perf_counter", side_effect=count(step=1 / 60)), \
                patch.object(main, "sleep"), patch.object(pico, "update_canvas"):
            main.run_opening_cave(False, after_relic=True)
        self.assertTrue(state.mounted and state.launched and state.recalled)
        self.assertGreater(len(moving_views), 10)
        self.assertGreater(max(view[0] for view in moving_views), moving_views[0][0])
        self.assertGreater(max(view[1] for view in moving_views), A_ORIGIN[1])
        for _, _, (x, y) in moving_views:
            self.assertAlmostEqual(x, main.SCREEN_WIDTH / 2)
            self.assertTrue(0 <= y < main.SCREEN_HEIGHT)
        # The moving view stays held on the frame when the carriage reaches the dock.
        self.assertEqual(len(dock_views), 5)
        for index, x in enumerate(dock_views):
            if index == 0 or index % 2:
                self.assertAlmostEqual(x, main.SCREEN_WIDTH / 2)
            else:
                self.assertLess(x, 0)
        self.assertFalse(state.room.route_a.carriage.relic_mounted)
        self.assertTrue(state.room.route_a.seal_unlocked)
        self.assertEqual(state.room.room, "route_b")
        self.assertLess(state.player.x, PASSAGE_LEFT - 100)
        self.assertEqual(state.player.y, PASSAGE_FLOOR)
        self.assertEqual(travel.anchor.x, anchor_point)
        self.assertTrue(state.room.route_a.powered)
        self.assertGreater(len(passage_views), 50)
        for before, after in zip(passage_views, passage_views[1:]):
            self.assertAlmostEqual(before[1], PASSAGE_FLOOR)
            self.assertTrue(0 < before[0] - after[0] < 21)
            self.assertAlmostEqual(before[0] - after[0], before[2] - after[2])
            self.assertLess(abs(before[3] - after[3]), 7)

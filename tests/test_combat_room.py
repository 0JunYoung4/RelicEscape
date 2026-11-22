"""Check the new chamber's passage, sealed floor, camera, and game-loop render."""

import gc
import os
import unittest
from ctypes import byref, c_uint32
from itertools import count
from types import SimpleNamespace
from unittest.mock import Mock, patch

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_RENDER_DRIVER"] = "software"

from pico2d import pico2d as pico

import main
from lower_caves import COMBAT_CEILING_Y, COMBAT_LEFT_WALL, COMBAT_PLATFORMS, COMBAT_RIGHT_WALL, COMBAT_TERRAIN, COMBAT_WIDTH, GALLERY_WIDTH, LowerCaves
from player import Player


class CombatRoomTests(unittest.TestCase):
    def setUp(self):
        pico.open_canvas(960, 540)
        self.cave = SimpleNamespace(width=960, height=540, shaft=SimpleNamespace(w=4096))
        self.lower = LowerCaves(self.cave)
        self.player = Player(130, 0, GALLERY_WIDTH)
        self.camera = main.Camera(960, GALLERY_WIDTH)

    def tearDown(self):
        del self.lower, self.player
        gc.collect()
        pico.close_canvas()

    def step(self, direction=0, dt=1 / 60):
        self.lower.update(self.player, self.camera, dt, interact=False, direction=direction,
                          running=False, jump_pressed=False, jump_held=False,
                          crouching=False, attack_pressed=False)

    def test_gallery_right_exit_enters_from_left_and_can_return_with_relic(self):
        self.lower.room, self.lower.has_relic = "gallery", True
        self.lower.enter(self.player, self.camera)
        self.player.x = GALLERY_WIDTH - 100
        self.step(1, .05)
        self.assertEqual((self.lower.room, self.player.x), ("combat", 130))
        self.assertEqual(self.player.world_width, COMBAT_WIDTH)
        self.assertTrue(self.lower.has_relic)
        self.assertIsNone(self.lower.target(self.player))
        self.step(1, .3)
        self.assertEqual(self.lower.room, "combat")
        self.assertGreater(self.player.x, 130)
        self.player.x = 100
        self.step(-1, .05)
        self.assertEqual((self.lower.room, self.player.facing), ("gallery", -1))
        self.assertEqual(self.player.x, GALLERY_WIDTH - 130)
        self.assertTrue(self.lower.has_relic)

    def test_closed_floor_and_entry_ceiling_and_right_wall_are_solid(self):
        self.lower.room = "combat"
        self.lower.enter(self.player, self.camera)
        self.player.update(0, False, 0, jump_pressed=True)
        for _ in range(20):
            self.player.update(0, False, 1 / 60)
            self.assertLessEqual(self.player.get_hitbox()[3], COMBAT_TERRAIN[0][1])
        gap_x = (COMBAT_PLATFORMS[0][2] + COMBAT_PLATFORMS[1][0]) / 2
        self.assertTrue(self.player.recover_at(gap_x, 300, 0))
        for _ in range(90):
            self.step()
        self.assertEqual((self.player.y, self.player.grounded), (0, True))
        self.assertTrue(self.player.recover_at(COMBAT_RIGHT_WALL - 60, 0, 0))
        for _ in range(30):
            self.step(1)
        self.assertEqual(self.player.get_hitbox()[2], COMBAT_TERRAIN[1][0])

    def test_camera_keeps_exploration_scale_and_follows_high_positions(self):
        self.lower.room = "combat"
        self.lower.enter(self.player, self.camera)
        base = self.camera.y
        self.assertTrue(self.player.teleport_to(960, 650, 0))
        self.lower.follow_camera(self.player, self.camera)
        self.assertGreater(self.camera.y, base)
        self.assertEqual(self.camera.zoom, self.camera.normal_zoom)
        self.assertLessEqual(self.camera.world_to_screen(960, COMBAT_CEILING_Y)[1], 540)
        self.player.recover_at(960, 0, 0)
        self.lower.follow_camera(self.player, self.camera)
        self.assertEqual(self.camera.y, base)

    def test_both_straight_walls_stop_the_body_at_each_height_and_allow_wall_jumps(self):
        self.lower.room = "combat"
        self.lower.enter(self.player, self.camera)
        for direction, wall in ((-1, COMBAT_LEFT_WALL), (1, COMBAT_RIGHT_WALL)):
            for height in (500, 700, 900):
                with self.subTest(direction=direction, height=height):
                    self.assertTrue(self.player.recover_at(wall - direction * 80, height, 0))
                    self.player.update(direction, False, .3)
                    box = self.player.get_hitbox()
                    self.assertAlmostEqual(box[0] if direction < 0 else box[2], wall)
                    self.assertFalse(self.player._overlaps_terrain())
            self.assertTrue(self.player.recover_at(wall - direction * 20, 600, 0))
            start = self.player.x
            self.player.update(direction, False, .03, jump_pressed=True)
            self.assertGreater((self.player.x - start) * -direction, 0)
            self.assertGreater(self.player.vertical_speed, 0)

    def test_square_doorway_can_be_crossed_standing_in_both_directions(self):
        self.lower.room = "combat"
        self.lower.enter(self.player, self.camera)
        self.player.update(1, False, .7)
        self.assertGreater(self.player.get_hitbox()[0], COMBAT_LEFT_WALL)
        self.assertEqual((self.player.y, self.player.crouch_time), (0, 0))
        self.player.update(-1, False, .7)
        self.assertLess(self.player.get_hitbox()[2], COMBAT_LEFT_WALL)
        self.assertEqual((self.player.y, self.player.crouch_time), (0, 0))

    def test_all_three_platforms_support_a_landing(self):
        self.lower.room = "combat"
        self.lower.enter(self.player, self.camera)
        for left, _, right, top in COMBAT_PLATFORMS:
            with self.subTest(top=top, left=left):
                self.assertTrue(self.player.recover_at((left + right) / 2, top + 200, 0))
                for _ in range(90):
                    self.step()
                self.assertEqual((self.player.y, self.player.grounded), (top, True))

    def test_ground_jump_touches_each_side_and_wall_jump_climbs_it(self):
        self.lower.room = "combat"
        self.lower.enter(self.player, self.camera)
        for fps in (30, 60, 120):
            for platform, direction in ((COMBAT_PLATFORMS[0], -1),
                                        (COMBAT_PLATFORMS[2], 1)):
                with self.subTest(fps=fps, direction=direction):
                    edge = platform[2] if direction < 0 else platform[0]
                    self.assertTrue(self.player.recover_at(edge - direction * 21, 0, 0))
                    wall_jumped = False
                    for frame in range(3 * fps):
                        second = (not wall_jumped and self.player.wall_direction == direction
                                  and self.player.vertical_speed <= 50 and self.player.y > 190)
                        wall_jumped |= second
                        movement = direction if self.player.y > 180 or wall_jumped else 0
                        self.player.update(movement, True, 1 / fps,
                                           jump_pressed=frame == 0 or second, jump_held=True)
                        if self.player.grounded and self.player.y == platform[3]:
                            break
                    self.assertTrue(wall_jumped)
                    self.assertEqual((self.player.y, self.player.grounded), (platform[3], True))
                    self.assertFalse(self.player._overlaps_terrain())

    def test_jump_route_reaches_long_center_from_both_sides_and_returns(self):
        self.lower.room = "combat"
        self.lower.enter(self.player, self.camera)
        left, center, right = COMBAT_PLATFORMS
        for fps in (30, 60, 120):
            for start_x, start_y, direction, target in (
                (left[2] - 25, left[3], 1, center),
                (right[0] + 25, right[3], -1, center),
                (center[2] - 25, center[3], 1, right),
            ):
                with self.subTest(fps=fps, target=target, direction=direction):
                    self.assertTrue(self.player.recover_at(start_x, start_y, 0))
                    for frame in range(2 * fps):
                        target_x = (target[0] + target[2]) / 2
                        movement = direction if (target_x - self.player.x) * direction > 0 else 0
                        self.player.update(movement, True, 1 / fps, jump_pressed=frame == 0,
                                           jump_held=frame / fps < .25)
                        if frame > 0 and self.player.grounded and self.player.y == target[3]:
                            break
                    self.assertEqual((self.player.y, self.player.grounded), (target[3], True))
                    self.assertFalse(self.player._overlaps_terrain())

    def test_game_loop_clears_old_room_anchor_and_hides_the_lower_shaft(self):
        players, rooms, travels, samples = [], [], [], []
        sequence = Mock(active=True, stood_up=True)
        event_frames = count()
        real_travel = main.RelicTravel

        def make_player(*args, **kwargs):
            player = Player(*args, **kwargs)
            players.append(player)
            return player

        def make_room(cave):
            room = LowerCaves(cave)
            room.room, room.has_relic = "gallery", True
            rooms.append(room)
            return room

        def make_travel():
            travel = real_travel()
            travels.append(travel)
            return travel

        def read_events():
            frame = next(event_frames)
            if frame == 1:
                players[0].x = GALLERY_WIDTH - 100
                travels[0].place_or_recall(players[0], 0)
            return [pico.Event(pico.SDL_QUIT)] if frame == 3 else []

        def record_frame():
            if not rooms or rooms[0].room != "combat":
                return
            colors = []
            for x, y in ((480, 490), (200, 430), (480, 300)):
                pixel = c_uint32()
                self.assertEqual(pico.SDL_RenderReadPixels(pico.renderer, pico.SDL_Rect(x, y, 1, 1),
                                                         pico.SDL_PIXELFORMAT_ARGB8888, byref(pixel), 4), 0)
                colors.append(pixel.value & 0xFFFFFF)
            samples.append(colors)

        with patch.object(main, "Player", side_effect=make_player), \
                patch.object(main, "LowerCaves", side_effect=make_room) as room_factory, \
                patch.object(main, "RelicTravel", side_effect=make_travel), \
                patch.object(main, "SigilApproach", return_value=sequence), \
                patch.object(main, "read_movement", return_value=(1, False, False)), \
                patch.object(main, "perf_counter", side_effect=count(step=1 / 60)), \
                patch.object(main, "sleep"), \
                patch.object(pico, "SDL_GetKeyboardFocus", return_value=True), \
                patch.object(pico, "get_events", side_effect=read_events), \
                patch.object(pico, "update_canvas", side_effect=record_frame):
            self.assertIsNone(main.run_opening_cave(False))
        self.assertEqual(rooms[0].room, "combat")
        self.assertTrue(rooms[0].has_relic)
        self.assertIsNone(travels[0].anchor)
        self.assertEqual(len(samples), 2)
        for shaft, floor, backdrop in samples:
            self.assertEqual(shaft, 0)
            self.assertNotEqual(floor, 0)
            self.assertNotEqual(backdrop, 0)
        sequence.reset_mock()
        room_factory.reset_mock()
        players.clear()
        rooms.clear()
        travels.clear()
        gc.collect()

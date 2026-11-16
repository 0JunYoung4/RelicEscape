"""Verify the test room's damage and restart through its normal frame loop."""

import os
import unittest
from ctypes import byref, c_uint32
from itertools import count
from unittest.mock import patch

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_RENDER_DRIVER"] = "software"

import main
from pico2d import pico2d as pico
from player import Player


class HealthTests(unittest.TestCase):
    def test_spike_return_and_restart_happen_under_a_black_screen(self):
        spike = main.TEST_SPIKES[0]
        safe_x = spike.left - 150
        player = None
        frames = []
        visible = {}
        event_frame = count()

        def create_player(*args, **kwargs):
            nonlocal player
            player = Player(*args, **kwargs)
            return player

        def read_events():
            frame = next(event_frame)
            if frame == 0:
                player.teleport_to(safe_x, main.GROUND_Y, 0.0)
            if frame in (1, 37, 73, 109, 196):
                player.teleport_to(spike.left + 30, main.GROUND_Y, 0.0)
            key = {
                0: pico.SDLK_e, 195: pico.SDLK_e, 199: pico.SDLK_r, 201: pico.SDLK_ESCAPE,
            }.get(frame)
            if key is None:
                return []
            event = pico.Event(pico.SDL_KEYDOWN)
            event.key = key
            return [event]

        def record_scene(player, camera, *args, **kwargs):
            health = kwargs["health"]
            frames.append((health.current, player.x, player.y, kwargs["relic_center"]))
            pico.SDL_SetRenderDrawColor(pico.renderer, 255, 255, 255, 255)
            pico.SDL_RenderClear(pico.renderer)

        def record_visible_pixels():
            frame = len(frames) - 1
            if frame not in (0, 5, 12, 22, 33, 48, 84, 124, 160, 170, 178, 190, 199):
                return
            pixels = []
            for x, y in ((60, 29), (main.SCREEN_WIDTH - 1, main.SCREEN_HEIGHT - 1)):
                pixel = c_uint32()
                self.assertEqual(pico.SDL_RenderReadPixels(
                    pico.renderer, pico.SDL_Rect(x, y, 1, 1), pico.SDL_PIXELFORMAT_ARGB8888,
                    byref(pixel), 4,
                ), 0)
                pixels.append(pixel.value & 0xFFFFFF)
            visible[frame] = pixels

        with patch.object(main, "Player", side_effect=create_player), \
                patch.object(main, "configure_display", return_value=False), \
                patch.object(main, "run_title", return_value=False), \
                patch.object(pico, "get_events", side_effect=read_events), \
                patch.object(pico, "SDL_GetKeyboardFocus", return_value=True), \
                patch.object(pico, "update_canvas", side_effect=record_visible_pixels), \
                patch.object(main, "read_movement", return_value=(0, False, False)), \
                patch.object(main, "perf_counter", side_effect=count(step=1 / 120)), \
                patch.object(main, "sleep"), \
                patch.object(main, "draw_scene", side_effect=record_scene):
            main.main()

        self.assertEqual([frames[i][0] for i in (0, 1, 36, 37, 73, 109)], [100, 75, 75, 50, 25, 0])
        for hit, returned in ((1, 12), (37, 48), (73, 84)):
            self.assertEqual(frames[hit][1], spike.left + 30)
            self.assertEqual(frames[returned - 1][1], spike.left + 30)
            self.assertEqual(frames[returned][1:3], (safe_x, main.GROUND_Y))
            self.assertIsNotNone(frames[returned][3])
            self.assertEqual(visible[returned], [0, 0])
        self.assertTrue(0 < visible[5][1] < visible[0][1])
        self.assertTrue(0 < visible[22][1] < visible[33][1])

        self.assertEqual(frames[124][:2], (0, spike.left + 30))
        self.assertEqual(visible[124][1], 0xFFFFFF)
        self.assertTrue(0 < visible[160][1] < 0xFFFFFF)
        self.assertEqual(frames[170], (100, *main.TEST_SPAWN[:2], None))
        self.assertEqual(visible[170], [0, 0])
        self.assertTrue(0 < visible[178][1] < visible[190][1])

        self.assertEqual(frames[196][0], 75)
        self.assertIsNotNone(frames[196][3])
        self.assertEqual(frames[199], (100, *main.TEST_SPAWN[:2], None))
        self.assertEqual(visible[199][1], 0xFFFFFF)

    def test_low_passage_accepts_crawling_from_either_side(self):
        pico.open_canvas(main.SCREEN_WIDTH, main.SCREEN_HEIGHT)
        try:
            player = Player(main.TEST_SPAWN[0], main.GROUND_Y, main.WORLD_WIDTH, main.TEST_TERRAIN)
            left, _, right, _ = main.TEST_LOW_PASSAGE
            for start, end, direction in ((left, right, 1), (right, left, -1)):
                with self.subTest(direction=direction):
                    self.assertTrue(player.teleport_to(start - 80 * direction, main.GROUND_Y, 0))
                    for _ in range(40):
                        player.update(direction, False, 1 / 60)
                    self.assertLess((player.x - start) * direction, 0)

                    self.assertTrue(player.teleport_to(start - 80 * direction, main.GROUND_Y, 0))
                    for _ in range(280):
                        player.update(direction, False, 1 / 60, crouch_held=True)
                    self.assertGreater((player.x - end) * direction, 50)
                    for _ in range(15):
                        player.update(0, False, 1 / 60)
                    self.assertEqual(player.crouch_time, 0)
        finally:
            pico.close_canvas()

"""Check the sliding opening reveals only the passage and preserves SDL clipping."""

import gc
import os
import unittest
from ctypes import byref, c_ubyte
from types import SimpleNamespace

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_RENDER_DRIVER"] = "software"

from pico2d import pico2d as pico

from lower_caves import (COMBAT_CENTER_X, COMBAT_COVER_THICKNESS, COMBAT_EXIT_LEFT,
                         COMBAT_EXIT_RIGHT, COMBAT_WIDTH, LowerCaves)
from main import Camera


class CombatExitArtTests(unittest.TestCase):
    def setUp(self):
        pico.open_canvas(960, 540)
        self.room = LowerCaves(SimpleNamespace(width=960, height=540, shaft=SimpleNamespace(w=4096)))
        self.room.room = "combat"
        self.room.shaft_visibility = 1
        self.camera = Camera(960, COMBAT_WIDTH, zoom=.5, y=-400)

    def tearDown(self):
        pico.SDL_RenderSetClipRect(pico.renderer, None)
        del self.room
        gc.collect()
        pico.close_canvas()

    def render(self, progress):
        self.room.exit_progress = progress
        pico.clear_canvas()
        self.room.draw(self.camera)
        self.room.draw_combat_exit(self.camera)

    def pixel(self, x, y):
        sx, sy = self.camera.world_to_screen(x, y)
        point = pico.SDL_Rect(round(sx), 539 - round(sy), 1, 1)
        pixel = (c_ubyte * 4)()
        self.assertEqual(pico.SDL_RenderReadPixels(pico.renderer, byref(point),
                         pico.SDL_PIXELFORMAT_RGBA32, pixel, 4), 0)
        return tuple(pixel[:3])

    def test_closed_partial_and_open_passage_reveal_left_to_right_only(self):
        left, right = COMBAT_EXIT_LEFT, COMBAT_EXIT_RIGHT
        for progress, left_visible, right_visible in ((0, False, False), (.5, True, False),
                                                     (1, True, True)):
            with self.subTest(progress=progress):
                self.render(progress)
                self.assertEqual(max(self.pixel(left + 45, -180)) > 4, left_visible)
                self.assertEqual(max(self.pixel(right - 45, -180)) > 4, right_visible)
                for x in (left - 100, right + 100):
                    self.assertEqual(self.pixel(x, -180), (0, 0, 0))
                for x in (30, COMBAT_WIDTH - 30):
                    self.assertEqual(self.pixel(x, 400), (0, 0, 0))

    def test_passage_render_restores_the_previous_renderer_clip(self):
        self.room.exit_progress = .5
        self.room.draw_combat_exit(self.camera)
        self.assertFalse(pico.SDL_RenderIsClipEnabled(pico.renderer))
        before = pico.SDL_Rect(100, 120, 500, 300)
        pico.SDL_RenderSetClipRect(pico.renderer, byref(before))
        self.room.draw_combat_exit(self.camera)
        after = pico.SDL_Rect()
        pico.SDL_RenderGetClipRect(pico.renderer, byref(after))
        self.assertTrue(pico.SDL_RenderIsClipEnabled(pico.renderer))
        self.assertEqual((after.x, after.y, after.w, after.h), (100, 120, 500, 300))

    def test_shaft_shoulders_blend_across_the_lid_depth(self):
        self.camera = Camera(960, COMBAT_WIDTH, zoom=.8, y=-415)
        self.camera.follow(COMBAT_CENTER_X)
        self.render(1)
        seam = -COMBAT_COVER_THICKNESS
        for offsets in (range(-150, -100, 4), range(100, 151, 4)):
            contrast = []
            for offset in offsets:
                x = COMBAT_CENTER_X + offset
                upper, lower = self.pixel(x, seam + 3), self.pixel(x, seam - 4)
                contrast.append(max(abs(a - b) for a, b in zip(upper, lower)))
            # Local foliage may be sharp; a hard cut produces a jump across
            # the entire shoulder at the old join between its two layers.
            self.assertLess(sum(contrast) / len(contrast), 18)

    def test_opening_stays_dark_until_the_player_approaches_then_fades_in(self):
        self.room.shaft_visibility = 0
        player = SimpleNamespace(x=COMBAT_EXIT_LEFT - 400, y=0)
        self.room.exit_progress = 1
        for _ in range(60):
            self.room.update_effects(1 / 60, player)
        self.assertEqual(self.room.shaft_visibility, 0)
        self.render(1)
        self.assertEqual(self.pixel(COMBAT_EXIT_LEFT + 45, -180), (0, 0, 0))
        player.x = (COMBAT_EXIT_LEFT + COMBAT_EXIT_RIGHT) / 2
        self.room.update_effects(1 / 60, player)
        self.assertGreater(self.room.shaft_visibility, 0)
        self.assertLess(self.room.shaft_visibility, .1)
        for _ in range(60):
            self.room.update_effects(1 / 60, player)
        self.assertEqual(self.room.shaft_visibility, 1)
        self.render(1)
        self.assertGreater(max(self.pixel(COMBAT_EXIT_LEFT + 45, -180)), 4)

    def test_closed_lid_and_high_platform_do_not_reveal_the_shaft(self):
        player = SimpleNamespace(x=(COMBAT_EXIT_LEFT + COMBAT_EXIT_RIGHT) / 2, y=0)
        self.room.shaft_visibility = 0
        self.room.exit_progress = .5
        self.room.update_effects(1, player)
        self.assertEqual(self.room.shaft_visibility, 0)
        self.room.exit_progress = 1
        player.y = 568
        self.room.update_effects(1, player)
        self.assertEqual(self.room.shaft_visibility, 0)


if __name__ == "__main__":
    unittest.main()

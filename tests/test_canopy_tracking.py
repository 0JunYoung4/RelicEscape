"""Regress screen-pinned ceiling vines and camera changes near the roof."""

import gc
import os
import unittest
from ctypes import c_ubyte
from types import SimpleNamespace

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_RENDER_DRIVER"] = "software"

from pico2d import pico2d as pico

from lower_caves import COMBAT_CEILING_Y, GALLERY_WIDTH, LowerCaves
from main import Camera
from moss_art import MossCaveArt
from relic_shrine import RelicShrine


class CanopyTrackingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pico.open_canvas(960, 540)
        cls.art = MossCaveArt(960, 540)
        cls.shrine = RelicShrine(540)

    @classmethod
    def tearDownClass(cls):
        del cls.art, cls.shrine
        gc.collect()
        pico.close_canvas()

    def setUp(self):
        self.room = LowerCaves.__new__(LowerCaves)
        self.room.cave = SimpleNamespace(width=960, height=540)
        self.room.art = self.art
        self.room.shrine = self.shrine
        self.room.has_relic = True
        self.room.room = "gallery"
        self.room.passage_time = None
        self.room.exit_progress = 0
        self.camera = Camera(960, GALLERY_WIDTH, zoom=.5)
        self.camera.x = 2040

    def render_foreground(self):
        pico.SDL_SetRenderDrawColor(pico.renderer, 61, 91, 111, 255)
        pico.SDL_RenderClear(pico.renderer)
        self.room.draw_foreground(self.camera)
        pixels = (c_ubyte * (960 * 540 * 4))()
        self.assertEqual(pico.SDL_RenderReadPixels(pico.renderer, None,
                         pico.SDL_PIXELFORMAT_RGBA32, pixels, 960 * 4), 0)
        return bytes(pixels)

    def assert_pan_matches(self, dx, dy):
        before = self.render_foreground()
        self.camera.x += dx / self.camera.zoom
        self.camera.y += dy / self.camera.zoom
        after = self.render_foreground()
        total_error, samples = 0, 0
        for row in range(540 - dy):
            start = (row * 960 + dx) * 4
            end = (row + 1) * 960 * 4
            shifted = (row + dy) * 960 * 4
            total_error += sum(abs(a - b) for a, b in
                               zip(before[start:end], after[shifted:shifted + end - start]))
            samples += end - start
        # SDL can sample adjacent texels along a few triangle edges after a pan.
        self.assertLess(total_error / samples, .02, "Ceiling moved relative to the world")

    def test_canopy_stays_on_same_world_points_when_camera_pans(self):
        for room in ("gallery", "combat"):
            with self.subTest(room=room):
                self.room.room = room
                self.camera.x, self.camera.y = 2040, 100
                self.assert_pan_matches(32, 40)

    def test_ceiling_above_view_does_not_add_screen_edge_vines(self):
        for room in ("gallery", "combat"):
            with self.subTest(room=room):
                self.room.room = room
                self.camera.y = -1000
                pixels = self.render_foreground()
                self.assertEqual(pixels, bytes((61, 91, 111, 255)) * (960 * 540))

    def test_crossing_former_screen_threshold_does_not_snap_canopy(self):
        self.room.room = "combat"
        self.camera.y = COMBAT_CEILING_Y - 540 * 1.2 / self.camera.zoom - 2
        self.assert_pan_matches(0, 2)

    def test_camera_tracks_character_height_without_ceiling_limit(self):
        player = SimpleNamespace(x=3200, y=0)
        for room in ("gallery", "combat"):
            with self.subTest(room=room):
                self.room.room = room
                for height in (0, 242, 364, 650, 850):
                    player.y = height
                    self.room.follow_camera(player, self.camera)
                    expected = min(height * .5 + 108, 216)
                    self.assertAlmostEqual(self.camera.world_to_screen(player.x, height)[1], expected)
                    self.assertEqual(self.camera.zoom, .5)


if __name__ == "__main__":
    unittest.main()

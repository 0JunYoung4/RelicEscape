"""Keep combat atmosphere inside the room without leaking SDL state or tint."""
import gc
import os
import unittest
from ctypes import byref, c_ubyte

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_RENDER_DRIVER"] = "software"

from pico2d import pico2d as pico
from combat_scenery import COMBAT_BACKGROUND_TINT
from lower_caves import COMBAT_CEILING_Y, COMBAT_LEFT_WALL, COMBAT_RIGHT_WALL, COMBAT_WIDTH
from main import Camera
from moss_art import MossCaveArt


class CombatSceneryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pico.open_canvas(960, 540)
        cls.art = MossCaveArt(960, 540)
        cls.scenery = cls.art.combat_scenery()

    @classmethod
    def tearDownClass(cls):
        del cls.scenery, cls.art
        gc.collect()
        pico.close_canvas()

    def setUp(self):
        pico.SDL_RenderSetClipRect(pico.renderer, None)
        self.camera = Camera(960, COMBAT_WIDTH, zoom=.5, y=-216)

    def pixels(self):
        pixels = (c_ubyte * (960 * 540 * 4))()
        self.assertEqual(pico.SDL_RenderReadPixels(pico.renderer, None,
                         pico.SDL_PIXELFORMAT_RGBA32, pixels, 960 * 4), 0)
        return bytes(pixels)

    def test_combat_tint_does_not_change_the_shared_gallery_background(self):
        self.art.draw_background(self.camera)
        before = self.pixels()
        self.art.draw_background(self.camera, tint=COMBAT_BACKGROUND_TINT)
        self.assertNotEqual(before, self.pixels())
        self.art.draw_background(self.camera)
        self.assertEqual(before, self.pixels())

    def test_scenery_never_lights_or_covers_the_lower_shaft(self):
        pico.SDL_SetRenderDrawColor(pico.renderer, 25, 40, 52, 255)
        pico.SDL_RenderClear(pico.renderer)
        before = self.pixels()
        self.scenery.draw_background(self.camera, COMBAT_LEFT_WALL, COMBAT_RIGHT_WALL,
                                      COMBAT_CEILING_Y)
        self.scenery.draw_floor_plants(self.camera, COMBAT_LEFT_WALL, COMBAT_RIGHT_WALL,
                                        COMBAT_CEILING_Y)
        self.scenery.draw_foreground(self.camera, COMBAT_LEFT_WALL, COMBAT_RIGHT_WALL,
                                      COMBAT_CEILING_Y)
        after = self.pixels()
        self.assertNotEqual(before, after)
        # World y<0 is below screen row 432 with this camera.
        self.assertEqual(before[433 * 960 * 4:], after[433 * 960 * 4:])
        self.camera.y = -1400
        before = self.pixels()
        self.scenery.draw_background(self.camera, COMBAT_LEFT_WALL, COMBAT_RIGHT_WALL,
                                      COMBAT_CEILING_Y)
        self.scenery.draw_floor_plants(self.camera, COMBAT_LEFT_WALL, COMBAT_RIGHT_WALL,
                                        COMBAT_CEILING_Y)
        self.scenery.draw_foreground(self.camera, COMBAT_LEFT_WALL, COMBAT_RIGHT_WALL,
                                      COMBAT_CEILING_Y)
        self.assertEqual(before, self.pixels())

    def test_background_and_foreground_restore_the_callers_clip_and_blend(self):
        clip = pico.SDL_Rect(180, 100, 480, 300)
        pico.SDL_RenderSetClipRect(pico.renderer, byref(clip))
        pico.SDL_SetRenderDrawBlendMode(pico.renderer, pico.SDL_BLENDMODE_ADD)
        for draw in (self.scenery.draw_background, self.scenery.draw_floor_plants,
                     self.scenery.draw_foreground):
            draw(self.camera, COMBAT_LEFT_WALL, COMBAT_RIGHT_WALL, COMBAT_CEILING_Y)
            actual = pico.SDL_Rect()
            pico.SDL_RenderGetClipRect(pico.renderer, byref(actual))
            self.assertTrue(pico.SDL_RenderIsClipEnabled(pico.renderer))
            self.assertEqual((actual.x, actual.y, actual.w, actual.h), (180, 100, 480, 300))
            blend = pico.SDL_BlendMode()
            pico.SDL_GetRenderDrawBlendMode(pico.renderer, byref(blend))
            self.assertEqual(blend.value, pico.SDL_BLENDMODE_ADD)
        pico.SDL_RenderSetClipRect(pico.renderer, None)
        pico.SDL_SetRenderDrawBlendMode(pico.renderer, pico.SDL_BLENDMODE_BLEND)

    def test_new_foreground_tracks_world_points_during_a_camera_pan(self):
        def foreground():
            pico.SDL_SetRenderDrawColor(pico.renderer, 61, 91, 111, 255)
            pico.SDL_RenderClear(pico.renderer)
            self.scenery.draw_foreground(self.camera, COMBAT_LEFT_WALL,
                                          COMBAT_RIGHT_WALL, COMBAT_CEILING_Y)
            return self.pixels()

        self.camera.x, self.camera.y = 0, 300
        before = foreground()
        self.assertNotEqual(before, bytes((61, 91, 111, 255)) * (960 * 540))
        self.camera.x += 32 / self.camera.zoom
        self.camera.y += 40 / self.camera.zoom
        after = foreground()
        error = samples = 0
        for row in range(500):
            start, end = (row * 960 + 32) * 4, (row + 1) * 960 * 4
            shifted = (row + 40) * 960 * 4
            error += sum(abs(a - b) for a, b in zip(before[start:end],
                         after[shifted:shifted + end - start]))
            samples += end - start
        self.assertLess(error / samples, .02)


if __name__ == "__main__":
    unittest.main()

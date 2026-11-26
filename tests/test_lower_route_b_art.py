"""Check the new B wall covers the deep relic view and the upper platform camera."""

import gc
import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("SDL_RENDER_DRIVER", "software")

from pico2d import pico2d as pico
from PIL import ImageChops, ImageStat

from lower_route_b_art import LowerRouteBArt
from lower_route_b_layout import BOTTOM, TOP, WIDTH
from lower_route_b_scenery import LowerRouteBScenery
from main import Camera
from tools.preview_lower_route_a import read_render


class LowerRouteBArtTests(unittest.TestCase):
    def test_c_arch_does_not_pop_when_camera_crosses_zero(self):
        pico.open_canvas(960, 540)
        art = LowerRouteBArt()
        camera = Camera(960, WIDTH, y=93.2)
        try:
            frames = []
            for camera.x in (-.001, .001):
                pico.clear_canvas()
                art.draw_depth(camera, 540, -1600, 5900)
                frames.append(read_render(0, 0, 960, 540))
            changed = ImageChops.difference(*frames)
            # Allow fractional-texel rounding, while rejecting an entire arch disappearing.
            mean_change = sum(ImageStat.Stat(changed).mean) / 3
            self.assertLess(mean_change, .15)
        finally:
            del art
            gc.collect()
            pico.close_canvas()

    def test_wall_covers_below_second_rail_at_every_normal_camera_zoom(self):
        pico.open_canvas(960, 540)
        scenery = LowerRouteBScenery()
        camera = Camera(960, WIDTH)
        try:
            for camera.zoom in (.4, .5, .65):
                for camera.x in (700, WIDTH - camera.view_width):
                    for camera.y in (BOTTOM, TOP - 540 / camera.zoom):
                        with self.subTest(zoom=camera.zoom, x=camera.x, y=camera.y):
                            pico.SDL_SetRenderDrawColor(pico.renderer, 255, 0, 255, 255)
                            pico.SDL_RenderClear(pico.renderer)
                            pico.SDL_ClearError()
                            scenery.draw_background(camera)
                            self.assertFalse(pico.SDL_GetError())
                            image = read_render(0, 0, 960, 540)
                            border = [(x, y) for x in range(0, 960, 16) for y in (0, 539)]
                            border.extend((x, y) for y in range(0, 540, 16) for x in (0, 959))
                            self.assertTrue(all(image.getpixel(point) != (255, 0, 255) for point in border))
        finally:
            del scenery
            gc.collect()
            pico.close_canvas()

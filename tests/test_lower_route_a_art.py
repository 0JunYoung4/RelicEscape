"""Guard wall overscan when jumping or focusing on either end of A's lift."""

import gc
import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("SDL_RENDER_DRIVER", "software")

from pico2d import pico2d as pico

from lower_route_a_art import HEIGHT, WIDTH, LowerRouteAArt
from lower_route_connection import A_ORIGIN
from main import Camera
from tools.preview_lower_route_a import read_render


class LowerRouteAArtTests(unittest.TestCase):
    def test_wall_covers_viewport_at_both_camera_extremes_and_keeps_sdl_valid(self):
        pico.open_canvas(960, 540)
        scenery = LowerRouteAArt(A_ORIGIN)
        camera = Camera(960, A_ORIGIN[0] + WIDTH)
        try:
            for camera.zoom in (.4, .5, .65):
                for local_x in (0, WIDTH - camera.view_width):
                    for local_y in (0, HEIGHT - 540 / camera.zoom):
                        camera.x, camera.y = A_ORIGIN[0] + local_x, A_ORIGIN[1] + local_y
                        with self.subTest(zoom=camera.zoom, x=local_x, y=local_y):
                            pico.SDL_SetRenderDrawColor(pico.renderer, 255, 0, 255, 255)
                            pico.SDL_RenderClear(pico.renderer)
                            pico.SDL_ClearError()
                            scenery.draw_background(camera)
                            self.assertFalse(pico.SDL_GetError())
                            pixels = read_render(0, 0, 960, 540)
                            border = [(x, y) for x in range(0, 960, 16) for y in (0, 539)]
                            border.extend((x, y) for y in range(0, 540, 16) for x in (0, 959))
                            self.assertTrue(all(pixels.getpixel(point) != (255, 0, 255) for point in border))
        finally:
            del scenery
            gc.collect()
            pico.close_canvas()

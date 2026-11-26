"""Guard C's visible wall coverage and smooth B/C compositing."""

import gc
import os
from types import SimpleNamespace
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("SDL_RENDER_DRIVER", "software")

from PIL import ImageChops, ImageFilter, ImageStat
from pico2d import pico2d as pico

from lower_caves import LowerCaves
from lower_route_c import FLOOR, TOP, LowerRouteC
from main import Camera
from player import Player
from tools.preview_lower_route_a import read_render


class LowerRouteCArtTests(unittest.TestCase):
    def setUp(self):
        pico.open_canvas(960, 540)

    def tearDown(self):
        gc.collect()
        pico.close_canvas()

    def test_open_wall_is_filled_at_normal_camera_heights_and_zooms(self):
        route = LowerRouteC()
        camera = Camera(960, 12000)
        try:
            for camera.zoom in (.4, .5, .65):
                for camera.x in (-1600, -1100, -505):
                    for camera.y in (93.2, 290):
                        with self.subTest(zoom=camera.zoom, x=camera.x, y=camera.y):
                            pico.SDL_SetRenderDrawColor(pico.renderer, 255, 0, 255, 255)
                            pico.SDL_RenderClear(pico.renderer)
                            pico.SDL_ClearError()
                            route.draw_background(camera)
                            self.assertFalse(pico.SDL_GetError())
                            picture = read_render(0, 0, 960, 540)
                            left = max(-1130, camera.x + 12 / camera.zoom)
                            right = min(-20, camera.x + camera.view_width - 12 / camera.zoom)
                            bottom = max(FLOOR + 32, camera.y + 12 / camera.zoom)
                            top = min(TOP - 150, camera.y + 528 / camera.zoom)
                            self.assertLess(left, right)
                            self.assertLess(bottom, top)
                            for column in range(5):
                                for row in range(5):
                                    world_x = left + (right - left) * column / 4
                                    world_y = bottom + (top - bottom) * row / 4
                                    x, y = camera.world_to_screen(world_x, world_y)
                                    self.assertNotEqual(picture.getpixel((round(x), 539 - round(y))),
                                                        (255, 0, 255))
        finally:
            del route

    def test_c_arch_and_foreground_do_not_pop_at_the_b_c_camera_seam(self):
        cave = SimpleNamespace(width=960, height=540, shaft=SimpleNamespace(w=4096))
        rooms = LowerCaves(cave)
        player = Player(0, 0, 12000)
        camera = Camera(960, 12000, zoom=.5, y=93.2)
        rooms.room = "route_b"
        rooms.enter(player, camera)
        camera.y = 93.2
        frames = []
        try:
            for camera.x in (-.001, .001):
                pico.clear_canvas()
                pico.SDL_ClearError()
                rooms.draw(camera)
                rooms.draw_foreground(camera)
                self.assertFalse(pico.SDL_GetError())
                frames.append(read_render(0, 0, 960, 540))
            # Existing terrain sprites can round the subpixel camera change by one pixel.
            # Reject changes beyond that local color range, including a layer disappearing.
            before, after = frames
            brighter = ImageChops.subtract(before, after.filter(ImageFilter.MaxFilter(3)))
            darker = ImageChops.subtract(after.filter(ImageFilter.MinFilter(3)), before)
            change = ImageStat.Stat(ImageChops.lighter(brighter, darker))
            self.assertLess(sum(change.mean) / 3, .15)
        finally:
            del rooms, player

    def test_c_foreground_does_not_leak_into_the_deep_b_secret_passage_view(self):
        route = LowerRouteC()
        camera = Camera(960, 12000, zoom=.5, y=-900)
        camera.x = -505
        try:
            pico.SDL_SetRenderDrawColor(pico.renderer, 17, 29, 43, 255)
            pico.SDL_RenderClear(pico.renderer)
            before = read_render(0, 0, 960, 540)
            pico.SDL_ClearError()
            route.draw_foreground(camera)
            self.assertFalse(pico.SDL_GetError())
            after = read_render(0, 0, 960, 540)
            self.assertIsNone(ImageChops.difference(before, after).getbbox())
        finally:
            del route

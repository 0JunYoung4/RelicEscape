"""Exercise fullscreen startup, logical rendering, and the F11 window toggle."""

import ctypes
import os
import unittest
from unittest.mock import patch

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_RENDER_DRIVER"] = "software"

import main
from lighting import Lighting
from pico2d import pico2d as pico


class DisplayTests(unittest.TestCase):
    def test_relic_indicator_draws_at_the_edge_only_for_offscreen_relics(self):
        width, height = main.SCREEN_WIDTH, main.SCREEN_HEIGHT
        center_x, center_y = width // 2, height // 2
        margin, top_margin = main.RELIC_ARROW_MARGIN, main.RELIC_ARROW_TOP_MARGIN
        pico.open_canvas(width, height)
        self.addCleanup(pico.close_canvas)

        def pixel_at(x, y):
            pixel = ctypes.c_uint32()
            self.assertEqual(pico.SDL_RenderReadPixels(
                pico.renderer, pico.SDL_Rect(x, height - 1 - y, 1, 1),
                pico.SDL_PIXELFORMAT_ARGB8888, ctypes.byref(pixel), 4,
            ), 0, pico.SDL_GetError())
            return pixel.value & 0xFFFFFF

        for position, edge in (
            ((-100, center_y), (margin, center_y)),
            ((width + 100, center_y), (width - margin, center_y)),
            ((center_x, -100), (center_x, margin)),
            ((center_x, height + 100), (center_x, height - top_margin)),
            ((-center_x, height + center_y), (96, height - top_margin)),
        ):
            with self.subTest(position=position):
                pico.SDL_SetRenderDrawColor(pico.renderer, 0, 0, 0, 255)
                pico.SDL_RenderClear(pico.renderer)
                main.draw_relic_indicator(position)
                self.assertEqual(pixel_at(*edge), 0x80E7FF)

        with patch.object(pico, "SDL_RenderGeometry") as draw:
            main.draw_relic_indicator(None)
            main.draw_relic_indicator((center_x, center_y))
            main.draw_relic_indicator((width - 1, height - 1))
            draw.assert_not_called()

    def test_relic_lights_nearby_terrain_and_ambient_returns_after_recovery(self):
        pico.open_canvas(main.SCREEN_WIDTH, main.SCREEN_HEIGHT)
        self.addCleanup(pico.close_canvas)
        terrain = ((270, 200, 480, 500), (900, 200, 1110, 500))
        player = main.Player(2000, main.GROUND_Y, main.WORLD_WIDTH, terrain=terrain)
        camera = main.Camera(main.SCREEN_WIDTH, main.WORLD_WIDTH, main.CAMERA_ZOOM)
        lighting = Lighting(main.SCREEN_WIDTH, main.SCREEN_HEIGHT, main.RELIC_GLOW_IMAGE)

        def terrain_pixel(x):
            pixel = ctypes.c_uint32()
            result = pico.SDL_RenderReadPixels(
                pico.renderer, pico.SDL_Rect(x, 440, 1, 1),
                pico.SDL_PIXELFORMAT_ARGB8888, ctypes.byref(pixel), 4,
            )
            self.assertEqual(result, 0, pico.SDL_GetError())
            return tuple((pixel.value >> shift) & 255 for shift in (16, 8, 0))

        main.draw_scene(player, camera)
        original = terrain_pixel(135)
        main.draw_scene(player, camera, lighting=lighting)
        ambient = terrain_pixel(135)
        self.assertLess(sum(ambient), sum(original))

        main.draw_scene(player, camera, lighting=lighting, relic_center=(135, 125))
        nearby = terrain_pixel(135)
        self.assertGreater(nearby[2], ambient[2])
        self.assertEqual(terrain_pixel(335), ambient)

        main.draw_scene(player, camera, lighting=lighting)
        self.assertEqual(terrain_pixel(135), ambient)

    def test_modes_preserve_camera_and_textures_and_restore_larger_window(self):
        pico.open_canvas(main.SCREEN_WIDTH, main.SCREEN_HEIGHT)
        try:
            player = main.Player(400, main.GROUND_Y, main.WORLD_WIDTH)
            camera = main.Camera(main.SCREEN_WIDTH, main.WORLD_WIDTH, main.CAMERA_ZOOM)
            self.assertTrue(main.configure_display())
            for fullscreen in (True, False, True, False):
                self.assertEqual(main.set_fullscreen(fullscreen), fullscreen)
                width, height = ctypes.c_int(), ctypes.c_int()
                pico.SDL_RenderGetLogicalSize(pico.renderer, ctypes.byref(width), ctypes.byref(height))
                self.assertEqual((width.value, height.value), (main.SCREEN_WIDTH, main.SCREEN_HEIGHT))
                self.assertAlmostEqual(camera.view_width, 2880)
                if not fullscreen:
                    pico.SDL_GetWindowSize(pico.window, ctypes.byref(width), ctypes.byref(height))
                    self.assertEqual((width.value, height.value), (1280, 720))
                pico.SDL_ClearError()
                main.draw_scene(player, camera, show_hitboxes=True)
                self.assertFalse(pico.SDL_GetError())
                pico.update_canvas()
        finally:
            pico.close_canvas()

    def test_main_starts_fullscreen_and_f11_toggles_before_quit(self):
        press = pico.Event(pico.SDL_KEYDOWN)
        press.key = pico.SDLK_F11
        quit_event = pico.Event(pico.SDL_QUIT)
        with patch.object(pico, "get_events", side_effect=[[], [press], [], [quit_event]]), \
                patch.object(main, "read_movement", return_value=(0, False, False)), \
                patch.object(main, "sleep"), \
                patch.object(main, "set_fullscreen", wraps=main.set_fullscreen) as switch:
            main.main()
            self.assertEqual([call.args[0] for call in switch.call_args_list], [True, False])

    def test_escape_returns_to_title_and_enter_starts_a_fresh_run(self):
        enter, mount, toggle, escape = (pico.Event(pico.SDL_KEYDOWN) for _ in range(4))
        enter.key, mount.key, toggle.key, escape.key = (
            pico.SDLK_RETURN, pico.SDLK_e, pico.SDLK_F11, pico.SDLK_ESCAPE,
        )
        events = ([], [enter], [mount], [toggle], [escape], [], [enter], [], [escape], [], [escape])
        game_frames = []

        def record_scene(player, camera, *args, **kwargs):
            game_frames.append((player.x, kwargs["rail_relic_image"] is not None))

        with patch.object(pico, "get_events", side_effect=events), \
                patch.object(pico, "SDL_GetKeyboardFocus", return_value=True), \
                patch.object(pico, "close_canvas", wraps=pico.close_canvas) as close, \
                patch.object(main, "read_movement", return_value=(0, False, False)), \
                patch.object(main, "sleep"), \
                patch.object(main, "run_title", wraps=main.run_title) as title, \
                patch.object(main, "draw_scene", new=record_scene):
            main.main()

        self.assertEqual([call.args for call in title.call_args_list], [(True,), (False,), (False,)])
        self.assertEqual(game_frames, [(main.TEST_SPAWN[0], mounted) for mounted in (True, True, False)])
        close.assert_called_once_with()

    def test_title_animates_and_blinks_until_enter_starts_play(self):
        space, enter = (pico.Event(pico.SDL_KEYDOWN) for _ in range(2))
        space.key, enter.key = pico.SDLK_SPACE, pico.SDLK_RETURN
        events = iter(([], [space], [], [enter], [], [pico.Event(pico.SDL_QUIT)]))
        batches_read = 0
        title_frames = []
        present = pico.update_canvas

        def get_events():
            nonlocal batches_read
            batches_read += 1
            return next(events)

        def read_rect(x, y, width, height):
            pixels = (ctypes.c_ubyte * (width * height * 4))()
            result = pico.SDL_RenderReadPixels(
                pico.renderer, pico.SDL_Rect(x, y, width, height),
                pico.SDL_PIXELFORMAT_RGBA32, pixels, width * 4,
            )
            self.assertEqual(result, 0, pico.SDL_GetError())
            return bytes(pixels)

        def record_canvas():
            if 1 <= batches_read <= 3:
                prompt_rows = read_rect(350, 470, 260, 40)
                crack = read_rect(460, 245, 45, 40)
                title_frames.append((max(prompt_rows[::4]), crack))
                player.assert_not_called()
            present()

        period = main.TITLE_BLINK_PERIOD
        half_blink = period / 2
        times = (
            0, 0, 0, half_blink, half_blink, period, period,
            period + 0.1, period + 0.2, period + 0.25, period + 0.25, period + 0.3,
        )
        with patch.object(main, "configure_display", return_value=False), \
                patch.object(main, "perf_counter", side_effect=times), \
                patch.object(main, "sleep"), \
                patch.object(main, "Player", wraps=main.Player) as player, \
                patch.object(main, "draw_scene", wraps=main.draw_scene) as game_scene, \
                patch.object(pico, "get_events", new=get_events), \
                patch.object(pico, "update_canvas", new=record_canvas):
            main.main()

        visible, hidden, visible_again = title_frames
        self.assertGreater(visible[0], 160)
        self.assertLess(hidden[0], 80)
        self.assertGreater(visible_again[0], 160)
        self.assertNotEqual(visible[1], hidden[1])
        player.assert_called_once()
        game_scene.assert_called_once()


if __name__ == "__main__":
    unittest.main()

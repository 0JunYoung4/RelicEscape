"""Exercise fullscreen startup, logical rendering, and the F11 window toggle."""

import ctypes
import os
import unittest
from unittest.mock import patch

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_RENDER_DRIVER"] = "software"

import main
from pico2d import pico2d as pico


class DisplayTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()

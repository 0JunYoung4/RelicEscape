"""Preserve the game's SDL input contract without timing side effects."""

from ctypes import byref
import os
import unittest
from unittest.mock import patch

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("SDL_RENDER_DRIVER", "software")

from pico2d import pico2d as pico

from input_events import poll_events


class InputEventsTests(unittest.TestCase):
    def setUp(self):
        pico.open_canvas(64, 64)
        self.addCleanup(pico.close_canvas)
        poll_events()

    def push(self, event):
        self.assertEqual(pico.SDL_PushEvent(byref(event)), 1, pico.SDL_GetError())

    def test_preserves_quit_keys_mouse_and_queue_order(self):
        quit_event = pico.SDL_Event()
        quit_event.type = pico.SDL_QUIT
        down = pico.SDL_Event()
        down.type, down.key.keysym.sym = pico.SDL_KEYDOWN, pico.SDLK_e
        up = pico.SDL_Event()
        up.type, up.key.keysym.sym = pico.SDL_KEYUP, pico.SDLK_SPACE
        motion = pico.SDL_Event()
        motion.type, motion.motion.x, motion.motion.y = pico.SDL_MOUSEMOTION, 23, 41
        button_down = pico.SDL_Event()
        button_down.type, button_down.button.button = pico.SDL_MOUSEBUTTONDOWN, 1
        button_down.button.x, button_down.button.y = 17, 29
        button_up = pico.SDL_Event()
        button_up.type, button_up.button.button = pico.SDL_MOUSEBUTTONUP, 3
        button_up.button.x, button_up.button.y = 31, 12
        wheel = pico.SDL_Event()
        wheel.type, wheel.wheel.x, wheel.wheel.y = pico.SDL_MOUSEWHEEL, -2, 4
        for event in (down, motion, button_down, up, wheel, button_up, quit_event):
            self.push(event)

        events = poll_events()
        self.assertEqual([(event.type, event.key, event.button, event.x, event.y) for event in events], [
            (pico.SDL_KEYDOWN, pico.SDLK_e, None, None, None),
            (pico.SDL_MOUSEMOTION, None, None, 23, 41),
            (pico.SDL_MOUSEBUTTONDOWN, None, 1, 17, 29),
            (pico.SDL_KEYUP, pico.SDLK_SPACE, None, None, None),
            (pico.SDL_MOUSEWHEEL, None, None, -2, 4),
            (pico.SDL_MOUSEBUTTONUP, None, 3, 31, 12),
            (pico.SDL_QUIT, None, None, None, None),
        ])
        self.assertEqual(poll_events(), [])

    def test_filters_repeated_keys_and_unsupported_events(self):
        for event_type in (pico.SDL_KEYDOWN, pico.SDL_KEYUP):
            event = pico.SDL_Event()
            event.type = event_type
            event.key.repeat, event.key.keysym.sym = 1, pico.SDLK_x
            self.push(event)
        unsupported = pico.SDL_Event()
        unsupported.type = pico.SDL_USEREVENT
        self.push(unsupported)
        self.assertEqual(poll_events(), [])

    def test_polling_has_no_delay_or_title_side_effects(self):
        with patch.object(pico, "SDL_Delay") as delay, \
                patch.object(pico, "print_fps") as fps, \
                patch.object(pico, "SDL_SetWindowTitle") as title:
            self.assertEqual(poll_events(), [])
        delay.assert_not_called()
        fps.assert_not_called()
        title.assert_not_called()


if __name__ == "__main__":
    unittest.main()

"""Check movement, jump/crouch transitions, and SDL software rendering."""

import os
import unittest
from unittest.mock import patch

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_RENDER_DRIVER"] = "software"

from pico2d import pico2d as pico

from main import CAMERA_ZOOM, GROUND_Y, SCREEN_WIDTH, WORLD_WIDTH, Camera, draw_scene, read_movement, update_hitbox_visibility
from player import CROUCH_DURATION, CROUCH_SPEED, GRAVITY, JUMP_SPEED, RUN_SPEED, TAKEOFF_DURATION, WALK_SPEED, Player


class PlayerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pico.open_canvas(960, 540)

    @classmethod
    def tearDownClass(cls):
        pico.close_canvas()

    def setUp(self):
        self.player = Player(400, GROUND_Y, WORLD_WIDTH)

    def tearDown(self):
        del self.player

    def test_anticipation_then_ascent_and_ground_contact(self):
        self.player.update(0, False, 0, jump_pressed=True)
        self.assertEqual(self.player.get_jump_frame(), 0)
        self.player.update(0, False, TAKEOFF_DURATION / 2)
        self.assertEqual(self.player.y, GROUND_Y)
        self.player.update(0, False, TAKEOFF_DURATION)
        self.assertGreater(self.player.y, GROUND_Y)
        self.assertGreater(self.player.vertical_speed, 0)
        for _ in range(120):
            self.player.update(0, False, 1 / 60)
            self.assertGreaterEqual(self.player.y, GROUND_Y)
        self.assertEqual(self.player.y, GROUND_Y)
        self.assertEqual(self.player.vertical_speed, 0)
        self.assertEqual(self.player.state, "idle")

    def test_all_eight_frames_play_once_in_order_at_different_frame_rates(self):
        expected_peak = GROUND_Y + JUMP_SPEED ** 2 / (2 * GRAVITY)
        for rate in (30, 60, 144):
            with self.subTest(rate=rate):
                self.player.update(0, False, 0, jump_pressed=True)
                frames = []
                peak = self.player.y
                for _ in range(rate * 2):
                    if self.player.state in ("jump", "land"):
                        frame = self.player.get_jump_frame()
                        if not frames or frames[-1] != frame:
                            frames.append(frame)
                    self.player.update(0, False, 1 / rate)
                    peak = max(peak, self.player.y)
                self.assertEqual(frames, list(range(8)))
                self.assertAlmostEqual(peak, expected_peak, delta=0.3)
                self.assertEqual(self.player.y, GROUND_Y)
                self.assertEqual(self.player.state, "idle")

    def test_an_airborne_jump_request_does_not_restart_the_jump(self):
        self.player.update(0, False, 0.25, jump_pressed=True)
        previous_y = self.player.y
        previous_speed = self.player.vertical_speed
        previous_time = self.player.animation_time
        self.player.update(0, False, 0.01, jump_pressed=True)
        self.assertGreater(self.player.y, previous_y)
        self.assertLess(self.player.vertical_speed, previous_speed)
        self.assertAlmostEqual(self.player.animation_time, previous_time + 0.01)

    def test_walk_run_and_camera_follow_work_during_a_jump(self):
        self.player.x = 2000
        self.player.update(1, False, 0.2, jump_pressed=True)
        self.assertAlmostEqual(self.player.x, 2000 + WALK_SPEED * 0.2)
        self.assertEqual(self.player.state, "jump")
        self.player.update(-1, True, 0.1)
        self.assertAlmostEqual(self.player.x, 2000 + WALK_SPEED * 0.2 - RUN_SPEED * 0.1)
        self.assertEqual(self.player.facing, -1)
        self.assertEqual(self.player.state, "jump")
        camera = Camera(SCREEN_WIDTH, WORLD_WIDTH, CAMERA_ZOOM)
        camera.follow(self.player.x)
        self.assertAlmostEqual(camera.world_to_screen(self.player.x, self.player.y)[0], 480)

    def test_landing_returns_to_current_movement(self):
        for direction, running, expected_state in ((0, False, "idle"), (1, False, "walk"), (1, True, "run")):
            with self.subTest(state=expected_state):
                self.player.update(direction, running, 0, jump_pressed=True)
                for _ in range(90):
                    self.player.update(direction, running, 1 / 60)
                self.assertEqual(self.player.state, expected_state)
                self.assertEqual(self.player.y, GROUND_Y)

    def test_jump_frame_bounds_and_both_directions_render(self):
        animation = self.player.animations["jump"]
        self.assertEqual(len(animation.frames), 8)
        camera = Camera(SCREEN_WIDTH, WORLD_WIDTH, CAMERA_ZOOM)
        for index, frame in enumerate(animation.frames):
            with self.subTest(frame=index):
                self.assertGreaterEqual(frame["x"], 0)
                self.assertGreaterEqual(frame["y"], 0)
                self.assertLessEqual(frame["x"] + frame["width"], animation.image.w)
                self.assertLessEqual(frame["y"] + frame["height"], animation.image.h)
                for facing in (-1, 1):
                    pico.SDL_ClearError()
                    animation.draw(400, 300, facing, 0, camera, index)
                    self.assertFalse(pico.SDL_GetError())
        self.player.update(0, False, 0, jump_pressed=True)
        for _ in range(90):
            draw_scene(self.player, camera)
            self.player.update(0, False, 1 / 60)
        self.assertEqual(self.player.state, "idle")

    def test_crouch_plays_forward_holds_and_reverses_at_different_frame_rates(self):
        for rate in (30, 60, 144):
            with self.subTest(rate=rate):
                self.player.update(0, False, 0, crouch_held=True)
                forward = [self.player.get_crouch_frame()]
                for _ in range(rate):
                    self.player.update(0, False, 1 / rate, crouch_held=True)
                    frame = self.player.get_crouch_frame()
                    if forward[-1] != frame:
                        forward.append(frame)
                self.assertEqual(forward, list(range(4)))
                self.assertEqual(self.player.state, "crouch")
                self.assertEqual(self.player.y, GROUND_Y)
                backward = [3]
                for _ in range(rate):
                    self.player.update(0, False, 1 / rate)
                    frame = self.player.get_crouch_frame()
                    if backward[-1] != frame:
                        backward.append(frame)
                self.assertEqual(backward, list(range(3, -1, -1)))
                self.assertEqual(self.player.state, "idle")

    def test_reversing_a_partial_crouch_does_not_restart_it(self):
        self.player.update(0, False, CROUCH_DURATION * 0.6, crouch_held=True)
        self.player.update(0, False, CROUCH_DURATION * 0.2)
        self.assertAlmostEqual(self.player.crouch_time, CROUCH_DURATION * 0.4)
        self.player.update(0, False, CROUCH_DURATION * 0.2, crouch_held=True)
        self.assertAlmostEqual(self.player.crouch_time, CROUCH_DURATION * 0.6)

    def test_fast_crouch_and_stand_each_finish_in_fifteen_hundredths(self):
        self.player.update(0, False, 0.15, crouch_held=True)
        self.assertEqual(self.player.get_crouch_frame(), 3)
        self.assertEqual(self.player.state, "crouch")
        self.player.update(0, False, 0.15)
        self.assertEqual(self.player.state, "idle")

    def test_crouch_movement_is_slow_even_with_shift(self):
        self.player.update(1, True, 0.5, crouch_held=True)
        self.assertAlmostEqual(self.player.x, 400 + CROUCH_SPEED * 0.5)
        self.assertEqual(self.player.state, "crawl")
        self.player.update(-1, False, 0.1, crouch_held=True)
        self.assertEqual(self.player.facing, -1)
        self.assertAlmostEqual(self.player.x, 400 + CROUCH_SPEED * 0.4)
        self.player.update(1, True, 100, crouch_held=True)
        self.assertEqual(self.player.x, WORLD_WIDTH - 64)
        self.assertEqual(self.player.y, GROUND_Y)

    def test_crawl_waits_for_full_crouch_and_stops_when_movement_stops(self):
        self.player.update(1, False, CROUCH_DURATION / 2, crouch_held=True)
        self.assertEqual(self.player.state, "crouch")
        self.player.update(1, False, CROUCH_DURATION / 2, crouch_held=True)
        self.assertEqual(self.player.state, "crawl")
        for _ in range(30):
            self.player.update(1, True, 1 / 60, crouch_held=True)
        self.assertGreater(self.player.animation_time, 0)
        self.player.update(0, False, 1 / 60, crouch_held=True)
        self.assertEqual(self.player.state, "crouch")
        self.assertEqual(self.player.get_crouch_frame(), 3)
        self.assertEqual(self.player.animation_time, 0)

    def test_crawl_reverses_and_stands_when_crouch_is_released(self):
        self.player.update(1, False, CROUCH_DURATION, crouch_held=True)
        self.player.update(-1, True, 0.1, crouch_held=True)
        self.assertEqual(self.player.state, "crawl")
        self.assertEqual(self.player.facing, -1)
        self.player.update(-1, False, 0.05)
        self.assertEqual(self.player.state, "crouch")
        self.player.update(0, False, CROUCH_DURATION)
        self.assertEqual(self.player.state, "idle")

    def test_crawl_returns_to_hold_at_world_edges(self):
        for x, direction in ((64, -1), (WORLD_WIDTH - 64, 1)):
            with self.subTest(direction=direction):
                self.player.x = x
                self.player.update(direction, True, CROUCH_DURATION, crouch_held=True)
                self.assertEqual(self.player.state, "crouch")
                self.assertEqual(self.player.x, x)
                self.assertEqual(self.player.animation_time, 0)

    def test_crawl_cycle_loops_and_renders_all_frames_in_both_directions(self):
        animation = self.player.animations["crawl"]
        self.assertEqual(len(animation.frames), 8)
        camera = Camera(SCREEN_WIDTH, WORLD_WIDTH, CAMERA_ZOOM)
        self.player.update(1, False, CROUCH_DURATION, crouch_held=True)
        frames = []
        for _ in range(16):
            frames.append(int(self.player.animation_time * animation.fps) % 8)
            for facing in (-1, 1):
                self.player.facing = facing
                pico.SDL_ClearError()
                draw_scene(self.player, camera)
                self.assertFalse(pico.SDL_GetError())
            self.player.update(1, False, 1 / animation.fps, crouch_held=True)
        self.assertEqual(frames, list(range(8)) * 2)
        for frame in animation.frames:
            self.assertGreaterEqual(frame["x"], 0)
            self.assertGreaterEqual(frame["y"], 0)
            self.assertLessEqual(frame["x"] + frame["width"], animation.image.w)
            self.assertLessEqual(frame["y"] + frame["height"], animation.image.h)

    def test_jump_is_blocked_until_fully_standing(self):
        self.player.update(0, False, 0.2, jump_pressed=True, crouch_held=True)
        self.assertEqual(self.player.state, "crouch")
        self.player.update(0, False, 0.05, jump_pressed=True)
        self.assertEqual(self.player.state, "crouch")
        self.assertEqual(self.player.y, GROUND_Y)
        self.player.update(0, False, CROUCH_DURATION)
        self.player.update(0, False, 0.15, jump_pressed=True)
        self.assertEqual(self.player.state, "jump")
        self.assertGreater(self.player.y, GROUND_Y)

    def test_crouch_held_in_air_starts_after_landing(self):
        self.player.update(0, False, 0.2, jump_pressed=True)
        self.player.update(0, False, 0.1, crouch_held=True)
        self.assertEqual(self.player.state, "jump")
        self.assertEqual(self.player.crouch_time, 0)
        for _ in range(90):
            self.player.update(0, False, 1 / 60, crouch_held=True)
        self.assertEqual(self.player.state, "crouch")
        self.assertEqual(self.player.get_crouch_frame(), 3)
        self.assertEqual(self.player.y, GROUND_Y)

    def test_crouch_keys_and_focus_loss(self):
        keys = [0] * 512
        with patch.object(pico, "SDL_GetKeyboardFocus", return_value=True), patch.object(pico, "SDL_GetKeyboardState", return_value=keys):
            for key in (pico.SDL_SCANCODE_S, pico.SDL_SCANCODE_DOWN):
                keys[key] = 1
                self.assertEqual(read_movement(), (0, False, True))
                keys[key] = 0
        with patch.object(pico, "SDL_GetKeyboardFocus", return_value=None):
            self.assertEqual(read_movement(), (0, False, False))

    def test_crouch_frame_bounds_and_both_directions_render(self):
        animation = self.player.animations["crouch"]
        camera = Camera(SCREEN_WIDTH, WORLD_WIDTH, CAMERA_ZOOM)
        self.assertEqual(len(animation.frames), 4)
        for index, frame in enumerate(animation.frames):
            self.assertLessEqual(frame["x"] + frame["width"], animation.image.w)
            self.assertLessEqual(frame["y"] + frame["height"], animation.image.h)
            for facing in (-1, 1):
                pico.SDL_ClearError()
                animation.draw(400, GROUND_Y, facing, 0, camera, index)
                self.assertFalse(pico.SDL_GetError())
        for crouch_held in (True, False):
            for _ in range(30):
                self.player.update(0, False, 1 / 60, crouch_held=crouch_held)
                draw_scene(self.player, camera)
        self.assertEqual(self.player.state, "idle")

    def test_hitbox_follows_position_and_changes_with_crouch(self):
        standing = self.player.get_hitbox()
        self.assertEqual(standing, (380, GROUND_Y, 420, GROUND_Y + 140))
        self.player.update(0, False, CROUCH_DURATION / 2, crouch_held=True)
        middle = self.player.get_hitbox()
        self.assertEqual(middle[1], GROUND_Y)
        self.assertGreater(middle[2] - middle[0], standing[2] - standing[0])
        self.assertLess(middle[3], standing[3])
        self.player.update(0, False, CROUCH_DURATION, crouch_held=True)
        self.assertEqual(self.player.get_hitbox(), (350, GROUND_Y, 450, GROUND_Y + 80))
        self.player.facing = -1
        self.assertEqual(self.player.get_hitbox(), (350, GROUND_Y, 450, GROUND_Y + 80))
        self.player.update(0, False, CROUCH_DURATION)
        self.player.update(1, False, 0.2, jump_pressed=True)
        left, bottom, right, top = self.player.get_hitbox()
        self.assertAlmostEqual((left + right) / 2, self.player.x)
        self.assertEqual(bottom, self.player.y)
        self.assertGreater(bottom, GROUND_Y)
        self.assertEqual(top - bottom, 140)

    def test_hitbox_overlay_is_hidden_by_default_and_projects_with_camera(self):
        camera = Camera(SCREEN_WIDTH, WORLD_WIDTH, CAMERA_ZOOM)
        self.player.x = 3200
        camera.follow(self.player.x)
        with patch.object(self.player, "draw_hitbox") as draw_hitbox:
            draw_scene(self.player, camera)
            draw_hitbox.assert_not_called()
            draw_scene(self.player, camera, show_hitboxes=True)
            draw_hitbox.assert_called_once_with(camera)
        with patch("player.draw_rectangle") as rectangle:
            self.player.draw_hitbox(camera)
            rectangle.assert_called_once()
            expected = (480 - 20 * CAMERA_ZOOM, 200 * CAMERA_ZOOM,
                        480 + 20 * CAMERA_ZOOM, 340 * CAMERA_ZOOM)
            for actual, coordinate in zip(rectangle.call_args.args[:4], expected):
                self.assertAlmostEqual(actual, coordinate)
            self.assertEqual(rectangle.call_args.args[4:], (255, 96, 80))
        for crouch_held in (True, False):
            self.player.update(0, False, CROUCH_DURATION, crouch_held=crouch_held)
            pico.SDL_ClearError()
            draw_scene(self.player, camera, show_hitboxes=True)
            self.assertFalse(pico.SDL_GetError())

    def test_hitbox_shortcut_requires_control_and_keydown(self):
        press = pico.Event(pico.SDL_KEYDOWN)
        press.key = pico.SDLK_h
        release = pico.Event(pico.SDL_KEYUP)
        release.key = pico.SDLK_h
        with patch.object(pico, "SDL_GetKeyboardFocus", return_value=True):
            for modifier in (pico.KMOD_LCTRL, pico.KMOD_RCTRL):
                with patch.object(pico, "SDL_GetModState", return_value=modifier):
                    self.assertTrue(update_hitbox_visibility([press], False))
                    self.assertFalse(update_hitbox_visibility([press], True))
                    self.assertTrue(update_hitbox_visibility([], True))
                    self.assertTrue(update_hitbox_visibility([release], True))
                    self.assertFalse(update_hitbox_visibility([press, press], False))
            with patch.object(pico, "SDL_GetModState", return_value=0):
                self.assertFalse(update_hitbox_visibility([press], False))
        with patch.object(pico, "SDL_GetKeyboardFocus", return_value=None):
            self.assertFalse(update_hitbox_visibility([press], False))

    def test_hitbox_shortcut_handles_quick_control_release_in_same_batch(self):
        def event(event_type, key):
            result = pico.Event(event_type)
            result.key = key
            return result

        for control in (pico.SDLK_LCTRL, pico.SDLK_RCTRL):
            press_control = event(pico.SDL_KEYDOWN, control)
            press_h = event(pico.SDL_KEYDOWN, pico.SDLK_h)
            release_h = event(pico.SDL_KEYUP, pico.SDLK_h)
            release_control = event(pico.SDL_KEYUP, control)
            with patch.object(pico, "SDL_GetKeyboardFocus", return_value=True), patch.object(pico, "SDL_GetModState", return_value=0):
                self.assertTrue(update_hitbox_visibility([press_control, press_h, release_h, release_control], False))
                self.assertTrue(update_hitbox_visibility([press_h, release_control], False))
                self.assertFalse(update_hitbox_visibility([press_control, release_control, press_h], False))


if __name__ == "__main__":
    unittest.main()

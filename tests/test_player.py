"""Check jump physics and actual sprite rendering with SDL's software driver."""

import os
import unittest

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_RENDER_DRIVER"] = "software"

from pico2d import pico2d as pico

from main import CAMERA_ZOOM, GROUND_Y, SCREEN_WIDTH, WORLD_WIDTH, Camera, draw_scene
from player import GRAVITY, JUMP_SPEED, RUN_SPEED, TAKEOFF_DURATION, WALK_SPEED, Player


class PlayerJumpTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()

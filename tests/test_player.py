"""Check movement, jump/crouch transitions, and SDL software rendering."""

import os
import unittest
from unittest.mock import patch

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_RENDER_DRIVER"] = "software"

from pico2d import pico2d as pico

from main import CAMERA_ZOOM, GROUND_Y, SCREEN_WIDTH, WORLD_WIDTH, Camera, draw_scene, read_movement, update_hitbox_visibility
from player import CROUCH_DURATION, CROUCH_SPEED, GRAVITY, IDLE_FLOURISH_DELAY, JUMP_SPEED, RUN_SPEED, WALK_SPEED, Player


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

    def test_sword_dust_plays_after_standing_still_and_returns_to_idle(self):
        camera = Camera(SCREEN_WIDTH, WORLD_WIDTH, CAMERA_ZOOM)
        idle = self.player.animations["idle"]
        dust = self.player.animations["idle_sword_dust"]
        self.player.update(0, False, IDLE_FLOURISH_DELAY - 0.01)
        with patch.object(idle, "draw", wraps=idle.draw) as draw_idle:
            self.player.draw(camera)
            draw_idle.assert_called_once()

        self.player.update(0, False, 0.02)
        with patch.object(dust, "draw", wraps=dust.draw) as draw_dust:
            self.player.draw(camera)
            draw_dust.assert_called_once()
            self.assertEqual(dust.frame_at(draw_dust.call_args.args[3]), 0)
            self.player.update(0, False, dust.duration - 0.02)
            self.player.draw(camera)
            self.assertEqual(dust.frame_at(draw_dust.call_args.args[3]), 23)

        self.player.update(0, False, 0.02)
        with patch.object(idle, "draw", wraps=idle.draw) as draw_idle:
            self.player.draw(camera)
            draw_idle.assert_called_once()
            self.assertEqual(draw_idle.call_args.args[3], 0.0)

    def test_sword_dust_yields_to_player_input(self):
        camera = Camera(SCREEN_WIDTH, WORLD_WIDTH, CAMERA_ZOOM)
        for direction, action, pose in (
            (-1, {}, "walk"),
            (0, {"jump_pressed": True}, "jump"),
            (0, {"attack_pressed": True}, "attack"),
            (0, {"crouch_held": True}, "crouch"),
        ):
            with self.subTest(pose=pose):
                player = Player(400, GROUND_Y, WORLD_WIDTH)
                player.update(0, False, IDLE_FLOURISH_DELAY + 0.5)
                player.update(direction, False, 1 / 60, **action)
                with patch.object(player.animations[pose], "draw") as draw:
                    player.draw(camera)
                    draw.assert_called_once()
                if pose == "attack":
                    player.update(0, False, player.animations["attack"].duration)
                    with patch.object(player.animations["idle"], "draw") as draw:
                        player.draw(camera)
                        draw.assert_called_once()

    def test_jump_ascends_on_the_input_frame_and_lands(self):
        self.player.update(0, False, 1 / 60, jump_pressed=True)
        self.assertEqual(self.player.get_jump_frame(), 1)
        self.assertGreater(self.player.y, GROUND_Y)
        self.assertGreater(self.player.vertical_speed, 0)
        for _ in range(120):
            self.player.update(0, False, 1 / 60)
            self.assertGreaterEqual(self.player.y, GROUND_Y)
        self.assertEqual(self.player.y, GROUND_Y)
        self.assertEqual(self.player.vertical_speed, 0)
        self.assertEqual(self.player.state, "idle")

    def test_jump_frames_play_once_in_order_at_different_frame_rates(self):
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
                self.assertEqual(frames, list(range(1, 8)))
                self.assertAlmostEqual(peak, expected_peak, delta=0.3)
                self.assertEqual(self.player.y, GROUND_Y)
                self.assertEqual(self.player.state, "idle")

    def test_space_hold_selects_three_distinct_jump_heights(self):
        for rate in (30, 60, 144):
            for hold, height in ((0, 90), (0.06, 90), (0.13, 145), (0.17, 145), (0.24, 202.5)):
                with self.subTest(rate=rate, hold=hold):
                    player = Player(400, GROUND_Y, WORLD_WIDTH)
                    player.update(0, False, 0, jump_pressed=True, jump_held=hold > 0)
                    elapsed = 0.0
                    peak = player.y
                    while elapsed < hold:
                        step = min(1 / rate, hold - elapsed)
                        player.update(0, False, step, jump_held=True)
                        elapsed += step
                        peak = max(peak, player.y)
                    for _ in range(rate):
                        player.update(0, False, 1 / rate, jump_held=False)
                        peak = max(peak, player.y)
                    self.assertAlmostEqual(peak - GROUND_Y, height, delta=0.3)
                    self.assertEqual(player.y, GROUND_Y)

    def test_tap_buffered_before_landing_rebounds_as_short_jump(self):
        self.player.y = GROUND_Y + 5
        self.player.vertical_speed = -200
        self.player.state = "jump"
        self.player.update(0, False, 1 / 60, jump_pressed=True, jump_held=False)
        self.player.update(0, False, 1 / 60, jump_held=False)
        self.assertEqual(self.player.state, "jump")
        self.assertEqual(self.player.y, GROUND_Y)
        peak = self.player.y
        for _ in range(60):
            self.player.update(0, False, 1 / 60, jump_held=False)
            peak = max(peak, self.player.y)
        self.assertAlmostEqual(peak - GROUND_Y, 90, delta=0.3)

    def test_an_airborne_jump_request_does_not_restart_the_jump(self):
        self.player.update(0, False, 0.25, jump_pressed=True)
        previous_y = self.player.y
        previous_speed = self.player.vertical_speed
        previous_time = self.player.animation_time
        self.player.update(0, False, 0.01, jump_pressed=True)
        self.assertGreater(self.player.y, previous_y)
        self.assertLess(self.player.vertical_speed, previous_speed)
        self.assertAlmostEqual(self.player.animation_time, previous_time + 0.01)
        for _ in range(45):
            self.player.update(0, False, 1 / 60)
        self.assertEqual(self.player.y, GROUND_Y)
        self.assertEqual(self.player.vertical_speed, 0)

    def test_jump_can_interrupt_the_landing_animation(self):
        self.player.update(0, False, 0, jump_pressed=True)
        for _ in range(60):
            self.player.update(0, False, 1 / 60)
            if self.player.state == "land":
                break
        self.assertEqual(self.player.state, "land")
        self.player.update(0, False, 1 / 60, jump_pressed=True)
        self.assertEqual(self.player.state, "jump")
        self.assertGreater(self.player.y, GROUND_Y)
        self.assertGreater(self.player.vertical_speed, 0)

    def test_jump_pressed_just_before_landing_launches_from_floor_or_platform(self):
        for surface in (GROUND_Y, GROUND_Y + 60):
            with self.subTest(surface=surface):
                self.player.terrain = () if surface == GROUND_Y else ((320, GROUND_Y, 500, surface),)
                self.player.y = surface + 5
                self.player.vertical_speed = -200
                self.player.state = "jump"
                self.player.update(0, False, 1 / 60, jump_pressed=True)
                self.assertGreater(self.player.y, surface)
                self.assertLess(self.player.vertical_speed, 0)
                self.player.update(0, False, 1 / 60)
                self.assertEqual(self.player.y, surface)
                self.assertEqual(self.player.state, "jump")
                self.assertEqual(self.player.vertical_speed, JUMP_SPEED)
                self.player.update(0, False, 1 / 60)
                self.assertGreater(self.player.y, surface)

    def test_attack_continues_while_running_and_preserves_its_facing(self):
        self.player.update(1, True, 0.1, attack_pressed=True)
        self.assertEqual(self.player.state, "run")
        self.assertAlmostEqual(self.player.x, 400 + RUN_SPEED * 0.1)
        self.assertEqual(self.player.attack_time, 0)
        camera = Camera(SCREEN_WIDTH, WORLD_WIDTH, CAMERA_ZOOM)
        with patch.object(self.player.animations["attack"], "draw") as draw:
            self.player.draw(camera)
            draw.assert_called_once_with(self.player.x, GROUND_Y, 1, 0, camera, 0)
        self.player.update(-1, True, 0.125, attack_pressed=True)
        self.assertAlmostEqual(self.player.x, 400 + RUN_SPEED * (0.1 - 0.125))
        self.assertEqual(self.player.attack_time, 0.125)
        with patch.object(self.player.animations["attack"], "draw") as draw, patch("player.draw_slash") as trail:
            self.player.draw(camera)
            draw.assert_called_once_with(self.player.x, GROUND_Y, 1, 0.125, camera, 3)
            trail.assert_called_once()
            self.assertEqual(trail.call_args.args[:3], (self.player.x, GROUND_Y, 1))
            self.assertAlmostEqual(trail.call_args.args[3], 0.059)
            self.assertFalse(trail.call_args.kwargs["downward"])
        self.player.update(-1, True, 0.06)
        with patch.object(self.player.animations["attack"], "draw") as draw, patch("player.draw_slash") as trail:
            self.player.draw(camera)
            draw.assert_called_once_with(self.player.x, GROUND_Y, 1, self.player.attack_time, camera, 4)
            trail.assert_called_once()
        self.player.update(-1, True, 0.02)
        self.assertIsNone(self.player.attack_time)
        self.assertEqual(self.player.state, "run")
        with patch("player.draw_slash") as trail:
            self.player.draw(camera)
            trail.assert_called_once()
            self.assertEqual(trail.call_args.args[2], 1)
            self.assertAlmostEqual(trail.call_args.args[3], 0.139)
        self.player.update(-1, True, 0.01)
        with patch("player.draw_slash") as trail:
            self.player.draw(camera)
            trail.assert_not_called()

    def test_forward_attacks_share_active_bounds_and_mirror(self):
        bounds = {}
        for facing in (-1, 1):
            for airborne in (False, True):
                with self.subTest(facing=facing, airborne=airborne):
                    player = Player(400, GROUND_Y, WORLD_WIDTH)
                    player.facing = facing
                    player.update(0, False, 0.01, jump_pressed=airborne, attack_pressed=True)
                    self.assertEqual(player.attack_animation_key, "air_attack" if airborne else "attack")
                    player.update(0, False, 0.05)
                    self.assertIsNone(player.get_attack_hitbox())
                    player.update(0, False, 0.06)
                    left, bottom, right, top = player.get_attack_hitbox()
                    bounds[facing, airborne] = (left - player.x, bottom - player.y, right - player.x, top - player.y)
                    player.update(0, False, 0.09)
                    self.assertIsNone(player.get_attack_hitbox())

        for facing in (-1, 1):
            for ground, air in zip(bounds[facing, False], bounds[facing, True]):
                self.assertAlmostEqual(ground, air)
        left, bottom, right, top = bounds[1, False]
        self.assertGreater(right, 0)
        for mirrored, expected in zip(bounds[-1, False], (-right, bottom, -left, top)):
            self.assertAlmostEqual(mirrored, expected)

    def test_jump_and_air_attack_do_not_interrupt_motion(self):
        self.player.update(1, False, 0.1, jump_pressed=True, attack_pressed=True)
        self.assertEqual(self.player.state, "jump")
        self.assertEqual(self.player.attack_time, 0)
        self.assertGreater(self.player.y, GROUND_Y)
        camera = Camera(SCREEN_WIDTH, WORLD_WIDTH, CAMERA_ZOOM)
        with patch.object(self.player.animations["jump"], "draw") as draw:
            self.player.draw(camera)
            draw.assert_called_once_with(self.player.x, self.player.y, 1, self.player.animation_time, camera, 2)
        self.player.update(1, False, 0.18)
        self.assertAlmostEqual(self.player.attack_time, 0.18)
        self.player.update(1, False, 0.04)
        self.assertIsNone(self.player.attack_time)
        self.player.update(1, False, 0.17)
        previous_y = self.player.y
        previous_x = self.player.x
        self.player.update(1, False, 0.03, attack_pressed=True)
        self.assertEqual(self.player.attack_time, 0)
        self.assertEqual(self.player.state, "jump")
        self.assertLess(self.player.y, previous_y)
        self.assertAlmostEqual(self.player.x, previous_x + WALK_SPEED * 0.03)
        self.player.update(1, False, 0.03)
        with patch.object(self.player.animations["air_attack"], "draw") as draw:
            self.player.draw(camera)
            draw.assert_called_once_with(self.player.x, self.player.y, 1, 0.03, camera, 1)

    def test_late_attack_input_chains_once_and_keeps_the_down_modifier(self):
        self.player.update(0, False, 0.1, jump_pressed=True, attack_pressed=True)
        self.player.update(0, False, 0.15, crouch_held=True, attack_pressed=True)
        self.assertEqual(self.player.attack_animation_key, "air_attack")
        self.assertAlmostEqual(self.player.attack_time, 0.15)
        self.player.update(0, False, 0.041)
        self.assertEqual(self.player.attack_animation_key, "air_down_attack")
        self.assertEqual(self.player.attack_time, 0)
        self.player.update(0, False, 0.17)
        self.assertIsNone(self.player.attack_time)

    def test_down_attack_plays_while_falling_and_then_resumes_jump_animation(self):
        self.player.update(0, False, 0.47, jump_pressed=True)
        previous_y = self.player.y
        self.player.update(-1, False, 0.01, crouch_held=True, attack_pressed=True)
        self.assertEqual(self.player.attack_animation_key, "air_down_attack")
        self.assertEqual(self.player.state, "jump")
        self.assertEqual(self.player.crouch_time, 0)
        self.assertLess(self.player.y, previous_y)
        self.assertAlmostEqual(self.player.x, 400 - WALK_SPEED * 0.01)
        animation = self.player.animations["air_down_attack"]
        camera = Camera(SCREEN_WIDTH, WORLD_WIDTH, CAMERA_ZOOM)
        for index, delta_time in enumerate((0, 0.08, 0.06)):
            self.player.update(1, False, delta_time)
            with patch.object(animation.image, "clip_composite_draw", wraps=animation.image.clip_composite_draw) as draw:
                pico.SDL_ClearError()
                self.player.draw(camera)
                self.assertFalse(pico.SDL_GetError())
                draw.assert_called_once()
                self.assertEqual(draw.call_args.args[0], animation.frames[index]["x"])
                self.assertEqual(draw.call_args.args[5], "h")
        self.player.update(1, False, 0.1)
        self.assertIsNone(self.player.attack_time)
        self.assertEqual(self.player.state, "jump")
        with patch.object(self.player.animations["jump_look_down"], "draw") as draw:
            self.player.draw(camera)
            draw.assert_called_once()

    def test_look_down_uses_air_input_and_descent_until_landing(self):
        camera = Camera(SCREEN_WIDTH, WORLD_WIDTH, CAMERA_ZOOM)
        normal = self.player.animations["jump"]
        look_down = self.player.animations["jump_look_down"]
        self.player.update(0, False, 0.1, jump_pressed=True)
        self.player.update(-1, False, 0.05, crouch_held=True)
        self.assertGreater(self.player.vertical_speed, 0)
        with patch.object(look_down, "draw", wraps=look_down.draw) as draw:
            self.player.draw(camera)
            draw.assert_called_once_with(self.player.x, self.player.y, -1, self.player.animation_time, camera, 2)
        self.player.update(0, False, 0.03)
        with patch.object(normal, "draw") as draw:
            self.player.draw(camera)
            draw.assert_called_once()
        self.player.update(0, False, 0.35)
        self.assertLess(self.player.vertical_speed, 0)
        with patch.object(look_down, "draw", wraps=look_down.draw) as draw:
            self.player.draw(camera)
            draw.assert_called_once()
        self.player.update(0, False, 0.42)
        self.assertEqual(self.player.state, "land")
        with patch.object(normal, "draw") as draw:
            self.player.draw(camera)
            draw.assert_called_once()

    def test_grounded_down_and_attack_starts_crouch(self):
        self.player.update(0, False, 0.05, crouch_held=True, attack_pressed=True)
        self.assertEqual(self.player.state, "crouch")
        self.assertIsNone(self.player.attack_time)

    def test_air_attack_draws_frames_at_their_configured_times(self):
        animation = self.player.animations["air_attack"]
        camera = Camera(SCREEN_WIDTH, WORLD_WIDTH, CAMERA_ZOOM)
        for elapsed, index in ((0.024, 0), (0.025, 1), (0.065, 2), (0.105, 3), (0.160, 4), (0.189, 4)):
            with self.subTest(elapsed=elapsed), patch.object(animation.image, "clip_composite_draw") as draw:
                animation.draw(self.player.x, self.player.y, 1, elapsed, camera)
                self.assertEqual(draw.call_args.args[0], animation.frames[index]["x"])

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

    def test_crouch_jump_uses_the_jump_animation_while_down_is_held(self):
        self.player.update(0, False, CROUCH_DURATION, crouch_held=True)
        self.assertEqual(self.player.state, "crouch")
        start_x = self.player.x
        self.player.update(1, False, 0.05, jump_pressed=True, crouch_held=True)
        self.assertEqual(self.player.state, "jump")
        self.assertGreater(self.player.y, GROUND_Y)
        self.assertEqual(self.player.crouch_time, 0)
        self.assertAlmostEqual(self.player.x, start_x + WALK_SPEED * 0.05)
        camera = Camera(SCREEN_WIDTH, WORLD_WIDTH, CAMERA_ZOOM)
        with patch.object(self.player.animations["jump_look_down"], "draw") as draw:
            self.player.draw(camera)
            draw.assert_called_once_with(self.player.x, self.player.y, 1, 0.05, camera, 1)

        self.player.update(0, False, 0.05)
        with patch.object(self.player.animations["jump"], "draw") as draw:
            self.player.draw(camera)
            draw.assert_called_once()

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

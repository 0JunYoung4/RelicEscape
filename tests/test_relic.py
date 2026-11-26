"""Verify relic placement and return through the game loop."""

import os
import unittest
from ctypes import byref, c_uint32
from itertools import chain, count
from math import floor
from unittest.mock import patch

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_RENDER_DRIVER"] = "software"

import main
from pico2d import pico2d as pico
from lower_route_a import lift_path
from lower_route_b_layout import RAIL_ONE, RAIL_TWO
from player import CROUCH_DURATION, STANDING_HITBOX_HEIGHT, Player
from rail import (RAIL_BEND_IMAGE, RAIL_IMAGE, RAIL_MOUNT_RADIUS, RAIL_TRAVEL_SPEED,
                  RailCarriage, draw_rail)


def keydown(key):
    event = pico.Event(pico.SDL_KEYDOWN)
    event.key = key
    return event


class RelicTests(unittest.TestCase):
    def test_return_mark_can_be_used_once_and_absorbs_into_the_current_relic(self):
        e, q = pico.SDLK_e, pico.SDLK_q
        commands = (
            (0.05, e, 0), (0.10, None, 1), (0.15, e, 0),
            (0.20, q, 0), (0.25, None, 1), (0.30, q, 0),
            (1.15, e, 0), (1.20, None, 1), (1.25, e, 0),
            (1.30, None, 1), (1.35, e, 0), (1.40, None, 1), (1.45, q, 0),
            (4.45, None, 0), (5.15, None, 0), (5.20, e, 0),
            (8.40, None, 1), (8.45, q, 0), (9.10, None, 0),
        )
        clock = chain((0,), chain.from_iterable((time, time) for time, _, _ in commands), (10,))
        inputs = iter(commands)
        positions, marks = {}, {}
        direction = 0
        draw_mark = main.ReturnMark.draw

        def events():
            nonlocal direction
            command = next(inputs, None)
            if command is None:
                return [pico.Event(pico.SDL_QUIT)]
            _, key, direction = command
            return [] if key is None else [keydown(key)]

        def record_scene(player, camera, *args, **kwargs):
            _, bottom, _, top = player.get_hitbox()
            positions[kwargs["frame_start"]] = (
                player.x, kwargs["relic_center"], camera.world_to_screen(player.x, (bottom + top) / 2),
            )

        def record_mark(mark, camera, target, now):
            marks[now] = mark.pose, mark.can_return(now), target
            draw_mark(mark, camera, target, now)

        with patch.object(main, "TEST_SPAWN", (700, main.GROUND_Y, 0.0)), \
                patch.object(main, "run_title", return_value=False), \
                patch.object(main, "perf_counter", side_effect=clock), \
                patch.object(main, "read_movement", side_effect=lambda: (direction, False, False)), \
                patch.object(main, "poll_events", side_effect=events), \
                patch.object(pico, "SDL_GetKeyboardFocus", return_value=True), \
                patch.object(main, "sleep"), patch.object(main, "draw_scene", new=record_scene), \
                patch.object(main.ReturnMark, "draw", new=record_mark):
            main.main(test_room=True)

        self.assertTrue(marks[0.15][1])
        self.assertEqual(positions[0.20][0], positions[0.10][0])
        self.assertFalse(marks[0.20][1])
        self.assertEqual(marks[0.20][2], positions[0.20][2])
        self.assertEqual(positions[0.30][0], positions[0.25][0])
        self.assertEqual(positions[1.45][0], positions[1.40][0])
        self.assertTrue(marks[1.45][1])
        self.assertFalse(marks[4.45][1])
        self.assertIsNotNone(positions[4.45][1])
        self.assertEqual(marks[4.45][2], positions[4.45][1])
        self.assertNotIn(5.15, marks)
        self.assertEqual(positions[8.45][0], positions[8.40][0])
        self.assertFalse(marks[8.40][1])
        self.assertEqual(marks[8.40][2], positions[8.40][2])
        self.assertNotIn(9.10, marks)

    def test_ground_and_air_return_to_the_position_at_keydown(self):
        start_x = 700
        events = [
            [keydown(pico.SDLK_e)], [], [keydown(pico.SDLK_e)],
            [keydown(pico.SDLK_SPACE)], [keydown(pico.SDLK_e)], [],
            [keydown(pico.SDLK_e)], [],
            *([] for _ in range(36)), [pico.Event(pico.SDL_QUIT)],
        ]
        player_frames = []
        relic_frames = []
        effect_starts = []
        effect_active = []
        draw_scene = main.draw_scene
        draw_relic = main.draw_relic

        def record_player(player, *args, **kwargs):
            player_frames.append((player.x, player.y, player.vertical_speed))
            draw_scene(player, *args, **kwargs)
            effect = kwargs["return_effect"]
            effect_active.append(effect.started_at is not None)
            if effect.started_at == kwargs["frame_start"]:
                self.assertTrue(effect.departure)
                self.assertTrue(effect.arrival)
                effect_starts.append((len(player_frames) - 1, effect.origin))

        def record_relic(image, camera, x, y, elapsed):
            relic_frames.append((len(player_frames) - 1, x, y, elapsed))
            self.assertEqual((image.w, image.h), (12, 12))
            pico.SDL_ClearError()
            draw_relic(image, camera, x, y, elapsed)
            self.assertFalse(pico.SDL_GetError())

        with patch.object(main, "TEST_SPAWN", (start_x, main.GROUND_Y, 0.0)), \
                patch.object(main, "run_title", return_value=True), \
                patch.object(main, "poll_events", side_effect=events), \
                patch.object(pico, "SDL_GetKeyboardFocus", return_value=True), \
                patch.object(main, "read_movement", return_value=(1, False, False)), \
                patch.object(main, "perf_counter", side_effect=count(step=1 / 60)), \
                patch.object(main, "sleep"), \
                patch.object(main, "draw_scene", new=record_player), \
                patch.object(main, "draw_relic", new=record_relic):
            main.main(test_room=True)

        self.assertGreater(player_frames[0][0], start_x)
        self.assertEqual(player_frames[2], (start_x, main.GROUND_Y, 0.0))
        air_x, air_y, _ = player_frames[3]
        self.assertGreater(air_y, main.GROUND_Y)
        self.assertEqual(player_frames[6], (air_x, air_y, 0.0))
        self.assertLess(player_frames[7][1], air_y)
        self.assertLess(player_frames[7][2], 0.0)
        ground_center_y = main.GROUND_Y + STANDING_HITBOX_HEIGHT / 2
        air_center_y = air_y + STANDING_HITBOX_HEIGHT / 2
        self.assertEqual(
            [(index, x, y) for index, x, y, _ in relic_frames],
            [
                (0, start_x, ground_center_y), (1, start_x, ground_center_y),
                (4, air_x, air_center_y), (5, air_x, air_center_y),
            ],
        )
        self.assertEqual([elapsed for _, _, _, elapsed in relic_frames[::2]], [0.0, 0.0])
        self.assertEqual(effect_starts, [(2, player_frames[1][:2]), (6, player_frames[5][:2])])
        self.assertTrue(effect_active[7])
        self.assertFalse(effect_active[-1])

    def test_mounted_relic_follows_the_single_carriage_and_returns_mid_trip(self):
        left, rail_y = main.TEST_RAIL_PATH[0].start
        ground = main.GROUND_Y
        return_frame = 73
        e, x = pico.SDLK_e, pico.SDLK_x
        commands = iter((
            (None, (pico.SDLK_f,)),
            (None, (e,)),
            (None, (x,)),
            *((None, ()) for _ in range(return_frame - 3)),
            (None, (e,)),
            (left, ()),
            (None, (e,)),
            ("carriage", ()),
            (None, (e,)),
            ("carriage", (e,)),
            (None, (e,)),
        ))
        player = None
        player_frames = []
        carriage_frames = []
        mount_frames = []
        prompt_frames = []
        relic_views = []
        held = [0] * pico.SDL_NUM_SCANCODES
        draw_scene = main.draw_scene

        def create_player(*args, **kwargs):
            nonlocal player
            player = Player(*args, **kwargs)
            return player

        def frame_events():
            command = next(commands, None)
            if command is None:
                return [pico.Event(pico.SDL_QUIT)]
            player_x, keys = command
            player_y = ground
            index = len(carriage_frames)
            held[pico.SDL_SCANCODE_C] = int(56 <= index < 63)
            if index == 55:
                player_x = 2800
            if player_x == "carriage":
                player_x, rail_y = carriage_frames[-1]
                player_y = rail_y - STANDING_HITBOX_HEIGHT / 2
            if player_x is not None:
                self.assertTrue(player.teleport_to(player_x, player_y, 0.0))
            return [keydown(key) for key in keys]

        def record_scene(player, camera, *args, **kwargs):
            player_frames.append((player.x, player.y))
            position = kwargs["carriage_position"]
            carriage_frames.append(position)
            mounted = kwargs["rail_relic_image"] is not None
            mount_frames.append(mounted)
            prompt_visible = kwargs["show_mount_prompt"]
            prompt_frames.append(prompt_visible)
            carriage = kwargs["carriage_image"]
            self.assertEqual((carriage.w, carriage.h), (24, 21))
            if mounted:
                self.assertEqual(kwargs["relic_center"], camera.world_to_screen(*position))
            relic_views.append(kwargs["relic_center"])
            carriage_draws = []
            draw_carriage = carriage.draw

            def record_carriage(x, y, width, height):
                carriage_draws.append((x, y, width, height))
                draw_carriage(x, y, width, height)

            with patch.object(carriage, "draw", new=record_carriage):
                draw_scene(player, camera, *args, **kwargs)
            self.assertEqual(carriage_draws, [(*camera.world_to_screen(*position), 24, 21)])

        with patch.object(main, "Player", new=create_player), \
                patch.object(main, "run_title", return_value=True), \
                patch.object(main, "poll_events", new=frame_events), \
                patch.object(pico, "SDL_GetKeyboardFocus", return_value=True), \
                patch.object(pico, "SDL_GetKeyboardState", return_value=held), \
                patch.object(main, "read_movement", return_value=(0, False, False)), \
                patch.object(main, "perf_counter", side_effect=count(step=1 / 120)), \
                patch.object(main, "sleep"), \
                patch.object(main, "draw_scene", new=record_scene):
            main.main(test_room=True)

        self.assertEqual(carriage_frames[0], (left, rail_y))
        self.assertLess(relic_views[55][0], 0)
        self.assertTrue(all(0 <= x < main.SCREEN_WIDTH for x, _ in relic_views[56:63]))
        self.assertLess(relic_views[63][0], 0)
        self.assertEqual(mount_frames, [False] + [True] * (return_frame - 1) + [False] * 5 + [True, False])
        self.assertEqual(
            [index for index, visible in enumerate(prompt_frames) if visible],
            [0, return_frame, return_frame + 6],
        )
        x, y = carriage_frames[return_frame - 1]
        self.assertGreater(x, left + RAIL_MOUNT_RADIUS)
        self.assertGreater(y, rail_y)
        self.assertEqual(player_frames[return_frame], (x, y - STANDING_HITBOX_HEIGHT / 2))
        self.assertNotEqual(carriage_frames[return_frame], (x, y))
        self.assertEqual(player_frames[return_frame + 4], (left, ground))
        x, y = carriage_frames[return_frame + 5]
        self.assertEqual(player_frames[return_frame + 6], (x, y - STANDING_HITBOX_HEIGHT / 2))

    def test_bend_matches_straight_rail_thickness(self):
        width, height = 450, 220
        pico.open_canvas(width, height)
        self.addCleanup(pico.close_canvas)
        straight, bend = RAIL_ONE[:2]
        camera = main.Camera(width, main.WORLD_WIDTH, main.EXPLORATION_CAMERA_ZOOM)
        camera.x = 3300
        track, curve = (pico.load_image(str(path)) for path in (RAIL_IMAGE, RAIL_BEND_IMAGE))
        pico.SDL_SetRenderDrawColor(pico.renderer, 0, 0, 0, 255)
        pico.SDL_RenderClear(pico.renderer)
        draw_rail(track, curve, camera, RAIL_ONE)

        def visible_pixels(x, y, w, h):
            pixels = (c_uint32 * (w * h))()
            bounds = pico.SDL_Rect(x, height - y - h, w, h)
            self.assertEqual(pico.SDL_RenderReadPixels(
                pico.renderer, byref(bounds), pico.SDL_PIXELFORMAT_ARGB8888, pixels, w * 4,
            ), 0, pico.SDL_GetError())
            return sum(bool(pixel & 0xFFFFFF) for pixel in pixels)

        straight_x, straight_y = map(round, camera.world_to_screen(*straight.point_at(0.5)))
        bend_x, bend_y = map(round, camera.world_to_screen(*bend.point_at(0.9)))
        straight_width = visible_pixels(straight_x, straight_y - 22, 1, 44)
        bend_width = visible_pixels(bend_x - 22, bend_y, 44, 1)
        self.assertEqual(straight_width, 18)
        self.assertAlmostEqual(bend_width, straight_width, delta=2)

    def test_cyan_channel_continues_through_curves_and_joins(self):
        width, height = 1050, 730
        pico.open_canvas(width, height)
        self.addCleanup(pico.close_canvas)
        track, curve = (pico.load_image(str(path)) for path in (RAIL_IMAGE, RAIL_BEND_IMAGE))
        pixels = (c_uint32 * (width * height))()
        bounds = pico.SDL_Rect(0, 0, width, height)

        def is_cyan(x, y):
            pixel = pixels[(height - 1 - y) * width + x]
            return (pixel >> 8 & 0xFF) > 155 and (pixel & 0xFF) > 150

        for path in (lift_path(), RAIL_ONE, RAIL_TWO, main.TEST_RAIL_PATH):
            left = min(segment.start[0] for segment in path) - 30.2
            bottom = min(segment.start[1] for segment in path) - 48.7
            for zoom in (main.AIM_CAMERA_ZOOM, main.EXPLORATION_CAMERA_ZOOM):
                camera = main.Camera(width, main.WORLD_WIDTH, zoom, y=bottom)
                camera.x = left
                pico.SDL_SetRenderDrawColor(pico.renderer, 0, 0, 0, 255)
                pico.SDL_RenderClear(pico.renderer)
                draw_rail(track, curve, camera, path)
                self.assertEqual(pico.SDL_RenderReadPixels(
                    pico.renderer, byref(bounds), pico.SDL_PIXELFORMAT_ARGB8888, pixels, width * 4,
                ), 0, pico.SDL_GetError())
                for segment in path:
                    if segment.center is None:
                        continue
                    with self.subTest(bend=segment.start, zoom=zoom):
                        for step in range(101):
                            x, y = map(floor, camera.world_to_screen(*segment.point_at(step / 100)))
                            # The nearest bright pixel can land beside the mathematical centerline.
                            self.assertTrue(any(
                                is_cyan(x + dx, y + dy)
                                for dx, dy in ((0, 0), (-1, 0), (1, 0), (0, -1), (0, 1))
                            ), f"Missing cyan light at {step}% of the bend")

    def test_carriage_travels_by_distance_through_the_first_curve(self):
        straight, bend, *_ = main.TEST_RAIL_PATH
        self.assertEqual(straight.end, bend.start)
        carriage = RailCarriage(main.TEST_RAIL_PATH, 72, 63)
        carriage.direction = 1
        carriage.move(straight.length / RAIL_TRAVEL_SPEED)
        self.assertEqual(carriage.position, bend.start)
        carriage.move(bend.length / (2 * RAIL_TRAVEL_SPEED))
        x, y = carriage.position
        expected_x, expected_y = bend.point_at(0.5)
        self.assertAlmostEqual(x, expected_x)
        self.assertAlmostEqual(y, expected_y)
        carriage.move(bend.length / (2 * RAIL_TRAVEL_SPEED))
        self.assertAlmostEqual(carriage.position[0], bend.end[0])
        self.assertAlmostEqual(carriage.position[1], bend.end[1])

    def test_horizontal_slashes_move_reverse_and_stop_the_carriage(self):
        pico.open_canvas(main.SCREEN_WIDTH, main.SCREEN_HEIGHT)
        self.addCleanup(pico.close_canvas)
        left = main.TEST_RAIL_PATH[0].start[0]
        right = main.TEST_RAIL_PATH[-1].end[0]
        carriage = RailCarriage(main.TEST_RAIL_PATH, 72, 63)
        player = Player(100, main.GROUND_Y, main.WORLD_WIDTH)

        def swing(facing):
            player.facing = facing
            for frame in range(15):
                player.update(0, False, 1 / 60, attack_pressed=frame == 0)
                carriage.check_attack(player)
                carriage.move(1 / 60)

        swing(1)
        self.assertEqual((carriage.position[0], carriage.direction), (left, 0))

        player.x = left - 40
        swing(1)
        self.assertGreater(carriage.position[0], left)
        self.assertEqual(carriage.direction, 1)

        player.x = carriage.position[0] + 110
        swing(-1)
        self.assertEqual(carriage.direction, -1)
        carriage.move(10)
        self.assertEqual((carriage.position[0], carriage.direction), (left, 0))

        player.x = left - 40
        swing(1)
        carriage.move(10)
        self.assertEqual((carriage.position[0], carriage.direction), (right, 0))

        player.x = right + 40
        swing(-1)
        self.assertLess(carriage.position[0], right)
        self.assertEqual(carriage.direction, -1)

    def test_return_restores_a_safe_crouch_and_rejects_an_overlap(self):
        pico.open_canvas(main.SCREEN_WIDTH, main.SCREEN_HEIGHT)
        self.addCleanup(pico.close_canvas)
        ground = main.GROUND_Y
        ceiling = (250, ground + 90, 550, ground + 120)
        player = Player(800, ground, main.WORLD_WIDTH, terrain=(ceiling,))
        player.wall_jump_speed = 480.0
        player.wall_jump_remaining = 0.1
        player.jump_buffer_remaining = 0.1
        player.jump_origin_y = ground

        self.assertFalse(player.teleport_to(400, ground, 0.0))
        self.assertEqual((player.x, player.y, player.crouch_time), (800, ground, 0.0))
        self.assertEqual(player.wall_jump_remaining, 0.1)

        self.assertTrue(player.teleport_to(400, ground, CROUCH_DURATION))
        self.assertEqual((player.x, player.y, player.crouch_time), (400, ground, CROUCH_DURATION))
        self.assertEqual(player.state, "crouch")
        self.assertEqual(player.wall_jump_speed, 0.0)
        self.assertEqual(player.wall_jump_remaining, 0.0)
        self.assertEqual(player.jump_buffer_remaining, 0.0)
        self.assertIsNone(player.jump_origin_y)

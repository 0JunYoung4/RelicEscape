"""Verify relic placement and return through the game loop."""

import os
import unittest
from itertools import count
from unittest.mock import patch

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_RENDER_DRIVER"] = "software"

import main
from pico2d import pico2d as pico
from player import CROUCH_DURATION, STANDING_HITBOX_HEIGHT, Player
from rail import RAIL_MOUNT_RADIUS, RAIL_TRAVEL_SPEED, RailCarriage


def keydown(key):
    event = pico.Event(pico.SDL_KEYDOWN)
    event.key = key
    return event


class RelicTests(unittest.TestCase):
    def test_ground_and_air_return_to_the_position_at_keydown(self):
        events = [
            [keydown(pico.SDLK_e)], [], [keydown(pico.SDLK_e)],
            [keydown(pico.SDLK_SPACE)], [keydown(pico.SDLK_e)], [],
            [keydown(pico.SDLK_e)], [],
            *([] for _ in range(36)), [keydown(pico.SDLK_ESCAPE)],
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

        with patch.object(pico, "get_events", side_effect=events), \
                patch.object(pico, "SDL_GetKeyboardFocus", return_value=True), \
                patch.object(main, "read_movement", return_value=(1, False, False)), \
                patch.object(main, "perf_counter", side_effect=count(step=1 / 60)), \
                patch.object(main, "sleep"), \
                patch.object(main, "draw_scene", new=record_player), \
                patch.object(main, "draw_relic", new=record_relic):
            main.main()

        self.assertGreater(player_frames[0][0], 400)
        self.assertEqual(player_frames[2], (400, main.GROUND_Y, 0.0))
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
                (0, 400, ground_center_y), (1, 400, ground_center_y),
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
        e, f, x = pico.SDLK_e, pico.SDLK_f, pico.SDLK_x
        commands = iter((
            (None, ()),
            (None, (f,)),
            (None, (x,)),
            *((None, ()) for _ in range(return_frame - 3)),
            (None, (e,)),
            (left, (f,)),
            (None, (e,)),
            ("carriage", (f,)),
            (None, (e,)),
            ("carriage", (f,)),
            (None, (e,)),
            (None, (pico.SDLK_ESCAPE,)),
        ))
        player = None
        player_frames = []
        carriage_frames = []
        mount_frames = []
        prompt_frames = []
        draw_scene = main.draw_scene

        def create_player(*args, **kwargs):
            nonlocal player
            player = Player(*args, **kwargs)
            return player

        def frame_events():
            player_x, keys = next(commands)
            player_y = ground
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
            carriage_draws = []
            draw_carriage = carriage.draw

            def record_carriage(x, y, width, height):
                carriage_draws.append((x, y, width, height))
                draw_carriage(x, y, width, height)

            with patch.object(carriage, "draw", new=record_carriage):
                draw_scene(player, camera, *args, **kwargs)
            self.assertEqual(carriage_draws, [(*camera.world_to_screen(*position), 24, 21)])

        with patch.object(main, "Player", new=create_player), \
                patch.object(pico, "get_events", new=frame_events), \
                patch.object(pico, "SDL_GetKeyboardFocus", return_value=True), \
                patch.object(main, "read_movement", return_value=(0, False, False)), \
                patch.object(main, "perf_counter", side_effect=count(step=1 / 120)), \
                patch.object(main, "sleep"), \
                patch.object(main, "draw_scene", new=record_scene):
            main.main()

        self.assertEqual(carriage_frames[0], (left, rail_y))
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

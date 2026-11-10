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


def keydown(key):
    event = pico.Event(pico.SDL_KEYDOWN)
    event.key = key
    return event


class RelicTests(unittest.TestCase):
    def test_ground_and_air_return_to_the_position_at_keydown(self):
        events = [
            [keydown(pico.SDLK_e)], [], [keydown(pico.SDLK_e)],
            [keydown(pico.SDLK_SPACE)], [keydown(pico.SDLK_e)], [],
            [keydown(pico.SDLK_e)], [], [keydown(pico.SDLK_ESCAPE)],
        ]
        player_frames = []
        relic_frames = []
        draw_scene = main.draw_scene
        draw_relic = main.draw_relic

        def record_player(player, *args, **kwargs):
            player_frames.append((player.x, player.y, player.vertical_speed))
            draw_scene(player, *args, **kwargs)

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
                patch.object(main, "draw_scene", side_effect=record_player), \
                patch.object(main, "draw_relic", side_effect=record_relic):
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

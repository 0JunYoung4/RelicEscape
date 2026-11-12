"""Check crossbow input, projectile motion, and relic recovery."""

import os
import unittest
from itertools import count
from math import radians
from unittest.mock import patch

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_RENDER_DRIVER"] = "software"

import main
from launcher import Crossbow, FLIGHT_GRAVITY, FLIGHT_RADIUS, RelicFlight
from pico2d import pico2d as pico
from player import Player


def keydown(key):
    event = pico.Event(pico.SDL_KEYDOWN)
    event.key = key
    return event


class LauncherTests(unittest.TestCase):
    def test_f_mouse_aim_click_and_midflight_return_through_game_loop(self):
        click = pico.Event(pico.SDL_MOUSEBUTTONDOWN)
        click.button = pico.SDL_BUTTON_LEFT
        f, e = keydown(pico.SDLK_f), keydown(pico.SDLK_e)
        events = iter(([f], [], [f], [f], [click], *([] for _ in range(8)), [e], [keydown(pico.SDLK_ESCAPE)]))
        frames = []
        scene = main.draw_scene

        def create_player(x, y, world_width, terrain):
            return Player(main.TEST_CROSSBOW_X - 40, y, world_width, terrain=terrain)

        def record(player, camera, *args, **kwargs):
            crossbow = kwargs["crossbow"]
            flight = crossbow.flight
            frames.append((
                crossbow.aiming, crossbow.angle, crossbow.relic_position,
                flight.return_pose(main.GROUND_Y)[:2] if flight is not None else None,
                (player.x, player.y), kwargs["show_crossbow_prompt"],
            ))
            if crossbow.relic_position is not None:
                self.assertEqual(kwargs["relic_center"], camera.world_to_screen(*crossbow.relic_position))
            scene(player, camera, *args, **kwargs)

        low_target = (main.TEST_CROSSBOW_X + 400, main.GROUND_Y)
        high_target = (main.TEST_CROSSBOW_X + 400, main.GROUND_Y + 350)
        with patch.object(main, "Player", new=create_player), \
                patch.object(pico, "get_events", new=lambda: next(events)), \
                patch.object(pico, "SDL_GetKeyboardFocus", return_value=True), \
                patch.object(main, "read_movement", return_value=(1, True, False)), \
                patch.object(main, "mouse_world_position", side_effect=(low_target, high_target, high_target, high_target)), \
                patch.object(main, "perf_counter", side_effect=count(step=1 / 120)), \
                patch.object(main, "sleep"), \
                patch.object(main, "draw_scene", new=record):
            main.main()

        self.assertEqual([frame[0] for frame in frames[:5]], [True, True, False, True, False])
        self.assertEqual(frames[0][1], 0)
        self.assertGreater(frames[1][1], radians(30))
        self.assertEqual(frames[0][4], frames[1][4])
        self.assertIsNone(frames[2][2])
        self.assertTrue(frames[2][5])
        self.assertGreater(frames[12][2][0], frames[4][2][0])
        self.assertGreater(frames[12][2][1], frames[4][2][1])
        self.assertEqual(frames[13][4], frames[12][3])
        self.assertIsNone(frames[13][2])

    def test_flight_follows_a_parabola_and_lands_on_a_platform(self):
        ground = main.GROUND_Y
        flight = RelicFlight(300, ground + 70, 700, 450)
        flight.update(0.25, (), ground, main.WORLD_WIDTH)
        self.assertAlmostEqual(flight.x, 300 + 700 * 0.25)
        self.assertAlmostEqual(flight.y, ground + 70 + 450 * 0.25 - FLIGHT_GRAVITY * 0.25 ** 2 / 2)
        flight.update(2, (), ground, main.WORLD_WIDTH)
        self.assertTrue(flight.landed)
        self.assertEqual(flight.return_pose(ground)[1], ground)

        platform_top = ground + 200
        platform = (400, ground + 160, 800, platform_top)
        flight = RelicFlight(550, platform_top + 130, 100, -250)
        flight.update(1, (platform,), ground, main.WORLD_WIDTH)
        self.assertTrue(flight.landed)
        self.assertEqual(flight.y, platform_top + FLIGHT_RADIUS)
        self.assertEqual(flight.return_pose(ground)[1], platform_top)

    def test_mouse_direction_mirrors_the_crossbow_and_its_trajectory(self):
        ground = main.GROUND_Y
        crossbow = Crossbow(1400, ground, None, None)
        positions = []
        for direction in (1, -1):
            crossbow.aim_toward(crossbow.x + 200 * direction, crossbow.y + 200)
            self.assertEqual(crossbow.facing, direction)
            first_preview_point = next(crossbow.trajectory((), main.WORLD_WIDTH))
            crossbow.fire()
            crossbow.flight.update(0.085, (), ground, main.WORLD_WIDTH)
            self.assertEqual(crossbow.flight.position, first_preview_point)
            positions.append(crossbow.flight.position)
        self.assertAlmostEqual(positions[0][0] - crossbow.x, crossbow.x - positions[1][0])
        self.assertAlmostEqual(positions[0][1], positions[1][1])

    def test_long_shot_preview_reaches_the_landing_point(self):
        ground = main.GROUND_Y
        crossbow = Crossbow(main.TEST_CROSSBOW_X, ground, None, None)
        for slope in (1, 2):
            crossbow.aim_toward(crossbow.x + 400, crossbow.y + 400 * slope)
            preview = list(crossbow.trajectory((), main.WORLD_WIDTH))
            crossbow.fire()
            crossbow.flight.update(3, (), ground, main.WORLD_WIDTH)
            self.assertTrue(crossbow.flight.landed)
            self.assertGreater(crossbow.flight.x - crossbow.x, 2300)
            self.assertEqual(preview[-1][1], ground + FLIGHT_RADIUS)
            self.assertAlmostEqual(preview[-1][0], crossbow.flight.x, delta=13)

    def test_shot_camera_changes_zoom_follows_and_restores_normal_view(self):
        camera = main.Camera(main.SCREEN_WIDTH, main.WORLD_WIDTH, main.CAMERA_ZOOM)
        camera.update(400, 1 / 60, view_target=215, view_zoom=main.AIM_CAMERA_ZOOM)
        self.assertGreater(camera.zoom, main.AIM_CAMERA_ZOOM)
        self.assertLess(camera.zoom, main.CAMERA_ZOOM)
        self.assertEqual(camera.x, 0)

        for _ in range(90):
            camera.update(400, 1 / 60, view_target=2600, view_zoom=main.FLIGHT_CAMERA_ZOOM)
        self.assertGreater(camera.x, 900)
        self.assertLess(camera.x, main.WORLD_WIDTH - camera.view_width)

        for _ in range(90):
            camera.update(400, 1 / 60)
        self.assertEqual(camera.zoom, main.CAMERA_ZOOM)
        self.assertEqual(camera.x, 0)
        self.assertFalse(camera.transitioning)
        camera.update(1800, 1 / 60)
        self.assertAlmostEqual(camera.x, 360)

    def test_relic_stops_at_wall_and_can_be_recovered_below_it(self):
        ground = main.GROUND_Y
        wall = (500, ground, 580, ground + 400)
        flight = RelicFlight(420, ground + 70, 1100, 0)
        flight.update(1, (wall,), ground, main.WORLD_WIDTH)
        self.assertTrue(flight.landed)
        self.assertEqual(flight.return_pose(ground), (wall[0] - FLIGHT_RADIUS, ground, 0.0))

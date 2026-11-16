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
from launcher import Crossbow, FLIGHT_GRAVITY, FLIGHT_RADIUS, MAX_ELEVATION, RelicFlight
from pico2d import pico2d as pico
from player import Player


def keydown(key):
    event = pico.Event(pico.SDL_KEYDOWN)
    event.key = key
    return event


class LauncherTests(unittest.TestCase):
    def test_e_arrow_aim_x_and_midflight_return_through_game_loop(self):
        e = keydown(pico.SDLK_e)
        inputs = iter((
            ([e], ()),
            *(([], (pico.SDL_SCANCODE_LEFT, pico.SDL_SCANCODE_UP)) for _ in range(30)),
            ([], (pico.SDL_SCANCODE_DOWN,)),
            ([], ()),
            ([e], ()),
            ([e], ()),
            ([keydown(pico.SDLK_x)], (pico.SDL_SCANCODE_RIGHT,)),
            *(([], ()) for _ in range(8)),
            ([e], ()),
            ([keydown(pico.SDLK_ESCAPE)], ()),
        ))
        keys = [0] * pico.SDL_NUM_SCANCODES
        frames = []
        scene = main.draw_scene

        def get_events():
            events, held = next(inputs)
            keys[:] = [0] * len(keys)
            for key in held:
                keys[key] = 1
            return events

        def create_player(x, y, world_width, **kwargs):
            return Player(main.TEST_CROSSBOW_X - 40, y, world_width, **kwargs)

        def record(player, camera, *args, **kwargs):
            crossbow = kwargs["crossbow"]
            flight = crossbow.flight
            frames.append((
                crossbow.aiming, crossbow.angle, crossbow.relic_position,
                flight.return_pose(main.GROUND_Y)[:2] if flight is not None else None,
                (player.x, player.y), kwargs["show_crossbow_prompt"], crossbow.facing,
            ))
            self.assertIsNone(player.attack_time)
            if crossbow.relic_position is not None:
                self.assertEqual(kwargs["relic_center"], camera.world_to_screen(*crossbow.relic_position))
            scene(player, camera, *args, **kwargs)

        with patch.object(main, "Player", new=create_player), \
                patch.object(main, "run_title", return_value=True), \
                patch.object(pico, "get_events", new=get_events), \
                patch.object(pico, "SDL_GetKeyboardFocus", return_value=True), \
                patch.object(pico, "SDL_GetKeyboardState", return_value=keys), \
                patch.object(main, "perf_counter", side_effect=count(step=1 / 120)), \
                patch.object(main, "sleep"), \
                patch.object(main, "draw_scene", new=record):
            main.main()

        self.assertTrue(all(frame[0] for frame in frames[:33]))
        self.assertEqual(frames[0][1], 0)
        self.assertAlmostEqual(frames[30][1], radians(30))
        self.assertAlmostEqual(frames[31][1], radians(29))
        self.assertEqual(frames[31][1], frames[32][1])
        self.assertEqual(frames[30][6], -1)
        self.assertEqual(frames[0][4], frames[30][4])
        canceled, resumed, fired = frames[33:36]
        self.assertFalse(canceled[0])
        self.assertIsNone(canceled[2])
        self.assertTrue(canceled[5])
        self.assertTrue(resumed[0])
        self.assertFalse(fired[0])
        self.assertEqual(fired[6], 1)
        self.assertEqual(resumed[4], fired[4])
        last_flight, returned = frames[-2:]
        self.assertGreater(last_flight[2][0], fired[2][0])
        self.assertGreater(last_flight[2][1], fired[2][1])
        self.assertEqual(returned[4], last_flight[3])
        self.assertIsNone(returned[2])

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

    def test_aim_direction_mirrors_the_crossbow_and_its_trajectory(self):
        ground = main.GROUND_Y
        crossbow = Crossbow(1400, ground, None, None)
        crossbow.adjust_aim(0, 1, 0.75)
        positions = []
        for direction in (1, -1):
            crossbow.adjust_aim(direction, 0, 1 / 60)
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
        for aim_time, angle in ((0.75, radians(45)), (1, MAX_ELEVATION)):
            crossbow.adjust_aim(1, -1, 1)
            self.assertEqual(crossbow.angle, 0)
            crossbow.adjust_aim(0, 1, aim_time)
            self.assertAlmostEqual(crossbow.angle, angle)
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

"""Exercise the opening cave route, solid terrain, and dark map rendering."""

import ctypes
from itertools import count
import os
import unittest
from unittest.mock import patch

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_RENDER_DRIVER"] = "software"

from pico2d import pico2d as pico

import main
import opening_cave as cave


def keydown(key):
    event = pico.Event(pico.SDL_KEYDOWN)
    event.key = key
    return event


class OpeningCaveTests(unittest.TestCase):
    def test_enter_starts_cave_and_escape_then_enter_restarts_it(self):
        enter, escape = keydown(pico.SDLK_RETURN), keydown(pico.SDLK_ESCAPE)
        events = ([enter], [], [escape], [enter], [], [pico.Event(pico.SDL_QUIT)])
        frames = []
        draw = cave.OpeningCave.draw

        def record(scene, camera, **kwargs):
            frames.append((camera.world_width, camera.view_width, camera.world_to_screen(0, cave.GROUND_Y)[1]))
            draw(scene, camera, **kwargs)

        with patch.object(main, "configure_display", return_value=False), \
                patch.object(pico, "get_events", side_effect=events), \
                patch.object(main, "read_movement", return_value=(0, False, False)), \
                patch.object(main, "sleep"), \
                patch.object(main, "run_game") as test_room, \
                patch.object(main, "Player", wraps=main.Player) as player, \
                patch.object(cave.OpeningCave, "draw", new=record):
            main.main(opening=True)

        self.assertEqual(frames, [(cave.WORLD_WIDTH, 1920, 130)] * 2)
        self.assertEqual(player.call_count, 2)
        test_room.assert_not_called()

    def test_movement_restart_and_no_relic_before_falling(self):
        commands = ([], [], [keydown(pico.SDLK_e)], [keydown(pico.SDLK_q)],
                    [keydown(pico.SDLK_r)], [], [keydown(pico.SDLK_ESCAPE)])
        positions = []
        draw = main.Player.draw

        def record(player, camera):
            positions.append((player.x, player.y))
            draw(player, camera)

        pico.open_canvas(main.SCREEN_WIDTH, main.SCREEN_HEIGHT)
        self.addCleanup(pico.close_canvas)
        with patch.object(pico, "get_events", side_effect=commands), \
                patch.object(pico, "SDL_GetKeyboardFocus", return_value=True), \
                patch.object(main, "read_movement", return_value=(1, False, False)), \
                patch.object(main, "perf_counter", side_effect=count(step=1 / 60)), \
                patch.object(main, "sleep"), \
                patch.object(main.Player, "draw", new=record):
            self.assertFalse(main.run_opening_cave(False))

        for before, after in zip(positions[:3], positions[1:4]):
            self.assertGreater(after[0], before[0])
        self.assertTrue(all(y == cave.GROUND_Y for _, y in positions))
        self.assertEqual(positions[4], cave.SPAWN[:2])
        self.assertGreater(positions[5][0], positions[4][0])

    def test_whole_floor_is_solid_and_end_wall_cannot_be_passed(self):
        pico.open_canvas(main.SCREEN_WIDTH, main.SCREEN_HEIGHT)
        self.addCleanup(pico.close_canvas)
        player = main.Player(*cave.SPAWN[:2], cave.WORLD_WIDTH, terrain=cave.TERRAIN)
        for frame in range(280):
            player.update(1, True, 0.05, jump_pressed=frame % 20 == 0)
            self.assertGreaterEqual(player.y, cave.GROUND_Y)
            self.assertLessEqual(player.get_hitbox()[2], cave.END_WALL_X)
        self.assertEqual(player.get_hitbox()[2], cave.END_WALL_X)
        for _ in range(30):
            player.update(0, False, 0.05)
        self.assertEqual(player.y, cave.GROUND_Y)
        self.assertTrue(player.grounded)

    def test_background_is_darkened_and_both_camera_limits_render(self):
        pico.open_canvas(main.SCREEN_WIDTH, main.SCREEN_HEIGHT)
        self.addCleanup(pico.close_canvas)
        scene = cave.OpeningCave(main.SCREEN_WIDTH, main.SCREEN_HEIGHT)
        camera = main.Camera(
            main.SCREEN_WIDTH, cave.WORLD_WIDTH,
            y=cave.GROUND_Y - main.CAVE_FLOOR_SCREEN_Y / main.EXPLORATION_CAMERA_ZOOM,
        )

        def sample_wall():
            pixels = (ctypes.c_ubyte * (20 * 20 * 4))()
            result = pico.SDL_RenderReadPixels(
                pico.renderer, pico.SDL_Rect(470, 280, 20, 20),
                pico.SDL_PIXELFORMAT_RGBA32, pixels, 20 * 4,
            )
            self.assertEqual(result, 0, pico.SDL_GetError())
            return sum(sum(pixels[i:i + 3]) for i in range(0, len(pixels), 4))

        camera.follow(cave.WORLD_WIDTH / 2)
        scene.draw(camera)
        dark = sample_wall()
        pico.SDL_SetTextureColorMod(scene.backdrop.texture, 255, 255, 255)
        scene.draw(camera)
        self.assertGreater(sample_wall(), dark)
        self.assertGreater(dark, 0)
        for x in (cave.SPAWN[0], cave.DOOR_X):
            camera.follow(x)
            pico.SDL_ClearError()
            scene.draw(camera, show_hitboxes=True)
            self.assertEqual(pico.SDL_GetError(), b"")


if __name__ == "__main__":
    unittest.main()

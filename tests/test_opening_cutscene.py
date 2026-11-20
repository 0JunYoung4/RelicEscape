"""Check investigation gating, automatic approach, input lock, and replay."""

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
from opening_cutscene import APPROACH_SPEED, INTERACTION_DISTANCE, OBSERVE_DURATION, TOUCH_X, SigilApproach
from player import Player


def keydown(key):
    event = pico.Event(pico.SDL_KEYDOWN)
    event.key = key
    return event


class OpeningCutsceneTests(unittest.TestCase):
    def setUp(self):
        pico.open_canvas(main.SCREEN_WIDTH, main.SCREEN_HEIGHT)
        self.addCleanup(pico.close_canvas)
        self.player = Player(TOUCH_X - 270, cave.GROUND_Y, cave.WORLD_WIDTH, terrain=cave.TERRAIN)
        self.sequence = SigilApproach()

    def test_only_grounded_player_near_wall_can_investigate(self):
        self.player.recover_at(TOUCH_X - INTERACTION_DISTANCE - 1, cave.GROUND_Y, 0)
        self.assertFalse(self.sequence.start(self.player))
        self.player.recover_at(TOUCH_X - 100, cave.GROUND_Y + 80, 0)
        self.assertFalse(self.sequence.start(self.player))
        self.player.recover_at(TOUCH_X - 100, cave.GROUND_Y, 0)
        self.player.facing = -1
        self.player.update(0, False, 0.01, attack_pressed=True)
        self.assertTrue(self.sequence.start(self.player))
        self.assertEqual(self.player.facing, 1)
        self.assertIsNone(self.player.attack_time)
        self.assertIsNone(self.player.slash)

    def test_observe_then_slow_walk_then_reach_and_hold(self):
        initial_x = self.player.x
        self.assertTrue(self.sequence.start(self.player))
        self.assertEqual(self.sequence.frame_index, 8)
        self.sequence.update(self.player, OBSERVE_DURATION)
        self.assertEqual(self.player.x, initial_x)
        self.assertEqual(self.sequence.phase, "walk")
        self.sequence.update(self.player, 0.25)
        self.assertAlmostEqual(self.player.x, initial_x + APPROACH_SPEED * 0.25)
        self.sequence.update(self.player, 2.75)
        self.assertEqual(self.player.x, TOUCH_X)
        self.assertEqual(self.sequence.phase, "reach")
        self.sequence.update(self.player, 0.2)
        self.assertEqual(self.sequence.frame_index, 10)
        self.sequence.update(self.player, 0.3)
        self.assertEqual(self.sequence.frame_index, 12)
        self.sequence.update(self.player, 5)
        self.assertEqual(self.sequence.phase, "touch")
        self.assertEqual(self.sequence.frame_index, 15)
        self.sequence.update(self.player, 10)
        self.assertEqual((self.player.x, self.player.y), (TOUCH_X, cave.GROUND_Y))
        self.assertFalse(self.sequence.start(self.player))

    def test_large_delta_can_cross_phases_and_reset_can_replay(self):
        self.assertTrue(self.sequence.start(self.player))
        self.sequence.update(self.player, 30)
        self.assertEqual(self.sequence.phase, "touch")
        self.assertEqual(self.player.get_hitbox()[2], cave.END_WALL_X)
        self.sequence.reset()
        self.player.recover_at(TOUCH_X - 90, cave.GROUND_Y, 0)
        self.assertTrue(self.sequence.can_start(self.player))
        self.assertTrue(self.sequence.start(self.player))
        self.assertEqual(self.sequence.phase, "observe")

    def test_game_loop_locks_controls_until_restart(self):
        # This test owns the renderer through main(), so release the setup canvas first.
        del self.sequence
        del self.player
        self.doCleanups()
        start = [keydown(key) for key in (pico.SDLK_e, pico.SDLK_SPACE, pico.SDLK_x)]
        interfere = [keydown(key) for key in (pico.SDLK_e, pico.SDLK_q, pico.SDLK_SPACE, pico.SDLK_x)]
        events = [[], start, *([interfere] * 180), [keydown(pico.SDLK_r)], [pico.Event(pico.SDL_QUIT)]]
        keys = [0] * pico.SDL_NUM_SCANCODES
        keys[pico.SDL_SCANCODE_SPACE] = 1
        frames = []
        draw = SigilApproach.draw
        update = Player.update

        def create_player(x, y, width, **kwargs):
            return Player(TOUCH_X - 270, y, width, **kwargs)

        def record(sequence, player, camera):
            frames.append((sequence.phase, player.x, player.y, player.facing, player.attack_time))
            return draw(sequence, player, camera)

        with patch.object(main, "configure_display", return_value=False), \
                patch.object(main, "run_title", return_value=False), \
                patch.object(main, "Player", new=create_player), \
                patch.object(pico, "get_events", side_effect=events), \
                patch.object(pico, "SDL_GetKeyboardFocus", return_value=True), \
                patch.object(pico, "SDL_GetKeyboardState", return_value=keys), \
                patch.object(main, "read_movement", return_value=(-1, True, True)), \
                patch.object(main, "perf_counter", side_effect=count(step=1 / 60)), \
                patch.object(main, "sleep"), \
                patch.object(main, "draw_mount_prompt") as prompt, \
                patch.object(Player, "update", autospec=True, side_effect=update) as manual_update, \
                patch.object(SigilApproach, "draw", new=record):
            main.main()

        self.assertEqual(manual_update.call_count, 2)  # Before investigation and after R only.
        prompt.assert_called_once()
        controlled = frames[1:-1]
        self.assertTrue(all(frame[0] != "idle" for frame in controlled))
        self.assertTrue(all(frame[2:] == (cave.GROUND_Y, 1, None) for frame in controlled))
        self.assertTrue(all(a[1] <= b[1] for a, b in zip(controlled, controlled[1:])))
        self.assertEqual(controlled[-1][:2], ("touch", TOUCH_X))
        self.assertEqual(frames[-1][:3], ("idle", cave.SPAWN[0], cave.GROUND_Y))


if __name__ == "__main__":
    unittest.main()

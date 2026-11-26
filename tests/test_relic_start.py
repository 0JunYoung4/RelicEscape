"""Exercise the acquired-relic checkpoint through the normal game loop."""

import gc
import os
import unittest
from itertools import count
from unittest.mock import patch

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_RENDER_DRIVER"] = "software"

from pico2d import pico2d as pico

import main
from lower_caves import COMBAT_CENTER_X, GALLERY_WIDTH, RELIC_X, LowerCaves


def keydown(key):
    event = pico.Event(pico.SDL_KEYDOWN)
    event.key = key
    return event


class RelicStartTests(unittest.TestCase):
    def tearDown(self):
        gc.collect()

    def test_default_enter_and_r_start_a_fresh_combat_room_with_the_relic(self):
        players, frames = [], []
        player_type, draw = main.Player, LowerCaves.draw
        event_index = count()

        def make_player(*args, **kwargs):
            player = player_type(*args, **kwargs)
            players.append(player)
            return player

        def events():
            frame = next(event_index)
            if frame == 0:
                return [keydown(pico.SDLK_RETURN)]
            if frame == 2:
                players[0].x = COMBAT_CENTER_X
            if frame == 3:
                return [keydown(pico.SDLK_r)]
            return [pico.Event(pico.SDL_QUIT)] if frame == 4 else []

        def record(room, camera):
            frames.append((room.room, room.has_relic, players[0].x, room.encounter_started, room.exit_progress))
            draw(room, camera)

        with patch.object(main, "configure_display", return_value=False), \
                patch.object(main, "Player", side_effect=make_player), \
                patch.object(main, "poll_events", side_effect=events), \
                patch.object(pico, "SDL_GetKeyboardFocus", return_value=True), \
                patch.object(main, "read_movement", return_value=(0, False, False)), \
                patch.object(main, "perf_counter", side_effect=count(step=1 / 60)), \
                patch.object(main, "sleep"), patch.object(LowerCaves, "draw", new=record):
            main.main()

        self.assertEqual(frames[0], ("combat", True, 130, False, 0))
        self.assertTrue(frames[1][3])
        self.assertEqual(frames[2], frames[0])

    def test_checkpoint_has_relic_supports_placement_restart_and_combat_entry(self):
        players, travels, frames = [], [], []
        event_index = count()
        player_type, travel_type = main.Player, main.RelicTravel
        draw = LowerCaves.draw

        def make_player(*args, **kwargs):
            player = player_type(*args, **kwargs)
            players.append(player)
            return player

        def make_travel():
            travel = travel_type()
            travels.append(travel)
            return travel

        def events():
            frame = next(event_index)
            if frame == 1:
                return [keydown(pico.SDLK_e)]
            if frame == 2:
                return [keydown(pico.SDLK_r)]
            if frame == 3:
                players[0].x = GALLERY_WIDTH - 95
            return [pico.Event(pico.SDL_QUIT)] if frame == 4 else []

        def record(room, camera):
            frames.append((room.room, players[0].x, room.has_relic,
                           travels[0].anchor is not None, tuple(p.hp for p in room.pillbugs)))
            draw(room, camera)

        with patch.object(main, "configure_display", return_value=False), \
                patch.object(main, "run_title", return_value=False), \
                patch.object(main, "Player", side_effect=make_player) as player_factory, \
                patch.object(main, "RelicTravel", side_effect=make_travel), \
                patch.object(main, "poll_events", side_effect=events), \
                patch.object(pico, "SDL_GetKeyboardFocus", return_value=True), \
                patch.object(main, "read_movement", return_value=(1, False, False)), \
                patch.object(main, "perf_counter", side_effect=count(step=1 / 60)), \
                patch.object(main, "sleep"), \
                patch.object(LowerCaves, "draw", new=record):
            main.main(after_relic=True)
            self.assertEqual(frames[0][0], "gallery")
            self.assertGreaterEqual(frames[0][1], RELIC_X)
            self.assertTrue(all(frame[2] for frame in frames))
            self.assertTrue(frames[1][3])
            self.assertEqual(frames[2][:4], ("gallery", RELIC_X, True, False))
            self.assertEqual(frames[2][4], (0, 0))
            self.assertEqual(frames[3][0], "combat")
            player_factory.reset_mock()
            players.clear()
            travels.clear()

    def test_gallery_death_returns_to_acquired_relic_checkpoint(self):
        pico.open_canvas(960, 540)
        self.addCleanup(pico.close_canvas)
        rooms, frames = [], []
        draw, health_type = LowerCaves.draw, main.Health

        def make_room(cave):
            room = LowerCaves(cave)
            rooms.append(room)
            return room

        def make_health(*args, **kwargs):
            health = health_type(*args, **kwargs)
            health.current = 0
            health.hit_at = -100
            return health

        def record(room, camera):
            frames.append((room.room, room.has_relic, room.target(player[0])))
            draw(room, camera)

        player = []
        player_type = main.Player

        def make_player(*args, **kwargs):
            player.append(player_type(*args, **kwargs))
            return player[-1]

        with patch.object(main, "LowerCaves", side_effect=make_room) as room_factory, \
                patch.object(main, "Player", side_effect=make_player) as player_factory, \
                patch.object(main, "Health", side_effect=make_health), \
                patch.object(main, "poll_events", side_effect=([], [pico.Event(pico.SDL_QUIT)])), \
                patch.object(pico, "SDL_GetKeyboardFocus", return_value=True), \
                patch.object(main, "read_movement", return_value=(0, False, False)), \
                patch.object(main, "sleep"), \
                patch.object(LowerCaves, "draw", new=record):
            self.assertIsNone(main.run_opening_cave(False, after_relic=True))
            self.assertEqual(len(rooms), 2)
            self.assertEqual(frames, [("gallery", True, None)])
            self.assertEqual(player[0].x, RELIC_X)
            room_factory.reset_mock()
            player_factory.reset_mock()
            rooms.clear()
            player.clear()

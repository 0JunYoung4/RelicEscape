"""Verify the arena seals before spawn, prevents relic escape, and opens on clear."""

import gc
import os
import unittest
from itertools import count
from types import SimpleNamespace
from unittest.mock import Mock, patch

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_RENDER_DRIVER"] = "software"

from pico2d import pico2d as pico

import main
from lower_caves import (COMBAT_CENTER_X, COMBAT_ENTRANCE_BARRIER, COMBAT_EXIT_DURATION,
                         COMBAT_GATE_DURATION, COMBAT_WIDTH, LowerCaves)
from player import Player


class CombatGateTests(unittest.TestCase):
    def setUp(self):
        pico.open_canvas(960, 540)
        self.cave = SimpleNamespace(width=960, height=540, shaft=SimpleNamespace(w=4096))
        self.room = LowerCaves(self.cave)
        self.room.room, self.room.has_relic = "combat", True
        self.player = Player(130, 0, COMBAT_WIDTH)
        self.camera = main.Camera(960, COMBAT_WIDTH)
        self.room.enter(self.player, self.camera)

    def tearDown(self):
        del self.room, self.player
        gc.collect()
        pico.close_canvas()

    def trigger(self, dt=COMBAT_GATE_DURATION):
        self.player.recover_at(COMBAT_CENTER_X, 0, 0)
        self.room.update_enemies(self.player, dt)

    def clear_pillbugs(self):
        for bug in self.room.combat_pillbugs:
            bug.hp = 0
        self.room.update_enemies(self.player, 0)

    def test_center_trigger_immediately_seals_then_blocks_standing_crouched_and_jumping_exit(self):
        self.assertFalse(self.room.entrance_locked)
        self.trigger(0)
        self.assertTrue(self.room.entrance_locked)
        self.assertIn(COMBAT_ENTRANCE_BARRIER, self.player.terrain)
        for crouching in (False, True):
            self.player.recover_at(COMBAT_ENTRANCE_BARRIER[2] + 100, 0, 0)
            for _ in range(90):
                self.room.update(self.player, self.camera, 1 / 60, interact=False,
                                 direction=-1, running=True, jump_pressed=False, jump_held=False,
                                 crouching=crouching, attack_pressed=False)
            self.assertEqual(self.room.room, "combat")
            self.assertGreaterEqual(self.player.get_hitbox()[0], COMBAT_ENTRANCE_BARRIER[2] - 1e-6)
        self.player.recover_at(COMBAT_ENTRANCE_BARRIER[2] + 20, 0, 0)
        for frame in range(90):
            self.room.update(self.player, self.camera, 1 / 60, interact=False,
                             direction=-1, running=True, jump_pressed=frame == 0, jump_held=True,
                             crouching=False, attack_pressed=False)
        self.assertEqual(self.room.room, "combat")
        self.assertGreater(self.player.x, COMBAT_ENTRANCE_BARRIER[0])

    def test_one_remaining_enemy_keeps_seal_and_clear_reopens_both_exits(self):
        self.trigger()
        self.clear_pillbugs()
        self.room.golems[0].hp = 0
        self.room.update_enemies(self.player, 1)
        self.assertEqual(self.room.entrance_progress, 1)
        self.assertFalse(self.room.exit_open)
        self.room.golems[-1].hp = 0
        self.room.update_enemies(self.player, COMBAT_GATE_DURATION / 2)
        self.assertTrue(self.room.entrance_locked)
        self.assertGreater(self.room.entrance_progress, 0)
        self.assertGreater(self.room.exit_progress, 0)
        self.room.update_enemies(self.player, COMBAT_EXIT_DURATION)
        self.assertFalse(self.room.entrance_locked)
        self.assertTrue(self.room.exit_open)
        self.assertNotIn(COMBAT_ENTRANCE_BARRIER, self.player.terrain)
        self.player.recover_at(COMBAT_ENTRANCE_BARRIER[2] + 50, 0, 0)
        self.room.update(self.player, self.camera, .8, interact=False, direction=-1, running=True,
                         jump_pressed=False, jump_held=False, crouching=False, attack_pressed=False)
        self.assertEqual(self.room.room, "gallery")
        self.assertTrue(self.room.has_relic)

    def test_relic_can_move_inside_but_cannot_cross_the_locked_entrance(self):
        outside = (130, 0, 0)
        self.assertTrue(self.room.allows_relic_destination(outside))
        self.trigger()
        self.assertFalse(self.room.allows_relic_destination(outside))
        self.assertFalse(self.room.allows_relic_destination((130, 700, 0)))
        self.assertTrue(self.room.allows_relic_destination((COMBAT_CENTER_X + 100, 0, 0)))
        self.clear_pillbugs()
        for golem in self.room.golems:
            golem.hp = 0
        self.room.update_enemies(self.player, COMBAT_EXIT_DURATION)
        self.assertTrue(self.room.allows_relic_destination(outside))

    def test_fresh_encounter_has_an_open_entrance_and_completed_room_never_reseals(self):
        self.assertEqual((self.room.encounter_started, self.room.entrance_progress), (False, 0))
        self.trigger()
        self.room.enter(self.player, self.camera)
        self.assertGreater(self.player.get_hitbox()[0], COMBAT_ENTRANCE_BARRIER[2])
        self.clear_pillbugs()
        for golem in self.room.golems:
            golem.hp = 0
        self.room.update_enemies(self.player, COMBAT_EXIT_DURATION)
        self.room.room = "gallery"
        self.room.enter(self.player, self.camera)
        self.room.room = "combat"
        self.room.enter(self.player, self.camera)
        self.trigger()
        self.assertFalse(self.room.entrance_locked)
        self.assertTrue(self.room.exit_open)
        fresh = LowerCaves(self.cave)
        self.assertFalse(fresh.encounter_started)
        self.assertFalse(fresh.entrance_locked)


class CombatGateMainLoopTests(unittest.TestCase):
    def test_start_reclaims_old_relic_and_actual_recall_cannot_bypass_the_seal(self):
        pico.open_canvas(960, 540)
        rooms, players, travels = [], [], []
        sequence = Mock(active=True, stood_up=True)
        event_frames = count()
        player_type, travel_type = main.Player, main.RelicTravel

        def make_room(cave):
            room = LowerCaves(cave)
            room.room, room.has_relic = "combat", True
            rooms.append(room)
            return room

        def make_player(*args, **kwargs):
            player = player_type(*args, **kwargs)
            players.append(player)
            return player

        def make_travel():
            travel = travel_type()
            travels.append(travel)
            return travel

        def events():
            frame = next(event_frames)
            if frame == 2:
                self.assertIsNotNone(travels[0].anchor)
                players[0].recover_at(COMBAT_CENTER_X, 0, 0)
            if frame == 3:
                self.assertTrue(rooms[0].entrance_locked)
                self.assertIsNone(travels[0].anchor)
                self.assertEqual(travels[0].marks, [])
                travels[0].anchor = main.RelicAnchor(130, 0, 0, 70, 0)
            if frame == 4:
                self.assertEqual(players[0].x, COMBAT_CENTER_X)
                self.assertIsNotNone(travels[0].anchor)
            if frame in (1, 3):
                event = pico.Event(pico.SDL_KEYDOWN)
                event.key = pico.SDLK_e
                return [event]
            return [pico.Event(pico.SDL_QUIT)] if frame == 5 else []

        try:
            with patch.object(main, "LowerCaves", side_effect=make_room) as room_factory, \
                    patch.object(main, "Player", side_effect=make_player) as player_factory, \
                    patch.object(main, "RelicTravel", side_effect=make_travel), \
                    patch.object(main, "SigilApproach", return_value=sequence), \
                    patch.object(main, "read_movement", return_value=(0, False, False)), \
                    patch.object(main, "perf_counter", side_effect=count(step=1 / 60)), \
                    patch.object(main, "sleep"), \
                    patch.object(pico, "SDL_GetKeyboardFocus", return_value=True), \
                    patch.object(pico, "get_events", side_effect=events):
                self.assertIsNone(main.run_opening_cave(False))
                sequence.reset_mock()
                room_factory.reset_mock()
                player_factory.reset_mock()
                rooms.clear()
                players.clear()
                travels.clear()
        finally:
            gc.collect()
            pico.close_canvas()

"""Check the 65-HP golem through sword damage and the actual combat room."""

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
from crystal_golem import BODY_WIDTH, MAX_HP, CrystalGolem
from health import CONTACT_DAMAGE, Health
from lower_caves import COMBAT_PLATFORMS, COMBAT_TERRAIN, COMBAT_WIDTH, LowerCaves
from player import STARTING_ATTACK_POWER, Player


class CrystalGolemTests(unittest.TestCase):
    def test_free_patrol_does_not_flip_due_to_float_rounding_at_large_coordinates(self):
        for fps in (20, 30, 60, 120):
            for direction in (-1, 1):
                with self.subTest(fps=fps, direction=direction):
                    golem = CrystalGolem(1512.796005706134, 1652.796005706134,
                                         direction=direction)
                    start = golem.x
                    for _ in range(2 * fps):
                        golem.update(1 / fps, (), (), 1920)
                        self.assertEqual(golem.direction, direction)
                    self.assertAlmostEqual(golem.x, start + direction * 44)

    def test_patrol_turns_once_at_edge_then_moves_away(self):
        golem = CrystalGolem(1512.796005706134, 1652.796005706134, direction=1)
        golem.x = golem.right - .01
        golem.update(1 / 60, (), (), 1920)
        self.assertEqual((golem.x, golem.direction), (golem.right, -1))
        golem.update(1 / 60, (), (), 1920)
        self.assertEqual(golem.direction, -1)
        self.assertLess(golem.x, golem.right)

    def test_six_separate_12_damage_hits_kill_a_65_hp_golem(self):
        golem = CrystalGolem(700, 900)
        self.assertEqual(golem.hp, 65)
        strike = (760, 10, 840, 80)
        for swing, expected in enumerate((53, 41, 29, 17, 5, 0), 1):
            self.assertTrue(golem.check_strike(strike, 1, STARTING_ATTACK_POWER, swing))
            self.assertEqual(golem.hp, expected)
        self.assertFalse(golem.check_strike(strike, 1, STARTING_ATTACK_POWER, 7))
        x = golem.x
        golem.update(5, (), (), 1920)
        self.assertEqual((golem.x, golem.hp), (x, 0))

    def test_misses_and_repeated_contact_with_one_swing_do_not_remove_extra_hp(self):
        golem = CrystalGolem(700, 900)
        self.assertFalse(golem.check_strike((0, 0, 20, 100), 1, 12, 1))
        self.assertFalse(golem.check_strike((760, 200, 840, 300), 1, 12, 1))
        self.assertEqual(golem.hp, MAX_HP)
        self.assertTrue(golem.check_strike((760, 0, 840, 100), 1, 12, 1))
        self.assertFalse(golem.check_strike((760, 0, 840, 100), -1, 12, 1))
        self.assertEqual(golem.hp, 53)

    def test_patrol_stops_at_stone_faces_and_keeps_moving_when_hit(self):
        golem = CrystalGolem(100, 900, direction=1)
        golem.x = 400
        wall = (500, 0, 600, 200)
        golem.update(10, (), (wall,), 1000)
        self.assertEqual(golem.x + BODY_WIDTH / 2, wall[0])
        self.assertEqual(golem.direction, -1)
        golem.check_strike((400, 0, 450, 100), 1, 12, 1)
        position = golem.x
        golem.update(.1, (), (wall,), 1000)
        self.assertAlmostEqual(golem.x, position - 2.2)
        for _ in range(500):
            golem.update(.1, (), (wall,), 1000)
            self.assertGreaterEqual(golem.x, golem.left)
            self.assertLessEqual(golem.x + BODY_WIDTH / 2, wall[0])


class CrystalGolemRoomTests(unittest.TestCase):
    def setUp(self):
        pico.open_canvas(960, 540)
        cave = SimpleNamespace(width=960, height=540, shaft=SimpleNamespace(w=4096))
        self.lower = LowerCaves(cave)
        self.lower.room = "combat"
        self.lower.encounter_started = True
        self.player = Player(130, 0, COMBAT_WIDTH)
        self.camera = main.Camera(960, COMBAT_WIDTH)
        self.lower.enter(self.player, self.camera)

    def tearDown(self):
        del self.lower, self.player
        gc.collect()
        pico.close_canvas()

    def test_combat_room_damage_recoil_contact_and_dead_enemy_removal(self):
        first, second = self.lower.golems
        self.assertEqual((first.hp, second.hp), (65, 65))
        for swing, expected in enumerate((53, 41, 29, 17, 5, 0), 1):
            self.assertTrue(self.player.recover_at(first.x - 120, first.floor_y, 0))
            self.player.swing_id = swing
            self.player.slash = (0, 1, "attack")
            self.lower.update_enemies(self.player, 0)
            self.assertEqual((first.hp, second.hp), (expected, 65))
            self.assertGreater(self.player.recoil_remaining, 0)
            self.lower.update_enemies(self.player, 0)
            self.assertEqual(first.hp, expected)
        self.player.slash = None
        self.lower.update_enemies(self.player, .2)
        with patch.object(self.lower.golem_walk, "draw", wraps=self.lower.golem_walk.draw) as draw:
            self.lower.draw(self.camera)
            self.assertEqual(draw.call_count, 1)
        self.player.recover_at(second.x, second.floor_y, 0)
        health = Health((130, 0, 0))
        self.assertTrue(health.check_contact(self.player, self.lower.enemies, 0))
        self.assertEqual(health.current, 100 - CONTACT_DAMAGE)
        second.hp = 0
        self.assertFalse(health.check_contact(self.player, self.lower.enemies, 1))

    def test_both_golems_start_at_top_ends_and_patrol_separate_halves(self):
        left, bottom, right, top = COMBAT_PLATFORMS[1]
        center = (left + right) / 2
        first, second = self.lower.golems
        self.assertEqual(first.x, left + BODY_WIDTH / 2)
        self.assertEqual(second.x, right - BODY_WIDTH / 2)
        self.assertEqual((first.direction, second.direction), (1, -1))
        for golem, platform in zip(self.lower.golems,
                                   ((left, bottom, center, top), (center, bottom, right, top))):
            self.assertEqual(golem.floor_y, platform[3])
            for _ in range(600):
                golem.update(.1, (), COMBAT_TERRAIN, COMBAT_WIDTH)
                self.assertGreaterEqual(golem.x - BODY_WIDTH / 2, platform[0])
                self.assertLessEqual(golem.x + BODY_WIDTH / 2, platform[2])

    def test_death_restarts_golems_at_65_hp_and_keeps_acquired_relic(self):
        rooms, healths, frames = [], [], []
        sequence = Mock(active=True, stood_up=True)
        event_frames = count()

        def make_room(cave):
            room = LowerCaves(cave)
            room.room = "combat"
            room.encounter_started = True
            room.has_relic = not rooms
            room.golems = [CrystalGolem(120, 140)]
            rooms.append(room)
            return room

        def make_health(*args, **kwargs):
            health = Health(*args, **kwargs)
            if not healths:
                health.current = CONTACT_DAMAGE
            healths.append(health)
            return health

        def read_events():
            return [pico.Event(pico.SDL_QUIT)] if next(event_frames) == 100 else []

        def record_hud(health, height, now):
            frames.append(health.current)

        with patch.object(main, "LowerCaves", side_effect=make_room) as room_factory, \
                patch.object(main, "Health", side_effect=make_health), \
                patch.object(main, "SigilApproach", return_value=sequence), \
                patch.object(main, "read_movement", return_value=(0, False, False)), \
                patch.object(main, "perf_counter", side_effect=count(step=1 / 120)), \
                patch.object(main, "sleep"), \
                patch.object(pico, "SDL_GetKeyboardFocus", return_value=True), \
                patch.object(pico, "get_events", side_effect=read_events), \
                patch.object(Health, "draw_hud", new=record_hud):
            self.assertIsNone(main.run_opening_cave(False))
        self.assertEqual(len(rooms), 2)
        self.assertIn(0, frames)
        self.assertIn(100, frames)
        self.assertTrue(rooms[-1].has_relic)
        self.assertEqual(rooms[-1].golems[0].hp, 65)
        sequence.reset_mock()
        room_factory.reset_mock()
        rooms.clear()
        gc.collect()

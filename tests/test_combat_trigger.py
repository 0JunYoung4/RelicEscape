"""Verify the room remains empty until the hero reaches its center."""

import gc
import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_RENDER_DRIVER"] = "software"

from pico2d import pico2d as pico

from health import Health
from lower_caves import (COMBAT_CENTER_X, COMBAT_EXIT_DURATION, COMBAT_TRIGGER_RADIUS,
                         COMBAT_WIDTH, LowerCaves)
from main import Camera
from player import Player


class CombatTriggerTests(unittest.TestCase):
    def setUp(self):
        pico.open_canvas(960, 540)
        self.cave = SimpleNamespace(width=960, height=540, shaft=SimpleNamespace(w=4096))
        self.room = LowerCaves(self.cave)
        self.room.room = "combat"
        self.player = Player(130, 0, COMBAT_WIDTH)
        self.camera = Camera(960, COMBAT_WIDTH)
        self.room.enter(self.player, self.camera)

    def tearDown(self):
        del self.room, self.player
        gc.collect()
        pico.close_canvas()

    def test_waiting_room_has_no_visible_active_or_hittable_enemies_and_stays_sealed(self):
        golem = self.room.golems[0]
        initial = golem.x, golem.attack_cooldown
        for _ in range(600):
            self.room.update_enemies(self.player, 1 / 60)
        self.assertFalse(self.room.encounter_started)
        self.assertEqual(self.room.enemies, ())
        self.assertEqual((golem.x, golem.attack_cooldown), initial)
        self.assertEqual(self.room.projectiles, [])
        self.assertEqual(self.room.exit_progress, 0)
        bug = self.room.combat_pillbugs[0]
        self.player.recover_at(bug.x - 30, 0, 0)
        self.player.slash, self.player.swing_id = (0, 1, "attack"), 1
        self.room.update_enemies(self.player, .1)
        self.assertEqual(bug.hp, 30)
        health = Health((130, 0, 0))
        self.assertFalse(health.check_contact(self.player, self.room.enemies, 0))
        with patch.object(self.room.golem_walk, "draw") as golems, \
                patch.object(self.room.crawl, "draw") as bugs:
            self.room.draw(self.camera)
            golems.assert_not_called()
            bugs.assert_not_called()

    def test_running_to_center_triggers_four_enemies_at_each_frame_rate(self):
        for fps in (30, 60, 120):
            with self.subTest(fps=fps):
                self.room.encounter_started = False
                self.room.enter(self.player, self.camera)
                for _ in range(3 * fps):
                    self.room.update(self.player, self.camera, 1 / fps, interact=False,
                                     direction=1, running=True, jump_pressed=False, jump_held=False,
                                     crouching=False, attack_pressed=False)
                    self.room.update_enemies(self.player, 1 / fps)
                    if self.room.encounter_started:
                        break
                    self.assertLess(self.player.x, COMBAT_CENTER_X - COMBAT_TRIGGER_RADIUS)
                    self.assertEqual(self.room.enemies, ())
                self.assertTrue(self.room.encounter_started)
                self.assertLessEqual(abs(self.player.x - COMBAT_CENTER_X), COMBAT_TRIGGER_RADIUS)
                self.assertEqual([enemy.hp for enemy in self.room.enemies], [65, 65, 30, 30])

    def test_encounter_and_clear_persist_on_retreat_and_only_fresh_room_waits_again(self):
        self.player.recover_at(COMBAT_CENTER_X, 0, 0)
        self.room.update_enemies(self.player, 0)
        enemies = self.room.enemies
        enemies[0].hp = 53
        self.room.room = "gallery"
        self.room.enter(self.player, self.camera)
        self.room.room = "combat"
        self.room.enter(self.player, self.camera)
        self.assertTrue(self.room.encounter_started)
        self.assertEqual(self.room.enemies, enemies)
        self.assertEqual(self.room.enemies[0].hp, 53)
        for enemy in enemies:
            enemy.hp = 0
        self.room.update_enemies(self.player, COMBAT_EXIT_DURATION)
        self.player.recover_at(COMBAT_CENTER_X, 0, 0)
        self.room.update_enemies(self.player, .1)
        self.assertTrue(self.room.exit_open)
        self.assertTrue(all(enemy.hp == 0 for enemy in self.room.enemies))
        fresh = LowerCaves(self.cave)
        fresh.room = "combat"
        self.assertFalse(fresh.encounter_started)
        self.assertEqual(fresh.enemies, ())
        self.assertFalse(fresh.exit_open)

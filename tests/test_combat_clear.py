"""Exercise four-enemy clear, the stone cover, and the traversable lower shaft."""

import gc
import os
import unittest
from types import SimpleNamespace

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_RENDER_DRIVER"] = "software"

from pico2d import pico2d as pico

from crystal_projectile import CrystalProjectile
from health import Health
from lower_caves import (COMBAT_CENTER_X, COMBAT_EXIT_DURATION, COMBAT_EXIT_LEFT,
                         COMBAT_EXIT_RIGHT, COMBAT_OPEN_TERRAIN, COMBAT_SHAFT_FLOOR,
                         COMBAT_WIDTH, LowerCaves)
from main import Camera
from player import Player


class CombatClearTests(unittest.TestCase):
    def setUp(self):
        pico.open_canvas(960, 540)
        self.cave = SimpleNamespace(width=960, height=540, shaft=SimpleNamespace(w=4096))
        self.room = LowerCaves(self.cave)
        self.room.room, self.room.has_relic = "combat", True
        self.room.encounter_started = True
        self.player = Player(130, 0, COMBAT_WIDTH)
        self.camera = Camera(960, COMBAT_WIDTH)
        self.room.enter(self.player, self.camera)

    def tearDown(self):
        del self.room, self.player
        gc.collect()
        pico.close_canvas()

    def step(self, dt=1 / 60):
        self.room.update(self.player, self.camera, dt, interact=False, direction=0,
                         running=False, jump_pressed=False, jump_held=False,
                         crouching=False, attack_pressed=False)
        self.room.update_enemies(self.player, dt)

    def kill_with_sword(self, enemy):
        while enemy.hp:
            self.assertTrue(self.player.recover_at(enemy.x - 120, enemy.floor_y, 0))
            self.player.swing_id += 1
            self.player.slash = (0, 1, "attack")
            self.room.update_enemies(self.player, 0)
        self.player.slash = None

    def test_four_enemies_are_two_golems_above_and_two_pillbugs_on_either_side(self):
        self.assertEqual(len(self.room.enemies), 4)
        self.assertEqual([enemy.hp for enemy in self.room.enemies], [65, 65, 30, 30])
        left, right = self.room.combat_pillbugs
        self.assertLess(left.x, COMBAT_CENTER_X)
        self.assertGreater(right.x, COMBAT_CENTER_X)
        self.assertEqual((left.floor_y, right.floor_y), (0, 0))
        self.assertTrue(all(golem.floor_y > 0 for golem in self.room.golems))

    def test_all_four_actual_sword_kills_are_required_before_cover_opens(self):
        for enemy in self.room.enemies[:-1]:
            self.kill_with_sword(enemy)
            self.room.update_enemies(self.player, .1)
            self.assertFalse(self.room.exit_open)
            self.assertEqual(self.room.exit_progress, 0)
        self.kill_with_sword(self.room.enemies[-1])
        self.room.update_enemies(self.player, COMBAT_EXIT_DURATION / 2)
        self.assertGreater(self.room.exit_progress, 0)
        self.assertFalse(self.room.exit_open)
        self.assertEqual(self.player.ground_y, 0)
        self.room.update_enemies(self.player, COMBAT_EXIT_DURATION / 2)
        self.assertTrue(self.room.exit_open)
        self.assertEqual(self.player.terrain, COMBAT_OPEN_TERRAIN)

    def test_opening_only_removes_center_floor_and_camera_follows_descent(self):
        self.player.recover_at(COMBAT_CENTER_X, 0, 0)
        for _ in range(20):
            self.step()
        self.assertEqual((self.player.y, self.player.grounded), (0, True))
        for enemy in self.room.enemies:
            enemy.hp = 0
        self.room.update_enemies(self.player, COMBAT_EXIT_DURATION)
        for x in (COMBAT_EXIT_LEFT - 80, COMBAT_EXIT_RIGHT + 80):
            self.assertTrue(self.player.recover_at(x, 100, 0))
            for _ in range(60):
                self.step()
            self.assertEqual((self.player.y, self.player.grounded), (0, True))
        self.player.recover_at(COMBAT_CENTER_X, 0, 0)
        original_camera_y = self.camera.y
        for _ in range(120):
            self.step()
            foot = self.camera.world_to_screen(self.player.x, self.player.y)[1]
            self.assertGreaterEqual(foot, 0)
            self.assertLess(foot, 540)
        self.assertEqual((self.player.y, self.player.grounded), (COMBAT_SHAFT_FLOOR, True))
        self.assertLess(self.camera.y, original_camera_y)
        self.assertFalse(self.player._overlaps_terrain())

    def test_clear_persists_on_room_return_but_fresh_encounter_is_closed(self):
        for enemy in self.room.enemies:
            enemy.hp = 0
        self.room.update_enemies(self.player, COMBAT_EXIT_DURATION)
        self.room.room = "gallery"
        self.room.enter(self.player, self.camera)
        self.room.room = "combat"
        self.room.enter(self.player, self.camera)
        self.assertTrue(self.room.exit_open)
        self.assertEqual(self.player.ground_y, COMBAT_SHAFT_FLOOR)
        fresh = LowerCaves(self.cave)
        self.assertFalse(fresh.exit_open)
        self.assertEqual(sum(enemy.hp > 0 for enemy in (*fresh.golems, *fresh.combat_pillbugs)), 4)

    def test_ground_pillbug_contact_and_remaining_crystal_can_enter_the_open_shaft(self):
        bug = self.room.combat_pillbugs[0]
        self.player.recover_at(bug.x, 0, 0)
        health = Health((130, 0, 0))
        self.assertTrue(health.check_contact(self.player, self.room.enemies, 0))
        self.assertEqual(health.current, 90)
        for enemy in self.room.enemies:
            enemy.hp = 0
        self.room.update_enemies(self.player, COMBAT_EXIT_DURATION)
        shot = CrystalProjectile(COMBAT_CENTER_X, 80, 0, -200)
        self.room.projectiles.append(shot)
        self.room.update_projectiles(self.player, health, .3, 1)
        self.assertLess(shot.y, 0)
        self.assertTrue(shot.active)
        self.room.draw(self.camera)
        self.room.draw_combat_exit(self.camera)

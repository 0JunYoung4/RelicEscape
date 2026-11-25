"""Exercise four-enemy clear, the stone cover, and the traversable lower shaft."""

import gc
import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_RENDER_DRIVER"] = "software"

from pico2d import pico2d as pico

from crystal_golem import EMERGE_DURATION as GOLEM_EMERGE_DURATION
from crystal_projectile import CrystalProjectile
from health import Health
from lower_caves import (COMBAT_CENTER_X, COMBAT_COVER_THICKNESS, COMBAT_EXIT_DELAY, COMBAT_EXIT_DURATION,
                         COMBAT_EXIT_LEFT, COMBAT_EXIT_LIGHT_DURATION, COMBAT_EXIT_QUIET_DURATION,
                         COMBAT_EXIT_RIGHT, COMBAT_GATE_DURATION, COMBAT_OPEN_TERRAIN, COMBAT_SHAFT_FLOOR,
                         COMBAT_TERRAIN, COMBAT_WIDTH, LowerCaves)
from lower_route_a import ENTRY_LEDGE, ENTRY_X
from lower_route_connection import A_ORIGIN
from main import Camera
from pillbug import EMERGE_DURATION as PILLBUG_EMERGE_DURATION
from player import Player


class CombatClearTests(unittest.TestCase):
    def setUp(self):
        pico.open_canvas(960, 540)
        self.cave = SimpleNamespace(width=960, height=540, shaft=SimpleNamespace(w=4096))
        self.room = LowerCaves(self.cave)
        self.room.room, self.room.has_relic = "combat", True
        self.player = Player(130, 0, COMBAT_WIDTH)
        self.camera = Camera(960, COMBAT_WIDTH)
        self.room.enter(self.player, self.camera)
        self.player.recover_at(COMBAT_CENTER_X, 0, 0)
        self.room.update_enemies(self.player, COMBAT_GATE_DURATION)
        self.room.update_enemies(self.player, PILLBUG_EMERGE_DURATION)

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

    def defeat_enemies(self):
        for wave in (self.room.combat_pillbugs, self.room.golems):
            for enemy in wave:
                enemy.hp = 0
            self.room.update_enemies(self.player, 0)

    def test_ground_wave_has_two_pillbugs_below_the_hidden_golems(self):
        self.assertEqual(self.room.enemies, tuple(self.room.combat_pillbugs))
        self.assertEqual([enemy.hp for enemy in self.room.enemies], [30, 30])
        left, right = self.room.combat_pillbugs
        self.assertLess(left.x, COMBAT_CENTER_X)
        self.assertGreater(right.x, COMBAT_CENTER_X)
        self.assertEqual((left.floor_y, right.floor_y), (0, 0))
        self.assertTrue(all(golem.floor_y > 0 for golem in self.room.golems))

    def test_all_four_actual_sword_kills_are_required_before_cover_opens(self):
        first_bug, last_bug = self.room.combat_pillbugs
        first_golem, last_golem = self.room.golems
        initial_golem = first_golem.x, first_golem.attack_cooldown
        self.player.recover_at(first_golem.x - 120, first_golem.floor_y, 0)
        self.player.slash, self.player.swing_id = (0, 1, "attack"), 1
        self.room.update_enemies(self.player, .1)
        self.assertEqual((first_golem.x, first_golem.attack_cooldown, first_golem.hp), (*initial_golem, 45))
        self.assertFalse(Health((130, 0, 0)).check_contact(self.player, self.room.enemies, 0))
        with patch.object(first_golem, "draw") as draw:
            self.room.draw(self.camera)
            draw.assert_not_called()
        self.kill_with_sword(first_bug)
        self.assertEqual(self.room.enemies, tuple(self.room.combat_pillbugs))
        self.kill_with_sword(last_bug)
        self.assertTrue(all(golem.phase == "emerge" for golem in self.room.golems))
        self.assertTrue(self.room.entrance_locked)
        self.assertEqual(self.room.exit_progress, 0)
        with patch.object(self.room.golem_emergence, "draw") as draw:
            self.room.draw(self.camera)
            self.assertEqual(draw.call_count, 2)
        self.room.update_enemies(self.player, GOLEM_EMERGE_DURATION)
        self.kill_with_sword(first_golem)
        self.room.update_enemies(self.player, .1)
        self.assertTrue(self.room.entrance_locked)
        self.assertEqual(self.room.exit_progress, 0)
        self.assertEqual(self.room.exit_seam_light, 0)
        self.kill_with_sword(last_golem)
        self.room.update_enemies(self.player, COMBAT_EXIT_QUIET_DURATION)
        self.assertEqual(self.room.exit_seam_light, 0)
        self.assertEqual(self.room.exit_progress, 0)
        self.room.follow_camera(self.player, self.camera)
        _, seam_y = self.camera.world_to_screen(COMBAT_EXIT_LEFT, 0)
        _, hero_y = self.camera.world_to_screen(self.player.x, self.player.y)
        self.assertGreater(seam_y, 24)
        self.assertLess(hero_y, self.cave.height * .8)
        self.player.recover_at(COMBAT_CENTER_X, 0, 0)
        self.step(COMBAT_EXIT_LIGHT_DURATION / 2)
        self.assertGreater(self.room.exit_seam_light, 0)
        self.assertEqual(self.room.exit_progress, 0)
        self.assertEqual(self.room.entrance_progress, 1)
        self.assertIn(COMBAT_TERRAIN[-1], self.player.terrain)
        self.assertEqual((self.player.y, self.player.ground_y), (0, 0))
        self.room.update_enemies(self.player, (COMBAT_EXIT_LIGHT_DURATION + COMBAT_EXIT_DURATION) / 2)
        self.assertAlmostEqual(self.room.exit_progress, .5)
        self.assertFalse(self.room.exit_open)
        self.assertEqual(self.player.ground_y, COMBAT_SHAFT_FLOOR)
        self.room.update_enemies(self.player, COMBAT_EXIT_DURATION / 2 + 1 / 60)
        self.assertTrue(self.room.exit_open)
        self.assertEqual(self.room.exit_seam_light, 0)
        self.assertEqual(self.player.terrain, COMBAT_OPEN_TERRAIN)

    def test_opening_only_removes_center_floor_and_camera_follows_descent(self):
        self.player.recover_at(COMBAT_CENTER_X, 0, 0)
        for _ in range(20):
            self.step()
        self.assertEqual((self.player.y, self.player.grounded), (0, True))
        self.defeat_enemies()
        self.room.update_enemies(self.player, COMBAT_EXIT_DELAY + COMBAT_EXIT_DURATION)
        for x in (COMBAT_EXIT_LEFT - 80, COMBAT_EXIT_RIGHT + 80):
            self.assertTrue(self.player.recover_at(x, 100, 0))
            for _ in range(60):
                self.step()
            self.assertEqual((self.player.y, self.player.grounded), (0, True))
        self.player.recover_at(COMBAT_CENTER_X, 0, 0)
        original_camera_y = self.camera.y
        lowest_combat_camera = original_camera_y
        saw_route_fall = False
        for _ in range(120):
            self.step()
            if self.room.room == "combat":
                lowest_combat_camera = min(lowest_combat_camera, self.camera.y)
            elif self.player.vertical_speed < 0:
                saw_route_fall = True
            foot = self.camera.world_to_screen(self.player.x, self.player.y)[1]
            self.assertGreaterEqual(foot, 0)
            self.assertLess(foot, 540)
        self.assertEqual(self.room.room, "route_a")
        self.assertEqual((self.player.x, self.player.y, self.player.grounded),
                         (A_ORIGIN[0] + ENTRY_X, A_ORIGIN[1] + ENTRY_LEDGE[3], True))
        self.assertTrue(saw_route_fall)
        self.assertLess(lowest_combat_camera, original_camera_y)
        self.assertFalse(self.player._overlaps_terrain())

    def test_crumbling_floor_removes_both_sides_of_the_cover_together(self):
        self.defeat_enemies()
        self.room.update_enemies(self.player, COMBAT_EXIT_DELAY + COMBAT_EXIT_DURATION / 2)
        terrain = self.room.combat_terrain()
        self.assertFalse(self.room.exit_open)
        self.assertNotIn(COMBAT_TERRAIN[-1], terrain)
        # Check both sides before the falling debris finishes animating.
        for x in (COMBAT_EXIT_LEFT + 50, COMBAT_EXIT_RIGHT - 50):
            self.player.terrain = terrain
            self.player.recover_at(x, 0, 0)
            for _ in range(12):
                self.player.update(0, False, 1 / 60)
            self.assertLess(self.player.y, 0)

    def test_clear_persists_on_room_return_but_fresh_encounter_is_closed(self):
        self.defeat_enemies()
        self.room.update_enemies(self.player, COMBAT_EXIT_DELAY + COMBAT_EXIT_DURATION)
        self.room.room = "gallery"
        self.room.enter(self.player, self.camera)
        self.room.room = "combat"
        self.room.enter(self.player, self.camera)
        self.assertTrue(self.room.exit_open)
        self.assertEqual(self.player.ground_y, COMBAT_SHAFT_FLOOR)
        fresh = LowerCaves(self.cave)
        self.assertFalse(fresh.exit_open)
        self.assertEqual(fresh.exit_seam_light, 0)
        self.assertEqual(sum(enemy.hp > 0 for enemy in (*fresh.golems, *fresh.combat_pillbugs)), 4)

    def test_fixed_shaft_ledges_remain_after_the_floor_collapses(self):
        self.defeat_enemies()
        self.room.update_enemies(self.player, COMBAT_EXIT_DELAY + COMBAT_EXIT_DURATION)
        for x in (COMBAT_EXIT_LEFT + 20, COMBAT_EXIT_RIGHT - 20):
            self.assertTrue(self.player.recover_at(x, 0, 0))
            for _ in range(60):
                self.player.update(0, False, 1 / 60)
            self.assertEqual((self.player.y, self.player.grounded), (-COMBAT_COVER_THICKNESS, True))

    def test_ground_pillbug_contact_and_remaining_crystal_can_enter_the_open_shaft(self):
        bug = self.room.combat_pillbugs[0]
        self.player.recover_at(bug.x, 0, 0)
        health = Health((130, 0, 0))
        self.assertTrue(health.check_contact(self.player, self.room.enemies, 0))
        self.assertEqual(health.current, 90)
        self.defeat_enemies()
        self.room.update_enemies(self.player, COMBAT_EXIT_DELAY + COMBAT_EXIT_DURATION)
        shot = CrystalProjectile(COMBAT_CENTER_X, 80, 0, -200)
        self.room.projectiles.append(shot)
        self.room.update_projectiles(self.player, health, .3, 1)
        self.assertLess(shot.y, 0)
        self.assertTrue(shot.active)
        self.room.draw(self.camera)
        self.room.draw_combat_exit(self.camera)

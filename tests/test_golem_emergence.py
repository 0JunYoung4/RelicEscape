"""Check heavy fist-braced emergence before normal golem combat."""

import gc
import os
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_RENDER_DRIVER"] = "software"

from pico2d import pico2d as pico

from crystal_golem import EMERGE_ATTACK_DELAY, EMERGE_DURATION, CrystalGolem
from health import Health
from lower_caves import COMBAT_CENTER_X, COMBAT_PLATFORMS, COMBAT_WIDTH, LowerCaves
from main import Camera
from player import Player


class GolemEmergenceTests(unittest.TestCase):
    def test_fists_stay_on_platform_and_normal_patrol_resumes_at_each_frame_rate(self):
        for fps in (30, 60, 120):
            with self.subTest(fps=fps):
                golem = CrystalGolem.on_platform(COMBAT_PLATFORMS[2], direction=-1)
                golem.begin_emergence()
                start = golem.x, golem.floor_y, golem.direction, golem.attack_cooldown
                for _ in range(round(EMERGE_DURATION * fps) + 2):
                    self.assertIsNone(golem.update(1 / fps, (900, 0, 940, 140), (), COMBAT_WIDTH))
                    self.assertEqual((golem.x, golem.floor_y, golem.direction), start[:3])
                    if golem.phase != "emerge":
                        break
                    self.assertEqual(golem.attack_cooldown, start[3])
                self.assertEqual((golem.phase, golem.time), ("active", 0))
                self.assertGreaterEqual(golem.attack_cooldown, EMERGE_ATTACK_DELAY)
                golem.update(.05, (), (), COMBAT_WIDTH)
                self.assertLess(golem.x, start[0])

    def test_buried_golem_cannot_take_or_deal_invisible_damage(self):
        golem = CrystalGolem(400, 600)
        golem.begin_emergence()
        player = Mock()
        player.get_hitbox.return_value = (480, 0, 520, 140)
        health = Health((130, 0, 0))
        self.assertFalse(golem.check_strike((450, 0, 550, 100), 1, 12, 1))
        self.assertFalse(health.check_contact(player, (golem,), 0))
        self.assertEqual((golem.hp, health.current), (65, 100))
        golem.update(EMERGE_DURATION, player.get_hitbox(), (), COMBAT_WIDTH)
        self.assertTrue(golem.check_strike((450, 0, 550, 100), 1, 12, 1))
        self.assertTrue(health.check_contact(player, (golem,), 2))
        self.assertEqual((golem.hp, health.current), (53, 90))

    def test_repeated_start_does_not_reset_time_fire_a_queued_attack_or_revive(self):
        golem = CrystalGolem(400, 600)
        golem.attack_cooldown = 0
        golem.update(.01, (900, 0, 940, 140), (), COMBAT_WIDTH)
        self.assertIsNotNone(golem.attack_time)
        golem.begin_emergence()
        self.assertIsNone(golem.attack_time)
        self.assertIsNone(golem.update(.4, (), (), COMBAT_WIDTH))
        golem.begin_emergence()
        self.assertEqual(golem.time, .4)
        golem.hp = 0
        golem.begin_emergence()
        self.assertIsNone(golem.update(10, (), (), COMBAT_WIDTH))
        self.assertEqual((golem.hp, golem.time), (0, .4))


class GolemEmergenceRoomTests(unittest.TestCase):
    def test_center_trigger_and_return_preserve_both_golem_emergences_then_resume(self):
        pico.open_canvas(960, 540)
        try:
            room = LowerCaves(SimpleNamespace(width=960, height=540, shaft=SimpleNamespace(w=4096)))
            room.room = "combat"
            player = Player(130, 0, COMBAT_WIDTH)
            camera = Camera(960, COMBAT_WIDTH)
            room.enter(player, camera)
            player.recover_at(COMBAT_CENTER_X, 0, 0)
            room.update_enemies(player, 0)
            self.assertEqual(len(room.enemies), 4)
            self.assertTrue(all(enemy.phase == "emerge" for enemy in room.enemies))
            with patch.object(room.golem_emergence, "draw") as emerging, \
                    patch.object(room.golem_walk, "draw") as walking, \
                    patch.object(room.golem_attack, "draw") as attack:
                room.draw(camera)
                self.assertEqual(emerging.call_count, 2)
                walking.assert_not_called()
                attack.assert_not_called()
            room.update_enemies(player, .4)
            room.room = "gallery"
            room.enter(player, camera)
            room.room = "combat"
            room.enter(player, camera)
            self.assertEqual([golem.time for golem in room.golems], [.4, .4])
            room.update_enemies(player, EMERGE_DURATION - .4)
            self.assertTrue(all(golem.phase == "active" for golem in room.golems))
            with patch.object(room.golem_emergence, "draw") as emerging, \
                    patch.object(room.golem_walk, "draw") as walking:
                room.draw(camera)
                emerging.assert_not_called()
                self.assertEqual(walking.call_count, 2)
            self.assertEqual(room.projectiles, [])
            self.assertFalse(room.exit_open)
            del room, player
        finally:
            gc.collect()
            pico.close_canvas()

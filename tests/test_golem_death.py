"""Check an unstaggerable golem's lethal collapse and blue-pixel removal."""

import gc
import os
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_RENDER_DRIVER"] = "software"

from pico2d import pico2d as pico

from crystal_golem import ATTACK_RELEASE, DEATH_COLLAPSE_DURATION, DEATH_DURATION, CrystalGolem
from crystal_projectile import CrystalProjectile
from death_pixels import COLORS
from enemy_knockback import KNOCKBACK_DURATION
from health import Health
from lower_caves import COMBAT_WIDTH, LowerCaves
from main import Camera
from player import Player
from slash_effect import forward_slash_bounds


class GolemDeathTests(unittest.TestCase):
    def test_nonlethal_hits_near_release_preserve_charge_target_and_shot_timing(self):
        golem = CrystalGolem(400, 600)
        golem.attack_cooldown = 0
        golem.update(.01, (900, 0, 940, 140), (), 1920)
        golem.update(ATTACK_RELEASE - .02, (900, 0, 940, 140), (), 1920)
        before = golem.attack_time, golem.attack_target, golem.direction, golem.attack_cooldown
        self.assertTrue(golem.check_strike((450, 0, 550, 100), 1, 12, 1))
        self.assertEqual((golem.attack_time, golem.attack_target, golem.direction,
                          golem.attack_cooldown), before)
        self.assertIsInstance(golem.update(.03, (1000, 0, 1040, 140), (), 1920), CrystalProjectile)
        self.assertEqual(golem.hp, 33)

    def test_fourth_hit_starts_death_cancels_attack_and_never_moves_hurts_or_revives(self):
        for fps in (30, 60, 120):
            with self.subTest(fps=fps):
                golem = CrystalGolem(400, 600)
                golem.attack_cooldown = 0
                golem.update(.01, (900, 0, 940, 140), (), 1920)
                for swing, hp in enumerate((33, 21, 9, 0), 1):
                    self.assertTrue(golem.check_strike((450, 0, 550, 100), 1, 12, swing))
                    self.assertEqual(golem.hp, hp)
                self.assertEqual((golem.phase, golem.death_time), ("death", 0))
                self.assertIsNone(golem.attack_time)
                self.assertFalse(golem.check_strike((450, 0, 550, 100), 1, 12, 5))
                golem.begin_emergence()
                player = Mock()
                player.get_hitbox.return_value = (480, 0, 520, 140)
                self.assertFalse(Health((130, 0, 0)).check_contact(player, (golem,), 0))
                for _ in range(3 * fps):
                    self.assertIsNone(golem.update(1 / fps, (900, 0, 940, 140), (), 1920))
                    self.assertEqual((golem.x, golem.hp, golem.phase), (500, 0, "death"))
                self.assertEqual(golem.death_time, DEATH_DURATION)


class GolemDeathRenderTests(unittest.TestCase):
    def setUp(self):
        pico.open_canvas(960, 540)
        self.room = LowerCaves(SimpleNamespace(width=960, height=540, shaft=SimpleNamespace(w=4096)))
        self.room.room, self.room.combat_phase = "combat", "golems"
        self.player = Player(130, 0, COMBAT_WIDTH)
        self.camera = Camera(960, COMBAT_WIDTH)
        self.room.enter(self.player, self.camera)

    def tearDown(self):
        del self.room, self.player
        gc.collect()
        pico.close_canvas()

    def test_collapse_then_many_blue_pixels_then_no_render(self):
        golem = self.room.golems[0]
        golem.hp = 12
        golem.check_strike((golem.x - 50, golem.floor_y, golem.x + 50, golem.floor_y + 100), 1, 12, 1)

        def draw():
            golem.draw(self.room.golem_walk, self.camera, self.room.golem_attack,
                       self.room.golem_emergence, self.room.golem_death)

        with patch.object(self.room.golem_death, "draw") as collapse, \
                patch.object(pico, "draw_rectangle") as pixels:
            golem.death_time = DEATH_COLLAPSE_DURATION - .01
            draw()
            collapse.assert_called_once()
            pixels.assert_not_called()
            collapse.reset_mock()
            golem.death_time = DEATH_COLLAPSE_DURATION + .15
            draw()
            collapse.assert_not_called()
            self.assertGreater(pixels.call_count, 20)
            self.assertTrue(all(call.args[4:7] in COLORS for call in pixels.call_args_list))
            pixels.reset_mock()
            golem.death_time = DEATH_DURATION
            draw()
            pixels.assert_not_called()
            collapse.assert_not_called()

    def test_actual_combat_sword_hits_push_golem_then_render_its_death(self):
        golem = self.room.golems[0]
        position = golem.x, golem.floor_y
        for swing in range(4):
            self.player.recover_at(golem.x - 120, golem.floor_y, 0)
            self.player.swing_id += 1
            self.player.slash = (0, 1, "attack")
            self.room.update_enemies(self.player, KNOCKBACK_DURATION if swing == 0 else 0)
            if swing == 0:
                self.assertAlmostEqual(golem.x, position[0] + forward_slash_bounds(0, 0, 1)[2])
            self.assertEqual(golem.floor_y, position[1])
            self.assertGreater(self.player.recoil_remaining, 0)
        self.player.slash = None
        self.assertEqual((golem.hp, golem.phase), (0, "death"))
        self.room.update_enemies(self.player, DEATH_COLLAPSE_DURATION + .1)
        with patch.object(pico, "draw_rectangle") as render:
            self.room.draw(self.camera)
            self.assertGreater(sum(call.args[4:7] in COLORS for call in render.call_args_list), 20)

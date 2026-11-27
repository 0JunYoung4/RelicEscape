"""Exercise sword damage and the shell puzzle through the SDL encounter."""

import os
import unittest
from unittest.mock import patch

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_RENDER_DRIVER"] = "software"

from pico2d import pico2d as pico

from tools.b1_combat_terrain import LEDGES
from tools.b1_combat_tree import Attack
from tools.b1_encounter_stage import B1EncounterStage, BOSS_HALF_HP, BOSS_MAX_HP, REVEAL_RECOVERY, SCALE
from tools.preview_b1_intro import GROUND, SHELL_X, SIZE


DT = 1 / 60


class B1ShellPhaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pico.open_canvas(*SIZE)
        cls.addClassCleanup(pico.close_canvas)
        cls.stage = B1EncounterStage()
        cls.addClassCleanup(cls.stage.close)

    def setUp(self):
        self.stage.reset()

    def wait_for(self, condition, **controls):
        for _ in range(900):
            if condition():
                return
            self.stage.advance(DT, **controls)
        self.fail(f"Timed out in {self.stage.state} at {(self.stage.player.x, self.stage.player.y)}")

    def start_claw(self):
        stage = self.stage
        self.wait_for(lambda: stage.can_inspect, direction=-1, running=True)
        stage.advance(DT, inspect_pressed=True)
        self.wait_for(lambda: stage.state == "claw")

    def line_up_with_claw(self):
        stage = self.stage
        self.assertTrue(stage.player.recover_at(stage.claw_center - stage.boss_facing * 142, 0, 0))
        stage.player.facing = stage.boss_facing

    def swing(self):
        stage = self.stage
        swing_id = stage.player.swing_id
        stage.advance(DT, attack_pressed=True)
        self.wait_for(lambda: stage.player.swing_id != swing_id)

    def test_only_recovery_sword_hit_damages_boss_once_per_swing(self):
        stage = self.stage
        self.start_claw()
        self.line_up_with_claw()
        self.swing()
        self.assertLess(stage.age, stage.claw.impact)
        self.assertEqual(stage.boss_hp, BOSS_MAX_HP)
        self.wait_for(lambda: stage.age >= stage.claw.impact)
        self.assertFalse(stage.hit_landed)

        self.swing()
        self.assertEqual(stage.boss_hp, BOSS_MAX_HP - stage.player.attack_power)
        self.wait_for(lambda: stage.player.slash is None)
        self.assertEqual(stage.boss_hp, BOSS_MAX_HP - stage.player.attack_power)

    def test_half_health_waits_for_openers_then_center_claw_and_hidden(self):
        stage = self.stage
        self.start_claw()
        self.line_up_with_claw()
        stage.boss_hp = BOSS_HALF_HP + 1
        self.wait_for(lambda: stage.age >= stage.claw.impact)
        self.swing()
        self.assertEqual(stage.boss_hp, BOSS_HALF_HP)
        self.assertEqual(stage.state, "claw")
        self.assertEqual(stage.phase, "first")
        self.wait_for(lambda: stage.state == "jump")
        self.wait_for(lambda: stage.age >= stage.jump.impact)
        self.assertEqual(stage.combat.completed, 1)
        self.assertEqual(stage.phase, "first")

        with patch.object(stage, "_strike", wraps=stage._strike) as strike:
            self.wait_for(lambda: stage.state == "center_claw")
            center = SHELL_X * SCALE
            self.assertEqual(stage.boss_x, center)
            self.assertEqual(stage.combat.completed, 2)
            facing = stage.boss_facing
            self.assertTrue(stage.player.recover_at(center - facing * 70, 0, 0))
            self.wait_for(lambda: stage.state == "hidden")
            self.assertEqual(stage.boss_x, center)
            self.assertEqual(stage.boss_facing, facing)
            self.assertEqual(strike.call_count, 1)
            self.assertTrue(stage.rails_enabled)

            stage.player.facing = facing
            self.swing()
            self.wait_for(lambda: stage.player.slash is None)
            self.assertEqual(stage.state, "hidden")
            self.assertEqual(stage.boss_hp, BOSS_HALF_HP)
            self.assertEqual(strike.call_count, 1)

    def take_rail(self, index):
        stage = self.stage
        x, y = stage.rails.landings[index]
        direction = 1 if index == 0 else -1
        self.assertTrue(stage.player.recover_at(x - direction * 50, 0, 0))
        stage.player.facing = direction
        self.assertEqual(stage.rails.prompt(stage.player), "mount")
        stage.advance(DT, inspect_pressed=True)
        carriage = stage.rails.carriages[index]
        self.assertTrue(carriage.relic_mounted)
        self.assertEqual(stage.rails.prompt(stage.player), "send")
        self.swing()
        self.wait_for(lambda: stage.rails.prompt(stage.player) == "travel")
        self.assertEqual(carriage.distance, carriage.length)
        stage.advance(DT, inspect_pressed=True)
        self.assertEqual((stage.player.x, stage.player.y), (x, y))
        self.assertTrue(stage.player.grounded)

    def jump_to_inner_ledge(self, index):
        stage = self.stage
        direction = 1 if index == 0 else -1
        outer, inner = (LEDGES[0], LEDGES[1]) if index == 0 else (LEDGES[-1], LEDGES[-2])
        _, lower_x, _, lower_width, _ = outer
        _, upper_x, upper_top, upper_width, _ = inner
        edge = (lower_x + (lower_width if direction > 0 else 0)) * SCALE
        takeoff = edge - direction * 30
        self.wait_for(lambda: (stage.player.x - takeoff) * direction >= 0,
                      direction=direction, running=True)
        self.assertTrue(stage.player.grounded)
        stage.advance(DT, direction=direction, running=True, jump_pressed=True, jump_held=True)
        target = (upper_x + (upper_width / 2)) * SCALE
        self.wait_for(lambda: (stage.player.x - target) * direction >= 0,
                      direction=direction, running=True, jump_held=True)
        landing_y = (GROUND - upper_top) * SCALE
        self.wait_for(lambda: stage.player.grounded)
        self.assertEqual(stage.player.y, landing_y)

    def test_both_rails_reach_rock_then_floor_return_opens_recovery(self):
        stage = self.stage
        for index in (0, 1):
            with self.subTest(rail=index):
                stage.reset()
                self.start_claw()
                stage.boss_hp = BOSS_HALF_HP
                self.wait_for(lambda: stage.state == "hidden")
                self.assertEqual(stage.boss_x, SHELL_X * SCALE)
                self.take_rail(index)
                self.jump_to_inner_ledge(index)

                direction = 1 if index == 0 else -1
                cave_target = (960 if index == 0 else 1225) * SCALE
                self.wait_for(lambda: (stage.player.x - cave_target) * direction >= 0,
                              direction=direction)
                self.assertTrue(stage.player.grounded)
                self.swing()
                self.assertEqual(stage.state, "boulder_fall")
                self.assertIsNone(stage.rock_hit_at)
                with patch.object(stage.boulder, "draw_fall", wraps=stage.boulder.draw_fall) as falling:
                    stage.draw()
                    falling.assert_called_once()

                self.wait_for(lambda: stage.state == "reveal")
                self.assertIsNotNone(stage.rock_hit_at)
                with patch.object(stage.boulder, "draw_shatter", wraps=stage.boulder.draw_shatter) as shattered:
                    stage.draw()
                    shattered.assert_called_once()

                self.wait_for(lambda: stage.state == "wait_floor")
                for _ in range(90):
                    stage.advance(DT)
                self.assertEqual(stage.state, "wait_floor")
                self.assertIsNone(stage.combat.attack)

                center = SHELL_X * SCALE
                self.wait_for(lambda: (stage.player.x - center) * direction >= 0, direction=direction)
                self.wait_for(lambda: stage.state == "face_open")
                self.assertEqual(stage.player.y, 0)
                self.swing()
                self.assertLess(stage.boss_hp, BOSS_HALF_HP)
                self.wait_for(lambda: stage.age >= REVEAL_RECOVERY - 3 * DT)
                self.assertEqual(stage.state, "face_open")
                self.assertIsNone(stage.combat.attack)
                self.wait_for(lambda: stage.phase == "resumed")
                self.assertEqual(stage.combat.attack, Attack.CLAW)

        stage.reset()
        self.assertEqual(stage.state, "waiting")
        self.assertEqual(stage.boss_hp, BOSS_MAX_HP)
        self.assertIsNone(stage.rock_hit_at)
        self.assertFalse(stage.rails_enabled)
        self.assertIsNone(stage.rails.active)

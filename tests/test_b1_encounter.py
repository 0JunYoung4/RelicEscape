"""Verify the independent B1 encounter with the real SDL assets and player."""

import os
import unittest

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_RENDER_DRIVER"] = "software"

from pico2d import pico2d as pico

from health import MAX_HEALTH
from tools.b1_combat_tree import Attack
from tools.b1_combat_terrain import GATE_LEFT
from tools.b1_encounter_stage import (B1EncounterStage, CLAW_DAMAGE, CLAW_HOLD, JUMP_DAMAGE,
                                     JUMP_RECOVERY, JUMP_TELL, JUMP_WAIT, JUMP_WALL_MARGIN, SCALE, SPAWN)
from tools.preview_b1_intro import LAST_TREMOR, SIZE


DT = 1 / 60


class B1EncounterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pico.open_canvas(*SIZE)
        cls.addClassCleanup(pico.close_canvas)
        cls.stage = B1EncounterStage()
        cls.addClassCleanup(cls.stage.close)

    def setUp(self):
        self.stage.reset()

    def advance_until(self, condition, **controls):
        for _ in range(420):
            if condition():
                return
            self.stage.advance(DT, **controls)
        self.fail(f"Timed out in {self.stage.state}")

    def start_intro(self):
        self.advance_until(lambda: self.stage.can_inspect, direction=-1, running=True)
        self.stage.advance(DT, inspect_pressed=True)

    def start_claw(self):
        self.start_intro()
        self.advance_until(lambda: self.stage.state == "claw")

    def finish_attack(self, **controls):
        completed = self.stage.combat.completed
        self.advance_until(lambda: self.stage.combat.completed == completed + 1, **controls)

    def test_only_grounded_inspection_starts_a_single_tremor_and_roar(self):
        stage = self.stage
        stage.advance(DT, inspect_pressed=True)
        self.assertEqual(stage.state, "waiting")
        self.advance_until(lambda: stage.can_inspect, direction=-1, running=True)
        stage.advance(.10, jump_pressed=True, jump_held=True)
        self.assertGreater(stage.player.y, 0)
        stage.advance(DT, inspect_pressed=True)
        self.assertEqual(stage.state, "waiting")
        self.advance_until(lambda: stage.can_inspect)
        stage.advance(DT, inspect_pressed=True)
        position = stage.player.x
        self.assertEqual(stage.state, "tremor")
        first_view = stage._view()
        stage.advance(.60, direction=1, jump_pressed=True, inspect_pressed=True)
        self.assertEqual(stage.age, .60)
        self.assertNotEqual(first_view, stage._view())
        self.assertEqual(stage.player.x, position)

        self.advance_until(lambda: stage.state == "roar", inspect_pressed=True)
        self.assertEqual(stage.gate_progress, 1)
        self.assertGreaterEqual(stage.time, LAST_TREMOR)
        self.advance_until(lambda: stage.state == "approach", inspect_pressed=True)
        self.assertEqual(stage.player.x, position)
        self.assertEqual(stage.health.current, MAX_HEALTH)
        self.assertEqual(len(stage.player.terrain), len(stage.ledges) + 1)
        stage.advance(.10, direction=1)
        self.assertGreater(stage.player.x, position)

    def test_first_claw_warns_then_costs_health_exactly_once(self):
        self.start_claw()
        stage = self.stage
        self.assertAlmostEqual(stage.claw.ends[22] - stage.claw.tell, CLAW_HOLD)
        self.advance_until(lambda: stage.age >= stage.claw.tell)
        self.assertIsNone(stage.hit_landed)
        self.assertEqual(stage.health.current, MAX_HEALTH)
        self.advance_until(lambda: stage.hit_landed is not None)
        self.assertTrue(stage.hit_landed)
        self.finish_attack()
        self.assertEqual(stage.health.current, MAX_HEALTH - CLAW_DAMAGE)
        self.assertEqual(stage.state, "ready")
        stage.advance(DT, inspect_pressed=True)
        self.assertIs(stage.combat.attack, Attack.JUMP)

    def test_claw_target_stays_fixed_while_player_dodges_and_reset_reopens_gate(self):
        self.start_claw()
        stage = self.stage
        self.advance_until(lambda: stage.age >= stage.claw.tell)
        center, facing = stage.claw_center, stage.boss_facing
        self.finish_attack(direction=facing, running=True)
        self.assertEqual(stage.claw_center, center)
        self.assertEqual(stage.boss_facing, facing)
        self.assertFalse(stage.hit_landed)
        self.assertEqual(stage.health.current, MAX_HEALTH)

        stage.reset()
        self.assertEqual(stage.state, "waiting")
        self.assertEqual(stage.player.x, SPAWN[0])
        self.assertEqual(stage.gate_progress, 0)
        self.assertEqual(stage.player.terrain, stage.ledges)
        self.assertIsNone(stage.hit_landed)
        self.assertFalse(stage.can_inspect)
        self.assertEqual(stage.combat.completed, 0)
        self.assertIsNone(stage.combat.attack)

    def test_closed_gate_blocks_repeated_wall_jumps(self):
        self.start_claw()
        for index in range(900):
            self.stage.advance(DT, direction=1, running=True, jump_pressed=index % 40 == 0,
                               jump_held=True)
            self.assertLessEqual(self.stage.player.get_hitbox()[2], GATE_LEFT * SCALE + 1e-6)

    def test_player_crossing_the_boss_locks_claw_onto_the_left(self):
        self.start_intro()
        stage = self.stage
        self.advance_until(lambda: stage.state == "approach")
        self.assertTrue(stage.player.recover_at(stage.boss_x - 250 * SCALE, 0, 0))
        stage.advance(DT)
        self.assertEqual(stage.state, "claw")
        self.assertEqual(stage.boss_facing, -1)
        self.assertLess(stage.claw_center, stage.boss_x)
        self.advance_until(lambda: stage.hit_landed is not None)
        self.assertTrue(stage.hit_landed)

    def test_jump_target_locks_after_wait_and_player_can_walk_clear_at_the_gate(self):
        self.start_claw()
        self.finish_attack()
        stage = self.stage
        stage.advance(DT)
        self.assertEqual(stage.state, "jump")
        self.assertTrue(stage.player.recover_at(GATE_LEFT * SCALE - 22, 0, 0))
        self.advance_until(lambda: stage.age >= stage.jump.offscreen)
        self.assertIsNone(stage.jump_target)
        self.assertTrue(stage.airborne)
        self.advance_until(lambda: stage.jump_target is not None)
        target = stage.jump_target
        self.assertEqual(target, GATE_LEFT * SCALE - JUMP_WALL_MARGIN)
        self.assertAlmostEqual(stage.jump.tell - stage.jump.offscreen, JUMP_WAIT)
        self.assertAlmostEqual(stage.jump.drop - stage.jump.tell, JUMP_TELL)
        health_before = stage.health.current
        self.advance_until(lambda: stage.hit_landed is not None, direction=-1)
        self.assertEqual(stage.jump_target, target)
        self.assertEqual(stage.boss_x, target)
        self.assertFalse(stage.hit_landed)
        self.assertEqual(stage.health.current, health_before)

    def test_jump_hits_once_and_finishes_its_full_recovery(self):
        self.start_claw()
        self.finish_attack()
        stage = self.stage
        stage.advance(DT)
        health_before = stage.health.current
        self.advance_until(lambda: stage.jump_target is not None)
        self.assertIsNone(stage.hit_landed)
        self.advance_until(lambda: stage.hit_landed is not None)
        self.assertTrue(stage.hit_landed)
        self.assertEqual(stage.health.current, health_before - JUMP_DAMAGE)
        self.advance_until(lambda: stage.age >= stage.jump.impact + JUMP_RECOVERY - .04)
        self.assertEqual(stage.combat.completed, 1)
        self.finish_attack()
        self.assertEqual(stage.combat.completed, 2)
        self.assertEqual(stage.health.current, health_before - JUMP_DAMAGE)

    def test_tree_uses_distance_after_opening_and_switches_after_two_repeats(self):
        stage = self.stage
        for position, expected in (
            ("near", (Attack.CLAW, Attack.CLAW, Attack.JUMP)),
            ("far", (Attack.JUMP, Attack.CLAW)),
        ):
            with self.subTest(position=position):
                stage.reset()
                self.start_claw()
                self.assertIs(stage.combat.attack, Attack.CLAW)
                self.finish_attack()
                stage.advance(DT)
                self.assertIs(stage.combat.attack, Attack.JUMP)
                self.finish_attack()
                for index, attack in enumerate(expected):
                    x = stage.boss_x - 90 * SCALE if position == "near" else 120 * SCALE
                    self.assertTrue(stage.player.recover_at(x, 0, 0))
                    stage.advance(DT)
                    self.assertIs(stage.combat.attack, attack)
                    if index < len(expected) - 1:
                        self.finish_attack()

    def test_defeat_stops_selection_and_reset_restarts_opening(self):
        self.start_claw()
        stage = self.stage
        stage.health.current = 1
        self.advance_until(lambda: stage.state == "defeated")
        self.assertEqual(stage.health.current, 0)
        self.assertEqual(stage.combat.completed, 0)
        for _ in range(360):
            stage.advance(DT, direction=1, inspect_pressed=True)
        self.assertEqual(stage.state, "defeated")
        self.assertIsNone(stage.combat.attack)
        stage.draw()
        stage.reset()
        self.start_claw()
        self.assertIs(stage.combat.attack, Attack.CLAW)

"""Verify the playable B1 defeat sequence and its combat boundaries."""

import os
import unittest
from unittest.mock import patch

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("SDL_RENDER_DRIVER", "software")

from pico2d import pico2d as pico

from health import Health, MAX_HEALTH
from main import RelicTravel, update_b1
from player import Player
from tools.b1_combat_terrain import GATE_LEFT
from tools.b1_combat_tree import Attack
from tools.b1_defeat_sequence import DURATION
from tools.b1_encounter_stage import B1EncounterStage, EXIT_X, GATE_DURATION, SCALE, SIZE
from tools.preview_b1_intro import GROUND, SHELL_X


class B1DefeatSequenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pico.open_canvas(*SIZE)
        cls.addClassCleanup(pico.close_canvas)
        cls.player = Player(100, 0, 2000)
        cls.stage = B1EncounterStage(player=cls.player, health=Health((100, 0, 0)))
        cls.addClassCleanup(cls.stage.close)

    def setUp(self):
        self.reset_combat()

    def reset_combat(self):
        self.stage.enter(self.player, Health((100, 0, 0)))
        self.stage.phase = "second"
        self.stage.gate_progress = 1
        gate_wall = (GATE_LEFT * SCALE, 0, (GATE_LEFT + self.stage.gate.w) * SCALE, GROUND * SCALE)
        self.player.terrain = (*self.stage.ledges, gate_wall)
        self.player.world_left = 0
        self.stage.boss_x = (SHELL_X - 165) * SCALE

    def prepare_last_hit(self):
        stage = self.stage
        stage.combat.attack = Attack.CLAW
        stage.boss_facing = self.player.facing = -1
        stage.boss_hp = self.player.attack_power
        stage._enter("claw")
        stage.age = stage.claw.impact + .03
        self.assertTrue(self.player.recover_at(stage.claw_center + 142, 0, 0))

    def test_last_sword_hit_locks_combat_until_the_four_second_sequence_is_over(self):
        stage, player = self.stage, self.player
        self.prepare_last_hit()
        dt = 1 / 60
        closed_terrain = player.terrain
        stage.advance(dt, attack_pressed=True)
        for _ in range(45):
            if stage.state == "dying":
                break
            stage.advance(dt)
        self.assertEqual(stage.state, "dying")
        self.assertEqual(stage.boss_hp, 0)
        self.assertIsNone(stage.combat.attack)
        self.assertFalse(stage.accepts_player_input)
        self.assertFalse(stage.can_leave)
        self.assertFalse(stage.allows_relic_destination((player.x, player.y, player.crouch_time)))

        travel = RelicTravel()
        position = player.x, player.y
        swing = player.swing_id
        age_at_start = stage.age
        with patch.object(stage, "_strike") as strike, patch.object(travel, "return_pose") as return_pose:
            for tick in range(1, int((DURATION - .08 - age_at_start) / dt) + 1):
                relic_key = pico.SDLK_e if tick % 2 else pico.SDLK_q
                update_b1(stage, travel, dt, 100 + tick * dt,
                          pressed_keys={relic_key, pico.SDLK_x, pico.SDLK_SPACE},
                          direction=1, running=True, crouching=True, jump_held=True)
                if tick in (20, 85, 105, 180):
                    pico.SDL_ClearError()
                    stage.draw(relic_focus=(EXIT_X, 0))
                    self.assertFalse(pico.SDL_GetError())
            strike.assert_not_called()
            return_pose.assert_not_called()

        self.assertEqual(stage.state, "dying")
        self.assertEqual(player.terrain, closed_terrain)
        self.assertEqual(stage.gate_progress, 1)
        self.assertEqual((player.x, player.y), position)
        self.assertEqual(player.swing_id, swing)
        self.assertIsNone(travel.anchor)
        self.assertFalse(travel.marks)
        self.assertEqual(stage.health.current, MAX_HEALTH)
        age = stage.age
        stage.end_combat(victory=True)
        self.assertEqual(stage.age, age)

        while stage.state == "dying" and age <= DURATION + dt:
            stage.advance(dt)
            age += dt
        self.assertEqual(stage.state, "victory")
        self.assertAlmostEqual(age, 4.0, delta=dt + .0001)
        self.assertTrue(stage.accepts_player_input)
        self.assertIsNone(player.buffered_attack_down)
        self.assertIsNone(stage.combat.attack)
        self.assertEqual(player.swing_id, swing)

        for _ in range(round(GATE_DURATION / dt) + 2):
            stage.advance(dt)
        stage.end_combat(victory=True)
        self.assertEqual(stage.state, "victory")
        self.assertEqual(player.terrain, stage.ledges)
        self.assertTrue(player.recover_at(EXIT_X, 0, 0))
        self.assertTrue(stage.can_leave)

        corpse_pose = stage.boss_x, stage.boss_facing
        stage.enter(player, stage.health, defeated=True)
        self.assertEqual(stage.state, "victory")
        self.assertEqual((stage.boss_x, stage.boss_facing), corpse_pose)
        self.assertEqual(stage.gate_progress, 0)
        self.assertIsNone(stage.combat.attack)
        stage.enter(player, Health((100, 0, 0)))
        self.assertEqual(stage.state, "waiting")
        self.assertNotEqual((stage.boss_x, stage.boss_facing), corpse_pose)

    def test_timeline_finishes_once_at_supported_frame_intervals(self):
        stage = self.stage
        for fps in (30, 60, 144):
            with self.subTest(fps=fps):
                self.reset_combat()
                self.prepare_last_hit()
                stage.boss_hp = 0
                stage.advance(1 / fps)
                self.assertEqual(stage.state, "dying")
                elapsed = stage.age
                while stage.state == "dying" and elapsed <= DURATION + 1 / fps:
                    stage.advance(1 / fps)
                    elapsed += 1 / fps
                self.assertEqual(stage.state, "victory")
                self.assertAlmostEqual(elapsed, 4.0, delta=1 / fps + .0001)

    def test_player_defeat_has_priority_on_the_same_frame(self):
        stage = self.stage
        self.prepare_last_hit()
        stage.boss_hp = 0
        self.assertTrue(stage.health.take_enemy_hit((self.player.x, 0), 100, MAX_HEALTH))
        stage.advance(1 / 60, now=100)
        self.assertEqual(stage.state, "defeated")
        self.assertFalse(stage.can_leave)
        self.assertEqual(stage.gate_progress, 1)

import unittest

from pillbug import BODY_LENGTH, CURL_TIME, HURT_TIME, MAX_ROLL, NOTICE_DISTANCE, RADIUS, Pillbug
from player import STARTING_ATTACK_POWER


class PillbugAttackTests(unittest.TestCase):
    def test_only_one_flinch_per_swing_even_on_an_overturned_bug(self):
        bug = Pillbug(400, 800, 0)
        bug.phase = "overturned"
        bug.time = 1
        sword = (760, 10, 840, 50)
        bug.check_strike((760, 200, 840, 250), 1, STARTING_ATTACK_POWER, 1)
        self.assertEqual(bug.hurt_remaining, 0)
        self.assertEqual(bug.hp, 30)
        bug.check_strike(sword, 1, STARTING_ATTACK_POWER, 1)
        bug.update(.08, sword, (), 2400)
        bug.check_strike(sword, 1, STARTING_ATTACK_POWER, 1)
        self.assertEqual(bug.hp, 18)
        self.assertAlmostEqual(bug.hurt_remaining, HURT_TIME - .08)
        bug.update(HURT_TIME, sword, (), 2400)
        self.assertEqual((bug.phase, bug.hurt_remaining), ("overturned", 0))
        bug.check_strike(sword, -1, STARTING_ATTACK_POWER, 2)
        self.assertEqual(bug.hp, 6)
        self.assertEqual((bug.hurt_remaining, bug.strike_direction), (HURT_TIME, -1))
        bug.check_strike(sword, -1, STARTING_ATTACK_POWER, 3)
        self.assertEqual(bug.hp, 0)
        bug.update(1.0, sword, (), 2400)
        bug.check_strike(sword, 1, STARTING_ATTACK_POWER, 4)
        self.assertEqual((bug.hp, bug.hurt_remaining), (0, 0))

    def test_notice_at_body_edge_and_lock_direction(self):
        bug = Pillbug(400, 800, 0)
        threshold = bug.x - BODY_LENGTH / 2 - NOTICE_DISTANCE
        bug.update(0, (0, 0, threshold - 1, 140), (), 2400)
        self.assertEqual(bug.phase, "crawl")
        bug.update(.1, (0, 0, threshold + 1, 140), (), 2400)
        self.assertEqual((bug.phase, bug.direction), ("curl", -1))
        bug.update(CURL_TIME, (920, 0, 960, 140), (), 2400)
        self.assertEqual((bug.phase, bug.direction), ("roll", -1))

    def test_sweep_hits_player_obstacle_or_boundary_and_stays_overturned(self):
        for player, terrain, width, expected in (
            ((520, 0, 560, 140), (), 2400, 560 + RADIUS),
            ((960, 0, 1000, 140), ((920, 0, 930, 200),), 2400, 920 - RADIUS),
            ((940, 105, 980, 245), (), 1140, 1140 - RADIUS),
        ):
            with self.subTest(expected=expected):
                bug = Pillbug(400, 800, 0)
                bug.update(CURL_TIME, player, terrain, width)
                for _ in range(50):
                    bug.update(.05, player, terrain, width)
                self.assertEqual(bug.phase, "overturned")
                self.assertEqual(bug.x, expected)

    def test_jump_over_roll_stops_at_maximum_range(self):
        bug = Pillbug(400, 800, 0)
        bug.update(CURL_TIME, (570, 0, 610, 140), (), 2400)
        for _ in range(100):
            bug.update(.025, (570, 150, 610, 290), ((0, -100, 2400, 0),), 2400)
        self.assertEqual(bug.phase, "overturned")
        self.assertAlmostEqual(bug.x, 800 - MAX_ROLL)
        self.assertFalse(bug.hit)

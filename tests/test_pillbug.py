import unittest

from pillbug import ATTACK_COOLDOWN, BODY_LENGTH, CURL_TIME, HURT_TIME, MAX_ROLL, NOTICE_DISTANCE, OVERTURNED_TIME, RADIUS, RIGHTING_TIME, Pillbug
from player import STARTING_ATTACK_POWER


class PillbugAttackTests(unittest.TestCase):
    def test_platform_patrol_turns_at_both_edges_and_ignores_the_floor_below(self):
        platform = (500, 274, 756, 364)
        bug = Pillbug.on_platform(platform)
        directions = set()
        for _ in range(600):
            bug.update(1/60, (620, 0, 660, 140), (platform,), 2000)
            x, y, width, _ = bug.body_bounds()
            self.assertEqual((bug.phase, y), ("crawl", platform[3]))
            self.assertGreaterEqual(x - width/2, platform[0])
            self.assertLessEqual(x + width/2, platform[2])
            directions.add(bug.direction)
        self.assertEqual(directions, {-1, 1})
        for side in (-1, 1):
            bug = Pillbug.on_platform(platform)
            target = bug.x + side * 220
            box = (target - 20, 364, target + 20, 504)
            for _ in range(120):
                bug.update(1/60, box, (platform,), 2000)
            x, y, width, _ = bug.body_bounds()
            self.assertEqual((bug.phase, y), ("overturned", platform[3]))
            self.assertGreaterEqual(x - width/2, platform[0])
            self.assertLessEqual(x + width/2, platform[2])

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

    def test_sweep_hits_player_obstacle_or_boundary_then_overturns(self):
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
                    if bug.phase == "overturned":
                        break
                self.assertEqual(bug.phase, "overturned")
                self.assertEqual(bug.x, expected)

    def test_overturned_bug_gets_up_and_can_charge_again_without_teleporting(self):
        bug = Pillbug(700, 900, 0)
        bug.x, bug.direction = 610, -1
        bug.phase, bug.time, bug.hit = "overturned", 0, True
        target = (520, 0, 560, 140)
        bug.update(OVERTURNED_TIME - .01, target, (), 2400)
        self.assertEqual(bug.phase, "overturned")
        bug.update(.02, target, (), 2400)
        self.assertEqual(bug.phase, "recover")
        bug.update(RIGHTING_TIME, target, (), 2400)
        self.assertEqual((bug.phase, bug.rolled, bug.hit), ("crawl", 0, False))
        self.assertEqual(bug.x, 610 + BODY_LENGTH / 2 - RADIUS)
        bug.update(.1, target, (), 2400)
        self.assertEqual(bug.phase, "crawl")
        self.assertLess(bug.x, 650)  # Do not snap back to the old patrol interval.
        bug.update(ATTACK_COOLDOWN, target, (), 2400)
        self.assertIn(bug.phase, ("curl", "roll", "flip"))

    def test_righting_on_both_platform_edges_keeps_the_whole_body_supported(self):
        platform = (500, 274, 756, 364)
        for direction in (-1, 1):
            bug = Pillbug.on_platform(platform)
            bug.x = platform[0] + RADIUS if direction < 0 else platform[2] - RADIUS
            bug.direction, bug.phase, bug.time, bug.hit = direction, "overturned", 0, True
            target = (600, 0, 640, 140)
            bug.update(OVERTURNED_TIME + RIGHTING_TIME, target, (platform,), 2000)
            self.assertEqual(bug.phase, "crawl")
            for _ in range(120):
                bug.update(1 / 60, target, (platform,), 2000)
                x, y, width, _ = bug.body_bounds()
                self.assertEqual(y, platform[3])
                self.assertGreaterEqual(x - width / 2, platform[0])
                self.assertLessEqual(x + width / 2, platform[2])

    def test_dead_bug_never_recovers(self):
        bug = Pillbug(700, 900, 0)
        bug.phase, bug.time, bug.hp = "overturned", 0, 0
        bug.update(10, (800, 0, 840, 140), (), 2400)
        self.assertEqual((bug.phase, bug.time), ("overturned", 0))

    def test_jump_over_roll_stops_at_maximum_range(self):
        bug = Pillbug(400, 800, 0)
        bug.update(CURL_TIME, (570, 0, 610, 140), (), 2400)
        for _ in range(100):
            bug.update(.025, (570, 150, 610, 290), ((0, -100, 2400, 0),), 2400)
        self.assertEqual(bug.phase, "overturned")
        self.assertAlmostEqual(bug.x, 800 - MAX_ROLL)
        self.assertFalse(bug.hit)

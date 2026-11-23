"""Check real pillbug knockback, repeated hits, and solid ground boundaries."""

import unittest

from pillbug import HURT_TIME, KNOCKBACK_DURATION, KNOCKBACK_SPEED, Pillbug


class PillbugKnockbackTests(unittest.TestCase):
    def strike(self, bug, facing, swing=1, damage=1):
        x, y, width, height = bug.body_bounds()
        return bug.check_strike((x - width / 2, y, x + width / 2, y + height),
                                facing, damage, swing)

    def test_every_live_pose_moves_away_once_at_different_frame_rates(self):
        for phase in ("crawl", "curl", "roll", "flip", "overturned", "recover"):
            for facing in (-1, 1):
                for fps in (30, 60, 120):
                    with self.subTest(phase=phase, facing=facing, fps=fps):
                        bug = Pillbug(400, 800, 0)
                        bug.phase, bug.time = phase, .05
                        self.assertTrue(self.strike(bug, facing))
                        start = bug.x
                        elapsed = 0
                        while elapsed < KNOCKBACK_DURATION:
                            dt = min(1 / fps, KNOCKBACK_DURATION - elapsed)
                            bug.update(dt, (1600, 0, 1640, 140), (), 2400)
                            elapsed += dt
                        self.assertAlmostEqual(bug.x, start + facing * KNOCKBACK_SPEED * KNOCKBACK_DURATION / 2)
                        self.assertEqual((bug.phase, bug.time), (phase, .05))
                        self.assertAlmostEqual(bug.knockback_remaining, 0)
                        self.assertFalse(self.strike(bug, facing, 1))
                        self.assertAlmostEqual(bug.knockback_remaining, 0)

    def test_new_hit_refreshes_and_can_reverse_knockback(self):
        bug = Pillbug(400, 800, 0)
        self.strike(bug, 1)
        bug.update(.04, (1600, 0, 1640, 140), (), 2400)
        start = bug.x
        self.assertTrue(self.strike(bug, -1, 2))
        self.assertEqual(bug.hurt_remaining, HURT_TIME)
        bug.update(KNOCKBACK_DURATION, (1600, 0, 1640, 140), (), 2400)
        self.assertAlmostEqual(bug.x, start - KNOCKBACK_SPEED * KNOCKBACK_DURATION / 2)

    def test_push_stops_at_walls_world_edges_and_both_platform_edges(self):
        for facing in (-1, 1):
            for boundary in ("wall", "world", "platform"):
                with self.subTest(facing=facing, boundary=boundary):
                    platform = (500, 274, 756, 364)
                    bug = Pillbug.on_platform(platform) if boundary == "platform" else Pillbug(100, 1800, 0)
                    bug.x = 600 if boundary == "wall" else (84 if facing < 0 else 1916)
                    if boundary == "platform":
                        bug.x = platform[0] + 84 if facing < 0 else platform[2] - 84
                    x, y, width, _ = bug.body_bounds()
                    wall = (x + width / 2 + 2, y, x + 200, y + 200) if facing > 0 else (x - 200, y, x - width / 2 - 2, y + 200)
                    terrain = (wall,) if boundary == "wall" else ((platform,) if boundary == "platform" else ())
                    start = bug.x
                    self.strike(bug, facing)
                    bug.update(HURT_TIME, (1600, 0, 1640, 140), terrain, 2000)
                    self.assertAlmostEqual(bug.x, start + facing * 2)
                    self.strike(bug, facing, 2)
                    bug.update(HURT_TIME, (1600, 0, 1640, 140), terrain, 2000)
                    self.assertAlmostEqual(bug.x, start + facing * 2)

    def test_patrol_resumes_at_pushed_position_instead_of_snapping_back(self):
        for facing in (-1, 1):
            bug = Pillbug(800, 800, 0)
            bug.direction = -facing
            self.strike(bug, facing)
            bug.update(HURT_TIME, (1600, 400, 1640, 540), (), 2400)
            pushed = bug.x
            bug.update(.01, (1600, 400, 1640, 540), (), 2400)
            self.assertLess(abs(bug.x - pushed), 1)

    def test_death_and_emergence_clear_pending_push(self):
        for mode in ("death", "emerge"):
            bug = Pillbug(400, 800, 0)
            self.strike(bug, 1)
            if mode == "death":
                self.strike(bug, 1, 2, 100)
            else:
                bug.begin_emergence()
            start = bug.x
            bug.update(KNOCKBACK_DURATION, (1600, 0, 1640, 140), (), 2400)
            self.assertEqual((bug.x, bug.knockback_remaining), (start, 0))


if __name__ == "__main__":
    unittest.main()

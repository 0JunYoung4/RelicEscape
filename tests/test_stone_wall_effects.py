"""Wall motion emits transient dust and bounded rumble in both directions."""

import unittest

from stone_wall_effects import StoneWallEffects


class StoneWallEffectsTests(unittest.TestCase):
    def test_idle_room_has_no_dust_or_rumble(self):
        effects = StoneWallEffects(100, 210)
        for _ in range(120):
            effects.update(0, 1 / 60)
        self.assertEqual(effects.puffs, [])
        self.assertEqual(effects.shake(), (0, 0))

    def test_both_directions_emit_and_settle_without_repeated_end_impacts(self):
        effects = StoneWallEffects(100, 210)
        for start, end in ((0, 1), (1, 0)):
            for step in range(1, 34):
                effects.update(start + (end - start) * step / 33, 1 / 60)
                x, y = effects.shake()
                self.assertLessEqual(abs(x), 2.08)
                self.assertLessEqual(abs(y), 3.2)
            self.assertTrue(effects.puffs)
            self.assertNotEqual(effects.shake(), (0, 0))
            for _ in range(120):
                effects.update(end, 1 / 60)
            self.assertEqual(effects.puffs, [])
            self.assertEqual(effects.shake(), (0, 0))

    def test_emission_is_bounded_and_independent_of_frame_rate(self):
        counts = []
        for steps in (1, 17, 33, 66):
            effects = StoneWallEffects(100, 210)
            for step in range(1, steps + 1):
                effects.update(step / steps, .55 / steps)
            counts.append(len(effects.puffs))
        self.assertEqual(counts, [46] * 4)

    def test_clear_removes_transients_when_leaving_or_restarting(self):
        effects = StoneWallEffects(100, 210)
        effects.update(.5, .275)
        effects.clear()
        self.assertEqual(effects.puffs, [])
        self.assertEqual(effects.shake(), (0, 0))


if __name__ == "__main__":
    unittest.main()

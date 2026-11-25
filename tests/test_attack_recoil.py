"""Check stone-enemy hit recoil through the combat and movement paths."""

import os
import unittest

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_RENDER_DRIVER"] = "software"

from pico2d import pico2d as pico

from health import Health
from lower_caves import GALLERY_WIDTH, LowerCaves
from pillbug import Pillbug
from player import ATTACK_RECOIL_DURATION, ATTACK_RECOIL_SPEED, WALK_SPEED, WORLD_MARGIN, Player


class AttackRecoilTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pico.open_canvas(960, 540)

    @classmethod
    def tearDownClass(cls):
        pico.close_canvas()

    def gallery(self, *bugs):
        gallery = LowerCaves.__new__(LowerCaves)
        gallery.room = "gallery"
        gallery.pillbugs = list(bugs)
        gallery.hit_impacts = []
        return gallery

    def test_only_successful_hits_trigger_recoil_once_per_swing(self):
        player = Player(600, 0, GALLERY_WIDTH)
        first, second = Pillbug(700, 750, 0), Pillbug(720, 780, 0)
        gallery = self.gallery(first, second)
        player.slash = (0, 1, "attack")
        gallery.update_enemies(player, 0)
        self.assertEqual((first.hp, second.hp), (18, 18))
        player.update(0, False, .04)
        remaining = player.recoil_remaining
        gallery.update_enemies(player, 0)
        self.assertEqual(player.recoil_remaining, remaining)
        # A second target first struck later in the SAME swing must not restart recoil.
        third = Pillbug(700, 750, 0)
        gallery.pillbugs.append(third)
        gallery.update_enemies(player, 0)
        self.assertEqual(third.hp, 18)
        self.assertEqual(player.recoil_remaining, remaining)
        player.slash = (0, 1, "attack")
        player.swing_id += 1
        gallery.update_enemies(player, 0)
        self.assertEqual(player.recoil_remaining, ATTACK_RECOIL_DURATION)
        player.recover_at(1600, 0, 0)
        player.slash = (0, 1, "attack")
        player.swing_id += 1
        gallery.update_enemies(player, 0)
        self.assertEqual(player.recoil_remaining, 0)
        first.hp = second.hp = third.hp = 0
        player.recover_at(600, 0, 0)
        gallery.update_enemies(player, 0)
        self.assertEqual(player.recoil_remaining, 0)

    def test_recoil_pushes_back_in_both_directions_and_restores_input(self):
        for facing in (-1, 1):
            for steps in (1, 4, 12):
                with self.subTest(facing=facing, steps=steps):
                    player = Player(600, 0, GALLERY_WIDTH)
                    player.recoil_from_hit(facing, 1)
                    for _ in range(steps):
                        player.update(facing, False, ATTACK_RECOIL_DURATION / steps)
                    distance = ATTACK_RECOIL_SPEED * ATTACK_RECOIL_DURATION / 2
                    self.assertAlmostEqual(player.x, 600 - facing * distance)
                    self.assertEqual(player.facing, facing)
                    start = player.x
                    player.update(facing, False, .1)
                    self.assertAlmostEqual(player.x - start, facing * WALK_SPEED * .1)

    def test_continuous_attacks_keep_small_enemies_out_of_contact(self):
        for phase in ("crawl", "roll"):
            for facing in (-1, 1):
                for fps in (30, 60, 120):
                    with self.subTest(phase=phase, facing=facing, fps=fps):
                        player = Player(1800, 0, GALLERY_WIDTH)
                        player.facing, player.attack_power = facing, 1
                        bug = Pillbug(1200, 2400, 0)
                        bug.x, bug.hp = player.x + facing * 170, 300
                        bug.phase, bug.direction = phase, -facing
                        gallery = self.gallery(bug)
                        health = Health((player.x, 0, 0))
                        for frame in range(4 * fps):
                            player.update(0, False, 1 / fps, attack_pressed=True)
                            before, swing = bug.x, bug.last_swing
                            gallery.update_enemies(player, 1 / fps)
                            if bug.last_swing != swing:
                                self.assertGreater(facing * (bug.x - before), 0)
                            self.assertFalse(health.check_contact(player, (bug,), frame / fps))
                            x, _, width, _ = bug.body_bounds()
                            left, _, right, _ = player.get_hitbox()
                            gap = x - width / 2 - right if facing > 0 else left - x - width / 2
                            self.assertGreater(gap, 20)
                        # Longer knockback sends the bug out of reach between hits.
                        self.assertGreaterEqual(300 - bug.hp, 2)
                        self.assertEqual(health.current, 100)

    def test_recoil_respects_walls_and_world_edges(self):
        wall = (400, 0, 500, 200)
        player = Player(525, 0, GALLERY_WIDTH, terrain=(wall,))
        player.recoil_from_hit(1, 1)
        player.update(0, False, ATTACK_RECOIL_DURATION)
        self.assertEqual(player.get_hitbox()[0], wall[2])
        player = Player(WORLD_MARGIN + 2, 0, GALLERY_WIDTH)
        player.recoil_from_hit(1, 1)
        player.update(0, False, ATTACK_RECOIL_DURATION)
        self.assertEqual(player.x, WORLD_MARGIN)

    def test_air_recoil_preserves_gravity_jump_and_teleport(self):
        player = Player(600, 0, GALLERY_WIDTH, spawn_y=200)
        control = Player(600, 0, GALLERY_WIDTH, spawn_y=200)
        player.recoil_from_hit(1, 1)
        player.update(0, False, .06)
        control.update(0, False, .06)
        self.assertLess(player.x, control.x)
        self.assertEqual((player.y, player.vertical_speed), (control.y, control.vertical_speed))
        self.assertTrue(player.teleport_to(1000, 0, 0))
        player.update(0, False, .04)
        self.assertEqual(player.x, 1000)
        player.recoil_from_hit(-1, 2)
        player.update(0, False, .02, jump_pressed=True)
        self.assertGreater(player.y, 0)
        self.assertGreater(player.vertical_speed, 0)
        self.assertTrue(player.recover_at(1200, 0, 0))
        player.update(0, False, .04)
        self.assertEqual((player.x, player.recoil_remaining), (1200, 0))

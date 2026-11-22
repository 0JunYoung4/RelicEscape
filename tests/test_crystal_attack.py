"""Check the release event, aimed ballistic arc, cover, and shared hit immunity."""

import gc
import os
import unittest
from math import sqrt
from types import SimpleNamespace

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_RENDER_DRIVER"] = "software"

from pico2d import pico2d as pico

from crystal_golem import ATTACK_DURATION, ATTACK_RELEASE, CrystalGolem
from crystal_projectile import ARC_RISE, DAMAGE, GRAVITY, RADIUS, CrystalProjectile
from health import CONTACT_INVULNERABILITY, Health
from lower_caves import COMBAT_WIDTH, LowerCaves
from main import Camera
from player import Player


class CrystalAttackTests(unittest.TestCase):
    def test_charge_stops_movement_locks_target_and_releases_only_once_at_frame_eight(self):
        golem = CrystalGolem(400, 600)
        golem.attack_cooldown = 0
        target = (900, 0, 940, 140)
        self.assertIsNone(golem.update(.01, target, (), 1920))
        self.assertEqual((golem.attack_time, golem.x, golem.direction), (0, 500, 1))
        moved_target = (1300, 200, 1340, 340)
        self.assertIsNone(golem.update(ATTACK_RELEASE - .001, moved_target, (), 1920))
        shot = golem.update(.002, moved_target, (), 1920)
        self.assertIsInstance(shot, CrystalProjectile)
        self.assertEqual((shot.x, shot.y), (480, 128))
        self.assertEqual(golem.attack_target, (920, 70))
        self.assertEqual(golem.x, 500)
        for _ in range(10):
            self.assertIsNone(golem.update(.02, moved_target, (), 1920))
        golem.update(ATTACK_DURATION, (), (), 1920)
        self.assertIsNone(golem.attack_time)

    def test_sword_hit_does_not_interrupt_charge_and_dead_golem_never_fires(self):
        golem = CrystalGolem(400, 600)
        golem.attack_cooldown = 0
        golem.update(.01, (900, 0, 940, 140), (), 1920)
        self.assertTrue(golem.check_strike((450, 0, 550, 100), 1, 12, 1))
        self.assertEqual(golem.attack_time, 0)
        self.assertIsInstance(golem.update(ATTACK_RELEASE, (900, 0, 940, 140), (), 1920), CrystalProjectile)
        golem.hp = 12
        self.assertTrue(golem.check_strike((450, 0, 550, 100), 1, 12, 2))
        self.assertIsNone(golem.attack_time)
        self.assertIsNone(golem.update(10, (900, 0, 940, 140), (), 1920))

    def test_ballistic_arc_rises_then_reaches_both_low_and_high_targets(self):
        for origin, target in (((400, 500), (1100, 70)), ((1500, 500), (900, 640))):
            with self.subTest(target=target):
                shot = CrystalProjectile.aimed(origin, target)
                rise_time = shot.vy / GRAVITY
                apex = max(origin[1], target[1]) + ARC_RISE
                flight_time = rise_time + sqrt(2 * (apex - target[1]) / GRAVITY)
                shot.update(rise_time, (), 1920)
                self.assertAlmostEqual(shot.y, apex)
                self.assertAlmostEqual(shot.vy, 0)
                shot.update(flight_time - rise_time, (), 1920)
                self.assertAlmostEqual(shot.x, target[0])
                self.assertAlmostEqual(shot.y, target[1])
                self.assertLess(shot.vy, 0)

    def test_swept_collision_stops_at_thin_cover_before_a_player_at_low_fps(self):
        shot = CrystalProjectile(100, 100, 2000, 0)
        result = shot.update(.2, ((180, 0, 181, 200),), 1920, (240, 0, 280, 140))
        self.assertEqual(result, "terrain")
        self.assertAlmostEqual(shot.x, 180 - RADIUS)
        self.assertFalse(shot.active)
        self.assertIsNone(shot.update(.2, (), 1920, (240, 0, 280, 140)))

    def test_projectile_stops_at_ground_platform_underside_and_world_edge(self):
        cases = ((CrystalProjectile(500, 200, 0, -900), (), "terrain"),
                 (CrystalProjectile(500, 100, 0, 900), ((400, 200, 600, 220),), "terrain"),
                 (CrystalProjectile(1900, 200, 900, 0), (), None))
        for shot, terrain, expected in cases:
            with self.subTest(terrain=terrain):
                self.assertEqual(shot.update(.5, terrain, 1920), expected)
                self.assertFalse(shot.active)


class CrystalAttackRoomTests(unittest.TestCase):
    def setUp(self):
        pico.open_canvas(960, 540)
        self.room = LowerCaves(SimpleNamespace(width=960, height=540, shaft=SimpleNamespace(w=4096)))
        self.room.room = "combat"
        self.room.encounter_started = True
        self.player = Player(130, 0, COMBAT_WIDTH)
        self.camera = Camera(960, COMBAT_WIDTH)
        self.room.enter(self.player, self.camera)
        self.health = Health((130, 0, 0))

    def tearDown(self):
        del self.room, self.player
        gc.collect()
        pico.close_canvas()

    def test_attack_sprite_release_and_room_projectile_lifecycle(self):
        self.player.recover_at(900, 0, 0)
        first, second = self.room.golems
        first.attack_cooldown = 0
        second.attack_cooldown = 100
        self.room.update_enemies(self.player, .01)
        self.room.update_enemies(self.player, ATTACK_RELEASE + .001)
        self.assertEqual(len(self.room.projectiles), 1)
        self.assertEqual(self.room.golem_attack.frame_at(first.attack_time), 8)
        # A detached projectile continues even after its caster dies.
        first.hp = 0
        shot = self.room.projectiles[0]
        x, y = shot.x, shot.y
        self.room.update_projectiles(self.player, self.health, .05, 1)
        self.assertNotEqual((shot.x, shot.y), (x, y))
        self.room.draw(self.camera)
        self.room.room = "gallery"
        self.room.enter(self.player, self.camera)
        self.assertEqual(self.room.projectiles, [])

    def test_projectile_hit_consumes_shard_and_shares_contact_immunity_and_death(self):
        self.player.recover_at(900, 0, 0)

        def hit(now):
            self.room.projectiles.append(CrystalProjectile(850, 70, 1200, 0))
            self.room.update_projectiles(self.player, self.health, .1, now)
            self.assertEqual(self.room.projectiles, [])

        hit(0)
        self.assertEqual(self.health.current, 100 - DAMAGE)
        self.assertIsNotNone(self.health.hit_tint(0))
        hit(.1)
        self.assertEqual(self.health.current, 100 - DAMAGE)
        self.assertFalse(self.health.take_enemy_hit((900, 70), .2, 10))
        self.health.current = DAMAGE
        hit(CONTACT_INVULNERABILITY)
        self.assertEqual(self.health.current, 0)
        self.assertTrue(self.health.ready_to_restart(CONTACT_INVULNERABILITY + 1))

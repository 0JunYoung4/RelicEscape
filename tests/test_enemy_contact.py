"""Check enemy-body damage, contact immunity, and the main-route death restart."""

import os
import gc
import unittest
from itertools import count
from unittest.mock import Mock, patch

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_RENDER_DRIVER"] = "software"

from pico2d import pico2d as pico

import main
from health import CONTACT_DAMAGE, CONTACT_INVULNERABILITY, RESTART_DELAY, Health
from lower_caves import LowerCaves
from pillbug import CURL_TIME, Pillbug


class EnemyContactTests(unittest.TestCase):
    def test_body_damage_covers_every_live_pose_but_not_dead_or_separated_enemies(self):
        player = Mock()
        bug = Pillbug(400, 800, 0)
        for phase in ("crawl", "curl", "roll", "flip", "overturned", "recover"):
            with self.subTest(phase=phase):
                bug.phase, bug.time = phase, 0
                x, y, width, height = bug.body_bounds()
                player.get_hitbox.return_value = (x - 20, y, x + 20, y + height)
                health = Health((100, 0, 0))
                self.assertTrue(health.check_contact(player, (bug,), 1))
                self.assertEqual(health.current, 100 - CONTACT_DAMAGE)
                self.assertFalse(health.recovering(1))
                self.assertIsNotNone(health.hit_tint(1))
                self.assertIsNone(health.hit_tint(1.2))
                player.get_hitbox.return_value = (x + width + 10, y, x + width + 50, y + 140)
                self.assertFalse(Health((100, 0, 0)).check_contact(player, (bug,), 1))
                player.get_hitbox.return_value = (x - 20, y + height + 1, x + 20, y + height + 141)
                self.assertFalse(Health((100, 0, 0)).check_contact(player, (bug,), 1))
        bug.hp = 0
        player.get_hitbox.return_value = (780, 0, 820, 140)
        self.assertFalse(Health((100, 0, 0)).check_contact(player, (bug,), 1))

    def test_continuous_contact_and_multiple_enemies_share_immunity(self):
        player = Mock()
        player.get_hitbox.return_value = (780, 0, 820, 140)
        enemies = (Pillbug(400, 800, 0), Pillbug(400, 800, 0))
        health = Health((100, 0, 0))
        self.assertTrue(health.check_contact(player, enemies, 0))
        for frame in range(1, 48):
            self.assertFalse(health.check_contact(player, enemies, frame / 60))
        self.assertEqual(health.current, 100 - CONTACT_DAMAGE)
        self.assertTrue(health.check_contact(player, enemies, CONTACT_INVULNERABILITY))
        self.assertEqual(health.current, 100 - 2 * CONTACT_DAMAGE)

    def test_rolling_shell_deals_damage_at_its_stopping_surface(self):
        player = Mock()
        player.get_hitbox.return_value = (520, 0, 560, 140)
        bug = Pillbug(400, 800, 0)
        bug.update(CURL_TIME, player.get_hitbox(), (), 2400)
        bug.update(1, player.get_hitbox(), (), 2400)
        self.assertEqual(bug.phase, "overturned")
        self.assertTrue(Health((100, 0, 0)).check_contact(player, (bug,), 1))

    def test_lethal_contact_enters_existing_death_delay_and_ignores_more_contacts(self):
        player = Mock()
        player.get_hitbox.return_value = (780, 0, 820, 140)
        bug = Pillbug(400, 800, 0)
        health = Health((100, 0, 0))
        health.current = CONTACT_DAMAGE
        self.assertTrue(health.check_contact(player, (bug,), 2))
        self.assertEqual(health.current, 0)
        self.assertTrue(health.recovering(2))
        self.assertFalse(health.ready_to_restart(2.1))
        self.assertTrue(health.ready_to_restart(2 + RESTART_DELAY))
        self.assertFalse(health.check_contact(player, (bug,), 5))

    def test_main_route_restarts_the_gallery_after_contact_death(self):
        pico.open_canvas(main.SCREEN_WIDTH, main.SCREEN_HEIGHT)
        self.addCleanup(pico.close_canvas)
        healths, rooms, frames = [], [], []
        sequence = Mock(active=True, stood_up=True)
        event_frames = count()

        def make_health(*args, **kwargs):
            health = Health(*args, **kwargs)
            if not healths:
                health.current = CONTACT_DAMAGE
            healths.append(health)
            return health

        def make_room(cave):
            room = LowerCaves(cave)
            room.room = "gallery"
            room.pillbugs = [Pillbug(120, 150, 0)]
            rooms.append(room)
            return room

        def read_events():
            if next(event_frames) == 100:
                return [pico.Event(pico.SDL_QUIT)]
            return []

        def record_hud(health, height, now):
            frames.append((health.current, rooms[-1].room if rooms else None))

        with patch.object(main, "Health", side_effect=make_health), \
                patch.object(main, "LowerCaves", side_effect=make_room) as room_factory, \
                patch.object(main, "SigilApproach", return_value=sequence), \
                patch.object(main, "read_movement", return_value=(0, False, False)), \
                patch.object(main, "perf_counter", side_effect=count(step=1 / 120)), \
                patch.object(main, "sleep"), \
                patch.object(pico, "SDL_GetKeyboardFocus", return_value=True), \
                patch.object(main, "poll_events", side_effect=read_events), \
                patch.object(Health, "draw_hud", new=record_hud):
            self.assertIsNone(main.run_opening_cave(False))
        self.assertIn((0, "gallery"), frames)
        self.assertIn((100, "gallery"), frames)
        self.assertEqual(len(rooms), 2)
        self.assertEqual(healths[-1].spawn_pose, (130, 0, 0))
        self.assertEqual(rooms[-1].pillbugs[0].hp, 30)
        # Release textures retained by mock call records before SDL closes this canvas.
        sequence.reset_mock()
        room_factory.reset_mock()
        rooms.clear()
        gc.collect()

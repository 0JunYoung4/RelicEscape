"""Verify the ground-emergence pose finishes before normal pillbug combat."""

import gc
import os
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_RENDER_DRIVER"] = "software"

from pico2d import pico2d as pico

from health import Health
from lower_caves import COMBAT_CENTER_X, COMBAT_WIDTH, LowerCaves
from main import Camera
from pillbug import ATTACK_COOLDOWN, EMERGE_DURATION, Pillbug
from player import Player


class PillbugEmergenceTests(unittest.TestCase):
    def test_emergence_stays_grounded_and_transitions_once_to_the_existing_crawl(self):
        for fps in (30, 60, 120):
            with self.subTest(fps=fps):
                bug = Pillbug(400, 800, 0)
                bug.floor_y = 200
                bug.begin_emergence()
                start = bug.x, bug.floor_y, bug.direction
                for _ in range(round(EMERGE_DURATION * fps) + 1):
                    bug.update(1 / fps, (1600, 0, 1640, 140), (), 1920)
                    self.assertEqual((bug.x, bug.floor_y, bug.direction), start)
                    if bug.phase != "emerge":
                        break
                self.assertEqual((bug.phase, bug.time), ("crawl", 0))
                self.assertEqual(bug.attack_cooldown, ATTACK_COOLDOWN)
                bug.update(.05, (1600, 0, 1640, 140), (), 1920)
                self.assertLess(bug.x, start[0])

    def test_buried_pillbug_cannot_take_or_deal_invisible_damage(self):
        bug = Pillbug(400, 800, 0)
        player = Mock()
        player.get_hitbox.return_value = (760, 0, 840, 140)
        health = Health((130, 0, 0))
        bug.begin_emergence()
        self.assertFalse(bug.check_strike((760, 0, 840, 100), 1, 12, 1))
        self.assertFalse(health.check_contact(player, (bug,), 0))
        self.assertEqual((bug.hp, health.current), (30, 100))
        bug.update(EMERGE_DURATION, player.get_hitbox(), (), 1920)
        self.assertTrue(bug.check_strike((760, 0, 840, 100), 1, 12, 1))
        self.assertTrue(health.check_contact(player, (bug,), 2))
        self.assertEqual((bug.hp, health.current), (18, 90))

    def test_repeated_start_does_not_reset_progress_and_death_does_not_revive(self):
        bug = Pillbug(400, 800, 0)
        bug.begin_emergence()
        bug.update(.4, (), (), 1920)
        bug.begin_emergence()
        self.assertEqual(bug.time, .4)
        bug.hp = 0
        bug.begin_emergence()
        bug.update(10, (), (), 1920)
        self.assertEqual((bug.hp, bug.time), (0, .4))


class PillbugEmergenceRoomTests(unittest.TestCase):
    def test_center_trigger_uses_emergence_art_then_normal_crawl_without_restarting_on_return(self):
        pico.open_canvas(960, 540)
        try:
            room = LowerCaves(SimpleNamespace(width=960, height=540, shaft=SimpleNamespace(w=4096)))
            room.room = "combat"
            player = Player(130, 0, COMBAT_WIDTH)
            camera = Camera(960, COMBAT_WIDTH)
            room.enter(player, camera)
            self.assertFalse(room.encounter_started)
            player.recover_at(COMBAT_CENTER_X, 0, 0)
            room.update_enemies(player, 0)
            self.assertEqual([bug.phase for bug in room.combat_pillbugs], ["emerge", "emerge"])
            with patch.object(room.pillbug_emergence, "draw") as emerging, \
                    patch.object(room.crawl, "draw") as crawl:
                room.draw(camera)
                self.assertEqual(emerging.call_count, 2)
                crawl.assert_not_called()
            room.update_enemies(player, .4)
            room.room = "gallery"
            room.enter(player, camera)
            room.room = "combat"
            room.enter(player, camera)
            self.assertEqual([bug.time for bug in room.combat_pillbugs], [.4, .4])
            room.update_enemies(player, EMERGE_DURATION - .4)
            with patch.object(room.pillbug_emergence, "draw") as emerging, \
                    patch.object(room.crawl, "draw") as crawl:
                room.draw(camera)
                emerging.assert_not_called()
                self.assertEqual(crawl.call_count, 2)
            self.assertFalse(room.exit_open)
            del room, player
        finally:
            gc.collect()
            pico.close_canvas()

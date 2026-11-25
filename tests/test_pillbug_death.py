"""Check lethal curl, textured pixel breakup, and removal without extra damage."""

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
from lower_caves import COMBAT_WIDTH, LowerCaves
from main import Camera
from pillbug import DEATH_CURL_DURATION, DEATH_DURATION, DEATH_PIXEL_COLORS, Pillbug
from player import Player


class PillbugDeathTests(unittest.TestCase):
    def test_third_sword_hit_enters_death_once_and_never_moves_attacks_or_hurts(self):
        for fps in (30, 60, 120):
            with self.subTest(fps=fps):
                bug = Pillbug(400, 800, 0)
                box = (760, 0, 840, 100)
                for swing, hp in enumerate((18, 6, 0), 1):
                    self.assertTrue(bug.check_strike(box, 1, 12, swing))
                    self.assertEqual(bug.hp, hp)
                self.assertEqual((bug.phase, bug.death_time), ("death", 0))
                self.assertFalse(bug.check_strike(box, 1, 12, 4))
                bug.begin_emergence()
                player = Mock()
                player.get_hitbox.return_value = box
                self.assertFalse(Health((100, 0, 0)).check_contact(player, (bug,), 0))
                x = bug.x
                for _ in range(2 * fps):
                    bug.update(1 / fps, box, (), 1920)
                    self.assertEqual((bug.x, bug.hp, bug.phase), (x, 0, "death"))
                self.assertEqual(bug.death_time, DEATH_DURATION)

    def test_overturned_death_keeps_orientation_and_rolling_death_stays_curled(self):
        for phase in ("overturned", "roll", "recover"):
            with self.subTest(phase=phase):
                bug = Pillbug(400, 800, 0)
                bug.phase, bug.time, bug.hp = phase, 0, 12
                self.assertTrue(bug.check_strike((700, -20, 900, 160), 1, 12, 1))
                self.assertEqual(bug.death_flipped, phase != "roll")
                self.assertEqual(bug.death_first_frame, 7 if phase == "roll" else 0)


class PillbugDeathRenderTests(unittest.TestCase):
    def setUp(self):
        pico.open_canvas(960, 540)
        self.room = LowerCaves(SimpleNamespace(width=960, height=540, shaft=SimpleNamespace(w=4096)))
        self.player = Player(130, 0, COMBAT_WIDTH)
        self.camera = Camera(960, COMBAT_WIDTH)

    def tearDown(self):
        del self.room, self.player
        gc.collect()
        pico.close_canvas()

    def test_curl_is_one_sprite_then_ball_becomes_many_separating_blue_pixels(self):
        bug = Pillbug(400, 800, 0)
        bug.hp = 12
        bug.check_strike((760, 0, 840, 100), 1, 12, 1)
        art = self.room.pillbug_death

        def draw():
            bug.draw(self.room.crawl, self.room.attack_poses, self.camera,
                     self.room.hurt_poses, death=art)

        with patch.object(art.image, "clip_composite_draw") as render, \
                patch.object(pico, "draw_rectangle") as pixels:
            bug.death_time = DEATH_CURL_DURATION - .01
            draw()
            self.assertEqual(render.call_count, 1)
            pixels.assert_not_called()
            render.reset_mock()
            bug.death_time = DEATH_CURL_DURATION + .15
            draw()
            render.assert_not_called()
            self.assertGreater(pixels.call_count, 20)
            self.assertTrue(all(call.args[4:7] in DEATH_PIXEL_COLORS for call in pixels.call_args_list))
            first_positions = [call.args[:2] for call in pixels.call_args_list]
            pixels.reset_mock()
            bug.death_time += .1
            draw()
            self.assertNotEqual(first_positions, [call.args[:2] for call in pixels.call_args_list])
            pixels.reset_mock()
            bug.death_time = DEATH_DURATION
            draw()
            render.assert_not_called()
            pixels.assert_not_called()

    def test_actual_room_sword_kills_use_death_art_in_both_gallery_and_combat(self):
        for name in ("gallery", "combat"):
            with self.subTest(room=name):
                self.room.room = name
                self.room.combat_phase = "pillbugs"
                self.room.enter(self.player, self.camera)
                bug = (self.room.pillbugs if name == "gallery" else self.room.combat_pillbugs)[0]
                for _ in range(3):
                    self.player.recover_at(bug.x - 120, bug.floor_y, 0)
                    self.player.swing_id += 1
                    self.player.slash = (0, 1, "attack")
                    self.room.update_enemies(self.player, 0)
                self.player.slash = None
                self.assertEqual((bug.hp, bug.phase), (0, "death"))
                self.room.update_enemies(self.player, DEATH_CURL_DURATION + .1)
                with patch.object(pico, "draw_rectangle") as render:
                    self.room.draw(self.camera)
                    blue_pixels = [call for call in render.call_args_list if call.args[4:7] in DEATH_PIXEL_COLORS]
                    self.assertGreater(len(blue_pixels), 20)

"""Exercise solid terrain, wall contact, wall slides and wall jumps."""

import os
import unittest
from unittest.mock import patch

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["SDL_RENDER_DRIVER"] = "software"

from pico2d import pico2d as pico

from main import CAMERA_ZOOM, GROUND_Y, SCREEN_WIDTH, TEST_TERRAIN, WORLD_WIDTH, Camera, draw_scene
from player import CROUCH_DURATION, WALL_JUMP_PUSH_TIME, WALL_SLIDE_SPEED, Player


class WallMovementTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pico.open_canvas(960, 540)

    @classmethod
    def tearDownClass(cls):
        pico.close_canvas()

    def setUp(self):
        self.player = Player(400, GROUND_Y, WORLD_WIDTH, terrain=((900, 200, 980, 700),))

    def tearDown(self):
        del self.player

    def put_on_wall(self, side, speed=-500):
        self.player.x = 880 if side == 1 else 1000
        self.player.y = 450
        self.player.vertical_speed = speed

    def test_horizontal_collision_does_not_tunnel_through_either_face(self):
        self.player.update(1, True, 2)
        self.assertEqual(self.player.get_hitbox()[2], 900)
        self.player.x = 1400
        self.player.update(-1, True, 2)
        self.assertEqual(self.player.get_hitbox()[0], 980)
        self.assertFalse(self.player._overlaps_terrain())

    def test_wall_slide_requires_air_contact_direction_and_falling(self):
        for side in (-1, 1):
            with self.subTest(side=side):
                self.put_on_wall(side)
                self.player.update(side, False, 1 / 60)
                self.assertEqual(self.player.state, "wall_slide")
                self.assertEqual(self.player.wall_direction, side)
                self.assertGreaterEqual(self.player.vertical_speed, -WALL_SLIDE_SPEED)
                self.assertLessEqual(450 - self.player.y, WALL_SLIDE_SPEED / 60 + 0.001)
                self.assertFalse(self.player.grounded)

    def test_releasing_or_moving_away_from_wall_restores_normal_falling(self):
        for direction in (0, -1):
            with self.subTest(direction=direction):
                self.put_on_wall(1)
                self.player.update(1, False, 1 / 60)
                self.player.update(direction, False, 0.1)
                self.assertEqual(self.player.state, "jump")
                self.assertLess(self.player.vertical_speed, -WALL_SLIDE_SPEED)

    def test_wall_slide_plays_three_frames_once_then_holds_and_restarts_on_contact(self):
        self.put_on_wall(1)
        self.player.animation_time = 3.0
        self.player.update(1, False, 1 / 60)
        self.assertEqual(self.player.get_wall_slide_frame(), 0)
        self.player.update(1, False, 1 / 24)
        self.assertEqual(self.player.get_wall_slide_frame(), 1)
        self.player.update(1, False, 1 / 24)
        self.assertEqual(self.player.get_wall_slide_frame(), 2)
        self.player.update(1, False, 0.3)
        self.assertEqual(self.player.get_wall_slide_frame(), 2)
        self.player.update(0, False, 1 / 60)
        self.assertEqual(self.player.state, "jump")
        self.assertGreaterEqual(self.player.get_jump_frame(), 4)
        self.player.update(1, False, 1 / 60)
        self.assertEqual(self.player.get_wall_slide_frame(), 0)

    def test_wall_slide_uses_approved_art_and_mirrors_for_both_walls(self):
        animation = self.player.animations["wall_slide"]
        camera = Camera(SCREEN_WIDTH, WORLD_WIDTH, CAMERA_ZOOM)
        self.assertEqual(len(animation.frames), 3)
        self.assertEqual((animation.image.w, animation.image.h), (2172, 724))
        for side in (-1, 1):
            self.put_on_wall(side)
            self.player.state = "jump"
            self.player.update(side, False, 1 / 60)
            for index in range(3):
                self.player.animation_time = index / animation.fps
                with patch.object(animation, "draw", wraps=animation.draw) as draw:
                    pico.SDL_ClearError()
                    self.player.draw(camera)
                    self.assertFalse(pico.SDL_GetError())
                    self.assertEqual(draw.call_count, 1)
                    self.assertEqual(draw.call_args.args[2], side)
                    self.assertEqual(draw.call_args.args[-1], index)

    def test_wall_slide_hand_contact_and_clipped_boots_align_with_body_hitbox(self):
        animation = self.player.animations["wall_slide"]
        for side in (-1, 1):
            self.put_on_wall(side)
            contact_x = self.player.get_hitbox()[2 if side == 1 else 0]
            for frame in animation.frames:
                anchor_x, _ = frame["foot_anchor"]
                art_contact_x = self.player.x + side * (frame["width"] - anchor_x) * animation.scale
                self.assertAlmostEqual(art_contact_x, contact_x)

    def test_top_of_wall_requires_support_at_hand_height_but_still_allows_wall_jump(self):
        for side in (-1, 1):
            with self.subTest(side=side):
                self.player.wall_jump_remaining = 0
                self.put_on_wall(side, speed=-120)
                self.player.y = 650
                self.player.state = "jump"
                self.player.update(side, False, 1 / 60)
                self.assertNotEqual(self.player.state, "wall_slide")
                self.assertLess(self.player.vertical_speed, -WALL_SLIDE_SPEED)
                self.assertEqual(self.player.wall_direction, side)
                self.player.update(side, False, 1 / 60, jump_pressed=True)
                self.assertGreater(self.player.vertical_speed, 0)
                self.put_on_wall(side)
                self.player.wall_jump_remaining = 0
                self.player.y = 575
                self.player.update(side, False, 1 / 60)
                self.assertNotEqual(self.player.state, "wall_slide")
                for _ in range(20):
                    self.player.update(side, False, 1 / 60)
                self.assertEqual(self.player.state, "wall_slide")
                self.assertLessEqual(self.player.get_hitbox()[3], 700)

    def test_rising_along_wall_is_not_stopped_before_apex(self):
        self.put_on_wall(1, speed=400)
        self.player.update(1, False, 0.05)
        self.assertGreater(self.player.y, 450)
        self.assertGreater(self.player.vertical_speed, 0)
        self.assertEqual(self.player.state, "jump")
        for _ in range(20):
            self.player.update(1, False, 1 / 60)
        self.assertEqual(self.player.state, "wall_slide")

    def test_wall_jump_pushes_away_even_while_holding_towards_wall(self):
        for side in (-1, 1):
            with self.subTest(side=side):
                self.player.wall_jump_remaining = 0
                self.put_on_wall(side)
                previous_x = self.player.x
                self.player.update(side, False, 1 / 60, jump_pressed=True)
                self.assertEqual(self.player.state, "jump")
                self.assertGreater(self.player.vertical_speed, 0)
                self.assertEqual(self.player.facing, -side)
                self.assertGreater((self.player.x - previous_x) * -side, 0)
                self.assertEqual(self.player.wall_direction, 0)
                self.player.update(side, False, WALL_JUMP_PUSH_TIME / 2)
                self.assertGreater((self.player.x - previous_x) * -side, 0)
                self.assertFalse(self.player._overlaps_terrain())

    def test_ground_at_wall_and_map_boundary_do_not_count_as_wall_slide(self):
        self.player.x = 880
        self.player.update(1, False, 0.1)
        self.assertNotEqual(self.player.state, "wall_slide")
        self.player.update(1, False, 0.1, jump_pressed=True)
        self.assertEqual(self.player.wall_jump_remaining, 0)
        self.assertGreater(self.player.vertical_speed, 0)
        self.player.x = 64
        self.player.y = 500
        self.player.vertical_speed = -200
        self.player.update(-1, False, 1 / 60)
        self.assertEqual(self.player.wall_direction, 0)
        self.assertEqual(self.player.state, "jump")

    def test_platform_landing_support_and_walking_off(self):
        self.player.terrain = ((500, 300, 800, 340),)
        self.player.x = 600
        self.player.y = 500
        self.player.vertical_speed = -300
        self.player.update(0, False, 0.5)
        self.assertEqual(self.player.y, 340)
        self.assertTrue(self.player.grounded)
        self.player.update(0, False, 0.2)
        self.assertEqual(self.player.y, 340)
        self.assertEqual(self.player.state, "idle")
        self.player.update(1, True, 0.5)
        self.assertLess(self.player.y, 340)

    def test_ceiling_collision_stops_upward_speed(self):
        self.player.terrain = ((500, 420, 800, 460),)
        self.player.x = 600
        self.player.update(0, False, 0.3, jump_pressed=True)
        self.assertEqual(self.player.get_hitbox()[3], 420)
        self.assertEqual(self.player.vertical_speed, 0)
        self.assertFalse(self.player.grounded)
        self.player.update(0, False, 0.05)
        self.assertLess(self.player.get_hitbox()[3], 420)
        self.assertFalse(self.player._overlaps_terrain())

    def test_crouch_jump_stops_at_low_ceiling_and_stays_low_until_clear(self):
        self.player.terrain = ((500, 300, 800, 340),)
        self.player.x = 600
        self.player.crouch_time = CROUCH_DURATION
        self.player.state = "crouch"
        self.player.update(0, False, 0.05, jump_pressed=True, crouch_held=True)
        self.assertEqual(self.player.state, "jump")
        self.assertGreater(self.player.y, self.player.ground_y)
        self.assertEqual(self.player.get_hitbox()[3], 300)
        self.assertEqual(self.player.vertical_speed, 0)
        self.player.update(0, False, 1 / 60)
        self.assertEqual(self.player.crouch_time, CROUCH_DURATION)
        self.assertFalse(self.player._overlaps_terrain())
        for _ in range(30):
            self.player.update(0, False, 1 / 60)
        self.assertGreater(self.player.crouch_time, 0)
        self.assertLessEqual(self.player.get_hitbox()[3], 300.001)
        for _ in range(180):
            self.player.update(-1, False, 1 / 60)
        self.assertEqual(self.player.crouch_time, 0)
        self.assertEqual(self.player.state, "walk")
        self.assertFalse(self.player._overlaps_terrain())

    def test_leaving_platform_crouched_recovers_airborne_body_when_clear(self):
        self.player.terrain = ((500, 300, 800, 340),)
        self.player.x = 835
        self.player.y = 340
        self.player.crouch_time = CROUCH_DURATION
        self.player.state = "crouch"
        self.player.update(1, False, 0.2, crouch_held=True)
        self.assertEqual(self.player.state, "jump")
        self.assertEqual(self.player.crouch_time, 0)
        self.assertLess(self.player.y, 340)

    def test_test_map_first_wall_can_be_climbed_with_repeated_wall_jumps(self):
        self.player.terrain = TEST_TERRAIN
        self.player.x = 900
        self.player.update(1, False, 1 / 60, jump_pressed=True)
        wall_jumps = 0
        for _ in range(600):
            pressed = self.player.state == "wall_slide"
            wall_jumps += int(pressed)
            self.player.update(1, False, 1 / 60, jump_pressed=pressed)
            self.assertFalse(self.player._overlaps_terrain())
            if self.player.grounded and self.player.y == 620:
                break
        self.assertGreaterEqual(wall_jumps, 2)
        self.assertTrue(self.player.grounded)
        self.assertEqual(self.player.y, 620)
        self.assertGreater(self.player.x, 920)

    def test_slide_lands_and_terrain_renders_with_hitboxes(self):
        self.put_on_wall(1)
        camera = Camera(SCREEN_WIDTH, WORLD_WIDTH, CAMERA_ZOOM)
        for _ in range(180):
            self.player.update(1, False, 1 / 60)
        self.assertTrue(self.player.grounded)
        self.assertEqual(self.player.y, GROUND_Y)
        self.assertNotEqual(self.player.state, "wall_slide")
        self.player.terrain = TEST_TERRAIN
        pico.SDL_ClearError()
        draw_scene(self.player, camera, show_hitboxes=True)
        self.assertFalse(pico.SDL_GetError())


if __name__ == "__main__":
    unittest.main()

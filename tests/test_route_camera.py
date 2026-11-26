"""Keep corridor framing steady across jumps, climbs and explicit relocations."""

import gc
import os
from types import SimpleNamespace
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("SDL_RENDER_DRIVER", "software")

from pico2d import pico2d as pico

from lower_caves import LowerCaves
from lower_route_b import LowerRouteB
from main import Camera
from player import GRAVITY, JUMP_SPEED, Player
from route_camera import FOOT_LINE, ROUTE_CAMERA_ZOOM


HEIGHT = 540
BOUNDS = (LowerRouteB.camera_bottom, LowerRouteB.camera_top)


class RouteCameraTests(unittest.TestCase):
    def setUp(self):
        self.camera = Camera(960, 12000)
        self.player = SimpleNamespace(x=2500, y=180, grounded=True)
        self.camera.follow_route(self.player, HEIGHT, BOUNDS)

    def follow(self, dt=1 / 60):
        self.camera.follow_route(self.player, HEIGHT, BOUNDS, dt)

    def test_a_full_ordinary_jump_does_not_move_the_camera_vertically(self):
        start_y = self.camera.y
        self.player.grounded = False
        for step in range(55):
            elapsed = step / 60
            self.player.y = 180 + max(0, JUMP_SPEED * elapsed - GRAVITY * elapsed ** 2 / 2)
            self.follow()
            self.assertEqual(self.camera.y, start_y)
        self.player.y, self.player.grounded = 180, True
        self.follow()
        self.assertEqual(self.camera.y, start_y)

    def test_a_climb_tracks_smoothly_and_a_higher_landing_sets_the_new_foot_line(self):
        start_y = self.camera.y
        self.player.grounded = False
        for _ in range(70):
            previous = self.camera.y
            self.player.y += 5
            self.follow()
            self.assertLess(abs(self.camera.y - previous), 6)
        self.assertGreater(self.camera.y, start_y)
        self.player.y, self.player.grounded = 590, True
        for _ in range(90):
            self.follow()
        feet = self.camera.world_to_screen(self.player.x, self.player.y)[1]
        self.assertAlmostEqual(feet, HEIGHT * FOOT_LINE, delta=.01)

    def test_a_long_fall_tracks_down_and_keeps_the_feet_visible(self):
        self.player.y = 590
        self.follow(None)
        start_y = self.camera.y
        self.player.grounded = False
        for step in range(1, 69):
            elapsed = step / 60
            self.player.y = max(-690, 590 - GRAVITY * elapsed ** 2 / 2)
            self.follow()
            feet = self.camera.world_to_screen(self.player.x, self.player.y)[1]
            self.assertGreaterEqual(feet, HEIGHT * .08 - .001)
            self.assertLess(feet, HEIGHT * .5)
        self.assertLess(self.camera.y, start_y)
        self.player.y, self.player.grounded = -690, True
        for _ in range(90):
            self.follow()
        self.assertEqual(self.camera.y, BOUNDS[0])

    def test_landing_response_is_independent_of_frame_rate(self):
        results = []
        for frequency in (30, 60, 120):
            camera = Camera(960, 12000)
            player = SimpleNamespace(x=2500, y=180, grounded=True)
            camera.follow_route(player, HEIGHT, BOUNDS)
            player.x, player.y = 2900, 590
            for _ in range(frequency):
                camera.follow_route(player, HEIGHT, BOUNDS, 1 / frequency)
            results.append((camera.x, camera.y))
        for x, y in results[1:]:
            self.assertAlmostEqual(x, results[0][0], places=8)
            self.assertAlmostEqual(y, results[0][1], places=8)

    def test_explicit_teleport_snaps_and_temporary_relic_view_does_not_shift_tracking(self):
        self.player.x, self.player.y = 1160, 590
        self.follow(None)
        self.assertEqual(self.camera.zoom, ROUTE_CAMERA_ZOOM)
        self.assertEqual(self.camera.normal_zoom, .5)
        self.assertAlmostEqual(self.camera.world_to_screen(self.player.x, self.player.y)[1], HEIGHT * FOOT_LINE)
        origin = self.camera.x, self.camera.y
        self.camera.focus_relic((4500, -560), bottom=BOUNDS[0], top=BOUNDS[1])
        self.assertNotEqual((self.camera.x, self.camera.y), origin)
        self.camera.x, self.camera.y = origin
        self.follow()
        self.assertEqual((self.camera.x, self.camera.y), origin)


class RouteCameraIntegrationTests(unittest.TestCase):
    def setUp(self):
        pico.open_canvas(960, HEIGHT)
        cave = SimpleNamespace(width=960, height=HEIGHT, shaft=SimpleNamespace(w=4096))
        self.rooms = LowerCaves(cave)
        self.player = Player(0, 0, 12000)
        self.camera = Camera(960, 12000)

    def tearDown(self):
        del self.rooms, self.player
        gc.collect()
        pico.close_canvas()

    def test_route_entry_combat_return_and_reentry_keep_their_own_zoom(self):
        for section, zoom in (("route_b", .45), ("combat", .5), ("route_c", .45), ("route_a", .45)):
            self.rooms.room = section
            self.rooms.enter(self.player, self.camera)
            self.assertEqual(self.camera.zoom, zoom)
            self.assertEqual(self.camera.normal_zoom, .5)
            self.assertLessEqual(0, self.camera.world_to_screen(self.player.x, self.player.y)[1])
            self.assertLessEqual(self.camera.world_to_screen(self.player.x, self.player.y)[1], HEIGHT)

    def test_live_route_update_keeps_the_ground_anchor_through_a_jump(self):
        self.rooms.room = "route_b"
        self.rooms.enter(self.player, self.camera)
        start_y = self.camera.y
        peak = self.player.y
        for frame in range(70):
            self.rooms.update(self.player, self.camera, 1 / 60, interact=False, direction=0,
                              running=False, jump_pressed=frame == 0, jump_held=True,
                              crouching=False, attack_pressed=False)
            peak = max(peak, self.player.y)
            self.assertEqual(self.camera.y, start_y)
        self.assertGreater(peak, self.player.y + 200)
        self.assertTrue(self.player.grounded)


if __name__ == "__main__":
    unittest.main()

"""Exercise the playable gorge through the game's input and recovery loop."""

from itertools import count
import os
from types import SimpleNamespace
import unittest
from unittest.mock import patch

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("SDL_RENDER_DRIVER", "software")

from pico2d import pico2d as pico

import main
from enemy_knockback import KNOCKBACK_DURATION
from health import MAX_HEALTH, SPIKE_DAMAGE, Health
from lower_caves import LowerCaves
from lower_route_b import PLAY_TERRAIN, SPAWN, SPIKES, LowerRouteB
from lower_route_b_layout import (C_APPROACH_LEDGE, C_PASSAGE, PILLBUG_LEDGE, RAIL_ONE, RAIL_TWO,
                                  SHIELD_LEDGE, THORN_WALLS, WIDTH)
from player import Player, STANDING_HITBOX_HEIGHT
from rail import RAIL_TRAVEL_SPEED
from shield_soldier import KNOCKBACK_DISTANCE, REAR_OPENING


def keydown(key):
    event = pico.Event(pico.SDL_KEYDOWN)
    event.key = key
    return [event]


class LowerRouteBTests(unittest.TestCase):
    def setUp(self):
        pico.open_canvas(main.SCREEN_WIDTH, main.SCREEN_HEIGHT)
        self.addCleanup(pico.close_canvas)

    def test_plays_both_rails_wall_jumps_and_recovers_from_early_recall(self):
        state = SimpleNamespace(room=None, player=None, step="first_dock", direction=0, health=None)
        view_positions = []
        health_samples = []
        keys = [0] * pico.SDL_NUM_SCANCODES
        draw = LowerCaves.draw
        check_spikes = LowerRouteB.check_spikes

        def start(room, player, camera):
            room.room, room.has_relic = "route_b", True
            room.enter(player, camera)
            state.room, state.player = room, player

        def after_step(route, player, health, now):
            state.health = health
            hit = check_spikes(route, player, health, now)
            if hit:
                health_samples.append((health.current, health.safe_pose, route.carriages[0].position))
            return hit

        def record(room, camera):
            if keys[pico.SDL_SCANCODE_C] and room.route_b.mounted_carriage is not None:
                position = camera.world_to_screen(*room.route_b.mounted_carriage.position)
                view_positions.append(position)
            draw(room, camera)

        frames = count()

        def events():
            player = state.player
            first, second = state.room.route_b.carriages
            step = state.step
            state.direction = 0
            keys[pico.SDL_SCANCODE_C] = 0
            keys[pico.SDL_SCANCODE_SPACE] = 1
            if next(frames) > 2000:
                self.fail(f"Stopped at {step}: {player.x:.1f}, {player.y:.1f}, wall={player.wall_direction}")
            if step in ("first_dock", "retry_dock"):
                if step == "retry_dock" and (state.health.current == MAX_HEALTH
                                             or state.health.recovering(clock.now)):
                    return []
                if player.x > 4680:
                    state.direction = -1
                    return []
                state.step = "fail_launch" if step == "first_dock" else "first_launch"
                return keydown(pico.SDLK_e)
            if step in ("fail_launch", "first_launch"):
                self.assertTrue(first.relic_mounted)
                state.step = "early_recall" if step == "fail_launch" else "first_ride"
                return keydown(pico.SDLK_x)
            if step == "early_recall" and first.position[0] < 4080:
                state.step = "retry_dock"
                return keydown(pico.SDLK_e)
            if step == "first_ride":
                keys[pico.SDL_SCANCODE_C] = 1
                if first.distance == 0:
                    state.step = "to_wall"
                    return keydown(pico.SDLK_e)
            if step == "to_wall" and player.grounded:
                self.assertEqual(player.y, PILLBUG_LEDGE[3])
                state.direction = -1
                if player.x <= 3096:
                    state.step = "left_wall"
                    return keydown(pico.SDLK_SPACE)
            if step == "left_wall":
                state.direction = -1
                if player.wall_direction == -1 and player.y >= 370:
                    state.direction, state.step = 1, "right_wall"
                    return keydown(pico.SDLK_SPACE)
            if step == "right_wall":
                state.direction = 1
                if player.wall_direction == 1 and player.y >= 530:
                    state.direction, state.step = -1, "top_ledge"
                    return keydown(pico.SDLK_SPACE)
            if step == "top_ledge":
                state.direction = -1
                if player.grounded:
                    self.assertEqual(player.y, SHIELD_LEDGE[3])
                    state.step = "second_dock"
            if step == "second_dock":
                state.direction = -1
                if player.x <= 2375:
                    state.direction, state.step = 0, "second_launch"
                    return keydown(pico.SDLK_e)
            if step == "second_launch":
                self.assertTrue(second.relic_mounted)
                state.step = "second_ride"
                return keydown(pico.SDLK_x)
            if step == "second_ride":
                keys[pico.SDL_SCANCODE_C] = 1
                if second.distance == 0:
                    state.step = "exit"
                    return keydown(pico.SDLK_e)
            if step == "exit" and player.grounded:
                self.assertEqual(player.y, C_APPROACH_LEDGE[3])
                if player.x <= C_PASSAGE[2] - 80:
                    return [pico.Event(pico.SDL_QUIT)]
                state.direction = -1
            return []

        # The event driver uses the current game time while waiting out the return fade.
        timer = count(step=1 / 120)
        clock = SimpleNamespace(now=0)

        def now():
            clock.now = next(timer)
            return clock.now

        with patch.object(LowerCaves, "start_after_relic", new=start), \
                patch.object(LowerCaves, "draw", new=record), \
                patch.object(LowerRouteB, "check_spikes", new=after_step), \
                patch.object(pico, "get_events", side_effect=events), \
                patch.object(pico, "SDL_GetKeyboardFocus", return_value=True), \
                patch.object(pico, "SDL_GetKeyboardState", return_value=keys), \
                patch.object(main, "read_movement", side_effect=lambda: (state.direction, True, False)), \
                patch.object(main, "perf_counter", side_effect=now), \
                patch.object(main, "sleep"), patch.object(pico, "update_canvas"):
            main.run_opening_cave(False, after_relic=True)
        self.assertEqual(health_samples, [(MAX_HEALTH - SPIKE_DAMAGE, SPAWN, (4620, 280))])
        self.assertTrue(state.room.has_relic)
        self.assertEqual(state.step, "exit")
        self.assertGreater(len(view_positions), 75)
        self.assertTrue(all(0 <= x < main.SCREEN_WIDTH and 0 <= y < main.SCREEN_HEIGHT
                            for x, y in view_positions))

    def test_rail_paths_clear_thorns_and_terrain_at_recall_height(self):
        route = LowerRouteB()
        player = Player(*SPAWN[:2], WIDTH)
        route.enter(player)
        for path in (RAIL_ONE, RAIL_TWO):
            for segment in path:
                for step in range(51):
                    x, y = segment.point_at(step / 50)
                    self.assertTrue(player.recover_at(x, y - STANDING_HITBOX_HEIGHT / 2, 0), (x, y))
                    self.assertFalse(any(spike.overlaps(player.get_hitbox()) for spike in SPIKES), (x, y))

        for (left, bottom, right, top), _ in THORN_WALLS:
            feet = bottom + min((top - bottom) / 2, 100)
            self.assertTrue(player.recover_at((left + right) / 2, feet, 0))
            health = Health(SPAWN)
            self.assertTrue(route.check_spikes(player, health, 1))
            self.assertEqual(health.current, MAX_HEALTH - SPIKE_DAMAGE)

    def test_second_rail_moves_continuously_to_the_end(self):
        route = LowerRouteB()
        player = Player(*SPAWN[:2], WIDTH)
        route.enter(player)
        self.assertTrue(player.recover_at(2320, SHIELD_LEDGE[3], 0))
        self.assertEqual(route.use_relic(player, relic_placed=False), (True, None))
        carriage = route.carriages[1]
        carriage.direction = -1
        dt = 1 / 60
        frames = int(carriage.length / (RAIL_TRAVEL_SPEED * dt))
        for frame in range(1, frames + 1):
            route.update(player, dt)
            self.assertAlmostEqual(carriage.distance, carriage.length - frame * RAIL_TRAVEL_SPEED * dt)
        route.update(player, dt)
        self.assertEqual((carriage.distance, carriage.direction), (0, 0))
        self.assertEqual(carriage.position, RAIL_TWO[0].start)
        self.assertIs(route.mounted_carriage, carriage)

    def test_spikes_restore_last_ledge_without_reviving_enemies(self):
        route = LowerRouteB()
        player = Player(*SPAWN[:2], WIDTH, terrain=PLAY_TERRAIN)
        route.enter(player)
        health = Health(SPAWN)
        self.assertTrue(player.recover_at(3500, PILLBUG_LEDGE[3], 0))
        route.pillbug.hp = 0
        self.assertFalse(route.check_spikes(player, health, 0))
        self.assertTrue(player.recover_at(4050, SPIKES[0].y, 0))
        self.assertTrue(route.check_spikes(player, health, 1))
        self.assertTrue(health.return_to_safety(player, 1.3))
        self.assertEqual((player.x, player.y), (3450, PILLBUG_LEDGE[3]))
        self.assertEqual(route.pillbug.hp, 0)

    def test_shield_blocks_frontal_slash_and_only_hits_once_during_bash(self):
        route = LowerRouteB()
        shield = route.shield
        x, y, _, _ = shield.body_bounds()
        strike = (x - 60, y + 10, x + 60, y + 100)
        self.assertFalse(shield.check_strike(strike, x + 90, 12, 1))
        self.assertEqual(shield.hp, 65)
        self.assertEqual(shield.knockback_remaining, 0)
        self.assertIsNotNone(shield.block_time)
        target = (x + 70, y, x + 110, y + 140)
        shield.update(.7, target, PLAY_TERRAIN, WIDTH)
        shield.update(.6, target, PLAY_TERRAIN, WIDTH)
        shield.update(.55, target, PLAY_TERRAIN, WIDTH)
        self.assertFalse(shield.check_strike(strike, x + 90, 12, 2))
        self.assertEqual(shield.hp, 65)
        self.assertIsNotNone(shield.bash_contact(target))
        self.assertIsNone(shield.bash_contact(target))

    def test_rear_hit_in_combat_turns_guard_and_blocks_next_hit_from_that_side(self):
        cave = SimpleNamespace(width=960, height=540, shaft=SimpleNamespace(w=4096))
        room = LowerCaves(cave)
        room.room = "route_b"
        player = Player(*SPAWN[:2], WIDTH, terrain=PLAY_TERRAIN)
        room.enter(player, main.Camera(960, WIDTH))
        shield = room.route_b.shield
        shield.bash_time = shield.bash_start
        start = shield.x

        self.assertTrue(player.recover_at(shield.x - 84, shield.floor_y, 0))
        player.slash = (0.04, 1, "attack")
        player.swing_id = 1
        room.update_enemies(player, 1 / 60)
        self.assertEqual(shield.hp, 53)
        self.assertGreater(shield.x, start)
        self.assertEqual(shield.direction, -1)
        self.assertIsNone(shield.bash_time)
        self.assertEqual(len(room.hit_impacts), 1)

        player.swing_id = 2
        room.update_enemies(player, 1 / 60)
        self.assertEqual(shield.hp, 53)
        self.assertIsNotNone(shield.block_time)
        self.assertEqual(len(room.hit_impacts), 1)
        shield.update(KNOCKBACK_DURATION, None, PLAY_TERRAIN, WIDTH)
        self.assertAlmostEqual(shield.x, start + KNOCKBACK_DISTANCE)

    def test_guard_turns_after_an_uninterrupted_rear_opening(self):
        shield = LowerRouteB().shield
        x, y, _, _ = shield.body_bounds()
        behind = (x - 120, y, x - 80, y + 140)
        front = (x + 80, y, x + 120, y + 140)
        shield.update(.9, behind, PLAY_TERRAIN, WIDTH)
        self.assertEqual(shield.direction, 1)
        shield.update(.01, front, PLAY_TERRAIN, WIDTH)
        shield.update(REAR_OPENING - .02, behind, PLAY_TERRAIN, WIDTH)
        self.assertEqual(shield.direction, 1)
        shield.update(.03, behind, PLAY_TERRAIN, WIDTH)
        self.assertEqual(shield.direction, -1)
        self.assertEqual(shield.hp, 65)

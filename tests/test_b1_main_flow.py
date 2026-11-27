"""Exercise the production C entrance, boss checkpoint and cleared passage."""

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
from health import Health, MAX_HEALTH, RESTART_DELAY
from lower_caves import LowerCaves
from lower_route_c import BOSS_RETURN, CHECKPOINT
from tools.b1_combat_terrain import LEDGES
from tools.b1_combat_tree import Attack
from tools.b1_encounter_stage import B1EncounterStage, BOSS_HALF_HP, BOSS_MAX_HP, CLAW_DAMAGE, SCALE
from tools.preview_b1_intro import GROUND


def _press(key):
    event = pico.Event(pico.SDL_KEYDOWN)
    event.key = key
    return [event]


class B1MainFlowTests(unittest.TestCase):
    def test_c_to_b1_with_relic_retry_and_persistent_victory(self):
        pico.open_canvas(main.SCREEN_WIDTH, main.SCREEN_HEIGHT)
        self.addCleanup(pico.close_canvas)
        state = SimpleNamespace(step="place_c_relic", direction=0, stage=None)
        clock = count(500, 1 / 40)
        frames = count()
        travel = main.RelicTravel()
        draw_boss = B1EncounterStage.draw
        rendered = set()

        def start_at_lantern(room, player, camera):
            state.room, state.player = room, player
            room.room, room.has_relic = "route_c", True
            room.enter(player, camera)

        def create_health(*args, **kwargs):
            state.health = Health(*args, **kwargs)
            return state.health

        def time_now():
            state.now = next(clock)
            return state.now

        def render_boss(stage, *args, **kwargs):
            state.stage = stage
            if stage.state not in rendered:
                rendered.add(stage.state)
                pico.SDL_ClearError()
                draw_boss(stage, *args, **kwargs)
                self.assertFalse(pico.SDL_GetError())

        def events():
            if next(frames) > 1400:
                self.fail(f"B1 flow timed out in {state.step}, room {state.room.room}, "
                          f"position={(state.player.x, state.player.y)}, grounded={state.player.grounded}, "
                          f"health={state.health.current}")
            room, player, stage = state.room, state.player, state.stage
            state.direction = 0
            if state.step == "place_c_relic":
                self.assertTrue(room.route_c.checkpoint_reached)
                state.health.current = CLAW_DAMAGE
                state.step = "enter_b1"
                return _press(pico.SDLK_e)
            if state.step == "enter_b1":
                if room.room == "route_c":
                    self.assertIsNotNone(travel.anchor)
                    state.direction = -1
                else:
                    self.assertEqual(room.room, "b1")
                    self.assertIs(stage.player, player)
                    self.assertIs(stage.health, state.health)
                    self.assertEqual(stage.health.current, CLAW_DAMAGE)
                    self.assertEqual(stage.state, "waiting")
                    self.assertIsNone(travel.anchor)
                    state.spawn_x = player.x
                    state.step = "walk_from_anchor"
                    return _press(pico.SDLK_e)
            elif state.step == "walk_from_anchor":
                self.assertAlmostEqual(travel.anchor.x, state.spawn_x)
                if state.spawn_x - player.x > 80:
                    state.departure_x = player.x
                    state.step = "return_to_mark"
                    return _press(pico.SDLK_e)
                state.direction = -1
            elif state.step == "return_to_mark":
                self.assertAlmostEqual(player.x, state.spawn_x)
                self.assertIsNone(travel.anchor)
                self.assertEqual(len(travel.marks), 1)
                state.step = "inspect"
                return _press(pico.SDLK_q)
            elif state.step == "inspect":
                if hasattr(state, "departure_x"):
                    self.assertAlmostEqual(player.x, state.departure_x)
                    del state.departure_x
                if stage.can_inspect:
                    state.step = "wait_for_claw"
                    return _press(pico.SDLK_e)
                state.direction = -1
            elif state.step == "wait_for_claw":
                self.assertIsNone(travel.anchor)
                self.assertFalse(travel.marks)
                if stage.state == "claw":
                    self.assertEqual(stage.gate_progress, 1)
                    self.assertTrue(player.recover_at(stage.claw_center, 0, 0))
                    state.step = "take_hit"
            elif state.step == "take_hit" and stage.state == "defeated":
                self.assertEqual(stage.health.current, 0)
                self.assertIs(stage.health, state.health)
                self.assertGreater(stage.health.hit_at, 500)
                state.hit_at = stage.health.hit_at
                state.step = "wait_for_checkpoint"
            elif state.step == "wait_for_checkpoint" and room.room == "route_c":
                self.assertGreaterEqual(state.now - state.hit_at, RESTART_DELAY)
                self.assertLess(state.now - state.hit_at, RESTART_DELAY + .15)
                self.assertEqual((player.x, player.y), CHECKPOINT[:2])
                self.assertEqual(state.health.current, MAX_HEALTH)
                self.assertTrue(room.has_relic and room.route_c.checkpoint_reached)
                self.assertFalse(room.b1_cleared)
                self.assertIsNone(travel.anchor)
                state.step = "reenter_after_death"
            elif state.step == "reenter_after_death":
                if room.room == "route_c":
                    state.direction = -1
                else:
                    self.assertEqual(stage.state, "waiting")
                    self.assertEqual(stage.phase, "first")
                    self.assertEqual(stage.boss_hp, BOSS_MAX_HP)
                    self.assertEqual(stage.gate_progress, 0)
                    self.assertIsNone(stage.rock_hit_at)
                    self.assertIs(stage.health, state.health)
                    state.step = "inspect_retry"
            elif state.step == "inspect_retry":
                if stage.can_inspect:
                    state.step = "first_claw"
                    return _press(pico.SDLK_e)
                state.direction = -1
            elif state.step == "first_claw" and stage.state == "claw":
                stage.boss_hp = BOSS_HALF_HP
                self.assertTrue(player.recover_at(500, 0, 0))
                state.step = "mount_rail"
            elif state.step == "mount_rail" and stage.state == "hidden":
                rail_x, _ = stage.rails.landings[1]
                self.assertTrue(player.recover_at(rail_x + 50, 0, 0))
                player.facing = -1
                self.assertEqual(stage.rails.prompt(player), "mount")
                state.step = "send_carriage"
                return _press(pico.SDLK_e)
            elif state.step == "send_carriage":
                self.assertIs(stage.rails.active, stage.rails.carriages[1])
                self.assertIsNone(travel.anchor)
                self.assertEqual(stage.rails.prompt(player), "send")
                state.step = "ride_carriage"
                return _press(pico.SDLK_x)
            elif state.step == "ride_carriage" and stage.rails.prompt(player) == "travel":
                state.rail_departure = player.x, player.y
                state.step = "cut_rock"
                return _press(pico.SDLK_e)
            elif state.step == "cut_rock":
                self.assertEqual((player.x, player.y), stage.rails.landings[1])
                self.assertIsNone(stage.rails.active)
                self.assertIsNone(travel.anchor)
                self.assertEqual(travel.marks[-1].pose[:2], state.rail_departure)
                self.assertTrue(travel.marks[-1].can_return(state.now))
                # The independent encounter tests already walk and jump onto both inner ledges.
                self.assertTrue(player.recover_at(1225 * SCALE, (GROUND - LEDGES[-2][2]) * SCALE, 0))
                player.facing = -1
                state.step = "return_to_floor"
                return _press(pico.SDLK_x)
            elif state.step == "return_to_floor" and stage.state == "wait_floor":
                self.assertIsNotNone(stage.rock_hit_at)
                self.assertTrue(player.recover_at(stage.boss_x + 145, 0, 0))
                state.step = "last_counter"
            elif (state.step == "last_counter" and stage.phase == "second" and stage.state == "jump"
                  and not stage.jump_relaunch and stage.age >= stage.jump.impact):
                self.assertIs(stage.combat.attack, Attack.DOUBLE_JUMP)
                stage.boss_hp = player.attack_power
                self.assertTrue(player.recover_at(stage.boss_x - 142, 0, 0))
                player.facing = 1
                state.step = "open_gate"
                return _press(pico.SDLK_x)
            elif state.step == "open_gate" and stage.state == "dying":
                self.assertFalse(room.b1_cleared)
                self.assertFalse(stage.can_leave)
                self.assertFalse(stage.accepts_player_input)
            elif state.step == "open_gate" and stage.state == "victory":
                self.assertEqual(stage.boss_hp, 0)
                self.assertTrue(room.b1_cleared)
                if stage.gate_progress == 0:
                    state.step = "leave_b1"
            elif state.step == "leave_b1":
                if room.room == "b1":
                    state.direction = 1
                else:
                    self.assertEqual(room.room, "route_c")
                    self.assertEqual((player.x, player.y), BOSS_RETURN[:2])
                    self.assertTrue(room.b1_cleared)
                    state.step = "reenter_cleared_b1"
            elif state.step == "reenter_cleared_b1":
                if room.room == "route_c":
                    state.direction = -1
                else:
                    self.assertTrue(room.b1_cleared)
                    self.assertEqual(stage.state, "victory")
                    self.assertEqual(stage.boss_hp, 0)
                    self.assertEqual(stage.gate_progress, 0)
                    state.step = "done"
                    return [pico.Event(pico.SDL_QUIT)]
            return []

        with patch.object(LowerCaves, "start_after_relic", new=start_at_lantern), \
                patch.object(LowerCaves, "draw"), \
                patch.object(B1EncounterStage, "draw", new=render_boss), \
                patch.object(main, "Health", side_effect=create_health), \
                patch.object(main, "RelicTravel", return_value=travel), \
                patch.object(main, "poll_events", side_effect=events), \
                patch.object(main, "read_movement", side_effect=lambda: (state.direction, True, False)), \
                patch.object(main, "perf_counter", side_effect=time_now), \
                patch.object(main, "sleep"), \
                patch.object(pico, "SDL_GetKeyboardFocus", return_value=True), \
                patch.object(pico, "update_canvas"):
            main.run_opening_cave(False, after_relic=True)
        self.assertEqual(state.step, "done")

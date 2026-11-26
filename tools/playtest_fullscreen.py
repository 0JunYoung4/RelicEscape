"""Record an actual fullscreen playtest while the operator uses the normal game loop."""

from argparse import ArgumentParser
from contextlib import ExitStack
from ctypes import byref, c_int
from datetime import datetime
import json
import os
from pathlib import Path
import platform
import statistics
import sys
from time import perf_counter
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.pop("SDL_VIDEODRIVER", None)
os.environ.pop("SDL_RENDER_DRIVER", None)

from pico2d import pico2d as pico
import main
from health import Health
from lower_caves import COMBAT_CENTER_X, LowerCaves
from lower_route_a import GROUND_Y as A_GROUND
from lower_route_connection import A_ORIGIN


def summary(rows, key):
    values = sorted(row[key] for row in rows if key in row)
    if not values:
        return {"frames": 0}
    def percentile(number):
        return values[max(0, (number * len(values) + 99) // 100 - 1)]
    return {"frames": len(values), "p50_ms": statistics.median(values),
            "p95_ms": percentile(95), "p99_ms": percentile(99), "max_ms": values[-1],
            **{f"over_{threshold:g}_ms": sum(value > threshold for value in values)
               for threshold in (20, 25, 33.3, 50)}}


def display_info():
    info = pico.SDL_RendererInfo()
    pico.SDL_GetRendererInfo(pico.renderer, byref(info))
    width, height = c_int(), c_int()
    pico.SDL_GetRendererOutputSize(pico.renderer, byref(width), byref(height))
    flags = pico.SDL_GetWindowFlags(pico.window)
    return {"renderer": info.name.decode(), "renderer_flags": info.flags,
            "accelerated": bool(info.flags & pico.SDL_RENDERER_ACCELERATED),
            "vsync": bool(info.flags & pico.SDL_RENDERER_PRESENTVSYNC),
            "window_flags": flags, "fullscreen": bool(flags & pico.SDL_WINDOW_FULLSCREEN),
            "logical_size": [main.SCREEN_WIDTH, main.SCREEN_HEIGHT],
            "output_size": [width.value, height.value]}


class Recorder:
    def __init__(self):
        self.started = perf_counter()
        self.current = None
        self.frames, self.markers, self.loads = [], [], []
        self.recording, self.segment = False, 0
        self.warm_until = self.started
        self.latch_direction, self.latch_until = 0, 0.0
        self.live = {}
        self.test_stage = "combat"
        self.initial_setup_ms = None

    def marker(self, kind, **details):
        self.markers.append({"kind": kind, "time": perf_counter() - self.started,
                             "segment": self.segment, "test_stage": self.test_stage, **details})

    def cancel_latch(self, reason):
        if self.latch_direction:
            self.marker("movement_override_end", direction=self.latch_direction, reason=reason)
        self.latch_direction, self.latch_until = 0, 0.0

    def switch_scene(self, scene):
        lower, player, camera = (self.live[name] for name in ("lower", "player", "camera"))
        if lower is None:
            return
        self.cancel_latch("scene_change")
        started = perf_counter()
        fresh = LowerCaves(lower.cave)
        fresh.room, fresh.has_relic = scene, True
        fresh.enter(player, camera)
        if scene == "combat":
            player.recover_at(COMBAT_CENTER_X, 0, 0)
        elif scene == "route_a":
            player.recover_at(A_ORIGIN[0] + 2500, A_ORIGIN[1] + A_GROUND, 0)
        fresh.follow_camera(player, camera)
        # Preserve main's object references while giving each shortcut a fresh normal room.
        lower.__dict__.clear()
        lower.__dict__.update(fresh.__dict__)
        replacement_health = Health((player.x, player.y, player.crouch_time))
        self.live["health"].__dict__.clear()
        self.live["health"].__dict__.update(replacement_health.__dict__)
        self.live["travel"].reset()
        finished = perf_counter()
        self.test_stage = scene
        self.warm_until = finished + 1.0
        self.recording = False
        self.loads.append({"scene": scene, "load_ms": (finished - started) * 1000,
                           "time": started - self.started, "display": display_info()})
        self.marker("scene_loaded", scene=scene)
        print(f"Loaded {scene}. F6 starts the measured segment.", flush=True)

    def begin(self, caller):
        frame_start = caller.f_locals["frame_start"]
        if self.current is not None and self.current.get("sleep_completed"):
            self.current["interval_ms"] = (frame_start - self.current["frame_start"]) * 1000
            self.frames.append(self.current)
        self.live = {name: caller.f_locals.get(name) for name in ("lower", "player", "camera", "health", "travel")}
        if self.initial_setup_ms is None:
            self.initial_setup_ms = (frame_start - self.started) * 1000
            self.warm_until = frame_start + 1.0
            self.live["player"].recover_at(COMBAT_CENTER_X, 0, 0)
            self.live["lower"].follow_camera(self.live["player"], self.live["camera"])
        self.current = {"frame_start": frame_start, "time": frame_start - self.started,
                        "segment": self.segment, "recording": self.recording,
                        "pressed_keys": [], "movement_source": "none",
                        "synthetic_direction_override": False,
                        "focus": bool(pico.SDL_GetKeyboardFocus()),
                        "window_flags": pico.SDL_GetWindowFlags(pico.window)}

    def poll(self, original, caller):
        started = perf_counter()
        self.begin(caller)
        events = original()
        returned = []
        shortcuts = {pico.SDLK_F2: "combat", pico.SDLK_F3: "route_a",
                     pico.SDLK_F4: "route_b", pico.SDLK_F5: "route_c"}
        for event in events:
            if event.type != pico.SDL_KEYDOWN:
                returned.append(event)
                continue
            self.current["pressed_keys"].append(event.key)
            if event.key in shortcuts:
                self.switch_scene(shortcuts[event.key])
            elif event.key == pico.SDLK_F6:
                self.recording = not self.recording
                if self.recording:
                    self.segment += 1
                self.marker("recording_started" if self.recording else "recording_stopped")
                print(f"Segment {self.segment} recording {self.recording}", flush=True)
            elif event.key == pico.SDLK_F7:
                self.marker("operator_reported_hitch")
            elif event.key in (pico.SDLK_F9, pico.SDLK_F10):
                self.cancel_latch("replaced")
                self.latch_direction = -1 if event.key == pico.SDLK_F9 else 1
                self.latch_until = perf_counter() + 1.0
                self.marker("movement_override_start", direction=self.latch_direction,
                            seconds=1.0, running=False, synthetic_direction_override=True)
            elif event.key == pico.SDLK_F8:
                self.marker("operator_finished")
                returned.append(pico.Event(pico.SDL_QUIT))
            else:
                returned.append(event)
        self.current["segment"], self.current["recording"] = self.segment, self.recording
        self.current["poll_ms"] = (perf_counter() - started) * 1000
        self.current["poll_finished"] = perf_counter()
        return returned

    def movement(self, original):
        direction, running, crouching = original()
        if self.latch_direction and perf_counter() >= self.latch_until:
            self.cancel_latch("expired")
        if direction:
            self.current["movement_source"] = "native_direction"
        elif self.latch_direction and self.current["focus"]:
            direction, running = self.latch_direction, False
            self.current["movement_source"] = "shortcut_latch"
            self.current["synthetic_direction_override"] = True
        self.current["direction"], self.current["running"] = direction, running
        held = pico.SDL_GetKeyboardState(None)
        self.current["held"] = [name for name, scan in (
            ("A", pico.SDL_SCANCODE_A), ("D", pico.SDL_SCANCODE_D),
            ("Left", pico.SDL_SCANCODE_LEFT), ("Right", pico.SDL_SCANCODE_RIGHT),
            ("Space", pico.SDL_SCANCODE_SPACE), ("X", pico.SDL_SCANCODE_X),
            ("Shift", pico.SDL_SCANCODE_LSHIFT), ("C", pico.SDL_SCANCODE_C))
            if held[scan]]
        return direction, running, crouching

    def draw(self, original, lower, camera, caller):
        started = perf_counter()
        if self.live.get("lower") is not lower:
            self.cancel_latch("normal_room_restart")
            self.recording = False
            self.warm_until = started + 1.0
            self.marker("normal_room_recreated", room=lower.room,
                        update_to_render_ms=(started - self.current["poll_finished"]) * 1000)
            self.current["recording"] = False
            print("Normal checkpoint restart. F6 resumes recording after loading.", flush=True)
        self.live.update({name: caller.f_locals[name]
                          for name in ("lower", "player", "camera", "health", "travel")
                          if name in caller.f_locals})
        if self.current is not None:
            self.current["render_started"] = started
            self.current["update_before_render_ms"] = (started - self.current["poll_finished"]) * 1000
        result = original(lower, camera)
        if self.current is not None:
            self.current["lower_draw_ms"] = (perf_counter() - started) * 1000
        return result

    def present(self, original):
        started = perf_counter()
        result = original()
        finished = perf_counter()
        if self.current is not None:
            self.current["present_ms"] = (finished - started) * 1000
            if "render_started" in self.current:
                self.current["render_before_present_ms"] = (started - self.current["render_started"]) * 1000
        return result

    def sleep(self, original, seconds):
        started = perf_counter()
        row = self.current
        if row is None:
            return original(seconds)
        row["work_ms"] = (started - row["frame_start"]) * 1000
        row["requested_sleep_ms"] = seconds * 1000
        result = original(seconds)
        finished = perf_counter()
        row["actual_sleep_ms"] = (finished - started) * 1000
        row["sleep_overshoot_ms"] = row["actual_sleep_ms"] - row["requested_sleep_ms"]
        row["sleep_completed"] = True
        player, lower, camera = (self.live[name] for name in ("player", "lower", "camera"))
        row.update({"room": lower.room if lower is not None else "opening",
                    "test_stage": self.test_stage, "x": player.x, "y": player.y,
                    "grounded": player.grounded, "player_state": player.state,
                    "health": self.live["health"].current,
                    "camera": [camera.x, camera.y, camera.zoom],
                    "focus_after": bool(pico.SDL_GetKeyboardFocus()),
                    "settling_or_loading": finished < self.warm_until})
        row["fullscreen"] = bool(row["window_flags"] & pico.SDL_WINDOW_FULLSCREEN)
        row["eligible"] = row["recording"] and row["focus"] and row["focus_after"] and row["fullscreen"] and not row["settling_or_loading"]
        row["activity"] = bool(row.get("direction") or not player.grounded or row["held"] or row["pressed_keys"])
        return result

    def save(self, output, display):
        output.mkdir(parents=True, exist_ok=True)
        accepted = [row for row in self.frames if row["eligible"]]
        active = [row for row in accepted if row["activity"]]
        groups = {}
        for room in sorted({row["room"] for row in accepted}):
            rows = [row for row in accepted if row["room"] == room]
            movement_rows = [row for row in rows if row["activity"]]
            groups[room] = {"recorded": summary(rows, "interval_ms"),
                            "active": summary(movement_rows, "interval_ms"),
                            "work": summary(rows, "work_ms"),
                            "present": summary(rows, "present_ms"),
                            "actual_sleep": summary(rows, "actual_sleep_ms"),
                            "sleep_overshoot": summary(rows, "sleep_overshoot_ms"),
                            "shortcut_override_frames": sum(row["synthetic_direction_override"] for row in rows),
                            "airborne_frames": sum(not row["grounded"] for row in rows),
                            "x_range": [min(row["x"] for row in rows), max(row["x"] for row in rows)],
                            "y_range": [min(row["y"] for row in rows), max(row["y"] for row in rows)]}
        hitches = []
        for row in accepted:
            if row["interval_ms"] > 25:
                cause = "present" if row.get("present_ms", 0) > 16.7 else (
                    "work" if row["work_ms"] > 16.7 else "sleep_or_scheduling")
                hitches.append({**row, "timing_category": cause})
        report = {"display": display, "python": sys.version, "platform": platform.platform(),
                  "initial_setup_ms": self.initial_setup_ms,
                  "captured_frames": len(self.frames), "accepted_recorded_frames": len(accepted),
                  "active_recorded_frames": len(active), "interval": summary(accepted, "interval_ms"),
                  "active_interval": summary(active, "interval_ms"), "by_room": groups,
                  "scene_loads": self.loads, "markers": self.markers, "hitches_over_25_ms": hitches,
                  "method": "Actual main.run_opening_cave 60fps loop, SDL fullscreen, normal keyboard events, physics, enemies, render and sleep.",
                  "input_note": "F9/F10 trigger a 1.0 second runtime walking latch while focused. Native direction keys take precedence. This is not a physical held direction key.",
                  "exclusions": "Only F6-recorded, focused, fullscreen frames outside initial/scene-load settling enter statistics. Captures and output writes are outside the gameplay loop.",
                  "measurement_note": "CPU frame intervals and present wall-clock time. This does not isolate GPU completion or prove every hitch perceptible.",
                  "wall_clock_saved": datetime.now().astimezone().isoformat()}
        (output / "frames.json").write_text(json.dumps(self.frames, indent=2), encoding="utf-8")
        (output / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        print("Saved fullscreen playtest", output)
        print("Accepted frames", len(accepted), "active frames", len(active))


def run(output):
    recorder = Recorder()
    original_poll, original_sleep = main.poll_events, main.sleep
    original_movement, original_draw = main.read_movement, LowerCaves.draw
    original_present = pico.update_canvas
    pico.SDL_SetHint(pico.SDL_HINT_RENDER_SCALE_QUALITY, b"0")
    pico.open_canvas(main.SCREEN_WIDTH, main.SCREEN_HEIGHT)
    try:
        pico.SDL_SetWindowTitle(pico.window, b"RelicEscape Fullscreen Playtest | F2-F5 scenes, F6 record, F8 finish")
        fullscreen = main.configure_display()
        display = display_info()
        print("F2 combat | F3 A | F4 B | F5 C | F6 record on/off | F7 hitch | F8 save and exit", flush=True)
        print("F9 walk left 1.0s | F10 walk right 1.0s | Space jump | X attack | E relic | Esc normal exit", flush=True)
        print("Scene shortcuts stop recording. Wait one second after loading, then press F6.", flush=True)
        with ExitStack() as stack:
            stack.enter_context(patch.object(main, "poll_events",
                lambda: recorder.poll(original_poll, sys._getframe(1))))
            stack.enter_context(patch.object(main, "read_movement",
                lambda: recorder.movement(original_movement)))
            stack.enter_context(patch.object(main, "sleep",
                lambda seconds: recorder.sleep(original_sleep, seconds)))
            stack.enter_context(patch.object(LowerCaves, "draw",
                lambda lower, camera: recorder.draw(original_draw, lower, camera, sys._getframe(1))))
            stack.enter_context(patch.object(pico, "update_canvas",
                lambda: recorder.present(original_present)))
            main.run_opening_cave(fullscreen, start_in_combat=True)
        recorder.cancel_latch("exit")
    except BaseException as error:
        recorder.marker("harness_exception", detail=str(error))
        raise
    finally:
        if "display" in locals():
            recorder.save(output.resolve(), display)
        pico.close_canvas()


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / ".cache/fullscreen-playtest")
    run(parser.parse_args().output_dir)

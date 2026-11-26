"""Benchmark deterministic gameplay update and SDL rendering without sleep or vsync."""

from argparse import ArgumentParser, SUPPRESS
import cProfile
from ctypes import byref, c_int, c_ubyte
import gc
import hashlib
import io
import json
from math import sin, tau
import os
from pathlib import Path
import platform
import pstats
import statistics
import subprocess
import sys
from time import perf_counter
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[1]
SCENES = ("opening", "combat", "a", "b", "c")
FRAME_BUDGET_MS = 1000 / 60


def distribution(values):
    ordered = sorted(values)
    return {
        "median_ms": statistics.median(ordered),
        "p95_ms": ordered[max(0, (95 * len(ordered) + 99) // 100 - 1)],
        "max_ms": max(ordered),
        "over_16_67_ms": sum(value > FRAME_BUDGET_MS for value in ordered),
        "frames": len(ordered),
    }


def worker(arguments):
    """Each backend gets its own SDL process and renderer lifetime."""
    os.environ["SDL_VIDEODRIVER"] = "dummy" if arguments.worker == "software" else "windows"
    os.environ["SDL_RENDER_DRIVER"] = "software" if arguments.worker == "software" else "direct3d11"
    os.environ["SDL_AUDIODRIVER"] = "dummy"
    sys.path.insert(0, str(ROOT))
    from PIL import Image
    from pico2d import pico2d as pico
    import main
    import moss_art
    import opening_cave
    from health import Health
    from lower_caves import COMBAT_CENTER_X, LowerCaves
    from lower_route_a import GROUND_Y as A_GROUND, LOWER_DOCK
    from lower_route_b_layout import SHIELD_LEDGE
    from lower_route_c import CHECKPOINT
    from lower_route_connection import A_ORIGIN
    from player import Player

    output = arguments.output_dir / arguments.worker
    output.mkdir(parents=True, exist_ok=True)
    simulation = SimpleNamespace(now=0.0)
    moss_art.perf_counter = lambda: simulation.now
    original_create_window = pico.SDL_CreateWindow

    def create_hidden_window(title, x, y, width, height, flags):
        if arguments.worker == "native" and arguments.native_output == "desktop":
            mode = pico.SDL_DisplayMode()
            if pico.SDL_GetCurrentDisplayMode(0, byref(mode)) == 0:
                width, height = mode.w, mode.h
        return original_create_window(title, x, y, width, height,
                                      (flags & ~pico.SDL_WINDOW_SHOWN) | pico.SDL_WINDOW_HIDDEN)

    pico.SDL_CreateWindow = create_hidden_window
    pico.open_canvas(main.SCREEN_WIDTH, main.SCREEN_HEIGHT, sync=False)
    if not pico.renderer:
        raise RuntimeError("SDL did not create a renderer")
    pico.SDL_HideWindow(pico.window)
    pico.SDL_RenderSetLogicalSize(pico.renderer, main.SCREEN_WIDTH, main.SCREEN_HEIGHT)
    if hasattr(pico, "SDL_RenderSetVSync"):
        pico.SDL_RenderSetVSync(pico.renderer, 0)
    info = pico.SDL_RendererInfo()
    pico.SDL_GetRendererInfo(pico.renderer, byref(info))
    output_w, output_h, window_w, window_h = c_int(), c_int(), c_int(), c_int()
    pico.SDL_GetRendererOutputSize(pico.renderer, byref(output_w), byref(output_h))
    pico.SDL_GetWindowSize(pico.window, byref(window_w), byref(window_h))
    display = pico.SDL_DisplayMode()
    display_ok = pico.SDL_GetCurrentDisplayMode(0, byref(display)) == 0
    metadata = {
        "backend": arguments.worker, "renderer": info.name.decode(),
        "renderer_flags": info.flags,
        "accelerated": bool(info.flags & pico.SDL_RENDERER_ACCELERATED),
        "vsync": bool(info.flags & pico.SDL_RENDERER_PRESENTVSYNC),
        "window_hidden": bool(pico.SDL_GetWindowFlags(pico.window) & pico.SDL_WINDOW_HIDDEN),
        "logical_size": [main.SCREEN_WIDTH, main.SCREEN_HEIGHT],
        "window_size": [window_w.value, window_h.value],
        "renderer_output_size": [output_w.value, output_h.value],
        "driver_display_mode": [display.w, display.h, display.refresh_rate] if display_ok else None,
        "display_mode_note": "Native desktop mode" if arguments.worker == "native" else "Dummy driver's virtual mode",
        "python": sys.version, "platform": platform.platform(),
        "simulation_dt_seconds": 1 / 60, "warmup_frames": arguments.warmup,
        "measured_frames": arguments.frames, "profile_frames_per_case": arguments.profile_frames,
        "timing_note": "CPU elapsed update, draw submission, and present. Hidden accelerated present does not measure full GPU completion.",
        "excluded": ["SDL setup", "asset loading", "sleep", "vsync wait", "screenshot readback", "PNG encoding", "cProfile pass"],
        "scope_note": "Fixed gameplay scenes, idle player update and deterministic moving camera. No input-event polling or operating-system compositor benchmark.",
    }
    if metadata["vsync"]:
        raise RuntimeError("Renderer still advertises present vsync")
    if arguments.worker == "native" and not metadata["accelerated"]:
        raise RuntimeError("Native accelerated renderer is unavailable")
    pico.SDL_ClearError()
    if arguments.events_only:
        functions = {"legacy_pico_get_events": pico.get_events}
        if hasattr(main, "poll_events"):
            functions["app_poll_events"] = main.poll_events
        events = {}
        for name, function in functions.items():
            for _ in range(10):
                function()
            durations, delivered = [], 0
            for _ in range(arguments.event_frames):
                started = perf_counter()
                received = function()
                durations.append((perf_counter() - started) * 1000)
                delivered += len(received)
            events[name] = {"timings": distribution(durations), "samples_ms": durations,
                            "delivered_events": delivered}
            print(f"{arguments.worker} {name} median {statistics.median(durations):.2f} ms", flush=True)
        data = {"metadata": metadata, "events": events,
                "note": "Separate event polling benchmark, including each function's own delay and window-title behavior."}
        (output / "event-results.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
        pico.close_canvas()
        return

    class Scene:
        def __init__(self, name, moving):
            self.name, self.moving, self.index = name, moving, 0
            simulation.now = 0.0
            self.lower = None
            self.cave = opening_cave.OpeningCave(main.SCREEN_WIDTH, main.SCREEN_HEIGHT) if name == "opening" else None
            self.player = Player(0, 0, 12000)
            self.camera = main.Camera(main.SCREEN_WIDTH, 12000, zoom=.5)
            if name == "opening":
                self.player.world_width = self.camera.world_width = opening_cave.WORLD_WIDTH
                self.player.terrain, self.player.ground_y = opening_cave.TERRAIN, opening_cave.GROUND_Y
                self.player.recover_at(2600, opening_cave.GROUND_Y, 0)
                self.camera.follow(self.player.x)
                self.camera.y = opening_cave.GROUND_Y - main.CAVE_FLOOR_SCREEN_Y / self.camera.zoom
            else:
                cave = SimpleNamespace(width=main.SCREEN_WIDTH, height=main.SCREEN_HEIGHT,
                                       shaft=SimpleNamespace(w=4096))
                self.lower = LowerCaves(cave)
                self.lower.room = "combat" if name == "combat" else "route_" + name
                self.lower.has_relic = True
                self.lower.enter(self.player, self.camera, seal_open=True)
                self.lower.art.started = 0.0
                if name == "combat":
                    self.player.recover_at(COMBAT_CENTER_X, 0, 0)
                    self.lower.combat_phase, self.lower.entrance_progress = "golems", 1.0
                    for bug in self.lower.combat_pillbugs:
                        bug.hp = 0
                elif name == "a":
                    self.lower.route_a.powered = True
                    self.player.recover_at(A_ORIGIN[0] + LOWER_DOCK[0] + 350,
                                           A_ORIGIN[1] + A_GROUND, 0)
                elif name == "b":
                    self.player.recover_at(2500, SHIELD_LEDGE[3], 0)
                else:
                    self.player.recover_at(*CHECKPOINT)
                self.lower.follow_camera(self.player, self.camera)
            self.health = Health((self.player.x, self.player.y, 0))
            self.base_x, self.base_y = self.camera.x, self.camera.y

        def update(self):
            simulation.now = self.index / 60
            if self.lower is None:
                self.player.update(0, False, 1 / 60)
                self.camera.follow(self.player.x)
            else:
                self.lower.update(self.player, self.camera, 1 / 60, interact=False, direction=0,
                                  running=False, jump_pressed=False, jump_held=False,
                                  crouching=False, attack_pressed=False)
                self.lower.update_relic_seal(self.player, simulation.now)
                self.lower.update_enemies(self.player, 1 / 60)
                self.lower.update_projectiles(self.player, self.health, 1 / 60, simulation.now)
                self.lower.update_effects(1 / 60, self.player)
            if self.moving:
                phase = self.index * tau / 120
                self.camera.x = self.camera._clamp_x(self.base_x + sin(phase) * 260)
                self.camera.y = self.base_y + sin(phase * 2) * 100
            self.index += 1

        def draw(self):
            pico.clear_canvas()
            if self.lower is None:
                self.cave.draw(self.camera)
                main.shade_stone_depth(0, main.SCREEN_WIDTH,
                                      main.SCREEN_HEIGHT - main.CAVE_FLOOR_SCREEN_Y, main.SCREEN_HEIGHT)
                self.player.draw(self.camera)
                self.cave.draw_foreground(self.camera)
            else:
                self.lower.draw(self.camera)
                if self.name == "combat":
                    self.lower.draw_combat_exit(self.camera)
                self.player.draw(self.camera)
                self.lower.draw_hit_impacts(self.camera)
                self.lower.draw_foreground(self.camera)
            self.health.draw_hud(main.SCREEN_HEIGHT, simulation.now)

    profile = cProfile.Profile()
    cases = []
    for name in SCENES:
        for moving in (False, True):
            scene = Scene(name, moving)
            for _ in range(arguments.warmup):
                scene.update()
                scene.draw()
                pico.SDL_RenderPresent(pico.renderer)
            pico.SDL_ClearError()
            timings = {key: [] for key in ("update", "draw", "present", "total")}
            for _ in range(arguments.frames):
                start = perf_counter()
                scene.update()
                updated = perf_counter()
                scene.draw()
                drawn = perf_counter()
                pico.SDL_RenderPresent(pico.renderer)
                finished = perf_counter()
                for key, duration in (("update", updated - start), ("draw", drawn - updated),
                                      ("present", finished - drawn), ("total", finished - start)):
                    timings[key].append(duration * 1000)
            error = pico.SDL_GetError()
            measured_error = error.decode() if error else None
            pico.SDL_ClearError()
            tag = name + ("-moving" if moving else "-static")
            # Re-render exactly the final measured state. Readback and encoding stay outside timings.
            scene.draw()
            pixels = (c_ubyte * (output_w.value * output_h.value * 4))()
            if pico.SDL_RenderReadPixels(pico.renderer, None, pico.SDL_PIXELFORMAT_RGBA32,
                                        pixels, output_w.value * 4) != 0:
                raise RuntimeError(pico.SDL_GetError())
            screenshot = Image.frombytes("RGBA", (output_w.value, output_h.value), bytes(pixels))
            screenshot.save(output / f"{tag}.png")
            screenshot_hash = hashlib.sha256(screenshot.tobytes()).hexdigest()
            case = {"name": tag, "scene": name, "moving_camera": moving,
                    "sdl_error_after_measured_batch": measured_error,
                    "camera": {"x": scene.camera.x, "y": scene.camera.y, "zoom": scene.camera.zoom},
                    "simulation_time": simulation.now, "screenshot_pixel_sha256": screenshot_hash,
                    "timings": {key: distribution(values) for key, values in timings.items()},
                    "samples_ms": timings}
            cases.append(case)
            print(f"{arguments.worker} {tag} median {case['timings']['total']['median_ms']:.2f} ms", flush=True)
            profile.enable()
            for _ in range(arguments.profile_frames):
                scene.update()
                scene.draw()
                pico.SDL_RenderPresent(pico.renderer)
            profile.disable()
            del scene
            gc.collect()
    profile.dump_stats(output / "gameplay.prof")
    stream = io.StringIO()
    pstats.Stats(profile, stream=stream).strip_dirs().sort_stats("cumulative").print_stats(35)
    (output / "hotspots.txt").write_text(stream.getvalue(), encoding="utf-8")
    (output / "results.json").write_text(json.dumps({"metadata": metadata, "cases": cases}, indent=2), encoding="utf-8")
    pico.close_canvas()


def run(arguments):
    arguments.output_dir = arguments.output_dir.resolve()
    arguments.output_dir.mkdir(parents=True, exist_ok=True)
    if arguments.worker:
        try:
            worker(arguments)
        except Exception as error:
            failure = {"available": False, "error": str(error), "backend": arguments.worker}
            target = arguments.output_dir / arguments.worker
            target.mkdir(parents=True, exist_ok=True)
            failure_name = "events-unavailable.json" if arguments.events_only else "unavailable.json"
            (target / failure_name).write_text(json.dumps(failure, indent=2), encoding="utf-8")
            raise
        return
    report = {}
    for backend in arguments.backends:
        command = [sys.executable, "-B", str(Path(__file__).resolve()),
                   "--worker", backend, "--output-dir", str(arguments.output_dir),
                   "--frames", str(arguments.frames), "--warmup", str(arguments.warmup),
                   "--profile-frames", str(arguments.profile_frames),
                   "--native-output", arguments.native_output,
                   "--event-frames", str(arguments.event_frames)]
        if arguments.events_only:
            command.append("--events-only")
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
        log_name = f"{backend}-events.log" if arguments.events_only else f"{backend}-worker.log"
        (arguments.output_dir / log_name).write_text(result.stdout + result.stderr, encoding="utf-8")
        print(result.stdout.strip())
        path = arguments.output_dir / backend / ("event-results.json" if arguments.events_only else "results.json")
        report[backend] = json.loads(path.read_text(encoding="utf-8")) if result.returncode == 0 else {
            "available": False, "error": result.stderr[-2000:]}
        if backend == "software" and result.returncode:
            print(result.stderr, file=sys.stderr)
            raise RuntimeError("Required software baseline did not complete")
    summary_name = "event-summary.json" if arguments.events_only else "summary.json"
    (arguments.output_dir / summary_name).write_text(json.dumps(report, indent=2), encoding="utf-8")
    if arguments.compare and not arguments.events_only:
        before = json.loads((arguments.compare / "summary.json").read_text(encoding="utf-8"))
        comparison = []
        for backend, data in report.items():
            old = {case["name"]: case for case in before.get(backend, {}).get("cases", [])}
            for case in data.get("cases", []):
                if case["name"] in old:
                    previous = old[case["name"]]
                    first = previous["timings"]["total"]["median_ms"]
                    latest = case["timings"]["total"]["median_ms"]
                    comparison.append({"backend": backend, "scene": case["name"],
                                       "before_median_ms": first, "after_median_ms": latest,
                                       "median_change_percent": (latest / first - 1) * 100,
                                       "screenshot_pixels_equal": case["screenshot_pixel_sha256"] == previous["screenshot_pixel_sha256"]})
        (arguments.output_dir / "comparison.json").write_text(json.dumps(comparison, indent=2), encoding="utf-8")
    print("Saved gameplay profile", arguments.output_dir)


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / ".cache/perf")
    parser.add_argument("--frames", type=int, default=60)
    parser.add_argument("--warmup", type=int, default=10)
    parser.add_argument("--profile-frames", type=int, default=8)
    parser.add_argument("--backends", nargs="+", choices=("software", "native"), default=["software", "native"])
    parser.add_argument("--native-output", choices=("desktop", "logical"), default="desktop")
    parser.add_argument("--events-only", action="store_true")
    parser.add_argument("--event-frames", type=int, default=240)
    parser.add_argument("--compare", type=Path)
    parser.add_argument("--worker", choices=("software", "native"), help=SUPPRESS)
    run(parser.parse_args())

"""Render and check B's wall art through the existing game camera and movement."""

from argparse import ArgumentParser
from dataclasses import asdict, is_dataclass
import gc
import json
import os
from pathlib import Path
import sys
from types import SimpleNamespace

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("SDL_RENDER_DRIVER", "software")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from PIL import Image, ImageDraw
from pico2d import pico2d as pico

import lower_route_b as route_module
import lower_route_b_layout as layout
import lower_route_connection as connection
from lower_caves import LowerCaves
from lower_route_c import FLOOR as C_FLOOR, TERRAIN as C_TERRAIN
from main import Camera, SCREEN_HEIGHT, SCREEN_WIDTH
from player import Player
from rail import RAIL_TRAVEL_SPEED
from route_camera import B_CAMERA_HEADROOM
from tools.preview_lower_route_a import read_render


DEFAULT_OUTPUT = ROOT / ".cache/b-wall-review"
LOCAL_BASELINE = DEFAULT_OUTPUT / "layout-before.json"
TRACKED_BASELINE = ROOT / "assets/terrain/lower-route-b-wall-v1/layout-baseline.json"


def serializable(value):
    if is_dataclass(value):
        return serializable(asdict(value))
    if isinstance(value, dict):
        return {name: serializable(item) for name, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [serializable(item) for item in value]
    return value


def geometry_snapshot():
    """Keep independent numeric geometry, rail curves, hazards, and safe poses."""
    values = {name: serializable(value) for name, value in vars(layout).items() if name.isupper()}
    values["runtime"] = {
        name: serializable(getattr(route_module, name))
        for name in ("SPAWN", "SPIKES", "PLAY_TERRAIN", "SAFE_POSES")
    }
    values["camera"] = {
        "bottom": route_module.LowerRouteB.camera_bottom,
        "top": route_module.LowerRouteB.camera_top,
        "right": route_module.LowerRouteB.camera_right,
    }
    values["connection"] = {
        name: serializable(getattr(connection, name))
        for name in ("PASSAGE_LEFT", "PASSAGE_RIGHT", "PASSAGE_FLOOR", "PASSAGE_CENTER", "A_ORIGIN")
    }
    values["c_terrain"] = serializable(C_TERRAIN)
    return values


def save_animation(frames, path, duration):
    frames[0].save(path, save_all=True, append_images=frames[1:],
                   duration=duration, loop=0, quality=80)


def main(arguments):
    baseline = arguments.baseline
    if baseline is None:
        baseline = TRACKED_BASELINE if TRACKED_BASELINE.exists() else LOCAL_BASELINE
    baseline = baseline.resolve()
    output = arguments.output_dir.resolve()
    current = geometry_snapshot()
    if arguments.snapshot:
        if baseline.exists():
            raise RuntimeError(f"Preserve the original before snapshot at {baseline}")
        baseline.parent.mkdir(parents=True, exist_ok=True)
        baseline.write_text(json.dumps(current, indent=2), encoding="utf-8")
        print("Saved B geometry snapshot", baseline)
        return
    expected = json.loads(baseline.read_text(encoding="utf-8"))
    assert {name: value for name, value in current.items() if name != "camera"} == {
        name: value for name, value in expected.items() if name != "camera"
    }, "B geometry, rail, hazards, safe poses, or A/B connection changed"
    assert current["camera"]["bottom"] == expected["camera"]["bottom"]
    assert current["camera"]["right"] == expected["camera"]["right"]
    assert current["camera"]["top"] == expected["camera"]["top"] + B_CAMERA_HEADROOM
    output.mkdir(parents=True, exist_ok=True)
    pico.open_canvas(SCREEN_WIDTH, SCREEN_HEIGHT)
    cave = SimpleNamespace(width=SCREEN_WIDTH, height=SCREEN_HEIGHT,
                           shaft=SimpleNamespace(w=4096))
    rooms = LowerCaves(cave)
    player = Player(0, 0, 12000)
    camera = Camera(SCREEN_WIDTH, player.world_width)
    rooms.room, rooms.has_relic = "route_b", True
    rooms.enter(player, camera, seal_open=True)
    route = rooms.route_b
    assert serializable(route_module.PLAY_TERRAIN) == expected["runtime"]["PLAY_TERRAIN"]
    assert serializable(rooms.route_connection.base_terrain) == serializable(
        (*C_TERRAIN, *route_module.PLAY_TERRAIN, *rooms.route_a.terrain,
         (connection.PASSAGE_LEFT, layout.BOTTOM, connection.PASSAGE_RIGHT, connection.PASSAGE_FLOOR),
         (connection.PASSAGE_RIGHT, layout.BOTTOM, rooms.route_a.world_width, rooms.route_a.ground_y)))
    samples, stills, jump_log = [], [], []

    def draw(tag, *, capture=False):
        pico.SDL_ClearError()
        rooms.update_effects(1 / 60, player)
        pico.clear_canvas()
        rooms.draw(camera)
        player.draw(camera)
        rooms.draw_foreground(camera)
        error = pico.SDL_GetError()
        assert not error, (tag, camera.x, camera.y, camera.zoom, error)
        samples.append({"tag": tag, "x": camera.x, "y": camera.y, "zoom": camera.zoom})
        return read_render(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT) if capture else None

    def position(x, y):
        # Synthetic camera checks include spaces the player usually crosses by rail.
        player.x, player.y = x, y
        rooms.follow_camera(player, camera)

    def still(tag, x, y, zoom=.5):
        camera.zoom = zoom
        position(x, y)
        image = draw(tag, capture=True)
        image.save(output / f"{tag}.png")
        stills.append((tag, image))

    # Both directions expose B's upper wall, deep lower rail and room transitions.
    for zoom in (.4, .5, .65):
        camera.zoom = zoom
        centers = list(range(-400, round(connection.A_ORIGIN[0] + 500), 280))
        for direction, positions in (("out", centers), ("back", reversed(centers))):
            for x in positions:
                for y in (layout.BOTTOM + 60, layout.SECRET_FLOOR_Y,
                          layout.PILLBUG_LEDGE[3], layout.SHIELD_LEDGE[3], layout.TOP - 30):
                    position(x, y)
                    camera.zoom = zoom
                    camera.follow(x)
                    bottom, top = rooms.route_camera_bounds(x)
                    view_height = SCREEN_HEIGHT / zoom
                    camera.y = max(bottom, min(top - view_height, y - view_height * .22))
                    draw(f"sweep-{zoom}-{direction}")

    still("01-b-entry", 4720, layout.A_ENTRY[3])
    still("02-b-first-rail-high", 4010, 870)
    still("03-b-pillbug-ledge", 3450, layout.PILLBUG_LEDGE[3])
    still("04-b-shield-ledge", 2590, layout.SHIELD_LEDGE[3])
    still("05-b-second-rail-low", 1740, -560)
    still("06-b-c-join", 180, C_FLOOR)
    still("07-a-b-join", connection.PASSAGE_CENTER + 130, connection.PASSAGE_FLOOR)
    for revealed, collected, tag in (
        (False, False, "08-b-secret-hidden"),
        (True, False, "09-b-secret-revealed"),
        (True, True, "10-b-secret-collected"),
    ):
        route.secret_revealed, route.secret_relic_collected = revealed, collected
        still(tag, 970, layout.SECRET_FLOOR_Y)
    route.secret_revealed = route.secret_relic_collected = False

    # Full B camera retains the same renderer entry point at a wide review zoom.
    overview_zoom = min(SCREEN_WIDTH / (layout.WIDTH + 300),
                        SCREEN_HEIGHT / (layout.TOP - layout.BOTTOM + 130))
    still("11-b-overview", layout.WIDTH / 2, (layout.TOP + layout.BOTTOM) / 2, overview_zoom)
    # Keep the normal gameplay gallery separate from the unusually wide map-review camera.
    stills.pop()

    jump_frames = []
    for tag, x, surface in (
        ("entry", 4730, layout.A_ENTRY[3]),
        ("pillbug", 3500, layout.PILLBUG_LEDGE[3]),
        ("shield", 2500, layout.SHIELD_LEDGE[3]),
    ):
        camera.zoom = .5
        assert player.recover_at(x, surface, 0), tag
        heights = []
        for frame in range(74):
            rooms.update(player, camera, 1 / 60, interact=False, direction=0,
                         running=False, jump_pressed=frame == 0, jump_held=frame < 18,
                         crouching=False, attack_pressed=False)
            heights.append(player.y)
            image = draw("jump-" + tag, capture=frame % 3 == 0)
            if image is not None:
                jump_frames.append(image)
        assert max(heights) > surface + 100, (tag, max(heights))
        assert player.grounded and abs(player.y - surface) < .01, (tag, player.y)
        jump_log.append({"surface": tag, "apex_world_y": max(heights), "landing_world_y": player.y})
    save_animation(jump_frames, output / "b-jump-motion.webp", 50)

    # Camera.focus_relic is also used by the game's held-C view. Both rails run right to left.
    rail_reports = []
    for index, carriage in enumerate(route.carriages, start=1):
        route.reset_carriage(carriage)
        carriage.relic_mounted = True
        route.rail_attempt = carriage
        carriage.direction = -1
        x, y = carriage.segments[-1].end
        assert player.recover_at(x, layout.A_ENTRY[3] if index == 1 else layout.SHIELD_LEDGE[3], 0)
        frames = []
        step_time = carriage.length / RAIL_TRAVEL_SPEED / 54
        for frame in range(56):
            camera.zoom = .5 if frame < 28 else .4
            x, y = carriage.position
            bottom, top = rooms.route_camera_bounds(x)
            camera.focus_relic((x, y), bottom=bottom, top=top)
            frames.append(draw(f"rail-{index}-focus", capture=True))
            route.update(player, step_time)
        assert carriage.distance == 0 and carriage.position == carriage.segments[0].start
        rail_reports.append({"rail": index, "start": carriage.segments[-1].end,
                             "end": carriage.position, "length": carriage.length})
        save_animation(frames, output / f"b-rail-{index}-focus.webp", 65)
        carriage.relic_mounted = False
        route.rail_attempt = None

    # Smooth pan across the A/B join in both directions, without switching renderers.
    join_frames = []
    for direction in (1, -1):
        for frame in range(31):
            fraction = frame / 30 if direction > 0 else 1 - frame / 30
            x = 4400 + (connection.A_ORIGIN[0] + 700 - 4400) * fraction
            camera.zoom = .5
            position(x, connection.PASSAGE_FLOOR)
            join_frames.append(draw("a-b-round-trip", capture=True))
    save_animation(join_frames, output / "b-a-connection.webp", 65)
    c_frames = []
    for direction in (1, -1):
        for frame in range(25):
            fraction = frame / 24 if direction > 0 else 1 - frame / 24
            position(-700 + 1850 * fraction, C_FLOOR)
            c_frames.append(draw("b-c-round-trip", capture=True))
    save_animation(c_frames, output / "b-c-connection.webp", 65)

    rows = (len(stills) + 1) // 2
    gallery = Image.new("RGB", (960, rows * 288), (8, 18, 24))
    labels = ImageDraw.Draw(gallery)
    for index, (tag, image) in enumerate(stills):
        x, y = index % 2 * 480, index // 2 * 288
        gallery.paste(image.resize((480, 270), Image.Resampling.LANCZOS), (x, y))
        labels.text((x + 5, y + 272), tag, fill=(200, 216, 215))
    gallery.save(output / "runtime-gallery.jpg", quality=91)
    report = {
        "geometry_unchanged": True,
        "camera_baseline": expected["camera"], "camera_current": current["camera"],
        "baseline": str(baseline),
        "verification": "Automated SDL renderer, synthetic camera sweeps, real Player jumps, moving relic rails.",
        "sdl_samples": len(samples),
        "zoom_values": sorted({sample["zoom"] for sample in samples}),
        "jumps": jump_log,
        "rails": rail_reports,
        "secret_states": ["hidden", "revealed", "collected"],
        "camera_samples": samples,
    }
    (output / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("B geometry preserved; SDL samples without errors", len(samples))
    print("Real Player jumps completed", len(jump_log))
    print("Both relic rails completed; review captures", output)
    del route, rooms, player
    gc.collect()
    pico.close_canvas()


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", action="store_true", help="Save an immutable layout baseline and exit.")
    parser.add_argument("--baseline", type=Path,
                        help="Geometry baseline JSON; prefers the tracked asset baseline when it exists.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    main(parser.parse_args())

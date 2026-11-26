"""Capture fixed B platform, wall, basement, and lamp views through the game renderer."""

from argparse import ArgumentParser
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

import moss_art
from lower_caves import LowerCaves
from lower_route_b_layout import A_ENTRY, C_APPROACH_LEDGE, PILLBUG_LEDGE, SECRET_FLOOR_Y, SHIELD_LEDGE
from main import Camera, SCREEN_HEIGHT, SCREEN_WIDTH
from player import Player
from route_camera import B_CAMERA_HEADROOM
from tools.preview_lower_route_a import read_render
from tools.preview_lower_route_b_wall import TRACKED_BASELINE, geometry_snapshot


VIEWS = (
    ("01-left-connection", 1050, C_APPROACH_LEDGE[3]),
    ("02-shield-wall", 2775, SHIELD_LEDGE[3]),
    ("03-pillbug-pillar", 3450, PILLBUG_LEDGE[3]),
    ("04-a-entry", 4780, A_ENTRY[3]),
    ("05-basement", 1740, SECRET_FLOOR_Y),
)


def main(output, reference_cameras):
    expected = json.loads(TRACKED_BASELINE.read_text(encoding="utf-8"))
    current = geometry_snapshot()
    assert {name: value for name, value in current.items() if name != "camera"} == {
        name: value for name, value in expected.items() if name != "camera"
    }, "B geometry, rails, hazards, or safe positions changed"
    assert current["camera"]["bottom"] == expected["camera"]["bottom"]
    assert current["camera"]["right"] == expected["camera"]["right"]
    assert current["camera"]["top"] == expected["camera"]["top"] + B_CAMERA_HEADROOM
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    pico.open_canvas(SCREEN_WIDTH, SCREEN_HEIGHT)
    rooms = LowerCaves(SimpleNamespace(width=SCREEN_WIDTH, height=SCREEN_HEIGHT,
                                      shaft=SimpleNamespace(w=4096)))
    player = Player(0, 0, 12000)
    camera = Camera(SCREEN_WIDTH, 12000)
    rooms.room, rooms.has_relic = "route_b", True
    rooms.enter(player, camera, seal_open=True)
    moss_art.perf_counter = lambda: 1.25
    rooms.art.started = 0
    records, frames = [], []
    if reference_cameras:
        reference = json.loads(reference_cameras.read_text(encoding="utf-8"))
        jobs = reference.get("before", reference)["views"]
    else:
        jobs = [{"name": tag, "player": [x, y]} for tag, x, y in VIEWS]
    for job in jobs:
        tag = job["name"].split("-z")[0]
        x, y = job["player"]
        assert player.recover_at(x, y, 0), tag
        rooms.follow_camera(player, camera)
        if reference_cameras:
            # The production route follow sets .45. Restore the recorded camera only after it.
            camera.x, camera.y = job["camera"]
            camera.zoom = job["zoom"]
        zoom = camera.zoom
        rooms.route_b.secret_revealed = job.get("secret_revealed", tag == "05-basement")
        rooms.route_b.secret_relic_collected = False
        for scenery in (rooms.route_a.scenery, rooms.route_b.art.scenery, rooms.route_c.scenery):
            scenery.time = 1.25
        pico.SDL_ClearError()
        pico.clear_canvas()
        rooms.draw(camera)
        player.draw(camera)
        rooms.draw_foreground(camera)
        assert not pico.SDL_GetError(), (tag, zoom, pico.SDL_GetError())
        name = job["name"] if reference_cameras else f"{tag}-z{round(zoom * 100):03d}"
        frame = read_render(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        frame.save(output / f"{name}.png")
        frames.append((name, frame))
        records.append({"name": name, "player": [x, y], "zoom": zoom,
                        "camera": [camera.x, camera.y], "room": rooms.room,
                        "secret_revealed": rooms.route_b.secret_revealed})
        if (not reference_cameras or zoom == .5) and tag in ("03-pillbug-pillar", "01-left-connection"):
            sample = "user-1-shield-pillbug" if tag == "03-pillbug-pillar" else "user-2-c-approach"
            frame.save(output / f"{sample}.png")
    gallery = Image.new("RGB", (1152, ((len(frames) + 2) // 3) * 236), (8, 18, 24))
    labels = ImageDraw.Draw(gallery)
    for index, (name, frame) in enumerate(frames):
        x, y = index % 3 * 384, index // 3 * 236
        gallery.paste(frame.resize((384, 216), Image.Resampling.LANCZOS), (x, y))
        labels.text((x + 4, y + 218), name, fill=(200, 216, 215))
    gallery.save(output / "runtime-gallery.jpg", quality=91)
    report = {
        "geometry_unchanged": True, "baseline": str(TRACKED_BASELINE),
        "camera_baseline": expected["camera"], "camera_current": current["camera"],
        "reference_cameras": str(reference_cameras.resolve()) if reference_cameras else None,
        "renderer_scope": "Actual LowerCaves B renderer, recorded comparison cameras or normal current follow-camera, SDL software.",
        "fixed_scenery_time_seconds": 1.25, "views": records,
        "visual_review": "Inspect platform/wall joins and lamp scale against the player, wall-jump face and cyan rail. Image labels identify the two requested comparison compositions.",
        "motion_validation_command": ".\\.venv\\Scripts\\python.exe -B -m tools.preview_lower_route_b_wall --output-dir .cache/b-surfaces-motion",
    }
    (output / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("B geometry baseline preserved; surface views rendered without SDL errors", len(records))
    print("Captures", output)
    del rooms, player
    gc.collect()
    pico.close_canvas()


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / ".cache/b-surfaces-review")
    parser.add_argument("--reference-cameras", type=Path,
                        help="Use every camera and zoom from an earlier preview report for an art-only comparison.")
    arguments = parser.parse_args()
    main(arguments.output_dir, arguments.reference_cameras)

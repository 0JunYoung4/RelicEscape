"""Capture A's real renderer through camera sweeps, jumps, and relic rail focus."""

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

import lower_route_a as layout
from lower_caves import LowerCaves
from lower_route_connection import A_ORIGIN, PASSAGE_CENTER
from main import Camera, SCREEN_HEIGHT, SCREEN_WIDTH
from player import Player, STANDING_HITBOX_HEIGHT
from rail import RAIL_TRAVEL_SPEED
from tools.preview_lower_route_a import read_render


OUTPUT = ROOT / ".cache/a-wall-review"
SNAPSHOT = ROOT / "assets/terrain/lower-route-a-wall-v1/layout-baseline.json"
CONSTANTS = (
    "ART_ZOOM", "ART_WIDTH", "ART_HEIGHT", "WIDTH", "HEIGHT", "HOLE_PIXEL",
    "GROUND_Y", "EXIT_LEDGE", "ENTRY_LEDGE", "ENTRY_STEP", "RECESS_BACK",
    "OVERHANG", "CEILING_LIPS", "TERRAIN", "ENTRY_X", "ENTRY_Y",
    "BUTTON_LEFT", "BUTTON_RIGHT", "BUTTON_CENTER", "BUTTON_PILLBUGS",
    "RECOVERY", "RECOVERY_RADIUS", "LOWER_DOCK", "UPPER_DOCK", "RAIL_X",
    "LIFT_BEND_RADIUS", "SEAL_GATE", "SEAL_LOWER_PLATE", "SEAL_UPPER_PLATE",
    "SEAL_PLATE_HALF_WIDTH", "SEAL_WINDOW", "SEAL_OPEN_DURATION",
)


def layout_snapshot():
    data = {name: getattr(layout, name) for name in CONSTANTS}
    data["origin"] = A_ORIGIN
    data["rail"] = [
        {"start": part.start, "end": part.end, "center": part.center}
        for part in layout.lift_path()
    ]
    return json.loads(json.dumps(data))


def main(output_dir):
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    current = layout_snapshot()
    before = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    assert current == before, "A's device or collision layout changed"

    pico.open_canvas(SCREEN_WIDTH, SCREEN_HEIGHT)
    cave = SimpleNamespace(width=SCREEN_WIDTH, height=SCREEN_HEIGHT,
                           shaft=SimpleNamespace(w=4096))
    rooms = LowerCaves(cave)
    player = Player(0, 0, A_ORIGIN[0] + layout.WIDTH)
    camera = Camera(SCREEN_WIDTH, player.world_width)
    rooms.room = "route_a"
    rooms.enter(player, camera, seal_open=True)
    route = rooms.route_a
    expected_terrain = [
        [box[0] + A_ORIGIN[0], box[1] + A_ORIGIN[1],
         box[2] + A_ORIGIN[0], box[3] + A_ORIGIN[1]]
        for box in before["TERRAIN"]
    ]
    assert [list(box) for box in route.terrain] == expected_terrain
    route.powered = True
    samples = []
    stills = []

    def draw(tag, *, capture=False):
        rooms.update_effects(1 / 60, player)
        pico.SDL_ClearError()
        pico.clear_canvas()
        rooms.draw(camera)
        player.draw(camera)
        rooms.draw_foreground(camera)
        error = pico.SDL_GetError()
        assert not error, (tag, camera.x, camera.y, camera.zoom, error)
        samples.append({"tag": tag, "x": camera.x, "y": camera.y, "zoom": camera.zoom})
        return read_render(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT) if capture else None

    # Synthetic camera sweep exposes all image edges, both directions and different heights.
    for zoom in (.4, .5, .65):
        camera.zoom = zoom
        centers = list(range(round(PASSAGE_CENTER), round(route.world_width) + 1, 250))
        for direction, positions in (("out", centers), ("back", reversed(centers))):
            for center in positions:
                for local_y in (layout.GROUND_Y, layout.EXIT_LEDGE[3], layout.HEIGHT - 40):
                    player.x, player.y = center, A_ORIGIN[1] + local_y
                    rooms.follow_camera(player, camera)
                    draw(f"sweep-{zoom}-{direction}")

    # Representative views with real normal camera bounds.
    camera.zoom = .5
    points = (
        ("01-a-entry", *route.point(layout.ENTRY_X, layout.ENTRY_LEDGE[3])),
        ("02-lower-right", *route.point(layout.RECOVERY[0], layout.GROUND_Y)),
        ("03-lower-left", *route.point(layout.LOWER_DOCK[0], layout.GROUND_Y)),
        ("04-lift-upper", *route.point(layout.UPPER_DOCK[0], layout.EXIT_LEDGE[3])),
        ("05-seal-gate", *route.point(1150, layout.EXIT_LEDGE[3])),
        ("06-a-b-join", PASSAGE_CENTER + 160, 180),
    )
    for tag, x, y in points:
        assert player.recover_at(x, y, 0), tag
        rooms.follow_camera(player, camera)
        image = draw(tag, capture=True)
        image.save(output_dir / f"{tag}.png")
        stills.append((tag, image))

    # Drive Player.update through the ordinary LowerCaves.update jump entry point.
    jump_frames = []
    jump_log = []
    for tag, x, surface in (
        ("floor", layout.RECOVERY[0] - 200, layout.GROUND_Y),
        ("entry", layout.ENTRY_X, layout.ENTRY_LEDGE[3]),
        ("upper", layout.UPPER_DOCK[0], layout.EXIT_LEDGE[3]),
    ):
        camera.zoom = .5
        assert player.recover_at(*route.point(x, surface), 0), tag
        heights = []
        for frame in range(74):
            rooms.update(player, camera, 1 / 60, interact=False, direction=0,
                         running=False, jump_pressed=frame == 0,
                         jump_held=frame < 18, crouching=False, attack_pressed=False)
            heights.append(player.y)
            image = draw("jump-" + tag, capture=frame % 3 == 0)
            if image is not None:
                jump_frames.append(image)
        assert max(heights) > heights[0] + 100, (tag, heights)
        assert player.grounded and abs(player.y - (surface + A_ORIGIN[1])) < .01, tag
        jump_log.append({"surface": tag, "apex_world_y": max(heights), "landing_world_y": player.y})
    jump_frames[0].save(output_dir / "jump-motion.webp", save_all=True,
                        append_images=jump_frames[1:], duration=50, loop=0, quality=80)

    # Use the same Camera.focus_relic call as the actual hold-C relic view.
    carriage = route.carriage
    carriage.distance = 0
    carriage.direction = 1
    carriage.relic_mounted = True
    rail_frames = []
    steps = 48
    for frame in range(steps + 1):
        camera.zoom = .5 if frame < steps / 2 else .4
        x, y = carriage.position
        bottom, top = rooms.route_camera_bounds(x)
        camera.focus_relic((x, y), bottom=bottom, top=top)
        image = draw("rail-focus", capture=True)
        rail_frames.append(image)
        if frame < steps:
            carriage.move(carriage.length / RAIL_TRAVEL_SPEED / steps)
    assert carriage.position == route.point(*layout.UPPER_DOCK)
    rail_frames[0].save(output_dir / "rail-focus.webp", save_all=True,
                        append_images=rail_frames[1:], duration=70, loop=0, quality=80)

    # A camera round-trip exposes entrance and exit fades for visual review.
    walk_frames = []
    for direction in (1, -1):
        for index in range(35):
            fraction = index / 34 if direction > 0 else 1 - index / 34
            player.x = PASSAGE_CENTER + (route.world_width - PASSAGE_CENTER) * fraction
            player.y = A_ORIGIN[1] + layout.EXIT_LEDGE[3]
            camera.zoom = .5
            rooms.follow_camera(player, camera)
            walk_frames.append(draw("pan-round-trip", capture=True))
    walk_frames[0].save(output_dir / "pan-round-trip.webp", save_all=True,
                        append_images=walk_frames[1:], duration=65, loop=0, quality=80)
    gallery = Image.new("RGB", (960, 3 * 288), (8, 18, 24))
    labels = ImageDraw.Draw(gallery)
    for index, (tag, image) in enumerate(stills):
        x, y = (index % 2) * 480, (index // 2) * 288
        gallery.paste(image.resize((480, 270), Image.Resampling.LANCZOS), (x, y))
        labels.text((x + 5, y + 272), tag, fill=(200, 216, 215))
    gallery.save(output_dir / "runtime-gallery.jpg", quality=91)
    report = {"layout_unchanged": True, "sdl_samples": len(samples),
              "zoom_values": [.4, .5, .65], "jumps": jump_log,
              "camera_samples": samples}
    (output_dir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("Geometry preserved; rendered SDL samples without errors", len(samples))
    print("Actual Player jumps completed", len(jump_log))
    print("Review captures", output_dir)
    del rooms, route, player
    gc.collect()
    pico.close_canvas()


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT,
                        help="Review capture directory.")
    arguments = parser.parse_args()
    main(arguments.output_dir)

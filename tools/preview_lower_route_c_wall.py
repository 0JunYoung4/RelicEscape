"""Check C's existing checkpoint, sealed boundary, jumps, and B/C camera crossing."""

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

import lower_route_c as layout
from lower_caves import LowerCaves
from lower_route_b_layout import C_APPROACH_LEDGE, C_PASSAGE, C_PASSAGE_LEFT
from main import Camera, SCREEN_HEIGHT, SCREEN_WIDTH
from player import Player, STANDING_HITBOX_WIDTH
from tools.preview_lower_route_a import read_render


BASELINE = ROOT / "assets/terrain/lower-route-c-wall-v1/layout-baseline.json"


def geometry_snapshot():
    names = ("LEFT", "RIGHT", "FLOOR", "ENTRANCE_X", "ENTRANCE_WIDTH",
             "CHECKPOINT", "CHECKPOINT_RADIUS", "FLOOR_BOUNDS", "TERRAIN")
    values = {name: getattr(layout, name) for name in names}
    values["connection"] = {"C_PASSAGE": C_PASSAGE, "C_PASSAGE_LEFT": C_PASSAGE_LEFT,
                            "C_APPROACH_LEDGE": C_APPROACH_LEDGE}
    return json.loads(json.dumps(values))


def main(output):
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    expected = json.loads(BASELINE.read_text(encoding="utf-8"))
    expected_geometry = {name: value for name, value in expected.items() if name != "enemies"}
    assert geometry_snapshot() == expected_geometry, "C geometry, devices, or B/C connection changed"

    pico.open_canvas(SCREEN_WIDTH, SCREEN_HEIGHT)
    cave = SimpleNamespace(width=SCREEN_WIDTH, height=SCREEN_HEIGHT,
                           shaft=SimpleNamespace(w=4096))
    rooms = LowerCaves(cave)
    player = Player(0, 0, 12000)
    camera = Camera(SCREEN_WIDTH, player.world_width)
    rooms.room, rooms.has_relic = "route_b", True
    rooms.enter(player, camera, seal_open=True)
    route = rooms.route_c
    enemies = [{"x": bug.x, "floor_y": bug.floor_y, "support_edges": bug.support_edges, "hp": bug.hp}
               for bug in route.enemies]
    assert json.loads(json.dumps(enemies)) == expected["enemies"], "C enemy placement changed"
    samples, stills = [], []

    def draw(tag, capture=False):
        pico.SDL_ClearError()
        rooms.update_effects(1 / 60, player)
        pico.clear_canvas()
        rooms.draw(camera)
        player.draw(camera)
        rooms.draw_foreground(camera)
        assert not pico.SDL_GetError(), (tag, pico.SDL_GetError(), camera.x, camera.y, camera.zoom)
        samples.append({"tag": tag, "x": camera.x, "y": camera.y, "zoom": camera.zoom})
        return read_render(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT) if capture else None

    def tick(direction=0, jump=False, jump_held=False):
        rooms.update(player, camera, 1 / 60, interact=False, direction=direction,
                     running=True, jump_pressed=jump, jump_held=jump_held,
                     crouching=False, attack_pressed=False)

    def still(tag):
        frame = draw(tag, True)
        frame.save(output / f"{tag}.png")
        stills.append((tag, frame))

    assert player.recover_at(-900, layout.FLOOR, 0)
    rooms.follow_camera(player, camera)
    assert not route.checkpoint_reached and rooms.restart_room == "route_b"
    still("01-c-unlit")

    # Actual grounded arrival activates the checkpoint. Entering its trigger in the air does not.
    player.x, player.y = layout.CHECKPOINT[0], layout.FLOOR + 130
    player.grounded = False
    route.check_arrival(player)
    assert not route.checkpoint_reached
    assert player.recover_at(*layout.CHECKPOINT)
    rooms.follow_camera(player, camera)
    assert route.checkpoint_reached and rooms.restart_room == "route_c"
    still("02-c-lit")

    # The existing B1 doorway is sealed. Check its current movement boundary.
    for frame in range(160):
        tick(-1)
        draw("closed-door-approach")
    expected_x = layout.ENTRANCE_X + (layout.ENTRANCE_WIDTH + STANDING_HITBOX_WIDTH) / 2
    assert abs(player.x - expected_x) < .001 and player.grounded
    still("03-c-sealed-door")

    for zoom in (.4, .5, .65):
        camera.zoom = zoom
        positions = (-1300, -900, -500, -100, 300, 800)
        for direction in (positions, reversed(positions)):
            for x in direction:
                for y in (layout.FLOOR, layout.FLOOR + 200, 1210):
                    player.x, player.y = x, y
                    rooms.follow_camera(player, camera)
                    draw(f"camera-sweep-{zoom}")
        player.x, player.y = -900, layout.FLOOR
        rooms.follow_camera(player, camera)
        still(f"04-c-zoom-{zoom}")

    camera.zoom = .5
    assert player.recover_at(*layout.CHECKPOINT)
    jump_frames, heights = [], []
    for frame in range(74):
        tick(jump=frame == 0, jump_held=frame < 18)
        heights.append(player.y)
        picture = draw("checkpoint-jump", frame % 3 == 0)
        if picture is not None:
            jump_frames.append(picture)
    assert max(heights) > layout.FLOOR + 100
    assert player.grounded and abs(player.y - layout.FLOOR) < .001
    jump_frames[0].save(output / "c-jump.webp", save_all=True,
                        append_images=jump_frames[1:], duration=50, loop=0, quality=80)

    crossing_frames, crossing_rooms = [], set()
    assert player.recover_at(180, layout.FLOOR, 0)
    for direction, destination in ((-1, -850), (1, 180)):
        for frame in range(180):
            tick(direction)
            crossing_rooms.add(rooms.room)
            picture = draw("b-c-crossing", frame % 4 == 0)
            if picture is not None:
                crossing_frames.append(picture)
            arrived = player.x <= destination if direction < 0 else player.x >= destination
            if arrived:
                break
        assert arrived and player.grounded and player.y == layout.FLOOR
    assert crossing_rooms == {"route_b", "route_c"}
    assert rooms.route_c is route, "B/C crossing replaced the checkpoint room"
    still("05-b-c-seam")
    crossing_frames[0].save(output / "c-b-crossing.webp", save_all=True,
                            append_images=crossing_frames[1:], duration=65, loop=0, quality=80)

    # Use the same room entry selected by main's existing checkpoint restart.
    restart = LowerCaves(cave)
    restart.room, restart.has_relic = rooms.restart_room, rooms.has_relic
    restart.enter(player, camera, seal_open=True)
    assert restart.room == "route_c" and restart.has_relic
    assert (player.x, player.y) == layout.CHECKPOINT[:2]
    assert player.grounded and restart.route_c.checkpoint_reached

    rows = (len(stills) + 1) // 2
    gallery = Image.new("RGB", (960, rows * 288), (8, 18, 24))
    labels = ImageDraw.Draw(gallery)
    for index, (tag, picture) in enumerate(stills):
        x, y = index % 2 * 480, index // 2 * 288
        gallery.paste(picture.resize((480, 270), Image.Resampling.LANCZOS), (x, y))
        labels.text((x + 5, y + 272), tag, fill=(200, 216, 215))
    gallery.save(output / "runtime-gallery.jpg", quality=91)
    report = {
        "geometry_unchanged": True, "enemy_placement_unchanged": True,
        "sdl_samples": len(samples), "zoom_values": [.4, .5, .65],
        "checkpoint_grounded_trigger": True, "checkpoint_airborne_trigger_rejected": True,
        "restart_entry_relic_and_checkpoint_preserved": True,
        "jump_apex_world_y": max(heights), "jump_landed": True,
        "b_c_crossing_both_directions": True, "sealed_door_limit_x": expected_x,
        "door_opening_supported": False,
        "door_opening_note": "The existing C/B1 doorway has a permanent sealed terrain boundary and no open state API.",
        "verification": "Automated SDL camera samples, real Player movement and jump, existing checkpoint restart entry.",
        "camera_samples": samples,
    }
    (output / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("C geometry, devices, and enemy placement preserved")
    print("SDL samples without errors", len(samples))
    print("Grounded checkpoint, sealed door, jump, B/C crossing and restart entry checked")
    print("Door open state is unavailable in the existing game")
    print("Captures", output)
    del restart, route, rooms, player
    gc.collect()
    pico.close_canvas()


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / ".cache/c-wall-review")
    main(parser.parse_args().output_dir)

"""Render B's painted background and existing game assets on the blockout."""

import json
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("SDL_RENDER_DRIVER", "software")

from pico2d import pico2d as pico

from main import Camera, RELIC_GLOW_IMAGE, RELIC_IMAGE
from player import ASSET_ROOT, Animation, Player
from rail import RAIL_ART_SCALE, RAIL_BEND_IMAGE, RAIL_CARRIAGE_IMAGE, RAIL_IMAGE, draw_rail
from lower_route_b_art import LowerRouteBArt
from lower_route_b_layout import A_ENTRY, BOTTOM, GOLEM_LEDGE, PILLBUG_LEDGE, RAIL_ONE, RAIL_TWO, SHIELD_LEDGE
from tools.preview_lower_route_a import read_render


CONCEPTS = ASSET_ROOT / "concepts"
ENEMIES = ASSET_ROOT / "sprites/enemies"
WIDTH, HEIGHT = 2500, 850
ZOOM = .5


def actor(stem):
    data = json.loads((ENEMIES / (stem + ".json")).read_text(encoding="utf-8"))
    return Animation(ENEMIES / data["image"], data["frames"], data["foot_anchor"],
                     data["scale"], data["fps"], data.get("frame_durations_ms", ()))


def draw_scene(camera):
    LowerRouteBArt().draw(camera, HEIGHT)
    straight, bend, carriage, relic, glow = (
        pico.load_image(str(path)) for path in
        (RAIL_IMAGE, RAIL_BEND_IMAGE, RAIL_CARRIAGE_IMAGE, RELIC_IMAGE, RELIC_GLOW_IMAGE)
    )
    for path in (RAIL_ONE, RAIL_TWO):
        draw_rail(straight, bend, camera, path)
        center = camera.world_to_screen(*path[-1].end)
        scale = RAIL_ART_SCALE * camera.zoom
        if path is RAIL_ONE:
            glow.opacify(.62)
            glow.draw(*center, 104, 104)
        carriage.draw(*center, carriage.w * scale, carriage.h * scale)
        if path is RAIL_ONE:
            relic.draw(*center, 18, 18)

    actor("stone-crystal-golem-idle-left-v1").draw(885, GOLEM_LEDGE[3], -1, 0, camera)
    actor("shield-stone-soldier-walk-right-v2").draw(2500, SHIELD_LEDGE[3], 1, 0, camera)
    crawl = Animation(ENEMIES / "stone-pillbug-moss-crawl-left.png",
                      [{"x": 0, "y": 0, "width": 170, "height": 72}], (85, 71), 1.0, 8)
    crawl.draw(3265, PILLBUG_LEDGE[3], -1, 0, camera)
    player = Player(4780, A_ENTRY[3], A_ENTRY[2], spawn_y=A_ENTRY[3])
    player.facing = -1
    player.draw(camera)


if __name__ == "__main__":
    pico.SDL_SetHint(pico.SDL_HINT_RENDER_SCALE_QUALITY, b"1")
    pico.open_canvas(WIDTH, HEIGHT)
    try:
        camera = Camera(WIDTH, A_ENTRY[2], zoom=ZOOM, y=BOTTOM)
        draw_scene(camera)
        read_render(0, 0, WIDTH, HEIGHT).save(CONCEPTS / "map1-lower-route-b-v3.png")
    finally:
        pico.close_canvas()

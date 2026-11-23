"""Render B's painted background and existing game assets on the blockout."""

from ctypes import c_int
import json
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("SDL_RENDER_DRIVER", "software")

from pico2d import pico2d as pico

from main import Camera, RELIC_GLOW_IMAGE, RELIC_IMAGE
from moss_art import MossCaveArt
from player import ASSET_ROOT, Animation, Player
from rail import RAIL_ART_SCALE, RAIL_BEND_IMAGE, RAIL_CARRIAGE_IMAGE, RAIL_IMAGE, draw_rail
from tools.lower_route_b_layout import (A_ENTRY, C_PASSAGE, GOLEM_LEDGE, LEFT_WALL, PILLBUG_LEDGE,
                                       RAIL_ONE, RAIL_TWO, RIGHT_WALL, SHIELD_LEDGE, SPIKE_TIP_Y)
from tools.preview_lower_route_a import read_render


CONCEPTS = ASSET_ROOT / "concepts"
STRUCTURES = ASSET_ROOT / "structures/map1-lower-route"
ENEMIES = ASSET_ROOT / "sprites/enemies"
STEM = "map1-lower-route-b-v2"
WIDTH, HEIGHT = 2500, 850
ZOOM = .5
BOTTOM = -330


def draw_rock_wall(texture, camera, profile):
    """Keep the wall-jump face fixed while the outer edge widens into the rock."""
    bottom, top = profile[0][0], profile[-1][0]
    indices = []
    for index in range(0, 2 * (len(profile) - 1), 2):
        indices.extend((index, index + 1, index + 2, index + 1, index + 2, index + 3))
    triangles = (c_int * len(indices))(*indices)
    for left_half in (True, False):
        vertices = []
        for y, left, right in profile:
            center = (left + right) / 2
            endpoints = ((left, .997), (center, .60)) if left_half else ((center, .60), (right, .997))
            for x, u in endpoints:
                sx, sy = camera.world_to_screen(x, y)
                vertices.append(pico.SDL_Vertex((sx, HEIGHT - sy), (255, 255, 255, 255),
                                                (u, (top - y) / (top - bottom))))
        geometry = (pico.SDL_Vertex * len(vertices))(*vertices)
        pico.SDL_RenderGeometry(pico.renderer, texture.texture, geometry, len(vertices),
                                triangles, len(indices))


def draw_structure(image, crop, camera, x, bottom, width, height, *, flip=""):
    left, top, right, base = crop
    source_width, source_height = right - left, base - top
    image.clip_composite_draw(left, image.h - base, source_width, source_height, 0, flip,
                              *camera.world_to_screen(x, bottom + height / 2),
                              width * camera.zoom, height * camera.zoom)


def draw_spike_bank(camera):
    spikes = pico.load_image(str(STRUCTURES / "lower-cave-thorn-bed-v1.png"))
    pico.draw_rectangle(0, 0, WIDTH, camera.world_to_screen(0, -300)[1], 5, 13, 15, filled=True)
    source = (40, 53, 2133, 640)
    # Two overlapping rows hide the repeated outline and cover every part of the floor.
    pico.SDL_SetTextureColorMod(spikes.texture, 95, 134, 140)
    for index in range(9):
        draw_structure(spikes, source, camera, index * 612 + 50, -315, 730, 102,
                       flip="h" if index % 2 else "")
    pico.SDL_SetTextureColorMod(spikes.texture, 195, 210, 203)
    x = -175
    for index, width in enumerate((630, 740, 668, 798, 640, 760, 695, 840, 637)):
        height = 102 + (index * 13) % 23
        draw_structure(spikes, source, camera, x + width / 2, SPIKE_TIP_Y - height,
                       width, height, flip="h" if index % 2 else "")
        x += width - 55


def actor(stem):
    data = json.loads((ENEMIES / (stem + ".json")).read_text(encoding="utf-8"))
    return Animation(ENEMIES / data["image"], data["frames"], data["foot_anchor"],
                     data["scale"], data["fps"], data.get("frame_durations_ms", ()))


def draw_scene(camera):
    art = MossCaveArt(WIDTH, HEIGHT)
    background = pico.load_image(str(CONCEPTS / (STEM + "-background.png")))
    background.draw_to_origin(0, 0, WIDTH, HEIGHT)

    left, bottom, right, top = LEFT_WALL
    draw_rock_wall(art.wall, camera, ((bottom, right - 25, right - 9),
                                     (bottom + 38, left + 16, right),
                                     (bottom + 120, left - 24, right),
                                     (top, left - 85, right)))
    left, bottom, right, top = RIGHT_WALL
    draw_rock_wall(art.wall, camera, ((bottom - 16, left + 60, right - 58),
                                     (bottom + 4, left + 26, right - 36),
                                     (bottom + 28, left, right - 18),
                                     (bottom + 120, left, right + 8),
                                     (790, left, right + 12),
                                     (top, left - 27, right + 40),
                                     (1210, left - 78, right + 122),
                                     (1380, left - 130, right + 192)))

    art.draw_platform(camera, (C_PASSAGE[0] - 160, 418, GOLEM_LEDGE[2], GOLEM_LEDGE[3]))
    art.draw_platform(camera, (PILLBUG_LEDGE[0], 58, PILLBUG_LEDGE[2], PILLBUG_LEDGE[3]))
    art.draw_platform(camera, (A_ENTRY[0], 48, A_ENTRY[2] + 110, A_ENTRY[3]))
    bridge = pico.load_image(str(STRUCTURES / "lower-cave-stone-bridge-v1.png"))
    left, _, right, top = SHIELD_LEDGE
    draw_structure(bridge, (40, 193, 2132, 579), camera, (left + right) / 2, top - 136,
                   right - left, 136)

    marker = pico.load_image(str(STRUCTURES / "lower-cave-safe-waymarker-v1.png"))
    for x, surface, size in ((240, C_PASSAGE[3], 139), (1200, GOLEM_LEDGE[3], 66),
                             (2760, SHIELD_LEDGE[3], 86), (3530, PILLBUG_LEDGE[3], 66)):
        draw_structure(marker, (207, 15, 1040, 1206), camera, x, surface, size * .70, size)
    rubble = pico.load_image(str(STRUCTURES / "lower-cave-landing-rubble-v1.png"))
    pico.SDL_SetTextureColorMod(rubble.texture, 139, 175, 186)
    draw_structure(rubble, (88, 133, 1454, 882), camera, 4880, A_ENTRY[3], 219, 122)

    draw_spike_bank(camera)
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
        read_render(0, 0, WIDTH, HEIGHT).save(CONCEPTS / (STEM + ".png"))
    finally:
        pico.close_canvas()

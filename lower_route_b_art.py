"""Draw the B-part scenery and terrain using the approved asset anchors."""

from ctypes import c_int
import json

from pico2d import pico2d as pico

from lower_route_b_layout import (A_ENTRY, BOTTOM, C_PASSAGE, GOLEM_LEDGE, LEFT_WALL,
                                  PILLBUG_LEDGE, RIGHT_WALL, SHIELD_LEDGE, SPIKE_TIP_Y, TOP, WIDTH)
from player import ASSET_ROOT


STRUCTURES = ASSET_ROOT / "structures/map1-lower-route"
PLATFORMS = ASSET_ROOT / "terrain/ruin-platforms"


def draw_rock_wall(texture, camera, profile, screen_height):
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
                vertices.append(pico.SDL_Vertex((sx, screen_height - sy), (255, 255, 255, 255),
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


def draw_ruin_platform(camera, image, entry, bounds, *, base_y=None):
    left, _, right, top = bounds
    source_left, surface_y, source_right = entry["walk_surface"]
    crop_left, crop_top, crop_right, crop_bottom = entry["crop"]
    scale = (right - left) / (source_right - source_left)
    center = left + ((crop_left + crop_right) / 2 - source_left) * scale
    height_scale = scale if base_y is None else (top - base_y) / (crop_bottom - surface_y)
    bottom = top + (surface_y - crop_bottom) * height_scale
    draw_structure(image, entry["crop"], camera, center, bottom,
                   (crop_right - crop_left) * scale, (crop_bottom - crop_top) * height_scale)


def draw_spike_bank(spikes, camera, screen_height):
    bed_top = min(screen_height, camera.world_to_screen(0, -300)[1])
    if bed_top > 0:
        pico.draw_rectangle(0, 0, camera.screen_width, bed_top, 5, 13, 15, filled=True)
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


class LowerRouteBArt:
    def __init__(self):
        self.background = pico.load_image(str(ASSET_ROOT / "concepts/map1-lower-route-b-v2-background.png"))
        self.wall = pico.load_image(str(ASSET_ROOT / "terrain/green-cavern-wall-v1.png"))
        self.marker = pico.load_image(str(STRUCTURES / "lower-cave-safe-waymarker-v1.png"))
        self.rubble = pico.load_image(str(STRUCTURES / "lower-cave-landing-rubble-v1.png"))
        self.spikes = pico.load_image(str(STRUCTURES / "lower-cave-thorn-bed-v1.png"))
        pico.SDL_SetTextureColorMod(self.rubble.texture, 139, 175, 186)
        self.platforms = json.loads((PLATFORMS / "manifest.json").read_text(encoding="utf-8"))["platforms"]
        self.platform_images = {
            name: pico.load_image(str(PLATFORMS / self.platforms[name]["image"]))
            for name in ("root-wedge", "connected-guard-wall", "connected-passage", "spike-bed-pier")
        }

    def draw(self, camera, screen_height):
        self.background.draw_to_origin(*camera.world_to_screen(0, BOTTOM),
                                       WIDTH * camera.zoom, (TOP - BOTTOM) * camera.zoom)
        wall = self.wall
        left, bottom, right, top = RIGHT_WALL
        draw_rock_wall(wall, camera, ((bottom - 16, left + 60, right - 58),
                                     (bottom + 4, left + 26, right - 36),
                                     (bottom + 28, left, right - 18),
                                     (bottom + 120, left, right + 8),
                                     (790, left, right + 12),
                                     (top, left - 27, right + 40),
                                     (1210, left - 78, right + 122),
                                     (1380, left - 130, right + 192)), screen_height)

        passage = (C_PASSAGE[0] - 105, C_PASSAGE[1], GOLEM_LEDGE[2], GOLEM_LEDGE[3])
        entry = (A_ENTRY[0], A_ENTRY[1], A_ENTRY[2] + 110, A_ENTRY[3])
        for name, bounds, base_y in (("root-wedge", entry, None),
                                     ("connected-guard-wall", SHIELD_LEDGE, LEFT_WALL[1]),
                                     ("connected-passage", passage, None),
                                     ("spike-bed-pier", PILLBUG_LEDGE, SPIKE_TIP_Y - 113)):
            draw_ruin_platform(camera, self.platform_images[name], self.platforms[name], bounds, base_y=base_y)

        for x, surface, size in ((240, C_PASSAGE[3], 139), (1200, GOLEM_LEDGE[3], 66),
                                 (2760, SHIELD_LEDGE[3], 86), (3530, PILLBUG_LEDGE[3], 66)):
            draw_structure(self.marker, (207, 15, 1040, 1206), camera, x, surface, size * .70, size)
        draw_structure(self.rubble, (88, 133, 1454, 882), camera, 4880, A_ENTRY[3], 219, 122)
        draw_spike_bank(self.spikes, camera, screen_height)

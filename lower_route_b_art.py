"""Draw the B-part scenery and terrain using the approved asset anchors."""

from ctypes import c_int
import json
from math import ceil

from pico2d import pico2d as pico

from health import SPIKE_HEIGHT
from lower_route_b_layout import (A_ENTRY, BACKGROUND_BOTTOM, BOTTOM, C_APPROACH_LEDGE, C_PASSAGE,
                                  LEFT_WALL, PILLBUG_LEDGE, RIGHT_WALL,
                                  SHIELD_LEDGE, SPIKE_SHELVES, SPIKE_TIP_Y, THORN_WALL_CROP,
                                  THORN_WALLS, TOP, WIDTH)
from player import ASSET_ROOT


STRUCTURES = ASSET_ROOT / "structures/map1-lower-route"
PLATFORMS = ASSET_ROOT / "terrain/ruin-platforms"
CEILING_SPANS = (
    (-1200, 1250, TOP + 74, 358, False),
    (820, 3260, TOP + 64, 380, True),
    (2830, WIDTH, TOP + 94, 370, False),
)


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


def draw_spike_bank(spikes, camera, left, right, tip):
    source = (40, 53, 2133, 640)
    tiles = ceil((right - left) / 650)
    stride = (right - left) / tiles
    # Keep both rows entirely within the shelf, leaving the rail shafts clear.
    for tint, height, offset in (((95, 134, 140), 82, -13), ((195, 210, 203), 96, 0)):
        pico.SDL_SetTextureColorMod(spikes.texture, *tint)
        for index in range(tiles):
            start = max(left, left + index * stride - 33)
            end = min(right, left + (index + 1) * stride + 33)
            if start < camera.x + camera.view_width and end > camera.x:
                draw_structure(spikes, source, camera, (start + end) / 2, tip + offset - height,
                               end - start, height, flip="h" if index % 2 else "")


class LowerRouteBArt:
    def __init__(self):
        self.background = pico.load_image(str(ASSET_ROOT / "concepts/map1-lower-route-b-v2-background.png"))
        if pico.SDL_SetTextureScaleMode(self.background.texture, pico.SDL_ScaleModeLinear) != 0:
            raise RuntimeError(pico.SDL_GetError())
        self.wall = pico.load_image(str(ASSET_ROOT / "terrain/green-cavern-wall-v1.png"))
        self.marker = pico.load_image(str(STRUCTURES / "lower-cave-safe-waymarker-v1.png"))
        self.rubble = pico.load_image(str(STRUCTURES / "lower-cave-landing-rubble-v1.png"))
        self.spikes = pico.load_image(str(STRUCTURES / "lower-cave-thorn-bed-v1.png"))
        self.thorn_wall = pico.load_image(str(STRUCTURES / "lower-cave-thorn-wall-v1.png"))
        self.canopy = pico.load_image(str(ASSET_ROOT / "terrain/green-cavern-canopy-v1.png"))
        pico.SDL_SetTextureColorMod(self.rubble.texture, 139, 175, 186)
        self.platforms = json.loads((PLATFORMS / "manifest.json").read_text(encoding="utf-8"))["platforms"]
        self.platform_images = {
            name: pico.load_image(str(PLATFORMS / self.platforms[name]["image"]))
            for name in ("root-wedge", "connected-guard-wall", "connected-passage", "spike-bed-pier",
                         "waterworn-sill")
        }

    def draw(self, camera, screen_height, *, passage_left=C_PASSAGE[0]):
        panorama_width = WIDTH - passage_left
        panorama_height = TOP - BACKGROUND_BOTTOM
        if camera.y < BACKGROUND_BOTTOM:
            # Extend from the same edge at the same vertical texel density.
            lower_height = BACKGROUND_BOTTOM - BOTTOM
            source_height = round(self.background.h * lower_height / panorama_height)
            crop = (0, self.background.h - source_height, self.background.w, self.background.h)
            draw_structure(self.background, crop, camera, (passage_left + WIDTH) / 2, BOTTOM,
                           panorama_width, lower_height, flip="v")
        self.background.draw_to_origin(*camera.world_to_screen(passage_left, BACKGROUND_BOTTOM),
                                       panorama_width * camera.zoom, panorama_height * camera.zoom)
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

        passage = (min(passage_left, C_PASSAGE[0] - 105), C_PASSAGE[1], C_APPROACH_LEDGE[2], C_APPROACH_LEDGE[3])
        passage_base = 104  # Keep the ledge depth when extending its surface into C.
        entry = (A_ENTRY[0], A_ENTRY[1], A_ENTRY[2] + 110, A_ENTRY[3])
        for name, bounds, base_y in (("root-wedge", entry, None),
                                     ("connected-guard-wall", SHIELD_LEDGE, LEFT_WALL[1]),
                                     ("connected-passage", passage, passage_base),
                                     ("spike-bed-pier", PILLBUG_LEDGE, SPIKE_TIP_Y - 113)):
            draw_ruin_platform(camera, self.platform_images[name], self.platforms[name], bounds, base_y=base_y)

        for x, surface, size in ((1200, C_APPROACH_LEDGE[3], 66), (2760, SHIELD_LEDGE[3], 86),
                                 (3530, PILLBUG_LEDGE[3], 66)):
            draw_structure(self.marker, (207, 15, 1040, 1206), camera, x, surface, size * .70, size)
        draw_structure(self.rubble, (88, 133, 1454, 882), camera, 4880, A_ENTRY[3], 219, 122)
        self.draw_hazards(camera)
        self.draw_ceiling(camera, screen_height)

    def draw_hazards(self, camera):
        for (left, bottom, right, top), hanging in THORN_WALLS:
            if right > camera.x and left < camera.x + camera.view_width:
                draw_structure(self.thorn_wall, THORN_WALL_CROP, camera, (left + right) / 2, bottom,
                               right - left, top - bottom, flip="hv" if hanging else "")
        for left, bottom, right, top in SPIKE_SHELVES:
            if right <= camera.x or left >= camera.x + camera.view_width:
                continue
            name = "waterworn-sill"
            count = ceil((right - left) / 490)
            stride = (right - left) / count
            for index in range(count):
                start = max(left, left + index * stride - 20)
                end = min(right, left + (index + 1) * stride + 20)
                if start < camera.x + camera.view_width and end > camera.x:
                    draw_ruin_platform(camera, self.platform_images[name], self.platforms[name],
                                       (start, bottom, end, top), base_y=bottom)
            draw_spike_bank(self.spikes, camera, left, right, SPIKE_TIP_Y)
        if camera.y < BOTTOM + SPIKE_HEIGHT:
            draw_spike_bank(self.spikes, camera, 0, WIDTH, BOTTOM + SPIKE_HEIGHT)

    def draw_ceiling(self, camera, screen_height):
        # Overlap the canopy strips and feather their ends into the painted roof.
        # Drawing over the hazards tucks both hanging thorn walls into the roots.
        view_right = camera.x + camera.view_width
        view_top = camera.y + screen_height / camera.zoom
        for left, right, top, height, flipped in CEILING_SPANS:
            bottom = top - height
            if right <= camera.x or left >= view_right or bottom >= view_top or top <= camera.y:
                continue
            stops = ((left, 0), (left + 260, 255), (right - 170, 255), (right, 0))
            vertices, indices = [], []
            for index, (x, alpha) in enumerate(stops):
                u = (x - left) / (right - left)
                if flipped:
                    u = 1 - u
                for y, v in ((top, 0), (bottom, 1)):
                    sx, sy = camera.world_to_screen(x, y)
                    vertices.append(pico.SDL_Vertex((sx, screen_height - sy), (255, 255, 255, alpha), (u, v)))
                if index:
                    first = 2 * (index - 1)
                    indices.extend((first, first + 1, first + 2, first + 1, first + 2, first + 3))
            geometry = (pico.SDL_Vertex * len(vertices))(*vertices)
            triangles = (c_int * len(indices))(*indices)
            pico.SDL_RenderGeometry(pico.renderer, self.canopy.texture, geometry, len(vertices),
                                    triangles, len(indices))

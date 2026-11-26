"""Draw the B-part scenery and terrain using the approved asset anchors."""

from ctypes import byref, c_int
import json
from math import ceil

from pico2d import pico2d as pico

from lower_route_atmosphere import ROUTE_ART, RouteAtmosphere, draw_parallax, load_image
from lower_route_b_layout import (A_ENTRY, BOTTOM, C_APPROACH_LEDGE, C_PASSAGE,
                                  LEFT_WALL, PILLBUG_LEDGE, RIGHT_WALL, SECRET_FLOOR,
                                  SECRET_FLOOR_Y, SECRET_LEFT_WALL, SECRET_PASSAGE, SECRET_RELIC_X, SHIELD_LEDGE,
                                  STONE_SHELVES, STONE_SURFACE, THORN_WALL_CROP, THORN_WALLS, TOP, WIDTH)
from player import ASSET_ROOT


STRUCTURES = ASSET_ROOT / "structures/map1-lower-route"
PLATFORMS = ASSET_ROOT / "terrain/ruin-platforms"
FLOOR_DECOR = ASSET_ROOT / "terrain/moss-grotto-floor-decor"
ROCK_CORE = (8, 16, 23)
AMBER_RELIC_CROP = (287, 158, 946, 1103)
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


def fill_rock(camera, screen_height, bounds, color=ROCK_CORE):
    left, bottom, right, top = bounds
    x1, y1 = map(round, camera.world_to_screen(left, bottom))
    x2, y2 = map(round, camera.world_to_screen(right, top))
    pico.SDL_SetRenderDrawColor(pico.renderer, *color, 255)
    rect = pico.SDL_Rect(x1, screen_height - y2, x2 - x1, y2 - y1)
    pico.SDL_RenderFillRect(pico.renderer, rect)


def draw_amber_light(camera, screen_height):
    x, y = SECRET_RELIC_X, SECRET_FLOOR_Y + 48
    rim = ((-145, 0), (-100, 78), (0, 110), (100, 78), (145, 0),
           (100, -78), (0, -110), (-100, -78))
    vertices = []
    for index, (dx, dy) in enumerate(((0, 0), *rim)):
        sx, sy = camera.world_to_screen(x + dx, y + dy)
        alpha = 140 if index == 0 else 0
        vertices.append(pico.SDL_Vertex((sx, screen_height - sy), (226, 139, 53, alpha)))
    data = (pico.SDL_Vertex * len(vertices))(*vertices)
    triangles = (c_int * 24)(*(value for i in range(8) for value in (0, i + 1, (i + 1) % 8 + 1)))
    previous = pico.SDL_BlendMode()
    pico.SDL_GetRenderDrawBlendMode(pico.renderer, byref(previous))
    pico.SDL_SetRenderDrawBlendMode(pico.renderer, pico.SDL_BLENDMODE_BLEND)
    try:
        pico.SDL_RenderGeometry(pico.renderer, None, data, len(data), triangles, len(triangles))
    finally:
        pico.SDL_SetRenderDrawBlendMode(pico.renderer, previous)


class LowerRouteBArt:
    def __init__(self):
        self.background = load_image(ROUTE_ART / "bc-far.png")
        self.atmosphere = RouteAtmosphere()
        self.wall = pico.load_image(str(ASSET_ROOT / "terrain/green-cavern-wall-v1.png"))
        self.marker = pico.load_image(str(STRUCTURES / "lower-cave-safe-waymarker-v1.png"))
        self.rubble = pico.load_image(str(STRUCTURES / "lower-cave-landing-rubble-v1.png"))
        self.thorn_wall = pico.load_image(str(STRUCTURES / "lower-cave-thorn-wall-v1.png"))
        self.canopy = pico.load_image(str(ASSET_ROOT / "terrain/green-cavern-canopy-v1.png"))
        self.amber_relic = pico.load_image(str(ASSET_ROOT / "sprites/relic/amber-fossil-v1.png"))
        pico.SDL_SetTextureScaleMode(self.amber_relic.texture, pico.SDL_ScaleModeLinear)
        self.rock_chips = pico.load_image(str(FLOOR_DECOR / "moss-rock-chips.png"))
        self.bead_moss = pico.load_image(str(FLOOR_DECOR / "bead-moss-patch.png"))
        pico.SDL_SetTextureColorMod(self.rubble.texture, 139, 175, 186)
        self.platforms = json.loads((PLATFORMS / "manifest.json").read_text(encoding="utf-8"))["platforms"]
        self.platform_images = {
            name: pico.load_image(str(PLATFORMS / self.platforms[name]["image"]))
            for name in ("root-wedge", "connected-guard-wall", "connected-passage", "spike-bed-pier",
                         "waterworn-sill")
        }

    def draw(self, camera, screen_height, *, passage_left=C_PASSAGE[0], backdrop_right=WIDTH,
             secret_revealed=False, secret_relic_collected=False, draw_entry=True):
        self.draw_depth(camera, screen_height, passage_left, backdrop_right)
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
        if draw_entry:
            entry = (A_ENTRY[0], A_ENTRY[1], A_ENTRY[2] + 110, A_ENTRY[3])
            draw_ruin_platform(camera, self.platform_images["root-wedge"], self.platforms["root-wedge"], entry)
            draw_structure(self.rubble, (88, 133, 1454, 882), camera, 4880, A_ENTRY[3], 219, 122)
        for name, bounds, base_y in (("connected-guard-wall", SHIELD_LEDGE, LEFT_WALL[1]),
                                     ("connected-passage", passage, passage_base),
                                     ("spike-bed-pier", PILLBUG_LEDGE, -313)):
            draw_ruin_platform(camera, self.platform_images[name], self.platforms[name], bounds, base_y=base_y)

        for x, surface, size in ((1200, C_APPROACH_LEDGE[3], 66), (2760, SHIELD_LEDGE[3], 86),
                                 (3530, PILLBUG_LEDGE[3], 66)):
            draw_structure(self.marker, (207, 15, 1040, 1206), camera, x, surface, size * .70, size)
        for x, surface, width in ((996, C_APPROACH_LEDGE[3], 130), (2260, SHIELD_LEDGE[3], 94),
                                  (3170, PILLBUG_LEDGE[3], 110)):
            draw_structure(self.bead_moss, (114, 134, 2053, 585), camera, x, surface - 9, width, 21)
        self.draw_hazards(camera)
        if camera.y < STONE_SURFACE:
            self.draw_basement(camera, screen_height, secret_revealed, secret_relic_collected)
        self.draw_ceiling(camera, screen_height)

    def draw_depth(self, camera, screen_height, passage_left, backdrop_right):
        draw_parallax(self.background, camera, screen_height,
                      (passage_left, BOTTOM, backdrop_right, TOP + 240), (216, 218, 204))
        self.atmosphere.draw_ruin(camera, "broken-arch", 1030, 245, 900, 530)
        self.atmosphere.draw_ruin(camera, "stele", 2610, -90, 420, 570, flip="h")
        self.atmosphere.draw_ruin(camera, "broken-arch", 4120, 128, 1050, 690, flip="h")
        self.atmosphere.draw_light(camera, 3310, 163, 1630, 1390)
        self.atmosphere.draw_light(camera, 590, 480, 1330, 1090, strength=112)
        if passage_left < C_PASSAGE[0]:
            self.atmosphere.draw_ruin(camera, "stele", -650, 540, 400, 580)
            self.atmosphere.draw_ruin(camera, "broken-arch", -30, 525, 790, 540)
            self.atmosphere.draw_light(camera, -260, 550, 980, 790, strength=170)

    def draw_hazards(self, camera):
        for (left, bottom, right, top), hanging in THORN_WALLS:
            if right > camera.x and left < camera.x + camera.view_width:
                draw_structure(self.thorn_wall, THORN_WALL_CROP, camera, (left + right) / 2, bottom,
                               right - left, top - bottom, flip="hv" if hanging else "")

    def draw_stone_surface(self, camera, left, right, top, *, depth=106):
        name = "waterworn-sill"
        count = ceil((right - left) / 490)
        stride = (right - left) / count
        for index in range(count):
            start = max(left, left + index * stride - 20)
            end = min(right, left + (index + 1) * stride + 20)
            if start < camera.x + camera.view_width and end > camera.x:
                draw_ruin_platform(camera, self.platform_images[name], self.platforms[name],
                                   (start, top - depth, end, top), base_y=top - depth)

    def draw_basement(self, camera, screen_height, revealed, collected):
        left, floor, mouth, ceiling = SECRET_PASSAGE
        if not revealed:
            fill_rock(camera, screen_height, SECRET_PASSAGE)
        if revealed and not collected:
            draw_amber_light(camera, screen_height)
        for bounds in (*STONE_SHELVES, SECRET_FLOOR, SECRET_LEFT_WALL):
            fill_rock(camera, screen_height, bounds)
        for shelf_left, _, shelf_right, shelf_top in STONE_SHELVES:
            self.draw_stone_surface(camera, shelf_left, shelf_right, shelf_top)
        right = SECRET_FLOOR[2]
        draw_rock_wall(self.wall, camera, ((ceiling, mouth - 55, mouth),
                                           (-415, mouth - 90, mouth),
                                           (STONE_SURFACE, mouth - 65, mouth)), screen_height)
        draw_rock_wall(self.wall, camera, ((floor, right, right + 80),
                                           (-520, right, right + 104),
                                           (STONE_SURFACE, right, right + 65)), screen_height)
        self.draw_stone_surface(camera, left if revealed else mouth, right, floor, depth=68)
        if revealed:
            draw_structure(self.canopy, (0, 160, self.canopy.w, 474), camera,
                           (left + mouth) / 2, ceiling - 12, mouth - left, 60)
            draw_rock_wall(self.wall, camera, ((floor, left - 65, left),
                                               (-585, left - 70, left),
                                               (ceiling, left - 39, left)), screen_height)
            draw_structure(self.rock_chips, (225, 235, 1370, 730), camera, SECRET_RELIC_X, floor, 128, 24)
            draw_structure(self.bead_moss, (114, 134, 2053, 585), camera, 1090, floor, 108, 19)
            if not collected:
                draw_structure(self.amber_relic, AMBER_RELIC_CROP, camera, SECRET_RELIC_X,
                               floor + 18, 44, 63)

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

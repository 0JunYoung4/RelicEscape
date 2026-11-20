"""The opening cave and the breakaway floor in front of the sigil slab."""

from ctypes import byref, c_int
from math import ceil, inf

from pico2d import pico2d as pico

from player import ASSET_ROOT


WORLD_WIDTH = 6000
GROUND_Y = 420
CEILING_START_Y = GROUND_Y + 440
CEILING_Y = GROUND_Y + 740
CEILING_STEP = 40


def ceiling_height_at(x):
    progress = max(0.0, min(1.0, (x - 600) / 4000))
    progress = progress * progress * (3 - 2 * progress)
    return CEILING_START_Y + (CEILING_Y - CEILING_START_Y) * progress


CEILING_SPANS = tuple(
    (left, min(left + CEILING_STEP, WORLD_WIDTH), round(ceiling_height_at(left + CEILING_STEP / 2)))
    for left in range(0, WORLD_WIDTH, CEILING_STEP)
)
SPAWN = (380, GROUND_Y, 0.0)
# Preserve the existing end boundary; the rune wall is now painted into the backdrop.
END_WALL_X = WORLD_WIDTH - 740 * 681 / 2138
DOOR_X = (END_WALL_X + WORLD_WIDTH) / 2
BACKDROP_IMAGE = ASSET_ROOT / "terrain/opening-cave-backdrop-rune-v7.png"
FLOOR_IMAGE = ASSET_ROOT / "terrain/opening-cave-floor-v1.png"
SHADOW_IMAGE = ASSET_ROOT / "terrain/opening-cave-stalactite-shadow-v1.png"
SHADOW_TILE_WIDTH = 1260
# World units per source pixel; the 1024px lower chamber spans over two camera widths.
SHAFT_SCALE = 4
SHAFT_TOP = -140
SHAFT_FLOOR = SHAFT_TOP - 1421 * SHAFT_SCALE
# Trim the transparent export margin; pico2D source coordinates start at the bottom.
FLOOR_ART_HEIGHT = 580
TERRAIN = (
    (0, 0, WORLD_WIDTH, GROUND_Y),
    *((left, height, right, inf) for left, right, height in CEILING_SPANS),
    (END_WALL_X, GROUND_Y, WORLD_WIDTH, inf),
)
PIT_LEFT = END_WALL_X - 340
BROKEN_TERRAIN = ((0, 0, PIT_LEFT, GROUND_Y), (END_WALL_X, 0, WORLD_WIDTH, GROUND_Y), *TERRAIN[1:])
# Width, delay and falling acceleration for each slab, ordered left to right.
FLOOR_SLABS = ((37, .22, 870), (60, .09, 1040), (49, 0, 1240),
               (68, .035, 1150), (45, .12, 960), (51, .19, 1100), (30, .27, 930))
# Bottom-left source rectangles in the breakaway floor atlas.
SLAB_FRAMES = ((31, 288, 198, 177), (259, 251, 389, 214), (668, 256, 308, 209),
               (993, 220, 427, 245), (1447, 265, 184, 199), (1651, 256, 337, 208),
               (2016, 276, 134, 189))


class OpeningCave:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.backdrop = pico.load_image(str(BACKDROP_IMAGE))
        self.shaft = pico.load_image(str(ASSET_ROOT / "terrain/opening-fall-shaft-v4.png"))
        pico.SDL_SetTextureColorMod(self.shaft.texture, 154, 163, 174)
        self.emission = pico.load_image(str(ASSET_ROOT / "terrain/opening-slab-edge-emission.png"))
        pico.SDL_SetTextureBlendMode(self.emission.texture, pico.SDL_BLENDMODE_ADD)
        self.fissure = pico.load_image(str(ASSET_ROOT / "terrain/opening-sigil-emission.png"))
        pico.SDL_SetTextureBlendMode(self.fissure.texture, pico.SDL_BLENDMODE_ADD)
        self.floor = pico.load_image(str(FLOOR_IMAGE))
        self.slabs = pico.load_image(str(ASSET_ROOT / "terrain/opening-collapse-slabs.png"))
        self.stalactites = pico.load_image(str(SHADOW_IMAGE))
        # Darken terrain only. The player is drawn afterwards at its normal brightness.
        pico.SDL_SetTextureColorMod(self.backdrop.texture, 76, 80, 88)
        pico.SDL_SetTextureColorMod(self.floor.texture, 158, 164, 174)
        pico.SDL_SetTextureColorMod(self.stalactites.texture, 96, 104, 112)

    def draw_descent(self, camera, player):
        bottom = SHAFT_TOP - self.shaft.h * SHAFT_SCALE
        # In the painting the shaft opens at row 1005; finish pulling back above the floor.
        depth = (SHAFT_TOP - player.y) / SHAFT_SCALE
        u = min(1.0, max(0.0, (depth - 1005) / 380))
        camera.zoom = camera.normal_zoom * (1 - 0.26 * u * u * (3 - 2 * u))
        camera.x = player.x - camera.view_width / 2
        camera.y = max(SHAFT_FLOOR - self.height * 0.20 / camera.zoom,
                       min(SHAFT_TOP - self.height / camera.zoom,
                                   player.y - self.height * 0.50 / camera.zoom))
        scale = SHAFT_SCALE * camera.zoom
        self.shaft.draw_to_origin((self.width - self.shaft.w * scale) / 2,
                                  (bottom - camera.y) * camera.zoom,
                                  self.shaft.w * scale, self.shaft.h * scale)

    def _draw_rock(self, camera, left, right, surface_y, depth):
        left = max(left, camera.x)
        right = min(right, camera.x + camera.view_width)
        if left >= right:
            return
        scale = depth / FLOOR_ART_HEIGHT
        tile_width = self.floor.w * scale
        for tile in range(int(left // tile_width), ceil(right / tile_width)):
            tile_left = tile * tile_width
            start, end = max(left, tile_left), min(right, tile_left + tile_width)
            source_left = round((start - tile_left) / scale)
            source_right = min(self.floor.w, round((end - tile_left) / scale))
            x1, x2 = round((start - camera.x) * camera.zoom), round((end - camera.x) * camera.zoom)
            if x1 == x2 or source_left == source_right:
                continue
            y = surface_y - depth / 2
            self.floor.clip_composite_draw(
                source_left, 0, source_right - source_left, FLOOR_ART_HEIGHT,
                0, "", (x1 + x2) / 2, round((y - camera.y) * camera.zoom),
                x2 - x1, round(depth * camera.zoom),
            )

    def _draw_entrance_light(self, camera):
        if camera.x >= 780:
            return
        positions = ((0, GROUND_Y), (0, GROUND_Y + 420), (780, GROUND_Y + 260), (780, GROUND_Y))
        near, far = (26, 49, 62, 140), (26, 49, 62, 0)
        vertices = (pico.SDL_Vertex * 4)(*(
            pico.SDL_Vertex((x, self.height - y), near if index < 2 else far)
            for index, position in enumerate(positions)
            for x, y in (camera.world_to_screen(*position),)
        ))
        indices = (c_int * 6)(0, 1, 2, 0, 2, 3)
        previous_blend = pico.SDL_BlendMode()
        pico.SDL_GetRenderDrawBlendMode(pico.renderer, byref(previous_blend))
        pico.SDL_SetRenderDrawBlendMode(pico.renderer, pico.SDL_BLENDMODE_BLEND)
        try:
            pico.SDL_RenderGeometry(pico.renderer, None, vertices, 4, indices, 6)
        finally:
            pico.SDL_SetRenderDrawBlendMode(pico.renderer, previous_blend)

    def _draw_shaft(self, camera):
        # Vertical rock faces catch a little light at the broken lips of the shaft.
        depth = GROUND_Y
        levels = (0, 12, 29, 53, 91, 130, 183, 250, depth)
        profiles = (
            (PIT_LEFT, 1, (0, 9, 5, 20, 13, 25, 17, 33, 36)),
            (END_WALL_X, -1, (0, 7, 16, 9, 22, 17, 35, 26, 38)),
        )
        for edge, direction, profile in profiles:
            points = []
            for i, (below, inset) in enumerate(zip(levels, profile)):
                shade = max(0.12, 1 - below / 240)
                facet = (22 if i % 3 else 35) * shade
                for offset, value in ((-12, facet), (inset, facet * .75),
                                      (inset + 15, facet * .15)):
                    x, y = camera.world_to_screen(edge + direction * offset, GROUND_Y - below)
                    points.append(pico.SDL_Vertex((x, self.height - y),
                        (int(value * .57), int(value * .8), int(value), 255)))
            indices = []
            for row in range(len(levels) - 1):
                for column in range(2):
                    first = row * 3 + column
                    indices.extend(first + offset for offset in (0, 1, 3, 1, 4, 3))
            pico.SDL_RenderGeometry(pico.renderer, None, (pico.SDL_Vertex * len(points))(*points),
                                    len(points), (c_int * len(indices))(*indices), len(indices))

    def draw_foreground(self, camera):
        source_width, source_height = self.stalactites.w - 16, self.stalactites.h - 6
        width = SHADOW_TILE_WIDTH * camera.zoom
        for left, right, roof in CEILING_SPANS:
            left, right = max(left, camera.x), min(right, camera.x + camera.view_width)
            if left >= right:
                continue
            ceiling = round(camera.world_to_screen(0, roof)[1])
            x1, x2 = round((left - camera.x) * camera.zoom), round((right - camera.x) * camera.zoom)
            pico.draw_rectangle(x1, ceiling, x2 - 1, self.height - 1, 0, 0, 0, filled=True)
            # Shorter tips in the low entrance leave the full jump silhouette readable.
            openness = (roof - CEILING_START_Y) / (CEILING_Y - CEILING_START_Y)
            height = width * source_height / source_width * (0.35 + 0.35 * openness)
            top = ceiling + height * 0.14
            for tile in range(int(left // SHADOW_TILE_WIDTH), ceil(right / SHADOW_TILE_WIDTH)):
                tile_left = tile * SHADOW_TILE_WIDTH
                start, end = max(left, tile_left), min(right, tile_left + SHADOW_TILE_WIDTH)
                source_start = round((start - tile_left) / SHADOW_TILE_WIDTH * source_width)
                source_end = round((end - tile_left) / SHADOW_TILE_WIDTH * source_width)
                if tile % 2:
                    source_left = 8 + source_width - source_end
                else:
                    source_left = 8 + source_start
                x1, x2 = round((start - camera.x) * camera.zoom), round((end - camera.x) * camera.zoom)
                self.stalactites.clip_composite_draw(
                    source_left, 0, source_end - source_start, source_height, 0,
                    "h" if tile % 2 else "", (x1 + x2) / 2, top - height / 2,
                    x2 - x1, height,
                )

    def draw(self, camera, *, show_hitboxes=False, sigil_light=0.0, collapse_time=None):
        pico.SDL_SetRenderDrawColor(pico.renderer, 0, 0, 0, 255)
        pico.SDL_RenderClear(pico.renderer)
        # One panorama is fixed to the world: no repeated wall motifs or distant parallax.
        width = WORLD_WIDTH * camera.zoom
        self.backdrop.draw_to_origin(
            -camera.x * camera.zoom, -camera.y * camera.zoom,
            width, width * self.backdrop.h / self.backdrop.w,
        )
        if sigil_light > 0:
            # Authored against the 128 x 402 source patch starting at (2044, 237).
            scale = width / self.backdrop.w
            x = 2044 * scale - camera.x * camera.zoom
            y = (self.backdrop.h - 639) * scale - camera.y * camera.zoom
            # Additive passes let the outer seam rise above its original brightness.
            for layer in range(ceil(sigil_light)):
                alpha = min(1, sigil_light - layer)
                pico.SDL_SetTextureAlphaMod(self.emission.texture, round(255 * alpha))
                self.emission.draw_to_origin(x, y, 128 * scale, 402 * scale)
            # Sample only the central groove of the original 256 x 804 emission map.
            vertices = []
            for sy, gain in ((216, 0), (255, 1), (485, 1)):
                alpha = round(58 * sigil_light * gain)
                for sx in (90, 174):
                    vertices.append(pico.SDL_Vertex(
                        (x + sx * scale / 2, self.height - y - (804 - sy) * scale / 2),
                        (255, 255, 255, alpha), (sx / 256, sy / 804)))
            triangles = (c_int * 12)(0, 1, 2, 1, 3, 2, 2, 3, 4, 3, 5, 4)
            pico.SDL_RenderGeometry(pico.renderer, self.fissure.texture,
                                    (pico.SDL_Vertex * 6)(*vertices), 6, triangles, 12)
        self._draw_entrance_light(camera)

        surface = round(camera.world_to_screen(0, GROUND_Y)[1])
        pico.draw_rectangle(0, 0, self.width - 1, surface - 1, 0, 0, 0, filled=True)
        if collapse_time is None:
            self._draw_rock(camera, 0, WORLD_WIDTH, GROUND_Y, GROUND_Y)
        else:
            self._draw_rock(camera, 0, PIT_LEFT, GROUND_Y, GROUND_Y)
            self._draw_rock(camera, END_WALL_X, WORLD_WIDTH, GROUND_Y, GROUND_Y)
            self._draw_shaft(camera)
            left = PIT_LEFT
            for i, (width, delay, acceleration) in enumerate(FLOOR_SLABS):
                elapsed = collapse_time - delay
                top = GROUND_Y - acceleration * max(0, elapsed) ** 2
                if elapsed <= 0:
                    self._draw_rock(camera, left, left + width, GROUND_Y, GROUND_Y)
                elif top > camera.y:
                    frame = SLAB_FRAMES[i]
                    height = width * frame[3] / frame[2]
                    x, y = camera.world_to_screen(left + width / 2, top - height / 2)
                    tilt = min(elapsed, 1) * (0.48 if i % 2 else -0.38)
                    self.slabs.clip_composite_draw(*frame, tilt, "", x, y,
                                                   width * camera.zoom, height * camera.zoom)
                left += width
        for left, right, roof in CEILING_SPANS:
            if right <= camera.x or left >= camera.x + camera.view_width:
                continue
            x1, y = camera.world_to_screen(left, roof)
            x2, _ = camera.world_to_screen(right, roof)
            pico.draw_rectangle(round(x1), round(y), round(x2) - 1, self.height - 1, 0, 0, 0, filled=True)

        if show_hitboxes:
            for left, bottom, right, top in (TERRAIN if collapse_time is None else BROKEN_TERRAIN):
                if right <= camera.x or left >= camera.x + camera.view_width:
                    continue
                x1, y1 = camera.world_to_screen(left, bottom)
                x2, y2 = camera.world_to_screen(right, top)
                pico.draw_rectangle(x1, y1, x2, self.height - 1 if top == inf else y2, 76, 220, 220)

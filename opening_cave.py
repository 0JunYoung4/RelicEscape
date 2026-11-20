"""The small, dark opening cave, before the collapse is implemented."""

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
# Trim the transparent export margin; pico2D source coordinates start at the bottom.
FLOOR_ART_HEIGHT = 580
TERRAIN = (
    (0, 0, WORLD_WIDTH, GROUND_Y),
    *((left, height, right, inf) for left, right, height in CEILING_SPANS),
    (END_WALL_X, GROUND_Y, WORLD_WIDTH, inf),
)


class OpeningCave:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.backdrop = pico.load_image(str(BACKDROP_IMAGE))
        self.floor = pico.load_image(str(FLOOR_IMAGE))
        self.stalactites = pico.load_image(str(SHADOW_IMAGE))
        # Darken terrain only. The player is drawn afterwards at its normal brightness.
        pico.SDL_SetTextureColorMod(self.backdrop.texture, 76, 80, 88)
        pico.SDL_SetTextureColorMod(self.floor.texture, 158, 164, 174)
        pico.SDL_SetTextureColorMod(self.stalactites.texture, 96, 104, 112)

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

    def draw(self, camera, *, show_hitboxes=False):
        pico.SDL_SetRenderDrawColor(pico.renderer, 0, 0, 0, 255)
        pico.SDL_RenderClear(pico.renderer)
        # One panorama is fixed to the world: no repeated wall motifs or distant parallax.
        width = WORLD_WIDTH * camera.zoom
        self.backdrop.draw_to_origin(
            -camera.x * camera.zoom, -camera.y * camera.zoom,
            width, width * self.backdrop.h / self.backdrop.w,
        )
        self._draw_entrance_light(camera)

        surface = round(camera.world_to_screen(0, GROUND_Y)[1])
        pico.draw_rectangle(0, 0, self.width - 1, surface - 1, 0, 0, 0, filled=True)
        self._draw_rock(camera, 0, WORLD_WIDTH, GROUND_Y, GROUND_Y)
        for left, right, roof in CEILING_SPANS:
            if right <= camera.x or left >= camera.x + camera.view_width:
                continue
            x1, y = camera.world_to_screen(left, roof)
            x2, _ = camera.world_to_screen(right, roof)
            pico.draw_rectangle(round(x1), round(y), round(x2) - 1, self.height - 1, 0, 0, 0, filled=True)

        if show_hitboxes:
            for left, bottom, right, top in TERRAIN:
                if right <= camera.x or left >= camera.x + camera.view_width:
                    continue
                x1, y1 = camera.world_to_screen(left, bottom)
                x2, y2 = camera.world_to_screen(right, top)
                pico.draw_rectangle(x1, y1, x2, self.height - 1 if top == inf else y2, 76, 220, 220)

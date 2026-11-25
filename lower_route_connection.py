"""A walkable join with one world scale and a shared camera."""

from ctypes import c_int
from math import ceil

from pico2d import pico2d as pico

from lower_route_a import EXIT_LEDGE
from lower_route_b import PLAY_TERRAIN
from lower_route_b_layout import A_ENTRY, BOTTOM, WIDTH as B_WIDTH
from player import ASSET_ROOT


PASSAGE_LEFT = B_WIDTH
PASSAGE_RIGHT = PASSAGE_LEFT + 900
PASSAGE_FLOOR = A_ENTRY[3]
PASSAGE_CENTER = (PASSAGE_LEFT + PASSAGE_RIGHT) / 2
A_ORIGIN = (PASSAGE_RIGHT, PASSAGE_FLOOR - EXIT_LEDGE[3])


class LowerRouteConnection:
    def __init__(self, route_a):
        self.plate = pico.load_image(str(ASSET_ROOT / "terrain/lower-route-ab-passage-v1.png"))
        pico.SDL_SetTextureBlendMode(self.plate.texture, pico.SDL_BLENDMODE_BLEND)
        self.ground_y = BOTTOM
        self.terrain = (*PLAY_TERRAIN, *route_a.terrain,
                        (PASSAGE_LEFT, BOTTOM, PASSAGE_RIGHT, PASSAGE_FLOOR),
                        (PASSAGE_RIGHT, BOTTOM, route_a.world_width, route_a.ground_y))

    @staticmethod
    def blend(x, b_value, a_value):
        # Use the same horizontal transition for ordinary and relic camera framing.
        progress = max(0.0, min(1.0, (x - (PASSAGE_LEFT - 200)) / (PASSAGE_RIGHT - PASSAGE_LEFT + 600)))
        weight = progress * progress * (3 - 2 * progress)
        return b_value + (a_value - b_value) * weight

    def draw(self, camera, screen_height):
        start, end = PASSAGE_LEFT - 310, PASSAGE_RIGHT + 330
        if camera.x >= end or camera.x + camera.view_width <= start:
            return
        # The walk line in the panorama is at source row 371. Feather both ends
        # over the authored shelves, keeping the actual gap panel fully opaque.
        art_top = PASSAGE_FLOOR + 371 * 2.5
        art_bottom = art_top - self.plate.h * 2.5
        view_left, view_right = camera.x, camera.x + camera.view_width
        bottom = max(art_bottom, camera.y)
        top = min(art_top, camera.y + screen_height / camera.zoom)
        if top <= bottom:
            return
        rows = ceil((top - bottom) * camera.zoom / 100)
        stops = ((start, 0), (PASSAGE_LEFT - 155, 140), (PASSAGE_LEFT, 255),
                 (PASSAGE_RIGHT, 255), (PASSAGE_RIGHT + 165, 140), (end, 0))
        vertices, indices = [], []
        for (x1, alpha1), (x2, alpha2) in zip(stops, stops[1:]):
            left, right = max(view_left, x1), min(view_right, x2)
            if right <= left:
                continue
            offset = len(vertices)
            for row in range(rows + 1):
                y = bottom + (top - bottom) * row / rows
                v = (art_top - y) / (art_top - art_bottom)
                for x in (left, right):
                    opacity = round(alpha1 + (alpha2 - alpha1) * (x - x1) / (x2 - x1))
                    u = (820 + (x - start) * 860 / (end - start)) / self.plate.w
                    sx, sy = camera.world_to_screen(x, y)
                    vertices.append(pico.SDL_Vertex((sx, screen_height - sy), (255, 255, 255, opacity), (u, v)))
                if row > 0:
                    first = offset + (row - 1) * 2
                    indices.extend((first, first + 1, first + 2, first + 1, first + 2, first + 3))
        geometry = (pico.SDL_Vertex * len(vertices))(*vertices)
        triangles = (c_int * len(indices))(*indices)
        pico.SDL_RenderGeometry(pico.renderer, self.plate.texture, geometry, len(vertices), triangles, len(indices))

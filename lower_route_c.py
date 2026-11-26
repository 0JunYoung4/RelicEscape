"""The passage and checkpoint before the first boss entrance."""

from ctypes import c_int
from math import ceil

from pico2d import pico2d as pico

from lower_route_atmosphere import ROUTE_ART, load_image
from lower_route_b_layout import C_PASSAGE, C_PASSAGE_LEFT, STONE_SURFACE, TOP
from pillbug import Pillbug
from player import ASSET_ROOT


LEFT, RIGHT = C_PASSAGE_LEFT, C_PASSAGE[0]
FLOOR = C_PASSAGE[3]
ENTRANCE_X = -1290
ENTRANCE_WIDTH = 220
CHECKPOINT = (-710, FLOOR, 0.0)
CHECKPOINT_RADIUS = 115
FLOOR_BOUNDS = (LEFT, STONE_SURFACE, RIGHT, FLOOR)
ART_FLOOR_ROW = 589
ART_DOOR_COLUMN = 254
ART_CHECKPOINT_COLUMN = 624
ART_LAMP_ROW = 510
ART_SCALE = (CHECKPOINT[0] - ENTRANCE_X) / (ART_CHECKPOINT_COLUMN - ART_DOOR_COLUMN)
ART_LEFT = ENTRANCE_X - ART_DOOR_COLUMN * ART_SCALE
ART_BLEND_END = RIGHT + 690
TERRAIN = (
    FLOOR_BOUNDS,
    (LEFT, FLOOR, ENTRANCE_X + ENTRANCE_WIDTH / 2, TOP),
    (LEFT, 1270, RIGHT, TOP),
)


def _subdivide(stops, max_span):
    for (start, first), (end, last) in zip(stops, stops[1:]):
        steps = ceil(abs(end - start) / max_span)
        for index in range(steps):
            fraction = index / steps
            yield start + (end - start) * fraction, first + (last - first) * fraction
    yield stops[-1]


class LowerRouteC:
    def __init__(self):
        self.plate = load_image(ROUTE_ART / "c-terrain.png")
        pico.SDL_SetTextureBlendMode(self.plate.texture, pico.SDL_BLENDMODE_BLEND)
        self.lamp_glow = pico.load_image(str(ASSET_ROOT / "sprites/relic/relic-blue-glow-v1.png"))
        pico.SDL_SetTextureBlendMode(self.lamp_glow.texture, pico.SDL_BLENDMODE_ADD)
        pico.SDL_SetTextureScaleMode(self.lamp_glow.texture, pico.SDL_ScaleModeLinear)
        pico.SDL_SetTextureAlphaMod(self.lamp_glow.texture, 180)
        self.enemies = (
            Pillbug.on_platform((-527, FLOOR_BOUNDS[1], -302, FLOOR)),
            Pillbug.on_platform((-260, FLOOR_BOUNDS[1], -32, FLOOR)),
        )
        self.checkpoint_reached = False

    def check_arrival(self, player):
        if player.grounded and player.y == FLOOR and abs(player.x - CHECKPOINT[0]) <= CHECKPOINT_RADIUS:
            self.checkpoint_reached = True

    def draw(self, camera, screen_height):
        if camera.x >= ART_BLEND_END or camera.x + camera.view_width <= ART_LEFT:
            return
        self.draw_plate(camera, screen_height)
        if self.checkpoint_reached:
            lamp_y = FLOOR + (ART_FLOOR_ROW - ART_LAMP_ROW) * ART_SCALE
            x, y = camera.world_to_screen(CHECKPOINT[0], lamp_y)
            floor_x, floor_y = camera.world_to_screen(CHECKPOINT[0], FLOOR)
            self.lamp_glow.draw(floor_x, floor_y + 4 * camera.zoom, 175 * camera.zoom, 44 * camera.zoom)
            self.lamp_glow.draw(x, y, 90 * camera.zoom, 90 * camera.zoom)

    def draw_plate(self, camera, screen_height):
        # The same walk line anchors both the painted rock and the existing passage into B.
        columns = ((ART_LEFT, 255), (RIGHT, 255), (RIGHT + 180, 218),
                   (RIGHT + 510, 37), (ART_BLEND_END, 0))
        last_row = self.plate.h - .5
        art_top = FLOOR + ART_FLOOR_ROW * ART_SCALE
        art_bottom = FLOOR + (ART_FLOOR_ROW - last_row) * ART_SCALE
        rows = ((art_top, 0), (FLOOR, ART_FLOOR_ROW),
                (art_bottom, last_row), (STONE_SURFACE, last_row))
        # Keep the same fade and source anchors within SDL's software triangle limits.
        max_span = 400 / camera.zoom
        columns = tuple(_subdivide(columns, max_span))
        rows = tuple(_subdivide(rows, max_span))
        vertices, indices = [], []
        stride = len(columns)
        for row, (y, pixel_y) in enumerate(rows):
            for column, (x, alpha) in enumerate(columns):
                sx, sy = camera.world_to_screen(x, y)
                u = (x - ART_LEFT) / (ART_SCALE * self.plate.w)
                v = pixel_y / self.plate.h
                vertices.append(pico.SDL_Vertex((sx, screen_height - sy), (255, 255, 255, round(alpha)), (u, v)))
                if row and column:
                    a = (row - 1) * stride + column - 1
                    b = a + stride
                    indices.extend((a, a + 1, b, a + 1, b + 1, b))
        geometry = (pico.SDL_Vertex * len(vertices))(*vertices)
        triangles = (c_int * len(indices))(*indices)
        pico.SDL_RenderGeometry(pico.renderer, self.plate.texture, geometry, len(geometry), triangles, len(triangles))

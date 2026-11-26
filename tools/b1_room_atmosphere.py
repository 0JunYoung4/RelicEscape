"""Small world-space motes for the B1 ceiling light and plant clusters."""

from ctypes import byref
from math import pi, sin
from random import Random

from pico2d import pico2d as pico

from render_mesh import VERTEX_SIZE, index_buffer, pack_vertex, vertex_buffer
from tools.b1_room_art import BEAM_FLOOR_X, BEAM_MOUTH, WORLD_PER_ART_PIXEL
from tools.preview_b1_intro import GROUND


class B1Motes:
    def __init__(self):
        rng = Random(251)
        self.dust = tuple((rng.random(), rng.uniform(-1, 1), rng.uniform(.72, 1.5))
                          for _ in range(17))
        self.spores = tuple((x + rng.uniform(-31, 31), y, rng.random(), rng.uniform(.75, 1.35))
                            for x, y in ((538, 686), (782, 684), (1606, 683), (1938, 682))
                            for _ in range(3))
        count = len(self.dust) + len(self.spores)
        corners = (0, 1, 2, 0, 2, 3, 0, 3, 4, 0, 4, 1)
        self.indices = index_buffer(tuple(5 * i + corner for i in range(count) for corner in corners))
        self.vertices = vertex_buffer(count * 5)

    def _write(self, index, camera, height, x, y, radius, alpha, color):
        scale = WORLD_PER_ART_PIXEL
        sx, sy = camera.world_to_screen(x * scale, (GROUND - y) * scale)
        sy = height - sy
        # Keep soft points rasterizable at wide zooms on the SDL software renderer.
        r = max(1.65, radius * scale * camera.zoom)
        for vertex, (dx, dy) in enumerate(((0, 0), (-r, 0), (0, -r), (r, 0), (0, r))):
            pack_vertex(self.vertices, (index * 5 + vertex) * VERTEX_SIZE,
                        sx + dx, sy + dy, *color, 0 if vertex else alpha, 0, 0)

    def draw(self, camera, elapsed_ms):
        height = pico.get_canvas_height()
        seconds = elapsed_ms / 1000
        for index, (seed, side, radius) in enumerate(self.dust):
            age = (seed + seconds * .061) % 1
            x = BEAM_MOUTH[0] + (BEAM_FLOOR_X - BEAM_MOUTH[0]) * age
            x += side * (22 + 62 * age) + 7 * sin(seed * 19 + seconds * .54)
            y = BEAM_MOUTH[1] + 568 * age
            self._write(index, camera, height, x, y, radius, round(88 * sin(pi * age)), (174, 204, 171))
        for index, (x, y, seed, radius) in enumerate(self.spores, len(self.dust)):
            age = (seed + seconds * .09) % 1
            x += 11 * sin(6 * age + seed * 14)
            self._write(index, camera, height, x, y - 61 * age, radius, round(69 * sin(pi * age)),
                        (140, 185, 139))

        previous = pico.SDL_BlendMode()
        pico.SDL_GetRenderDrawBlendMode(pico.renderer, byref(previous))
        pico.SDL_SetRenderDrawBlendMode(pico.renderer, pico.SDL_BLENDMODE_BLEND)
        try:
            pico.SDL_RenderGeometry(pico.renderer, None, self.vertices, len(self.vertices),
                                    self.indices, len(self.indices))
        finally:
            pico.SDL_SetRenderDrawBlendMode(pico.renderer, previous)

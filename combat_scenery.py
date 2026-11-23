"""Combat-only depth, soft background light, and world-anchored root silhouettes."""

from contextlib import contextmanager
from ctypes import byref, c_int
from math import ceil, cos, floor, sin, tau

from pico2d import pico2d as pico

from player import ASSET_ROOT


class CombatScenery:
    def __init__(self, width, height):
        self.width, self.height = width, height
        terrain = ASSET_ROOT / "terrain"
        self.ruins = pico.load_image(str(terrain / "green-combat-midground-ruins-v1.png"))
        self.roots = pico.load_image(str(terrain / "green-combat-foreground-roots-v1.png"))
        pico.SDL_SetTextureColorMod(self.ruins.texture, 140, 175, 190)
        pico.SDL_SetTextureAlphaMod(self.ruins.texture, 132)
        pico.SDL_SetTextureColorMod(self.roots.texture, 125, 150, 162)

    @contextmanager
    def room_clip(self, camera, left, right, ceiling, *, margin=0):
        """Never reveal the lower shaft, and respect a caller's existing SDL clip."""
        x1, y1 = camera.world_to_screen(left - margin, 0)
        x2, y2 = camera.world_to_screen(right + margin, ceiling)
        x1, x2 = max(0, floor(x1)), min(self.width, ceil(x2))
        y1, y2 = max(0, floor(self.height - y2)), min(self.height, ceil(self.height - y1))
        previous = pico.SDL_Rect()
        clipped = pico.SDL_RenderIsClipEnabled(pico.renderer)
        pico.SDL_RenderGetClipRect(pico.renderer, byref(previous))
        if clipped:
            x1, y1 = max(x1, previous.x), max(y1, previous.y)
            x2, y2 = min(x2, previous.x + previous.w), min(y2, previous.y + previous.h)
        if x2 <= x1 or y2 <= y1:
            yield False
            return
        clip = pico.SDL_Rect(x1, y1, x2 - x1, y2 - y1)
        pico.SDL_RenderSetClipRect(pico.renderer, byref(clip))
        try:
            yield True
        finally:
            pico.SDL_RenderSetClipRect(pico.renderer, byref(previous) if clipped else None)

    @contextmanager
    def alpha_geometry(self):
        previous = pico.SDL_BlendMode()
        pico.SDL_GetRenderDrawBlendMode(pico.renderer, byref(previous))
        pico.SDL_SetRenderDrawBlendMode(pico.renderer, pico.SDL_BLENDMODE_BLEND)
        try:
            yield
        finally:
            pico.SDL_SetRenderDrawBlendMode(pico.renderer, previous)

    def geometry(self, camera, points, colors, triangles):
        vertices = []
        for (x, y), color in zip(points, colors):
            sx, sy = camera.world_to_screen(x, y)
            vertices.append(pico.SDL_Vertex((sx, self.height - sy), color))
        data = (pico.SDL_Vertex * len(vertices))(*vertices)
        indices = (c_int * len(triangles))(*triangles)
        pico.SDL_RenderGeometry(pico.renderer, None, data, len(vertices), indices, len(triangles))

    def soft_light(self, camera, center, size, color, opacity):
        """A center and two rings avoid a hard ellipse around a light source."""
        cx, cy = center
        rx, ry = size
        points, colors = [(cx, cy)], [(*color, opacity)]
        steps = 32
        for radius, alpha in ((.42, opacity // 2), (1, 0)):
            for step in range(steps):
                angle = tau * step / steps
                points.append((cx + cos(angle) * rx * radius, cy + sin(angle) * ry * radius))
                colors.append((*color, alpha))
        triangles = []
        for step in range(steps):
            nxt = (step + 1) % steps
            triangles.extend((0, 1 + step, 1 + nxt,
                              1 + step, 1 + steps + step, 1 + nxt,
                              1 + nxt, 1 + steps + step, 1 + steps + nxt))
        self.geometry(camera, points, colors, triangles)

    def light_shaft(self, camera, left, right, ceiling):
        span = right - left
        points, colors = [], []
        # The opening is high on the right; the light spreads softly toward the center.
        rows = ((1.04, .72, 55, 0), (.86, .66, 100, 38),
                (.52, .55, 175, 46), (.19, .45, 235, 20), (.01, .40, 265, 0))
        for height, center, half_width, opacity in rows:
            for across, strength in ((-1, 0), (-.55, .5), (0, 1), (.55, .5), (1, 0)):
                points.append((left + span * center + half_width * across, ceiling * height))
                colors.append((160, 204, 185, round(opacity * strength)))
        triangles = []
        for row in range(len(rows) - 1):
            for column in range(4):
                first = row * 5 + column
                triangles.extend((first, first + 5, first + 1, first + 1, first + 5, first + 6))
        self.geometry(camera, points, colors, triangles)

    def draw_background(self, camera, left, right, ceiling):
        # Include the low entrance recess so its background shares the room's mood.
        with self.room_clip(camera, left - 360, right + 360, ceiling) as visible:
            if not visible:
                return
            span = right - left
            with self.alpha_geometry():
                # Unequal dark sides leave an open, brighter center behind combat.
                points = [(left + span * x, ceiling * y)
                          for y in (0, .50, 1) for x in (-.25, 0, .26, .58, 1, 1.25)]
                colors = [(4, 12, 22, alpha) for row in ((80, 80, 28, 8, 58, 58),
                                                        (104, 104, 24, 0, 70, 70),
                                                        (126, 126, 55, 10, 86, 86)) for alpha in row]
                triangles = []
                for row in range(2):
                    for column in range(5):
                        first = row * 6 + column
                        triangles.extend((first, first + 6, first + 1,
                                          first + 1, first + 6, first + 7))
                self.geometry(camera, points, colors, triangles)
            width = span * .84
            height = width * self.ruins.h / self.ruins.w
            self.ruins.draw_to_origin(*camera.world_to_screen(left + span * .08, -28),
                                      width * camera.zoom, height * camera.zoom)
            with self.alpha_geometry():
                self.soft_light(camera, (left + span * .51, ceiling * .43),
                                (span * .46, ceiling * .60), (77, 139, 148), 17)
                self.light_shaft(camera, left, right, ceiling)
                # Local air glow along the ruin's right pier, kept weaker than relic effects.
                self.soft_light(camera, (left + span * .78, 210), (120, 180), (110, 170, 152), 12)

    def draw_foreground(self, camera, left, right, ceiling):
        with self.room_clip(camera, left, right, ceiling, margin=64) as visible:
            if not visible:
                return
            # Both origins stay attached to the world ceiling at every camera height.
            for edge, top, height, flip in ((left - 100, ceiling + 60, 670, ""),
                                            (right + 80, ceiling + 28, 535, "h")):
                width = height * self.roots.w / self.roots.h
                x = edge + width / 2 if not flip else edge - width / 2
                y = top - height / 2
                self.roots.composite_draw(0, flip, *camera.world_to_screen(x, y),
                                          width * camera.zoom, height * camera.zoom)

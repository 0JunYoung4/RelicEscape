"""Combat-only depth, soft background light, and world-anchored root silhouettes."""

from contextlib import contextmanager
from ctypes import byref, c_int
from math import ceil, cos, floor, sin, tau

from pico2d import pico2d as pico

from player import ASSET_ROOT


COMBAT_BACKGROUND_TINT = (120, 145, 178)


class CombatScenery:
    def __init__(self, width, height):
        self.width, self.height = width, height
        terrain = ASSET_ROOT / "terrain"
        self.grotto = pico.load_image(str(terrain / "moss-combat-relic-grotto-v1.png"))
        self.seedpods = pico.load_image(str(terrain / "moss-combat-seedpods-v1.png"))
        self.roots = pico.load_image(str(terrain / "green-combat-foreground-roots-v1.png"))
        pico.SDL_SetTextureColorMod(self.roots.texture, 99, 123, 143)
        pico.SDL_SetTextureAlphaMod(self.seedpods.texture, 216)

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

    def draw_exit_seam(self, camera, x, strength):
        with self.alpha_geometry():
            self.soft_light(camera, (x, 12), (57, 57), (83, 195, 195), round(133 * strength))
            points = ((x - 18, 1), (x - 5, 3), (x + 4, 6),
                      (x - 5, 0), (x + 4, 2), (x + 16, 9))
            colors = [(174, 248, 240, round(alpha * strength))
                      for alpha in (0, 185, 245, 185, 245, 0)]
            self.geometry(camera, points, colors, (0, 3, 1, 1, 3, 2, 2, 3, 4, 2, 4, 5))

    def draw_background(self, camera, left, right, ceiling):
        with self.room_clip(camera, left - 360, right + 360, ceiling) as visible:
            if not visible:
                return
            width = (right - left) * 1.46
            height = width * self.grotto.h / self.grotto.w
            # Overscan lets the distant roots shift more slowly than the floor and walls.
            x = (left + right - width) / 2 + camera.x * .10
            y = -200 + camera.y * .12
            self.grotto.draw_to_origin(*camera.world_to_screen(x, y),
                                      width * camera.zoom, height * camera.zoom)

    def draw_floor_plants(self, camera, left, right, ceiling):
        with self.room_clip(camera, left, right, ceiling) as visible:
            if not visible:
                return
            for x, width, flip in ((left + 132, 260, ""), (right - 122, 214, "h")):
                height = width * self.seedpods.h / self.seedpods.w
                self.seedpods.composite_draw(0, flip, *camera.world_to_screen(x, height / 2 - 11),
                                             width * camera.zoom, height * camera.zoom)

    def draw_foreground(self, camera, left, right, ceiling):
        with self.room_clip(camera, left, right, ceiling, margin=64) as visible:
            if not visible:
                return
            # Both origins stay attached to the world ceiling at every camera height.
            for edge, top, height, flip in ((left - 68, ceiling + 60, 490, ""),
                                            (right + 54, ceiling + 28, 410, "h")):
                width = height * self.roots.w / self.roots.h
                x = edge + width / 2 if not flip else edge - width / 2
                y = top - height / 2
                self.roots.composite_draw(0, flip, *camera.world_to_screen(x, y),
                                          width * camera.zoom, height * camera.zoom)

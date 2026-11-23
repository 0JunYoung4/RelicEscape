"""Brief world-space sparks for confirmed sword hits."""

from ctypes import byref, c_int
from dataclasses import dataclass
from math import cos, pi, sin

from pico2d import pico2d as pico


IMPACT_DURATION = .23


@dataclass
class HitImpact:
    x: float
    y: float
    angle: float
    scale: float
    age: float = 0.0

    @classmethod
    def from_strike(cls, strike, body, facing, *, downward, heavy):
        x, y, width, height = body
        left, bottom = max(strike[0], x - width / 2), max(strike[1], y)
        right, top = min(strike[2], x + width / 2), min(strike[3], y + height)
        if downward:
            return cls((left + right) / 2, top - (top - bottom) * .25,
                       -pi / 2 + facing * .32, 1.0 if heavy else .62)
        return cls(left + (right - left) * (.34 if facing > 0 else .66), (bottom + top) / 2,
                   0 if facing > 0 else pi, 1.0 if heavy else .62)

    def draw(self, camera):
        vertices, indices = [], []

        def polygon(x, y, angle, points, color):
            start = len(vertices)
            cosine, sine = cos(angle), sin(angle)
            for dx, dy in points:
                sx, sy = camera.world_to_screen(
                    x + (dx * cosine - dy * sine) * self.scale,
                    y + (dx * sine + dy * cosine) * self.scale,
                )
                vertices.append(pico.SDL_Vertex((sx, pico.canvas_height - sy), color))
            for i in range(1, len(points) - 1):
                indices.extend((start, start + i, start + i + 1))

        t = self.age / IMPACT_DURATION
        flash = max(0, 1 - self.age / .095)
        if flash:
            # Use four triangles so the narrow rays meet at the actual contact.
            for turn, length in enumerate((37, 23, 25, 21)):
                angle = self.angle + .25 + turn * pi / 2
                reach = length * (.72 + .28 * flash)
                polygon(self.x, self.y, angle, ((0, -7), (reach, 0), (0, 7)),
                        (255, 190, 100, round(238 * flash)))
                polygon(self.x, self.y, angle, ((0, -4), (reach * .69, 0), (0, 4)),
                        (255, 249, 219, round(255 * flash)))

        for offset, speed, length in ((-.91, 208, 12), (-.52, 290, 22), (-.12, 345, 30),
                                      (.34, 308, 24), (.67, 255, 19), (1.10, 192, 15),
                                      (2.54, 156, 9)):
            angle = self.angle + offset
            distance = (13 + speed * self.age * (1 - .41 * t)) * self.scale
            x, y = self.x + distance * cos(angle), self.y + distance * sin(angle)
            reach = length * (1 - t)
            polygon(x, y, angle, ((-reach * .60, 0), (0, 2), (reach, 0), (0, -2)),
                    (255, 216, 149, round(241 * (1 - t))))

        for vx, vy, size in ((96, 110, 5), (184, 155, 6), (244, 69, 5), (-81, 116, 4),
                             (129, -64, 4), (206, -35, 3)):
            x = self.x + (vx * cos(self.angle) - vy * sin(self.angle)) * self.age * self.scale
            y = self.y + ((vx * sin(self.angle) + vy * cos(self.angle)) * self.age
                          - 185 * self.age**2) * self.scale
            polygon(x, y, self.angle + vx * self.age * .2,
                    ((-size, -size * .28), (size, -size * .28), (size * .33, size * .70)),
                    (219, 187, 133, round(212 * (1 - t))))

        blend = pico.SDL_BlendMode()
        pico.SDL_GetRenderDrawBlendMode(pico.renderer, byref(blend))
        pico.SDL_SetRenderDrawBlendMode(pico.renderer, pico.SDL_BLENDMODE_BLEND)
        try:
            points = (pico.SDL_Vertex * len(vertices))(*vertices)
            triangles = (c_int * len(indices))(*indices)
            pico.SDL_RenderGeometry(pico.renderer, None, points, len(points), triangles, len(triangles))
        finally:
            pico.SDL_SetRenderDrawBlendMode(pico.renderer, blend)

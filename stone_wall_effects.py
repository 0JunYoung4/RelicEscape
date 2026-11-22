"""Ground dust and a small screen-space rumble for the arena's stone blocker."""

from ctypes import byref, c_int
from dataclasses import dataclass
from math import cos, sin, tau
from random import Random

from pico2d import pico2d as pico


@dataclass
class DustPuff:
    x: float
    vx: float
    vy: float
    radius: float
    lifetime: float
    age: float = 0.0


class StoneWallEffects:
    def __init__(self, left, right):
        self.left, self.right = left, right
        self.random = Random(41)
        self.clear()

    def clear(self):
        self.puffs = []
        self.progress = 0.0
        self.direction = 0
        self.emission = 0.0
        self.time = 0.0
        self.shake_remaining = 0.0
        self.shake_duration = 0.0
        self.shake_strength = 0.0

    def burst(self, count):
        for _ in range(count):
            position = self.random.random()
            outward = -1 if position < .5 else 1
            self.puffs.append(DustPuff(
                self.left + (self.right - self.left) * position,
                outward * self.random.uniform(25, 85), self.random.uniform(16, 45),
                self.random.uniform(9, 17), self.random.uniform(.7, 1.1)))

    def impact(self, strength, duration):
        self.shake_strength = strength
        self.shake_remaining = self.shake_duration = duration

    def update(self, progress, dt):
        self.time += dt
        self.shake_remaining = max(0.0, self.shake_remaining - dt)
        for puff in self.puffs:
            puff.age += dt
        self.puffs[:] = [puff for puff in self.puffs if puff.age < puff.lifetime]
        delta = progress - self.progress
        direction = (delta > 0) - (delta < 0)
        if direction:
            if direction != self.direction:
                self.burst(12)
                self.impact(1.8, .16)
            # Emit only for the distance actually travelled, including long frames.
            self.emission += abs(delta) * 20
            count = int(self.emission + 1e-9)
            self.emission -= count
            self.burst(count)
            if progress in (0.0, 1.0):
                self.burst(14)
                self.impact(3.2, .28)
                direction = 0
        else:
            self.emission = 0.0
        self.direction = direction
        self.progress = progress

    def shake(self):
        strength = 1.1 if self.direction else 0.0
        if self.shake_remaining:
            strength = max(strength, self.shake_strength *
                           (self.shake_remaining / self.shake_duration) ** 2)
        return (sin(self.time * 91) * strength * .65,
                sin(self.time * 73 + .8) * strength)

    def draw(self, camera):
        if not self.puffs:
            return
        blend = pico.SDL_BlendMode()
        pico.SDL_GetRenderDrawBlendMode(pico.renderer, byref(blend))
        pico.SDL_SetRenderDrawBlendMode(pico.renderer, pico.SDL_BLENDMODE_BLEND)
        try:
            indices = (c_int * 36)(*(i for edge in range(12)
                                     for i in (0, edge + 1, (edge + 1) % 12 + 1)))
            for puff in self.puffs:
                age = puff.age
                fade = (1 - age / puff.lifetime) ** 1.4
                x = puff.x + puff.vx * age / (1 + age)
                y = 5 + puff.vy * age
                radius = puff.radius + age * 22
                sx, sy = camera.world_to_screen(x, y)
                alpha = round(105 * fade)
                vertices = [pico.SDL_Vertex((sx, pico.canvas_height - sy),
                                            (148, 156, 140, alpha))]
                for edge in range(12):
                    angle = tau * edge / 12
                    px, py = camera.world_to_screen(x + cos(angle) * radius,
                                                    max(1, y + sin(angle) * radius * .65))
                    vertices.append(pico.SDL_Vertex((px, pico.canvas_height - py),
                                                    (112, 128, 116, 0)))
                geometry = (pico.SDL_Vertex * len(vertices))(*vertices)
                pico.SDL_RenderGeometry(pico.renderer, None, geometry, len(vertices), indices, 36)
        finally:
            pico.SDL_SetRenderDrawBlendMode(pico.renderer, blend)

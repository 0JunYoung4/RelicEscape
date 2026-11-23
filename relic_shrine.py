"""World-anchored shrine, ceiling shafts and drifting illuminated dust."""

import json
from ctypes import byref, c_int
from math import sin
from time import perf_counter

from pico2d import pico2d as pico

from player import ASSET_ROOT


class RelicShrine:
    def __init__(self, height):
        self.height = height
        path = ASSET_ROOT / "concepts/relic-acquisition-shrine-v1.json"
        self.metadata = json.loads(path.read_text(encoding="utf-8"))
        self.stone = pico.load_image(str(path.parent / self.metadata["image"]))
        self.glow = pico.load_image(str(ASSET_ROOT / "sprites/relic/relic-blue-glow-v1.png"))
        pico.SDL_SetTextureBlendMode(self.glow.texture, pico.SDL_BLENDMODE_ADD)
        pico.SDL_SetTextureScaleMode(self.glow.texture, pico.SDL_ScaleModeLinear)
        self.started = perf_counter()

    def draw_stone(self, camera, x):
        anchor, ground = self.metadata["ground_anchor"]
        scale = self.metadata["world_height"] / ground
        self.stone.draw_to_origin(*camera.world_to_screen(x - anchor * scale,
            -(self.stone.h - ground) * scale), self.stone.w * scale * camera.zoom,
            self.stone.h * scale * camera.zoom)

    def glow_at(self, camera, x, y, width, height, alpha):
        pico.SDL_SetTextureAlphaMod(self.glow.texture, round(alpha))
        self.glow.draw(*camera.world_to_screen(x, y), width * camera.zoom, height * camera.zoom)

    def draw_light(self, camera, x, y, ceiling, *, collected=False, elapsed=None):
        if x + 650 < camera.x or x - 650 > camera.x + camera.view_width:
            return
        elapsed = perf_counter() - self.started if elapsed is None else elapsed
        pulse = .94 + .06 * sin(elapsed * 1.3)
        # The quiet daylight remains after pickup; the magical halo disappears.
        strength = (.55 if collected else 1) * pulse
        previous = pico.SDL_BlendMode()
        pico.SDL_GetRenderDrawBlendMode(pico.renderer, byref(previous))
        pico.SDL_SetRenderDrawBlendMode(pico.renderer, pico.SDL_BLENDMODE_ADD)
        try:
            for offset, width, opacity in ((-75, 125, 30), (20, 74, 47), (100, 32, 32)):
                vertices, indices = [], []
                # Feather both sides and the foot instead of drawing solid triangles.
                for row, (height, spread, fade) in enumerate(((ceiling + 24, .32, .45),
                        (ceiling - 85, .48, 1), (y + 110, 1, .65), (0, 1.15, 0))):
                    center = x + 175 * height / ceiling + offset
                    for across, weight in ((-1, 0), (-.55, .5), (0, 1), (.55, .5), (1, 0)):
                        sx, sy = camera.world_to_screen(center + width * spread * across, height)
                        vertices.append(pico.SDL_Vertex((sx, self.height - sy),
                            (154, 211, 240, round(opacity * fade * weight * strength))))
                    if row < 3:
                        for col in range(4):
                            start = row * 5 + col
                            indices.extend((start, start + 5, start + 1,
                                            start + 1, start + 5, start + 6))
                data = (pico.SDL_Vertex * len(vertices))(*vertices)
                triangles = (c_int * len(indices))(*indices)
                pico.SDL_RenderGeometry(pico.renderer, None, data, len(vertices), triangles, len(indices))
            self.glow_at(camera, x + 175, ceiling - 18, 165, 75, 95 * strength)
            self.glow_at(camera, x + 25, 25, 540, 90, 105 * strength)
            self.glow_at(camera, x, 170, 460, 440, 48 * strength)
            if not collected:
                self.glow_at(camera, x, y, 225, 210, 155 * pulse)
                self.glow_at(camera, x, y, 70, 65, 110 * pulse)
            for index in range(22):
                height = 32 + (index * 137.7 + elapsed * (9 + index % 5)) % (ceiling - 65)
                center = x + 175 * height / ceiling
                drift = sin(elapsed * .35 + index * 2.4) * 28
                px = center + (index * 73 % 210) - 105 + drift
                alpha = (32 + 65 * (.5 + .5 * sin(elapsed * .8 + index))) * strength
                size = 5 + index % 3 * 2
                self.glow_at(camera, px, height, size, size, alpha)
        finally:
            pico.SDL_SetTextureAlphaMod(self.glow.texture, 255)
            pico.SDL_SetRenderDrawBlendMode(pico.renderer, previous)

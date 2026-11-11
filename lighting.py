"""Composite ambient and relic lighting over the map."""

from pico2d import pico2d as pico


AMBIENT_COLOR = (128, 128, 140)
RELIC_LIGHT_DIAMETER = 216


class Lighting:
    def __init__(self, width, height, glow_path):
        self.height = height
        self.glow = pico.load_image(str(glow_path))
        if pico.SDL_SetTextureBlendMode(self.glow.texture, pico.SDL_BLENDMODE_ADD) != 0:
            raise RuntimeError(pico.SDL_GetError())
        if pico.SDL_SetTextureScaleMode(self.glow.texture, pico.SDL_ScaleModeLinear) != 0:
            raise RuntimeError(pico.SDL_GetError())

        texture = pico.SDL_CreateTexture(
            pico.renderer, pico.SDL_PIXELFORMAT_RGBA8888, pico.SDL_TEXTUREACCESS_TARGET,
            width, height,
        )
        if not texture:
            raise RuntimeError(pico.SDL_GetError())
        self.light_map = pico.Image(texture)
        if pico.SDL_SetTextureBlendMode(texture, pico.SDL_BLENDMODE_MOD) != 0:
            raise RuntimeError(pico.SDL_GetError())

    def apply(self, relic_center):
        previous_target = pico.SDL_GetRenderTarget(pico.renderer)
        if pico.SDL_SetRenderTarget(pico.renderer, self.light_map.texture) != 0:
            raise RuntimeError(pico.SDL_GetError())
        try:
            pico.SDL_SetRenderDrawColor(pico.renderer, *AMBIENT_COLOR, 255)
            pico.SDL_RenderClear(pico.renderer)
            if relic_center is not None:
                self.draw_glow(relic_center, RELIC_LIGHT_DIAMETER, RELIC_LIGHT_DIAMETER)
        finally:
            if pico.SDL_SetRenderTarget(pico.renderer, previous_target) != 0:
                raise RuntimeError(pico.SDL_GetError())

        # Multiply map colors by the light map, then add the compact visible halo.
        pico.SDL_RenderCopy(pico.renderer, self.light_map.texture, None, None)
        if relic_center is not None:
            self.draw_glow(relic_center, self.glow.w, self.glow.h)

    def draw_glow(self, center, width, height, *, alpha=255):
        if alpha == 0:
            return
        x, y = center
        bounds = pico.SDL_FRect(x - width / 2, self.height - y - height / 2, width, height)
        if alpha != 255:
            pico.SDL_SetTextureAlphaMod(self.glow.texture, alpha)
        try:
            pico.SDL_RenderCopyF(pico.renderer, self.glow.texture, None, bounds)
        finally:
            if alpha != 255:
                pico.SDL_SetTextureAlphaMod(self.glow.texture, 255)

"""Shared forest-cave surfaces, distant scenery and dark foreground framing."""

import json
from ctypes import byref, c_int
from math import ceil, floor, sin
from time import perf_counter

from pico2d import pico2d as pico

from player import ASSET_ROOT


WALL_SKIN_WIDTH = 360
WALL_TILE_HEIGHT = 1536


class MossCaveArt:
    def __init__(self, width, height):
        self.width, self.height = width, height
        root = ASSET_ROOT / "terrain"
        self.background = pico.load_image(str(root / "green-cavern-background-v1.png"))
        self.floor = pico.load_image(str(root / "green-cavern-floor-v1.png"))
        self.platform = pico.load_image(str(root / "green-cavern-platform-v1.png"))
        self.wall = pico.load_image(str(root / "green-cavern-wall-v1.png"))
        self.canopy = pico.load_image(str(root / "green-cavern-canopy-v1.png"))
        self.corner_ivy = pico.load_image(str(root / "green-cavern-corner-ivy-v1.png"))
        self.pillar = pico.load_image(str(root / "green-cavern-ground-pillar-v2.png"))
        self.floor_art = json.loads((root / "green-cavern-floor-v1.json").read_text(encoding="utf-8"))
        self.platform_art = json.loads((root / "green-cavern-platform-v1.json").read_text(encoding="utf-8"))
        self.corner_art = json.loads((root / "green-cavern-corner-ivy-v1.json").read_text(encoding="utf-8"))
        self.pillar_art = json.loads((root / "green-cavern-ground-pillar-v2.json").read_text(encoding="utf-8"))
        pico.SDL_SetTextureColorMod(self.background.texture, 172, 199, 214)
        self.started = perf_counter()

    def draw_background(self, camera):
        height = self.height * 1.24
        width = height * self.background.w / self.background.h
        left = (self.width - width) / 2 - camera.x * camera.zoom * .16
        bottom = max(self.height - height, min(0, (self.height - height) / 2 - camera.y * camera.zoom * .08))
        for tile in range(floor(-left / width), ceil((self.width - left) / width)):
            self.background.draw_to_origin(left + tile * width, bottom, width + 1, height)

    def draw_platform(self, camera, bounds):
        left, bottom, right, top = bounds
        image = self.platform
        height = (top - bottom) * image.h / (image.h - self.platform_art["surface_y"])
        image.draw_to_origin(*camera.world_to_screen(left, bottom),
                             (right - left) * camera.zoom, height * camera.zoom)

    def draw_pillar(self, camera, bounds):
        """Align the solid stone with collision, leaving foliage outside the block."""
        left, bottom, right, top = bounds
        image = self.pillar
        stone_left, surface, stone_right, ground = self.pillar_art["collision_rect"]
        scale_x = (right - left) / (stone_right - stone_left)
        scale_y = (top - bottom) / (ground - surface)
        origin_x = left - stone_left * scale_x
        origin_y = bottom - (image.h - ground) * scale_y
        image.draw_to_origin(*camera.world_to_screen(origin_x, origin_y),
                             image.w * scale_x * camera.zoom, image.h * scale_y * camera.zoom)

    def draw_corner(self, camera, x, y, *, width=120, right_wall=False, grow_up=False, alpha=1.0):
        image = self.corner_ivy
        anchor_x, anchor_y = self.corner_art["anchor"]
        if right_wall:
            anchor_x = image.w - anchor_x
        if grow_up:
            anchor_y = image.h - anchor_y
        scale = width / image.w
        center_x = x + (image.w / 2 - anchor_x) * scale
        center_y = y + (anchor_y - image.h / 2) * scale
        flip = ("h" if right_wall else "") + ("v" if grow_up else "")
        pico.SDL_SetTextureAlphaMod(image.texture, round(255 * alpha))
        try:
            image.composite_draw(0, flip, *camera.world_to_screen(center_x, center_y),
                                 width * camera.zoom, image.h * scale * camera.zoom)
        finally:
            pico.SDL_SetTextureAlphaMod(image.texture, 255)

    def draw_floor(self, camera, left, right, top, depth=128, *, tiled=True):
        """Put the authored walk line on the actual collision plane."""
        image = self.floor
        surface = self.floor_art["surface_y"]
        height = depth * image.h / (image.h - surface)
        bottom = top - depth
        # An opaque rock core also prevents hairline gaps between textured mesh strips.
        pico.draw_rectangle(*camera.world_to_screen(left, bottom),
                            *camera.world_to_screen(right, top), 0, 0, 0, filled=True)
        tile_width = 640 if tiled else right - left
        start_tile = floor(left / tile_width) if tiled else 0
        end_tile = ceil(right / tile_width) if tiled else 1
        for tile in range(start_tile, end_tile):
            origin = tile * tile_width if tiled else left
            start, end = max(left, origin), min(right, origin + tile_width)
            if end <= start or end < camera.x or start > camera.x + camera.view_width:
                continue
            source_left = round((start - origin) / tile_width * image.w)
            source_right = round((end - origin) / tile_width * image.w)
            if source_right <= source_left:
                continue
            self.draw_surface(camera, image, start, bottom, end - start, height,
                              source_left=source_left, source_right=source_right)

    def draw_surface(self, camera, image, left, bottom, width, height, *, source_left=0,
                     source_right=None, profile_origin=None, amount=1.0):
        """Give decorative stone and moss a continuous uneven edge, without moving collision."""
        source_right = image.w if source_right is None else source_right
        profile_origin = left if profile_origin is None else profile_origin
        steps = max(1, ceil(width / 24))
        vertices, indices = [], []
        for index in range(steps + 1):
            part = index / steps
            x = left + width * part
            profile_x = profile_origin + width * part
            lift = amount * max(0, 4 + 4 * sin(profile_x * .031) + 2.5 * sin(profile_x * .071 + 1.3))
            u = (source_left + (source_right - source_left) * part) / image.w
            for y, v in ((bottom + lift, 1), (bottom + height + lift, 0)):
                sx, sy = camera.world_to_screen(x, y)
                vertices.append(pico.SDL_Vertex((sx, self.height - sy), (255, 255, 255, 255), (u, v)))
            if index < steps:
                first = index * 2
                indices.extend((first, first + 1, first + 2, first + 1, first + 2, first + 3))
        geometry = (pico.SDL_Vertex * len(vertices))(*vertices)
        triangles = (c_int * len(indices))(*indices)
        pico.SDL_RenderGeometry(pico.renderer, image.texture, geometry, len(vertices), triangles, len(indices))

    def draw_wall(self, camera, face, bottom, top, *, right_wall=False, skin_width=WALL_SKIN_WIDTH):
        image = self.wall
        source_width = min(image.w, round(skin_width / WALL_SKIN_WIDTH * image.w))
        for y in range(floor(bottom / WALL_TILE_HEIGHT) * WALL_TILE_HEIGHT,
                       ceil(top / WALL_TILE_HEIGHT) * WALL_TILE_HEIGHT, WALL_TILE_HEIGHT):
            low, high = max(bottom, y), min(top, y + WALL_TILE_HEIGHT)
            source_bottom = round((low - y) / WALL_TILE_HEIGHT * image.h)
            source_top = round((high - y) / WALL_TILE_HEIGHT * image.h)
            if source_top <= source_bottom:
                continue
            x = face if right_wall else face - skin_width
            sx, sy = camera.world_to_screen(x + skin_width / 2, (low + high) / 2)
            image.clip_composite_draw(image.w - source_width, source_bottom, source_width,
                source_top - source_bottom, 0, "h" if right_wall else "", sx, sy,
                skin_width * camera.zoom, (high - low) * camera.zoom)

    def draw_canopy(self, camera, roof):
        """Attach hanging roots to the map ceiling, independent of the viewport."""
        width = 1120
        height = width * self.canopy.h / self.canopy.w
        top = roof + 30
        screen_roof = camera.world_to_screen(0, roof)[1]
        if screen_roof < self.height:
            pico.draw_rectangle(0, max(0, ceil(screen_roof)), self.width, self.height,
                                0, 0, 0, filled=True)
        bottom = top - height
        # The uneven silhouette can hang another 19 world units below the strip.
        if bottom - 19 > camera.y + self.height / camera.zoom or top < camera.y:
            return
        for tile in range(floor(camera.x / width), ceil((camera.x + camera.view_width) / width)):
            self.draw_surface(camera, self.canopy, tile * width, bottom,
                              width + 2, height,
                              profile_origin=tile * width, amount=-1.8)

    def draw_motes(self, camera, floor_y, ceiling_y, *, left=0, right=None):
        right = camera.world_width if right is None else right
        elapsed = perf_counter() - self.started
        blend = pico.SDL_BlendMode()
        pico.SDL_GetRenderDrawBlendMode(pico.renderer, byref(blend))
        pico.SDL_SetRenderDrawBlendMode(pico.renderer, pico.SDL_BLENDMODE_BLEND)
        try:
            for index in range(32):
                x = left + ((index * 347.7 + sin(elapsed * .13 + index) * 20) % max(1, right - left))
                y = floor_y + 55 + ((index * 123.3 + elapsed * (5 + index % 4)) % max(1, ceiling_y - floor_y - 120))
                sx, sy = camera.world_to_screen(x, y)
                if not (0 <= sx < self.width and 0 <= sy < self.height):
                    continue
                alpha = round(65 + 65 * (.5 + .5 * sin(elapsed * .8 + index)))
                radius = 1 if index % 5 else 2
                pico.draw_circle(round(sx), round(sy), radius, 162, 205, 158, alpha, filled=True)
        finally:
            pico.SDL_SetRenderDrawBlendMode(pico.renderer, blend)

    def shadow_floor(self, camera, top):
        _, surface = camera.world_to_screen(0, top)
        _, deep = camera.world_to_screen(0, top - 56)
        bottom = max(0, round(deep))
        if bottom > 0:
            pico.draw_rectangle(0, 0, self.width, bottom, 0, 0, 0, filled=True)
        vertices = (pico.SDL_Vertex * 4)(
            pico.SDL_Vertex((0, self.height - surface), (0, 0, 0, 0)),
            pico.SDL_Vertex((self.width, self.height - surface), (0, 0, 0, 0)),
            pico.SDL_Vertex((0, self.height - deep), (0, 0, 0, 255)),
            pico.SDL_Vertex((self.width, self.height - deep), (0, 0, 0, 255)))
        indices = (c_int * 6)(0, 1, 2, 1, 3, 2)
        blend = pico.SDL_BlendMode()
        pico.SDL_GetRenderDrawBlendMode(pico.renderer, byref(blend))
        pico.SDL_SetRenderDrawBlendMode(pico.renderer, pico.SDL_BLENDMODE_BLEND)
        try:
            pico.SDL_RenderGeometry(pico.renderer, None, vertices, 4, indices, 6)
        finally:
            pico.SDL_SetRenderDrawBlendMode(pico.renderer, blend)

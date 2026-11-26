"""Layered moss chamber art and the post-combat floor collapse."""

import json
from contextlib import contextmanager
from ctypes import byref, c_int
from math import ceil, cos, floor, radians, sin, tau

from PIL import Image
from pico2d import pico2d as pico

from combat_room_lighting import CombatRoomLighting
from combat_vegetation import CombatVegetation
from player import ASSET_ROOT


COMBAT_BACKGROUND_TINT = (172, 191, 224)
COMBAT_ART_PATH = ASSET_ROOT / "terrain" / "combat-room-v2"
COMBAT_ART = json.loads((COMBAT_ART_PATH / "manifest.json").read_text(encoding="utf-8"))
FAR_STELES = (
    (342, 110, 172, 428, ""),
    (565, 126, 143, 471, "h"),
    (1430, 134, 184, 397, "h"),
)
MIDGROUND_RUINS = (
    ("midground-stele", 416, -30, 332, 492),
    ("midground-broken-arch", 1110, -36, 432, 354),
)
FALLING_ROCKS = ((.10, .05, 19, -26), (.29, .02, -8, 34), (.48, 0, -24, -21),
                 (.68, .035, 16, 25), (.89, .06, 26, -32))


def _load_distant_stele():
    """Mix the stele with the cavern air and keep its original cutout."""
    with Image.open(COMBAT_ART_PATH / "midground-stele.png") as source:
        stele = source.convert("RGBA")
    stele.thumbnail((360, 450), Image.Resampling.LANCZOS)
    air = Image.new("RGB", stele.size, (23, 53, 66))
    distant = Image.blend(stele.convert("RGB"), air, .76)
    distant.putalpha(stele.getchannel("A"))

    width, height = distant.size
    texture = pico.SDL_CreateTexture(pico.renderer, pico.SDL_PIXELFORMAT_RGBA32,
                                     pico.SDL_TEXTUREACCESS_STATIC, width, height)
    if not texture:
        raise RuntimeError(pico.SDL_GetError())
    image = pico.Image(texture)
    if pico.SDL_UpdateTexture(texture, None, distant.tobytes(), width * 4) != 0:
        raise RuntimeError(pico.SDL_GetError())
    pico.SDL_SetTextureBlendMode(texture, pico.SDL_BLENDMODE_BLEND)
    pico.SDL_SetTextureScaleMode(texture, pico.SDL_ScaleModeLinear)
    return image


class CombatScenery:
    def __init__(self, width, height):
        self.width, self.height = width, height
        names = ("background", "foreground", "gate", "shaft", "vine-joint", "vine-wall", "vine-ceiling",
                 *COMBAT_ART["terrain_origins"], *(entry[0] for entry in COMBAT_ART["platform_surfaces"]),
                 *(entry[0] for entry in MIDGROUND_RUINS))
        self.images = {name: pico.load_image(str(COMBAT_ART_PATH / f"{name}.png")) for name in names}
        self.room_width = self.images["floor"].w
        for image in self.images.values():
            pico.SDL_SetTextureScaleMode(image.texture, pico.SDL_ScaleModeLinear)
        pico.SDL_SetTextureColorMod(self.images["background"].texture, *COMBAT_BACKGROUND_TINT)
        self.distant_stele = _load_distant_stele()
        self.seedpods = pico.load_image(str(ASSET_ROOT / "terrain" / "moss-combat-seedpods-v1.png"))
        pico.SDL_SetTextureAlphaMod(self.seedpods.texture, 205)
        self.lighting = CombatRoomLighting(self)
        self.vegetation = CombatVegetation(height)

    @contextmanager
    def room_clip(self, camera, left, right, ceiling, *, margin=0, bottom=0):
        """Clip art to the room and preserve a caller's existing SDL clip."""
        x1, y1 = camera.world_to_screen(left - margin, bottom)
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

    def draw_background(self, camera, left, right, ceiling, *, broken=False):
        bottom = -36 if broken else 0
        with self.room_clip(camera, 0, self.room_width - 12, ceiling + 30, bottom=bottom) as visible:
            if not visible:
                return
            width = self.room_width * 1.14
            far_dx, far_dy = camera.x * .10, camera.y * .10
            x = (left + right - width) / 2 + far_dx
            far_bottom = -80 + far_dy
            self.draw_sprite("background", camera, x, far_bottom, width, ceiling + 176)
            for sx, sy, sw, sh, flip in FAR_STELES:
                center = camera.world_to_screen(sx + sw / 2 + far_dx, sy + sh / 2 + far_dy)
                self.distant_stele.composite_draw(0, flip, *center, sw * camera.zoom, sh * camera.zoom)
            # Keep the illustration's central glow behind the two brighter world-space shafts.
            with self.alpha_geometry():
                self.soft_light(camera, (x + width * .566, far_bottom + ceiling * .945),
                                (410, 490), (9, 25, 39), 168)
            self.lighting.draw_rear(camera, ceiling)
        # Background color can reach the top of the shaft. Ruins, plants and light stop at the room floor.
        with self.room_clip(camera, 0, self.room_width - 12, ceiling) as visible:
            if visible:
                self.draw_hanging_roots(camera, ceiling)
                self.draw_midground(camera, ceiling)
                self.vegetation.draw_background(camera, tint_at=self.vegetation_tint(ceiling))
                self.lighting.draw_midair(camera, ceiling)

    def vegetation_tint(self, ceiling):
        return lambda x, y, tint, strength: self.lighting.surface_tint(x, y, ceiling, tint, strength)

    def draw_hanging_roots(self, camera, ceiling):
        """Deep-rooted silhouettes remain visible when the near roof is above the camera."""
        roots = self.images["vine-ceiling"]
        pico.SDL_SetTextureColorMod(roots.texture, 68, 103, 112)
        try:
            self.draw_sprite("vine-ceiling", camera, 417, ceiling - 334, 437, 346)
            self.draw_sprite("vine-ceiling", camera, 1170, ceiling - 316, 450, 331)
        finally:
            pico.SDL_SetTextureColorMod(roots.texture, 255, 255, 255)

    def draw_midground(self, camera, ceiling):
        """Light the ruin surfaces independently of the distant ring and play terrain."""

        def shade(x, y, v):
            ambient = (round(104 + 47 * v), round(146 + 39 * v), round(169 + 27 * v))
            return self.lighting.surface_tint(x, y, ceiling, ambient, .55 + .45 * v)

        for name, left, bottom, width, height in MIDGROUND_RUINS:
            self.draw_lit_sprite(name, camera, left + camera.x * .035, bottom + camera.y * .055,
                                 width, height, shade, columns=5, rows=5)

    def draw_lit_sprite(self, name, camera, left, bottom, width, height, shade, *, columns, rows):
        """Sample the local light across a textured layer while preserving its silhouette."""
        vertices, triangles = [], []
        for row in range(rows):
            v = row / (rows - 1)
            y = bottom + v * height
            for col in range(columns):
                u = col / (columns - 1)
                x = left + u * width
                sx, sy = camera.world_to_screen(x, y)
                vertices.append(pico.SDL_Vertex((sx, self.height - sy), (*shade(x, y, v), 255), (u, 1 - v)))
                if row and col:
                    i = row * columns + col
                    triangles.extend((i - columns - 1, i - columns, i - 1, i - columns, i, i - 1))
        data = (pico.SDL_Vertex * len(vertices))(*vertices)
        indices = (c_int * len(triangles))(*triangles)
        pico.SDL_RenderGeometry(pico.renderer, self.images[name].texture,
                                data, len(vertices), indices, len(triangles))

    def draw_sprite(self, name, camera, x, bottom, width=None, height=None):
        image = self.images[name]
        width = image.w if width is None else width
        height = width * image.h / image.w if height is None else height
        image.draw_to_origin(*camera.world_to_screen(x, bottom), width * camera.zoom, height * camera.zoom)

    def draw_terrain(self, camera, platforms, exit_left, exit_right, ceiling, *, broken):
        floor = self.images["floor"]
        _, bottom = COMBAT_ART["terrain_origins"]["floor"]
        sections = ((0, round(exit_left)), (round(exit_right), floor.w)) if broken else ((0, floor.w),)
        for x0, x1 in sections:
            floor.clip_draw_to_origin(x0, 0, x1 - x0, floor.h, *camera.world_to_screen(x0, bottom),
                                      (x1 - x0) * camera.zoom, floor.h * camera.zoom)
        for index, ((left, base, right, top), (name, lip, rock_base)) in enumerate(
                zip(platforms, COMBAT_ART["platform_surfaces"])):
            image = self.images[name]
            scale = (top - base) / (rock_base - lip)
            bottom = top - (image.h - lip) * scale
            if index == 2:
                # Seat the wall end behind the cave outline, beyond the playable lip.
                outer = round(image.w * .14)
                start = lip + 9
                image.clip_draw_to_origin(image.w - outer, 0, outer, image.h - start,
                                          *camera.world_to_screen(right - 6, bottom),
                                          72 * camera.zoom, (image.h - start) * scale * camera.zoom)
            self.draw_sprite(name, camera, left, bottom, right - left, image.h * scale)
        for name in ("left-wall", "right-wall", "ceiling"):
            self.draw_sprite(name, camera, *COMBAT_ART["terrain_origins"][name])
        # The join covers the wall end while leaving the exposed jump edge clear.
        self.draw_sprite("vine-joint", camera, 244, 151, 126, 196)
        self.draw_sprite("vine-wall", camera, 1670, 489, 91, 204)
        banks = ((0, exit_left), (exit_right, self.room_width)) if broken else None
        self.lighting.draw_floor_bounce(camera, banks=banks)
        self.lighting.draw_ledge_bounce(camera, ceiling, platforms)
        self.vegetation.draw_terrain(camera, ceiling, exit_left, exit_right, broken=broken,
                                     tint_at=self.vegetation_tint(ceiling))

    def draw_gate(self, camera, bounds, progress):
        image = self.images["gate"]
        left, bottom, right, top = bounds
        visible = round(image.h * progress)
        if visible:
            image.clip_draw_to_origin(0, image.h - visible, image.w, visible,
                                      *camera.world_to_screen(left, bottom), (right - left) * camera.zoom,
                                      (top - bottom) * visible / image.h * camera.zoom)

    def draw_floor_plants(self, camera, left, right, ceiling):
        with self.room_clip(camera, left - 20, right, ceiling) as visible:
            if not visible:
                return
            width = 164
            height = width * self.seedpods.h / self.seedpods.w
            self.seedpods.draw_to_origin(*camera.world_to_screen(left - 14, -8),
                                         width * camera.zoom, height * camera.zoom)

    def draw_foreground(self, camera, left, right, ceiling):
        with self.room_clip(camera, 0, self.room_width, ceiling + 45, margin=64) as visible:
            if visible:
                self.draw_sprite("vine-ceiling", camera, left + 153, ceiling - 112, 272, 144)
                self.draw_sprite("vine-ceiling", camera, right - 355, ceiling - 94, 252, 128)
        if camera.y < 32 and camera.y + self.height / camera.zoom >= 0:
            self.vegetation.draw_foreground(camera, tint_at=self.lighting.foreground_tint)

            def shade(x, y, v):
                ambient = (round(110 + 41 * v), round(140 + 36 * v), round(158 + 35 * v))
                return self.lighting.foreground_tint(x, y, ambient)

            self.draw_lit_sprite("foreground", camera, 0, -318, self.room_width, 350,
                                 shade, columns=17, rows=6)

    def draw_shaft(self, camera, exit_left, visibility):
        image = self.images["shaft"]
        x0 = exit_left - COMBAT_ART["shaft_mouth_offset"]
        # Blend the sheer sides into the solid banks and keep the depth unreadable at range.
        columns = ((.17, 0), (.29, 255), (.306, 255), (.692, 255), (.71, 255), (.83, 0))
        rows = ((0, max(.68, visibility)), (.015, max(.62, visibility)),
                (.034, max(.48, visibility)), (.16, visibility), (.82, visibility), (1, 0))
        vertices, faces = [], []
        stride = len(columns)
        for row, (v, light) in enumerate(rows):
            for col, (u, opacity) in enumerate(columns):
                world_x, world_y = x0 + u * image.w, -v * image.h
                x, y = camera.world_to_screen(world_x, world_y)
                # Bring the lower shaft toward the lift's teal-green ambient light.
                depth = min(1.0, max(0.0, (v - .04) / .55))
                tint = tuple(round(channel * light) for channel in
                             (220 - 9 * depth, 235 - 3 * depth, 239 - 19 * depth))
                if col in (2, 3) and v <= .015:
                    opacity = 0
                vertices.append(pico.SDL_Vertex((x, self.height - y), (*tint, opacity), (u, v)))
                if row and col:
                    i = row * stride + col
                    faces.extend((i - stride - 1, i - stride, i - 1, i - stride, i, i - 1))
        points = (pico.SDL_Vertex * len(vertices))(*vertices)
        indices = (c_int * len(faces))(*faces)
        pico.SDL_RenderGeometry(pico.renderer, image.texture, points, len(vertices), indices, len(faces))

    def draw_collapse(self, camera, left, right, age):
        span = right - left
        piece_width = span / len(FALLING_ROCKS)
        with self.alpha_geometry():
            for fraction, delay, drift, spin in FALLING_ROCKS:
                t = max(0.0, age - delay)
                x = left + fraction * span + drift * t
                y = -12 - 82 * t - 540 * t * t
                angle = radians(spin * t * 5)
                c, s = cos(angle), sin(angle)
                offsets = ((-.5, 10), (.47, 10), (.52, -3), (.09, -28), (-.43, -18))
                points = [(x + ox * piece_width * c - oy * s, y + ox * piece_width * s + oy * c)
                          for ox, oy in offsets]
                self.geometry(camera, points, ((78, 121, 128, 255), (82, 132, 137, 255),
                              (47, 73, 84, 255), (10, 24, 34, 255), (20, 40, 50, 255)),
                              (0, 1, 2, 0, 2, 3, 0, 3, 4))
            dust = max(0.0, 1 - age / .7)
            for index in range(12):
                offset = (index + .5) / 12
                x = left + span * offset + (offset - .5) * age * 130
                y = age * (58 - (index * 29) % 81) - 148 * age * age
                size = 2 + index % 4
                color = (104, 151, 149, round(178 * dust))
                self.geometry(camera, ((x - size, y), (x, y + size), (x + size, y - size)),
                              (color,) * 3, (0, 1, 2))
            for fraction in (.13, .37, .62, .86):
                self.soft_light(camera, (left + span * fraction, 4 + age * 18),
                                (34 + age * 50, 16 + age * 32), (91, 125, 122), round(42 * dust))

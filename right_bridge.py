"""The raised stone bridge and the blue seal on the right of passage A."""

from ctypes import byref
from math import cos, pi, sin

from pico2d import pico2d as pico

from lower_route_atmosphere import COMBAT_ART, ROUTE_ART, draw_layer, draw_soft_light, load_image
from lower_route_a_art import ART as ROUTE_A_ART
from player import ASSET_ROOT
from render_mesh import VERTEX_SIZE, grid_indices, pack_vertex, vertex_buffer


WORLD_WIDTH = 2240
ENTRY_SPAWN = (150, 0, 0)
LEFT_EXIT = 72
CAMERA_ZOOM = .42
CAMERA_LEFT = -23
CAMERA_Y = -315
BARRIER = (1080, 0, 1140, 550)
TERRAIN = ((0, BARRIER[3], BARRIER[2], 1320),)
CONTACT_DURATION = .34
RELEASE_DURATION = 1.8
RELEASE_APPROACH_X = 875

_CENTER_X = (BARRIER[0] + BARRIER[2]) / 2
_CENTER_Y = BARRIER[3] / 2
_ENERGY = (63, 216, 249)
_BLUE = (26, 123, 223)
_CORE = (219, 247, 255)
_SPILL = (145, 197, 226)
_ROOF_EDGE = (
    (-210, 550), (60, 557), (260, 550), (430, 568), (600, 555),
    (790, 562), (970, 553), (BARRIER[2], BARRIER[3]), (1240, 610), (1360, 751),
    (1512, 856), (1695, 944), (1890, 1008), (2110, 1081), (2460, 1115),
)
_VEGETATION = ASSET_ROOT / "terrain/moss-grotto-floor-decor"


def _crop(image, rectangle):
    left, top, right, bottom = rectangle
    return left / image.w, top / image.h, right / image.w, bottom / image.h


class RightBridge:
    """Draw separate chasm, masonry, arch deck, and seal effects."""

    def __init__(self, screen_height):
        self.screen_height = screen_height
        self.time = 0.0
        self.recess = load_image(ROUTE_A_ART / "recess.png")
        self.masonry = load_image(ROUTE_A_ART / "wall-depth.png")
        self.terrain = load_image(ROUTE_A_ART / "terrain.png")
        self.bracket = load_image(ROUTE_A_ART / "rail-bracket.png")
        self.bridge = load_image(ASSET_ROOT / "structures/map1-lower-route/lower-cave-stone-bridge-v1.png")
        self.arch = load_image(COMBAT_ART / "midground-broken-arch.png")
        self.light = load_image(ROUTE_ART / "mint-light.png")
        self.orb = load_image(ASSET_ROOT / "concepts/b1-hermit-crab/defeat-orb-v4/energy-orb-sheet.png")
        pico.SDL_SetTextureBlendMode(self.light.texture, pico.SDL_BLENDMODE_ADD)
        self.fern = load_image(_VEGETATION / "near-shadow-rounded-leaves.png")
        self.roots = load_image(_VEGETATION / "crooked-root-drop.png")
        self.drape = load_image(_VEGETATION / "ceiling-moss-drip.png")
        self.moss = load_image(_VEGETATION / "moss-rock-chips.png")

    def draw(self, camera, *, sealed, contact_age=None, contact_y=75, release_age=None):
        draw_layer(self.recess, camera, (-220, -865, 2500, 1190), tint=(137, 179, 189))
        draw_layer(self.masonry, camera, (-260, -330, 1320, 890),
                   tint=(173, 201, 198), fade_range=(1160, 490),
                   crop=_crop(self.masonry, (40, 32, 1260, 710)))
        draw_layer(self.arch, camera, (1400, -290, 2430, 480), tint=(61, 104, 110))
        draw_layer(self.light, camera, (1460, -155, 2050, 1110), tint=(112, 171, 183), opacity=86)
        draw_soft_light(camera, (760, -242), (450, 150), (52, 108, 123), 45)
        self._draw_roof(camera)
        self._draw_deck(camera)
        bracket_crop = _crop(self.bracket, (705, 141, 1468, 579))
        draw_layer(self.bracket, camera, (_CENTER_X - 81, 516, _CENTER_X + 81, 617),
                   crop=bracket_crop, tint=(127, 154, 157))
        draw_layer(self.bracket, camera, (_CENTER_X - 67, -57, _CENTER_X + 67, -1),
                   crop=bracket_crop, tint=(176, 194, 196))

        if sealed:
            hit = contact_age is not None and 0 <= contact_age < CONTACT_DURATION
            impact = contact_age / CONTACT_DURATION if hit else 1.0
            self._draw_seal(camera, extent=1.0, strength=1.0, impact=impact, impact_y=contact_y)
            if hit:
                self._draw_impact(camera, impact, contact_y)
        elif release_age is not None and 0 <= release_age < RELEASE_DURATION:
            self._draw_release(camera, release_age)

    def _draw_roof(self, camera):
        geometry = vertex_buffer(3 * len(_ROOF_EDGE))
        offset = 0
        for depth, tint in ((1, (35, 47, 50)), (.26, (70, 91, 93)), (0, (103, 127, 130))):
            for x, edge_y in _ROOF_EDGE:
                sx, sy = camera.world_to_screen(x, edge_y + (1350 - edge_y) * depth)
                u = .015 + .50 * (x + 210) / 2670
                v = .03 + .50 * (1 - depth)
                pack_vertex(geometry, offset, sx, self.screen_height - sy, *tint, 255, u, v)
                offset += VERTEX_SIZE
        indices = grid_indices(len(_ROOF_EDGE) - 1, 2)
        pico.SDL_RenderGeometry(pico.renderer, self.masonry.texture, geometry, len(geometry),
                                indices, len(indices))
        for left, top, width, height in ((-48, 571, 278, 126), (336, 572, 156, 83), (743, 575, 220, 96)):
            draw_layer(self.drape, camera, (left, top - height, left + width, top), tint=(100, 134, 137))
        draw_layer(self.roots, camera, (1174, 528, 1328, 695), tint=(108, 149, 154), opacity=180)

    def _draw_deck(self, camera):
        draw_layer(self.bridge, camera, (59, -336, 2190, 12),
                   crop=_crop(self.bridge, (35, 180, 2137, 583)), tint=(195, 218, 222))
        draw_layer(self.terrain, camera, (-62, -144, 221, 15), fade_range=(221, 106),
                   crop=_crop(self.terrain, (1875, 397, 2172, 547)), tint=(154, 181, 181))
        draw_layer(self.terrain, camera, (2051, -169, 2300, 15),
                   fade_range=(2051, 2190), crop=_crop(self.terrain, (2172, 397, 1890, 547)),
                   tint=(137, 173, 178))
        for x, width in ((355, 84), (925, 49), (1814, 70)):
            draw_layer(self.moss, camera, (x, -2, x + width, width * .40),
                       tint=(150, 174, 170), opacity=217)

    def _draw_seal(self, camera, *, extent, strength, impact=1.0, impact_y=0.0):
        draw_soft_light(camera, (_CENTER_X, _CENTER_Y), (150 * extent + 44, 360 * extent + 24),
                        _BLUE, round(68 * strength))
        draw_soft_light(camera, (_CENTER_X, -1), (225, 22), _SPILL, round(75 * strength * extent))
        rows = 30
        columns = (-1.0, -.62, -.11, .27, .69, 1.0)
        phases = ((0, _BLUE), (74, _BLUE), (128, _ENERGY),
                  (103, _SPILL), (57, _BLUE), (0, _BLUE))
        geometry = vertex_buffer((rows + 1) * len(columns))
        offset = 0
        for row in range(rows + 1):
            part = row / rows
            y = _CENTER_Y + (2 * part - 1) * _CENTER_Y * extent
            bend = sin(part * 17 + self.time * 4.7) * 8 + sin(part * 44 - self.time * 5) * 3.5
            contact = max(0, 1 - abs(y - impact_y) / 100)
            bend += 31 * (1 - impact) ** 2 * contact ** 2
            flicker = .85 + .15 * sin(part * 29 - self.time * 6.8)
            half = (37 + 8 * cos(part * 18 - self.time * 4.4)) * extent
            for column, (alpha, color) in zip(columns, phases):
                x = _CENTER_X + bend * extent + column * half
                sx, sy = camera.world_to_screen(x, y)
                pack_vertex(geometry, offset, sx, self.screen_height - sy, *color,
                            round(alpha * strength * flicker), 0, 0)
                offset += VERTEX_SIZE
        indices = grid_indices(len(columns) - 1, rows)
        previous = pico.SDL_BlendMode()
        pico.SDL_GetRenderDrawBlendMode(pico.renderer, byref(previous))
        pico.SDL_SetRenderDrawBlendMode(pico.renderer, pico.SDL_BLENDMODE_ADD)
        try:
            pico.SDL_RenderGeometry(pico.renderer, None, geometry, len(geometry), indices, len(indices))
            for point in range(10):
                part = (point * .213 + self.time * .25) % 1.0
                y = _CENTER_Y + (2 * part - 1) * _CENTER_Y * extent
                x = _CENTER_X + sin(part * 38 + point) * 25 * extent
                start = camera.world_to_screen(x, y)
                end = camera.world_to_screen(x + 1, y + 6 + point % 4)
                pico.draw_line(*start, *end, *_CORE, round(129 * strength))
        finally:
            pico.SDL_SetRenderDrawBlendMode(pico.renderer, previous)

    def _draw_impact(self, camera, part, y):
        fade = (1 - part) ** 1.4
        x = BARRIER[0]
        draw_soft_light(camera, (x, y), (42 + 92 * part, 25 + 57 * part), _ENERGY, round(176 * fade))
        previous = pico.SDL_BlendMode()
        pico.SDL_GetRenderDrawBlendMode(pico.renderer, byref(previous))
        pico.SDL_SetRenderDrawBlendMode(pico.renderer, pico.SDL_BLENDMODE_ADD)
        try:
            arc = [camera.world_to_screen(x - (25 + 104 * part) * cos(theta),
                                          y + (22 + 69 * part) * sin(theta))
                   for theta in (-pi / 2 + index * pi / 12 for index in range(13))]
            for start, end in zip(arc, arc[1:]):
                pico.draw_line(*start, *end, *_ENERGY, round(214 * fade))
        finally:
            pico.SDL_SetRenderDrawBlendMode(pico.renderer, previous)

    def _draw_release(self, camera, age):
        gather = max(0, (age - .45) / (RELEASE_DURATION - .45))
        extent = 1 - gather * gather * (3 - 2 * gather)
        self._draw_seal(camera, extent=extent, strength=.54 * extent)
        burst = sin(pi * gather) ** 2
        draw_soft_light(camera, (_CENTER_X, _CENTER_Y), (93, 90), _BLUE, round(160 * burst))
        if burst > .02:
            # Reuse the same four-by-four atlas as the B1 release.
            row, column = divmod(int(age / .075) % 16, 4)
            cell = self.orb.w // 4
            size = (83 + 88 * burst) * camera.zoom
            self.orb.opacify(.82 * burst)
            self.orb.clip_draw(column * cell, (3 - row) * cell, cell, cell,
                               *camera.world_to_screen(_CENTER_X, _CENTER_Y), size, size)
            self.orb.opacify(1)
        flash = (age - 1.18) / .35
        if 0 <= flash < 1:
            draw_soft_light(camera, (_CENTER_X, _CENTER_Y), (17, 19 + 240 * flash),
                            _CORE, round(133 * (1 - flash) ** 1.4))

    def draw_foreground(self, camera):
        draw_layer(self.fern, camera, (-136, -294, 245, 78), tint=(63, 95, 102), opacity=226)
        draw_layer(self.fern, camera, (2020, -343, 2340, 19), tint=(55, 82, 91), opacity=231)

"""Independent stone wall, wall reliefs and near leaves for the A passage."""

import json
from math import exp, sin

from pico2d import pico2d as pico

from lower_route_atmosphere import ROUTE_ART, draw_layer, draw_soft_light, load_image
from player import ASSET_ROOT


ART = ASSET_ROOT / "terrain/lower-route-a-wall-v1"
SCALE = 2.5
WIDTH, HEIGHT = 5430, 1810
WALL_PARALLAX = (.84, .93)
RECESS_PARALLAX = (.42, .38)
FOREGROUND_PARALLAX = 1.08
# Left, top, width, height, opacity, first receiving terrain surface (art pixels).
LIGHTS = (
    (2, 100, 350, 300, 116, 369),
    (439, 72, 450, 560, 210, 369),
    (1145, 70, 250, 560, 98, 624),
    (1599, 38, 450, 430, 230, 407),
)
DECOR = ASSET_ROOT / "terrain/moss-grotto-floor-decor"
FLOOR_GROUPS = (
    ("round-fan-fern", 514, 625, 68),
    ("moss-rock-chips", 624, 626, 58),
    ("split-moss-cushion", 1037, 626, 58),
    ("moss-rock-chips", 1265, 626, 39),
    ("round-fan-fern", 1405, 625, 42),
    ("split-moss-cushion", 1746, 408, 68),
    ("moss-rock-chips", 1890, 409, 44),
    ("crooked-root-drop", 520, 445, 45),
)
FIREFLIES = (
    (267, 254), (312, 225), (380, 284), (570, 514), (625, 549),
    (688, 490), (1190, 545), (1245, 508), (1340, 476), (1610, 346),
    (1660, 321), (1705, 365), (2034, 350), (2101, 376),
)


class LowerRouteAArt:
    def __init__(self, origin):
        self.origin = origin
        self.background = load_image(ART / "wall-depth.png")
        pico.SDL_SetTextureBlendMode(self.background.texture, pico.SDL_BLENDMODE_BLEND)
        self.recess = load_image(ART / "recess.png")
        pico.SDL_SetTextureBlendMode(self.recess.texture, pico.SDL_BLENDMODE_BLEND)
        self.midground = load_image(ART / "midground.png")
        self.foreground = load_image(ART / "foreground.png")
        self.terrain = load_image(ART / "terrain.png")
        self.light = load_image(ROUTE_ART / "mint-light.png")
        pico.SDL_SetTextureBlendMode(self.light.texture, pico.SDL_BLENDMODE_ADD)
        self.glow = load_image(ASSET_ROOT / "sprites/relic/relic-blue-glow-v1.png")
        pico.SDL_SetTextureColorMod(self.glow.texture, 221, 225, 116)
        self.bracket = load_image(ART / "rail-bracket.png")
        self.decor = {name: load_image(DECOR / f"{name}.png") for name, *_ in FLOOR_GROUPS}
        self.decor_info = {entry["file"][:-4]: entry for entry in json.loads(
            (DECOR / "placement.json").read_text(encoding="utf-8"))["assets"]}
        self.time = 0.0

    def point(self, x, y):
        """Position relative to the authored 2172 by 724 panorama."""
        return self.origin[0] + x * SCALE, self.origin[1] + HEIGHT - y * SCALE

    def draw_image(self, image, camera, bounds, *, tint=(255, 255, 255), opacity=255,
                   crop=None, fade_entry=False, clip_bottom=None, shade=None):
        fade_range = (self.origin[0] - 900, self.origin[0] - 180) if fade_entry else None
        draw_layer(image, camera, bounds, tint=tint, opacity=opacity, crop=crop,
                   fade_range=fade_range, clip_bottom=clip_bottom, shade=shade)

    def draw_background(self, camera):
        x, y = self.origin
        focus_x = camera.x + camera.view_width / 2 - x - WIDTH / 2
        focus_y = camera.y + pico.canvas_height / (2 * camera.zoom) - y - HEIGHT / 2
        # Overscan covers both the normal camera and the relic-focus view at either height.
        far_left = x - 2300 + focus_x * (1 - RECESS_PARALLAX[0])
        far_bottom = y - 750 + focus_y * (1 - RECESS_PARALLAX[1])
        self.draw_image(self.recess, camera,
                        (far_left, far_bottom, far_left + WIDTH + 4600, far_bottom + 3344),
                        tint=(192, 220, 223), fade_entry=True)
        left = x - 900 + focus_x * (1 - WALL_PARALLAX[0])
        bottom = y - 350 + focus_y * (1 - WALL_PARALLAX[1])
        self.draw_image(self.background, camera, (left, bottom, left + WIDTH + 1800, bottom + 2410),
                        tint=(186, 208, 209), fade_entry=True)
        # Reliefs stay close to the wall. Their original transparent margins remain intact.
        mx, my = x + focus_x * (1 - WALL_PARALLAX[0]), y + focus_y * (1 - WALL_PARALLAX[1])
        self.draw_image(self.midground, camera, (mx, my + 70, mx + WIDTH, my + HEIGHT + 70),
                        tint=(105, 138, 140), fade_entry=True)
        for px, py, width, height, strength, receiving_y in LIGHTS:
            left, top = self.point(px, py)
            self.draw_image(self.light, camera, (left, top - height * SCALE,
                                                left + width * SCALE, top), opacity=strength,
                            clip_bottom=self.point(0, receiving_y)[1])
        self.draw_dust(camera)
        self.draw_fireflies(camera)

    def draw_dust(self, camera):
        for number in range(12):
            left, top, width, height, _, surface = LIGHTS[1 + number % 3]
            py = top + 30 + (number * 47 + self.time * 7) % max(35, surface - top - 45)
            progress = (py - top) / height
            px = left + width * (.78 - .55 * progress) + 14 * sin(number * 2.7 + self.time * .23)
            sx, sy = camera.world_to_screen(*self.point(px, py))
            if 0 < sx < pico.canvas_width and 0 < sy < pico.canvas_height:
                pico.draw_rectangle(sx, sy, sx + .7, sy + .7, 85, 108, 98, filled=True)

    def draw_fireflies(self, camera):
        for number, (px, py) in enumerate(FIREFLIES):
            phase = self.time * .72 + number * 2.1
            x, y = self.point(px, py)
            x += 11 * sin(phase)
            y += 8 * sin(phase * 1.36)
            sx, sy = camera.world_to_screen(x, y)
            if -24 < sx < pico.canvas_width + 24 and -24 < sy < pico.canvas_height + 24:
                pulse = .65 + .35 * sin(phase * 1.7)
                pico.SDL_SetTextureAlphaMod(self.glow.texture, round(44 * pulse))
                self.glow.draw(sx, sy, 47 * camera.zoom, 47 * camera.zoom)
                pico.draw_rectangle(sx - .8, sy - .8, sx + .8, sy + .8,
                                    round(112 * pulse), round(139 * pulse), 68, filled=True)

    def draw_terrain(self, camera):
        x, y = self.origin
        # The blended A/B camera can rise a few pixels above A's authored roof.
        roof_top = y + HEIGHT
        view_top = camera.y + pico.canvas_height / camera.zoom
        left, right = max(x, camera.x), min(x + WIDTH, camera.x + camera.view_width)
        if view_top > roof_top and left < right:
            x0, y0 = camera.world_to_screen(left, roof_top)
            x1, y1 = camera.world_to_screen(right, view_top)
            pico.draw_rectangle(x0, y0, x1, y1, 0, 0, 0, filled=True)
        # The original collision bodies remain opaque below their painted surface rims.
        for left, bottom, right, top in ((0, -400, WIDTH, 182),
                                         (0, 170, 1190, 815),
                                         (3940, 170, WIDTH, 725),
                                         (3710, 170, 3890, 587)):
            x0, y0 = camera.world_to_screen(x + left, y + bottom)
            x1, y1 = camera.world_to_screen(x + right, y + top)
            pico.draw_rectangle(x0, y0, x1, y1, 0, 0, 0, filled=True)
        self.draw_image(self.terrain, camera, (x, y, x + WIDTH, y + HEIGHT), shade=self.surface_tint)
        self.draw_contacts(camera)
        for name, px, py, width in FLOOR_GROUPS:
            self.draw_decor(camera, name, px, py, width)
        self.draw_rail_supports(camera)

    def surface_tint(self, x, y, tint):
        px = (x - self.origin[0]) / SCALE
        py = (HEIGHT - y + self.origin[1]) / SCALE
        base = (210, 224, 227)
        # Large shaded faces descend from the lit upper edge into the cliff interior.
        if px >= 1467 and py > 425:
            fade = min(.35, (py - 425) / 450)
            base = tuple(round(channel * (1 - fade)) for channel in base)
        exposure = 0.0
        for left, top, width, height, strength, surface in LIGHTS:
            hit_x = left + width * (.78 - .55 * (surface - top) / height)
            exposure = max(exposure, exp(-((px - hit_x) / (width * .28)) ** 2
                                         - ((py - surface) / 24) ** 2) * strength / 255)
        return tuple(round(channel + (lit - channel) * exposure)
                     for channel, lit in zip(base, (251, 255, 229)))

    def soft_patch(self, camera, px, py, rx, ry, color, opacity):
        draw_soft_light(camera, self.point(px, py), (rx * SCALE, ry * SCALE), color, opacity)

    def draw_contacts(self, camera):
        for px, py, rx, ry in ((970, 619, 91, 9), (1808, 403, 132, 10),
                               (1434, 623, 39, 4), (451, 369, 43, 5)):
            self.soft_patch(camera, px, py, rx, ry, (3, 12, 15), 118)
        for left, top, width, height, strength, surface in LIGHTS:
            hit_x = left + width * (.78 - .55 * (surface - top) / height)
            self.soft_patch(camera, hit_x, surface + 1, width * .17, 3,
                            (177, 215, 171), round(strength * .22))

    def draw_decor(self, camera, name, px, py, width):
        image = self.decor[name]
        entry = self.decor_info[name]
        x0, y0, x1, y1 = entry["visible_bounds"]
        pivot_x, pivot_y = entry["pivot_px"]
        scale = width * SCALE / (x1 - x0)
        anchor_x, anchor_y = self.point(px, py)
        left = anchor_x - (pivot_x - x0) * scale
        top = anchor_y + (pivot_y - y0) * scale
        self.draw_image(image, camera, (left, top - (y1 - y0) * scale, left + width * SCALE, top),
                        crop=(x0 / image.w, y0 / image.h, x1 / image.w, y1 / image.h),
                        tint=self.surface_tint(anchor_x, anchor_y, (255, 255, 255)))

    def draw_rail_supports(self, camera):
        for px, py, width, height in ((975, 403, 54, 32), (975, 516, 54, 32),
                                      (931, 329, 42, 25), (931, 594, 42, 25),
                                      (655, 329, 39, 23), (774, 594, 39, 23)):
            self.soft_patch(camera, px + 2, py + 4, width * .65, height * .65, (2, 10, 14), 115)
            x, y = self.point(px - width / 2, py + height / 2)
            self.draw_image(self.bracket, camera, (x, y, x + width * SCALE, y + height * SCALE),
                            crop=(716 / 2172, 143 / 724, 1457 / 2172, 573 / 724),
                            tint=(171, 198, 204))
            self.soft_patch(camera, px, py, width * .46, 4, (64, 171, 192), 25)

    def draw_gate_collar(self, camera):
        # A fixed lintel connects the sliding stone's housing to the ceiling slot.
        self.soft_patch(camera, 451, 122, 52, 11, (2, 9, 12), 138)
        left, bottom = self.point(400, 136)
        self.draw_image(self.bracket, camera, (left, bottom, left + 102 * SCALE, bottom + 32 * SCALE),
                        crop=(716 / 2172, 143 / 724, 1457 / 2172, 573 / 724),
                        tint=(148, 178, 182))

    def draw_foreground(self, camera):
        x, y = self.origin
        # Independent leaf silhouettes move slightly faster than the camera.
        drift = (1 - FOREGROUND_PARALLAX) * (camera.x + camera.view_width / 2 - x - WIDTH / 2)
        for left, bottom, width, height, crop in (
            (30, 830, 940, 450, (0, 0, .30, 1)),
            (WIDTH - 850, 720, 820, 440, (.70, 0, 1, 1)),
            (2400, 150, 600, 280, (.70, 0, 1, 1)),
        ):
            self.draw_image(self.foreground, camera,
                            (x + left + drift, y + bottom - height,
                             x + left + width + drift, y + bottom),
                            tint=(91, 119, 125), opacity=230)

"""Independent damp wall, reliefs and foreground vegetation for passage B."""

from math import sin

from pico2d import pico2d as pico

from lower_route_atmosphere import ROUTE_ART, draw_layer, draw_soft_light, load_image
from lower_route_b_layout import BOTTOM, TOP, WIDTH
from player import ASSET_ROOT


ART = ASSET_ROOT / "terrain/lower-route-b-wall-v1"
A_ART = ASSET_ROOT / "terrain/lower-route-a-wall-v1"
WALL_PARALLAX = (.84, .93)
RECESS_PARALLAX = (.42, .38)
FOREGROUND_PARALLAX = 1.08
LIGHTS = (
    (4360, 1350, 550, 1170, 228, 180),
    (2203, 1370, 900, 780, 190, 590),
    (850, 1300, 600, 710, 118, 590),
)
FIREFLIES = (
    (4660, 227), (4780, 263), (3450, 232), (3510, 261),
    (2490, 647), (2570, 678), (1120, 655), (1040, 702),
    (1760, -595), (1850, -530),
)
SUPPORTS = ((3794, 510), (4204, 510), (1514, 240), (1944, 240),
            (4510, 280), (2250, 690), (1230, 690))


class LowerRouteBScenery:
    def __init__(self):
        self.background = load_image(ART / "background.png")
        self.midground = load_image(ART / "midground.png")
        self.foreground = load_image(ART / "foreground.png")
        self.recess = load_image(A_ART / "recess.png")
        self.bracket = load_image(A_ART / "rail-bracket.png")
        self.light = load_image(ROUTE_ART / "mint-light.png")
        self.glow = load_image(ASSET_ROOT / "sprites/relic/relic-blue-glow-v1.png")
        for image in (self.background, self.recess):
            pico.SDL_SetTextureBlendMode(image.texture, pico.SDL_BLENDMODE_BLEND)
        pico.SDL_SetTextureBlendMode(self.light.texture, pico.SDL_BLENDMODE_ADD)
        pico.SDL_SetTextureColorMod(self.glow.texture, 221, 225, 116)
        self.time = 0.0

    def draw_background(self, camera):
        focus_x = camera.x + camera.view_width / 2 - WIDTH / 2
        focus_y = camera.y + pico.canvas_height / (2 * camera.zoom) - (BOTTOM + TOP) / 2
        far_left = -2300 + focus_x * (1 - RECESS_PARALLAX[0])
        far_bottom = BOTTOM - 800 + focus_y * (1 - RECESS_PARALLAX[1])
        draw_layer(self.recess, camera, (far_left, far_bottom, far_left + 10300, far_bottom + 3800),
                   tint=(192, 220, 223))
        dx = focus_x * (1 - WALL_PARALLAX[0])
        dy = focus_y * (1 - WALL_PARALLAX[1])
        left, bottom = -1100 + dx, BOTTOM - 90 + dy
        draw_layer(self.background, camera, (left, bottom, left + 7230, bottom + 2410),
                   tint=(186, 208, 209))
        draw_layer(self.midground, camera, (400 + dx, 120 + dy, 4740 + dx, 1567 + dy),
                   tint=(111, 144, 146))
        for left, top, width, height, strength, surface in LIGHTS:
            draw_layer(self.light, camera, (left, top - height, left + width, top),
                       opacity=strength, clip_bottom=surface)
        self.draw_fireflies(camera)

    def draw_fireflies(self, camera):
        for number, (x, y) in enumerate(FIREFLIES):
            phase = self.time * .72 + number * 2.1
            sx, sy = camera.world_to_screen(x + 12 * sin(phase), y + 9 * sin(phase * 1.36))
            if -24 < sx < pico.canvas_width + 24 and -24 < sy < pico.canvas_height + 24:
                pulse = .65 + .35 * sin(phase * 1.7)
                pico.SDL_SetTextureAlphaMod(self.glow.texture, round(44 * pulse))
                self.glow.draw(sx, sy, 47 * camera.zoom, 47 * camera.zoom)
                pico.draw_rectangle(sx - .8, sy - .8, sx + .8, sy + .8,
                                    round(112 * pulse), round(139 * pulse), 68, filled=True)

    def draw_surfaces(self, camera):
        for left, top, width, height, strength, surface in LIGHTS:
            hit_x = left + width * (.78 - .55 * (top - surface) / height)
            draw_soft_light(camera, (hit_x, surface + 1), (width * .16, 9),
                            (177, 215, 171), round(strength * .22))
        for x, y in ((1200, 590), (2760, 590), (3530, 180)):
            draw_soft_light(camera, (x, y + 1), (48, 9), (3, 12, 15), 105)
        crop = (716 / 2172, 143 / 724, 1457 / 2172, 573 / 724)
        for x, y in SUPPORTS:
            draw_soft_light(camera, (x + 4, y - 5), (91, 46), (2, 10, 14), 105)
            draw_layer(self.bracket, camera, (x - 67, y - 39, x + 67, y + 39),
                       crop=crop, tint=(171, 198, 204))
            draw_soft_light(camera, (x, y), (55, 10), (64, 171, 192), 24)

    def draw_foreground(self, camera):
        drift = (1 - FOREGROUND_PARALLAX) * (camera.x + camera.view_width / 2 - WIDTH / 2)
        for left, bottom, width, height, crop in (
            (800, 170, 400, 350, (0, 0, .25, 1)),
            (3300, 745, 175, 530, (.78, 0, 1, 1)),
            (4520, -225, 400, 350, (0, 0, .25, 1)),
            (480, 970, 135, 390, (.78, 0, 1, 1)),
        ):
            draw_layer(self.foreground, camera,
                       (left + drift, bottom, left + width + drift, bottom + height),
                       crop=crop, tint=(82, 111, 118), opacity=230)

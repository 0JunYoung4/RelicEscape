"""Close damp masonry and independent reliefs for the boss antechamber."""

from math import sin

from pico2d import pico2d as pico

from lower_route_atmosphere import ROUTE_ART, draw_layer, draw_soft_light, load_image
from player import ASSET_ROOT


ART = ASSET_ROOT / "terrain/lower-route-c-wall-v1"
WALL_PARALLAX = (.84, .93)
RECESS_PARALLAX = (.42, .38)
FOREGROUND_PARALLAX = 1.08
# Full C opacity at x=0, fading out over B's existing continuous wall.
JOIN_FADE = (690, 0)
LIGHTS = ((-150, 1330, 440, 740, 156, 590),
          (-1050, 1370, 260, 780, 64, 590))
FIREFLIES = ((-1080, 665), (-1015, 705), (-570, 755), (-135, 650), (35, 710))


class LowerRouteCScenery:
    def __init__(self):
        self.background = load_image(ART / "background.png")
        self.midground = load_image(ART / "midground.png")
        self.foreground = load_image(ART / "foreground.png")
        self.recess = load_image(ASSET_ROOT / "terrain/lower-route-a-wall-v1/recess.png")
        self.light = load_image(ROUTE_ART / "mint-light.png")
        self.glow = load_image(ASSET_ROOT / "sprites/relic/relic-blue-glow-v1.png")
        pico.SDL_SetTextureBlendMode(self.light.texture, pico.SDL_BLENDMODE_ADD)
        pico.SDL_SetTextureColorMod(self.glow.texture, 221, 225, 116)
        self.time = 0.0

    def draw_background(self, camera):
        if camera.x >= JOIN_FADE[0]:
            return
        focus_x = camera.x + camera.view_width / 2 + 800
        focus_y = camera.y + pico.canvas_height / (2 * camera.zoom) - 800
        far_left = -3800 + focus_x * (1 - RECESS_PARALLAX[0])
        far_bottom = -1400 + focus_y * (1 - RECESS_PARALLAX[1])
        draw_layer(self.recess, camera, (far_left, far_bottom, far_left + 7600, far_bottom + 4200),
                   tint=(192, 220, 223), fade_range=JOIN_FADE)
        dx = focus_x * (1 - WALL_PARALLAX[0])
        dy = focus_y * (1 - WALL_PARALLAX[1])
        left, bottom = -2600 + dx, -1100 + dy
        draw_layer(self.background, camera, (left, bottom, left + 4608, bottom + 3072),
                   tint=(186, 208, 209), fade_range=JOIN_FADE)
        draw_layer(self.midground, camera, (-1850 + dx, 500 + dy, 450 + dx, 1267 + dy),
                   tint=(111, 144, 146), fade_range=JOIN_FADE)
        for left, top, width, height, strength, surface in LIGHTS:
            draw_layer(self.light, camera, (left, top - height, left + width, top),
                       opacity=strength, clip_bottom=surface, fade_range=JOIN_FADE)
        for number, (x, y) in enumerate(FIREFLIES):
            phase = self.time * .72 + number * 2.1
            sx, sy = camera.world_to_screen(x + 10 * sin(phase), y + 7 * sin(phase * 1.36))
            if -24 < sx < pico.canvas_width + 24 and -24 < sy < pico.canvas_height + 24:
                pulse = .65 + .35 * sin(phase * 1.7)
                pico.SDL_SetTextureAlphaMod(self.glow.texture, round(40 * pulse))
                self.glow.draw(sx, sy, 43 * camera.zoom, 43 * camera.zoom)
                pico.draw_rectangle(sx - .7, sy - .7, sx + .7, sy + .7,
                                    round(105 * pulse), round(130 * pulse), 65, filled=True)

    def draw_surfaces(self, camera, floor):
        for left, top, width, height, strength, surface in LIGHTS:
            hit_x = left + width * (.78 - .55 * (top - surface) / height)
            draw_soft_light(camera, (hit_x, surface + 1), (width * .16, 8),
                            (177, 215, 171), round(strength * .22))
        for x, width in ((-1190, 95), (-710, 58)):
            draw_soft_light(camera, (x, floor + 1), (width, 8), (3, 12, 15), 100)

    def draw_foreground(self, camera):
        drift = (1 - FOREGROUND_PARALLAX) * (camera.x + camera.view_width / 2 + 800)
        for left, bottom, width, height, crop in (
            (-1450, 285, 430, 430, (0, 0, 1 / 3, 1)),
            (90, 1140, 235, 395, (.73, 0, 1, 1)),
        ):
            draw_layer(self.foreground, camera,
                       (left + drift, bottom, left + width + drift, bottom + height),
                       crop=crop, tint=(82, 111, 118), opacity=230)

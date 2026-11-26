"""A walkable join with one world scale and a shared camera."""

from pico2d import pico2d as pico

from lower_route_a import EXIT_LEDGE
from lower_route_b import PLAY_TERRAIN
from lower_route_b_layout import A_ENTRY, BOTTOM, WIDTH as B_WIDTH
from lower_route_c import TERRAIN as C_TERRAIN
from lower_route_passage_art import PASSAGE_LAYERS, PassageArt


PASSAGE_LEFT = B_WIDTH
PASSAGE_RIGHT = PASSAGE_LEFT + 900
PASSAGE_FLOOR = A_ENTRY[3]
PASSAGE_CENTER = (PASSAGE_LEFT + PASSAGE_RIGHT) / 2
A_ORIGIN = (PASSAGE_RIGHT, PASSAGE_FLOOR - EXIT_LEDGE[3])

# Preserve the panorama's source-to-world scale when extending it to B's cliff.
PASSAGE_ART_CROP = (690, 0, 1680, 724)
PASSAGE_ART_FLOOR_ROW = 371
PASSAGE_ART_ORIGINAL_LEFT = 820
PASSAGE_ART_FADE_LEFT = PASSAGE_LEFT - 310
PASSAGE_ART_FADE_RIGHT = PASSAGE_RIGHT + 330
PASSAGE_ART_SCALE_X = (PASSAGE_ART_FADE_RIGHT - PASSAGE_ART_FADE_LEFT) / (PASSAGE_ART_CROP[2] - PASSAGE_ART_ORIGINAL_LEFT)
PASSAGE_ART_SCALE_Y = 2.5
PASSAGE_ART_X = PASSAGE_ART_FADE_LEFT + (PASSAGE_ART_CROP[0] - PASSAGE_ART_ORIGINAL_LEFT) * PASSAGE_ART_SCALE_X
PASSAGE_ART_TOP = PASSAGE_FLOOR + PASSAGE_ART_FLOOR_ROW * PASSAGE_ART_SCALE_Y


class LowerRouteConnection:
    def __init__(self, route_a):
        self.route_a = route_a
        self.art = PassageArt((PASSAGE_ART_X, PASSAGE_ART_TOP), (PASSAGE_ART_SCALE_X, PASSAGE_ART_SCALE_Y))
        backdrop = self.art.plates["far"]
        pico.SDL_SetTextureColorMod(backdrop.texture, 224, 214, 196)
        backdrop.opacify(.86)
        self.ground_y = BOTTOM
        self.base_terrain = (*C_TERRAIN, *PLAY_TERRAIN, *route_a.terrain,
                             (PASSAGE_LEFT, BOTTOM, PASSAGE_RIGHT, PASSAGE_FLOOR),
                             (PASSAGE_RIGHT, BOTTOM, route_a.world_width, route_a.ground_y))

    @property
    def terrain(self):
        barrier = self.route_a.seal_barrier
        return (*self.base_terrain, barrier) if barrier is not None else self.base_terrain

    @staticmethod
    def blend(x, b_value, a_value):
        # Use the same horizontal transition for ordinary and relic camera framing.
        progress = max(0.0, min(1.0, (x - (PASSAGE_LEFT - 200)) / (PASSAGE_RIGHT - PASSAGE_LEFT + 600)))
        weight = progress * progress * (3 - 2 * progress)
        return b_value + (a_value - b_value) * weight

    def draw(self, camera, screen_height):
        if not self.art.visible(camera, screen_height):
            return
        # Keep the rock lip in front of the light and distant ruins.
        for layer in PASSAGE_LAYERS[:-1]:
            if layer == "middle":
                self.route_a.atmosphere.draw_light(camera, PASSAGE_CENTER - 280, PASSAGE_FLOOR - 40,
                                                   1420, 1030, strength=150)
            self.draw_layer(camera, screen_height, layer)

    def draw_foreground(self, camera, screen_height):
        if self.art.visible(camera, screen_height):
            self.draw_layer(camera, screen_height, "near")

    def draw_layer(self, camera, screen_height, layer):
        self.art.draw_layer(camera, screen_height, layer)

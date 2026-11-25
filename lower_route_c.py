"""The safe passage between B's golem ledge and the first boss entrance."""

from pico2d import pico2d as pico

from lower_route_b_art import STRUCTURES, draw_rock_wall, draw_ruin_platform, draw_structure
from lower_route_b_layout import BACKGROUND_BOTTOM, C_PASSAGE, TOP, WIDTH as B_WIDTH


LEFT, RIGHT = -1600, C_PASSAGE[0]
FLOOR = C_PASSAGE[3]
ENTRANCE_X = -1290
ENTRANCE_WIDTH = 220
CHECKPOINT = (-710, FLOOR, 0.0)
CHECKPOINT_RADIUS = 115
FLOOR_BOUNDS = (LEFT, 485, RIGHT, FLOOR)
TERRAIN = (
    FLOOR_BOUNDS,
    (LEFT, FLOOR, ENTRANCE_X + ENTRANCE_WIDTH / 2, TOP),
    (LEFT, 1270, RIGHT, TOP),
)


class LowerRouteC:
    def __init__(self, b_art, stone_seal):
        self.cave_art = b_art
        self.stone_seal = stone_seal
        self.arch = pico.load_image(str(STRUCTURES / "lower-cave-b1-entrance-v1.png"))
        self.checkpoint_reached = False

    def check_arrival(self, player):
        if player.grounded and player.y == FLOOR and abs(player.x - CHECKPOINT[0]) <= CHECKPOINT_RADIUS:
            self.checkpoint_reached = True

    def draw(self, camera, screen_height):
        art = self.cave_art
        width = RIGHT - LEFT
        crop_width = round(art.background.w * width / B_WIDTH)
        # Reflect the neighbor's edge so both the backdrop and its scale meet at the seam.
        draw_structure(art.background, (0, 0, crop_width, art.background.h), camera,
                       (LEFT + RIGHT) / 2, BACKGROUND_BOTTOM, width, TOP - BACKGROUND_BOTTOM, flip="h")

        draw_rock_wall(art.wall, camera, (
            (FLOOR - 60, LEFT - 70, -1410), (FLOOR + 64, LEFT - 70, -1435),
            (FLOOR + 335, LEFT - 80, -1445), (TOP, LEFT - 100, -1325),
        ), screen_height)
        name = "connected-passage"
        draw_ruin_platform(camera, art.platform_images[name], art.platforms[name], FLOOR_BOUNDS)

        x, y = camera.world_to_screen(ENTRANCE_X, FLOOR + 165)
        self.stone_seal.draw(x, y, 320 * camera.zoom, 330 * camera.zoom)
        draw_structure(self.arch, (97, 27, 1439, 986), camera, ENTRANCE_X, FLOOR - 14, 510, 364)
        draw_structure(art.rubble, (88, 133, 1454, 882), camera, -255, FLOOR, 168, 92)

        if not self.checkpoint_reached:
            pico.SDL_SetTextureColorMod(art.marker.texture, 133, 145, 151)
        try:
            draw_structure(art.marker, (207, 15, 1040, 1206), camera, CHECKPOINT[0], FLOOR, 132, 188)
        finally:
            if not self.checkpoint_reached:
                pico.SDL_SetTextureColorMod(art.marker.texture, 255, 255, 255)

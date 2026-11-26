"""World-anchored vegetation on the arena's back bank, rock, and near edges."""

from dataclasses import dataclass
import json

from pico2d import pico2d as pico

from player import ASSET_ROOT


@dataclass(frozen=True)
class Plant:
    sprite: str
    x: float
    y: float
    width: float
    tint: tuple[int, int, int]
    flip: bool = False


# Broad masses around the ruin bases. The center stays quiet behind the player.
REAR_BANK = (
    Plant("grass-rounded-tuft", 339, 2, 191, (76, 129, 142)),
    Plant("grass-soft-sedge", 485, 8, 252, (83, 138, 154), True),
    Plant("grass-rounded-tuft", 628, 31, 258, (82, 143, 155), True),
    Plant("low-hooked-grass", 734, 10, 186, (91, 143, 151)),
    Plant("round-fan-fern", 804, 1, 96, (112, 155, 148)),
    Plant("low-club-spores", 1176, 8, 58, (75, 132, 144), True),
    Plant("grass-small-sprigs", 1261, 7, 126, (82, 143, 153)),
    Plant("low-hooked-grass", 1458, 18, 207, (84, 144, 156), True),
    Plant("grass-rounded-tuft", 1611, 8, 248, (88, 147, 155), True),
    Plant("round-fan-fern", 1672, 1, 127, (103, 154, 162), True),
    Plant("split-moss-cushion", 386, 4, 181, (95, 143, 143), True),
    Plant("round-fan-fern", 536, 18, 161, (107, 163, 157)),
    Plant("bead-moss-patch", 674, 9, 188, (101, 151, 150), True),
    Plant("split-moss-cushion", 755, 3, 169, (106, 147, 145)),
    Plant("bead-moss-patch", 1287, 6, 192, (109, 160, 158)),
    Plant("grass-small-sprigs", 1541, 13, 113, (98, 151, 155), True),
    Plant("split-moss-cushion", 1634, 2, 144, (106, 154, 152), True),
)

# Asymmetric patches follow the existing rough wall outline in world space.
WALLS = (
    Plant("vine-wall-creeper", 226, 275, 58, (147, 195, 185)),
    Plant("wall-flat-ivy", 266, 350, 76, (143, 188, 183), True),
    Plant("vine-wall-creeper", 245, 414, 67, (139, 183, 185)),
    Plant("ceiling-moss-drip", 280, 500, 125, (150, 194, 191), True),
    Plant("wall-flat-ivy", 300, 538, 70, (143, 183, 181), True),
    Plant("vine-wall-creeper", 275, 604, 88, (137, 178, 179)),
    Plant("wall-flat-ivy", 355, 697, 89, (153, 198, 193), True),
    Plant("ledge-moss-cascade", 332, 747, 87, (139, 187, 181)),
    Plant("vine-wall-creeper", 350, 852, 69, (142, 189, 182)),
    Plant("wall-flat-ivy", 377, 911, 66, (133, 178, 180), True),
    Plant("ceiling-moss-drip", 425, 994, 144, (146, 186, 176)),
    Plant("wall-flat-ivy", 1745, 80, 62, (142, 189, 182)),
    Plant("vine-wall-creeper", 1783, 152, 74, (148, 189, 183), True),
    Plant("wall-flat-ivy", 1750, 228, 82, (157, 200, 190)),
    Plant("ceiling-moss-drip", 1778, 325, 134, (146, 188, 185)),
    Plant("vine-wall-creeper", 1815, 399, 67, (136, 177, 179), True),
    Plant("wall-flat-ivy", 1737, 490, 94, (149, 192, 188)),
    Plant("ledge-moss-cascade", 1740, 575, 102, (151, 194, 184), True),
    Plant("vine-wall-creeper", 1791, 629, 96, (154, 197, 185), True),
    Plant("wall-flat-ivy", 1754, 740, 75, (142, 187, 183)),
    Plant("ceiling-moss-drip", 1730, 802, 138, (145, 192, 192)),
    Plant("vine-wall-creeper", 1747, 899, 67, (130, 179, 179), True),
    Plant("wall-flat-ivy", 1719, 980, 85, (149, 192, 189)),
)

# Anchors overlap the painted roof lip above the collision plane.
CEILING = (
    Plant("ceiling-moss-drip", 467, 23, 145, (138, 184, 183)),
    Plant("crooked-root-drop", 522, 19, 70, (114, 157, 170), True),
    Plant("ceiling-moss-drip", 782, 15, 121, (141, 180, 172), True),
    Plant("vine-ceiling-drape", 816, 16, 115, (119, 167, 172)),
    Plant("crooked-root-drop", 1038, 25, 47, (122, 170, 174)),
    Plant("ceiling-moss-drip", 1269, 20, 153, (148, 191, 181)),
    Plant("crooked-root-drop", 1286, 15, 67, (120, 163, 169)),
    Plant("crooked-root-drop", 1518, 21, 52, (122, 170, 174), True),
    Plant("ceiling-moss-drip", 1640, 11, 134, (143, 187, 195), True),
)

# Short silhouettes catch light along the walk line. Large foliage lives behind it.
FLOOR_EDGE = (
    Plant("bead-moss-patch", 41, -4, 99, (133, 173, 165)),
    Plant("split-moss-cushion", 123, -9, 83, (132, 170, 169), True),
    Plant("low-hooked-grass", 311, -6, 78, (154, 200, 180), True),
    Plant("bead-moss-patch", 403, -5, 123, (155, 197, 189)),
    Plant("split-moss-cushion", 487, -8, 85, (145, 188, 179)),
    Plant("bead-moss-patch", 568, -4, 122, (161, 208, 195), True),
    Plant("low-hooked-grass", 631, -8, 73, (161, 199, 184)),
    Plant("bead-moss-patch", 730, -6, 104, (150, 195, 191)),
    Plant("split-moss-cushion", 807, -6, 86, (150, 199, 187), True),
    Plant("bead-moss-patch", 973, -10, 106, (136, 170, 166), True),
    Plant("split-moss-cushion", 1177, -6, 79, (148, 193, 186)),
    Plant("bead-moss-patch", 1266, -4, 102, (156, 200, 194)),
    Plant("low-hooked-grass", 1347, -9, 62, (156, 196, 180), True),
    Plant("bead-moss-patch", 1422, -7, 115, (157, 198, 190), True),
    Plant("split-moss-cushion", 1523, -8, 94, (144, 190, 181)),
    Plant("bead-moss-patch", 1619, -5, 138, (151, 193, 182)),
    Plant("low-hooked-grass", 1717, -8, 90, (147, 185, 177), True),
)

NEAR_BANK = (
    Plant("near-shadow-rounded-leaves", 115, -130, 240, (109, 143, 147)),
    Plant("shadow-low-moss-lobes", 230, -83, 181, (105, 147, 152), True),
    Plant("shadow-fern-scroll", 345, -95, 98, (109, 146, 151), True),
    Plant("near-shadow-ribbon-grass", 1575, -102, 255, (100, 140, 145), True),
    Plant("near-shadow-rounded-leaves", 1801, -121, 261, (112, 147, 158), True),
    Plant("shadow-fern-scroll", 1701, -112, 92, (111, 151, 151)),
)


class CombatVegetation:
    def __init__(self, height):
        self.height = height
        required = {plant.sprite + ".png" for group in (REAR_BANK, WALLS, CEILING, FLOOR_EDGE, NEAR_BANK)
                    for plant in group}
        self.images = {}
        for folder in ("moss-grotto-floor-decor", "moss-grotto-foliage"):
            root = ASSET_ROOT / "terrain" / folder
            manifest = json.loads((root / "placement.json").read_text(encoding="utf-8"))
            for entry in manifest["assets"]:
                filename = entry["file"]
                if filename not in required:
                    continue
                image = pico.load_image(str(root / filename))
                pico.SDL_SetTextureScaleMode(image.texture, pico.SDL_ScaleModeLinear)
                self.images[filename[:-4]] = (image, entry["visible_bounds"], entry["pivot_px"])

    def draw_background(self, camera, *, tint_at=None):
        for plant in REAR_BANK:
            self._draw(camera, plant, tint_at=tint_at, strength=.44)

    def draw_terrain(self, camera, ceiling, exit_left, exit_right, *, broken, tint_at=None):
        for plant in WALLS:
            self._draw(camera, plant, tint_at=tint_at, strength=.52)
        for plant in CEILING:
            self._draw(camera, plant, height_offset=ceiling, tint_at=tint_at, strength=.65)
        for plant in FLOOR_EDGE:
            if broken and exit_left - plant.width / 2 < plant.x < exit_right + plant.width / 2:
                continue
            self._draw(camera, plant, tint_at=tint_at, strength=.85)

    def draw_foreground(self, camera, *, tint_at=None):
        for plant in NEAR_BANK:
            self._draw(camera, plant, tint_at=tint_at, strength=.74, light_height=.72)

    def _draw(self, camera, plant, *, height_offset=0, tint_at=None, strength=0, light_height=0):
        image, (x0, y0, x1, y1), (pivot_x, pivot_y) = self.images[plant.sprite]
        source_width, source_height = x1 - x0, y1 - y0
        scale = plant.width / source_width
        anchor_x = x1 - pivot_x if plant.flip else pivot_x - x0
        world_y = plant.y + height_offset
        left = plant.x - anchor_x * scale
        top = world_y + (pivot_y - y0) * scale
        height = source_height * scale
        if (left + plant.width <= camera.x or left >= camera.x + camera.view_width
                or top <= camera.y or top - height >= camera.y + self.height / camera.zoom):
            return
        tint = plant.tint if tint_at is None else tint_at(plant.x, world_y + height * light_height,
                                                         plant.tint, strength)
        pico.SDL_SetTextureColorMod(image.texture, *tint)
        screen_x, screen_y = camera.world_to_screen(left, top)
        source = pico.SDL_Rect(x0, y0, source_width, source_height)
        dest = pico.SDL_FRect(screen_x, self.height - screen_y, plant.width * camera.zoom, height * camera.zoom)
        flip = pico.SDL_FLIP_HORIZONTAL if plant.flip else pico.SDL_FLIP_NONE
        pico.SDL_RenderCopyExF(pico.renderer, image.texture, source, dest, 0, None, flip)

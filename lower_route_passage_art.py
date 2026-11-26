"""World-anchored art for the A–B passage and its standing stones."""

from dataclasses import dataclass
import json
from pathlib import Path

from pico2d import pico2d as pico

from player import ASSET_ROOT


DECOR = ASSET_ROOT / "terrain/moss-grotto-floor-decor"
FOLIAGE = ASSET_ROOT / "terrain/moss-grotto-foliage"
PASSAGE_ART = ASSET_ROOT / "terrain/lower-route-ab-depth"
PASSAGE_LAYERS = ("far", "middle", "terrain", "attached", "near")


@dataclass(frozen=True)
class Plant:
    pack: Path
    name: str
    # Anchor on the production panorama, measured from the upper-left texel.
    anchor: tuple[float, float]
    width: float
    tint: tuple[int, int, int]
    flip: bool = False


# The two tiers of rounded leaves use the same asset. Keep the carving and walk line clear.
BEHIND_STONE = (
    Plant(FOLIAGE, "grass-soft-sedge", (425, 349), 232, (101, 162, 167), True),
    Plant(FOLIAGE, "grass-rounded-tuft", (770, 320), 338, (110, 170, 164)),
)
ON_STONE = (
    Plant(FOLIAGE, "vine-wall-creeper", (714, 203), 72, (170, 221, 201)),
    Plant(DECOR, "split-moss-cushion", (627, 369), 112, (161, 208, 189)),
    Plant(FOLIAGE, "grass-rounded-tuft", (651, 368), 120, (151, 220, 196), True),
)
NEAR_BANK = (
    Plant(FOLIAGE, "shadow-arching-grass", (174, 540), 307, (118, 157, 173)),
    Plant(FOLIAGE, "shadow-overlapping-leaves", (803, 565), 457, (120, 158, 171), True),
)
PASSAGE_PLANTS = {"middle": BEHIND_STONE, "attached": ON_STONE, "near": NEAR_BANK}


class PassageArt:
    def __init__(self, origin, plate_scale, *, plate_dir=PASSAGE_ART, plants=PASSAGE_PLANTS):
        self.origin = origin
        self.plate_scale = plate_scale
        self.plates = {
            "far": pico.load_image(str(plate_dir / "backdrop.png")),
            "middle": pico.load_image(str(plate_dir / "monument.png")),
            "terrain": pico.load_image(str(plate_dir / "terrain.png")),
        }
        self.plants = plants
        packs = {plant.pack for layer in plants.values() for plant in layer}
        manifests = {
            pack: {entry["file"]: entry for entry in json.loads(
                (pack / "placement.json").read_text(encoding="utf-8"))["assets"]}
            for pack in packs
        }
        self.sprites = {}
        for plants in self.plants.values():
            for plant in plants:
                file = f"{plant.name}.png"
                image = pico.load_image(str(plant.pack / file))
                metadata = manifests[plant.pack][file]
                pico.SDL_SetTextureColorMod(image.texture, *plant.tint)
                pico.SDL_SetTextureScaleMode(image.texture, pico.SDL_ScaleModeLinear)
                self.sprites[plant] = (image, metadata["visible_bounds"], metadata["pivot_px"])

    def visible(self, camera, screen_height):
        x, y = self.origin
        plate = self.plates["far"]
        scale_x, scale_y = self.plate_scale
        return (x < camera.x + camera.view_width and x + plate.w * scale_x > camera.x
                and y > camera.y and y - plate.h * scale_y < camera.y + screen_height / camera.zoom)

    def draw_layer(self, camera, screen_height, layer):
        for plant in self.plants.get(layer, ()):
            self.draw_plant(camera, screen_height, plant)
        if layer in self.plates:
            image = self.plates[layer]
            x, y = camera.world_to_screen(*self.origin)
            scale_x, scale_y = self.plate_scale
            dest = pico.SDL_FRect(x, screen_height - y, image.w * scale_x * camera.zoom,
                                 image.h * scale_y * camera.zoom)
            pico.SDL_RenderCopyF(pico.renderer, image.texture, None, dest)

    def draw_plant(self, camera, screen_height, plant):
        image, (x0, y0, x1, y1), (pivot_x, pivot_y) = self.sprites[plant]
        width, height = x1 - x0, y1 - y0
        # The metadata pivot is visual (e.g. a root or the point a vine clings to).
        anchor_x = x1 - pivot_x if plant.flip else pivot_x - x0
        scale = plant.width / width
        origin_x, origin_y = self.origin
        scale_x, scale_y = self.plate_scale
        world_x = origin_x + plant.anchor[0] * scale_x
        world_y = origin_y - plant.anchor[1] * scale_y
        x, y = camera.world_to_screen(world_x - anchor_x * scale,
                                      world_y + (pivot_y - y0) * scale)
        source = pico.SDL_Rect(x0, y0, width, height)
        dest = pico.SDL_FRect(x, screen_height - y, plant.width * camera.zoom, height * scale * camera.zoom)
        flip = pico.SDL_FLIP_HORIZONTAL if plant.flip else pico.SDL_FLIP_NONE
        pico.SDL_RenderCopyExF(pico.renderer, image.texture, source, dest, 0, None, flip)

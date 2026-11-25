"""Bake the A–B panorama and its unbroken left cliff from the same source."""

from argparse import ArgumentParser
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter

from lower_route_b_layout import A_ENTRY
from lower_route_connection import (
    PASSAGE_ART_CROP,
    PASSAGE_ART_FADE_LEFT,
    PASSAGE_ART_FADE_RIGHT,
    PASSAGE_ART_FLOOR_ROW,
    PASSAGE_ART_SCALE_X,
    PASSAGE_ART_X,
    PASSAGE_LEFT,
    PASSAGE_RIGHT,
)
from player import ASSET_ROOT


SOURCE = ASSET_ROOT / "terrain/lower-route-ab-passage-v1.png"
OUTPUT = ASSET_ROOT / "terrain/lower-route-ab-passage-joined-v2.png"


def terrain_mask(plate):
    left, _, right, _ = PASSAGE_ART_CROP
    cliff_x = round(left + (A_ENTRY[0] - PASSAGE_ART_X) / PASSAGE_ART_SCALE_X)
    # Find the first lit moss texel along the lip. The shaded base is traced below.
    top = []
    for x in range(cliff_x + 2, right):
        y_start = 352 if x < 993 else 360
        colors = (plate.getpixel((x, y)) for y in range(y_start, PASSAGE_ART_FLOOR_ROW))
        surface = next((y for y, (red, green, blue) in enumerate(colors, start=y_start)
                        if red >= 24 and green - blue >= 20), 367)
        top.append((x, surface))
    outline = [
        *top,
        (right, 476), (1560, 473), (1440, 487), (1310, 480), (1240, 471),
        (1160, 492), (1100, 480), (1060, 461), (1000, 485), (960, 462),
        (929, 477), (907, 470), (889, 483), (862, 496), (837, 490),
        (820, 480), (799, 478), (780, 474), (763, 478), (746, 473),
        (734, 467), (727, 467), (715, 461), (707, 458), (702, 452),
        (697, 447), (695, 436), (693, 427),
        (694, 418), (692, 409), (cliff_x, 400), (cliff_x, 381), (cliff_x + 3, 373),
    ]
    # Subpixel coverage belongs at the silhouette. The interior stays at alpha 255.
    mask = Image.new("L", (plate.width * 2, plate.height * 2))
    ImageDraw.Draw(mask).polygon([(x * 2, y * 2) for x, y in outline], fill=255)
    return mask.resize(plate.size, Image.Resampling.BOX).crop(PASSAGE_ART_CROP)


def panorama_opacity(x):
    stops = ((PASSAGE_ART_FADE_LEFT, 0), (PASSAGE_LEFT - 155, 140), (PASSAGE_LEFT, 255),
             (PASSAGE_RIGHT, 255), (PASSAGE_RIGHT + 165, 140), (PASSAGE_ART_FADE_RIGHT, 0))
    if x <= stops[0][0]:
        return 0
    for (left, low), (right, high) in zip(stops, stops[1:]):
        if x <= right:
            return round(low + (high - low) * (x - left) / (right - left))
    return 0


def bake(terrain_preview):
    with Image.open(SOURCE) as source:
        source = source.convert("RGB")
    plate = source.crop(PASSAGE_ART_CROP)
    core = terrain_mask(source)
    # Give the exposed cut face a dark rim. Taper it out before the old panorama starts.
    rim = core.filter(ImageFilter.MinFilter(7))
    alpha_columns = []
    for x in range(plate.width):
        world_x = PASSAGE_ART_X + (x + .5) * PASSAGE_ART_SCALE_X
        backdrop = panorama_opacity(world_x)
        alpha_columns.append(backdrop)
        strength = .55 * max(0, min(1, (PASSAGE_ART_FADE_LEFT - world_x) / 60))
        if strength:
            for y in range(375, plate.height):
                if core.getpixel((x, y)):
                    darken = 1 - strength * (1 - rim.getpixel((x, y)) / 255)
                    plate.putpixel((x, y), tuple(round(channel * darken)
                                                 for channel in plate.getpixel((x, y))))
    alpha = Image.frombytes("L", plate.size, bytes(alpha_columns) * plate.height)
    left_width = round((PASSAGE_LEFT - PASSAGE_ART_X) / PASSAGE_ART_SCALE_X)
    left_strip = (0, 0, left_width, plate.height)
    alpha.paste(ImageChops.lighter(alpha.crop(left_strip), core.crop(left_strip)), (0, 0))
    plate.putalpha(alpha)
    plate.save(OUTPUT, optimize=True)
    if terrain_preview:
        plate.putalpha(core)
        plate.save(terrain_preview)


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--terrain-preview", type=Path)
    bake(parser.parse_args().terrain_preview)

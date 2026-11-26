"""Prepare the painted A and C terrain and the shared mint shaft texture."""

from math import exp
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter


ASSETS = Path(__file__).resolve().parents[1] / "assets"
OUTPUT = ASSETS / "terrain/lower-route-art-v2"


def rock_mask(source, keep, shallow_stone):
    """Key the cyan air out of the paintings and protect the fixed devices and walk line."""
    red, _, blue = source.split()
    blue_air = ImageChops.subtract(blue, red)
    mask = blue_air.point(lambda value: max(0, min(255, round((70 - value) * 255 / 35))))
    protected = Image.new("L", source.size)
    draw = ImageDraw.Draw(protected)
    for shape in keep:
        draw.polygon(shape, fill=255)
    for box in shallow_stone:
        tones = red.crop(box).point(lambda value: min(255, max(0, (value - 4) * 25)))
        protected.paste(tones, box, tones)
    return ImageChops.lighter(mask, protected)


def terrain(name, source, keep, light, *, shallow_stone=()):
    with Image.open(ASSETS / source) as original:
        source = original.convert("RGB")
    alpha = rock_mask(source, keep, shallow_stone)
    cooled_rock = source.convert("RGB", (.84, .07, .09, 0,
                                         .06, .84, .06, 0,
                                         .04, .14, .84, 0))
    x, y, horizontal, vertical = light
    # Tint the existing rock pixels, preserving the alpha and the terrain outlines.
    exposure = Image.new("L", source.size)
    exposure.putdata([round(86 * exp(-2.6 * ((column - x) / horizontal) ** 2
                                    - 3.0 * ((row - y) / vertical) ** 2))
                      for row in range(source.height) for column in range(source.width)])
    rim = cooled_rock.convert("RGB", (1.05, .16, .06, 4,
                                     .07, 1.14, .07, 7,
                                     .03, .13, 1.04, 4))
    plate = Image.composite(rim, cooled_rock, exposure)
    plate.putalpha(alpha)
    plate.save(OUTPUT / name, optimize=True)


def light_shaft():
    width, height = 192, 256
    alpha = Image.new("L", (width, height))
    pixels = []
    for y in range(height):
        progress = y / (height - 1)
        center = width * (.78 - progress * .55)
        spread = width * (.10 + progress * .09)
        fade = min(1, progress * 31) * (1 - progress) ** 1.36
        for x in range(width):
            u = (x - center) / spread
            broad = exp(-2.1 * u * u)
            strand = exp(-19 * (u + .35) ** 2)
            pixels.append(round((125 * broad + 39 * strand) * fade))
    alpha.putdata(pixels)
    light = Image.new("RGBA", alpha.size, (152, 224, 197))
    light.putalpha(alpha.filter(ImageFilter.GaussianBlur(1.3)))
    light.save(OUTPUT / "mint-light.png", optimize=True)


def main():
    OUTPUT.mkdir(exist_ok=True)
    terrain("a-terrain.png", "concepts/map1-lower-route-a-v3-plate.png", (
        ((0, 370), (480, 370), (850, 370), (850, 405), (745, 454), (520, 451), (502, 624),
         (1466, 624), (1466, 462), (1554, 462), (1554, 407), (2172, 407), (2172, 724), (0, 724)),
        ((1398, 545), (1463, 545), (1463, 617), (1398, 617)),
        ((914, 210), (1024, 188), (1018, 357), (1010, 600), (919, 603)),
    ), light=(1895, 398, 270, 120), shallow_stone=((1488, 276, 1556, 458), (1563, 319, 1627, 405)))
    terrain("c-terrain.png", "terrain/lower-route-c/antechamber-v2-plate.png", (
        ((0, 589), (1672, 589), (1672, 941), (0, 941)),
        ((0, 0), (441, 0), (396, 123), (317, 264), (339, 318), (404, 382),
         (403, 533), (465, 587), (0, 589)),
        ((597, 490), (642, 482), (655, 520), (657, 588), (586, 588)),
    ), light=(1410, 590, 225, 120))
    light_shaft()


if __name__ == "__main__":
    main()

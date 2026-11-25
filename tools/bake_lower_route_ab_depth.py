"""Separate the A–B panorama into backdrop, monument, and terrain plates."""

from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter


ASSETS = Path(__file__).resolve().parents[1] / "assets" / "terrain"
SOURCE = ASSETS / "lower-route-ab-passage-joined-v2.png"
OUTPUT = ASSETS / "lower-route-ab-depth"

# Outline the two stones and their attached greenery in joined-v2 source pixels.
# The terrain cut supplies the bottom edge.
MONUMENT_OUTLINE = (
    (303, 366), (305, 349), (308, 339), (316, 339), (329, 345), (345, 337),
    (359, 338), (376, 334), (367, 323), (346, 326), (330, 341), (335, 326),
    (353, 318), (376, 312), (389, 317), (377, 299), (354, 301), (367, 294),
    (384, 292), (401, 299), (398, 286), (388, 278), (378, 275), (394, 274),
    (413, 286), (429, 272), (445, 264), (463, 258), (470, 263), (466, 268),
    (450, 273), (436, 285), (425, 299), (447, 283), (465, 282), (479, 290),
    (498, 277), (509, 260), (524, 252), (541, 247), (554, 246), (552, 236),
    (539, 229), (531, 229), (541, 225), (559, 230), (564, 240), (574, 250),
    (588, 218), (598, 202), (609, 196), (610, 181), (618, 171), (634, 166),
    (654, 166), (665, 161), (676, 163), (683, 156), (695, 154), (700, 157),
    (706, 153), (720, 152), (711, 158), (728, 158), (747, 166), (755, 173),
    (759, 183), (754, 200), (752, 222), (755, 249), (751, 269), (756, 299),
    (772, 288), (782, 278), (798, 274), (797, 280), (781, 287), (774, 300),
    (791, 303), (813, 293), (826, 291), (844, 299), (849, 307), (843, 307),
    (832, 302), (820, 303), (805, 311), (791, 325), (818, 317), (835, 320),
    (848, 327), (854, 339), (847, 336), (834, 330), (817, 330), (801, 342),
    (829, 352), (841, 360), (850, 364), (850, 371), (303, 371),
)


def terrain_mask(source):
    mask = Image.new("L", source.size)
    pixels = source.load()
    draw = ImageDraw.Draw(mask)
    for x in range(source.width):
        # The bright yellow-green lip separates the walkable rock from the blue air.
        for y in range(361, 371):
            red, green, blue, _ = pixels[x, y]
            if red >= 96 and green - blue >= 42:
                break
        else:
            y = 371
        draw.line((x, y, x, source.height - 1), fill=255)
    return mask


def fill_backdrop(rgb, cut, terrain):
    """Recover a soft blue backdrop from the open area surrounding the stones."""
    known = ImageChops.invert(ImageChops.lighter(cut, terrain))
    weighted = [ImageChops.multiply(channel, known) for channel in rgb.split()]
    recovered = Image.new("RGB", rgb.size, (18, 83, 110))
    left, top, right, bottom = cut.getbbox()
    for radius in (84, 48, 24, 12, 5):
        weights = known.filter(ImageFilter.GaussianBlur(radius))
        bands = [channel.filter(ImageFilter.GaussianBlur(radius)) for channel in weighted]
        for x in range(left, right):
            for y in range(top, bottom):
                weight = weights.getpixel((x, y))
                if not cut.getpixel((x, y)) or weight < 8:
                    continue
                influence = min(1, (weight - 8) / 90)
                previous = recovered.getpixel((x, y))
                recovered.putpixel((x, y), tuple(
                    round(old * (1 - influence) + influence * min(255, 255 * band.getpixel((x, y)) / weight))
                    for old, band in zip(previous, bands)
                ))
    return recovered


def bake():
    with Image.open(SOURCE) as source:
        source = source.convert("RGBA")
    rgb = source.convert("RGB")
    source_alpha = source.getchannel("A")
    ground = terrain_mask(source)

    silhouette = Image.new("L", source.size)
    ImageDraw.Draw(silhouette).polygon(MONUMENT_OUTLINE, fill=255)
    silhouette = ImageChops.subtract(silhouette, ground)
    # Include the surrounding leaf tips in the repair so none are left floating.
    margin = silhouette.filter(ImageFilter.MaxFilter(19))
    cleanup = margin.filter(ImageFilter.GaussianBlur(3))
    recovered = fill_backdrop(rgb, cleanup.point(lambda opacity: 255 if opacity else 0), ground)
    feather = silhouette.filter(ImageFilter.GaussianBlur(.85))
    feather = ImageChops.subtract(feather, ground)

    backdrop = Image.composite(recovered, rgb, cleanup)
    backdrop.putalpha(ImageChops.subtract(source_alpha, ground))
    monument = source.copy()
    monument.putalpha(ImageChops.multiply(source_alpha, feather))
    terrain = source.copy()
    terrain.putalpha(ImageChops.multiply(source_alpha, ground))

    OUTPUT.mkdir(exist_ok=True)
    for name, plate in (("backdrop", backdrop), ("monument", monument), ("terrain", terrain)):
        # Drop covered RGB data so sparse layers compress without changing visible pixels.
        clean = Image.new("RGBA", plate.size)
        clean.paste(plate, mask=plate.getchannel("A").point(lambda alpha: 255 if alpha else 0))
        clean.save(OUTPUT / f"{name}.png", optimize=True)


if __name__ == "__main__":
    bake()

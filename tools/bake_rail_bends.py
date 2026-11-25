"""Bake the quarter-turn atlas with `python -m tools.bake_rail_bends`."""

from math import hypot
from statistics import median_low

from PIL import Image

from rail import BEND_RADII, RAIL_ART_SCALE, RAIL_BEND_IMAGE, RAIL_IMAGE


SUPERSAMPLE = 4


def straight_profile(image):
    """Take the typical color of each row, leaving the end caps and brackets out."""
    profile = []
    for y in range(image.height):
        row = image.crop((image.width // 4, y, 3 * image.width // 4, y + 1))
        profile.append(tuple(median_low(channel) for channel in zip(*row.get_flattened_data())))
    return profile


def bake_bend(radius, profile):
    half_width = len(profile) * RAIL_ART_SCALE // 2
    size = radius + half_width
    inner_edge = radius - half_width
    sample_size = size * SUPERSAMPLE
    image = Image.new("RGBA", (sample_size, sample_size))
    pixels = image.load()
    coordinates = [(pixel + 0.5) / SUPERSAMPLE for pixel in range(sample_size)]
    # The center is the top-left corner. Both ends cut flush along the axes.
    for y, dy in enumerate(coordinates):
        for x, dx in enumerate(coordinates):
            distance = hypot(dx, dy)
            if inner_edge <= distance < size:
                row = int((distance - inner_edge) / RAIL_ART_SCALE)
                pixels[x, y] = profile[row]
    return image.resize((size, size), Image.Resampling.BOX)


def main():
    with Image.open(RAIL_IMAGE) as straight:
        profile = straight_profile(straight)
    bends = [bake_bend(radius, profile) for radius in BEND_RADII]
    cell_size = bends[-1].width
    atlas = Image.new("RGBA", (len(bends) * cell_size, cell_size))
    for column, bend in enumerate(bends):
        atlas.paste(bend, (column * cell_size, 0))
    atlas.save(RAIL_BEND_IMAGE)


if __name__ == "__main__":
    main()

"""Fit the first combat room's terrain art to the B1 test room's existing surfaces."""

import json

from PIL import Image, ImageChops, ImageOps

from tools.preview_b1_intro import ART, GROUND, ROOT
from tools.render_b1_roar_preview import resize, rgba


COMBAT_ART = ROOT / "assets/terrain/combat-room-v2"
DECOR = ROOT / "assets/terrain/moss-grotto-floor-decor"
FLOOR_WALKWAY_RIGHT = 1664

# Existing B1 art positions: left, walking surface, width, underside of the rock.
LEDGES = (
    ("platform-left", 142, 252, 449, 323, False),
    ("platform-center", 724, 179, 257, 227, False),
    ("platform-center", 1204, 183, 257, 236, True),
    ("platform-right", 1588, 239, 449, 307, False),
)

# Low clumps on the walking surface leave clear stretches under the boss and player.
FLOOR_MOSS = (
    ("bead-moss-patch", 226, 59, False),
    ("split-moss-cushion", 444, 92, True),
    ("low-hooked-grass", 571, 72, False),
    ("bead-moss-patch", 777, 91, True),
    ("bead-moss-patch", 1426, 69, False),
    ("split-moss-cushion", 1582, 75, False),
    ("low-hooked-grass", 1860, 62, True),
    ("bead-moss-patch", 2015, 72, True),
    ("split-moss-cushion", 2247, 81, False),
)

# Place these behind the floor lip so the shoreline plants and rubble sit in the rock.
# Keep the middle of the arena, the rails, and the gate clear.
REAR_BANK = (
    ("shadow-low-moss-lobes", 113, 105, True),
    ("moss-rock-chips", 459, 115, False),
    ("round-fan-fern", 545, 98, True),
    ("split-slate-scrap", 693, 121, False),
    ("low-hooked-grass", 813, 67, True),
    ("mossy-ring-shard", 1461, 99, True),
    ("moss-rock-chips", 1510, 112, True),
    ("round-fan-fern", 1659, 79, False),
    ("dark-root-stump", 1892, 106, False),
    ("split-moss-cushion", 1967, 73, True),
    ("shadow-low-moss-lobes", 2253, 112, False),
)


def _short_center_ledge(image):
    """Keep both original rounded ends without squeezing the center platform's moss."""
    left_width, right_width, overlap = 388, 418, 112
    left = image.crop((0, 0, left_width, image.height))
    right = image.crop((image.width - right_width, 0, image.width, image.height))
    result = Image.new("RGBA", (left_width + right_width - overlap, image.height))
    result.paste(left, (0, 0))
    join = left_width - overlap
    fade = Image.new("L", (overlap, 1))
    fade.putdata([round(255 * x / (overlap - 1)) for x in range(overlap)])
    splice = Image.composite(right.crop((0, 0, overlap, image.height)),
                             left.crop((join, 0, left_width, image.height)),
                             fade.resize((overlap, image.height)))
    result.paste(splice, (join, 0))
    result.paste(right.crop((overlap, 0, right_width, image.height)), (left_width, 0))
    return result


def _place_ledge(canvas, source, x, top, width, bottom, lip, rock_base, flip):
    scale_y = (bottom - top) / (rock_base - lip)
    sprite = resize(source, (width, round(source.height * scale_y)))
    if flip:
        sprite = ImageOps.mirror(sprite)
    canvas.alpha_composite(sprite, (x, top - round(lip * scale_y)))


def _place_floor(canvas, floor_origin):
    source = rgba(COMBAT_ART / "floor.png")
    # The far-right pixels meet the old room wall and sit above the contact line.
    source = source.crop((0, 0, FLOOR_WALKWAY_RIGHT, source.height))
    source_ground = source.height + floor_origin
    scale_y = (canvas.height - GROUND) / (source.height - source_ground)
    floor = resize(source, (canvas.width, round(source.height * scale_y)))
    canvas.alpha_composite(floor, (0, GROUND - round(source_ground * scale_y)))


def _place_decor(canvas, placements, tint, bottom):
    for name, left, width, flip in placements:
        source = rgba(DECOR / f"{name}.png")
        source = source.crop(source.getbbox())
        sprite = resize(source, (width, round(source.height * width / source.width)))
        if flip:
            sprite = ImageOps.mirror(sprite)
        color = ImageChops.multiply(sprite.convert("RGB"), Image.new("RGB", sprite.size, tint))
        color.putalpha(sprite.getchannel("A"))
        canvas.alpha_composite(color, (left, bottom - color.height))


def stage_terrain():
    """Compose the new floor and ledges with the existing B1 tunnel and hardware."""
    manifest = json.loads((COMBAT_ART / "manifest.json").read_text(encoding="utf-8"))
    lip_map = {name: (lip, rock_base) for name, lip, rock_base in manifest["platform_surfaces"]}
    old_terrain = rgba(ART / "terrain.png")
    canvas = Image.new("RGBA", old_terrain.size)

    gate = rgba(ART / "right-passage-gate.png")
    canvas.alpha_composite(gate, (2055, GROUND - gate.height))
    # The cave wall ends above this split. The lower strip contains the old floor and plants.
    canvas.alpha_composite(old_terrain.crop((0, 0, old_terrain.width, 663)))
    _place_decor(canvas, REAR_BANK, (129, 166, 171), GROUND + 9)
    _place_floor(canvas, manifest["terrain_origins"]["floor"][1])

    rails = ROOT / "assets/sprites/rail"
    source_track = rgba(rails / "relic-track-blue-v4.png").transpose(Image.Transpose.ROTATE_90)
    carriage = rgba(rails / "relic-carriage-v2.png")
    # Both ends begin inside their ledge, so the lit track never sticks out above the top.
    for center, ledge in ((387, LEDGES[0]), (1795, LEDGES[-1])):
        anchor = ledge[2] + 16
        track = resize(source_track, (12, GROUND - anchor))
        canvas.alpha_composite(track, (center - track.width // 2, anchor))
        canvas.alpha_composite(carriage, (center - carriage.width // 2, 389))

    platforms = {name: rgba(COMBAT_ART / f"{name}.png") for name in lip_map}
    platforms["platform-center"] = _short_center_ledge(platforms["platform-center"])
    for name, left, top, width, bottom, flip in LEDGES:
        _place_ledge(canvas, platforms[name], left, top, width, bottom, *lip_map[name], flip)

    _place_decor(canvas, FLOOR_MOSS, (155, 198, 187), GROUND + 4)
    scrap = rgba(DECOR / "split-slate-scrap.png")
    scrap = scrap.crop(scrap.getbbox())
    canvas.alpha_composite(resize(scrap, (57, 26)), (686, 675))
    canvas.alpha_composite(ImageOps.mirror(resize(scrap, (47, 22))), (1480, 679))
    return canvas

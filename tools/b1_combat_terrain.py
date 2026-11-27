"""Fit the hall's masonry and rail art to the existing B1 surfaces."""

import json

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageOps

from tools.preview_b1_intro import ART, GROUND, ROOT, SHELL_X
from tools.render_b1_roar_preview import resize, rgba


TERRAIN_ART = ROOT / "assets/terrain"
PLATFORM_ART = ART.parent / "platforms-v1"
DECOR = TERRAIN_ART / "moss-grotto-floor-decor"
FLOOR_SOURCE = TERRAIN_ART / "ruins-floor-blue-fissures-v1.png"
RAIL_CENTERS = (387, 1795)
GATE_LEFT = 2055

# Existing B1 art positions: left, walking surface, width, underside of the rock.
LEDGES = (
    ("sluice-crown", 142, 252, 449, 323),
    ("counterweight-step", 724, 179, 257, 227),
    ("root-keystone", 1204, 183, 257, 236),
    ("aqueduct-crown", 1588, 239, 449, 307),
)

# Low clumps on the walking surface leave clear stretches under the boss and player.
FLOOR_MOSS = (
    ("bead-moss-patch", 226, 59, False),
    ("split-moss-cushion", 444, 92, True),
    ("low-hooked-grass", 571, 72, False),
    ("moss-crack-shoots", 640, 34, False),
    ("bead-moss-patch", 777, 91, True),
    ("bead-moss-patch", 1426, 69, False),
    ("split-moss-cushion", 1582, 75, False),
    ("low-hooked-grass", 1860, 62, True),
    ("low-club-spores", 1923, 37, False),
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


def _place_ledge(canvas, entry, x, top, width, bottom):
    left, upper, right, base = entry["crop"]
    start, surface, end = entry["walk_surface"]
    sx, sy = width / (end - start), (bottom - top) / (base - surface)
    source = rgba(PLATFORM_ART / entry["image"]).crop((left, upper, right, base))
    ledge = resize(source, (round((right - left) * sx), round((base - upper) * sy)))
    shade = Image.new("L", (1, ledge.height))
    shade.putdata([round(115 * (y / ledge.height) ** 2) for y in range(ledge.height)])
    rgb = Image.composite(Image.new("RGB", ledge.size, (6, 13, 19)), ledge.convert("RGB"), shade.resize(ledge.size))
    rgb.putalpha(ledge.getchannel("A"))
    canvas.alpha_composite(rgb, (x + round((left - start) * sx), top + round((upper - surface) * sy)))


def _place_floor(canvas):
    stone = rgba(FLOOR_SOURCE)
    # Retain the old contact line while exposing the worn masonry below it.
    floor = resize(stone.crop((0, 356, stone.width, stone.height)),
                   (canvas.width, canvas.height - GROUND + 3))
    aprons = Image.new("L", (floor.width, 8))
    pen = ImageDraw.Draw(aprons)
    for left, right in ((269, 308), (581, 615), (809, 835), (1136, 1189), (1458, 1501),
                        (1748, 1778), (1978, 2013), (2189, 2258), (2332, 2360)):
        pen.polygon(((left, 0), (right, 0), (right - 9, 2), (left + 15, 5)), fill=123)
    worn = Image.composite(Image.new("RGB", aprons.size, (26, 36, 41)),
                           floor.crop((0, 0, floor.width, aprons.height)).convert("RGB"),
                           aprons.filter(ImageFilter.GaussianBlur(1)))
    worn.putalpha(floor.getchannel("A").crop((0, 0, floor.width, aprons.height)))
    floor.paste(worn)
    canvas.alpha_composite(floor, (0, GROUND - 3))

    engraving = Image.new("RGBA", (384, 46))
    pen = ImageDraw.Draw(engraving)
    corners = ((21, 16), (103, 3), (281, 3), (363, 16), (284, 32), (101, 32))
    for start, end in zip(corners, (*corners[1:], corners[0])):
        pen.line(((start[0], start[1] + 2), (end[0], end[1] + 2)), fill=(9, 16, 22, 145), width=2)
        pen.line((start, end), fill=(153, 143, 101, 91), width=2)
    pen.line(((91, 16), (155, 8), (224, 11), (268, 18), (216, 25), (155, 23), (132, 17),
              (176, 13), (212, 17), (184, 20)), fill=(145, 145, 109, 92), width=2)
    for cut in ((67, 6, 72, 16), (304, 6, 312, 12), (127, 26, 134, 36), (248, 23, 256, 35)):
        pen.rectangle(cut, fill=(0, 0, 0, 0))
    canvas.alpha_composite(engraving, (SHELL_X - 192, GROUND + 3))

    shade = Image.new("L", (1, floor.height))
    shade.putdata([round(169 * (y / (floor.height - 1)) ** 1.6) for y in range(floor.height)])
    shadow = Image.new("RGBA", floor.size, (5, 12, 16))
    shadow.putalpha(shade.resize(floor.size))
    canvas.alpha_composite(shadow, (0, GROUND - 3))


def _place_rails(canvas, platforms, show_carriages):
    rails = ROOT / "assets/sprites/rail"
    source = rgba(rails / "relic-track-blue-v4.png").transpose(Image.Transpose.ROTATE_90)
    carriage = rgba(rails / "relic-carriage-v2.png") if show_carriages else None
    bracket = rgba(TERRAIN_ART / "lower-route-a-wall-v1/rail-bracket.png").crop((544, 26, 1620, 692))
    bracket = bracket.crop(bracket.getbbox())
    top_mount = resize(bracket, (58, 34))
    foot_mount = resize(bracket, (54, 28))
    for x, ledge in zip(RAIL_CENTERS, (LEDGES[0], LEDGES[-1])):
        anchor = ledge[2] + 16
        length = GROUND - anchor
        glow = Image.new("L", (38, length))
        ImageDraw.Draw(glow).line((19, 9, 19, length - 8), fill=80, width=6)
        halo = Image.new("RGBA", glow.size, (48, 125, 196))
        halo.putalpha(glow.filter(ImageFilter.GaussianBlur(5)))
        canvas.alpha_composite(halo, (x - 19, anchor))
        canvas.alpha_composite(resize(source, (12, length)), (x - 6, anchor))
    for name, left, top, width, bottom in LEDGES:
        _place_ledge(canvas, platforms[name], left, top, width, bottom)
    # Mount the right bracket on the underside of the new arch pier.
    mount_tops = (LEDGES[0][2] + 28, LEDGES[-1][4] - 24)
    for x, top in zip(RAIL_CENTERS, mount_tops):
        canvas.alpha_composite(top_mount, (x - top_mount.width // 2, top))
        canvas.alpha_composite(foot_mount, (x - foot_mount.width // 2, GROUND - 19))
        if carriage is not None:
            canvas.alpha_composite(carriage, (x - carriage.width // 2, 389))


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


def stage_terrain(*, gate_closed=True, show_carriages=True):
    """Compose art over the B1 walk lines and retain the existing tunnel."""
    platforms = json.loads((PLATFORM_ART / "manifest.json").read_text(encoding="utf-8"))["platforms"]
    old_terrain = rgba(ART / "terrain.png")
    canvas = Image.new("RGBA", old_terrain.size)

    if gate_closed:
        gate = rgba(ART / "right-passage-gate.png")
        canvas.alpha_composite(gate, (GATE_LEFT, GROUND - gate.height))
    canvas.alpha_composite(old_terrain.crop((0, 0, old_terrain.width, 663)))
    _place_decor(canvas, REAR_BANK, (129, 166, 171), GROUND + 9)
    _place_floor(canvas)
    _place_rails(canvas, platforms, show_carriages)
    _place_decor(canvas, FLOOR_MOSS, (155, 198, 187), GROUND + 4)
    _place_decor(canvas, (("split-slate-scrap", 328, 57, False), ("moss-rock-chips", 471, 66, True),
                          ("split-slate-scrap", 1944, 60, True), ("weathered-marker-fragment", 2043, 43, False)),
                 (166, 183, 185), GROUND + 2)
    return canvas

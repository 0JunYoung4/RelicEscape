"""Bake a compact B1 light source and preview it at game size."""

from math import cos, hypot, sqrt, tau

from PIL import Image

from tools.b1_defeat_lighting import apply_light
from tools.render_b1_defeat_orb import (
    CELL,
    COLUMNS,
    FRAME_COUNT,
    FRAME_MS,
    PREVIEW_BOUNDS,
    PREVIEW_CENTER,
)
from tools.render_b1_defeat_preview import (
    BLUE_LIGHT,
    LANCZOS,
    OUTPUT,
    SIZE,
    WISP_START,
    capture_room,
    draw_pose,
    glow,
    load_pose,
)


DESTINATION = OUTPUT.with_name("defeat-orb-v3")
PIVOT = CELL // 2
CORE_SHADE = (79, 140, 186)
CORE_LIGHT = (210, 240, 252)


def light_level(phase):
    return (1 - cos(phase + .4)) / 2


def orb_frame(phase):
    pulse = (1 - cos(phase)) / 2
    brightness = light_level(phase)
    frame = Image.new("RGBA", (CELL, CELL))
    glow(frame, PIVOT, PIVOT, 45 + 4 * pulse, BLUE_LIGHT, 68 + 21 * brightness)
    glow(frame, PIVOT, PIVOT, 29 + 2 * pulse, (94, 167, 223), 106 + 16 * brightness)

    # Only the small source is solid. Its silhouette stays at the cell pivot.
    radius = 10.6 + .68 * pulse
    source = Image.new("RGBA", frame.size)
    pixels = []
    for y in range(CELL):
        for x in range(CELL):
            u = (x + .5 - PIVOT) / radius
            v = (y + .5 - PIVOT) / radius
            r = hypot(u, v)
            if r >= 1:
                pixels.append((0, 0, 0, 0))
                continue
            z = sqrt(1 - r * r)
            surface = max(0, .89 * z - .29 * u - .35 * v)
            rgb = tuple(round(shade + (light - shade) * surface)
                        for shade, light in zip(CORE_SHADE, CORE_LIGHT))
            edge = min(1, (1 - r) * radius / 2)
            alpha = round((233 + 12 * brightness) * edge * edge * (3 - 2 * edge))
            pixels.append((*rgb, alpha))
    source.putdata(pixels)
    frame.alpha_composite(source)
    return frame


def chamber_frames(frames, phases):
    background, foreground = capture_room()
    after = load_pose("after-flash.png")
    boss = Image.new("RGBA", SIZE)
    draw_pose(boss, WISP_START, after, after)
    x, y = PREVIEW_CENTER
    size = CELL // 2
    for frame, phase in zip(frames, phases):
        light = Image.new("RGBA", SIZE)
        brightness = light_level(phase)
        glow(light, x, y, 89 + 6 * brightness, BLUE_LIGHT, 90 + 17 * brightness)
        preview = apply_light(background, light, .53)
        preview.alpha_composite(apply_light(boss, light, .74))
        preview.alpha_composite(frame.resize((size, size), LANCZOS), (x - size // 2, y - size // 2))
        preview.alpha_composite(apply_light(foreground, light, .30))
        yield preview.crop(PREVIEW_BOUNDS).convert("RGB")


def main():
    phases = [index * tau / FRAME_COUNT for index in range(FRAME_COUNT)]
    frames = [orb_frame(phase) for phase in phases]
    sheet = Image.new("RGBA", (CELL * COLUMNS, CELL * (FRAME_COUNT // COLUMNS)))
    for index, frame in enumerate(frames):
        row, column = divmod(index, COLUMNS)
        sheet.paste(frame, (column * CELL, row * CELL))

    DESTINATION.mkdir(parents=True, exist_ok=True)
    sheet.save(DESTINATION / "energy-orb-sheet.png", optimize=True)
    first, *rest = chamber_frames(frames, phases)
    first.save(DESTINATION / "energy-orb-hover.webp", save_all=True, append_images=rest,
               duration=FRAME_MS, loop=0, lossless=True, method=4)
    print(f"Rendered {FRAME_COUNT} frames of {CELL} x {CELL} at {FRAME_MS} ms in {DESTINATION}")


if __name__ == "__main__":
    main()

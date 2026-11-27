"""Render a 16-frame blue energy hover and preview it in the B1 chamber."""

from math import cos, pi, sin, tau

from PIL import Image

from tools.b1_defeat_lighting import apply_light
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


DESTINATION = OUTPUT.with_name("defeat-orb-v1")
CELL = 128
COLUMNS = 4
FRAME_COUNT = 16
FRAME_MS = 75
PREVIEW_CENTER = (533, 267)
PREVIEW_BOUNDS = (218, 207, 742, 516)


def hover_offset(phase):
    return 2.5 * sin(phase), 5 * cos(phase)


def draw_energy_flow(frame, x, y, radius, phase):
    # Two broad, open currents fold toward the center without a hard outline.
    for stream in range(2):
        offset = phase + pi * stream
        sweep = 2.25 + .33 * cos(offset)
        for point in range(18):
            along = point / 17
            angle = offset + sweep * along
            distance = radius * (.23 + (.77 + .07 * stream) * along)
            fade = sin(pi * along) ** 1.5
            pulse = .76 + .24 * sin(offset - 3 * along)
            glow(frame, x + distance * cos(angle), y + .87 * distance * sin(angle),
                 7 - 3 * along, (165, 222, 244), 92 * pulse * fade)


def orb_frame(phase):
    frame = Image.new("RGBA", (CELL, CELL))
    dx, dy = hover_offset(phase)
    x, y = CELL / 2 + dx, CELL / 2 + dy
    gather = (1 - cos(phase)) / 2
    radius = 36 + 5 * gather

    glow(frame, x, y, 50 + 5 * gather, BLUE_LIGHT, 76 + 20 * gather)
    glow(frame, x, y, radius + 5, (87, 165, 218), 171 + 28 * gather)
    glow(frame, x + 2 * cos(phase), y + 2 * sin(phase), radius * .73,
         (138, 204, 239), 184 + 24 * gather)
    draw_energy_flow(frame, x, y, radius, phase)
    glow(frame, x - 2 * sin(phase), y - 3 * cos(phase), 14 + 2 * gather,
         (214, 240, 252), 193 + 24 * gather)

    for index in range(5):
        angle = phase + index * tau / 5 + .16 * sin(phase - index)
        distance = radius + 7 + 3 * sin(phase + 2 * index)
        brightness = .26 + .74 * ((1 + sin(phase + 2.4 * index)) / 2) ** 2
        glow(frame, x + distance * cos(angle), y + .89 * distance * sin(angle),
             3.9 - .35 * (index % 3), (155, 213, 240), 152 * brightness)

    return frame


def chamber_frames(frames, phases):
    background, foreground = capture_room()
    after = load_pose("after-flash.png")
    boss = Image.new("RGBA", SIZE)
    draw_pose(boss, WISP_START, after, after)

    pivot_x, pivot_y = PREVIEW_CENTER
    for sprite, phase in zip(frames, phases):
        light = Image.new("RGBA", SIZE)
        dx, dy = hover_offset(phase)
        pulse = (1 - cos(phase)) / 2
        glow(light, pivot_x + dx / 2, pivot_y + dy / 2,
             94 + 5 * pulse, BLUE_LIGHT, 100 + 17 * pulse)
        preview = apply_light(background, light, .53)
        preview.alpha_composite(apply_light(boss, light, .74))
        preview.alpha_composite(sprite.resize((CELL // 2, CELL // 2), LANCZOS),
                                (pivot_x - CELL // 4, pivot_y - CELL // 4))
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
    first.save(DESTINATION / "energy-orb-hover.webp", save_all=True,
               append_images=rest, duration=FRAME_MS, loop=0, quality=92, method=4)
    print(f"Rendered {FRAME_COUNT} frames of {CELL} x {CELL} at {FRAME_MS} ms in {DESTINATION}")


if __name__ == "__main__":
    main()

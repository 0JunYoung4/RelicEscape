"""Bake the rounded B1 energy sprite and its same-size chamber preview."""

from math import atan2, cos, exp, hypot, pi, sin, tau

from PIL import Image

from tools.render_b1_defeat_orb import (
    CELL,
    COLUMNS,
    FRAME_COUNT,
    FRAME_MS,
    chamber_frames,
    hover_offset,
)
from tools.render_b1_defeat_preview import OUTPUT


DESTINATION = OUTPUT.with_name("defeat-orb-v2")
PIVOT = CELL // 2
LOW_BLUE = (32, 111, 204)
CORE_BLUE = (219, 247, 255)
# Start angle, turn, reach, width, intensity. The currents are open arcs.
CURRENTS = (
    (1.00, 2.35, .96, 8.5, 1.00),
    (3.87, 1.83, .83, 7.1, .77),
    (5.23, 1.94, .91, 7.9, .48),
)


def orb_frame(phase):
    dx, dy = hover_offset(phase)
    center_x, center_y = PIVOT + dx, PIVOT + dy
    radius = 39 + 1.6 * sin(phase)
    core_size = 7.2 + .35 * cos(phase)
    # Different phase offsets leave the core stable while the currents breathe.
    currents = tuple((start + .15 * sin(phase + index * 1.7),
                      turn + .20 * cos(phase + index * 2.3), reach,
                      width * (1 + .13 * sin(phase - index)),
                      intensity * (.88 + .12 * cos(phase + index * 1.5)))
                     for index, (start, turn, reach, width, intensity) in enumerate(CURRENTS))
    pixels = []
    for y in range(CELL):
        for x in range(CELL):
            ox, oy = x + .5 - center_x, y + .5 - center_y
            distance = hypot(ox, oy)
            if distance >= 55:
                pixels.append((0, 0, 0, 0))
                continue

            angle = atan2(oy, ox)
            irregularity = .060 * sin(3 * angle + phase) + .031 * cos(5 * angle - phase)
            normalized = distance / (radius * (1 + irregularity))
            haze = max(0, 1 - (distance / (51 + 27 * irregularity)) ** 2) ** 3
            body = max(0, 1 - normalized ** 2) ** 1.4
            core = exp(-(distance / core_size) ** 2)
            current = 0
            for start, turn, reach, width, intensity in currents:
                along = (normalized - .18) / reach
                if 0 < along < 1:
                    arc = start + turn * along
                    cross = distance * ((angle - arc + pi) % tau - pi)
                    taper = sin(pi * along) ** .75
                    strand = exp(-(cross / (width * (1 - .34 * along))) ** 2)
                    current += intensity * taper * strand

            mottling = .018 * sin(ox * .29 + oy * .23 + phase) * body
            flow_light = min(.78, .11 + .31 * body + .66 * current + mottling)
            radiance = flow_light + (1 - flow_light) * core ** .72
            rgb = tuple(round(low + (high - low) * radiance)
                        for low, high in zip(LOW_BLUE, CORE_BLUE))
            alpha = min(255, round(46 * haze + 183 * body + 134 * current + 47 * core))
            pixels.append((*rgb, alpha) if alpha else (0, 0, 0, 0))

    frame = Image.new("RGBA", (CELL, CELL))
    frame.putdata(pixels)
    return frame


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
               duration=FRAME_MS, loop=0, quality=92, method=4)
    print(f"Rendered {FRAME_COUNT} frames of {CELL} x {CELL} at {FRAME_MS} ms in {DESTINATION}")


if __name__ == "__main__":
    main()

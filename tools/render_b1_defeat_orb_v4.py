"""Bake the condensed energy approved for the B1 defeat sequence."""

from math import atan2, cos, exp, hypot, sin, tau

from PIL import Image

from tools.render_b1_defeat_orb import CELL, COLUMNS, FRAME_COUNT, FRAME_MS
from tools.render_b1_defeat_orb_v3 import chamber_frames
from tools.render_b1_defeat_preview import LANCZOS, OUTPUT


DESTINATION = OUTPUT.with_name("defeat-orb-v4")
SOURCE_CELL = 320
HALF = SOURCE_CELL / 2
NORMALIZER = 115 * 1.15


def condensed_frame(phase):
    phase_sine, phase_cosine = sin(phase), cos(phase)
    breath = .5 - .5 * phase_cosine
    pixels = []
    for y in range(SOURCE_CELL):
        v = (y + .5 - HALF) / NORMALIZER
        for x in range(SOURCE_CELL):
            u = (x + .5 - HALF) / NORMALIZER
            r = hypot(u, v)
            canvas_fade = min(1, (HALF - 4 - r * NORMALIZER) / 12)
            if canvas_fade <= 0 or r >= 1.31:
                pixels.append((0, 0, 0, 0))
                continue

            angle = atan2(v, u)
            wave = (.080 * sin(3 * angle + phase + 2.7 * r)
                    + .043 * cos(5 * angle - phase + 4.2 * r)
                    + .025 * sin(7 * angle + 1.4 * phase))
            d = r * (1 + wave)
            peak = exp(-(d / (.216 + .022 * breath)) ** 2)
            body = exp(-(d / (.326 + .037 * breath)) ** 2)
            halo = exp(-(d / (.573 + .028 * breath)) ** 2)
            current = .5 + .5 * sin(2 * angle - 7.1 * d + phase + .65)
            rim_energy = exp(-((d - .40) / .19) ** 2) * current ** 2
            haze = exp(-((d - .71) / .19) ** 2) * (.5 + .5 * cos(3 * angle + phase)) ** 3

            shadow_x = u + .185 + .034 * phase_sine
            shadow_y = v - .119 - .031 * phase_cosine
            veil = exp(-((shadow_x + .37 * shadow_y) / .10) ** 2 - (shadow_y / .21) ** 2)
            intensity = 2.85 * peak + .73 * body + .55 * rim_energy + .105 * halo
            heat = max(0, 1 - exp(-intensity) - .23 * veil * (body - peak))
            color = (round(39 + 215 * heat ** 1.15),
                     round(103 + 152 * heat ** .85),
                     round(202 + 53 * heat ** .65))
            falloff = 1 - (r / 1.31) ** 4
            opacity = (1 - exp(-(3.0 * peak + 1.31 * body + .64 * halo
                                  + .35 * rim_energy + .24 * haze))) * falloff ** 2
            alpha = round(255 * opacity * canvas_fade)
            pixels.append((*color, alpha) if alpha else (0, 0, 0, 0))

    frame = Image.new("RGBA", (SOURCE_CELL, SOURCE_CELL))
    frame.putdata(pixels)
    return frame


def main():
    phases = [tau * index / FRAME_COUNT for index in range(FRAME_COUNT)]
    frames = [condensed_frame(phase).resize((CELL, CELL), LANCZOS) for phase in phases]
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

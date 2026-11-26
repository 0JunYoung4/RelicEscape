"""Render separate B1 roar pressure and debris layers with transparent backgrounds."""

from dataclasses import dataclass
from functools import lru_cache
import json
import math
from pathlib import Path
import random

from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
BOSS_ART = ROOT / "assets/concepts/b1-hermit-crab"
OUTPUT = BOSS_ART / "roar-v1"
SIZE = (900, 440)
SIZE_HALF = (450, 220)
PIVOT = (450, 420)
WAVE_ORIGIN = (450, 254)
FPS = 24
FRAME_COUNT = 48
COLUMNS = 8
DURATIONS = [round((i + 1) * 1000 / FPS) - round(i * 1000 / FPS) for i in range(FRAME_COUNT)]


def half_point(x, y):
    return round(x / 2), round(y / 2)


def ramp(value, start, end):
    return min(1.0, max(0.0, (value - start) / (end - start)))


def ribbon(pen, side, span, radius, rise, width, opacity, phase):
    """Draw a broken section of an expanding pressure front."""
    points = []
    start, end = span
    for i in range(17):
        fraction = i / 16
        angle = math.radians(start + (end - start) * fraction)
        shake = 1.7 * math.sin(12 * angle + phase) + 1.2 * math.sin(31 * angle)
        taper = math.sin(math.pi * fraction) ** .58
        points.append((angle, shake, width * taper))

    def band(offset, thickness, color):
        outer = []
        inner = []
        for angle, shake, taper in points:
            cosine, sine = math.cos(angle), math.sin(angle)
            for edge, sign in ((outer, 1), (inner, -1)):
                rim = shake + offset + sign * taper * thickness
                edge.append(half_point(WAVE_ORIGIN[0] + side * (radius + rim) * cosine,
                                       WAVE_ORIGIN[1] + (rise + .64 * rim) * sine))
        pen.polygon(outer + inner[::-1], fill=color)

    band(0, 1.7, (65, 120, 135, round(opacity * .38)))
    band(1, 1, (134, 189, 197, round(opacity * .73)))
    band(3, .56, (217, 233, 222, opacity))


def wave_frame(frame):
    canvas = Image.new("RGBA", SIZE_HALF)
    seconds = frame / FPS
    for onset, magnitude in ((16 / FPS, 1.0), (22 / FPS, .48)):
        age = seconds - onset
        if not 0 <= age < .46:
            continue
        front = Image.new("RGBA", SIZE_HALF)
        pen = ImageDraw.Draw(front)
        radius = 205 + 503 * age
        rise = 52 + 154 * age
        force = ramp(age, -.035, .09) * (1 - ramp(age, .16, .46)) ** 1.32 * magnitude
        opacity = round(245 * force)
        for side in (-1, 1):
            yaw = 5 * side
            for span, width, energy in (((-73 + yaw, -54 + yaw), 4.0, .69),
                                        ((-49 + yaw, -18 + yaw), 5.6, .93),
                                        ((-13 + yaw, 25 + yaw), 6.8, 1.0),
                                        ((32 + yaw, 59 + yaw), 4.5, .76)):
                ribbon(pen, side, span, radius, rise, width, round(opacity * energy), 26 * age)
            ribbon(pen, side, (-36 - yaw, 29 - yaw), radius - 30, rise - 11, 2.8,
                   round(opacity * .41), 30 * age)

            # Flecks follow each front and break up the near-horizontal gaps.
            for idx, y_offset in enumerate((-72, -53, -35, 23, 48, 70)):
                x = WAVE_ORIGIN[0] + side * (radius - 24 - (idx % 3) * 18)
                y = WAVE_ORIGIN[1] + y_offset * (.67 + 1.6 * age)
                pen.line((half_point(x, y), half_point(x + side * (8 + 26 * age), y + y_offset * .06)),
                         fill=(188, 218, 217, round(opacity * (.42 + (idx % 2) * .25))), width=1)
        canvas.alpha_composite(front)
    return canvas.resize(SIZE, Image.Resampling.NEAREST)


@dataclass(frozen=True)
class Particle:
    x: float
    vx: float
    vy: float
    start: float
    life: float
    size: float
    tone: int
    spin: float


def particles():
    rng = random.Random(1090)
    cloud, gravel = [], []
    for side in (-1, 1):
        for i in range(17):
            cloud.append(Particle(PIVOT[0] + side * rng.uniform(117, 227), side * rng.uniform(80, 250),
                                  rng.uniform(17, 65), .68 + rng.uniform(0, .13), rng.uniform(.45, .95),
                                  rng.uniform(16, 37), i % 3, 0))
        for i in range(14):
            gravel.append(Particle(PIVOT[0] + side * rng.uniform(143, 233), side * rng.uniform(54, 222),
                                   rng.uniform(68, 204), .70 + rng.uniform(0, .11), rng.uniform(.47, .85),
                                   rng.uniform(5, 16), i % 3, rng.uniform(-440, 440)))
    return cloud, gravel


@lru_cache(maxsize=96)
def dust_tile(radius, tone):
    mask = Image.new("L", (2 * radius + 4, 2 * radius + 4))
    r = radius
    draw = ImageDraw.Draw(mask)
    draw.ellipse((1, .72 * r, 2 * r + 2, 1.63 * r + 2), fill=94)
    draw.ellipse((.37 * r, .36 * r, 1.64 * r, 1.51 * r), fill=160)
    draw.ellipse((.94 * r, .61 * r, 1.85 * r, 1.57 * r), fill=128)
    mask = mask.filter(ImageFilter.GaussianBlur(max(1, radius * .13)))
    tile = Image.new("RGBA", mask.size, ((142, 144, 116), (109, 130, 123), (171, 162, 123))[tone])
    tile.putalpha(mask)
    return tile


def debris_frame(frame, cloud, gravel, shards):
    canvas = Image.new("RGBA", SIZE_HALF)
    seconds = frame / FPS
    for dust in cloud:
        age = seconds - dust.start
        if not 0 <= age < dust.life:
            continue
        fade = ramp(age, -.025, .13) * (1 - ramp(age, .12, dust.life)) ** 1.28
        x, y = half_point(dust.x + dust.vx * age / (1 + age), PIVOT[1] - 10 - dust.vy * age)
        tile = dust_tile(round(dust.size * (.56 + age) / 2), dust.tone).copy()
        tile.putalpha(tile.getchannel("A").point(lambda a: round(a * fade * .83)))
        canvas.alpha_composite(tile, (x - tile.width // 2, y - tile.height // 2))

    for chip in gravel:
        age = seconds - chip.start
        if not 0 <= age < chip.life:
            continue
        height = chip.vy * age - 242 * age ** 2
        if height < -2:
            continue
        x, y = half_point(chip.x + chip.vx * age, PIVOT[1] - 4 - height)
        tile = shards[chip.tone].copy()
        tile.thumbnail((max(2, round(chip.size / 2)), max(2, round(chip.size / 2))), Image.Resampling.LANCZOS)
        tile = tile.rotate(chip.spin * age, resample=Image.Resampling.NEAREST, expand=True)
        fade = 1 - ramp(age, .19, chip.life)
        tile.putalpha(tile.getchannel("A").point(lambda a: round(a * fade)))
        canvas.alpha_composite(tile, (x - tile.width // 2, y - tile.height // 2))
    return canvas.resize(SIZE, Image.Resampling.NEAREST)


def export(name, frames):
    rows = math.ceil(len(frames) / COLUMNS)
    sheet = Image.new("RGBA", (SIZE[0] * COLUMNS, SIZE[1] * rows))
    for index, frame in enumerate(frames):
        sheet.paste(frame, (index % COLUMNS * SIZE[0], index // COLUMNS * SIZE[1]))
    sheet.save(OUTPUT / f"{name}-sheet.png", optimize=True)
    frames[0].save(OUTPUT / f"{name}-animation.webp", save_all=True, append_images=frames[1:],
                   duration=DURATIONS, loop=1, lossless=True, method=4)


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    rng_cloud, rng_gravel = particles()
    source = BOSS_ART / "ceiling-rock-v2/debris-v1"
    shards = []
    for index in range(1, 4):
        with Image.open(source / f"shard-small-{index:02}.png") as image:
            sprite = image.convert("RGBA")
            shards.append(sprite.crop(sprite.getbbox()))
    export("roar-wave", [wave_frame(frame) for frame in range(FRAME_COUNT)])
    export("roar-debris", [debris_frame(frame, rng_cloud, rng_gravel, shards) for frame in range(FRAME_COUNT)])

    spec = {
        "frame_size": SIZE, "pivot": PIVOT, "wave_origin": WAVE_ORIGIN,
        "columns": COLUMNS, "frame_count": FRAME_COUNT, "fps": FPS,
        "frame_durations_ms": DURATIONS,
        "layers": [
            {"name": "roar-wave", "first_visible_frame": 16, "order": "behind_actors"},
            {"name": "roar-debris", "first_visible_frame": 17, "order": "in_front_of_boss"},
        ],
    }
    (OUTPUT / "roar-effects.json").write_text(json.dumps(spec, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

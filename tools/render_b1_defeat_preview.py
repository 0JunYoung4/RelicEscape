"""Render the two B1 defeat poses in the cave, without gameplay hooks."""

from ctypes import c_ubyte
from math import sin
import os
from pathlib import Path
from random import Random

from PIL import Image, ImageChops, ImageDraw, ImageFilter

from tools.b1_room_art import ROOM_SIZE, WORLD_PER_ART_PIXEL, B1RoomArt
from tools.preview_b1_intro import ART, GROUND, SHELL_X
from tools.preview_b1_roar_game import SIZE, _read_pixels


OUTPUT = ART.parent / "defeat-v1"
CENTER, FLOOR = 480, 496
HITSTOP, CLAW_FALL, CONDENSE, BURST, REVEAL, SETTLED = 150, 440, 1450, 1600, 1900, 2500
HOLD = 1500
SWAP_POSE = 1700
OVERSCAN = 12
LANCZOS = Image.Resampling.LANCZOS


def progress(t, start, end):
    return max(0, min(1, (t - start) / (end - start)))


def capture_room():
    from main import Camera
    from pico2d import pico2d as pico

    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    os.environ.setdefault("SDL_RENDER_DRIVER", "software")
    pico.open_canvas(*SIZE)
    room = None
    try:
        scale = WORLD_PER_ART_PIXEL
        camera = Camera(SIZE[0], ROOM_SIZE[0] * scale, zoom=.75 / scale)
        camera.x, camera.y = (SHELL_X - 640) * scale, (GROUND - 762) * scale
        pixels = (c_ubyte * (SIZE[0] * SIZE[1] * 4))()
        room = B1RoomArt(gate_closed=True, show_carriages=True)

        def clear(value):
            pico.SDL_SetRenderDrawColor(pico.renderer, value, value, value, 255)
            pico.SDL_RenderClear(pico.renderer)

        clear(0)
        room.draw_behind_actors(camera, show_boulder=False)
        room.draw_actor_shadows(camera, SHELL_X, -5000)
        background = _read_pixels(pico, pixels).convert("RGBA")

        clear(0)
        room.draw_in_front(camera)
        black = _read_pixels(pico, pixels)
        clear(255)
        room.draw_in_front(camera)
        white = _read_pixels(pico, pixels)
        # Recover straight alpha from SDL's black and white composites.
        alpha = ImageChops.invert(ImageChops.subtract(white, black).convert("L"))
        foreground = Image.new("RGBA", SIZE)
        foreground.putdata([
            tuple(min(255, (channel * 255 + a // 2) // a) for channel in rgb) + (a,)
            if a else (0, 0, 0, 0)
            for rgb, a in zip(black.get_flattened_data(), alpha.get_flattened_data())
        ])
        return background, foreground
    finally:
        room = None
        pico.close_canvas()


def load_pose(name):
    with Image.open(OUTPUT / name) as source:
        box = source.getchannel("A").point(lambda value: 255 if value > 8 else 0).getbbox()
        crop = source.crop(box)
        scale = 387 / 1459
        left = CENTER + round((box[0] - source.width / 2) * scale)
        pose = crop.resize((round(crop.width * scale), round(crop.height * scale)), LANCZOS)
    return pose, left


def draw_pose(frame, t, before, after):
    pose, left = before if t < SWAP_POSE else after
    if t < SWAP_POSE:
        drop = progress(t, HITSTOP, CLAW_FALL)
        shiver = 0
        if HITSTOP <= t < CONDENSE:
            strength = 1 + 2 * progress(t, CLAW_FALL, CONDENSE)
            shiver = round(sin(t * .057) * strength)
        height = round(pose.height * (1.02 - .05 * drop))
        y = FLOOR - height - round(4 * (1 - drop))
        frame.alpha_composite(pose.resize((pose.width, height), LANCZOS), (left + shiver, y))
    else:
        compression = 1 - progress(t, SWAP_POSE, 2100)
        height = round(pose.height * (1 - .025 * compression))
        frame.alpha_composite(pose.resize((pose.width, height), LANCZOS), (left, FLOOR - height))


def glow(frame, x, y, radius, color, opacity):
    if opacity <= 0:
        return
    radius = max(1, round(radius))
    size = radius * 2
    alpha = Image.new("L", (size, size))
    ImageDraw.Draw(alpha).ellipse((radius * .35, radius * .35, radius * 1.65, radius * 1.65),
                                 fill=round(opacity))
    image = Image.new("RGBA", (size, size), (*color, 0))
    image.putalpha(alpha.filter(ImageFilter.GaussianBlur(radius * .29)))
    frame.alpha_composite(image, (round(x - radius), round(y - radius)))


def energy(frame, t):
    if not 550 <= t < BURST:
        return
    charge = progress(t, 550, CONDENSE)
    collapse = progress(t, CONDENSE, BURST)
    streaks = Image.new("RGBA", SIZE)
    ink = ImageDraw.Draw(streaks)
    for index, (x, y, lean) in enumerate(((347, 392, -25), (430, 356, -16), (500, 335, 9),
                                           (569, 374, 26), (606, 413, 31))):
        lift = (16 + 42 * charge) * (1 - collapse)
        start_x = x + (CENTER - x) * collapse
        start_y = y + (400 - y) * collapse
        points = []
        for step in range(9):
            distance = step / 8
            curve = sin(t * .013 + index * 2 + distance * 5) * 8 * distance
            points.append((start_x + (lean * distance + curve) * (1 - collapse),
                           start_y - lift * distance))
        ink.line(points, fill=(114, 224, 252, round((70 + 133 * charge) * (1 - collapse))), width=2)
    frame.alpha_composite(streaks.filter(ImageFilter.GaussianBlur(4)))
    frame.alpha_composite(streaks)
    glow(frame, CENTER, 399, 48 - 21 * collapse, (174, 239, 255),
         28 * charge + 136 * collapse)


def draw_dust(frame, t, particles):
    layer = Image.new("RGBA", SIZE)
    ink = ImageDraw.Draw(layer)
    contact = (t - CLAW_FALL) / 1000
    blast = (t - BURST) / 1000
    for index, (direction, speed, rise, radius) in enumerate(particles):
        age = contact if index < 10 else blast
        life = .36 if index < 10 else .75
        if not 0 <= age < life:
            continue
        origin = 358 if index < 10 else CENTER
        x = origin + direction * (13 + age * speed)
        y = FLOOR - 2 - max(0, (rise - age * 102) * age)
        size = radius * (1 + age * .7)
        alpha = round((1 - age / life) * (95 if index < 10 else 115))
        ink.ellipse((x - size, y - size * .58, x + size, y + size * .58),
                    fill=(160, 183, 168, alpha))
    if 0 <= blast < .46:
        reach = 56 + blast * 530
        ink.ellipse((CENTER - reach, FLOOR - 9, CENTER + reach, FLOOR + 7),
                    outline=(148, 225, 239, round(115 * (1 - blast / .46))), width=2)
    if .09 <= blast < .78:
        for index in range(11):
            age = blast - .09 - (index % 3) * .032
            if age < 0:
                continue
            x = (45 + index * 91) + sin(index * 2.6) * (14 + 20 * age)
            y = 22 + (index % 4) * 15 + 215 * age ** 2
            ink.polygon([(x, y), (x + 3, y + 2), (x + 1, y + 6), (x - 2, y + 2)],
                        fill=(101, 128, 125, round(150 * (1 - blast / .78))))
    frame.alpha_composite(layer.filter(ImageFilter.GaussianBlur(.6)))


def render(t, room, poses, particles):
    bg, fg = room
    frame = bg.copy()
    expansion = progress(t, BURST, 1810)
    fade = 1 - progress(t, 1730, 2350)
    if t >= BURST:
        glow(frame, CENTER, 399, 75 + 485 * expansion, (183, 226, 251), 192 * fade)
    draw_pose(frame, t, *poses)
    energy(frame, t)
    if t >= BURST:
        glow(frame, CENTER, 406, 47 + 270 * expansion, (216, 245, 255), 188 * fade)
    draw_dust(frame, t, particles)
    frame.alpha_composite(fg)
    if t >= BURST:
        glow(frame, CENTER, FLOOR - 36, 65 + 385 * expansion, (178, 224, 244), 59 * fade)
    flash = progress(t, 1640, 1670) * (1 - progress(t, 1740, REVEAL))
    if flash:
        frame.alpha_composite(Image.new("RGBA", SIZE, (255, 255, 255, round(flash * 255))))

    shake = 0
    if HITSTOP <= t < CONDENSE:
        shake = 1.1 + 2.6 * progress(t, HITSTOP, CONDENSE)
    elif BURST <= t < REVEAL:
        shake = 6 * (1 - progress(t, BURST, REVEAL))
    center_x = OVERSCAN // 2 + round(sin(t * .083) * shake)
    center_y = OVERSCAN // 2 + round(sin(t * .061) * shake * .46)
    view = frame.resize((SIZE[0] + OVERSCAN, SIZE[1] + OVERSCAN), LANCZOS)
    return view.crop((center_x, center_y, center_x + SIZE[0], center_y + SIZE[1])).convert("RGB")


def main():
    room = capture_room()
    poses = load_pose("before-flash.png"), load_pose("after-flash.png")
    rng = Random(405)
    particles = [
        (-1 if index % 2 == 0 else 1, rng.uniform(95, 410), rng.uniform(31, 82), rng.uniform(.7, 3.2))
        for index in range(34)
    ]
    beats = {HITSTOP, CLAW_FALL, CONDENSE, BURST, SWAP_POSE, REVEAL, SETTLED, 1640, 1670, 1740}
    times = sorted(beats | set(range(0, SETTLED, 40)))
    frames = [render(t, room, poses, particles) for t in times]
    durations = [end - start for start, end in zip(times, times[1:])] + [HOLD]
    destination = OUTPUT / "defeat-preview.webp"
    frames[0].save(destination, format="WEBP", save_all=True, append_images=frames[1:],
                   duration=durations, loop=0, quality=89, method=4)
    print(f"Captured {sum(durations)} ms into {destination}")


if __name__ == "__main__":
    main()

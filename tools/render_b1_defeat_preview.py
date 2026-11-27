"""Render the B1 defeat preview and its separate transparent flash."""

from ctypes import c_ubyte
from math import hypot, sin
import os
from random import Random

from PIL import Image, ImageChops, ImageDraw, ImageFilter

from tools.b1_room_art import ROOM_SIZE, WORLD_PER_ART_PIXEL, B1RoomArt
from tools.preview_b1_intro import ART, GROUND, SHELL_X
from tools.preview_b1_roar_game import SIZE, _read_pixels


OUTPUT = ART.parent / "defeat-v1"
CENTER, FLOOR = 480, 496
HITSTOP, CLAW_FALL, STILL, BURST, REVEAL, SETTLED = 150, 440, 1450, 1600, 1900, 2500
BEAM_SWELL_END, BEAM_END, LIGHT_END = 1660, 1870, 2350
WHITE_START, WHITE_PEAK, WHITE_RELEASE = 1670, 1710, 1770
FLASH_Y = 399
# Each ray has its own onset, exit point past the camera, and narrow half-width.
BEAMS = (
    (550, (409, 382), (-40, 214), 6),
    (670, (553, 369), (1000, 207), 6),
    (790, (478, 341), (330, -42), 5),
    (910, (396, 410), (-40, 459), 7),
    (1030, (588, 418), (1000, 505), 7),
    (1150, (526, 320), (788, -42), 5),
    (1270, (458, 426), (289, 582), 6),
    (1390, (532, 436), (778, 582), 6),
)
BEAM_START = BEAMS[0][0]
BEAM_TRAVEL = 45
HOLD = 1500
SWAP_POSE = 1730
OVERSCAN = 12
LANCZOS = Image.Resampling.LANCZOS
GLOW_PROFILE = Image.radial_gradient("L").point(
    [round(255 * max(0, 1 - level / 175) ** 1.7) for level in range(256)]
)


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


def shiver_offset(t):
    if not HITSTOP <= t < STILL:
        return 0
    strength = 1 + 2 * progress(t, CLAW_FALL, STILL)
    return round(sin(t * .057) * strength)


def draw_pose(frame, t, before, after):
    pose, left = before if t < SWAP_POSE else after
    if t < SWAP_POSE:
        drop = progress(t, HITSTOP, CLAW_FALL)
        height = round(pose.height * (1.02 - .05 * drop))
        y = FLOOR - height - round(4 * (1 - drop))
        frame.alpha_composite(pose.resize((pose.width, height), LANCZOS),
                              (left + shiver_offset(t), y))
    else:
        compression = 1 - progress(t, SWAP_POSE, 2100)
        height = round(pose.height * (1 - .025 * compression))
        frame.alpha_composite(pose.resize((pose.width, height), LANCZOS), (left, FLOOR - height))


def glow(frame, x, y, radius, color, opacity):
    if opacity <= 0:
        return
    radius = max(1, round(radius))
    size = radius * 2
    alpha = GLOW_PROFILE.resize((size, size), Image.Resampling.BILINEAR)
    alpha = alpha.point([round(level * opacity / 255) for level in range(256)])
    image = Image.new("RGBA", (size, size), (*color, 0))
    image.putalpha(alpha)
    frame.alpha_composite(image, (round(x - radius), round(y - radius)))


def beam_flash(t):
    """Draw staggered beams from shell seams to beyond the frame."""
    spill = Image.new("RGBA", SIZE)
    if not BEAM_START < t < BEAM_END:
        return spill
    core = Image.new("RGBA", SIZE)
    shade = ImageDraw.Draw(spill)
    light = ImageDraw.Draw(core)
    swell = progress(t, BURST, BEAM_SWELL_END) ** 1.7
    remaining = 1 - progress(t, WHITE_PEAK, BEAM_END)
    shiver = shiver_offset(t)

    for start, (x, y), (far_x, far_y), width in BEAMS:
        reach = progress(t, start, start + BEAM_TRAVEL)
        if reach == 0:
            continue
        x += shiver
        dx, dy = far_x - x, far_y - y
        length = hypot(dx, dy)
        nx, ny = -dy / length, dx / length
        tip_x, tip_y = x + dx * reach, y + dy * reach
        tip_width = width * (.30 + .70 * reach) * (1 + 17 * swell)
        root_width = width * (.25 + 6 * swell)
        intensity = (.48 + .52 * reach) * remaining

        for painter, spread, color, opacity in (
            (shade, 1.65, (91, 177, 250), 125 + 48 * swell),
            (light, .33 + .47 * swell, (220, 247, 255), 220 + 35 * swell),
        ):
            root, tip = root_width * spread, tip_width * spread
            painter.polygon((
                (x - root * nx, y - root * ny),
                (tip_x - tip * nx, tip_y - tip * ny),
                (tip_x + tip * nx, tip_y + tip * ny),
                (x + root * nx, y + root * ny),
            ), fill=(*color, round(opacity * intensity)))

    spill = spill.filter(ImageFilter.GaussianBlur(4 + 9 * swell))
    spill.alpha_composite(core)
    return spill


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
    fade = 1 - progress(t, SWAP_POSE, LIGHT_END)
    if t >= BURST:
        glow(frame, CENTER, FLASH_Y, 75 + 485 * expansion, (183, 226, 251), 192 * fade)
    draw_pose(frame, t, *poses)
    draw_dust(frame, t, particles)
    frame.alpha_composite(fg)
    if t >= BURST:
        glow(frame, CENTER, FLOOR - 36, 65 + 385 * expansion, (178, 224, 244), 59 * fade)
    if BEAM_START < t < BEAM_END:
        frame.alpha_composite(beam_flash(t))
    flash = progress(t, WHITE_START, WHITE_PEAK) * (1 - progress(t, WHITE_RELEASE, REVEAL))
    if flash:
        frame.alpha_composite(Image.new("RGBA", SIZE, (255, 255, 255, round(flash * 255))))

    shake = 0
    if HITSTOP <= t < STILL:
        shake = 1.1 + 2.6 * progress(t, HITSTOP, STILL)
    elif BURST <= t < REVEAL:
        shake = 6 * (1 - progress(t, BURST, REVEAL))
    center_x = OVERSCAN // 2 + round(sin(t * .083) * shake)
    center_y = OVERSCAN // 2 + round(sin(t * .061) * shake * .46)
    view = frame.resize((SIZE[0] + OVERSCAN, SIZE[1] + OVERSCAN), LANCZOS)
    return view.crop((center_x, center_y, center_x + SIZE[0], center_y + SIZE[1])).convert("RGB")


def flash_beat_times():
    starts = {start for start, *_ in BEAMS}
    arrivals = {start + BEAM_TRAVEL for start in starts}
    return starts | arrivals | {STILL, BURST, BEAM_SWELL_END, WHITE_START,
                                WHITE_PEAK, SWAP_POSE, WHITE_RELEASE, BEAM_END}


def export_flash(beats):
    times = sorted(set(range(BEAM_START, BEAM_END, 20)) | beats)
    frames = [beam_flash(t) for t in times]
    durations = [end - start for start, end in zip(times, times[1:])] + [20]
    destination = OUTPUT / "defeat-flash.webp"
    frames[0].save(destination, format="WEBP", save_all=True, append_images=frames[1:],
                   duration=durations, loop=0, lossless=True, method=4)
    print(f"Captured {sum(durations)} ms of transparent flash into {destination}")


def main():
    room = capture_room()
    poses = load_pose("before-flash.png"), load_pose("after-flash.png")
    rng = Random(405)
    particles = [
        (-1 if index % 2 == 0 else 1, rng.uniform(95, 410), rng.uniform(31, 82), rng.uniform(.7, 3.2))
        for index in range(34)
    ]
    flash_beats = flash_beat_times()
    beats = flash_beats | {HITSTOP, CLAW_FALL, REVEAL, SETTLED}
    beats.update(range(BEAM_START, REVEAL, 20))
    times = sorted(beats | set(range(0, SETTLED, 40)))
    frames = [render(t, room, poses, particles) for t in times]
    durations = [end - start for start, end in zip(times, times[1:])] + [HOLD]
    destination = OUTPUT / "defeat-preview.webp"
    frames[0].save(destination, format="WEBP", save_all=True, append_images=frames[1:],
                   duration=durations, loop=0, quality=89, method=4)
    print(f"Captured {sum(durations)} ms into {destination}")
    export_flash(flash_beats)


if __name__ == "__main__":
    main()

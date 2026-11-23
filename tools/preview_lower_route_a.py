"""Render the A route art plate with the existing rail and ceiling reveal."""

from argparse import ArgumentParser
from ctypes import byref, c_ubyte
from math import hypot
import os
from pathlib import Path
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("SDL_RENDER_DRIVER", "software")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from PIL import Image
from pico2d import pico2d as pico

from lower_route_a import ART_ZOOM as ZOOM, HOLE_PIXEL as HOLE, SHADOW_BOUNDS, lift_path
from main import CAMERA_ZOOM, Camera, RAIL_BEND_IMAGE, RAIL_CARRIAGE_IMAGE, RAIL_IMAGE, RELIC_IMAGE
from player import Player
from rail import BEND_ART_RADIUS, RAIL_ART_SCALE, RAIL_TRAVEL_SPEED, RailCarriage, RailSegment, draw_rail


SHADOW = ROOT / "assets/terrain/lower-route-a-ceiling-shadow-v2.png"

# Anchor positions in art pixels, measured from the top left of the source plate.
V2_UPPER_DOCK = (600, 350)
V2_LOWER_DOCK = (1315, 599)
V2_RAIL_X = 935
WALK_START = (1632, 405)
WALK_END = (1950, 404)


def rail_path(height, version=2):
    if version == 3:
        return lift_path()
    radius = BEND_ART_RADIUS * ZOOM
    upper_x, upper = V2_UPPER_DOCK
    lower_x, lower = V2_LOWER_DOCK
    top_center = (V2_RAIL_X - radius, upper + radius)
    bottom_center = (V2_RAIL_X + radius, lower - radius)
    points = [
        (upper_x, upper), (top_center[0], upper), (V2_RAIL_X, top_center[1]),
        (V2_RAIL_X, bottom_center[1]), (bottom_center[0], lower), (lower_x, lower),
    ]

    def world(point):
        x, y = point
        return x / ZOOM, (height - y) / ZOOM

    centers = (None, top_center, None, bottom_center, None)
    return tuple(
        RailSegment(world(start), world(end), world(center) if center else None)
        for start, end, center in zip(points, points[1:], centers)
    )


def shadow_alpha(position):
    x, y = position
    distance = hypot(x - HOLE[0], y - 32 - HOLE[1])
    progress = min(1.0, max(0.0, (distance - 293) / 118))
    return round(255 * progress * progress * (3 - 2 * progress))


def read_render(x, y, width, height):
    bounds = pico.SDL_Rect(x, y, width, height)
    pixels = (c_ubyte * (width * height * 4))()
    if pico.SDL_RenderReadPixels(pico.renderer, byref(bounds), pico.SDL_PIXELFORMAT_RGBA32,
                                pixels, width * 4) != 0:
        raise RuntimeError(pico.SDL_GetError())
    return Image.frombytes("RGBA", (width, height), bytes(pixels)).convert("RGB")


def save_gif(frames, durations, path):
    palette = frames[-1].quantize(colors=256)
    indexed = [frame.quantize(palette=palette, dither=Image.Dither.NONE) for frame in frames]
    indexed[0].save(path, save_all=True, append_images=indexed[1:],
                    duration=durations, loop=0, optimize=True)


def main(version):
    stem = f"map1-lower-route-a-v{version}"
    plate = ROOT / "assets/concepts" / f"{stem}-plate.png"
    output = ROOT / "docs" / stem
    with Image.open(plate) as source:
        width, height = source.size
    pico.open_canvas(width, height)
    try:
        art = pico.load_image(str(plate))
        shadow = pico.load_image(str(SHADOW))
        straight, bend, carriage = (pico.load_image(str(path)) for path in (
            RAIL_IMAGE, RAIL_BEND_IMAGE, RAIL_CARRIAGE_IMAGE,
        ))
        camera = Camera(width, width / ZOOM, zoom=ZOOM)
        path = rail_path(height, version)
        dock = path[0].start if version == 3 else path[-1].end
        player = Player(0, 0, width / ZOOM)
        player.facing = 1

        def draw(position, *, elapsed=None, carriage_position=dock, relic=None):
            pico.clear_canvas()
            art.draw_to_origin(0, 0, width, height)
            draw_rail(straight, bend, camera, path)
            scale = RAIL_ART_SCALE * ZOOM
            mount = camera.world_to_screen(*carriage_position)
            carriage.draw(*mount, carriage.w * scale, carriage.h * scale)
            if relic is not None:
                relic_scale = ZOOM / CAMERA_ZOOM
                relic.draw(*mount, relic.w * relic_scale, relic.h * relic_scale)
            if elapsed is not None:
                player.x = position[0] / ZOOM
                player.y = (height - position[1]) / ZOOM
                player.state = "walk" if elapsed >= 0 else "idle"
                player.animation_time = max(0, elapsed)
                player.draw(camera)
            x, y, w, h = SHADOW_BOUNDS
            pico.SDL_SetTextureAlphaMod(shadow.texture, shadow_alpha(position))
            shadow.draw_to_origin(x, height - y - h, w, h)

        for name, position in (("covered", WALK_START), ("open", WALK_END)):
            draw(position)
            read_render(0, 0, width, height).save(output.with_name(f"{stem}-{name}.png"))

        frames = []
        left = max(0, width - 780)
        view = left, 0, width - left, min(height, 476)
        for i in range(34):
            t = i / 33
            position = tuple(a + (b - a) * t for a, b in zip(WALK_START, WALK_END))
            draw(position, elapsed=i * .065 if 0 < i < 33 else -1)
            frames.append(read_render(*view))
        save_gif(frames, [550] + [65] * 32 + [900], output.with_suffix(".gif"))

        if version == 3:
            relic = pico.load_image(str(RELIC_IMAGE))
            moving = RailCarriage(path, carriage.w * RAIL_ART_SCALE, carriage.h * RAIL_ART_SCALE)
            moving.direction = 1
            step = moving.length / RAIL_TRAVEL_SPEED / 32
            frames = []
            for i in range(33):
                draw(WALK_END, carriage_position=moving.position, relic=relic)
                frames.append(read_render(470, 270, 625, 405))
                if i < 32:
                    moving.move(step)
            save_gif(frames, [550] + [round(step * 1000)] * 31 + [900],
                     output.with_name(f"{stem}-rail.gif"))
            del relic
        del art, shadow, straight, bend, carriage, player
    finally:
        pico.close_canvas()


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--version", type=int, choices=(2, 3), default=2)
    main(parser.parse_args().version)

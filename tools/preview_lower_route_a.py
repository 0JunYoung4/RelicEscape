"""Render the A route art plate with the existing rail and ceiling reveal."""

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

from main import Camera, RAIL_BEND_IMAGE, RAIL_CARRIAGE_IMAGE, RAIL_IMAGE
from player import Player
from rail import BEND_ART_RADIUS, RAIL_ART_SCALE, RailSegment, draw_rail


PLATE = ROOT / "assets/concepts/map1-lower-route-a-v2-plate.png"
SHADOW = ROOT / "assets/terrain/lower-route-a-ceiling-shadow-v2.png"
OUTPUT = ROOT / "docs/map1-lower-route-a-v2"
ZOOM = 0.4

# Anchor positions in art pixels, measured from the top left of the source plate.
UPPER_DOCK = (600, 350)
RAIL_X = 935
LOWER_DOCK = (1315, 599)
HOLE = (1950, 90)
SHADOW_BOUNDS = (1808, -8, 480, 300)
WALK_START = (1632, 405)
WALK_END = (1950, 404)


def rail_path(height):
    radius = BEND_ART_RADIUS * ZOOM
    left, upper = UPPER_DOCK
    right, lower = LOWER_DOCK
    top_center = (RAIL_X - radius, upper + radius)
    bottom_center = (RAIL_X + radius, lower - radius)
    points = [
        (left, upper), (top_center[0], upper), (RAIL_X, top_center[1]),
        (RAIL_X, bottom_center[1]), (bottom_center[0], lower), (right, lower),
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


def main():
    with Image.open(PLATE) as source:
        width, height = source.size
    pico.open_canvas(width, height)
    try:
        art = pico.load_image(str(PLATE))
        shadow = pico.load_image(str(SHADOW))
        straight, bend, carriage = (pico.load_image(str(path)) for path in (
            RAIL_IMAGE, RAIL_BEND_IMAGE, RAIL_CARRIAGE_IMAGE,
        ))
        camera = Camera(width, width / ZOOM, zoom=ZOOM)
        path = rail_path(height)
        player = Player(0, 0, width / ZOOM)
        player.facing = 1

        def draw(position, *, elapsed=None):
            pico.clear_canvas()
            art.draw_to_origin(0, 0, width, height)
            draw_rail(straight, bend, camera, path)
            scale = RAIL_ART_SCALE * ZOOM
            carriage.draw(*camera.world_to_screen(*path[-1].end), carriage.w * scale, carriage.h * scale)
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
            read_render(0, 0, width, height).save(OUTPUT.with_name(f"{OUTPUT.name}-{name}.png"))

        frames = []
        left = max(0, width - 780)
        view = left, 0, width - left, min(height, 476)
        for i in range(34):
            t = i / 33
            position = tuple(a + (b - a) * t for a, b in zip(WALK_START, WALK_END))
            draw(position, elapsed=i * .065 if 0 < i < 33 else -1)
            frames.append(read_render(*view))
        palette = frames[-1].quantize(colors=256)
        indexed = [frame.quantize(palette=palette, dither=Image.Dither.NONE) for frame in frames]
        indexed[0].save(OUTPUT.with_suffix(".gif"), save_all=True, append_images=indexed[1:],
                        duration=[550] + [65] * 32 + [900], loop=0, optimize=True)
        del art, shadow, straight, bend, carriage, player
    finally:
        pico.close_canvas()


if __name__ == "__main__":
    main()

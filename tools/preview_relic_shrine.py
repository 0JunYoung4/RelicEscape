"""Render the playable shrine and its ceiling lighting through the room renderer."""

from ctypes import c_ubyte
import os
from pathlib import Path
import sys
from types import SimpleNamespace

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("SDL_RENDER_DRIVER", "software")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from PIL import Image
from pico2d import pico2d as pico

from lower_caves import GALLERY_WIDTH, RELIC_X, RELIC_Y, LowerCaves
from main import Camera, RELIC_IMAGE, draw_relic
from player import Player


def render(room, relic, player, zoom, path, *, collected=False):
    camera = Camera(960, GALLERY_WIDTH, zoom=zoom, y=-108 / zoom)
    camera.follow(RELIC_X - 90)
    room.has_relic = collected
    pico.clear_canvas()
    room.draw(camera)
    if not collected:
        draw_relic(relic, camera, RELIC_X, RELIC_Y, 0)
    player.draw(camera)
    room.draw_foreground(camera)
    pixels = (c_ubyte * (960 * 540 * 4))()
    if pico.SDL_RenderReadPixels(pico.renderer, None, pico.SDL_PIXELFORMAT_RGBA32,
                                pixels, 960 * 4) != 0:
        raise RuntimeError(pico.SDL_GetError())
    Image.frombytes("RGBA", (960, 540), bytes(pixels)).save(path)


def main():
    pico.open_canvas(960, 540)
    try:
        room = LowerCaves(SimpleNamespace(width=960, height=540, shaft=SimpleNamespace(w=4096)))
        room.room = "gallery"
        relic = pico.load_image(str(RELIC_IMAGE))
        player = Player(RELIC_X - 310, 0, GALLERY_WIDTH)
        for zoom, name in ((.5, "gallery"), (.8, "closeup")):
            render(room, relic, player, zoom,
                   ROOT / "docs" / f"relic-shrine-runtime-{name}.png")
        render(room, relic, player, .5, ROOT / "docs/relic-shrine-runtime-collected.png", collected=True)
        del room, relic, player
    finally:
        pico.close_canvas()
    print("Saved playable shrine previews before and after pickup")


if __name__ == "__main__":
    main()

"""Render the shrine design in the gallery without changing the playable map."""

from ctypes import c_ubyte
import json
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

from lower_caves import GALLERY_CEILING_Y, GALLERY_WIDTH, RELIC_X, RELIC_Y
from main import Camera, RELIC_IMAGE, draw_relic
from moss_art import MossCaveArt
from player import Player


def render(art, shrine, metadata, relic, player, zoom, path):
    camera = Camera(960, GALLERY_WIDTH, zoom=zoom, y=-108 / zoom)
    camera.follow(RELIC_X - 90)
    anchor_x, ground = metadata["ground_anchor"]
    scale = metadata["world_height"] / ground
    left = RELIC_X - anchor_x * scale
    bottom = -(shrine.h - ground) * scale
    pico.clear_canvas()
    art.draw_background(camera)
    art.draw_motes(camera, 0, GALLERY_CEILING_Y, right=GALLERY_WIDTH)
    shrine.draw_to_origin(*camera.world_to_screen(left, bottom),
                          shrine.w * scale * zoom, shrine.h * scale * zoom)
    art.draw_floor(camera, 0, GALLERY_WIDTH, 0)
    art.shadow_floor(camera, 0)
    draw_relic(relic, camera, RELIC_X, RELIC_Y, 0)
    player.draw(camera)
    art.draw_canopy(camera, GALLERY_CEILING_Y)
    pixels = (c_ubyte * (960 * 540 * 4))()
    if pico.SDL_RenderReadPixels(pico.renderer, None, pico.SDL_PIXELFORMAT_RGBA32,
                                pixels, 960 * 4) != 0:
        raise RuntimeError(pico.SDL_GetError())
    Image.frombytes("RGBA", (960, 540), bytes(pixels)).save(path)


def main():
    concept = ROOT / "assets/concepts/relic-acquisition-shrine-v1.json"
    metadata = json.loads(concept.read_text(encoding="utf-8"))
    pico.open_canvas(960, 540)
    try:
        art = MossCaveArt(960, 540)
        shrine = pico.load_image(str(concept.parent / metadata["image"]))
        relic = pico.load_image(str(RELIC_IMAGE))
        player = Player(RELIC_X - 310, 0, GALLERY_WIDTH)
        for zoom, name in ((.5, "gallery"), (.8, "closeup")):
            render(art, shrine, metadata, relic, player, zoom,
                   ROOT / "docs" / f"relic-acquisition-shrine-v1-{name}.png")
        del art, shrine, relic, player
    finally:
        pico.close_canvas()
    print("Saved two shrine placement previews; playable map unchanged")


if __name__ == "__main__":
    main()

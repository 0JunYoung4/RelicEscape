"""Save reproducible SDL renders of the combat room at different camera heights."""
import argparse
from ctypes import c_ubyte
import os
from pathlib import Path
import sys
from types import SimpleNamespace

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("SDL_RENDER_DRIVER", "software")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from PIL import Image
from pico2d import pico2d as pico
from lower_caves import COMBAT_CENTER_X, COMBAT_WIDTH, LowerCaves
from main import Camera
from player import Player


def render(room, player, camera, path):
    pico.clear_canvas()
    room.draw(camera)
    room.draw_combat_exit(camera)
    player.draw(camera)
    room.draw_foreground(camera)
    pixels = (c_ubyte * (960 * 540 * 4))()
    if pico.SDL_RenderReadPixels(pico.renderer, None, pico.SDL_PIXELFORMAT_RGBA32,
                                pixels, 960 * 4) != 0:
        raise RuntimeError(pico.SDL_GetError())
    Image.frombytes("RGBA", (960, 540), bytes(pixels)).save(path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--prefix", default="combat-atmosphere")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    pico.open_canvas(960, 540)
    cave = SimpleNamespace(width=960, height=540, shaft=SimpleNamespace(w=4096))
    room = LowerCaves(cave)
    room.room, room.has_relic = "combat", True
    player = Player(COMBAT_CENTER_X, 0, COMBAT_WIDTH)
    camera = Camera(960, COMBAT_WIDTH, zoom=.5)
    room.enter(player, camera)
    room.art.started = __import__("time").perf_counter()
    player.recover_at(COMBAT_CENTER_X, 0, 0)
    room.follow_camera(player, camera)
    render(room, player, camera, root / "docs" / f"{args.prefix}-floor.png")
    room.encounter_started = True
    player.recover_at(COMBAT_CENTER_X, 0, 0)
    render(room, player, camera, root / "docs" / f"{args.prefix}-combat.png")
    player.recover_at(COMBAT_CENTER_X, 650, 0)
    room.follow_camera(player, camera)
    render(room, player, camera, root / "docs" / f"{args.prefix}-high.png")
    room.exit_progress, room.shaft_visibility = 1, 1
    player.recover_at(COMBAT_CENTER_X, -300, 0)
    room.follow_camera(player, camera)
    render(room, player, camera, root / "docs" / f"{args.prefix}-shaft.png")
    print(f"Saved {args.prefix}: floor, combat, high, shaft")

"""Save reproducible SDL renders of the combat room at different camera heights."""
import argparse
from ctypes import c_ubyte
import os
from pathlib import Path
import sys
from time import perf_counter
from types import SimpleNamespace

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("SDL_RENDER_DRIVER", "software")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from PIL import Image
from pico2d import pico2d as pico
from crystal_golem import ATTACK_RELEASE, EMERGE_DURATION as GOLEM_EMERGE_DURATION
from lower_caves import (COMBAT_CENTER_X, COMBAT_EXIT_DURATION, COMBAT_GATE_DURATION,
                         COMBAT_WIDTH, LowerCaves)
from main import Camera
from pillbug import EMERGE_DURATION as PILLBUG_EMERGE_DURATION
from player import Player


def render(room, player, camera, path=None):
    pico.clear_canvas()
    room.draw(camera)
    room.draw_combat_exit(camera)
    room.draw_combat_gate(camera)
    player.draw(camera)
    room.draw_hit_impacts(camera)
    room.draw_foreground(camera)
    pixels = (c_ubyte * (960 * 540 * 4))()
    if pico.SDL_RenderReadPixels(pico.renderer, None, pico.SDL_PIXELFORMAT_RGBA32,
                                pixels, 960 * 4) != 0:
        raise RuntimeError(pico.SDL_GetError())
    image = Image.frombytes("RGBA", (960, 540), bytes(pixels))
    if path is not None:
        image.save(path)
    return image


def render_projectile_sample(room, player, camera, path):
    """Capture live crystal sprites early in their flight over the side platforms."""
    target = player.get_hitbox()
    for golem in room.golems:
        golem.attack_cooldown = 0
        golem.update(1 / 60, target, player.terrain, player.world_width)
        projectile = golem.update(ATTACK_RELEASE, target, player.terrain, player.world_width)
        if projectile is None:
            raise RuntimeError("Preview golem did not fire")
        projectile.update(.19, player.terrain, player.world_width)
        if not projectile.active:
            raise RuntimeError("Preview crystal hit terrain before the sample")
        room.projectiles.append(projectile)
    render(room, player, camera, path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--prefix", default="combat-atmosphere")
    parser.add_argument("--animate", action="store_true")
    parser.add_argument("--projectiles", action="store_true")
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    output = args.output_dir or root / "docs"
    output.mkdir(parents=True, exist_ok=True)
    pico.open_canvas(960, 540)
    cave = SimpleNamespace(width=960, height=540, shaft=SimpleNamespace(w=4096))
    room = LowerCaves(cave)
    room.room, room.has_relic = "combat", True
    player = Player(COMBAT_CENTER_X, 0, COMBAT_WIDTH)
    camera = Camera(960, COMBAT_WIDTH, zoom=.5)
    room.enter(player, camera)
    room.art.started = perf_counter()
    player.recover_at(COMBAT_CENTER_X, 0, 0)
    room.follow_camera(player, camera)
    render(room, player, camera, output / f"{args.prefix}-floor.png")
    room.update_enemies(player, COMBAT_GATE_DURATION)
    room.update_enemies(player, PILLBUG_EMERGE_DURATION)
    render(room, player, camera, output / f"{args.prefix}-combat.png")
    player.recover_at(COMBAT_CENTER_X, 650, 0)
    room.follow_camera(player, camera)
    render(room, player, camera, output / f"{args.prefix}-high.png")
    if args.animate:
        frames = []
        for index in list(range(17)) + list(range(15, -1, -1)):
            player.recover_at(COMBAT_CENTER_X, index * 650 / 16, 0)
            room.follow_camera(player, camera)
            frames.append(render(room, player, camera).convert("RGB"))
        frames[0].save(output / f"{args.prefix}-camera.gif", save_all=True,
                       append_images=frames[1:], duration=85, loop=0, optimize=False)
    for bug in room.combat_pillbugs:
        bug.hp = 0
    room.update_enemies(player, 0)
    if args.projectiles:
        player.recover_at(COMBAT_CENTER_X, 0, 0)
        room.follow_camera(player, camera)
        room.update_enemies(player, GOLEM_EMERGE_DURATION)
        render_projectile_sample(room, player, camera, output / f"{args.prefix}-projectiles.png")
        room.projectiles.clear()
    for golem in room.golems:
        golem.hp = 0
    room.update_enemies(player, COMBAT_EXIT_DURATION)
    room.shaft_visibility = 1
    player.recover_at(COMBAT_CENTER_X, -300, 0)
    room.follow_camera(player, camera)
    render(room, player, camera, output / f"{args.prefix}-shaft.png")
    print(f"Saved {args.prefix} to {output}")

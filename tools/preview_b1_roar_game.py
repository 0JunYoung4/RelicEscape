"""Replay the B1 roar in a standalone RelicEscape SDL scene."""

from argparse import ArgumentParser
from ctypes import c_ubyte
import os
from pathlib import Path
from time import perf_counter, sleep

from PIL import Image


SIZE = (960, 540)
TOUR_PAUSE_MS = 220
TOUR_PAN_MS = 820
TOUR_ROAR_START_MS = TOUR_PAUSE_MS + TOUR_PAN_MS + 80


def _view(left, top, width):
    return left, top, left + width, top + width * SIZE[1] / SIZE[0]


ENTRY_VIEW = _view(1305, 177.5, 1040)
COMBAT_VIEW = _view(528, 37, 1280)
LEFT_RAIL_VIEW = _view(24, 181, 1008)
UPPER_PLATFORM_VIEW = _view(600, 8, 1112)


def _tour_view(elapsed_ms):
    progress = min(1, max(0, (elapsed_ms - TOUR_PAUSE_MS) / TOUR_PAN_MS))
    blend = progress * progress * (3 - 2 * progress)
    return tuple(start + (end - start) * blend for start, end in zip(ENTRY_VIEW, COMBAT_VIEW))


def _draw_replay(stage, elapsed_ms, camera_tour):
    if camera_tour:
        stage.draw(max(0, elapsed_ms - TOUR_ROAR_START_MS), camera_view=_tour_view(elapsed_ms),
                   ambient_ms=elapsed_ms)
    else:
        stage.draw(elapsed_ms)


def _read_pixels(pico, pixels, size=SIZE):
    if pico.SDL_RenderReadPixels(pico.renderer, None, pico.SDL_PIXELFORMAT_RGBA32,
                                pixels, size[0] * 4) != 0:
        raise RuntimeError(pico.SDL_GetError())
    return Image.frombytes("RGBA", size, bytes(pixels)).convert("RGB")


def capture(pico, stage, destination, *, camera_tour=False):
    """Capture the same renderer as the window, including short boss poses."""
    roar_start = TOUR_ROAR_START_MS if camera_tour else 0
    end_time = roar_start + stage.duration_ms
    boss_changes = {roar_start + pose_time for pose_time in stage.boss_change_times}
    times = sorted(set(range(0, end_time + 1, 40)) | boss_changes | {end_time})
    durations = [end - start for start, end in zip(times, times[1:])] + [400]
    pixels = (c_ubyte * (SIZE[0] * SIZE[1] * 4))()
    frames = []
    for milliseconds in times:
        _draw_replay(stage, milliseconds, camera_tour)
        frames.append(_read_pixels(pico, pixels))

    destination.parent.mkdir(parents=True, exist_ok=True)
    encoding = {"quality": 92, "lossless": False} if camera_tour else {"lossless": True}
    frames[0].save(destination, format="WEBP", save_all=True, append_images=frames[1:],
                   duration=durations, loop=0, method=2, **encoding)
    print(f"Captured B1 from the SDL renderer: {destination}")


def capture_stills(pico, stage, destination):
    """Export stationary reference views for layer and readability checks."""
    views = (
        ("right-entry", ENTRY_VIEW, 0),
        ("left-rail", LEFT_RAIL_VIEW, 0),
        ("upper-platforms", UPPER_PLATFORM_VIEW, 0),
        ("boss-roar", COMBAT_VIEW, stage.apex_ms + 160),
    )
    pixels = (c_ubyte * (SIZE[0] * SIZE[1] * 4))()
    destination.mkdir(parents=True, exist_ok=True)
    for name, view, elapsed_ms in views:
        stage.draw(elapsed_ms, camera_view=view)
        _read_pixels(pico, pixels).save(destination / f"{name}.png")
    print(f"Captured B1 inspection views: {destination}")


def capture_full_room(pico, stage, destination, size):
    pixels = (c_ubyte * (size[0] * size[1] * 4))()
    stage.draw(stage.apex_ms, camera_view=(0, 0, *size))
    destination.parent.mkdir(parents=True, exist_ok=True)
    _read_pixels(pico, pixels, size).save(destination)
    print(f"Captured the full B1 room: {destination}")


def play(pico, stage, *, camera_tour=False):
    title = "RelicEscape · B1 포효 테스트 | E/R 다시 보기 · Esc 종료"
    pico.SDL_SetWindowTitle(pico.window, title.encode("utf-8"))
    start = perf_counter()
    while True:
        now = perf_counter()
        for event in pico.get_events():
            if event.type == pico.SDL_QUIT or (event.type == pico.SDL_KEYDOWN and event.key == pico.SDLK_ESCAPE):
                return
            if event.type == pico.SDL_KEYDOWN and event.key in (pico.SDLK_e, pico.SDLK_r):
                start = now
        _draw_replay(stage, (now - start) * 1000, camera_tour)
        pico.update_canvas()
        sleep(max(0, 1 / 60 - (perf_counter() - now)))


def main():
    parser = ArgumentParser(description=__doc__)
    output = parser.add_mutually_exclusive_group()
    output.add_argument("--capture", type=Path, metavar="WEBP", help="export the SDL scene without opening a window")
    output.add_argument("--stills", type=Path, metavar="DIR", help="export four fixed inspection views as PNGs")
    output.add_argument("--full-room", type=Path, metavar="PNG", help="export the entire room at its native size")
    parser.add_argument("--camera-tour", action="store_true", help="pan from the passage into the arena before the roar")
    options = parser.parse_args()
    if options.capture is not None and options.capture.suffix.lower() != ".webp":
        parser.error("--capture requires a .webp filename")
    if options.full_room is not None and options.full_room.suffix.lower() != ".png":
        parser.error("--full-room requires a .png filename")
    if any((options.capture, options.stills, options.full_room)):
        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
        os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
        os.environ.setdefault("SDL_RENDER_DRIVER", "software")

    from pico2d import pico2d as pico
    from tools.b1_room_art import ROOM_SIZE
    from tools.b1_roar_game_stage import B1RoarStage

    canvas_size = ROOM_SIZE if options.full_room is not None else SIZE
    pico.open_canvas(*canvas_size)
    stage = None
    try:
        stage = B1RoarStage()
        if options.capture is not None:
            capture(pico, stage, options.capture, camera_tour=options.camera_tour)
        elif options.stills is not None:
            capture_stills(pico, stage, options.stills)
        elif options.full_room is not None:
            capture_full_room(pico, stage, options.full_room, canvas_size)
        else:
            play(pico, stage, camera_tour=options.camera_tour)
    finally:
        if stage is not None:
            stage.close()
        pico.close_canvas()


if __name__ == "__main__":
    main()

"""Replay the B1 roar in a standalone RelicEscape SDL scene."""

from argparse import ArgumentParser
from ctypes import c_ubyte
import os
from pathlib import Path
from time import perf_counter, sleep

from PIL import Image


SIZE = (960, 540)


def capture(pico, stage, destination):
    """Capture the same renderer as the window, including short boss poses."""
    end_time = stage.duration_ms
    times = sorted(set(range(0, end_time + 1, 40)) | set(stage.boss_change_times) | {end_time})
    durations = [end - start for start, end in zip(times, times[1:])] + [400]
    pixels = (c_ubyte * (SIZE[0] * SIZE[1] * 4))()
    frames = []
    for milliseconds in times:
        stage.draw(milliseconds)
        if pico.SDL_RenderReadPixels(pico.renderer, None, pico.SDL_PIXELFORMAT_RGBA32,
                                    pixels, SIZE[0] * 4) != 0:
            raise RuntimeError(pico.SDL_GetError())
        frames.append(Image.frombytes("RGBA", SIZE, bytes(pixels)).convert("RGB"))

    destination.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(destination, format="WEBP", save_all=True, append_images=frames[1:],
                   duration=durations, loop=0, lossless=True, method=2)
    print(f"Captured B1 from the SDL renderer: {destination}")


def play(pico, stage):
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
        stage.draw((now - start) * 1000)
        pico.update_canvas()
        sleep(max(0, 1 / 60 - (perf_counter() - now)))


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--capture", type=Path, metavar="WEBP", help="export the SDL scene without opening a window")
    options = parser.parse_args()
    if options.capture is not None:
        if options.capture.suffix.lower() != ".webp":
            parser.error("--capture requires a .webp filename")
        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
        os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
        os.environ.setdefault("SDL_RENDER_DRIVER", "software")

    from pico2d import pico2d as pico
    from tools.b1_roar_game_stage import B1RoarStage

    pico.open_canvas(*SIZE)
    stage = None
    try:
        stage = B1RoarStage()
        if options.capture is not None:
            capture(pico, stage, options.capture)
        else:
            play(pico, stage)
    finally:
        if stage is not None:
            stage.close()
        pico.close_canvas()


if __name__ == "__main__":
    main()

"""Play the RelicEscape B1 intro and adaptive attack loop."""

from argparse import ArgumentParser
from ctypes import c_ubyte
import os
from pathlib import Path
from time import perf_counter, sleep

from tools.preview_b1_roar_game import SIZE, _read_pixels


def capture_stills(pico, stage, destination):
    destination.mkdir(parents=True, exist_ok=True)
    pixels = (c_ubyte * (SIZE[0] * SIZE[1] * 4))()
    dt = 1 / 60

    def capture(name):
        stage.draw()
        _read_pixels(pico, pixels).save(destination / f"{name}.png")

    capture("entry")
    for _ in range(240):
        if stage.can_inspect:
            break
        stage.advance(dt, -1, running=True)
    if not stage.can_inspect:
        raise RuntimeError("The test player could not reach the shell.")
    capture("inspect")
    stage.advance(dt, inspect_pressed=True)
    for state, elapsed, name in (
        ("tremor", 1.56, "tremor"), ("tremor", 2.53, "falling-rock"),
        ("roar", stage.apex_ms / 1000 + .16, "roar"),
        ("claw", stage.claw.tell + .16, "first-claw-tell"),
        ("claw", stage.claw.impact + .07, "first-claw-hit"),
        ("jump", stage.jump.tell + .27, "jump-tell"),
        ("jump", stage.jump.impact + .09, "jump-impact"),
        ("ready", 0, "jump-recovered"),
    ):
        for _ in range(360):
            if stage.state == state and stage.age >= elapsed:
                capture(name)
                break
            stage.advance(dt)
        else:
            raise RuntimeError(f"The test did not reach {state} at {elapsed}s.")
    print(f"Captured the B1 combat rehearsal: {destination}")


def play(pico, stage):
    from input_events import poll_events
    from main import read_movement

    title = "RelicEscape · B1 전투 AI 테스트 | E 조사 · R 다시 · Esc 종료"
    pico.SDL_SetWindowTitle(pico.window, title.encode("utf-8"))
    previous = perf_counter()
    while True:
        now = perf_counter()
        keys = set()
        for event in poll_events():
            if event.type == pico.SDL_QUIT:
                return
            if event.type == pico.SDL_KEYDOWN:
                keys.add(event.key)
        if pico.SDLK_ESCAPE in keys:
            return
        direction, running, crouching = read_movement()
        if pico.SDLK_r in keys:
            stage.reset()
        else:
            keyboard = pico.SDL_GetKeyboardState(None)
            stage.advance(min(.05, now - previous), direction, running=running, crouching=crouching,
                          jump_pressed=pico.SDLK_SPACE in keys,
                          jump_held=bool(keyboard[pico.SDL_SCANCODE_SPACE]),
                          inspect_pressed=pico.SDLK_e in keys, attack_pressed=pico.SDLK_x in keys)
        previous = now
        stage.draw()
        pico.update_canvas()
        sleep(max(0, 1 / 60 - (perf_counter() - now)))


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--stills", type=Path, metavar="DIR")
    options = parser.parse_args()
    if options.stills is not None:
        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
        os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
        os.environ.setdefault("SDL_RENDER_DRIVER", "software")

    from pico2d import pico2d as pico
    from tools.b1_encounter_stage import B1EncounterStage

    pico.open_canvas(*SIZE)
    stage = None
    try:
        stage = B1EncounterStage()
        if options.stills is None:
            play(pico, stage)
        else:
            capture_stills(pico, stage, options.stills)
    finally:
        if stage is not None:
            stage.close()
        pico.close_canvas()


if __name__ == "__main__":
    main()

"""Translate SDL input events without adding delays or window-title updates."""

from ctypes import byref

from pico2d import pico2d as pico


def poll_events():
    events = []
    sdl_event = pico.SDL_Event()
    while pico.SDL_PollEvent(byref(sdl_event)):
        event = pico.Event(sdl_event.type)
        if event.type == pico.SDL_QUIT:
            events.append(event)
        elif event.type in (pico.SDL_KEYDOWN, pico.SDL_KEYUP):
            if not sdl_event.key.repeat:
                event.key = sdl_event.key.keysym.sym
                events.append(event)
        elif event.type == pico.SDL_MOUSEMOTION:
            event.x, event.y = sdl_event.motion.x, sdl_event.motion.y
            events.append(event)
        elif event.type in (pico.SDL_MOUSEBUTTONDOWN, pico.SDL_MOUSEBUTTONUP):
            event.button = sdl_event.button.button
            event.x, event.y = sdl_event.button.x, sdl_event.button.y
            events.append(event)
        elif event.type == pico.SDL_MOUSEWHEEL:
            event.x, event.y = sdl_event.wheel.x, sdl_event.wheel.y
            events.append(event)
    return events

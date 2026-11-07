"""Draw a blade trail that sweeps outward and dissolves behind the player."""

from ctypes import byref
from math import cos, pi, radians, sin

from pico2d import pico2d as pico


SLASH_DURATION = 0.14
ARC_SEGMENTS = 20


def draw_slash(x, y, facing, age, camera, *, downward=False):
    if downward:
        center_x, center_y = 8, 42
        radius_x, radius_y = 128, 66
        half_arc = 82
        rotation = radians(-55)
    else:
        center_x, center_y = 31, 82
        radius_x, radius_y = 150, 78
        half_arc = 102
        rotation = 0

    progress = age / SLASH_DURATION
    buildup = min(1.0, progress / 0.22)
    decay = max(0.0, (progress - 0.22) / 0.78)
    head = 0.32 + 0.68 * buildup
    tail = decay ** 1.5
    opacity = (0.72 + 0.28 * buildup) * (1 - decay ** 1.35)
    radius_x += 6 * decay - 18 * (1 - buildup)
    radius_y += 3 * decay
    rotation_cos, rotation_sin = cos(rotation), sin(rotation)
    vertices = []
    indices = []
    for step in range(ARC_SEGMENTS + 1):
        span = step / ARC_SEGMENTS
        arc_progress = tail + (head - tail) * span
        angle = radians(half_arc * (1 - 2 * arc_progress))
        taper = min(1.0, 5 * span, 8 * (1 - span))
        thickness = 50 * sin(pi * arc_progress) * taper * (1 - 0.55 * decay)
        alpha = opacity * min(1.0, 3 * span)
        edge = pico.SDL_Color(178, 221, 251, round(216 * alpha))
        highlight = pico.SDL_Color(248, 253, 255, round(255 * alpha))
        inner = pico.SDL_Color(141, 199, 249, 0)
        for inset, color in (
            (0, edge), (thickness * 0.18, highlight), (thickness * 0.70, highlight), (thickness, inner),
        ):
            arc_x = (radius_x - inset) * cos(angle)
            arc_y = (radius_y - inset) * sin(angle)
            offset_x = center_x + arc_x * rotation_cos - arc_y * rotation_sin
            offset_y = center_y + arc_x * rotation_sin + arc_y * rotation_cos
            screen_x, screen_y = camera.world_to_screen(x + facing * offset_x, y + offset_y)
            point = pico.SDL_FPoint(screen_x, pico.canvas_height - 1 - screen_y)
            vertices.append(pico.SDL_Vertex(point, color))
        if step > 0:
            start = (step - 1) * 4
            for band in range(start, start + 3):
                indices.extend((band, band + 1, band + 4, band + 1, band + 5, band + 4))

    vertex_buffer = (pico.SDL_Vertex * len(vertices))(*vertices)
    index_buffer = (pico.c_int * len(indices))(*indices)
    previous_blend_mode = pico.SDL_BlendMode()
    pico.SDL_GetRenderDrawBlendMode(pico.renderer, byref(previous_blend_mode))
    pico.SDL_SetRenderDrawBlendMode(pico.renderer, pico.SDL_BLENDMODE_BLEND)
    pico.SDL_RenderGeometry(pico.renderer, None, vertex_buffer, len(vertices), index_buffer, len(indices))
    pico.SDL_SetRenderDrawBlendMode(pico.renderer, previous_blend_mode)

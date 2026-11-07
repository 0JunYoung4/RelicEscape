"""Draw a tapered blade trail behind the attack sprite during release."""

from math import cos, pi, radians, sin

from pico2d import pico2d as pico


SLASH_DURATION = 0.075
ARC_SEGMENTS = 16


def draw_slash(x, y, facing, age, camera, *, downward=False):
    if downward:
        center_x, center_y = 8, 42
        radius_x, radius_y = 52, 33
        rotation = radians(-55)
    else:
        center_x, center_y = 41, 78
        radius_x, radius_y = 61, 36
        rotation = 0

    opacity = 1 - age / SLASH_DURATION
    outer_color = pico.SDL_Color(232, 249, 255, round(235 * opacity))
    inner_color = pico.SDL_Color(111, 189, 237, round(105 * opacity))
    vertices = []
    indices = []
    for step in range(ARC_SEGMENTS + 1):
        progress = step / ARC_SEGMENTS
        angle = radians(-65 + 130 * progress)
        thickness = 13 * sin(pi * progress)
        for inset, color in ((0, outer_color), (thickness, inner_color)):
            arc_x = (radius_x - inset) * cos(angle)
            arc_y = (radius_y - inset) * sin(angle)
            offset_x = center_x + arc_x * cos(rotation) - arc_y * sin(rotation)
            offset_y = center_y + arc_x * sin(rotation) + arc_y * cos(rotation)
            screen_x, screen_y = camera.world_to_screen(x + facing * offset_x, y + offset_y)
            point = pico.SDL_FPoint(screen_x, pico.canvas_height - 1 - screen_y)
            vertices.append(pico.SDL_Vertex(point, color))
        if step > 0:
            start = (step - 1) * 2
            indices.extend((start, start + 1, start + 2, start + 1, start + 3, start + 2))

    vertex_buffer = (pico.SDL_Vertex * len(vertices))(*vertices)
    index_buffer = (pico.c_int * len(indices))(*indices)
    pico.SDL_RenderGeometry(pico.renderer, None, vertex_buffer, len(vertices), index_buffer, len(indices))

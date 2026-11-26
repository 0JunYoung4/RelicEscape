"""Depth and fixed light sources for the lower caves."""

from ctypes import byref
from math import ceil

from pico2d import pico2d as pico

from player import ASSET_ROOT
from render_mesh import VERTEX_SIZE, grid_indices, index_buffer, pack_vertex, unit_circle, vertex_buffer


ROUTE_ART = ASSET_ROOT / "terrain/lower-route-art-v2"
COMBAT_ART = ASSET_ROOT / "terrain/combat-room-v2"
_LIGHT_CIRCLE = unit_circle(24)
_LIGHT_INDICES = index_buffer(tuple(value for i in range(24)
                                   for value in (0, i + 1, (i + 1) % 24 + 1)))


def load_image(path):
    image = pico.load_image(str(path))
    pico.SDL_SetTextureScaleMode(image.texture, pico.SDL_ScaleModeLinear)
    return image


def draw_layer(image, camera, bounds, *, tint=(255, 255, 255), opacity=255,
               crop=None, fade_range=None, clip_bottom=None, shade=None):
    """Submit only visible texels, keeping SDL software triangles small."""
    left, bottom, right, top = bounds
    width, height = right - left, top - bottom
    view_left, view_right = max(left, camera.x), min(right, camera.x + camera.view_width)
    view_bottom = max(bottom, camera.y)
    if clip_bottom is not None:
        view_bottom = max(view_bottom, clip_bottom)
    view_top = min(top, camera.y + pico.canvas_height / camera.zoom)
    if view_left >= view_right or view_bottom >= view_top:
        return
    u0, v0, u1, v1 = crop or (0, 0, 1, 1)
    spacing = 48 if shade is not None else 240
    columns = ceil((view_right - view_left) * camera.zoom / spacing)
    rows = ceil((view_top - view_bottom) * camera.zoom / spacing)
    stride = columns + 1
    column_data = []
    for column in range(stride):
        x = view_left + (view_right - view_left) * column / columns
        u = u0 + (x - left) / width * (u1 - u0)
        weight = 1.0
        if fade_range is not None:
            fade_left, fade_right = fade_range
            weight = max(0.0, min(1.0, (x - fade_left) / (fade_right - fade_left)))
            weight = weight * weight * (3 - 2 * weight)
        column_data.append((x, u, round(opacity * weight)))
    count = stride * (rows + 1)
    geometry = vertex_buffer(count)
    offset = 0
    for row in range(rows + 1):
        y = view_top - (view_top - view_bottom) * row / rows
        v = v0 + (top - y) / height * (v1 - v0)
        for x, u, alpha in column_data:
            sx, sy = camera.world_to_screen(x, y)
            color = shade(x, y, tint) if shade is not None else tint
            pack_vertex(geometry, offset, sx, pico.canvas_height - sy, *color, alpha, u, v)
            offset += VERTEX_SIZE
    triangles = grid_indices(columns, rows)
    pico.SDL_RenderGeometry(pico.renderer, image.texture, geometry, count, triangles, len(triangles))


def draw_soft_light(camera, center, radius, color, opacity):
    """Draw a feathered world-space ellipse without changing the caller's blend state."""
    center_x, center_y = center
    rx, ry = radius
    if (center_x + rx < camera.x or center_x - rx > camera.x + camera.view_width
            or center_y + ry < camera.y or center_y - ry > camera.y + pico.canvas_height / camera.zoom):
        return
    sx, sy = camera.world_to_screen(center_x, center_y)
    vertices = vertex_buffer(25)
    pack_vertex(vertices, 0, sx, pico.canvas_height - sy, *color, opacity, 0, 0)
    for index, (cosine, sine) in enumerate(_LIGHT_CIRCLE, 1):
        x, y = camera.world_to_screen(center_x + rx * cosine, center_y + ry * sine)
        pack_vertex(vertices, index * VERTEX_SIZE, x, pico.canvas_height - y, *color, 0, 0, 0)
    previous = pico.SDL_BlendMode()
    pico.SDL_GetRenderDrawBlendMode(pico.renderer, byref(previous))
    pico.SDL_SetRenderDrawBlendMode(pico.renderer, pico.SDL_BLENDMODE_BLEND)
    try:
        pico.SDL_RenderGeometry(pico.renderer, None, vertices, 25, _LIGHT_INDICES, len(_LIGHT_INDICES))
    finally:
        pico.SDL_SetRenderDrawBlendMode(pico.renderer, previous)


def draw_parallax(image, camera, screen_height, bounds, tint):
    """Move the painting at quarter speed inside fixed room boundaries."""
    left, bottom, right, top = bounds
    width, height = right - left, top - bottom
    focus_x = max(left, min(right, camera.x + camera.view_width / 2))
    focus_y = max(bottom, min(top, camera.y + screen_height / (2 * camera.zoom)))
    # Pad the virtual painting so the same four room edges always have valid UVs.
    image_width, image_height = width * 1.75, height * 1.75
    u = .75 * (right - focus_x) / image_width
    v = .75 * (focus_y - bottom) / image_height
    # Clip before submitting triangles. The SDL software renderer uses fixed-point area math.
    visible_left = max(left, camera.x)
    visible_right = min(right, camera.x + camera.view_width)
    visible_bottom = max(bottom, camera.y)
    visible_top = min(top, camera.y + screen_height / camera.zoom)
    if visible_left >= visible_right or visible_bottom >= visible_top:
        return
    # Subdivide the clipped quad so software rendering also works at full viewport size.
    columns = ceil((visible_right - visible_left) * camera.zoom / 400)
    rows = ceil((visible_top - visible_bottom) * camera.zoom / 400)
    stride = columns + 1
    column_data = []
    for col_index in range(stride):
        x = visible_left + (visible_right - visible_left) * col_index / columns
        column_data.append((x, u + (x - left) / image_width))
    count = stride * (rows + 1)
    geometry = vertex_buffer(count)
    offset = 0
    for row_index in range(rows + 1):
        y = visible_top - (visible_top - visible_bottom) * row_index / rows
        row = v + (top - y) / image_height
        for x, column in column_data:
            sx, sy = camera.world_to_screen(x, y)
            pack_vertex(geometry, offset, sx, screen_height - sy, *tint, 255, column, row)
            offset += VERTEX_SIZE
    indices = grid_indices(columns, rows)
    pico.SDL_RenderGeometry(pico.renderer, image.texture, geometry, count, indices, len(indices))


class RouteAtmosphere:
    def __init__(self):
        self.light = load_image(ROUTE_ART / "mint-light.png")
        self.ruins = {name: load_image(COMBAT_ART / f"midground-{name}.png")
                      for name in ("stele", "broken-arch")}

    def draw_light(self, camera, left, bottom, width, height, *, strength=255):
        if left + width <= camera.x or left >= camera.x + camera.view_width:
            return
        pico.SDL_SetTextureAlphaMod(self.light.texture, strength)
        self.light.draw_to_origin(*camera.world_to_screen(left, bottom), width * camera.zoom, height * camera.zoom)

    def draw_ruin(self, camera, name, x, bottom, width, height, *, flip=""):
        """Let the individual ruin silhouettes disappear into the air at their base."""
        view_center = camera.x + camera.view_width / 2
        x += (view_center - x) * .40
        left, right = x - width / 2, x + width / 2
        if right <= camera.x or left >= camera.x + camera.view_width:
            return
        geometry = vertex_buffer(8)
        offset = 0
        for depth, alpha in ((0, 123), (.68, 123), (.90, 47), (1, 0)):
            for index, side in enumerate((left, right)):
                sx, sy = camera.world_to_screen(side, bottom + height * (1 - depth))
                column = 1 - index if flip else index
                pack_vertex(geometry, offset, sx, pico.canvas_height - sy, 115, 158, 161, alpha, column, depth)
                offset += VERTEX_SIZE
        triangles = index_buffer((0, 1, 2, 1, 3, 2, 2, 3, 4, 3, 5, 4, 4, 5, 6, 5, 7, 6))
        pico.SDL_RenderGeometry(pico.renderer, self.ruins[name].texture, geometry, 8, triangles, 18)

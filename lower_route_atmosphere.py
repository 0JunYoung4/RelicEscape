"""Depth and fixed light sources for the lower caves."""

from ctypes import c_int
from math import ceil

from pico2d import pico2d as pico

from player import ASSET_ROOT


ROUTE_ART = ASSET_ROOT / "terrain/lower-route-art-v2"
COMBAT_ART = ASSET_ROOT / "terrain/combat-room-v2"


def load_image(path):
    image = pico.load_image(str(path))
    pico.SDL_SetTextureScaleMode(image.texture, pico.SDL_ScaleModeLinear)
    return image


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
    vertices, triangles = [], []
    stride = columns + 1
    for row_index in range(rows + 1):
        y = visible_top - (visible_top - visible_bottom) * row_index / rows
        row = v + (top - y) / image_height
        for col_index in range(stride):
            x = visible_left + (visible_right - visible_left) * col_index / columns
            column = u + (x - left) / image_width
            sx, sy = camera.world_to_screen(x, y)
            vertices.append(pico.SDL_Vertex((sx, screen_height - sy), (*tint, 255), (column, row)))
            if row_index and col_index:
                corner = len(vertices) - 1
                triangles.extend((corner - stride - 1, corner - stride, corner - 1,
                                  corner - stride, corner, corner - 1))
    geometry = (pico.SDL_Vertex * len(vertices))(*vertices)
    indices = (c_int * len(triangles))(*triangles)
    pico.SDL_RenderGeometry(pico.renderer, image.texture, geometry, len(vertices), indices, len(triangles))


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
        vertices = []
        for depth, alpha in ((0, 123), (.68, 123), (.90, 47), (1, 0)):
            for index, side in enumerate((left, right)):
                sx, sy = camera.world_to_screen(side, bottom + height * (1 - depth))
                column = 1 - index if flip else index
                vertices.append(pico.SDL_Vertex((sx, pico.canvas_height - sy), (115, 158, 161, alpha),
                                                (column, depth)))
        geometry = (pico.SDL_Vertex * 8)(*vertices)
        triangles = (c_int * 18)(0, 1, 2, 1, 3, 2, 2, 3, 4, 3, 5, 4, 4, 5, 6, 5, 7, 6)
        pico.SDL_RenderGeometry(pico.renderer, self.ruins[name].texture, geometry, 8, triangles, 18)

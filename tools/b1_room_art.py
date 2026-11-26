"""Layered art and local lighting for the B1 roar test room."""

from ctypes import create_string_buffer
from math import exp

from PIL import Image, ImageChops, ImageOps
from pico2d import pico2d as pico

from tools.b1_combat_terrain import stage_terrain
from tools.preview_b1_intro import ART, GROUND, SHELL_X
from tools.render_b1_roar_preview import PLAYER_X, resize, rgba


WORLD_PER_ART_PIXEL = 2
ROOM_SIZE = (2410, 790)
FAR_SIZE = (2690, 950)
ROOM_ART = ART.parent / "room-art-v4"
BASE_ROOM_ART = ART.parent / "room-art-v3"
NEUTRAL_VIEW_CENTER = (1168, 397)
FAR_PARALLAX, MID_PARALLAX, NEAR_PARALLAX = .25, .62, 1.10
FLOOR_LIGHTS = (
    (1087, 376, (125, 188, 135), 52),
    (1541, 256, (123, 164, 111), 40),
    (2077, 377, (138, 160, 91), 42),
)


def rgba_texture(image):
    """Upload a straight RGBA plate while its source buffer is alive."""
    width, height = image.size
    pixels = create_string_buffer(image.tobytes())
    surface = pico.SDL_CreateRGBSurfaceWithFormatFrom(
        pixels, width, height, 32, width * 4, pico.SDL_PIXELFORMAT_RGBA32,
    )
    if not surface:
        raise RuntimeError(pico.SDL_GetError())
    try:
        texture = pico.SDL_CreateTextureFromSurface(pico.renderer, surface)
    finally:
        pico.SDL_FreeSurface(surface)
    if not texture:
        raise RuntimeError(pico.SDL_GetError())
    pico.SDL_SetTextureBlendMode(texture, pico.SDL_BLENDMODE_BLEND)
    pico.SDL_SetTextureScaleMode(texture, pico.SDL_ScaleModeLinear)
    return pico.Image(texture)


def _room_image(path, size, *, opaque=False):
    image = rgba(path)
    if image.size != size:
        raise ValueError(f"{path.name} must use {size}, got {image.size}")
    if opaque and image.getchannel("A").getextrema() != (255, 255):
        raise ValueError(f"{path.name} must cover the full far background")
    return image


def _air_mix(image, color, fraction):
    rgb = image.convert("RGB")
    mixed = Image.blend(rgb, Image.new("RGB", image.size, color), fraction)
    mixed.putalpha(image.getchannel("A"))
    return mixed


def _green_grade(image, shadows, highlights, fraction):
    """Grade the color range on this layer while retaining its cutout alpha."""
    rgb = image.convert("RGB")
    tint = ImageOps.colorize(ImageOps.grayscale(rgb), shadows, highlights)
    mixed = Image.blend(rgb, tint, fraction)
    mixed.putalpha(image.getchannel("A"))
    return mixed


def _attached_vault():
    """Keep the overhead vault and wall return on the fixed room plane."""
    image = rgba(ART / "foreground.png")
    w, h = image.size
    ceiling = Image.new("L", (1, h))
    ceiling.putdata([round(255 * min(1, max(0, (535 - y) / 105))) for y in range(h)])
    wall = Image.new("L", (w, 1))
    wall.putdata([round(255 * min(1, max(0, (138 - x) / 88))) for x in range(w)])
    mask = ImageChops.lighter(ceiling.resize(image.size), wall.resize(image.size))
    image.putalpha(ImageChops.multiply(image.getchannel("A"), mask))
    return image


def _tinted_image(size, color, values):
    mask = Image.new("L", size)
    mask.putdata(values)
    image = Image.new("RGB", size, color)
    image.putalpha(mask)
    return image


def _pool_image(size, color, opacity):
    w, h = size
    values = [round(opacity * max(0, 1 - ((x + .5) * 2 / w - 1) ** 2
                                   - ((y + .5) * 2 / h - 1) ** 2) ** 2)
              for y in range(h) for x in range(w)]
    return _tinted_image(size, color, values)


def _light_pool(size, color, opacity):
    return rgba_texture(_pool_image(size, color, opacity))


def _apply_surface_light(image, spill, x, y):
    """Light visible surfaces at room coordinates while retaining their silhouette."""
    patch = image.crop((x, y, x + spill.width, y + spill.height))
    surface = patch.getchannel("A")
    mask = ImageChops.multiply(spill.getchannel("A"), surface)
    rgb = patch.convert("RGB")
    rgb.paste(spill.convert("RGB"), (0, 0), mask)
    rgb.putalpha(surface)
    image.paste(rgb, (x, y))


def _light_floor_edges(image):
    for center, width, color, opacity in FLOOR_LIGHTS:
        spill = _pool_image((width, 88), color, opacity)
        _apply_surface_light(image, spill, center - width // 2, GROUND - 45)
    return image


def _lit_terrain():
    terrain = _green_grade(stage_terrain(), (6, 19, 13), (144, 184, 121), .22)
    _light_floor_edges(terrain)
    _apply_surface_light(terrain, _pool_image((385, 180), (135, 162, 91), 84), 1857, 460)
    return terrain


def _shaft(width, mouth, floor, narrow, wide, color, opacity):
    """Feathered light from a ceiling break, widening towards the arena."""
    size = (width, GROUND)
    values = []
    for y in range(size[1]):
        progress = y / (size[1] - 1)
        center = mouth + (floor - mouth) * progress
        radius = narrow + (wide - narrow) * progress
        falloff = min(1, (1 - progress) / .22) * (1 - .51 * progress)
        for x in range(size[0]):
            u = (x - center) / radius
            edge = max(0, 1 - (u / 1.25) ** 2)
            scatter = .74 * exp(-2.5 * u * u) + .26 * exp(-16 * (u + .22) ** 2)
            values.append(round(opacity * falloff * edge * scatter))
    return rgba_texture(_tinted_image(size, color, values))


def _view_bounds(camera):
    scale = WORLD_PER_ART_PIXEL
    left = camera.x / scale
    bottom = GROUND - camera.y / scale
    top = bottom - pico.get_canvas_height() / (camera.zoom * scale)
    return left, top, left + camera.view_width / scale, bottom


def _draw_plate(camera, image, left=0, top=0, *, size=None):
    width, height = (image.w, image.h) if size is None else size
    scale = WORLD_PER_ART_PIXEL
    center_x = (left + width / 2) * scale
    center_y = (GROUND - top - height / 2) * scale
    image.draw(*camera.world_to_screen(center_x, center_y),
               width * scale * camera.zoom, height * scale * camera.zoom)


def _parallax_origin(view, factor):
    left, top, right, bottom = view
    x, y = NEUTRAL_VIEW_CENTER
    # The fixed origin does not shrink with the factor. Only camera travel is reduced.
    return ((.5 * (left + right) - x) * (1 - factor),
            (.5 * (top + bottom) - y) * (1 - factor))


class B1RoomArt:
    def __init__(self, art_dir=ROOM_ART):
        near_dir = BASE_ROOM_ART if art_dir == ROOM_ART else art_dir
        far = _room_image(art_dir / "far-background.png", FAR_SIZE, opaque=True)
        self.far = rgba_texture(_air_mix(far, (21, 52, 61), .12))
        middle = _room_image(art_dir / "midground.png", ROOM_SIZE)
        middle = _green_grade(middle, (13, 28, 29), (119, 163, 124), .34)
        self.middle = rgba_texture(_air_mix(middle, (28, 55, 61), .18))
        self.terrain = rgba_texture(_lit_terrain())
        boulder = rgba(ART.parent / "ceiling-rock-v2/ceiling-boulder.png")
        boulder = resize(boulder.crop(boulder.getbbox()), (210, 219))
        self.ceiling_boulder = rgba_texture(_green_grade(boulder, (6, 19, 13), (144, 184, 121), .22))
        self.vault = rgba_texture(_green_grade(_attached_vault(), (3, 10, 7), (101, 135, 81), .29))
        edge = _room_image(ROOM_ART / "attached-foreground.png", ROOM_SIZE)
        self.edge = rgba_texture(_light_floor_edges(edge))
        near = _room_image(near_dir / "near-foreground.png", ROOM_SIZE)
        self.near = rgba_texture(_green_grade(near, (3, 11, 8), (88, 122, 73), .31))

        self.air = _light_pool((304, 96), (75, 123, 117), 34)
        self.shaft = _shaft(530, 83, 329, 22, 154, (126, 207, 158), 113)
        self.stele_shaft = _shaft(380, 255, 173, 18, 113, (125, 174, 133), 66)
        self.tunnel_glow = _light_pool((196, 96), (137, 163, 89), 65)
        self.foot_shadow = _light_pool((128, 16), (8, 17, 13), 151)

    def draw_behind_actors(self, camera):
        view = _view_bounds(camera)
        left, top, right, bottom = view
        offset_x, offset_y = _parallax_origin(view, FAR_PARALLAX)
        width, height = self.far.w, self.far.h
        far_x = offset_x + (ROOM_SIZE[0] - width) / 2
        far_y = offset_y + (ROOM_SIZE[1] - height) / 2
        # At a camera edge, trade the last pixels of travel for full paint coverage.
        far_x = min(left, max(right - width, far_x))
        far_y = min(top, max(bottom - height, far_y))
        _draw_plate(camera, self.far, far_x, far_y)

        air_x, air_y = _parallax_origin(view, .40)
        _draw_plate(camera, self.air, 543 + air_x, 445 + air_y, size=(1270, 290))
        middle_x, _ = _parallax_origin(view, MID_PARALLAX)
        # Base rubble stays at floor height as the camera moves vertically.
        _draw_plate(camera, self.middle, middle_x)
        _draw_plate(camera, self.shaft, 762, 0)
        _draw_plate(camera, self.stele_shaft, 1368, 0)
        _draw_plate(camera, self.tunnel_glow, 1814, 493, size=(526, 268))
        _draw_plate(camera, self.terrain)
        # The shell-breaking boulder stays above the boss after the intro rockfall.
        _draw_plate(camera, self.ceiling_boulder, SHELL_X - 100, 42)

        _draw_plate(camera, self.foot_shadow, SHELL_X - 141, GROUND - 4, size=(282, 15))
        _draw_plate(camera, self.foot_shadow, PLAYER_X - 20, GROUND - 3, size=(40, 9))

    def draw_in_front(self, camera):
        _draw_plate(camera, self.vault)
        _draw_plate(camera, self.edge)
        _draw_plate(camera, self.near, *_parallax_origin(_view_bounds(camera), NEAR_PARALLAX))

"""Layered art and local lighting for the B1 roar test room."""

from ctypes import create_string_buffer
from math import exp

from PIL import Image, ImageChops
from pico2d import pico2d as pico

from tools.preview_b1_intro import ART, GROUND, SHELL_X, SIZE
from tools.render_b1_roar_preview import PLAYER_X, rgba, stage_terrain


WORLD_PER_ART_PIXEL = 2
ROOM_SIZE = (2410, 790)
FAR_SIZE = (2690, 950)
ROOM_ART = ART.parent / "room-art-v3"
NEUTRAL_VIEW_CENTER = (1168, 397)
FAR_PARALLAX, MID_PARALLAX, NEAR_PARALLAX = .25, .62, 1.10


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


def _lit_terrain():
    """Catch a little gate light on the slate overhang without changing its alpha."""
    terrain = stage_terrain()
    alpha = terrain.getchannel("A")
    spill = _pool_image((385, 180), (192, 142, 91), 89)
    x, y = 1857, 460
    surface = alpha.crop((x, y, x + spill.width, y + spill.height))
    mask = ImageChops.multiply(spill.getchannel("A"), surface)
    terrain.paste(spill.convert("RGB"), (x, y), mask)
    terrain.putalpha(alpha)
    return terrain


def _shaft():
    """Feathered light from a ceiling break, widening towards the arena."""
    size = (530, GROUND)
    values = []
    for y in range(size[1]):
        progress = y / (size[1] - 1)
        center = 83 + 246 * progress
        radius = 22 + 132 * progress
        falloff = min(1, (1 - progress) / .22) * (1 - .51 * progress)
        for x in range(size[0]):
            u = (x - center) / radius
            edge = max(0, 1 - (u / 1.25) ** 2)
            scatter = .74 * exp(-2.5 * u * u) + .26 * exp(-16 * (u + .22) ** 2)
            values.append(round(82 * falloff * edge * scatter))
    return rgba_texture(_tinted_image(size, (162, 205, 202), values))


def _view_bounds(camera):
    scale = WORLD_PER_ART_PIXEL
    left = camera.x / scale
    bottom = GROUND - camera.y / scale
    return left, bottom - SIZE[1] / (camera.zoom * scale), left + camera.view_width / scale, bottom


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
        far = _room_image(art_dir / "far-background.png", FAR_SIZE, opaque=True)
        self.far = rgba_texture(_air_mix(far, (23, 48, 63), .18))
        middle = _room_image(art_dir / "midground.png", ROOM_SIZE)
        self.middle = rgba_texture(_air_mix(middle, (31, 72, 83), .24))
        self.terrain = rgba_texture(_lit_terrain())
        self.vault = rgba_texture(_attached_vault())
        self.near = rgba_texture(_room_image(art_dir / "near-foreground.png", ROOM_SIZE))

        self.air = _light_pool((304, 96), (121, 161, 163), 29)
        self.shaft = _shaft()
        self.tunnel_glow = _light_pool((196, 96), (190, 147, 92), 66)
        self.stone_bounce = _light_pool((96, 16), (170, 204, 183), 34)
        self.tunnel_bounce = _light_pool((86, 14), (194, 149, 91), 59)
        self.foot_shadow = _light_pool((128, 16), (10, 18, 18), 151)

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
        _draw_plate(camera, self.middle, *_parallax_origin(view, MID_PARALLAX))
        _draw_plate(camera, self.shaft, 762, 0)
        _draw_plate(camera, self.tunnel_glow, 1814, 493, size=(526, 268))
        _draw_plate(camera, self.terrain)

        _draw_plate(camera, self.stone_bounce, 899, GROUND - 7, size=(376, 22))
        _draw_plate(camera, self.tunnel_bounce, 1888, GROUND - 6, size=(377, 21))
        _draw_plate(camera, self.foot_shadow, SHELL_X - 141, GROUND - 4, size=(282, 15))
        _draw_plate(camera, self.foot_shadow, PLAYER_X - 20, GROUND - 3, size=(40, 9))

    def draw_in_front(self, camera):
        _draw_plate(camera, self.vault)
        _draw_plate(camera, self.near, *_parallax_origin(_view_bounds(camera), NEAR_PARALLAX))

"""Layered art and local lighting for the B1 roar test room."""

from ctypes import create_string_buffer
from functools import lru_cache
from math import exp

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageOps
from pico2d import pico2d as pico

from tools.b1_combat_terrain import FLOOR_SOURCE, TERRAIN_ART, stage_terrain
from tools.preview_b1_intro import ART, GROUND, SHELL_X
from tools.render_b1_roar_preview import resize, rgba


WORLD_PER_ART_PIXEL = 2
ROOM_SIZE = (2410, 790)
FAR_SIZE = (2690, 950)
ROOM_ART = ART.parent / "room-art-v4"
BASE_ROOM_ART = ART.parent / "room-art-v3"
NEUTRAL_VIEW_CENTER = (1168, 397)
FAR_PARALLAX, REAR_PARALLAX, MID_PARALLAX, NEAR_PARALLAX = .16, .34, .62, 1.08
BEAM_MOUTH = (952, 71)
BEAM_FLOOR_X = SHELL_X
FLOOR_LIGHTS = (
    (BEAM_FLOOR_X, 575, (149, 169, 133), 88),
    (1548, 325, (83, 136, 125), 31),
    (2077, 377, (121, 147, 106), 32),
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


def _far_art(source):
    """Put the deepest arches in cool shadow and lift the air behind the boss."""
    image = _green_grade(source, (6, 13, 22), (62, 96, 99), .65)
    image = _air_mix(image, (12, 23, 31), .23)
    x_offset = (FAR_SIZE[0] - ROOM_SIZE[0]) // 2
    _apply_surface_light(image, _pool_image((1152, 620), (71, 110, 105), 137),
                         BEAM_FLOOR_X + x_offset - 576, 228)
    return image


def _rear_ruins():
    """Build recessed flights of stairs from the old slate, below the distant arches."""
    image = Image.new("RGBA", (1590, 254))
    source = rgba(FLOOR_SOURCE)
    slate = source.crop((30, 363, source.width - 20, source.height))
    flights = (
        (0, 83, 347, (.28, .46, .65, .82), False),
        (388, 151, 376, (.32, .53, .76), True),
        (805, 140, 307, (.24, .53, .79), False),
        (1120, 65, 470, (.28, .49, .67, .81), True),
    )
    for x, y, width, breaks, flip in flights:
        height = image.height - y
        terrace = resize(slate, (width, height))
        silhouette = Image.new("L", terrace.size)
        pen = ImageDraw.Draw(silhouette)
        nosing = Image.new("RGBA", terrace.size)
        lip = ImageDraw.Draw(nosing)
        left = 0
        for step, edge in enumerate((*breaks, 1)):
            right = min(width - 1, round(edge * width))
            upper = step * 11
            pen.rectangle((left, upper, right, height - 1), fill=255)
            lip.line(((left, upper), (right - 2, upper)), fill=(91, 114, 103, 89), width=2)
            left = right + 1
        terrace.alpha_composite(nosing)
        fade = Image.new("L", (1, height))
        fade.putdata([round(255 * min(1, max(0, (height - 1 - row) / 77))) for row in range(height)])
        terrace.putalpha(ImageChops.multiply(silhouette, fade.resize(terrace.size)))
        if flip:
            terrace = ImageOps.mirror(terrace)
        image.alpha_composite(terrace, (x, y))
    arch = rgba(TERRAIN_ART / "combat-room-v2/midground-broken-arch.png")
    arch = resize(arch.crop(arch.getbbox()), (268, 197))
    image.alpha_composite(arch, (1262, 16))
    image = _green_grade(image, (14, 27, 35), (57, 81, 83), .83)
    image = _air_mix(image, (36, 58, 64), .42)
    blurred_alpha = image.getchannel("A").filter(ImageFilter.GaussianBlur(1.2))
    image = image.filter(ImageFilter.GaussianBlur(.7))
    image.putalpha(blurred_alpha)
    return image


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


@lru_cache(maxsize=1)
def _pool_alpha():
    size = 128
    mask = Image.new("L", (size, size))
    mask.putdata([round(255 * max(0, 1 - ((x + .5) * 2 / size - 1) ** 2
                                      - ((y + .5) * 2 / size - 1) ** 2) ** 2)
                  for y in range(size) for x in range(size)])
    return mask


def _pool_image(size, color, opacity):
    image = Image.new("RGB", size, color)
    mask = _pool_alpha().resize(size, Image.Resampling.BILINEAR)
    image.putalpha(mask.point(lambda value: round(value * opacity / 255)))
    return image


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


def _lit_terrain(gate_closed, show_carriages):
    terrain = stage_terrain(gate_closed=gate_closed, show_carriages=show_carriages)
    terrain = _green_grade(terrain, (7, 17, 21), (150, 169, 151), .25)
    _light_floor_edges(terrain)
    _apply_surface_light(terrain, _pool_image((395, 170), (105, 156, 143), 66), 710, 112)
    _apply_surface_light(terrain, _pool_image((385, 180), (135, 162, 113), 48), 1857, 460)
    return terrain


def _shaft(width, height, mouth, floor, narrow, wide, color, opacity):
    """Feathered light from a ceiling break, widening towards the arena."""
    size = (width, height)
    values = []
    for y in range(height):
        progress = y / (height - 1)
        center = mouth + (floor - mouth) * progress
        radius = narrow + (wide - narrow) * progress
        falloff = min(1, progress / .045, (1 - progress) / .13) * (1 - .34 * progress)
        for x in range(width):
            u = (x - center) / radius
            edge = max(0, 1 - (u / 1.25) ** 2)
            scatter = .74 * exp(-2.5 * u * u) + .26 * exp(-16 * (u + .22) ** 2)
            values.append(round(opacity * falloff * edge * scatter))
    return rgba_texture(_tinted_image(size, color, values))


def _foreground(source):
    """Lift the lightward leaves, then thin the silhouettes at the side openings."""
    image = _green_grade(source, (7, 14, 18), (86, 124, 107), .52)
    _apply_surface_light(image, _pool_image((441, 213), (70, 123, 111), 115), 727, 0)
    _apply_surface_light(image, _pool_image((352, 261), (67, 116, 111), 57), 1999, 403)
    _apply_surface_light(image, _pool_image((327, 214), (60, 112, 109), 63), 0, 481)
    alpha = image.getchannel("A")
    for left in (0, 2090):
        box = (left, 188, left + 320, 594)
        faded = ImageChops.multiply(alpha.crop(box), ImageOps.invert(
            _pool_image((320, 406), (0, 0, 0), 49).getchannel("A")))
        alpha.paste(faded, box[:2])
    image.putalpha(alpha)
    return image


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


def _trim_plate(image, top=0):
    left, upper, right, bottom = image.getbbox()
    return rgba_texture(image.crop((left, upper, right, bottom))), left, upper + top


def _draw_trimmed(camera, plate, dx=0, dy=0):
    image, left, top = plate
    _draw_plate(camera, image, left + dx, top + dy)


def _parallax_origin(view, factor):
    left, top, right, bottom = view
    x, y = NEUTRAL_VIEW_CENTER
    # The fixed origin does not shrink with the factor. Only camera travel is reduced.
    return ((.5 * (left + right) - x) * (1 - factor),
            (.5 * (top + bottom) - y) * (1 - factor))


class B1RoomArt:
    def __init__(self, art_dir=ROOM_ART, *, gate_closed=True, show_carriages=True):
        near_dir = BASE_ROOM_ART if art_dir == ROOM_ART else art_dir
        far = _room_image(art_dir / "far-background.png", FAR_SIZE, opaque=True)
        self.far = rgba_texture(_far_art(far))
        pico.SDL_SetTextureBlendMode(self.far.texture, pico.SDL_BLENDMODE_NONE)
        self.rear = _trim_plate(_rear_ruins())
        middle = _room_image(art_dir / "midground.png", ROOM_SIZE)
        middle = _air_mix(_green_grade(middle, (12, 23, 29), (99, 132, 116), .46), (28, 49, 55), .17)
        _apply_surface_light(middle, _pool_image((448, 450), (123, 159, 136), 78), 592, 276)
        _apply_surface_light(middle, _pool_image((282, 335), (77, 129, 122), 72), 1435, 402)
        self.middle = _trim_plate(middle)
        terrain = _lit_terrain(gate_closed, show_carriages)
        # Upload the middle rails and the floor as narrower strips for SDL's software path.
        bands = ((0, 340), (340, 652), (652, ROOM_SIZE[1]))
        self.terrain = tuple(_trim_plate(terrain.crop((0, top, ROOM_SIZE[0], bottom)), top)
                             for top, bottom in bands)
        boulder = rgba(ART.parent / "ceiling-rock-v2/ceiling-boulder.png")
        boulder = resize(boulder.crop(boulder.getbbox()), (210, 219))
        boulder = _green_grade(boulder, (6, 19, 23), (151, 184, 162), .37)
        _apply_surface_light(boulder, _pool_image((160, 215), (110, 163, 150), 101), -26, -17)
        self.ceiling_boulder = rgba_texture(boulder)
        self.vault = _trim_plate(_foreground(_attached_vault()))
        edge = _room_image(ROOM_ART / "attached-foreground.png", ROOM_SIZE)
        self.edge = _trim_plate(_light_floor_edges(_foreground(edge)))
        near = _room_image(near_dir / "near-foreground.png", ROOM_SIZE)
        self.near = _trim_plate(_foreground(near))

        self.air = _light_pool((280, 54), (69, 102, 105), 37)
        self.shaft = _shaft(290, 320, 100, 169, 13, 87, (159, 209, 185), 104)
        self.stele_shaft = _shaft(166, 275, 107, 70, 6, 52, (92, 156, 152), 36)
        self.tunnel_glow = _light_pool((132, 58), (113, 146, 112), 42)
        self.shadow = _light_pool((96, 18), (4, 9, 14), 189)

    def draw_behind_actors(self, camera, *, show_boulder=True):
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

        rear_x, rear_y = _parallax_origin(view, REAR_PARALLAX)
        _draw_trimmed(camera, self.rear, 349 + rear_x, 452 + rear_y)
        _draw_plate(camera, self.air, 420 + rear_x, 526 + rear_y, size=(1650, 168))
        middle_x, _ = _parallax_origin(view, MID_PARALLAX)
        # Base rubble stays at floor height as the camera moves vertically.
        _draw_trimmed(camera, self.middle, middle_x)
        _draw_plate(camera, self.shaft, BEAM_MOUTH[0] - 200, BEAM_MOUTH[1] - 13, size=(580, 652))
        _draw_plate(camera, self.stele_shaft, 1375, 68, size=(332, 620))
        _draw_plate(camera, self.tunnel_glow, 1814, 493, size=(526, 268))
        for plate in self.terrain:
            _draw_trimmed(camera, plate)
        # The shell-breaking boulder stays above the boss after the intro rockfall.
        if show_boulder:
            _draw_plate(camera, self.ceiling_boulder, SHELL_X - 100, 42)

    def draw_actor_shadows(self, camera, boss_x, player_x):
        if boss_x is not None:
            _draw_plate(camera, self.shadow, boss_x - 185, GROUND - 7, size=(370, 25))
            _draw_plate(camera, self.shadow, boss_x - 121, GROUND - 5, size=(87, 13))
            _draw_plate(camera, self.shadow, boss_x + 34, GROUND - 5, size=(87, 13))
        _draw_plate(camera, self.shadow, player_x - 25, GROUND - 4, size=(50, 12))

    def draw_in_front(self, camera):
        _draw_trimmed(camera, self.vault)
        _draw_trimmed(camera, self.edge)
        _draw_trimmed(camera, self.near, *_parallax_origin(_view_bounds(camera), NEAR_PARALLAX))

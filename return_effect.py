"""Draw relic teleportation and the mark left at its departure point."""

from ctypes import byref, c_uint32
from math import pi, sin
from random import Random
from typing import NamedTuple

from PIL import Image
from pico2d import pico2d as pico


DEPARTURE_DURATION = 0.36
ARRIVAL_DELAY = 0.16
ARRIVAL_DURATION = 0.43
RETURN_DURATION = ARRIVAL_DELAY + ARRIVAL_DURATION
CAPTURE_WIDTH = 128
CAPTURE_HEIGHT = 104
CAPTURE_FEET_X = 64
CAPTURE_FEET_Y = 76
FRAGMENT_SIZE = 2
RETURN_MARK_DURATION = 3.0
RETURN_MARK_ABSORB_DURATION = 0.85
MARK_WORLD_SIZE = 42  # 14 px at the normal camera zoom.
MARK_SAMPLE_SIZE = 14


def sample_mark_pixels(image_path):
    with Image.open(image_path) as image:
        sample = image.convert("RGBA").resize((MARK_SAMPLE_SIZE, MARK_SAMPLE_SIZE), Image.Resampling.BOX)
    pixels = sample.load()
    center = (MARK_SAMPLE_SIZE - 1) / 2
    rng = Random(81)
    for row in range(MARK_SAMPLE_SIZE):
        for column in range(MARK_SAMPLE_SIZE):
            red, green, blue, alpha = pixels[column, row]
            if alpha > 16:
                yield (
                    column - center, center - row, (red, green, blue), alpha, rng.uniform(0, 0.27),
                    rng.uniform(-62, 62), rng.uniform(-34, 68),
                )


class ReturnMarkArt:
    def __init__(self, image_path):
        self.image = pico.load_image(str(image_path))
        if pico.SDL_SetTextureScaleMode(self.image.texture, pico.SDL_ScaleModeLinear) != 0:
            raise RuntimeError(pico.SDL_GetError())
        self.pixels = tuple(sample_mark_pixels(image_path))


class ReturnMark:
    def __init__(self, departure, now, art):
        self.art = art
        self.pose = departure.x, departure.y, departure.crouch_time
        _, bottom, _, top = departure.get_hitbox()
        self.position = departure.x, (bottom + top) / 2
        self.created_at = now
        self.absorbs_at = now + RETURN_MARK_DURATION

    def can_return(self, now):
        return now < self.absorbs_at

    def finish(self, now):
        self.absorbs_at = min(now, self.absorbs_at)

    def visible(self, now):
        return now < self.absorbs_at + RETURN_MARK_ABSORB_DURATION

    def draw(self, camera, target, now):
        center_x, center_y = camera.world_to_screen(*self.position)
        width = MARK_WORLD_SIZE * camera.zoom
        age = now - self.created_at
        pulse = (0.88 + 0.12 * sin(age * 6)) * min(1.0, 0.4 + age / 0.15)
        opacity = 0.88 * pulse
        if self.can_return(now):
            self.art.image.opacify(opacity)
            self.art.image.draw(center_x, center_y, width, width)
            return

        target_x, target_y = target
        pixel_size = width / MARK_SAMPLE_SIZE
        size = max(1, round(pixel_size))
        absorption = (now - self.absorbs_at) / RETURN_MARK_ABSORB_DURATION
        previous_blend_mode = pico.SDL_BlendMode()
        pico.SDL_GetRenderDrawBlendMode(pico.renderer, byref(previous_blend_mode))
        pico.SDL_SetRenderDrawBlendMode(pico.renderer, pico.SDL_BLENDMODE_BLEND)
        try:
            for column, row, color, alpha, delay, drift_x, drift_y in self.art.pixels:
                flight = max(0.0, (absorption - delay) / (1 - delay))
                travel = flight ** 2
                scatter = sin(pi * flight) * camera.zoom
                origin_x = center_x + column * pixel_size
                origin_y = center_y + row * pixel_size
                x = round(origin_x + (target_x - origin_x) * travel + drift_x * scatter)
                y = round(origin_y + (target_y - origin_y) * travel + drift_y * scatter)
                fade = round(alpha * opacity * (1 - flight ** 3))
                pico.draw_rectangle(x, y, x + size - 1, y + size - 1, *color, fade, filled=True)
        finally:
            pico.SDL_SetRenderDrawBlendMode(pico.renderer, previous_blend_mode)


class Fragment(NamedTuple):
    pixels: list
    release: float
    drift_x: float
    drift_y: float
    light: tuple[int, int, int]


class PoseCamera:
    """Keep the normal sprite scale, with the feet inside the capture texture."""

    def __init__(self, player, zoom):
        self.x = player.x
        self.y = player.y
        self.zoom = zoom

    def world_to_screen(self, x, y):
        return (
            CAPTURE_FEET_X + (x - self.x) * self.zoom,
            pico.canvas_height - CAPTURE_FEET_Y + (y - self.y) * self.zoom,
        )


def capture_fragments(player, zoom):
    pico.SDL_SetRenderDrawColor(pico.renderer, 0, 0, 0, 0)
    pico.SDL_RenderClear(pico.renderer)
    player.draw_body(PoseCamera(player, zoom))
    pixels = (c_uint32 * (CAPTURE_WIDTH * CAPTURE_HEIGHT))()
    bounds = pico.SDL_Rect(0, 0, CAPTURE_WIDTH, CAPTURE_HEIGHT)
    if pico.SDL_RenderReadPixels(
        pico.renderer, bounds, pico.SDL_PIXELFORMAT_ARGB8888, pixels, CAPTURE_WIDTH * 4,
    ) != 0:
        raise RuntimeError(pico.SDL_GetError())

    rng = Random(412)
    fragments = []
    for top in range(0, CAPTURE_HEIGHT, FRAGMENT_SIZE):
        for left in range(0, CAPTURE_WIDTH, FRAGMENT_SIZE):
            tile = []
            for y in range(top, top + FRAGMENT_SIZE):
                for x in range(left, left + FRAGMENT_SIZE):
                    pixel = pixels[y * CAPTURE_WIDTH + x]
                    alpha = pixel >> 24
                    if alpha > 32:
                        # Blending onto a transparent capture premultiplies the color.
                        red, green, blue = (
                            min(255, round(((pixel >> shift) & 255) * 255 / alpha))
                            for shift in (16, 8, 0)
                        )
                        tile.append((x - CAPTURE_FEET_X, y - CAPTURE_FEET_Y, red, green, blue, alpha))
            if tile:
                fragments.append(Fragment(
                    tile,
                    0.03 + 0.36 * rng.random() + 0.17 * top / CAPTURE_FEET_Y,
                    (left - CAPTURE_FEET_X) * 1.5 + rng.uniform(-15, 15),
                    rng.uniform(-31, -7),
                    (139, 227, 255) if rng.random() < 0.33 else (37, 151, 255),
                ))
    return fragments


def draw_fragments(fragments, camera, position, progress, horizontal_drift):
    if progress >= 1:
        return
    x, y = camera.world_to_screen(*position)
    x, y = round(x), round(pico.canvas_height - y)
    for fragment in fragments:
        flight = max(0.0, (progress - fragment.release) / (1 - fragment.release))
        distance = flight ** 0.86
        tint = min(1.0, flight * 5.5)
        opacity = (1 - flight) ** 0.78
        offset_x = round((fragment.drift_x + horizontal_drift) * distance)
        offset_y = round(fragment.drift_y * distance)
        light_r, light_g, light_b = fragment.light
        for pixel_x, pixel_y, red, green, blue, alpha in fragment.pixels:
            pico.SDL_SetRenderDrawColor(
                pico.renderer, round(red + (light_r - red) * tint),
                round(green + (light_g - green) * tint),
                round(blue + (light_b - blue) * tint), round(alpha * opacity),
            )
            pico.SDL_RenderDrawPoint(pico.renderer, x + pixel_x + offset_x, y + pixel_y + offset_y)


class ReturnEffect:
    def __init__(self):
        self.started_at = None

    def start(self, departure, player, camera, now):
        self.started_at = None
        texture = pico.SDL_CreateTexture(
            pico.renderer, pico.SDL_PIXELFORMAT_RGBA8888, pico.SDL_TEXTUREACCESS_TARGET,
            CAPTURE_WIDTH, CAPTURE_HEIGHT,
        )
        if not texture:
            print("Could not capture relic return pose:", pico.SDL_GetError())
            return

        previous_target = pico.SDL_GetRenderTarget(pico.renderer)
        try:
            if pico.SDL_SetRenderTarget(pico.renderer, texture) != 0:
                raise RuntimeError(pico.SDL_GetError())
            self.departure = capture_fragments(departure, camera.zoom)
            self.arrival = capture_fragments(player, camera.zoom)
        except RuntimeError as error:
            print("Could not capture relic return pose:", error)
            return
        finally:
            restored = pico.SDL_SetRenderTarget(pico.renderer, previous_target)
            pico.SDL_DestroyTexture(texture)
            if restored != 0:
                raise RuntimeError(pico.SDL_GetError())

        if not self.departure or not self.arrival:
            return
        self.origin = departure.x, departure.y
        _, bottom, _, top = departure.get_hitbox()
        self.origin_light = departure.x, (bottom + top) / 2
        self.destination = player.x, player.y
        _, bottom, _, top = player.get_hitbox()
        self.arrival_light_height = (top - bottom) / 2
        self.started_at = now

    def draw(self, player, camera, now, lighting):
        if self.started_at is None:
            return False
        age = now - self.started_at
        if age >= RETURN_DURATION:
            self.started_at = None
            return False

        departure = min(1.0, age / DEPARTURE_DURATION)
        arrival = max(0.0, (age - ARRIVAL_DELAY) / ARRIVAL_DURATION)
        # Start gathering at the relic and follow the player as the body forms.
        tracking = min(1.0, arrival * 2.5)
        destination_x, destination_y = self.destination
        arrival_x = destination_x + (player.x - destination_x) * tracking
        arrival_y = destination_y + (player.y - destination_y) * tracking
        if lighting is not None:
            lighting.draw_glow(
                camera.world_to_screen(*self.origin_light), 48, 48,
                alpha=round(61 * sin(pi * departure)),
            )
            lighting.draw_glow(
                camera.world_to_screen(arrival_x, arrival_y + self.arrival_light_height), 48, 48,
                alpha=round(87 * sin(pi * arrival)),
            )

        previous_blend_mode = pico.SDL_BlendMode()
        pico.SDL_GetRenderDrawBlendMode(pico.renderer, byref(previous_blend_mode))
        pico.SDL_SetRenderDrawBlendMode(pico.renderer, pico.SDL_BLENDMODE_BLEND)
        try:
            draw_fragments(self.departure, camera, self.origin, departure, 4)
            player.draw(camera, show_body=False)
            draw_fragments(self.arrival, camera, (arrival_x, arrival_y), 1 - arrival, -5)
        finally:
            pico.SDL_SetRenderDrawBlendMode(pico.renderer, previous_blend_mode)
        return True

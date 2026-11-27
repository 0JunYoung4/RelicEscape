"""Draw the B1 intro's roar in the same SDL renderer as RelicEscape."""

from bisect import bisect_right
from itertools import accumulate
import json

from PIL import Image, ImageChops, ImageFilter
from pico2d import pico2d as pico

from player import Animation, CROUCH_DURATION, Player
from tools.b1_room_art import B1RoomArt, ROOM_ART, ROOM_SIZE, WORLD_PER_ART_PIXEL, rgba_texture
from tools.b1_room_atmosphere import B1Motes
from tools.preview_b1_intro import ART, GROUND, SHELL_X
from tools.render_b1_roar_preview import FPS, PLAYER_X, RELEASE_FRAME, ROAR_ART, camera_box


ROAR_V4 = ART.parent / "roar-v4"


def _lit_boss_atlas(path, frames):
    with Image.open(path) as source:
        atlas = source.convert("RGBA")
    for frame in frames:
        x, y, width, height = (frame[key] for key in ("x", "y", "width", "height"))
        rgb = atlas.crop((x, y, x + width, y + height))
        red, green, blue, alpha = rgb.split()
        rgb = rgb.convert("RGB")
        # Light the upper-left silhouette from the ceiling opening.
        rim = ImageChops.subtract(alpha, ImageChops.offset(alpha, 2, 3))
        rim = rim.filter(ImageFilter.GaussianBlur(.65)).point(lambda v: round(v * .48))
        rgb.paste((103, 181, 174), (0, 0, width, height), rim)
        gold = ImageChops.subtract(ImageChops.darker(red, green), blue)
        gold = gold.point(lambda v: min(55, max(0, v - 23)))
        rgb.paste((222, 203, 126), (0, 0, width, height), gold)
        eyes = ImageChops.darker(ImageChops.subtract(red, green).point(lambda v: max(0, v - 16) * 7),
                                 red.point(lambda v: max(0, v - 169) * 3))
        rgb.paste((230, 172, 94), (0, 0, width, height),
                  eyes.filter(ImageFilter.GaussianBlur(3)).point(lambda v: min(65, v * 2)))
        rgb.paste((255, 234, 171), (0, 0, width, height), eyes)
        rgb.putalpha(alpha)
        atlas.paste(rgb, (x, y))
    return rgba_texture(atlas)


def _load_boss():
    spec = json.loads((ROAR_V4 / "boss-roar.json").read_text(encoding="utf-8"))
    width, height = spec["frame_size"]
    frames = [{"x": frame["column"] * width, "y": frame["row"] * height,
               "width": width, "height": height} for frame in spec["frames"]]
    durations = tuple(frame["duration_ms"] for frame in spec["frames"])
    atlas_path = ROAR_V4 / "boss-roar-sheet.png"
    animation = Animation(atlas_path, frames, spec["pivot"],
                          WORLD_PER_ART_PIXEL, 0, durations)
    animation.image = _lit_boss_atlas(atlas_path, frames)
    apex = next(start for start, frame in zip(accumulate((0, *durations)), spec["frames"])
                if frame["label"] == "K5")
    return animation, apex


class _Effect:
    def __init__(self, name):
        frames, durations = [], []
        with Image.open(ROAR_ART / f"{name}-animation.webp") as source:
            for index in range(source.n_frames):
                source.seek(index)
                frame = source.convert("RGBA")
                frames.append(rgba_texture(frame) if frame.getbbox() else None)
                durations.append(source.info["duration"])
        self.frames = frames
        self.ends = tuple(accumulate(durations))

    def draw(self, camera, elapsed_ms, pivot):
        index = bisect_right(self.ends, elapsed_ms)
        if index == len(self.frames) or self.frames[index] is None:
            return
        image = self.frames[index]
        scale = WORLD_PER_ART_PIXEL
        center_x = (SHELL_X + image.w / 2 - pivot[0]) * scale
        center_y = (pivot[1] - image.h / 2) * scale
        image.draw(*camera.world_to_screen(center_x, center_y),
                   image.w * scale * camera.zoom, image.h * scale * camera.zoom)


class B1RoarStage:
    """A deterministic, self-contained shot beginning after the intro rockfall."""

    def __init__(self, *, art_dir=ROOM_ART, gate_closed=True, show_carriages=True, player=None):
        from main import Camera

        self.room_art = B1RoomArt(art_dir, gate_closed=gate_closed, show_carriages=show_carriages)
        self.motes = B1Motes()
        world_width = ROOM_SIZE[0] * WORLD_PER_ART_PIXEL
        self.camera = Camera(pico.get_canvas_width(), world_width)
        self.boss_x = SHELL_X * WORLD_PER_ART_PIXEL
        self.player = player
        if self.player is None:
            self.player = Player(PLAYER_X * WORLD_PER_ART_PIXEL, 0, world_width)
            self.player.facing = -1

        self.boss, self.apex_ms = _load_boss()
        self.duration_ms = self.boss.frame_ends_ms[-1]
        self.boss_change_times = (0, *self.boss.frame_ends_ms[:-1])

        spec = json.loads((ROAR_ART / "roar-effects.json").read_text(encoding="utf-8"))
        self.effect_pivot = spec["pivot"]
        self.effect_in_point = sum(spec["frame_durations_ms"][:spec["layers"][0]["first_visible_frame"]])
        self.wave = _Effect("roar-wave")
        self.debris = _Effect("roar-debris")

    def _set_camera(self, elapsed_ms, camera_view):
        if camera_view is None:
            phase = RELEASE_FRAME + (elapsed_ms - self.apex_ms) * FPS / 1000
            camera_view = camera_box(phase)
        left, _, right, bottom = camera_view
        scale = WORLD_PER_ART_PIXEL
        self.camera.zoom = self.camera.screen_width / ((right - left) * scale)
        self.camera.x = left * scale
        self.camera.y = (GROUND - bottom) * scale

    def _draw_room(self, ambient_ms, *, airborne=False, show_boulder=True):
        pico.clear_canvas()
        self.room_art.draw_behind_actors(self.camera, show_boulder=show_boulder)
        self.motes.draw(self.camera, ambient_ms)
        boss_x = None if airborne else self.boss_x / WORLD_PER_ART_PIXEL
        self.room_art.draw_actor_shadows(self.camera, boss_x, self.player.x / WORLD_PER_ART_PIXEL)

    def _draw_roar(self, elapsed_ms):
        since_release = (elapsed_ms - self.apex_ms) / 1000
        effect_elapsed = elapsed_ms - self.apex_ms + self.effect_in_point
        if since_release >= 0:
            self.wave.draw(self.camera, effect_elapsed, self.effect_pivot)
        self.boss.draw(self.boss_x, 0, 1, elapsed_ms / 1000, self.camera)
        if since_release >= 0:
            self.debris.draw(self.camera, effect_elapsed, self.effect_pivot)

    def _brace_player(self, elapsed_ms):
        since_release = (elapsed_ms - self.apex_ms) / 1000
        brace = max(0, min(CROUCH_DURATION, since_release - .08, .6 - since_release))
        self.player.crouch_time = brace
        self.player.state = "crouch" if brace > 0 else "idle"

    def draw(self, elapsed_ms, *, camera_view=None, ambient_ms=None):
        ambient_ms = elapsed_ms if ambient_ms is None else ambient_ms
        elapsed_ms = min(self.duration_ms, max(0, elapsed_ms))
        self._set_camera(elapsed_ms, camera_view)
        self._draw_room(ambient_ms)
        self._draw_roar(elapsed_ms)
        self._brace_player(elapsed_ms)
        self.player.draw(self.camera)
        self.room_art.draw_in_front(self.camera)

    def close(self):
        """Release pico2D images while the SDL renderer is still open."""
        self.room_art = self.boss = self.player = self.wave = self.debris = None

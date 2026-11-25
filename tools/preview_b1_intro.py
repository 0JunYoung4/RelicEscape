"""Play the B1 shell investigation and ceiling-tremor concept separately."""

import argparse
from dataclasses import dataclass
from functools import lru_cache
import json
import math
import os
from pathlib import Path
import random
import time

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
PLAYER_ART = ROOT / "assets/sprites/player"
ART = ROOT / "assets/concepts/b1-hermit-crab/right-passage-v1"
SIZE = (960, 540)
GROUND = 703
SHELL_X = 1090
APPROACH_LIMIT = 1352
INTERACT_DISTANCE = 350
LAST_TREMOR = 3.2
GIF = ART / "shell-investigation-preview.gif"


def clamp(value, minimum, maximum):
    return min(max(value, minimum), maximum)


def lerp(start, end, fraction):
    return start + (end - start) * fraction


def smoothstep(fraction):
    fraction = clamp(fraction, 0.0, 1.0)
    return fraction * fraction * (3 - 2 * fraction)


@dataclass
class Preview:
    x: float = 2235.0
    facing: int = -1
    walk_time: float = 0.0
    elapsed: float | None = None

    @property
    def can_interact(self):
        return self.elapsed is None and abs(self.x - SHELL_X) <= INTERACT_DISTANCE

    def interact(self):
        if not self.can_interact:
            return False
        self.elapsed = 0.0
        return True

    def advance(self, seconds, direction):
        if direction:
            self.facing = direction
        next_x = clamp(self.x + direction * 410 * seconds, APPROACH_LIMIT, 2320)
        self.walk_time = self.walk_time + seconds if next_x != self.x else 0.0
        self.x = next_x
        if self.elapsed is not None:
            self.elapsed = min(self.elapsed + seconds, LAST_TREMOR)


def load_actor():
    atlas = Image.open(PLAYER_ART / "run-right-v1.png").convert("RGBA")
    meta = json.loads((PLAYER_ART / "run-right-v1.json").read_text(encoding="utf-8"))
    walk = []
    for frame in meta["frames"]:
        x, y, w, h = (frame[key] for key in ("x", "y", "width", "height"))
        pose = atlas.crop((x, y, x + w, y + h))
        pose = pose.resize((round(w * .253), round(h * .253)), Image.Resampling.LANCZOS)
        ax, ay = (round(coordinate * .253) for coordinate in frame["foot_anchor"])
        walk.append((pose, ax, ay))
    pose = Image.open(PLAYER_ART / "idle-right-v3.png").convert("RGBA")
    pose = pose.resize((89, 89), Image.Resampling.NEAREST)
    return walk, (pose, 44, pose.getchannel("A").getbbox()[3])


@dataclass(frozen=True)
class Particle:
    birth: float
    x: float
    y: float
    drift: float
    speed: float
    radius: int
    lifetime: float
    is_stone: bool


def ceiling_particles():
    rng = random.Random(15)
    sources = ((768, 107), (930, 95), (989, 118), (1196, 126), (1264, 105), (1472, 101))
    particles = []
    for when, count in ((.12, 12), (.49, 20), (.94, 25), (1.42, 28), (1.86, 30)):
        for i in range(count):
            x, y = sources[rng.randrange(len(sources))]
            stone = i % 3 == 0
            particles.append(Particle(
                when + rng.uniform(0, .18), x + rng.uniform(-40, 40), y + rng.uniform(-6, 20),
                rng.uniform(-43, 43), rng.uniform(20, 55), rng.randint(2, 7) if stone else rng.randint(8, 27),
                rng.uniform(.7, 1.4) if stone else rng.uniform(.74, 1.22), stone,
            ))
    return particles


@lru_cache(maxsize=32)
def dust_tile(radius):
    alpha = Image.new("L", (radius * 3, radius * 5))
    draw = ImageDraw.Draw(alpha)
    draw.ellipse((radius * .58, radius * .45, radius * 1.9, radius * 2.85), fill=52)
    draw.ellipse((radius * .8, radius * 1.35, radius * 2.35, radius * 3.40), fill=78)
    draw.ellipse((radius * .56, radius * 2.52, radius * 2.45, radius * 4.1), fill=96)
    alpha = alpha.filter(ImageFilter.GaussianBlur(radius * .42))
    image = Image.new("RGBA", alpha.size, (172, 157, 133, 0))
    image.putalpha(alpha)
    return image


def camera_box(preview):
    t = preview.elapsed or 0.0
    widen = smoothstep(t / .60)
    width = lerp(960, 1264, widen)
    height = width * 9 / 16
    left = clamp(preview.x - lerp(411, 699, widen), 0, 2410 - width)
    top = lerp(205, 35, widen)
    tremor = 0.0
    for onset, strength, duration in ((0.0, 3.2, .55), (.46, 4.2, .64), (.94, 5.0, .68),
                                      (1.43, 6.5, .79), (1.90, 7.0, .91)):
        age = t - onset
        if 0 <= age < duration:
            tremor += strength * (1 - age / duration) ** .8
    if preview.elapsed is not None:
        left += math.sin(49 * t) * tremor * .57
        top += math.sin(61 * t + .30) * tremor
    left = clamp(left, 0, 2410 - width)
    top = clamp(top, 0, 790 - height)
    return left, top, left + width, top + height


class Art:
    def __init__(self):
        scene = Image.open(ART / "room-placement-preview.png").convert("RGBA")
        patch = 2118, 625, 2191, 705
        back, terrain, self.foreground = [
            Image.open(ART / f"{layer}.png").convert("RGBA") for layer in ("background", "terrain", "foreground")
        ]
        clean = Image.alpha_composite(back.crop(patch), terrain.crop(patch))
        clean.alpha_composite(self.foreground.crop(patch))
        scene.paste(clean, patch[:2])
        self.scene = scene
        self.walk, self.idle = load_actor()
        self.particles = ceiling_particles()
        font_dir = Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts"
        try:
            self.font = ImageFont.truetype(str(font_dir / "malgun.ttf"), 16)
            self.interaction_label = "조사"
        except OSError:
            self.font = ImageFont.load_default()
            self.interaction_label = "Inspect"

    def draw_particles(self, frame, box, elapsed):
        left, top, right, _ = box
        scale = SIZE[0] / (right - left)
        layer = Image.new("RGBA", SIZE)
        stones = ImageDraw.Draw(layer)
        for particle in self.particles:
            age = elapsed - particle.birth
            if not 0 <= age < particle.lifetime:
                continue
            world_x = particle.x + particle.drift * age
            gravity = 480 if particle.is_stone else 212
            speed = particle.speed if particle.is_stone else particle.speed + 44
            world_y = particle.y + speed * age + gravity * age * age / 2
            if world_y >= GROUND:
                continue
            x = (world_x - left) * scale
            y = (world_y - top) * scale
            if not -56 < x < SIZE[0] + 56 or not -56 < y < SIZE[1] + 56:
                continue
            strength = (1 - age / particle.lifetime) ** .65
            if particle.is_stone:
                r = max(2, particle.radius * scale)
                tilt = age * 6 + particle.x
                points = [(x + math.cos(tilt + i * math.tau / 4) * r * extent,
                           y + math.sin(tilt + i * math.tau / 4) * r * extent)
                          for i, extent in enumerate((1.2, .78, 1, .65))]
                opacity = round(243 * strength)
                stones.polygon(points, fill=(97, 113, 111, opacity), outline=(27, 41, 43, opacity))
                stones.line((points[0], points[1]), fill=(164, 175, 156, opacity), width=1)
            else:
                r = max(2, round((particle.radius + age * 7) * scale))
                tile = dust_tile(r).copy()
                fade = strength * min(1, age / .10)
                tile.putalpha(tile.getchannel("A").point([round(value * fade) for value in range(256)]))
                layer.alpha_composite(tile, (round(x - tile.width / 2), round(y - tile.height / 2)))
        foreground = self.foreground.resize(SIZE, Image.Resampling.BILINEAR, box=box)
        open_pixels = ImageOps.invert(foreground.getchannel("A"))
        layer.putalpha(ImageChops.multiply(layer.getchannel("A"), open_pixels))
        frame.alpha_composite(layer)

    def render(self, preview):
        box = camera_box(preview)
        left, top, right, _ = box
        scale = SIZE[0] / (right - left)
        frame = self.scene.resize(SIZE, Image.Resampling.BILINEAR, box=box)
        if preview.elapsed is not None and preview.elapsed < LAST_TREMOR:
            self.draw_particles(frame, box, preview.elapsed)

        pose, ax, ay = self.walk[int(preview.walk_time * 16) % len(self.walk)] if preview.walk_time else self.idle
        if preview.facing < 0:
            pose, ax = ImageOps.mirror(pose), pose.width - ax
        pose = pose.resize((round(pose.width * scale), round(pose.height * scale)), Image.Resampling.LANCZOS)
        x = (preview.x - left) * scale
        floor = (GROUND - top) * scale
        frame.alpha_composite(pose, (round(x - ax * scale), round(floor - ay * scale)))
        if preview.can_interact:
            label = f"E  {self.interaction_label}"
            pen = ImageDraw.Draw(frame)
            w = round(pen.textlength(label, font=self.font)) + 24
            y = round(floor - 98 * scale)
            pen.rounded_rectangle((x - w/2, y - 15, x + w/2, y + 15), radius=9,
                                  fill=(13, 25, 28, 255), outline=(150, 143, 102, 255))
            pen.text((x, y - 1), label, anchor="mm", font=self.font, fill=(246, 228, 178, 255))
        return frame.convert("RGB")


def write_gif(art):
    preview = Preview()
    step = .04
    frames = []
    seconds = 0.0
    ready_since = None
    while preview.elapsed is None or preview.elapsed < LAST_TREMOR:
        frames.append(art.render(preview).resize((768, 432), Image.Resampling.LANCZOS))
        if preview.can_interact and ready_since is None:
            ready_since = seconds
        if ready_since is not None and seconds - ready_since >= .36 and preview.elapsed is None:
            preview.interact()
        preview.advance(step, -1 if ready_since is None else 0)
        seconds += step
    frames.append(art.render(preview).resize((768, 432), Image.Resampling.LANCZOS))
    palette_samples = Image.new("RGB", (960, 540))
    for i, index in enumerate(round((len(frames) - 1) * k / 8) for k in range(9)):
        palette_samples.paste(frames[index].resize((320, 180), Image.Resampling.BOX), (i % 3 * 320, i // 3 * 180))
    palette = palette_samples.quantize(colors=251)
    accents = [249, 222, 172, 242, 226, 198, 105, 174, 218, 70, 135, 197, 49, 91, 147]
    palette.putpalette(palette.getpalette()[:753] + accents)
    packed = [item.quantize(palette=palette, dither=Image.Dither.NONE) for item in frames]
    packed[0].save(GIF, save_all=True, append_images=packed[1:], duration=[40] * (len(packed) - 1) + [560],
                   loop=0, optimize=True)
    print(f"Saved {GIF.relative_to(ROOT)}")


def play(art):
    import tkinter as tk
    from PIL import ImageTk

    window = tk.Tk()
    window.title("RelicEscape B1 | A/D 또는 ←/→ 이동 · E 조사 · R 다시 시작")
    window.resizable(False, False)
    canvas = tk.Canvas(window, width=SIZE[0], height=SIZE[1], highlightthickness=0)
    canvas.pack()
    surface = canvas.create_image(0, 0, anchor="nw")
    keys = set()
    preview = Preview()
    last = time.monotonic()

    def pressed(event):
        nonlocal preview
        key = event.keysym.lower()
        if key in keys:
            return
        keys.add(key)
        if key == "e":
            preview.interact()
        elif key == "r":
            preview = Preview()
        elif key == "escape":
            window.destroy()

    def update():
        nonlocal last
        now = time.monotonic()
        direction = int(bool(keys & {"d", "right"})) - int(bool(keys & {"a", "left"}))
        preview.advance(min(now - last, .060), direction)
        last = now
        canvas.image = ImageTk.PhotoImage(art.render(preview))
        canvas.itemconfigure(surface, image=canvas.image)
        window.after(16, update)

    window.bind("<KeyPress>", pressed)
    window.bind("<KeyRelease>", lambda event: keys.discard(event.keysym.lower()))
    window.bind("<FocusOut>", lambda _: keys.clear())
    canvas.focus_set()
    update()
    window.mainloop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gif", action="store_true", help="render the same interaction sequence to a GIF")
    options = parser.parse_args()
    art = Art()
    if options.gif:
        write_gif(art)
    else:
        play(art)

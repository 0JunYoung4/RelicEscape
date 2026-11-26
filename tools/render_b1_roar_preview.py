"""Render the B1 roar layers in the existing nest concept (no gameplay hooks)."""

from bisect import bisect_right
import json
from math import pi, sin

from PIL import Image, ImageOps

from tools.preview_b1_intro import ART, GROUND, PLAYER_ART, ROOT, SHELL_X, SIZE, load_actor


ROAR_ART = ART.parent / "roar-v1"
OUTPUT = ROAR_ART / "boss-roar-preview.gif"
FPS = 24
FRAME_COUNT = 48
RELEASE_FRAME = 18
PLAYER_X = 1388
PLATFORMS = (
    ("platform-outer-left.png", (142, 226), (449, 164)),
    ("platform-inner-left.png", (724, 164), (257, 91)),
    ("platform-inner-right.png", (1204, 168), (257, 89)),
    ("platform-outer-right.png", (1588, 210), (449, 153)),
)


def rgba(path):
    with Image.open(path) as source:
        return source.convert("RGBA")


def resize(image, size):
    return image.resize(size, Image.Resampling.LANCZOS)


def _lay_terrain(back, terrain):
    gate = rgba(ART / "right-passage-gate.png")
    back.alpha_composite(gate, (2055, GROUND - gate.height))
    back.alpha_composite(terrain)

    rails = ROOT / "assets/sprites/rail"
    track = rgba(rails / "relic-track-blue-v4.png").transpose(Image.Transpose.ROTATE_90)
    track = resize(track, (12, GROUND - 242))
    carriage = rgba(rails / "relic-carriage-v2.png")
    for center in (387, 1795):
        back.alpha_composite(track, (center - track.width // 2, 242))
        back.alpha_composite(carriage, (center - carriage.width // 2, 389))

    for name, position, dimensions in PLATFORMS:
        platform = rgba(ART.parent / "ceiling-rock-v2" / name)
        back.alpha_composite(resize(platform.crop(platform.getbbox()), dimensions), position)

    scrap = rgba(ROOT / "assets/terrain/moss-grotto-floor-decor/split-slate-scrap.png")
    scrap = scrap.crop(scrap.getbbox())
    back.alpha_composite(resize(scrap, (57, 26)), (686, 675))
    back.alpha_composite(ImageOps.mirror(resize(scrap, (47, 22))), (1480, 679))
    return back


def stage_terrain():
    """Keep the tunnel, rock floor, ledges, rails and rubble on one plane."""
    terrain = rgba(ART / "terrain.png")
    return _lay_terrain(Image.new("RGBA", terrain.size), terrain)


def stage():
    """Build the original room plate for the first roar comparison."""
    back = _lay_terrain(rgba(ART / "background.png"), rgba(ART / "terrain.png"))
    return back, rgba(ART / "foreground.png")


def sample_layer(filename, expected_size):
    """Recover the common timeline even when WebP combines identical frames."""
    with Image.open(ROAR_ART / filename) as source:
        if source.size != expected_size:
            raise ValueError(f"{filename}: expected {expected_size}, got {source.size}")
        frames = []
        ends_ms = []
        for index in range(source.n_frames):
            source.seek(index)
            frames.append(source.convert("RGBA"))
            ends_ms.append((ends_ms[-1] if ends_ms else 0) + source.info["duration"])
    runtime = FRAME_COUNT * 1000 / FPS
    if not runtime - 500 / FPS < ends_ms[-1] < runtime + 1000 / FPS:
        raise ValueError(f"{filename}: expected {runtime:.0f} ms, got {ends_ms[-1]} ms")
    return tuple(frames[bisect_right(ends_ms, (i + .5) * 1000 / FPS)] for i in range(FRAME_COUNT))


def mirrored(pose, anchor_x, anchor_y):
    return ImageOps.mirror(pose), pose.width - anchor_x, anchor_y


def player_poses():
    _, idle = load_actor()
    metadata = json.loads((PLAYER_ART / "crouch-right-fast-v1.json").read_text(encoding="utf-8"))
    atlas = rgba(PLAYER_ART / metadata["image"])
    brace = []
    scale = .253
    for definition in metadata["frames"]:
        x, y, width, height = (definition[key] for key in ("x", "y", "width", "height"))
        pose = atlas.crop((x, y, x + width, y + height))
        pose = resize(pose, (round(width * scale), round(height * scale)))
        anchor_x, anchor_y = (round(value * scale) for value in definition["foot_anchor"])
        brace.append(mirrored(pose, anchor_x, anchor_y))
    return mirrored(*idle), brace


def draw_player(frame, index, idle, brace):
    since_release = index - RELEASE_FRAME
    if 2 <= since_release < 16:
        pose, anchor_x, anchor_y = brace[min(since_release - 2, 15 - since_release, 3)]
    else:
        pose, anchor_x, anchor_y = idle
    frame.alpha_composite(pose, (PLAYER_X - anchor_x, GROUND - anchor_y))


def camera_box(index):
    elapsed = index - RELEASE_FRAME
    pullback = sin(pi * min(1, max(0, (elapsed + 2) / 28))) ** 2
    shake = 3.2 * max(0, 1 - elapsed / 13) ** 2 if elapsed >= 0 else 0
    width = 1280 + 52 * pullback
    height = width * SIZE[1] / SIZE[0]
    center_x = 1168 + shake * sin(elapsed * 2.2)
    center_y = 397 + shake * sin(elapsed * 2.7 + .7)
    return center_x - width / 2, center_y - height / 2, center_x + width / 2, center_y + height / 2


def write_preview():
    base, foreground = stage()
    boss = sample_layer("boss-roar-animation.webp", (600, 420))
    waves = sample_layer("roar-wave-animation.webp", (900, 440))
    debris = sample_layer("roar-debris-animation.webp", (900, 440))
    idle, brace = player_poses()

    frames = []
    for index, (boss_pose, wave, grit) in enumerate(zip(boss, waves, debris)):
        scene = base.copy()
        scene.alpha_composite(wave, (SHELL_X - 450, GROUND - 420))
        scene.alpha_composite(boss_pose, (SHELL_X - 300, GROUND - 400))
        scene.alpha_composite(grit, (SHELL_X - 450, GROUND - 420))
        draw_player(scene, index, idle, brace)
        scene.alpha_composite(foreground)
        frames.append(scene.resize(SIZE, Image.Resampling.LANCZOS, box=camera_box(index)).convert("RGB"))

    # Quantize all frames against one palette so the cavern stays visually steady.
    sample_indices = (0, 8, 15, 18, 21, 24, 28, 35, 47)
    samples = Image.new("RGB", (960, 540))
    for slot, index in enumerate(sample_indices):
        samples.paste(frames[index].resize((320, 180), Image.Resampling.BOX), (320 * (slot % 3), 180 * (slot // 3)))
    palette = samples.quantize(colors=256)
    packed = [frame.quantize(palette=palette, dither=Image.Dither.NONE) for frame in frames]
    ticks = [round(index * 100 / FPS) for index in range(FRAME_COUNT + 1)]
    durations_ms = [10 * (end - start) for start, end in zip(ticks, ticks[1:])]
    durations_ms[-1] += 340  # Keep the final face-off visible before the GIF loops.
    packed[0].save(OUTPUT, save_all=True, append_images=packed[1:], duration=durations_ms, loop=0, optimize=True)
    print(f"Saved {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    write_preview()

"""Animate the existing B1 sprite without replacing its face or stone plates."""

from math import pi, sin
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "assets/concepts/b1-hermit-crab"
SIZE = (600, 420)
GROUND_ANCHOR = (300, 400)
FPS = 24
FRAME_COUNT = 48
SHEET_COLUMNS = 8


def smooth(value):
    value = max(0.0, min(1.0, value))
    return value * value * (3 - 2 * value)


def between(frame, start, end):
    return smooth((frame - start) / (end - start))


def pose_amounts(frame):
    inhale = between(frame, 0, 10) * (1 - between(frame, 11, 17))
    lift = between(frame, 11, 18) * (1 - between(frame, 25, 41))
    spread = between(frame, 9, 18) * (1 - between(frame, 24, 44))
    rattle = sin((frame - 16) * 1.45) * lift
    recoil = 0.0
    if frame > 30:
        recoil = sin((frame - 30) / 17 * 2 * pi) * (1 - between(frame, 30, 47))
    return inhale, lift, spread, rattle, recoil


def base_art():
    with Image.open(ART / "assembled-upright-v6.png") as source:
        asset = source.convert("RGBA").resize((540, 350), Image.Resampling.LANCZOS)
    alpha = asset.getchannel("A").point(lambda value: 255 if value >= 128 else 0)
    feet = alpha.getbbox()[3]
    base = Image.new("RGBA", SIZE)
    base.alpha_composite(asset, (GROUND_ANCHOR[0] - asset.width // 2, GROUND_ANCHOR[1] - feet))
    return base


def distort(source, inhale, lift, spread, rattle, recoil):
    """Raise the brow and claws with a continuous mesh while keeping the feet planted."""
    if max(inhale, lift, spread, abs(rattle), abs(recoil)) < 0.00001:
        return source.copy()

    def offsets(x, y):
        feet_lock = 1 - smooth((y - 339) / 60)
        shell_weight = 1 - smooth((y - 270) / 114)
        tilt_weight = 1 - smooth((y - 50) / 254)
        palm_height = 1 - smooth(abs(y - 277) / 118)
        left_palm = (1 - smooth(abs(x - 110) / 162)) * palm_height
        right_palm = (1 - smooth(abs(x - 493) / 162)) * palm_height
        inner_hook = max(1 - smooth(abs(x - 182) / 45), 1 - smooth(abs(x - 413) / 45))
        upper_hook = 1 - smooth(abs(y - 303) / 24)
        lower_hook = 1 - smooth(abs(y - 342) / 24)
        gape = inner_hook * (5 * lower_hook - 7 * upper_hook) * spread
        dx = feet_lock * ((right_palm - left_palm) * (40 * spread - 12 * inhale)
                          + tilt_weight * (-13 * lift + 5 * inhale)
                          + shell_weight * (2.4 * rattle))
        dy = feet_lock * (shell_weight * (25 * inhale - 37 * lift + 6 * recoil)
                          - left_palm * (35 * spread + 4 * rattle)
                          - right_palm * (31 * spread - 3 * rattle)
                          + tilt_weight * (5 * lift + 2 * rattle) * (x - GROUND_ANCHOR[0]) / 160
                          + gape)
        return dx, dy

    # Invert the smooth field at lattice vertices with damping near the shoulders.
    def original_point(x, y):
        sx, sy = x, y
        for _ in range(8):
            dx, dy = offsets(sx, sy)
            sx += (x - dx - sx) * 0.62
            sy += (y - dy - sy) * 0.62
        return sx, sy

    xs = [*range(0, SIZE[0], 16), SIZE[0]]
    ys = [*range(0, SIZE[1], 16), SIZE[1]]
    grid = [[original_point(x, y) for x in xs] for y in ys]
    mesh = []
    for row, (top, bottom) in enumerate(zip(ys, ys[1:])):
        for col, (left, right) in enumerate(zip(xs, xs[1:])):
            corners = (*grid[row][col], *grid[row + 1][col],
                       *grid[row + 1][col + 1], *grid[row][col + 1])
            mesh.append(((left, top, right, bottom), corners))
    return source.transform(SIZE, Image.Transform.MESH, mesh, Image.Resampling.BICUBIC)


def render_frames():
    base = base_art()
    return [distort(base, *pose_amounts(frame)) for frame in range(FRAME_COUNT)]


def save_sheet(frames, path):
    width, height = SIZE
    rows = (FRAME_COUNT + SHEET_COLUMNS - 1) // SHEET_COLUMNS
    sheet = Image.new("RGBA", (width * SHEET_COLUMNS, height * rows))
    for index, frame in enumerate(frames):
        sheet.paste(frame, (index % SHEET_COLUMNS * width, index // SHEET_COLUMNS * height))
    sheet.save(path, format="PNG", compress_level=4)


def main():
    output = ART / "roar-v1"
    output.mkdir(exist_ok=True)
    frames = render_frames()
    duration = [round(1000 * (index + 1) / FPS) - round(1000 * index / FPS)
                for index in range(FRAME_COUNT)]
    webp = output / "boss-roar-animation.webp"
    temp_webp = webp.with_suffix(".webp.tmp")
    frames[0].save(temp_webp, format="WEBP", save_all=True, append_images=frames[1:],
                   duration=duration, loop=0, lossless=True, quality=70, method=2)
    temp_webp.replace(webp)

    sheet = output / "boss-roar-sheet.png"
    temp_sheet = sheet.with_suffix(".png.tmp")
    save_sheet(frames, temp_sheet)
    temp_sheet.replace(sheet)


if __name__ == "__main__":
    main()

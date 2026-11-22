"""Blue square-pixel dissolution shared by enemy death animations."""

from pico2d import pico2d as pico


COLORS = ((40, 125, 255), (65, 170, 255), (100, 205, 255), (155, 230, 255))


def draw_blue_pixels(animation, camera, x, floor_y, facing, elapsed, *, flipped=False):
    frame = animation.frames[-1]
    left, top, right, bottom = frame["body_bounds"]
    for column, row, source_x, source_y, width, height in frame["pixel_cells"]:
        seed = ((column * 73 + row * 151 + 17) % 251) / 250
        age = max(0, elapsed - .09 * seed)
        if elapsed >= .09 * seed + .43 + .20 * seed:
            continue
        local_x = (source_x + width / 2 - (left + right) / 2) * animation.scale
        local_y = ((source_y + height / 2 - top) if flipped
                   else (bottom - source_y - height / 2)) * animation.scale
        spread = local_x / max(1, (right - left) * animation.scale / 2)
        vx = facing * (spread * 110 + (seed - .5) * 48)
        vy = 105 + seed * 130
        px = x + facing * local_x + vx * age
        py = floor_y + local_y + vy * age - 140 * age ** 2
        screen_x, screen_y = camera.world_to_screen(px, py)
        half_w = width * animation.scale * camera.zoom / 2
        half_h = height * animation.scale * camera.zoom / 2
        color = COLORS[(column * 7 + row * 11) % len(COLORS)]
        pico.draw_rectangle(round(screen_x - half_w), round(screen_y - half_h),
                            round(screen_x + half_w) - 1, round(screen_y + half_h) - 1,
                            *color, filled=True)

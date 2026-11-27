"""SDL drawing for the B1 ceiling rock and its authored shatter sequence."""

import json

from PIL import Image

from tools.b1_room_art import _draw_plate, _green_grade, rgba_texture
from tools.preview_b1_intro import ART


class B1BoulderImpact:
    def __init__(self, resting_texture):
        self.resting_texture = resting_texture
        assets = ART.parent / "ceiling-rock-v2"
        spec = json.loads((assets / "ceiling-boulder-shatter-sheet-v2.json").read_text(encoding="utf-8"))
        width, height = spec["frame_size"]
        self.fps = spec["fps"]
        self.duration = spec["frame_count"] / self.fps
        self.frames = [None]

        with Image.open(assets / spec["image"]) as atlas:
            intact = atlas.crop((0, 0, width, height)).convert("RGBA")
            left, top, right, bottom = intact.getbbox()
            scale = self.resting_texture.h / (bottom - top)
            center = (left + right) / 2
            for index in range(1, spec["frame_count"]):
                row, column = divmod(index, spec["columns"])
                x, y = column * width, row * height
                frame = atlas.crop((x, y, x + width, y + height)).convert("RGBA")
                bounds = frame.getbbox()
                if bounds is None:
                    self.frames.append(None)
                    continue
                frame = _green_grade(frame.crop(bounds), (6, 19, 23), (151, 184, 162), .37)
                # Offsets share the intact frame's center and contact edge.
                offset_x = (bounds[0] - center) * scale
                offset_y = (bounds[1] - bottom) * scale
                self.frames.append((rgba_texture(frame), offset_x, offset_y,
                                    (frame.width * scale, frame.height * scale)))

    def draw_fall(self, camera, center_x, top):
        image = self.resting_texture
        _draw_plate(camera, image, center_x - image.w / 2, top)

    def draw_shatter(self, camera, center_x, impact_y, elapsed_seconds):
        if not 0 <= elapsed_seconds < self.duration:
            return
        frame = int(elapsed_seconds * self.fps)
        if frame == 0:
            # The first contact holds the same lit rock that was falling.
            self.draw_fall(camera, center_x, impact_y - self.resting_texture.h)
            return
        plate = self.frames[frame]
        if plate is not None:
            image, x, y, size = plate
            _draw_plate(camera, image, center_x + x, impact_y + y, size=size)

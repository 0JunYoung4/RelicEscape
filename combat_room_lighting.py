"""World-space backlighting for the first combat room."""

from dataclasses import dataclass
from functools import lru_cache
from math import exp, sin


@dataclass(frozen=True)
class _Shaft:
    mouth_x: int
    floor_x: int
    mouth_radius: int
    floor_radius: int
    color: tuple[int, int, int]
    opacity: int

    def center(self, height):
        return self.floor_x + (self.mouth_x - self.floor_x) * height

    def radius(self, height):
        return self.floor_radius + (self.mouth_radius - self.floor_radius) * height


_SHAFTS = (
    _Shaft(740, 480, 140, 210, (151, 232, 201), 170),
    _Shaft(1605, 1270, 151, 223, (141, 226, 198), 186),
)
_ROWS = (
    (0.00, 0.00), (.045, .13), (.15, .34), (.28, .53), (.40, .64),
    (.53, .70), (.65, .77), (.77, .84), (.87, .90), (.95, .98), (1.00, 1.00),
)
_COLUMNS = tuple(i / 9 for i in range(-9, 10))
_RIM_COLOR = (204, 238, 212)
_FOREGROUND_POOLS = ((350, -52, 148, 101), (1540, -73, 185, 110))


@lru_cache(maxsize=8)
def _shaft_mesh(shaft, ceiling):
    """Feather the outer shaft and vary narrow streaks within the broader pool of air."""
    points, colors, faces = [], [], []
    columns = len(_COLUMNS)
    for row, (height, strength) in enumerate(_ROWS):
        radius = shaft.radius(height)
        center = shaft.center(height)
        for col, u in enumerate(_COLUMNS):
            cloud = .66 * exp(-5.6 * u * u)
            streak = .34 * exp(-26 * (u + .22 - .065 * sin(height * 8)) ** 2)
            fringe = .14 * exp(-42 * (u - .34) ** 2)
            alpha = round(shaft.opacity * strength * (1 - u * u) * (cloud + streak + fringe))
            points.append((center + radius * u, height * ceiling))
            colors.append((*shaft.color, alpha))
            if row and col:
                i = row * columns + col
                faces.extend((i - columns - 1, i - columns, i - 1, i - columns, i, i - 1))
    return points, colors, faces


class CombatRoomLighting:
    def __init__(self, scenery):
        self.scenery = scenery

    def draw_rear(self, camera, ceiling):
        """Backlight the far atmosphere before the ruin and terrain silhouettes occlude it."""
        with self.scenery.alpha_geometry():
            for shaft in _SHAFTS:
                self.scenery.geometry(camera, *_shaft_mesh(shaft, ceiling))
                self.scenery.soft_light(camera, (shaft.floor_x, 49), (165, 44), shaft.color, 22)

    def draw_midair(self, camera, ceiling):
        """Each shaft scatters across the face of its ruin and into its mossy footing."""
        with self.scenery.alpha_geometry():
            for shaft, height in zip(_SHAFTS, (.37, .29)):
                self.scenery.soft_light(camera, (shaft.center(height), ceiling * height),
                                        (118, 170), shaft.color, 30)
                self.scenery.soft_light(camera, (shaft.center(.13), ceiling * .13),
                                        (132, 104), shaft.color, 22)

    def draw_floor_bounce(self, camera, ceiling, *, banks=None):
        """The localized reflection hugs the floor and stays above the exit shaft."""
        banks = ((0, self.scenery.room_width),) if banks is None else banks
        with self.scenery.alpha_geometry():
            for left, right in banks:
                with self.scenery.room_clip(camera, left, right, ceiling) as visible:
                    if visible:
                        for shaft in _SHAFTS:
                            self.scenery.soft_light(camera, (shaft.floor_x, 4), (164, 25), shaft.color, 51)

    def draw_ledge_bounce(self, camera, ceiling, platforms):
        """Catch a little green light along each exposed stone lip."""
        with self.scenery.alpha_geometry():
            for left, _, right, top in platforms:
                with self.scenery.room_clip(camera, left, right, top + 2, bottom=top - 8) as visible:
                    if visible:
                        for shaft in _SHAFTS:
                            height = top / ceiling
                            self.scenery.soft_light(camera, (shaft.center(height), top - 1),
                                                    (shaft.radius(height) * .91, 8), shaft.color, 40)

    def draw_foreground_air(self, camera):
        """A little reflected light scatters in front of the leaves below the walk line."""
        with self.scenery.room_clip(camera, 0, self.scenery.room_width, 0, bottom=-190) as visible:
            if visible:
                with self.scenery.alpha_geometry():
                    for (x, y, rx, ry), shaft in zip(_FOREGROUND_POOLS, _SHAFTS):
                        spill_x = shaft.floor_x + (x - shaft.floor_x) * .45
                        self.scenery.soft_light(camera, (spill_x, -22), (rx, ry * .38), shaft.color, 27)
                        self.scenery.soft_light(camera, (x, y + 12), (rx * .77, ry * .82), shaft.color, 55)

    def surface_tint(self, x, y, ceiling, tint, strength=1.0):
        """Light airborne and floor vegetation close to either shaft's footprint."""
        height = min(1.0, max(0.0, y / ceiling))
        exposure = max(
            exp(-3.2 * ((x - shaft.center(height)) / shaft.radius(height)) ** 2)
            for shaft in _SHAFTS
        )
        weight = max(0.0, (exposure - .07) / .93) * strength
        return tuple(round(ambient + (lit - ambient) * weight) for ambient, lit in zip(tint, _RIM_COLOR))

    def foreground_tint(self, x, y, tint, strength=1.0):
        """Reflected light reaches only the inner edge of the near leaves and roots."""
        exposure = max(exp(-((x - cx) / rx) ** 2 - ((y - cy) / ry) ** 2)
                       for cx, cy, rx, ry in _FOREGROUND_POOLS)
        weight = strength * exposure
        return tuple(round(ambient + (lit - ambient) * weight)
                     for ambient, lit in zip(tint, (250, 255, 198)))

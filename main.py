"""Run the opening cave or the original movement and device test room."""

from copy import copy
from ctypes import byref, c_int
from dataclasses import dataclass
from math import ceil, cos, exp, hypot, inf, radians, tau
from time import perf_counter, sleep

from PIL import Image
from pico2d import pico2d as pico

import opening_cave
from opening_cutscene import SigilApproach
from health import Health, SpikeBed
from launcher import FLIGHT_RADIUS, Crossbow
from lower_caves import LowerCaves
from lighting import Lighting
from player import ASSET_ROOT, STANDING_HITBOX_HEIGHT, Player
from rail import RAIL_ART_SCALE, RailCarriage, RailSegment, draw_rail
from return_effect import ReturnEffect, ReturnMark, ReturnMarkArt


SCREEN_WIDTH = 960
SCREEN_HEIGHT = 540
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
TITLE_ANIMATION = ASSET_ROOT / "concepts/opening-cave-rune-loop-v4.png"
TITLE_PROMPT = ASSET_ROOT / "ui/title-enter-prompt.png"
TITLE_PROMPT_Y = 52
TITLE_BLINK_PERIOD = 2.6
GROUND_Y = 200
WORLD_WIDTH = 9000
CAMERA_ZOOM = 1 / 3  # Wide view for the relic/device test room.
EXPLORATION_CAMERA_ZOOM = 0.5
CAVE_FLOOR_SCREEN_Y = 130
AIM_CAMERA_ZOOM = 0.26
AIM_CAMERA_LOOKAHEAD = 650
FLIGHT_CAMERA_ZOOM = 0.30
FLIGHT_CAMERA_LOOKAHEAD = 0.20
GROUND_IMAGE = ASSET_ROOT / "terrain/ruins-floor-blue-fissures-v1.png"
GROUND_ART_HEIGHT = 362  # The lower half of the source is stone.
PILLAR_IMAGE = ASSET_ROOT / "terrain/ruins-carved-pillar-v1.png"
PILLAR_FOOT_DEPTH = 6
BACKGROUND_WALL_IMAGES = (
    ASSET_ROOT / "terrain/ruins-background-wall-tile-v2.png",
    ASSET_ROOT / "terrain/ruins-background-wall-left-edge-v1.png",
    ASSET_ROOT / "terrain/ruins-background-wall-right-edge-v1.png",
    ASSET_ROOT / "terrain/ruins-background-wall-outer-corner-v1.png",
)
# Bring the brighter interior bricks into the same slate palette as the edge tiles.
BACKGROUND_WALL_INTERIOR_TINT = (226, 221, 225)
BACKGROUND_WALL_TILE_WIDTH = 360
BACKGROUND_WALL_TILE_HEIGHT = 180
TEST_WALL_LEFT = 6520
TEST_WALL_COLUMNS = 5
TEST_WALL_ROWS = 2
TEST_CEILING_OVERHANG = 80
# The ceiling covers the top of the background wall and has no traversable upper edge.
TEST_CEILING_Y = GROUND_Y + TEST_WALL_ROWS * BACKGROUND_WALL_TILE_HEIGHT - 30
TEST_CEILING = (
    TEST_WALL_LEFT - TEST_CEILING_OVERHANG,
    TEST_CEILING_Y,
    TEST_WALL_LEFT + TEST_WALL_COLUMNS * BACKGROUND_WALL_TILE_WIDTH + TEST_CEILING_OVERHANG,
    inf,
)
TEST_BACKGROUND_WALLS = (
    # Left, columns, rows, joined rows on the left and right, whether the top is exposed.
    (170, 7, 4, 0, 0, True),
    (2920, 10, 5, 0, TEST_WALL_ROWS, True),
    (TEST_WALL_LEFT, TEST_WALL_COLUMNS, TEST_WALL_ROWS, TEST_WALL_ROWS, 0, False),
)
RAIL_IMAGE = ASSET_ROOT / "sprites/rail/relic-track-blue-v4.png"
RAIL_BEND_IMAGE = ASSET_ROOT / "sprites/rail/relic-track-bend-v2.png"
RAIL_CARRIAGE_IMAGE = ASSET_ROOT / "sprites/rail/relic-carriage-v2.png"
RAIL_LOW_Y = GROUND_Y + STANDING_HITBOX_HEIGHT / 2
RAIL_MIDDLE_Y = RAIL_LOW_Y + 216
RAIL_HIGH_Y = RAIL_MIDDLE_Y + 216
TEST_RAIL_PATH = (
    RailSegment((440, RAIL_LOW_Y), (836, RAIL_LOW_Y)),
    RailSegment((836, RAIL_LOW_Y), (1052, RAIL_MIDDLE_Y), center=(836, RAIL_MIDDLE_Y)),
    RailSegment((1052, RAIL_MIDDLE_Y), (1268, RAIL_HIGH_Y), center=(1268, RAIL_MIDDLE_Y)),
    RailSegment((1268, RAIL_HIGH_Y), (1592, RAIL_HIGH_Y)),
    RailSegment((1592, RAIL_HIGH_Y), (1808, RAIL_MIDDLE_Y), center=(1592, RAIL_MIDDLE_Y)),
    RailSegment((1808, RAIL_MIDDLE_Y), (2024, RAIL_LOW_Y), center=(2024, RAIL_MIDDLE_Y)),
    RailSegment((2024, RAIL_LOW_Y), (2420, RAIL_LOW_Y)),
)
RELIC_IMAGE = ASSET_ROOT / "sprites/relic/teleport-relic-v1.png"
RELIC_DEPARTURE_SIGIL = ASSET_ROOT / "sprites/relic/relic-departure-sigil-v3.png"
RELIC_GLOW_IMAGE = ASSET_ROOT / "sprites/relic/relic-blue-glow-v1.png"
RELIC_HOVER_FRAMES = 24
RELIC_HOVER_FPS = 20
RELIC_ARROW_MARGIN = 22
RELIC_ARROW_TOP_MARGIN = 54  # Leave space for the health bar.
CROSSBOW_BASE_IMAGE = ASSET_ROOT / "sprites/launcher/crossbow-base-v1.png"
CROSSBOW_BODY_IMAGE = ASSET_ROOT / "sprites/launcher/crossbow-body-v1.png"
TEST_CROSSBOW_X = 3300
TEST_CROSSBOW_ANGLE = radians(40)
TEST_SPAWN = (400, GROUND_Y, 0.0)
SPIKE_IMAGE = ASSET_ROOT / "sprites/hazards/mutant-floor-spikes-v1.png"
TEST_SPIKE_FLOOR_Y = GROUND_Y - 18
TEST_SPIKE_BED = SpikeBed(3600, 5100, TEST_SPIKE_FLOOR_Y, art_margin=18)
TEST_SPIKES = (TEST_SPIKE_BED,)
TEST_FLOOR = (
    (0, 0, TEST_SPIKE_BED.left, GROUND_Y),
    (TEST_SPIKE_BED.left, 0, TEST_SPIKE_BED.right, TEST_SPIKE_FLOOR_Y),
    (TEST_SPIKE_BED.right, 0, WORLD_WIDTH, GROUND_Y),
)
TEST_LOW_PASSAGE = (7220, GROUND_Y + 106, 7500, inf)
# The wider walls grow outward from the two wall-jump faces.
TEST_PILLARS = (
    (5540, GROUND_Y, 5700, 620),
    (5960, GROUND_Y, 6120, 700),
)
TEST_TERRAIN = (
    *TEST_PILLARS,
    TEST_CEILING,
    TEST_LOW_PASSAGE,
    *TEST_FLOOR,
)


@dataclass(frozen=True)
class RelicAnchor:
    x: float
    feet_y: float
    crouch_time: float
    display_y: float
    placed_at: float


class RelicTravel:
    def __init__(self):
        self.art = ReturnMarkArt(RELIC_DEPARTURE_SIGIL)
        self.reset()

    def reset(self):
        self.anchor = None
        self.effect = ReturnEffect()
        self.marks = []

    def place_or_recall(self, player, now):
        if self.anchor is not None:
            return self.anchor.x, self.anchor.feet_y, self.anchor.crouch_time
        _, bottom, _, top = player.get_hitbox()
        self.anchor = RelicAnchor(player.x, player.y, player.crouch_time, (bottom + top) / 2, now)
        return None

    def return_pose(self, now):
        if self.anchor is None and self.marks and self.marks[-1].can_return(now):
            return self.marks[-1].pose
        return None

    def teleport(self, player, camera, destination, now, *, reclaim):
        if destination is None:
            return False
        departure = copy(player)
        if not player.teleport_to(*destination):
            return False
        if self.marks:
            self.marks[-1].finish(now)
        if reclaim:
            self.anchor = None
            self.marks.append(ReturnMark(departure, now, self.art))
        self.effect.start(departure, player, camera, now)
        return True

    def draw_marks(self, player, camera, target, now):
        self.marks = [mark for mark in self.marks if mark.visible(now)]
        if self.marks and target is None:
            _, bottom, _, top = player.get_hitbox()
            target = camera.world_to_screen(player.x, (bottom + top) / 2)
        for mark in self.marks:
            mark.draw(camera, target, now)


class Camera:
    def __init__(self, screen_width, world_width, zoom=EXPLORATION_CAMERA_ZOOM, *, y=0.0):
        self.screen_width = screen_width
        self.normal_zoom = zoom
        self.zoom = zoom
        self.world_width = world_width
        self.x = 0.0
        self.y = y
        self.transitioning = False

    @property
    def view_width(self):
        return self.screen_width / self.zoom

    def _clamp_x(self, x):
        return max(0.0, min(max(0.0, self.world_width - self.view_width), x))

    def follow(self, player_x):
        self.x = self._clamp_x(player_x - self.view_width / 2)

    def update(self, player_x, delta_time, *, view_target=None, view_zoom=None):
        if view_target is None and not self.transitioning:
            self.follow(player_x)
            return
        target_zoom = self.normal_zoom if view_zoom is None else view_zoom
        target_focus = player_x if view_target is None else view_target
        blend = 1 - exp(-7 * delta_time)
        self.zoom += (target_zoom - self.zoom) * blend
        if abs(self.zoom - target_zoom) < 0.0001:
            self.zoom = target_zoom
        target_x = self._clamp_x(target_focus - self.view_width / 2)
        self.x = self._clamp_x(self.x + (target_x - self.x) * blend)
        if abs(self.x - target_x) < 1:
            self.x = target_x
        self.transitioning = view_target is not None or self.zoom != target_zoom or self.x != target_x

    def world_to_screen(self, x, y):
        return (x - self.x) * self.zoom, (y - self.y) * self.zoom


def read_movement():
    # Read held keys after pumping events. Losing focus immediately stops movement.
    if not pico.SDL_GetKeyboardFocus():
        return 0, False, False
    keys = pico.SDL_GetKeyboardState(None)
    left = bool(keys[pico.SDL_SCANCODE_A] or keys[pico.SDL_SCANCODE_LEFT])
    right = bool(keys[pico.SDL_SCANCODE_D] or keys[pico.SDL_SCANCODE_RIGHT])
    running = bool(keys[pico.SDL_SCANCODE_LSHIFT] or keys[pico.SDL_SCANCODE_RSHIFT])
    crouching = bool(keys[pico.SDL_SCANCODE_S] or keys[pico.SDL_SCANCODE_DOWN])
    return int(right) - int(left), running, crouching


def update_hitbox_visibility(events, visible):
    if not pico.SDL_GetKeyboardFocus():
        return visible
    control_keys = {pico.SDLK_LCTRL: pico.KMOD_LCTRL, pico.SDLK_RCTRL: pico.KMOD_RCTRL}
    control_mask = pico.SDL_GetModState() & pico.KMOD_CTRL
    # SDL's modifier query reflects the end of the event batch. Rewind Ctrl
    # events so a quick Ctrl+H release in the same frame still counts.
    for event in reversed(events):
        flag = control_keys.get(event.key, 0)
        if event.type == pico.SDL_KEYDOWN:
            control_mask &= ~flag
        elif event.type == pico.SDL_KEYUP:
            control_mask |= flag
    for event in events:
        flag = control_keys.get(event.key, 0)
        if event.type == pico.SDL_KEYDOWN:
            control_mask |= flag
            if event.key == pico.SDLK_h and control_mask:
                visible = not visible
        elif event.type == pico.SDL_KEYUP:
            control_mask &= ~flag
    return visible


def shade_stone_depth(left, right, surface_y, deep_y):
    if left >= right or surface_y == deep_y:
        return
    fade_end_y = round(surface_y + (deep_y - surface_y) * 0.8)
    clear = (0, 0, 0, 0)
    black = (0, 0, 0, 255)
    vertices = (pico.SDL_Vertex * 4)(
        pico.SDL_Vertex((left, surface_y), clear),
        pico.SDL_Vertex((right, surface_y), clear),
        pico.SDL_Vertex((left, fade_end_y), black),
        pico.SDL_Vertex((right, fade_end_y), black),
    )
    triangles = (c_int * 6)(0, 1, 2, 1, 3, 2)
    blend_mode = pico.SDL_BlendMode()
    pico.SDL_GetRenderDrawBlendMode(pico.renderer, byref(blend_mode))
    pico.SDL_SetRenderDrawBlendMode(pico.renderer, pico.SDL_BLENDMODE_BLEND)
    try:
        pico.SDL_RenderGeometry(pico.renderer, None, vertices, 4, triangles, 6)
    finally:
        pico.SDL_SetRenderDrawBlendMode(pico.renderer, blend_mode)
    dark_bounds = pico.SDL_Rect(left, min(fade_end_y, deep_y), right - left, abs(deep_y - fade_end_y))
    pico.SDL_SetRenderDrawColor(pico.renderer, *black)
    pico.SDL_RenderFillRect(pico.renderer, dark_bounds)


def draw_stone_strip(image, camera, bounds, *, flip=""):
    left, bottom, right, top = bounds
    tile_width = image.w * (top - bottom) / GROUND_ART_HEIGHT
    first_tile = max(0, int((camera.x - left) // tile_width))
    view_right = min(right, camera.x + camera.view_width)
    last_tile = ceil((view_right - left) / tile_width)
    screen_bottom = round(bottom * camera.zoom)
    screen_top = round(top * camera.zoom)
    for index in range(first_tile, last_tile):
        tile_left = left + index * tile_width
        tile_right = min(right, left + (index + 1) * tile_width)
        # Round shared edges and crop the final tile at the end of the strip.
        screen_left = round((tile_left - camera.x) * camera.zoom)
        screen_right = round((tile_right - camera.x) * camera.zoom)
        source_width = round(image.w * (tile_right - tile_left) / tile_width)
        image.clip_composite_draw(
            0, 0, source_width, GROUND_ART_HEIGHT, 0, flip,
            (screen_left + screen_right) / 2, (screen_bottom + screen_top) / 2,
            screen_right - screen_left, screen_top - screen_bottom,
        )
    surface, deep = (screen_bottom, screen_top) if flip == "v" else (screen_top, screen_bottom)
    shade_stone_depth(
        max(0, round((left - camera.x) * camera.zoom)),
        min(SCREEN_WIDTH, round((right - camera.x) * camera.zoom)),
        SCREEN_HEIGHT - surface, SCREEN_HEIGHT - deep,
    )


def draw_background_wall(tiles, camera, ground_screen_y, layout):
    interior, left_edge, right_edge, corner = tiles
    wall_left, columns, rows, left_join, right_join, exposed_top = layout
    tile_width = BACKGROUND_WALL_TILE_WIDTH
    view_left = camera.x - wall_left
    first_column = max(0, int(view_left // tile_width))
    last_column = min(columns, ceil((view_left + camera.view_width) / tile_width))
    tile_screen_height = BACKGROUND_WALL_TILE_HEIGHT * camera.zoom
    for column in range(first_column, last_column):
        # Round shared tile edges so neighboring tiles stay flush.
        left = round((column * tile_width - view_left) * camera.zoom)
        right = round(((column + 1) * tile_width - view_left) * camera.zoom)
        for row in range(rows):
            bottom = ground_screen_y + round(row * tile_screen_height)
            top = ground_screen_y + round((row + 1) * tile_screen_height)
            is_left = column == 0 and row >= left_join
            is_right = column == columns - 1 and row >= right_join
            width, height = right - left, top - bottom
            if exposed_top and row == rows - 1:
                # Away from the corners, use just the unbroken width of the cap.
                cap_width = corner.w - 20 if is_left or is_right else 1450
                flip = "h" if is_left or (not is_right and column % 2) else ""
                corner.clip_composite_draw(
                    20, 15, cap_width, corner.h - 15, 0, flip,
                    (left + right) / 2, (bottom + top) / 2, width, height,
                )
            elif is_left:
                # Trim export padding from the sides that meet another tile.
                left_edge.clip_draw_to_origin(0, 12, 1750, 864, left, bottom, width, height)
            elif is_right:
                right_edge.clip_draw_to_origin(20, 15, right_edge.w - 20, 864, left, bottom, width, height)
            else:
                interior.draw_to_origin(left, bottom, width, height)


def draw_mount_prompt(camera, position, time):
    x, y = map(round, camera.world_to_screen(*position))
    pulse = (1 - cos(tau * time / 1.2)) / 2
    y += 24 + round(2 * pulse)
    outline = (round(64 + 47 * pulse), round(155 + 66 * pulse), round(188 + 58 * pulse))
    pale_blue = (220, 249, 255)

    pico.draw_line(x - 3, y - 7, x, y - 11, *outline)
    pico.draw_line(x, y - 11, x + 3, y - 7, *outline)
    pico.draw_rectangle(x - 7, y - 7, x + 7, y + 7, *outline, filled=True)
    pico.draw_rectangle(x - 6, y - 6, x + 6, y + 6, 14, 25, 37, filled=True)
    pico.draw_rectangle(x - 3, y - 4, x - 2, y + 4, *pale_blue, filled=True)
    pico.draw_rectangle(x - 1, y + 3, x + 3, y + 4, *pale_blue, filled=True)
    pico.draw_rectangle(x - 1, y, x + 2, y + 1, *pale_blue, filled=True)
    pico.draw_rectangle(x - 1, y - 4, x + 3, y - 3, *pale_blue, filled=True)


def draw_scene(
    player, camera, show_hitboxes=False, *, ground_image=None, background_wall=None, spike_image=None,
    pillar_image=None,
    rail_image=None, rail_bend_image=None, carriage_image=None, carriage_position=None,
    rail_relic_image=None, show_mount_prompt=False, crossbow=None, crossbow_relic_image=None,
    show_crossbow_prompt=False, lighting=None, relic_center=None, return_effect=None, frame_start=0.0,
    health=None,
):
    # Clear the full output, including letterbox bars on non-16:9 monitors.
    pico.SDL_SetRenderDrawColor(pico.renderer, 0, 0, 0, 255)
    pico.SDL_RenderClear(pico.renderer)
    ground_screen_y = round(GROUND_Y * camera.zoom)
    pico.draw_rectangle(
        0, 0, SCREEN_WIDTH - 1, SCREEN_HEIGHT - 1, 22, 26, 34, filled=True,
    )
    if background_wall is not None:
        for layout in TEST_BACKGROUND_WALLS:
            draw_background_wall(background_wall, camera, ground_screen_y, layout)
    for bounds in TEST_FLOOR:
        left, bottom, right, top = bounds
        x1, y1 = map(round, camera.world_to_screen(left, bottom))
        x2, y2 = map(round, camera.world_to_screen(right, top))
        if x1 >= SCREEN_WIDTH or x2 <= 0:
            continue
        if ground_image is None:
            pico.draw_rectangle(x1, y1, x2 - 1, y2 - 1, 38, 44, 52, filled=True)
        else:
            draw_stone_strip(ground_image, camera, bounds)
        if show_hitboxes:
            pico.draw_rectangle(x1, y1, x2 - 1, y2, 76, 220, 220)
    for bounds in player.terrain:
        if bounds in TEST_FLOOR:
            continue
        left, bottom, right, top = bounds
        if right <= camera.x or left >= camera.x + camera.view_width:
            continue
        x1, y1 = camera.world_to_screen(left, bottom)
        if y1 >= SCREEN_HEIGHT:
            continue
        x2, y2 = camera.world_to_screen(right, top)
        if top == inf:
            y2 = SCREEN_HEIGHT - 1
            pico.draw_rectangle(round(x1), round(y1), round(x2) - 1, y2, 0, 0, 0, filled=True)
            if ground_image is not None:
                draw_stone_strip(ground_image, camera, (left, bottom, right, bottom + GROUND_Y), flip="v")
        elif pillar_image is not None and bounds in TEST_PILLARS:
            screen_left, screen_right = round(x1), round(x2)
            foot = round((bottom - PILLAR_FOOT_DEPTH) * camera.zoom)
            pillar_image.draw_to_origin(screen_left, foot, screen_right - screen_left, round(y2) - foot)
        else:
            pico.draw_rectangle(x1, y1, x2, y2, 66, 75, 85, filled=True)
            pico.draw_line(x1, y2, x2, y2, 124, 157, 164)
        if show_hitboxes:
            pico.draw_rectangle(x1, y1, x2, y2, 76, 220, 220)
    for spikes in TEST_SPIKES:
        spikes.draw(spike_image, camera, show_hitboxes)
    if lighting is not None:
        lighting.apply(relic_center)
    if rail_image is not None and rail_bend_image is not None:
        # The track's illuminated path stays readable in the dark.
        draw_rail(rail_image, rail_bend_image, camera, TEST_RAIL_PATH)
    if carriage_position is not None:
        scale = RAIL_ART_SCALE * camera.zoom
        carriage_image.draw(
            *camera.world_to_screen(*carriage_position), carriage_image.w * scale, carriage_image.h * scale,
        )
        if rail_relic_image is not None:
            draw_relic(rail_relic_image, camera, *carriage_position, None)
    if crossbow is not None:
        crossbow.draw(camera, SCREEN_HEIGHT)
        if crossbow.aiming:
            for point in crossbow.trajectory(player.terrain, camera.world_width, ground_y=player.ground_y):
                x, y = map(round, camera.world_to_screen(*point))
                pico.draw_rectangle(x - 1, y - 1, x + 1, y + 1, 120, 216, 247, filled=True)
        if crossbow_relic_image is not None:
            draw_relic(crossbow_relic_image, camera, *crossbow.relic_position, None)
    if return_effect is None or not return_effect.draw(player, camera, frame_start, lighting):
        player.draw(camera, tint=health.hit_tint(frame_start) if health is not None else None)
    if health is not None:
        health.draw_hit(camera, frame_start)
    if show_hitboxes:
        player.draw_hitbox(camera)
    if show_mount_prompt and carriage_position is not None:
        draw_mount_prompt(camera, carriage_position, frame_start)
    if show_crossbow_prompt and crossbow is not None:
        draw_mount_prompt(camera, crossbow.socket_position, frame_start)


def relic_screen_center(camera, x, y, elapsed):
    screen_x, screen_y = camera.world_to_screen(x, y)
    if elapsed is None:
        return screen_x, screen_y
    frame = int(elapsed * RELIC_HOVER_FPS) % RELIC_HOVER_FRAMES
    hover = 1 - cos(tau * frame / RELIC_HOVER_FRAMES)
    return screen_x, screen_y + hover * camera.zoom / CAMERA_ZOOM


def draw_relic(image, camera, x, y, elapsed):
    screen_x, screen_y = relic_screen_center(camera, x, y, elapsed)
    scale = camera.zoom / CAMERA_ZOOM
    width, height = image.w * scale, image.h * scale
    bounds = pico.SDL_FRect(
        screen_x - width / 2, SCREEN_HEIGHT - screen_y - height / 2, width, height,
    )
    pico.SDL_RenderCopyF(pico.renderer, image.texture, None, bounds)


def draw_relic_indicator(relic_center):
    if relic_center is None:
        return
    x, y = relic_center
    if 0 <= x < SCREEN_WIDTH and 0 <= y < SCREEN_HEIGHT:
        return

    center_x, center_y = SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2
    dx, dy = x - center_x, y - center_y
    distance = hypot(dx, dy)
    unit_x, unit_y = dx / distance, dy / distance
    vertical_margin = RELIC_ARROW_TOP_MARGIN if unit_y > 0 else RELIC_ARROW_MARGIN
    # Intersect the direction ray with the inset screen edges.
    edge_distance = min(
        (center_x - RELIC_ARROW_MARGIN) / abs(unit_x) if unit_x else inf,
        (center_y - vertical_margin) / abs(unit_y) if unit_y else inf,
    )
    edge_x = center_x + edge_distance * unit_x
    edge_y = center_y + edge_distance * unit_y

    shape = ((10, 0), (0, 7), (0, 3), (-9, 3), (-9, -3), (0, -3), (0, -7))
    points = [
        (edge_x + forward * unit_x - side * unit_y, edge_y + forward * unit_y + side * unit_x)
        for forward, side in shape
    ]
    vertices = (pico.SDL_Vertex * len(points))(*(
        pico.SDL_Vertex((px, SCREEN_HEIGHT - 1 - py), (128, 231, 255, 255))
        for px, py in points
    ))
    triangles = (c_int * 9)(0, 1, 6, 2, 3, 4, 2, 4, 5)
    pico.SDL_RenderGeometry(pico.renderer, None, vertices, len(vertices), triangles, len(triangles))
    for start, end in zip(points, points[1:] + points[:1]):
        pico.draw_line(*map(round, start), *map(round, end), 11, 32, 45)


def set_fullscreen(enabled):
    flags = pico.SDL_WINDOW_FULLSCREEN_DESKTOP if enabled else 0
    if pico.SDL_SetWindowFullscreen(pico.window, flags) != 0:
        print("Display mode change failed:", pico.SDL_GetError())
    if not enabled:
        pico.SDL_SetWindowSize(pico.window, WINDOW_WIDTH, WINDOW_HEIGHT)
        pico.SDL_SetWindowPosition(pico.window, pico.SDL_WINDOWPOS_CENTERED, pico.SDL_WINDOWPOS_CENTERED)
    return bool(pico.SDL_GetWindowFlags(pico.window) & pico.SDL_WINDOW_FULLSCREEN)


def configure_display():
    # Keep the camera composition consistent across monitor sizes and modes.
    if pico.SDL_RenderSetLogicalSize(pico.renderer, SCREEN_WIDTH, SCREEN_HEIGHT) != 0:
        raise RuntimeError(pico.SDL_GetError())
    pico.SDL_SetWindowSize(pico.window, WINDOW_WIDTH, WINDOW_HEIGHT)
    return set_fullscreen(True)


def quit_requested(events):
    return any(event.type == pico.SDL_QUIT for event in events)


def run_title(fullscreen):
    prompt = pico.load_image(str(TITLE_PROMPT))
    with Image.open(TITLE_ANIMATION) as animation:
        width, height = animation.size
        texture = pico.SDL_CreateTexture(
            pico.renderer, pico.SDL_PIXELFORMAT_RGBA32, pico.SDL_TEXTUREACCESS_STREAMING, width, height,
        )
        if not texture:
            raise RuntimeError(pico.SDL_GetError())
        try:
            if pico.SDL_SetTextureScaleMode(texture, pico.SDL_ScaleModeLinear) != 0:
                raise RuntimeError(pico.SDL_GetError())
            # The exported APNG has a constant frame duration. Decode on demand and reuse one texture.
            frame_duration = animation.info["duration"] / 1000
            frame_count = animation.n_frames
            started_at = perf_counter()
            previous_frame = -1
            while True:
                frame_start = perf_counter()
                events = pico.get_events()
                keys = {event.key for event in events if event.type == pico.SDL_KEYDOWN}
                if quit_requested(events) or pico.SDLK_ESCAPE in keys:
                    return None
                if pico.SDLK_F11 in keys:
                    fullscreen = set_fullscreen(not fullscreen)
                if pico.SDLK_RETURN in keys or pico.SDLK_KP_ENTER in keys:
                    return fullscreen

                elapsed = frame_start - started_at
                frame = int(elapsed / frame_duration) % frame_count
                if frame != previous_frame:
                    animation.seek(frame)
                    pixels = animation.convert("RGBA").tobytes()
                    if pico.SDL_UpdateTexture(texture, None, pixels, width * 4) != 0:
                        raise RuntimeError(pico.SDL_GetError())
                    previous_frame = frame

                pico.SDL_RenderCopy(pico.renderer, texture, None, None)
                pulse = cos(tau * elapsed / TITLE_BLINK_PERIOD)
                alpha = round(255 * max(0, (pulse + 0.55) / 1.55))
                if alpha:
                    pico.SDL_SetTextureAlphaMod(prompt.texture, alpha)
                    prompt.draw(SCREEN_WIDTH / 2, TITLE_PROMPT_Y)
                pico.SDL_SetWindowTitle(pico.window, b"RelicEscape")
                pico.update_canvas()
                sleep(max(0, 1 / 60 - (perf_counter() - frame_start)))
        finally:
            pico.SDL_DestroyTexture(texture)


def run_game(fullscreen):
    ground_image = pico.load_image(str(GROUND_IMAGE))
    pillar_image = pico.load_image(str(PILLAR_IMAGE))
    background_wall = tuple(pico.load_image(str(path)) for path in BACKGROUND_WALL_IMAGES)
    if pico.SDL_SetTextureColorMod(background_wall[0].texture, *BACKGROUND_WALL_INTERIOR_TINT) != 0:
        raise RuntimeError(pico.SDL_GetError())
    spike_image = pico.load_image(str(SPIKE_IMAGE))
    rail_image = pico.load_image(str(RAIL_IMAGE))
    rail_bend_image = pico.load_image(str(RAIL_BEND_IMAGE))
    carriage_image = pico.load_image(str(RAIL_CARRIAGE_IMAGE))
    initial_carriage = RailCarriage(
        TEST_RAIL_PATH, carriage_image.w * RAIL_ART_SCALE, carriage_image.h * RAIL_ART_SCALE,
    )
    initial_crossbow = Crossbow(
        TEST_CROSSBOW_X, GROUND_Y,
        pico.load_image(str(CROSSBOW_BASE_IMAGE)), pico.load_image(str(CROSSBOW_BODY_IMAGE)),
    )
    initial_crossbow.angle = TEST_CROSSBOW_ANGLE
    relic_image = pico.load_image(str(RELIC_IMAGE))
    travel = RelicTravel()
    lighting = Lighting(SCREEN_WIDTH, SCREEN_HEIGHT, RELIC_GLOW_IMAGE)
    carriage = copy(initial_carriage)
    crossbow = copy(initial_crossbow)
    player = Player(
        TEST_SPAWN[0], TEST_SPIKE_FLOOR_Y, WORLD_WIDTH, terrain=TEST_TERRAIN, spawn_y=TEST_SPAWN[1],
    )
    health = Health(TEST_SPAWN)
    camera = Camera(SCREEN_WIDTH, WORLD_WIDTH, CAMERA_ZOOM)
    camera.follow(player.x)
    show_hitboxes = False
    previous_time = perf_counter()

    while True:
        frame_start = perf_counter()
        delta_time = min(frame_start - previous_time, 0.05)
        previous_time = frame_start
        events = pico.get_events()
        if quit_requested(events):
            return None

        pressed_keys = {event.key for event in events if event.type == pico.SDL_KEYDOWN}
        if pico.SDLK_ESCAPE in pressed_keys:
            return fullscreen
        if pico.SDLK_F11 in pressed_keys:
            fullscreen = set_fullscreen(not fullscreen)
        show_hitboxes = update_hitbox_visibility(events, show_hitboxes)
        direction, running, crouching = read_movement()
        manual_restart = pico.SDLK_r in pressed_keys
        if manual_restart or health.ready_to_restart(frame_start):
            player.recover_at(*TEST_SPAWN)
            player.facing = 1
            health = Health(TEST_SPAWN, returned_at=None if manual_restart else frame_start)
            carriage = copy(initial_carriage)
            crossbow = copy(initial_crossbow)
            travel.reset()
            camera = Camera(SCREEN_WIDTH, WORLD_WIDTH, CAMERA_ZOOM)
            camera.follow(player.x)
            pressed_keys.clear()
            direction, running, crouching = 0, False, False
        jump_held = False
        has_focus = bool(pico.SDL_GetKeyboardFocus())
        if has_focus:
            keys = pico.SDL_GetKeyboardState(None)
            jump_held = bool(keys[pico.SDL_SCANCODE_SPACE])
        if not has_focus or health.recovering(frame_start):
            pressed_keys.clear()
        was_aiming = crossbow.aiming
        relic_elsewhere = travel.anchor is not None or crossbow.flight is not None
        carrying_relic = not relic_elsewhere and not carriage.relic_mounted
        use_relic = pico.SDLK_e in pressed_keys
        destination = None
        if crossbow.aiming:
            if use_relic:
                crossbow.aiming = False
            elif has_focus:
                aim_direction = keys[pico.SDL_SCANCODE_RIGHT] - keys[pico.SDL_SCANCODE_LEFT]
                aim_elevation = keys[pico.SDL_SCANCODE_UP] - keys[pico.SDL_SCANCODE_DOWN]
                crossbow.adjust_aim(aim_direction, aim_elevation, delta_time)
                if pico.SDLK_x in pressed_keys:
                    crossbow.fire()
        elif use_relic and carrying_relic and crossbow.can_aim(player):
            crossbow.aiming = True
        elif use_relic and carriage.can_mount(player, relic_elsewhere):
            carriage.relic_mounted = True
        elif use_relic:
            if carriage.relic_mounted:
                x, y = carriage.position
                destination = (x, y - STANDING_HITBOX_HEIGHT / 2, 0.0)
            elif crossbow.flight is not None:
                flight_x = crossbow.flight.x
                floor_y = max(
                    top for left, _, right, top in TEST_FLOOR
                    if left < flight_x + FLIGHT_RADIUS and right > flight_x - FLIGHT_RADIUS
                )
                destination = crossbow.flight.return_pose(floor_y)
            else:
                destination = travel.place_or_recall(player, frame_start)
        elif pico.SDLK_q in pressed_keys and carrying_relic:
            destination = travel.return_pose(frame_start)
        teleported = travel.teleport(player, camera, destination, frame_start, reclaim=use_relic)
        if teleported and use_relic:
            carriage.relic_mounted = False
            crossbow.flight = None
        if was_aiming or crossbow.aiming:
            direction, running, crouching = 0, False, False
            jump_held = False
            pressed_keys.clear()
        if not teleported and not health.recovering(frame_start):
            player.update(
                direction, running, delta_time,
                jump_pressed=pico.SDLK_SPACE in pressed_keys,
                jump_held=jump_held,
                crouch_held=crouching,
                attack_pressed=pico.SDLK_x in pressed_keys,
            )
        if health.check_spikes(player, TEST_SPIKES, frame_start):
            crossbow.aiming = False
            travel.effect = ReturnEffect()
        elif not teleported and not health.recovering(frame_start):
            carriage.check_attack(player)
        if health.return_to_safety(player, frame_start):
            camera.zoom = camera.normal_zoom
            camera.transitioning = False
        carriage.move(delta_time)
        flight = crossbow.flight
        if flight is not None:
            flight.update(delta_time, player.terrain, player.ground_y, WORLD_WIDTH)
        if health.recovering(frame_start):
            camera.update(player.x, delta_time)
        elif crossbow.aiming:
            focus = crossbow.x + crossbow.facing * AIM_CAMERA_LOOKAHEAD
            camera.update(player.x, delta_time, view_target=focus, view_zoom=AIM_CAMERA_ZOOM)
        elif flight is not None and not flight.landed:
            focus = flight.x + flight.vx * FLIGHT_CAMERA_LOOKAHEAD
            camera.update(player.x, delta_time, view_target=focus, view_zoom=FLIGHT_CAMERA_ZOOM)
        else:
            camera.update(player.x, delta_time)
        carriage_position = carriage.position
        crossbow_relic_position = crossbow.relic_position
        relic_anchor = travel.anchor
        relic_elsewhere = relic_anchor is not None or crossbow_relic_position is not None
        can_interact = has_focus and not health.recovering(frame_start)
        show_crossbow_prompt = (
            can_interact and not relic_elsewhere and not carriage.relic_mounted and crossbow.can_aim(player)
        )
        relic_center = None
        if carriage.relic_mounted:
            relic_center = camera.world_to_screen(*carriage_position)
        elif crossbow_relic_position is not None:
            relic_center = camera.world_to_screen(*crossbow_relic_position)
        elif relic_anchor is not None:
            relic_position = (relic_anchor.x, relic_anchor.display_y)
            relic_elapsed = frame_start - relic_anchor.placed_at
            relic_center = relic_screen_center(camera, *relic_position, relic_elapsed)
        draw_scene(
            player, camera, show_hitboxes, ground_image=ground_image, spike_image=spike_image,
            pillar_image=pillar_image,
            background_wall=background_wall, rail_image=rail_image, rail_bend_image=rail_bend_image,
            carriage_image=carriage_image,
            carriage_position=carriage_position,
            rail_relic_image=relic_image if carriage.relic_mounted else None,
            show_mount_prompt=(
                can_interact and not show_crossbow_prompt and carriage.can_mount(player, relic_elsewhere)
            ),
            crossbow=crossbow, crossbow_relic_image=relic_image if crossbow_relic_position is not None else None,
            show_crossbow_prompt=show_crossbow_prompt,
            lighting=lighting, relic_center=relic_center,
            return_effect=travel.effect, frame_start=frame_start, health=health,
        )
        travel.draw_marks(player, camera, relic_center, frame_start)
        if relic_anchor is not None:
            draw_relic(relic_image, camera, *relic_position, relic_elapsed)
        health.draw_hud(SCREEN_HEIGHT, frame_start)
        draw_relic_indicator(relic_center)
        health.draw_blackout(SCREEN_WIDTH, SCREEN_HEIGHT, frame_start)
        pico.SDL_SetWindowTitle(pico.window, b"RelicEscape")
        pico.update_canvas()
        sleep(max(0, 1 / 60 - (perf_counter() - frame_start)))


def run_opening_cave(fullscreen):
    cave = opening_cave.OpeningCave(SCREEN_WIDTH, SCREEN_HEIGHT)
    approach = SigilApproach()
    lower = None
    travel = RelicTravel()
    relic_image = pico.load_image(str(RELIC_IMAGE))
    player = Player(*opening_cave.SPAWN[:2], opening_cave.WORLD_WIDTH, terrain=opening_cave.TERRAIN)
    # Keep the floor low in the frame when zooming in, rather than magnifying the underground rock.
    camera = Camera(
        SCREEN_WIDTH, opening_cave.WORLD_WIDTH,
        y=opening_cave.GROUND_Y - CAVE_FLOOR_SCREEN_Y / EXPLORATION_CAMERA_ZOOM,
    )
    health = Health(opening_cave.SPAWN)
    show_hitboxes = False
    previous_time = perf_counter()
    while True:
        frame_start = perf_counter()
        delta_time = min(frame_start - previous_time, 0.05)
        previous_time = frame_start
        events = pico.get_events()
        if quit_requested(events):
            return None
        pressed_keys = {event.key for event in events if event.type == pico.SDL_KEYDOWN}
        if pico.SDLK_ESCAPE in pressed_keys:
            return fullscreen
        if pico.SDLK_F11 in pressed_keys:
            fullscreen = set_fullscreen(not fullscreen)
        show_hitboxes = update_hitbox_visibility(events, show_hitboxes)
        direction, running, crouching = read_movement()
        has_focus = bool(pico.SDL_GetKeyboardFocus())
        jump_held = False
        if has_focus:
            jump_held = bool(pico.SDL_GetKeyboardState(None)[pico.SDL_SCANCODE_SPACE])
        else:
            pressed_keys.clear()
        if pico.SDLK_r in pressed_keys:
            lower = None
            travel.reset()
            camera.world_width = player.world_width = opening_cave.WORLD_WIDTH
            approach.reset(player)
            camera.zoom = camera.normal_zoom
            player.recover_at(*opening_cave.SPAWN)
            player.facing = 1
            pressed_keys.clear()
            direction, running, crouching = 0, False, False
            jump_held = False
        if lower is None and pico.SDLK_e in pressed_keys:
            approach.start(player)
        if lower is not None:
            use = pico.SDLK_e in pressed_keys
            destination = None
            if lower.has_relic:
                if use:
                    destination = travel.place_or_recall(player, frame_start)
                elif pico.SDLK_q in pressed_keys:
                    destination = travel.return_pose(frame_start)
            if travel.teleport(player, camera, destination, frame_start, reclaim=use):
                camera.follow(player.x)
            else:
                lower.update(player, camera, delta_time, interact=use and not lower.has_relic,
                             direction=direction, running=running, jump_pressed=pico.SDLK_SPACE in pressed_keys,
                             jump_held=jump_held, crouching=crouching, attack_pressed=pico.SDLK_x in pressed_keys)
            lower.update_pillbugs(player, delta_time)
        elif approach.active:
            approach.update(player, delta_time)
            if approach.stood_up:
                lower = LowerCaves(cave)
                lower.enter(player, camera)
        else:
            player.update(
                direction, running, delta_time,
                jump_pressed=pico.SDLK_SPACE in pressed_keys, jump_held=jump_held,
                crouch_held=crouching, attack_pressed=pico.SDLK_x in pressed_keys,
            )
        shaft_cut = approach.phase in ("descent", "impact")
        relic_center = None
        if lower is not None:
            lower.draw(camera)
            relic = lower.relic_position(player)
            if relic is not None:
                draw_relic(relic_image, camera, *relic, frame_start)
        elif shaft_cut:
            cave.draw_descent(camera, player)
        else:
            camera.follow(player.x)
            shake_x, shake_y = approach.shake()
            camera.x += shake_x / camera.zoom
            camera.y = opening_cave.GROUND_Y - (CAVE_FLOOR_SCREEN_Y + shake_y) / camera.zoom
            cave.draw(camera, show_hitboxes=show_hitboxes, sigil_light=approach.sigil_light,
                      collapse_time=approach.collapse_time)
            shade_stone_depth(
                0, SCREEN_WIDTH, SCREEN_HEIGHT - round(CAVE_FLOOR_SCREEN_Y + shake_y), SCREEN_HEIGHT,
            )
        if lower is not None:
            if not travel.effect.draw(player, camera, frame_start, None):
                player.draw(camera)
            if travel.anchor is not None:
                anchor = travel.anchor
                elapsed = frame_start - anchor.placed_at
                relic_center = relic_screen_center(camera, anchor.x, anchor.display_y, elapsed)
                draw_relic(relic_image, camera, anchor.x, anchor.display_y, elapsed)
            travel.draw_marks(player, camera, relic_center, frame_start)
            lower.draw_foreground(camera)
            lower.draw_attack_hint(player)
        else:
            if not approach.draw(player, camera):
                player.draw(camera)
            if not shaft_cut:
                cave.draw_foreground(camera)
        if show_hitboxes:
            player.draw_hitbox(camera)
        if lower is not None and has_focus and lower.target(player) is not None:
            draw_mount_prompt(camera, (lower.target(player), STANDING_HITBOX_HEIGHT), frame_start)
        elif lower is None and has_focus and approach.can_start(player):
            draw_mount_prompt(camera, (player.x, player.y + STANDING_HITBOX_HEIGHT), frame_start)
        health.draw_hud(SCREEN_HEIGHT, frame_start)
        draw_relic_indicator(relic_center)
        pico.SDL_SetWindowTitle(pico.window, b"RelicEscape")
        pico.update_canvas()
        sleep(max(0, 1 / 60 - (perf_counter() - frame_start)))


def main(*, test_room=False):
    pico.SDL_SetHint(pico.SDL_HINT_RENDER_SCALE_QUALITY, b"0")
    pico.open_canvas(SCREEN_WIDTH, SCREEN_HEIGHT)
    try:
        fullscreen = configure_display()
        while fullscreen is not None:
            fullscreen = run_title(fullscreen)
            if fullscreen is not None:
                fullscreen = run_game(fullscreen) if test_room else run_opening_cave(fullscreen)
    finally:
        pico.close_canvas()


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser(description="RelicEscape")
    parser.add_argument("--test-room", action="store_true", help="Start the original movement/device test room")
    main(test_room=parser.parse_args().test_room)

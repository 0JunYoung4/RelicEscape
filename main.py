"""Run the first RelicEscape movement prototype."""

from copy import copy
from ctypes import byref, c_float, c_int
from dataclasses import dataclass
from math import ceil, cos, exp, inf, tau
from time import perf_counter, sleep

from pico2d import pico2d as pico

from launcher import Crossbow
from lighting import Lighting
from player import ASSET_ROOT, STANDING_HITBOX_HEIGHT, Player
from rail import RAIL_ART_SCALE, RailCarriage, RailSegment, draw_rail
from return_effect import ReturnEffect


SCREEN_WIDTH = 960
SCREEN_HEIGHT = 540
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
GROUND_Y = 200
WORLD_WIDTH = 6400
CAMERA_ZOOM = 1 / 3
AIM_CAMERA_ZOOM = 0.26
FLIGHT_CAMERA_ZOOM = 0.30
FLIGHT_CAMERA_LOOKAHEAD = 0.20
GROUND_IMAGE = ASSET_ROOT / "terrain/ruins-floor-blue-fissures-v1.png"
GROUND_ART_HEIGHT = 362  # The lower half of the source is stone.
BACKGROUND_WALL_IMAGE = ASSET_ROOT / "terrain/ruins-background-wall-tile-v2.png"
BACKGROUND_WALL_TILE_WIDTH = 360
BACKGROUND_WALL_TILE_HEIGHT = 180
TEST_WALL_LEFT = 4120
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
    (170, 7, 4),
    (TEST_WALL_LEFT, TEST_WALL_COLUMNS, TEST_WALL_ROWS),
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
RELIC_GLOW_IMAGE = ASSET_ROOT / "sprites/relic/relic-blue-glow-v1.png"
RELIC_HOVER_FRAMES = 24
RELIC_HOVER_FPS = 20
CROSSBOW_BASE_IMAGE = ASSET_ROOT / "sprites/launcher/crossbow-base-v1.png"
CROSSBOW_BODY_IMAGE = ASSET_ROOT / "sprites/launcher/crossbow-body-v1.png"
TEST_CROSSBOW_X = 215
# The step, wall jumps, exit platform, and passage follow the rail area.
TEST_TERRAIN = (
    (2920, 200, 3080, 320),
    (3220, 200, 3300, 620),
    (3560, 200, 3640, 700),
    (3780, 460, 4040, 500),
    TEST_CEILING,
)


@dataclass(frozen=True)
class RelicAnchor:
    x: float
    feet_y: float
    crouch_time: float
    display_y: float
    placed_at: float


class Camera:
    def __init__(self, screen_width, world_width, zoom):
        self.screen_width = screen_width
        self.normal_zoom = zoom
        self.zoom = zoom
        self.world_width = world_width
        self.x = 0.0
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
        return (x - self.x) * self.zoom, y * self.zoom


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


def mouse_world_position(camera):
    window_x, window_y = c_int(), c_int()
    pico.SDL_GetMouseState(byref(window_x), byref(window_y))
    logical_x, logical_y = c_float(), c_float()
    pico.SDL_RenderWindowToLogical(
        pico.renderer, window_x.value, window_y.value, byref(logical_x), byref(logical_y),
    )
    return camera.x + logical_x.value / camera.zoom, (SCREEN_HEIGHT - logical_y.value) / camera.zoom


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


def draw_background_wall(image, camera, ground_screen_y, layout):
    wall_left, columns, rows = layout
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
            image.draw_to_origin(left, bottom, right - left, top - bottom)


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


def draw_scene(
    player, camera, show_hitboxes=False, *, ground_image=None, background_wall=None,
    rail_image=None, rail_bend_image=None, carriage_image=None, carriage_position=None,
    rail_relic_image=None, show_mount_prompt=False, crossbow=None, crossbow_relic_image=None,
    show_crossbow_prompt=False, lighting=None, relic_center=None, return_effect=None, frame_start=0.0,
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
    pico.draw_rectangle(
        0, 0, SCREEN_WIDTH - 1, ground_screen_y - 1, 38, 44, 52, filled=True,
    )
    if ground_image is not None:
        draw_stone_strip(ground_image, camera, (0, 0, camera.world_width, GROUND_Y))
    if show_hitboxes:
        pico.draw_line(0, ground_screen_y, SCREEN_WIDTH - 1, ground_screen_y, 76, 220, 220)
    for bounds in player.terrain:
        left, bottom, right, top = bounds
        if right <= camera.x or left >= camera.x + camera.view_width:
            continue
        x1, y1 = camera.world_to_screen(left, bottom)
        if y1 >= SCREEN_HEIGHT:
            continue
        x2, y2 = camera.world_to_screen(right, top)
        if bounds == TEST_CEILING:
            y2 = SCREEN_HEIGHT - 1
            pico.draw_rectangle(round(x1), round(y1), round(x2) - 1, y2, 0, 0, 0, filled=True)
            if ground_image is not None:
                draw_stone_strip(ground_image, camera, (left, bottom, right, bottom + GROUND_Y), flip="v")
        else:
            pico.draw_rectangle(x1, y1, x2, y2, 66, 75, 85, filled=True)
            pico.draw_line(x1, y2, x2, y2, 124, 157, 164)
        if show_hitboxes:
            pico.draw_rectangle(x1, y1, x2, y2, 76, 220, 220)
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
            for point in crossbow.trajectory(player.terrain, camera.world_width):
                x, y = map(round, camera.world_to_screen(*point))
                pico.draw_rectangle(x - 1, y - 1, x + 1, y + 1, 120, 216, 247, filled=True)
        if crossbow_relic_image is not None:
            draw_relic(crossbow_relic_image, camera, *crossbow.relic_position, None)
    if return_effect is None or not return_effect.draw(player, camera, frame_start, lighting):
        player.draw(camera)
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


def main():
    pico.SDL_SetHint(pico.SDL_HINT_RENDER_SCALE_QUALITY, b"0")
    pico.open_canvas(SCREEN_WIDTH, SCREEN_HEIGHT)
    lighting = None
    try:
        fullscreen = configure_display()
        ground_image = pico.load_image(str(GROUND_IMAGE))
        background_wall = pico.load_image(str(BACKGROUND_WALL_IMAGE))
        rail_image = pico.load_image(str(RAIL_IMAGE))
        rail_bend_image = pico.load_image(str(RAIL_BEND_IMAGE))
        carriage_image = pico.load_image(str(RAIL_CARRIAGE_IMAGE))
        carriage = RailCarriage(
            TEST_RAIL_PATH, carriage_image.w * RAIL_ART_SCALE, carriage_image.h * RAIL_ART_SCALE,
        )
        crossbow = Crossbow(
            TEST_CROSSBOW_X, GROUND_Y,
            pico.load_image(str(CROSSBOW_BASE_IMAGE)), pico.load_image(str(CROSSBOW_BODY_IMAGE)),
        )
        relic_image = pico.load_image(str(RELIC_IMAGE))
        lighting = Lighting(SCREEN_WIDTH, SCREEN_HEIGHT, RELIC_GLOW_IMAGE)
        relic_anchor = None
        return_effect = ReturnEffect()
        player = Player(400, GROUND_Y, WORLD_WIDTH, terrain=TEST_TERRAIN)
        camera = Camera(SCREEN_WIDTH, WORLD_WIDTH, CAMERA_ZOOM)
        camera.follow(player.x)
        show_hitboxes = False
        previous_time = perf_counter()

        while True:
            frame_start = perf_counter()
            delta_time = min(frame_start - previous_time, 0.05)
            previous_time = frame_start
            events = pico.get_events()
            if any(
                event.type == pico.SDL_QUIT
                or (event.type == pico.SDL_KEYDOWN and event.key == pico.SDLK_ESCAPE)
                for event in events
            ):
                break

            if any(event.type == pico.SDL_KEYDOWN and event.key == pico.SDLK_F11 for event in events):
                fullscreen = set_fullscreen(not fullscreen)
            show_hitboxes = update_hitbox_visibility(events, show_hitboxes)
            direction, running, crouching = read_movement()
            pressed_keys = {event.key for event in events if event.type == pico.SDL_KEYDOWN}
            jump_held = False
            has_focus = bool(pico.SDL_GetKeyboardFocus())
            if has_focus:
                jump_held = bool(pico.SDL_GetKeyboardState(None)[pico.SDL_SCANCODE_SPACE])
            else:
                pressed_keys.clear()
            teleported = False
            was_aiming = crossbow.aiming
            relic_elsewhere = relic_anchor is not None or crossbow.flight is not None
            carrying_relic = not relic_elsewhere and not carriage.relic_mounted
            interact = pico.SDLK_f in pressed_keys
            if crossbow.aiming:
                if interact:
                    crossbow.aiming = False
                elif has_focus:
                    crossbow.aim_toward(*mouse_world_position(camera))
                    if any(event.type == pico.SDL_MOUSEBUTTONDOWN and event.button == pico.SDL_BUTTON_LEFT
                           for event in events):
                        crossbow.fire()
            elif interact and carrying_relic and crossbow.can_aim(player):
                crossbow.aiming = True
                crossbow.aim_toward(*mouse_world_position(camera))
            elif interact and carriage.can_mount(player, relic_elsewhere):
                carriage.relic_mounted = True
            elif pico.SDLK_e in pressed_keys:
                if carrying_relic:
                    _, bottom, _, top = player.get_hitbox()
                    relic_anchor = RelicAnchor(
                        player.x, player.y, player.crouch_time, (bottom + top) / 2, frame_start,
                    )
                else:
                    if carriage.relic_mounted:
                        x, y = carriage.position
                        destination = (x, y - STANDING_HITBOX_HEIGHT / 2, 0.0)
                    elif crossbow.flight is not None:
                        destination = crossbow.flight.return_pose(GROUND_Y)
                    else:
                        destination = (relic_anchor.x, relic_anchor.feet_y, relic_anchor.crouch_time)
                    departure = copy(player)
                    if player.teleport_to(*destination):
                        relic_anchor = None
                        carriage.relic_mounted = False
                        crossbow.flight = None
                        teleported = True
                        return_effect.start(departure, player, camera, frame_start)
            if was_aiming or crossbow.aiming:
                direction, running, crouching = 0, False, False
                jump_held = False
                pressed_keys.clear()
            if not teleported:
                player.update(
                    direction, running, delta_time,
                    jump_pressed=pico.SDLK_SPACE in pressed_keys,
                    jump_held=jump_held,
                    crouch_held=crouching,
                    attack_pressed=pico.SDLK_x in pressed_keys,
                )
                carriage.check_attack(player)
            carriage.move(delta_time)
            flight = crossbow.flight
            if flight is not None:
                flight.update(delta_time, player.terrain, GROUND_Y, WORLD_WIDTH)
            if crossbow.aiming:
                camera.update(player.x, delta_time, view_target=crossbow.x, view_zoom=AIM_CAMERA_ZOOM)
            elif flight is not None and not flight.landed:
                focus = flight.x + flight.vx * FLIGHT_CAMERA_LOOKAHEAD
                camera.update(player.x, delta_time, view_target=focus, view_zoom=FLIGHT_CAMERA_ZOOM)
            else:
                camera.update(player.x, delta_time)
            carriage_position = carriage.position
            crossbow_relic_position = crossbow.relic_position
            relic_elsewhere = relic_anchor is not None or crossbow_relic_position is not None
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
                player, camera, show_hitboxes, ground_image=ground_image,
                background_wall=background_wall, rail_image=rail_image, rail_bend_image=rail_bend_image,
                carriage_image=carriage_image,
                carriage_position=carriage_position,
                rail_relic_image=relic_image if carriage.relic_mounted else None,
                show_mount_prompt=has_focus and carriage.can_mount(player, relic_elsewhere),
                crossbow=crossbow, crossbow_relic_image=relic_image if crossbow_relic_position is not None else None,
                show_crossbow_prompt=(
                    has_focus and not relic_elsewhere and not carriage.relic_mounted and crossbow.can_aim(player)
                ),
                lighting=lighting, relic_center=relic_center,
                return_effect=return_effect, frame_start=frame_start,
            )
            if relic_anchor is not None:
                draw_relic(relic_image, camera, *relic_position, relic_elapsed)
            pico.SDL_SetWindowTitle(pico.window, b"RelicEscape")
            pico.update_canvas()
            sleep(max(0, 1 / 60 - (perf_counter() - frame_start)))
    finally:
        del lighting
        pico.close_canvas()


if __name__ == "__main__":
    main()

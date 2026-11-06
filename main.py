"""Run the first RelicEscape movement prototype."""

from time import perf_counter, sleep

from pico2d import pico2d as pico

from player import Player


SCREEN_WIDTH = 960
SCREEN_HEIGHT = 540
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
GROUND_Y = 200
WORLD_WIDTH = 6400
CAMERA_ZOOM = 1 / 3
# Starter step, two tall walls for repeated wall jumps, and an exit platform.
TEST_TERRAIN = (
    (620, 200, 780, 320),
    (920, 200, 1000, 620),
    (1260, 200, 1340, 700),
    (1480, 460, 1740, 500),
)


class Camera:
    def __init__(self, screen_width, world_width, zoom):
        self.zoom = zoom
        self.view_width = screen_width / zoom
        self.world_width = world_width
        self.x = 0.0

    def follow(self, player_x):
        # Stop scrolling at the map edges so the camera never reveals empty space.
        self.x = max(0.0, min(
            max(0.0, self.world_width - self.view_width),
            player_x - self.view_width / 2,
        ))

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


def draw_scene(player, camera, show_hitboxes=False):
    # Clear the full output, including letterbox bars on non-16:9 monitors.
    pico.SDL_SetRenderDrawColor(pico.renderer, 0, 0, 0, 255)
    pico.SDL_RenderClear(pico.renderer)
    ground_screen_y = GROUND_Y * camera.zoom
    pico.draw_rectangle(
        0, 0, SCREEN_WIDTH - 1, SCREEN_HEIGHT - 1, 22, 26, 34, filled=True,
    )
    pico.draw_rectangle(
        0, 0, SCREEN_WIDTH - 1, ground_screen_y - 1, 38, 44, 52, filled=True,
    )
    pico.draw_line(0, ground_screen_y, SCREEN_WIDTH - 1, ground_screen_y, 94, 137, 142)
    # World-anchored floor seams make scrolling visible in the temporary test room.
    first_seam = int(camera.x // 200) * 200
    for world_x in range(first_seam, min(WORLD_WIDTH, int(camera.x + camera.view_width)) + 1, 200):
        screen_x, _ = camera.world_to_screen(world_x, 0)
        pico.draw_line(screen_x, 0, screen_x, ground_screen_y - 1, 53, 61, 70)
    for left, bottom, right, top in player.terrain:
        if right < camera.x or left > camera.x + camera.view_width:
            continue
        x1, y1 = camera.world_to_screen(left, bottom)
        x2, y2 = camera.world_to_screen(right, top)
        pico.draw_rectangle(x1, y1, x2, y2, 66, 75, 85, filled=True)
        pico.draw_line(x1, y2, x2, y2, 124, 157, 164)
        if show_hitboxes:
            pico.draw_rectangle(x1, y1, x2, y2, 76, 220, 220)
    player.draw(camera)
    if show_hitboxes:
        player.draw_hitbox(camera)


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
    try:
        fullscreen = configure_display()
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
            jump_pressed = bool(pico.SDL_GetKeyboardFocus()) and any(
                event.type == pico.SDL_KEYDOWN and event.key == pico.SDLK_SPACE
                for event in events
            )
            player.update(direction, running, delta_time, jump_pressed, crouching)
            camera.follow(player.x)
            draw_scene(player, camera, show_hitboxes)
            pico.SDL_SetWindowTitle(pico.window, b"RelicEscape")
            pico.update_canvas()
            sleep(max(0, 1 / 60 - (perf_counter() - frame_start)))
    finally:
        pico.close_canvas()


if __name__ == "__main__":
    main()

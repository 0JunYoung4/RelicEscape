"""Run the first RelicEscape movement prototype."""

from time import perf_counter, sleep

from pico2d import pico2d as pico

from player import Player


SCREEN_WIDTH = 960
SCREEN_HEIGHT = 540
GROUND_Y = 200
WORLD_WIDTH = 6400
CAMERA_ZOOM = 0.5


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
        return 0, False
    keys = pico.SDL_GetKeyboardState(None)
    left = bool(keys[pico.SDL_SCANCODE_A] or keys[pico.SDL_SCANCODE_LEFT])
    right = bool(keys[pico.SDL_SCANCODE_D] or keys[pico.SDL_SCANCODE_RIGHT])
    running = bool(keys[pico.SDL_SCANCODE_LSHIFT] or keys[pico.SDL_SCANCODE_RSHIFT])
    return int(right) - int(left), running


def draw_scene(player, camera):
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
    player.draw(camera)


def main():
    pico.SDL_SetHint(pico.SDL_HINT_RENDER_SCALE_QUALITY, b"0")
    pico.open_canvas(SCREEN_WIDTH, SCREEN_HEIGHT)
    try:
        player = Player(400, GROUND_Y, WORLD_WIDTH)
        camera = Camera(SCREEN_WIDTH, WORLD_WIDTH, CAMERA_ZOOM)
        camera.follow(player.x)
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

            direction, running = read_movement()
            player.update(direction, running, delta_time)
            camera.follow(player.x)
            draw_scene(player, camera)
            pico.SDL_SetWindowTitle(pico.window, b"RelicEscape")
            pico.update_canvas()
            sleep(max(0, 1 / 60 - (perf_counter() - frame_start)))
    finally:
        pico.close_canvas()


if __name__ == "__main__":
    main()

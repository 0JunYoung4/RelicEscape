"""Spike damage, safe footing, and the test room health display."""

from ctypes import byref
from dataclasses import dataclass
from math import cos, pi, sin

from pico2d import pico2d as pico


MAX_HEALTH = 100
SPIKE_DAMAGE = 25
SPIKE_HEIGHT = 44
SAFE_CLEARANCE = 108
HIT_FLASH_DURATION = 0.36
FADE_OUT = 0.18
BLACKOUT_HOLD = 0.08
FADE_IN = 0.22
RESTART_DELAY = 0.95

STONE = (62, 79, 92)
STONE_EDGE = (107, 130, 144)
RECESS = (22, 33, 45)
HEALTH_BLUE = (60, 161, 185)


@dataclass(frozen=True)
class SpikeBed:
    left: int
    right: int
    y: int

    def overlaps(self, hitbox, clearance=0):
        left, bottom, right, top = hitbox
        return (
            right > self.left - clearance and left < self.right + clearance
            and bottom < self.y + SPIKE_HEIGHT and top > self.y
        )

    def draw(self, camera, screen_height, show_hitboxes):
        if self.right < camera.x or self.left > camera.x + camera.view_width:
            return
        left, base = camera.world_to_screen(self.left, self.y)
        right, tip = camera.world_to_screen(self.right, self.y + SPIKE_HEIGHT)
        teeth = max(1, round((self.right - self.left) / 24))
        tooth_width = (right - left) / teeth
        vertices = []
        for tooth in range(teeth):
            x = left + tooth * tooth_width
            foot_left = (x, screen_height - base)
            foot_right = (x + tooth_width, screen_height - base)
            middle = (x + tooth_width / 2, screen_height - base)
            peak = (middle[0], screen_height - tip)
            vertices.extend((
                pico.SDL_Vertex(foot_left, (94, 101, 110, 255)),
                pico.SDL_Vertex(peak, (189, 199, 207, 255)),
                pico.SDL_Vertex(middle, (98, 110, 122, 255)),
                pico.SDL_Vertex(middle, (50, 59, 71, 255)),
                pico.SDL_Vertex(peak, (141, 156, 171, 255)),
                pico.SDL_Vertex(foot_right, (54, 62, 73, 255)),
            ))
        geometry = (pico.SDL_Vertex * len(vertices))(*vertices)
        pico.SDL_RenderGeometry(pico.renderer, None, geometry, len(geometry), None, 0)
        pico.draw_line(left, base, right, base, 122, 89, 78)
        if show_hitboxes:
            pico.draw_rectangle(left, base, right, tip, 245, 164, 85)


class Health:
    def __init__(self, spawn_pose, *, returned_at=None):
        self.spawn_pose = spawn_pose
        self.safe_pose = spawn_pose
        self.current = MAX_HEALTH
        self.hit_at = None
        self.hit_position = None
        self.returned_at = returned_at

    def recovering(self, now):
        if self.returned_at is not None:
            return now - self.returned_at < BLACKOUT_HOLD + FADE_IN
        return self.hit_at is not None

    def ready_to_restart(self, now):
        return self.current == 0 and now - self.hit_at >= RESTART_DELAY

    def return_to_safety(self, player, now):
        if (
            self.hit_at is None or self.current == 0 or self.returned_at is not None
            or now - self.hit_at < FADE_OUT
        ):
            return False
        if not player.recover_at(*self.safe_pose):
            player.recover_at(*self.spawn_pose)
        self.returned_at = now
        return True

    def check_spikes(self, player, spike_beds, now):
        if self.recovering(now):
            return False
        hitbox = player.get_hitbox()
        if any(spikes.overlaps(hitbox) for spikes in spike_beds):
            self.hit_position = (player.x, player.y + 24)
            self.hit_at = now
            self.returned_at = None
            self.current = max(0, self.current - SPIKE_DAMAGE)
            return True
        if player.grounded and not any(spikes.overlaps(hitbox, SAFE_CLEARANCE) for spikes in spike_beds):
            self.safe_pose = (player.x, player.y, player.crouch_time)
        return False

    def draw_hit(self, camera, now):
        if self.hit_at is None:
            return
        age = now - self.hit_at
        if age >= HIT_FLASH_DURATION:
            return
        x, y = camera.world_to_screen(*self.hit_position)
        progress = age / HIT_FLASH_DURATION
        for index in range(9):
            angle = pi * (index + 1) / 10
            distance = 3 + progress * (18 + index % 3 * 3)
            start_x = round(x + cos(angle) * distance)
            start_y = round(y + sin(angle) * distance)
            length = 2 + (1 - progress) * 6
            pico.draw_line(
                start_x, start_y,
                round(start_x + cos(angle) * length), round(start_y + sin(angle) * length),
                230, round(125 + (1 - progress) * 85), 124,
            )

    def draw_hud(self, screen_height, now):
        x, y = 31, screen_height - 29
        if self.current == 0:
            self.draw_fragments(x, y, now - self.hit_at)
            return

        width = 134
        edge = (172, 140, 128) if self.hit_at is not None and self.recovering(now) else STONE_EDGE
        pico.draw_rectangle(x, y - 8, x + width, y + 8, *STONE, filled=True)
        pico.draw_line(x, y + 8, x + width, y + 8, *edge)
        pico.draw_line(x + width, y - 8, x + width, y + 8, *edge)
        pico.draw_rectangle(x + 12, y - 5, x + width - 4, y + 5, *RECESS, filled=True)
        start, end = x + 12, x + width - 4
        fill_end = start + round((end - start) * self.current / MAX_HEALTH)
        pico.draw_rectangle(start, y - 4, fill_end, y + 4, *HEALTH_BLUE, filled=True)
        pico.draw_line(start, y + 4, fill_end, y + 4, 125, 209, 222)
        for index, offset in enumerate((103, 76, 47), 1):
            crack = x + offset
            if self.current <= MAX_HEALTH - index * SPIKE_DAMAGE:
                pico.draw_line(crack + 5, y + 8, crack + 1, y + 3, *RECESS)
                pico.draw_line(crack + 1, y + 3, crack + 3, y - 1, *RECESS)
                pico.draw_line(crack + 3, y - 1, crack - 3, y - 8, *RECESS)

        pico.draw_circle(x, y, 12, *edge, filled=True)
        pico.draw_circle(x, y, 10, *RECESS, filled=True)
        for dx, dy in ((0, 9), (-8, -5), (8, -5)):
            pico.draw_line(x, y, x + dx, y + dy, *STONE)

    def draw_blackout(self, screen_width, screen_height, now):
        if self.returned_at is not None:
            fade = 1 - (now - self.returned_at - BLACKOUT_HOLD) / FADE_IN
        elif self.hit_at is not None:
            # Let the health bar disintegrate before fading into a full restart.
            delay = RESTART_DELAY - FADE_OUT if self.current == 0 else 0
            fade = (now - self.hit_at - delay) / FADE_OUT
        else:
            return
        alpha = round(255 * max(0, min(1, fade)))
        if alpha == 0:
            return
        blend_mode = pico.SDL_BlendMode()
        pico.SDL_GetRenderDrawBlendMode(pico.renderer, byref(blend_mode))
        pico.SDL_SetRenderDrawBlendMode(pico.renderer, pico.SDL_BLENDMODE_BLEND)
        try:
            pico.draw_rectangle(0, 0, screen_width - 1, screen_height - 1, 0, 0, 0, alpha, filled=True)
        finally:
            pico.SDL_SetRenderDrawBlendMode(pico.renderer, blend_mode)

    @staticmethod
    def draw_fragments(x, y, age):
        for index in range(31):
            # Stagger the release across the bar and shrink the trailing pixels.
            offset = index * 5 - 11
            flight = max(0.0, age - (30 - index) * 0.006)
            if flight >= 0.68:
                continue
            px = round(x + offset + flight * (30 + index % 5 * 25))
            py = round(y + (index % 3 - 1) * 5 + flight * ((index % 7) - 3) * 16)
            size = max(1, round(4 - 5 * flight))
            color = HEALTH_BLUE if index % 3 == 1 else STONE_EDGE
            shade = max(0.25, 1 - flight)
            pico.draw_rectangle(px, py, px + size, py + size, *(round(c * shade) for c in color), filled=True)

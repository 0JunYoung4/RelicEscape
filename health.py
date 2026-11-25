"""Player health, enemy contact, spike recovery, and the health display."""

from ctypes import byref
from dataclasses import dataclass
from math import ceil

from pico2d import pico2d as pico


MAX_HEALTH = 100
SPIKE_DAMAGE = 25
CONTACT_DAMAGE = 10
CONTACT_INVULNERABILITY = 0.8
SPIKE_HEIGHT = 44
SPIKE_ROOT_DEPTH = 6
SPIKE_TILE_WIDTH = 196
SAFE_CLEARANCE = 108
HIT_FLASH_DURATION = 0.12
FADE_OUT = 0.18
BLACKOUT_HOLD = 0.08
FADE_IN = 0.22
RESTART_DELAY = 0.95

STONE = (62, 79, 92)
STONE_EDGE = (107, 130, 144)
RECESS = (22, 33, 45)
HEALTH_BLUE = (60, 161, 185)
HIT_CORAL = (214, 117, 88)
HIT_OLIVE = (154, 159, 83)
# Horizontal travel, rise, release time (fraction of the burst), size, and color.
HIT_PARTICLES = (
    (-12, 5, 0.15, 2, HIT_OLIVE),
    (-7, 10, 0.00, 2, HIT_CORAL),
    (-3, 6, 0.26, 1, HIT_CORAL),
    (4, 12, 0.06, 2, HIT_CORAL),
    (8, 7, 0.18, 2, HIT_OLIVE),
    (13, 4, 0.28, 1, HIT_OLIVE),
)


@dataclass(frozen=True)
class SpikeBed:
    left: float
    right: float
    y: float
    art_margin: int = 0
    height: float = SPIKE_HEIGHT

    @property
    def top(self):
        return self.y + self.height

    def overlaps(self, hitbox, clearance=0):
        left, bottom, right, top = hitbox
        return (
            right > self.left - clearance and left < self.right + clearance
            and bottom < self.top and top > self.y
        )

    def draw(self, image, camera, show_hitboxes):
        art_left = self.left - self.art_margin
        art_right = self.right + self.art_margin
        if art_right < camera.x or art_left > camera.x + camera.view_width:
            return
        if image is not None:
            left, root = camera.world_to_screen(art_left, self.y - SPIKE_ROOT_DEPTH)
            right, tip = camera.world_to_screen(art_right, self.top)
            tiles = ceil((art_right - art_left) / SPIKE_TILE_WIDTH)
            width = (right - left) / tiles
            root, tip = round(root), round(tip)
            for index in range(tiles):
                x1 = round(left + index * width)
                x2 = round(left + (index + 1) * width)
                image.draw_to_origin(x1, root, x2 - x1, tip - root)
        if show_hitboxes:
            left, base = map(round, camera.world_to_screen(self.left, self.y))
            right, tip = map(round, camera.world_to_screen(self.right, self.top))
            pico.draw_rectangle(left, base, right, tip, 245, 164, 85)


class Health:
    def __init__(self, spawn_pose, *, returned_at=None):
        self.spawn_pose = spawn_pose
        self.safe_pose = spawn_pose
        self.current = MAX_HEALTH
        self.hit_at = None
        self.contact_hit_at = None
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
        for spikes in spike_beds:
            if not spikes.overlaps(hitbox):
                continue
            left, _, right, top = hitbox
            hit_x = (max(left, spikes.left) + min(right, spikes.right)) / 2
            self.hit_position = hit_x, min(top, spikes.top)
            self.hit_at = now
            self.returned_at = None
            self.current = max(0, self.current - SPIKE_DAMAGE)
            return True
        if player.grounded and not any(spikes.overlaps(hitbox, SAFE_CLEARANCE) for spikes in spike_beds):
            self.safe_pose = (player.x, player.y, player.crouch_time)
        return False

    def check_contact(self, player, enemies, now):
        if self.current == 0 or self.recovering(now):
            return False
        if self.contact_hit_at is not None and now - self.contact_hit_at < CONTACT_INVULNERABILITY:
            return False
        left, bottom, right, top = player.get_hitbox()
        for enemy in enemies:
            if enemy.hp == 0 or getattr(enemy, "phase", None) == "emerge":
                continue
            x, y, width, height = enemy.body_bounds()
            # Include tangency: a rolling shell stops at the player's body surface.
            if right < x - width / 2 or left > x + width / 2 or top < y or bottom > y + height:
                continue
            position = ((max(left, x - width / 2) + min(right, x + width / 2)) / 2,
                        (max(bottom, y) + min(top, y + height)) / 2)
            return self.take_enemy_hit(position, now, CONTACT_DAMAGE)
        return False

    def take_enemy_hit(self, position, now, damage):
        if self.current == 0 or self.recovering(now):
            return False
        if self.contact_hit_at is not None and now - self.contact_hit_at < CONTACT_INVULNERABILITY:
            return False
        self.hit_position = position
        self.contact_hit_at = now
        self.current = max(0, self.current - damage)
        if self.current == 0:
            self.hit_at = now
            self.returned_at = None
        return True

    def hit_strength(self, now):
        hits = [hit for hit in (self.hit_at, self.contact_hit_at) if hit is not None]
        if not hits:
            return 0.0
        return max(0.0, 1 - (now - max(hits)) / HIT_FLASH_DURATION)

    def hit_tint(self, now):
        strength = self.hit_strength(now)
        if strength > 0:
            return 255, 255 - round(92 * strength), 255 - round(111 * strength)
        return None

    def draw_hit(self, camera, now):
        strength = self.hit_strength(now)
        if strength == 0:
            return
        x, y = camera.world_to_screen(*self.hit_position)
        progress = 1 - strength
        blend_mode = pico.SDL_BlendMode()
        pico.SDL_GetRenderDrawBlendMode(pico.renderer, byref(blend_mode))
        pico.SDL_SetRenderDrawBlendMode(pico.renderer, pico.SDL_BLENDMODE_BLEND)
        try:
            for travel, rise, delay, size, color in HIT_PARTICLES:
                flight = (progress - delay) / (1 - delay)
                if flight < 0:
                    continue
                px = round(x + travel * (0.12 + 0.88 * flight))
                py = round(y + rise * flight * (2.7 - 2 * flight))
                alpha = round(255 * min(1, (1 - flight) * 1.7))
                pico.draw_rectangle(px, py, px + size - 1, py + size - 1, *color, alpha, filled=True)
        finally:
            pico.SDL_SetRenderDrawBlendMode(pico.renderer, blend_mode)

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

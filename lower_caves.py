"""Playable landing chamber and the adjoining moss gallery."""

from pico2d import pico2d as pico

from opening_cave import SHAFT_FLOOR, SHAFT_SCALE, SHAFT_TOP
from pillbug import Pillbug
from slash_effect import downward_slash_bounds, forward_slash_bounds
from player import ASSET_ROOT, Animation


GALLERY_SECTION_WIDTH = 3240
GALLERY_WIDTH = 2 * GALLERY_SECTION_WIDTH
RELIC_X = GALLERY_SECTION_WIDTH * 1.65
RELIC_Y = 100
PASSAGE_TIME = 0.55
PICKUP_TIME = 0.32
PILLBUG_PATROLS = ((1120, 1450, 0.0), (3070, 3380, 2.4), (3990, 4290, 0.7))


class LowerCaves:
    def __init__(self, cave):
        self.cave = cave
        terrain = ASSET_ROOT / "terrain"
        self.backdrop = pico.load_image(str(terrain / "moss-gallery-backdrop.png"))
        self.entry_backdrop = pico.load_image(str(terrain / "moss-gallery-entry.png"))
        self.attack_hints = pico.load_image(str(ASSET_ROOT / "ui/gallery-attack-hints.png"))
        self.floor = pico.load_image(str(terrain / "moss-gallery-floor.png"))
        self.ceiling = pico.load_image(str(terrain / "moss-gallery-ceiling.png"))
        pico.SDL_SetTextureColorMod(self.backdrop.texture, 166, 180, 178)
        pico.SDL_SetTextureColorMod(self.entry_backdrop.texture, 166, 180, 178)
        pico.SDL_SetTextureColorMod(self.floor.texture, 154, 163, 174)
        pico.SDL_SetTextureColorMod(self.ceiling.texture, 115, 123, 129)
        self.landing_width = cave.shaft.w * SHAFT_SCALE
        self.door_x = self.landing_width * 0.965
        self.room = "landing"
        self.passage_time = None
        self.pickup_time = None
        self.has_relic = False
        self.pillbugs = [Pillbug(*patrol) for patrol in PILLBUG_PATROLS]
        self.attack_poses = pico.load_image(str(ASSET_ROOT / "sprites/enemies/stone-pillbug-roll-flip.png"))
        self.hurt_poses = pico.load_image(str(ASSET_ROOT / "sprites/enemies/stone-pillbug-hurt.png"))
        frames = [{"x": i % 4 * 170, "y": i // 4 * 72, "width": 170, "height": 72}
                  for i in range(8)]
        self.crawl = Animation(ASSET_ROOT / "sprites/enemies/stone-pillbug-moss-crawl-left.png",
                               frames, (85, 71), 1.0, 8)

    def enter(self, player, camera):
        landing = self.room == "landing"
        width = self.landing_width if landing else GALLERY_WIDTH
        player.world_width = camera.world_width = width
        player.terrain = ()
        player.ground_y = 0
        player.recover_at(width / 2 if landing else 130, 0, 0)
        player.facing = 1
        if not landing:
            camera.zoom = camera.normal_zoom
        camera.y = -self.cave.height * 0.20 / camera.zoom
        camera.follow(player.x)

    def target(self, player):
        if not player.grounded or self.passage_time is not None or self.pickup_time is not None:
            return None
        if self.room == "landing":
            if abs(player.x - self.door_x) <= 145:
                return self.door_x
        elif not self.has_relic and abs(player.x - RELIC_X) <= 135:
            return RELIC_X
        return None

    def update(self, player, camera, dt, *, interact, direction, running, jump_pressed,
               jump_held, crouching, attack_pressed):
        if interact and self.target(player) is not None:
            if self.room == "landing":
                self.passage_time = 0
            else:
                self.pickup_time = 0
        if self.passage_time is not None:
            self.passage_time += dt
            player.update(1, False, dt)
            if self.passage_time >= PASSAGE_TIME:
                self.room = "gallery"
                self.passage_time = None
                self.enter(player, camera)
        elif self.pickup_time is not None:
            self.pickup_time += dt
            player.update(0, False, dt)
            if self.pickup_time >= PICKUP_TIME:
                self.has_relic = True
                self.pickup_time = None
        else:
            player.update(direction, running, dt, jump_pressed=jump_pressed, jump_held=jump_held,
                          crouch_held=crouching, attack_pressed=attack_pressed)
        camera.follow(player.x)

    def draw(self, camera):
        if self.room == "landing":
            shaft = self.cave.shaft
            bottom = SHAFT_TOP - SHAFT_FLOOR - shaft.h * SHAFT_SCALE
            shaft.draw_to_origin(*camera.world_to_screen(0, bottom),
                                 self.landing_width * camera.zoom, shaft.h * SHAFT_SCALE * camera.zoom)
            return
        width = GALLERY_SECTION_WIDTH * camera.zoom
        left, _ = camera.world_to_screen(0, 0)
        self.entry_backdrop.draw_to_origin(left, 0, width, self.cave.height)
        self.backdrop.draw_to_origin(left + width, 0, width, self.cave.height)
        # The walking surface is 208 pixels from the top of the 724px floor painting.
        floor_height = 620
        bottom = -floor_height * (1 - 208 / self.floor.h)
        self.draw_stone_strip(self.floor, left, (bottom - camera.y) * camera.zoom, width, floor_height * camera.zoom)
        for bug in self.pillbugs:
            bug.draw(self.crawl, self.attack_poses, camera, self.hurt_poses)

    def update_pillbugs(self, player, dt):
        if self.room == "gallery":
            strike = None
            facing = player.attack_facing
            if player.slash is not None:
                _, facing, kind = player.slash
                bounds = downward_slash_bounds if kind == "air_down_attack" else forward_slash_bounds
                strike = bounds(player.x, player.y, facing)
            for bug in self.pillbugs:
                bug.check_strike(strike, facing, player.attack_power, player.swing_id)
                bug.update(dt, player.get_hitbox(), player.terrain, GALLERY_WIDTH)

    @staticmethod
    def draw_stone_strip(image, left, bottom, width, height):
        image.composite_draw(0, "h", left + width / 2, bottom + height / 2, width, height)
        image.draw_to_origin(left + width, bottom, width, height)

    def draw_attack_hint(self, player):
        if self.room != "gallery" or self.has_relic:
            return
        if 450 <= player.x <= 1810 and self.pillbugs[0].hp > 0:
            row = 0
        elif 2460 <= player.x <= 4450 and any(bug.hp for bug in self.pillbugs[1:]):
            row = 1
        else:
            return
        height = self.attack_hints.h // 2
        self.attack_hints.clip_draw(0, (1 - row) * height, self.attack_hints.w, height,
                                    self.cave.width / 2, 38, self.attack_hints.w, height)

    def draw_foreground(self, camera):
        if self.room == "gallery":
            height = 430 * camera.zoom
            self.draw_stone_strip(self.ceiling, -camera.x * camera.zoom, self.cave.height - height,
                                  GALLERY_SECTION_WIDTH * camera.zoom, height)
        elif self.passage_time is not None:
            opacity = round(255 * min(1, self.passage_time / PASSAGE_TIME))
            pico.SDL_SetRenderDrawBlendMode(pico.renderer, pico.SDL_BLENDMODE_BLEND)
            pico.SDL_SetRenderDrawColor(pico.renderer, 4, 13, 16, opacity)
            pico.SDL_RenderFillRect(pico.renderer, None)

    def relic_position(self, player):
        if self.room != "gallery" or self.has_relic:
            return None
        t = (self.pickup_time or 0) / PICKUP_TIME
        return RELIC_X + (player.x - RELIC_X) * t, RELIC_Y + (player.y + 74 - RELIC_Y) * t

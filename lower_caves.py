"""Playable landing chamber, moss gallery, and adjoining combat chamber."""

import json

from pico2d import pico2d as pico

from crystal_golem import CrystalGolem
from crystal_projectile import DAMAGE as CRYSTAL_DAMAGE
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
PILLAR = (3240, 0, 3380, 242)
AIR_PLATFORM = (3488, 274, 3744, 364)
GALLERY_TERRAIN = (PILLAR, AIR_PLATFORM)
COMBAT_WIDTH = 1920
# Match the straight inner faces and doorway in the 1402x1122 source artwork.
COMBAT_ART_SCALE = COMBAT_WIDTH / 1402
COMBAT_LEFT_WALL = 199 * COMBAT_ART_SCALE
COMBAT_RIGHT_WALL = 1258 * COMBAT_ART_SCALE
COMBAT_DOOR_HEIGHT = (888 - 770) * COMBAT_ART_SCALE
COMBAT_CEILING_Y = (888 - 96) * COMBAT_ART_SCALE
COMBAT_FLOOR_FRACTION = 888 / 1122
COMBAT_CENTER_X = (COMBAT_LEFT_WALL + COMBAT_RIGHT_WALL) / 2
COMBAT_TRIGGER_RADIUS = 80
# Near the 370.6-unit ground-jump + wall-jump apex, with landing clearance.
# The center remains one held jump (202.5 units) above either side.
COMBAT_PLATFORMS = (
    (COMBAT_LEFT_WALL, 278, COMBAT_LEFT_WALL + 280, 368),
    (COMBAT_CENTER_X - 280, 478, COMBAT_CENTER_X + 280, 568),
    (COMBAT_RIGHT_WALL - 280, 278, COMBAT_RIGHT_WALL, 368),
)
COMBAT_EXIT_LEFT = COMBAT_CENTER_X - 150
COMBAT_EXIT_RIGHT = COMBAT_CENTER_X + 150
COMBAT_SHAFT_FLOOR = -960
COMBAT_EXIT_DURATION = .7
COMBAT_FLOOR_BANKS = ((0, COMBAT_SHAFT_FLOOR, COMBAT_EXIT_LEFT, 0),
                      (COMBAT_EXIT_RIGHT, COMBAT_SHAFT_FLOOR, COMBAT_WIDTH, 0))
COMBAT_TERRAIN = ((0, COMBAT_DOOR_HEIGHT, COMBAT_LEFT_WALL, 1280),
                  (COMBAT_RIGHT_WALL, 0, COMBAT_WIDTH, 1280),
                  (COMBAT_LEFT_WALL, COMBAT_CEILING_Y, COMBAT_RIGHT_WALL, 1280),
                  *COMBAT_PLATFORMS, *COMBAT_FLOOR_BANKS,
                  (COMBAT_EXIT_LEFT, -80, COMBAT_EXIT_RIGHT, 0))
COMBAT_OPEN_TERRAIN = COMBAT_TERRAIN[:-1]
ROOM_EDGE = 96


class LowerCaves:
    def __init__(self, cave):
        self.cave = cave
        terrain = ASSET_ROOT / "terrain"
        self.backdrop = pico.load_image(str(terrain / "moss-gallery-backdrop.png"))
        self.entry_backdrop = pico.load_image(str(terrain / "moss-gallery-entry.png"))
        self.attack_hints = pico.load_image(str(ASSET_ROOT / "ui/gallery-attack-hints.png"))
        self.wall_jump_hint = pico.load_image(str(ASSET_ROOT / "ui/gallery-wall-jump-hint.png"))
        self.pillar = pico.load_image(str(terrain / "moss-gallery-small-pillar-v2.png"))
        self.platform = pico.load_image(str(terrain / "moss-gallery-small-platform.png"))
        self.floor = pico.load_image(str(terrain / "moss-gallery-floor.png"))
        self.ceiling = pico.load_image(str(terrain / "moss-gallery-ceiling.png"))
        self.combat_shell = pico.load_image(str(terrain / "moss-combat-room-shell-v5.png"))
        pico.SDL_SetTextureColorMod(self.backdrop.texture, 166, 180, 178)
        pico.SDL_SetTextureColorMod(self.entry_backdrop.texture, 166, 180, 178)
        pico.SDL_SetTextureColorMod(self.floor.texture, 154, 163, 174)
        pico.SDL_SetTextureColorMod(self.ceiling.texture, 115, 123, 129)
        pico.SDL_SetTextureColorMod(self.combat_shell.texture, 166, 180, 178)
        self.landing_width = cave.shaft.w * SHAFT_SCALE
        self.door_x = self.landing_width * 0.965
        self.room = "landing"
        self.passage_time = None
        self.pickup_time = None
        self.has_relic = False
        self.pillbugs = [Pillbug(1120, 1450, 0.0), Pillbug.on_platform(AIR_PLATFORM)]
        self.golems = [CrystalGolem.on_platform(COMBAT_PLATFORMS[0]),
                       CrystalGolem.on_platform(COMBAT_PLATFORMS[2], direction=1)]
        self.combat_pillbugs = [Pillbug(COMBAT_LEFT_WALL + 140, COMBAT_LEFT_WALL + 480, 0),
                               Pillbug(COMBAT_RIGHT_WALL - 480, COMBAT_RIGHT_WALL - 140, 0)]
        for bug, direction in zip(self.combat_pillbugs, (1, -1)):
            bug.x = (bug.left + bug.right) / 2
            bug.direction = direction
            bug.support_edges = COMBAT_LEFT_WALL, COMBAT_RIGHT_WALL
        self.encounter_started = False
        self.exit_progress = 0.0
        golem_path = ASSET_ROOT / "sprites/enemies/stone-crystal-golem-walk-left-v2.json"
        golem = json.loads(golem_path.read_text(encoding="utf-8"))
        self.golem_walk = Animation(golem_path.parent / golem["image"], golem["frames"],
                                    golem["foot_anchor"], golem["scale"], golem["fps"])
        attack_path = golem_path.with_name("stone-crystal-golem-attack-left-v1.json")
        attack = json.loads(attack_path.read_text(encoding="utf-8"))
        self.golem_attack = Animation(attack_path.parent / attack["image"], attack["frames"],
                                      attack["foot_anchor"], attack["scale"], attack["fps"],
                                      attack["frame_durations_ms"])
        golem_emerge_path = golem_path.with_name("stone-crystal-golem-emerge-left-v1.json")
        golem_emerge = json.loads(golem_emerge_path.read_text(encoding="utf-8"))
        self.golem_emergence = Animation(golem_emerge_path.parent / golem_emerge["image"],
                                        golem_emerge["frames"], golem_emerge["foot_anchor"],
                                        golem_emerge["scale"], golem_emerge["fps"],
                                        golem_emerge["frame_durations_ms"])
        self.crystal_image = pico.load_image(str(ASSET_ROOT / "sprites/projectiles/back-crystal-shard-v2.png"))
        self.projectiles = []
        self.attack_poses = pico.load_image(str(ASSET_ROOT / "sprites/enemies/stone-pillbug-roll-flip.png"))
        self.hurt_poses = pico.load_image(str(ASSET_ROOT / "sprites/enemies/stone-pillbug-hurt.png"))
        frames = [{"x": i % 4 * 170, "y": i // 4 * 72, "width": 170, "height": 72}
                  for i in range(8)]
        self.crawl = Animation(ASSET_ROOT / "sprites/enemies/stone-pillbug-moss-crawl-left.png",
                               frames, (85, 71), 1.0, 8)
        emerge_path = ASSET_ROOT / "sprites/enemies/stone-pillbug-emerge-left-v1.json"
        emerge = json.loads(emerge_path.read_text(encoding="utf-8"))
        self.pillbug_emergence = Animation(emerge_path.parent / emerge["image"], emerge["frames"],
                                          emerge["foot_anchor"], emerge["scale"], emerge["fps"],
                                          emerge["frame_durations_ms"])
        death_path = ASSET_ROOT / "sprites/enemies/stone-pillbug-death-curl-left-v1.json"
        death = json.loads(death_path.read_text(encoding="utf-8"))
        self.pillbug_death = Animation(death_path.parent / death["image"], death["frames"],
                                      death["foot_anchor"], death["scale"], death["fps"],
                                      death["frame_durations_ms"])

    @property
    def enemies(self):
        if self.room == "gallery":
            return self.pillbugs
        if self.room == "combat" and self.encounter_started:
            return (*self.golems, *self.combat_pillbugs)
        return ()

    @property
    def exit_open(self):
        return self.exit_progress >= 1.0

    def enter(self, player, camera, *, from_right=False):
        self.projectiles.clear()
        for golem in self.golems:
            golem.attack_time = None
            golem.attack_target = None
        landing = self.room == "landing"
        width = self.landing_width if landing else (COMBAT_WIDTH if self.room == "combat" else GALLERY_WIDTH)
        player.world_width = camera.world_width = width
        player.terrain = () if landing else (COMBAT_TERRAIN if self.room == "combat" else GALLERY_TERRAIN)
        player.ground_y = 0
        if self.room == "combat" and self.exit_open:
            player.terrain = COMBAT_OPEN_TERRAIN
            player.ground_y = COMBAT_SHAFT_FLOOR
        player.recover_at(width / 2 if landing else (width - 130 if from_right else 130), 0, 0)
        player.facing = -1 if from_right else 1
        if not landing:
            camera.zoom = camera.normal_zoom
        camera.y = -self.cave.height * 0.20 / camera.zoom
        self.follow_camera(player, camera)

    def follow_camera(self, player, camera):
        camera.follow(player.x)
        if self.room == "combat":
            base = -self.cave.height * 0.20 / camera.zoom
            if self.exit_open and player.y < 0:
                camera.y = max(COMBAT_SHAFT_FLOOR + base, player.y + base)
                return
            ceiling_limit = COMBAT_CEILING_Y - self.cave.height * 0.90 / camera.zoom
            camera.y = max(base, min(player.y - self.cave.height * 0.40 / camera.zoom, ceiling_limit))

    def start_after_relic(self, player, camera):
        self.room = "gallery"
        self.has_relic = True
        for pillbug in self.pillbugs:
            pillbug.hp = 0
        self.enter(player, camera)
        player.recover_at(RELIC_X, 0, 0)
        self.follow_camera(player, camera)

    def target(self, player):
        if not player.grounded or self.passage_time is not None or self.pickup_time is not None:
            return None
        if self.room == "landing":
            if abs(player.x - self.door_x) <= 145:
                return self.door_x
        elif self.room == "gallery" and not self.has_relic and abs(player.x - RELIC_X) <= 135:
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
        if self.room == "gallery" and direction > 0 and player.x >= GALLERY_WIDTH - ROOM_EDGE:
            self.room = "combat"
            self.enter(player, camera)
        elif self.room == "combat" and direction < 0 and player.x <= ROOM_EDGE:
            self.room = "gallery"
            self.enter(player, camera, from_right=True)
        self.follow_camera(player, camera)

    def draw(self, camera):
        if self.room == "landing":
            shaft = self.cave.shaft
            bottom = SHAFT_TOP - SHAFT_FLOOR - shaft.h * SHAFT_SCALE
            shaft.draw_to_origin(*camera.world_to_screen(0, bottom),
                                 self.landing_width * camera.zoom, shaft.h * SHAFT_SCALE * camera.zoom)
            return
        if self.room == "combat":
            height = self.combat_shell.h * COMBAT_WIDTH / self.combat_shell.w
            bottom = -height * (1 - COMBAT_FLOOR_FRACTION)
            self.combat_shell.draw_to_origin(*camera.world_to_screen(0, bottom),
                                             COMBAT_WIDTH * camera.zoom, height * camera.zoom)
            for x1, y1, x2, y2 in COMBAT_PLATFORMS:
                self.platform.draw_to_origin(*camera.world_to_screen(x1, y1),
                                             (x2 - x1) * camera.zoom, (y2 - y1) * camera.zoom)
            if self.encounter_started:
                for golem in self.golems:
                    golem.draw(self.golem_walk, camera, self.golem_attack, self.golem_emergence)
                for bug in self.combat_pillbugs:
                    bug.draw(self.crawl, self.attack_poses, camera, self.hurt_poses,
                             self.pillbug_emergence, self.pillbug_death)
            for projectile in self.projectiles:
                projectile.draw(self.crystal_image, camera)
            return
        width = GALLERY_SECTION_WIDTH * camera.zoom
        left, _ = camera.world_to_screen(0, 0)
        self.entry_backdrop.draw_to_origin(left, 0, width, self.cave.height)
        self.backdrop.draw_to_origin(left + width, 0, width, self.cave.height)
        # The walking surface is 208 pixels from the top of the 724px floor painting.
        floor_height = 620
        bottom = -floor_height * (1 - 208 / self.floor.h)
        self.draw_stone_strip(self.floor, left, (bottom - camera.y) * camera.zoom, width, floor_height * camera.zoom)
        for image, (x1, y1, x2, y2) in zip((self.pillar, self.platform), GALLERY_TERRAIN):
            image.draw_to_origin(*camera.world_to_screen(x1, y1), (x2-x1)*camera.zoom, (y2-y1)*camera.zoom)
        for bug in self.pillbugs:
            bug.draw(self.crawl, self.attack_poses, camera, self.hurt_poses, death=self.pillbug_death)

    def update_enemies(self, player, dt):
        if (self.room == "combat" and not self.encounter_started
                and abs(player.x - COMBAT_CENTER_X) <= COMBAT_TRIGGER_RADIUS):
            self.encounter_started = True
            for golem in self.golems:
                golem.begin_emergence()
            for bug in self.combat_pillbugs:
                bug.begin_emergence()
        if self.enemies:
            strike = None
            facing = player.attack_facing
            if player.slash is not None:
                _, facing, kind = player.slash
                bounds = downward_slash_bounds if kind == "air_down_attack" else forward_slash_bounds
                strike = bounds(player.x, player.y, facing)
            for enemy in self.enemies:
                if enemy.check_strike(strike, facing, player.attack_power, player.swing_id):
                    player.recoil_from_hit(facing, player.swing_id)
                projectile = enemy.update(dt, player.get_hitbox(), player.terrain, player.world_width)
                if projectile is not None:
                    self.projectiles.append(projectile)
        if (self.room == "combat" and self.encounter_started
                and all(enemy.hp == 0 for enemy in self.enemies)):
            self.exit_progress = min(1.0, self.exit_progress + dt / COMBAT_EXIT_DURATION)
            if self.exit_open:
                player.terrain = COMBAT_OPEN_TERRAIN
                player.ground_y = COMBAT_SHAFT_FLOOR

    def draw_combat_exit(self, camera):
        """Reveal the reserved shaft after the main scene's underground blackout."""
        if self.room != "combat" or self.exit_progress <= 0:
            return
        left, right, floor = COMBAT_EXIT_LEFT, COMBAT_EXIT_RIGHT, COMBAT_SHAFT_FLOOR
        pico.draw_rectangle(*camera.world_to_screen(left, floor),
                            *camera.world_to_screen(right, 14), 5, 17, 23, filled=True)
        # Straight stone faces use the established vertical pillar artwork.
        for bottom in range(floor, 0, 128):
            height = min(128, -bottom)
            for edge in (left - 36, right):
                self.pillar.draw_to_origin(*camera.world_to_screen(edge, bottom),
                                           36 * camera.zoom, height * camera.zoom)
        self.platform.draw_to_origin(*camera.world_to_screen(left - 36, floor - 90),
                                     (right - left + 72) * camera.zoom, 90 * camera.zoom)
        # The two halves retract into the banks before collision is released.
        half = (right - left) / 2
        shift = self.exit_progress * (half + 36)
        if not self.exit_open:
            for x in (left - shift, left + half + shift):
                self.platform.draw_to_origin(*camera.world_to_screen(x, -54),
                                             half * camera.zoom, 54 * camera.zoom)

    def update_projectiles(self, player, health, dt, now):
        if self.room != "combat":
            return
        for projectile in self.projectiles:
            impact = projectile.update(dt, player.terrain, player.world_width, player.get_hitbox(),
                                        ground_y=player.ground_y)
            if impact == "player":
                health.take_enemy_hit((projectile.x, projectile.y), now, CRYSTAL_DAMAGE)
        self.projectiles[:] = [projectile for projectile in self.projectiles if projectile.active]

    @staticmethod
    def draw_stone_strip(image, left, bottom, width, height):
        image.composite_draw(0, "h", left + width / 2, bottom + height / 2, width, height)
        image.draw_to_origin(left + width, bottom, width, height)

    def draw_attack_hint(self, player):
        if self.room != "gallery" or self.has_relic:
            return
        if 450 <= player.x <= 1810 and self.pillbugs[0].hp > 0:
            row = 0
        elif PILLAR[0] - 580 <= player.x < PILLAR[2] and player.y < PILLAR[3]:
            self.wall_jump_hint.draw(self.cave.width / 2, 38)
            return
        elif PILLAR[0] - 120 <= player.x <= AIR_PLATFORM[2] + 320 and self.pillbugs[1].hp > 0:
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

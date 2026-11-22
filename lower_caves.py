"""Playable landing chamber, moss gallery, and adjoining combat chamber."""

import json
from ctypes import byref, c_int
from math import ceil, floor, hypot

from pico2d import pico2d as pico

from crystal_golem import CrystalGolem
from crystal_projectile import DAMAGE as CRYSTAL_DAMAGE
from opening_cave import SHAFT_FLOOR, SHAFT_SCALE, SHAFT_TOP
from pillbug import Pillbug
from slash_effect import downward_slash_bounds, forward_slash_bounds
from stone_wall_effects import StoneWallEffects
from moss_art import MossCaveArt, WALL_SKIN_WIDTH, WALL_TILE_HEIGHT
from player import ASSET_ROOT, STANDING_HITBOX_WIDTH, Animation


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
# Keep the rising slab flush with the doorway's inner face and lintel.
COMBAT_ENTRANCE_BARRIER = (COMBAT_LEFT_WALL - 112, 0,
                           COMBAT_LEFT_WALL, COMBAT_DOOR_HEIGHT)
COMBAT_GATE_DURATION = .55
# Near the 370.6-unit ground-jump + wall-jump apex, with landing clearance.
# The center remains one held jump (202.5 units) above either side.
COMBAT_PLATFORMS = (
    (COMBAT_LEFT_WALL, 278, COMBAT_LEFT_WALL + 280, 368),
    (COMBAT_CENTER_X - 280, 478, COMBAT_CENTER_X + 280, 568),
    (COMBAT_RIGHT_WALL - 280, 278, COMBAT_RIGHT_WALL, 368),
)
COMBAT_EXIT_LEFT = COMBAT_CENTER_X - 124
COMBAT_EXIT_RIGHT = COMBAT_CENTER_X + 124
COMBAT_SHAFT_LEFT = COMBAT_CENTER_X - 90
COMBAT_SHAFT_RIGHT = COMBAT_CENTER_X + 90
COMBAT_COVER_THICKNESS = COMBAT_ENTRANCE_BARRIER[2] - COMBAT_ENTRANCE_BARRIER[0]
COMBAT_RIM_HEIGHT = COMBAT_COVER_THICKNESS + 64
COMBAT_RIM_WIDTH = 997
COMBAT_SHAFT_FLOOR = -960
COMBAT_EXIT_DURATION = .7
COMBAT_FLOOR_BANKS = ((0, -COMBAT_COVER_THICKNESS, COMBAT_EXIT_LEFT, 0),
                      (COMBAT_EXIT_RIGHT, -COMBAT_COVER_THICKNESS, COMBAT_WIDTH, 0),
                      (0, COMBAT_SHAFT_FLOOR, COMBAT_SHAFT_LEFT, -COMBAT_COVER_THICKNESS),
                      (COMBAT_SHAFT_RIGHT, COMBAT_SHAFT_FLOOR, COMBAT_WIDTH, -COMBAT_COVER_THICKNESS))
COMBAT_TERRAIN = ((0, COMBAT_DOOR_HEIGHT, COMBAT_LEFT_WALL, 1280),
                  (COMBAT_RIGHT_WALL, 0, COMBAT_WIDTH, 1280),
                  (COMBAT_LEFT_WALL, COMBAT_CEILING_Y, COMBAT_RIGHT_WALL, 1280),
                  *COMBAT_PLATFORMS, *COMBAT_FLOOR_BANKS,
                  (COMBAT_EXIT_LEFT, -COMBAT_COVER_THICKNESS, COMBAT_EXIT_RIGHT, 0))
COMBAT_OPEN_TERRAIN = COMBAT_TERRAIN[:-1]
ROOM_EDGE = 96


class LowerCaves:
    def __init__(self, cave):
        self.cave = cave
        self.art = MossCaveArt(cave.width, cave.height)
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
        self.combat_blocker = pico.load_image(str(terrain / "moss-combat-door-blocker-v1.png"))
        self.descent = pico.load_image(str(terrain / "moss-combat-descent-shaft-v1.png"))
        self.descent_art = json.loads((terrain / "moss-combat-descent-shaft-v1.json").read_text(encoding="utf-8"))
        self.exit_cover = pico.load_image(str(terrain / "moss-combat-floor-cover-v4.png"))
        self.exit_rim = pico.load_image(str(terrain / "moss-combat-shaft-rim-v3.png"))
        self.rim_art = json.loads((terrain / "moss-combat-shaft-rim-v3.json").read_text(encoding="utf-8"))
        pico.SDL_SetTextureColorMod(self.backdrop.texture, 166, 180, 178)
        pico.SDL_SetTextureColorMod(self.entry_backdrop.texture, 166, 180, 178)
        pico.SDL_SetTextureColorMod(self.floor.texture, 154, 163, 174)
        pico.SDL_SetTextureColorMod(self.ceiling.texture, 115, 123, 129)
        pico.SDL_SetTextureColorMod(self.combat_shell.texture, 166, 180, 178)
        pico.SDL_SetTextureColorMod(self.combat_blocker.texture, 166, 180, 178)
        pico.SDL_SetTextureColorMod(self.descent.texture, 166, 180, 178)
        pico.SDL_SetTextureColorMod(self.exit_cover.texture, 166, 180, 178)
        pico.SDL_SetTextureColorMod(self.exit_rim.texture, 166, 180, 178)
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
        self.entrance_progress = 0.0
        self.wall_effects = StoneWallEffects(COMBAT_ENTRANCE_BARRIER[0], COMBAT_ENTRANCE_BARRIER[2])
        self.exit_progress = 0.0
        self.shaft_visibility = 0.0
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
        golem_death_path = golem_path.with_name("stone-crystal-golem-death-left-v1.json")
        golem_death = json.loads(golem_death_path.read_text(encoding="utf-8"))
        self.golem_death = Animation(golem_death_path.parent / golem_death["image"],
                                    golem_death["frames"], golem_death["foot_anchor"],
                                    golem_death["scale"], golem_death["fps"],
                                    golem_death["frame_durations_ms"])
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

    @property
    def exit_slide(self):
        progress = self.exit_progress
        return progress * progress * (3 - 2 * progress)

    @property
    def entrance_locked(self):
        return self.encounter_started and (self.entrance_progress > 0 or
               any(enemy.hp > 0 for enemy in (*self.golems, *self.combat_pillbugs)))

    def combat_terrain(self):
        terrain = COMBAT_TERRAIN
        if self.exit_progress > 0:
            terrain = COMBAT_OPEN_TERRAIN
            if not self.exit_open:
                cover_left = COMBAT_EXIT_LEFT + (COMBAT_EXIT_RIGHT - COMBAT_EXIT_LEFT) * self.exit_slide
                terrain = (*terrain, (cover_left, -COMBAT_COVER_THICKNESS, COMBAT_EXIT_RIGHT, 0))
        return (*terrain, COMBAT_ENTRANCE_BARRIER) if self.entrance_locked else terrain

    def allows_relic_destination(self, destination):
        return (destination is None or self.room != "combat" or not self.entrance_locked
                or destination[0] >= COMBAT_ENTRANCE_BARRIER[2])

    def enter(self, player, camera, *, from_right=False):
        self.shaft_visibility = 0.0
        self.wall_effects.clear()
        self.wall_effects.progress = self.entrance_progress
        self.projectiles.clear()
        for golem in self.golems:
            golem.attack_time = None
            golem.attack_target = None
        landing = self.room == "landing"
        width = self.landing_width if landing else (COMBAT_WIDTH if self.room == "combat" else GALLERY_WIDTH)
        player.world_width = camera.world_width = width
        player.terrain = () if landing else (self.combat_terrain() if self.room == "combat" else GALLERY_TERRAIN)
        player.ground_y = 0
        if self.room == "combat" and self.exit_progress > 0:
            player.ground_y = COMBAT_SHAFT_FLOOR
        spawn_x = width / 2 if landing else (width - 130 if from_right else 130)
        if self.room == "combat" and self.entrance_locked:
            spawn_x = max(spawn_x, COMBAT_ENTRANCE_BARRIER[2] + STANDING_HITBOX_WIDTH / 2 + 16)
        player.recover_at(spawn_x, 0, 0)
        player.facing = -1 if from_right else 1
        if not landing:
            camera.zoom = camera.normal_zoom
        camera.y = -self.cave.height * 0.20 / camera.zoom
        self.follow_camera(player, camera)

    def follow_camera(self, player, camera):
        camera.follow(player.x)
        if self.room == "combat":
            base = -self.cave.height * 0.20 / camera.zoom
            if self.exit_progress > 0 and player.y < 0:
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
        elif (self.room == "combat" and not self.entrance_locked
              and direction < 0 and player.x <= ROOM_EDGE):
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
            self.art.draw_background(camera)
            self.art.draw_motes(camera, 0, COMBAT_CEILING_Y,
                                left=COMBAT_LEFT_WALL, right=COMBAT_RIGHT_WALL)
            pico.draw_rectangle(*camera.world_to_screen(0, COMBAT_CEILING_Y),
                                *camera.world_to_screen(COMBAT_WIDTH, 1600), 0, 0, 0, filled=True)
            self.art.draw_wall(camera, COMBAT_LEFT_WALL, COMBAT_DOOR_HEIGHT, COMBAT_CEILING_Y)
            self.art.draw_wall(camera, COMBAT_RIGHT_WALL, 0, COMBAT_CEILING_Y, right_wall=True)
            self.art.draw_floor(camera, 0, COMBAT_WIDTH, 0)
            for x1, y1, x2, y2 in COMBAT_PLATFORMS:
                self.art.draw_platform(camera, (x1, y1, x2, y2))
            self.draw_combat_gate(camera)
            self.wall_effects.draw(camera)
            self.art.draw_corner(camera, COMBAT_LEFT_WALL, COMBAT_CEILING_Y, width=120)
            self.art.draw_corner(camera, COMBAT_RIGHT_WALL, COMBAT_CEILING_Y,
                                 width=120, right_wall=True)
            self.art.draw_corner(camera, COMBAT_RIGHT_WALL, 0, width=110,
                                 right_wall=True, grow_up=True)
            self.art.draw_corner(camera, COMBAT_LEFT_WALL, COMBAT_PLATFORMS[0][3], width=84)
            self.art.draw_corner(camera, COMBAT_RIGHT_WALL, COMBAT_PLATFORMS[2][3],
                                 width=84, right_wall=True)
            if self.encounter_started:
                for golem in self.golems:
                    golem.draw(self.golem_walk, camera, self.golem_attack,
                               self.golem_emergence, self.golem_death)
                for bug in self.combat_pillbugs:
                    bug.draw(self.crawl, self.attack_poses, camera, self.hurt_poses,
                             self.pillbug_emergence, self.pillbug_death)
            for projectile in self.projectiles:
                projectile.draw(self.crystal_image, camera)
            return
        self.art.draw_background(camera)
        self.art.draw_motes(camera, 0, 900, right=GALLERY_WIDTH)
        self.art.draw_floor(camera, 0, GALLERY_WIDTH, 0)
        self.art.shadow_floor(camera, 0)
        self.art.draw_pillar(camera, PILLAR)
        self.art.draw_platform(camera, AIR_PLATFORM)
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
            if self.exit_progress > 0:
                player.ground_y = COMBAT_SHAFT_FLOOR
        if self.room == "combat":
            closing = self.encounter_started and any(enemy.hp > 0 for enemy in self.enemies)
            direction = 1 if closing else -1
            self.entrance_progress = max(0.0, min(1.0,
                self.entrance_progress + direction * dt / COMBAT_GATE_DURATION))
            player.terrain = self.combat_terrain()

    def update_effects(self, dt, player):
        if self.room == "combat":
            self.wall_effects.update(self.entrance_progress, dt)
        else:
            self.wall_effects.clear()
        target = 0.0
        if self.room == "combat" and self.exit_open:
            distance = hypot(max(COMBAT_EXIT_LEFT - player.x, player.x - COMBAT_EXIT_RIGHT, 0),
                             max(player.y, 0))
            proximity = max(0.0, 1 - distance / 240)
            target = proximity * proximity * (3 - 2 * proximity)
        # Light follows the player's approach after the lid opens, independently of its motion.
        change = dt / .7
        self.shaft_visibility += max(-change, min(change, target - self.shaft_visibility))

    def draw_combat_gate(self, camera):
        if self.room != "combat" or self.entrance_progress <= 0:
            return
        left, _, right, height = COMBAT_ENTRANCE_BARRIER
        # Show the slab's upper part above ground as it rises from below the floor.
        # Reversing the same progress sinks it back down when the arena clears.
        image = self.art.wall
        source_width = min(image.w, round((right - left) / WALL_SKIN_WIDTH * image.w))
        source_height = min(image.h, round(height / WALL_TILE_HEIGHT * image.h))
        visible_pixels = round(source_height * self.entrance_progress)
        if visible_pixels:
            image.clip_draw_to_origin(image.w - source_width, source_height - visible_pixels, source_width, visible_pixels,
                                      *camera.world_to_screen(left, 0),
                                      (right - left) * camera.zoom,
                                      height * visible_pixels / source_height * camera.zoom)

    def draw_combat_exit(self, camera):
        """Slide the heavy cover beneath the same foreground shadow as the floor."""
        if self.room != "combat":
            return
        left, right = COMBAT_EXIT_LEFT, COMBAT_EXIT_RIGHT
        slide = self.exit_slide
        width = right - left
        # The supporting shoulders remain in place while the top cap slides away.
        # Match the floor plane and socket depth separately; feathered banks blend over the floor.
        image, art = self.exit_rim, self.rim_art
        upper_scale = width / (art["upper_right"] - art["upper_left"])
        lower_scale = (COMBAT_SHAFT_RIGHT - COMBAT_SHAFT_LEFT) / (art["lower_right"] - art["lower_left"])
        image.clip_draw_to_origin(0, image.h - art["step_y"], image.w,
            art["step_y"] - art["surface_y"],
            *camera.world_to_screen(left - art["upper_left"] * upper_scale, -COMBAT_COVER_THICKNESS),
            image.w * upper_scale * camera.zoom, COMBAT_COVER_THICKNESS * camera.zoom)
        image.clip_draw_to_origin(0, 0, image.w, image.h - art["step_y"],
            *camera.world_to_screen(COMBAT_SHAFT_LEFT - art["lower_left"] * lower_scale, -COMBAT_RIM_HEIGHT),
            image.w * lower_scale * camera.zoom,
            (COMBAT_RIM_HEIGHT - COMBAT_COVER_THICKNESS) * camera.zoom)
        self.art.draw_floor(camera, 0, left, 0)
        self.art.draw_floor(camera, right, COMBAT_WIDTH, 0)
        image = self.art.floor
        visible_pixels = round(image.w * (1 - slide))
        if visible_pixels:
            height = COMBAT_COVER_THICKNESS * image.h / (image.h - self.art.floor_art["surface_y"])
            self.art.draw_surface(camera, image, left + width * slide, -COMBAT_COVER_THICKNESS,
                                  width * (1 - slide), height, source_right=visible_pixels,
                                  profile_origin=left)
        # Hide the cover and socket's buried rock with one continuous floor shadow.
        self.draw_combat_shadows(camera)
        if self.exit_progress > 0:
            reveal_right = right + 36 if self.exit_open else left + width * slide
            self.draw_combat_passage(camera, reveal_right)

    def draw_combat_passage(self, camera, reveal_right):
        # The slab disappears into the right bank; no shaft art leaks through it.
        left, right = COMBAT_EXIT_LEFT, COMBAT_EXIT_RIGHT
        x1, y1 = camera.world_to_screen(left - 36, COMBAT_SHAFT_FLOOR - 80)
        x2, y2 = camera.world_to_screen(reveal_right, 0)
        clip_left, clip_top = max(0, floor(x1)), max(0, floor(self.cave.height - y2))
        clip_right = min(self.cave.width, ceil(x2))
        clip_bottom = min(self.cave.height, ceil(self.cave.height - y1))
        if clip_right <= clip_left or clip_bottom <= clip_top:
            return
        previous_clip = pico.SDL_Rect()
        clipped = pico.SDL_RenderIsClipEnabled(pico.renderer)
        pico.SDL_RenderGetClipRect(pico.renderer, byref(previous_clip))
        clip = pico.SDL_Rect(clip_left, clip_top, clip_right - clip_left, clip_bottom - clip_top)
        if clipped:
            pico.SDL_IntersectRect(byref(clip), byref(previous_clip), byref(clip))
        pico.SDL_RenderSetClipRect(pico.renderer, byref(clip))
        try:
            brightness = self.shaft_visibility
            pico.SDL_SetTextureColorMod(self.descent.texture, round(166 * brightness),
                                       round(180 * brightness), round(178 * brightness))
            art = self.descent_art
            inner_width = art["inner_right"] - art["inner_left"]
            scale_x = (COMBAT_SHAFT_RIGHT - COMBAT_SHAFT_LEFT) / inner_width
            height = self.descent.h * (-COMBAT_SHAFT_FLOOR - COMBAT_COVER_THICKNESS) / art["floor_y"]
            # The short, wider mouth sits above the permanent supporting ledges.
            self.descent.clip_draw_to_origin(art["inner_left"], self.descent.h - 40,
                inner_width, 40, *camera.world_to_screen(left, -COMBAT_COVER_THICKNESS),
                (right - left) * camera.zoom, COMBAT_COVER_THICKNESS * camera.zoom)
            self.descent.draw_to_origin(
                *camera.world_to_screen(COMBAT_SHAFT_LEFT - art["inner_left"] * scale_x,
                                        -COMBAT_COVER_THICKNESS - height),
                self.descent.w * scale_x * camera.zoom, height * camera.zoom)
            tint = round(255 * brightness)
            pico.SDL_SetTextureColorMod(self.art.wall.texture, tint, tint, tint)
            pico.SDL_SetTextureColorMod(self.art.floor.texture, tint, tint, tint)
            self.art.draw_wall(camera, COMBAT_SHAFT_LEFT, COMBAT_SHAFT_FLOOR, -COMBAT_COVER_THICKNESS)
            self.art.draw_wall(camera, COMBAT_SHAFT_RIGHT, COMBAT_SHAFT_FLOOR,
                               -COMBAT_COVER_THICKNESS, right_wall=True)
            self.art.draw_floor(camera, COMBAT_SHAFT_LEFT, COMBAT_SHAFT_RIGHT,
                                COMBAT_SHAFT_FLOOR, depth=64, tiled=False)
            self.art.draw_corner(camera, COMBAT_SHAFT_LEFT, COMBAT_SHAFT_FLOOR,
                                 width=55, grow_up=True, alpha=brightness)
            self.art.draw_corner(camera, COMBAT_SHAFT_RIGHT, COMBAT_SHAFT_FLOOR,
                                 width=55, right_wall=True, grow_up=True, alpha=brightness)
        finally:
            pico.SDL_SetTextureColorMod(self.art.wall.texture, 255, 255, 255)
            pico.SDL_SetTextureColorMod(self.art.floor.texture, 255, 255, 255)
            pico.SDL_SetTextureColorMod(self.descent.texture, 166, 180, 178)
            pico.SDL_RenderSetClipRect(pico.renderer, byref(previous_clip) if clipped else None)

    def draw_combat_shadows(self, camera):
        """Keep solid rock interiors black, with a narrow readable surface edge."""
        def solid(bounds):
            x1, y1, x2, y2 = bounds
            if x2 > x1 and y2 > y1:
                pico.draw_rectangle(*camera.world_to_screen(x1, y1),
                                    *camera.world_to_screen(x2, y2), 0, 0, 0, filled=True)

        def gradient(bounds, alpha):
            x1, y1, x2, y2 = bounds
            vertices = []
            for (x, y), opacity in zip(((x1, y1), (x2, y1), (x1, y2), (x2, y2)), alpha):
                sx, sy = camera.world_to_screen(x, y)
                vertices.append(pico.SDL_Vertex((sx, self.cave.height - sy), (0, 0, 0, opacity)))
            geometry = (pico.SDL_Vertex * 4)(*vertices)
            indices = (c_int * 6)(0, 1, 2, 1, 3, 2)
            pico.SDL_RenderGeometry(pico.renderer, None, geometry, 4, indices, 6)

        solid((0, min(camera.y - 4 / camera.zoom, -57), COMBAT_WIDTH, -56))
        solid((COMBAT_EXIT_LEFT, min(camera.y - 4 / camera.zoom, -COMBAT_COVER_THICKNESS - 1),
               COMBAT_EXIT_RIGHT, -COMBAT_COVER_THICKNESS))
        solid((0, COMBAT_DOOR_HEIGHT, COMBAT_LEFT_WALL - 192, 1280))
        solid((COMBAT_RIGHT_WALL + 192, 0, COMBAT_WIDTH, 1280))
        blend = pico.SDL_BlendMode()
        pico.SDL_GetRenderDrawBlendMode(pico.renderer, byref(blend))
        pico.SDL_SetRenderDrawBlendMode(pico.renderer, pico.SDL_BLENDMODE_BLEND)
        try:
            gradient((0, -56, COMBAT_WIDTH, 0), (255, 255, 0, 0))
            gradient((COMBAT_LEFT_WALL - 192, COMBAT_DOOR_HEIGHT, COMBAT_LEFT_WALL, 1280),
                     (255, 0, 255, 0))
            gradient((COMBAT_RIGHT_WALL, 0, COMBAT_RIGHT_WALL + 192, 1280),
                     (0, 255, 0, 255))
        finally:
            pico.SDL_SetRenderDrawBlendMode(pico.renderer, blend)

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
        if self.room == "combat":
            roof = COMBAT_CEILING_Y if camera.world_to_screen(0, COMBAT_CEILING_Y)[1] < self.cave.height * 1.2 else None
            self.art.draw_canopy(camera, roof)
        elif self.room == "gallery":
            self.art.draw_canopy(camera)
        if self.passage_time is not None:
            opacity = round(255 * min(1, self.passage_time / PASSAGE_TIME))
            pico.SDL_SetRenderDrawBlendMode(pico.renderer, pico.SDL_BLENDMODE_BLEND)
            pico.SDL_SetRenderDrawColor(pico.renderer, 4, 13, 16, opacity)
            pico.SDL_RenderFillRect(pico.renderer, None)

    def relic_position(self, player):
        if self.room != "gallery" or self.has_relic:
            return None
        t = (self.pickup_time or 0) / PICKUP_TIME
        return RELIC_X + (player.x - RELIC_X) * t, RELIC_Y + (player.y + 74 - RELIC_Y) * t

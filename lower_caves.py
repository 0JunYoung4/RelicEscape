"""Playable landing chamber, moss gallery, combat chamber, and lower route."""

import json
from math import hypot

from pico2d import pico2d as pico

from combat_scenery import COMBAT_ART
from crystal_golem import CrystalGolem
from crystal_projectile import DAMAGE as CRYSTAL_DAMAGE
from hit_impact import IMPACT_DURATION, HitImpact
from lower_route_a import LowerRouteA
from lower_route_b import LowerRouteB
from lower_route_b_layout import WIDTH as B_ROUTE_WIDTH
from lower_route_c import CHECKPOINT as C_CHECKPOINT, LEFT as C_LEFT, RIGHT as C_RIGHT, LowerRouteC
from lower_route_connection import A_ORIGIN, PASSAGE_CENTER, LowerRouteConnection
from opening_cave import SHAFT_FLOOR, SHAFT_SCALE, SHAFT_TOP
from pillbug import Pillbug
from slash_effect import downward_slash_bounds, forward_slash_bounds
from stone_wall_effects import StoneWallEffects
from moss_art import MossCaveArt
from relic_shrine import RelicShrine
from player import ASSET_ROOT, STANDING_HITBOX_WIDTH, Animation


GALLERY_SECTION_WIDTH = 3240
GALLERY_WIDTH = 2 * GALLERY_SECTION_WIDTH
GALLERY_CEILING_Y = 900
RELIC_X = GALLERY_SECTION_WIDTH * 1.65
RELIC_Y = 100
PASSAGE_TIME = 0.55
PICKUP_TIME = 0.32
PILLAR = (3240, 0, 3380, 242)
AIR_PLATFORM = (3488, 274, 3744, 364)
GALLERY_TERRAIN = (PILLAR, AIR_PLATFORM)
COMBAT_WIDTH = 1920
# Preserve the doorway, walkable width and platform datum of the original room.
COMBAT_ART_SCALE = COMBAT_WIDTH / 1402
COMBAT_LEFT_WALL = 199 * COMBAT_ART_SCALE
COMBAT_RIGHT_WALL = 1258 * COMBAT_ART_SCALE
COMBAT_DOOR_HEIGHT = (888 - 770) * COMBAT_ART_SCALE
COMBAT_CEILING_Y = (888 - 96) * COMBAT_ART_SCALE
COMBAT_CENTER_X = (COMBAT_LEFT_WALL + COMBAT_RIGHT_WALL) / 2
COMBAT_TRIGGER_RADIUS = 80
# Keep the rising slab flush with the doorway's inner face and lintel.
COMBAT_ENTRANCE_BARRIER = (COMBAT_LEFT_WALL - 112, 0,
                           COMBAT_LEFT_WALL, COMBAT_DOOR_HEIGHT)
COMBAT_GATE_DURATION = .55
# Lower all three platforms by 120 units, keeping the 200-unit step
# from either side to the center within one held jump (202.5 units).
COMBAT_PLATFORMS = (
    (COMBAT_LEFT_WALL, 158, COMBAT_LEFT_WALL + 280, 248),
    (COMBAT_CENTER_X - 280, 358, COMBAT_CENTER_X + 280, 448),
    (COMBAT_RIGHT_WALL - 280, 158, COMBAT_RIGHT_WALL, 248),
)
COMBAT_EXIT_LEFT = COMBAT_CENTER_X - 124
COMBAT_EXIT_RIGHT = COMBAT_CENTER_X + 124
COMBAT_SHAFT_LEFT = COMBAT_CENTER_X - 90
COMBAT_SHAFT_RIGHT = COMBAT_CENTER_X + 90
COMBAT_COVER_THICKNESS = COMBAT_ENTRANCE_BARRIER[2] - COMBAT_ENTRANCE_BARRIER[0]
COMBAT_SHAFT_FLOOR = -960
COMBAT_ROUTE_SEAM = COMBAT_SHAFT_FLOOR + 96
COMBAT_EXIT_QUIET_DURATION = .5
COMBAT_EXIT_LIGHT_DURATION = .6
COMBAT_EXIT_DELAY = COMBAT_EXIT_QUIET_DURATION + COMBAT_EXIT_LIGHT_DURATION
COMBAT_EXIT_DURATION = .7
COMBAT_FLOOR_BANKS = ((0, -COMBAT_COVER_THICKNESS, COMBAT_EXIT_LEFT, 0),
                      (COMBAT_EXIT_RIGHT, -COMBAT_COVER_THICKNESS, COMBAT_WIDTH, 0),
                      (0, COMBAT_SHAFT_FLOOR, COMBAT_SHAFT_LEFT, -COMBAT_COVER_THICKNESS),
                      (COMBAT_SHAFT_RIGHT, COMBAT_SHAFT_FLOOR, COMBAT_WIDTH, -COMBAT_COVER_THICKNESS))
COMBAT_TERRAIN = (*map(tuple, COMBAT_ART["wall_colliders"]),
                  (0, COMBAT_CEILING_Y, COMBAT_WIDTH, 1280),
                  *COMBAT_PLATFORMS, *COMBAT_FLOOR_BANKS,
                  (COMBAT_EXIT_LEFT, -COMBAT_COVER_THICKNESS, COMBAT_EXIT_RIGHT, 0))
COMBAT_OPEN_TERRAIN = COMBAT_TERRAIN[:-1]
ROOM_EDGE = 96


class LowerCaves:
    def __init__(self, cave):
        self.cave = cave
        self.art = MossCaveArt(cave.width, cave.height)
        self.shrine = RelicShrine(cave.height)
        terrain = ASSET_ROOT / "terrain"
        self.backdrop = pico.load_image(str(terrain / "moss-gallery-backdrop.png"))
        self.entry_backdrop = pico.load_image(str(terrain / "moss-gallery-entry.png"))
        self.attack_hints = pico.load_image(str(ASSET_ROOT / "ui/gallery-attack-hints.png"))
        self.wall_jump_hint = pico.load_image(str(ASSET_ROOT / "ui/gallery-wall-jump-hint.png"))
        self.platform = pico.load_image(str(terrain / "moss-gallery-small-platform.png"))
        self.floor = pico.load_image(str(terrain / "moss-gallery-floor.png"))
        self.ceiling = pico.load_image(str(terrain / "moss-gallery-ceiling.png"))
        pico.SDL_SetTextureColorMod(self.backdrop.texture, 166, 180, 178)
        pico.SDL_SetTextureColorMod(self.entry_backdrop.texture, 166, 180, 178)
        pico.SDL_SetTextureColorMod(self.floor.texture, 154, 163, 174)
        pico.SDL_SetTextureColorMod(self.ceiling.texture, 115, 123, 129)
        self.landing_width = cave.shaft.w * SHAFT_SCALE
        self.door_x = self.landing_width * 0.965
        self.room = "landing"
        self.route_a = None
        self.route_b = None
        self.route_c = None
        self.route_connection = None
        self.passage_time = None
        self.pickup_time = None
        self.has_relic = False
        self.pillbugs = [Pillbug(1120, 1450, 0.0), Pillbug.on_platform(AIR_PLATFORM)]
        left, bottom, right, top = COMBAT_PLATFORMS[1]
        self.golems = [CrystalGolem.on_platform((left, bottom, COMBAT_CENTER_X, top),
                                               direction=1, support_edges=(left, right)),
                       CrystalGolem.on_platform((COMBAT_CENTER_X, bottom, right, top),
                                               support_edges=(left, right))]
        # Start at opposite ends; each golem patrols its own half of the top platform.
        self.golems[0].x = self.golems[0].left
        self.golems[1].x = self.golems[1].right
        self.combat_pillbugs = [Pillbug(COMBAT_LEFT_WALL + 140, COMBAT_LEFT_WALL + 480, 0),
                               Pillbug(COMBAT_RIGHT_WALL - 480, COMBAT_RIGHT_WALL - 140, 0)]
        for bug, direction in zip(self.combat_pillbugs, (1, -1)):
            bug.x = (bug.left + bug.right) / 2
            bug.direction = direction
            bug.support_edges = COMBAT_LEFT_WALL, COMBAT_RIGHT_WALL
        self.combat_phase = "waiting"
        self.entrance_progress = 0.0
        self.wall_effects = StoneWallEffects(COMBAT_ENTRANCE_BARRIER[0], COMBAT_ENTRANCE_BARRIER[2])
        self.exit_cue_time = 0.0
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
        self.hit_impacts = []
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
    def in_lower_route(self):
        return self.room in ("route_a", "route_b", "route_c")

    @property
    def restart_room(self):
        if self.in_lower_route and self.route_c is not None and self.route_c.checkpoint_reached:
            return "route_c"
        return "route_b" if self.room == "route_c" else self.room

    @property
    def route(self):
        if not self.in_lower_route:
            return None
        for route in (self.route_a, self.route_b):
            if route is not None and route.mounted_carriage is not None:
                return route
        if self.room == "route_a":
            return self.route_a
        if self.room == "route_b":
            return self.route_b
        return None

    @property
    def encounter_started(self):
        return self.combat_phase != "waiting"

    @property
    def enemies(self):
        if self.room == "gallery":
            return self.pillbugs
        if self.room == "combat":
            if self.combat_phase in ("golems", "cleared"):
                return (*self.golems, *self.combat_pillbugs)
            if self.combat_phase == "pillbugs":
                return tuple(self.combat_pillbugs)
        if self.in_lower_route:
            return tuple(enemy for route in (self.route_a, self.route_b, self.route_c) if route is not None
                         for enemy in route.enemies)
        return ()

    @property
    def exit_open(self):
        return self.exit_progress >= 1.0

    @property
    def exit_seam_light(self):
        progress = max(0.0, self.exit_cue_time - COMBAT_EXIT_QUIET_DURATION) / COMBAT_EXIT_LIGHT_DURATION
        return min(1.0, progress) * max(0.0, 1 - 2 * self.exit_progress)

    @property
    def entrance_locked(self):
        return self.combat_phase not in ("waiting", "cleared") or self.entrance_progress > 0

    def combat_terrain(self):
        terrain = COMBAT_OPEN_TERRAIN if self.exit_progress > 0 else COMBAT_TERRAIN
        return (*terrain, COMBAT_ENTRANCE_BARRIER) if self.entrance_locked else terrain

    def allows_relic_destination(self, destination):
        return (destination is None or self.room != "combat" or not self.entrance_locked
                or destination[0] >= COMBAT_ENTRANCE_BARRIER[2])

    def update_relic_seal(self, player, now):
        if self.in_lower_route and self.route_a.update_seal(player, now):
            player.terrain = self.route_connection.terrain

    def enter(self, player, camera, *, from_right=False, shaft_offset=None, seal_open=False):
        self.shaft_visibility = 0.0
        self.wall_effects.clear()
        self.wall_effects.progress = self.entrance_progress
        self.projectiles.clear()
        self.hit_impacts.clear()
        for golem in self.golems:
            golem.attack_time = None
            golem.attack_target = None
        if self.in_lower_route:
            if self.route_a is None:
                self.route_a = LowerRouteA(A_ORIGIN, seal_open=seal_open)
            if self.route_b is None:
                self.route_b = LowerRouteB()
            if self.route_c is None:
                self.route_c = LowerRouteC()
            if self.route_connection is None:
                self.route_connection = LowerRouteConnection(self.route_a)
            if self.room == "route_a":
                self.route_a.enter(player, shaft_offset=shaft_offset)
            elif self.room == "route_b":
                self.route_b.enter(player)
            player.world_left = camera.world_left = C_LEFT
            player.world_width = camera.world_width = self.route_a.world_width
            player.terrain = self.route_connection.terrain
            player.ground_y = self.route_connection.ground_y
            if self.room == "route_c":
                player.recover_at(*C_CHECKPOINT)
                player.facing = -1
            camera.zoom = camera.normal_zoom
            self.follow_camera(player, camera)
            return
        landing = self.room == "landing"
        width = self.landing_width if landing else (COMBAT_WIDTH if self.room == "combat" else GALLERY_WIDTH)
        player.world_left = camera.world_left = 0
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
        if self.in_lower_route and self.route_connection is not None:
            # The section name selects a checkpoint and hazard rules, not a room load.
            if player.x < C_RIGHT:
                self.room = "route_c"
                self.route_c.check_arrival(player)
            else:
                self.room = "route_a" if player.x >= PASSAGE_CENTER else "route_b"
            camera.follow(player.x)
            view_height = self.cave.height / camera.zoom
            camera.y = self.route_connection.blend(
                player.x, self.route_b.camera_y(player.y, view_height), self.route_a.camera_y(player.y, view_height))
            return
        if self.route is not None:
            self.route.follow_camera(player, camera, self.cave.height)
            return
        camera.follow(player.x)
        if self.room in ("gallery", "combat"):
            base = -self.cave.height * 0.20 / camera.zoom
            if self.room == "combat" and self.exit_progress > 0 and player.y < 0:
                camera.y = max(COMBAT_SHAFT_FLOOR + base, player.y + base)
                return
            camera.y = max(base, player.y - self.cave.height * 0.40 / camera.zoom)
            if self.room == "combat" and self.exit_cue_time and not self.exit_open:
                pan = min(1.0, self.exit_cue_time / COMBAT_EXIT_QUIET_DURATION)
                weight = pan * pan * (3 - 2 * pan) * (1 - self.exit_progress)
                # Bring the seam into view from the upper platform while keeping the hero in frame.
                seam_view = max(base / 2, player.y - self.cave.height * .80 / camera.zoom)
                camera.y += min(0.0, seam_view - camera.y) * weight

    def route_camera_bounds(self, x):
        if self.route_connection is None:
            return self.route.camera_bottom, self.route.camera_top
        blend = self.route_connection.blend
        return (blend(x, self.route_b.camera_bottom, self.route_a.camera_bottom),
                blend(x, self.route_b.camera_top, self.route_a.camera_top))

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
        if (self.room == "gallery" and self.has_relic
                and direction > 0 and player.x >= GALLERY_WIDTH - ROOM_EDGE):
            self.room = "combat"
            self.enter(player, camera)
        elif self.room == "combat" and self.exit_open and player.y <= COMBAT_ROUTE_SEAM:
            shaft_offset = player.x - COMBAT_CENTER_X
            self.room = "route_a"
            self.enter(player, camera, shaft_offset=shaft_offset)
        elif (self.room == "combat" and not self.entrance_locked
              and direction < 0 and player.x <= ROOM_EDGE):
            self.room = "gallery"
            self.enter(player, camera, from_right=True)
        if self.in_lower_route:
            for route in (self.route_a, self.route_b):
                if route is not None:
                    route.update(player, dt)
        self.follow_camera(player, camera)

    def draw(self, camera):
        if self.room == "landing":
            shaft = self.cave.shaft
            bottom = SHAFT_TOP - SHAFT_FLOOR - shaft.h * SHAFT_SCALE
            shaft.draw_to_origin(*camera.world_to_screen(0, bottom),
                                 self.landing_width * camera.zoom, shaft.h * SHAFT_SCALE * camera.zoom)
            return
        if self.in_lower_route:
            self.draw_lower_route(camera)
            return
        if self.room == "combat":
            pico.draw_rectangle(0, 0, self.cave.width, self.cave.height, 0, 0, 0, filled=True)
            scenery = self.art.combat_scenery()
            scenery.draw_background(camera, COMBAT_LEFT_WALL, COMBAT_RIGHT_WALL,
                                    COMBAT_CEILING_Y, broken=self.exit_progress > 0)
            self.art.draw_motes(camera, 0, COMBAT_CEILING_Y,
                                left=COMBAT_LEFT_WALL, right=COMBAT_RIGHT_WALL,
                                count=8, opacity_scale=.45)
            scenery.draw_terrain(camera, COMBAT_PLATFORMS, COMBAT_EXIT_LEFT, COMBAT_EXIT_RIGHT, COMBAT_CEILING_Y,
                                 broken=self.exit_progress > 0)
            scenery.draw_floor_plants(camera, COMBAT_LEFT_WALL, COMBAT_RIGHT_WALL, COMBAT_CEILING_Y)
            self.draw_combat_gate(camera)
            self.wall_effects.draw(camera)
            if self.combat_phase in ("golems", "cleared"):
                for golem in self.golems:
                    golem.draw(self.golem_walk, camera, self.golem_attack,
                               self.golem_emergence, self.golem_death)
            if self.combat_phase in ("pillbugs", "golems", "cleared"):
                for bug in self.combat_pillbugs:
                    bug.draw(self.crawl, self.attack_poses, camera, self.hurt_poses,
                             self.pillbug_emergence, self.pillbug_death)
            for projectile in self.projectiles:
                projectile.draw(self.crystal_image, camera)
            return
        self.art.draw_background(camera)
        self.art.draw_motes(camera, 0, GALLERY_CEILING_Y, right=GALLERY_WIDTH)
        self.shrine.draw_stone(camera, RELIC_X)
        self.art.draw_pillar(camera, PILLAR)
        self.art.draw_floor(camera, 0, GALLERY_WIDTH, 0)
        self.art.shadow_floor(camera, 0)
        self.art.draw_platform(camera, AIR_PLATFORM)
        # Light the scenery first so additive shafts cannot wash out the relic sprite.
        self.shrine.draw_light(camera, RELIC_X, RELIC_Y, GALLERY_CEILING_Y,
                               collected=self.has_relic)
        for bug in self.pillbugs:
            bug.draw(self.crawl, self.attack_poses, camera, self.hurt_poses, death=self.pillbug_death)

    def draw_lower_route(self, camera):
        route_a, route_b, route_c = self.route_a, self.route_b, self.route_c
        draw_a = route_a is not None and camera.x + camera.view_width > route_a.origin[0]
        backdrop_right = A_ORIGIN[0] if self.route_connection is not None else B_ROUTE_WIDTH
        draw_b = route_b is not None and camera.x < backdrop_right
        draw_c = route_c is not None and camera.x < C_RIGHT
        if draw_b:
            route_b.draw(camera, self.cave.height, passage_left=C_LEFT if route_c is not None else C_RIGHT,
                         backdrop_right=backdrop_right,
                         draw_entry=self.route_connection is None)
        if route_c is not None:
            route_c.draw(camera, self.cave.height)
        if draw_a:
            route_a.draw(camera)
        if self.route_connection is not None:
            self.route_connection.draw(camera, self.cave.height)
        for route, visible in ((route_a, draw_a), (route_c, draw_c)):
            if visible:
                for bug in route.enemies:
                    bug.draw(self.crawl, self.attack_poses, camera, self.hurt_poses,
                             self.pillbug_emergence, self.pillbug_death)
        if draw_b:
            route_b.pillbug.draw(self.crawl, self.attack_poses, camera, self.hurt_poses,
                                 self.pillbug_emergence, self.pillbug_death)
            route_b.shield.draw(camera)

    def update_enemies(self, player, dt):
        route_b = self.route_b if self.in_lower_route else None
        b_enemies = ()
        if route_b is not None:
            route_b.activate_enemies(player)
            b_enemies = route_b.enemies
        if self.enemies:
            strike = None
            downward = False
            facing = player.attack_facing
            if player.slash is not None:
                _, facing, kind = player.slash
                downward = kind == "air_down_attack"
                bounds = downward_slash_bounds if downward else forward_slash_bounds
                strike = bounds(player.x, player.y, facing)
            for enemy in self.enemies:
                if strike is not None:
                    body = enemy.body_bounds()
                    if route_b is not None and enemy is route_b.shield:
                        hit = enemy.check_strike(strike, player.x, player.attack_power, player.swing_id)
                    else:
                        hit = enemy.check_strike(strike, facing, player.attack_power, player.swing_id)
                    if hit:
                        self.hit_impacts.append(HitImpact.from_strike(
                            strike, body, facing, downward=downward, heavy=isinstance(enemy, CrystalGolem)))
                        player.recoil_from_hit(facing, player.swing_id)
                target = route_b.enemy_target(enemy, player) if enemy in b_enemies else player.get_hitbox()
                projectile = enemy.update(dt, target, player.terrain, player.world_width)
                if projectile is not None:
                    self.projectiles.append(projectile)
        if self.room == "combat":
            self.update_combat_encounter(player, dt)
            player.terrain = self.combat_terrain()

    def update_combat_encounter(self, player, dt):
        if (self.combat_phase == "waiting"
                and abs(player.x - COMBAT_CENTER_X) <= COMBAT_TRIGGER_RADIUS):
            self.combat_phase = "closing"
        if self.combat_phase == "closing":
            self.entrance_progress = min(1.0, self.entrance_progress + dt / COMBAT_GATE_DURATION)
            if self.entrance_progress >= 1.0:
                self.combat_phase = "pillbugs"
                for bug in self.combat_pillbugs:
                    bug.begin_emergence()
        elif self.combat_phase == "pillbugs" and all(bug.hp == 0 for bug in self.combat_pillbugs):
            self.combat_phase = "golems"
            for golem in self.golems:
                golem.begin_emergence()
        elif self.combat_phase == "golems" and all(golem.hp == 0 for golem in self.golems):
            self.combat_phase = "cleared"
        if self.combat_phase == "cleared":
            cue_step = min(dt, COMBAT_EXIT_DELAY - self.exit_cue_time)
            self.exit_cue_time += cue_step
            opening_step = dt - cue_step
            self.entrance_progress = max(0.0, self.entrance_progress - opening_step / COMBAT_GATE_DURATION)
            self.exit_progress = min(1.0, self.exit_progress + opening_step / COMBAT_EXIT_DURATION)
            if self.exit_progress > 0:
                player.ground_y = COMBAT_SHAFT_FLOOR

    def update_effects(self, dt, player):
        for impact in self.hit_impacts:
            impact.age += dt
        self.hit_impacts[:] = [impact for impact in self.hit_impacts if impact.age < IMPACT_DURATION]
        if self.in_lower_route and self.route_a is not None:
            self.route_a.update_shadow(player, dt)
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
        # Light follows the player's approach after the floor collapses.
        change = dt / .7
        self.shaft_visibility += max(-change, min(change, target - self.shaft_visibility))

    def draw_hit_impacts(self, camera):
        for impact in self.hit_impacts:
            impact.draw(camera)

    def draw_combat_gate(self, camera):
        if self.room == "combat" and self.entrance_progress > 0:
            self.art.combat_scenery().draw_gate(camera, COMBAT_ENTRANCE_BARRIER, self.entrance_progress)

    def draw_combat_exit(self, camera):
        if self.room != "combat":
            return
        scenery = self.art.combat_scenery()
        if self.exit_progress > 0:
            scenery.draw_shaft(camera, COMBAT_EXIT_LEFT, self.shaft_visibility)
            if not self.exit_open:
                scenery.draw_collapse(camera, COMBAT_EXIT_LEFT, COMBAT_EXIT_RIGHT,
                                      self.exit_progress * COMBAT_EXIT_DURATION)
        light = self.exit_seam_light
        if light > 0:
            scenery.draw_exit_seam(camera, COMBAT_EXIT_LEFT, light)
            scenery.draw_exit_seam(camera, COMBAT_EXIT_RIGHT, light * .55)

    def update_projectiles(self, player, health, dt, now):
        if self.in_lower_route and self.route_b is not None:
            self.route_b.check_enemy_attack(player, health, now)
        if self.room != "combat":
            return
        target = player.get_hitbox()
        for projectile in self.projectiles:
            impact = projectile.update(dt, player.terrain, player.world_width, target,
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
            self.art.combat_scenery().draw_foreground(camera, COMBAT_LEFT_WALL,
                                                     COMBAT_RIGHT_WALL, COMBAT_CEILING_Y)
        elif self.room == "gallery":
            self.art.draw_canopy(camera, GALLERY_CEILING_Y)
        elif self.in_lower_route and self.route_a is not None:
            self.route_a.draw_foreground(camera)
            if self.route_connection is not None:
                self.route_connection.draw_foreground(camera, self.cave.height)
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

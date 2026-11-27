"""Operate the two wall rails in the B1 shell puzzle."""

from pico2d import pico2d as pico

from player import STANDING_HITBOX_HEIGHT
from rail import RAIL_CARRIAGE_IMAGE, RAIL_MOUNT_RADIUS, RailCarriage, RailSegment
from tools.b1_combat_terrain import LEDGES, RAIL_CENTERS
from tools.b1_room_art import WORLD_PER_ART_PIXEL
from tools.preview_b1_intro import GROUND


SCALE = WORLD_PER_ART_PIXEL


class B1PuzzleRails:
    def __init__(self):
        from main import RELIC_IMAGE, draw_relic

        self.mount = pico.load_image(str(RAIL_CARRIAGE_IMAGE))
        self.relic = pico.load_image(str(RELIC_IMAGE))
        self.draw_relic = draw_relic
        outer_ledges = LEDGES[0], LEDGES[-1]
        top_bracket_y = outer_ledges[0][2] + 28, outer_ledges[-1][4] - 24
        self.landings = tuple((x * SCALE, (GROUND - ledge[2]) * SCALE)
                              for x, ledge in zip(RAIL_CENTERS, outer_ledges))
        self.carriages = tuple(
            RailCarriage((RailSegment(
                (x, STANDING_HITBOX_HEIGHT / 2),
                (x, (GROUND - bracket_y - 17) * SCALE),
            ),), self.mount.w * SCALE, self.mount.h * SCALE)
            for (x, _), bracket_y in zip(self.landings, top_bracket_y)
        )
        self.reset()

    def reset(self):
        for carriage in self.carriages:
            carriage.distance = 0.0
            carriage.direction = 0
            carriage.relic_mounted = False
            carriage.hit_by_swing = False
        self.active = None

    def _nearby_rail(self, player):
        if not player.grounded or player.y != player.ground_y:
            return None
        return next((i for i, (x, _) in enumerate(self.landings)
                     if abs(player.x - x) <= RAIL_MOUNT_RADIUS), None)

    def can_interact(self, player):
        return self._nearby_rail(player) is not None

    def prompt(self, player):
        index = self._nearby_rail(player)
        if index is None:
            return None
        carriage = self.carriages[index]
        if carriage is not self.active:
            return "mount"
        if carriage.distance == carriage.length:
            return "travel"
        if carriage.distance == 0 and carriage.direction == 0:
            return "send"
        return None

    def interact(self, player, *, teleport=None):
        """Mount a nearby rail or report a successful ascent."""
        index = self._nearby_rail(player)
        if index is None:
            return False
        carriage = self.carriages[index]
        if carriage is not self.active:
            self.reset()
            carriage.relic_mounted = True
            self.active = carriage
            return False
        if carriage.distance != carriage.length:
            return False
        landing = (*self.landings[index], 0)
        arrived = player.recover_at(*landing) if teleport is None else teleport(landing)
        if arrived:
            self.reset()
        return arrived

    def advance(self, player, dt):
        carriage = self.active
        if carriage is None:
            return
        if carriage.distance == 0 and carriage.direction == 0:
            carriage.check_attack(player)
            if carriage.direction:
                # Both faces of a vertical dock send the relic upward.
                carriage.direction = 1
        carriage.move(dt)

    def draw(self, camera, *, enabled):
        idle_y = (GROUND - 389 - self.mount.h / 2) * SCALE
        scale = SCALE * camera.zoom
        for carriage, (dock_x, _) in zip(self.carriages, self.landings):
            x, y = carriage.position if enabled else (dock_x, idle_y)
            self.mount.draw(*camera.world_to_screen(x, y), self.mount.w * scale,
                            self.mount.h * scale)
            if enabled and carriage.relic_mounted:
                self.draw_relic(self.relic, camera, x, y, None)

    def close(self):
        self.mount = self.relic = None

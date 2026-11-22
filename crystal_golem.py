"""Slow crystal-golem patrol, charged back-crystal attack, and sword damage."""

from crystal_projectile import CrystalProjectile
from death_pixels import draw_blue_pixels


MAX_HP = 65
WALK_SPEED = 22.0
BODY_WIDTH = 140
BODY_HEIGHT = 140
ATTACK_RANGE = 1400.0
ATTACK_RELEASE = 0.72
ATTACK_DURATION = 1.44
ATTACK_COOLDOWN = 2.0
EMERGE_DURATION = 1.92
EMERGE_ATTACK_DELAY = .65
DEATH_COLLAPSE_DURATION = 1.28
DEATH_DURATION = DEATH_COLLAPSE_DURATION + .72


class CrystalGolem:
    def __init__(self, left, right, *, direction=-1):
        self.left, self.right = left, right
        self.x = (left + right) / 2
        self.floor_y = 0
        self.direction = direction
        self.hp = MAX_HP
        self.phase = "active"
        self.time = 0.0
        self.last_swing = None
        self.death_time = None
        self.attack_time = None
        self.attack_target = None
        self.attack_cooldown = 1.0 if direction < 0 else 1.7
        self.fired = False

    @classmethod
    def on_platform(cls, platform, *, direction=-1):
        left, _, right, top = platform
        golem = cls(left + BODY_WIDTH / 2, right - BODY_WIDTH / 2, direction=direction)
        golem.floor_y = top
        return golem

    def body_bounds(self):
        return self.x, self.floor_y, BODY_WIDTH, BODY_HEIGHT

    def begin_emergence(self):
        if self.hp == 0 or self.phase == "emerge":
            return
        self.phase, self.time = "emerge", 0.0
        self.attack_time = None
        self.attack_target = None
        self.fired = False

    def check_strike(self, box, facing, damage, swing_id):
        if box is None or self.hp == 0 or self.phase == "emerge" or self.last_swing == swing_id:
            return False
        left, bottom, right, top = box
        if (right <= self.x - BODY_WIDTH / 2 or left >= self.x + BODY_WIDTH / 2
                or top <= self.floor_y or bottom >= self.floor_y + BODY_HEIGHT):
            return False
        self.hp = max(0, self.hp - damage)
        self.last_swing = swing_id
        if self.hp == 0:
            self.phase, self.death_time = "death", 0.0
            self.attack_time = None
            self.attack_target = None
        return True

    def update(self, dt, player_box, terrain, world_width):
        if self.death_time is not None:
            self.death_time = min(DEATH_DURATION, self.death_time + max(0, dt))
            return
        if self.hp == 0 or dt <= 0:
            return
        if self.phase == "emerge":
            self.time += dt
            if self.time >= EMERGE_DURATION:
                self.phase, self.time = "active", 0.0
                self.attack_cooldown = max(EMERGE_ATTACK_DELAY, self.attack_cooldown)
            return
        if self.attack_time is not None:
            previous = self.attack_time
            self.attack_time += dt
            projectile = None
            if not self.fired and previous < ATTACK_RELEASE <= self.attack_time:
                self.fired = True
                projectile = CrystalProjectile.aimed(
                    (self.x - self.direction * 20, self.floor_y + 128), self.attack_target)
            if self.attack_time >= ATTACK_DURATION:
                self.attack_time = None
                self.attack_cooldown = ATTACK_COOLDOWN
            return projectile
        self.attack_cooldown = max(0.0, self.attack_cooldown - dt)
        if len(player_box) == 4 and self.attack_cooldown == 0:
            left, bottom, right, top = player_box
            target = (left + right) / 2, (bottom + top) / 2
            if 100 <= abs(target[0] - self.x) <= ATTACK_RANGE:
                self.direction = 1 if target[0] > self.x else -1
                self.attack_time = 0.0
                self.attack_target = target
                self.fired = False
                return
        requested_distance = self.direction * WALK_SPEED * dt
        distance = requested_distance
        start = self.x
        left, right = self.x - BODY_WIDTH / 2, self.x + BODY_WIDTH / 2
        for x1, y1, x2, y2 in terrain:
            if self.floor_y >= y2 or self.floor_y + BODY_HEIGHT <= y1:
                continue
            if distance > 0 and right <= x1 and right + distance >= x1:
                distance = min(distance, x1 - right)
            elif distance < 0 and left >= x2 and left + distance <= x2:
                distance = max(distance, x2 - left)
        low, high = max(BODY_WIDTH / 2, self.left), min(world_width - BODY_WIDTH / 2, self.right)
        self.x = max(low, min(high, self.x + distance))
        # Only real collision clipping or reaching a patrol edge can turn us.
        # Subtracting large coordinates introduces tiny float errors in free motion.
        if distance != requested_distance or self.x in (low, high):
            self.direction *= -1
        if self.x != start:
            self.time += dt

    def draw(self, animation, camera, attack_animation=None, emergence=None, death=None):
        if self.death_time is not None:
            if death is not None and self.death_time < DEATH_DURATION:
                if self.death_time < DEATH_COLLAPSE_DURATION:
                    death.draw(self.x, self.floor_y, -self.direction, self.death_time, camera)
                else:
                    draw_blue_pixels(death, camera, self.x, self.floor_y, -self.direction,
                                     self.death_time - DEATH_COLLAPSE_DURATION)
            return
        if self.hp == 0:
            return
        if self.phase == "emerge":
            if emergence is not None:
                emergence.draw(self.x, self.floor_y, -self.direction, self.time, camera)
            return
        if self.attack_time is not None and attack_animation is not None:
            attack_animation.draw(self.x, self.floor_y, -self.direction, self.attack_time,
                                  camera)
        else:
            animation.draw(self.x, self.floor_y, -self.direction, self.time, camera)

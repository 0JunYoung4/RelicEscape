"""Slow crystal-golem patrol, charged back-crystal attack, and sword damage."""

from crystal_projectile import CrystalProjectile


MAX_HP = 65
WALK_SPEED = 22.0
BODY_WIDTH = 140
BODY_HEIGHT = 140
HURT_TIME = 0.20
ATTACK_RANGE = 1400.0
ATTACK_RELEASE = 0.72
ATTACK_DURATION = 1.44
ATTACK_COOLDOWN = 2.0
EMERGE_DURATION = 1.92
EMERGE_ATTACK_DELAY = .65


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
        self.hurt_remaining = 0.0
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
        self.hurt_remaining = 0.0
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
        self.hurt_remaining = HURT_TIME
        # A sword hit interrupts concentration before the release event.
        self.attack_time = None
        self.attack_target = None
        self.attack_cooldown = ATTACK_COOLDOWN
        return True

    def update(self, dt, player_box, terrain, world_width):
        if self.hurt_remaining > 0:
            paused = min(dt, self.hurt_remaining)
            self.hurt_remaining -= paused
            dt -= paused
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

    def draw(self, animation, camera, attack_animation=None, emergence=None):
        if self.hp == 0 and self.hurt_remaining <= 0:
            return
        if self.phase == "emerge":
            if emergence is not None:
                emergence.draw(self.x, self.floor_y, -self.direction, self.time, camera)
            return
        tint = (255, 185, 165) if self.hurt_remaining > 0 else None
        if self.attack_time is not None and attack_animation is not None:
            attack_animation.draw(self.x, self.floor_y, -self.direction, self.attack_time,
                                  camera, tint=tint)
        else:
            animation.draw(self.x, self.floor_y, -self.direction, self.time, camera, tint=tint)

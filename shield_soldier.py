"""The stone guard's frontal block and short shield bash."""

import json

from enemy_knockback import KNOCKBACK_DURATION, advance_knockback
from player import ASSET_ROOT, Animation


BODY_WIDTH, BODY_HEIGHT = 96, 120
MAX_HP = 65
BASH_DAMAGE = 15
BASH_REACH = 126
WALK_SPEED = 54
KNOCKBACK_DISTANCE = 45.0
KNOCKBACK_SPEED = 2 * KNOCKBACK_DISTANCE / KNOCKBACK_DURATION
REAR_OPENING = 1.5
TURN_COOLDOWN = .55


def load_pose(version):
    folder = ASSET_ROOT / "sprites/enemies"
    data = json.loads((folder / f"shield-stone-soldier-{version}.json").read_text(encoding="utf-8"))
    animation = Animation(folder / data["image"], data["frames"], data["foot_anchor"],
                          data["scale"], data["fps"], data["frame_durations_ms"])
    return animation, data


class ShieldSoldier:
    def __init__(self, x, floor_y, left, right, *, support_edges=None):
        self.x, self.floor_y = x, floor_y
        self.left, self.right = left, right
        self.direction = 1
        self.hp = MAX_HP
        self.last_swing = None
        self.knockback_remaining = 0.0
        self.strike_direction = 1
        self.support_edges = support_edges
        self.walk_time = 0.0
        self.block_time = None
        self.bash_time = None
        self.bash_hit = False
        self.cooldown = TURN_COOLDOWN
        self.rear_time = 0.0
        self.walk, _ = load_pose("walk-right-v2")
        self.block, _ = load_pose("block-right-v1")
        self.bash, data = load_pose("bash-right-v1")
        self.bash_start = data["contact_start_ms"] / 1000
        self.bash_end = data["contact_end_ms"] / 1000

    def body_bounds(self):
        return self.x, self.floor_y, BODY_WIDTH, BODY_HEIGHT

    def check_strike(self, box, attacker_x, damage, swing_id):
        if self.hp == 0 or self.last_swing == swing_id or box is None:
            return False
        left, bottom, right, top = box
        if (right <= self.x - BODY_WIDTH / 2 or left >= self.x + BODY_WIDTH / 2
                or bottom >= self.floor_y + BODY_HEIGHT or top <= self.floor_y):
            return False
        self.last_swing = swing_id
        if (attacker_x - self.x) * self.direction >= 0:
            if self.bash_time is None:
                self.block_time = 0.0
            return False
        self.hp = max(0, self.hp - damage)
        if self.hp > 0:
            self.knockback_remaining = KNOCKBACK_DURATION
            self.strike_direction = self.direction
            self._turn_around()
        else:
            self.knockback_remaining = 0.0
        return True

    def _turn_around(self):
        self.direction *= -1
        self.rear_time = 0.0
        self.block_time = None
        self.bash_time = None
        self.cooldown = max(self.cooldown, TURN_COOLDOWN)

    def update(self, dt, player_box, terrain, world_width):
        if self.hp == 0:
            return
        walk_time = dt
        if self.knockback_remaining > 0:
            step = min(dt, self.knockback_remaining)
            push, self.knockback_remaining = advance_knockback(
                step, self.knockback_remaining, self.strike_direction, self.body_bounds(),
                terrain, world_width, self.support_edges, speed=KNOCKBACK_SPEED,
            )
            if push:
                self.x += push
                self.left, self.right = min(self.left, self.x), max(self.right, self.x)
                walk_time -= step
        target_x = (player_box[0] + player_box[2]) / 2 if player_box else self.x
        dx = target_x - self.x
        behind = dx * self.direction < 0
        self.rear_time = self.rear_time + dt if behind else 0.0
        if self.rear_time >= REAR_OPENING:
            self._turn_around()
            return
        if self.bash_time is not None:
            self.bash_time += dt
            if self.bash_time >= self.bash.duration:
                self.bash_time = None
                self.cooldown = .92
            return
        if self.block_time is not None:
            self.block_time += dt
            if self.block_time >= self.block.duration:
                self.block_time = None
            return
        if not player_box or behind:
            return
        self.cooldown = max(0, self.cooldown - dt)
        if abs(dx) <= BASH_REACH and self.cooldown == 0:
            self.bash_time = 0.0
            self.bash_hit = False
        elif abs(dx) > 78:
            step = min(WALK_SPEED * walk_time, abs(dx) - 78)
            x = max(self.left, min(self.right, self.x + self.direction * step))
            if x != self.x:
                self.x = x
                self.walk_time += walk_time

    def bash_contact(self, player_box):
        if (self.hp == 0 or self.bash_hit or self.bash_time is None
                or not self.bash_start <= self.bash_time < self.bash_end):
            return None
        left, bottom, right, top = player_box
        front = self.x + self.direction * BASH_REACH
        if (right <= min(self.x, front) or left >= max(self.x, front)
                or bottom >= self.floor_y + 105 or top <= self.floor_y + 30):
            return None
        self.bash_hit = True
        return max(left, min(front, right)), self.floor_y + 76

    def draw(self, camera):
        if self.hp == 0:
            return
        if self.bash_time is not None:
            animation, elapsed = self.bash, self.bash_time
        elif self.block_time is not None:
            animation, elapsed = self.block, self.block_time
        else:
            animation, elapsed = self.walk, self.walk_time
        animation.draw(self.x, self.floor_y, self.direction, elapsed, camera)

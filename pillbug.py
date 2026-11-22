"""Ground patrol, rolling charge and overturn animation for the stone pillbug."""

from math import hypot, pi, sin, sqrt
from pico2d import pico2d as pico


BODY_LENGTH = 164
NOTICE_DISTANCE = BODY_LENGTH * 1.7
MAX_ROLL = BODY_LENGTH * 3
RADIUS = 50
CRAWL_SPEED = 28
ROLL_SPEED = 485
CURL_TIME = 0.24
FLIP_TIME = 0.52
POSE_SIZES = ((120, 102), (100, 100), (136, 102), (164, 76))
HURT_TIME = .28
MAX_HP = 30


class Pillbug:
    def __init__(self, left, right, offset):
        self.left, self.right = left, right
        self.x = right - offset * CRAWL_SPEED
        self.direction = -1
        self.phase = "crawl"
        self.time = offset
        self.rolled = 0.0
        self.hit = False
        self.hp = MAX_HP
        self.last_swing = None
        self.hurt_remaining = 0.0
        self.strike_direction = 1
        self.floor_y = 0
        self.support_edges = None

    @classmethod
    def on_platform(cls, bounds):
        left, _, right, top = bounds
        bug = cls(left + BODY_LENGTH / 2, right - BODY_LENGTH / 2, 0)
        bug.floor_y = top
        bug.support_edges = (left, right)
        return bug

    def check_strike(self, box, facing, damage, swing_id):
        if box is None or self.hp == 0 or self.last_swing == swing_id:
            return
        x, bottom, width, height = self.body_bounds()
        left, low, right, high = box
        if left < x + width / 2 and right > x - width / 2 and low < bottom + height and high > bottom:
            self.last_swing = swing_id
            self.hp = max(0, self.hp - damage)
            self.hurt_remaining = HURT_TIME
            self.strike_direction = facing

    def _clearance(self, box):
        """Horizontal travel before the rolling circle first touches a solid box."""
        left, bottom, right, top = box
        center_y = self.floor_y + RADIUS
        dy = max(bottom - center_y, center_y - top, 0)
        if dy >= RADIUS:  # Ground directly beneath the shell supports the roll.
            return float("inf")
        reach = sqrt(RADIUS ** 2 - dy ** 2)
        if self.direction < 0:
            near, far = self.x - right, self.x - left
        else:
            near, far = left - self.x, right - self.x
        return max(0.0, near - reach) if far > -reach else float("inf")

    def update(self, dt, player_box, terrain, world_width):
        if self.hurt_remaining > 0:
            paused = min(dt, self.hurt_remaining)
            self.hurt_remaining -= paused
            dt -= paused
            if dt <= 0:
                return
        if self.hp == 0 or self.phase == "overturned":
            return
        if self.phase == "crawl":
            left, bottom, right, top = player_box
            gap_x = max(left - self.x - BODY_LENGTH / 2, self.x - BODY_LENGTH / 2 - right, 0)
            gap_y = max(bottom - self.floor_y - 70, self.floor_y - top, 0)
            below_ledge = self.support_edges is not None and top < self.floor_y
            if below_ledge or hypot(gap_x, gap_y) > NOTICE_DISTANCE:
                self.time += dt
                self.x += self.direction * CRAWL_SPEED * dt
                if self.x <= self.left or self.x >= self.right:
                    self.x = max(self.left, min(self.right, self.x))
                    self.direction *= -1
                return
            self.direction = -1 if (left + right) / 2 < self.x else 1
            self.phase, self.time = "curl", 0.0

        if self.phase == "curl":
            step = min(dt, CURL_TIME - self.time)
            self.time += step
            dt -= step
            if self.time < CURL_TIME:
                return
            self.phase, self.time = "roll", 0.0

        if self.phase == "roll":
            left_edge, right_edge = self.support_edges or (0, world_width)
            wall = self.x - RADIUS - left_edge if self.direction < 0 else right_edge - self.x - RADIUS
            clearance = min(max(0.0, wall), self._clearance(player_box))
            for box in terrain:
                clearance = min(clearance, self._clearance(box))
            limit = min(MAX_ROLL - self.rolled, clearance)
            distance = min(ROLL_SPEED * dt, limit)
            self.x += self.direction * distance
            self.rolled += distance
            if distance < limit:
                return
            self.hit = clearance <= limit
            self.phase, self.time = "flip", 0.0
            dt -= distance / ROLL_SPEED

        self.time += dt
        if self.time >= FLIP_TIME:
            self.phase = "overturned"

    def attack_pose(self):
        pose, angle, lift = 1, -self.direction * self.rolled / RADIUS, 0
        if self.phase == "curl":
            pose = 0 if self.time < CURL_TIME * .72 else 1
        elif self.phase in ("flip", "overturned"):
            t = min(1.0, self.time / FLIP_TIME)
            if t < .23:
                angle -= self.direction * 1.1 * t / .23
            elif t < .70:
                pose, angle = 2, -self.direction * .48 * (1 - (t - .23) / .47)
            else:
                pose, angle = 3, self.direction * .08 * sin(pi * (t - .70) / .30)
            lift = 17 * sin(pi * min(1.0, t / .80))
        width, height = POSE_SIZES[pose]
        # Unfold away from the contact surface while keeping the leading edge fixed.
        x = self.x - self.direction * max(0, width / 2 - RADIUS) if self.hit else self.x
        return pose, angle, x, self.floor_y + lift, width, height

    def body_bounds(self):
        if self.phase == "crawl":
            return self.x, self.floor_y, BODY_LENGTH, 70
        _, _, x, lift, width, height = self.attack_pose()
        return x, lift, width, height

    def draw(self, crawl, poses, camera, hurt_poses):
        if 0 < self.hp < MAX_HP:
            x, lift, _, height = self.body_bounds()
            sx, sy = map(round, camera.world_to_screen(x, lift + height + 20))
            pico.draw_rectangle(sx-16, sy-2, sx+16, sy+2, 16, 29, 30, filled=True)
            pico.draw_rectangle(sx-15, sy-1, sx-15+round(30*self.hp/MAX_HP), sy+1, 184, 197, 128, filled=True)
        if self.hurt_remaining > 0:
            self.draw_hurt(poses, hurt_poses, camera)
            return
        if self.hp == 0:
            return
        if self.phase == "crawl":
            crawl.draw(self.x, self.floor_y, -self.direction, self.time, camera)
            return
        pose, angle, x, lift, width, height = self.attack_pose()
        poses.clip_composite_draw(pose * 168, 0, width, height, angle,
                                  "h" if self.direction > 0 else "",
                                  *camera.world_to_screen(x, lift + height / 2),
                                  width * camera.zoom, height * camera.zoom)

    def draw_hurt(self, poses, hurt_poses, camera):
        x, lift, width, height = self.body_bounds()
        t = 1 - self.hurt_remaining / HURT_TIME
        kick = sin(pi * min(1, t * 1.6))
        side = self.strike_direction
        flip = "h" if self.direction > 0 else ""
        if self.phase == "roll" or (self.phase == "flip" and self.time < .23 * FLIP_TIME):
            art, source_x, w, h = poses, 168, 100, 100
            angle = -self.direction * self.rolled / RADIUS
        else:
            upside_down = self.phase in ("flip", "overturned")
            art, source_x, w, h = hurt_poses, 160 if upside_down else 0, 160, 86
            angle = 0
        art.clip_composite_draw(source_x, 0, w, h, angle - side * .18 * kick, flip,
                                *camera.world_to_screen(x + side * 8 * kick, lift + height / 2 + 9 * kick),
                                width * camera.zoom, (height + 6 * kick) * camera.zoom)
        for vx, vy, size, color in ((-54, 108, 4, (161, 173, 170)), (82, 150, 3, (177, 178, 112)),
                                    (39, 78, 3, (92, 118, 64)), (-96, 55, 2, (148, 166, 167))):
            age = HURT_TIME - self.hurt_remaining
            px, py = camera.world_to_screen(x - side * width * .32 + side * vx * age,
                                            lift + height * .76 + vy * age - 330 * age ** 2)
            radius = max(0, round(size * camera.zoom * (1 - t)))
            pico.draw_rectangle(round(px)-radius, round(py)-radius, round(px)+radius, round(py)+radius,
                                *color, filled=True)

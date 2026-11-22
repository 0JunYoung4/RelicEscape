"""Patrol, rolling charge, overturning and recovery for the stone pillbug."""

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
OVERTURNED_TIME = 1.25
RIGHTING_TIME = 0.52
ATTACK_COOLDOWN = 0.65
POSE_SIZES = ((120, 102), (100, 100), (136, 102), (164, 76))
HURT_TIME = .28
MAX_HP = 30
EMERGE_DURATION = 1.6
DEATH_CURL_DURATION = .64
DEATH_SCATTER_DURATION = .72
DEATH_DURATION = DEATH_CURL_DURATION + DEATH_SCATTER_DURATION
DEATH_PIXEL_SIZE = 8.0
DEATH_PIXEL_COLORS = ((40, 125, 255), (65, 170, 255), (100, 205, 255), (155, 230, 255))


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
        self.attack_cooldown = 0.0
        self.death_time = None
        self.death_flipped = False
        self.death_first_frame = 0

    @classmethod
    def on_platform(cls, bounds):
        left, _, right, top = bounds
        bug = cls(left + BODY_LENGTH / 2, right - BODY_LENGTH / 2, 0)
        bug.floor_y = top
        bug.support_edges = (left, right)
        return bug

    def check_strike(self, box, facing, damage, swing_id):
        if box is None or self.hp == 0 or self.phase == "emerge" or self.last_swing == swing_id:
            return False
        x, bottom, width, height = self.body_bounds()
        left, low, right, high = box
        if left < x + width / 2 and right > x - width / 2 and low < bottom + height and high > bottom:
            self.last_swing = swing_id
            self.hp = max(0, self.hp - damage)
            self.hurt_remaining = HURT_TIME
            self.strike_direction = facing
            if self.hp == 0:
                self.death_flipped = (self.phase in ("flip", "overturned") or
                                      (self.phase == "recover" and self.time < RIGHTING_TIME / 2))
                self.death_first_frame = 7 if self.phase == "roll" else 0
                self.x = x
                self.phase, self.time = "death", 0.0
                self.death_time = 0.0
                self.hurt_remaining = 0.0
            return True
        return False

    def begin_emergence(self):
        if self.hp == 0 or self.phase == "emerge":
            return
        self.phase, self.time = "emerge", 0.0
        self.hurt_remaining = 0.0

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
        if self.death_time is not None:
            self.death_time = min(DEATH_DURATION, self.death_time + max(0, dt))
            return
        if self.hurt_remaining > 0:
            paused = min(dt, self.hurt_remaining)
            self.hurt_remaining -= paused
            dt -= paused
            if dt <= 0:
                return
        if self.hp == 0:
            return
        if self.phase == "emerge":
            self.time += dt
            if self.time >= EMERGE_DURATION:
                self.phase, self.time = "crawl", 0.0
                self.attack_cooldown = ATTACK_COOLDOWN
            return
        if self.phase == "overturned":
            step = min(dt, max(0, OVERTURNED_TIME - self.time))
            self.time += step
            dt -= step
            if self.time < OVERTURNED_TIME:
                return
            self.phase, self.time = "recover", 0.0
        if self.phase == "recover":
            self.time += dt
            if self.time < RIGHTING_TIME:
                return
            if self.hit:
                self.x -= self.direction * (BODY_LENGTH / 2 - RADIUS)
            left, right = self.support_edges or (0, world_width)
            self.x = max(left + BODY_LENGTH / 2, min(right - BODY_LENGTH / 2, self.x))
            self.left, self.right = min(self.left, self.x), max(self.right, self.x)
            self.phase, self.time = "crawl", 0.0
            self.rolled, self.hit = 0.0, False
            self.attack_cooldown = ATTACK_COOLDOWN
            return
        self.attack_cooldown = max(0.0, self.attack_cooldown - dt)
        if self.phase == "crawl":
            left, bottom, right, top = player_box
            gap_x = max(left - self.x - BODY_LENGTH / 2, self.x - BODY_LENGTH / 2 - right, 0)
            gap_y = max(bottom - self.floor_y - 70, self.floor_y - top, 0)
            below_ledge = self.support_edges is not None and top < self.floor_y
            if self.attack_cooldown > 0 or below_ledge or hypot(gap_x, gap_y) > NOTICE_DISTANCE:
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
            self.phase, self.time = "overturned", 0.0

    def attack_pose(self):
        pose, angle, lift = 1, -self.direction * self.rolled / RADIUS, 0
        if self.phase == "curl":
            pose = 0 if self.time < CURL_TIME * .72 else 1
        elif self.phase in ("flip", "overturned", "recover"):
            t = 1.0 if self.phase == "overturned" else min(1.0, self.time / FLIP_TIME)
            if self.phase == "recover":
                t = 1 - min(1.0, self.time / RIGHTING_TIME)
            if t < .23:
                if self.phase == "recover":
                    pose, angle = 0, -self.direction * .45 * t / .23
                else:
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
        if self.phase in ("crawl", "emerge", "death"):
            return self.x, self.floor_y, BODY_LENGTH, 70
        _, _, x, lift, width, height = self.attack_pose()
        return x, lift, width, height

    def draw(self, crawl, poses, camera, hurt_poses, emergence=None, death=None):
        if self.death_time is not None:
            if death is not None and self.death_time < DEATH_DURATION:
                self.draw_death(death, camera)
            return
        if self.phase == "emerge":
            if self.hp > 0 and emergence is not None:
                emergence.draw(self.x, self.floor_y, -self.direction, self.time, camera)
            return
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

    def draw_death(self, animation, camera):
        facing = -self.direction
        flip = ("h" if facing < 0 else "") + ("v" if self.death_flipped else "")
        if self.death_time < DEATH_CURL_DURATION:
            index = max(self.death_first_frame, animation.frame_at(self.death_time))
            frame = animation.frames[index]
            left, top, right, bottom = frame["body_bounds"]
            width, height = right - left, bottom - top
            animation.image.clip_composite_draw(
                frame["x"] + left, animation.image.h - frame["y"] - bottom,
                width, height, 0, flip,
                *camera.world_to_screen(self.x, self.floor_y + height * animation.scale / 2),
                width * animation.scale * camera.zoom, height * animation.scale * camera.zoom)
            return
        # The final curled silhouette breaks into bright blue square pixels.
        frame = animation.frames[-1]
        left, top, right, bottom = frame["body_bounds"]
        elapsed = self.death_time - DEATH_CURL_DURATION
        for column, row, x, y, width, height in frame["pixel_cells"]:
                seed = ((column * 73 + row * 151 + 17) % 251) / 250
                age = max(0, elapsed - .09 * seed)
                if elapsed >= .09 * seed + .43 + .20 * seed:
                    continue
                local_x = (x + width / 2 - (left + right) / 2) * animation.scale
                local_y = ((y + height / 2 - top) if self.death_flipped
                           else (bottom - y - height / 2)) * animation.scale
                spread = local_x / max(1, (right - left) * animation.scale / 2)
                vx = facing * (spread * 110 + (seed - .5) * 48)
                vy = 105 + seed * 130
                px = self.x + facing * local_x + vx * age
                py = self.floor_y + local_y + vy * age - 140 * age ** 2
                screen_x, screen_y = camera.world_to_screen(px, py)
                half_w = width * animation.scale * camera.zoom / 2
                half_h = height * animation.scale * camera.zoom / 2
                color = DEATH_PIXEL_COLORS[(column * 7 + row * 11) % len(DEATH_PIXEL_COLORS)]
                pico.draw_rectangle(round(screen_x - half_w), round(screen_y - half_h),
                                    round(screen_x + half_w) - 1, round(screen_y + half_h) - 1,
                                    *color, filled=True)

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
            upside_down = self.phase in ("flip", "overturned") or (self.phase == "recover" and self.time < RIGHTING_TIME / 2)
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

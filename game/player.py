"""Diana, the player character: forgiving platformer physics."""
import pygame

from .characters import draw_diana
from .settings import (AIR_ACCEL, COYOTE_TIME, FRICTION, GROUND_ACCEL, JUMP_BUFFER,
                       MAX_FALL, PLAYER_H, PLAYER_W, RUN_SPEED)


def approach(value, target, step):
    if value < target:
        return min(value + step, target)
    return max(value - step, target)


class Player:
    def __init__(self, bottom_center):
        self.w, self.h = PLAYER_W, PLAYER_H
        self.reset(bottom_center)

    def reset(self, bottom_center):
        cx, bottom = bottom_center
        self.x = float(cx - self.w // 2)
        self.y = float(bottom - self.h)
        self.vx = self.vy = 0.0
        self.on_ground = False
        self.facing = 1
        self.coyote = 0.0
        self.buffer = 0.0
        self.squash = 0.0      # >0 squashed (landing), <0 stretched (jumping)
        self.run_phase = 0.0

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    def update(self, dt, controls, level, world):
        """Advance physics one step. Returns a set of event names."""
        events = set()

        # Horizontal
        target = controls.move_x * RUN_SPEED
        if controls.move_x:
            self.facing = controls.move_x
            accel = GROUND_ACCEL if self.on_ground else AIR_ACCEL
        else:
            accel = FRICTION if self.on_ground else AIR_ACCEL
        self.vx = approach(self.vx, target, accel * dt)

        # Jump (with coyote time and buffering)
        self.coyote = COYOTE_TIME if self.on_ground else self.coyote - dt
        self.buffer = JUMP_BUFFER if controls.jump_pressed else self.buffer - dt
        if self.buffer > 0 and self.coyote > 0:
            self.vy = -world.jump_speed
            self.buffer = self.coyote = 0
            self.on_ground = False
            self.squash = -0.2
            events.add("jump")

        self.vy = min(self.vy + world.gravity * dt, MAX_FALL)

        self._move_x(dt, level)
        prev_bottom = self.y + self.h
        self._move_y(dt, level, prev_bottom, events)

        # Springs: any downward/resting contact bounces
        if self.vy >= 0:
            r = self.rect
            for s in level.springs:
                if r.colliderect(s.rect):
                    self.y = s.rect.top - self.h
                    self.vy = -world.spring_speed
                    self.on_ground = False
                    self.squash = -0.3
                    s.squash = 1.0
                    events.add("bounce")
                    break
            # Pit trampolines: a fall into a hole bounces Diana back out
            for pad in level.pit_pads:
                if r.colliderect(pad.rect.inflate(0, 40)):
                    self.y = pad.rect.top - self.h
                    self.vy = -world.spring_speed
                    self.on_ground = False
                    self.squash = -0.3
                    pad.squash = 1.0
                    events.add("bounce")
                    break

        # Animation
        if self.on_ground and abs(self.vx) > 10:
            self.run_phase += abs(self.vx) * dt * 0.06
        self.squash = approach(self.squash, 0, dt * 1.5)
        return events

    def _move_x(self, dt, level):
        self.x += self.vx * dt
        self.x = max(0.0, min(level.pixel_w - self.w, self.x))
        r = self.rect
        for t in level.solids_near(r):
            if r.colliderect(t):
                if self.vx > 0:
                    r.right = t.left
                elif self.vx < 0:
                    r.left = t.right
                self.x = float(r.x)
                self.vx = 0

    def _move_y(self, dt, level, prev_bottom, events):
        self.y += self.vy * dt
        r = self.rect
        if self.vy < 0:
            for t in level.solids_near(r):
                if r.colliderect(t):
                    r.top = t.bottom
                    self.y = float(r.y)
                    self.vy = 0
            self.on_ground = False
            return

        # Falling or resting: look for a surface just under the feet
        probe = r.move(0, 1)
        top = None
        for t in level.solids_near(probe):
            if probe.colliderect(t):
                top = t.top if top is None else min(top, t.top)
        for t in level.platforms_near(probe):
            if probe.colliderect(t) and prev_bottom <= t.top + 1:
                top = t.top if top is None else min(top, t.top)
        if top is not None:
            self.y = float(top - self.h)
            if not self.on_ground and self.vy > 300:
                self.squash = min(0.35, self.vy / 3000)
                events.add("land")
            self.vy = 0
            self.on_ground = True
        else:
            self.on_ground = False

    # ---------------------------------------------------------------- drawing
    def draw(self, surf, offset, t):
        ox, oy = offset
        draw_diana(surf, self.x - ox + self.w / 2, self.y - oy + self.h,
                   self.facing, self.squash, self.run_phase, self.on_ground, t)

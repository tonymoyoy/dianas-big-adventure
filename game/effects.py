"""Simple particle effects: sparkles, poofs, confetti and falling snow."""
import math
import random

import pygame

from .settings import HEIGHT, WIDTH, WHITE

CONFETTI = [(255, 90, 90), (255, 200, 60), (90, 200, 120), (80, 160, 255), (200, 110, 255), (255, 140, 200)]


class Particle:
    __slots__ = ("x", "y", "vx", "vy", "life", "max_life", "color", "size", "gravity", "kind", "spin")

    def __init__(self, x, y, vx, vy, life, color, size, gravity=0.0, kind="dot"):
        self.x, self.y, self.vx, self.vy = x, y, vx, vy
        self.life = self.max_life = life
        self.color, self.size, self.gravity, self.kind = color, size, gravity, kind
        self.spin = random.uniform(0, math.tau)


class Particles:
    """World-space particles (drawn with the camera offset)."""

    def __init__(self):
        self.items = []

    def sparkle(self, x, y, color, n=14):
        for i in range(n):
            a = i * math.tau / n + random.uniform(-0.2, 0.2)
            sp = random.uniform(120, 260)
            self.items.append(Particle(x, y, math.cos(a) * sp, math.sin(a) * sp, 0.5, color, 5, 300, "star"))
        self.items.append(Particle(x, y, 0, 0, 0.3, WHITE, 26, 0, "ring"))

    def poof(self, x, y, color=WHITE, n=12):
        for _ in range(n):
            a = random.uniform(0, math.tau)
            sp = random.uniform(40, 140)
            self.items.append(Particle(x, y, math.cos(a) * sp, math.sin(a) * sp - 40, 0.6, color, random.uniform(6, 11)))

    def dust(self, x, y):
        for side in (-1, 1):
            for _ in range(3):
                self.items.append(Particle(x, y, side * random.uniform(40, 110), random.uniform(-60, -20),
                                           0.35, (235, 235, 235), random.uniform(3, 6)))

    def confetti(self, x, y, n=40):
        for _ in range(n):
            a = random.uniform(-math.pi * 0.9, -math.pi * 0.1)
            sp = random.uniform(250, 600)
            self.items.append(Particle(x, y, math.cos(a) * sp, math.sin(a) * sp, random.uniform(1.2, 2.2),
                                       random.choice(CONFETTI), random.uniform(5, 9), 700, "confetti"))

    def update(self, dt):
        alive = []
        for p in self.items:
            p.life -= dt
            if p.life <= 0:
                continue
            p.vy += p.gravity * dt
            if p.kind == "confetti":
                p.vx *= 1 - 1.5 * dt
                p.vy = min(p.vy, 160)
            p.x += p.vx * dt
            p.y += p.vy * dt
            p.spin += dt * 8
            alive.append(p)
        self.items = alive

    def draw(self, surf, offset=(0, 0)):
        ox, oy = offset
        for p in self.items:
            k = p.life / p.max_life
            x, y = p.x - ox, p.y - oy
            if p.kind == "ring":
                r = p.size * (1.6 - k)
                pygame.draw.circle(surf, p.color, (x, y), r, max(1, int(4 * k)))
            elif p.kind == "star":
                s = p.size * k + 1
                pygame.draw.line(surf, p.color, (x - s, y), (x + s, y), 3)
                pygame.draw.line(surf, p.color, (x, y - s), (x, y + s), 3)
            elif p.kind == "confetti":
                w = abs(math.cos(p.spin)) * p.size + 1
                pygame.draw.rect(surf, p.color, (x - w / 2, y - p.size / 2, w, p.size))
            else:
                pygame.draw.circle(surf, p.color, (x, y), max(1, p.size * k))


class Snow:
    """Screen-space snowfall with slight parallax."""

    def __init__(self, n=70):
        self.flakes = [[random.uniform(0, WIDTH), random.uniform(0, HEIGHT), random.uniform(1.5, 4)] for _ in range(n)]
        self.last_cam = None

    def update(self, dt, cam_x, t):
        dx = 0 if self.last_cam is None else cam_x - self.last_cam
        self.last_cam = cam_x
        for f in self.flakes:
            f[1] += (25 + f[2] * 12) * dt
            f[0] += math.sin(t + f[1] * 0.02) * 20 * dt - dx * (f[2] / 4)
            if f[1] > HEIGHT + 5:
                f[1] = -5
                f[0] = random.uniform(0, WIDTH)
            f[0] %= WIDTH

    def draw(self, surf):
        for x, y, s in self.flakes:
            pygame.draw.circle(surf, WHITE, (x, y), s)

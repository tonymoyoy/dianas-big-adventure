"""Drawing for Diana (the player) and her dog (Azulita or Vainilla), plus the puppy's follow logic.

The draw functions take the bottom-center point (cx, bottom) where the feet touch the ground.
"""
import math
from collections import deque

import pygame

from .settings import OUTLINE, WHITE

SKIN = (255, 214, 186)
HAIR = (115, 65, 40)
HAIR_LIGHT = (150, 90, 55)
DRESS = (255, 120, 185)
DRESS_DARK = (225, 75, 150)
SASH = (255, 200, 230)
SHOES = (190, 60, 140)
CROWN = (255, 205, 60)
GEM = (255, 90, 160)
BLUSH = (255, 150, 160)

NOSE = (30, 25, 35)


class Dog:
    """A border collie's look: coat, white markings, inner-ear shade and collar."""

    def __init__(self, key, name, coat, marking, shade, collar):
        self.key, self.name = key, name
        self.coat, self.marking, self.shade, self.collar = coat, marking, shade, collar


DOGS = {
    "azulita": Dog("azulita", "Azulita", coat=(52, 48, 60), marking=(250, 250, 248),
                   shade=(85, 78, 95), collar=(80, 165, 255)),
    "vainilla": Dog("vainilla", "Vainilla", coat=(250, 250, 246), marking=(250, 250, 246),
                    shade=(232, 222, 215), collar=(255, 90, 160)),
}
DEFAULT_DOG = "azulita"


def draw_diana(surf, cx, bottom, facing=1, squash=0.0, run_phase=0.0, on_ground=True, t=0.0, scale=1.0):
    sx = scale * (1 + squash)
    sy = scale * (1 - squash)
    f = facing

    def P(dx, dy):
        """Point relative to the feet: dx forward (mirrored by facing), dy up."""
        return (cx + dx * sx * f, bottom - dy * sy)

    def poly(color, pts, width=2):
        pygame.draw.polygon(surf, color, pts)
        pygame.draw.polygon(surf, OUTLINE, pts, width)

    swing = math.sin(run_phase) * 4 if on_ground else 2.5
    head = P(1, 45)
    head_r = 11 * scale

    # Long hair behind everything
    pygame.draw.circle(surf, OUTLINE, P(-2, 46), head_r * 1.18 + 2)
    pygame.draw.circle(surf, HAIR, P(-2, 46), head_r * 1.18)
    poly(HAIR, [P(-13, 48), P(-15, 30 + math.sin(t * 3) * 1.5), P(-6, 28), P(2, 40)])

    # Legs + shoes
    for side, sw in ((-1, swing), (1, -swing)):
        hip = P(side * 4 + sw * 0.3, 13)
        foot = P(side * 4 + sw, 3)
        pygame.draw.line(surf, SKIN, hip, foot, max(2, int(4 * scale)))
        shoe = pygame.Rect(0, 0, 10 * scale, 6 * scale)
        shoe.center = (foot[0] + 2 * f * scale, foot[1] + 1)
        pygame.draw.ellipse(surf, SHOES, shoe)
        pygame.draw.ellipse(surf, OUTLINE, shoe, 1)

    # Twirly skirt (A-line with a wavy hem)
    hem = []
    for i in range(9):
        k = i / 8
        dx = -17 + 34 * k
        wave = math.sin(t * 6 + k * 6) * (1.5 if on_ground and abs(swing) > 0.5 else 0.8)
        hem.append(P(dx, 11 + wave + (2 if i % 2 else 0)))
    skirt = [P(-8, 27)] + hem + [P(8, 27)]
    poly(DRESS, skirt)
    for i in range(1, 8, 2):
        pygame.draw.circle(surf, WHITE, hem[i], 1.6 * scale)

    # Bodice + sash
    body = [P(-7, 37), P(7, 37), P(8, 26), P(-8, 26)]
    poly(DRESS, body)
    pygame.draw.line(surf, SASH, P(-8, 27), P(8, 27), max(2, int(3 * scale)))
    pygame.draw.circle(surf, SASH, P(-7, 27), 3 * scale)
    # Puffy sleeves + arms
    for side in (-1, 1):
        sw = -swing * side if on_ground else -6
        hand = P(side * 12 + sw * 0.4, 24 + (6 if not on_ground else 0))
        pygame.draw.line(surf, SKIN, P(side * 8, 34), hand, max(2, int(4 * scale)))
        pygame.draw.circle(surf, SKIN, hand, 2.5 * scale)
        pygame.draw.circle(surf, OUTLINE, P(side * 8, 35), 4.5 * scale + 1.5)
        pygame.draw.circle(surf, DRESS, P(side * 8, 35), 4.5 * scale)

    # Head
    pygame.draw.circle(surf, OUTLINE, head, head_r + 2)
    pygame.draw.circle(surf, SKIN, head, head_r)
    # Bangs
    poly(HAIR, [P(-11, 47), P(-9, 54), P(-2, 57), P(6, 56), P(11, 51), P(12, 47), P(6, 51), P(1, 49), P(-4, 51)], 1)
    pygame.draw.line(surf, HAIR_LIGHT, P(-5, 54), P(3, 55), max(1, int(2 * scale)))

    # Face
    blink = (t % 3.9) < 0.12
    for ex in (-1.5, 6):
        e = P(ex, 45)
        if blink:
            pygame.draw.line(surf, OUTLINE, (e[0] - 2 * scale, e[1]), (e[0] + 2 * scale, e[1]), 2)
        else:
            pygame.draw.ellipse(surf, OUTLINE, pygame.Rect(e[0] - 2.2 * scale, e[1] - 3 * scale, 4.4 * scale, 6 * scale))
            pygame.draw.circle(surf, WHITE, (e[0] + 0.8 * scale, e[1] - 1.3 * scale), 1.1 * scale)
    pygame.draw.circle(surf, BLUSH, P(-4, 40.5), 2.2 * scale)
    pygame.draw.circle(surf, BLUSH, P(9.5, 40.5), 2.2 * scale)
    mouth = P(2.5, 39.5)
    pygame.draw.arc(surf, (200, 70, 90), pygame.Rect(mouth[0] - 3 * scale, mouth[1] - 3 * scale, 6 * scale, 5 * scale),
                    math.pi * 1.1, math.pi * 1.9, max(1, int(2 * scale)))

    # Princess crown
    crown = [P(-6, 55), P(-6, 61), P(-3, 58), P(0, 63), P(3, 58), P(6, 61), P(6, 55)]
    poly(CROWN, crown, 1)
    pygame.draw.circle(surf, GEM, P(0, 57.5), 1.8 * scale)
    if (t * 1.3) % 2 < 0.25:  # little twinkle
        tw = P(6, 63)
        pygame.draw.line(surf, WHITE, (tw[0] - 3, tw[1]), (tw[0] + 3, tw[1]), 2)
        pygame.draw.line(surf, WHITE, (tw[0], tw[1] - 3), (tw[0], tw[1] + 3), 2)


def draw_puppy(surf, cx, bottom, facing=1, t=0.0, moving=False, scale=1.0, dog=DEFAULT_DOG):
    """A border collie (see DOGS). The white markings only show on a dark coat."""
    d = DOGS.get(dog, DOGS[DEFAULT_DOG])
    f = facing

    def P(dx, dy):
        return (cx + dx * scale * f, bottom - dy * scale)

    def poly(color, pts, width=1):
        pygame.draw.polygon(surf, color, pts)
        pygame.draw.polygon(surf, OUTLINE, pts, width)

    w = lambda px: max(1, int(px * scale))
    step = math.sin(t * 16) * 2.5 if moving else 0
    # Legs: coat on top, white socks below
    for x, ph in ((-7, step), (-3, -step), (5, -step), (9, step)):
        hip, knee, paw = P(x, 10), P(x + ph * 0.25, 5), P(x + ph * 0.5, 0)
        pygame.draw.line(surf, OUTLINE, hip, paw, w(5))
        pygame.draw.line(surf, d.coat, hip, knee, w(3))
        pygame.draw.line(surf, d.marking, knee, paw, w(3))
    # Fluffy, low-swept collie tail with a white tip
    wag = math.sin(t * (18 if moving else 9)) * 4
    tail = [P(-11, 13), P(-17, 13 + wag * 0.4), P(-21, 16 + wag)]
    pygame.draw.lines(surf, OUTLINE, False, tail, w(7))
    pygame.draw.lines(surf, d.coat, False, tail, w(5))
    pygame.draw.circle(surf, d.marking, tail[-1], 2.5 * scale)
    # Body + white chest ruff
    body = pygame.Rect(0, 0, 26 * scale, 14 * scale)
    body.center = P(0, 12)
    pygame.draw.ellipse(surf, OUTLINE, body.inflate(4, 4))
    pygame.draw.ellipse(surf, d.coat, body)
    ruff = pygame.Rect(0, 0, 10 * scale, 11 * scale)
    ruff.center = P(8, 12)
    pygame.draw.ellipse(surf, d.marking, ruff)
    # Head
    hop = abs(math.sin(t * 8)) * 1.5 if moving else 0
    head = P(12, 20 + hop)
    ear_flop = math.sin(t * 6) * 0.8
    for ex in (8, 13):   # semi-erect ears with folded tips
        ear = [P(ex - 3, 25 + hop), P(ex + 3, 26 + hop), P(ex + 1, 32 + hop), P(ex + 3.5 + ear_flop, 30 + hop)]
        poly(d.coat, [ear[0], ear[1], ear[3], ear[2]])
        pygame.draw.line(surf, d.shade, P(ex - 0.5, 26 + hop), P(ex + 1, 30 + hop), w(2))
    pygame.draw.circle(surf, OUTLINE, head, 8 * scale + 2)
    pygame.draw.circle(surf, d.coat, head, 8 * scale)
    # White blaze down the face and a white muzzle
    pygame.draw.polygon(surf, d.marking, [P(13, 28 + hop), P(15, 28 + hop), P(17, 19 + hop), P(13, 18 + hop)])
    pygame.draw.circle(surf, d.marking, P(18, 18 + hop), 4.5 * scale)
    pygame.draw.line(surf, d.collar, P(7, 15), P(11, 12), w(3))
    pygame.draw.circle(surf, NOSE, P(21.5, 19 + hop), 1.9 * scale)
    eye = P(12, 22 + hop)
    pygame.draw.circle(surf, NOSE, eye, 1.7 * scale)
    pygame.draw.circle(surf, WHITE, (eye[0] + 0.5 * scale * f, eye[1] - 0.6 * scale), 0.7 * scale)


class PuppyFollower:
    """Diana's puppy: replays her path a moment later, trotting just behind her."""

    DELAY = 8      # frames behind Diana
    BEHIND = 26    # px behind her, in the direction she faces

    def __init__(self, player, dog=DEFAULT_DOG):
        self.dog = dog
        self.trail = deque(maxlen=self.DELAY)
        self.reset(player)

    def reset(self, player):
        self.trail.clear()
        self.update(player)
        while len(self.trail) < self.DELAY:
            self.trail.append(self.trail[-1])
        self.x, self.bottom, self.facing = self.trail[0]
        self.moving = False

    def update(self, player):
        self.trail.append((player.x + player.w / 2, player.y + player.h, player.facing))
        tx, tb, tf = self.trail[0]
        new_x = tx - tf * self.BEHIND
        self.moving = abs(new_x - getattr(self, "x", new_x)) > 0.3
        if self.moving:
            self.facing = 1 if new_x > self.x else -1
        self.x, self.bottom = new_x, tb

    def draw(self, surf, offset, t, hop=0.0):
        draw_puppy(surf, self.x - offset[0], self.bottom - offset[1] - hop, self.facing, t, self.moving,
                   dog=self.dog)

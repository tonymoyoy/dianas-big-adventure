"""Drawing for Diana (the player, in one of her OUTFITS) and her dog (Azulita or Vainilla), plus the puppy's follow logic.

The draw functions take the bottom-center point (cx, bottom) where the feet touch the ground.
"""
import math
from collections import deque

import pygame

from .draw import circle
from .settings import OUTLINE, WHITE

SKIN = (255, 214, 186)
HAIR = (115, 65, 40)
HAIR_LIGHT = (150, 90, 55)
GOLD_CROWN = (255, 205, 60)
SILVER_CROWN = (215, 225, 245)
RAINBOW = [(240, 70, 80), (255, 160, 60), (255, 225, 70), (90, 200, 110), (80, 160, 255), (160, 100, 230)]


class Outfit:
    """One of Diana's dresses.

    shape:   aline | ball (wide, to the ankles) | long (straight, to the ankles)
             | tutu (short and puffy) | mermaid (fitted, flared fin hem)
    pattern: none | dots | sparkle | scales | stars | spots | rainbow | hearts | flowers
    """

    def __init__(self, key, name, dress, sash, shoes, gem, shape="aline", pattern="none",
                 pattern_color=WHITE, crown=GOLD_CROWN):
        self.key, self.name = key, name
        self.dress, self.sash, self.shoes, self.gem, self.crown = dress, sash, shoes, gem, crown
        self.shape, self.pattern, self.pattern_color = shape, pattern, pattern_color


OUTFITS = {o.key: o for o in (
    Outfit("pink", "Pink Princess", (255, 120, 185), (255, 200, 230), (190, 60, 140), (255, 90, 160),
           pattern="dots"),
    Outfit("snow", "Snow Queen", (130, 200, 245), (225, 245, 255), (90, 150, 210), (120, 200, 255),
           shape="long", pattern="sparkle", crown=SILVER_CROWN),
    Outfit("mermaid", "Little Mermaid", (40, 200, 180), (190, 130, 230), (30, 150, 140), (190, 130, 230),
           shape="mermaid", pattern="scales", pattern_color=(130, 240, 220)),
    Outfit("sunshine", "Sunshine Gown", (255, 205, 60), (255, 240, 170), (220, 150, 40), (255, 120, 60),
           shape="ball", pattern="sparkle"),
    Outfit("tutu", "Lavender Tutu", (190, 140, 240), (240, 220, 255), (140, 90, 200), (255, 120, 200),
           shape="tutu", pattern="stars"),
    Outfit("strawberry", "Strawberry", (235, 60, 80), (110, 200, 90), (170, 30, 60), (110, 200, 90),
           pattern="spots", pattern_color=(255, 230, 120)),
    Outfit("rainbow", "Rainbow", (255, 150, 190), WHITE, (90, 160, 255), (90, 160, 255),
           pattern="rainbow"),
    Outfit("mint", "Mint Hearts", (150, 225, 190), (255, 190, 215), (70, 170, 130), (255, 120, 170),
           shape="tutu", pattern="hearts", pattern_color=(255, 120, 170)),
    Outfit("night", "Starry Night", (60, 65, 150), (255, 215, 90), (35, 35, 90), (255, 215, 90),
           shape="ball", pattern="stars", pattern_color=(255, 215, 90)),
    Outfit("garden", "Flower Garden", (255, 150, 120), (255, 230, 200), (220, 100, 80), (120, 200, 100),
           shape="long", pattern="flowers"),
)}
DEFAULT_OUTFIT = "pink"

# Skirt trapezoids: (hem half-width, hem height above the feet). The waist is 8 wide at height 27.
SKIRTS = {"aline": (17, 11), "ball": (21, 4), "long": (14, 3), "tutu": (21, 16), "mermaid": (16, 2)}
# Where pattern marks sit on a skirt: (fraction of half-width, fraction of the way down to the hem)
PATTERN_SPOTS = [(-0.55, 0.45), (0.1, 0.3), (0.6, 0.55), (-0.2, 0.75), (0.35, 0.85), (-0.7, 0.9)]
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


def draw_diana(surf, cx, bottom, facing=1, squash=0.0, run_phase=0.0, on_ground=True, t=0.0, scale=1.0,
               outfit=DEFAULT_OUTFIT):
    outfit = OUTFITS.get(outfit, OUTFITS[DEFAULT_OUTFIT])
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
    circle(surf, OUTLINE, P(-2, 46), head_r * 1.18 + 2)
    circle(surf, HAIR, P(-2, 46), head_r * 1.18)
    poly(HAIR, [P(-13, 48), P(-15, 30 + math.sin(t * 3) * 1.5), P(-6, 28), P(2, 40)])

    # Legs + shoes
    for side, sw in ((-1, swing), (1, -swing)):
        hip = P(side * 4 + sw * 0.3, 13)
        foot = P(side * 4 + sw, 3)
        pygame.draw.line(surf, SKIN, hip, foot, max(2, int(4 * scale)))
        shoe = pygame.Rect(0, 0, 10 * scale, 6 * scale)
        shoe.center = (foot[0] + 2 * f * scale, foot[1] + 1)
        pygame.draw.ellipse(surf, outfit.shoes, shoe)
        pygame.draw.ellipse(surf, OUTLINE, shoe, 1)

    _draw_skirt(surf, outfit, P, poly, t, scale, on_ground and abs(swing) > 0.5)

    # Bodice + sash
    body = [P(-7, 37), P(7, 37), P(8, 26), P(-8, 26)]
    poly(outfit.dress, body)
    pygame.draw.line(surf, outfit.sash, P(-8, 27), P(8, 27), max(2, int(3 * scale)))
    circle(surf, outfit.sash, P(-7, 27), 3 * scale)
    # Puffy sleeves + arms
    for side in (-1, 1):
        sw = -swing * side if on_ground else -6
        hand = P(side * 12 + sw * 0.4, 24 + (6 if not on_ground else 0))
        pygame.draw.line(surf, SKIN, P(side * 8, 34), hand, max(2, int(4 * scale)))
        circle(surf, SKIN, hand, 2.5 * scale)
        circle(surf, OUTLINE, P(side * 8, 35), 4.5 * scale + 1.5)
        circle(surf, outfit.dress, P(side * 8, 35), 4.5 * scale)

    # Head
    circle(surf, OUTLINE, head, head_r + 2)
    circle(surf, SKIN, head, head_r)
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
            circle(surf, WHITE, (e[0] + 0.8 * scale, e[1] - 1.3 * scale), 1.1 * scale)
    circle(surf, BLUSH, P(-4, 40.5), 2.2 * scale)
    circle(surf, BLUSH, P(9.5, 40.5), 2.2 * scale)
    mouth = P(2.5, 39.5)
    pygame.draw.arc(surf, (200, 70, 90), pygame.Rect(mouth[0] - 3 * scale, mouth[1] - 3 * scale, 6 * scale, 5 * scale),
                    math.pi * 1.1, math.pi * 1.9, max(1, int(2 * scale)))

    # Princess crown
    crown = [P(-6, 55), P(-6, 61), P(-3, 58), P(0, 63), P(3, 58), P(6, 61), P(6, 55)]
    poly(outfit.crown, crown, 1)
    circle(surf, outfit.gem, P(0, 57.5), 1.8 * scale)
    if (t * 1.3) % 2 < 0.25:  # little twinkle
        tw = P(6, 63)
        pygame.draw.line(surf, WHITE, (tw[0] - 3, tw[1]), (tw[0] + 3, tw[1]), 2)
        pygame.draw.line(surf, WHITE, (tw[0], tw[1] - 3), (tw[0], tw[1] + 3), 2)


def _draw_skirt(surf, outfit, P, poly, t, scale, twirl):
    """The skirt in the outfit's shape, then its pattern on top."""
    hem_w, hem_y = SKIRTS[outfit.shape]
    hem = []
    for i in range(9):
        k = i / 8
        wave = math.sin(t * 6 + k * 6) * (1.5 if twirl else 0.8)
        zig = (3 if outfit.shape == "tutu" else 2) if i % 2 else 0
        hem.append(P(-hem_w + 2 * hem_w * k, hem_y + wave + zig))
    if outfit.shape == "mermaid":   # fitted down to the knees, then a fin
        poly(outfit.dress, [P(-8, 27), P(-7, 13)] + hem + [P(7, 13), P(8, 27)])
    else:
        poly(outfit.dress, [P(-8, 27)] + hem + [P(8, 27)])
    if outfit.shape == "tutu":      # second, lighter layer of tulle
        light = [min(255, c + 45) for c in outfit.dress]
        poly(light, [P(-8, 27), P(-hem_w + 3, 19), P(-hem_w / 2, 21), P(0, 19), P(hem_w / 2, 21), P(hem_w - 3, 19), P(8, 27)], 1)

    def at(fx, fy):   # a point inside the skirt
        if outfit.shape == "mermaid":
            return P(fx * 6, 27 - 12 * fy)
        return P(fx * (8 + (hem_w - 8) * fy) * 0.8, 27 - (27 - hem_y) * fy)

    r = 1.7 * scale
    c = outfit.pattern_color
    pattern = outfit.pattern
    if pattern == "dots":
        for i in range(1, 8, 2):
            circle(surf, c, hem[i], 1.6 * scale)
    elif pattern == "rainbow":
        n = len(RAINBOW)
        for j, color in enumerate(RAINBOW):
            k0, k1 = j / n, (j + 1) / n
            w0, w1 = 8 + (hem_w - 8) * k0, 8 + (hem_w - 8) * k1
            y0, y1 = 27 - (27 - hem_y) * k0, 27 - (27 - hem_y) * k1
            pygame.draw.polygon(surf, color, [P(-w0, y0), P(w0, y0), P(w1, y1), P(-w1, y1)])
        pygame.draw.polygon(surf, OUTLINE, [P(-8, 27)] + hem + [P(8, 27)], 2)
    elif pattern == "scales":
        for row, fy in enumerate((0.25, 0.55, 0.85)):
            for fx in (-0.6, 0, 0.6):
                x, y = at(fx + (0.3 if row % 2 else 0), fy)
                pygame.draw.arc(surf, c, (x - 2 * scale, y - 1.5 * scale, 4 * scale, 3 * scale), math.pi, math.tau, 1)
        for i in range(1, 8, 2):
            pygame.draw.line(surf, c, hem[i], P(0, 6), 1)
    else:
        for fx, fy in PATTERN_SPOTS:
            x, y = at(fx, fy)
            if pattern == "sparkle":
                if (t * 2 + fx * 3) % 2 < 1.5:
                    pygame.draw.line(surf, c, (x - r, y), (x + r, y), 1)
                    pygame.draw.line(surf, c, (x, y - r), (x, y + r), 1)
            elif pattern == "spots":
                pygame.draw.ellipse(surf, c, (x - r * 0.5, y - r * 0.7, r, r * 1.4))
            elif pattern == "stars":
                pts = []
                for i in range(10):
                    rr = r * 1.3 if i % 2 == 0 else r * 0.55
                    a = -math.pi / 2 + i * math.pi / 5
                    pts.append((x + math.cos(a) * rr, y + math.sin(a) * rr))
                pygame.draw.polygon(surf, c, pts)
            elif pattern == "hearts":
                circle(surf, c, (x - r * 0.5, y - r * 0.3), r * 0.6)
                circle(surf, c, (x + r * 0.5, y - r * 0.3), r * 0.6)
                pygame.draw.polygon(surf, c, [(x - r * 1.05, y - r * 0.15), (x + r * 1.05, y - r * 0.15), (x, y + r)])
            elif pattern == "flowers":
                for a in range(5):
                    ang = t + a * math.tau / 5
                    circle(surf, c, (x + math.cos(ang) * r * 0.8, y + math.sin(ang) * r * 0.8), r * 0.55)
                circle(surf, (255, 210, 70), (x, y), r * 0.5)


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
    circle(surf, d.marking, tail[-1], 2.5 * scale)
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
    circle(surf, OUTLINE, head, 8 * scale + 2)
    circle(surf, d.coat, head, 8 * scale)
    # White blaze down the face and a white muzzle
    pygame.draw.polygon(surf, d.marking, [P(13, 28 + hop), P(15, 28 + hop), P(17, 19 + hop), P(13, 18 + hop)])
    circle(surf, d.marking, P(18, 18 + hop), 4.5 * scale)
    pygame.draw.line(surf, d.collar, P(7, 15), P(11, 12), w(3))
    circle(surf, NOSE, P(21.5, 19 + hop), 1.9 * scale)
    eye = P(12, 22 + hop)
    circle(surf, NOSE, eye, 1.7 * scale)
    circle(surf, WHITE, (eye[0] + 0.5 * scale * f, eye[1] - 0.6 * scale), 0.7 * scale)


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

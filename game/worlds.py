"""The five themed worlds: colors, physics tweaks, backgrounds, tiles and items.

Everything is drawn with pygame primitives, so there are no image files.
A World's `draw_background(surf, cam_x, t)` paints the whole screen, and
`draw_item(surf, cx, cy, size, t)` draws its collectible centered at (cx, cy).
"""
import math
import random

import pygame

from .settings import GRAVITY, HEIGHT, JUMP_SPEED, OUTLINE, SPRING_SPEED, TILE, WIDTH, WHITE


# ----------------------------------------------------------------- helpers
def gradient(top, bottom, w=WIDTH, h=HEIGHT):
    surf = pygame.Surface((w, h))
    for y in range(h):
        k = y / (h - 1)
        c = [int(top[i] + (bottom[i] - top[i]) * k) for i in range(3)]
        pygame.draw.line(surf, c, (0, y), (w, y))
    return surf


def repeat(cam_x, factor, period):
    """Yield screen x of each repetition of a parallax layer covering the screen."""
    off = (cam_x * factor) % period
    x = -off - period
    while x < WIDTH + period:
        yield x
        x += period


def cloud(surf, x, y, s, color=WHITE):
    for dx, dy, r in ((0, 0, 22), (24, -10, 28), (52, 0, 22), (26, 6, 22)):
        pygame.draw.circle(surf, color, (int(x + dx * s), int(y + dy * s)), int(r * s))


def star_points(cx, cy, r_out, r_in, n=5, rot=-math.pi / 2):
    pts = []
    for i in range(n * 2):
        r = r_out if i % 2 == 0 else r_in
        a = rot + i * math.pi / n
        pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
    return pts


def outlined_polygon(surf, color, pts, width=2):
    pygame.draw.polygon(surf, color, pts)
    pygame.draw.polygon(surf, OUTLINE, pts, width)


# ----------------------------------------------------------------- items
def item_flower(surf, cx, cy, size, t, color=(255, 110, 170)):
    r = size * 0.22
    for i in range(5):
        a = t * 0.8 + i * math.tau / 5
        px, py = cx + math.cos(a) * r * 1.2, cy + math.sin(a) * r * 1.2
        pygame.draw.circle(surf, OUTLINE, (px, py), r + 2)
    for i in range(5):
        a = t * 0.8 + i * math.tau / 5
        pygame.draw.circle(surf, color, (cx + math.cos(a) * r * 1.2, cy + math.sin(a) * r * 1.2), r)
    pygame.draw.circle(surf, OUTLINE, (cx, cy), r * 0.9 + 2)
    pygame.draw.circle(surf, (255, 220, 70), (cx, cy), r * 0.9)


def item_pearl(surf, cx, cy, size, t):
    """A pink clam shell holding a shiny pearl."""
    s = size / 40
    base = cy + 10 * s
    pts = [(cx - 18 * s, base)]
    for i in range(9):
        a = math.pi + i * math.pi / 8
        rr = 18 * s + (2 * s if i % 2 else 0)
        pts.append((cx + math.cos(a) * rr, base - 4 * s + math.sin(a) * rr * 0.75))
    pts += [(cx + 18 * s, base), (cx, base + 6 * s)]
    outlined_polygon(surf, (255, 175, 200), pts)
    for i in range(2, 7, 2):
        a = math.pi + i * math.pi / 8
        pygame.draw.line(surf, (230, 120, 160), (cx, base + 2 * s),
                         (cx + math.cos(a) * 15 * s, base - 4 * s + math.sin(a) * 11 * s), 2)
    pr = 9 * s
    pygame.draw.circle(surf, OUTLINE, (cx, base - 3 * s), pr + 2)
    pygame.draw.circle(surf, (245, 240, 255), (cx, base - 3 * s), pr)
    pygame.draw.circle(surf, (215, 205, 240), (cx + 2 * s, base - 1 * s), pr * 0.6)
    pygame.draw.circle(surf, WHITE, (cx - 3 * s, base - 6 * s), pr * 0.3)
    if (t * 1.5) % 2 < 0.3:
        gx, gy = cx + 10 * s, cy - 10 * s
        pygame.draw.line(surf, WHITE, (gx - 4, gy), (gx + 4, gy), 2)
        pygame.draw.line(surf, WHITE, (gx, gy - 4), (gx, gy + 4), 2)


def item_snowflake(surf, cx, cy, size, t):
    r = size * 0.45
    rot = t * 0.6
    for col, wd in ((OUTLINE, 6), ((120, 200, 255), 3)):
        for i in range(6):
            a = rot + i * math.pi / 3
            ex, ey = cx + math.cos(a) * r, cy + math.sin(a) * r
            pygame.draw.line(surf, col, (cx, cy), (ex, ey), wd)
            for side in (-1, 1):
                b = a + side * 0.6
                mx, my = cx + math.cos(a) * r * 0.6, cy + math.sin(a) * r * 0.6
                pygame.draw.line(surf, col, (mx, my), (mx + math.cos(b) * r * 0.35, my + math.sin(b) * r * 0.35), wd)
    pygame.draw.circle(surf, WHITE, (cx, cy), r * 0.22)


def item_chocolate(surf, cx, cy, size, t):
    """A chocolate bar half-unwrapped from pink paper and gold foil."""
    s = size / 40
    tilt = math.sin(t * 2) * 2 * s
    bar = pygame.Rect(0, 0, 26 * s, 34 * s)
    bar.center = (cx, cy + tilt)
    pygame.draw.rect(surf, OUTLINE, bar.inflate(4, 4), border_radius=int(4 * s))
    pygame.draw.rect(surf, (115, 65, 40), bar, border_radius=int(4 * s))
    cw, ch = bar.w / 2, bar.h * 0.55 / 2
    for i in range(2):
        for j in range(2):
            sq = pygame.Rect(bar.left + i * cw + 2, bar.top + j * ch + 2, cw - 4, ch - 4)
            pygame.draw.rect(surf, (150, 90, 55), sq, border_radius=2)
            pygame.draw.line(surf, (185, 120, 80), sq.topleft, (sq.right - 2, sq.top), 2)
    foil = pygame.Rect(bar.left, bar.top + bar.h * 0.55, bar.w, 4 * s)
    pygame.draw.rect(surf, (255, 210, 80), foil)
    wrap = pygame.Rect(bar.left, foil.bottom, bar.w, bar.bottom - foil.bottom)
    pygame.draw.rect(surf, (255, 105, 170), wrap, border_bottom_left_radius=int(4 * s),
                     border_bottom_right_radius=int(4 * s))
    pygame.draw.circle(surf, WHITE, wrap.center, 3.5 * s)
    pygame.draw.rect(surf, OUTLINE, bar.inflate(2, 2), 2, border_radius=int(4 * s))


def item_star(surf, cx, cy, size, t):
    r = size * 0.5
    pts = star_points(cx, cy, r, r * 0.45, rot=-math.pi / 2 + math.sin(t * 2) * 0.15)
    outlined_polygon(surf, (255, 225, 70), pts, 3)
    pygame.draw.circle(surf, (255, 250, 200), (cx - r * 0.15, cy - r * 0.15), r * 0.15)


# ----------------------------------------------------------------- backgrounds
def bg_meadow(world, surf, cam_x, t):
    surf.blit(world.sky, (0, 0))
    pygame.draw.circle(surf, (255, 245, 170), (820, 90), 70)
    pygame.draw.circle(surf, (255, 225, 80), (820, 90), 50)
    for base in repeat(cam_x - t * 15, 0.1, 1100):
        cloud(surf, base + 100, 80, 1.2)
        cloud(surf, base + 600, 150, 0.9)
    for base in repeat(cam_x, 0.2, 900):
        for x in (0, 380, 680):
            pygame.draw.circle(surf, (160, 215, 140), (int(base + x), HEIGHT + 120), 260)
    for base in repeat(cam_x, 0.4, 700):
        for x in (120, 470):
            pygame.draw.circle(surf, (115, 190, 100), (int(base + x), HEIGHT + 90), 190)
            trunk = pygame.Rect(int(base + x + 60), HEIGHT - 170, 12, 40)
            pygame.draw.rect(surf, (130, 90, 60), trunk)
            pygame.draw.circle(surf, (80, 160, 80), (trunk.centerx, trunk.top - 6), 26)


def mermaid(surf, x, y, t):
    """A mermaid sitting on a rock at (x, y) = top of the rock, waving."""
    pygame.draw.ellipse(surf, (120, 125, 150), (x - 55, y - 4, 110, 50))
    pygame.draw.ellipse(surf, (150, 155, 180), (x - 40, y - 2, 60, 16))
    # tail curling over the rock, with a fin that flicks
    tail = [(x - 6, y - 26), (x + 10, y - 22), (x + 26, y - 6), (x + 40, y + 6), (x + 34, y + 12), (x + 14, y + 2), (x - 10, y - 4)]
    outlined_polygon(surf, (40, 200, 180), tail)
    flick = math.sin(t * 3) * 5
    fin = [(x + 38, y + 8), (x + 56, y - 4 + flick), (x + 52, y + 14), (x + 60, y + 24 + flick)]
    outlined_polygon(surf, (90, 230, 210), fin)
    # hair behind, body, shell top
    pygame.draw.ellipse(surf, (230, 80, 70), (x - 20, y - 66, 30, 50))
    pygame.draw.rect(surf, (255, 214, 186), (x - 12, y - 46, 16, 22), border_radius=6)
    pygame.draw.circle(surf, (190, 130, 230), (x - 8, y - 36), 5)
    pygame.draw.circle(surf, (190, 130, 230), (x + 1, y - 36), 5)
    # waving arm
    wave = math.sin(t * 5) * 0.5
    hx, hy = x + 2 + math.cos(-1.2 + wave) * 22, y - 44 + math.sin(-1.2 + wave) * 22
    pygame.draw.line(surf, (255, 214, 186), (x + 2, y - 42), (hx, hy), 5)
    pygame.draw.circle(surf, (255, 214, 186), (hx, hy), 4)
    # head + face
    pygame.draw.circle(surf, OUTLINE, (x - 4, y - 58), 12)
    pygame.draw.circle(surf, (255, 214, 186), (x - 4, y - 58), 10)
    pygame.draw.arc(surf, (230, 80, 70), (x - 16, y - 72, 24, 18), 0, math.pi, 7)
    pygame.draw.circle(surf, OUTLINE, (x - 1, y - 59), 2)
    pygame.draw.circle(surf, (255, 150, 160), (x + 2, y - 54), 2)
    pygame.draw.circle(surf, (255, 120, 180), (x - 12, y - 66), 4)  # hair flower


def bg_lagoon(world, surf, cam_x, t):
    surf.blit(world.sky, (0, 0))
    pygame.draw.circle(surf, (255, 200, 150), (760, 220), 80)
    for base in repeat(cam_x - t * 12, 0.1, 1200):
        cloud(surf, base + 200, 90, 1.0)
        cloud(surf, base + 800, 60, 0.8)
    sea_top = 290
    pygame.draw.rect(surf, (40, 175, 200), (0, sea_top, WIDTH, HEIGHT - sea_top))
    pygame.draw.rect(surf, (90, 210, 225), (0, sea_top, WIDTH, 14))
    for row, y in enumerate(range(sea_top + 30, HEIGHT, 34)):
        shift = math.sin(t * 1.5 + row) * 12
        for base in repeat(cam_x, 0.15 + row * 0.03, 120):
            pygame.draw.arc(surf, (190, 240, 245), (base + shift, y, 40, 14), 0, math.pi, 2)
    for base in repeat(cam_x, 0.3, 1300):
        mermaid(surf, base + 500, sea_top + 70 + math.sin(t) * 2, t)
        # bubbles rising
        for i in range(4):
            by = sea_top + 150 - ((t * 30 + i * 37) % 130)
            pygame.draw.circle(surf, (210, 245, 250), (int(base + 470 + i * 22), int(by)), 4, 2)
    for base in repeat(cam_x, 0.5, 650):
        for x, hgt in ((80, 170), (390, 210)):
            bx, by = base + x, HEIGHT - 70
            sway = math.sin(t * 1.2 + x) * 4
            pts = []
            for i in range(9):
                k = i / 8
                pts.append((bx + math.sin(k * 1.8) * 30 + sway * k, by - hgt * k))
            pygame.draw.lines(surf, (150, 100, 60), False, pts, 12)
            tx, ty = pts[-1]
            for a in (-2.6, -2.0, -1.2, -0.5, 0.1):
                ex, ey = tx + math.cos(a) * 70, ty + math.sin(a) * 30 + 30
                pygame.draw.line(surf, (60, 160, 80), (tx, ty), (ex, ey), 10)
            pygame.draw.circle(surf, (110, 80, 50), (int(tx - 6), int(ty + 10)), 8)


def castle(surf, x, base, t):
    """A princess castle with pink roofs and waving pennants; x is center, base is the ground line."""
    wall = (225, 230, 245)
    roof = (255, 130, 190)
    for tx, w, h in ((-95, 44, 170), (95, 44, 170), (-40, 40, 210), (40, 40, 210), (0, 54, 260)):
        r = pygame.Rect(0, 0, w, h)
        r.midbottom = (x + tx, base)
        pygame.draw.rect(surf, wall, r)
        pygame.draw.rect(surf, (190, 195, 220), r, 2)
        cone = [(r.left - 6, r.top), (r.centerx, r.top - w * 1.2), (r.right + 6, r.top)]
        pygame.draw.polygon(surf, roof, cone)
        pygame.draw.polygon(surf, (220, 90, 150), cone, 2)
        px, py = r.centerx, r.top - w * 1.2
        pygame.draw.line(surf, (150, 150, 170), (px, py), (px, py - 18), 2)
        flap = math.sin(t * 4 + tx) * 3
        pygame.draw.polygon(surf, (255, 205, 60), [(px, py - 18), (px + 14, py - 13 + flap), (px, py - 9)])
        win = pygame.Rect(0, 0, w * 0.3, w * 0.45)
        win.center = (r.centerx, r.top + h * 0.25)
        pygame.draw.rect(surf, (120, 140, 200), win, border_top_left_radius=8, border_top_right_radius=8)
    body = pygame.Rect(0, 0, 200, 120)
    body.midbottom = (x, base)
    pygame.draw.rect(surf, wall, body)
    for i in range(10):
        pygame.draw.rect(surf, wall, (body.left + i * 20, body.top - 10, 12, 12))
    door = pygame.Rect(0, 0, 40, 56)
    door.midbottom = (x, base)
    pygame.draw.rect(surf, (200, 110, 160), door, border_top_left_radius=20, border_top_right_radius=20)
    pygame.draw.circle(surf, (255, 205, 60), (x + 10, base - 26), 3)


def bg_snow(world, surf, cam_x, t):
    surf.blit(world.sky, (0, 0))
    for base in repeat(cam_x, 0.15, 800):
        for x, w, h in ((0, 520, 300), (380, 600, 360)):
            peak = (base + x + w / 2, HEIGHT - 60 - h)
            pygame.draw.polygon(surf, (190, 205, 228), [(base + x, HEIGHT), peak, (base + x + w, HEIGHT)])
            cap = [(peak[0] - w * 0.12, peak[1] + h * 0.24), peak, (peak[0] + w * 0.12, peak[1] + h * 0.24)]
            pygame.draw.polygon(surf, WHITE, cap)
    for base in repeat(cam_x, 0.22, 1500):
        castle(surf, base + 700, HEIGHT - 90, t)
    for base in repeat(cam_x, 0.3, 600):
        for x, w, h in ((100, 420, 230),):
            peak = (base + x + w / 2, HEIGHT - 40 - h)
            pygame.draw.polygon(surf, (150, 178, 210), [(base + x, HEIGHT), peak, (base + x + w, HEIGHT)])
            cap = [(peak[0] - w * 0.13, peak[1] + h * 0.28), peak, (peak[0] + w * 0.13, peak[1] + h * 0.28)]
            pygame.draw.polygon(surf, WHITE, cap)
    for base in repeat(cam_x, 0.5, 420):
        for x in (40, 210, 300):
            bx, by = base + x, HEIGHT - 70
            pygame.draw.rect(surf, (110, 80, 60), (bx - 5, by - 10, 10, 20))
            for i, w in enumerate((44, 36, 26)):
                y = by - 10 - i * 26
                pygame.draw.polygon(surf, (50, 120, 90), [(bx - w, y), (bx, y - 44), (bx + w, y)])
                pygame.draw.polygon(surf, WHITE, [(bx - 10, y - 30), (bx, y - 44), (bx + 10, y - 30)])


def bg_chocolate(world, surf, cam_x, t):
    surf.blit(world.sky, (0, 0))
    for base in repeat(cam_x - t * 10, 0.1, 1000):
        cloud(surf, base + 150, 90, 1.1, (255, 240, 235))
        cloud(surf, base + 650, 140, 0.9, (255, 225, 235))
    # far: chocolate hills with cream drizzle
    for base in repeat(cam_x, 0.2, 800):
        for i, (x, c) in enumerate(((0, (150, 95, 60)), (260, (125, 75, 45)), (520, (165, 110, 70)))):
            cx = int(base + x)
            pygame.draw.circle(surf, c, (cx, HEIGHT + 30), 200)
            pts = [(cx - 150 + k * 30, HEIGHT - 120 + (12 if k % 2 else 0) - abs(k - 5) * 6) for k in range(11)]
            pygame.draw.lines(surf, (255, 240, 220), False, pts, 5)
    # near: giant chocolate bars and strawberries
    for base in repeat(cam_x, 0.45, 600):
        for x, h in ((60, 190), (360, 150)):
            bar = pygame.Rect(int(base + x), HEIGHT - 60 - h, 90, h)
            pygame.draw.rect(surf, (95, 55, 35), bar, border_radius=8)
            for gx in range(2):
                for gy in range(h // 45):
                    sq = pygame.Rect(bar.left + 6 + gx * 42, bar.top + 6 + gy * 45, 36, 38)
                    pygame.draw.rect(surf, (130, 80, 50), sq, border_radius=4)
            wrap = pygame.Rect(bar.left - 3, bar.bottom - 60, bar.w + 6, 60)
            pygame.draw.rect(surf, (255, 120, 180), wrap)
            pygame.draw.rect(surf, (255, 210, 80), (wrap.left, wrap.top, wrap.w, 8))
        sx, sy = base + 250, HEIGHT - 95
        pygame.draw.polygon(surf, (235, 60, 80), [(sx - 22, sy - 20), (sx + 22, sy - 20), (sx, sy + 22)])
        pygame.draw.circle(surf, (235, 60, 80), (int(sx - 11), int(sy - 20)), 11)
        pygame.draw.circle(surf, (235, 60, 80), (int(sx + 11), int(sy - 20)), 11)
        pygame.draw.polygon(surf, (70, 170, 80), [(sx - 14, sy - 30), (sx, sy - 40), (sx + 14, sy - 30), (sx, sy - 24)])
        for dx, dy in ((-8, -12), (6, -10), (0, 0), (-4, 8), (9, -2)):
            pygame.draw.circle(surf, (255, 230, 120), (int(sx + dx), int(sy + dy)), 2)


def bg_moon(world, surf, cam_x, t):
    surf.blit(world.sky, (0, 0))
    for base in repeat(cam_x, 0.05, 1600):
        for i, (x, y) in enumerate(world.stars):
            tw = 1.5 + math.sin(t * 2 + i) * 1.2
            pygame.draw.circle(surf, WHITE, (int(base + x), y), max(1, int(tw)))
    ex = 780 - cam_x * 0.02
    pygame.draw.circle(surf, (70, 130, 230), (int(ex), 110), 55)
    for dx, dy, r in ((-15, -10, 18), (12, 14, 14), (20, -20, 9)):
        pygame.draw.circle(surf, (90, 190, 110), (int(ex + dx), 110 + dy), r)
    pygame.draw.circle(surf, (200, 230, 255), (int(ex), 110), 55, 3)
    # little ringed planet
    px = 200 - cam_x * 0.03
    pygame.draw.circle(surf, (240, 160, 90), (int(px), 170), 26)
    pygame.draw.ellipse(surf, (255, 220, 160), (px - 45, 162, 90, 16), 3)
    for base in repeat(cam_x, 0.25, 900):
        for x, r in ((0, 220), (450, 260)):
            cx = int(base + x)
            pygame.draw.circle(surf, (110, 110, 135), (cx, HEIGHT + 100), r)
            pygame.draw.ellipse(surf, (90, 90, 115), (cx - 60, HEIGHT - 90, 50, 16))
            pygame.draw.ellipse(surf, (90, 90, 115), (cx + 40, HEIGHT - 50, 34, 12))


# ----------------------------------------------------------------- world
class World:
    def __init__(self, key, name, item_name, sky, ground, ground_top, platform, accent,
                 background, item, gravity=GRAVITY, jump_speed=JUMP_SPEED,
                 spring_speed=SPRING_SPEED, snow=False):
        self.key, self.name, self.item_name = key, name, item_name
        self.sky_colors = sky
        self.ground, self.ground_top, self.platform, self.accent = ground, ground_top, platform, accent
        self._background, self._item = background, item
        self.gravity, self.jump_speed, self.spring_speed = gravity, jump_speed, spring_speed
        self.snow = snow
        self._built = False

    def build(self):
        """Create surfaces lazily (needs pygame display initialised)."""
        if self._built:
            return
        self.sky = gradient(*self.sky_colors)
        rng = random.Random(self.key)
        self.stars = [(rng.randrange(1600), rng.randrange(HEIGHT - 120)) for _ in range(70)]
        self.tile_mid = self._make_tile(rng, top=False)
        self.tile_top = self._make_tile(rng, top=True)
        self._built = True

    def _make_tile(self, rng, top):
        s = pygame.Surface((TILE, TILE))
        s.fill(self.ground)
        dark = [max(0, c - 25) for c in self.ground]
        for _ in range(4):
            pygame.draw.circle(s, dark, (rng.randrange(6, TILE - 6), rng.randrange(14 if top else 4, TILE - 4)), rng.randrange(2, 5))
        if top:
            pygame.draw.rect(s, self.ground_top, (0, 0, TILE, 12))
            for x in range(0, TILE + 1, 12):
                pygame.draw.circle(s, self.ground_top, (x, 12), 6)
            light = [min(255, c + 40) for c in self.ground_top]
            pygame.draw.line(s, light, (0, 2), (TILE, 2), 3)
        return s

    def draw_background(self, surf, cam_x, t):
        self.build()
        self._background(self, surf, cam_x, t)

    def draw_item(self, surf, cx, cy, size, t):
        self._item(surf, cx, cy, size, t)

    def draw_tiles(self, surf, level, offset):
        self.build()
        ox, oy = offset
        c0, c1 = ox // TILE, (ox + WIDTH) // TILE + 1
        r0, r1 = oy // TILE, (oy + HEIGHT) // TILE + 1
        for c in range(c0, c1 + 1):
            for r in range(r0, r1 + 1):
                if (c, r) in level.solids:
                    img = self.tile_mid if (c, r - 1) in level.solids else self.tile_top
                    surf.blit(img, (c * TILE - ox, r * TILE - oy))
                elif (c, r) in level.platforms:
                    rect = level.platforms[(c, r)].move(-ox, -oy)
                    pygame.draw.rect(surf, OUTLINE, rect.inflate(2, 2), border_radius=6)
                    pygame.draw.rect(surf, self.platform, rect, border_radius=6)
                    hl = [min(255, v + 50) for v in self.platform]
                    pygame.draw.line(surf, hl, (rect.left + 5, rect.top + 4), (rect.right - 6, rect.top + 4), 3)


WORLDS = {
    "meadow": World("meadow", "Sunny Meadow", "flowers",
                    ((120, 195, 250), (210, 240, 255)), (150, 100, 60), (100, 200, 80),
                    (200, 150, 100), (255, 110, 170), bg_meadow, item_flower),
    "lagoon": World("lagoon", "Mermaid Lagoon", "pearls",
                    ((110, 205, 245), (255, 220, 225)), (225, 185, 120), (250, 225, 160),
                    (170, 120, 80), (255, 150, 200), bg_lagoon, item_pearl),
    "snow": World("snow", "Snowy Hills", "snowflakes",
                  ((160, 190, 225), (235, 245, 255)), (120, 140, 170), (250, 252, 255),
                  (170, 210, 240), (90, 170, 255), bg_snow, item_snowflake, snow=True),
    "chocolate": World("chocolate", "Chocolate Land", "chocolates",
                       ((255, 200, 215), (255, 235, 215)), (95, 55, 35), (160, 100, 60),
                       (240, 200, 140), (255, 120, 180), bg_chocolate, item_chocolate),
    "moon": World("moon", "Moon Base", "stars",
                  ((10, 10, 40), (55, 40, 95)), (125, 125, 145), (190, 190, 205),
                  (150, 160, 200), (255, 220, 70), bg_moon, item_star,
                  gravity=1100, jump_speed=720, spring_speed=1000),
}

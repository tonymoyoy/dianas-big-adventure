"""The themed worlds: colors, physics tweaks, backgrounds, tiles and items.

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


def item_diamond(surf, cx, cy, size, t):
    """A blocky pixel-art diamond."""
    px = max(2, int(size / 9))
    pattern = ["..XXX..", ".XLLXX.", "XLXXXXX", ".XXXXD.", "..XXD..", "...D..."]
    colors = {"X": (90, 225, 235), "L": (215, 255, 255), "D": (40, 160, 190)}
    bob = int(math.sin(t * 2) * 2)
    x0, y0 = cx - 3.5 * px, cy - 3 * px + bob
    for j, line in enumerate(pattern):
        for i, ch in enumerate(line):
            if ch != ".":
                pygame.draw.rect(surf, OUTLINE, (x0 + i * px - 2, y0 + j * px - 2, px + 4, px + 4))
    for j, line in enumerate(pattern):
        for i, ch in enumerate(line):
            if ch != ".":
                pygame.draw.rect(surf, colors[ch], (x0 + i * px, y0 + j * px, px, px))


BALLOON_COLORS = [(255, 100, 160), (90, 170, 255), (255, 200, 60), (150, 110, 255)]


def item_balloon(surf, cx, cy, size, t):
    s = size / 40
    color = BALLOON_COLORS[int(cx // 97 + cy // 89) % len(BALLOON_COLORS)]
    sway = math.sin(t * 2) * 3 * s
    body = pygame.Rect(0, 0, 26 * s, 31 * s)
    body.center = (cx + sway, cy - 5 * s)
    pts = [(body.centerx, body.bottom), (cx + sway * 0.3 + 3 * s, cy + 15 * s), (cx - 2 * s, cy + 20 * s)]
    pygame.draw.lines(surf, OUTLINE, False, pts, 2)
    pygame.draw.ellipse(surf, OUTLINE, body.inflate(4, 4))
    pygame.draw.ellipse(surf, color, body)
    knot = [(body.centerx - 3 * s, body.bottom + 3 * s), (body.centerx + 3 * s, body.bottom + 3 * s),
            (body.centerx, body.bottom - 1)]
    pygame.draw.polygon(surf, color, knot)
    pygame.draw.ellipse(surf, WHITE, (body.left + 5 * s, body.top + 5 * s, 6 * s, 9 * s))


def item_icecream(surf, cx, cy, size, t):
    """A two-scoop ice cream cone with a cherry."""
    s = size / 40
    tilt = math.sin(t * 2) * 1.5 * s
    cone = [(cx - 10 * s, cy), (cx + 10 * s, cy), (cx + tilt * 0.3, cy + 20 * s)]
    outlined_polygon(surf, (235, 180, 100), cone)
    pygame.draw.line(surf, (200, 140, 70), (cx - 6 * s, cy + 3 * s), (cx + 4 * s, cy + 13 * s), 2)
    pygame.draw.line(surf, (200, 140, 70), (cx + 6 * s, cy + 3 * s), (cx - 4 * s, cy + 13 * s), 2)
    for dy, color in ((-5, (255, 170, 200)), (-15, (250, 245, 230))):
        p = (cx + tilt, cy + dy * s)
        pygame.draw.circle(surf, OUTLINE, p, 11 * s + 2)
        pygame.draw.circle(surf, color, p, 11 * s)
    pygame.draw.circle(surf, OUTLINE, (cx + tilt + 2 * s, cy - 27 * s), 4 * s + 2)
    pygame.draw.circle(surf, (230, 40, 70), (cx + tilt + 2 * s, cy - 27 * s), 4 * s)
    pygame.draw.circle(surf, WHITE, (cx + tilt - 4 * s, cy - 19 * s), 2.5 * s)


RAINBOW = [(240, 70, 80), (255, 160, 60), (255, 225, 70), (90, 200, 110), (80, 160, 255), (160, 100, 230)]


def item_rainbow(surf, cx, cy, size, t):
    """A little rainbow with a cloud at each end."""
    s = size / 40
    bob = math.sin(t * 2) * 2 * s
    base = cy + 8 * s + bob
    r = 18 * s
    band = max(2, int(3 * s))
    rect = pygame.Rect(0, 0, 2 * (r + 2), 2 * (r + 2))
    rect.center = (cx, base)
    pygame.draw.arc(surf, OUTLINE, rect, 0, math.pi, band + 2)
    for i, color in enumerate(RAINBOW):
        rr = r - i * band
        rect = pygame.Rect(0, 0, 2 * rr, 2 * rr)
        rect.center = (cx, base)
        pygame.draw.arc(surf, color, rect, 0, math.pi, band + 1)
    for side in (-1, 1):
        x = cx + side * (r - 3 * s)
        for dx, dy, cr in ((-5, 0, 6), (0, -4, 7), (5, 0, 6)):
            pygame.draw.circle(surf, OUTLINE, (x + dx * s, base + dy * s), cr * s + 2)
        for dx, dy, cr in ((-5, 0, 6), (0, -4, 7), (5, 0, 6)):
            pygame.draw.circle(surf, WHITE, (x + dx * s, base + dy * s), cr * s)


BARBIE_PINK = (224, 33, 138)   # Pantone 219 C, #E0218A


def item_purse(surf, cx, cy, size, t):
    """A Barbie-pink handbag with a gold heart clasp."""
    s = size / 40
    sway = math.sin(t * 2) * 1.5 * s
    handle = pygame.Rect(0, 0, 18 * s, 18 * s)
    handle.center = (cx + sway, cy - 6 * s)
    pygame.draw.arc(surf, OUTLINE, handle.inflate(4, 4), 0, math.pi, int(5 * s) + 2)
    pygame.draw.arc(surf, (255, 150, 200), handle, 0, math.pi, max(2, int(4 * s)))
    bag = [(cx - 15 * s + sway, cy - 4 * s), (cx + 15 * s + sway, cy - 4 * s),
           (cx + 18 * s + sway, cy + 15 * s), (cx - 18 * s + sway, cy + 15 * s)]
    outlined_polygon(surf, BARBIE_PINK, bag)
    pygame.draw.line(surf, (255, 120, 190), (cx - 14 * s + sway, cy + 1 * s), (cx + 14 * s + sway, cy + 1 * s), 2)
    hx, hy, r = cx + sway, cy + 6 * s, 4 * s
    pygame.draw.circle(surf, (255, 205, 60), (hx - r * 0.5, hy - r * 0.2), r * 0.6)
    pygame.draw.circle(surf, (255, 205, 60), (hx + r * 0.5, hy - r * 0.2), r * 0.6)
    pygame.draw.polygon(surf, (255, 205, 60), [(hx - r * 1.05, hy - r * 0.1), (hx + r * 1.05, hy - r * 0.1), (hx, hy + r)])
    if (t * 1.5) % 2 < 0.3:
        gx, gy = cx + 14 * s, cy - 12 * s
        pygame.draw.line(surf, WHITE, (gx - 4, gy), (gx + 4, gy), 2)
        pygame.draw.line(surf, WHITE, (gx, gy - 4), (gx, gy + 4), 2)


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


def blocky_tree(surf, x, base, h, t):
    """A Minecraft-style tree: square trunk and leaf blocks."""
    b = 22
    trunk = pygame.Rect(0, 0, b, h)
    trunk.midbottom = (x, base)
    pygame.draw.rect(surf, (110, 80, 50), trunk)
    for y in range(trunk.top, trunk.bottom, b):
        pygame.draw.line(surf, (85, 60, 40), (trunk.left, y), (trunk.right, y), 2)
    for row, (n, dy) in enumerate(((5, 0), (5, 1), (3, 2))):
        for i in range(n):
            leaf = pygame.Rect(x - n * b / 2 + i * b, trunk.top - (dy + 1) * b + b, b, b)
            shade = (60, 150, 60) if (i + row) % 2 else (75, 170, 70)
            pygame.draw.rect(surf, shade, leaf)
            pygame.draw.rect(surf, (45, 120, 50), leaf, 2)


def bg_woods(world, surf, cam_x, t):
    surf.blit(world.sky, (0, 0))
    pygame.draw.rect(surf, (255, 240, 150), (770, 50, 90, 90))
    pygame.draw.rect(surf, (255, 220, 90), (785, 65, 60, 60))
    for base in repeat(cam_x - t * 12, 0.1, 1100):
        for x, y, w in ((100, 70, 160), (600, 130, 120)):
            pygame.draw.rect(surf, WHITE, (base + x, y, w, 30))
            pygame.draw.rect(surf, WHITE, (base + x + 30, y - 20, w - 60, 22))
    for base in repeat(cam_x, 0.2, 960):
        for i, h in enumerate((140, 190, 230, 200, 160, 120, 170, 210)):
            pygame.draw.rect(surf, (120, 175, 120), (base + i * 120, HEIGHT - h, 120, h))
    for base in repeat(cam_x, 0.45, 700):
        blocky_tree(surf, base + 120, HEIGHT - 70, 110, t)
        blocky_tree(surf, base + 460, HEIGHT - 70, 150, t)
        # a little red mushroom block
        mx = base + 300
        pygame.draw.rect(surf, (235, 225, 210), (mx - 6, HEIGHT - 92, 12, 22))
        pygame.draw.rect(surf, (220, 60, 60), (mx - 18, HEIGHT - 106, 36, 16))
        pygame.draw.rect(surf, WHITE, (mx - 10, HEIGHT - 104, 6, 6))
        pygame.draw.rect(surf, WHITE, (mx + 4, HEIGHT - 102, 6, 6))


def ferris_wheel(surf, x, y, r, t):
    rot = t * 0.4
    pygame.draw.polygon(surf, (150, 140, 190), [(x - r * 0.6, HEIGHT), (x, y), (x + r * 0.6, HEIGHT)], 6)
    pygame.draw.circle(surf, (200, 180, 240), (x, y), r, 5)
    pygame.draw.circle(surf, (200, 180, 240), (x, y), r * 0.6, 3)
    for i in range(8):
        a = rot + i * math.tau / 8
        ex, ey = x + math.cos(a) * r, y + math.sin(a) * r
        pygame.draw.line(surf, (200, 180, 240), (x, y), (ex, ey), 2)
        cab = pygame.Rect(0, 0, 22, 18)
        cab.midtop = (ex, ey)
        pygame.draw.rect(surf, BALLOON_COLORS[i % 4], cab, border_radius=6)
    pygame.draw.circle(surf, (255, 205, 60), (x, y), 9)


def carousel(surf, x, base, t):
    roof_y = base - 130
    for i in range(4):
        px = x - 75 + i * 50
        pygame.draw.line(surf, (255, 215, 90), (px, roof_y), (px, base - 10), 4)
        hy = base - 55 + math.sin(t * 3 + i * 1.5) * 10
        pygame.draw.ellipse(surf, WHITE, (px - 16, hy - 8, 32, 16))
        pygame.draw.circle(surf, WHITE, (px + 13, int(hy - 10)), 7)
    pygame.draw.rect(surf, (255, 150, 200), (x - 95, base - 14, 190, 14), border_radius=5)
    roof = [(x - 105, roof_y), (x, roof_y - 70), (x + 105, roof_y)]
    pygame.draw.polygon(surf, (255, 110, 170), roof)
    for i in range(0, 6, 2):
        k0, k1 = i / 6, (i + 1) / 6
        stripe = [(x, roof_y - 70), (x - 105 + 210 * k0, roof_y), (x - 105 + 210 * k1, roof_y)]
        pygame.draw.polygon(surf, WHITE, stripe)
    for i in range(7):
        pygame.draw.circle(surf, (255, 110, 170) if i % 2 else WHITE, (x - 90 + i * 30, roof_y + 4), 12)
    pygame.draw.circle(surf, (255, 205, 60), (x, roof_y - 74), 7)


def bg_themepark(world, surf, cam_x, t):
    surf.blit(world.sky, (0, 0))
    for i in range(3):   # gentle fireworks
        k = (t * 0.5 + i / 3) % 1
        fx, fy = (180 + i * 300 - cam_x * 0.05) % WIDTH, 90 + i * 25
        color = BALLOON_COLORS[i]
        for j in range(10):
            a = j * math.tau / 10
            pygame.draw.circle(surf, color, (fx + math.cos(a) * 50 * k, fy + math.sin(a) * 50 * k), max(1, 4 * (1 - k)))
    for base in repeat(cam_x, 0.15, 1400):
        castle(surf, base + 400, HEIGHT - 80, t)
        ferris_wheel(surf, base + 1000, HEIGHT - 260, 140, t)
    for base in repeat(cam_x, 0.45, 900):
        carousel(surf, base + 250, HEIGHT - 70, t)
        # bunting
        pts = [(base + 450 + i * 40, HEIGHT - 230 + math.sin(i * 0.8) * 14) for i in range(11)]
        pygame.draw.lines(surf, (120, 100, 140), False, pts, 2)
        for i, (px, py) in enumerate(pts[:-1]):
            pygame.draw.polygon(surf, BALLOON_COLORS[i % 4], [(px + 4, py), (px + 34, py + 2), (px + 19, py + 24)])


def swing_set(surf, x, base, t):
    top = base - 150
    for side in (-1, 1):
        sx = x + side * 90
        pygame.draw.line(surf, (230, 90, 80), (sx - 35, base), (sx, top), 7)
        pygame.draw.line(surf, (230, 90, 80), (sx + 35, base), (sx, top), 7)
    pygame.draw.line(surf, (230, 90, 80), (x - 90, top), (x + 90, top), 8)
    for i, cx in enumerate((x - 40, x + 40)):
        a = math.sin(t * 2.2 + i * 2.5) * 0.5
        sx, sy = cx + math.sin(a) * 100, top + math.cos(a) * 100
        pygame.draw.line(surf, (90, 90, 110), (cx - 12, top), (sx - 12, sy), 2)
        pygame.draw.line(surf, (90, 90, 110), (cx + 12, top), (sx + 12, sy), 2)
        pygame.draw.rect(surf, (255, 200, 60), (sx - 16, sy - 3, 32, 7), border_radius=3)


def slide(surf, x, base):
    top = base - 130
    for lx in (x - 18, x + 18):
        pygame.draw.line(surf, (80, 150, 230), (lx, base), (lx, top), 6)
    for y in range(top + 15, base, 22):
        pygame.draw.line(surf, (80, 150, 230), (x - 18, y), (x + 18, y), 4)
    pygame.draw.rect(surf, (80, 150, 230), (x - 26, top - 8, 52, 10), border_radius=4)
    chute = [(x + 20, top), (x + 34, top), (x + 175, base - 6), (x + 150, base - 6)]
    pygame.draw.polygon(surf, (255, 200, 60), chute)
    pygame.draw.polygon(surf, (230, 160, 40), chute, 3)


def bg_playground(world, surf, cam_x, t):
    surf.blit(world.sky, (0, 0))
    pygame.draw.circle(surf, (255, 245, 170), (130, 90), 60)
    pygame.draw.circle(surf, (255, 225, 80), (130, 90), 42)
    for base in repeat(cam_x - t * 15, 0.1, 1100):
        cloud(surf, base + 300, 80, 1.1)
        cloud(surf, base + 800, 140, 0.8)
    for base in repeat(cam_x, 0.2, 800):
        for x in (100, 330, 600):
            pygame.draw.rect(surf, (130, 95, 65), (base + x - 8, HEIGHT - 190, 16, 120))
            for dx, dy, r in ((0, -200, 55), (-40, -170, 40), (40, -170, 40)):
                pygame.draw.circle(surf, (95, 175, 95), (int(base + x + dx), HEIGHT + dy), r)
    for base in repeat(cam_x, 0.45, 1000):
        swing_set(surf, base + 200, HEIGHT - 70, t)
        slide(surf, base + 520, HEIGHT - 70)
        # sandbox with a bucket
        box = pygame.Rect(base + 760, HEIGHT - 100, 170, 30)
        pygame.draw.rect(surf, (240, 215, 150), box, border_radius=6)
        pygame.draw.rect(surf, (200, 120, 70), box, 6, border_radius=6)
        pygame.draw.polygon(surf, (90, 170, 255), [(box.left + 40, box.top - 22), (box.left + 70, box.top - 22),
                                                    (box.left + 64, box.top + 4), (box.left + 46, box.top + 4)])


def hot_air_balloon(surf, x, y, color):
    pygame.draw.circle(surf, color, (x, y), 40)
    pygame.draw.polygon(surf, color, [(x - 34, y + 20), (x + 34, y + 20), (x + 12, y + 55), (x - 12, y + 55)])
    pygame.draw.ellipse(surf, WHITE, (x - 12, y - 40, 24, 95), 4)
    for dx in (-10, 10):
        pygame.draw.line(surf, (120, 100, 90), (x + dx, y + 55), (x + dx * 0.8, y + 72), 2)
    pygame.draw.rect(surf, (170, 110, 70), (x - 11, y + 70, 22, 16), border_radius=3)


def bg_sky(world, surf, cam_x, t):
    surf.blit(world.sky, (0, 0))
    # big rainbow far away
    rx = int(500 - cam_x * 0.03) % 1400 - 200
    for i, color in enumerate(RAINBOW):
        r = 330 - i * 16
        pygame.draw.circle(surf, color, (rx, HEIGHT + 60), r, 16)
    for base in repeat(cam_x - t * 8, 0.08, 1200):
        cloud(surf, base + 100, 100, 1.4, (250, 250, 255))
        cloud(surf, base + 700, 60, 1.0, (250, 250, 255))
    for base in repeat(cam_x, 0.2, 1000):
        hot_air_balloon(surf, base + 300, 150 + math.sin(t * 1.2) * 12, (255, 120, 170))
        hot_air_balloon(surf, base + 780, 230 + math.sin(t * 1.2 + 2) * 12, (120, 180, 255))
    for base in repeat(cam_x - t * 40, 0.3, 900):   # birds flying by
        for i in range(3):
            bx, by = base + 200 + i * 40, 120 + i * 18
            flap = math.sin(t * 8 + i) * 6
            pygame.draw.lines(surf, (80, 80, 110), False, [(bx - 12, by - flap), (bx, by), (bx + 12, by - flap)], 3)
    for base in repeat(cam_x, 0.5, 700):
        cloud(surf, base + 50, HEIGHT - 70, 2.2, (235, 240, 255))
        cloud(surf, base + 400, HEIGHT - 50, 2.6, (235, 240, 255))


def dream_house(surf, x, base, t):
    """A three-storey pink dream house with balconies and a slide into the pool."""
    wall, trim = (255, 235, 245), (255, 150, 200)
    house = pygame.Rect(0, 0, 300, 250)
    house.midbottom = (x, base)
    pygame.draw.rect(surf, wall, house)
    for i in range(3):   # floors: windows + balcony rails
        fy = house.bottom - (i + 1) * 80
        for wx in (house.left + 30, house.centerx - 25, house.right - 80):
            win = pygame.Rect(wx, fy + 18, 50, 40)
            pygame.draw.rect(surf, (170, 215, 250), win, border_top_left_radius=20, border_top_right_radius=20)
            pygame.draw.rect(surf, trim, win, 4, border_top_left_radius=20, border_top_right_radius=20)
        if i:
            pygame.draw.rect(surf, BARBIE_PINK, (house.left - 15, fy + 70, house.w + 30, 10), border_radius=4)
            for bx in range(house.left - 10, house.right + 15, 16):
                pygame.draw.line(surf, WHITE, (bx, fy + 70), (bx, fy + 56), 3)
            pygame.draw.line(surf, WHITE, (house.left - 12, fy + 56), (house.right + 12, fy + 56), 3)
    roof = [(house.left - 30, house.top), (x, house.top - 90), (house.right + 30, house.top)]
    pygame.draw.polygon(surf, BARBIE_PINK, roof)
    pygame.draw.polygon(surf, (190, 20, 110), roof, 4)
    hy = house.top - 40
    pygame.draw.circle(surf, WHITE, (x - 7, hy - 3), 9)
    pygame.draw.circle(surf, WHITE, (x + 7, hy - 3), 9)
    pygame.draw.polygon(surf, WHITE, [(x - 16, hy), (x + 16, hy), (x, hy + 17)])
    door = pygame.Rect(0, 0, 44, 60)
    door.midbottom = (x, base)
    pygame.draw.rect(surf, BARBIE_PINK, door, border_top_left_radius=22, border_top_right_radius=22)
    # slide from the top balcony down to a pool
    pygame.draw.polygon(surf, (255, 205, 60), [(house.right + 10, house.top + 90), (house.right + 30, house.top + 90),
                                               (house.right + 170, base - 30), (house.right + 140, base - 30)])
    pool = pygame.Rect(house.right + 110, base - 30, 170, 30)
    pygame.draw.rect(surf, (90, 200, 240), pool, border_radius=10)
    pygame.draw.rect(surf, WHITE, pool, 5, border_radius=10)
    shimmer = math.sin(t * 3) * 10
    pygame.draw.line(surf, WHITE, (pool.left + 30 + shimmer, pool.top + 12), (pool.left + 70 + shimmer, pool.top + 12), 3)


def pink_car(surf, x, base, t):
    """A little pink convertible."""
    body = pygame.Rect(0, 0, 150, 34)
    body.midbottom = (x, base - 14)
    pygame.draw.rect(surf, BARBIE_PINK, body, border_radius=14)
    pygame.draw.rect(surf, BARBIE_PINK, (body.left + 30, body.top - 16, 70, 20), border_top_left_radius=12)
    pygame.draw.line(surf, (190, 225, 250), (body.left + 40, body.top - 12), (body.left + 50, body.top - 30), 5)
    pygame.draw.rect(surf, WHITE, (body.left + 6, body.top + 12, body.w - 12, 5))
    pygame.draw.circle(surf, (255, 240, 150), (body.right - 6, body.top + 10), 6)
    for wx in (body.left + 30, body.right - 30):
        pygame.draw.circle(surf, (60, 50, 70), (wx, base - 14), 16)
        pygame.draw.circle(surf, WHITE, (wx, base - 14), 7)


def bg_dream(world, surf, cam_x, t):
    surf.blit(world.sky, (0, 0))
    pygame.draw.circle(surf, (255, 245, 200), (130, 90), 55)
    for base in repeat(cam_x - t * 12, 0.1, 1100):
        cloud(surf, base + 300, 80, 1.0, (255, 235, 245))
        cloud(surf, base + 800, 130, 0.8, (255, 235, 245))
    for i in range(12):   # floating sparkles
        sx = (i * 173 - cam_x * 0.08) % WIDTH
        sy = 60 + (i * 97) % 260 + math.sin(t * 2 + i) * 8
        if (t * 1.5 + i * 0.37) % 2 < 1.4:
            pygame.draw.line(surf, WHITE, (sx - 5, sy), (sx + 5, sy), 2)
            pygame.draw.line(surf, WHITE, (sx, sy - 5), (sx, sy + 5), 2)
    for base in repeat(cam_x, 0.2, 900):
        for x in (0, 450):
            pygame.draw.circle(surf, (255, 190, 220), (int(base + x), HEIGHT + 130), 290)
    for base in repeat(cam_x, 0.45, 1100):
        dream_house(surf, base + 260, HEIGHT - 96, t)
        pink_car(surf, base + 820, HEIGHT - 94, t)
        px = base + 1000
        pygame.draw.line(surf, (190, 140, 100), (px, HEIGHT - 75), (px - 12, HEIGHT - 260), 12)
        for a in (-2.8, -2.1, -1.2, -0.4, 0.2):
            pygame.draw.line(surf, (70, 175, 110), (px - 12, HEIGHT - 260),
                             (px - 12 + math.cos(a) * 75, HEIGHT - 240 + math.sin(a) * 30), 10)

# ----------------------------------------------------------------- world
class World:
    def __init__(self, key, name, item_name, sky, ground, ground_top, platform, accent,
                 background, item, gravity=GRAVITY, jump_speed=JUMP_SPEED,
                 spring_speed=SPRING_SPEED, snow=False, tiles="round"):
        self.key, self.name, self.item_name = key, name, item_name
        self.sky_colors = sky
        self.ground, self.ground_top, self.platform, self.accent = ground, ground_top, platform, accent
        self._background, self._item = background, item
        self.gravity, self.jump_speed, self.spring_speed = gravity, jump_speed, spring_speed
        self.snow = snow
        self.tile_style = tiles    # round | blocky | brick
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
        if self.tile_style == "blocky":
            return self._make_blocky_tile(rng, top)
        if self.tile_style == "brick":
            return self._make_brick_tile(top)
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

    def _make_blocky_tile(self, rng, top):
        """A Minecraft-style grass/dirt block made of 8px pixels."""
        px = 8
        s = pygame.Surface((TILE, TILE))
        for y in range(0, TILE, px):
            for x in range(0, TILE, px):
                k = rng.choice((-18, 0, 0, 14))
                color = [max(0, min(255, c + k)) for c in self.ground]
                if top and (y < px * 2 or (y < px * 3 and rng.random() < 0.5)):
                    color = [max(0, min(255, c + k)) for c in self.ground_top]
                pygame.draw.rect(s, color, (x, y, px, px))
        pygame.draw.rect(s, [max(0, c - 35) for c in self.ground], s.get_rect(), 1)
        return s

    def _make_brick_tile(self, top):
        """Pastel paving bricks with a candy-striped top edge."""
        s = pygame.Surface((TILE, TILE))
        s.fill(self.ground)
        line = [max(0, c - 30) for c in self.ground]
        for j, y in enumerate(range(0, TILE, 16)):
            pygame.draw.line(s, line, (0, y), (TILE, y), 2)
            off = 12 if j % 2 else 0
            for x in range(off, TILE + 1, 24):
                pygame.draw.line(s, line, (x, y), (x, y + 16), 2)
        if top:
            for i, x in enumerate(range(0, TILE, 12)):
                pygame.draw.rect(s, self.ground_top if i % 2 else WHITE, (x, 0, 12, 10))
            pygame.draw.line(s, line, (0, 10), (TILE, 10), 2)
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
    "woods": World("woods", "Blocky Woods", "diamonds",
                   ((120, 180, 255), (200, 230, 255)), (135, 95, 60), (95, 175, 70),
                   (160, 120, 80), (90, 225, 235), bg_woods, item_diamond, tiles="blocky"),
    "themepark": World("themepark", "Magic Theme Park", "balloons",
                       ((255, 180, 210), (255, 235, 200)), (235, 200, 225), (255, 120, 180),
                       (160, 140, 230), (255, 120, 180), bg_themepark, item_balloon, tiles="brick"),
    "playground": World("playground", "Playground Park", "ice creams",
                        ((130, 200, 255), (220, 245, 255)), (220, 175, 120), (120, 205, 90),
                        (255, 170, 80), (255, 140, 60), bg_playground, item_icecream),
    "sky": World("sky", "Cloud Kingdom", "rainbows",
                 ((90, 170, 255), (210, 235, 255)), (225, 235, 255), (255, 255, 255),
                 (255, 255, 255), (160, 100, 230), bg_sky, item_rainbow,
                 gravity=1500, jump_speed=800, spring_speed=1150),
    "dream": World("dream", "Pink Dream House", "purses",
                   ((255, 175, 215), (255, 235, 245)), (255, 170, 210), BARBIE_PINK,
                   (255, 255, 255), BARBIE_PINK, bg_dream, item_purse, tiles="brick"),
}

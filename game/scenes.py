"""Game screens. Each scene has update(dt) and draw(surf); the App switches between them."""
import math

import pygame

from .camera import Camera
from .effects import Particles, Snow
from .levels import LEVELS
from .characters import DOGS, PuppyFollower, draw_diana, draw_puppy
from .player import Player
from .settings import FALL_LIMIT, GOLD, HEIGHT, OUTLINE, TILE, TITLE, WHITE, WIDTH
from .tiles import Level
from .worlds import WORLDS


def draw_text(surf, text, font, center, color=WHITE, outline=OUTLINE, width=3):
    img = font.render(text, True, color)
    rect = img.get_rect(center=center)
    if outline:
        shadow = font.render(text, True, outline)
        for dx in range(-width, width + 1, width):
            for dy in range(-width, width + 1, width):
                if dx or dy:
                    surf.blit(shadow, rect.move(dx, dy))
    surf.blit(img, rect)
    return rect


def panel(surf, rect, alpha=200, color=(255, 255, 255)):
    s = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(s, (*color, alpha), s.get_rect(), border_radius=24)
    surf.blit(s, rect)
    pygame.draw.rect(surf, OUTLINE, rect, 4, border_radius=24)


FINISH_PINK = (255, 105, 180)


def draw_heart(surf, cx, cy, r, color):
    pygame.draw.circle(surf, color, (cx - r * 0.5, cy - r * 0.2), r * 0.55)
    pygame.draw.circle(surf, color, (cx + r * 0.5, cy - r * 0.2), r * 0.55)
    pygame.draw.polygon(surf, color, [(cx - r * 1.02, cy - r * 0.05), (cx + r * 1.02, cy - r * 0.05), (cx, cy + r)])


def draw_flag_pole(surf, base, height, color, t, wave=True, big=False):
    """Flag on a pole; base is the pole's bottom. big=True is the pink finish flag with a heart."""
    bx, by = base
    pygame.draw.rect(surf, OUTLINE, (bx - 4, by - height - 2, 8, height + 2), border_radius=3)
    pygame.draw.rect(surf, (235, 235, 235), (bx - 2, by - height, 4, height))
    pygame.draw.circle(surf, OUTLINE, (bx, by - height - 4), 8)
    pygame.draw.circle(surf, GOLD, (bx, by - height - 4), 6)
    if big:
        color = FINISH_PINK
    fw, fh = (70, 48) if big else (40, 28)
    top = by - height + 4

    def off(k):
        return math.sin(t * 5 - k * 4) * 5 * k if wave else k * 4

    upper = [(bx + 2 + k / 8 * fw, top + off(k / 8)) for k in range(9)]
    lower = [(x, y + fh) for x, y in reversed(upper)]
    pygame.draw.polygon(surf, color, upper + lower)
    pygame.draw.polygon(surf, OUTLINE, upper + lower, 2)
    if big:
        hx, hy = bx + 2 + fw * 0.5, top + fh * 0.5 + off(0.5)
        draw_heart(surf, hx, hy, fh * 0.28, WHITE)
        for i in range(1, 8, 2):
            x, y = upper[i]
            pygame.draw.circle(surf, (255, 190, 225), (x, y + 4), 2)
            pygame.draw.circle(surf, (255, 190, 225), (x, y + fh - 4), 2)


class Scene:
    music = None   # song name from game.music.SONGS, started by App.switch

    def __init__(self, app):
        self.app = app
        self.t = 0.0

    def handle_event(self, e):
        pass

    def update(self, dt):
        self.t += dt

    def draw(self, surf):
        pass


# ---------------------------------------------------------------- title
class TitleScene(Scene):
    music = "title"

    def update(self, dt):
        super().update(dt)
        c = self.app.controls
        if c.confirm or c.jump_pressed:
            self.app.sound.play("select")
            self.app.switch(DogSelectScene(self.app))
        elif c.back:
            self.app.running = False

    def handle_event(self, e):
        if e.type == pygame.MOUSEBUTTONDOWN:
            self.app.switch(DogSelectScene(self.app))

    def draw(self, surf):
        world = WORLDS["meadow"]
        world.draw_background(surf, self.t * 40, self.t)
        pygame.draw.rect(surf, world.ground_top, (0, HEIGHT - 70, WIDTH, 16))
        pygame.draw.rect(surf, world.ground, (0, HEIGHT - 56, WIDTH, 56))
        bob = abs(math.sin(self.t * 3)) * 40
        draw_diana(surf, WIDTH / 2 - 30, HEIGHT - 70 - bob, 1, 0, self.t * 6, bob < 2, self.t, scale=2.0)
        draw_puppy(surf, WIDTH / 2 - 130, HEIGHT - 70 - abs(math.sin(self.t * 3 - 0.5)) * 25, 1, self.t, True, scale=2.0,
                   dog=self.app.dog)
        for i, w in enumerate(WORLDS.values()):
            a = self.t * 0.8 + i * math.tau / len(WORLDS)
            w.draw_item(surf, WIDTH / 2 + math.cos(a) * 220, 330 + math.sin(a) * 40, 40, self.t)
        draw_text(surf, TITLE, self.app.font_big, (WIDTH / 2, 110 + math.sin(self.t * 2) * 6), GOLD, width=4)
        if (self.t % 1.2) < 0.85:
            draw_text(surf, "Press SPACE to play!", self.app.font_mid, (WIDTH / 2, 200))
        draw_text(surf, "M: music on/off", self.app.font_small, (WIDTH - 110, HEIGHT - 24))


# ---------------------------------------------------------------- dog select
class DogSelectScene(Scene):
    """Pick which border collie comes along: Azulita or Vainilla."""
    music = "title"
    CARD_W, CARD_H, GAP = 300, 280, 60

    def __init__(self, app):
        super().__init__(app)
        self.keys = list(DOGS)
        self.selected = self.keys.index(app.dog)

    def _card_rect(self, i):
        total = len(self.keys) * self.CARD_W + (len(self.keys) - 1) * self.GAP
        x = (WIDTH - total) // 2 + i * (self.CARD_W + self.GAP)
        return pygame.Rect(x, 130, self.CARD_W, self.CARD_H)

    def _choose(self, i):
        self.app.save.dog = self.keys[i]
        self.app.save.save()
        self.app.sound.play("select")
        self.app.switch(LevelSelectScene(self.app))

    def handle_event(self, e):
        if e.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN):
            for i in range(len(self.keys)):
                if self._card_rect(i).collidepoint(e.pos):
                    self.selected = i
                    if e.type == pygame.MOUSEBUTTONDOWN:
                        self._choose(i)

    def update(self, dt):
        super().update(dt)
        c = self.app.controls
        if c.nav_x:
            new = max(0, min(len(self.keys) - 1, self.selected + c.nav_x))
            if new != self.selected:
                self.selected = new
                self.app.sound.play("select")
        if c.confirm or c.jump_pressed:
            self._choose(self.selected)
        elif c.back:
            self.app.switch(TitleScene(self.app))

    def draw(self, surf):
        world = WORLDS["meadow"]
        world.draw_background(surf, self.t * 30, self.t)
        draw_text(surf, "Who comes with Diana?", self.app.font_big, (WIDTH / 2, 64), GOLD, width=4)
        for i, key in enumerate(self.keys):
            dog = DOGS[key]
            rect = self._card_rect(i)
            sel = i == self.selected
            if sel:
                rect = rect.inflate(16, 16).move(0, -8 + math.sin(self.t * 4) * 4)
            panel(surf, rect, 230 if sel else 170, (205, 230, 250))
            pygame.draw.rect(surf, dog.collar if sel else OUTLINE, rect, 6 if sel else 4, border_radius=24)
            ground = rect.bottom - 70
            pygame.draw.rect(surf, world.ground_top, (rect.left + 20, ground, rect.w - 40, 10), border_radius=5)
            hop = abs(math.sin(self.t * 5)) * 22 if sel else 0
            draw_puppy(surf, rect.centerx - 4, ground - hop, 1, self.t, sel, scale=3.4, dog=key)
            if sel:
                draw_heart(surf, rect.centerx + 70, rect.top + 40 + math.sin(self.t * 3) * 4, 12, dog.collar)
            draw_text(surf, dog.name, self.app.font_mid, (rect.centerx, rect.bottom - 34),
                      WHITE if sel else (225, 225, 225))
        draw_text(surf, "Left / Right to choose,  SPACE to go!", self.app.font_small, (WIDTH / 2, 500))


# ---------------------------------------------------------------- level select
class LevelSelectScene(Scene):
    music = "title"
    CARD_W, CARD_H, GAP = 160, 250, 20

    def __init__(self, app, selected=None):
        super().__init__(app)
        self.selected = selected if selected is not None else app.save.unlocked - 1

    def _card_rect(self, i):
        total = len(LEVELS) * self.CARD_W + (len(LEVELS) - 1) * self.GAP
        x = (WIDTH - total) // 2 + i * (self.CARD_W + self.GAP)
        return pygame.Rect(x, 185, self.CARD_W, self.CARD_H)

    def _start(self, i):
        if i < self.app.save.unlocked:
            self.app.sound.play("select")
            self.app.switch(PlayScene(self.app, i))
        else:
            self.app.sound.play("locked")

    def handle_event(self, e):
        if e.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN):
            for i in range(len(LEVELS)):
                if self._card_rect(i).collidepoint(e.pos):
                    self.selected = i
                    if e.type == pygame.MOUSEBUTTONDOWN:
                        self._start(i)

    def update(self, dt):
        super().update(dt)
        c = self.app.controls
        if c.nav_x:
            new = max(0, min(len(LEVELS) - 1, self.selected + c.nav_x))
            if new != self.selected:
                self.selected = new
                self.app.sound.play("select")
        if c.confirm or c.jump_pressed:
            self._start(self.selected)
        elif c.back:
            self.app.switch(DogSelectScene(self.app))

    def draw(self, surf):
        WORLDS[LEVELS[self.selected].world].draw_background(surf, self.t * 30, self.t)
        draw_text(surf, "Choose a world!", self.app.font_big, (WIDTH / 2, 56), GOLD, width=4)
        for i, ldef in enumerate(LEVELS):
            world = WORLDS[ldef.world]
            rect = self._card_rect(i)
            sel = i == self.selected
            if sel:
                rect = rect.inflate(16, 16).move(0, -8 + math.sin(self.t * 4) * 4)
            card = pygame.Surface(rect.size)
            world.build()
            card.blit(pygame.transform.smoothscale(world.sky, rect.size), (0, 0))
            pygame.draw.rect(card, world.ground, (0, rect.h - 60, rect.w, 60))
            pygame.draw.rect(card, world.ground_top, (0, rect.h - 60, rect.w, 12))
            locked = i >= self.app.save.unlocked
            if not locked:
                world.draw_item(card, rect.w / 2, rect.h / 2 - 10, 70 if sel else 60, self.t)
            else:
                shade = pygame.Surface(rect.size, pygame.SRCALPHA)
                shade.fill((30, 30, 50, 160))
                card.blit(shade, (0, 0))
            surf.blit(card, rect)
            pygame.draw.rect(surf, WHITE if sel else OUTLINE, rect, 6 if sel else 4, border_radius=4)
            draw_text(surf, str(i + 1), self.app.font_mid, (rect.centerx, rect.top + 30))
            if locked:
                cx, cy = rect.centerx, rect.centery - 10
                pygame.draw.arc(surf, (230, 230, 230), (cx - 18, cy - 38, 36, 44), 0, math.pi, 6)
                pygame.draw.rect(surf, GOLD, (cx - 26, cy - 16, 52, 40), border_radius=6)
                pygame.draw.rect(surf, OUTLINE, (cx - 26, cy - 16, 52, 40), 3, border_radius=6)
                pygame.draw.circle(surf, OUTLINE, (cx, cy + 2), 5)
            else:
                total = sum(ch == "*" for row in ldef.rows for ch in row)
                best = self.app.save.best.get(i)
                label = f"{best}/{total}" if best is not None else "New!"
                draw_text(surf, label, self.app.font_small, (rect.centerx, rect.bottom - 26))
        sel_rect = self._card_rect(self.selected)
        hop = abs(math.sin(self.t * 4)) * 10
        draw_diana(surf, sel_rect.centerx + 8, sel_rect.top - 14 - hop, 1, 0, 0, True, self.t)
        draw_puppy(surf, sel_rect.centerx - 30, sel_rect.top - 14 - hop, 1, self.t, False, dog=self.app.dog)
        draw_text(surf, WORLDS[LEVELS[self.selected].world].name, self.app.font_mid, (WIDTH / 2, 470))
        draw_text(surf, "Left / Right to choose,  SPACE to go!", self.app.font_small, (WIDTH / 2, 515))


# ---------------------------------------------------------------- gameplay
class PlayScene(Scene):
    FINISH_TIME = 2.2
    RESPAWN_TIME = 0.7

    def __init__(self, app, index):
        super().__init__(app)
        self.index = index
        ldef = LEVELS[index]
        self.world = WORLDS[ldef.world]
        self.music = ldef.world
        self.level = Level(ldef.rows)
        self.player = Player(self.level.start)
        self.camera = Camera(self.level.pixel_w, self.level.pixel_h)
        self.camera.snap(self.player.rect)
        self.puppy = PuppyFollower(self.player, app.dog)
        self.particles = Particles()
        self.snow = Snow() if self.world.snow else None
        self.respawn_point = self.level.start
        self.collected = 0
        self.total = len(self.level.items)
        self.state = "play"      # play | respawn | finish | paused
        self.timer = 0.0
        self.finished = False

    def update(self, dt):
        super().update(dt)
        c = self.app.controls
        self.timer += dt

        if self.state == "paused":
            if c.confirm or c.jump_pressed:
                self.state = "play"
            elif c.back:
                self.app.switch(LevelSelectScene(self.app, self.index))
            return
        if c.back and self.state == "play":
            self.state = "paused"
            return

        if self.state == "play":
            self._update_play(dt, c)
        elif self.state == "respawn":
            if self.timer >= self.RESPAWN_TIME:
                self.player.reset(self.respawn_point)
                self.puppy.reset(self.player)
                self.camera.snap(self.player.rect, self.player.facing)
                self.particles.poof(self.player.rect.centerx, self.player.rect.centery)
                self.state = "play"
        elif self.state == "finish":
            self.player.vx = 0
            if int((self.timer - dt) * 3) != int(self.timer * 3):
                fx, fy = self.level.finish_base
                self.particles.confetti(fx, fy - TILE * 2, 25)
            if self.timer >= self.FINISH_TIME:
                self.app.switch(LevelCompleteScene(self.app, self.index, self.collected, self.total))

        for s in (*self.level.springs, *self.level.pit_pads):
            s.squash = max(0.0, s.squash - dt * 4)
        self.particles.update(dt)
        self.camera.update(self.player.rect, self.player.facing, dt)
        if self.snow:
            self.snow.update(dt, self.camera.x, self.t)

    def _update_play(self, dt, controls):
        p = self.player
        events = p.update(dt, controls, self.level, self.world)
        self.puppy.update(p)
        r = p.rect
        if "jump" in events:
            self.app.sound.play("jump")
        if "bounce" in events:
            self.app.sound.play("bounce")
        if "land" in events:
            self.particles.dust(r.centerx, r.bottom)
        # Remember the last spot standing firmly on ground so falls cost almost nothing
        row = r.bottom // TILE
        if p.on_ground and self.level.is_solid(r.left // TILE, row) and self.level.is_solid((r.right - 1) // TILE, row):
            self.respawn_point = (r.centerx, r.bottom)

        for item in self.level.items:
            if not item.taken and r.colliderect(item.rect):
                item.taken = True
                self.collected += 1
                self.particles.sparkle(*item.rect.center, self.world.accent)
                self.app.sound.play("collect")

        for cp in self.level.checkpoints:
            if not cp.active and r.colliderect(cp.rect):
                for other in self.level.checkpoints:
                    other.active = other is cp or other.active
                self.respawn_point = cp.base
                self.particles.sparkle(cp.base[0], cp.base[1] - TILE * 2, self.world.accent, 20)
                self.app.sound.play("checkpoint")

        if self.level.finish and r.colliderect(self.level.finish):
            self.state, self.timer = "finish", 0.0
            self.finished = True
            self.app.save.record(self.index, self.collected)
            fx, fy = self.level.finish_base
            self.particles.confetti(fx, fy - TILE * 2, 60)
            self.app.sound.play("finish")
        elif r.top > self.level.pixel_h + FALL_LIMIT:
            self.state, self.timer = "respawn", 0.0
            self.app.sound.play("respawn")

    # drawing
    def draw(self, surf):
        off = self.camera.offset
        self.world.draw_background(surf, self.camera.x, self.t)
        self.world.draw_tiles(surf, self.level, off)
        self._draw_objects(surf, off)
        if self.state != "respawn":
            if self.state == "finish":
                hop = abs(math.sin(self.timer * 6)) * 20
                self.puppy.draw(surf, off, self.t, abs(math.sin(self.timer * 6 - 0.8)) * 14)
                draw_diana(surf, self.player.x - off[0] + self.player.w / 2, self.player.y - off[1] + self.player.h - hop,
                           1, 0, 0, False, self.t)
            else:
                self.puppy.draw(surf, off, self.t)
                self.player.draw(surf, off, self.t)
        self.particles.draw(surf, off)
        if self.snow:
            self.snow.draw(surf)
        self._draw_hud(surf)
        if self.state == "paused":
            shade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            shade.fill((20, 20, 40, 150))
            surf.blit(shade, (0, 0))
            draw_text(surf, "Paused", self.app.font_big, (WIDTH / 2, HEIGHT / 2 - 50), GOLD, width=4)
            draw_text(surf, "SPACE: keep playing     ESC: choose world", self.app.font_small, (WIDTH / 2, HEIGHT / 2 + 30))

    def _draw_objects(self, surf, off):
        ox, oy = off
        for s in self.level.springs:
            r = s.rect.move(-ox, -oy)
            h = int(r.h * (1 - 0.5 * s.squash))
            pad = pygame.Rect(r.left, r.bottom - h, r.w, h)
            pygame.draw.rect(surf, OUTLINE, pad.inflate(4, 4), border_radius=10)
            pygame.draw.rect(surf, (120, 220, 120), pad, border_radius=10)
            pygame.draw.line(surf, (200, 255, 200), (pad.left + 8, pad.top + 5), (pad.right - 8, pad.top + 5), 3)
            if (self.t % 1.0) < 0.6 and s.squash == 0:
                ax, ay = r.centerx, r.top - 16 + math.sin(self.t * 6) * 3
                pygame.draw.polygon(surf, WHITE, [(ax - 8, ay + 4), (ax, ay - 6), (ax + 8, ay + 4)])
        for pad in self.level.pit_pads:
            self._draw_pit_pad(surf, pad.rect.move(-ox, -oy), pad.squash)
        for cp in self.level.checkpoints:
            bx, by = cp.base
            color = self.world.accent if cp.active else (200, 200, 200)
            draw_flag_pole(surf, (bx - ox, by - oy), TILE * 2 - 4, color, self.t, wave=cp.active)
        if self.level.finish:
            bx, by = self.level.finish_base
            draw_flag_pole(surf, (bx - ox, by - oy), TILE * 3, None, self.t, big=True)
        for item in self.level.items:
            if item.taken:
                continue
            cx, cy = item.rect.centerx - ox, item.rect.centery - oy
            if -40 < cx < WIDTH + 40:
                bob = math.sin(self.t * 3 + item.phase) * 5
                self.world.draw_item(surf, cx, cy + bob, 34, self.t + item.phase)

    def _draw_pit_pad(self, surf, r, squash):
        """Striped trampoline whose bed sags when Diana lands on it."""
        if r.right < 0 or r.left > WIDTH:
            return
        rim = r.top + 6
        dip = int(20 * squash)    # how far the middle of the bed sinks
        for x in (r.left + 6, r.right - 6):
            pygame.draw.line(surf, OUTLINE, (x, rim), (x, r.bottom), 4)

        def bed(k):  # point on the bed, k from 0 (left rim) to 1 (right rim)
            return (r.left + r.w * k, rim + dip * (1 - abs(2 * k - 1)))

        pygame.draw.lines(surf, OUTLINE, False, [bed(0), bed(0.5), bed(1)], 12)
        stripes = 6
        for i in range(stripes):
            color = self.world.accent if i % 2 == 0 else WHITE
            pygame.draw.line(surf, color, bed(i / stripes), bed((i + 1) / stripes), 7)
        if (self.t % 1.0) < 0.6 and squash == 0:
            ax, ay = r.centerx, r.top - 18 + math.sin(self.t * 6) * 3
            pygame.draw.polygon(surf, WHITE, [(ax - 8, ay + 4), (ax, ay - 6), (ax + 8, ay + 4)])

    def _draw_hud(self, surf):
        box = pygame.Rect(16, 14, 190, 56)
        panel(surf, box, 210)
        self.world.draw_item(surf, box.left + 32, box.centery, 32, self.t)
        draw_text(surf, f"{self.collected} / {self.total}", self.app.font_mid, (box.left + 120, box.centery + 2),
                  OUTLINE, outline=None)
        # Progress bar toward the finish flag
        x0, x1, y = WIDTH // 2 - 160, WIDTH // 2 + 160, 40
        pygame.draw.line(surf, OUTLINE, (x0, y), (x1, y), 10)
        pygame.draw.line(surf, WHITE, (x0, y), (x1, y), 6)
        goal = self.level.finish_base[0] if self.level.finish else self.level.pixel_w
        k = max(0.0, min(1.0, (self.player.rect.centerx - self.level.start[0]) / max(1, goal - self.level.start[0])))
        draw_flag_pole(surf, (x1 + 4, y + 12), 34, None, self.t, big=True)
        pygame.draw.circle(surf, OUTLINE, (x0 + (x1 - x0) * k, y), 12)
        pygame.draw.circle(surf, (255, 145, 60), (x0 + (x1 - x0) * k, y), 9)
        draw_text(surf, self.world.name, self.app.font_small, (WIDTH - 130, 40))


# ---------------------------------------------------------------- results
class LevelCompleteScene(Scene):
    music = "victory"

    def __init__(self, app, index, collected, total):
        super().__init__(app)
        self.index, self.collected, self.total = index, collected, total
        self.world = WORLDS[LEVELS[index].world]
        self.particles = Particles()
        self.shown = 0
        self.last_pop = 0.0

    def update(self, dt):
        super().update(dt)
        self.particles.update(dt)
        if self.shown < self.total and self.t - self.last_pop > 0.08 and self.t > 0.5:
            self.shown += 1
            self.last_pop = self.t
            if self.shown <= self.collected:
                self.app.sound.play("collect")
        if int((self.t - dt) * 2) != int(self.t * 2):
            self.particles.confetti(WIDTH * (0.2 + 0.6 * ((self.t * 7) % 1)), HEIGHT, 25)
        c = self.app.controls
        if (c.confirm or c.jump_pressed) and self.t > 0.6:
            if self.index + 1 < len(LEVELS):
                self.app.switch(PlayScene(self.app, self.index + 1))
            else:
                self.app.switch(EndScene(self.app))
        elif c.back:
            self.app.switch(LevelSelectScene(self.app, min(self.index + 1, len(LEVELS) - 1)))

    def draw(self, surf):
        self.world.draw_background(surf, self.t * 30, self.t)
        box = pygame.Rect(0, 0, 720, 380)
        box.center = (WIDTH // 2, HEIGHT // 2 + 10)
        panel(surf, box, 220)
        msg = "Amazing!" if self.collected == self.total else "Great job!"
        draw_text(surf, msg, self.app.font_big, (WIDTH / 2, box.top + 60 + math.sin(self.t * 3) * 4), GOLD, width=4)
        draw_text(surf, f"You found {self.collected} of {self.total} {self.world.item_name}!", self.app.font_mid,
                  (WIDTH / 2, box.top + 130), OUTLINE, outline=None)
        per_row = 12
        size = 42
        for i in range(self.shown):
            row, col = divmod(i, per_row)
            n_in_row = min(per_row, self.total - row * per_row)
            x = WIDTH / 2 + (col - (n_in_row - 1) / 2) * (size + 6)
            y = box.top + 200 + row * (size + 8)
            if i < self.collected:
                self.world.draw_item(surf, x, y, size, self.t + i)
            else:
                pygame.draw.circle(surf, (200, 200, 210), (x, y), size * 0.35, 3)
        nxt = "SPACE: next world!" if self.index + 1 < len(LEVELS) else "SPACE: celebrate!"
        if (self.t % 1.2) < 0.85:
            draw_text(surf, nxt, self.app.font_mid, (WIDTH / 2, box.bottom - 40))
        self.particles.draw(surf)


class EndScene(Scene):
    music = "victory"

    def __init__(self, app):
        super().__init__(app)
        self.particles = Particles()
        save = app.save
        self.found = sum(save.best.values())
        self.total = sum(ch == "*" for ldef in LEVELS for row in ldef.rows for ch in row)

    def update(self, dt):
        super().update(dt)
        self.particles.update(dt)
        if int((self.t - dt) * 3) != int(self.t * 3):
            self.particles.confetti(WIDTH * ((self.t * 3.7) % 1), HEIGHT, 30)
        c = self.app.controls
        if (c.confirm or c.jump_pressed or c.back) and self.t > 1.0:
            self.app.switch(TitleScene(self.app))

    def draw(self, surf):
        WORLDS["chocolate"].draw_background(surf, self.t * 40, self.t)
        draw_text(surf, "You did it!", self.app.font_big, (WIDTH / 2, 100 + math.sin(self.t * 3) * 6), GOLD, width=4)
        draw_text(surf, "All 5 worlds complete!", self.app.font_mid, (WIDTH / 2, 170))
        for i, ldef in enumerate(LEVELS):
            a = self.t * 1.2 + i * math.tau / len(LEVELS)
            WORLDS[ldef.world].draw_item(surf, WIDTH / 2 + math.cos(a) * 170, 320 + math.sin(a) * 60, 50, self.t)
        hop = abs(math.sin(self.t * 5)) * 30
        draw_diana(surf, WIDTH / 2 + 20, 380 - hop, 1, 0, 0, hop < 2, self.t, scale=2.2)
        draw_puppy(surf, WIDTH / 2 - 80, 380 - abs(math.sin(self.t * 5 - 0.6)) * 20, 1, self.t, True, scale=2.2,
                   dog=self.app.dog)
        draw_text(surf, f"You found {self.found} of {self.total} treasures!", self.app.font_mid, (WIDTH / 2, 440))
        if self.t > 1.0 and (self.t % 1.2) < 0.85:
            draw_text(surf, "Press SPACE", self.app.font_small, (WIDTH / 2, 500))
        self.particles.draw(surf)

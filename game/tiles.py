"""Turns an ASCII level map into collision data and objects."""
import pygame

from .settings import TILE

ITEM_SIZE = 40       # generous pickup box
PLATFORM_THICK = 16


class Item:
    def __init__(self, col, row):
        self.rect = pygame.Rect(0, 0, ITEM_SIZE, ITEM_SIZE)
        self.rect.center = (col * TILE + TILE // 2, row * TILE + TILE // 2)
        self.phase = (col * 0.7 + row * 1.3) % 6.28
        self.taken = False


class Spring:
    def __init__(self, col, row):
        self.rect = pygame.Rect(col * TILE + 4, row * TILE + 28, TILE - 8, 20)
        self.squash = 0.0


class PitPad:
    """A bouncy trampoline at the bottom of a pit: falling in bounces you back out."""
    THICK = 22

    def __init__(self, col0, col1, level_h):
        self.rect = pygame.Rect(col0 * TILE + 2, level_h - self.THICK, (col1 - col0 + 1) * TILE - 4, self.THICK)
        self.squash = 0.0


class Checkpoint:
    def __init__(self, col, row):
        x = col * TILE + TILE // 2
        self.base = (x, (row + 1) * TILE)
        self.rect = pygame.Rect(x - TILE // 2, row * TILE - TILE, TILE, TILE * 2)
        self.active = False


class Level:
    def __init__(self, rows):
        self.rows = rows
        self.cols = max(len(r) for r in rows)
        self.pixel_w = self.cols * TILE
        self.pixel_h = len(rows) * TILE
        self.solids = {}       # (col,row) -> Rect
        self.platforms = {}    # (col,row) -> Rect (one-way, top surface only)
        self.items = []
        self.springs = []
        self.pit_pads = []
        self.checkpoints = []
        self.start = (TILE, TILE)
        self.finish = None     # Rect
        self.finish_base = (0, 0)
        for r, line in enumerate(rows):
            for c, ch in enumerate(line):
                x, y = c * TILE, r * TILE
                if ch == "#":
                    self.solids[(c, r)] = pygame.Rect(x, y, TILE, TILE)
                elif ch == "=":
                    self.platforms[(c, r)] = pygame.Rect(x, y, TILE, PLATFORM_THICK)
                elif ch == "*":
                    self.items.append(Item(c, r))
                elif ch == "^":
                    self.springs.append(Spring(c, r))
                elif ch == "C":
                    self.checkpoints.append(Checkpoint(c, r))
                elif ch == "P":
                    self.start = (x + TILE // 2, y + TILE)   # bottom-center of tile
                elif ch == "F":
                    self.finish = pygame.Rect(x - TILE // 2, y - TILE * 3, TILE * 2, TILE * 4)
                    self.finish_base = (x + TILE // 2, y + TILE)
        self._add_pit_pads()

    def _add_pit_pads(self):
        """Put a trampoline under every run of columns with no ground at the bottom."""
        bottom = len(self.rows) - 1
        col = 0
        while col < self.cols:
            if (col, bottom) in self.solids:
                col += 1
                continue
            start = col
            while col < self.cols and (col, bottom) not in self.solids:
                col += 1
            self.pit_pads.append(PitPad(start, col - 1, self.pixel_h))

    def _near(self, grid, rect):
        c0, c1 = rect.left // TILE - 1, rect.right // TILE + 1
        r0, r1 = rect.top // TILE - 1, rect.bottom // TILE + 1
        for c in range(c0, c1 + 1):
            for r in range(r0, r1 + 1):
                t = grid.get((c, r))
                if t is not None:
                    yield t

    def solids_near(self, rect):
        return self._near(self.solids, rect)

    def platforms_near(self, rect):
        return self._near(self.platforms, rect)

    def is_solid(self, c, r):
        return (c, r) in self.solids

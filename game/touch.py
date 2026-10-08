"""On-screen touch buttons for playing on a phone or tablet.

Big see-through buttons: left / right in the bottom-left corner, jump in the
bottom-right, and a small pause button at the top-right. The areas you can touch
are larger than the drawn buttons so little fingers don't have to be precise.
"""
import math

import pygame

from .draw import circle
from .settings import HEIGHT, OUTLINE, WHITE, WIDTH

BUTTON_R = 58
JUMP_R = 70
PAUSE_R = 26

LEFT_CENTER = (88, HEIGHT - 82)
RIGHT_CENTER = (232, HEIGHT - 82)
JUMP_CENTER = (WIDTH - 100, HEIGHT - 92)
PAUSE_CENTER = (WIDTH - 40, 96)

# Touch zones (bigger than the drawings)
LEFT_ZONE = pygame.Rect(0, HEIGHT - 220, 160, 220)
RIGHT_ZONE = pygame.Rect(160, HEIGHT - 220, 160, 220)
JUMP_ZONE = pygame.Rect(WIDTH - 280, HEIGHT - 260, 280, 260)
PAUSE_ZONE = pygame.Rect(0, 0, 76, 76)
PAUSE_ZONE.center = PAUSE_CENTER


class TouchPad:
    def __init__(self):
        self.left = self.right = self.jump = False

    def apply(self, controls):
        """Turn held/pressed pointers into move_x, jump_pressed and back for this frame."""
        held = list(getattr(controls, "pointers", {}).values())
        downs = getattr(controls, "pointer_downs", [])
        self.left = any(LEFT_ZONE.collidepoint(p) for p in held)
        self.right = any(RIGHT_ZONE.collidepoint(p) for p in held)
        self.jump = any(JUMP_ZONE.collidepoint(p) for p in held)
        if not getattr(controls, "touch_mode", False):
            return
        if self.left != self.right:
            controls.move_x = -1 if self.left else 1
        if any(JUMP_ZONE.collidepoint(p) for p in downs):
            controls.jump_pressed = True
        if any(PAUSE_ZONE.collidepoint(p) for p in downs):
            controls.back = True

    def draw(self, surf, t):
        layer = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self._button(layer, LEFT_CENTER, BUTTON_R, self.left, "left")
        self._button(layer, RIGHT_CENTER, BUTTON_R, self.right, "right")
        self._button(layer, JUMP_CENTER, JUMP_R, self.jump, "jump", t)
        self._button(layer, PAUSE_CENTER, PAUSE_R, False, "pause")
        surf.blit(layer, (0, 0))

    @staticmethod
    def _button(surf, center, r, pressed, icon, t=0.0):
        cx, cy = center
        fill = (255, 235, 140, 190) if pressed else (255, 255, 255, 80)
        circle(surf, (45, 35, 60, 120), center, r + 3)
        circle(surf, fill, center, r)
        ink = (*OUTLINE, 200)
        if icon in ("left", "right"):
            d = -1 if icon == "left" else 1
            s = r * 0.42
            pts = [(cx + d * s, cy), (cx - d * s * 0.6, cy - s), (cx - d * s * 0.6, cy + s)]
            pygame.draw.polygon(surf, (*WHITE, 230), pts)
            pygame.draw.polygon(surf, ink, pts, 4)
        elif icon == "jump":
            lift = 0 if pressed else math.sin(t * 4) * 3
            s = r * 0.42
            pts = [(cx, cy - s - lift), (cx + s, cy + s * 0.5 - lift), (cx - s, cy + s * 0.5 - lift)]
            pygame.draw.polygon(surf, (255, 205, 60, 235), pts)
            pygame.draw.polygon(surf, ink, pts, 4)
        elif icon == "pause":
            for dx in (-7, 4):
                bar = pygame.Rect(cx + dx, cy - 10, 6, 20)
                pygame.draw.rect(surf, ink, bar.inflate(4, 4), border_radius=3)
                pygame.draw.rect(surf, (*WHITE, 230), bar, border_radius=2)

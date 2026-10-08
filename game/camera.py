import math

from .settings import WIDTH, HEIGHT


class Camera:
    """Smoothly follows the player with a little look-ahead, clamped to the level."""

    LOOK_AHEAD = 90

    def __init__(self, level_w, level_h):
        self.level_w, self.level_h = level_w, level_h
        self.x = self.y = 0.0

    def _target(self, rect, facing):
        tx = rect.centerx - WIDTH / 2 + facing * self.LOOK_AHEAD
        ty = rect.centery - HEIGHT * 0.55
        return self._clamp(tx, ty)

    def _clamp(self, x, y):
        x = max(0, min(self.level_w - WIDTH, x))
        y = max(0, min(self.level_h - HEIGHT, y))
        return x, y

    def snap(self, rect, facing=1):
        self.x, self.y = self._target(rect, facing)

    def update(self, rect, facing, dt):
        tx, ty = self._target(rect, facing)
        k = 1 - math.exp(-dt * 5)
        self.x += (tx - self.x) * k
        self.y += (ty - self.y) * k

    @property
    def offset(self):
        return int(self.x), int(self.y)

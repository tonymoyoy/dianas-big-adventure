"""Physics + full-playthrough tests (headless)."""
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from game.player import Player  # noqa: E402
from game.settings import TILE  # noqa: E402
from game.tiles import Level  # noqa: E402
from game.worlds import WORLDS  # noqa: E402

DT = 1 / 60
FLAT = ["." * 20] * 9 + ["P" + "." * 19] + ["#" * 20] * 2


class Pad:
    def __init__(self, move_x=0, jump=False):
        self.move_x, self.jump_pressed = move_x, jump


def step(player, level, n=1, **kw):
    for _ in range(n):
        player.update(DT, Pad(**kw), level, WORLDS["meadow"])


def test_player_rests_on_ground():
    level = Level(FLAT)
    p = Player(level.start)
    step(p, level, 60)
    assert p.on_ground
    assert p.rect.bottom == 10 * TILE


def test_jump_rises_at_least_three_tiles():
    level = Level(FLAT)
    p = Player(level.start)
    step(p, level, 5)
    start_y = p.y
    step(p, level, 1, jump=True)
    top = start_y
    for _ in range(90):
        step(p, level)
        top = min(top, p.y)
    assert start_y - top > 3 * TILE
    assert p.on_ground


def test_coyote_time_allows_late_jump():
    rows = ["." * 20] * 9 + ["P" + "." * 19] + ["####" + "." * 16] * 2
    level = Level(rows)
    p = Player(level.start)
    step(p, level, 5)
    while p.on_ground:
        step(p, level, move_x=1)
    events = p.update(DT, Pad(move_x=1, jump=True), level, WORLDS["meadow"])
    assert "jump" in events


def test_one_way_platform_jump_through():
    rows = ["." * 20] * 7 + ["." * 20] + ["=" * 20] + ["P" + "." * 19] + ["#" * 20] * 2
    level = Level(rows)
    p = Player(level.start)
    step(p, level, 5)
    step(p, level, 1, jump=True)
    step(p, level, 90)
    assert p.on_ground and p.rect.bottom == 8 * TILE


def test_spring_bounces():
    rows = ["." * 20] * 9 + ["P.^" + "." * 17] + ["#" * 20] * 2
    level = Level(rows)
    p = Player(level.start)
    seen = set()
    for _ in range(60):
        seen |= p.update(DT, Pad(move_x=1), level, WORLDS["meadow"])
    assert "bounce" in seen


def test_autopilot_finishes_every_level():
    from game.app import smoke_test
    for i, finished, got, total, secs in smoke_test():
        assert finished, f"level {i + 1} not finished"


def test_pit_trampoline_bounces_back_out():
    rows = ["." * 20] * 9 + ["P" + "." * 19] + ["####...#############"] * 2
    level = Level(rows)
    assert len(level.pit_pads) == 1
    p = Player(level.start)
    p.reset((5 * TILE + TILE // 2, 10 * TILE))   # drop straight into the pit
    seen, top = set(), p.y
    for _ in range(120):
        seen |= p.update(DT, Pad(), level, WORLDS["meadow"])
        assert p.rect.top < level.pixel_h, "fell out of the level"
        if "bounce" in seen:
            top = min(top, p.y)
    assert "bounce" in seen
    assert top + p.h < 10 * TILE - TILE, "bounce should clear the ground level"

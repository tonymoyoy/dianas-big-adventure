"""Static checks that keep every level well-formed and easy."""
import os

import pytest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from game.levels import LEVELS  # noqa: E402
from game.settings import PLAYER_H, RUN_SPEED, TILE  # noqa: E402
from game.worlds import WORLDS  # noqa: E402

GROUND_ROW = 10
SPRING_HELP_RANGE = 6   # a spring this many columns before an obstacle makes it OK


def jump_height(world):
    return world.jump_speed ** 2 / (2 * world.gravity)


def jump_reach_tiles(world):
    return 2 * world.jump_speed / world.gravity * RUN_SPEED / TILE


def cells(ldef, ch):
    return [(c, r) for r, row in enumerate(ldef.rows) for c, x in enumerate(row) if x == ch]


def spring_before(ldef, col):
    return any(col - SPRING_HELP_RANGE <= c <= col for c, _ in cells(ldef, "^"))


@pytest.mark.parametrize("ldef", LEVELS, ids=[l.world for l in LEVELS])
class TestLevel:
    def test_shape(self, ldef):
        assert len(ldef.rows) == 12
        assert len({len(r) for r in ldef.rows}) == 1, "all rows should be the same width"
        assert set("".join(ldef.rows)) <= set(".#=*^CPF")
        assert ldef.world in WORLDS

    def test_one_start_and_finish(self, ldef):
        assert len(cells(ldef, "P")) == 1
        assert len(cells(ldef, "F")) == 1
        (pc, _), (fc, _) = cells(ldef, "P")[0], cells(ldef, "F")[0]
        assert pc < fc

    def test_has_items_and_checkpoint(self, ldef):
        assert len(cells(ldef, "*")) >= 10
        assert cells(ldef, "C")

    def test_gaps_are_jumpable(self, ldef):
        world = WORLDS[ldef.world]
        limit = jump_reach_tiles(world) * 0.65
        ground = ldef.rows[GROUND_ROW]
        col = 0
        while col < len(ground):
            if ground[col] == "#":
                col += 1
                continue
            start = col
            while col < len(ground) and ground[col] != "#":
                col += 1
            width = col - start
            platform_help = any(ldef.rows[r][c] in "=#" for r in range(4, 10) for c in range(start, col))
            assert width <= limit or platform_help or spring_before(ldef, start), \
                f"gap at column {start} is {width} tiles wide (max {limit:.1f})"

    def test_walls_are_climbable(self, ldef):
        world = WORLDS[ldef.world]
        max_tiles = int(jump_height(world) // TILE)
        width = len(ldef.rows[0])
        heights = []
        for c in range(width):
            h = 0
            for r in range(GROUND_ROW - 1, -1, -1):
                if ldef.rows[r][c] != "#":
                    break
                h += 1
            heights.append(h)
        for c in range(1, width):
            step = heights[c] - heights[c - 1]
            if step > max_tiles:
                assert spring_before(ldef, c), f"wall at column {c} is {step} tiles tall (max {max_tiles})"

    def test_items_reachable(self, ldef):
        world = WORLDS[ldef.world]
        reach_rows = int((jump_height(world) + PLAYER_H) // TILE) + 1
        standable = set()
        for r, row in enumerate(ldef.rows[:-1]):
            for c, ch in enumerate(row):
                below = ldef.rows[r + 1][c]
                if ch != "#" and below in "#=":
                    standable.add((c, r))
        for c, r in cells(ldef, "*"):
            near_stand = any((c2, r2) in standable for c2 in range(c - 4, c + 5)
                             for r2 in range(r, r + reach_rows + 1))
            assert near_stand or spring_before(ldef, c), f"item at ({c},{r}) looks unreachable"

"""Diana's ten outfits, and remembering the choice."""
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame  # noqa: E402
import pytest  # noqa: E402

from game.characters import DEFAULT_OUTFIT, OUTFITS, SKIRTS, draw_diana  # noqa: E402
from game.save import SaveData  # noqa: E402


def test_ten_distinct_outfits():
    assert len(OUTFITS) == 10
    assert DEFAULT_OUTFIT in OUTFITS
    assert len({o.name for o in OUTFITS.values()}) == 10
    assert len({(o.dress, o.shape, o.pattern) for o in OUTFITS.values()}) == 10
    assert all(o.shape in SKIRTS for o in OUTFITS.values())


@pytest.mark.parametrize("key", list(OUTFITS))
def test_outfit_draws(key):
    surf = pygame.Surface((200, 200))
    for facing, scale in ((1, 1.0), (-1, 2.5)):
        surf.fill((0, 0, 0))
        draw_diana(surf, 100, 190, facing, 0.2, 1.0, True, 0.7, scale=scale, outfit=key)
        assert surf.get_bounding_rect().h > 40 * scale


def test_outfit_choice_is_saved(tmp_path):
    path = tmp_path / "save.json"
    save = SaveData(10, path=path)
    assert save.outfit is None
    save.outfit = "mermaid"
    save.save()
    assert SaveData(10, path=path).outfit == "mermaid"

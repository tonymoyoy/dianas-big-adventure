"""The two dogs Diana can bring along, and remembering the choice."""
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame  # noqa: E402

from game.characters import DEFAULT_DOG, DOGS, draw_puppy  # noqa: E402
from game.save import SaveData  # noqa: E402


def test_both_border_collies_exist():
    assert DOGS["azulita"].name == "Azulita"
    assert DOGS["vainilla"].name == "Vainilla"
    assert DEFAULT_DOG in DOGS


def test_every_dog_draws():
    surf = pygame.Surface((200, 120))
    for key in DOGS:
        surf.fill((0, 0, 0))
        draw_puppy(surf, 100, 100, 1, 0.5, True, scale=2.0, dog=key)
        assert surf.get_bounding_rect().w > 0


def test_dog_choice_is_saved(tmp_path):
    path = tmp_path / "save.json"
    save = SaveData(5, path=path)
    assert save.dog is None
    save.dog = "vainilla"
    save.save()
    assert SaveData(5, path=path).dog == "vainilla"

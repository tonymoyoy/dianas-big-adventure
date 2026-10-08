"""The smooth-circle helper must keep shapes the size the art was designed with."""
import pygame
import pytest

from game.draw import AA_MIN_RADIUS, circle


def coverage(draw, radius):
    surf = pygame.Surface((120, 120))
    draw(surf, (255, 255, 255), (60.3, 60.6), radius)
    return pygame.surfarray.array3d(surf)[:, :, 0].sum() / 255


def test_running_on_pygame_ce():
    assert getattr(pygame, "IS_CE", False), "requirements.txt expects pygame-ce (pip install pygame-ce)"


@pytest.mark.parametrize("radius", [AA_MIN_RADIUS, 11, 13.6, 22, 40])
def test_smooth_circles_keep_their_size(radius):
    ratio = coverage(circle, radius) / coverage(pygame.draw.circle, radius)
    assert 0.9 < ratio < 1.05


def test_small_dots_stay_crisp():
    assert coverage(circle, 3.4) == coverage(pygame.draw.circle, 3.4)

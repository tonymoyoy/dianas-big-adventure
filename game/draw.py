"""Small drawing helpers shared by the art modules."""
import pygame

# Below this radius a smooth edge only blurs a small dot, so those stay crisp.
AA_MIN_RADIUS = 8


def circle(surf, color, center, radius, width=0):
    """Circle with a smooth, anti-aliased edge (needs pygame-ce) when it is big enough.

    aacircle rounds the radius down and adds about half a pixel of soft fringe, so it
    is drawn one pixel smaller to match the size of pygame.draw.circle, which the art
    was designed with.
    """
    if radius < AA_MIN_RADIUS:
        return pygame.draw.circle(surf, color, center, radius, width)
    return pygame.draw.aacircle(surf, color, center, int(radius) - 1, width)

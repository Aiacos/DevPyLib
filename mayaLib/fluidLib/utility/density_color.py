"""Predefined color values for fluid effects.

Provides RGB color presets for various smoke and fire effects including
wispy smoke, regular smoke, fire colors, and ember colors.
"""

__author__ = "Lorenzo Argentieri"

# Color definitions for smoke and fire


def wispy_smoke_color():
    """Wispy Smoke Color in RGB.

    Returns:
        tuple: RGB values as floats between 0 and 1.
    """
    r = 0.0895799
    g = 0.100438
    b = 0.114084
    return r, g, b


def smoke_color():
    """Smoke Color in RGB.

    Returns:
        tuple: RGB values as floats between 0 and 1.
    """
    r = 0.122141
    g = 0.122141
    b = 0.122141
    return r, g, b


def explosion_smoke_color():
    """Explosion Smoke Color in RGB.

    Returns:
        tuple: RGB values as floats between 0 and 1.
    """
    r = 0.07
    g = 0.07
    b = 0.07
    return r, g, b

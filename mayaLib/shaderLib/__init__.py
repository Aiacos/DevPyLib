"""Shader and material creation utilities for Maya renderers.

Provides tools for creating and managing shaders across multiple render
engines including Arnold, RenderMan, and 3Delight.
"""

import importlib

# Define submodules to lazily load
_submodules = {
    "add_gamma_correct": ".add_gamma_correct",
    "base": ".base",
    "utils": ".utils",
}


def __getattr__(name):
    """Lazy load submodules on first access."""
    if name in _submodules:
        module = importlib.import_module(_submodules[name], package=__name__)
        globals()[name] = module
        return module
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__():
    """Return list of available attributes."""
    return list(_submodules.keys())

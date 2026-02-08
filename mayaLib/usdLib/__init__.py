"""USD (Universal Scene Description) utilities.

Provides tools for working with USD stages, layers, and
Maya USD integration.
"""

import importlib

# Define submodules to lazily load
_submodules = {
    "usd": ".usd",
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

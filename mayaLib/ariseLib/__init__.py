"""Arise Rig integration utilities.

Provides utilities for working with the Arise rigging system including
base classes and helper functions.
"""

import importlib

# Define submodules to lazily load
_submodules = {
    "base": ".base",
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

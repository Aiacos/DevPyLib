"""Modeling utilities for Maya.

Provides tools for UV operations, mesh cleanup, quad patching,
and modeling workflow helpers.
"""

import importlib
from typing import Any

__all__ = ["base", "tools", "utils"]

_loaded_modules = {}


def __getattr__(name: str) -> Any:
    """Lazy load submodules on first access.

    Args:
        name: Name of the submodule to load.

    Returns:
        The loaded submodule.

    Raises:
        AttributeError: If the submodule doesn't exist.
    """
    if name in __all__:
        if name not in _loaded_modules:
            _loaded_modules[name] = importlib.import_module(f".{name}", __name__)
        return _loaded_modules[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__():
    """Return list of available attributes for dir() and tab completion.

    Returns:
        List of attribute names.
    """
    return __all__

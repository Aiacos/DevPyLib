"""Facial rigging framework for Maya.

Provides a comprehensive facial rigging system including Qt widgets,
file I/O operations, facial rig operations, and skin/deformation utilities.
This module was extracted from the monolithic facial3.py for better
maintainability and single responsibility adherence.
"""

from typing import Any

__all__ = [
    "constants",
    "io",
    "operations",
    "skin",
    "utils",
    "widgets",
]


def __getattr__(name: str) -> Any:
    """Lazy load facial rig modules.

    Args:
        name: Module name to load.

    Returns:
        The requested module.

    Raises:
        AttributeError: If module not found.
    """
    if name in __all__:
        from importlib import import_module

        module = import_module(f".{name}", __name__)
        globals()[name] = module
        return module

    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

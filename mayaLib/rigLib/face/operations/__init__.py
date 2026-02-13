"""Facial rigging operation algorithms.

Provides facial rig operation functions including edge detection,
curve projection, and geometry selection handlers.
"""

from typing import Any

__all__ = [
    "curve_operations",
    "edge_detection",
    "geometry_selection",
]


def __getattr__(name: str) -> Any:
    """Lazy load facial operation modules.

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

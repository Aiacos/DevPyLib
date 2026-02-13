"""File I/O operations for facial rigging data.

Provides import/export functionality for facial rig settings,
skin cluster weights, and control shapes.
"""

from typing import Any

__all__ = [
    "ctrl_shapes_io",
    "settings_io",
    "skin_io",
]


def __getattr__(name: str) -> Any:
    """Lazy load facial I/O modules.

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

"""Core rig system for assembling complete character rigs.

Provides the main Rig class for building and managing complete character
rigs by assembling base modules and utilities into a cohesive system.
"""

from typing import Any

__all__ = ["rig"]


def __getattr__(name: str) -> Any:
    """Lazy load core rig modules.

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

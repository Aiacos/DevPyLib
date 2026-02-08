"""AdonisFX integration tools for muscle and soft tissue simulation.

Provides utilities for working with AdonisFX dynamics and muscle systems.
"""

from typing import Any

__all__ = []


def __getattr__(name: str) -> Any:
    """Lazy load AdonisFX modules.

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

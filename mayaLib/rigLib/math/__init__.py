"""Matrix-based rigging utilities for Maya.

Provides collision and constraint systems using matrix operations
for efficient rigging workflows.
"""

from typing import Any

__all__ = ["collision", "vector", "matrix", "rbf"]


def __getattr__(name: str) -> Any:
    """Lazy load matrix rigging modules.

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

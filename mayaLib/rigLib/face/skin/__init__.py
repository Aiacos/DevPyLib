"""Skin and deformation utilities for facial rigging.

Provides skin cluster operations including copy/transfer,
cluster utilities, and joint connection functions.
"""

from typing import Any

__all__ = [
    "cluster_utils",
    "copy",
    "joint_connection",
]


def __getattr__(name: str) -> Any:
    """Lazy load facial skin modules.

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

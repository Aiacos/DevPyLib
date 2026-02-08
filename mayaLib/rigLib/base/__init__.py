"""Base rig module classes for character rigging.

Provides foundational rig module classes including the base module hierarchy,
IK chains, spine, neck, face, and limb systems that form the core of character rigs.
"""

from typing import Any

__all__ = ["face", "ik_chain", "limb", "module", "neck", "spine"]


def __getattr__(name: str) -> Any:
    """Lazy load base rig modules.

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

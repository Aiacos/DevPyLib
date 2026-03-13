"""Houdini utilities - Professional DCC tools for Houdini.

Provides utilities for Houdini rigging, simulation, and pipeline integration.

This module uses lazy loading to defer imports of submodules until first access,
optimising Houdini startup performance.
"""

from importlib import import_module

# Submodules available for lazy loading
_SUBMODULES = {
    "utility",
}

__all__ = sorted(_SUBMODULES)


def __getattr__(name):
    """Lazy load submodules on first access.

    Args:
        name: Name of the attribute being accessed.

    Returns:
        The imported submodule.

    Raises:
        AttributeError: If the attribute is not a known submodule.
        ImportError: If the submodule cannot be imported.
    """
    if name in _SUBMODULES:
        try:
            module = import_module(f".{name}", __name__)
            globals()[name] = module
            return module
        except ImportError as e:
            raise ImportError(f"Failed to import {__name__}.{name}: {e}") from e
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__():
    """Return list of available attributes for introspection."""
    return sorted(list(globals().keys()) + list(_SUBMODULES))

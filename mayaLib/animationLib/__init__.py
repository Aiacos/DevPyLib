"""Animation utilities and importers.

Provides tools for animation workflows including BVH import
and animation data management.
"""

import sys

# Lazy loading state
_submodules_loaded = {}


def __getattr__(name):
    """Module-level __getattr__ for lazy loading of submodules.

    Args:
        name: The attribute name being accessed.

    Returns:
        The requested module or attribute.

    Raises:
        AttributeError: If the attribute doesn't exist.
    """
    # List of available submodules
    _available_submodules = ["bvh_importer"]

    if name in _available_submodules:
        # Check if already loaded
        if name not in _submodules_loaded:
            # Lazy import the submodule
            from importlib import import_module
            module = import_module(f".{name}", package=__name__)
            _submodules_loaded[name] = module
            # Add to module's globals so subsequent access is direct
            globals()[name] = module
        return _submodules_loaded[name]

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

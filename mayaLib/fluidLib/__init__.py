"""Maya fluid simulation setup utilities.

Provides classes and utilities for creating and managing Maya fluid effects
including fire, smoke, explosions, and custom fluid configurations with
containers and emitters.
"""

# Lazy loading state
_submodules_loaded = {}

# Available submodules
_SUBMODULES = ["base", "fire", "fire_smoke", "smoke", "explosion", "utility"]


def __getattr__(name):
    """Lazy load submodules on first access.

    Args:
        name: The name of the submodule to load.

    Returns:
        The loaded submodule.

    Raises:
        AttributeError: If the submodule does not exist.
    """
    if name in _SUBMODULES:
        if name not in _submodules_loaded:
            # Import the submodule
            from importlib import import_module

            submodule = import_module(f".{name}", package=__name__)
            _submodules_loaded[name] = submodule
            return submodule
        return _submodules_loaded[name]

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__():
    """Return list of available attributes including lazy-loaded submodules.

    Returns:
        list: Available attributes in this module.
    """
    # Combine standard module attributes with available submodules
    standard_attrs = list(globals().keys())
    return sorted(set(standard_attrs + _SUBMODULES))

"""Bridge module for Luna-mayaLib integration.

This module provides utilities for bidirectional integration between
Luna and mayaLib, allowing Luna components to access mayaLib utilities.
"""

__all__ = ["mayalib_to_luna"]


def __getattr__(name):
    """Lazy load submodules on first access.

    Args:
        name: The attribute name being accessed.

    Returns:
        The requested module or attribute.

    Raises:
        AttributeError: If the attribute is not found.
    """
    if name in __all__:
        import importlib

        module = importlib.import_module(f".{name}", __name__)
        globals()[name] = module
        return module

    # Support direct access to commonly used exports
    if name in ("MayaLibBridge", "register_mayalib_utilities"):
        import importlib

        mayalib_to_luna = importlib.import_module(".mayalib_to_luna", __name__)
        globals()["mayalib_to_luna"] = mayalib_to_luna
        return getattr(mayalib_to_luna, name)

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__():
    """Return the list of available attributes for introspection.

    Returns:
        List of attribute names.
    """
    return __all__ + ["MayaLibBridge", "register_mayalib_utilities"]

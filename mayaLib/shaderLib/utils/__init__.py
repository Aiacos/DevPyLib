"""Shader utility functions.

Provides helper functions for shader configuration, file management,
and render-specific utilities.
"""

__all__ = ["config", "file", "texture_ext_path"]


def __getattr__(name):
    """Lazy load submodules on first access.

    Args:
        name: The attribute name being accessed.

    Returns:
        The requested module.

    Raises:
        AttributeError: If the attribute is not in __all__.
    """
    if name in __all__:
        import importlib

        module = importlib.import_module(f".{name}", __name__)
        globals()[name] = module
        return module
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__():
    """Return the list of available attributes for introspection.

    Returns:
        List of attribute names.
    """
    return __all__

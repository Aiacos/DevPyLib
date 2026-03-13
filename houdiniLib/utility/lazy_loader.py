"""Lazy loading utilities for houdiniLib.

Provides helper functions to implement the lazy loading pattern in houdiniLib
__init__.py files, following the established mayaLib convention.

The pattern defers Houdini module imports until first access, avoiding import
errors in non-Houdini environments and reducing startup overhead.

Example:
    Basic usage in an __init__.py file::

        from houdiniLib.utility.lazy_loader import create_lazy_loader

        _SUBMODULES = ["solvers", "rigs", "utils"]
        __getattr__ = create_lazy_loader(_SUBMODULES, __name__, globals())

    With Houdini availability check::

        from houdiniLib.utility.lazy_loader import create_lazy_loader, is_houdini_available

        if is_houdini_available():
            __getattr__ = create_lazy_loader(["hdaUtils"], __name__, globals())
"""

from importlib import import_module


def is_houdini_available():
    """Check if the Houdini Python API (hou) is available.

    Returns:
        True if running inside Houdini or hython, False otherwise.
    """
    try:
        import_module("hou")
        return True
    except ImportError:
        return False


def create_lazy_loader(submodules, package_name, globals_dict=None):
    """Create a module-level __getattr__ function for lazy loading.

    Returns a callable suitable for assigning to ``__getattr__`` at module
    level. On first attribute access, the corresponding submodule is imported
    and cached in *globals_dict* (or in the module's own globals if not given).

    Args:
        submodules: Iterable of submodule names to lazily load.
        package_name: The ``__name__`` of the package (pass ``__name__``).
        globals_dict: Optional ``globals()`` dict to cache imports in.

    Returns:
        A ``__getattr__`` function that can be assigned at module level.

    Example:
        >>> __getattr__ = create_lazy_loader(["solvers", "rigs"], __name__, globals())
    """
    _submodules = frozenset(submodules)

    def __getattr__(name):
        """Module-level __getattr__ for lazy loading."""
        if name in _submodules:
            try:
                module = import_module(f".{name}", package_name)
                if globals_dict is not None:
                    globals_dict[name] = module
                return module
            except ImportError as e:
                raise ImportError(f"Failed to import {package_name}.{name}: {e}") from e
        raise AttributeError(f"module {package_name!r} has no attribute {name!r}")

    return __getattr__


def make_dir_func(submodules, globals_dict):
    """Create a module-level __dir__ function for introspection.

    Returns a callable that merges currently-loaded globals with the full
    list of available submodule names, so IDE autocomplete works correctly.

    Args:
        submodules: Iterable of submodule names available for lazy loading.
        globals_dict: The ``globals()`` dict of the calling module.

    Returns:
        A ``__dir__`` function that can be assigned at module level.

    Example:
        >>> __dir__ = make_dir_func(["solvers", "rigs"], globals())
    """
    _submodules = list(submodules)

    def __dir__():
        """Return list of available attributes for introspection."""
        return sorted(set(list(globals_dict.keys()) + _submodules))

    return __dir__

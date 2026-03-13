"""Lazy loading utilities for deferred module imports.

This module provides helper functions to implement lazy loading patterns in
__init__.py files, deferring expensive imports until first access.

The lazy loading pattern significantly reduces Maya startup time by avoiding
upfront imports of heavy modules (fluidLib, rigLib, bifrostLib, etc.).

Based on the pattern established in mayaLib/lunaLib/__init__.py.

Example:
    Basic usage in an __init__.py file:

    ```python
    from mayaLib.utility.lazy_loader import create_lazy_loader

    # Define what modules to lazily load
    _SUBMODULES = ['rigLib', 'fluidLib', 'bifrostLib']

    # Create the __getattr__ function
    __getattr__ = create_lazy_loader(
        submodules=_SUBMODULES,
        package_name=__name__
    )
    ```

    Advanced usage with initialization callback:

    ```python
    from mayaLib.utility.lazy_loader import create_lazy_loader

    def _init_callback(name):
        '''Custom initialization for each module.'''
        print(f"Loading {name}...")
        return True

    __getattr__ = create_lazy_loader(
        submodules=['module1', 'module2'],
        package_name=__name__,
        init_callback=_init_callback
    )
    ```
"""

import traceback
from importlib import import_module


def create_lazy_loader(
    submodules,
    package_name,
    init_callback=None,
    error_mode="warn",
    globals_dict=None,
):
    """Create a module-level __getattr__ function for lazy loading.

    This function returns a __getattr__ callable that implements lazy loading
    for the specified submodules. When an attribute is accessed, the submodule
    is imported on-demand.

    Args:
        submodules: List of submodule names to lazily load (e.g., ['rigLib', 'fluidLib']).
        package_name: The __name__ of the package (typically passed as __name__).
        init_callback: Optional callable(module_name) -> bool called before import.
            If it returns False, the import is skipped.
        error_mode: How to handle import errors:
            - "warn": Print warning and return None (default)
            - "raise": Re-raise the exception
            - "silent": Return None silently
        globals_dict: Optional globals() dict to cache imports in.
            If None, imports are cached in sys.modules only.

    Returns:
        A __getattr__ function that can be assigned at module level.

    Example:
        >>> __getattr__ = create_lazy_loader(
        ...     submodules=['rigLib', 'fluidLib'],
        ...     package_name=__name__
        ... )
    """
    # Convert to set for O(1) lookup
    _submodules = set(submodules)

    def __getattr__(name):
        """Module-level __getattr__ for lazy loading."""
        # Check if this is a known submodule
        if name in _submodules:
            # Run initialization callback if provided
            if init_callback is not None:
                try:
                    if not init_callback(name):
                        return None
                except Exception as e:
                    if error_mode == "raise":
                        raise
                    if error_mode == "warn":
                        print(f"Warning: Initialization callback failed for {name}: {e}")
                    return None

            # Import the submodule
            try:
                full_name = f"{package_name}.{name}"
                module = import_module(full_name)

                # Cache in globals if provided
                if globals_dict is not None:
                    globals_dict[name] = module

                return module

            except ImportError as e:
                if error_mode == "raise":
                    raise
                if error_mode == "warn":
                    print(f"Warning: Failed to import {package_name}.{name}: {e}")
                    traceback.print_exc()
                return None
            except Exception as e:
                if error_mode == "raise":
                    raise
                if error_mode == "warn":
                    print(f"Warning: Error during import of {package_name}.{name}: {e}")
                    traceback.print_exc()
                return None

        # Unknown attribute - raise AttributeError as expected
        raise AttributeError(f"module {package_name!r} has no attribute {name!r}")

    return __getattr__


class LazyModuleLoader:
    """A class-based lazy loader for more complex scenarios.

    This provides a more feature-rich alternative to create_lazy_loader(),
    with support for initialization state tracking, availability checks,
    and custom setup functions.

    Example:
        >>> loader = LazyModuleLoader(
        ...     package_name=__name__,
        ...     submodules=['rigLib', 'fluidLib']
        ... )
        >>> __getattr__ = loader.getattr
        >>> is_riglib_available = loader.is_available
    """

    def __init__(
        self,
        package_name,
        submodules,
        setup_func=None,
        error_mode="warn",
        globals_dict=None,
    ):
        """Initialize the lazy loader.

        Args:
            package_name: The __name__ of the package.
            submodules: List of submodule names to lazily load.
            setup_func: Optional callable() -> bool for one-time setup.
                Called before first import. If it returns False, imports fail.
            error_mode: How to handle import errors ("warn", "raise", "silent").
            globals_dict: Optional globals() dict to cache imports in.
        """
        self.package_name = package_name
        self.submodules = set(submodules)
        self.setup_func = setup_func
        self.error_mode = error_mode
        self.globals_dict = globals_dict

        # State tracking
        self._initialized = False
        self._available = False
        self._loaded_modules = set()

    def _ensure_initialized(self):
        """Run one-time initialization if needed.

        Returns:
            bool: True if initialized successfully.
        """
        if self._initialized:
            return self._available

        self._initialized = True

        if self.setup_func is not None:
            try:
                self._available = self.setup_func()
            except Exception as e:
                if self.error_mode == "raise":
                    raise
                if self.error_mode == "warn":
                    print(f"Warning: Setup function failed: {e}")
                    traceback.print_exc()
                self._available = False
        else:
            self._available = True

        return self._available

    def is_available(self, name=None):
        """Check if lazy loading is available.

        Args:
            name: Optional submodule name to check. If None, checks general availability.

        Returns:
            bool: True if the module/submodule is available.
        """
        if not self._ensure_initialized():
            return False

        if name is None:
            return True

        # Check if already loaded
        if name in self._loaded_modules:
            return True

        # Check if it's a known submodule
        return name in self.submodules

    def getattr(self, name):
        """Module-level __getattr__ implementation.

        This method should be assigned to __getattr__ at module level:
        >>> __getattr__ = loader.getattr

        Args:
            name: The attribute name being accessed.

        Returns:
            The imported module, or None on error.

        Raises:
            AttributeError: If the attribute is not a known submodule.
        """
        # Check if this is a known submodule
        if name not in self.submodules:
            raise AttributeError(f"module {self.package_name!r} has no attribute {name!r}")

        # Ensure initialization has run
        if not self._ensure_initialized():
            return None

        # Import the submodule
        try:
            full_name = f"{self.package_name}.{name}"
            module = import_module(full_name)

            # Cache in globals if provided
            if self.globals_dict is not None:
                self.globals_dict[name] = module

            # Track loaded modules
            self._loaded_modules.add(name)

            return module

        except ImportError as e:
            if self.error_mode == "raise":
                raise
            if self.error_mode == "warn":
                print(f"Warning: Failed to import {self.package_name}.{name}: {e}")
                traceback.print_exc()
            return None
        except Exception as e:
            if self.error_mode == "raise":
                raise
            if self.error_mode == "warn":
                print(f"Warning: Error during import of {self.package_name}.{name}: {e}")
                traceback.print_exc()
            return None


def make_availability_checker(init_func):
    """Create an is_available() function that wraps an initialization function.

    This is useful for maintaining backwards compatibility with existing
    code that uses module.is_available() checks.

    Args:
        init_func: A callable() -> bool that performs initialization.

    Returns:
        A function that can be used as is_available() in the module.

    Example:
        >>> def _initialize():
        ...     global _available
        ...     _available = True
        ...     return True
        >>> is_available = make_availability_checker(_initialize)
    """

    def is_available():
        """Check if module is available.

        This will trigger lazy initialization if not already done.

        Returns:
            bool: True if module is available and initialized.
        """
        try:
            return init_func()
        except Exception:
            return False

    return is_available


def get_submodule_names(module_globals, prefix="", exclude=None):
    """Auto-detect submodule names from a package's globals().

    This utility can scan a package's __init__.py globals() to automatically
    detect what submodules exist, useful for generating the submodules list
    for create_lazy_loader().

    Args:
        module_globals: The globals() dict from the __init__.py file.
        prefix: Optional prefix to filter by (e.g., "base_" to match base_*.py).
        exclude: Optional set of names to exclude.

    Returns:
        List of submodule names suitable for lazy loading.

    Example:
        >>> # In __init__.py
        >>> from mayaLib.utility.lazy_loader import get_submodule_names
        >>> _SUBMODULES = get_submodule_names(
        ...     globals(),
        ...     exclude={'__builtins__', '__doc__'}
        ... )
    """
    if exclude is None:
        exclude = set()

    submodules = []

    for name, value in module_globals.items():
        # Skip private attributes
        if name.startswith("_"):
            continue

        # Skip excluded names
        if name in exclude:
            continue

        # Check prefix filter
        if prefix and not name.startswith(prefix):
            continue

        # Check if it's a module
        if hasattr(value, "__file__") or hasattr(value, "__path__"):
            submodules.append(name)

    return sorted(submodules)

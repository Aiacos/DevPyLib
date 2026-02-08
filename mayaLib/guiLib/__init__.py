"""GUI framework for Maya tools.

Provides an introspection-based UI generation system that automatically
creates Qt interfaces from Python function signatures.
"""

import traceback

# Lazy loading state
_guilib_initialized = False
_guilib_available = False
base = None
main_menu = None
utils = None


def _initialize_guilib():
    """Initialize guiLib modules (lazy loading).

    This function is called on first access to guiLib functionality.

    Returns:
        bool: True if guiLib was successfully initialized.
    """
    global _guilib_initialized, _guilib_available, base, main_menu, utils

    if _guilib_initialized:
        return _guilib_available

    _guilib_initialized = True

    try:
        # Import submodules
        from . import base as _base
        from . import main_menu as _main_menu
        from . import utils as _utils

        base = _base
        main_menu = _main_menu
        utils = _utils
        _guilib_available = True

        return True

    except Exception as e:
        print(f"Warning: guiLib initialization error - {e}")
        traceback.print_exc()
        return False


def is_available():
    """Check if guiLib is available.

    This will trigger lazy initialization if not already done.

    Returns:
        bool: True if guiLib is available and initialized.
    """
    return _initialize_guilib()


def __getattr__(name):
    """Lazy load guiLib attributes.

    Args:
        name: The name of the attribute to load.

    Returns:
        The requested attribute.

    Raises:
        AttributeError: If the attribute is not found.
    """
    # Trigger initialization on first attribute access
    if not _initialize_guilib():
        raise ImportError("Failed to initialize guiLib")

    # Return the requested attribute
    module_globals = globals()
    if name in module_globals:
        return module_globals[name]

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

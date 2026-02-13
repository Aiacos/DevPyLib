"""Facial rigging framework for Maya.

Provides a comprehensive facial rigging system including Qt widgets,
file I/O operations, facial rig operations, and skin/deformation utilities.
This module was extracted from the monolithic facial3.py for better
maintainability and single responsibility adherence.
"""

# Lazy loading state
_face_initialized = False
_face_available = False

# Module references (initialized on first access)
arise_face_node = None
constants = None
io = None
operations = None
skin = None
utils = None
widgets = None


def _initialize_face():
    """Initialize face modules (lazy loading).

    This function is called on first access to face functionality.
    It imports all face submodules.

    Returns:
        bool: True if face module was successfully initialized.
    """
    global _face_initialized, _face_available
    global arise_face_node, constants, io, operations, skin, utils, widgets

    if _face_initialized:
        return _face_available

    _face_initialized = True

    try:
        # Import all submodules
        from . import arise_face_node as _arise_face_node
        from . import constants as _constants
        from . import io as _io
        from . import operations as _operations
        from . import skin as _skin
        from . import utils as _utils
        from . import widgets as _widgets

        # Assign to module-level variables
        arise_face_node = _arise_face_node
        constants = _constants
        io = _io
        operations = _operations
        skin = _skin
        utils = _utils
        widgets = _widgets

        _face_available = True
        return True

    except ImportError as e:
        print(f"Warning: face submodule import failed - {e}")
        return False
    except Exception as e:
        print(f"Warning: face initialization error - {e}")
        return False


def is_available():
    """Check if face module is available.

    This will trigger lazy initialization if not already done.

    Returns:
        bool: True if face module is available and initialized.
    """
    return _initialize_face()


def __getattr__(name):
    """Lazy loading of face submodules.

    This function is called when an attribute is accessed that doesn't exist
    in the module's __dict__. It triggers initialization of face module and
    returns the requested attribute.

    Args:
        name: The name of the attribute being accessed.

    Returns:
        The requested attribute from the initialized face module.

    Raises:
        AttributeError: If the attribute doesn't exist after initialization.
    """
    # List of available submodules
    _submodules = [
        "arise_face_node",
        "constants",
        "io",
        "operations",
        "skin",
        "utils",
        "widgets",
    ]

    if name in _submodules:
        if _initialize_face():
            return globals()[name]
        else:
            raise AttributeError(
                f"face submodule '{name}' could not be loaded - initialization failed"
            )

    raise AttributeError(f"module 'mayaLib.rigLib.face' has no attribute '{name}'")


def __dir__():
    """Return list of available attributes for introspection.

    Returns:
        list: Sorted list of available module attributes.
    """
    _submodules = [
        "arise_face_node",
        "constants",
        "io",
        "operations",
        "skin",
        "utils",
        "widgets",
    ]
    return sorted(list(globals().keys()) + _submodules + ["is_available"])

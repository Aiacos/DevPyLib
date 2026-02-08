"""Character rigging framework for Maya.

Provides a comprehensive rigging system including base modules for limbs,
spine, neck, and face, as well as specialized systems for Ziva VFX,
AdonisFX, cloth simulation, and a rich collection of rigging utilities.
"""

# Lazy loading state
_riglib_initialized = False
_riglib_available = False

# Module references (initialized on first access)
Ziva = None
base = None
cloth = None
core = None
facial_rig = None
matrix = None
orient_ctrl = None
set_muscle_weight = None
utils = None


def _initialize_riglib():
    """Initialize rigLib modules (lazy loading).

    This function is called on first access to rigLib functionality.
    It imports all rigLib submodules.

    Returns:
        bool: True if rigLib was successfully initialized.
    """
    global _riglib_initialized, _riglib_available
    global Ziva, base, cloth, core, facial_rig, matrix, orient_ctrl, set_muscle_weight, utils

    if _riglib_initialized:
        return _riglib_available

    _riglib_initialized = True

    try:
        # Import all submodules
        from . import Ziva as _Ziva
        from . import base as _base
        from . import cloth as _cloth
        from . import core as _core
        from . import facial_rig as _facial_rig
        from . import matrix as _matrix
        from . import orient_ctrl as _orient_ctrl
        from . import set_muscle_weight as _set_muscle_weight
        from . import utils as _utils

        # Assign to module-level variables
        Ziva = _Ziva
        base = _base
        cloth = _cloth
        core = _core
        facial_rig = _facial_rig
        matrix = _matrix
        orient_ctrl = _orient_ctrl
        set_muscle_weight = _set_muscle_weight
        utils = _utils

        _riglib_available = True
        return True

    except ImportError as e:
        print(f"Warning: rigLib submodule import failed - {e}")
        return False
    except Exception as e:
        print(f"Warning: rigLib initialization error - {e}")
        return False


def is_available():
    """Check if rigLib is available.

    This will trigger lazy initialization if not already done.

    Returns:
        bool: True if rigLib is available and initialized.
    """
    return _initialize_riglib()


def __getattr__(name):
    """Lazy loading of rigLib submodules.

    This function is called when an attribute is accessed that doesn't exist
    in the module's __dict__. It triggers initialization of rigLib and returns
    the requested attribute.

    Args:
        name: The name of the attribute being accessed.

    Returns:
        The requested attribute from the initialized rigLib.

    Raises:
        AttributeError: If the attribute doesn't exist after initialization.
    """
    # List of available submodules
    _submodules = [
        "Ziva",
        "base",
        "cloth",
        "core",
        "facial_rig",
        "matrix",
        "orient_ctrl",
        "set_muscle_weight",
        "utils",
    ]

    if name in _submodules:
        if _initialize_riglib():
            return globals()[name]
        else:
            raise AttributeError(
                f"rigLib submodule '{name}' could not be loaded - initialization failed"
            )

    raise AttributeError(f"module 'mayaLib.rigLib' has no attribute '{name}'")

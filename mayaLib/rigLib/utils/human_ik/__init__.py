"""HumanIK rigging framework for Maya.

Provides a comprehensive HumanIK integration system including constants,
skeleton mapping, control definitions, MEL interface, and rig templates.
This module was extracted from the monolithic human_ik.py for better
maintainability and single responsibility adherence.
"""

# Lazy loading state
_human_ik_initialized = False
_human_ik_available = False

# Module references (initialized on first access)
constants = None


def _initialize_human_ik():
    """Initialize human_ik modules (lazy loading).

    This function is called on first access to human_ik functionality.
    It imports all human_ik submodules.

    Returns:
        bool: True if human_ik module was successfully initialized.
    """
    global _human_ik_initialized, _human_ik_available
    global constants

    if _human_ik_initialized:
        return _human_ik_available

    _human_ik_initialized = True

    try:
        # Import all submodules
        from . import constants as _constants

        # Assign to module-level variables
        constants = _constants

        _human_ik_available = True
        return True

    except ImportError as e:
        print(f"Warning: human_ik submodule import failed - {e}")
        return False
    except Exception as e:
        print(f"Warning: human_ik initialization error - {e}")
        return False


def is_available():
    """Check if human_ik module is available.

    This will trigger lazy initialization if not already done.

    Returns:
        bool: True if human_ik module is available and initialized.
    """
    return _initialize_human_ik()


def __getattr__(name):
    """Lazy loading of human_ik submodules.

    This function is called when an attribute is accessed that doesn't exist
    in the module's __dict__. It triggers initialization of human_ik module and
    returns the requested attribute.

    Args:
        name: The name of the attribute being accessed.

    Returns:
        The requested attribute from the initialized human_ik module.

    Raises:
        AttributeError: If the attribute doesn't exist after initialization.
    """
    # List of available submodules
    _submodules = [
        "constants",
    ]

    if name in _submodules:
        if _initialize_human_ik():
            return globals()[name]
        else:
            raise AttributeError(
                f"human_ik submodule '{name}' could not be loaded - initialization failed"
            )

    raise AttributeError(
        f"module 'mayaLib.rigLib.utils.human_ik' has no attribute '{name}'"
    )


def __dir__():
    """Return list of available attributes for introspection.

    Returns:
        list: Sorted list of available module attributes.
    """
    _submodules = [
        "constants",
    ]
    return sorted(list(globals().keys()) + _submodules + ["is_available"])

"""Ziva VFX integration tools for tissue and muscle simulation.

Provides utilities for working with Ziva VFX dynamics including fiber
creation, attachment tools, and general Ziva workflow helpers.
Maya 2022+ only.
"""

import traceback

# Lazy loading state
_ziva_initialized = False
_ziva_available = False
ziva_attachments_tools = None
ziva_fiber_tools = None
ziva_tools = None


def _initialize_ziva():
    """Initialize Ziva modules (lazy loading).

    This function is called on first access to Ziva functionality.
    Only imports Ziva modules if Maya version is 2022.

    Returns:
        bool: True if Ziva was successfully initialized.
    """
    global _ziva_initialized, _ziva_available
    global ziva_attachments_tools, ziva_fiber_tools, ziva_tools

    if _ziva_initialized:
        return _ziva_available

    _ziva_initialized = True

    try:
        import pymel.core as pm

        # Check Maya version
        if pm.about(version=True) != "2022":
            print("Warning: Ziva tools only available in Maya 2022")
            return False

        # Import Ziva submodules
        from . import ziva_attachments_tools as _ziva_attachments_tools
        from . import ziva_fiber_tools as _ziva_fiber_tools
        from . import ziva_tools as _ziva_tools

        ziva_attachments_tools = _ziva_attachments_tools
        ziva_fiber_tools = _ziva_fiber_tools
        ziva_tools = _ziva_tools
        _ziva_available = True

        return True

    except ImportError as e:
        print(f"Warning: Ziva modules not available - {e}")
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"Warning: Ziva initialization error - {e}")
        traceback.print_exc()
        return False


def is_available():
    """Check if Ziva is available.

    This will trigger lazy initialization if not already done.

    Returns:
        bool: True if Ziva is available and initialized (Maya 2022 only).
    """
    return _initialize_ziva()


def __getattr__(name):
    """Lazy loading hook for module attributes.

    This is called when an attribute is not found in the module's __dict__.
    It triggers initialization and then looks up the attribute.

    Args:
        name: The name of the attribute being accessed.

    Returns:
        The requested attribute.

    Raises:
        AttributeError: If the attribute doesn't exist after initialization.
    """
    # Trigger initialization
    if not _initialize_ziva():
        raise AttributeError(
            f"Ziva module '{name}' not available (Maya 2022 only or import failed)"
        )

    # Look up the attribute in the global namespace
    if name in globals():
        return globals()[name]

    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


def __dir__():
    """Return list of available attributes in this module.

    Returns:
        list: List of attribute names available in this module.
    """
    # Initialize to get the full list if not already done
    _initialize_ziva()

    # Base attributes always available
    attrs = ["is_available", "_initialize_ziva"]

    # Add Ziva submodules if available
    if _ziva_available:
        attrs.extend(
            ["ziva_attachments_tools", "ziva_fiber_tools", "ziva_tools"]
        )

    return attrs


__all__ = [
    "is_available",
    "ziva_attachments_tools",
    "ziva_fiber_tools",
    "ziva_tools",
]

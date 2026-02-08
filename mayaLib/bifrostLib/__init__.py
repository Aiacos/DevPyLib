"""Bifrost graph and USD integration utilities.

Provides tools for creating Bifrost graphs, USD stages, and
integrating Bifrost with Maya geometry.
"""

import sys
import traceback

# Lazy loading state
_bifrost_initialized = False
_bifrost_available = False
bifrost_api = None
bifrost_util_nodes = None
stage_builder = None


def _initialize_bifrost():
    """Initialize Bifrost modules (lazy loading).

    This function is called on first access to Bifrost functionality.

    Returns:
        bool: True if Bifrost modules were successfully initialized.
    """
    global _bifrost_initialized, _bifrost_available
    global bifrost_api, bifrost_util_nodes, stage_builder

    if _bifrost_initialized:
        return _bifrost_available

    _bifrost_initialized = True

    try:
        # Import the three submodules
        from . import bifrost_api as _bifrost_api
        from . import bifrost_util_nodes as _bifrost_util_nodes
        from . import stage_builder as _stage_builder

        bifrost_api = _bifrost_api
        bifrost_util_nodes = _bifrost_util_nodes
        stage_builder = _stage_builder
        _bifrost_available = True

        return True

    except ImportError as e:
        print(f"Warning: Bifrost modules not available - {e}")
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"Warning: Bifrost initialization error - {e}")
        traceback.print_exc()
        return False


def is_available():
    """Check if Bifrost modules are available.

    This will trigger lazy initialization if not already done.

    Returns:
        bool: True if Bifrost modules are available and initialized.
    """
    return _initialize_bifrost()


def __getattr__(name):
    """Lazy load Bifrost modules on first access.

    Args:
        name: The name of the attribute being accessed.

    Returns:
        The requested module or attribute.

    Raises:
        AttributeError: If the attribute doesn't exist.
    """
    # List of modules we lazily load
    _modules = ["bifrost_api", "bifrost_util_nodes", "stage_builder"]

    if name in _modules:
        if not _initialize_bifrost():
            raise ImportError(f"Could not initialize bifrostLib to access {name}")
        return globals()[name]

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


# Define __all__ for explicit exports
__all__ = ["bifrost_api", "bifrost_util_nodes", "stage_builder", "is_available"]

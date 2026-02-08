"""Maya utilities - Professional DCC tools for Maya.

Comprehensive library for rigging, animation, modeling, shading,
fluids, and pipeline integration in Autodesk Maya.

This module uses lazy loading to defer imports of submodules until first access,
significantly reducing Maya startup time.
"""

from importlib import import_module

# Define submodules to lazily load
_SUBMODULES = {
    "animationLib",
    "bifrostLib",
    "fluidLib",
    "guiLib",
    "lookdevLib",
    "lunaLib",
    "modelLib",
    "pipelineLib",
    "rigLib",
    "shaderLib",
    "utility",
}


def __getattr__(name):
    """Lazy load submodules on first access.

    This function is called when an attribute is accessed that doesn't exist
    in the module's namespace. It imports the submodule on-demand and caches
    it in the module's globals.

    Args:
        name: Name of the attribute being accessed.

    Returns:
        The imported submodule.

    Raises:
        AttributeError: If the attribute is not a known submodule.
    """
    if name in _SUBMODULES:
        # Import the submodule
        try:
            full_name = f"{__name__}.{name}"
            module = import_module(full_name)
            # Cache in globals
            globals()[name] = module
            return module
        except ImportError as e:
            print(f"Warning: Failed to import {__name__}.{name}: {e}")
            return None
        except Exception as e:
            print(f"Warning: Error during import of {__name__}.{name}: {e}")
            return None

    # Unknown attribute - raise AttributeError as expected
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

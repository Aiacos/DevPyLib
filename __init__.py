"""DevPyLib - Development library for DCC applications.

This package provides utilities for Maya, Houdini, Blender, and Prism Pipeline.
Submodules are lazily loaded to minimize startup time.
"""

import sys
import traceback
from importlib import import_module

# Define submodules for lazy loading
_SUBMODULES = ['blenderLib', 'houdiniLib', 'mayaLib', 'prismLib']


def __getattr__(name):
    """Module-level __getattr__ for lazy loading submodules.

    This function defers imports of blenderLib, houdiniLib, mayaLib, and prismLib
    until they are actually accessed, significantly reducing startup time.

    Args:
        name: The attribute name being accessed.

    Returns:
        The requested submodule if it exists.

    Raises:
        AttributeError: If the attribute is not a known submodule.
    """
    # Check if this is a known submodule
    if name in _SUBMODULES:
        # Import the submodule
        try:
            module = import_module(name)

            # Cache in globals for faster subsequent access
            globals()[name] = module

            return module

        except ImportError as e:
            print(f"Warning: Failed to import {name}: {e}")
            traceback.print_exc()
            return None
        except Exception as e:
            print(f"Warning: Error during import of {name}: {e}")
            traceback.print_exc()
            return None

    # Unknown attribute - raise AttributeError as expected
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

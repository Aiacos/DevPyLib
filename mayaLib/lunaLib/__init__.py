"""Luna rigging framework integration for mayaLib.

This module provides a bridge between the Luna rigging framework and mayaLib,
exposing Luna components, functions and tools through the mayaLib menu system.

Luna expects to be installed as a Maya module (with a .mod file), but we're
integrating it as a submodule by adding it to sys.path. This requires patching
both the pymel.core.moduleInfo function and Luna's directories module BEFORE
any Luna imports occur.
"""

import os
import sys
from pathlib import Path
from types import ModuleType

# Determine Luna root path
_luna_path = Path(__file__).parent.parent.parent / "luna"
LUNA_ROOT_PATH = str(_luna_path) if _luna_path.exists() else None


def _patch_pymel_api():
    """Patch pymel.api to include MQtUtil functions that Luna expects.

    Luna uses pymel.api.MQtUtil_mainWindow() but this doesn't exist in modern
    PyMEL. The actual function is maya.OpenMayaUI.MQtUtil.mainWindow().
    """
    try:
        import pymel.api as pma
        from maya.OpenMayaUI import MQtUtil

        # Add the MQtUtil_mainWindow function that Luna expects
        if not hasattr(pma, "MQtUtil_mainWindow"):
            pma.MQtUtil_mainWindow = MQtUtil.mainWindow

        # Also ensure MQtUtil is available for other functions Luna might use
        if not hasattr(pma, "MQtUtil"):
            pma.MQtUtil = MQtUtil

    except ImportError:
        pass


def _setup_luna_integration():
    """Set up Luna integration by patching moduleInfo and pre-creating directories module.

    This function must be called BEFORE any Luna imports. It:
    1. Patches pymel.api to include MQtUtil functions Luna expects
    2. Patches pymel.core.moduleInfo to return Luna's path when queried
    3. Pre-creates the luna.static.directories module with correct paths

    Returns:
        bool: True if setup was successful, False otherwise.
    """
    if LUNA_ROOT_PATH is None:
        return False

    try:
        import pymel.core as pm
    except ImportError:
        return False

    # Patch pymel.api first for Qt utilities
    _patch_pymel_api()

    # Store the original moduleInfo function
    _original_module_info = pm.moduleInfo

    def _patched_module_info(*args, **kwargs):
        """Patched moduleInfo that returns Luna path for luna module queries."""
        module_name = kwargs.get("moduleName") or (args[0] if args else None)
        if module_name == "luna":
            # Check if path (p) flag is requested
            if kwargs.get("p") or kwargs.get("path"):
                return LUNA_ROOT_PATH
        # For all other cases, call the original function
        return _original_module_info(*args, **kwargs)

    # Patch the moduleInfo function in pymel.core
    pm.moduleInfo = _patched_module_info

    # Also pre-create the luna.static.directories module to avoid any issues
    # with import order or multiple moduleInfo calls
    _create_directories_module(pm)

    return True


def _create_directories_module(pm):
    """Pre-create Luna's directories module with correct paths.

    Args:
        pm: The pymel.core module.
    """
    # Create a fake directories module with pre-computed paths
    directories_module = ModuleType("luna.static.directories")

    # Set all the path variables that directories.py would normally compute
    directories_module.MAYA_APP_PATH = str(pm.internalVar(uad=1))
    directories_module.TMP_PATH = pm.internalVar(utd=1)
    directories_module.USER_PREFS_PATH = pm.internalVar(upd=1)
    directories_module.LUNA_ROOT_PATH = LUNA_ROOT_PATH
    directories_module.LOG_FILE = os.path.join(LUNA_ROOT_PATH, "luna.log")
    directories_module.SHAPES_LIB_PATH = os.path.join(LUNA_ROOT_PATH, "res", "shapes")
    directories_module.TEMPLATES_PATH = os.path.join(LUNA_ROOT_PATH, "res", "templates")
    directories_module.EMPTY_SCENES_PATH = os.path.join(
        directories_module.TEMPLATES_PATH, "emptyScenes"
    )
    directories_module.ICONS_PATH = os.path.join(
        LUNA_ROOT_PATH, "res", "images", "icons"
    )
    directories_module.FALLBACK_IMG_PATH = os.path.join(
        LUNA_ROOT_PATH, "res", "images", "fallbacks"
    )
    directories_module.COMET_ORIENT_PATH = (
        directories_module.MAYA_APP_PATH + "scripts/comet/cometJointOrient.mel"
    )
    directories_module.DEFAULT_CONFIG_PATH = os.path.join(
        LUNA_ROOT_PATH, "configs", "default_config.json"
    )
    directories_module.CONFIG_PATH = os.path.join(
        LUNA_ROOT_PATH, "configs", "config.json"
    )
    directories_module.EXTERNAL_TOOLS_REGISTER = os.path.join(
        LUNA_ROOT_PATH, "configs", "external_tools.json"
    )
    directories_module.TEST_DIR_PATH = os.path.join(LUNA_ROOT_PATH, "tests")
    directories_module.PLUGINS_DIR_PATH = os.path.join(LUNA_ROOT_PATH, "plug-ins")
    directories_module.EDITOR_PLUGINS_PATH = os.path.join(
        LUNA_ROOT_PATH, "luna_builder", "rig_nodes"
    )

    # Add the get_icon_path function
    def get_icon_path(*path_parts):
        return os.path.join(directories_module.ICONS_PATH, *path_parts)

    directories_module.get_icon_path = get_icon_path

    # Create parent namespace modules if they don't exist
    # This is needed for "from luna.static import directories" to work
    if "luna" not in sys.modules:
        luna_module = ModuleType("luna")
        luna_module.__path__ = [LUNA_ROOT_PATH]
        sys.modules["luna"] = luna_module

    if "luna.static" not in sys.modules:
        static_module = ModuleType("luna.static")
        static_module.__path__ = [os.path.join(LUNA_ROOT_PATH, "luna", "static")]
        sys.modules["luna.static"] = static_module

    # Inject the directories module
    sys.modules["luna.static.directories"] = directories_module

    # Also set directories as an attribute of luna.static
    sys.modules["luna.static"].directories = directories_module


# Add Luna path to sys.path
if LUNA_ROOT_PATH and LUNA_ROOT_PATH not in sys.path:
    sys.path.insert(0, LUNA_ROOT_PATH)

# Try to import Luna modules
LUNA_AVAILABLE = False
luna = None
luna_rig = None
luna_builder = None

# Setup Luna integration before importing
if LUNA_ROOT_PATH and _setup_luna_integration():
    try:
        # Now we can safely import Luna - moduleInfo is patched and
        # directories module is pre-created
        import luna
        import luna_rig
        import luna_builder

        LUNA_AVAILABLE = True

    except ImportError as e:
        print(f"Warning: Luna not available - {e}")
    except Exception as e:
        print(f"Warning: Luna initialization error - {e}")

# Only import submodules if Luna is available
if LUNA_AVAILABLE:
    from . import components
    from . import functions
    from . import tools

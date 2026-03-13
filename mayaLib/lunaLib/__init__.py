"""Luna rigging framework integration for mayaLib.

This module provides a bridge between the Luna rigging framework and mayaLib,
exposing Luna components, functions and tools through the mayaLib menu system.

Luna expects to be installed as a Maya module (with a .mod file), but we're
integrating it as a submodule by adding it to sys.path. This requires patching
both the pymel.core.moduleInfo function and Luna's directories module BEFORE
any Luna imports occur.

Luna auto-initializes on Maya startup via evalDeferred to ensure PyMEL is ready.
"""

import os
import sys
import traceback
from pathlib import Path
from types import ModuleType

# Determine Luna root path
_luna_path = Path(__file__).parent.parent.parent / "luna"
LUNA_ROOT_PATH = str(_luna_path) if _luna_path.exists() else None

# Add Luna path to sys.path early
if LUNA_ROOT_PATH and LUNA_ROOT_PATH not in sys.path:
    sys.path.insert(0, LUNA_ROOT_PATH)

# Lazy loading state
_luna_initialized = False
_luna_available = False
luna = None
luna_rig = None
luna_builder = None


def _setup_luna_integration():
    """Set up Luna integration by patching moduleInfo and pre-creating directories module.

    This function must be called BEFORE any Luna imports. It:
    1. Patches pymel.core.moduleInfo to return Luna's path when queried
    2. Pre-creates the luna.static.directories module with correct paths

    Returns:
        bool: True if setup was successful, False otherwise.
    """
    if LUNA_ROOT_PATH is None:
        return False

    try:
        import pymel.core as pm
    except ImportError:
        return False

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

    # We ONLY inject luna.static.directories into sys.modules.
    # We do NOT create luna or luna.static - those will import normally from
    # the real Luna package. When Python later tries to import luna.static.directories,
    # it will find our pre-injected module in sys.modules and use it instead of
    # running the real directories.py (which would fail due to moduleInfo).
    sys.modules["luna.static.directories"] = directories_module


def _install_pyside2_shim():
    """Install a PySide2 compatibility shim that redirects to PySide6.

    Maya 2025+ ships with PySide6 only. Luna hardcodes PySide2 imports,
    so we inject fake PySide2/shiboken2 modules into sys.modules that
    proxy to PySide6/shiboken6. This is a no-op if PySide2 is already available.
    """
    try:
        import PySide2  # noqa: F401
        return  # PySide2 genuinely available, no shim needed
    except ImportError:
        pass

    try:
        import PySide6
    except ImportError:
        return  # Neither available, let the import fail naturally

    # Map PySide2 top-level to PySide6
    sys.modules["PySide2"] = PySide6

    # Map each PySide2 submodule Luna uses to its PySide6 equivalent
    _submodules = [
        "QtCore", "QtGui", "QtWidgets", "QtNetwork", "QtSvg",
        "QtUiTools", "QtXml",
    ]
    for submod in _submodules:
        pyside6_submod = getattr(PySide6, submod, None)
        if pyside6_submod is None:
            try:
                pyside6_submod = __import__(f"PySide6.{submod}", fromlist=[submod])
            except ImportError:
                continue
        sys.modules[f"PySide2.{submod}"] = pyside6_submod

    # Map shiboken2 → shiboken6
    try:
        import shiboken6
        sys.modules["shiboken2"] = shiboken6
    except ImportError:
        pass


def _initialize_luna():
    """Initialize Luna modules (lazy loading).

    This function is called on first access to Luna functionality.
    It sets up the integration and imports Luna modules.

    Returns:
        bool: True if Luna was successfully initialized.
    """
    global _luna_initialized, _luna_available, luna, luna_rig, luna_builder

    if _luna_initialized:
        return _luna_available

    _luna_initialized = True

    # Respect the disable flag from Maya.env / userSetup.py
    if os.environ.get("DEVPYLIB_DISABLE_LUNA", "0") == "1":
        _luna_available = False
        return False

    if not LUNA_ROOT_PATH:
        print(f"Warning: Luna path not found at {_luna_path}")
        return False

    if not _setup_luna_integration():
        print("Warning: Luna setup failed - _setup_luna_integration() returned False")
        return False

    # Install PySide2 compatibility shim for Maya 2025+ (which ships PySide6 only).
    # Luna hardcodes `from PySide2 import ...` so we redirect to PySide6.
    _install_pyside2_shim()

    try:
        # Now we can safely import Luna - moduleInfo is patched and
        # directories module is pre-created in sys.modules
        import luna as _luna
        import luna_rig as _luna_rig
        import luna_builder as _luna_builder

        luna = _luna
        luna_rig = _luna_rig
        luna_builder = _luna_builder
        _luna_available = True

        # Import submodules
        from . import components
        from . import functions
        from . import tools

        return True

    except ImportError as e:
        print(f"Warning: Luna not available - {e}")
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"Warning: Luna initialization error - {e}")
        traceback.print_exc()
        return False


def is_available():
    """Check if Luna is available.

    This will trigger lazy initialization if not already done.

    Returns:
        bool: True if Luna is available and initialized.
    """
    return _initialize_luna()


# For backwards compatibility
@property
def LUNA_AVAILABLE():
    """Check if Luna is available (property for backwards compatibility)."""
    return is_available()


# Make LUNA_AVAILABLE work as a simple boolean check too
def __getattr__(name):
    """Module-level __getattr__ for lazy loading."""
    if name == "LUNA_AVAILABLE":
        return is_available()
    if name in ("luna", "luna_rig", "luna_builder"):
        _initialize_luna()
        return globals().get(name)
    if name in ("components", "functions", "tools"):
        if _initialize_luna():
            return getattr(sys.modules[__name__], name, None)
        return None
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def deferred_autostart():
    """Auto-start Luna on Maya startup.

    This is called via Maya's evalDeferred to ensure PyMEL is ready.
    """
    _initialize_luna()


# Auto-start Luna on Maya startup (deferred to ensure PyMEL is ready)
try:
    import maya.cmds as cmds
    cmds.evalDeferred("from mayaLib.lunaLib import deferred_autostart; deferred_autostart()", lowestPriority=True)
except ImportError:
    pass  # Not in Maya environment

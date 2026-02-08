"""Root pytest configuration for DevPyLib.

Mocks Maya and other DCC dependencies to allow testing without DCC environment.
"""

import sys
from types import ModuleType
from unittest.mock import MagicMock


class MockModule(ModuleType):
    """Mock module that auto-creates sub-modules on attribute access."""

    def __init__(self, name):
        """Initialize mock module."""
        super().__init__(name)
        self.__package__ = name  # Mark as package
        self.__path__ = []  # Mark as package with path

    def __getattr__(self, name):
        """Auto-create mock sub-modules."""
        # Check if already mocked in sys.modules
        full_name = f"{self.__name__}.{name}"
        if full_name in sys.modules:
            return sys.modules[full_name]

        # Create new mock module
        mock = MagicMock()
        sys.modules[full_name] = mock
        setattr(self, name, mock)
        return mock


# Create comprehensive Maya mock
maya = MockModule("maya")
sys.modules["maya"] = maya
sys.modules["maya.cmds"] = MagicMock()
sys.modules["maya.api"] = MagicMock()
sys.modules["maya.api.OpenMaya"] = MagicMock()
sys.modules["maya.OpenMayaUI"] = MagicMock()
sys.modules["maya.mel"] = MagicMock()
sys.modules["maya.internal"] = MagicMock()
sys.modules["maya.internal.nodes"] = MagicMock()
sys.modules["maya.internal.nodes.proximitywrap"] = MagicMock()
sys.modules["maya.internal.nodes.proximitywrap.node_interface"] = MagicMock()
sys.modules["pymel"] = MagicMock()
sys.modules["pymel.core"] = MagicMock()

# Mock Maya plugins and tools
sys.modules["ngSkinTools2"] = MagicMock()
sys.modules["ngSkinTools2.api"] = MagicMock()

# Mock Git/GitPython (if not installed)
try:
    import git  # noqa: F401
except ImportError:
    sys.modules["git"] = MagicMock()

# Mock Houdini modules
sys.modules["hou"] = MagicMock()

# Mock Blender modules
sys.modules["bpy"] = MagicMock()

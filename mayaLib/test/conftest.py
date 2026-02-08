"""Pytest configuration for mayaLib tests.

Mocks Maya dependencies to allow testing without Maya environment.
"""

import sys
from unittest.mock import MagicMock

# Mock Maya modules before any mayaLib imports
maya_mock = MagicMock()
sys.modules["maya"] = maya_mock
sys.modules["maya.cmds"] = MagicMock()
sys.modules["maya.api"] = MagicMock()
sys.modules["maya.api.OpenMaya"] = MagicMock()
sys.modules["maya.mel"] = MagicMock()
sys.modules["pymel"] = MagicMock()
sys.modules["pymel.core"] = MagicMock()

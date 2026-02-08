"""Pytest configuration for DevPyLib tests.

Provides fixtures and setup for testing without Maya.
"""

import sys
from unittest.mock import MagicMock


def pytest_configure(config):
    """Configure pytest before collecting tests."""
    # Ensure user site-packages is in path
    import site
    user_site = site.getusersitepackages()
    if user_site not in sys.path:
        sys.path.insert(0, user_site)

    # Mock all Maya modules and third-party plugins before any imports
    maya_modules = [
        # Core Maya modules
        "maya",
        "maya.cmds",
        "maya.mel",
        "maya.api",
        "maya.api.OpenMaya",
        "maya.utils",
        "maya.internal",
        "maya.internal.nodes",
        "maya.internal.nodes.proximitywrap",
        "maya.internal.nodes.proximitywrap.node_interface",
        "maya.OpenMayaUI",
        "pymel",
        "pymel.core",
        "OpenMaya",
        "OpenMayaUI",
        # Maya plugins and third-party tools
        "ngSkinTools2",
        "ngSkinTools2.api",
        "bifrost",
        "zBuilder",
        "zBuilder.bundle",
        "zBuilder.bundle.utils",
        "zBuilder.bundle.utils.vfxUtils",
        "vnnCompiler",
    ]

    for module in maya_modules:
        if module not in sys.modules:
            sys.modules[module] = MagicMock()

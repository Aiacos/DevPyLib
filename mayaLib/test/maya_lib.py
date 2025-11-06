"""MayaLib plugin registration example.

Demonstrates creating a simple Maya plugin command for
the DevPyLib library.
"""

__author__ = 'Lorenzo Argentieri'

import sys

import maya.api.OpenMaya as om

import mayaLib.guiLib.main_menu as mm


def maya_useNewAPI():
    """The presence of this function tells Maya that the plugin produces, and
    expects to be passed, objects created using the Maya Python API 2.0.
    """
    pass


# command
class MayaLibPlugin(om.MPxCommand):
    """MayaLib plugin command for loading the DevPyLib main menu."""

    k_plugin_cmd_name = 'MayaLib'

    def __init__(self):
        """Initialize the MayaLib plugin command."""
        om.MPxCommand.__init__(self)

    @staticmethod
    def cmdCreator():
        """Create and return a new instance of the command."""
        return MayaLibPlugin()

    def doIt(self, args):
        """Execute the command by launching the MainMenu."""
        mm.MainMenu()


# Initialize the plug-in
def initializePlugin(plugin):
    """Initialize the MayaLib plugin.

    Args:
        plugin: Maya plugin object to initialize.
    """
    pluginFn = om.MFnPlugin(plugin, 'Lorenzo Argentieri', '1.0')
    try:
        pluginFn.registerCommand(
            MayaLibPlugin.k_plugin_cmd_name, MayaLibPlugin.cmdCreator
        )
    except RuntimeError:
        sys.stderr.write(
            "Failed to register command: %s\n" % MayaLibPlugin.k_plugin_cmd_name
        )
        raise


# Uninitialize the plug-in
def uninitializePlugin(plugin):
    """Uninitialize the MayaLib plugin.

    Args:
        plugin: Maya plugin object to uninitialize.
    """
    pluginFn = om.MFnPlugin(plugin)
    try:
        pluginFn.deregisterCommand(MayaLibPlugin.k_plugin_cmd_name)
    except RuntimeError:
        sys.stderr.write(
            "Failed to unregister command: %s\n" % MayaLibPlugin.k_plugin_cmd_name
        )
        raise

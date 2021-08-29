__author__ = 'Lorenzo Argentieri'

import sys

import maya.api.OpenMaya as om

import mayaLib.guiLib.mainMenu as mm


def maya_useNewAPI():
    """
    The presence of this function tells Maya that the plugin produces, and
    expects to be passed, objects created using the Maya Python API 2.0.
    """
    pass


# command
class MayaLibPlugin(om.MPxCommand):
    kPluginCmdName = 'MayaLib'

    def __init__(self):
        om.MPxCommand.__init__(self)

    @staticmethod
    def cmdCreator():
        return MayaLibPlugin()

    def doIt(self, args):
        mm.MainMenu()


# Initialize the plug-in
def initializePlugin(plugin):
    pluginFn = om.MFnPlugin(plugin, 'Lorenzo Argentieri', '1.0')
    try:
        pluginFn.registerCommand(
            MayaLibPlugin.kPluginCmdName, MayaLibPlugin.cmdCreator
        )
    except:
        sys.stderr.write(
            "Failed to register command: %s\n" % MayaLibPlugin.kPluginCmdName
        )
        raise


# Uninitialize the plug-in
def uninitializePlugin(plugin):
    pluginFn = om.MFnPlugin(plugin)
    try:
        pluginFn.deregisterCommand(MayaLibPlugin.kPluginCmdName)
    except:
        sys.stderr.write(
            "Failed to unregister command: %s\n" % MayaLibPlugin.kPluginCmdName
        )
        raise

__author__ = 'Lorenzo Argentieri'

from maya import OpenMayaMPx
import maya.cmds as cmds
import mayaLib.guiLib.mainMenu as mm


class MayaLibPlugin(OpenMayaMPx.MPxCommand):
    def doIt(self, *args, **kwargs):
        self.lib = mm.MainMenu()

def create_plugin():
    return OpenMayaMPx.asMPxPtr(MayaLibPlugin())

plugin_name = 'MayaLib'

def _toplugin(mobject):
    return OpenMayaMPx.MFnPlugin(mobject, 'Lorenzo Argentieri', '0.01')

def initializePlugin(mobject):
    plugin = _toplugin(mobject)
    def register():
        import pymel.core as pmc
        plugin.registerCommand(plugin_name, create_plugin)
    cmds.evalDeferred(register)

def uninitializePlugin(mobject):
    plugin = _toplugin(mobject)
    plugin.deregisterCommand(plugin_name)
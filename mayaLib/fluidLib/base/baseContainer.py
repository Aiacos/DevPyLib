__author__ = 'Lorenzo Argentieri'

import maya.mel as mel
import pymel.core as pm


class FluidContainer():
    def __init__(self):
        """
        Fluid Container
        """
        self.container = pm.ls(mel.eval('create3DFluid 10 10 10 10 10 10;'))

    def getContainer(self):
        return self.container

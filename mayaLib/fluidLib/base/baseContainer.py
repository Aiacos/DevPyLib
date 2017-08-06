__author__ = 'Lorenzo Argentieri'

import pymel.core as pm
import maya.mel as mel

class FluidContainer():
    def __init__(self):
        self.container = pm.ls(mel.eval('create3DFluid 10 10 10 10 10 10;'))

    def getContainer(self):
        return self.container

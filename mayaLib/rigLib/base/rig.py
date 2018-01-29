__author__ = 'Lorenzo Argentieri'

import pymel.core as pm
from mayaLib.rigLib.base.module import  Base
from mayaLib.rigLib.utils import name


class Rig():
    def __init__(self, model_filePath='', buildScene_filePath='',
                       doProxyGeo=True,
                       loadSkinCLuster=True
                       ):
        # New Scene
        if model_filePath != '':
            pm.newFile()

        # Import model
        if model_filePath != '':
            pm.importFile(model_filePath)

        # Import buildScene
        if buildScene_filePath != '':
            pm.importFile(buildScene_filePath)

        # Load SkinCluster
        if loadSkinCLuster:
            pass

        # Create proxy geo
        if doProxyGeo:
            pass

        # Create rig
        baseModule = Base(characterName='new', scale=1.0, mainCtrlAttachObj='')

    def prepare(self):
        pass

    def upgrade(self):
        pass

    def finalize(self):
        pass


if __name__ == "__main__":
    mRig = Rig()

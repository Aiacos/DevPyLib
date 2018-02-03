__author__ = 'Lorenzo Argentieri'

import pymel.core as pm
from mayaLib.rigLib.base.module import  Base
from mayaLib.rigLib.utils import name
from mayaLib.rigLib.utils import skin


class Rig():
    def __init__(self, characterName='new',
                 model_filePath='', buildScene_filePath='',
                 rootJnt='spineJA_JNT',
                 doProxyGeo=True,
                 loadSkinCluster=True
                 ):
        """
        Create Base Rig
        :param characterName: str
        :param model_filePath: str
        :param buildScene_filePath: str
        :param rootJnt: str
        :param doProxyGeo: bool
        :param loadSkinCluster: bool
        """
        # New Scene
        if buildScene_filePath:
            pm.newFile()

        # Import model
        if model_filePath:
            pm.importFile(model_filePath)

        # Import buildScene
        if buildScene_filePath:
            pm.importFile(buildScene_filePath)

        # Load SkinCluster
        if loadSkinCluster:
            geoList = [geo.name() for geo in pm.ls('*_GEO')]
            skin.loadSkinWeights(characterName, geoList)

        # Create proxy geo
        if doProxyGeo:
            pass

        # Create rig
        baseModule = Base(characterName=characterName, scale=1.0, mainCtrlAttachObj='')

        # parent model group
        modelGrpName = characterName + 'model' + '_GRP'
        pm.parent(modelGrpName, baseModule.modelGrp)

        # parent joint group
        pm.parentConstraint(rootJnt, baseModule.jointsGrp)


    def prepare(self):
        pass

    def upgrade(self):
        pass

    def finalize(self):
        pass


if __name__ == "__main__":
    mRig = Rig()

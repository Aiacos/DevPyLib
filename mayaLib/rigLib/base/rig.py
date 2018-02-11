__author__ = 'Lorenzo Argentieri'

import pymel.core as pm
from mayaLib.rigLib.base.module import  Base
from mayaLib.rigLib.utils import name
from mayaLib.rigLib.utils import skin
from mayaLib.rigLib.utils import util


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
            pm.newFile(force=True)

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

        # search model grp
        modelGrp = pm.ls(characterName + '_model' + '_GRP')[0]
        if pm.objExists(modelGrp):
            modelBBox = modelGrp.getBoundingBox()
            radius = util.get_distance_from_coords([modelBBox[0][0], 0, modelBBox[0][2]], [modelBBox[1][0], 0, modelBBox[1][2]])
            radius = radius / 1.5

        # Create proxy geo
        if doProxyGeo:
            pass

        # Create rig
        baseModule = Base(characterName=characterName, scale=radius, mainCtrlAttachObj=rootJnt)

        # parent model group
        if pm.objExists(modelGrp):
            pm.parent(modelGrp, baseModule.modelGrp)

        # parent joint group
        if pm.objExists(rootJnt):
            pm.parent(rootJnt, baseModule.jointsGrp)


    def prepare(self):
        pass

    def upgrade(self):
        pass

    def finalize(self):
        pass


if __name__ == "__main__":
    mRig = Rig()

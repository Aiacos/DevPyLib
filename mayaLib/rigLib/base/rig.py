__author__ = 'Lorenzo Argentieri'

import pymel.core as pm
from mayaLib.rigLib.base.module import Base
from mayaLib.rigLib.utils import name
from mayaLib.rigLib.utils import skin
from mayaLib.rigLib.utils import util

from mayaLib.rigLib.base import control
from mayaLib.rigLib.base import spine
from mayaLib.rigLib.base import neck
from mayaLib.rigLib.base import ikChain

from mayaLib.rigLib.utils import proxyGeo


class BaseRig(object):
    def __init__(self, characterName='new',
                 model_filePath='', buildScene_filePath='',
                 rootJnt='spineJA_JNT',
                 headJnt='headJA_JNT',
                 loadSkinCluster=True,
                 doProxyGeo=True
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
        modelGrp = pm.ls(characterName + '_model' + '_GRP')
        if pm.objExists(modelGrp):
            modelBBox = modelGrp[0].getBoundingBox()
            radius = util.get_distance_from_coords([modelBBox[0][0], 0, modelBBox[0][2]], [modelBBox[1][0], 0, modelBBox[1][2]])
            radius = radius / 1.5

        # Create proxy geo
        if doProxyGeo:
            pass

        # Create rig
        self.baseModule = Base(characterName=characterName, scale=radius, mainCtrlAttachObj=headJnt)

        # parent model group
        if pm.objExists(modelGrp):
            pm.parent(modelGrp, self.baseModule.modelGrp)

        # parent joint group
        if pm.objExists(rootJnt):
            pm.parent(rootJnt, self.baseModule.jointsGrp)


    def prepare(self):
        pass

    def upgrade(self):
        pass

    def finalize(self):
        pass


class Rig(BaseRig):
    """
    Rig
    """
    def __init__(self, characterName='new',
                 model_filePath='', buildScene_filePath='',
                 sceneScale=1,
                 rootJnt='spineJA_JNT',
                 headJnt='headJA_JNT',
                 loadSkinCluster=True,
                 doProxyGeo=True,
                 doSpine=True,
                 doNeck=True,
                 doTail=True, doDynamicTail=False,
                 ):
        """
        Create Base Rig
        :param characterName: str
        :param model_filePath: str
        :param buildScene_filePath: str
        :param sceneScale: float
        :param rootJnt: str
        :param headJnt: str
        :param loadSkinCluster: bool
        :param doProxyGeo: bool
        :param doSpine: bool
        :param doNeck: bool
        :param doTail: bool
        """
        super(Rig, self).__init__(characterName, model_filePath, buildScene_filePath, rootJnt, headJnt, doProxyGeo, loadSkinCluster)

        if doSpine:
            spineJoints = pm.ls('spine*_JNT')
            #spineJoints = ['spine1_jnt', 'spine2_jnt', 'spine3_jnt', 'spine4_jnt', 'spine5_jnt', 'spine6_jnt']
            spineRig = spine.Spine(spineJoints, rootJnt, prefix='spine', rigScale=sceneScale, baseRig=self.baseModule)

        if doNeck:
            neckJoints = pm.ls('neck*_JNT')
            #neckJoints = ['neck1_jnt', 'neck2_jnt', 'neck3_jnt', 'neck4_jnt', 'neck5_jnt', 'neck6_jnt']
            neckRig = neck.Neck(neckJoints, headJnt, prefix='neck', rigScale=sceneScale, baseRig=self.baseModule)

        if doSpine and doNeck:
            pm.parentConstraint(spineJoints[-1], neckRig.getModuleDict()['baseAttachGrp'], mo=1)
            pm.parentConstraint(spineRig.getModuleDict()['bodyCtrl'].C, neckRig.getModuleDict()['bodyAttachGrp'], mo=1)

        if doTail:
            tailJoints = pm.ls('tail*_JNT')
            pelvisJnt = pm.ls('pelvis*_JNT')[-1]
            tailRig = ikChain.IKChain(
                chainJoints=tailJoints,
                prefix='tail',
                rigScale=sceneScale,
                doDynamic=doDynamicTail,
                smallestScalePercent=0.4,
                fkParenting=False,
                baseRig=self.baseModule)

            pm.parentConstraint(pelvisJnt, tailRig.getModuleDict()['baseAttachGrp'], mo=1)


if __name__ == "__main__":
    mRig = Rig()

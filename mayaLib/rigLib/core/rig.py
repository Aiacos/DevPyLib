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
from mayaLib.rigLib.base import limb
from mayaLib.rigLib.utils import ikfkSwitch
from mayaLib.rigLib.utils import ctrlShape

from mayaLib.rigLib.utils import proxyGeo


class BaseRig(object):
    def __init__(self, characterName='new',
                 model_filePath='', buildScene_filePath='',
                 rootJnt='spineJA_jnt',
                 headJnt='headJA_jnt',
                 loadSkinCluster=True,
                 doProxyGeo=True
                 ):
        """
        Create Base Rig
        :param characterName: str
        :param model_filePath: str
        :param buildScene_filePath: str
        :param rootJnt: str
        :param loadSkinCluster: bool
        :param doProxyGeo: bool
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

        # Create proxy geo
        self.prxGeoList = pm.ls('*_PRX')
        if doProxyGeo:
            if len(self.prxGeoList) == 0 and len(pm.ls('mainProxy_GEO')) > 0:
                mainProxyGeo = pm.ls('mainProxy_GEO')[0]
                prxGeoInstance = proxyGeo.ProxyGeo(mainProxyGeo)
                self.prxGeoList = prxGeoInstance.getProxyGeoList()

        self.prepare()

        # search model grp
        self.sceneRadius = 1
        modelGrp = pm.ls(characterName + '_model' + '_GRP')
        if modelGrp:
            radius = util.getPlanarRadiusBBOXFromTransform(modelGrp[0])['planarY']
            self.sceneRadius = radius

        # Create rig
        self.baseModule = Base(characterName=characterName, scale=self.sceneRadius, mainCtrlAttachObj=headJnt)

        # parent model group and clean scene
        if modelGrp:
            pm.parent(modelGrp, self.baseModule.mediumSlowGrp)
            if len(self.prxGeoList) > 0:
                pm.parent(self.prxGeoList, self.baseModule.fastModelGrp)
                if doProxyGeo and len(pm.ls('mainProxy_GEO')) > 0 and pm.objExists(prxGeoInstance.getFastGeoGroup()):
                    pm.delete(prxGeoInstance.getFastGeoGroup(), pm.ls('mainProxy_GEO'))

        # parent joint group
        if pm.objExists(rootJnt):
            pm.parent(rootJnt, self.baseModule.jointsGrp)

        # Load SkinCluster
        if loadSkinCluster:
            geoList = [geo.name() for geo in pm.ls('*_GEO')]
            skin.loadSkinWeights(characterName, geoList)

        self.upgrade()

        # control shape
        if pm.objExists('controlShapes_GRP'):
            controlShapeList = util.getAllObjectUnderGroup('controlShapes_GRP', type='transform')
            controlList = [cv for cv in pm.ls('*_CTRL') if cv not in controlShapeList]
            for ctrl in controlList:
                for ctrlshape in controlShapeList:
                    if ctrlshape.name().split('|')[-1] == ctrl.name().split('|')[-1]:
                        ctrlShape.copyShape(ctrlshape, ctrl)
            pm.delete('controlShapes_GRP')

        self.finalize()

    def prepare(self):
        pass

    def upgrade(self):
        pass

    def finalize(self):
        pass

    def makeSpine(self, rootJnt, spineJoints, sceneScale):
        """
        Make general Spine
        :param rootJnt:
        :param spineJoints:
        :param sceneScale:
        :return:
        """
        spineRig = spine.Spine(spineJoints, rootJnt, prefix='spine', rigScale=sceneScale, baseRig=self.baseModule)

        return spineRig

    def makeNeck(self, headJnt, neckJoints, sceneScale, spineRig=None, spineJoints=[]):
        neckRig = neck.Neck(neckJoints, headJnt, prefix='neck', rigScale=sceneScale, baseRig=self.baseModule)

        if spineRig and len(spineJoints) > 0:
            pm.parentConstraint(spineJoints[-1], neckRig.getModuleDict()['baseAttachGrp'], mo=1)
            pm.parentConstraint(spineRig.getModuleDict()['bodyCtrl'].C, neckRig.getModuleDict()['bodyAttachGrp'], mo=1)

        return neckRig

    def makeTail(self, pelvisJnt, tailJoints, doDynamicTail, sceneScale):
        tailRig = ikChain.IKChain(
            chainJoints=tailJoints,
            prefix='tail',
            rigScale=sceneScale,
            doDynamic=doDynamicTail,
            smallestScalePercent=0.4,
            fkParenting=False,
            baseRig=self.baseModule)

        pm.parentConstraint(pelvisJnt, tailRig.getModuleDict()['baseAttachGrp'], mo=1)

        return tailRig

    def makeLimb(self, spineRig, scapulaJoint, limbJoints, topFngJoints):
        """
        Make general Limb
        :param spineRig: instance
        :param scapulaJoint: str
        :param limbJoints: list(str)
        :param topFngJoints: list(str)
        :return: instance, limbRig
        """
        limbRig = limb.Limb(limbJoints=limbJoints, topFingerJoints=topFngJoints, scapulaJnt=scapulaJoint, baseRig=self.baseModule)

        if scapulaJoint:
            pm.parentConstraint(limbJoints[-1], limbRig.getModuleDict()['baseAttachGrp'], mo=1)
        else:
            pm.parentConstraint(spineRig.getModuleDict()['baseAttachGrp'], limbRig.getModuleDict()['baseAttachGrp'], mo=1)

        pm.parentConstraint(spineRig.getModuleDict()['bodyCtrl'].C, limbRig.getModuleDict()['bodyAttachGrp'], mo=1)

        return limbRig


class Rig(BaseRig):
    """
    Rig
    """
    def __init__(self, characterName='new',
                 model_filePath='', buildScene_filePath='',
                 sceneScale=1,
                 rootJnt='root1_jnt',
                 headJnt='head1_jnt',
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
        super(Rig, self).__init__(characterName, model_filePath, buildScene_filePath, rootJnt, headJnt, loadSkinCluster, doProxyGeo)

        if doSpine:
            spineJoints = pm.ls('spine*_jnt')
            #spineJoints = ['spine1_jnt', 'spine2_jnt', 'spine3_jnt', 'spine4_jnt', 'spine5_jnt', 'spine6_jnt']
            spineRig = spine.Spine(spineJoints, rootJnt, prefix='spine', rigScale=sceneScale, baseRig=self.baseModule)

        if doNeck:
            neckJoints = pm.ls('neck*_jnt')
            #neckJoints = ['neck1_jnt', 'neck2_jnt', 'neck3_jnt', 'neck4_jnt', 'neck5_jnt', 'neck6_jnt']
            neckRig = neck.Neck(neckJoints, headJnt, prefix='neck', rigScale=sceneScale, baseRig=self.baseModule)

        if doSpine and doNeck:
            pm.parentConstraint(spineJoints[-1], neckRig.getModuleDict()['baseAttachGrp'], mo=1)
            pm.parentConstraint(spineRig.getModuleDict()['bodyCtrl'].C, neckRig.getModuleDict()['bodyAttachGrp'], mo=1)

        if doTail:
            tailJoints = pm.ls('tail*_jnt')
            pelvisJnt = pm.ls('pelvis*_jnt')[-1]
            tailRig = ikChain.IKChain(
                chainJoints=tailJoints,
                prefix='tail',
                rigScale=sceneScale,
                doDynamic=doDynamicTail,
                smallestScalePercent=0.4,
                fkParenting=False,
                baseRig=self.baseModule)

            pm.parentConstraint(pelvisJnt, tailRig.getModuleDict()['baseAttachGrp'], mo=1)


        # left arm
        legJoints = ['l_shoulder1_jnt', 'l_elbow1_jnt', 'l_hand1_jnt']
        topToeJoints = ['l_foreToeA1_jnt', 'l_foreToeB1_jnt', 'l_foreToeC1_jnt', 'l_foreToeD1_jnt', 'l_foreToeE1_jnt']

        lArmRig = limb.Limb(limbJoints=legJoints, topFingerJoints=topToeJoints, scapulaJnt='l_scapula1_jnt', baseRig=self.baseModule)

        pm.parentConstraint(spineJoints[-2], lArmRig.getModuleDict()['baseAttachGrp'], mo=1)
        pm.parentConstraint(spineRig.getModuleDict()['bodyCtrl'].C, lArmRig.getModuleDict()['bodyAttachGrp'], mo=1)

        # right arm
        legJoints = ['r_shoulder1_jnt', 'r_elbow1_jnt', 'r_hand1_jnt']
        topToeJoints = ['r_foreToeA1_jnt', 'r_foreToeB1_jnt', 'r_foreToeC1_jnt', 'r_foreToeD1_jnt', 'r_foreToeE1_jnt']

        rArmRig = limb.Limb(limbJoints=legJoints, topFingerJoints=topToeJoints, scapulaJnt='r_scapula1_jnt', baseRig=self.baseModule)

        pm.parentConstraint(spineJoints[-2], rArmRig.getModuleDict()['baseAttachGrp'], mo=1)
        pm.parentConstraint(spineRig.getModuleDict()['bodyCtrl'].C, rArmRig.getModuleDict()['bodyAttachGrp'], mo=1)

        # left leg
        legJoints = ['l_hip1_jnt', 'l_knee1_jnt', 'l_foot1_jnt']
        topToeJoints = ['l_hindToeA1_jnt', 'l_hindToeB1_jnt', 'l_hindToeC1_jnt', 'l_hindToeD1_jnt', 'l_hindToeE1_jnt']

        lLegRig = limb.Limb(limbJoints=legJoints, topFingerJoints=topToeJoints, scapulaJnt='', baseRig=self.baseModule)

        pm.parentConstraint(spineJoints[0], lLegRig.getModuleDict()['baseAttachGrp'], mo=1)
        pm.parentConstraint(spineRig.getModuleDict()['bodyCtrl'].C, lLegRig.getModuleDict()['bodyAttachGrp'], mo=1)

        # right leg
        legJoints = ['r_hip1_jnt', 'r_knee1_jnt', 'r_foot1_jnt']
        topToeJoints = ['r_hindToeA1_jnt', 'r_hindToeB1_jnt', 'r_hindToeC1_jnt', 'r_hindToeD1_jnt', 'r_hindToeE1_jnt']

        rLegRig = limb.Limb(limbJoints=legJoints, topFingerJoints=topToeJoints, scapulaJnt='', baseRig=self.baseModule)

        pm.parentConstraint(spineJoints[0], rLegRig.getModuleDict()['baseAttachGrp'], mo=1)
        pm.parentConstraint(spineRig.getModuleDict()['bodyCtrl'].C, rLegRig.getModuleDict()['bodyAttachGrp'], mo=1)

        ikfkSwitch.installIKFK([lArmRig.getMainLimbIK(), rArmRig.getMainLimbIK(), lLegRig.getMainLimbIK(), rLegRig.getMainLimbIK()])




if __name__ == "__main__":
    mRig = Rig()

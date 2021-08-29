__author__ = 'Lorenzo Argentieri'

import pymel.core as pm

from mayaLib.rigLib.base import ikChain
from mayaLib.rigLib.base import limb
from mayaLib.rigLib.base import neck
from mayaLib.rigLib.base import spine
from mayaLib.rigLib.base.module import Base
from mayaLib.rigLib.utils import ctrlShape
from mayaLib.rigLib.utils import ikfkSwitch
from mayaLib.rigLib.utils import joint
from mayaLib.rigLib.utils import proxyGeo
from mayaLib.rigLib.utils import skin
from mayaLib.rigLib.utils import stretchyIKChain
from mayaLib.rigLib.utils import util


class BaseRig(object):
    def __init__(self, characterName='new',
                 model_filePath='', buildScene_filePath='',
                 rootJnt='spineJA_jnt',
                 headJnt='headJA_jnt',
                 loadSkinCluster=True,
                 doProxyGeo=True,
                 goToTPose=True
                 ):
        """
        Create Base Rig
        :param characterName: str
        :param model_filePath: str
        :param buildScene_filePath: str
        :param rootJnt: str
        :param loadSkinCluster: bool
        :param doProxyGeo: bool
        :param goToTPose: bool
        """

        start = pm.timerX()
        print('-- START --')

        # New Scene
        if buildScene_filePath:
            pm.newFile(force=True)

        # Import model
        if model_filePath:
            pm.importFile(model_filePath)

        # Import buildScene
        if buildScene_filePath:
            pm.importFile(buildScene_filePath)

        if goToTPose:
            joint.loadTPose(rootJnt)

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
        self.rig()

        # parent model group and clean scene
        if modelGrp:
            pm.parent(modelGrp, self.baseModule.mediumSlowGrp)
            if len(self.prxGeoList) > 0:
                pm.parent(self.prxGeoList, self.baseModule.fastModelGrp)
                if doProxyGeo and len(pm.ls('mainProxy_GEO')) > 0 and pm.objExists(prxGeoInstance.getFastGeoGroup()):
                    pm.delete(prxGeoInstance.getFastGeoGroup(), pm.ls('mainProxy_GEO'))

        if pm.objExists('skeletonModel_GRP'):
            pm.parent('skeletonModel_GRP', self.baseModule.rigModelGrp)

        # parent joint group
        if pm.objExists(rootJnt):
            pm.parent(rootJnt, self.baseModule.jointsGrp)

        # Load SkinCluster
        if loadSkinCluster:
            joint.loadProjectionPose(rootJnt)
            geoList = [geo.name() for geo in pm.ls('*_GEO')]
            skin.loadSkinWeights(characterName, geoList)

        self.upgrade()

        # control shape
        if pm.objExists('controlShapes_GRP'):
            controlShapeList = pm.ls('*_shape_CTRL*')
            controlList = [cv for cv in pm.ls('*_CTRL', '*_CTRL?') if cv not in controlShapeList]
            for ctrl in controlList:
                for ctrlshape in controlShapeList:
                    if str(ctrlshape.name()).replace('_shape_CTRL', '_CTRL') == str(ctrl.name()):
                        print('Transfering Shape: ', str(ctrlshape.name()), ' <-----> ', str(ctrl.name()))
                        ctrlShape.copyShape(ctrlshape, ctrl)
            pm.delete('controlShapes_GRP')

        self.finalize()

        totalTime = pm.timerX(startTime=start)
        print('-- END --')
        print('Total time: ', totalTime)

    def prepare(self):
        pass
        print('-- PREPARE --')

    def rig(self):
        pass
        print('-- RIG --')

    def upgrade(self):
        pass
        print('-- UPGRADE --')

    def finalize(self):
        pass
        print('-- FINALIZE --')

    def makeSpine(self, prefix, rootJnt, spineJoints, sceneScale):
        """
        Make general Spine
        :param rootJnt:
        :param spineJoints:
        :param sceneScale:
        :return:
        """
        spineRig = spine.Spine(spineJoints, rootJnt, prefix=prefix, rigScale=sceneScale, baseRig=self.baseModule)

        return spineRig

    def makeNeck(self, prefix, headJnt, neckJoints, sceneScale, spineRig=None, spineJoints=[]):
        neckRig = neck.Neck(neckJoints, headJnt, prefix=prefix, rigScale=sceneScale, baseRig=self.baseModule)

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

    def makeLimb(self, spineRig, clavicleJnt, scapulaJoint, limbJoints, topFngJoints, spineDriverJoint='',
                 useMetacarpalJoint=False):
        """
        Make general Limb
        :param spineRig: instance
        :param clavicleJnt: str
        :param scapulaJoint: str
        :param limbJoints: list(str)
        :param topFngJoints: list(str)
        :param spineDriverJoint: str
        :param useMetacarpalJoint: bool
        :return: instance, limbRig
        """
        limbRig = limb.Limb(limbJoints=limbJoints, topFingerJoints=topFngJoints, clavicleJoint=clavicleJnt,
                            scapulaJnt=scapulaJoint,
                            baseRig=self.baseModule, useMetacarpalJoint=useMetacarpalJoint)

        if clavicleJnt:
            pm.parentConstraint(spineDriverJoint, limbRig.getModuleDict()['baseAttachGrp'], mo=1)
        elif scapulaJoint:
            pm.parentConstraint(spineDriverJoint, limbRig.getModuleDict()['baseAttachGrp'], mo=1)
        else:
            pm.parentConstraint(spineDriverJoint, limbRig.getModuleDict()['baseAttachGrp'], mo=1)

        pm.parentConstraint(spineRig.getModuleDict()['bodyCtrl'].C, limbRig.getModuleDict()['bodyAttachGrp'], mo=1)

        return limbRig


class HumanoidRig(BaseRig):
    """
    Rig
    """

    def __init__(self, characterName='new',
                 model_filePath='', buildScene_filePath='',
                 sceneScale=1,
                 rootJnt='rootJA_JNT',
                 headJnt='headJA_JNT',
                 loadSkinCluster=True,
                 doProxyGeo=True,
                 doSpine=True,
                 doNeck=True,
                 doTail=False, doDynamicTail=False,
                 doStretchy=False,
                 doFlexyplane=False,
                 goToTPose=True
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
        :param doDynamicTail: bool
        :param goToTPose: bool
        """

        self.rootJnt = rootJnt
        self.headJnt = headJnt

        self.doSpine = doSpine
        self.doNeck = doNeck
        self.doTail = doTail
        self.doDynamicTail = doDynamicTail
        self.doStretchy = doStretchy
        self.doFlexyplane = doFlexyplane
        self.goToTPose = goToTPose

        self.sceneScale = sceneScale

        super(HumanoidRig, self).__init__(characterName, model_filePath, buildScene_filePath, rootJnt, headJnt,
                                          loadSkinCluster, doProxyGeo, goToTPose=goToTPose)

    def rig(self):
        print('-- RIG HUMANOID --')

        if self.goToTPose:
            joint.loadTPose(self.rootJnt)

        if self.doSpine:
            spineJoints = pm.ls('spineJ?_JNT')
            self.spineRig = self.makeSpine(self.rootJnt, spineJoints, self.sceneScale)

        if self.doNeck:
            neckJoints = pm.ls('neckJ?_JNT')
            self.neckRig = self.makeNeck(self.headJnt, neckJoints, self.sceneScale, self.spineRig)

        if self.doSpine and self.doNeck:
            pm.parentConstraint(spineJoints[-1], self.neckRig.getModuleDict()['baseAttachGrp'], mo=1)
            pm.parentConstraint(self.spineRig.getModuleDict()['bodyCtrl'].C,
                                self.neckRig.getModuleDict()['bodyAttachGrp'], mo=1)

        if self.doTail:
            tailJoints = pm.ls('tail*_JNT')
            pelvisJnt = pm.ls(self.rootJnt)[0]
            self.tailRig = self.makeTail(pelvisJnt, tailJoints, self.doDynamicTail, self.sceneScale)

        # left arm
        lClavicleJoint = pm.ls('l_clavicleJA_JNT')[0]
        lScapulaJoint = ''
        lArmJoints = pm.ls('l_armJ?_JNT', 'l_handJA_JNT')
        lTopFngJoints = pm.ls('l_fngThumbJA_JNT', 'l_fngIndexJA_JNT', 'l_fngMiddleJA_JNT', 'l_fngRingJA_JNT',
                              'l_fngPinkyJA_JNT')
        self.lArmRig = self.makeLimb(self.spineRig, lClavicleJoint, lScapulaJoint, lArmJoints, lTopFngJoints,
                                     spineJoints[-1])

        # right arm
        rClavicleJoint = pm.ls('r_clavicleJA_JNT')[0]
        rScapulaJoint = ''
        rArmJoints = pm.ls('r_armJ?_JNT', 'r_handJA_JNT')
        rTopFngJoints = pm.ls('r_fngThumbJA_JNT', 'r_fngIndexJA_JNT', 'r_fngMiddleJA_JNT', 'r_fngRingJA_JNT',
                              'r_fngPinkyJA_JNT')
        self.rArmRig = self.makeLimb(self.spineRig, rClavicleJoint, rScapulaJoint, rArmJoints, rTopFngJoints,
                                     spineJoints[-1])

        # left leg
        lLegJoints = pm.ls('l_legJ?_JNT', 'l_footJA_JNT')
        lTopToeJoints = pm.ls('l_toeThumbJA_JNT', 'l_toeIndexJA_JNT', 'l_toeMiddleJA_JNT', 'l_toeRingJA_JNT',
                              'l_toePinkyJA_JNT')
        self.lLegRig = self.makeLimb(self.spineRig, '', '', lLegJoints, lTopToeJoints, spineJoints[0])

        # right leg
        rLegJoints = pm.ls('r_legJ?_JNT', 'r_footJA_JNT')
        rTopToeJoints = pm.ls('r_toeThumbJA_JNT', 'r_toeIndexJA_JNT', 'r_toeMiddleJA_JNT', 'r_toeRingJA_JNT',
                              'r_toePinkyJA_JNT')
        self.rLegRig = self.makeLimb(self.spineRig, '', '', rLegJoints, rTopToeJoints, spineJoints[0])

        if self.doStretchy:
            stretchyIKChain.StretchyIKChain(self.lArmRig.getMainLimbIK(), self.lArmRig.getMainIKControl().getControl(),
                                            doFlexyplane=self.doFlexyplane)
            stretchyIKChain.StretchyIKChain(self.rArmRig.getMainLimbIK(), self.rArmRig.getMainIKControl().getControl(),
                                            doFlexyplane=self.doFlexyplane)
            stretchyIKChain.StretchyIKChain(self.lLegRig.getMainLimbIK(), self.lLegRig.getMainIKControl().getControl(),
                                            doFlexyplane=self.doFlexyplane)
            stretchyIKChain.StretchyIKChain(self.rLegRig.getMainLimbIK(), self.rLegRig.getMainIKControl().getControl(),
                                            doFlexyplane=self.doFlexyplane)

        # install IKFK Switch
        ikfkSwitch.installIKFK(
            [self.lArmRig.getMainLimbIK(), self.rArmRig.getMainLimbIK(), self.lLegRig.getMainLimbIK(),
             self.rLegRig.getMainLimbIK()])


if __name__ == "__main__":
    pass

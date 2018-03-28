"""
leg @ rig
"""

import pymel.core as pm

from mayaLib.rigLib.base import module
from mayaLib.rigLib.base import control

from mayaLib.rigLib.utils import joint
from mayaLib.rigLib.utils import name
from mayaLib.rigLib.utils import scapula
from mayaLib.rigLib.utils import footRoll
from mayaLib.rigLib.utils import poleVector
from mayaLib.rigLib.utils import ikfkSwitch


class Limb():
    def __init__(self,
                 limbJoints,
                 topFingerJoints,
                 scapulaJnt='',
                 doFK=True,
                 doIK=True,
                 prefix=None,
                 rigScale=1.0,
                 baseRig=None):

        """
        :param limbJoints: list( str ), shoulder - elbow - hand - toe - end toe
        :param topFingerJoints: list( str ), top metacarpal toe joints
        :param scapulaJnt: str, optional, scapula joint, parent of top leg joint
        :param doFK: bool, do FK controls
        :param doIK: bool, do IK controls
        :param prefix: str, prefix to name new objects
        :param rigScale: float, scale factor for size of controls
        :param baseRig: baseRig: instance of base.module.Base class
        :return: dictionary with rig module objects
        """
        # :param pvLocator: str, reference locator for position of Pole Vector control

        # prefix
        if not prefix:
            prefix = name.removeSuffix(limbJoints[0])

        # make rig module
        rigmodule = module.Module(prefix=prefix, baseObj=baseRig)

        # make attach groups
        bodyAttachGrp = pm.group(n=prefix + 'BodyAttach_GRP', em=1, p=rigmodule.partsGrp)
        baseAttachGrp = pm.group(n=prefix + 'BaseAttach_GRP', em=1, p=rigmodule.partsGrp)

        self.rigmodule = rigmodule
        self.baseAttachGrp = baseAttachGrp
        self.bodyAttachGrp = bodyAttachGrp

        if doFK:
            self.makeFK(limbJoints, topFingerJoints, rigScale, rigmodule)

        if doIK:
            ikHandle = self.makeIK(limbJoints, topFingerJoints, rigScale, rigmodule)
            self.makePoleVector(ikHandle, rigScale, rigmodule)

        if doFK and doIK:
            # IK/FK switch
            pass

        # check scapula
        if scapulaJnt:
            if limbJoints[0].getParent() == scapulaJnt:
                # simple scapula
                self.makeSimpleScapula(prefix, limbJoints, scapulaJnt, rigScale, rigmodule)
            else:
                # dynamic scapula
                self.makeDynamicScapula(limbJoints)

        ################################## OOK --------

        # make controls
        footCtrl = control.Control(prefix=prefix + 'Foot', translateTo=limbJoints[2], scale=rigScale * 3,
                                   parent=rigmodule.controlsGrp, shape='circleY')

        ballCtrl = control.Control(prefix=prefix + 'Ball', translateTo=limbJoints[3], rotateTo=limbJoints[3],
                                   scale=rigScale * 2, parent=footCtrl.C, shape='circleZ')

        toeIkControls = []

        for topToeJnt in topFingerJoints:
            toePrefix = name.removeSuffix(topToeJnt)[:-1]
            toeEndJnt = pm.listRelatives(topToeJnt, ad=1, type='joint')[0]

            toeIkCtrl = control.Control(prefix=toePrefix, translateTo=toeEndJnt, scale=rigScale,
                                        parent=footCtrl.C, shape='circleY')

            toeIkControls.append(toeIkCtrl)

        # make IK handles
        legIk = pm.ikHandle(n=prefix + 'Main_IKH', sol='ikRPsolver', sj=limbJoints[0], ee=limbJoints[2])[0]
        ballIk = pm.ikHandle(n=prefix + 'Ball_IKH', sol='ikSCsolver', sj=limbJoints[2], ee=limbJoints[3])[0]
        mainToeIk = pm.ikHandle(n=prefix + 'MainToe_IKH', sol='ikSCsolver', sj=limbJoints[3], ee=limbJoints[4])[0]

        pm.hide(legIk, ballIk, mainToeIk)

        for i, topToeJnt in enumerate(topFingerJoints):
            toePrefix = name.removeSuffix(topToeJnt)[:-1]
            toeJoints = joint.listHierarchy(topToeJnt)

            toeIk = pm.ikHandle(n=toePrefix + '_IKH', sol='ikSCsolver', sj=toeJoints[1], ee=toeJoints[-1])[0]
            pm.hide(toeIk)
            pm.parent(toeIk, toeIkControls[i].C)


        # attach objects to controls
        pm.parent(legIk, ballCtrl.C)
        pm.parent(ballIk, mainToeIk, footCtrl.C)


    def getModuleDict(self):
        return {'module': self.rigmodule, 'baseAttachGrp': self.baseAttachGrp, 'bodyAttachGrp': self.bodyAttachGrp}

    def makeSimpleScapula(self, prefix, limbJoints, scapulaJnt, rigScale, rigmodule):
        scapulaCtrl = control.Control(prefix=prefix + 'Scapula', translateTo=scapulaJnt, rotateTo=scapulaJnt,
                                      scale=rigScale * 3, parent=rigmodule.controlsGrp, shape='sphere',
                                      lockChannels=['ty', 'rx', 'rz', 's', 'v'])
        scapulaIk = pm.ikHandle(n=prefix + 'Scapula_IKH', sol='ikSCsolver', sj=scapulaJnt, ee=limbJoints[0])[0]
        pm.hide(scapulaIk)
        pm.parentConstraint(self.baseAttachGrp, scapulaCtrl.Off, mo=1)
        pm.parent(scapulaIk, scapulaCtrl.C)
        pm.pointConstraint(scapulaCtrl.C, scapulaJnt)

    def makeDynamicScapula(self, limbJoints, rigmodule):
        spineJnt = limbJoints[0].getParent().getParent()
        clavicleJnt = limbJoints[0].getParent()
        shoulderList = clavicleJnt.getChildren(type='joint')
        scapulaShoulder_jnt = None
        for jnt in shoulderList:
            if 'scapula' in jnt.name():
                scapulaShoulder_jnt = jnt
        if scapulaShoulder_jnt:
            scapulaInstance = scapula.Scapula(spineJnt, limbJoints[0], scapulaShoulder_jnt)
            pm.parent(scapulaInstance.getScapulaGrp(), rigmodule.partsGrp)

    def makeFK(self, limbJoints, topFingerJoints, rigScale, rigmodule):
        """
        Do FK Arm/Leg, Metacarpal and Finger/Toe ctrl
        :param limbJoints: list(str), Arm/leg joints
        :param topFingerJoints: list(str), Metacarpal joints
        :param rigScale: float
        :param rigmodule: dict
        :return:
        """

        limbCtrlInstanceList = []

        # Arm/Leg
        for jnt in limbJoints:
            prefix = name.removeSuffix(jnt.name())

            parent = rigmodule.controlsGrp
            if len(limbCtrlInstanceList) > 0:
                parent = limbCtrlInstanceList[-1].C

            ctrl = control.Control(prefix=prefix, translateTo=jnt, rotateTo=jnt, scale=rigScale * 3,
                            parent=parent, shape='circleY')

            pm.orientConstraint(ctrl.getControl(), jnt)
            limbCtrlInstanceList.append(ctrl)

        # Hand/Foot
        for topJntList in topFingerJoints:
            fnjJntList = joint.listHierarchy(topJntList, withEndJoints=False)
            #fingerJointList.extend(fnjJntList)

            fingerJointList = []
            for jnt in fnjJntList:
                prefix = name.removeSuffix(jnt.name())

                parent = limbCtrlInstanceList[-1].C
                if len(fingerJointList) > 0:
                    parent = fingerJointList[-1].C

                ctrl = control.Control(prefix=prefix, translateTo=jnt, rotateTo=jnt, scale=rigScale * 1.5,
                                       parent=parent, shape='circleY')

                pm.orientConstraint(ctrl.getControl(), jnt)
                fingerJointList.append(ctrl)
                

    def makePoleVector(self, ikHandle, rigScale, rigmodule):
        prefix = name.removeSuffix(ikHandle.name())
        pvInstance = poleVector.PoleVector(ikHandle)
        poleVectorLoc, poleVectorGrp = pvInstance.getPoleVector()
        pm.parent(poleVectorGrp, rigmodule.partsNoTransGrp)

        poleVectorCtrl = control.Control(prefix=prefix + 'PV', translateTo=poleVectorLoc, scale=rigScale,
                                         parent=rigmodule.controlsGrp, shape='sphere')
        pm.parentConstraint(self.bodyAttachGrp, poleVectorCtrl.Off, mo=1)
        pm.parentConstraint(poleVectorCtrl.getControl(), poleVectorLoc)

        # make pole vector connection line
        elbowJnt = ikHandle.getJointList()[1]
        pvLinePos1 = pm.xform(elbowJnt, q=1, t=1, ws=1)
        pvLinePos2 = pm.xform(poleVectorLoc, q=1, t=1, ws=1)
        poleVectorCrv = pm.curve(n=prefix + 'Pv_CRV', d=1, p=[pvLinePos1, pvLinePos2])
        pm.cluster(poleVectorCrv + '.cv[0]', n=prefix + 'Pv1_CLS', wn=[elbowJnt, elbowJnt], bs=True)
        pm.cluster(poleVectorCrv + '.cv[1]', n=prefix + 'Pv2_CLS', wn=[poleVectorCtrl.C, poleVectorCtrl.C], bs=True)
        pm.parent(poleVectorCrv, rigmodule.controlsGrp)
        pm.setAttr(poleVectorCrv + '.template', 1)
        pm.setAttr(poleVectorCrv + '.it', 0)


    def makeIK(self, limbJoints, topFingerJoints, rigScale, rigmodule):
        """
        Do IK Arm/Leg, Metacarpal and Finger/Toe ctrl
        :param limbJoints: list(str), Arm/leg joints
        :param topFingerJoints: list(str), Metacarpal joints
        :param rigScale: float
        :param rigmodule: dict
        :return:
        """

        metacarpalJointList = topFingerJoints
        topFngJntList = []
        for topJntList in metacarpalJointList:
            fnjJntList = joint.listHierarchy(topJntList, withEndJoints=False)[1:]
            topFngJntList.extend(fnjJntList)

        footRoolInstance = footRoll.FootRoll(limbJoints[0], limbJoints[2], topFingerJoints, topFngJntList)
        footRollGrpList = footRoolInstance.getGroupList()

        return footRoolInstance.getLimbIK()

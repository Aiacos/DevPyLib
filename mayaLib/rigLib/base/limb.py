"""
leg @ rig
"""

import pymel.core as pm

from mayaLib.rigLib.base import module
from mayaLib.rigLib.base import control

from mayaLib.rigLib.utils import common
from mayaLib.rigLib.utils import util
from mayaLib.rigLib.utils import joint
from mayaLib.rigLib.utils import name
from mayaLib.rigLib.utils import scapula
from mayaLib.rigLib.utils import footRoll
from mayaLib.rigLib.utils import poleVector
from mayaLib.rigLib.utils import spaces
from mayaLib.rigLib.utils import attributes


class Limb():
    def __init__(self,
                 limbJoints,
                 topFingerJoints,
                 clavicleJoint='',
                 scapulaJnt='',
                 visibilityIKFKCtrl='ikfk_CTRL',
                 doFK=True,
                 doIK=True,
                 useMetacarpalJoint=False,
                 doSmartFootRool=True,
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
            fkLimbCtrls, fkLimbCnst, fkHandsFeetCtrls, fkHandsFeetCnst = self.makeFK(limbJoints, topFingerJoints,
                                                                                     rigScale, rigmodule)

        if doIK:
            mainIKCtrl, ikHandle, fngCtrls, fngIKs, ballIKs, handIKOrientCnst = self.makeIK(limbJoints, topFingerJoints,
                                                                          rigScale, rigmodule, useMetacarpalJoint)
            poleVectorCtrl, poleVectorLoc = self.makePoleVector(ikHandle, mainIKCtrl.getControl(), rigScale, rigmodule)

        if doFK and doIK:
            # IK/FK switch
            if visibilityIKFKCtrl:
                IKFKCtrl = pm.ls(visibilityIKFKCtrl)[0]
                self.switchIKFK(prefix, IKFKCtrl,
                                fkLimbCtrls, fkLimbCnst, fkHandsFeetCtrls, fkHandsFeetCnst,
                                mainIKCtrl, ikHandle, fngCtrls, fngIKs, ballIKs, poleVectorCtrl, handIKOrientCnst)

        # clavicle
        if clavicleJoint != '' and pm.objExists(clavicleJoint):
            clavicleCtrl = self.makeClavicle(prefix, limbJoints, clavicleJoint, rigScale, rigmodule)
            pm.parentConstraint(clavicleCtrl.getControl(), fkLimbCtrls[0].getTop(), mo=1)
        else:
            pm.parentConstraint(self.baseAttachGrp, fkLimbCtrls[0].getTop(), mo=1)

        # scapula
        if scapulaJnt != '' and pm.objExists(scapulaJnt):
            scpJnt = pm.ls(limbJoints)[0].getParent()
            scapulaCtrl = None
            if scpJnt.name() == pm.ls(scapulaJnt)[0].name():
                # simple scapula
                scapulaCtrl = self.makeSimpleScapula(prefix, limbJoints, scapulaJnt, rigScale, rigmodule)
            else:
                # dynamic scapula
                self.makeDynamicScapula(limbJoints, rigmodule)

            # constriant FK limb
            if scapulaCtrl:
                pm.parentConstraint(scapulaCtrl.getControl(), fkLimbCtrls[0].getTop(), mo=1)

        self.limbIK = ikHandle

    def getMainLimbIK(self):
        return self.limbIK

    def getModuleDict(self):
        return {'module': self.rigmodule, 'baseAttachGrp': self.baseAttachGrp, 'bodyAttachGrp': self.bodyAttachGrp}

    def switchIKFK(self, prefix, visCtrl,
                   fkLimbCtrls, fkLimbCnst, fkHandsFeetCtrls, fkHandsFeetCnst,
                   mainIKCtrl, ikHandle, fngCtrls, fngIKs, ballIKs, poleVectorCtrl, handIKOrientCnst):

        if not pm.objExists('switchIKFK_LOC'):
            switchLoc = pm.spaceLocator(n='switchIKFK_LOC')
            pm.parent(switchLoc, 'rig_GRP')
            pm.hide(switchLoc)
            util.lock_and_hide_all(switchLoc)
        else:
            switchLoc = pm.ls('switchIKFK_LOC')[0]

        pm.addAttr(switchLoc, longName=prefix, attributeType='double', defaultValue=0, minValue=0, maxValue=1, k=True)
        pm.addAttr(visCtrl, longName=prefix, attributeType='double', defaultValue=0, minValue=0, maxValue=1, k=True)
        ctrlAttr = prefix#.lower()
        pm.connectAttr(visCtrl + '.' + ctrlAttr, switchLoc + '.' + ctrlAttr)

        reverseNode = pm.shadingNode('reverse', asUtility=True, n=prefix + 'ReverseNode')
        pm.connectAttr(switchLoc + '.' + ctrlAttr, reverseNode.inputX)

        # connect IK
        pm.connectAttr(reverseNode.outputX, mainIKCtrl.getTop().visibility)
        pm.connectAttr(reverseNode.outputX, ikHandle.ikBlend)
        IKcnstAttr = pm.listConnections(handIKOrientCnst.target[1].targetWeight, p=True, s=True)[0]
        pm.connectAttr(reverseNode.outputX, IKcnstAttr)

        for ctrl in fngCtrls[0]:
            pm.connectAttr(reverseNode.outputX, ctrl.getTop().visibility)
        for ctrl in fngCtrls[1]:
            pm.connectAttr(reverseNode.outputX, ctrl.getTop().visibility)

        for ik in fngIKs:
            pm.connectAttr(reverseNode.outputX, ik.ikBlend)
        for ik in ballIKs:
            pm.connectAttr(reverseNode.outputX, ik.ikBlend)

        pm.connectAttr(reverseNode.outputX, poleVectorCtrl.getTop().visibility)

        # connect FK
        for ctrl in fkLimbCtrls:
            pm.connectAttr(switchLoc + '.' + ctrlAttr, ctrl.getTop().visibility)
        for cnst in fkLimbCnst:
            attr = pm.listConnections(cnst.target[0].targetWeight, p=True, s=True)[0]
            pm.connectAttr(switchLoc + '.' + ctrlAttr, attr)

        for ctrl in fkHandsFeetCtrls:
            pm.connectAttr(switchLoc + '.' + ctrlAttr, ctrl.getTop().visibility)
        for cnst in fkHandsFeetCnst:
            attr = pm.listConnections(cnst.target[0].targetWeight, p=True, s=True)[0]
            pm.connectAttr(switchLoc + '.' + ctrlAttr, attr)

    def makeSimpleScapula(self, prefix, limbJoints, scapulaJnt, rigScale, rigmodule):
        scapulaCtrl = control.Control(prefix=prefix + 'Scapula', translateTo=scapulaJnt, rotateTo=scapulaJnt,
                                      scale=rigScale * 3, parent=rigmodule.controlsGrp, shape='sphere',
                                      lockChannels=['ty', 'rx', 'rz', 's', 'v'])
        scapulaIk = pm.ikHandle(n=prefix + 'Scapula_IKH', sol='ikSCsolver', sj=scapulaJnt, ee=limbJoints[0])[0]
        pm.hide(scapulaIk)
        pm.parentConstraint(self.baseAttachGrp, scapulaCtrl.Off, mo=1)
        pm.parent(scapulaIk, scapulaCtrl.C)
        pm.pointConstraint(scapulaCtrl.C, scapulaJnt)

        return scapulaCtrl

    def makeClavicle(self, prefix, limbJoints, scapulaJnt, rigScale, rigmodule):
        clavicleCtrl = control.Control(prefix=prefix + 'Clavicle', translateTo=scapulaJnt, rotateTo=scapulaJnt,
                                      scale=rigScale * 3, parent=rigmodule.controlsGrp, shape='sphere',
                                      lockChannels=['t', 's', 'v'])
        scapulaIk = pm.ikHandle(n=prefix + 'Scapula_IKH', sol='ikSCsolver', sj=scapulaJnt, ee=limbJoints[0])[0]
        pm.hide(scapulaIk)
        pm.parentConstraint(self.baseAttachGrp, clavicleCtrl.Off, mo=1)
        pm.parent(scapulaIk, clavicleCtrl.C)
        pm.pointConstraint(clavicleCtrl.C, scapulaJnt)

        return clavicleCtrl

    def makeDynamicScapula(self, limbJoints, rigmodule):
        limbJoints = pm.ls(limbJoints)
        spineJnt = limbJoints[0].getParent().getParent()
        clavicleJnt = limbJoints[0].getParent()
        shoulderList = clavicleJnt.getChildren(type='joint')
        scapulaShoulder_jnt = None
        for jnt in shoulderList:
            if 'scapula' in jnt:
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
        handFeetCtrlInstanceList = []

        limbCtrlConstraintList = []
        handFeetCtrlConstraintList = []

        # Arm/Leg
        for jnt in limbJoints:
            prefix = name.removeSuffix(jnt)

            parent = rigmodule.controlsGrp
            if len(limbCtrlInstanceList) > 0:
                parent = limbCtrlInstanceList[-1].C

            ctrl = control.Control(prefix=prefix, translateTo=jnt, rotateTo=jnt,
                                   scale=rigScale * 3, parent=parent, shape='circleX')

            orientCnst = pm.orientConstraint(ctrl.getControl(), jnt, mo=True)

            limbCtrlConstraintList.append(orientCnst)
            limbCtrlInstanceList.append(ctrl)

        # Hand/Foot
        for topJntList in topFingerJoints:
            fnjJntList = joint.listHierarchy(topJntList, withEndJoints=False)

            fingerJointList = []
            for jnt in fnjJntList:
                prefix = name.removeSuffix(jnt)

                parent = limbCtrlInstanceList[-1].C
                if len(fingerJointList) > 0:
                    parent = fingerJointList[-1].C

                ctrl = control.Control(prefix=prefix, translateTo=jnt, rotateTo=jnt,
                                       scale=rigScale * 1, parent=parent, shape='circleX')

                orientCnst = pm.orientConstraint(ctrl.getControl(), jnt)
                fingerJointList.append(ctrl)
                handFeetCtrlConstraintList.append(orientCnst)

            handFeetCtrlInstanceList.extend(fingerJointList)

        return limbCtrlInstanceList, limbCtrlConstraintList, handFeetCtrlInstanceList, handFeetCtrlConstraintList

    def makePoleVector(self, ikHandle, autoElbowCtrl, rigScale, rigmodule):
        prefix = name.removeSuffix(ikHandle)
        pvInstance = poleVector.PoleVector(ikHandle)
        poleVectorLoc, poleVectorGrp = pvInstance.getPoleVector()
        pm.parent(poleVectorGrp, rigmodule.partsNoTransGrp)

        poleVectorCtrl = control.Control(prefix=prefix + 'PV', translateTo=poleVectorLoc,
                                         scale=rigScale, parent=rigmodule.controlsGrp, shape='sphere')

        #pm.parentConstraint(self.bodyAttachGrp, poleVectorCtrl.Off, mo=1)
        spaces.spaces([self.bodyAttachGrp, autoElbowCtrl], ['body', 'control'], poleVectorCtrl.Off, poleVectorCtrl.getControl())

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

        return poleVectorCtrl, poleVectorLoc

    def makeIK(self, limbJoints, topFingerJoints, rigScale, rigmodule, useMetacarpalJoint=False, smartFootRoll=True):
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
        endFngJntList = []
        for mtJnt in metacarpalJointList:
            if useMetacarpalJoint:
                fngJnt = pm.listRelatives(mtJnt, type='joint', children=True)[0]
            else:
                fngJnt = mtJnt

            fngEndJnt = joint.listHierarchy(mtJnt, withEndJoints=True)[-1]
            topFngJntList.append(fngJnt)
            endFngJntList.append(fngEndJnt)

        footRoolInstance = footRoll.FootRoll(limbJoints[0], limbJoints[2], topFngJntList, endFngJntList)
        footRollGrpList = footRoolInstance.getGroupList()
        pm.parent(footRollGrpList[-1], rigmodule.partsNoTransGrp)

        prefix = name.removeSuffix(limbJoints[2])

        # make controls
        mainIKCtrl = control.Control(prefix=prefix + 'IK', translateTo=limbJoints[2], rotateTo=limbJoints[2],
                                     scale=rigScale * 3, parent=rigmodule.controlsGrp, shape='circleY')

        midFngIKIndex = int(round(len(footRoolInstance.getIkFingerList()) / 2.0)) - 1
        midFngJnt = footRoolInstance.getIkFingerList()[midFngIKIndex].getJointList()[0]
        ballCtrl = control.Control(prefix=prefix + 'BallIK', translateTo=midFngJnt, rotateTo=midFngJnt,
                                   scale=rigScale * 2, parent=mainIKCtrl.C, shape='circleZ')

        toeIkControls = []
        for topToeJnt in topFingerJoints:
            toePrefix = name.removeSuffix(topToeJnt)
            toeEndJnt = pm.listRelatives(topToeJnt, ad=1, type='joint')[0]

            toeIkCtrl = control.Control(prefix=toePrefix, translateTo=toeEndJnt, scale=rigScale,
                                        parent=mainIKCtrl.C, shape='circleY')

            toeIkControls.append(toeIkCtrl)

        # constraint IK
        for i, toeIK in enumerate(footRoolInstance.getIkFingerList()):
            pm.parentConstraint(toeIkControls[i].C, toeIK)

        pm.parentConstraint(mainIKCtrl.C, footRollGrpList[-1], mo=True)
        #pm.parentConstraint(ballCtrl.C, footRollGrpList[0], mo=True)
        handIKOrientContraint = pm.orientConstraint(mainIKCtrl.C, limbJoints[2], mo=True)

        ballRollGrp = footRollGrpList[0]
        toeTapGrp = footRollGrpList[1]
        tippyToeGrp = footRollGrpList[2]
        frontRollGrp, backRollGrp, innerRollGrp, outerRollGrp = footRollGrpList[3:-1]
        if smartFootRoll and frontRollGrp and ballRollGrp and innerRollGrp and outerRollGrp:
            rollAttr = attributes.addFloatAttribute(mainIKCtrl.getControl(), 'roll', defaultValue=0, keyable=True, minValue=-120, maxValue=120)
            bendLimitAttr = attributes.addFloatAttribute(mainIKCtrl.getControl(), 'bendLimitAngle', defaultValue=45, keyable=False)
            straightAngleAttr = attributes.addFloatAttribute(mainIKCtrl.getControl(), 'toeStraightAngle', defaultValue=70, keyable=False)

            heelClampNode = pm.shadingNode('clamp', asUtility=True, n=prefix+'_heelRotClamp')
            pm.connectAttr(rollAttr, heelClampNode.inputR)
            heelClampNode.minR.set(-90)
            pm.connectAttr(heelClampNode.outputR, backRollGrp.rotateX)

            ballClampNode = pm.shadingNode('clamp', asUtility=True, n=prefix + '_zeroToBendClamp')
            pm.connectAttr(rollAttr, ballClampNode.inputR)
            #heelClampNode.maxR.set(90)
            #pm.connectAttr(ballClampNode.outputR, ballRollGrp.rotateX)

            bendToStraightClampNode = pm.shadingNode('clamp', asUtility=True, n=prefix + '_bendToStraightClamp')
            pm.connectAttr(bendLimitAttr, bendToStraightClampNode.minR)
            pm.connectAttr(straightAngleAttr, bendToStraightClampNode.maxR)
            pm.connectAttr(rollAttr, bendToStraightClampNode.inputR)

            bendToStraightSetRangeNode = pm.shadingNode('setRange', asUtility=True, n=prefix + '_bendToStraightPercent')
            pm.connectAttr(bendToStraightClampNode.minR, bendToStraightSetRangeNode.oldMinX)
            pm.connectAttr(bendToStraightClampNode.maxR, bendToStraightSetRangeNode.oldMaxX)
            bendToStraightSetRangeNode.maxX.set(1)
            pm.connectAttr(bendToStraightClampNode.inputR, bendToStraightSetRangeNode.valueX)

            rollMultDivNode = pm.shadingNode('multiplyDivide', asUtility=True, n=prefix + '_rollMultDiv')
            pm.connectAttr(bendToStraightSetRangeNode.outValueX, rollMultDivNode.input1X)
            pm.connectAttr(bendToStraightClampNode.inputR, rollMultDivNode.input2X)
            pm.connectAttr(rollMultDivNode.outputX, tippyToeGrp.rotateX)

            pm.connectAttr(bendLimitAttr, ballClampNode.maxR)
            zeroToBendSetRangeNode = pm.shadingNode('setRange', asUtility=True, n=prefix + '_zeroToBendPercent')
            pm.connectAttr(ballClampNode.minR, zeroToBendSetRangeNode.oldMinX)
            pm.connectAttr(ballClampNode.maxR, zeroToBendSetRangeNode.oldMaxX)
            zeroToBendSetRangeNode.maxX.set(1)
            pm.connectAttr(ballClampNode.inputR, zeroToBendSetRangeNode.valueX)

            invertPercentNode = pm.shadingNode('plusMinusAverage', asUtility=True, n=prefix + '_invertPercent')
            invertPercentNode.input1D[0].set(1)
            invertPercentNode.input1D[1].set(1)
            pm.connectAttr(bendToStraightSetRangeNode.outValueX, invertPercentNode.input1D[1])
            invertPercentNode.operation.set(2)

            ballPercentMultDivNode = pm.shadingNode('multiplyDivide', asUtility=True, n=prefix + '_ballPercentMultDiv')
            pm.connectAttr(zeroToBendSetRangeNode.outValueX, ballPercentMultDivNode.input1X)
            pm.connectAttr(invertPercentNode.output1D, ballPercentMultDivNode.input2X)

            ballRollMultDivNode = pm.shadingNode('multiplyDivide', asUtility=True, n=prefix + '_ballRollMultDiv')
            pm.connectAttr(ballPercentMultDivNode.outputX, ballRollMultDivNode.input1X)
            pm.connectAttr(rollAttr, ballRollMultDivNode.input2X)

            pm.connectAttr(ballRollMultDivNode.outputX, ballRollGrp.rotateX)

            # Tilt
            tiltAttr = attributes.addFloatAttribute(mainIKCtrl.getControl(), 'tilt', defaultValue=0, keyable=True, minValue=-90, maxValue=90)
            common.setDrivenKey(tiltAttr, [-90, 0, 90], innerRollGrp.rotateZ, [90, 0, 0])
            common.setDrivenKey(tiltAttr, [-90, 0, 90], outerRollGrp.rotateZ, [0, 0, -90])

            # lean
            leanAttr = attributes.addFloatAttribute(mainIKCtrl.getControl(), 'lean', defaultValue=0, keyable=True, minValue=-90, maxValue=90)
            pm.connectAttr(leanAttr, ballRollGrp.rotateZ)

            # toeSpin
            toeSpinAttr = attributes.addFloatAttribute(mainIKCtrl.getControl(), 'toeSpin', defaultValue=0, keyable=True, minValue=-90, maxValue=90)
            pm.connectAttr(toeSpinAttr, tippyToeGrp.rotateY)
            tippyToeGrp.rotateOrder.set(2)

            # toeWiggle
            toeWiggleAttr = attributes.addFloatAttribute(mainIKCtrl.getControl(), 'toeWiggle', defaultValue=0, keyable=True, minValue=-90, maxValue=90)
            pm.connectAttr(toeWiggleAttr, toeTapGrp.rotateX)

        return mainIKCtrl, footRoolInstance.getLimbIK(), [[ballCtrl], toeIkControls], footRoolInstance.getIkFingerList(), footRoolInstance.getIkBallList(), handIKOrientContraint

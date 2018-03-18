"""
leg @ rig
"""

import pymel.core as pm

from mayaLib.rigLib.base import module
from mayaLib.rigLib.base import control

from mayaLib.rigLib.utils import joint
from mayaLib.rigLib.utils import name


class Limb():
    def __init__(self,
                 legJoints,
                 topToeJoints,
                 pvLocator,
                 scapulaJnt='',
                 prefix='l_leg',
                 rigScale=1.0,
                 baseRig=None):

        """
        :param legJoints: list( str ), shoulder - elbow - hand - toe - end toe
        :param topToeJoints: list( str ), top metacarpal toe joints
        :param pvLocator: str, reference locator for position of Pole Vector control
        :param scapulaJnt: str, optional, scapula joint, parent of top leg joint
        :param prefix: str, prefix to name new objects
        :param rigScale: float, scale factor for size of controls
        :param baseRig: baseRig: instance of base.module.Base class
        :return: dictionary with rig module objects
        """

        # make rig module
        rigmodule = module.Module(prefix=prefix, baseObj=baseRig)

        # make attach groups
        bodyAttachGrp = pm.group(n=prefix + 'BodyAttach_GRP', em=1, p=rigmodule.partsGrp)
        baseAttachGrp = pm.group(n=prefix + 'BaseAttach_GRP', em=1, p=rigmodule.partsGrp)

        # make controls
        if scapulaJnt:
            scapulaCtrl = control.Control(prefix=prefix + 'Scapula', translateTo=scapulaJnt, rotateTo=scapulaJnt,
                                          scale=rigScale * 3, parent=rigmodule.controlsGrp, shape='sphere',
                                          lockChannels=['ty', 'rx', 'rz', 's', 'v'])

        footCtrl = control.Control(prefix=prefix + 'Foot', translateTo=legJoints[2], scale=rigScale * 3,
                                   parent=rigmodule.controlsGrp, shape='circleY')

        ballCtrl = control.Control(prefix=prefix + 'Ball', translateTo=legJoints[3], rotateTo=legJoints[3],
                                   scale=rigScale * 2, parent=footCtrl.C, shape='circleZ')

        poleVectorCtrl = control.Control(prefix=prefix + 'PV', translateTo=pvLocator, scale=rigScale,
                                         parent=rigmodule.controlsGrp, shape='sphere')

        toeIkControls = []

        for topToeJnt in topToeJoints:
            toePrefix = name.removeSuffix(topToeJnt)[:-1]
            toeEndJnt = pm.listRelatives(topToeJnt, ad=1, type='joint')[0]

            toeIkCtrl = control.Control(prefix=toePrefix, translateTo=toeEndJnt, scale=rigScale,
                                        parent=footCtrl.C, shape='circleY')

            toeIkControls.append(toeIkCtrl)

        # make IK handles
        if scapulaJnt:
            scapulaIk = pm.ikHandle(n=prefix + 'Scapula_IKH', sol='ikSCsolver', sj=scapulaJnt, ee=legJoints[0])[0]
            pm.hide(scapulaIk)

        legIk = pm.ikHandle(n=prefix + 'Main_IKH', sol='ikRPsolver', sj=legJoints[0], ee=legJoints[2])[0]
        ballIk = pm.ikHandle(n=prefix + 'Ball_IKH', sol='ikSCsolver', sj=legJoints[2], ee=legJoints[3])[0]
        mainToeIk = pm.ikHandle(n=prefix + 'MainToe_IKH', sol='ikSCsolver', sj=legJoints[3], ee=legJoints[4])[0]

        pm.hide(legIk, ballIk, mainToeIk)

        for i, topToeJnt in enumerate(topToeJoints):
            toePrefix = name.removeSuffix(topToeJnt)[:-1]
            toeJoints = joint.listHierarchy(topToeJnt)

            toeIk = pm.ikHandle(n=toePrefix + '_IKH', sol='ikSCsolver', sj=toeJoints[1], ee=toeJoints[-1])[0]
            pm.hide(toeIk)
            pm.parent(toeIk, toeIkControls[i].C)

        # attach controls
        pm.parentConstraint(bodyAttachGrp, poleVectorCtrl.Off, mo=1)

        if scapulaJnt:
            pm.parentConstraint(baseAttachGrp, scapulaCtrl.Off, mo=1)

        # attach objects to controls
        pm.parent(legIk, ballCtrl.C)
        pm.parent(ballIk, mainToeIk, footCtrl.C)

        pm.poleVectorConstraint(poleVectorCtrl.C, legIk)

        if scapulaJnt:
            pm.parent(scapulaIk, scapulaCtrl.C)
            pm.pointConstraint(scapulaCtrl.C, scapulaJnt)

        # make pole vector connection line
        pvLinePos1 = pm.xform(legJoints[1], q=1, t=1, ws=1)
        pvLinePos2 = pm.xform(pvLocator, q=1, t=1, ws=1)
        poleVectorCrv = pm.curve(n=prefix + 'Pv_CRV', d=1, p=[pvLinePos1, pvLinePos2])
        pm.cluster(poleVectorCrv + '.cv[0]', n=prefix + 'Pv1_CLS', wn=[legJoints[1], legJoints[1]], bs=True)
        pm.cluster(poleVectorCrv + '.cv[1]', n=prefix + 'Pv2_CLS', wn=[poleVectorCtrl.C, poleVectorCtrl.C], bs=True)
        pm.parent(poleVectorCrv, rigmodule.controlsGrp)
        pm.setAttr(poleVectorCrv + '.template', 1)
        pm.setAttr(poleVectorCrv + '.it', 0)

        self.rigmodule = rigmodule
        self.baseAttachGrp = baseAttachGrp
        self.bodyAttachGrp = bodyAttachGrp

    def getModuleDict(self):
        return {'module': self.rigmodule, 'baseAttachGrp': self.baseAttachGrp, 'bodyAttachGrp': self.bodyAttachGrp}

    def makeFK(self):
        pass

    def makeIK(self):
        pass

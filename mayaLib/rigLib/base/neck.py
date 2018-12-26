"""
neck @ rig
"""

import pymel.core as pm
from mayaLib.rigLib.base import module
from mayaLib.rigLib.base import control


class Neck():
    def __init__(self,
                 neckJoints,
                 headJnt,
                 #neckCurve,
                 prefix='neck',
                 rigScale=1.0,
                 baseRig=None
                 ):
        """
        :param neckJoints: list( str ), list of neck joints
        :param headJnt: str, head joint at the end of neck joint chain
        :param prefix: str, prefix to name new objects
        :param rigScale: float, scale factor for size of controls
        :param baseRig: instance of base.module.Base class
        :return: dictionary with rig module objects
        """
        # :param neckCurve: str, name of neck cubic curve with 5 CVs matching neck joints

        # make rig module
        self.rigmodule = module.Module(prefix=prefix, baseObj=baseRig)

        # make IK handle
        neckIk, effector, neckCurve = pm.ikHandle(n=prefix + '_IKH', sol='ikSplineSolver', sj=neckJoints[0], ee=neckJoints[-1],
                             createCurve=True, numSpans=2)

        # rename curve
        pm.rename(neckCurve, prefix+'_CRV')

        # make neck curve clusters
        neckCurveCVs = pm.ls(neckCurve + '.cv[*]', fl=1)
        numNeckCVs = len(neckCurveCVs)
        neckCurveClusters = []

        for i in range(numNeckCVs):
            cls = pm.cluster(neckCurveCVs[i], n=prefix + 'Cluster%d' % (i + 1))[1]
            neckCurveClusters.append(cls)

        pm.hide(neckCurveClusters)

        # parent neck curve
        pm.parent(neckCurve, self.rigmodule.partsNoTransGrp)

        # make attach groups
        self.bodyAttachGrp = pm.group(n=prefix + 'BodyAttach_GRP', em=1, p=self.rigmodule.partsGrp)
        self.baseAttachGrp = pm.group(n=prefix + 'BaseAttach_GRP', em=1, p=self.rigmodule.partsGrp)

        pm.delete(pm.pointConstraint(neckJoints[0], self.baseAttachGrp))

        # make controls
        headMainCtrl = control.Control(prefix=prefix + 'HeadMain', translateTo=neckJoints[-1], scale=rigScale * 5,
                                       parent=self.rigmodule.controlsGrp, shape='head')

        headLocalCtrl = control.Control(prefix=prefix + 'HeadLocal', translateTo=headJnt, rotateTo=headJnt,
                                        scale=rigScale * 4, parent=headMainCtrl.C, shape='circleX', lockChannels=['t'])

        middleCtrl = control.Control(prefix=prefix + 'Middle', translateTo=neckCurveClusters[2], rotateTo=neckJoints[2],
                                     scale=rigScale * 4, parent=self.rigmodule.controlsGrp, shape='circleX', lockChannels=['r'])

        # attach controls
        pm.parentConstraint(headMainCtrl.C, self.baseAttachGrp, middleCtrl.Off, sr=['x', 'y', 'z'], mo=1)
        pm.orientConstraint(self.baseAttachGrp, middleCtrl.Off, mo=1)
        pm.parentConstraint(self.bodyAttachGrp, headMainCtrl.Off, mo=1)

        # attach clusters
        pm.parent(neckCurveClusters[3:], headMainCtrl.C)
        pm.parent(neckCurveClusters[2], middleCtrl.C)
        pm.parent(neckCurveClusters[:2], self.baseAttachGrp)

        # attach joints
        pm.orientConstraint(headLocalCtrl.C, headJnt, mo=1)

        pm.hide(neckIk)
        pm.parent(neckIk, self.rigmodule.partsNoTransGrp)

        # setup IK twist
        pm.setAttr(neckIk + '.dTwistControlEnable', 1)
        pm.setAttr(neckIk + '.dWorldUpType', 4)
        pm.connectAttr(headMainCtrl.C + '.worldMatrix[0]', neckIk + '.dWorldUpMatrixEnd')
        pm.connectAttr(self.baseAttachGrp + '.worldMatrix[0]', neckIk + '.dWorldUpMatrix')

    def getModuleDict(self):
        return {'module': self.rigmodule, 'baseAttachGrp': self.baseAttachGrp, 'bodyAttachGrp': self.bodyAttachGrp}

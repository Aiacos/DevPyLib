"""
spine @ rig
"""

import pymel.core as pm
from mayaLib.rigLib.base import module
from mayaLib.rigLib.base import control

class Spine():
    """
    class for building spine
    """

    def __init__(self,
                spineJoints,
                rootJnt,
                prefix='spine',
                rigScale=1.0,
                baseRig=None,
                bodyLocator='',
                chestLocator='',
                pelvisLocator=''
    ):
        """
        :param spineJoints: list( str ), list of 6 spine joints
        :param rootJnt: str, root joint
        :param prefix: str, prefix to name new objects
        :param rigScale: float, scale factor for size of controls
        :param baseRig: instance of base.module.Base class
        :param bodyLocator: str, reference transform for position of body control
        :param chestLocator: str, reference transform for position of chest control
        :param pelvisLocator: str, reference transform for position of pelvis control
        :return: dictionary with rig module objects
        """
        # :param spineCurve: str, name of spine cubic curve with 5 CVs matching first 5 spine joints

        # make rig module
        self.rigmodule = module.Module(prefix=prefix, baseObj=baseRig)

        # control locator reference position
        if bodyLocator == '' or chestLocator == '' or pelvisLocator == '':
            pass
        bodyLocator, chestLocator, pelvisLocator = self.makeControlLocatorReferencePosition(spineJoints)

        # make IK handle
        spineIk, effector, spineCurve = pm.ikHandle(n=prefix + '_IKH', sol='ikSplineSolver', sj=spineJoints[0], ee=spineJoints[-1], # -2
                                                    createCurve=True, numSpans=2)

        # rename curve
        pm.rename(spineCurve, prefix+'_CRV')

        # make spine curve clusters
        spineCurveCVs = pm.ls(spineCurve + '.cv[*]', fl=1)
        numSpineCVs = len(spineCurveCVs)
        spineCurveClusters = []

        for i in range(numSpineCVs):
            cls = pm.cluster(spineCurveCVs[i], n=prefix + 'Cluster%d' % (i + 1))[1]
            spineCurveClusters.append(cls)

        pm.hide(spineCurveClusters)

        # parent spine curve
        pm.parent(spineCurve, self.rigmodule.partsNoTransGrp)

        # make controls
        self.bodyCtrl = control.Control(prefix=prefix + 'Body', translateTo=bodyLocator, rotateTo=spineJoints[-1], scale=rigScale * 4,
                                   parent=self.rigmodule.controlsGrp, shape='spine')

        chestCtrl = control.Control(prefix=prefix + 'Chest', translateTo=chestLocator, rotateTo=spineJoints[-1], scale=rigScale * 6,
                                    parent=self.bodyCtrl.C, shape='chest')

        pelvisCtrl = control.Control(prefix=prefix + 'Pelvis', translateTo=pelvisLocator, scale=rigScale * 6,
                                     parent=self.bodyCtrl.C, shape='hip')

        middleCtrl = control.Control(prefix=prefix + 'Middle', translateTo=spineCurveClusters[2], scale=rigScale * 3,
                                     parent=self.bodyCtrl.C, shape='sphere')

        # attach controls
        pm.parentConstraint(chestCtrl.C, pelvisCtrl.C, middleCtrl.Off, sr=['x', 'y', 'z'], mo=1)

        # attach clusters
        pm.parent(spineCurveClusters[3:], chestCtrl.C)
        pm.parent(spineCurveClusters[2], middleCtrl.C)
        pm.parent(spineCurveClusters[:2], pelvisCtrl.C)

        # attach chest joint
        pm.orientConstraint(chestCtrl.C, spineJoints[-1], mo=1) # -2

        pm.hide(spineIk)
        pm.parent(spineIk, self.rigmodule.partsNoTransGrp)

        # setup IK twist
        pm.setAttr(spineIk + '.dTwistControlEnable', 1)
        pm.setAttr(spineIk + '.dWorldUpType', 4)
        pm.connectAttr(chestCtrl.C + '.worldMatrix[0]', spineIk + '.dWorldUpMatrixEnd')
        pm.connectAttr(pelvisCtrl.C + '.worldMatrix[0]', spineIk + '.dWorldUpMatrix')

        # attach root joint
        pm.parentConstraint(pelvisCtrl.C, rootJnt, mo=1)

        # clean locators
        pm.delete(bodyLocator, chestLocator, pelvisLocator)


    def getModuleDict(self):
        return {'module': self.rigmodule, 'bodyCtrl': self.bodyCtrl}


    def makeControlLocatorReferencePosition(self, spineJoints):
        numJoints = len(spineJoints)
        midJoint = numJoints/2
        bodyLocator = pm.spaceLocator(n='body_LOC')
        chestLocator = pm.spaceLocator(n='chest_LOC')
        pelvisLocator = pm.spaceLocator(n='pelvis_LOC')

        pm.delete(pm.pointConstraint(spineJoints[0], pelvisLocator))
        pm.delete(pm.pointConstraint(spineJoints[-1], chestLocator))
        if numJoints % 2 == 0:
            pm.delete(pm.pointConstraint([spineJoints[midJoint], spineJoints[midJoint + 1]], bodyLocator))
        else:
            pm.delete(pm.pointConstraint([spineJoints[midJoint]], bodyLocator))

        return bodyLocator, chestLocator, pelvisLocator

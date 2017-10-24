__author__ = 'Lorenzo Argentieri'

import pymel.core as pm
from mayaLib.rigLib.utils import util


class IKFKSwitch():
    def __init__(self, ikHandle, forearmMidJnt=False):
        self.joint1 = pm.listConnections(ikHandle, type='joint')[0]
        self.joint2 = self.joint1.outputs(type='joint')[0]

        if forearmMidJnt:
            self.jointMid = self.joint2.outputs(type='joint')[0]
            self.joint3 = self.jointMid.outputs(type='joint')[0]
        else:
            self.joint3 = self.joint2.outputs(type='joint')[0]

        # FK controls
        orientConstraintFK1 = self.joint1.outputs(type='constraint')[0]
        self.joint1FKCtrl = util.getDriverDrivenFromConstraint(orientConstraintFK1)[0][0]

        orientConstraintFK2 = self.joint2.outputs(type='constraint')[0]
        self.joint2FKCtrl = util.getDriverDrivenFromConstraint(orientConstraintFK2)[0][0]

        orientConstraintFK3 = self.joint3.outputs(type='constraint')[0]
        self.joint3FKCtrl = util.getDriverDrivenFromConstraint(orientConstraintFK3)[0][0]

        # IK control
        pointConstraintIK = pm.listConnections(ikHandle, type='constraint')[0]
        self.joint3IKCtrl = util.getDriverDrivenFromConstraint(pointConstraintIK)[0][0]

        poleVectorConstraint = pm.listConnections(ikHandle, type='poleVectorConstraint', et=True)[0]
        self.poleVector = util.getDriverDrivenFromConstraint(poleVectorConstraint)[0][0]

    def toIK(self):
        pm.delete(pm.parentConstraint(self.joint3FKCtrl, self.joint3IKCtrl))
        pm.delete(pm.pointConstraint(self.joint2FKCtrl, self.poleVector))

    def toFK(self):
        pm.delete(pm.orientConstraint(self.joint1, self.joint1FKCtrl))
        pm.delete(pm.orientConstraint(self.joint2, self.joint2FKCtrl))
        pm.delete(pm.orientConstraint(self.joint3, self.joint3FKCtrl))


def ikHandleSearch():
    ikHandleList = pm.ls(type='ikHandle')
    handleLocator = pm.spaceLocator(n='ikHandleCtrl_LOC')
    util.lock_and_hide_all(handleLocator)

    for handle in ikHandleList:
        # add attribute on locator control
        pm.addAttr(handleLocator, ln=handle, k=True, at='enum', en='FK=0:IK=1:')
        # intance switch class

        # add event
        # pm.evalDeferred("pm.deleteUI(button)")


if __name__ == "__main__":
    ikHandleSearch()
    # classeProva = IKFKSwitch('ikHandle1', forearmMidJnt=True)
    # classeProva.toIK()
    # classeProva.toFK()


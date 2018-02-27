__author__ = 'Lorenzo Argentieri'

import inspect
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

        self.ikHandle = ikHandle

    def toIK(self):
        pm.delete(pm.parentConstraint(self.joint3FKCtrl, self.joint3IKCtrl))
        pm.delete(pm.pointConstraint(self.joint2FKCtrl, self.poleVector))

    def toFK(self):
        pm.delete(pm.orientConstraint(self.joint1, self.joint1FKCtrl))
        pm.delete(pm.orientConstraint(self.joint2, self.joint2FKCtrl))
        pm.delete(pm.orientConstraint(self.joint3, self.joint3FKCtrl))

    def switchIKFK(self):
        blend = self.ikHandle.ikBlend.get()
        if blend == 0:
            self.toFK()
        elif blend == 1:
            self.toIK()

    def addScriptJob(self):
        pm.scriptJob(attributeChange=[self.ikHandle.ikBlend, self.switchIKFK])

def installIKFK(ikList):
    classDefinitionString = inspect.getsource(IKFKSwitch)
    utilDefinitionString = inspect.getsource(util.getDriverDrivenFromConstraint)

    cmdList = []
    cmdList.append('import pymel.core as pm')
    cmdList.append(utilDefinitionString)
    cmdList.append(classDefinitionString.replace('util.', ''))

    cmdList.append('ikList = pm.ls(' + ','.join("'" + str(x) + "'" for x in ikList) + ')')
    cmdList.append('ikInstanceList = [IKFKSwitch(ik) for ik in ikList]')
    cmdList.append('ikScriptJobList = [i.addScriptJob() for i in ikInstanceList]')

    cmdString = '\n'.join(cmdList)
    pm.scriptNode(st=2, bs=cmdString, n='switch_IKFK', stp='python')



if __name__ == "__main__":
    installIKFK()
    # classeProva = IKFKSwitch('ikHandle1', forearmMidJnt=True)
    # classeProva.toIK()
    # classeProva.toFK()


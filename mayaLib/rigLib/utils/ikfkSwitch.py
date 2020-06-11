__author__ = 'Lorenzo Argentieri'

import inspect
import pymel.core as pm
from mayaLib.rigLib.utils import util


class IKFKSwitch():
    def __init__(self, ikHandle, forearmMidJnt=False, simpleIK=False):
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
        if simpleIK:
            # IK control
            pointConstraintIK = pm.listConnections(ikHandle, type='constraint')[0]
            self.joint3IKCtrl = util.getDriverDrivenFromConstraint(pointConstraintIK)[0][0]

            poleVectorConstraint = pm.listConnections(ikHandle, type='poleVectorConstraint', et=True)[0]
            self.poleVector = util.getDriverDrivenFromConstraint(poleVectorConstraint)[0][0]
        else:
            peelHeelGrp = ikHandle.getParent()
            tippyToeGrp = peelHeelGrp.getParent()
            moveGrp = tippyToeGrp.getParent()
            pointConstraintIK = pm.listConnections(moveGrp, type='constraint')[0]
            self.joint3IKCtrl = util.getDriverDrivenFromConstraint(pointConstraintIK)[0][0]

            poleVectorConstraint = pm.listConnections(ikHandle, type='poleVectorConstraint', et=True)[0]
            poleVectorLoc = util.getDriverDrivenFromConstraint(poleVectorConstraint)[0][0]
            poleVectorLocConstraint = poleVectorLoc.getChildren()[1]
            self.poleVector =  util.getDriverDrivenFromConstraint(poleVectorLocConstraint)[0][0]


        self.ikHandle = ikHandle
        self.driverLoc = self.ikHandle.inputs(scn=True, type='reverse')[0].inputs(scn=True, plugs=True)[0]
        self.driverAttribute = self.driverLoc.inputs(scn=True, plugs=True)[0]

    def toIK(self):
        pm.delete(pm.parentConstraint(self.joint3FKCtrl, self.joint3IKCtrl))
        pm.delete(pm.pointConstraint(self.joint2FKCtrl, self.poleVector))

    def toFK(self):
        pm.delete(pm.orientConstraint(self.joint1, self.joint1FKCtrl))
        pm.delete(pm.orientConstraint(self.joint2, self.joint2FKCtrl))
        pm.delete(pm.orientConstraint(self.joint3, self.joint3FKCtrl))

    def switchIKFK(self):
        blend = self.ikHandle.ikBlend.get()

        self.disconnect()

        if blend == 0:
            pm.setAttr(self.driverLoc, 0)
            self.toFK()
            print('Snap FK CTRL To IK')
        elif blend == 1:
            pm.setAttr(self.driverLoc, 0)
            self.toIK()
            print('Snap IK CTRL To FK')

        self.reconnect()

    def addScriptJob(self):
        return pm.scriptJob(attributeChange=[self.driverAttribute, self.switchIKFK])

    def disconnect(self):
        pm.disconnectAttr(self.driverAttribute, self.driverLoc)

    def reconnect(self):
        pm.connectAttr(self.driverAttribute, self.driverLoc)

def installIKFK(ikList):
    from mayaLib.rigLib.utils import ikfkSwitch
    classDefinitionString = inspect.getsource(ikfkSwitch.IKFKSwitch)
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

    print('INSTALLED IKFK SWITCH!')



if __name__ == "__main__":
    ikList = pm.ls('l_shoulder1_IKH', 'r_shoulder1_IKH', 'l_hip1_IKH', 'r_hip1_IKH')
    ikInstanceList = [IKFKSwitch(ik) for ik in ikList]
    ikScriptJobList = [i.addScriptJob() for i in ikInstanceList]
    print(ikScriptJobList)

    c = IKFKSwitch(ikList[0])
    c.switchIKFK()
    print(c.addScriptJob())


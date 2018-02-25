__author__ = 'Lorenzo Argentieri'

import pymel.core as pm
from mayaLib.rigLib.utils import name
from mayaLib.rigLib.utils import util
from mayaLib.rigLib.base import flexiplane


class StretchyIKChain():
    def __init__(self, ikHandle, ikCtrl, doFlexyplane=True):
        prefix = name.removeSuffix(ikHandle.name())

        jointList = pm.ikHandle(ikHandle, jointList=True, q=True)
        endJoint = pm.listRelatives(jointList[-1], c=True, type='joint')[0]
        jointList.append(endJoint)

        distanceDimensionShape = pm.distanceDimension(sp=jointList[0].getTranslation(space='world'),
                                                      ep=jointList[-1].getTranslation(space='world'))

        locators = pm.listConnections(distanceDimensionShape, s=True)
        startLoc = pm.rename(locators[0], prefix + 'DistanceStart_LOC')
        endLoc = pm.rename(locators[1], prefix + 'DistanceEnd_LOC')

        pm.pointConstraint(jointList[0], startLoc)
        pm.pointConstraint(ikCtrl, endLoc)

        # multiplyDivide Node
        multiplyDivideNode = pm.shadingNode('multiplyDivide', asUtility=True, n=prefix + '_multiplyDivide')
        multiplyDivideNode.input2X.set(1)
        multiplyDivideNode.operation.set(2)
        pm.connectAttr(distanceDimensionShape.distance, multiplyDivideNode.input1X, f=True)
        distance = 0
        for i in range(0, len(jointList[:-1])):
            distance = distance + util.get_distance(jointList[i], jointList[i + 1])
        multiplyDivideNode.input2X.set(distance)

        # condition Node
        conditionNode = pm.shadingNode('condition', asUtility=True, n=prefix + '_condition')
        conditionNode.operation.set(2)
        pm.connectAttr(distanceDimensionShape.distance, conditionNode.firstTerm, f=True)
        pm.connectAttr(multiplyDivideNode.input2X, conditionNode.secondTerm, f=True)
        pm.connectAttr(multiplyDivideNode.outputX, conditionNode.colorIfTrueR, f=True)

        for jnt in jointList[:-1]:
            pm.connectAttr(conditionNode.outColorR, jnt.scaleX, f=True)

        self.stretchyGrp = pm.group(startLoc, endLoc, distanceDimensionShape.getParent(), n=prefix+'Stretchy_GRP')
        self.stretchyGrp.visibility.set(0)

        # save attributes
        self.prefix = prefix
        self.jointList = jointList

        if doFlexyplane:
            self.doFlexyPlane(prefix)

    def getStretchyGrp(self):
        return self.stretchyGrp

    def doFlexyPlane(self, prefix, stretchy=1):
        for i in range(0, len(self.jointList[:-1])):
            flex = flexiplane.Flexiplane(prefix + str(i))
            globalCtrl, ctrlA, ctrlB, ctrlMid = flex.getControls()
            pm.pointConstraint([self.jointList[i], self.jointList[i + 1]], globalCtrl)
            pm.parentConstraint(self.jointList[i], ctrlA)
            pm.parentConstraint(self.jointList[i+1], ctrlB)

            globalCtrl.enable.set(stretchy)

            pm.parent(flex.getTopGrp(), self.stretchyGrp)


if __name__ == "__main__":
    ikh = pm.ls('ikHandle1')[0]
    StretchyIKChain(ikh, pm.ls('nurbsCircle1')[0])

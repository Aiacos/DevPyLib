"""
joint @ utils

Various joint utility functions
"""

import pymel.core as pm
from mayaLib.rigLib.utils import name
from mayaLib.rigLib.utils import util
from mayaLib.rigLib.utils import common

def listHierarchy(topJoint, withEndJoints=True):
    """
    list joint hierarchy starting with top joint
    
    :param topJoint: str, joint to get listed with its joint hierarchy
    :param withEndJoints: bool, list hierarchy including end joints
    :return: list( str ), listed joints starting with top joint
    """

    listedJoints = pm.listRelatives(topJoint, type='joint', ad=True)
    listedJoints.append(topJoint)
    listedJoints.reverse()

    completeJoints = listedJoints[:]

    if not withEndJoints:
        completeJoints = [j for j in listedJoints if pm.listRelatives(j, c=1, type='joint')]

    return completeJoints


class TwistJoint():
    def __init__(self, parentGrp, parentJoints, nTwistJoint=3, rotAxis='X'):
        if not pm.objExists('twistJoints_GRP'):
            self.twistJointsMainGrp = pm.group(n='twistJoints_GRP', p=parentGrp, em=1)
        else:
            self.twistJointsMainGrp = pm.ls('twistJoints_GRP')[0]

        for parentJnt in parentJoints:
            self.maketwistJoints(parentJnt, nTwistJoint, rotAxis)

    def maketwistJoints(self, parentJnt, nTwistJoint, rotAxis):
        prefix = name.removeSuffix(parentJnt)
        parentJntChild = pm.listRelatives(parentJnt, c=1, type='joint')[0]

        # make twist joints
        twistJntGrp = pm.group(n=prefix + 'TwistJoint_GRP', p=self.twistJointsMainGrp, em=1)

        twistParentJnt = pm.duplicate(parentJnt, n=prefix + 'TwistStart_JNT', parentOnly=True)[0]
        twistChildJnt = pm.duplicate(parentJntChild, n=prefix + 'TwistEnd_JNT', parentOnly=True)[0]

        # adjust twist joints
        origJntRadius = pm.getAttr(parentJnt + '.radius')

        for j in [twistParentJnt, twistChildJnt]:
            pm.setAttr(j + '.radius', origJntRadius * 2)
            pm.color(j, ud=1)

        pm.parent(twistChildJnt, twistParentJnt)
        pm.parent(twistParentJnt, twistJntGrp)

        # attach twist joints
        pm.pointConstraint(parentJnt, twistParentJnt)

        # make IK handle
        twistIk = pm.ikHandle(n=prefix + 'TwistJoint_IKH', sol='ikSCsolver', sj=twistParentJnt, ee=twistChildJnt)[0]
        pm.hide(twistIk)
        pm.parent(twistIk, twistJntGrp)
        pm.parentConstraint(parentJntChild, twistIk)

        pm.hide(twistParentJnt)

        innerJointList = self.makeInnerTwistJoints(prefix, twistParentJnt, twistChildJnt, nTwistJoint, rotAxis)
        pm.parent(innerJointList, twistJntGrp)

        # Constriant twistJoint group to main Joint
        pm.parentConstraint(parentJnt, twistJntGrp, mo=True)

    def makeInnerTwistJoints(self, prefix, startJnt, endJnt, nTwistJoint=3, rotAxis='X'):
        """
        Add Twist Joint for selected Joint
        :param joint_selection:
        :param nTwistJoint:
        :return:
        """
        distance = util.get_distance(startJnt, endJnt) / (nTwistJoint + 1)

        joint_list = []
        for i in range(0, nTwistJoint):
            # Create new twist Joint
            joint_name = prefix + '_twistJ' + str(i + 1) + 'JNT'
            new_joint = pm.joint(n=joint_name)
            pm.delete(pm.parentConstraint(startJnt, new_joint))
            common.freezeTranform(new_joint)
            pm.parent(new_joint, startJnt)
            pm.move((i + 1) * distance, 0, 0, new_joint, relative=True, localSpace=True)

            # connect to mulDoubleLinear node
            multiplyNode = pm.shadingNode('multDoubleLinear', asUtility=True)
            pm.connectAttr(startJnt.name()+'.rotate'+rotAxis, multiplyNode.input1, f=True)
            pm.connectAttr(multiplyNode.output, new_joint.name()+'.rotate'+rotAxis)
            weight = (1.0 / (nTwistJoint + 1.0)) * (i + 1)
            multiplyNode.input2.set(weight)

            # ovveride joint color
            new_joint.ove.set(1)
            new_joint.ovc.set(13)

            joint_list.append(new_joint)

        return joint_list

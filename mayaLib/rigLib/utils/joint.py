"""
joint @ utils

Various joint utility functions
"""

import math

import pymel.core as pm

from mayaLib.rigLib.utils import attributes
from mayaLib.rigLib.utils import common
from mayaLib.rigLib.utils import name
from mayaLib.rigLib.utils import util


def jointDirection(joint):
    """
    Get joint orient direction
    :param joint: str, pymel object
    :return: int (1 || -1)
    """
    child = pm.listRelatives(joint, c=True, type='joint')[0]
    t = child.getTranslation()
    max = 0.0
    maxsign = 0
    for tv in t:
        if abs(tv) > max:
            max = abs(tv)
            if tv < 0.0:
                maxsign = -1
            else:
                maxsign = 1
    return maxsign


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


def savePose(topJoint, poseName):
    jointList = pm.ls(listHierarchy(topJoint))
    for jnt in jointList:
        # translate
        translate = jnt.translate.get()
        attributes.addVectorAttribute(jnt, poseName + 'Translate', translate)
        # rotate
        rotate = jnt.rotate.get()
        attributes.addVectorAttribute(jnt, poseName + 'Rotate', rotate)
        # scale
        scale = jnt.scale.get()
        attributes.addVectorAttribute(jnt, poseName + 'Scale', scale)
        # rotation order
        rotateOrder = jnt.rotateOrder.get()
        attributes.addFloatAttribute(jnt, poseName + 'RotateOrder', rotateOrder)
        # joint orient
        jointOrient = jnt.jointOrient.get()
        attributes.addVectorAttribute(jnt, poseName + 'JointOrient', jointOrient)


def loadPose(topJoint, poseName):
    jointList = pm.ls(listHierarchy(topJoint))
    for jnt in jointList:
        # translate
        attributeList = pm.ls(jnt + '.' + poseName + 'Translate')
        if len(attributeList) == 1:
            attribute = attributeList[0]
            translatePose = attribute.get()
            jnt.translate.set(translatePose)
        # rotate
        attributeList = pm.ls(jnt + '.' + poseName + 'Rotate')
        if len(attributeList) == 1:
            attribute = attributeList[0]
            rotatePose = attribute.get()
            jnt.rotate.set(rotatePose)
        # scale
        attributeList = pm.ls(jnt + '.' + poseName + 'Scale')
        if len(attributeList) == 1:
            attribute = attributeList[0]
            scalePose = attribute.get()
            jnt.scale.set(scalePose)
        # rotate order
        attributeList = pm.ls(jnt + '.' + poseName + 'RotateOrder')
        if len(attributeList) == 1:
            attribute = attributeList[0]
            rotateOrderPose = attribute.get()
            jnt.rotateOrder.set(rotateOrderPose)
        # joint orient
        attributeList = pm.ls(jnt + '.' + poseName + 'JointOrient')
        if len(attributeList) == 1:
            attribute = attributeList[0]
            jointOrientPose = attribute.get()
            jnt.jointOrient.set(jointOrientPose)


def saveProjectionPose(topJnt='rootJA_JNT'):
    mainJoint = pm.ls(topJnt)[0]
    savePose(mainJoint, 'projectionPose')


def saveTPose(topJnt='rootJA_JNT'):
    mainJoint = pm.ls(topJnt)[0]
    savePose(mainJoint, 'TPose')


def loadProjectionPose(topJnt='rootJA_JNT'):
    mainJoint = pm.ls(topJnt)[0]
    loadPose(mainJoint, 'projectionPose')


def loadTPose(topJnt='rootJA_JNT'):
    mainJoint = pm.ls(topJnt)[0]
    loadPose(mainJoint, 'TPose')


def setJointParallelToGrid(p1, p2):
    p1x, p1y, p1z = pm.xform(p1, query=True, translation=True, worldSpace=True)
    p2x, p2y, p2z = pm.xform(p2, query=True, translation=True, worldSpace=True)

    xOffset = p1x - p2x
    yOffset = p1y - p2y
    angle = math.atan(yOffset / xOffset)

    return math.degrees(angle)

def setArmParallelToGrid(arm_transforms=[]):
    """
    Set Clavicle, Shoulder, Elbow and Wrist parallel to grid
    :param arm_transforms: str or obj list, list of transform to orient
    """

    arm_transforms = pm.ls(arm_transforms)
    for i, jnt in enumerate(arm_transforms[:-1]):
        angle = setJointParallelToGrid(arm_transforms[i], arm_transforms[i + 1])
        pm.xform(jnt, r=True, ro=(0, 0, -angle), ws=True)

def setArmParallelToGrid_old():
    leftClavicleJntList = pm.ls('l_clavicleJA_JNT', 'l_armJA_JNT')
    for i, jnt in enumerate(leftClavicleJntList[:-1]):
        angle = setJointParallelToGrid(leftClavicleJntList[i], leftClavicleJntList[i + 1])
        pm.xform(jnt, r=True, ro=(0, 0, -angle), ws=True)

    rightClavicleJntList = pm.ls('r_clavicleJA_JNT', 'r_armJA_JNT')
    for i, jnt in enumerate(rightClavicleJntList[:-1]):
        angle = setJointParallelToGrid(rightClavicleJntList[i], rightClavicleJntList[i + 1])
        pm.xform(jnt, r=True, ro=(0, 0, -angle), ws=True)

    leftArmJntList = pm.ls('l_armJ?_JNT', 'l_handJA_JNT')
    for i, jnt in enumerate(leftArmJntList[:-1]):
        angle = setJointParallelToGrid(leftArmJntList[i], leftArmJntList[i + 1])
        pm.xform(jnt, r=True, ro=(0, 0, -angle), ws=True)

    rightArmJntList = pm.ls('r_armJ?_JNT', 'r_handJA_JNT')
    for i, jnt in enumerate(rightArmJntList[:-1]):
        angle = setJointParallelToGrid(rightArmJntList[i], rightArmJntList[i + 1])
        pm.xform(jnt, r=True, ro=(0, 0, -angle), ws=True)

    leftHandJntList = pm.ls('l_handJA_JNT', 'l_fngMiddleJA_JNT')
    for i, jnt in enumerate(leftHandJntList[:-1]):
        angle = setJointParallelToGrid(leftHandJntList[i], leftHandJntList[i + 1])
        pm.xform(jnt, r=True, ro=(0, 0, -angle), ws=True)

    rightHandJntList = pm.ls('r_handJA_JNT', 'r_fngMiddleJA_JNT')
    for i, jnt in enumerate(rightHandJntList[:-1]):
        angle = setJointParallelToGrid(rightHandJntList[i], rightHandJntList[i + 1])
        pm.xform(jnt, r=True, ro=(0, 0, -angle), ws=True)


class TwistJoint():
    """
    Add Twist Joint for selected Joint
    :param joint_selection:
    :param n_twist_joint:
    :return:
    """

    def __init__(self, parentJoint, parentGrp='rig_GRP', nTwistJoint=3, rotAxis='X'):
        if not pm.objExists(parentGrp):
            pm.group(n=parentGrp, em=True)

        if not pm.objExists('twistJoints_GRP'):
            self.twistJointsMainGrp = pm.group(n='twistJoints_GRP', p=parentGrp, em=1)
        else:
            self.twistJointsMainGrp = pm.ls('twistJoints_GRP')[0]

        if isinstance(parentJoint, str):
            self.maketwistJoints(pm.ls(parentJoint)[0], nTwistJoint, rotAxis)
        else:
            for jnt in parentJoint:
                self.maketwistJoints(jnt, nTwistJoint, rotAxis)

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

            direction = jointDirection(startJnt)
            pm.move((i + 1) * distance * direction, 0, 0, new_joint, relative=True, localSpace=True)

            # connect to mulDoubleLinear node
            multiplyNode = pm.shadingNode('multDoubleLinear', asUtility=True)
            pm.connectAttr(startJnt.name() + '.rotate' + rotAxis, multiplyNode.input1, f=True)
            pm.connectAttr(multiplyNode.output, new_joint.name() + '.rotate' + rotAxis)
            weight = (1.0 / (nTwistJoint + 1.0)) * (i + 1)
            multiplyNode.input2.set(weight)

            # ovveride joint color
            new_joint.ove.set(1)
            new_joint.ovc.set(13)

            joint_list.append(new_joint)

        return joint_list


def renameHumanIKJoint(element='Character1', deleteHumanIK=True):
    # Hip - Spine
    spineList = pm.ls(element + '_Hips', element + '_Spine*')
    for jnt, i in zip(spineList, list(range(0, len(spineList)))):
        newName = 'spineJ' + name.getAlpha(i) + '_JNT'
        pm.rename(jnt, newName)

    # Neck
    neckList = pm.ls(element + '_Neck*')
    for jnt, i in zip(neckList, list(range(0, len(neckList)))):
        newName = 'neckJ' + name.getAlpha(i) + '_JNT'
        pm.rename(jnt, newName)

    # Head
    headList = pm.ls(element + '_Head*')
    for jnt, i in zip(headList, list(range(0, len(headList)))):
        newName = 'headJ' + name.getAlpha(i) + '_JNT'
        pm.rename(jnt, newName)

    # Jaw
    jawList = pm.ls(element + '_Jaw*')
    for jnt, i in zip(jawList, list(range(0, len(jawList)))):
        newName = 'jawJ' + name.getAlpha(i) + '_JNT'
        pm.rename(jnt, newName)

    # Left - Right
    leftList = pm.ls(element + '_Left*')
    rightList = pm.ls(element + '_Right*')

    for sideList, i in zip([leftList, rightList], list(range(0, 2))):
        if i == 0:
            side = 'l_'
            oldSide = 'Left'
        else:
            side = 'r_'
            oldSide = 'Right'

        for jnt in sideList:
            elementSplit, jointSplit = jnt.name().split('_')
            newName = side + jointSplit.replace(oldSide, '') + '_JNT'
            pm.rename(jnt, newName)

        # Clavicle
        clavicleList = pm.ls(side + 'Shoulder_JNT')
        for jnt, i in zip(clavicleList, list(range(0, len(clavicleList)))):
            newName = side + 'clavicleJ' + name.getAlpha(i) + '_JNT'
            pm.rename(jnt, newName)

        # Arms
        armList = pm.ls(side + 'Arm_JNT', side + 'ForeArm_JNT')
        for jnt, i in zip(armList, list(range(0, len(armList)))):
            newName = side + 'armJ' + name.getAlpha(i) + '_JNT'
            pm.rename(jnt, newName)

        # Hand
        handList = pm.ls(side + '*Hand_JNT')
        for jnt, i in zip(handList, list(range(0, len(handList)))):
            newName = side + 'handJ' + name.getAlpha(i) + '_JNT'
            pm.rename(jnt, newName)

        # Fng - HandThumb
        fngThumbList = pm.ls(side + '*HandThumb*_JNT')
        for jnt, i in zip(fngThumbList, list(range(0, len(fngThumbList)))):
            newName = side + 'fngThumbJ' + name.getAlpha(i) + '_JNT'
            pm.rename(jnt, newName)

        # Fng - HandIndex
        fngIndexList = pm.ls(side + '*HandIndex*_JNT')
        for jnt, i in zip(fngIndexList, list(range(0, len(fngIndexList)))):
            newName = side + 'fngIndexJ' + name.getAlpha(i) + '_JNT'
            pm.rename(jnt, newName)

        # Fng - HandMiddle
        fngMidList = pm.ls(side + '*HandMiddle*_JNT')
        for jnt, i in zip(fngMidList, list(range(0, len(fngMidList)))):
            newName = side + 'fngMiddleJ' + name.getAlpha(i) + '_JNT'
            pm.rename(jnt, newName)

        # Fng - HandRing
        fngRingList = pm.ls(side + '*HandRing*_JNT')
        for jnt, i in zip(fngRingList, list(range(0, len(fngRingList)))):
            newName = side + 'fngRingJ' + name.getAlpha(i) + '_JNT'
            pm.rename(jnt, newName)

        # Fng - HandPinky
        fngPinkyList = pm.ls(side + '*HandPinky*_JNT')
        for jnt, i in zip(fngPinkyList, list(range(0, len(fngPinkyList)))):
            newName = side + 'fngPinkyJ' + name.getAlpha(i) + '_JNT'
            pm.rename(jnt, newName)

        ###
        # Legs
        legList = pm.ls(side + 'UpLeg_JNT', side + 'Leg_JNT')
        for jnt, i in zip(legList, list(range(0, len(legList)))):
            newName = side + 'legJ' + name.getAlpha(i) + '_JNT'
            pm.rename(jnt, newName)

        # Foot
        footList = pm.ls(side + '*Foot_JNT')
        for jnt, i in zip(footList, list(range(0, len(footList)))):
            newName = side + 'footJ' + name.getAlpha(i) + '_JNT'
            pm.rename(jnt, newName)

        # Toe - FootExtraFinger
        fngThumbList = pm.ls(side + '*FootExtraFinger*_JNT')
        for jnt, i in zip(fngThumbList, list(range(0, len(fngThumbList)))):
            newName = side + 'toeThumbJ' + name.getAlpha(i) + '_JNT'
            pm.rename(jnt, newName)

        # Toe - FootIndex
        fngIndexList = pm.ls(side + '*FootIndex*_JNT')
        for jnt, i in zip(fngIndexList, list(range(0, len(fngIndexList)))):
            newName = side + 'toeIndexJ' + name.getAlpha(i) + '_JNT'
            pm.rename(jnt, newName)

        # Toe - FootMiddle
        fngMidList = pm.ls(side + '*FootMiddle*_JNT')
        for jnt, i in zip(fngMidList, list(range(0, len(fngMidList)))):
            newName = side + 'toeMiddleJ' + name.getAlpha(i) + '_JNT'
            pm.rename(jnt, newName)

        # Toe - FootRing
        fngRingList = pm.ls(side + '*FootRing*_JNT')
        for jnt, i in zip(fngRingList, list(range(0, len(fngRingList)))):
            newName = side + 'toeRingJ' + name.getAlpha(i) + '_JNT'
            pm.rename(jnt, newName)

        # Toe - FootPinky
        fngPinkyList = pm.ls(side + '*FootPinky*_JNT')
        for jnt, i in zip(fngPinkyList, list(range(0, len(fngPinkyList)))):
            newName = side + 'toePinkyJ' + name.getAlpha(i) + '_JNT'
            pm.rename(jnt, newName)

    # End Joint
    endJointList = pm.ls(spineList[0], type='joint', dagObjects=True, leaf=True)
    for endJnt in endJointList:
        newName = str(endJnt.name())[:-5] + 'End_JNT'
        pm.rename(endJnt, newName)

    # delete HumanIK node
    if deleteHumanIK:
        hikNode = pm.ls(type=['HIKCharacterNode', 'HIKState2SK'])
        pm.delete(hikNode)

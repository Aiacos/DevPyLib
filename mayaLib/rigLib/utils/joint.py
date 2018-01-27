"""
joint @ utils

Various joint utility functions
"""

import pymel.core as pm


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

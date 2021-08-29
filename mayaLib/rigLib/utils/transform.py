"""
transform @ utils

Functions to manipulate and create transforms
"""

import pymel.core as pm

from mayaLib.rigLib.utils import name


def makeOffsetGrp(object, prefix=''):
    """
    make offset group for given object
    
    @param object: transform object to get offset group
    @param prefix: str, prefix to name new objects
    @return: str, name of new offset group
    """

    if not prefix:
        prefix = name.removeSuffix(object)

    offsetGrp = pm.group(n=prefix + 'Offset_GRP', em=1)

    objectParents = pm.listRelatives(object, p=1)

    if objectParents:
        pm.parent(offsetGrp, objectParents[0])

    # match object transform
    pm.delete(pm.parentConstraint(object, offsetGrp))
    pm.delete(pm.scaleConstraint(object, offsetGrp))

    # parent object under offset group
    pm.parent(object, offsetGrp)

    return offsetGrp


def makeModifyGrp(object, prefix=''):
    """
    make modify group for given object

    @param object: transform object to get modify group
    @param prefix: str, prefix to name new objects
    @return: str, name of new modify group
    """

    if not prefix:
        prefix = name.removeSuffix(object)

    modifyGrp = pm.group(n=prefix + 'Modify_GRP', em=1)

    objectParents = pm.listRelatives(object, p=1)

    if objectParents:
        pm.parent(modifyGrp, objectParents[0])

    # match object transform
    pm.delete(pm.parentConstraint(object, modifyGrp))
    pm.delete(pm.scaleConstraint(object, modifyGrp))

    # parent object under offset group
    pm.parent(object, modifyGrp)

    return modifyGrp

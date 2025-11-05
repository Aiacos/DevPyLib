"""Facial rig setup utilities for curve-based controls.

Provides tools for creating facial rig setups using curves with
locators and joints distributed along their length for facial animation.
"""

__author__ = 'Lorenzo Argentieri'

import maya.cmds as cmds

## Var ##
pointsNumber = 5

curve = cmds.ls(sl=True)
# nameBuilder_locator = curve[0] + "_loc"  #in function, lacal variables
# nameBuilder_joint = curve[0] + "_jnt"  #in function, local variables

spacing = 1.0 / (pointsNumber - 1)


## Main --wip

def delete_connection(plug):
    # """ Equivalent of MEL: CBdeleteConnection """

    if cmds.connectionInfo(plug, isDestination=True):
        plug = cmds.connectionInfo(plug, getExactDestination=True)
        readOnly = cmds.ls(plug, ro=True)
        # delete -icn doesn't work if destination attr is readOnly
        if readOnly:
            source = cmds.connectionInfo(plug, sourceFromDestination=True)
            cmds.disconnectAttr(source, plug)
        else:
            cmds.delete(plug, icn=True)


def path_mode(path, follow=False, sphere_size=0.1, offset_active=False, loc_size=0.1, joint_radius=0.1):
    nameBuilder_locator = path + "_loc"
    nameBuilder_offset = path + "_offset_jnt"
    nameBuilder_joint = path + "_jnt_ctrl"
    locatorList = []
    for p in range(0, pointsNumber):
        # place locator
        locator = cmds.spaceLocator(n=nameBuilder_locator + str(p + 1))
        cmds.setAttr(locator[0] + '.localScaleX', loc_size)
        cmds.setAttr(locator[0] + '.localScaleY', loc_size)
        cmds.setAttr(locator[0] + '.localScaleZ', loc_size)
        motionPath = cmds.pathAnimation(locator[0], c=path, f=follow)
        delete_connection(motionPath + '.u')
        cmds.setAttr(motionPath + '.uValue', spacing * p)
        locatorList.append(locator[0])
        # place joint
        # - crea joint con il nome
        # - imparentalo al locator e freza le trasfmormazioni
        if offset_active:
            jointOffset = cmds.joint(n=nameBuilder_offset, r=joint_radius)
            cmds.setAttr(jointOffset + '.radius', joint_radius)
        # - altro joint (con nome) imparentato al primo sempre freezato (o duplica il primo)
        joint = cmds.joint(n=nameBuilder_joint, r=joint_radius)
        cmds.setAttr(joint + '.radius', joint_radius)
        # - crea sfera e imparenta il nodo di shape al secondo joint
        sphereObj = cmds.sphere(r=sphere_size, axis=(0, 1, 0))  # color based on L/R
        sphereShape = cmds.listRelatives(sphereObj, children=True, shapes=True)
        cmds.parent(sphereShape, joint, r=True, s=True)
        cmds.delete(sphereObj)
    return locatorList


if __name__ == "__main__":
    locList = []
    for cv in curve:
        # print(cv)
        locList.extend(path_mode(cv))
    cmds.group(locList, n='locator_grp')

    ## --ToDo

    # gui
    # object oriented
    # multithreading --probabilmente si puo evitare

    # docstring not working. why?

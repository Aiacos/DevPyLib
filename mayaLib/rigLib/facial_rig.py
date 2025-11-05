"""Facial rig setup utilities for curve-based controls.

Provides tools for creating facial rig setups using curves with
locators and joints distributed along their length for facial animation.
"""

__author__ = 'Lorenzo Argentieri'

import maya.cmds as cmds

## Var ##
points_number = 5

curve = cmds.ls(sl=True)
# nameBuilder_locator = curve[0] + "_loc"  #in function, lacal variables
# nameBuilder_joint = curve[0] + "_jnt"  #in function, local variables

spacing = 1.0 / (points_number - 1)


## Main --wip

def delete_connection(plug):
    """Delete connection from a plug (equivalent of MEL CBdeleteConnection).

    Args:
        plug (str): Plug path (node.attribute).
    """
    # """ Equivalent of MEL: CBdeleteConnection """

    if cmds.connectionInfo(plug, isDestination=True):
        plug = cmds.connectionInfo(plug, getExactDestination=True)
        read_only = cmds.ls(plug, ro=True)
        # delete -icn doesn't work if destination attr is readOnly
        if read_only:
            source = cmds.connectionInfo(plug, sourceFromDestination=True)
            cmds.disconnectAttr(source, plug)
        else:
            cmds.delete(plug, icn=True)


def path_mode(path, follow=False, sphere_size=0.1, offset_active=False, loc_size=0.1, joint_radius=0.1):
    """Create locators and joints distributed along a curve path.

    Args:
        path (str): Curve path name.
        follow (bool): Whether locators follow curve direction.
        sphere_size (float): Size of visual sphere control.
        offset_active (bool): Create offset joint layer.
        loc_size (float): Size of locator visual.
        joint_radius (float): Radius of joint display.

    Returns:
        list: List of created locator names.
    """
    name_builder_locator = path + "_loc"
    name_builder_offset = path + "_offset_jnt"
    name_builder_joint = path + "_jnt_ctrl"
    locator_list = []
    for p in range(0, points_number):
        # place locator
        locator = cmds.spaceLocator(n=name_builder_locator + str(p + 1))
        cmds.setAttr(locator[0] + '.localScaleX', loc_size)
        cmds.setAttr(locator[0] + '.localScaleY', loc_size)
        cmds.setAttr(locator[0] + '.localScaleZ', loc_size)
        motion_path = cmds.pathAnimation(locator[0], c=path, f=follow)
        delete_connection(motion_path + '.u')
        cmds.setAttr(motion_path + '.uValue', spacing * p)
        locator_list.append(locator[0])
        # place joint
        # - crea joint con il nome
        # - imparentalo al locator e freza le trasfmormazioni
        if offset_active:
            joint_offset = cmds.joint(n=name_builder_offset, r=joint_radius)
            cmds.setAttr(joint_offset + '.radius', joint_radius)
        # - altro joint (con nome) imparentato al primo sempre freezato (o duplica il primo)
        joint = cmds.joint(n=name_builder_joint, r=joint_radius)
        cmds.setAttr(joint + '.radius', joint_radius)
        # - crea sfera e imparenta il nodo di shape al secondo joint
        sphere_obj = cmds.sphere(r=sphere_size, axis=(0, 1, 0))  # color based on L/R
        sphere_shape = cmds.listRelatives(sphere_obj, children=True, shapes=True)
        cmds.parent(sphere_shape, joint, r=True, s=True)
        cmds.delete(sphere_obj)
    return locator_list


if __name__ == "__main__":
    loc_list = []
    for cv in curve:
        # print(cv)
        loc_list.extend(path_mode(cv))
    cmds.group(loc_list, n='locator_grp')

    ## --ToDo

    # gui
    # object oriented
    # multithreading --probabilmente si puo evitare

    # docstring not working. why?

__author__ = 'Lorenzo Argentieri'

import pymel.core as pm


def renameCtrl(joint, control):
    """
    Renames the given control based on the joint's name.

    Args:
        joint (str): The name of the joint to derive the control's new name from.
        control (pm.nt.Transform): The control object to be renamed.

    Returns:
        pm.nt.Transform: The renamed control object.
    """
    jointName = joint
    controlName = jointName.replace('_jnt', '_ctrl')
    print(controlName)
    return control.rename(controlName)


def orientCtrl_constrain(control, joint):
    """
    Orients the given control to the given joint and constrains it via a parent constraint.

    Args:
        control (pm.nt.Transform): The control object to be oriented.
        joint (pm.nt.Transform): The joint object to orient the control to.

    Returns:
        pm.nt.Transform: The oriented control object.
    """
    control_name = renameCtrl(joint, control)
    control_group = pm.group(control, n=control_name + '_grp')
    control_group.rotateZ.set(90)
    pm.makeIdentity(control_group, apply=True)
    parentConstraint = pm.parentConstraint(joint, control_group)
    pm.delete(parentConstraint)


def orientCtrl_parent(control, joint):
    """
    Orients the given control to the given joint and parents it to the joint.

    Args:
        control (pm.nt.Transform): The control object to be oriented.
        joint (pm.nt.Transform): The joint object to orient the control to.

    Returns:
        pm.nt.Transform: The oriented control object.
    """
    control_name = renameCtrl(joint, control)
    joint_pivot = joint.getTranslation(worldSpace=True)
    # set PivotPoint to Joint location
    control_group = pm.group(control, n=control_name + '_grp')
    control.setPivots(joint_pivot, worldSpace=True)
    control_group.setPivots(joint_pivot, worldSpace=True)
    pm.parent(control_group, joint)
    pm.delete(control_group, constructionHistory=True)
    pm.makeIdentity(control_group, apply=True)  # translate=True, rotate=True, scale=True)
    pm.parent(control_group, world=True)


def main_orientCtrl():
    """
    Orients the selected control to the selected joint using either a parent constraint or parenting to the joint.

    If the selected object is a joint, the control is parented to the joint.
    If the selected object is not a joint, the control is constrained to the joint using a parent constraint.
    """
    sel1, sel2 = pm.ls(sl=True)

    print((sel2.nodeType()))

    if sel2.nodeType() == 'joint':
        print('parent')
        orientCtrl_parent(sel1, sel2)
    else:
        print('costrain')
        orientCtrl_constrain(sel2, sel1)


if __name__ == "__main__":
    main_orientCtrl()

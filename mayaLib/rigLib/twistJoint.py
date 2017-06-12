__author__ = 'Lorenzo Argentieri'

import pymel.core as pm
import mayaLib.rigLib.utils.util


def make_twist_joints(joint_selection=pm.ls(sl=True, type='joint', dag=True), n_twist_joint=3):
    """
    Add Twist Joint for selected Joint
    :param joint_selection:
    :param n_twist_joint:
    :return:
    """

    # Put all joints from selection in a variable
    head_jnt = joint_selection[0]
    tail_jnt = joint_selection[1]

    distance = mayaLib.rigLib.utils.util.get_distance(head_jnt, tail_jnt) / (n_twist_joint+1)

    pm.parent(tail_jnt.name(), world=True)
    twist_jnt_grp = pm.group(name=head_jnt.name() + '_twist' + '_grp')
    joint_list = []
    for i in range(0, n_twist_joint):
        # Create new twist Joint
        joint_name = head_jnt.name() + '_twist' + str(i + 1)
        new_joint_name = pm.insertJoint(head_jnt.name())
        new_joint = pm.PyNode(str(new_joint_name))
        pm.rename(new_joint, joint_name)
        joint_list.append(new_joint)
        pm.move((i+1) * distance, 0, 0, new_joint, relative=True, localSpace=True)

        # Constraint
        weight = (1.0/(n_twist_joint + 1.0)) * (i + 1)
        pm.orientConstraint(tail_jnt, new_joint, w=weight)

        # Reparent
        pm.parent(joint_list[i], twist_jnt_grp)

    pm.parent(tail_jnt, head_jnt)
    pm.parentConstraint(head_jnt, twist_jnt_grp, mo=True)


if __name__ == "__main__":
    make_twist_joints()

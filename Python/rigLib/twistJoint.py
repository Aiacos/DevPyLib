import pymel.core as pm
import rigLib


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

    distance = rigLib.utils.util.get_distance(head_jnt, tail_jnt)

    pm.parent(tail_jnt.name(), world=True)
    twist_jnt_grp = pm.group(name=head_jnt.name() + '_twist' + '_grp')
    joint_list = []
    for i in range(0, n_twist_joint):
        # joint_name = head_jnt.name() + '_twist' + str(i + 1)
        new_joint_name = pm.insertJoint(head_jnt.name())
        new_joint = pm.PyNode(str(new_joint_name))

        joint_list.append(new_joint)
        pm.move((i + 1) * distance, 0, 0, new_joint, relative=True, localSpace=True)
        # -ToDo: constraint
        pm.parent(joint_list[i], twist_jnt_grp)

    pm.parent(tail_jnt, head_jnt)


if __name__ == "__main__":
    make_twist_joints()

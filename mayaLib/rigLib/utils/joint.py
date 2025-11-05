"""Joint utility helpers used across the rigging toolkit."""

from __future__ import annotations

import math
from typing import Sequence

import pymel.core as pm

from mayaLib.rigLib.utils import attributes, common, name, util

__all__ = [
    'lock_transformation',
    'joint_direction',
    'list_hierarchy',
    'save_pose',
    'load_pose',
    'save_projection_pose',
    'save_t_pose',
    'load_projection_pose',
    'load_t_pose',
    'set_joint_parallel_to_grid',
    'set_arm_parallel_to_grid',
    'set_arm_parallel_to_grid_old',
    'TwistJoint',
    'rename_human_ik_joint',
]


def lock_transformation(
    node,
    translate_axes: Sequence[str] | None = None,
    rotate_axes: Sequence[str] | None = None,
) -> None:
    """Lock translation and rotation limits on the supplied node."""
    if not pm.objExists(node):
        return

    translate_axes = tuple(translate_axes or ('x', 'y', 'z'))
    rotate_axes = tuple(rotate_axes or ('x', 'y'))

    node = pm.PyNode(node)
    translation = node.translate.get()
    rotation = node.rotate.get()

    for axis in translate_axes:
        if 'x' in axis:
            pm.transformLimits(node, tx=[translation[0]] * 2, etx=[1, 1])
        if 'y' in axis:
            pm.transformLimits(node, ty=[translation[1]] * 2, ety=[1, 1])
        if 'z' in axis:
            pm.transformLimits(node, tz=[translation[2]] * 2, etz=[1, 1])

    for axis in rotate_axes:
        if 'x' in axis:
            pm.transformLimits(node, rx=[rotation[0]] * 2, erx=[1, 1])
        if 'y' in axis:
            pm.transformLimits(node, ry=[rotation[1]] * 2, ery=[1, 1])
        if 'z' in axis:
            pm.transformLimits(node, rz=[rotation[2]] * 2, erz=[1, 1])


def joint_direction(joint) -> int:
    """Return the primary direction of the child joint."""
    child_joints = pm.listRelatives(joint, c=True, type='joint') or []
    if not child_joints:
        return 0
    translation = child_joints[0].getTranslation()
    max_value = 0.0
    sign = 0
    for value in translation:
        abs_value = abs(value)
        if abs_value > max_value:
            max_value = abs_value
            sign = -1 if value < 0.0 else 1
    return sign


def list_hierarchy(top_joint, include_end_joints: bool = True) -> list[pm.PyNode]:
    """Return joints in the hierarchy rooted at ``top_joint``."""
    joint_list = pm.listRelatives(top_joint, type='joint', ad=True) or []
    joint_list.append(pm.PyNode(top_joint))
    joint_list.reverse()

    if include_end_joints:
        return joint_list
    return [
        joint for joint in joint_list if pm.listRelatives(joint, c=True, type='joint')
    ]


def save_pose(top_joint, pose_name: str) -> None:
    """Store the current pose on every joint in the hierarchy as custom attrs."""
    for joint in pm.ls(list_hierarchy(top_joint)):
        translate = joint.translate.get()
        attributes.add_vector_attribute(joint, f'{pose_name}Translate', translate)

        rotate = joint.rotate.get()
        attributes.add_vector_attribute(joint, f'{pose_name}Rotate', rotate)

        scale = joint.scale.get()
        attributes.add_vector_attribute(joint, f'{pose_name}Scale', scale)

        rotate_order = joint.rotateOrder.get()
        attributes.add_float_attribute(joint, f'{pose_name}RotateOrder', rotate_order)

        joint_orient = joint.jointOrient.get()
        attributes.add_vector_attribute(joint, f'{pose_name}JointOrient', joint_orient)


def load_pose(top_joint, pose_name: str) -> None:
    """Restore a pose previously stored via :func:`save_pose`."""
    for joint in pm.ls(list_hierarchy(top_joint)):
        translate_attr = pm.ls(f'{joint}.{pose_name}Translate')
        if len(translate_attr) == 1:
            joint.translate.set(translate_attr[0].get())

        rotate_attr = pm.ls(f'{joint}.{pose_name}Rotate')
        if len(rotate_attr) == 1:
            joint.rotate.set(rotate_attr[0].get())

        scale_attr = pm.ls(f'{joint}.{pose_name}Scale')
        if len(scale_attr) == 1:
            joint.scale.set(scale_attr[0].get())

        rotate_order_attr = pm.ls(f'{joint}.{pose_name}RotateOrder')
        if len(rotate_order_attr) == 1:
            joint.rotateOrder.set(rotate_order_attr[0].get())

        joint_orient_attr = pm.ls(f'{joint}.{pose_name}JointOrient')
        if len(joint_orient_attr) == 1:
            joint.jointOrient.set(joint_orient_attr[0].get())


def save_projection_pose(top_joint='god_M:godnode_srt') -> None:
    """Store the projection pose attributes on the joint hierarchy."""
    save_pose(top_joint, 'projectionPose')


def save_t_pose(top_joint='god_M:godnode_srt') -> None:
    """Store a T-pose on the joint hierarchy."""
    save_pose(top_joint, 'TPose')


def load_projection_pose(top_joint='god_M:godnode_srt') -> None:
    """Apply the previously stored projection pose to the joint hierarchy."""
    load_pose(top_joint, 'projectionPose')


def load_t_pose(top_joint='god_M:godnode_srt') -> None:
    """Apply the previously stored T-pose to the joint hierarchy."""
    load_pose(top_joint, 'TPose')


def set_joint_parallel_to_grid(joint_a, joint_b) -> float:
    """Return the rotation angle required to align ``joint_a`` to the grid."""
    p1x, p1y, _ = pm.xform(joint_a, query=True, translation=True, worldSpace=True)
    p2x, p2y, _ = pm.xform(joint_b, query=True, translation=True, worldSpace=True)
    x_offset = p1x - p2x
    y_offset = p1y - p2y
    angle = math.atan(y_offset / x_offset) if x_offset else 0.0
    return math.degrees(angle)


def set_arm_parallel_to_grid(transforms: Sequence) -> None:
    """Rotate transforms so the chain aligns parallel to the ground plane."""
    nodes = pm.ls(transforms)
    for index, joint in enumerate(nodes[:-1]):
        angle = set_joint_parallel_to_grid(nodes[index], nodes[index + 1])
        pm.xform(joint, r=True, ro=(0, 0, -angle), ws=True)


def set_arm_parallel_to_grid_old() -> None:
    """Legacy helper that aligns default Arise arm joints to the grid."""
    for joint_pair in [
        pm.ls('l_clavicleJA_JNT', 'l_armJA_JNT'),
        pm.ls('r_clavicleJA_JNT', 'r_armJA_JNT'),
        pm.ls('l_armJ?_JNT', 'l_handJA_JNT'),
        pm.ls('r_armJ?_JNT', 'r_handJA_JNT'),
        pm.ls('l_handJA_JNT', 'l_fngMiddleJA_JNT'),
        pm.ls('r_handJA_JNT', 'r_fngMiddleJA_JNT'),
    ]:
        for index, joint in enumerate(joint_pair[:-1]):
            angle = set_joint_parallel_to_grid(
                joint_pair[index], joint_pair[index + 1]
            )
            pm.xform(joint, r=True, ro=(0, 0, -angle), ws=True)


class TwistJoint:  # pylint: disable=too-many-instance-attributes
    """Construct a twist joint chain for a given parent joint."""

    def __init__(  # pylint: disable=too-many-arguments
        self,
        parent_joint,
        parent_group: str = 'rig_GRP',
        num_twist_joints: int = 3,
        rotation_axis: str = 'X',
    ) -> None:
        """Initialize twist joint chain for one or more parent joints.

        Creates a twist joint setup between parent and child joints to distribute
        rotation along the limb, preventing candy-wrapper deformation artifacts.

        Args:
            parent_joint: Single joint name/PyNode or list of joints to add twist to
            parent_group: Name of parent group for twist joint hierarchy. Defaults to 'rig_GRP'.
            num_twist_joints: Number of intermediate twist joints to create. Defaults to 3.
            rotation_axis: Axis along which twist rotation occurs ('X', 'Y', or 'Z'). Defaults to 'X'.

        Example:
            >>> twist = TwistJoint('upperarm_L_JNT', num_twist_joints=5)
            >>> twist = TwistJoint(['upperarm_L_JNT', 'upperarm_R_JNT'])
        """
        if not pm.objExists(parent_group):
            pm.group(n=parent_group, em=True)

        if not pm.objExists('twistJoints_GRP'):
            self.twist_joints_main_grp = pm.group(
                n='twistJoints_GRP', p=parent_group, em=True
            )
        else:
            self.twist_joints_main_grp = pm.ls('twistJoints_GRP')[0]

        targets = (
            pm.ls(parent_joint)
            if isinstance(parent_joint, str)
            else [pm.PyNode(joint) for joint in parent_joint]
        )
        for joint in targets:
            self.make_twist_joints(
                joint, num_twist_joints, rotation_axis.upper()
            )

    def make_twist_joints(
        self,
        parent_joint,
        num_twist_joints: int,
        rotation_axis: str,
    ) -> None:
        """Create a pair of twist joints and optional inner twist joints."""
        prefix = name.remove_suffix(parent_joint)
        child_joint = pm.listRelatives(parent_joint, c=True, type='joint')[0]

        twist_group = pm.group(
            n=f"{prefix}TwistJoint_GRP",
            p=self.twist_joints_main_grp,
            em=True,
        )

        start_joint = pm.duplicate(
            parent_joint, n=f"{prefix}TwistStart_JNT", parentOnly=True
        )[0]
        end_joint = pm.duplicate(
            child_joint, n=f"{prefix}TwistEnd_JNT", parentOnly=True
        )[0]

        radius = pm.getAttr(f'{parent_joint}.radius')
        for joint in (start_joint, end_joint):
            pm.setAttr(f'{joint}.radius', radius * 2)
            pm.color(joint, ud=1)

        pm.parent(end_joint, start_joint)
        pm.parent(start_joint, twist_group)

        pm.pointConstraint(parent_joint, start_joint)
        twist_ik = pm.ikHandle(
            n=f"{prefix}TwistJoint_IKH",
            sol='ikSCsolver',
            sj=start_joint,
            ee=end_joint,
        )[0]
        pm.hide(twist_ik)
        pm.parent(twist_ik, twist_group)
        pm.parentConstraint(child_joint, twist_ik)
        pm.hide(start_joint)

        inner_joints = self.make_inner_twist_joints(
            prefix,
            start_joint,
            end_joint,
            num_twist_joints,
            rotation_axis,
        )
        pm.parent(inner_joints, twist_group)
        pm.parentConstraint(parent_joint, twist_group, mo=True)

    def make_inner_twist_joints(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        prefix: str,
        start_joint,
        end_joint,
        num_twist_joints: int = 3,
        rotation_axis: str = 'X',
    ) -> list[pm.PyNode]:
        """Insert evenly spaced twist joints between start and end joints."""
        distance = util.get_distance(start_joint, end_joint) / (num_twist_joints + 1)
        joint_list: list[pm.PyNode] = []

        for index in range(num_twist_joints):
            joint_name = f"{prefix}_twistJ{index + 1}JNT"
            new_joint = pm.joint(n=joint_name)
            pm.delete(pm.parentConstraint(start_joint, new_joint))
            common.freeze_transform(new_joint)
            pm.parent(new_joint, start_joint)

            direction = joint_direction(start_joint)
            pm.move(
                (index + 1) * distance * direction,
                0,
                0,
                new_joint,
                relative=True,
                localSpace=True,
            )

            multiply_node = pm.shadingNode('multDoubleLinear', asUtility=True)
            pm.connectAttr(
                f'{start_joint}.rotate{rotation_axis}',
                multiply_node.input1,
                f=True,
            )
            pm.connectAttr(
                multiply_node.output,
                f'{new_joint}.rotate{rotation_axis}',
            )
            weight = (1.0 / (num_twist_joints + 1.0)) * (index + 1)
            multiply_node.input2.set(weight)

            new_joint.ove.set(1)
            new_joint.ovc.set(13)
            joint_list.append(new_joint)

        return joint_list


def rename_human_ik_joint(  # pylint: disable=too-many-locals
    element: str = 'Character1',
    delete_human_ik: bool = True,
) -> None:
    """Rename HumanIK-generated joints to the studio naming convention."""

    def alpha_name(prefix: str, index: int) -> str:
        """Generate alphabetically suffixed joint name.

        Args:
            prefix: Base name for the joint (e.g., 'spineJ', 'neckJ')
            index: Zero-based index to convert to alpha suffix

        Returns:
            Formatted joint name like 'spineJa_JNT', 'spineJb_JNT', etc.
        """
        return f"{prefix}{name.get_alpha(index)}_JNT"

    spine_joints = pm.ls(f'{element}_Hips', f'{element}_Spine*')
    for index, joint in enumerate(spine_joints):
        pm.rename(joint, alpha_name('spineJ', index))

    neck_joints = pm.ls(f'{element}_Neck*')
    for index, joint in enumerate(neck_joints):
        pm.rename(joint, alpha_name('neckJ', index))

    head_joints = pm.ls(f'{element}_Head*')
    for index, joint in enumerate(head_joints):
        pm.rename(joint, alpha_name('headJ', index))

    jaw_joints = pm.ls(f'{element}_Jaw*')
    for index, joint in enumerate(jaw_joints):
        pm.rename(joint, alpha_name('jawJ', index))

    for side_label, prefix in (('Left', 'l_'), ('Right', 'r_')):
        side_nodes = pm.ls(f'{element}_{side_label}*')
        for joint in side_nodes:
            _, joint_suffix = joint.name().split('_', 1)
            new_name = f"{prefix}{joint_suffix.replace(side_label, '')}_JNT"
            pm.rename(joint, new_name)

        rename_sets = [
            (pm.ls(f'{prefix}Shoulder_JNT'), 'clavicleJ'),
            (pm.ls(f'{prefix}Arm_JNT', f'{prefix}ForeArm_JNT'), 'armJ'),
            (pm.ls(f'{prefix}*Hand_JNT'), 'handJ'),
            (pm.ls(f'{prefix}*HandThumb*_JNT'), 'fngThumbJ'),
            (pm.ls(f'{prefix}*HandIndex*_JNT'), 'fngIndexJ'),
            (pm.ls(f'{prefix}*HandMiddle*_JNT'), 'fngMiddleJ'),
            (pm.ls(f'{prefix}*HandRing*_JNT'), 'fngRingJ'),
            (pm.ls(f'{prefix}*HandPinky*_JNT'), 'fngPinkyJ'),
            (pm.ls(f'{prefix}UpLeg_JNT', f'{prefix}Leg_JNT'), 'legJ'),
            (pm.ls(f'{prefix}*Foot_JNT'), 'footJ'),
            (pm.ls(f'{prefix}*FootExtraFinger*_JNT'), 'toeThumbJ'),
            (pm.ls(f'{prefix}*FootIndex*_JNT'), 'toeIndexJ'),
            (pm.ls(f'{prefix}*FootMiddle*_JNT'), 'toeMiddleJ'),
            (pm.ls(f'{prefix}*FootRing*_JNT'), 'toeRingJ'),
            (pm.ls(f'{prefix}*FootPinky*_JNT'), 'toePinkyJ'),
        ]
        for joint_list, base_name in rename_sets:
            for index, joint in enumerate(joint_list):
                pm.rename(joint, alpha_name(f'{prefix}{base_name}', index))

    hips = pm.ls(f'{element}_Hips')
    if hips:
        end_joints = pm.ls(hips[0], type='joint', dagObjects=True, leaf=True)
        for joint in end_joints:
            pm.rename(joint, f"{joint.name()[:-5]}End_JNT")

    if delete_human_ik:
        hik_nodes = pm.ls(type=['HIKCharacterNode', 'HIKState2SK'])
        if hik_nodes:
            pm.delete(hik_nodes)



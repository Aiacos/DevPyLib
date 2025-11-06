"""Utilities to add stretch behaviour to IK handle chains."""

# pylint: disable=invalid-name

from __future__ import annotations

from typing import Any

import pymel.core as pm

from mayaLib.rigLib.utils import flexiplane, name, util

__all__ = ['StretchyIKChain']


def _ensure_node(target: Any) -> pm.PyNode:
    """Return the first PyNode for ``target`` or raise ``ValueError``."""
    nodes = pm.ls(target)
    if not nodes:
        raise ValueError(f'Node {target!r} does not exist.')
    return nodes[0]


def _build_distance_nodes(
    prefix: str,
    joints: list[pm.PyNode],
    ik_ctrl: pm.PyNode,
) -> tuple[pm.PyNode, pm.PyNode, pm.PyNode, pm.PyNode]:
    """Create a distance dimension measuring the span of the IK chain."""
    distance_shape = pm.distanceDimension(
        sp=joints[0].getTranslation(space='world'),
        ep=joints[-1].getTranslation(space='world'),
    )
    distance_transform = distance_shape.getParent()

    locators = pm.listConnections(distance_shape, s=True)
    start_loc = pm.rename(locators[0], f'{prefix}DistanceStart_LOC')
    end_loc = pm.rename(locators[1], f'{prefix}DistanceEnd_LOC')

    pm.pointConstraint(joints[0], start_loc)
    pm.pointConstraint(ik_ctrl, end_loc)

    return distance_shape, distance_transform, start_loc, end_loc


class StretchyIKChain:  # pylint: disable=too-few-public-methods,too-many-instance-attributes
    """Add stretch controls to an existing IK handle."""

    def __init__(  # pylint: disable=too-many-locals
        self,
        ik_handle,
        ik_ctrl,
        do_flexyplane: bool = True,
    ) -> None:
        """Initialize stretchy IK chain on existing IK handle.

        Adds stretch and squash functionality to an IK chain, allowing joints
        to extend beyond their normal length when the IK control moves away.
        Optionally adds a Flexiplane deformer for volume preservation.

        Args:
            ik_handle: Existing IK handle to make stretchy (name or PyNode)
            ik_ctrl: IK control that drives the stretch behavior (name or PyNode)
            do_flexyplane: Add Flexiplane for volume preservation. Defaults to True.

        Example:
            >>> stretchy = StretchyIkChain('arm_IKH', 'hand_CTRL')
        """
        ik_handle_node = _ensure_node(ik_handle)
        ik_ctrl_node = _ensure_node(ik_ctrl)

        prefix = name.remove_suffix(ik_handle_node.name())
        joint_list = pm.ikHandle(ik_handle_node, jointList=True, q=True)
        end_joint = pm.listRelatives(joint_list[-1], c=True, type='joint')
        if end_joint:
            joint_list.append(end_joint[0])
        joint_nodes = [pm.PyNode(joint) for joint in joint_list]

        distance_shape, distance_transform, start_loc, end_loc = _build_distance_nodes(
            prefix,
            joint_nodes,
            ik_ctrl_node,
        )

        multiply_divide = pm.shadingNode(
            'multiplyDivide',
            asUtility=True,
            n=f'{prefix}_multiplyDivide',
        )
        multiply_divide.operation.set(2)
        pm.connectAttr(distance_shape.distance, multiply_divide.input1X, f=True)

        total_distance = 0.0
        for start, end in zip(joint_nodes[:-1], joint_nodes[1:], strict=False):
            total_distance += util.get_distance(start, end)
        multiply_divide.input2X.set(total_distance if total_distance else 1.0)

        condition_node = pm.shadingNode('condition', asUtility=True, n=f'{prefix}_condition')
        condition_node.operation.set(2)
        pm.connectAttr(distance_shape.distance, condition_node.firstTerm, f=True)
        pm.connectAttr(multiply_divide.input2X, condition_node.secondTerm, f=True)
        pm.connectAttr(multiply_divide.outputX, condition_node.colorIfTrueR, f=True)

        for joint in joint_nodes[:-1]:
            pm.connectAttr(condition_node.outColorR, joint.scaleX, f=True)

        stretchy_group = pm.group(start_loc, end_loc, distance_transform, n=f'{prefix}Stretchy_GRP')
        stretchy_group.visibility.set(0)

        self.ik_handle = ik_handle_node
        self.ik_ctrl = ik_ctrl_node
        self.prefix = prefix
        self.joint_list = joint_nodes
        self.distance_shape = distance_shape
        self.multiply_divide = multiply_divide
        self.condition_node = condition_node
        self.stretchy_group = stretchy_group

        if do_flexyplane:
            self.do_flexy_plane(prefix)

    def get_stretchy_group(self) -> pm.PyNode:
        """Return the grouping node that contains the stretch system."""
        return self.stretchy_group

    def do_flexy_plane(self, prefix: str, stretchy: int = 1) -> None:
        """Add flexi-plane controls along the chain."""
        for index, joint in enumerate(self.joint_list[:-1]):
            flex = flexiplane.Flexiplane(f'{prefix}{index}')
            global_ctrl, ctrl_a, ctrl_b, _ = flex.get_controls()
            pm.pointConstraint([joint, self.joint_list[index + 1]], global_ctrl)
            pm.parentConstraint(joint, ctrl_a)
            pm.parentConstraint(self.joint_list[index + 1], ctrl_b)
            global_ctrl.enable.set(stretchy)
            pm.parent(flex.get_top_group(), self.stretchy_group)


if __name__ == '__main__':
    raise SystemExit('Invoke within Maya to construct stretchy IK chains.')

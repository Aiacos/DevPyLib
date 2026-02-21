"""Utilities for managing IK/FK switching with Maya IK handles.

This module provides two distinct capabilities:

- **Build-time wiring** (:func:`wire_ikfk_switch`): Creates the attribute network
  and visibility connections that let animators toggle between IK and FK.
- **Runtime snapping** (:class:`IKFKSwitch`): Reads the live scene graph to snap
  FK controls onto the IK pose (or vice-versa) when the animator flips the switch.
"""

from __future__ import annotations

import inspect
from collections.abc import Sequence

import pymel.core as pm

from mayaLib.rigLib.utils import util

__all__ = ["IKFKSwitch", "install_ikfk", "wire_ikfk_switch"]


def _get_single_output(node, **kwargs):
    """Return the first output connection of a node with optional filters."""
    outputs = node.outputs(**kwargs)
    if not outputs:
        raise ValueError(f"No outputs found for {node} with filters {kwargs}.")
    return outputs[0]


class IKFKSwitch:
    """Manage snapping and connections between IK and FK controls for a chain."""

    # pylint: disable=too-many-instance-attributes

    def __init__(
        self,
        ik_handle,
        forearm_mid_joint: bool = False,
        simple_ik: bool = False,
    ) -> None:
        """Create a new IKFKSwitch for the given handle.

        Args:
            ik_handle: The Maya IK handle to manage.
            forearm_mid_joint: Whether the chain contains an extra forearm joint.
            simple_ik: Whether the IK setup is a simple handle without foot roll groups.
        """
        self.ik_handle = pm.PyNode(ik_handle)
        self.simple_ik = simple_ik

        self.shoulder_joint = pm.listConnections(self.ik_handle, type="joint")[0]
        self.elbow_joint = _get_single_output(self.shoulder_joint, type="joint")

        if forearm_mid_joint:
            self.forearm_joint = _get_single_output(self.elbow_joint, type="joint")
            self.wrist_joint = _get_single_output(self.forearm_joint, type="joint")
        else:
            self.forearm_joint = None
            self.wrist_joint = _get_single_output(self.elbow_joint, type="joint")

        self.shoulder_fk_ctrl = self._extract_ctrl(self.shoulder_joint)
        self.elbow_fk_ctrl = self._extract_ctrl(self.elbow_joint)
        self.wrist_fk_ctrl = self._extract_ctrl(self.wrist_joint)

        if simple_ik:
            ik_constraint = pm.listConnections(self.ik_handle, type="constraint")[0]
            pole_constraint = pm.listConnections(
                self.ik_handle,
                type="poleVectorConstraint",
                et=True,
            )[0]
            self.ik_ctrl = util.get_driver_driven_from_constraint(ik_constraint)[0][0]
            self.pole_vector = util.get_driver_driven_from_constraint(pole_constraint)[0][0]
        else:
            peel_heel_grp = self.ik_handle.getParent()
            tippy_toe_grp = peel_heel_grp.getParent()
            move_grp = tippy_toe_grp.getParent()
            ik_constraint = pm.listConnections(move_grp, type="constraint")[0]

            pole_constraint = pm.listConnections(
                self.ik_handle,
                type="poleVectorConstraint",
                et=True,
            )[0]
            pole_vector_loc = util.get_driver_driven_from_constraint(pole_constraint)[0][0]
            pole_vector_constraint = pole_vector_loc.getChildren()[1]

            self.ik_ctrl = util.get_driver_driven_from_constraint(ik_constraint)[0][0]
            self.pole_vector = util.get_driver_driven_from_constraint(
                pole_vector_constraint,
            )[0][0]

        reverse_node = self.ik_handle.inputs(scn=True, type="reverse")[0]
        driver_loc = reverse_node.inputs(scn=True, plugs=True)[0]

        self.reverse_node = reverse_node
        self.driver_loc = driver_loc
        self.driver_attribute = driver_loc.inputs(scn=True, plugs=True)[0]

    @staticmethod
    def _extract_ctrl(joint):
        """Retrieve the driving control for a joint based on its constraint."""
        orient_constraint = joint.outputs(type="constraint")[0]
        return util.get_driver_driven_from_constraint(orient_constraint)[0][0]

    def snap_to_ik(self) -> None:
        """Align FK controls to match the IK pose."""
        pm.delete(pm.parentConstraint(self.wrist_fk_ctrl, self.ik_ctrl))
        pm.delete(pm.pointConstraint(self.elbow_fk_ctrl, self.pole_vector))

    def snap_to_fk(self) -> None:
        """Align IK controls to match the FK pose."""
        pm.delete(pm.orientConstraint(self.shoulder_joint, self.shoulder_fk_ctrl))
        pm.delete(pm.orientConstraint(self.elbow_joint, self.elbow_fk_ctrl))
        pm.delete(pm.orientConstraint(self.wrist_joint, self.wrist_fk_ctrl))

    def switch_ik_fk(self) -> None:
        """Toggle between IK and FK, snapping controls accordingly."""
        blend = self.ik_handle.ikBlend.get()
        self.disconnect()

        if blend == 0:
            pm.setAttr(self.driver_loc, 0)
            self.snap_to_fk()
            pm.displayInfo("Snap FK CTRL to IK")
        elif blend == 1:
            pm.setAttr(self.driver_loc, 0)
            self.snap_to_ik()
            pm.displayInfo("Snap IK CTRL to FK")

        self.reconnect()

    def add_script_job(self) -> int:
        """Create a scriptJob that listens for IK/FK attribute changes."""
        return pm.scriptJob(
            attributeChange=[self.driver_attribute, self.switch_ik_fk],
        )

    def disconnect(self) -> None:
        """Disconnect the driver attribute from the reverse node."""
        pm.disconnectAttr(self.driver_attribute, self.driver_loc)

    def reconnect(self) -> None:
        """Reconnect the driver attribute to the reverse node."""
        pm.connectAttr(self.driver_attribute, self.driver_loc)


def install_ikfk(ik_nodes: Sequence) -> None:
    """Install script nodes to auto-snap IK/FK across the supplied IK handles."""
    node_names = [str(node) for node in ik_nodes]
    ik_list = [pm.PyNode(node) for node in pm.ls(*node_names)] if node_names else []
    class_definition = inspect.getsource(IKFKSwitch)
    util_definition = inspect.getsource(util.get_driver_driven_from_constraint)

    commands: list[str] = [
        "import pymel.core as pm",
        util_definition,
        class_definition.replace("util.", ""),
    ]

    if ik_list:
        node_args = ",".join(f"'{node}'" for node in ik_list)
        commands.append(f"ik_list = pm.ls({node_args})")
    else:
        commands.append("ik_list = []")

    commands.extend(
        [
            "ik_instances = [IKFKSwitch(ik) for ik in ik_list]",
            "ik_script_jobs = [item.add_script_job() for item in ik_instances]",
        ],
    )

    pm.scriptNode(
        st=2,
        bs="\n".join(commands),
        n="switch_IKFK",
        stp="python",
    )
    pm.displayInfo("Installed IK/FK switch script node.")


# ---------------------------------------------------------------------------
# Build-time wiring
# ---------------------------------------------------------------------------


def wire_ikfk_switch(  # noqa: PLR0913
    prefix: str,
    part: str,
    visibility_ctrl: pm.PyNode,
    fk_limb_controls: Sequence,
    fk_limb_constraints: Sequence,
    fk_hand_controls: Sequence,
    fk_hand_constraints: Sequence,
    main_ik_ctrl,
    ik_handle: pm.PyNode,
    finger_controls: tuple[Sequence, Sequence],
    finger_ik_handles: Sequence,
    ball_ik_handles: Sequence,
    pole_vector_ctrl,
    hand_ik_orient_constraint: pm.PyNode,
) -> None:
    """Wire IK/FK switch attributes and visibility connections at rig-build time.

    Creates a shared ``switchIKFK_LOC`` locator with per-limb attributes,
    reverse nodes, and visibility/blend connections so that animators can
    toggle between IK and FK from a single control.

    Args:
        prefix: Naming prefix for this limb (e.g. ``"l_shoulder1"``).
        part: Part label (``"Hand"`` or ``"Foot"``).
        visibility_ctrl: The animator-facing control that drives the switch.
        fk_limb_controls: FK controls for the main limb chain.
        fk_limb_constraints: Orient constraints driving limb joints from FK.
        fk_hand_controls: FK controls for fingers/toes.
        fk_hand_constraints: Orient constraints driving finger/toe joints.
        main_ik_ctrl: Main IK control instance.
        ik_handle: IK handle for the limb.
        finger_controls: Tuple of (ball controls, toe IK controls).
        finger_ik_handles: IK handles for fingers/toes.
        ball_ik_handles: IK handles for ball joints.
        pole_vector_ctrl: Pole vector control instance.
        hand_ik_orient_constraint: Orient constraint on the hand/foot joint.
    """
    switch_locator = _create_switch_locator()

    control_attr = prefix
    part_control_attr = f"{prefix}{part}"

    # Add switch attributes to both the locator and the visibility control
    for node, default_part in [
        (switch_locator, 1 if part == "Hand" else 0),
        (visibility_ctrl, 0),
    ]:
        if not node.hasAttr(control_attr):
            pm.addAttr(
                node,
                longName=control_attr,
                attributeType="double",
                defaultValue=0,
                minValue=0,
                maxValue=1,
                k=True,
            )
        if not node.hasAttr(part_control_attr):
            pm.addAttr(
                node,
                longName=part_control_attr,
                attributeType="double",
                defaultValue=default_part if node is switch_locator else 0,
                minValue=0,
                maxValue=1,
                k=True,
            )

    pm.connectAttr(
        f"{visibility_ctrl}.{control_attr}",
        f"{switch_locator}.{control_attr}",
        f=True,
    )
    pm.connectAttr(
        f"{visibility_ctrl}.{part_control_attr}",
        f"{switch_locator}.{part_control_attr}",
        f=True,
    )

    # Create reverse nodes
    reverse_node = pm.shadingNode(
        "reverse", asUtility=True, n=f"{prefix}ReverseNode"
    )
    part_reverse_node = pm.shadingNode(
        "reverse", asUtility=True, n=f"{prefix}{part}ReverseNode"
    )
    pm.connectAttr(f"{switch_locator}.{control_attr}", reverse_node.inputX)
    pm.connectAttr(f"{switch_locator}.{part_control_attr}", part_reverse_node.inputX)

    _wire_ik_visibility(
        reverse_node,
        part_reverse_node,
        main_ik_ctrl,
        ik_handle,
        finger_controls,
        finger_ik_handles,
        ball_ik_handles,
        pole_vector_ctrl,
        hand_ik_orient_constraint,
    )
    _wire_fk_visibility(
        switch_locator,
        control_attr,
        part_control_attr,
        reverse_node,
        main_ik_ctrl,
        fk_limb_controls,
        fk_limb_constraints,
        fk_hand_controls,
        fk_hand_constraints,
    )


def _create_switch_locator() -> pm.PyNode:
    """Get or create the shared ``switchIKFK_LOC`` locator.

    The locator is parented under ``rig_GRP``, hidden, and locked.
    """
    if not pm.objExists("switchIKFK_LOC"):
        switch_locator = pm.spaceLocator(n="switchIKFK_LOC")[0]
        pm.parent(switch_locator, "rig_GRP")
        pm.hide(switch_locator)
        util.lock_and_hide_all(switch_locator)
    else:
        switch_locator = pm.ls("switchIKFK_LOC")[0]
    return switch_locator


def _wire_ik_visibility(
    reverse_node: pm.PyNode,
    part_reverse_node: pm.PyNode,
    main_ik_ctrl,
    ik_handle: pm.PyNode,
    finger_controls: tuple[Sequence, Sequence],
    finger_ik_handles: Sequence,
    ball_ik_handles: Sequence,
    pole_vector_ctrl,
    hand_ik_orient_constraint: pm.PyNode,
) -> None:
    """Connect IK control visibility and blend weights to the reverse node."""
    pm.connectAttr(reverse_node.outputX, main_ik_ctrl.get_top().visibility)
    pm.connectAttr(reverse_node.outputX, ik_handle.ikBlend)

    ik_constraint_attr = pm.listConnections(
        hand_ik_orient_constraint.target[1].targetWeight, p=True, s=True
    )[0]
    pm.connectAttr(reverse_node.outputX, ik_constraint_attr)

    for ctrl in finger_controls[0]:
        pm.connectAttr(part_reverse_node.outputX, ctrl.get_top().visibility)
    for ctrl in finger_controls[1]:
        pm.connectAttr(part_reverse_node.outputX, ctrl.get_top().visibility)

    for ik_node in finger_ik_handles:
        pm.connectAttr(part_reverse_node.outputX, ik_node.ikBlend)
    for ball_ik in ball_ik_handles:
        pm.connectAttr(part_reverse_node.outputX, ball_ik.ikBlend)

    pm.connectAttr(reverse_node.outputX, pole_vector_ctrl.get_top().visibility)


def _wire_fk_visibility(
    switch_locator: pm.PyNode,
    control_attr: str,
    part_control_attr: str,
    reverse_node: pm.PyNode,
    main_ik_ctrl,
    fk_limb_controls: Sequence,
    fk_limb_constraints: Sequence,
    fk_hand_controls: Sequence,
    fk_hand_constraints: Sequence,
) -> None:
    """Connect FK control visibility and constraint weights to switch attributes."""
    for ctrl in fk_limb_controls:
        pm.connectAttr(f"{switch_locator}.{control_attr}", ctrl.get_top().visibility)
    for constraint in fk_limb_constraints:
        attr = pm.listConnections(
            constraint.target[0].targetWeight, p=True, s=True
        )[0]
        pm.connectAttr(f"{switch_locator}.{control_attr}", attr)

    for ctrl in fk_hand_controls:
        pm.connectAttr(
            f"{switch_locator}.{part_control_attr}", ctrl.get_top().visibility
        )
    for constraint in fk_hand_constraints:
        attr = pm.listConnections(
            constraint.target[0].targetWeight, p=True, s=True
        )[0]
        pm.connectAttr(f"{switch_locator}.{part_control_attr}", attr)

    if fk_limb_controls and fk_hand_controls and fk_hand_constraints:
        fk_finger_constraint = pm.parentConstraint(
            main_ik_ctrl.get_control(),
            fk_hand_controls[0].get_top().getParent(),
            mo=True,
        )
        target_names = fk_finger_constraint.getTargetList()
        pm.connectAttr(
            reverse_node.outputX,
            f"{fk_finger_constraint}.{target_names[1]}W1",
            f=True,
        )
        pm.connectAttr(
            f"{switch_locator}.{control_attr}",
            f"{fk_finger_constraint}.{target_names[0]}W0",
            f=True,
        )


def _demo() -> None:
    """Quick smoke test when executed as a script."""
    ik_list = pm.ls("l_shoulder1_IKH", "r_shoulder1_IKH", "l_hip1_IKH", "r_hip1_IKH")
    switches = [IKFKSwitch(ik) for ik in ik_list]
    jobs = [switch.add_script_job() for switch in switches]
    pm.displayInfo(str(jobs))


if __name__ == "__main__":
    _demo()

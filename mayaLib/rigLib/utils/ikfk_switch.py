"""Utilities for managing IK/FK switching with Maya IK handles."""

from __future__ import annotations

import inspect
from collections.abc import Sequence

import pymel.core as pm

from mayaLib.rigLib.utils import util

__all__ = ["IKFKSwitch", "install_ikfk"]


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

        self.shoulder_joint = pm.listConnections(self.ik_handle, type='joint')[0]
        self.elbow_joint = _get_single_output(self.shoulder_joint, type='joint')

        if forearm_mid_joint:
            self.forearm_joint = _get_single_output(self.elbow_joint, type='joint')
            self.wrist_joint = _get_single_output(self.forearm_joint, type='joint')
        else:
            self.forearm_joint = None
            self.wrist_joint = _get_single_output(self.elbow_joint, type='joint')

        self.shoulder_fk_ctrl = self._extract_ctrl(self.shoulder_joint)
        self.elbow_fk_ctrl = self._extract_ctrl(self.elbow_joint)
        self.wrist_fk_ctrl = self._extract_ctrl(self.wrist_joint)

        if simple_ik:
            ik_constraint = pm.listConnections(self.ik_handle, type='constraint')[0]
            pole_constraint = pm.listConnections(
                self.ik_handle,
                type='poleVectorConstraint',
                et=True,
            )[0]
            self.ik_ctrl = util.get_driver_driven_from_constraint(ik_constraint)[0][0]
            self.pole_vector = util.get_driver_driven_from_constraint(pole_constraint)[0][0]
        else:
            peel_heel_grp = self.ik_handle.getParent()
            tippy_toe_grp = peel_heel_grp.getParent()
            move_grp = tippy_toe_grp.getParent()
            ik_constraint = pm.listConnections(move_grp, type='constraint')[0]

            pole_constraint = pm.listConnections(
                self.ik_handle,
                type='poleVectorConstraint',
                et=True,
            )[0]
            pole_vector_loc = util.get_driver_driven_from_constraint(pole_constraint)[0][0]
            pole_vector_constraint = pole_vector_loc.getChildren()[1]

            self.ik_ctrl = util.get_driver_driven_from_constraint(ik_constraint)[0][0]
            self.pole_vector = util.get_driver_driven_from_constraint(
                pole_vector_constraint,
            )[0][0]

        reverse_node = self.ik_handle.inputs(scn=True, type='reverse')[0]
        driver_loc = reverse_node.inputs(scn=True, plugs=True)[0]

        self.reverse_node = reverse_node
        self.driver_loc = driver_loc
        self.driver_attribute = driver_loc.inputs(scn=True, plugs=True)[0]

    @staticmethod
    def _extract_ctrl(joint):
        """Retrieve the driving control for a joint based on its constraint."""
        orient_constraint = joint.outputs(type='constraint')[0]
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
            pm.displayInfo('Snap FK CTRL to IK')
        elif blend == 1:
            pm.setAttr(self.driver_loc, 0)
            self.snap_to_ik()
            pm.displayInfo('Snap IK CTRL to FK')

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
        'import pymel.core as pm',
        util_definition,
        class_definition.replace('util.', ''),
    ]

    if ik_list:
        node_args = ','.join(f"'{node}'" for node in ik_list)
        commands.append(f'ik_list = pm.ls({node_args})')
    else:
        commands.append('ik_list = []')

    commands.extend(
        [
            'ik_instances = [IKFKSwitch(ik) for ik in ik_list]',
            'ik_script_jobs = [item.add_script_job() for item in ik_instances]',
        ],
    )

    pm.scriptNode(
        st=2,
        bs='\n'.join(commands),
        n='switch_IKFK',
        stp='python',
    )
    pm.displayInfo('Installed IK/FK switch script node.')


def _demo() -> None:
    """Quick smoke test when executed as a script."""
    ik_list = pm.ls('l_shoulder1_IKH', 'r_shoulder1_IKH', 'l_hip1_IKH', 'r_hip1_IKH')
    switches = [IKFKSwitch(ik) for ik in ik_list]
    jobs = [switch.add_script_job() for switch in switches]
    pm.displayInfo(str(jobs))


if __name__ == "__main__":
    _demo()

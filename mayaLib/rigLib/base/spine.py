"""Spine rig construction helpers."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, cast

import pymel.core as pm

from mayaLib.rigLib.base import module
from mayaLib.rigLib.utils import control, parameter_resolution

__all__ = ["Spine", "create_locator_reference_positions"]


def _as_pynode(target: pm.PyNode | str | None) -> pm.PyNode | None:
    """Return the first matching PyNode for the given target if available."""
    if target in {None, ""}:
        return None
    nodes = pm.ls(target)
    return nodes[0] if nodes else None


def create_locator_reference_positions(
    spine_joints: Sequence[str],
    *,
    prefix: str = "spine",
) -> tuple[pm.PyNode, pm.PyNode, pm.PyNode]:
    """Create reference locators for body, chest, and pelvis positions.

    Args:
        spine_joints: Ordered list of spine joints.
        prefix: Prefix for new locator names.

    Returns:
        Tuple containing the body, chest, and pelvis locator nodes.
    """
    joint_nodes = pm.ls(spine_joints)
    if not joint_nodes:
        raise ValueError("spine_joints must contain valid Maya joints.")

    number_of_joints = len(joint_nodes)
    mid_index = number_of_joints // 2

    name_prefix = prefix if prefix and prefix != "spine" else ""
    body_name = f"{name_prefix}Body_LOC" if name_prefix else "body_LOC"
    chest_name = f"{name_prefix}Chest_LOC" if name_prefix else "chest_LOC"
    pelvis_name = f"{name_prefix}Pelvis_LOC" if name_prefix else "pelvis_LOC"

    body_locator = pm.spaceLocator(n=body_name)
    chest_locator = pm.spaceLocator(n=chest_name)
    pelvis_locator = pm.spaceLocator(n=pelvis_name)

    pm.delete(pm.parentConstraint(joint_nodes[0], pelvis_locator))
    pm.delete(pm.parentConstraint(joint_nodes[-1], chest_locator))

    if number_of_joints % 2 == 0 and number_of_joints > 1:
        pm.delete(
            pm.pointConstraint(
                [joint_nodes[mid_index - 1], joint_nodes[mid_index]],
                body_locator,
            )
        )
    else:
        pm.delete(pm.pointConstraint(joint_nodes[mid_index], body_locator))

    return body_locator, chest_locator, pelvis_locator


class Spine:
    """Construct a spline IK driven spine module."""

    def __init__(  # pylint: disable=too-many-arguments,too-many-locals,too-many-statements
        self,
        spine_joints: Sequence[str] | None = None,
        root_joint: str | None = None,
        *,
        prefix: str | None = None,
        rig_scale: float | None = None,
        base_rig: module.Module | None = None,
        body_locator: pm.PyNode | str | None = None,
        chest_locator: pm.PyNode | str | None = None,
        pelvis_locator: pm.PyNode | str | None = None,
        **legacy_kwargs: Any,
    ) -> None:
        """Initialise the spine rig builder."""
        legacy_kwargs = dict(legacy_kwargs)
        spine_joints = parameter_resolution.resolve_optional(
            spine_joints,
            legacy_kwargs,
            ("spineJoints",),
            None,
        )
        if not spine_joints:
            raise ValueError("spine_joints is required.")

        root_joint = parameter_resolution.resolve_optional(
            root_joint,
            legacy_kwargs,
            ("rootJnt",),
            spine_joints[0],
        )
        prefix = cast(
            str, parameter_resolution.resolve_optional(prefix, legacy_kwargs, ("prefix",), "spine")
        )
        rig_scale = parameter_resolution.resolve_optional(
            rig_scale, legacy_kwargs, ("rigScale",), 1.0
        )
        base_rig = parameter_resolution.resolve_optional(
            base_rig, legacy_kwargs, ("baseRig",), None
        )
        body_locator = parameter_resolution.resolve_optional(
            body_locator,
            legacy_kwargs,
            ("bodyLocator",),
            None,
        )
        chest_locator = parameter_resolution.resolve_optional(
            chest_locator,
            legacy_kwargs,
            ("chestLocator",),
            None,
        )
        pelvis_locator = parameter_resolution.resolve_optional(
            pelvis_locator,
            legacy_kwargs,
            ("pelvisLocator",),
            None,
        )

        if legacy_kwargs:
            raise ValueError(f"Unexpected arguments for Spine: {tuple(legacy_kwargs.keys())}")

        self.rig_module = module.Module(prefix=prefix, base_obj=base_rig)
        self.prefix = prefix

        body_locator_node = _as_pynode(body_locator)
        chest_locator_node = _as_pynode(chest_locator)
        pelvis_locator_node = _as_pynode(pelvis_locator)

        created_locators = []
        if not (body_locator_node and chest_locator_node and pelvis_locator_node):
            body_locator_node, chest_locator_node, pelvis_locator_node = (
                create_locator_reference_positions(spine_joints, prefix=prefix)
            )
            created_locators = [
                body_locator_node,
                chest_locator_node,
                pelvis_locator_node,
            ]

        (  # pylint: disable=unbalanced-tuple-unpacking
            spine_ik,
            _,
            spine_curve,
        ) = pm.ikHandle(
            n=f"{prefix}_IKH",
            sol="ikSplineSolver",
            sj=spine_joints[0],
            ee=spine_joints[-1],
            createCurve=True,
            numSpans=2,
        )
        spine_curve = pm.rename(spine_curve, f"{prefix}_CRV")

        clusters = []
        for index, cv in enumerate(pm.ls(f"{spine_curve}.cv[*]", fl=True), start=1):
            cluster = pm.cluster(cv, n=f"{prefix}Cluster{index}")[1]
            clusters.append(cluster)
        pm.hide(clusters)
        pm.parent(spine_curve, self.rig_module.parts_no_trans_group)

        self.body_control = control.Control(
            prefix=f"{prefix}Body",
            translate_to=body_locator_node,
            rotate_to=spine_joints[-1],
            scale=rig_scale * 4,
            parent=self.rig_module.controls_group,
            shape="spine",
        )
        chest_control = control.Control(
            prefix=f"{prefix}Chest",
            translate_to=chest_locator_node,
            rotate_to=spine_joints[-1],
            scale=rig_scale * 6,
            parent=self.body_control.C,
            shape="chest",
        )
        pelvis_control = control.Control(
            prefix=f"{prefix}Pelvis",
            translate_to=pelvis_locator_node,
            rotate_to=pelvis_locator_node,
            scale=rig_scale * 6,
            parent=self.body_control.C,
            shape="hip",
        )
        middle_control = control.Control(
            prefix=f"{prefix}Middle",
            translate_to=clusters[2],
            scale=rig_scale * 3,
            parent=self.body_control.C,
            shape="sphere",
            lock_channels=["r"],
        )

        pm.parentConstraint(
            chest_control.C,
            pelvis_control.C,
            middle_control.Off,
            sr=["x", "y", "z"],
            mo=True,
        )

        pm.parent(clusters[3:], chest_control.C)
        pm.parent(clusters[2], middle_control.C)
        pm.parent(clusters[:2], pelvis_control.C)
        pm.orientConstraint(chest_control.C, spine_joints[-1], mo=True)

        pm.hide(spine_ik)
        pm.parent(spine_ik, self.rig_module.parts_no_trans_group)

        pm.setAttr(f"{spine_ik}.dTwistControlEnable", 1)
        pm.setAttr(f"{spine_ik}.dWorldUpType", 4)
        pm.connectAttr(
            f"{chest_control.C}.worldMatrix[0]",
            f"{spine_ik}.dWorldUpMatrixEnd",
        )
        pm.connectAttr(
            f"{pelvis_control.C}.worldMatrix[0]",
            f"{spine_ik}.dWorldUpMatrix",
        )

        root_joint_node = _as_pynode(root_joint)
        if not root_joint_node:
            raise ValueError("root_joint must reference an existing Maya node.")
        pm.parentConstraint(pelvis_control.C, root_joint_node, mo=True)

        if created_locators:
            pm.delete(created_locators)

        self.created_locators = created_locators
        self.body_ctrl = self.body_control

    def get_module_dict(self) -> dict[str, Any]:
        """Return rig module bookkeeping data."""
        return {
            "module": self.rig_module,
            "body_ctrl": self.body_control,
            "body_control": self.body_control,
        }

    def make_control_locator_reference_position(
        self, spine_joints: Sequence[str]
    ) -> tuple[pm.PyNode, pm.PyNode, pm.PyNode]:
        """Deprecated helper retained for compatibility."""
        return create_locator_reference_positions(spine_joints, prefix=self.prefix)


Spine.getModuleDict = Spine.get_module_dict
Spine.makeControlLocatorReferencePosition = Spine.make_control_locator_reference_position

if __name__ == "__main__":
    raise SystemExit("Invoke within Maya to construct spine rigs.")

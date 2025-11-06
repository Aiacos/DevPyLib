"""Neck rig construction helpers."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, cast

import pymel.core as pm

from mayaLib.rigLib.base import module
from mayaLib.rigLib.utils import control, parameter_resolution

__all__ = ["Neck", "create_neck_spline"]


def create_neck_spline(
    prefix: str,
    neck_joints: Sequence[str],
) -> tuple[pm.PyNode, pm.PyNode, pm.PyNode]:
    """Create a spline IK handle for the provided neck joint chain."""
    (neck_ik, effector, neck_curve) = pm.ikHandle(  # pylint: disable=unbalanced-tuple-unpacking
        n=f"{prefix}_IKH",
        sol="ikSplineSolver",
        sj=neck_joints[0],
        ee=neck_joints[-1],
        createCurve=True,
        numSpans=2,
    )
    renamed_curve = pm.rename(neck_curve, f"{prefix}_CRV")
    return neck_ik, effector, renamed_curve


class Neck:  # pylint: disable=too-many-instance-attributes,too-few-public-methods
    """Construct a spline IK driven neck module."""

    def __init__(  # pylint: disable=too-many-arguments,too-many-locals,too-many-statements
        self,
        neck_joints: Sequence[str] | None = None,
        head_joint: str | None = None,
        *,
        prefix: str | None = None,
        rig_scale: float | None = None,
        base_rig: module.Module | None = None,
        **legacy_kwargs: Any,
    ) -> None:
        """Initialise the neck rig builder."""
        legacy_kwargs = dict(legacy_kwargs)
        neck_joints = parameter_resolution.resolve_required(
            neck_joints,
            legacy_kwargs,
            ("neckJoints",),
            "neck_joints",
        )
        head_joint = parameter_resolution.resolve_required(
            head_joint,
            legacy_kwargs,
            ("headJnt",),
            "head_joint",
        )
        prefix = cast(
            str, parameter_resolution.resolve_optional(prefix, legacy_kwargs, ("prefix",), "neck")
        )
        rig_scale = parameter_resolution.resolve_optional(
            rig_scale, legacy_kwargs, ("rigScale",), 1.0
        )
        base_rig = parameter_resolution.resolve_optional(
            base_rig, legacy_kwargs, ("baseRig",), None
        )

        if legacy_kwargs:
            raise ValueError(f"Unexpected arguments for Neck: {tuple(legacy_kwargs.keys())}")

        self.rig_module = module.Module(prefix=prefix, base_obj=base_rig)

        neck_joint_nodes = pm.ls(neck_joints)
        if not neck_joint_nodes:
            raise ValueError("neck_joints must reference existing Maya joints.")
        head_joint_node = pm.ls(head_joint)
        if not head_joint_node:
            raise ValueError("head_joint must reference an existing Maya joint.")
        head_joint_node = head_joint_node[0]

        neck_ik, _, neck_curve = create_neck_spline(prefix, neck_joint_nodes)
        curve_cvs = pm.ls(f"{neck_curve}.cv[*]", fl=True)
        clusters = []
        for index, cv in enumerate(curve_cvs, start=1):
            cluster = pm.cluster(cv, n=f"{prefix}Cluster{index}")[1]
            clusters.append(cluster)
        pm.hide(clusters)
        pm.parent(neck_curve, self.rig_module.parts_no_trans_group)

        self.body_attach_group = pm.group(
            n=f"{prefix}BodyAttach_GRP",
            em=True,
            p=self.rig_module.parts_group,
        )
        self.base_attach_group = pm.group(
            n=f"{prefix}BaseAttach_GRP",
            em=True,
            p=self.rig_module.parts_group,
        )

        pm.delete(pm.pointConstraint(neck_joint_nodes[0], self.base_attach_group))

        head_main_ctrl = control.Control(
            prefix=f"{prefix}HeadMain",
            translate_to=neck_joint_nodes[-1],
            rotate_to=head_joint_node,
            scale=rig_scale * 5,
            parent=self.rig_module.controls_group,
            shape="head",
        )
        head_local_ctrl = control.Control(
            prefix=f"{prefix}HeadLocal",
            translate_to=head_joint_node,
            rotate_to=head_joint_node,
            scale=rig_scale * 4,
            parent=head_main_ctrl.C,
            shape="circleX",
            lock_channels=["t"],
        )
        middle_ctrl = control.Control(
            prefix=f"{prefix}Middle",
            translate_to=clusters[2],
            rotate_to=neck_joint_nodes[2],
            scale=rig_scale * 4,
            parent=self.rig_module.controls_group,
            shape="circleX",
            lock_channels=["r"],
        )

        pm.parentConstraint(
            head_main_ctrl.C,
            self.base_attach_group,
            middle_ctrl.Off,
            sr=["x", "y", "z"],
            mo=True,
        )
        pm.orientConstraint(self.base_attach_group, middle_ctrl.Off, mo=True)
        pm.parentConstraint(self.body_attach_group, head_main_ctrl.Off, mo=True)

        pm.parent(clusters[3:], head_main_ctrl.C)
        pm.parent(clusters[2], middle_ctrl.C)
        pm.parent(clusters[:2], self.base_attach_group)

        pm.orientConstraint(head_local_ctrl.C, head_joint_node, mo=True)

        pm.hide(neck_ik)
        pm.parent(neck_ik, self.rig_module.parts_no_trans_group)

        pm.setAttr(f"{neck_ik}.dTwistControlEnable", 1)
        pm.setAttr(f"{neck_ik}.dWorldUpType", 4)
        pm.connectAttr(
            f"{head_main_ctrl.C}.worldMatrix[0]",
            f"{neck_ik}.dWorldUpMatrixEnd",
        )
        pm.connectAttr(
            f"{self.base_attach_group}.worldMatrix[0]",
            f"{neck_ik}.dWorldUpMatrix",
        )

        self.head_main_control = head_main_ctrl
        self.head_local_control = head_local_ctrl
        self.middle_control = middle_ctrl
        self.neck_ik = neck_ik
        self.neck_curve = neck_curve
        self.neck_clusters = clusters
        self.created_locators = []

    def get_module_dict(self) -> dict[str, Any]:
        """Return rig module bookkeeping data."""
        return {
            "module": self.rig_module,
            "base_attach_grp": self.base_attach_group,
            "body_attach_grp": self.body_attach_group,
        }


Neck.getModuleDict = Neck.get_module_dict

if __name__ == "__main__":
    raise SystemExit("Invoke within Maya to construct neck rigs.")

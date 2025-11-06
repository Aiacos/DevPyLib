
"""Spline IK chain builder utilities."""

# pylint: disable=invalid-name

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, cast

import pymel.core as pm

from mayaLib.rigLib.base import module
from mayaLib.rigLib.utils import control, deform, dynamic, name, parameter_resolution

__all__ = ['IKChain']


def _as_curve_node(curve: str | pm.PyNode) -> pm.PyNode:
    """Return the curve PyNode, ensuring the object exists."""
    nodes = pm.ls(curve)
    if not nodes:
        raise ValueError('Provided curve does not exist.')
    return nodes[0]


def _duplicate_curve(curve: pm.PyNode, name_suffix: str) -> pm.PyNode:
    """Return a duplicate of the provided curve with suffix applied."""
    duplicated = pm.duplicate(curve, n=f'{curve}_copy')[0]
    return pm.rename(duplicated, name_suffix)


class IKChain:  # pylint: disable=too-many-instance-attributes,too-few-public-methods,too-many-arguments
    """Construct a spline IK chain with optional dynamic motion."""

    def __init__(  # pylint: disable=too-many-arguments,too-many-locals,too-many-statements
        self,
        chain_joints: Sequence[str] | None = None,
        *,
        prefix: str | None = None,
        rig_scale: float | None = None,
        do_dynamic: bool | None = None,
        smallest_scale_percent: float | None = None,
        fk_parenting: bool | None = None,
        base_rig: module.Base | None = None,
        **legacy_kwargs: Any,
    ) -> None:
        """Initialise the IK chain rig builder."""
        legacy_kwargs = dict(legacy_kwargs)
        chain_joints = parameter_resolution.resolve_required(
            chain_joints,
            legacy_kwargs,
            ('chainJoints',),
            'chain_joints',
        )
        prefix = cast(str, parameter_resolution.resolve_optional(prefix, legacy_kwargs, ('prefix',), 'tail'))
        rig_scale = float(parameter_resolution.resolve_optional(rig_scale, legacy_kwargs, ('rigScale',), 1.0))
        do_dynamic = bool(parameter_resolution.resolve_optional(do_dynamic, legacy_kwargs, ('doDynamic',), False))
        smallest_scale_percent = float(
            parameter_resolution.resolve_optional(
                smallest_scale_percent,
                legacy_kwargs,
                ('smallestScalePercent',),
                0.1,
            )
        )
        fk_parenting = bool(
            parameter_resolution.resolve_optional(fk_parenting, legacy_kwargs, ('fkParenting',), True)
        )
        base_rig = parameter_resolution.resolve_optional(base_rig, legacy_kwargs, ('baseRig',), None)

        if legacy_kwargs:
            raise ValueError(
                f'Unexpected arguments for IKChain: {tuple(legacy_kwargs.keys())}'
            )

        self.rig_module = module.Module(prefix=prefix, base_obj=base_rig)

        joint_nodes = pm.ls(chain_joints)
        if len(joint_nodes) < 2:
            raise ValueError('chain_joints must contain at least two joints.')

        collision_point = len(joint_nodes)

        (
            chain_ik,
            _,
            chain_curve,
        ) = pm.ikHandle(
            n=f'{prefix}_IKH',
            sol='ikSplineSolver',
            sj=joint_nodes[0],
            ee=joint_nodes[-1],
            createCurve=True,
            numSpans=collision_point,
        )
        chain_curve = pm.rename(chain_curve, f'{prefix}_CRV')
        control_curve = pm.duplicate(chain_curve, n=f'{prefix}Ctrl_CRV')[0]

        chain_curve_cvs = pm.ls(f'{control_curve}.cv[*]', fl=True)
        clusters = []
        for index, cv in enumerate(chain_curve_cvs, start=1):
            cluster = pm.cluster(cv, n=f'{prefix}Cluster{index}')[1]
            clusters.append(cluster)
        pm.hide(clusters)

        pm.parent(chain_curve, self.rig_module.parts_no_trans_group)
        pm.parent(control_curve, self.rig_module.parts_no_trans_group)

        self.base_attach_group = pm.group(
            n=f'{prefix}BaseAttach_GRP',
            em=True,
            p=self.rig_module.parts_group,
        )
        pm.delete(pm.pointConstraint(joint_nodes[0], self.base_attach_group))

        chain_controls = []
        control_scale_increment = (1.0 - smallest_scale_percent) / len(clusters)
        main_ctrl_scale = 1.0

        for index, cluster in enumerate(clusters):
            ctrl_scale = rig_scale * main_ctrl_scale * (1.0 - (index * control_scale_increment))
            ctrl = control.Control(
                prefix=f'{prefix}{index + 1}',
                translate_to=cluster,
                scale=ctrl_scale,
                parent=self.rig_module.controls_group,
                shape='sphere',
            )
            chain_controls.append(ctrl)

        if fk_parenting:
            for control_a, control_b in zip(chain_controls[1:], chain_controls[:-1], strict=False):
                pm.parent(control_a.Off, control_b.C)

        for cluster, ctrl in zip(clusters, chain_controls, strict=False):
            pm.parent(cluster, ctrl.C)

        pm.parentConstraint(self.base_attach_group, chain_controls[0].Off, mo=True)

        pm.hide(chain_ik)
        pm.parent(chain_ik, self.rig_module.parts_no_trans_group)

        twist_attr = 'twist'
        if not chain_controls[-1].C.hasAttr(twist_attr):
            pm.addAttr(chain_controls[-1].C, ln=twist_attr, k=True)
        pm.connectAttr(
            f'{chain_controls[-1].C}.{twist_attr}',
            f'{chain_ik}.twist',
        )

        self.chain_curve = chain_curve
        self.control_curve = control_curve

        if do_dynamic:
            self.dyn_curve = self.make_dynamic(
                prefix,
                base_rig,
                self.rig_module,
                chain_controls,
                clusters,
            )
            deform.blend_shape_deformer(
                self.dyn_curve.get_input_curve(),
                [self.control_curve],
                node_name=f'{prefix}BlendShape',
                front_of_chain=True,
            )
            deform.blend_shape_deformer(
                self.chain_curve,
                [self.dyn_curve.get_output_curve()],
                node_name=f'{prefix}BlendShape',
                front_of_chain=True,
            )
        else:
            deform.blend_shape_deformer(
                self.chain_curve,
                [self.control_curve],
                node_name=f'{prefix}BlendShape',
                front_of_chain=True,
            )

        self.chain_controls = chain_controls

    def get_module_dict(self) -> dict[str, Any]:
        """Return rig module bookkeeping data."""
        return {
            'module': self.rig_module,
            'base_attach_grp': self.base_attach_group,
        }

    def make_dynamic(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        prefix: str,
        base_rig: module.Base | None,
        base_module: module.Module,
        chain_controls: Sequence[control.Control],
        clusters: Sequence[pm.PyNode],
    ):
        """Create the dynamic curve system for this IK chain."""
        del chain_controls, clusters  # Legacy compatibility; stored for future use.
        dynamic_curve_name = f"{name.remove_suffix(pm.ls(self.chain_curve)[0].shortName())}_CRV"
        dynamic_curve_base = pm.duplicate(self.chain_curve, n=dynamic_curve_name)
        pm.parent(dynamic_curve_base, w=True)

        dyn_curve = dynamic.DynamicCurve(dynamic_curve_base, prefix=prefix, base_rig=base_rig)
        pm.parent(dyn_curve.get_system_group(), base_module.parts_no_trans_group)
        return dyn_curve


if __name__ == "__main__":
    raise SystemExit('Invoke within Maya to construct IK chains.')

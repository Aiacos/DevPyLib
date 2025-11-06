
"""Face rig construction helpers."""

from __future__ import annotations

from typing import Any, Iterable, cast

import pymel.core as pm

from mayaLib.rigLib.base import module
from mayaLib.rigLib.utils import (
    control,
    deform,
    follow_ctrl,
    parameter_resolution,
    skin,
)

__all__ = ['Face']


def _as_single_node(target: Any, label: str) -> pm.PyNode:
    """Return the first matching PyNode for ``target`` or raise ``ValueError``."""
    nodes = pm.ls(target)
    if not nodes:
        raise ValueError(f'{label} must reference an existing Maya node.')
    return nodes[0]


class Face:  # pylint: disable=too-many-instance-attributes,too-few-public-methods
    """Construct facial deformation and control setups."""

    def __init__(  # pylint: disable=too-many-arguments,too-many-locals,too-many-statements
        self,
        cv_list: Iterable[str] | None = None,
        skin_geo: str | None = None,
        *,
        prefix: str | None = None,
        head_joint: str | None = None,
        points_number: int | None = None,
        scale: float | None = None,
        base_rig: module.Base | None = None,
        **legacy_kwargs: Any,
    ) -> None:
        """Initialise the facial rig builder."""
        legacy_kwargs = dict(legacy_kwargs)
        cv_list = parameter_resolution.resolve_required(
            cv_list,
            legacy_kwargs,
            ('cvList',),
            'cv_list',
        )
        skin_geo = parameter_resolution.resolve_required(
            skin_geo,
            legacy_kwargs,
            ('skinGeo',),
            'skin_geo',
        )
        prefix = cast(str, parameter_resolution.resolve_optional(prefix, legacy_kwargs, ('prefix',), 'face'))
        head_joint = parameter_resolution.resolve_optional(
            head_joint,
            legacy_kwargs,
            ('headJnt',),
            'head_JNT',
        )
        points_number = int(
            parameter_resolution.resolve_optional(points_number, legacy_kwargs, ('pointsNumber',), 5)
        )
        scale = float(parameter_resolution.resolve_optional(scale, legacy_kwargs, ('scale',), 0.1))
        base_rig = parameter_resolution.resolve_optional(base_rig, legacy_kwargs, ('baseRig',), None)

        if legacy_kwargs:
            raise ValueError(
                f'Unexpected arguments for Face: {tuple(legacy_kwargs.keys())}'
            )

        curve_nodes = pm.ls(cv_list)
        if not curve_nodes:
            raise ValueError('cv_list must contain valid curve names.')
        skin_geo_node = _as_single_node(skin_geo, 'skin_geo')
        head_joint_node = _as_single_node(head_joint, 'head_joint')
        self.skin_geo = skin_geo_node
        self.head_joint = head_joint_node

        if points_number < 2:
            raise ValueError('points_number must be at least 2.')

        self.rig_module = module.Module(prefix=prefix, base_obj=base_rig)

        self.points_number = points_number
        self.spacing = 1.0 / (points_number - 1)

        face_geo = pm.duplicate(skin_geo_node, n=f'{prefix}_GEO')[0]
        self.face_geo = face_geo
        pm.parent(face_geo, self.rig_module.parts_no_trans_group)
        deform.blend_shape_deformer(
            skin_geo_node,
            [face_geo],
            node_name='face_BS',
            front_of_chain=True,
        )

        head_face_joint = pm.duplicate(head_joint_node, renameChildren=True)[0]
        duplicated_joints = pm.listRelatives(head_face_joint, c=True, ad=True)
        duplicated_joints.append(head_face_joint)
        for joint in duplicated_joints:
            pm.rename(joint, str(joint.name()).replace('_JNT1', 'Face_JNT'))
        pm.parent(duplicated_joints[-1], self.rig_module.joints_group)

        pm.skinCluster(face_geo, head_face_joint)
        face_skin_cluster = skin.find_related_skin_cluster(face_geo)
        pm.skinCluster(face_geo, edit=True, ai=curve_nodes, ug=True)
        face_skin_cluster.useComponents.set(1)

        pm.parent(pm.ls('*_CRVBase'), self.rig_module.parts_no_trans_group)

        full_locator_list: list[pm.PyNode] = []
        full_cluster_list: list[pm.PyNode] = []
        for curve in curve_nodes:
            pm.rebuildCurve(
                curve,
                ch=False,
                rpo=True,
                rt=False,
                end=True,
                kr=False,
                kcp=False,
                kep=True,
                kt=False,
                s=4,
                d=1,
                tol=0.01,
            )
            pm.rebuildCurve(
                curve,
                ch=False,
                rpo=True,
                rt=False,
                end=True,
                kr=False,
                kcp=True,
                kep=True,
                kt=False,
                s=4,
                d=3,
                tol=0.01,
            )
            pm.parent(curve, self.rig_module.parts_no_trans_group)
            locators = self.setup_curve(curve, points_number)
            full_locator_list.extend(locators)

            curve_cvs = pm.ls(f'{curve}.cv[*]', fl=True)
            clusters = []
            for index, cv in enumerate(curve_cvs, start=1):
                cluster = pm.cluster(cv, n=f"{curve.name()}Cluster{index}")[1]
                clusters.append(cluster)
            full_cluster_list.extend(clusters)

        pm.group(
            full_cluster_list,
            n='faceCluster_GRP',
            p=self.rig_module.parts_no_trans_group,
        )

        follicle_list = []
        for locator, cluster in zip(full_locator_list, full_cluster_list):
            ctrl = control.Control(
                prefix=str(locator.name()).replace('_LOC', ''),
                translate_to=locator,
                parent=self.rig_module.controls_group,
                shape='sphere',
                do_modify=True,
                scale=scale,
            )
            follicle = follow_ctrl.make_control_follow_skin(
                skin_geo_node,
                ctrl.get_control(),
                cluster,
            )[-1]
            follicle_list.append(follicle)

        pm.group(
            follicle_list,
            n='faceFollicle_GRP',
            p=self.rig_module.parts_no_trans_group,
        )

    def setup_curve(  # pylint: disable=too-many-arguments
        self,
        curve: pm.PyNode,
        points_number: int,
        *,
        sphere_size: float = 0.1,
        offset_active: bool = False,
        locator_size: float = 0.1,
        joint_radius: float = 0.1,
        follow: bool = False,
    ) -> list[pm.PyNode]:
        """Create evenly spaced locators and joints along ``curve``."""
        del sphere_size  # Legacy parameter retained for API compatibility.
        curve_name = str(curve.name()).replace('_CRV', '')
        locators: list[pm.PyNode] = []

        for index in range(points_number):
            locator = pm.spaceLocator(n=f'{curve_name}{index + 1}_LOC')
            locator.localScaleX.set(locator_size)
            locator.localScaleY.set(locator_size)
            locator.localScaleZ.set(locator_size)

            motion_path = pm.ls(pm.pathAnimation(locator, c=curve, f=follow))[0]
            self.delete_connection(motion_path.u)
            motion_path.uValue.set(self.spacing * index)
            locators.append(locator)

            if offset_active:
                joint_offset = pm.joint(
                    n=f'{curve_name}Offset{index + 1}_JNT',
                    r=joint_radius,
                )
                joint_offset.radius.set(joint_radius)
                pm.delete(pm.pointConstraint(locator, joint_offset))

            joint = pm.joint(n=f'{curve_name}{index + 1}_JNT', r=joint_radius)
            joint.radius.set(joint_radius)
            if not offset_active:
                pm.delete(pm.pointConstraint(locator, joint))

            # Optional visualization sphere omitted; original commented block retained.
        pm.group(
            locators,
            n=f'{curve_name}Loc_GRP',
            p=self.rig_module.parts_no_trans_group,
        )
        return locators

    def delete_connection(self, plug: pm.Attribute) -> None:
        """Delete incoming connections on the provided plug."""
        if pm.connectionInfo(plug, isDestination=True):
            plug = pm.connectionInfo(plug, getExactDestination=True)
            if pm.ls(plug, ro=True):
                source = pm.connectionInfo(plug, sourceFromDestination=True)
                pm.disconnectAttr(source, plug)
            else:
                pm.delete(plug, icn=True)

    def get_module_dict(self) -> dict[str, Any]:
        """Return rig module bookkeeping data."""
        return {
            'module': self.rig_module,
            'module_obj': self.rig_module,
            'rig_module': self.rig_module,
        }


if __name__ == "__main__":
    raise SystemExit('Invoke within Maya to construct facial rigs.')

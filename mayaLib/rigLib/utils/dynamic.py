"""Utilities for building dynamic nCloth and hair-driven systems."""

from __future__ import annotations

from typing import Any, Iterable

import pymel.core as pm
from maya import mel

from mayaLib.rigLib.utils import deform, util

__all__ = [
    'create_collider',
    'create_ncloth',
    'setup_ncloth',
    'paint_cloth_input_attract',
    'DynamicCurve',
]


def _ensure_node(target) -> pm.PyNode:
    """Return the last PyNode found for ``target`` or raise ``ValueError``."""
    nodes = pm.ls(target)
    if not nodes:
        raise ValueError(f'Node {target!r} does not exist in the scene.')
    return nodes[-1]


def create_collider(geo, nucleus: str = 'nucleus1', collider_thickness: float = 0.005) -> pm.PyNode:
    """Create an nCloth collider for ``geo`` and parent it under the geometry."""
    geo_node = _ensure_node(geo)
    nucleus_node = _ensure_node(nucleus)

    pm.select(geo_node, nucleus_node)
    collider_shape = pm.ls(mel.eval('makeCollideNCloth;'))[-1]
    collider_transform = collider_shape.getParent()
    collider_transform = pm.rename(collider_transform, f'{geo_node.name()}_collider')
    pm.parent(collider_transform, geo_node)

    with pm.AttributeEnableState():
        collider_shape.thickness.set(collider_thickness)

    return collider_shape


def create_ncloth(
    geo,
    *,
    source_geo: str | pm.PyNode | None = None,
    rest_mesh: str | pm.PyNode | None = None,
) -> tuple[pm.PyNode, pm.PyNode, pm.PyNode]:
    """Create an nCloth from ``geo`` with optional source and rest meshes."""
    geo_node = _ensure_node(geo)
    pm.select(geo_node)
    cloth_shape = pm.ls(mel.eval('createNCloth 0;'))[-1]
    nucleus_node = pm.listConnections(cloth_shape, type='nucleus')[0]

    pm.rename(cloth_shape.getParent(), f'{geo_node.name()}_nCloth')
    pm.parent(cloth_shape.getParent(), geo_node)

    if source_geo:
        source_node = _ensure_node(source_geo)
        pm.connectAttr(source_node.getShape().worldMesh[0], cloth_shape.inputMesh, f=True)

    if rest_mesh:
        _ensure_node(rest_mesh)
        source_attr = pm.listConnections(cloth_shape.inputMesh, p=True)[-1]
        pm.connectAttr(source_attr, cloth_shape.restShapeMesh, f=True)

    cloth_output_shape = geo_node.getShapes()[-1]
    return cloth_shape, nucleus_node, cloth_output_shape


def setup_ncloth(  # pylint: disable=too-many-arguments
    geo,
    *,
    cloth_geo: str | pm.PyNode | None = None,
    input_geo: str | pm.PyNode | None = None,
    rest_mesh: str | pm.PyNode | None = None,
    do_direct_connection: bool = False,
    do_blendshape: bool = True,
) -> tuple[pm.PyNode, pm.PyNode, pm.PyNode, pm.PyNode]:
    """Create an nCloth setup duplicating geometry when needed."""
    geo_node = _ensure_node(geo)

    if cloth_geo:
        cloth_geo_node = _ensure_node(cloth_geo)
    else:
        cloth_name = (
            str(geo_node.name())
            .replace('_geo', '_cloth_geo')
            .replace('_proxy', '_proxy_cloth_geo')
        )
        cloth_geo_node = pm.duplicate(geo_node, n=cloth_name)[-1]

    if do_direct_connection:
        pm.connectAttr(geo_node.getShape().worldMesh[0], cloth_geo_node.inMesh, f=True)

    if do_blendshape:
        deform.blend_shape_deformer(cloth_geo_node, [geo_node], node_name='input_BS')

    cloth_shape, nucleus_node, geo_cloth_shape = create_ncloth(
        cloth_geo_node,
        source_geo=input_geo,
        rest_mesh=rest_mesh,
    )

    return cloth_geo_node, geo_cloth_shape, cloth_shape, nucleus_node


def paint_cloth_input_attract(
    cloth_node,
    vertices: Iterable[str],
    value: float,
    smooth_iterations: int = 1,
) -> None:
    """Paint the input attract map on an nCloth node."""
    cloth_shape = _ensure_node(cloth_node)
    channel = 'inputAttract'
    cloth_output = pm.listConnections(cloth_shape.outputMesh, sh=True)[0]

    mel.eval(
        f'setNClothMapType("{channel}","{cloth_output}",1); '
        f'artAttrNClothToolScript 4 {channel};'
    )
    pm.select(list(vertices))

    mel.eval(f'artAttrCtx -e -value {value} `currentCtx`;')
    mel.eval('artAttrPaintOperation artAttrCtx Replace;')
    mel.eval('artAttrCtx -e -clear `currentCtx`;')

    for _ in range(smooth_iterations):
        mel.eval('artAttrPaintOperation artAttrCtx Smooth;')
        mel.eval('artAttrCtx -e -clear `currentCtx`;')

    pm.select(cl=True)


class DynamicCurve:  # pylint: disable=too-many-instance-attributes
    """Create and manage a dynamic curve system driven by Maya hair."""

    def __init__(
        self,
        curve,
        prefix: str = 'new',
        base_rig: Any | None = None,
    ) -> None:
        """Initialize dynamic curve system with hair simulation.

        Creates a hair system setup on a curve for dynamic behavior like ropes,
        tails, or flexible appendages driven by Maya nHair dynamics.

        Args:
            curve: Curve to make dynamic (name or PyNode)
            prefix: Naming prefix for created nodes. Defaults to 'new'.
            base_rig: Optional base rig module for parenting. Defaults to None.

        Example:
            >>> dyn = DynamicCurve('tail_CRV', prefix='tail')
        """
        curve_node = _ensure_node(curve)

        main_grp_name = 'dynamicSystem_GRP'
        if not pm.objExists(main_grp_name):
            self.dynamic_system_group = pm.group(n=main_grp_name, em=1)
        else:
            self.dynamic_system_group = pm.ls(main_grp_name)[0]

        if base_rig:
            pm.parent(self.dynamic_system_group, base_rig.rigGrp)

        (
            self.follicle_group,
            self.follicle,
            self.input_curve,
            self.output_curve_group,
            self.output_curve,
            self.hair_system,
        ) = self.make_curve_dynamic(curve_node, prefix)

        self.nucleus = pm.listConnections(
            self.hair_system.getShape().currentState,
            destination=True,
        )
        with pm.ignoreErrors():
            pm.parent(self.nucleus, self.dynamic_system_group)

        self.system_group = pm.group(
            self.hair_system,
            self.follicle_group,
            self.output_curve_group,
            n=f'{prefix}Dynamic_GRP',
            p=self.dynamic_system_group,
        )

    def make_curve_dynamic(  # pylint: disable=too-many-locals
        self,
        curve: pm.PyNode,
        name: str,
    ) -> tuple[pm.PyNode, pm.PyNode, pm.PyNode, pm.PyNode, pm.PyNode, pm.PyNode]:
        """Convert ``curve`` into a dynamic hair-driven system."""
        pm.select(curve)
        mel.eval('makeCurvesDynamic 2 { "1", "0", "1", "1", "0"};')

        follicle_parent = pm.listRelatives(curve, parent=True)[0]
        follicle_transform = pm.rename(follicle_parent, f'{name}_follicle')
        follicle_shape = pm.listRelatives(follicle_transform, shapes=True)[0]

        input_curve_parent = util.get_driver_object(f'{follicle_shape}.startPosition')
        input_curve = pm.rename(input_curve_parent, f'{name}_input_CRV')

        output_curve_shape = util.get_driven_objects(f'{follicle_shape}.outCurve')
        output_curve = pm.rename(output_curve_shape, f'{name}_output_CRV')

        output_curve_parent = pm.listRelatives(output_curve, parent=True)[0]
        output_curve_group = pm.rename(output_curve_parent, f'{name}OutputCrvs_GRP')

        hair_system_parent = util.get_driver_object(f'{follicle_shape}.currentPosition')
        hair_system = pm.rename(hair_system_parent, f'{name}_hairSystem')

        follicles_group_parent = pm.listRelatives(follicle_transform, parent=True)[0]
        follicles_group = pm.rename(follicles_group_parent, f'{name}follicles_GRP')

        return (
            follicles_group,
            follicle_transform,
            input_curve,
            output_curve_group,
            output_curve,
            hair_system,
        )

    def get_output_curve(self) -> pm.PyNode:
        """Return the dynamic output curve."""
        return self.output_curve

    def get_input_curve(self) -> pm.PyNode:
        """Return the static input curve."""
        return self.input_curve

    def get_system_group(self) -> pm.PyNode:
        """Return the parent group containing the dynamic system."""
        return self.system_group

    def get_follicle_group(self) -> pm.PyNode:
        """Return the follicle group used by the dynamic system."""
        return self.follicle_group

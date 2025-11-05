"""Assorted helper utilities shared across the rigging toolkit."""

from __future__ import annotations

from maya import mel
import pymel.core as pm

__all__ = [
    'get_driver_driven_from_constraint',
    'get_driver_object',
    'get_driven_attributes',
    'get_driven_objects',
    'list_objects_under_group',
    'move_shape',
    'get_distance',
    'get_distance_from_coords',
    'lock_and_hide_all',
    'unlock_and_unhide_all',
    'no_render',
    'invert_selection',
    'get_planar_radius_bbox',
    'matrix_constrain',
    'cleanup_unknown_nodes',
]


def get_driver_driven_from_constraint(constraint):
    """Return the driver and driven objects attached to ``constraint``."""
    drivers = pm.listConnections(
        f'{constraint}.target[0].targetParentMatrix', destination=False
    )
    driven = pm.listConnections(constraint, source=False)[0]
    return drivers, driven


def get_driver_object(attribute, skip_conversion_nodes: bool = False):
    """Return the upstream node driving ``attribute`` if any."""
    connections = pm.listConnections(
        attribute,
        scn=skip_conversion_nodes,
        d=False,
        s=True,
        plugs=False,
    )
    return pm.ls(connections[0])[0] if connections else None


def get_driven_attributes(attribute, skip_conversion_nodes: bool = False):
    """Return attribute names driven by ``attribute`` or ``False`` when none."""
    if not pm.connectionInfo(attribute, isSource=True):
        return False

    destinations = pm.listConnections(
        attribute,
        scn=skip_conversion_nodes,
        s=False,
        d=True,
        plugs=True,
    )
    if not destinations:
        destinations = pm.connectionInfo(attribute, destinationFromSource=True)
    if not destinations:
        return False
    return [str(pm.ls(link)[0]) for link in destinations]


def get_driven_objects(attribute, skip_conversion_nodes: bool = True):
    """Return nodes driven by ``attribute`` or ``False`` when none."""
    destinations = pm.listConnections(
        attribute,
        scn=skip_conversion_nodes,
        s=False,
        d=True,
        plugs=False,
    )
    if not destinations:
        return False
    result = []
    for node in destinations:
        if attribute == node:
            continue
        result.append(str(pm.ls(node)[0]))
    return result


def list_objects_under_group(
    group,
    node_type: str = 'mesh',
    full_path: bool = True,
) -> list:
    """Return objects of ``node_type`` found under a group."""
    if node_type == 'transform':
        mesh_nodes = {
            pm.listRelatives(node, p=True, fullPath=full_path)[0]
            for node in pm.listRelatives(group, ad=True, type='mesh', fullPath=full_path)
        }
        objects = [
            node
            for node in pm.listRelatives(group, ad=True, type=node_type, fullPath=full_path)
            if node not in mesh_nodes
        ]
    else:
        objects = [
            pm.listRelatives(node, p=True, fullPath=full_path)[0]
            for node in pm.listRelatives(group, ad=True, type=node_type, fullPath=full_path)
        ]
    return sorted(set(objects))


def move_shape(source, destination) -> None:
    """Parent the shape from ``source`` beneath ``destination``."""
    if isinstance(source, pm.PyNode):
        pm.parent(source, destination[0], r=True, s=True)
    else:
        pm.parent(pm.PyNode(source[0]).getShape(), destination, r=True, s=True)


def get_distance(obj_a, obj_b) -> float:
    """Return the Euclidean distance between two scene nodes."""
    locator_a = pm.spaceLocator()
    locator_b = pm.spaceLocator()
    constraint_a = pm.pointConstraint(obj_a, locator_a)
    constraint_b = pm.pointConstraint(obj_b, locator_b)

    ax, ay, az = locator_a.getTranslation(space='world')
    bx, by, bz = locator_b.getTranslation(space='world')
    distance = ((ax - bx) ** 2 + (ay - by) ** 2 + (az - bz) ** 2) ** 0.5

    pm.delete(constraint_a, constraint_b, locator_a, locator_b)
    return distance


def get_distance_from_coords(min_corner, max_corner) -> float:
    """Return the Euclidean distance between two 3D points."""
    ax, ay, az = min_corner
    bx, by, bz = max_corner
    return ((ax - bx) ** 2 + (ay - by) ** 2 + (az - bz) ** 2) ** 0.5


def lock_and_hide_all(nodes) -> None:
    """Lock and hide transform channels on the given nodes."""
    for node in pm.ls(nodes):
        for attr in ('tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'):
            getattr(node, attr).set(lock=True, keyable=False, channelBox=False)


def unlock_and_unhide_all(nodes) -> None:
    """Unlock and expose transform channels on the given nodes."""
    for node in pm.ls(nodes):
        for attr in ('tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz'):
            getattr(node, attr).set(lock=False, keyable=True, channelBox=True)


def no_render(nodes) -> None:
    """Disable common renderable flags on the supplied shapes."""
    for node in pm.ls(nodes):
        node.castsShadows.set(0)
        node.receiveShadows.set(0)
        node.motionBlur.set(0)
        node.primaryVisibility.set(0)
        node.smoothShading.set(0)
        node.visibleInReflections.set(0)
        node.visibleInRefractions.set(0)


def invert_selection():
    """Invert the current Maya selection and return the new list."""
    mel.eval('InvertSelection;')
    return pm.ls(sl=True)


def get_planar_radius_bbox(transform, radius_factor: float = 2.0) -> dict[str, float]:
    """Return planar radii derived from the transform's bounding box."""
    transform = pm.ls(transform)[0]
    bbox = transform.getBoundingBox()
    xmin, ymin, zmin = bbox[0]
    xmax, ymax, zmax = bbox[1]

    radius = {
        'planarX': get_distance_from_coords([0, ymin, zmin], [0, ymin, zmax]) / radius_factor,
        'planarY': get_distance_from_coords([xmin, 0, zmin], [xmax, 0, zmax]) / radius_factor,
        'planarZ': get_distance_from_coords([xmin, ymin, 0], [xmax, ymin, 0]) / radius_factor,
        '3D': get_distance_from_coords([xmin, ymin, zmin], [xmax, ymax, zmax]) / radius_factor,
    }
    return radius


def matrix_constrain(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    driver,
    driven,
    parent=None,
    translate: bool = True,
    rotate: bool = True,
    scale: bool = False,
) -> None:
    """Apply a matrix-based constraint from ``driver`` to ``driven``."""
    driver = pm.ls(driver)[0]
    driven = pm.ls(driven)[0]
    parent = pm.ls(parent)[0] if parent else driven.getParent()

    mult_matrix = pm.shadingNode('multMatrix', asUtility=True)
    decompose = pm.shadingNode('decomposeMatrix', asUtility=True)

    pm.connectAttr(mult_matrix.matrixSum, decompose.inputMatrix)
    pm.connectAttr(driver.worldMatrix[0], mult_matrix.matrixIn[0])
    pm.connectAttr(parent.worldInverseMatrix[0], mult_matrix.matrixIn[1])

    if translate:
        pm.connectAttr(decompose.outputTranslate, driven.translate)
    if rotate:
        pm.connectAttr(decompose.outputRotate, driven.rotate)
    if scale:
        pm.connectAttr(decompose.outputScale, driven.scale)


def cleanup_unknown_nodes() -> None:
    """Remove unknown plugins and nodes lingering in the scene."""
    plugins = pm.unknownPlugin(q=True, list=True) or []
    for plugin in plugins:
        try:
            pm.unknownPlugin(plugin, remove=True)
        except RuntimeError:
            continue

    for node_type in ('unknown', 'unknownDag', 'unknownTransform'):
        for node in pm.ls(type=node_type):
            if node and not node.isReferenced():
                with pm.ignoreErrors():
                    node.unlock()
                with pm.ignoreErrors():
                    pm.delete(node)

"""Common rigging utilities shared across multiple Maya tools."""

from __future__ import annotations

import pymel.core as pm
from maya import mel


def center_pivot(obj, target_pivot=None):
    """Center the pivot of ``obj`` or match ``target_pivot``.

    This function centers the pivot of the specified object. If a target pivot
    is provided, the object's pivot is set to the target's pivot position.

    Args:
        obj: Object whose pivot will be centered.
        target_pivot: Optional target object whose pivot should be matched.
    """
    if target_pivot is None:
        pm.xform(obj, cp=1)
    else:
        pivot_translate = pm.xform(target_pivot, q=True, ws=True, rotatePivot=True)
        pm.xform(obj, ws=True, pivots=pivot_translate)


def freeze_transform(obj):
    """Freeze the transformation of ``obj`` (translate, rotate, scale)."""
    pm.makeIdentity(obj, apply=True, t=1, r=1, s=1, n=0)


def delete_history(obj):
    """Delete construction history for ``obj``."""
    pm.delete(obj, ch=True)


def delete_non_deformer_history(obj):
    """Delete all non-deformer history in ``obj``."""
    pm.bakePartialHistory(obj, pre=True)


def delete_connection(plug):
    """Delete the incoming connection on ``plug`` (CBdeleteConnection)."""
    if pm.connectionInfo(plug, isDestination=True):
        plug = pm.connectionInfo(plug, getExactDestination=True)
        read_only = pm.ls(plug, ro=True)
        # delete -icn doesn't work if destination attr is readOnly
        if read_only:
            source = pm.connectionInfo(plug, sourceFromDestination=True)
            pm.disconnectAttr(source, plug)
        else:
            pm.delete(plug, icn=True)


def delete_connection_legacy(obj_attr_list):
    """Delete multiple plugs, preserving legacy API name."""
    for plug in pm.ls(obj_attr_list):
        delete_connection(str(plug.name()))


def set_driven_key(driver, driver_value_list, driven, driven_value_list, cv_type="linear"):
    """Set driven keys using parallel driver/driven value lists.

    Args:
        driver: Attribute driving the relationship (e.g. ``ctrl.attr``).
        driver_value_list: Sequence of driver values.
        driven: Driven attribute (e.g. ``ctrl.attr``).
        driven_value_list: Sequence of values to key on the driven attribute.
        cv_type: Tangent type for the keyframes.
    """
    for driver_v, driven_v in zip(driver_value_list, driven_value_list, strict=False):
        pm.setDrivenKeyframe(
            driven,
            currentDriver=driver,
            driverValue=driver_v,
            value=driven_v,
            inTangentType=cv_type,
            outTangentType=cv_type,
        )


def delete_unknown_nodes():
    """Delete unknown/unknownDag/unknownTransform nodes in the scene."""
    unknown_list = pm.ls(mel.eval("ls -type unknown -type unknownDag -type unknownTransform"))
    while unknown_list:
        for node in unknown_list:
            pm.lockNode(node, lock=False)
            pm.delete(node)
        unknown_list = pm.ls(mel.eval("ls -type unknown -type unknownDag -type unknownTransform"))


def remove_shape_deformed():
    """Rename deformed shape nodes to remove the ``Deformed`` suffix."""
    shape_node_list = pm.ls("*Shape", type="mesh", long=True)
    for shape in shape_node_list:
        pm.rename(shape.name(), f"{shape.name()}_Original")

    for shape in pm.ls("*ShapeDeformed", type="mesh", long=True):
        new_name = str(shape.name()).replace("ShapeDeformed", "Shape")
        pm.rename(shape, new_name)

"""Utilities to attach controls to geometry via follicles."""

from __future__ import annotations

import pymel.core as pm

from mayaLib.rigLib.utils import common, name, util


def create_follicle(geo, u_param, v_param, prefix):
    """Create a follicle at the given UV coordinates."""
    follicle_shape = pm.createNode('follicle', n=f'{prefix}_FLCShape')
    geo_shape = geo.getShape()
    follicle = follicle_shape.getParent()
    follicle.rename(f'{prefix}_FLC')

    pm.connectAttr(geo_shape.outMesh, follicle_shape.inputMesh)
    pm.connectAttr(geo_shape.worldMatrix, follicle_shape.inputWorldMatrix)

    pm.connectAttr(follicle_shape.outRotate, follicle.rotate)
    pm.connectAttr(follicle_shape.outTranslate, follicle.translate)

    follicle_shape.parameterU.set(u_param)
    follicle_shape.parameterV.set(v_param)

    return follicle


def find_closest_uv_coordinate(geo, obj):
    """Return the closest UV coordinates on ``geo`` to ``obj``."""
    closest_point = pm.createNode("closestPointOnMesh")
    geo_shape = geo.getShape()
    pm.connectAttr(geo_shape.worldMesh, closest_point.inMesh)
    pm.connectAttr(geo_shape.worldMatrix, closest_point.inputMatrix)
    loc = pm.spaceLocator(n=f"{name.remove_suffix(geo.name())}_LOC")
    pm.matchTransform(loc, obj)
    pm.connectAttr(loc.translate, closest_point.inPosition)

    u_value = closest_point.result.parameterU.get()
    v_value = closest_point.result.parameterV.get()

    pm.delete(closest_point, loc)

    return u_value, v_value


def make_control_follow_skin(geo, ctrl, driven_obj):
    """Attach a control to a mesh via follicles and compensate translation."""
    geo = pm.ls(geo)[0]
    ctrl = pm.ls(ctrl)[0]
    driven_obj = pm.ls(driven_obj)[0]
    uv = find_closest_uv_coordinate(geo, ctrl)
    prefix = name.remove_suffix(ctrl.name())
    follicle = create_follicle(geo, uv[0], uv[1], prefix)

    follow_grp = pm.group(em=True, n=f"{prefix}Follow_GRP", w=True)
    compensate_grp = pm.group(em=True, n=f"{prefix}Compensate_GRP", w=True)

    common.center_pivot(compensate_grp, ctrl)
    common.center_pivot(follow_grp, ctrl)

    pm.parent(compensate_grp, follow_grp)
    pm.parent(follow_grp, ctrl.getParent())
    pm.parent(ctrl, compensate_grp)

    util.matrix_constrain(follicle, follow_grp, rotate=False)

    mult_divide = pm.createNode('multiplyDivide', n=f"{prefix}CompensateNode")
    pm.connectAttr(ctrl.translate, mult_divide.input1)
    pm.connectAttr(mult_divide.output, compensate_grp.translate)
    mult_divide.input2X.set(-1)
    mult_divide.input2Y.set(-1)
    mult_divide.input2Z.set(-1)

    ctrl.translate.set(0, 0, 0)
    pm.connectAttr(ctrl.translate, driven_obj.translate, f=True)

    return ctrl, follicle


if __name__ == "__main__":
    raise SystemExit('Invoke within Maya to use follow control utilities.')

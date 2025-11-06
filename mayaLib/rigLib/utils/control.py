"""Factory helpers for constructing rig controls."""

from __future__ import annotations

import pymel.core as pm

from mayaLib.pipelineLib.utility import name_check as nc
from mayaLib.rigLib.utils import common
from mayaLib.rigLib.utils import ctrl_shape as ctrl_shape_lib

# pylint: disable=too-many-arguments,too-many-positional-arguments
# pylint: disable=too-many-locals,too-many-branches,too-many-statements
# pylint: disable=too-many-instance-attributes


class Control:
    """Build rig controls with optional offset/modify groups."""

    def __init__(
            self,
            prefix='new',
            scale=1.0,
            translate_to='',
            rotate_to='',
            parent='',
            shape='circle',
            lock_channels=None,
            do_offset=True,
            do_modify=False,
            do_dynamic_pivot=False,
    ):
        """Initialise the control, offset, and modify hierarchy.

        Args:
            prefix: Prefix for new node names.
            scale: Uniform scale for control shapes.
            translate_to: Reference object for positioning.
            rotate_to: Reference object for orientation.
            parent: Optional parent for the control hierarchy.
            shape: Control shape type.
            lock_channels: Channels to lock/non-keyable.
            do_offset: Whether to create an offset group.
            do_modify: Whether to create a modify group.
            do_dynamic_pivot: Whether to add a dynamic pivot locator.
        """
        # name handle
        if '*' in prefix:
            prefix = nc.name_check(prefix + '_CTRL').split('_')[0]

        lock_channels = lock_channels or ['s', 'v']
        ctrl_object = None
        circle_normal = [1, 0, 0]

        if shape in {'circle', 'circleX'}:
            circle_normal = [1, 0, 0]

        elif shape == 'circleY':
            circle_normal = [0, 1, 0]

        elif shape == 'circleZ':
            circle_normal = [0, 0, 1]

        elif shape == 'sphere':
            ctrl_object = ctrl_shape_lib.sphereCtrlShape(name=prefix + '_CTRL', scale=scale)

        elif shape == 'move':
            ctrl_object = ctrl_shape_lib.moveCtrlShape(name=prefix + '_CTRL', scale=scale)

        elif shape == 'spine':
            ctrl_object = ctrl_shape_lib.trapeziumCtrlShape(
                name=f'{prefix}_CTRL', scale=scale
            )
            ctrl_object.translateY.set(3 * scale)
            common.freeze_transform(ctrl_object)

        elif shape == 'chest':
            ctrl_object = ctrl_shape_lib.chestCtrlShape(name=prefix + '_CTRL', scale=scale)

        elif shape == 'hip':
            ctrl_object = ctrl_shape_lib.hipCtrlShape(name=prefix + '_CTRL', scale=scale)

        elif shape == 'head':
            ctrl_object = ctrl_shape_lib.headCtrlShape(name=prefix + '_CTRL', scale=scale)

        elif shape == 'display':
            ctrl_object = ctrl_shape_lib.displayCtrlShape(name=prefix + '_CTRL', scale=scale)

        elif shape == 'ikfk':
            ctrl_object = ctrl_shape_lib.ikfkCtrlShape(name=prefix + '_CTRL', scale=scale)

        # default ctrl
        if not ctrl_object:
            ctrl_object = pm.circle(
                n=f'{prefix}_CTRL', ch=False, normal=circle_normal, radius=scale
            )[0]

        if do_modify:
            ctrl_modify = pm.group(n=f'{prefix}Modify_GRP', em=1)
            pm.parent(ctrl_object, ctrl_modify)

        if do_offset:
            ctrl_offset = pm.group(n=f'{prefix}Offset_GRP', em=1)
            if do_modify:
                pm.parent(ctrl_modify, ctrl_offset)
            else:
                pm.parent(ctrl_object, ctrl_offset)

        # color control
        ctrl_shapes = ctrl_object.getShapes()
        for ctrl_shape in ctrl_shapes:
            ctrl_shape.ove.set(1)

            colour = (
                6
                if prefix.startswith('l_')
                else 13 if prefix.startswith('r_') else 22
            )
            ctrl_shape.ovc.set(colour)

        # translate control
        if translate_to is not None and translate_to != '' and pm.objExists(translate_to):
            pm.delete(pm.pointConstraint(translate_to, ctrl_offset))

        # rotate control
        if rotate_to is not None and rotate_to != '' and pm.objExists(rotate_to):
            pm.delete(pm.orientConstraint(rotate_to, ctrl_offset))

        # lock control channels
        locked = []
        for lock_channel in lock_channels:
            if lock_channel in {'t', 'r', 's'}:
                locked.extend(f'{lock_channel}{axis}' for axis in 'xyz')
            else:
                locked.append(lock_channel)

        for attr in locked:
            pm.setAttr(f"{ctrl_object}.{attr}", l=True, k=False)

        # add public members
        self.scale = scale
        self.control = ctrl_object
        self.modify_grp = None
        self.offset_grp = None

        self.offset_grp = ctrl_offset if do_offset else None
        self.modify_grp = ctrl_modify if do_modify else None

        if parent and pm.objExists(parent):
            pm.parent(self.get_top(), parent)

        self.dynamic_pivot = None
        if do_dynamic_pivot:
            self.dynamic_pivot = self.make_dynamic_pivot(
                prefix, scale, translate_to, rotate_to
            )

        # Legacy attributes (CamelCase preserved for backward compatibility).
        self.C = self.control
        self.Modify = self.modify_grp
        self.Off = self.offset_grp

    def get_ctrl_scale(self):
        """Return the scale used when the control was created."""
        return self.scale

    def make_dynamic_pivot(self, prefix, scale, translate_to, rotate_to):
        """Create a dynamic pivot control constrained to this control."""
        pivot_ctrl = Control(
            prefix=f"{prefix}Pivot",
            scale=scale / 5,
            translate_to=translate_to,
            rotate_to=rotate_to,
            parent=self.control,
            shape='sphere',
            do_offset=True,
            do_dynamic_pivot=False,
        )
        pm.connectAttr(
            pivot_ctrl.get_control().translate,
            self.control.rotatePivot,
            f=True,
        )
        control = pm.group(
            n=f"{prefix}Con_GRP", p=self.get_control(), em=True
        )

        # add visibility Attribute on CTRL
        pm.addAttr(
            self.control, ln='PivotVisibility', at='enum', enumName='off:on', k=1, dv=0
        )
        pm.connectAttr(
            self.control.PivotVisibility,
            pivot_ctrl.get_offset_grp().visibility,
            f=True,
        )
        control.visibility.set(0)

        return control

    def get_control(self):
        """Return the active control node."""
        if self.dynamic_pivot:
            return self.dynamic_pivot

        return self.control

    def get_offset_grp(self):
        """Return the optional offset group."""
        return self.offset_grp

    def get_modify_grp(self):
        """Return the optional modify group."""
        return self.modify_grp

    def get_top(self):
        """Return the top-most node in the control hierarchy."""
        if self.offset_grp:
            return self.offset_grp
        if self.modify_grp:
            return self.modify_grp
        return self.control


# Legacy API compatibility
Control.getCtrlScale = Control.get_ctrl_scale
Control.makeDynamicPivot = Control.make_dynamic_pivot
Control.getControl = Control.get_control
Control.getOffsetGrp = Control.get_offset_grp
Control.getModifyGrp = Control.get_modify_grp
Control.getTop = Control.get_top


if __name__ == "__main__":
    raise SystemExit('Invoke within Maya to construct controls.')

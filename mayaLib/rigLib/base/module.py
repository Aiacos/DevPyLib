"""Rig module scaffolding for DevPyLib Maya rigs."""

from __future__ import annotations

from typing import Any, Tuple

import pymel.core as pm

from mayaLib.rigLib.utils import common, control, util

__all__ = ['Base', 'Module']


def _resolve_optional(
    value: Any,
    legacy_kwargs: dict[str, Any],
    legacy_keys: Tuple[str, ...],
    default: Any,
) -> Any:
    """Resolve an optional parameter supporting legacy keyword arguments."""
    if value is not None:
        return value
    for key in legacy_keys:
        if key in legacy_kwargs:
            return legacy_kwargs.pop(key)
    return default


def _resolve_required(
    value: Any,
    legacy_kwargs: dict[str, Any],
    legacy_keys: Tuple[str, ...],
    label: str,
) -> Any:
    """Resolve a required parameter supporting legacy keyword arguments."""
    resolved = _resolve_optional(value, legacy_kwargs, legacy_keys, None)
    if resolved is None:
        raise ValueError(f'{label} is required.')
    return resolved


class Base:  # pylint: disable=too-many-instance-attributes,too-few-public-methods
    """Build the top-level rig structure with global controls."""

    scene_object_type = 'rig'

    def __init__(  # pylint: disable=too-many-arguments,too-many-locals,too-many-statements
        self,
        character_name: str | None = None,
        scale: float | None = None,
        main_ctrl_attach_obj: str | None = None,
        **legacy_kwargs: Any,
    ) -> None:
        """Initialise the base rig scaffolding."""
        legacy_kwargs = dict(legacy_kwargs)
        character_name = _resolve_optional(
            character_name,
            legacy_kwargs,
            ('characterName',),
            'new',
        )
        scale = float(_resolve_optional(scale, legacy_kwargs, ('scale',), 1.0))
        main_ctrl_attach_obj = _resolve_optional(
            main_ctrl_attach_obj,
            legacy_kwargs,
            ('mainCtrlAttachObj',),
            '',
        )

        if legacy_kwargs:
            raise ValueError(
                f'Unexpected arguments for Base: {tuple(legacy_kwargs.keys())}'
            )

        attach_node_list = pm.ls(main_ctrl_attach_obj)
        attach_node = attach_node_list[0] if attach_node_list else None

        self.top_group = pm.group(n=f'{character_name}_rig_GRP', em=True)

        self.rig_ctrl_locator = pm.spaceLocator(n='rigCtrl_LOC')
        pm.rotate(self.rig_ctrl_locator, [0, -90, 0], r=True, ws=True)
        if attach_node:
            pm.delete(pm.pointConstraint(attach_node, self.rig_ctrl_locator))

        for attr_name, value in (
            ('characterName', character_name),
            ('sceneObjectType', self.scene_object_type),
        ):
            if not self.top_group.hasAttr(attr_name):
                pm.addAttr(self.top_group, ln=attr_name, dt='string')
            pm.setAttr(f'{self.top_group}.{attr_name}', value, type='string', l=True)

        self.global_control = control.Control(
            prefix='global',
            scale=scale,
            parent=self.top_group,
            lock_channels=['t', 'r', 'v'],
            shape='circleY',
            do_modify=False,
            do_offset=False,
        )

        self.main_control = control.Control(
            prefix='main',
            scale=scale,
            parent=self.global_control.get_control(),
            lock_channels=['s', 'v'],
            shape='move',
            do_modify=False,
            do_offset=False,
        )

        self.model_group = pm.group(n='model_GRP', em=True, p=self.top_group)
        self.fast_model_group = pm.group(
            n='fastModel_GRP', em=True, p=self.model_group
        )
        self.medium_model_group = pm.group(
            n='mediumModel_GRP', em=True, p=self.model_group
        )
        self.medium_slow_group = pm.group(
            n='mediumSlowModel_GRP', em=True, p=self.model_group
        )
        self.slow_model_group = pm.group(
            n='slowModel_GRP', em=True, p=self.model_group
        )
        self.all_model_group = pm.group(
            n='allModel_GRP', em=True, p=self.model_group
        )
        self.rig_model_group = pm.group(
            n='rigModel_GRP', em=True, p=self.model_group
        )
        pm.hide(self.rig_model_group)

        self.rig_group = pm.group(
            n='rig_GRP', em=True, p=self.main_control.get_control()
        )

        self.scale_locator = pm.spaceLocator(n='scale_LOC')
        self.scale_locator.inheritsTransform.set(False)
        self.scale_locator.visibility.set(False)
        pm.connectAttr(
            self.global_control.get_control().scale,
            self.scale_locator.scale,
        )
        pm.parent(self.scale_locator, self.rig_group)

        self.joints_group = pm.group(
            n='skeleton_GRP', em=True, p=self.main_control.get_control()
        )
        self.modules_group = pm.group(
            n='modules_GRP', em=True, p=self.main_control.get_control()
        )
        self.rig_control_group = pm.group(
            n='rigctrl_GRP', em=True, p=self.global_control.get_control()
        )
        util.lock_and_hide_all(self.rig_control_group)

        self.part_group = pm.group(n='parts_GRP', em=True, p=self.rig_group)
        pm.setAttr(f'{self.part_group}.it', 0, l=True)

        self.halo_control = control.Control(
            prefix='halo',
            scale=1,
            parent=self.rig_control_group,
            translate_to=attach_node,
            rotate_to=self.rig_ctrl_locator,
            lock_channels=['s'],
            shape='circleX',
            do_offset=True,
            do_modify=True,
            obj_bbox=attach_node,
        )
        self.halo_control.get_offset_grp().visibility.set(False)
        self.create_halo(attach_node, 1)

        main_visibility_attrs = ['modelVis', 'jointsVis']
        main_display_attrs = ['modelDisp', 'jointsDisp']
        main_objects = [self.model_group, self.joints_group]
        default_visibility = [1, 0]

        for attr_name, obj, default in zip(
            main_visibility_attrs, main_objects, default_visibility
        ):
            pm.addAttr(
                self.global_control.get_control(),
                ln=attr_name,
                at='enum',
                enumName='off:on',
                k=True,
                dv=default,
            )
            pm.setAttr(
                f'{self.global_control.get_control()}.{attr_name}', cb=True
            )
            pm.connectAttr(
                f'{self.global_control.get_control()}.{attr_name}',
                f'{obj}.v',
            )

        for attr_name, obj in zip(main_display_attrs, main_objects):
            pm.addAttr(
                self.global_control.get_control(),
                ln=attr_name,
                at='enum',
                enumName='normal:template:reference',
                k=True,
                dv=2,
            )
            pm.setAttr(
                f'{self.global_control.get_control()}.{attr_name}', cb=True
            )
            pm.setAttr(f'{obj}.ove', 1)
            pm.connectAttr(
                f'{self.global_control.get_control()}.{attr_name}',
                f'{obj}.ovdt',
            )

        display_level_attr = 'displayLevel'
        level_groups = [
            self.fast_model_group,
            self.medium_model_group,
            self.slow_model_group,
        ]
        pm.addAttr(
            self.global_control.get_control(),
            ln=display_level_attr,
            at='enum',
            enumName='fast:medium:slow',
            k=True,
            dv=1,
        )
        pm.setAttr(
            f'{self.global_control.get_control()}.{display_level_attr}', cb=True
        )
        common.set_driven_key(
            f'{self.global_control.get_control()}.{display_level_attr}',
            [0, 1, 2],
            f'{level_groups[0]}.v',
            [1, 0, 0],
        )
        common.set_driven_key(
            f'{self.global_control.get_control()}.{display_level_attr}',
            [0, 1, 2],
            f'{level_groups[1]}.v',
            [0, 1, 0],
        )
        common.set_driven_key(
            f'{self.global_control.get_control()}.{display_level_attr}',
            [0, 1, 2],
            f'{level_groups[2]}.v',
            [0, 0, 1],
        )
        common.set_driven_key(
            f'{self.global_control.get_control()}.{display_level_attr}',
            [0, 1, 2],
            f'{self.medium_slow_group}.v',
            [0, 1, 1],
        )

        self.display_control = self.create_display(attach_node, 1)
        self.ikfk_control = self.create_ik_fk(attach_node, 1)
        pm.delete(self.rig_ctrl_locator)

    def get_scale_locator(self) -> pm.PyNode:
        """Return the world scale locator."""
        return self.scale_locator

    def get_display_control(self) -> control.Control:
        """Return the display control wrapper."""
        return self.display_control

    def create_halo(self, attach_node: pm.PyNode | None, scale: float) -> None:
        """Create a halo overlay control around the rig."""
        del scale  # Legacy compatibility; halo scale driven by control size.
        if not attach_node:
            return
        halo_duplicate = pm.duplicate(self.halo_control.get_control(), n='halo')[0]
        halo_shape = halo_duplicate.getShape()
        pm.parent(halo_shape, self.global_control.get_control(), r=True, s=True)
        pm.delete(halo_duplicate)

        pm.blendShape(
            self.halo_control.get_control(),
            halo_shape,
            n='halo_blendShape',
            origin='world',
        )
        pm.setAttr('halo_blendShape.halo_CTRL', 1)
        pm.parentConstraint(attach_node, self.halo_control.get_offset_grp(), mo=True)
        self.halo_control.get_modify_grp().translateY.set(
            6 * self.halo_control.get_ctrl_scale()
        )

    def create_display(
        self, attach_node: pm.PyNode | None, scale: float
    ) -> control.Control:
        """Create the display control used for module visibility toggles."""
        display_ctrl = control.Control(
            prefix='display',
            scale=scale,
            parent=self.rig_control_group,
            translate_to=attach_node,
            rotate_to=self.rig_ctrl_locator,
            lock_channels=['t', 'r', 's'],
            shape='display',
            do_offset=True,
            do_modify=True,
            obj_bbox=attach_node,
        )

        if attach_node:
            common.center_pivot(display_ctrl.get_offset_grp())
            common.center_pivot(display_ctrl.get_control())
            pm.parentConstraint(attach_node, display_ctrl.get_offset_grp(), mo=True)
            display_ctrl.get_modify_grp().translateY.set(
                4 * display_ctrl.get_ctrl_scale()
            )

        return display_ctrl

    def create_ik_fk(
        self, attach_node: pm.PyNode | None, scale: float
    ) -> control.Control:
        """Create the IK/FK display control."""
        ikfk_ctrl = control.Control(
            prefix='ikfk',
            scale=scale,
            parent=self.rig_control_group,
            translate_to=attach_node,
            rotate_to=self.rig_ctrl_locator,
            lock_channels=['t', 'r', 's'],
            shape='ikfk',
            do_offset=True,
            do_modify=True,
            obj_bbox=attach_node,
        )

        if attach_node:
            common.center_pivot(ikfk_ctrl.get_offset_grp())
            common.center_pivot(ikfk_ctrl.get_control())
            pm.parentConstraint(attach_node, ikfk_ctrl.get_offset_grp(), mo=True)
            ikfk_ctrl.get_modify_grp().translateY.set(
                3 * ikfk_ctrl.get_ctrl_scale()
            )

        return ikfk_ctrl


class Module:  # pylint: disable=too-few-public-methods,too-many-instance-attributes
    """Container class for per-module rig groups."""

    def __init__(
        self,
        prefix: str | None = None,
        base_obj: Base | None = None,
        **legacy_kwargs: Any,
    ) -> None:
        """Initialise a module scaffold under the provided base rig."""
        legacy_kwargs = dict(legacy_kwargs)
        prefix = _resolve_optional(prefix, legacy_kwargs, ('prefix',), 'new')
        base_obj = _resolve_optional(base_obj, legacy_kwargs, ('baseObj',), None)

        if legacy_kwargs:
            raise ValueError(
                f'Unexpected arguments for Module: {tuple(legacy_kwargs.keys())}'
            )

        self.top_group = pm.group(n=f'{prefix}Module_GRP', em=True)

        self.controls_group = pm.group(
            n=f'{prefix}Controls_GRP', em=True, p=self.top_group
        )
        self.secondary_controls_group = pm.group(
            n=f'{prefix}secondaryControls_GRP', em=True, p=self.top_group
        )
        self.joints_group = pm.group(
            n=f'{prefix}Joints_GRP', em=True, p=self.top_group
        )
        self.parts_group = pm.group(
            n=f'{prefix}Parts_GRP', em=True, p=self.top_group
        )
        self.parts_no_trans_group = pm.group(
            n=f'{prefix}PartsNoTrans_GRP', em=True, p=self.top_group
        )

        pm.hide(self.parts_group, self.parts_no_trans_group)
        pm.setAttr(f'{self.parts_no_trans_group}.it', 0, l=True)

        if pm.objExists('display_CTRL'):
            display_ctrl = pm.ls('display_CTRL')[0]
            level_groups = [self.controls_group, self.secondary_controls_group]
            if not display_ctrl.hasAttr(prefix):
                pm.addAttr(
                    display_ctrl,
                    ln=prefix,
                    at='enum',
                    enumName='none:block:all',
                    k=True,
                    dv=1,
                )
            pm.setAttr(f'{display_ctrl}.{prefix}', cb=True)
            common.set_driven_key(
                f'{display_ctrl}.{prefix}',
                [0, 1, 2],
                f'{level_groups[0]}.v',
                [0, 1, 1],
            )
            common.set_driven_key(
                f'{display_ctrl}.{prefix}',
                [0, 1, 2],
                f'{level_groups[1]}.v',
                [0, 0, 1],
            )

        if base_obj:
            pm.parent(self.top_group, base_obj.modules_group)

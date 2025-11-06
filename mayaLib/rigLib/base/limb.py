"""Limb rig construction helpers."""

# pylint: disable=too-many-lines

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, cast

import pymel.core as pm

from mayaLib.rigLib.base import module
from mayaLib.rigLib.utils import (
    attributes,
    common,
    control,
    foot_roll,
    joint,
    name,
    parameter_resolution,
    pole_vector,  # type: ignore
    scapula,
    spaces,
    util,
)

__all__ = [
    "Limb",
    "Arm",
    "build_simple_scapula",
    "build_clavicle",
    "build_dynamic_scapula",
    "build_fk_controls",
    "build_pole_vector",
    "build_ik_controls",
]


def build_simple_scapula(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    prefix: str,
    limb_joints: Sequence[str],
    scapula_joint: str,
    rig_scale: float,
    rig_module: module.Module,
    base_attach_group: pm.PyNode,
) -> control.Control:
    """Create a simple scapula control that follows the body attach group."""
    scapula_ctrl = control.Control(
        prefix=f"{prefix}Scapula",
        translate_to=scapula_joint,
        rotate_to=scapula_joint,
        parent=rig_module.controls_group,
        shape="sphere",
        lock_channels=["ty", "rx", "rz", "s", "v"],
        scale=rig_scale,
    )
    scapula_ik = pm.ikHandle(
        n=f"{prefix}Scapula_IKH",
        sol="ikSCsolver",
        sj=scapula_joint,
        ee=limb_joints[0],
    )[0]
    pm.hide(scapula_ik)
    pm.parentConstraint(base_attach_group, scapula_ctrl.get_top(), mo=True)
    pm.parent(scapula_ik, scapula_ctrl.get_control())
    pm.pointConstraint(scapula_ctrl.get_control(), scapula_joint)
    return scapula_ctrl


def build_clavicle(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    prefix: str,
    limb_joints: Sequence[str],
    scapula_joint: str,
    rig_scale: float,
    rig_module: module.Module,
    base_attach_group: pm.PyNode,
) -> control.Control:
    """Create a clavicle control that anchors the top of the limb."""
    clavicle_ctrl = control.Control(
        prefix=f"{prefix}Clavicle",
        translate_to=scapula_joint,
        rotate_to=scapula_joint,
        parent=rig_module.controls_group,
        shape="sphere",
        lock_channels=["t", "s", "v"],
        scale=rig_scale,
    )
    scapula_ik = pm.ikHandle(
        n=f"{prefix}Scapula_IKH",
        sol="ikSCsolver",
        sj=scapula_joint,
        ee=limb_joints[0],
    )[0]
    pm.hide(scapula_ik)
    pm.parentConstraint(base_attach_group, clavicle_ctrl.get_top(), mo=True)
    pm.parent(scapula_ik, clavicle_ctrl.get_control())
    pm.pointConstraint(clavicle_ctrl.get_control(), scapula_joint)
    return clavicle_ctrl


def build_dynamic_scapula(limb_joints: Sequence[str], rig_module: module.Module) -> None:
    """Create a dynamic scapula rig if a scapula chain exists."""
    limb_joint_nodes = pm.ls(limb_joints)
    if not limb_joint_nodes:
        return
    shoulder_joint = limb_joint_nodes[0]
    clavicle_joint = shoulder_joint.getParent()
    if not clavicle_joint:
        return
    spine_joint = clavicle_joint.getParent()
    if not spine_joint:
        return
    scapula_joint = next(
        (
            child
            for child in clavicle_joint.getChildren(type="joint")
            if "scapula" in child.name().lower()
        ),
        None,
    )
    if not scapula_joint:
        return
    scapula_instance = scapula.Scapula(spine_joint, shoulder_joint, scapula_joint)
    pm.parent(scapula_instance.get_scapula_grp(), rig_module.parts_group)


def build_fk_controls(  # pylint: disable=too-many-locals
    limb_joints: Sequence[str],
    top_finger_joints: Sequence[str],
    rig_scale: float,
    rig_module: module.Module,
) -> tuple[list[control.Control], list[pm.PyNode], list[control.Control], list[pm.PyNode]]:
    """Create FK controls for the limb and optional finger/toe chains."""
    limb_controls: list[control.Control] = []
    limb_constraints: list[pm.PyNode] = []
    finger_controls: list[control.Control] = []
    finger_constraints: list[pm.PyNode] = []

    for joint_name in limb_joints:
        prefix = name.remove_suffix(joint_name)
        parent = rig_module.controls_group if not limb_controls else limb_controls[-1].get_control()
        ctrl = control.Control(
            prefix=prefix,
            translate_to=joint_name,
            rotate_to=joint_name,
            parent=parent,
            shape="circleX",
            scale=rig_scale,
        )
        orient_constraint = pm.orientConstraint(
            ctrl.get_control(),
            joint_name,
            mo=True,
        )
        limb_controls.append(ctrl)
        limb_constraints.append(orient_constraint)

    finger_fk_offset = pm.group(
        n="fingerFootFKOffset_GRP",
        em=True,
        p=rig_module.controls_group,
    )
    if limb_controls:
        pm.parentConstraint(limb_controls[-1].get_control(), finger_fk_offset, mo=True)

    for finger_root in pm.ls(top_finger_joints):
        finger_chain_controls: list[control.Control] = []
        for joint_name in joint.list_hierarchy(finger_root, include_end_joints=False):
            prefix = name.remove_suffix(joint_name)
            parent = (
                finger_fk_offset
                if not finger_chain_controls
                else finger_chain_controls[-1].get_control()
            )
            ctrl = control.Control(
                prefix=prefix,
                translate_to=joint_name,
                rotate_to=joint_name,
                parent=parent,
                shape="circleX",
                scale=rig_scale,
            )
            orient_constraint = pm.orientConstraint(
                ctrl.get_control(),
                joint_name,
            )
            finger_chain_controls.append(ctrl)
            finger_constraints.append(orient_constraint)
        finger_controls.extend(finger_chain_controls)

    return limb_controls, limb_constraints, finger_controls, finger_constraints


def build_pole_vector(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    ik_handle: pm.PyNode,
    auto_elbow_ctrl: pm.PyNode,
    rig_scale: float,
    rig_module: module.Module,
    body_attach_group: pm.PyNode,
) -> tuple[control.Control, pm.PyNode]:
    """Create a pole vector control connected to the IK handle."""
    prefix = name.remove_suffix(ik_handle)
    pole_vector_instance = pole_vector.PoleVector(ik_handle)
    pole_vector_locator, pole_vector_group = pole_vector_instance.get_pole_vector()
    pm.parent(pole_vector_group, rig_module.parts_no_trans_group)

    pole_vector_ctrl = control.Control(
        prefix=f"{prefix}PV",
        translate_to=pole_vector_locator,
        scale=rig_scale,
        parent=rig_module.controls_group,
        shape="sphere",
    )

    spaces.create_space_switch(
        [body_attach_group, auto_elbow_ctrl],
        ["body", "control"],
        pole_vector_ctrl.get_offset_grp(),
        pole_vector_ctrl.get_control(),
    )
    pole_vector_ctrl.get_control().space.set(1)

    pm.parentConstraint(pole_vector_ctrl.get_control(), pole_vector_locator)

    elbow_joint = ik_handle.getJointList()[1]
    start_position = pm.xform(elbow_joint, q=True, t=True, ws=True)
    end_position = pm.xform(pole_vector_locator, q=True, t=True, ws=True)
    pole_vector_curve = pm.curve(
        n=f"{prefix}Pv_CRV",
        d=1,
        p=[start_position, end_position],
    )
    pm.cluster(
        f"{pole_vector_curve}.cv[0]",
        n=f"{prefix}Pv1_CLS",
        wn=[elbow_joint, elbow_joint],
        bs=True,
    )
    pm.cluster(
        f"{pole_vector_curve}.cv[1]",
        n=f"{prefix}Pv2_CLS",
        wn=[pole_vector_ctrl.get_control(), pole_vector_ctrl.get_control()],
        bs=True,
    )
    pm.parent(pole_vector_curve, rig_module.controls_group)
    pm.setAttr(f"{pole_vector_curve}.template", 1)
    pm.setAttr(f"{pole_vector_curve}.it", 0)

    return pole_vector_ctrl, pole_vector_locator


def build_ik_controls(  # pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-locals,too-many-statements
    limb_joints: Sequence[str],
    top_finger_joints: Sequence[str],
    rig_scale: float,
    rig_module: module.Module,
    use_metacarpal_joint: bool = False,
    smart_foot_roll: bool = True,
    side_prefix: str = "l_",
) -> tuple[
    control.Control,
    pm.PyNode,
    tuple[list[control.Control], list[control.Control]],
    list[pm.PyNode],
    list[pm.PyNode],
    pm.PyNode,
]:
    """Create IK controls for the limb and optional fingers/toes."""
    finger_roots = pm.ls(top_finger_joints)
    prefix = name.remove_suffix(limb_joints[2])

    main_ik_ctrl = control.Control(
        prefix=f"{prefix}IK",
        translate_to=limb_joints[2],
        rotate_to=limb_joints[2],
        parent=rig_module.controls_group,
        shape="circleY",
        scale=rig_scale,
    )

    if not finger_roots:
        ik_handle = pm.ikHandle(
            n=f"{prefix}_IKH",
            sj=limb_joints[0],
            ee=limb_joints[2],
        )[0]
        pm.parent(ik_handle, rig_module.parts_no_trans_group)
        pm.parentConstraint(main_ik_ctrl.get_control(), ik_handle, mo=True)
        hand_orient_constraint = pm.orientConstraint(
            main_ik_ctrl.get_control(),
            limb_joints[2],
            mo=True,
        )
        return main_ik_ctrl, ik_handle, ([], []), [], [], hand_orient_constraint

    metacarpal_joint_list = finger_roots
    top_finger_joint_list: list[pm.PyNode] = []
    end_finger_joint_list: list[pm.PyNode] = []
    for metacarpal in metacarpal_joint_list:
        if use_metacarpal_joint:
            finger_joint = pm.listRelatives(
                metacarpal,
                type="joint",
                children=True,
            )[0]
        else:
            finger_joint = metacarpal
        finger_end_joint = joint.list_hierarchy(
            metacarpal,
            include_end_joints=True,
        )[-1]
        top_finger_joint_list.append(finger_joint)
        end_finger_joint_list.append(finger_end_joint)

    foot_roll_instance = foot_roll.FootRoll(
        limb_joints[0],
        limb_joints[2],
        top_finger_joint_list,
        end_finger_joint_list,
        do_smart_foot_roll=smart_foot_roll,
    )
    foot_roll_group_list = foot_roll_instance.get_group_list()
    pm.parent(foot_roll_group_list[-1], rig_module.parts_no_trans_group)

    mid_finger_index = int(round(len(foot_roll_instance.get_ik_finger_list()) / 2.0)) - 1
    mid_finger_index = max(mid_finger_index, -1)
    mid_finger_joint = foot_roll_instance.get_ik_finger_list()[mid_finger_index].getJointList()[0]
    ball_ctrl = control.Control(
        prefix=f"{prefix}BallIK",
        translate_to=mid_finger_joint,
        rotate_to=mid_finger_joint,
        parent=rig_module.controls_group,
        shape="circleZ",
        scale=rig_scale,
    )

    toe_ik_controls: list[control.Control] = []
    for toe_joint in finger_roots:
        toe_prefix = name.remove_suffix(toe_joint)
        toe_end_joint = pm.listRelatives(toe_joint, ad=True, type="joint")[0]
        toe_ctrl = control.Control(
            prefix=toe_prefix,
            translate_to=toe_end_joint,
            rotate_to=toe_end_joint,
            parent=ball_ctrl.get_control(),
            shape="circleY",
            scale=rig_scale,
        )
        toe_ik_controls.append(toe_ctrl)

    for ik_handle, toe_ctrl in zip(
        foot_roll_instance.get_ik_finger_list(),
        toe_ik_controls,
        strict=False,
    ):
        pm.parentConstraint(toe_ctrl.get_control(), ik_handle)

    pm.parentConstraint(main_ik_ctrl.get_control(), foot_roll_group_list[-1], mo=True)
    pm.parentConstraint(foot_roll_group_list[1], ball_ctrl.get_offset_grp(), mo=True)
    hand_orient_constraint = pm.orientConstraint(
        main_ik_ctrl.get_control(),
        limb_joints[2],
        mo=True,
    )

    ball_roll_grp = foot_roll_group_list[0]
    toe_tap_grp = foot_roll_group_list[1]
    tippy_toe_grp = foot_roll_group_list[2]
    front_roll_grp, back_roll_grp, inner_roll_grp, outer_roll_grp = foot_roll_group_list[3:-1]

    if smart_foot_roll and front_roll_grp and ball_roll_grp and inner_roll_grp and outer_roll_grp:
        roll_attr = attributes.add_float_attribute(
            main_ik_ctrl.get_control(),
            "roll",
            defaultValue=0,
            keyable=True,
            minValue=-120,
            maxValue=120,
        )
        bend_limit_attr = attributes.add_float_attribute(
            main_ik_ctrl.get_control(),
            "bendLimitAngle",
            defaultValue=45,
            keyable=False,
        )
        straight_angle_attr = attributes.add_float_attribute(
            main_ik_ctrl.get_control(),
            "toeStraightAngle",
            defaultValue=70,
            keyable=False,
        )

        heel_clamp = pm.shadingNode(
            "clamp",
            asUtility=True,
            n=f"{prefix}_heelRotClamp",
        )
        pm.connectAttr(roll_attr, heel_clamp.inputR)
        heel_clamp.minR.set(-90)
        pm.connectAttr(heel_clamp.outputR, back_roll_grp.rotateX)

        ball_clamp = pm.shadingNode(
            "clamp",
            asUtility=True,
            n=f"{prefix}_zeroToBendClamp",
        )
        pm.connectAttr(roll_attr, ball_clamp.inputR)

        bend_to_straight = pm.shadingNode(
            "clamp",
            asUtility=True,
            n=f"{prefix}_bendToStraightClamp",
        )
        pm.connectAttr(bend_limit_attr, bend_to_straight.minR)
        pm.connectAttr(straight_angle_attr, bend_to_straight.maxR)
        pm.connectAttr(roll_attr, bend_to_straight.inputR)

        bend_to_straight_range = pm.shadingNode(
            "setRange",
            asUtility=True,
            n=f"{prefix}_bendToStraightPercent",
        )
        pm.connectAttr(bend_to_straight.minR, bend_to_straight_range.oldMinX)
        pm.connectAttr(bend_to_straight.maxR, bend_to_straight_range.oldMaxX)
        bend_to_straight_range.maxX.set(1)
        pm.connectAttr(bend_to_straight.inputR, bend_to_straight_range.valueX)

        roll_multiplier = pm.shadingNode(
            "multiplyDivide",
            asUtility=True,
            n=f"{prefix}_rollMultDiv",
        )
        pm.connectAttr(bend_to_straight_range.outValueX, roll_multiplier.input1X)
        pm.connectAttr(bend_to_straight.inputR, roll_multiplier.input2X)
        pm.connectAttr(roll_multiplier.outputX, tippy_toe_grp.rotateX)

        pm.connectAttr(bend_limit_attr, ball_clamp.maxR)
        zero_to_bend_range = pm.shadingNode(
            "setRange",
            asUtility=True,
            n=f"{prefix}_zeroToBendPercent",
        )
        pm.connectAttr(ball_clamp.minR, zero_to_bend_range.oldMinX)
        pm.connectAttr(ball_clamp.maxR, zero_to_bend_range.oldMaxX)
        zero_to_bend_range.maxX.set(1)
        pm.connectAttr(ball_clamp.inputR, zero_to_bend_range.valueX)

        invert_percent = pm.shadingNode(
            "plusMinusAverage",
            asUtility=True,
            n=f"{prefix}_invertPercent",
        )
        invert_percent.input1D[0].set(1)
        invert_percent.input1D[1].set(1)
        pm.connectAttr(
            bend_to_straight_range.outValueX,
            invert_percent.input1D[1],
        )
        invert_percent.operation.set(2)

        ball_percent_multiplier = pm.shadingNode(
            "multiplyDivide",
            asUtility=True,
            n=f"{prefix}_ballPercentMultDiv",
        )
        pm.connectAttr(zero_to_bend_range.outValueX, ball_percent_multiplier.input1X)
        pm.connectAttr(invert_percent.output1D, ball_percent_multiplier.input2X)

        ball_roll_multiplier = pm.shadingNode(
            "multiplyDivide",
            asUtility=True,
            n=f"{prefix}_ballRollMultDiv",
        )
        pm.connectAttr(
            ball_percent_multiplier.outputX,
            ball_roll_multiplier.input1X,
        )
        pm.connectAttr(roll_attr, ball_roll_multiplier.input2X)
        pm.connectAttr(ball_roll_multiplier.outputX, ball_roll_grp.rotateX)

        tilt_attr = attributes.add_float_attribute(
            main_ik_ctrl.get_control(),
            "tilt",
            defaultValue=0,
            keyable=True,
            minValue=-90,
            maxValue=90,
        )
        if side_prefix in prefix:
            common.set_driven_key(
                tilt_attr,
                [-90, 0, 90],
                inner_roll_grp.rotateZ,
                [90, 0, 0],
            )
            common.set_driven_key(
                tilt_attr,
                [-90, 0, 90],
                outer_roll_grp.rotateZ,
                [0, 0, -90],
            )
        else:
            common.set_driven_key(
                tilt_attr,
                [-90, 0, 90],
                inner_roll_grp.rotateZ,
                [-90, 0, 0],
            )
            common.set_driven_key(
                tilt_attr,
                [-90, 0, 90],
                outer_roll_grp.rotateZ,
                [0, 0, 90],
            )

        lean_attr = attributes.add_float_attribute(
            main_ik_ctrl.get_control(),
            "lean",
            defaultValue=0,
            keyable=True,
            minValue=-90,
            maxValue=90,
        )
        pm.connectAttr(lean_attr, ball_roll_grp.rotateZ)

        toe_spin_attr = attributes.add_float_attribute(
            main_ik_ctrl.get_control(),
            "toeSpin",
            defaultValue=0,
            keyable=True,
            minValue=-90,
            maxValue=90,
        )
        pm.connectAttr(toe_spin_attr, tippy_toe_grp.rotateY)
        tippy_toe_grp.rotateOrder.set(2)

        toe_wiggle_attr = attributes.add_float_attribute(
            main_ik_ctrl.get_control(),
            "toeWiggle",
            defaultValue=0,
            keyable=True,
            minValue=-90,
            maxValue=90,
        )
        pm.connectAttr(toe_wiggle_attr, toe_tap_grp.rotateX)

    return (
        main_ik_ctrl,
        foot_roll_instance.get_limb_ik(),
        ([ball_ctrl], toe_ik_controls),
        foot_roll_instance.get_ik_finger_list(),
        foot_roll_instance.get_ik_ball_list(),
        hand_orient_constraint,
    )


class Limb:  # pylint: disable=too-many-instance-attributes
    """Construct an FK/IK limb module with optional scapula and clavicle controls."""

    def __init__(  # pylint: disable=too-many-arguments,too-many-locals,too-many-branches,too-many-statements,too-many-boolean-expressions
        self,
        limb_joints: Sequence[str] | None = None,
        top_finger_joints: Sequence[str] | None = None,
        *,
        clavicle_joint: str | None = None,
        scapula_joint: str | None = None,
        visibility_ik_fk_ctrl: str | None = None,
        do_fk: bool | None = None,
        do_ik: bool | None = None,
        part: str | None = None,
        use_metacarpal_joint: bool | None = None,
        do_smart_foot_roll: bool | None = None,
        prefix: str | None = None,
        rig_scale: float | None = None,
        base_rig: module.Base | None = None,
        **legacy_kwargs: Any,
    ) -> None:
        """Initialise the limb rig builder."""
        legacy_kwargs = dict(legacy_kwargs)
        limb_joints = parameter_resolution.resolve_required(
            limb_joints,
            legacy_kwargs,
            ("limbJoints",),
            "limb_joints",
        )
        top_finger_joints = parameter_resolution.resolve_optional(
            top_finger_joints,
            legacy_kwargs,
            ("topFingerJoints",),
            [],
        )
        clavicle_joint = parameter_resolution.resolve_optional(
            clavicle_joint,
            legacy_kwargs,
            ("clavicleJoint",),
            "",
        )
        scapula_joint = parameter_resolution.resolve_optional(
            scapula_joint,
            legacy_kwargs,
            ("scapulaJnt",),
            "",
        )
        visibility_ik_fk_ctrl = parameter_resolution.resolve_optional(
            visibility_ik_fk_ctrl,
            legacy_kwargs,
            ("visibilityIKFKCtrl",),
            "ikfk_CTRL",
        )
        do_fk = parameter_resolution.resolve_optional(do_fk, legacy_kwargs, ("doFK",), True)
        do_ik = parameter_resolution.resolve_optional(do_ik, legacy_kwargs, ("doIK",), True)
        part = cast(
            str, parameter_resolution.resolve_optional(part, legacy_kwargs, ("part",), "Hand")
        )
        use_metacarpal_joint = cast(
            bool,
            parameter_resolution.resolve_optional(
                use_metacarpal_joint,
                legacy_kwargs,
                ("useMetacarpalJoint",),
                False,
            ),
        )
        do_smart_foot_roll = cast(
            bool,
            parameter_resolution.resolve_optional(
                do_smart_foot_roll,
                legacy_kwargs,
                ("doSmartFootRool",),
                True,
            ),
        )
        rig_scale = cast(
            float,
            parameter_resolution.resolve_optional(rig_scale, legacy_kwargs, ("rigScale",), 1.0),
        )
        base_rig = parameter_resolution.resolve_optional(
            base_rig, legacy_kwargs, ("baseRig",), None
        )

        if legacy_kwargs:
            raise ValueError(f"Unexpected arguments for Limb: {tuple(legacy_kwargs.keys())}")

        limb_joints = list(cast(Sequence[str], limb_joints))
        top_finger_joints = list(cast(Sequence[str], top_finger_joints))
        if not limb_joints:
            raise ValueError("limb_joints must contain at least one joint.")

        if not prefix:
            prefix = name.remove_suffix(limb_joints[0])

        rig_module = module.Module(prefix=prefix, base_obj=base_rig)
        body_attach_group = pm.group(
            n=f"{prefix}BodyAttach_GRP",
            em=True,
            p=rig_module.parts_group,
        )
        base_attach_group = pm.group(
            n=f"{prefix}BaseAttach_GRP",
            em=True,
            p=rig_module.parts_group,
        )

        self.rig_module = rig_module
        self.body_attach_group = body_attach_group
        self.base_attach_group = base_attach_group

        fk_limb_controls: list[control.Control] = []
        fk_limb_constraints: list[pm.PyNode] = []
        fk_hand_controls: list[control.Control] = []
        fk_hand_constraints: list[pm.PyNode] = []

        if do_fk:
            (
                fk_limb_controls,
                fk_limb_constraints,
                fk_hand_controls,
                fk_hand_constraints,
            ) = self.make_fk(
                limb_joints,
                top_finger_joints,
                rig_scale,
                rig_module,
            )

        main_ik_ctrl: control.Control | None = None
        ik_handle: pm.PyNode | None = None
        finger_controls: tuple[list[control.Control], list[control.Control]] = ([], [])
        finger_ik_handles: list[pm.PyNode] = []
        ball_ik_handles: list[pm.PyNode] = []
        hand_ik_orient_constraint: pm.PyNode | None = None
        pole_vector_ctrl: control.Control | None = None
        pole_vector_locator: pm.PyNode | None = None

        if do_ik:
            (
                main_ik_ctrl,
                ik_handle,
                finger_controls,
                finger_ik_handles,
                ball_ik_handles,
                hand_ik_orient_constraint,
            ) = self.make_ik(
                limb_joints,
                top_finger_joints,
                rig_scale,
                rig_module,
                use_metacarpal_joint=use_metacarpal_joint,
                smart_foot_roll=do_smart_foot_roll,
            )
            pole_vector_ctrl, pole_vector_locator = self.make_pole_vector(
                ik_handle,
                main_ik_ctrl.get_control(),
                rig_scale,
                rig_module,
            )

        if (
            do_fk
            and do_ik
            and main_ik_ctrl
            and ik_handle
            and hand_ik_orient_constraint
            and pole_vector_ctrl
        ):
            visibility_nodes = pm.ls(visibility_ik_fk_ctrl)
            if visibility_nodes:
                self.switch_ik_fk(
                    prefix,
                    part,
                    visibility_nodes[0],
                    fk_limb_controls,
                    fk_limb_constraints,
                    fk_hand_controls,
                    fk_hand_constraints,
                    main_ik_ctrl,
                    ik_handle,
                    finger_controls,
                    finger_ik_handles,
                    ball_ik_handles,
                    pole_vector_ctrl,
                    hand_ik_orient_constraint,
                )

        if do_fk and fk_limb_controls:
            if clavicle_joint and pm.objExists(clavicle_joint):
                clavicle_ctrl = self.make_clavicle(
                    prefix,
                    limb_joints,
                    clavicle_joint,
                    rig_scale,
                    rig_module,
                )
                pm.parentConstraint(
                    clavicle_ctrl.get_control(),
                    fk_limb_controls[0].get_top(),
                    mo=True,
                )
            else:
                pm.parentConstraint(
                    self.base_attach_group,
                    fk_limb_controls[0].get_top(),
                    mo=True,
                )

        if scapula_joint and pm.objExists(scapula_joint):
            limb_joint_nodes = pm.ls(limb_joints)
            scapula_ctrl = None
            if limb_joint_nodes and limb_joint_nodes[0].getParent():
                shoulder_parent = limb_joint_nodes[0].getParent()
                target_joint = pm.ls(scapula_joint)
                if target_joint and shoulder_parent.name() == target_joint[0].name():
                    scapula_ctrl = self.make_simple_scapula(
                        prefix,
                        limb_joints,
                        scapula_joint,
                        rig_scale,
                        rig_module,
                    )
                else:
                    self.make_dynamic_scapula(limb_joints, rig_module)

            if scapula_ctrl and fk_limb_controls:
                pm.parentConstraint(
                    scapula_ctrl.get_control(),
                    fk_limb_controls[0].get_top(),
                    mo=True,
                )

        self.limb_ik = ik_handle
        self.main_ik_control = main_ik_ctrl
        self.pole_vector_control = pole_vector_ctrl
        self.pole_vector_locator = pole_vector_locator

    def get_main_limb_ik(self) -> pm.PyNode | None:
        """Return the main IK handle created for the limb."""
        return self.limb_ik

    def get_main_ik_control(self) -> control.Control | None:
        """Return the main IK control wrapper."""
        return self.main_ik_control

    def get_module_dict(self) -> dict[str, Any]:
        """Return rig module bookkeeping data."""
        return {
            "module": self.rig_module,
            "module_obj": self.rig_module,
            "rig_module": self.rig_module,
            "base_attach_grp": self.base_attach_group,
            "body_attach_grp": self.body_attach_group,
        }

    def switch_ik_fk(  # pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-locals,too-many-branches,too-many-boolean-expressions
        self,
        prefix: str,
        part: str,
        visibility_ctrl: pm.PyNode,
        fk_limb_controls: Sequence[control.Control],
        fk_limb_constraints: Sequence[pm.PyNode],
        fk_hand_controls: Sequence[control.Control],
        fk_hand_constraints: Sequence[pm.PyNode],
        main_ik_ctrl: control.Control,
        ik_handle: pm.PyNode,
        finger_controls: tuple[Sequence[control.Control], Sequence[control.Control]],
        finger_ik_handles: Sequence[pm.PyNode],
        ball_ik_handles: Sequence[pm.PyNode],
        pole_vector_ctrl: control.Control,
        hand_ik_orient_constraint: pm.PyNode,
    ) -> None:
        """Wire IK/FK switch attributes and visibility toggles."""
        if not pm.objExists("switchIKFK_LOC"):
            switch_locator = pm.spaceLocator(n="switchIKFK_LOC")[0]
            pm.parent(switch_locator, "rig_GRP")
            pm.hide(switch_locator)
            util.lock_and_hide_all(switch_locator)
        else:
            switch_locator = pm.ls("switchIKFK_LOC")[0]

        control_attr = prefix
        part_control_attr = f"{prefix}{part}"

        for node in (switch_locator, visibility_ctrl):
            if not node.hasAttr(control_attr):
                pm.addAttr(
                    node,
                    longName=control_attr,
                    attributeType="double",
                    defaultValue=0,
                    minValue=0,
                    maxValue=1,
                    k=True,
                )
            if not node.hasAttr(part_control_attr):
                pm.addAttr(
                    node,
                    longName=part_control_attr,
                    attributeType="double",
                    defaultValue=1 if part == "Hand" and node is switch_locator else 0,
                    minValue=0,
                    maxValue=1,
                    k=True,
                )

        pm.connectAttr(
            f"{visibility_ctrl}.{control_attr}",
            f"{switch_locator}.{control_attr}",
            f=True,
        )
        pm.connectAttr(
            f"{visibility_ctrl}.{part_control_attr}",
            f"{switch_locator}.{part_control_attr}",
            f=True,
        )

        reverse_node = pm.shadingNode(
            "reverse",
            asUtility=True,
            n=f"{prefix}ReverseNode",
        )
        part_reverse_node = pm.shadingNode(
            "reverse",
            asUtility=True,
            n=f"{prefix}{part}ReverseNode",
        )
        pm.connectAttr(f"{switch_locator}.{control_attr}", reverse_node.inputX)
        pm.connectAttr(
            f"{switch_locator}.{part_control_attr}",
            part_reverse_node.inputX,
        )

        pm.connectAttr(reverse_node.outputX, main_ik_ctrl.get_top().visibility)
        pm.connectAttr(reverse_node.outputX, ik_handle.ikBlend)
        ik_constraint_attr = pm.listConnections(
            hand_ik_orient_constraint.target[1].targetWeight,
            p=True,
            s=True,
        )[0]
        pm.connectAttr(reverse_node.outputX, ik_constraint_attr)

        for ctrl in finger_controls[0]:
            pm.connectAttr(
                part_reverse_node.outputX,
                ctrl.get_top().visibility,
            )
        for ctrl in finger_controls[1]:
            pm.connectAttr(
                part_reverse_node.outputX,
                ctrl.get_top().visibility,
            )

        for ik_node in finger_ik_handles:
            pm.connectAttr(part_reverse_node.outputX, ik_node.ikBlend)
        for ball_ik in ball_ik_handles:
            pm.connectAttr(part_reverse_node.outputX, ball_ik.ikBlend)

        pm.connectAttr(
            reverse_node.outputX,
            pole_vector_ctrl.get_top().visibility,
        )

        for ctrl in fk_limb_controls:
            pm.connectAttr(
                f"{switch_locator}.{control_attr}",
                ctrl.get_top().visibility,
            )
        for constraint in fk_limb_constraints:
            attr = pm.listConnections(
                constraint.target[0].targetWeight,
                p=True,
                s=True,
            )[0]
            pm.connectAttr(f"{switch_locator}.{control_attr}", attr)

        for ctrl in fk_hand_controls:
            pm.connectAttr(
                f"{switch_locator}.{part_control_attr}",
                ctrl.get_top().visibility,
            )
        for constraint in fk_hand_constraints:
            attr = pm.listConnections(
                constraint.target[0].targetWeight,
                p=True,
                s=True,
            )[0]
            pm.connectAttr(f"{switch_locator}.{part_control_attr}", attr)

        if fk_limb_controls and fk_hand_controls and fk_hand_constraints:
            fk_finger_constraint = pm.parentConstraint(
                main_ik_ctrl.get_control(),
                fk_hand_controls[0].get_top().getParent(),
                mo=True,
            )
            target_names = fk_finger_constraint.getTargetList()
            pm.connectAttr(
                reverse_node.outputX,
                f"{fk_finger_constraint}.{target_names[1]}W1",
                f=True,
            )
            pm.connectAttr(
                f"{switch_locator}.{control_attr}",
                f"{fk_finger_constraint}.{target_names[0]}W0",
                f=True,
            )

    def make_simple_scapula(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        prefix: str,
        limb_joints: Sequence[str],
        scapula_joint: str,
        rig_scale: float,
        rig_module: module.Module,
    ) -> control.Control:
        """Create a simple scapula control."""
        return build_simple_scapula(
            prefix,
            limb_joints,
            scapula_joint,
            rig_scale,
            rig_module,
            self.base_attach_group,
        )

    def make_clavicle(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        prefix: str,
        limb_joints: Sequence[str],
        scapula_joint: str,
        rig_scale: float,
        rig_module: module.Module,
    ) -> control.Control:
        """Create the clavicle control."""
        return build_clavicle(
            prefix,
            limb_joints,
            scapula_joint,
            rig_scale,
            rig_module,
            self.base_attach_group,
        )

    def make_dynamic_scapula(
        self,
        limb_joints: Sequence[str],
        rig_module: module.Module,
    ) -> None:
        """Create the dynamic scapula setup."""
        build_dynamic_scapula(limb_joints, rig_module)

    def make_fk(
        self,
        limb_joints: Sequence[str],
        top_finger_joints: Sequence[str],
        rig_scale: float,
        rig_module: module.Module,
    ) -> tuple[list[control.Control], list[pm.PyNode], list[control.Control], list[pm.PyNode]]:
        """Build FK controls for the limb."""
        return build_fk_controls(
            limb_joints,
            top_finger_joints,
            rig_scale,
            rig_module,
        )

    def make_pole_vector(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        ik_handle: pm.PyNode,
        auto_elbow_ctrl: pm.PyNode,
        rig_scale: float,
        rig_module: module.Module,
    ) -> tuple[control.Control, pm.PyNode]:
        """Create the pole vector control."""
        return build_pole_vector(
            ik_handle,
            auto_elbow_ctrl,
            rig_scale,
            rig_module,
            self.body_attach_group,
        )

    def make_ik(  # pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-locals
        self,
        limb_joints: Sequence[str],
        top_finger_joints: Sequence[str],
        rig_scale: float,
        rig_module: module.Module,
        *,
        use_metacarpal_joint: bool = False,
        smart_foot_roll: bool = True,
    ) -> tuple[
        control.Control,
        pm.PyNode,
        tuple[list[control.Control], list[control.Control]],
        list[pm.PyNode],
        list[pm.PyNode],
        pm.PyNode,
    ]:
        """Build IK controls for the limb."""
        return build_ik_controls(
            limb_joints,
            top_finger_joints,
            rig_scale,
            rig_module,
            use_metacarpal_joint=use_metacarpal_joint,
            smart_foot_roll=smart_foot_roll,
        )


class Arm(Limb):
    """Backwards-compatible wrapper around :class:`Limb` for arm rigs."""

    def __init__(  # pylint: disable=too-many-arguments,too-many-locals
        self,
        clavicle_joint: str,
        shoulder_joint: str,
        forearm_joint: str,
        wrist_joint: str,
        *,
        top_finger_joints: Sequence[str] | None = None,
        scapula_joint: str = "",
        visibility_ik_fk_ctrl: str = "ikfk_CTRL",
        do_fk: bool = True,
        do_ik: bool = True,
        prefix: str | None = None,
        rig_scale: float = 1.0,
        base_rig: module.Base | None = None,
        **legacy_kwargs: Any,
    ) -> None:
        """Initialise the arm rig builder."""
        legacy_kwargs = dict(legacy_kwargs)
        if "clavicleJoint" in legacy_kwargs and not clavicle_joint:
            clavicle_joint = legacy_kwargs.pop("clavicleJoint")
        if "shoulderJoint" in legacy_kwargs:
            shoulder_joint = legacy_kwargs.pop("shoulderJoint")
        if "forearmJoint" in legacy_kwargs:
            forearm_joint = legacy_kwargs.pop("forearmJoint")
        if "wristJoint" in legacy_kwargs:
            wrist_joint = legacy_kwargs.pop("wristJoint")
        if "scapulaJnt" in legacy_kwargs and not scapula_joint:
            scapula_joint = legacy_kwargs.pop("scapulaJnt")

        top_finger_joints = list(top_finger_joints or legacy_kwargs.pop("topFingerJoints", []))
        use_metacarpal_joint = legacy_kwargs.pop("useMetacarpalJoint", False)
        do_smart_foot_roll = legacy_kwargs.pop("doSmartFootRool", True)

        if legacy_kwargs:
            raise ValueError(f"Unexpected arguments for Arm: {tuple(legacy_kwargs.keys())}")

        super().__init__(
            limb_joints=[shoulder_joint, forearm_joint, wrist_joint],
            top_finger_joints=top_finger_joints,
            clavicle_joint=clavicle_joint,
            scapula_joint=scapula_joint,
            visibility_ik_fk_ctrl=visibility_ik_fk_ctrl,
            do_fk=do_fk,
            do_ik=do_ik,
            part="Hand",
            use_metacarpal_joint=use_metacarpal_joint,
            do_smart_foot_roll=do_smart_foot_roll,
            prefix=prefix,
            rig_scale=rig_scale,
            base_rig=base_rig,
        )


# Backwards compatibility aliases
Limb.getMainLimbIK = Limb.get_main_limb_ik
Limb.getMainIKControl = Limb.get_main_ik_control
Limb.getModuleDict = Limb.get_module_dict
Limb.switchIKFK = Limb.switch_ik_fk
Limb.makeSimpleScapula = Limb.make_simple_scapula
Limb.makeClavicle = Limb.make_clavicle
Limb.makeDynamicScapula = Limb.make_dynamic_scapula
Limb.makeFK = Limb.make_fk
Limb.makePoleVector = Limb.make_pole_vector
Limb.makeIK = Limb.make_ik


if __name__ == "__main__":
    raise SystemExit("Invoke within Maya to construct limb rigs.")

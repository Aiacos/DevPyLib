"""Limb rig module with FK/IK construction, scapula, and foot roll support.

Provides stateless builder functions (:func:`build_fk_controls`,
:func:`build_ik_controls`, etc.) and a stateful orchestrator class
(:class:`Limb`) that wires them together into a complete limb module
with IK/FK switching, pole vector, and optional scapula/clavicle controls.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, NamedTuple, cast

import pymel.core as pm

from mayaLib.rigLib.base import module
from mayaLib.rigLib.utils import (
    control,
    foot_roll,
    ikfk_switch,
    joint,
    name,
    parameter_resolution,
    pole_vector,  # type: ignore
    scapula,
    smart_foot_roll,
    spaces,
)

__all__ = [
    "FKResult",
    "IKResult",
    "Limb",
    "Arm",
    "build_simple_scapula",
    "build_clavicle",
    "build_dynamic_scapula",
    "build_fk_controls",
    "build_pole_vector",
    "build_ik_controls",
]


# ---------------------------------------------------------------------------
# Structured return types
# ---------------------------------------------------------------------------


class FKResult(NamedTuple):
    """Results from FK control construction.

    Attributes:
        limb_controls: FK control instances for the main limb chain.
        limb_constraints: Orient constraints driving limb joints from FK controls.
        finger_controls: FK control instances for fingers/toes.
        finger_constraints: Orient constraints driving finger/toe joints.
    """

    limb_controls: list[control.Control]
    limb_constraints: list[pm.PyNode]
    finger_controls: list[control.Control]
    finger_constraints: list[pm.PyNode]


class IKResult(NamedTuple):
    """Results from IK control construction.

    Attributes:
        main_ctrl: Main IK control instance for the limb end effector.
        ik_handle: IK handle driving the limb chain.
        finger_controls: Tuple of (ball controls, toe IK controls).
        finger_ik_handles: IK handles for each finger/toe.
        ball_ik_handles: IK handles for ball joints.
        orient_constraint: Orient constraint on the hand/foot joint.
    """

    main_ctrl: control.Control
    ik_handle: pm.PyNode
    finger_controls: tuple[list[control.Control], list[control.Control]]
    finger_ik_handles: list[pm.PyNode]
    ball_ik_handles: list[pm.PyNode]
    orient_constraint: pm.PyNode


# ---------------------------------------------------------------------------
# Free functions — stateless builders
# ---------------------------------------------------------------------------


def _build_control_with_ik_handle(
    ctrl: control.Control,
    ik_name: str,
    scapula_joint: str,
    limb_joints: Sequence[str],
    base_attach_group: pm.PyNode,
) -> None:
    """Create and configure an IK handle for a control.

    Args:
        ctrl: The control to attach the IK handle to.
        ik_name: Name for the IK handle.
        scapula_joint: Joint to constrain with point constraint.
        limb_joints: Sequence of limb joints (first joint is the IK end effector).
        base_attach_group: Group to parent constrain the control to.
    """
    scapula_ik = pm.ikHandle(
        n=ik_name,
        sol="ikSCsolver",
        sj=scapula_joint,
        ee=limb_joints[0],
    )[0]
    pm.hide(scapula_ik)
    pm.parentConstraint(base_attach_group, ctrl.get_top(), mo=True)
    pm.parent(scapula_ik, ctrl.get_control())
    pm.pointConstraint(ctrl.get_control(), scapula_joint)


def build_simple_scapula(
    prefix: str,
    limb_joints: Sequence[str],
    scapula_joint: str,
    rig_scale: float,
    rig_module: module.Module,
    base_attach_group: pm.PyNode,
) -> control.Control:
    """Create a simple scapula control that follows the body attach group.

    Args:
        prefix: Naming prefix for the control (e.g. ``"l_shoulder1"``).
        limb_joints: Joint chain for the limb.
        scapula_joint: Name of the scapula joint.
        rig_scale: Global rig scale factor.
        rig_module: Parent rig module for hierarchy.
        base_attach_group: Group to parent-constrain the scapula control to.

    Returns:
        The created scapula control instance.
    """
    scapula_ctrl = control.Control(
        prefix=f"{prefix}Scapula",
        translate_to=scapula_joint,
        rotate_to=scapula_joint,
        parent=rig_module.controls_group,
        shape="sphere",
        lock_channels=["ty", "rx", "rz", "s", "v"],
        scale=rig_scale,
    )
    _build_control_with_ik_handle(
        ctrl=scapula_ctrl,
        ik_name=f"{prefix}Scapula_IKH",
        scapula_joint=scapula_joint,
        limb_joints=limb_joints,
        base_attach_group=base_attach_group,
    )
    return scapula_ctrl


def build_clavicle(
    prefix: str,
    limb_joints: Sequence[str],
    scapula_joint: str,
    rig_scale: float,
    rig_module: module.Module,
    base_attach_group: pm.PyNode,
) -> control.Control:
    """Create a clavicle control that anchors the top of the limb.

    Args:
        prefix: Naming prefix for the control.
        limb_joints: Joint chain for the limb.
        scapula_joint: Name of the clavicle/scapula joint to attach to.
        rig_scale: Global rig scale factor.
        rig_module: Parent rig module for hierarchy.
        base_attach_group: Group to parent-constrain the clavicle control to.

    Returns:
        The created clavicle control instance.
    """
    clavicle_ctrl = control.Control(
        prefix=f"{prefix}Clavicle",
        translate_to=scapula_joint,
        rotate_to=scapula_joint,
        parent=rig_module.controls_group,
        shape="sphere",
        lock_channels=["t", "s", "v"],
        scale=rig_scale,
    )
    _build_control_with_ik_handle(
        ctrl=clavicle_ctrl,
        ik_name=f"{prefix}Scapula_IKH",
        scapula_joint=scapula_joint,
        limb_joints=limb_joints,
        base_attach_group=base_attach_group,
    )
    return clavicle_ctrl


def build_dynamic_scapula(limb_joints: Sequence[str], rig_module: module.Module) -> None:
    """Create a dynamic scapula rig if a scapula chain exists.

    Searches the joint hierarchy above the shoulder for a joint whose name
    contains ``"scapula"`` and, if found, builds a ``Scapula`` module parented
    under the rig module's parts group.

    Args:
        limb_joints: Joint chain for the limb (first entry is shoulder).
        rig_module: Parent rig module for hierarchy.
    """
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


def build_fk_controls(
    limb_joints: Sequence[str],
    top_finger_joints: Sequence[str],
    rig_scale: float,
    rig_module: module.Module,
) -> FKResult:
    """Create FK controls for the limb and optional finger/toe chains.

    Builds one FK control per limb joint with orient constraints, then iterates
    over finger/toe root joints to create per-chain FK controls parented under
    a shared offset group.

    Args:
        limb_joints: Main limb joint names (e.g. shoulder, elbow, wrist).
        top_finger_joints: Root joints for each finger/toe chain.
        rig_scale: Global rig scale factor.
        rig_module: Parent rig module for hierarchy.

    Returns:
        :class:`FKResult` containing controls and constraints for both limb
        and finger chains.
    """
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
        orient_constraint = pm.orientConstraint(ctrl.get_control(), joint_name, mo=True)
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
            orient_constraint = pm.orientConstraint(ctrl.get_control(), joint_name)
            finger_chain_controls.append(ctrl)
            finger_constraints.append(orient_constraint)
        finger_controls.extend(finger_chain_controls)

    return FKResult(limb_controls, limb_constraints, finger_controls, finger_constraints)


def build_pole_vector(
    ik_handle: pm.PyNode,
    auto_elbow_ctrl: pm.PyNode,
    rig_scale: float,
    rig_module: module.Module,
    body_attach_group: pm.PyNode,
) -> tuple[control.Control, pm.PyNode]:
    """Create a pole vector control connected to the IK handle.

    Builds the pole vector locator, a space-switchable control, and a display
    curve connecting the elbow joint to the pole vector position.

    Args:
        ik_handle: The IK handle to create the pole vector for.
        auto_elbow_ctrl: Control used as the secondary space-switch target.
        rig_scale: Global rig scale factor.
        rig_module: Parent rig module for hierarchy.
        body_attach_group: Primary space-switch target for the pole vector.

    Returns:
        Tuple of (pole_vector_control, pole_vector_locator).
    """
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


def build_ik_controls(
    limb_joints: Sequence[str],
    top_finger_joints: Sequence[str],
    rig_scale: float,
    rig_module: module.Module,
    use_metacarpal_joint: bool = False,
    do_smart_foot_roll: bool = True,
    side_prefix: str = "l_",
) -> IKResult:
    """Create IK controls for the limb and optional fingers/toes.

    When *top_finger_joints* is empty, builds a simple IK handle with a parent
    constraint.  Otherwise builds the full foot-roll hierarchy with per-toe
    IK controls and optionally wires the smart foot roll utility nodes.

    Args:
        limb_joints: Main limb joint names (shoulder, elbow, wrist/ankle).
        top_finger_joints: Root joints for each finger/toe chain.
        rig_scale: Global rig scale factor.
        rig_module: Parent rig module for hierarchy.
        use_metacarpal_joint: Skip one joint level to reach the actual finger.
        do_smart_foot_roll: Wire the smart foot roll node network.
        side_prefix: Side identifier (e.g. ``"l_"``) for tilt direction.

    Returns:
        :class:`IKResult` containing the main IK control, handles, finger
        controls, and orient constraint.
    """
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
            main_ik_ctrl.get_control(), limb_joints[2], mo=True
        )
        return IKResult(main_ik_ctrl, ik_handle, ([], []), [], [], hand_orient_constraint)

    # Resolve finger joints
    top_finger_joint_list, end_finger_joint_list = _resolve_finger_joints(
        finger_roots, use_metacarpal_joint
    )

    foot_roll_instance = foot_roll.FootRoll(
        limb_joints[0],
        limb_joints[2],
        top_finger_joint_list,
        end_finger_joint_list,
        do_smart_foot_roll=do_smart_foot_roll,
    )
    foot_roll_group_list = foot_roll_instance.get_group_list()
    pm.parent(foot_roll_group_list[-1], rig_module.parts_no_trans_group)

    # Ball control at midpoint of finger chain
    mid_finger_index = max(int(round(len(foot_roll_instance.get_ik_finger_list()) / 2.0)) - 1, -1)
    mid_finger_joint = foot_roll_instance.get_ik_finger_list()[mid_finger_index].getJointList()[0]
    ball_ctrl = control.Control(
        prefix=f"{prefix}BallIK",
        translate_to=mid_finger_joint,
        rotate_to=mid_finger_joint,
        parent=rig_module.controls_group,
        shape="circleZ",
        scale=rig_scale,
    )

    # Toe IK controls
    toe_ik_controls = _build_toe_ik_controls(finger_roots, rig_scale, ball_ctrl)

    for ik_handle_node, toe_ctrl in zip(
        foot_roll_instance.get_ik_finger_list(), toe_ik_controls, strict=False
    ):
        pm.parentConstraint(toe_ctrl.get_control(), ik_handle_node)

    pm.parentConstraint(main_ik_ctrl.get_control(), foot_roll_group_list[-1], mo=True)
    pm.parentConstraint(foot_roll_group_list[1], ball_ctrl.get_offset_grp(), mo=True)
    hand_orient_constraint = pm.orientConstraint(
        main_ik_ctrl.get_control(), limb_joints[2], mo=True
    )

    # Smart foot roll wiring
    ball_roll_grp = foot_roll_group_list[0]
    toe_tap_grp = foot_roll_group_list[1]
    tippy_toe_grp = foot_roll_group_list[2]
    (
        front_roll_grp,
        back_roll_grp,
        inner_roll_grp,
        outer_roll_grp,
    ) = foot_roll_group_list[3:-1]

    has_roll_groups = front_roll_grp and ball_roll_grp and inner_roll_grp and outer_roll_grp
    if do_smart_foot_roll and has_roll_groups:
        smart_foot_roll.build(
            prefix=prefix,
            side_prefix=side_prefix,
            ik_ctrl=main_ik_ctrl.get_control(),
            ball_roll_grp=ball_roll_grp,
            toe_tap_grp=toe_tap_grp,
            tippy_toe_grp=tippy_toe_grp,
            back_roll_grp=back_roll_grp,
            inner_roll_grp=inner_roll_grp,
            outer_roll_grp=outer_roll_grp,
        )

    return IKResult(
        main_ik_ctrl,
        foot_roll_instance.get_limb_ik(),
        ([ball_ctrl], toe_ik_controls),
        foot_roll_instance.get_ik_finger_list(),
        foot_roll_instance.get_ik_ball_list(),
        hand_orient_constraint,
    )


def _resolve_finger_joints(
    finger_roots: list[pm.PyNode],
    use_metacarpal_joint: bool,
) -> tuple[list[pm.PyNode], list[pm.PyNode]]:
    """Resolve top and end finger joints from metacarpal roots.

    Args:
        finger_roots: Metacarpal/finger root joints.
        use_metacarpal_joint: Whether to skip one level to the actual finger joint.

    Returns:
        Tuple of (top_finger_joints, end_finger_joints).
    """
    top_joints: list[pm.PyNode] = []
    end_joints: list[pm.PyNode] = []
    for metacarpal in finger_roots:
        if use_metacarpal_joint:
            finger_joint = pm.listRelatives(metacarpal, type="joint", children=True)[0]
        else:
            finger_joint = metacarpal
        finger_end = joint.list_hierarchy(metacarpal, include_end_joints=True)[-1]
        top_joints.append(finger_joint)
        end_joints.append(finger_end)
    return top_joints, end_joints


def _build_toe_ik_controls(
    finger_roots: list[pm.PyNode],
    rig_scale: float,
    ball_ctrl: control.Control,
) -> list[control.Control]:
    """Build individual IK controls for each toe/finger chain.

    Args:
        finger_roots: Root joints for each finger/toe chain.
        rig_scale: Scale factor for controls.
        ball_ctrl: Parent control for toe controls.

    Returns:
        List of toe IK controls.
    """
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
    return toe_ik_controls


# ---------------------------------------------------------------------------
# Limb class — stateful orchestrator
# ---------------------------------------------------------------------------


class Limb:
    """Construct an FK/IK limb module with optional scapula and clavicle controls."""

    def __init__(
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
        """Initialise the limb rig builder.

        Orchestrates FK/IK construction through five phases: parameter
        resolution, scaffold creation, FK build, IK build, and switching setup.
        Legacy camelCase keyword arguments are accepted for backwards
        compatibility.

        Args:
            limb_joints: Main limb joint names (e.g. shoulder, elbow, wrist).
            top_finger_joints: Root joints for finger/toe chains.
            clavicle_joint: Clavicle joint name (arm rigs only).
            scapula_joint: Scapula joint name for scapula control.
            visibility_ik_fk_ctrl: Name of the IK/FK visibility switch control.
            do_fk: Whether to build FK controls.
            do_ik: Whether to build IK controls.
            part: Part label (``"Hand"`` or ``"Foot"``).
            use_metacarpal_joint: Skip one joint level for fingers.
            do_smart_foot_roll: Wire smart foot roll node network.
            prefix: Naming prefix (auto-derived from first joint if omitted).
            rig_scale: Global rig scale factor.
            base_rig: Base rig instance for module attachment.
            **legacy_kwargs: CamelCase aliases for backwards compatibility.
        """
        params = self._resolve_params(
            limb_joints,
            top_finger_joints,
            clavicle_joint,
            scapula_joint,
            visibility_ik_fk_ctrl,
            do_fk,
            do_ik,
            part,
            use_metacarpal_joint,
            do_smart_foot_roll,
            prefix,
            rig_scale,
            base_rig,
            legacy_kwargs,
        )

        self._build_scaffold(params["prefix"], params["base_rig"])

        fk = self._build_fk(params)
        ik, pv = self._build_ik(params)
        self._setup_switching(params, fk, ik, pv)
        self._setup_scapula_clavicle(params, fk)

        self.limb_ik = ik.ik_handle if ik else None
        self.main_ik_control = ik.main_ctrl if ik else None
        self.pole_vector_control = pv
        self.pole_vector_locator = None

    def _resolve_params(
        self,
        limb_joints,
        top_finger_joints,
        clavicle_joint,
        scapula_joint,
        visibility_ik_fk_ctrl,
        do_fk,
        do_ik,
        part,
        use_metacarpal_joint,
        do_smart_foot_roll,
        prefix,
        rig_scale,
        base_rig,
        legacy_kwargs,
    ) -> dict[str, Any]:
        """Resolve and validate all constructor parameters.

        Handles legacy camelCase keyword arguments for backwards compatibility.

        Returns:
            Dictionary of resolved parameter values.
        """
        legacy_kwargs = dict(legacy_kwargs)
        limb_joints = parameter_resolution.resolve_required(
            limb_joints, legacy_kwargs, ("limbJoints",), "limb_joints"
        )
        top_finger_joints = parameter_resolution.resolve_optional(
            top_finger_joints, legacy_kwargs, ("topFingerJoints",), []
        )
        clavicle_joint = parameter_resolution.resolve_optional(
            clavicle_joint, legacy_kwargs, ("clavicleJoint",), ""
        )
        scapula_joint = parameter_resolution.resolve_optional(
            scapula_joint, legacy_kwargs, ("scapulaJnt",), ""
        )
        visibility_ik_fk_ctrl = parameter_resolution.resolve_optional(
            visibility_ik_fk_ctrl, legacy_kwargs, ("visibilityIKFKCtrl",), "ikfk_CTRL"
        )
        do_fk = parameter_resolution.resolve_optional(do_fk, legacy_kwargs, ("doFK",), True)
        do_ik = parameter_resolution.resolve_optional(do_ik, legacy_kwargs, ("doIK",), True)
        part = cast(
            str,
            parameter_resolution.resolve_optional(part, legacy_kwargs, ("part",), "Hand"),
        )
        use_metacarpal_joint = cast(
            bool,
            parameter_resolution.resolve_optional(
                use_metacarpal_joint, legacy_kwargs, ("useMetacarpalJoint",), False
            ),
        )
        do_smart_foot_roll = cast(
            bool,
            parameter_resolution.resolve_optional(
                do_smart_foot_roll, legacy_kwargs, ("doSmartFootRool",), True
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

        return {
            "limb_joints": limb_joints,
            "top_finger_joints": top_finger_joints,
            "clavicle_joint": clavicle_joint,
            "scapula_joint": scapula_joint,
            "visibility_ik_fk_ctrl": visibility_ik_fk_ctrl,
            "do_fk": do_fk,
            "do_ik": do_ik,
            "part": part,
            "use_metacarpal_joint": use_metacarpal_joint,
            "do_smart_foot_roll": do_smart_foot_roll,
            "prefix": prefix,
            "rig_scale": rig_scale,
            "base_rig": base_rig,
        }

    def _build_scaffold(self, prefix: str, base_rig: module.Base | None) -> None:
        """Create the rig module and attach groups.

        Sets ``self.rig_module``, ``self.body_attach_group``, and ``self.base_attach_group``.
        """
        self.rig_module = module.Module(prefix=prefix, base_obj=base_rig)
        self.body_attach_group = pm.group(
            n=f"{prefix}BodyAttach_GRP", em=True, p=self.rig_module.parts_group
        )
        self.base_attach_group = pm.group(
            n=f"{prefix}BaseAttach_GRP", em=True, p=self.rig_module.parts_group
        )

    def _build_fk(self, params: dict[str, Any]) -> FKResult | None:
        """Build FK controls if requested.

        Returns:
            FKResult or None if FK was not requested.
        """
        if not params["do_fk"]:
            return None
        return self.make_fk(
            params["limb_joints"],
            params["top_finger_joints"],
            params["rig_scale"],
            self.rig_module,
        )

    def _build_ik(self, params: dict[str, Any]) -> tuple[IKResult | None, control.Control | None]:
        """Build IK controls and pole vector if requested.

        Returns:
            Tuple of (IKResult, pole_vector_ctrl) or (None, None).
        """
        if not params["do_ik"]:
            return None, None
        ik = self.make_ik(
            params["limb_joints"],
            params["top_finger_joints"],
            params["rig_scale"],
            self.rig_module,
            use_metacarpal_joint=params["use_metacarpal_joint"],
            smart_foot_roll=params["do_smart_foot_roll"],
        )
        pv, pv_loc = self.make_pole_vector(
            ik.ik_handle,
            ik.main_ctrl.get_control(),
            params["rig_scale"],
            self.rig_module,
        )
        self.pole_vector_locator = pv_loc
        return ik, pv

    def _setup_switching(
        self,
        params: dict[str, Any],
        fk: FKResult | None,
        ik: IKResult | None,
        pole_vector_ctrl: control.Control | None,
    ) -> None:
        """Wire IK/FK switching if both systems were built.

        Args:
            params: Resolved parameter dictionary from :meth:`_resolve_params`.
            fk: FK build results, or ``None`` if FK was skipped.
            ik: IK build results, or ``None`` if IK was skipped.
            pole_vector_ctrl: Pole vector control, or ``None`` if IK was skipped.
        """
        if not (params["do_fk"] and params["do_ik"] and ik and fk and pole_vector_ctrl):
            return

        visibility_nodes = pm.ls(params["visibility_ik_fk_ctrl"])
        if not visibility_nodes:
            return

        self.switch_ik_fk(
            params["prefix"],
            params["part"],
            visibility_nodes[0],
            fk.limb_controls,
            fk.limb_constraints,
            fk.finger_controls,
            fk.finger_constraints,
            ik.main_ctrl,
            ik.ik_handle,
            ik.finger_controls,
            ik.finger_ik_handles,
            ik.ball_ik_handles,
            pole_vector_ctrl,
            ik.orient_constraint,
        )

    def _setup_scapula_clavicle(self, params: dict[str, Any], fk: FKResult | None) -> None:
        """Attach clavicle and/or scapula controls to the FK chain.

        Args:
            params: Resolved parameter dictionary from :meth:`_resolve_params`.
            fk: FK build results, or ``None`` if FK was skipped.
        """
        if not params["do_fk"] or not fk or not fk.limb_controls:
            return

        clavicle_joint = params["clavicle_joint"]
        scapula_joint = params["scapula_joint"]
        prefix = params["prefix"]
        limb_joints = params["limb_joints"]
        rig_scale = params["rig_scale"]

        if clavicle_joint and pm.objExists(clavicle_joint):
            clavicle_ctrl = self.make_clavicle(
                prefix, limb_joints, clavicle_joint, rig_scale, self.rig_module
            )
            pm.parentConstraint(clavicle_ctrl.get_control(), fk.limb_controls[0].get_top(), mo=True)
        else:
            pm.parentConstraint(self.base_attach_group, fk.limb_controls[0].get_top(), mo=True)

        if scapula_joint and pm.objExists(scapula_joint):
            limb_joint_nodes = pm.ls(limb_joints)
            scapula_ctrl = None
            if limb_joint_nodes and limb_joint_nodes[0].getParent():
                shoulder_parent = limb_joint_nodes[0].getParent()
                target_joint = pm.ls(scapula_joint)
                if target_joint and shoulder_parent.name() == target_joint[0].name():
                    scapula_ctrl = self.make_simple_scapula(
                        prefix, limb_joints, scapula_joint, rig_scale, self.rig_module
                    )
                else:
                    self.make_dynamic_scapula(limb_joints, self.rig_module)

            if scapula_ctrl and fk.limb_controls:
                pm.parentConstraint(
                    scapula_ctrl.get_control(), fk.limb_controls[0].get_top(), mo=True
                )

    # --- Public accessors ---

    def get_main_limb_ik(self) -> pm.PyNode | None:
        """Return the main IK handle created for the limb."""
        return self.limb_ik

    def get_main_ik_control(self) -> control.Control | None:
        """Return the main IK control wrapper."""
        return self.main_ik_control

    def get_module_dict(self) -> dict[str, Any]:
        """Return rig module bookkeeping data.

        Keys use snake_case with camelCase aliases for backwards compatibility.
        """
        return {
            # snake_case (preferred)
            "module": self.rig_module,
            "rig_module": self.rig_module,
            "base_attach_grp": self.base_attach_group,
            "body_attach_grp": self.body_attach_group,
            # camelCase (backwards compat)
            "module_obj": self.rig_module,
            "baseAttachGrp": self.base_attach_group,
            "bodyAttachGrp": self.body_attach_group,
        }

    # --- Delegates to free functions ---

    def switch_ik_fk(
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
        """Wire IK/FK switch attributes and visibility toggles.

        Delegates to :func:`ikfk_switch.wire_ikfk_switch` to create the
        attribute network and visibility connections.
        """
        ikfk_switch.wire_ikfk_switch(
            prefix=prefix,
            part=part,
            visibility_ctrl=visibility_ctrl,
            fk_limb_controls=fk_limb_controls,
            fk_limb_constraints=fk_limb_constraints,
            fk_hand_controls=fk_hand_controls,
            fk_hand_constraints=fk_hand_constraints,
            main_ik_ctrl=main_ik_ctrl,
            ik_handle=ik_handle,
            finger_controls=finger_controls,
            finger_ik_handles=finger_ik_handles,
            ball_ik_handles=ball_ik_handles,
            pole_vector_ctrl=pole_vector_ctrl,
            hand_ik_orient_constraint=hand_ik_orient_constraint,
        )

    def make_simple_scapula(
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

    def make_clavicle(
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
    ) -> FKResult:
        """Build FK controls for the limb."""
        return build_fk_controls(limb_joints, top_finger_joints, rig_scale, rig_module)

    def make_pole_vector(
        self,
        ik_handle: pm.PyNode,
        auto_elbow_ctrl: pm.PyNode,
        rig_scale: float,
        rig_module: module.Module,
    ) -> tuple[control.Control, pm.PyNode]:
        """Create the pole vector control."""
        return build_pole_vector(
            ik_handle, auto_elbow_ctrl, rig_scale, rig_module, self.body_attach_group
        )

    def make_ik(
        self,
        limb_joints: Sequence[str],
        top_finger_joints: Sequence[str],
        rig_scale: float,
        rig_module: module.Module,
        *,
        use_metacarpal_joint: bool = False,
        smart_foot_roll: bool = True,
    ) -> IKResult:
        """Build IK controls for the limb."""
        return build_ik_controls(
            limb_joints,
            top_finger_joints,
            rig_scale,
            rig_module,
            use_metacarpal_joint=use_metacarpal_joint,
            do_smart_foot_roll=smart_foot_roll,
        )


class Arm(Limb):
    """Backwards-compatible wrapper around :class:`Limb` for arm rigs.

    Translates the explicit joint arguments (clavicle, shoulder, forearm,
    wrist) into the generic ``limb_joints`` sequence expected by
    :class:`Limb`.
    """

    def __init__(
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
        """Initialise the arm rig builder.

        Args:
            clavicle_joint: Name of the clavicle joint.
            shoulder_joint: Name of the shoulder joint.
            forearm_joint: Name of the forearm/elbow joint.
            wrist_joint: Name of the wrist joint.
            top_finger_joints: Root joints for each finger chain.
            scapula_joint: Optional scapula joint name.
            visibility_ik_fk_ctrl: Name of the IK/FK visibility switch control.
            do_fk: Whether to build FK controls.
            do_ik: Whether to build IK controls.
            prefix: Naming prefix (auto-derived if omitted).
            rig_scale: Global rig scale factor.
            base_rig: Base rig instance for module attachment.
            **legacy_kwargs: CamelCase aliases for backwards compatibility.
        """
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

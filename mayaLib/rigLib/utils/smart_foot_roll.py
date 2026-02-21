"""Smart foot roll utility node wiring for IK limb rigs.

Builds the node network (clamp, setRange, multiplyDivide, driven keys)
that drives heel roll, ball roll, tilt, lean, toe spin, and toe wiggle
from a single set of attributes on the main IK control.
"""

from __future__ import annotations

import pymel.core as pm

from mayaLib.rigLib.utils import attributes, common

__all__ = ["build"]


def build(
    prefix: str,
    side_prefix: str,
    ik_ctrl: pm.PyNode,
    ball_roll_grp: pm.PyNode,
    toe_tap_grp: pm.PyNode,
    tippy_toe_grp: pm.PyNode,
    back_roll_grp: pm.PyNode,
    inner_roll_grp: pm.PyNode,
    outer_roll_grp: pm.PyNode,
) -> None:
    """Wire smart foot roll attributes and utility nodes to the IK control.

    Args:
        prefix: Naming prefix for utility nodes.
        side_prefix: Side identifier (e.g. ``"l_"``) used to flip tilt direction.
        ik_ctrl: The main IK control transform node.
        ball_roll_grp: Group driven by ball roll angle.
        toe_tap_grp: Group driven by toe wiggle.
        tippy_toe_grp: Group driven by toe roll and spin.
        back_roll_grp: Group driven by heel roll.
        inner_roll_grp: Group driven by inner tilt.
        outer_roll_grp: Group driven by outer tilt.
    """
    roll_attr, bend_limit_attr, straight_angle_attr = _add_roll_attributes(prefix, ik_ctrl)

    _build_roll(
        prefix,
        roll_attr,
        bend_limit_attr,
        straight_angle_attr,
        ball_roll_grp,
        tippy_toe_grp,
        back_roll_grp,
    )
    _build_tilt(prefix, side_prefix, ik_ctrl, inner_roll_grp, outer_roll_grp)
    _build_extras(ik_ctrl, ball_roll_grp, tippy_toe_grp, toe_tap_grp)


def _add_roll_attributes(prefix: str, ik_ctrl: pm.PyNode) -> tuple:
    """Add roll, bendLimitAngle, and toeStraightAngle attributes.

    Args:
        prefix: Naming prefix (unused but kept for API consistency).
        ik_ctrl: The IK control to add attributes to.

    Returns:
        Tuple of (roll_attr, bend_limit_attr, straight_angle_attr).
    """
    roll_attr = attributes.add_float_attribute(
        ik_ctrl, "roll", defaultValue=0, keyable=True, minValue=-120, maxValue=120
    )
    bend_limit_attr = attributes.add_float_attribute(
        ik_ctrl, "bendLimitAngle", defaultValue=45, keyable=False
    )
    straight_angle_attr = attributes.add_float_attribute(
        ik_ctrl, "toeStraightAngle", defaultValue=70, keyable=False
    )
    return roll_attr, bend_limit_attr, straight_angle_attr


def _build_roll(
    prefix: str,
    roll_attr: pm.Attribute,
    bend_limit_attr: pm.Attribute,
    straight_angle_attr: pm.Attribute,
    ball_roll_grp: pm.PyNode,
    tippy_toe_grp: pm.PyNode,
    back_roll_grp: pm.PyNode,
) -> None:
    """Build heel-to-toe roll node network.

    Creates clamp and setRange nodes that split the roll angle into
    heel rotation (negative), ball rotation (0 to bend limit), and
    toe rotation (bend limit to straight angle).

    Args:
        prefix: Naming prefix for utility nodes.
        roll_attr: Roll attribute on the IK control.
        bend_limit_attr: Bend limit angle attribute.
        straight_angle_attr: Toe straight angle attribute.
        ball_roll_grp: Group driven by ball roll rotation.
        tippy_toe_grp: Group driven by toe roll rotation.
        back_roll_grp: Group driven by heel roll rotation.
    """
    # Heel: clamp negative roll to [-90, 0]
    heel_clamp = pm.shadingNode("clamp", asUtility=True, n=f"{prefix}_heelRotClamp")
    pm.connectAttr(roll_attr, heel_clamp.inputR)
    heel_clamp.minR.set(-90)
    pm.connectAttr(heel_clamp.outputR, back_roll_grp.rotateX)

    # Ball: clamp positive roll to [0, bendLimit]
    ball_clamp = pm.shadingNode("clamp", asUtility=True, n=f"{prefix}_zeroToBendClamp")
    pm.connectAttr(roll_attr, ball_clamp.inputR)

    # Toe: clamp roll to [bendLimit, straightAngle]
    bend_to_straight = pm.shadingNode(
        "clamp", asUtility=True, n=f"{prefix}_bendToStraightClamp"
    )
    pm.connectAttr(bend_limit_attr, bend_to_straight.minR)
    pm.connectAttr(straight_angle_attr, bend_to_straight.maxR)
    pm.connectAttr(roll_attr, bend_to_straight.inputR)

    # Convert toe range to 0-1 percentage
    bend_to_straight_range = pm.shadingNode(
        "setRange", asUtility=True, n=f"{prefix}_bendToStraightPercent"
    )
    pm.connectAttr(bend_to_straight.minR, bend_to_straight_range.oldMinX)
    pm.connectAttr(bend_to_straight.maxR, bend_to_straight_range.oldMaxX)
    bend_to_straight_range.maxX.set(1)
    pm.connectAttr(bend_to_straight.inputR, bend_to_straight_range.valueX)

    # Toe roll = percentage * roll angle
    roll_multiplier = pm.shadingNode(
        "multiplyDivide", asUtility=True, n=f"{prefix}_rollMultDiv"
    )
    pm.connectAttr(bend_to_straight_range.outValueX, roll_multiplier.input1X)
    pm.connectAttr(bend_to_straight.inputR, roll_multiplier.input2X)
    pm.connectAttr(roll_multiplier.outputX, tippy_toe_grp.rotateX)

    # Ball roll: (1 - toe%) * ball% * roll
    pm.connectAttr(bend_limit_attr, ball_clamp.maxR)
    zero_to_bend_range = pm.shadingNode(
        "setRange", asUtility=True, n=f"{prefix}_zeroToBendPercent"
    )
    pm.connectAttr(ball_clamp.minR, zero_to_bend_range.oldMinX)
    pm.connectAttr(ball_clamp.maxR, zero_to_bend_range.oldMaxX)
    zero_to_bend_range.maxX.set(1)
    pm.connectAttr(ball_clamp.inputR, zero_to_bend_range.valueX)

    invert_percent = pm.shadingNode(
        "plusMinusAverage", asUtility=True, n=f"{prefix}_invertPercent"
    )
    invert_percent.input1D[0].set(1)
    invert_percent.input1D[1].set(1)
    pm.connectAttr(bend_to_straight_range.outValueX, invert_percent.input1D[1])
    invert_percent.operation.set(2)

    ball_percent_multiplier = pm.shadingNode(
        "multiplyDivide", asUtility=True, n=f"{prefix}_ballPercentMultDiv"
    )
    pm.connectAttr(zero_to_bend_range.outValueX, ball_percent_multiplier.input1X)
    pm.connectAttr(invert_percent.output1D, ball_percent_multiplier.input2X)

    ball_roll_multiplier = pm.shadingNode(
        "multiplyDivide", asUtility=True, n=f"{prefix}_ballRollMultDiv"
    )
    pm.connectAttr(ball_percent_multiplier.outputX, ball_roll_multiplier.input1X)
    pm.connectAttr(roll_attr, ball_roll_multiplier.input2X)
    pm.connectAttr(ball_roll_multiplier.outputX, ball_roll_grp.rotateX)


def _build_tilt(
    prefix: str,
    side_prefix: str,
    ik_ctrl: pm.PyNode,
    inner_roll_grp: pm.PyNode,
    outer_roll_grp: pm.PyNode,
) -> None:
    """Build inner/outer tilt driven keys.

    Tilt direction flips based on whether the prefix contains the side identifier
    (left side tilts inward with positive Z, right side tilts inward with negative Z).

    Args:
        prefix: Naming prefix used to determine side.
        side_prefix: Side identifier (e.g. ``"l_"``).
        ik_ctrl: The IK control to add the tilt attribute to.
        inner_roll_grp: Group driven by inner tilt rotation.
        outer_roll_grp: Group driven by outer tilt rotation.
    """
    tilt_attr = attributes.add_float_attribute(
        ik_ctrl, "tilt", defaultValue=0, keyable=True, minValue=-90, maxValue=90
    )
    if side_prefix in prefix:
        common.set_driven_key(tilt_attr, [-90, 0, 90], inner_roll_grp.rotateZ, [90, 0, 0])
        common.set_driven_key(tilt_attr, [-90, 0, 90], outer_roll_grp.rotateZ, [0, 0, -90])
    else:
        common.set_driven_key(tilt_attr, [-90, 0, 90], inner_roll_grp.rotateZ, [-90, 0, 0])
        common.set_driven_key(tilt_attr, [-90, 0, 90], outer_roll_grp.rotateZ, [0, 0, 90])


def _build_extras(
    ik_ctrl: pm.PyNode,
    ball_roll_grp: pm.PyNode,
    tippy_toe_grp: pm.PyNode,
    toe_tap_grp: pm.PyNode,
) -> None:
    """Add lean, toe spin, and toe wiggle attributes with direct connections.

    Args:
        ik_ctrl: The IK control to add extra attributes to.
        ball_roll_grp: Group driven by lean rotation.
        tippy_toe_grp: Group driven by toe spin rotation.
        toe_tap_grp: Group driven by toe wiggle rotation.
    """
    lean_attr = attributes.add_float_attribute(
        ik_ctrl, "lean", defaultValue=0, keyable=True, minValue=-90, maxValue=90
    )
    pm.connectAttr(lean_attr, ball_roll_grp.rotateZ)

    toe_spin_attr = attributes.add_float_attribute(
        ik_ctrl, "toeSpin", defaultValue=0, keyable=True, minValue=-90, maxValue=90
    )
    pm.connectAttr(toe_spin_attr, tippy_toe_grp.rotateY)
    tippy_toe_grp.rotateOrder.set(2)

    toe_wiggle_attr = attributes.add_float_attribute(
        ik_ctrl, "toeWiggle", defaultValue=0, keyable=True, minValue=-90, maxValue=90
    )
    pm.connectAttr(toe_wiggle_attr, toe_tap_grp.rotateX)

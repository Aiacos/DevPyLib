"""Build the Maya node network that makes a joint chain trail behind a lead transform.

The delay comes from 'springChainSolver' nodes (plugin 'mayaLib/plugin/spring_chain_solver.py'): a chain
of springs with internal state, one for the joints positions and one for the points that drive the
twist. This module wires the solvers and turns their points into joints that keep their bone length:
each joint sits on a pivot, aims at the solved position of the next joint, and the next pivot is one
bone length further.

Only 'maya.cmds' and transform names are used, so it runs in mayapy without Arise.
"""

from collections.abc import Sequence

import maya.cmds as mc
from maya.api import OpenMaya

AXES = "XYZ"
SOLVER_NODE = "springChainSolver"
RIGID_JOINTS = 2  # joint 0 is rigid to the lead, so joint 1 sits one rigid bone away from it.


def _node(node_type, name, **kwargs):
    """Create a utility node and set the attribute values passed as kwargs."""
    node = mc.createNode(node_type, name=name)
    for attr, value in kwargs.items():
        if isinstance(value, Sequence):
            mc.setAttr(f"{node}.{attr}", *value, type="double3")
        else:
            mc.setAttr(f"{node}.{attr}", value)

    return node


def _connect_point(point, node, attr, suffixes=AXES):
    """Connect a point (list of 3 scalar attributes) to the 3 children of 'node.attr'."""
    for index, suffix in enumerate(suffixes):
        mc.connectAttr(point[index], f"{node}.{attr}{suffix}")


def _outputs(node, attr, suffixes=AXES):
    """Return the 3 children of 'node.attr' as a point (list of 3 scalar attributes)."""
    return [f"{node}.{attr}{suffix}" for suffix in suffixes]


def _world_matrix(node):
    """Return the current world matrix of 'node' as an MMatrix."""
    return OpenMaya.MMatrix(mc.xform(node, query=True, worldSpace=True, matrix=True))


def _world_position(prefix, transform):
    """Return the live world position of 'transform' as a point."""
    decompose = _node("decomposeMatrix", f"{prefix}_world_decomposeMatrix")
    mc.connectAttr(f"{transform}.worldMatrix[0]", f"{decompose}.inputMatrix")
    return _outputs(decompose, "outputTranslate")


def _solve_points(name, points, lag_attr, damping_attr, weight_attr, space):
    """Create a 'springChainSolver' fed by 'points' and return its solved points.

    Args:
        name (str): name of the solver node.
        points (list): of points, the rigid chain world positions.
        lag_attr (str): attribute, frames of delay each point adds.
        damping_attr (str): attribute, damping ratio (1 = no overshoot).
        weight_attr (str): attribute, 0 (rigid) to 1 (solved).
        space (str or None): transform whose motion is not delayed. None is world.

    Returns:
        list: of points (3 scalar attributes each), one per input point.
    """
    solver = _node(SOLVER_NODE, name, rigidCount=RIGID_JOINTS)
    mc.connectAttr("time1.outTime", f"{solver}.time")
    mc.connectAttr(lag_attr, f"{solver}.lag")
    mc.connectAttr(damping_attr, f"{solver}.damping")
    mc.connectAttr(weight_attr, f"{solver}.weight")
    if space:
        mc.connectAttr(f"{space}.worldMatrix[0]", f"{solver}.spaceMatrix")

    solved = []
    for index, point in enumerate(points):
        _connect_point(point, solver, f"inPoint[{index}].inPoint", "012")
        solved.append(_outputs(solver, f"outPoint[{index}].outPoint", "012"))

    return solved


def _combine(name, operation, point_a, point_b):
    """Return 'point_a' + 'point_b' (operation 1) or 'point_a' - 'point_b' (operation 2)."""
    node = _node("plusMinusAverage", name, operation=operation)
    _connect_point(point_a, node, "input3D[0].input3D", "xyz")
    _connect_point(point_b, node, "input3D[1].input3D", "xyz")
    return _outputs(node, "output3D", "xyz")


def _drive_joint(prefix, joint, world_matrix_attr):
    """Drive the local transformation of 'joint' so its world matrix is 'world_matrix_attr'."""
    mc.setAttr(f"{joint}.jointOrient", 0, 0, 0, type="double3")
    mc.setAttr(f"{joint}.segmentScaleCompensate", 0)

    local = _node("multMatrix", f"{prefix}_local_multMatrix")
    mc.connectAttr(world_matrix_attr, f"{local}.matrixIn[0]")
    mc.connectAttr(f"{joint}.parentInverseMatrix[0]", f"{local}.matrixIn[1]")
    decompose = _node(
        "decomposeMatrix",
        f"{prefix}_local_decomposeMatrix",
        inputRotateOrder=mc.getAttr(f"{joint}.rotateOrder"),
    )
    mc.connectAttr(f"{local}.matrixSum", f"{decompose}.inputMatrix")
    for attr in ("translate", "rotate", "scale"):
        mc.connectAttr(f"{decompose}.output{attr.title()}", f"{joint}.{attr}", force=True)


def build_spring_chain(
    prefix,
    rest_points,
    up_points,
    joints,
    lead,
    lag_attr,
    damping_attr,
    weight_attr,
    space=None,
):
    """Drive 'joints' so they trail behind 'lead' with a cascading spring, keeping the bones length.

    The 'springChainSolver' plugin must be loaded. Joints 0 and 1 are rigid to the lead.

    Args:
        prefix (str): name prefix of every created node.
        rest_points (list): one transform per joint, under 'lead', holding the joint rest world matrix.
        up_points (list or None): one transform per joint, offset sideways from its rest point. Their
            solved positions drive the twist. None makes the twist follow the previous joint.
        joints (list): joints in a parent-child hierarchy. 'jointOrient' and
            'segmentScaleCompensate' get zeroed.
        lead (str): transform the chain follows. Its world scale becomes the joints scale.
        lag_attr (str): 'node.attribute', frames of delay each joint adds.
        damping_attr (str): 'node.attribute', damping ratio (1 = no overshoot).
        weight_attr (str): 'node.attribute' from 0 (rigid chain) to 1 (spring chain).
        space (str or None): transform whose motion is not delayed. None is world.

    Raises:
        ValueError: when there are fewer than 3 joints or the lists lengths do not match.
    """
    count = len(joints)
    if count < 3:
        raise ValueError("Spring chain needs at least 3 joints.")

    if len(rest_points) != count:
        raise ValueError("Spring chain needs one rest point per joint.")

    if up_points is not None and len(up_points) != count:
        raise ValueError("Spring chain needs one up point per joint.")

    rest_matrices = [_world_matrix(point) for point in rest_points]
    rigid = [
        _world_position(f"{prefix}_{index}_rest", point) for index, point in enumerate(rest_points)
    ]
    targets = _solve_points(
        f"{prefix}_position_{SOLVER_NODE}", rigid, lag_attr, damping_attr, weight_attr, space
    )
    up_targets = None
    if up_points is not None:
        up_rigid = [
            _world_position(f"{prefix}_{index}_up", point) for index, point in enumerate(up_points)
        ]
        up_targets = _solve_points(
            f"{prefix}_twist_{SOLVER_NODE}", up_rigid, lag_attr, damping_attr, weight_attr, space
        )

    lead_decompose = _node("decomposeMatrix", f"{prefix}_lead_decomposeMatrix")
    mc.connectAttr(f"{lead}.worldMatrix[0]", f"{lead_decompose}.inputMatrix")

    _drive_joint(f"{prefix}_0", joints[0], f"{rest_points[0]}.worldMatrix[0]")

    pivot = rigid[1]
    previous_matrix = f"{rest_points[0]}.worldMatrix[0]"
    for index in range(1, count - 1):
        bone = f"{prefix}_{index}"
        rest_inverse = rest_matrices[index].inverse()
        next_position = OpenMaya.MPoint(*mc.xform(rest_points[index + 1], q=True, ws=True, t=True))
        primary_axis = OpenMaya.MVector(next_position * rest_inverse).normal()

        driver = _node("composeMatrix", f"{bone}_driver_composeMatrix", useEulerRotation=0)
        mc.connectAttr(f"{lead_decompose}.outputQuat", f"{driver}.inputQuat")
        mc.connectAttr(f"{lead_decompose}.outputScale", f"{driver}.inputScale")
        _connect_point(pivot, driver, "inputTranslate")

        aim = _node(
            "aimMatrix",
            f"{bone}_aimMatrix",
            primaryMode=1,
            primaryInputAxis=(primary_axis.x, primary_axis.y, primary_axis.z),
        )
        mc.connectAttr(f"{driver}.outputMatrix", f"{aim}.inputMatrix")
        _connect_point(targets[index + 1], aim, "primaryTargetVector")

        if up_targets is not None:
            # twist: aim the side axis at the solved up point, moved from the target to the pivot.
            up_position = OpenMaya.MPoint(*mc.xform(up_points[index], q=True, ws=True, t=True))
            secondary_axis = OpenMaya.MVector(up_position * rest_inverse).normal()
            offset = _combine(
                f"{bone}_up_offset_plusMinusAverage", 2, up_targets[index], targets[index]
            )
            up_goal = _combine(f"{bone}_up_goal_plusMinusAverage", 1, pivot, offset)
            mc.setAttr(f"{aim}.secondaryMode", 1)
            _connect_point(up_goal, aim, "secondaryTargetVector")
        else:
            # twist: keep the side axis aligned with the solved matrix of the previous joint.
            helper = (
                OpenMaya.MVector(1, 0, 0)
                if abs(primary_axis.x) < 0.9
                else OpenMaya.MVector(0, 1, 0)
            )
            secondary_axis = ((primary_axis ^ helper) ^ primary_axis).normal()
            # the previous solved matrix, moved by the live offset between the two rest points: the
            # rotation of an FK ctrl above this joint is kept, on top of the solved chain.
            relative = _node("multMatrix", f"{bone}_twist_multMatrix")
            mc.connectAttr(f"{rest_points[index]}.worldMatrix[0]", f"{relative}.matrixIn[0]")
            mc.connectAttr(
                f"{rest_points[index - 1]}.worldInverseMatrix[0]", f"{relative}.matrixIn[1]"
            )
            mc.connectAttr(previous_matrix, f"{relative}.matrixIn[2]")
            mc.setAttr(f"{aim}.secondaryMode", 2)
            mc.setAttr(
                f"{aim}.secondaryTargetVector",
                secondary_axis.x,
                secondary_axis.y,
                secondary_axis.z,
                type="double3",
            )
            mc.connectAttr(f"{relative}.matrixSum", f"{aim}.secondaryTargetMatrix")

        mc.setAttr(
            f"{aim}.secondaryInputAxis",
            secondary_axis.x,
            secondary_axis.y,
            secondary_axis.z,
            type="double3",
        )
        previous_matrix = f"{aim}.outputMatrix"
        _drive_joint(bone, joints[index], previous_matrix)

        # the next pivot is one bone length away, towards the solved target.
        length = _node("distanceBetween", f"{bone}_length_distanceBetween")
        mc.connectAttr(f"{rest_points[index]}.worldMatrix[0]", length + ".inMatrix1")
        mc.connectAttr(f"{rest_points[index + 1]}.worldMatrix[0]", length + ".inMatrix2")

        to_target = _combine(f"{bone}_aim_plusMinusAverage", 2, targets[index + 1], pivot)
        direction = _node(
            "vectorProduct", f"{bone}_direction_vectorProduct", operation=0, normalizeOutput=1
        )
        _connect_point(to_target, direction, "input1")
        step = _node("multiplyDivide", f"{bone}_step_multiplyDivide")
        _connect_point(_outputs(direction, "output"), step, "input1")
        for axis in AXES:
            mc.connectAttr(f"{length}.distance", f"{step}.input2{axis}")

        pivot = _combine(f"{bone}_pivot_plusMinusAverage", 1, pivot, _outputs(step, "output"))

    # the tip has no target to aim at: it keeps the live offset of its rest point from the one
    # before it (so an FK ctrl on the tip still rotates it).
    tip = f"{prefix}_{count - 1}"
    tip_matrix = _node("multMatrix", f"{tip}_tip_multMatrix")
    mc.connectAttr(f"{rest_points[-1]}.worldMatrix[0]", f"{tip_matrix}.matrixIn[0]")
    mc.connectAttr(f"{rest_points[-2]}.worldInverseMatrix[0]", f"{tip_matrix}.matrixIn[1]")
    mc.connectAttr(previous_matrix, f"{tip_matrix}.matrixIn[2]")
    _drive_joint(tip, joints[-1], f"{tip_matrix}.matrixSum")

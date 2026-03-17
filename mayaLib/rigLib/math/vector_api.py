"""Vector math utilities using Maya API (OpenMaya 2.0).

Provides pure-math vector operations and rigging helpers (pole vector solver)
built on top of ``maya.api.OpenMaya.MVector``.
"""

import math

import maya.api.OpenMaya as om2
import maya.cmds as cmds


def add(v1, v2):
    """Add two vectors.

    Args:
        v1: First vector.
        v2: Second vector.

    Returns:
        The sum of the two vectors.
    """
    return v1 + v2


def subtract(v1, v2):
    """Subtract two vectors.

    Args:
        v1: First vector (minuend).
        v2: Second vector (subtrahend).

    Returns:
        The difference v1 - v2.
    """
    return v1 - v2


def multiply(v1, v2):
    """Multiply two vectors component-wise.

    Args:
        v1: First vector (MVector).
        v2: Second vector (MVector).

    Returns:
        MVector: The component-wise product.
    """
    return om2.MVector(v1.x * v2.x, v1.y * v2.y, v1.z * v2.z)


def midpoint(v1, v2, scale=0.5):
    """Compute a weighted midpoint between two vectors.

    Formula: result = v1 + (v2 - v1) * scale.
    When scale=0.5 (default), produces the exact midpoint.

    Args:
        v1: First vector (start point).
        v2: Second vector (end point).
        scale (float): Blend factor between v1 and v2. 0.0 = v1, 1.0 = v2.

    Returns:
        MVector: The interpolated position.
    """
    return v1 + (v2 - v1) * scale


def length(v1):
    """Compute the length (magnitude) of a vector.

    Args:
        v1: The input vector.

    Returns:
        float: The length of the vector.
    """
    return v1.length()


def normalize(v1):
    """Return the unit-length direction of a vector.

    Args:
        v1: The input vector.

    Returns:
        MVector: The normalized vector (length = 1).
    """
    return v1.normal()


def dot_product(v1, v2):
    """Compute the dot product of two vectors.

    Args:
        v1: First vector.
        v2: Second vector.

    Returns:
        float: The scalar dot product.
    """
    return v1 * v2


def cross_product(v1, v2):
    """Compute the cross product of two vectors.

    Args:
        v1: First vector.
        v2: Second vector.

    Returns:
        MVector: The cross product vector perpendicular to both inputs.
    """
    return v1 ^ v2


def get_angle_between(v1, v2):
    """Compute the angle between two vectors in degrees.

    Args:
        v1: First vector.
        v2: Second vector.

    Returns:
        float: The angle in degrees.
    """
    return math.degrees(v1.angle(v2))


def rotate(v1, angle_degrees, axis=None):
    """Rotate a vector around an axis by the given angle.

    Supports two modes:
    - **Euler**: pass *axis* as an MVector of (rx, ry, rz) in degrees.
    - **Single axis**: pass *axis* as one of ``MVector.kXaxis``,
      ``MVector.kYaxis``, ``MVector.kZaxis`` (default: kYaxis).

    Args:
        v1: The input vector.
        angle_degrees (float): Rotation angle in degrees.
        axis: Rotation axis — either an ``MVector`` of Euler angles
            (degrees) or an axis constant. Defaults to ``MVector.kYaxis``.

    Returns:
        MVector: The rotated vector.
    """
    if isinstance(axis, om2.MVector):
        euler = om2.MEulerRotation(
            math.radians(axis.x), math.radians(axis.y), math.radians(axis.z)
        )
        return v1.rotateBy(euler)

    if axis is None:
        axis = om2.MVector.kYaxisNeg  # sensible default
    return v1.rotateBy(axis, math.radians(angle_degrees))


def get_pole_vector_position(
    start_joint,
    mid_joint,
    end_joint,
    method="bulletproof",
    distance_scale=0.5,
):
    """Compute the pole vector position for a three-joint IK chain.

    Args:
        start_joint (str): Name of the root joint (e.g. shoulder).
        mid_joint (str): Name of the middle joint (e.g. elbow).
        end_joint (str): Name of the end joint (e.g. wrist).
        method (str): Solver algorithm — one of:
            - ``"midpoint"``: Simple midpoint projection (fastest).
            - ``"projection"``: Perpendicular projection onto chain line.
            - ``"studio"``: Chain-length based stable distance.
            - ``"bulletproof"`` (default): Studio + cross-product fallback
              for straight chains.
        distance_scale (float): Multiplier for pole vector distance.
            Default 0.5 gives half the total chain length.

    Returns:
        tuple[float, float, float]: World-space (x, y, z) position for the
        pole vector control.

    Raises:
        ValueError: If *method* is not one of the recognised names.
    """
    arm_pos = om2.MVector(cmds.xform(start_joint, q=True, ws=True, t=True))
    elbow_pos = om2.MVector(cmds.xform(mid_joint, q=True, ws=True, t=True))
    wrist_pos = om2.MVector(cmds.xform(end_joint, q=True, ws=True, t=True))

    if method == "midpoint":
        pv = _pv_midpoint(arm_pos, elbow_pos, wrist_pos)
    elif method == "projection":
        pv = _pv_projection(arm_pos, elbow_pos, wrist_pos)
    elif method == "studio":
        pv = _pv_studio(arm_pos, elbow_pos, wrist_pos, distance_scale)
    elif method == "bulletproof":
        pv = _pv_bulletproof(arm_pos, elbow_pos, wrist_pos, distance_scale)
    else:
        raise ValueError(
            f"Unknown method {method!r}. "
            "Choose from: midpoint, projection, studio, bulletproof."
        )

    return pv.x, pv.y, pv.z


# ── private solvers ──────────────────────────────────────────────


def _pv_midpoint(arm, elbow, wrist):
    """Simple midpoint projection.

    PV = midpoint(arm, wrist) + (elbow - midpoint) * 2.
    """
    mid = arm + (wrist - arm) * 0.5
    return mid + (elbow - mid) * 2


def _pv_projection(arm, elbow, wrist):
    """Perpendicular projection onto the chain line.

    Projects elbow onto arm→wrist, then extends outward by chain length.
    """
    ac = wrist - arm
    ac_dir = ac.normal()
    ab = elbow - arm
    closest = arm + ac_dir * (ab * ac_dir)
    pole_dir = (elbow - closest).normal()
    return elbow + pole_dir * ac.length()


def _pv_studio(arm, elbow, wrist, scale=0.5):
    """Chain-length based stable distance.

    Uses (|AB| + |BC|) * scale as distance — stays stable under stretch.
    """
    ab = elbow - arm
    ac = wrist - arm
    bc = wrist - elbow
    ac_dir = ac.normal()
    closest = arm + ac_dir * (ab * ac_dir)
    perp_dir = (elbow - closest).normal()
    dist = (ab.length() + bc.length()) * scale
    return elbow + perp_dir * dist


def _pv_bulletproof(arm, elbow, wrist, scale=0.5):
    """Studio solver + cross-product fallback for straight chains.

    When the perpendicular vector is near-zero (chain is almost straight),
    falls back to the cross product of AB and AC for a stable direction.
    """
    ab = elbow - arm
    ac = wrist - arm
    bc = wrist - elbow
    ac_dir = ac.normal()
    closest = arm + ac_dir * (ab * ac_dir)
    perp = elbow - closest

    direction = (ab ^ ac).normal() if perp.length() < 0.001 else perp.normal()

    dist = (ab.length() + bc.length()) * scale
    return elbow + direction * dist


# ── push vector ──────────────────────────────────────────────────


def get_mesh_fn(mesh_name):
    """Return an MFnMesh function set for the given mesh.

    Args:
        mesh_name (str): Name of a polygon mesh transform or shape node.

    Returns:
        om2.MFnMesh: Function set bound to *mesh_name*.
    """
    sel = om2.MSelectionList()
    sel.add(mesh_name)
    return om2.MFnMesh(sel.getDagPath(0))


def get_closest_normal(mesh_fn, position):
    """Return the world-space surface normal closest to *position*.

    Args:
        mesh_fn (om2.MFnMesh): Function set for the target mesh.
        position: World-space query point (MVector, MPoint, or 3-float sequence).

    Returns:
        om2.MVector: Unit normal at the closest surface point.
    """
    normal = mesh_fn.getClosestNormal(
        om2.MPoint(position), space=om2.MSpace.kWorld
    )[0]
    return normal.normal()


def push_vector(mesh_fn, position, magnitude=1.5):
    """Compute an outward offset vector along the closest surface normal.

    Args:
        mesh_fn (om2.MFnMesh): Function set for the reference mesh.
        position: World-space point from which to query the normal
            (MVector, MPoint, or 3-float sequence).
        magnitude (float): Length of the resulting push vector. Defaults to 1.5.

    Returns:
        om2.MVector: Offset vector pointing away from the mesh surface.
    """
    return get_closest_normal(mesh_fn, position) * magnitude


def push_joints_along_mesh(
    mesh_name,
    joints=None,
    magnitude=1.5,
    push_frames=3,
    return_frames=6,
    start_time=None,
):
    """Animate joints outward along the closest mesh normal and back.

    For each joint the function:

    1. Keys the current position at *start_time*.
    2. Moves the joint by the push vector and keys at *start_time + push_frames*.
    3. Returns the joint to its original position and keys at
       *start_time + return_frames*.

    Args:
        mesh_name (str): Polygon mesh used as the normal reference surface.
        joints (list[str] | None): Joint names to process. When ``None``,
            all joints in the scene are used.
        magnitude (float): Push distance along the surface normal.
            Defaults to 1.5.
        push_frames (int): Frame offset for the pushed keyframe.
            Defaults to 3.
        return_frames (int): Frame offset for the return keyframe.
            Defaults to 6.
        start_time (float | None): Timeline frame to begin the animation.
            When ``None``, the current time is used.
    """
    mesh_fn = get_mesh_fn(mesh_name)

    if joints is None:
        joints = cmds.ls(type="joint") or []

    if start_time is not None:
        cmds.currentTime(start_time, edit=True)

    for joint in joints:
        joint_pos = om2.MVector(cmds.xform(joint, q=True, rp=True, ws=True))
        cmds.setKeyframe(joint, at="translate")

        current_time = cmds.currentTime(q=True)

        # Push outward
        cmds.currentTime(current_time + push_frames, edit=True)
        vec = push_vector(mesh_fn, joint_pos, magnitude)
        cmds.xform(joint, r=True, t=(vec.x, vec.y, vec.z))
        cmds.setKeyframe(joint, at="translate")

        # Return to original position
        cmds.currentTime(current_time + return_frames, edit=True)
        cmds.xform(joint, ws=True, t=(joint_pos.x, joint_pos.y, joint_pos.z))
        cmds.setKeyframe(joint, at="translate")

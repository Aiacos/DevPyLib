import math

import maya.api.OpenMaya as om2
import maya.cmds as cmds

tmp = om2.MVector()


def add(v1, v2):
    """

    Args:
        v1:
        v2:
        output:
        name:

    Returns:

    """

    return v1 + v2


def subtract(v1, v2):
    """

    Args:
        v1:
        v2:
        output:
        name:

    Returns:

    """

    return v1 - v2


def multiply(v1, v2):
    """

    Args:
        v1:
        v2:
        output:
        name:

    Returns:

    """
    pass


def midpoint(v1, v2, output, scale=0.5):
    """Compute a weighted midpoint between two transforms using Maya nodes.

    Builds a node network: result = v1 + (v2 - v1) * scale.
    When scale=0.5 (default), produces the exact midpoint.

    Args:
        v1: First transform node (start point).
        v2: Second transform node (end point).
        output: Transform node to receive the resulting translation.
        scale (float): Blend factor between v1 and v2. 0.0 = v1, 1.0 = v2.
    """

    delta = v2 - v1
    envelope = delta * scale
    final = v1 + envelope

    return final


def lenght(v1):
    """
    Compute the length of a vector using Maya nodes.

    Args:
        v1:
        output:
        name:

    Returns:

    """

    return v1.lenght()


def normalize(v1):
    """
    Normalize a vector using Maya nodes.

    Args:
        v1:
        output:
        name:

    Returns:

    """

    pass


def dot_product(v1, v2):
    """
    Compute the dot product of two vectors using Maya nodes.

    Args:
        v1:
        v2:
        output:
        name:

    Returns:

    """

    return v1 * v2


def cross_product(v1, v2):
    """
    Compute the cross product of two vectors using Maya nodes.

    Args:
        v1:
        v2:
        output:
        name:

    Returns:

    """

    return v1 ^ v2


def get_angle_between(v1, v2):
    """

    Args:
        v1:
        v2:

    Returns:

    """
    return math.degrees(v1.angle(v2))


def rotate(v1, angle_degree):
    # ToDo: Cleanup and add condition to manage bot method based on input provided
    # rotate vector
    radians = om2.MVector(math.radians(90), 0, 0)  # degrees to radians
    rotateBy_vec_a = v1.rotateBy(om2.MEulerRotation(radians))
    rotateBy_vec_b = v1.rotateBy(om2.MVector.kYAxis, math.radians(90))

    print(rotateBy_vec_a)
    print(rotateBy_vec_b)


def get_pole_vector_position():
    # ToDo: usar euno switch per selezionare la soluzione da usare (default l'ultima la piu robusta)
    # Get world space positions of the three joints
    arm_pos = om2.MVector(cmds.xform("arm", q=True, rp=True, ws=True))
    elbow_pos = om2.MVector(cmds.xform("elbow", q=True, rp=True, ws=True))
    wrist_pos = om2.MVector(cmds.xform("wrist", q=True, rp=True, ws=True))

    # ------------------------------------------------------------
    # GEOMETRIC FORMULA FOR POLE VECTOR POSITION
    #
    # A = arm
    # B = elbow
    # C = wrist
    #
    # 1) Compute the midpoint of segment AC
    #    M = A + (C - A) / 2
    #
    # 2) Compute the vector from midpoint to elbow
    #    V = B - M
    #
    # 3) Extend this vector outward
    #    PV = M + V * k   (k = scale factor, here = 2)
    #
    # This projects the pole vector outward from the arm plane,
    # ensuring a stable IK pole direction.
    # ------------------------------------------------------------

    # Vector from arm to wrist
    arm_to_wrist = wrist_pos - arm_pos

    # Half of the vector length
    arm_to_wrist_scaled = arm_to_wrist / 2

    # Midpoint between arm and wrist
    mid_point = arm_pos + arm_to_wrist_scaled

    # Vector from midpoint to elbow
    mid_point_to_elbow_vec = elbow_pos - mid_point

    # Scale the vector (push it away from the chain)
    mid_point_to_elbow_vec_scaled = mid_point_to_elbow_vec * 2

    # Final pole vector position
    mid_point_to_elbow_point = mid_point + mid_point_to_elbow_vec_scaled

    # Move the pole vector control
    cmds.xform("PV", t=mid_point_to_elbow_point)

    ### Robust Version

    # Get world space positions
    arm_pos = om2.MVector(cmds.xform("arm", q=True, ws=True, t=True))
    elbow_pos = om2.MVector(cmds.xform("elbow", q=True, ws=True, t=True))
    wrist_pos = om2.MVector(cmds.xform("wrist", q=True, ws=True, t=True))

    # ------------------------------------------------------------
    # ROBUST POLE VECTOR FORMULA (VECTOR PROJECTION METHOD)
    #
    # A = arm
    # B = elbow
    # C = wrist
    #
    # 1) Define the arm direction
    #    AC = C - A
    #
    # 2) Project AB onto AC
    #    projection = dot(AB, AC_normalized)
    #
    # 3) Compute the closest point on the arm line
    #    P = A + AC_normalized * projection
    #
    # 4) Compute perpendicular direction toward the elbow
    #    V = B - P
    #
    # 5) Place the pole vector along that direction
    #    PV = B + normalize(V) * distance
    #
    # This guarantees the PV lies perpendicular to the arm chain.
    # ------------------------------------------------------------

    # Direction from arm to wrist
    arm_to_wrist = wrist_pos - arm_pos
    arm_to_wrist_dir = arm_to_wrist.normal()

    # Vector from arm to elbow
    arm_to_elbow = elbow_pos - arm_pos

    # Projection length of arm->elbow onto arm->wrist
    projection_len = arm_to_elbow * arm_to_wrist_dir

    # Closest point on the arm-wrist line
    closest_point = arm_pos + arm_to_wrist_dir * projection_len

    # Perpendicular direction toward the elbow
    pole_direction = (elbow_pos - closest_point).normal()

    # Distance for pole vector placement
    distance = arm_to_wrist.length()

    # Final pole vector position
    pole_position = elbow_pos + pole_direction * distance

    # Move the pole vector control
    cmds.xform("PV", ws=True, t=(pole_position.x, pole_position.y, pole_position.z))

    ### Professional implementation

    # Get world space joint positions
    arm_pos = om2.MVector(cmds.xform("arm", q=True, ws=True, t=True))
    elbow_pos = om2.MVector(cmds.xform("elbow", q=True, ws=True, t=True))
    wrist_pos = om2.MVector(cmds.xform("wrist", q=True, ws=True, t=True))

    # ------------------------------------------------------------
    # STUDIO-GRADE POLE VECTOR FORMULA
    #
    # A = arm
    # B = elbow
    # C = wrist
    #
    # 1) Define chain vectors
    #    AB = B - A
    #    AC = C - A
    #
    # 2) Project AB onto AC
    #    proj = dot(AB, normalize(AC))
    #
    # 3) Find closest point on AC
    #    P = A + normalize(AC) * proj
    #
    # 4) Compute perpendicular vector
    #    perp = B - P
    #
    # 5) Normalize perpendicular direction
    #    dir = normalize(perp)
    #
    # 6) Use a stable distance based on chain length
    #    dist = (|AB| + |BC|) * scale
    #
    # 7) Compute PV position
    #    PV = B + dir * dist
    #
    # This keeps the PV stable even if the arm stretches
    # and avoids degeneracy when the arm is almost straight.
    # ------------------------------------------------------------

    # Chain vectors
    AB = elbow_pos - arm_pos
    AC = wrist_pos - arm_pos
    BC = wrist_pos - elbow_pos

    AC_dir = AC.normal()

    # Projection
    proj = AB * AC_dir

    # Closest point on AC line
    P = arm_pos + AC_dir * proj

    # Perpendicular direction
    perp = elbow_pos - P
    dir_vec = perp.normal()

    # Stable pole vector distance
    dist = (AB.length() + BC.length()) * 0.5

    # Final pole vector position
    pv_pos = elbow_pos + dir_vec * dist

    # Move pole vector controller
    cmds.xform("PV", ws=True, t=(pv_pos.x, pv_pos.y, pv_pos.z))

    ### Best

    # Get world space joint positions
    arm_pos = om2.MVector(cmds.xform("arm", q=True, ws=True, t=True))
    elbow_pos = om2.MVector(cmds.xform("elbow", q=True, ws=True, t=True))
    wrist_pos = om2.MVector(cmds.xform("wrist", q=True, ws=True, t=True))

    # ------------------------------------------------------------
    # BULLETPROOF POLE VECTOR SOLVER
    #
    # A = arm
    # B = elbow
    # C = wrist
    #
    # Steps
    #
    # 1) Compute chain vectors
    #    AB = B - A
    #    AC = C - A
    #
    # 2) Project AB onto AC
    #    proj = dot(AB, normalize(AC))
    #
    # 3) Closest point on AC
    #    P = A + normalize(AC) * proj
    #
    # 4) Perpendicular vector
    #    perp = B - P
    #
    # 5) If perp is too small (chain is straight),
    #    compute fallback using cross product
    #
    #    fallback = normalize(cross(AB, AC))
    #
    # 6) Compute stable distance
    #
    #    dist = (|AB| + |BC|) * scale
    #
    # 7) Final PV position
    #
    #    PV = B + direction * dist
    #
    # ------------------------------------------------------------

    # Chain vectors
    AB = elbow_pos - arm_pos
    AC = wrist_pos - arm_pos
    BC = wrist_pos - elbow_pos

    AC_dir = AC.normal()

    # Projection of AB onto AC
    proj = AB * AC_dir

    # Closest point on arm-wrist line
    P = arm_pos + AC_dir * proj

    # Perpendicular vector toward elbow
    perp = elbow_pos - P

    # If the arm is almost straight, fallback to cross product
    if perp.length() < 0.001:
        direction = (AB ^ AC).normal()  # cross product
    else:
        direction = perp.normal()

    # Stable pole vector distance
    dist = (AB.length() + BC.length()) * 0.5

    # Final PV position
    pv_pos = elbow_pos + direction * dist

    # Move pole vector control
    cmds.xform("PV", ws=True, t=(pv_pos.x, pv_pos.y, pv_pos.z))

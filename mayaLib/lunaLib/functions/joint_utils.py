"""Joint utility wrappers for Luna.

Provides wrapper functions around Luna's joint manipulation utilities.
"""

import pymel.core as pm


def duplicate_chain(
    start_joint: str = "",
    end_joint: str = "",
    new_name: str = "dup",
    new_side: str = "c",
    new_suffix: str = "jnt",
    new_parent: str = "",
):
    """Duplicate a joint chain with new naming.

    Creates a copy of the joint chain between start and end joints,
    renaming them with the specified naming parameters.

    Args:
        start_joint: Name or path of the first joint in chain.
        end_joint: Name or path of the last joint in chain.
        new_name: New base name for duplicated joints. Defaults to "dup".
        new_side: Side prefix for new joints (c, l, r). Defaults to "c".
        new_suffix: Suffix for new joints. Defaults to "jnt".
        new_parent: Parent transform for new chain. Use "world" for world parent.

    Returns:
        list: List of duplicated joint PyNodes.

    Example:
        >>> new_chain = duplicate_chain(
        ...     start_joint="arm_01_jnt",
        ...     end_joint="arm_03_jnt",
        ...     new_name="fk",
        ...     new_side="l"
        ... )

    """
    import luna_rig.functions.jointFn as jointFn

    # Convert strings to PyNodes
    start_jnt = pm.PyNode(start_joint) if start_joint else None
    end_jnt = pm.PyNode(end_joint) if end_joint else None
    parent = pm.PyNode(new_parent) if new_parent and new_parent != "world" else new_parent

    return jointFn.duplicate_chain(
        new_joint_name=new_name,
        new_joint_side=new_side,
        new_joint_suffix=new_suffix,
        start_joint=start_jnt,
        end_joint=end_jnt,
        new_parent=parent if parent else None,
    )


def joint_chain(start_joint: str = "", end_joint: str = ""):
    """Get joint chain from start to end joint.

    Returns all joints in the hierarchy between start and end joints.

    Args:
        start_joint: Name or path of the first joint in chain.
        end_joint: Name or path of the last joint in chain. Optional.

    Returns:
        list: List of joint PyNodes in chain order.

    Example:
        >>> chain = joint_chain("spine_01_jnt", "spine_05_jnt")
        >>> print(len(chain))
        5

    """
    import luna_rig.functions.jointFn as jointFn

    start_jnt = pm.PyNode(start_joint) if start_joint else None
    end_jnt = pm.PyNode(end_joint) if end_joint else None

    return jointFn.joint_chain(start_jnt, end_jnt)


def get_pole_vector(start_joint: str = "", end_joint: str = ""):
    """Calculate and create pole vector locator for joint chain.

    Creates a locator positioned at the ideal pole vector location
    for the given joint chain, useful for IK setup.

    Args:
        start_joint: Name or path of the first joint in chain.
        end_joint: Name or path of the last joint in chain.

    Returns:
        PyNode: Locator at calculated pole vector position.

    Example:
        >>> pv_loc = get_pole_vector("l_arm_01_jnt", "l_arm_03_jnt")

    """
    import luna_rig.functions.jointFn as jointFn

    chain = joint_chain(start_joint, end_joint)
    return jointFn.get_pole_vector(chain)


def create_chain(joints: str = "", reverse: bool = False):
    """Parent joints into a chain hierarchy.

    Takes a list of joints and parents them sequentially to form a chain.

    Args:
        joints: Comma-separated list of joint names.
        reverse: Reverse the chain order before parenting. Defaults to False.

    Returns:
        list: List of joint PyNodes in chain hierarchy.

    Example:
        >>> chain = create_chain("jnt_a,jnt_b,jnt_c")

    """
    import luna_rig.functions.jointFn as jointFn

    joint_list = []
    if joints:
        joint_names = [j.strip() for j in joints.split(",")]
        joint_list = [pm.PyNode(j) for j in joint_names if pm.objExists(j)]

    return jointFn.create_chain(joint_list, reverse=reverse)


def mirror_chain(start_joints: str = ""):
    """Mirror joint chains across YZ plane.

    Creates mirrored copies of joint chains with proper naming
    based on Luna naming convention.

    Args:
        start_joints: Comma-separated list of chain start joint names.
            If empty, uses current selection.

    Returns:
        None: Creates mirrored chains in scene.

    Example:
        >>> mirror_chain("l_arm_01_jnt,l_leg_01_jnt")

    """
    import luna_rig.functions.jointFn as jointFn

    chains = []
    if start_joints:
        joint_names = [j.strip() for j in start_joints.split(",")]
        chains = [pm.PyNode(j) for j in joint_names if pm.objExists(j)]

    jointFn.mirror_chain(chains)


def joints_along_curve(
    curve: str = "",
    amount: int = 5,
    joint_name: str = "joint",
    joint_side: str = "c",
    joint_suffix: str = "jnt",
    delete_curve: bool = False,
    attach_to_curve: bool = False,
):
    """Create joints evenly distributed along a curve.

    Places joints at even parameter intervals along the given curve.
    Optionally attaches joints to curve with pointOnCurveInfo nodes.

    Args:
        curve: Name or path of the curve to place joints along.
        amount: Number of joints to create. Defaults to 5.
        joint_name: Base name for joints. Defaults to "joint".
        joint_side: Side prefix (c, l, r). Defaults to "c".
        joint_suffix: Suffix for joints. Defaults to "jnt".
        delete_curve: Delete curve after joint creation. Defaults to False.
        attach_to_curve: Attach joints to curve. Defaults to False.

    Returns:
        list: List of created joint PyNodes.

    Example:
        >>> jnts = joints_along_curve("spine_curve", amount=6)

    """
    import luna_rig.functions.jointFn as jointFn

    crv = pm.PyNode(curve) if curve else None

    return jointFn.along_curve(
        curve=crv,
        amount=amount,
        joint_name=joint_name,
        joint_side=joint_side,
        joint_suffix=joint_suffix,
        delete_curve=delete_curve,
        attach_to_curve=attach_to_curve,
    )

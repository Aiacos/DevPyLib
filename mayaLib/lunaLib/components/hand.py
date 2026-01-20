"""Hand component wrapper for Luna.

Provides a wrapper around Luna's HandComponent for creating
finger rig setups.
"""

import pymel.core as pm


def create_hand(
    finger_joints: str = "",
    name: str = "hand",
    side: str = "l",
    tag: str = "",
):
    """Create a Luna hand component.

    Creates a hand rig with FK controls for each finger.
    Automatically detects finger chains from the provided joints.

    Args:
        finger_joints: Comma-separated list of finger start joints or
            a single parent joint containing all finger chains.
        name: Component name for naming convention. Defaults to "hand".
        side: Side prefix (c, l, r). Defaults to "l" (left).
        tag: Tag string for component identification. Defaults to "".

    Returns:
        HandComponent: Luna hand component instance.

    Example:
        >>> hand = create_hand(
        ...     finger_joints="l_thumb_01_jnt,l_index_01_jnt,l_middle_01_jnt",
        ...     side="l"
        ... )

    """
    from luna_rig.components import HandComponent
    from luna_rig.components import Character

    # Get character if exists
    character = None
    characters = Character.list_nodes(of_type=Character)
    if characters:
        character = characters[0]

    # Parse finger joints
    finger_jnts = []
    if finger_joints:
        joint_names = [j.strip() for j in finger_joints.split(",")]
        finger_jnts = [pm.PyNode(j) for j in joint_names if pm.objExists(j)]

    return HandComponent.create(
        character=character,
        meta_parent=None,
        side=side,
        name=name,
        start_joints=finger_jnts,
        tag=tag,
    )

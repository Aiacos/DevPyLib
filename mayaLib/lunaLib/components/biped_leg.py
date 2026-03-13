"""Biped leg component wrapper for Luna.

Provides a wrapper around Luna's BipedLegComponent for creating
full leg rigs with foot roll.
"""

import pymel.core as pm


def create_biped_leg(
    start_joint: str = "",
    end_joint: str = "",
    foot_locators_grp: str = "",
    name: str = "leg",
    side: str = "l",
    ik_world_orient: bool = True,
    default_state: int = 1,
    tag: str = "",
):
    """Create a Luna biped leg component.

    Creates a complete biped leg rig with FK/IK switching and foot roll.
    Includes automatic pole vector placement and reverse foot setup.

    Args:
        start_joint: Name or path of the hip/thigh joint.
        end_joint: Name or path of the ankle/foot joint.
        foot_locators_grp: Group containing foot roll locators (heel, toe, ball, etc.).
        name: Component name for naming convention. Defaults to "leg".
        side: Side prefix (c, l, r). Defaults to "l" (left).
        ik_world_orient: Orient IK control to world. Defaults to True.
        default_state: Default FK/IK state (0=FK, 1=IK). Defaults to 1.
        tag: Tag string for component identification. Defaults to "".

    Returns:
        BipedLegComponent: Luna biped leg component instance.

    Example:
        >>> leg = create_biped_leg(
        ...     start_joint="l_thigh_jnt",
        ...     end_joint="l_ankle_jnt",
        ...     foot_locators_grp="l_foot_locators_grp",
        ...     side="l"
        ... )

    """
    from luna_rig.components import BipedLegComponent, Character

    # Get character if exists
    character = None
    characters = Character.list_nodes(of_type=Character)
    if characters:
        character = characters[0]

    # Convert string to PyNode
    start_jnt = pm.PyNode(start_joint) if start_joint else None
    end_jnt = pm.PyNode(end_joint) if end_joint else None
    foot_locs = pm.PyNode(foot_locators_grp) if foot_locators_grp else None

    return BipedLegComponent.create(
        character=character,
        start_joint=start_jnt,
        end_joint=end_jnt,
        foot_locators_grp=foot_locs,
        name=name,
        side=side,
        ik_world_orient=ik_world_orient,
        default_state=default_state,
        tag=tag,
    )

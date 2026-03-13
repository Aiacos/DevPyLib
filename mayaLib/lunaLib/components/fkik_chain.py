"""FK/IK switchable chain component wrapper for Luna.

Provides a wrapper around Luna's FKIKComponent for creating FK/IK
switchable control chains.
"""

import pymel.core as pm


def create_fkik_chain(
    start_joint: str = "",
    end_joint: str = "",
    name: str = "fkik_component",
    side: str = "c",
    ik_world_orient: bool = True,
    default_state: int = 1,
    tag: str = "",
):
    """Create a Luna FK/IK switchable chain component.

    Creates a chain with both FK and IK controls that can be switched
    between using a blend attribute. Useful for limbs that need both
    direct rotation control and IK goal-based posing.

    Args:
        start_joint: Name or path of the first joint in the chain.
        end_joint: Name or path of the last joint in the chain.
        name: Component name for naming convention. Defaults to "fkik_component".
        side: Side prefix (c, l, r). Defaults to "c" (center).
        ik_world_orient: Orient IK control to world. Defaults to True.
        default_state: Default FK/IK state (0=FK, 1=IK). Defaults to 1.
        tag: Tag string for component identification. Defaults to "".

    Returns:
        FKIKComponent: Luna FK/IK component instance.

    Example:
        >>> fkik = create_fkik_chain(
        ...     start_joint="arm_01_jnt",
        ...     end_joint="arm_03_jnt",
        ...     name="arm",
        ...     side="l",
        ...     default_state=1
        ... )

    """
    from luna_rig.components import Character, FKIKComponent

    # Get character if exists
    character = None
    characters = Character.list_nodes(of_type=Character)
    if characters:
        character = characters[0]

    # Convert string to PyNode
    start_jnt = pm.PyNode(start_joint) if start_joint else None
    end_jnt = pm.PyNode(end_joint) if end_joint else None

    return FKIKComponent.create(
        character=character,
        start_joint=start_jnt,
        end_joint=end_jnt,
        name=name,
        side=side,
        ik_world_orient=ik_world_orient,
        default_state=default_state,
        tag=tag,
    )

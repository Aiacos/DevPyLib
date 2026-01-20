"""IK chain component wrapper for Luna.

Provides a wrapper around Luna's IKComponent for creating IK control chains.
"""

import pymel.core as pm


def create_ik_chain(
    start_joint: str = "",
    end_joint: str = "",
    name: str = "ik_component",
    side: str = "c",
    tag: str = "",
):
    """Create a Luna IK chain component.

    Creates an IK (Inverse Kinematics) control chain from a joint chain.
    Includes an IK handle, pole vector control, and end effector control.

    Args:
        start_joint: Name or path of the first joint in the chain.
        end_joint: Name or path of the last joint in the chain.
        name: Component name for naming convention. Defaults to "ik_component".
        side: Side prefix (c, l, r). Defaults to "c" (center).
        tag: Tag string for component identification. Defaults to "".

    Returns:
        IKComponent: Luna IK component instance.

    Example:
        >>> ik = create_ik_chain(
        ...     start_joint="arm_01_jnt",
        ...     end_joint="arm_03_jnt",
        ...     name="arm",
        ...     side="l"
        ... )

    """
    from luna_rig.components import IKComponent
    from luna_rig.components import Character

    # Get character if exists
    character = None
    characters = Character.list_nodes(of_type=Character)
    if characters:
        character = characters[0]

    # Convert string to PyNode
    start_jnt = pm.PyNode(start_joint) if start_joint else None
    end_jnt = pm.PyNode(end_joint) if end_joint else None

    return IKComponent.create(
        character=character,
        start_joint=start_jnt,
        end_joint=end_jnt,
        name=name,
        side=side,
        tag=tag,
    )

"""FK chain component wrapper for Luna.

Provides a wrapper around Luna's FKComponent for creating FK control chains.
"""

import pymel.core as pm


def create_fk_chain(
    start_joint: str = "",
    end_joint: str = "",
    name: str = "fk_component",
    side: str = "c",
    add_end_control: bool = True,
    lock_translate: bool = True,
    tag: str = "",
):
    """Create a Luna FK chain component.

    Creates an FK (Forward Kinematics) control chain from a joint chain.
    Each joint gets an FK control for direct rotation manipulation.

    Args:
        start_joint: Name or path of the first joint in the chain.
        end_joint: Name or path of the last joint in the chain.
        name: Component name for naming convention. Defaults to "fk_component".
        side: Side prefix (c, l, r). Defaults to "c" (center).
        add_end_control: Add control to end joint. Defaults to True.
        lock_translate: Lock translation on controls. Defaults to True.
        tag: Tag string for component identification. Defaults to "".

    Returns:
        FKComponent: Luna FK component instance.

    Example:
        >>> fk = create_fk_chain(
        ...     start_joint="arm_01_jnt",
        ...     end_joint="arm_03_jnt",
        ...     name="arm",
        ...     side="l"
        ... )

    """
    from luna_rig.components import Character, FKComponent

    # Get character if exists
    character = None
    characters = Character.list_nodes(of_type=Character)
    if characters:
        character = characters[0]

    # Convert string to PyNode
    start_jnt = pm.PyNode(start_joint) if start_joint else None
    end_jnt = pm.PyNode(end_joint) if end_joint else None

    return FKComponent.create(
        character=character,
        start_joint=start_jnt,
        end_joint=end_jnt,
        name=name,
        side=side,
        add_end_ctl=add_end_control,
        lock_translate=lock_translate,
        tag=tag,
    )

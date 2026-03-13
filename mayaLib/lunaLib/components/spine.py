"""Spine component wrappers for Luna.

Provides wrappers around Luna's spine components for creating
FK/IK and ribbon-based spine rigs.
"""

import pymel.core as pm


def create_fkik_spine(
    start_joint: str = "",
    end_joint: str = "",
    name: str = "spine",
    side: str = "c",
    num_controls: int = 4,
    tag: str = "",
):
    """Create a Luna FK/IK spine component.

    Creates a spine rig with FK/IK switching capability.
    The spine uses a spline IK setup with FK controls along the curve.

    Args:
        start_joint: Name or path of the first spine joint.
        end_joint: Name or path of the last spine joint.
        name: Component name for naming convention. Defaults to "spine".
        side: Side prefix (c, l, r). Defaults to "c" (center).
        num_controls: Number of FK controls along spine. Defaults to 4.
        tag: Tag string for component identification. Defaults to "".

    Returns:
        FKIKSpineComponent: Luna FK/IK spine component instance.

    Example:
        >>> spine = create_fkik_spine(
        ...     start_joint="spine_01_jnt",
        ...     end_joint="spine_05_jnt",
        ...     num_controls=4
        ... )

    """
    from luna_rig.components import Character, FKIKSpineComponent

    # Get character if exists
    character = None
    characters = Character.list_nodes(of_type=Character)
    if characters:
        character = characters[0]

    # Convert string to PyNode
    start_jnt = pm.PyNode(start_joint) if start_joint else None
    end_jnt = pm.PyNode(end_joint) if end_joint else None

    return FKIKSpineComponent.create(
        character=character,
        start_joint=start_jnt,
        end_joint=end_jnt,
        name=name,
        side=side,
        tag=tag,
    )


def create_ribbon_spine(
    start_joint: str = "",
    end_joint: str = "",
    name: str = "spine",
    side: str = "c",
    tag: str = "",
):
    """Create a Luna ribbon spine component.

    Creates a spine rig using a ribbon/surface-based deformation setup.
    Provides smooth bending with volume preservation.

    Args:
        start_joint: Name or path of the first spine joint.
        end_joint: Name or path of the last spine joint.
        name: Component name for naming convention. Defaults to "spine".
        side: Side prefix (c, l, r). Defaults to "c" (center).
        tag: Tag string for component identification. Defaults to "".

    Returns:
        RibbonSpineComponent: Luna ribbon spine component instance.

    Example:
        >>> ribbon_spine = create_ribbon_spine(
        ...     start_joint="spine_01_jnt",
        ...     end_joint="spine_05_jnt"
        ... )

    """
    from luna_rig.components import Character, RibbonSpineComponent

    # Get character if exists
    character = None
    characters = Character.list_nodes(of_type=Character)
    if characters:
        character = characters[0]

    # Convert string to PyNode
    start_jnt = pm.PyNode(start_joint) if start_joint else None
    end_jnt = pm.PyNode(end_joint) if end_joint else None

    return RibbonSpineComponent.create(
        character=character,
        start_joint=start_jnt,
        end_joint=end_jnt,
        name=name,
        side=side,
        tag=tag,
    )

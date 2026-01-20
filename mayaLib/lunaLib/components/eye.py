"""Eye component wrapper for Luna.

Provides a wrapper around Luna's EyeComponent for creating
eye aim setups.
"""

import pymel.core as pm


def create_eye(
    eye_joint: str = "",
    aim_locator: str = "",
    name: str = "eye",
    side: str = "l",
    tag: str = "",
):
    """Create a Luna eye aim component.

    Creates an eye rig with aim constraint setup for look-at functionality.
    Includes controls for aim target and local eye rotation.

    Args:
        eye_joint: Name or path of the eye joint.
        aim_locator: Name or path of the aim target locator.
        name: Component name for naming convention. Defaults to "eye".
        side: Side prefix (c, l, r). Defaults to "l" (left).
        tag: Tag string for component identification. Defaults to "".

    Returns:
        EyeComponent: Luna eye component instance.

    Example:
        >>> eye = create_eye(
        ...     eye_joint="l_eye_jnt",
        ...     aim_locator="l_eye_aim_loc",
        ...     side="l"
        ... )

    """
    from luna_rig.components import EyeComponent
    from luna_rig.components import Character

    # Get character if exists
    character = None
    characters = Character.list_nodes(of_type=Character)
    if characters:
        character = characters[0]

    # Convert string to PyNode
    eye_jnt = pm.PyNode(eye_joint) if eye_joint else None
    aim_loc = pm.PyNode(aim_locator) if aim_locator else None

    return EyeComponent.create(
        character=character,
        meta_parent=None,
        side=side,
        name=name,
        eye_joint=eye_jnt,
        target_guide=aim_loc,
        tag=tag,
    )

"""Character component wrapper for Luna.

Provides a wrapper around Luna's Character component for creating
the root character rig structure.
"""

import pymel.core as pm


def create_character(name: str = "character", tag: str = "character"):
    """Create a Luna Character rig component.

    Creates the root character component which contains the main hierarchy
    for a Luna rig including control_rig, deformation_rig, geometry group,
    locators group, and utility group.

    Args:
        name: Character name used for naming convention. Defaults to "character".
        tag: Tag string for component identification. Defaults to "character".

    Returns:
        Character: Luna Character component instance.

    Example:
        >>> char = create_character(name="hero")
        >>> print(char.root_control)

    """
    from luna_rig.components import Character

    return Character.create(name=name, tag=tag)

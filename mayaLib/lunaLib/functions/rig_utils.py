"""Rig utility wrappers for Luna.

Provides wrapper functions around Luna's rig management utilities.
"""

import pymel.core as pm


def list_controls(tag: str = ""):
    """List all controls in the current Luna character.

    Returns all Luna Control objects attached to the current character,
    optionally filtered by tag.

    Args:
        tag: Filter controls by tag (e.g., "fk", "ik", "root"). Defaults to "".

    Returns:
        list: List of Luna Control objects.

    Example:
        >>> all_ctls = list_controls()
        >>> fk_ctls = list_controls(tag="fk")

    """
    from luna_rig.components import Character

    characters = Character.list_nodes(of_type=Character)
    if not characters:
        return []

    char = characters[0]
    return char.list_controls(tag=tag if tag else None)


def get_character(name: str = ""):
    """Get Luna Character by name.

    Finds and returns a Luna Character component by its name.
    If no name is provided, returns the first character found.

    Args:
        name: Character name to search for. Defaults to "" (first character).

    Returns:
        Character: Luna Character component instance, or None if not found.

    Example:
        >>> char = get_character("hero")
        >>> print(char.root_control)

    """
    from luna_rig.components import Character

    if name:
        return Character.find(name)

    characters = Character.list_nodes(of_type=Character)
    if characters:
        return characters[0]
    return None


def list_characters():
    """List all Luna Characters in the scene.

    Returns all Luna Character components currently in the scene.

    Returns:
        list: List of Luna Character component instances.

    Example:
        >>> chars = list_characters()
        >>> for char in chars:
        ...     print(char.pynode.characterName.get())

    """
    from luna_rig.components import Character

    return Character.list_nodes(of_type=Character)


def get_build_character():
    """Get or create the build character.

    Returns the current build character if one exists,
    otherwise creates a new one.

    Returns:
        Character: Luna Character component instance.

    Example:
        >>> char = get_build_character()

    """
    from luna_rig.components import Character

    characters = Character.list_nodes(of_type=Character)
    if characters:
        return characters[0]
    return Character.create()

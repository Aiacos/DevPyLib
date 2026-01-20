"""Naming utility wrappers for Luna.

Provides wrapper functions around Luna's naming convention utilities.
"""

import pymel.core as pm


def generate_name(
    name: str = "object",
    side: str = "c",
    suffix: str = "grp",
    override_index: str = "",
):
    """Generate a name following Luna naming convention.

    Creates a unique name using Luna's template-based naming system.
    Automatically increments index if name already exists.

    Args:
        name: Base name for the object. Can include underscores.
        side: Side prefix (c, l, r for center, left, right). Defaults to "c".
        suffix: Object type suffix (grp, jnt, ctl, etc.). Defaults to "grp".
        override_index: Force a specific index instead of auto-increment.

    Returns:
        str: Generated unique name string.

    Example:
        >>> name = generate_name("arm", "l", "jnt")
        >>> print(name)  # "l_arm_00_jnt"

    """
    import luna_rig.functions.nameFn as nameFn

    return nameFn.generate_name(
        name=name,
        side=side,
        suffix=suffix,
        override_index=override_index if override_index else None,
    )


def deconstruct_name(node: str = ""):
    """Parse a node name into its Luna convention parts.

    Breaks down a node name into side, name, index, and suffix
    components based on Luna's naming template.

    Args:
        node: Name or path of the node to parse.

    Returns:
        NameStruct: Object with side, name, indexed_name, index, suffix attributes.

    Example:
        >>> parts = deconstruct_name("l_arm_01_jnt")
        >>> print(parts.side, parts.name, parts.suffix)
        'l' 'arm' 'jnt'

    """
    import luna_rig.functions.nameFn as nameFn

    node_obj = pm.PyNode(node) if node else None
    return nameFn.deconstruct_name(node_obj)


def rename_node(
    node: str = "",
    side: str = "",
    name: str = "",
    index: str = "",
    suffix: str = "",
):
    """Rename a node using Luna naming convention.

    Updates a node's name by modifying specific parts of its
    current Luna-convention name.

    Args:
        node: Name or path of the node to rename.
        side: New side prefix. Leave empty to keep current.
        name: New base name. Leave empty to keep current.
        index: New index. Leave empty to keep current.
        suffix: New suffix. Leave empty to keep current.

    Returns:
        None: Renames node in place.

    Example:
        >>> rename_node("l_arm_01_jnt", side="r")  # -> "r_arm_01_jnt"

    """
    import luna_rig.functions.nameFn as nameFn

    node_obj = pm.PyNode(node) if node else None

    nameFn.rename(
        node=node_obj,
        side=side if side else None,
        name=name if name else None,
        index=index if index else None,
        suffix=suffix if suffix else None,
    )

"""Helpers for building common transform hierarchies in Maya rigs."""

from __future__ import annotations

import pymel.core as pm

from mayaLib.rigLib.utils import matrix_utils
from mayaLib.rigLib.utils import name as name_utils

__all__ = ["make_offset_group", "make_modify_group"]


def _default_prefix(node) -> str:
    """Derive a safe prefix from a node name when not supplied."""
    return name_utils.remove_suffix(node)


def make_offset_group(node, prefix: str | None = None):
    """Create an offset group above a transform while preserving parenting.

    Args:
        node: PyNode or string representing the transform to wrap.
        prefix: Optional prefix for naming the new group.

    Returns:
        The newly created offset group as a PyNode.
    """
    node = pm.PyNode(node)
    prefix = (prefix or _default_prefix(node)) + "Offset"

    offset_group = pm.group(n=f"{prefix}_GRP", em=True)
    parent = pm.listRelatives(node, parent=True)
    if parent:
        pm.parent(offset_group, parent[0])

    matrix_utils.match_transform_with_scale(node, offset_group)
    pm.parent(node, offset_group)
    return offset_group


def make_modify_group(node, prefix: str | None = None):
    """Create a modify group directly above a transform node."""
    node = pm.PyNode(node)
    prefix = (prefix or _default_prefix(node)) + "Modify"

    modify_group = pm.group(n=f"{prefix}_GRP", em=True)
    parent = pm.listRelatives(node, parent=True)
    if parent:
        pm.parent(modify_group, parent[0])

    matrix_utils.match_transform_with_scale(node, modify_group)
    pm.parent(node, modify_group)
    return modify_group

"""One-shot transform matching utilities that replace constraint-then-delete patterns."""

from __future__ import annotations

import pymel.core as pm

__all__ = [
    "match_translation",
    "match_rotation",
    "match_transform",
    "match_transform_with_scale",
]


def match_translation(source, target) -> None:
    """Copy world-space translation from source to target.

    Args:
        source: Node to read position from.
        target: Node to apply position to.
    """
    source = pm.PyNode(source)
    target = pm.PyNode(target)
    pos = pm.xform(source, q=True, ws=True, t=True)
    pm.xform(target, ws=True, t=pos)


def match_rotation(source, target) -> None:
    """Copy world-space rotation from source to target.

    Args:
        source: Node to read rotation from.
        target: Node to apply rotation to.
    """
    source = pm.PyNode(source)
    target = pm.PyNode(target)
    rot = pm.xform(source, q=True, ws=True, ro=True)
    pm.xform(target, ws=True, ro=rot)


def match_transform(source, target) -> None:
    """Copy world-space translation and rotation from source to target.

    This replaces the common pattern of creating a parent constraint,
    reading the result, and deleting the constraint.

    Args:
        source: Node to read transform from.
        target: Node to apply transform to.
    """
    source = pm.PyNode(source)
    target = pm.PyNode(target)
    pos = pm.xform(source, q=True, ws=True, t=True)
    rot = pm.xform(source, q=True, ws=True, ro=True)
    pm.xform(target, ws=True, t=pos)
    pm.xform(target, ws=True, ro=rot)


def match_transform_with_scale(source, target) -> None:
    """Copy world-space translation, rotation, and scale from source to target.

    Args:
        source: Node to read transform from.
        target: Node to apply transform to.
    """
    source = pm.PyNode(source)
    target = pm.PyNode(target)
    pos = pm.xform(source, q=True, ws=True, t=True)
    rot = pm.xform(source, q=True, ws=True, ro=True)
    scale = pm.xform(source, q=True, ws=True, s=True)
    pm.xform(target, ws=True, t=pos)
    pm.xform(target, ws=True, ro=rot)
    pm.xform(target, ws=True, s=scale)

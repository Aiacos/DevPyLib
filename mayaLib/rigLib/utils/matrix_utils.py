"""One-shot transform matching utilities that replace constraint-then-delete patterns."""

from __future__ import annotations

import pymel.core as pm

__all__ = [
    "match_translation",
    "match_rotation",
    "match_transform",
    "match_transform_with_scale",
    "connect_via_matrix",
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


def connect_via_matrix(source, target, maintain_offset=True) -> None:
    """Connect source to target using matrix multiplication nodes.

    Creates a matrix-based connection between source and target objects,
    replacing the need for parent constraints with more efficient
    matrix multiplication.

    Args:
        source: Name of the source object driving the connection.
        target: Name of the target object to be driven.
        maintain_offset: Whether to maintain the current offset
            between source and target. Defaults to True.
    """
    if not pm.objExists(source) or not pm.objExists(target):
        pm.warning(f"Cannot connect: {source} or {target} does not exist.")
        return

    # Create unique node names based on source and target
    node_prefix = f"{source}_{target}".replace("|", "_")

    # Create matrix multiplication node
    mult_matrix = pm.shadingNode(
        "multMatrix", asUtility=True, name=f"{node_prefix}_multMatrix"
    )

    # Create decompose matrix node
    decompose = pm.shadingNode(
        "decomposeMatrix", asUtility=True, name=f"{node_prefix}_decomposeMatrix"
    )

    if maintain_offset:
        # Calculate offset matrix
        source_world = pm.getAttr(f"{source}.worldMatrix[0]")
        target_world = pm.getAttr(f"{target}.worldMatrix[0]")
        offset_matrix = target_world * source_world.inverse()

        # Store offset in a constant matrix (using a hold node)
        offset_node = pm.shadingNode(
            "holdMatrix", asUtility=True, name=f"{node_prefix}_offsetMatrix"
        )
        pm.setAttr(f"{offset_node}.inMatrix", offset_matrix, type="matrix")

        # Connect: offset * source.worldMatrix * target.parentInverseMatrix
        pm.connectAttr(f"{offset_node}.outMatrix", f"{mult_matrix}.matrixIn[0]")
        pm.connectAttr(f"{source}.worldMatrix[0]", f"{mult_matrix}.matrixIn[1]")
        pm.connectAttr(
            f"{target}.parentInverseMatrix[0]", f"{mult_matrix}.matrixIn[2]"
        )
    else:
        # Direct connection: source.worldMatrix * target.parentInverseMatrix
        pm.connectAttr(f"{source}.worldMatrix[0]", f"{mult_matrix}.matrixIn[0]")
        pm.connectAttr(
            f"{target}.parentInverseMatrix[0]", f"{mult_matrix}.matrixIn[1]"
        )

    # Connect mult matrix output to decompose
    pm.connectAttr(f"{mult_matrix}.matrixSum", f"{decompose}.inputMatrix")

    # Connect decompose outputs to target transform
    pm.connectAttr(f"{decompose}.outputTranslate", f"{target}.translate", f=True)
    pm.connectAttr(f"{decompose}.outputRotate", f"{target}.rotate", f=True)
    pm.connectAttr(f"{decompose}.outputScale", f"{target}.scale", f=True)

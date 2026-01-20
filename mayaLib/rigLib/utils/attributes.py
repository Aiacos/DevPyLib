"""Attribute helpers used throughout the rigging utilities."""

from __future__ import annotations

from collections.abc import Sequence

import pymel.core as pm

__all__ = ["add_vector_attribute", "add_float_attribute"]


def add_vector_attribute(
    node,
    name: str,
    default_value: Sequence[float] | None = None,
) -> pm.general.Attribute:
    """Ensure a double3 attribute exists on ``node`` and set its value."""
    default_value = list(default_value or (0.0, 0.0, 0.0))
    node = pm.PyNode(node)
    attr = pm.ls(f"{node}.{name}")
    if not attr:
        pm.addAttr(node, longName=name, attributeType="double3")
        pm.addAttr(
            node,
            longName=f"{name}X",
            attributeType="double",
            parent=name,
            dv=default_value[0],
        )
        pm.addAttr(
            node,
            longName=f"{name}Y",
            attributeType="double",
            parent=name,
            dv=default_value[1],
        )
        pm.addAttr(
            node,
            longName=f"{name}Z",
            attributeType="double",
            parent=name,
            dv=default_value[2],
        )
    else:
        node.attr(f"{name}X").set(default_value[0])
        node.attr(f"{name}Y").set(default_value[1])
        node.attr(f"{name}Z").set(default_value[2])
    return node.attr(name)


def add_float_attribute(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    node,
    name: str,
    default_value: float = 0.0,
    keyable: bool = False,
    min_value: float | None = None,
    max_value: float | None = None,
) -> pm.general.Attribute:
    """Ensure a float attribute exists on ``node`` and set its value."""
    node = pm.PyNode(node)
    attr = pm.ls(f"{node}.{name}")
    if not attr:
        kwargs = {
            "longName": name,
            "attributeType": "float",
            "k": keyable,
            "dv": default_value,
        }
        if min_value is not None:
            kwargs["min"] = min_value
        if max_value is not None:
            kwargs["max"] = max_value
        pm.addAttr(node, **kwargs)
    else:
        node.attr(name).set(default_value)
    return node.attr(name)

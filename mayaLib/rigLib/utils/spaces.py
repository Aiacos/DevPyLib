"""Space switching utilities for rig controls."""

from __future__ import annotations

import pymel.core as pm

from mayaLib.rigLib.utils import common

__all__ = ["create_space_switch"]


def _ensure_enum_attribute(node, attr_name: str, labels: list[str]) -> pm.general.Attribute:
    """Create or update an enum attribute used to select spaces."""
    if node.hasAttr(attr_name):
        enum_attr = node.attr(attr_name)
        enum_attr.setEnums({label: index for index, label in enumerate(labels)})
    else:
        enum_attr = pm.addAttr(
            node,
            longName=attr_name,
            attributeType="enum",
            enumName=":".join(labels),
            k=True,
            dv=0,
        )
        enum_attr = node.attr(attr_name)
    return enum_attr

# pylint: disable=too-many-arguments,too-many-positional-arguments
def create_space_switch(
    drivers,
    driver_names,
    destination_constraint,
    destination_node,
    attribute_name: str = "space",
    maintain_offset: bool = True,
) -> None:
    """Create a classic space-switch setup driven by an enum attribute.

    Args:
        drivers: Sequence of transforms providing the spaces.
        driver_names: Matching list of labels for each driver.
        destination_constraint: The parent constraint controlling the driven node.
        destination_node: Control object receiving the enum attribute.
        attribute_name: Name of the enum attribute to add. Defaults to ``"space"``.
        maintain_offset: Whether to keep offset on the constraint. Defaults to True.
    """
    if len(drivers) != len(driver_names):
        raise ValueError("drivers and driver_names must have matching lengths.")

    destination_constraint = pm.PyNode(destination_constraint)
    destination_node = pm.PyNode(destination_node)
    enum_attr = _ensure_enum_attribute(destination_node, attribute_name, list(driver_names))

    constraints = [
        pm.parentConstraint(driver, destination_constraint, mo=maintain_offset)
        for driver in drivers
    ]

    driver_enum = enum_attr
    space_count = len(constraints)
    driver_values = list(range(space_count))

    for index, constraint in enumerate(constraints):
        driven_values = [0] * space_count
        driven_values[index] = 1
        target_plug = pm.listConnections(
            constraint.target[index].targetWeight,
            source=True,
            plugs=True,
        )[0]
        common.set_driven_key(driver_enum, driver_values, target_plug, driven_values)

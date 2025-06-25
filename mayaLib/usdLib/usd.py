import pymel.core as pm

USD_PURPOSES = {"render", "proxy", "guide", "default"}


def ensure_string_attr(node, attr_name):
    """
    Ensure a string attribute exists on a Maya node.

    Args:
        node (pm.PyNode): The node to add the attribute to.
        attr_name (str): The name of the attribute to add.
    """
    # Check if the attribute already exists
    if not pm.attributeQuery(attr_name, node=node, exists=True):
        # Add the attribute to the node if it doesn't exist
        pm.addAttr(node, longName=attr_name, dataType="string")


def ensure_bool_attr(node, attr_name, default=False):
    """
    Ensure a boolean attribute exists on a Maya node.

    Args:
        node (pm.PyNode): The node to add the attribute to.
        attr_name (str): The name of the attribute to add.
        default (bool, optional): The default value of the attribute. Defaults to False.
    """
    # Check if the attribute already exists
    if not pm.attributeQuery(attr_name, node=node, exists=True):
        # Add the attribute to the node if it doesn't exist
        pm.addAttr(node, longName=attr_name, attributeType="bool")
    # Set the attribute value
    pm.setAttr(f"{node}.{attr_name}", default)
    # Set the attribute to be keyable
    pm.setAttr(f"{node}.{attr_name}", keyable=True)


def ensure_visibility_attr(node, visibility="inherited"):
    """Ensure a USD visibility attribute exists on a Maya node.

    Args:
        node (pm.PyNode): The node to add the attribute to.
        visibility (str, optional): The visibility to set. Defaults to "inherited".
    """
    attr = "USD_visibility"
    if not pm.attributeQuery(attr, node=node, exists=True):
        # Add a USD visibility attribute to the node if it doesn't exist
        pm.addAttr(node, longName=attr, dataType="string")
    # Set the visibility attribute value
    pm.setAttr(f"{node}.{attr}", visibility, type="string")


def set_usd(group_name, type_name="Xform", kind="", purpose="default", hidden=False):
    """Set USD attributes to a given object in Maya.

    This function sets various USD attributes to a given object in Maya.

    Args:
        group_name (str): The name of the object to set USD attributes for.
        type_name (str): The USD type name to set. Defaults to "Xform".
        kind (str): The USD kind to set. Defaults to an empty string.
        purpose (str): The USD purpose to set. Must be one of:
            - default
            - proxy
            - guide
            - render
        hidden (bool): Whether the object should be hidden in USD. Defaults to False.

    Raises:
        ValueError: If the given purpose is invalid.

    """
    if purpose not in USD_PURPOSES:
        raise ValueError(f"USD purpose '{purpose}' is invalid")
    if pm.objExists(group_name):
        ensure_string_attr(group_name, "USD_typeName")
        ensure_string_attr(group_name, "USD_kind")
        ensure_string_attr(group_name, "USD_purpose")
        ensure_bool_attr(group_name, "USD_hidden", hidden)
        ensure_string_attr(group_name, "USD_visibility")

        pm.setAttr(f"{group_name}.USD_typeName", type_name, type="string")
        pm.setAttr(f"{group_name}.USD_kind", kind, type="string")
        pm.setAttr(f"{group_name}.USD_purpose", purpose, type="string")
        pm.setAttr(f"{group_name}.USD_visibility", "inherited", type="string")


def set_usd_attributes_to_group(group_name):
    """Set USD attributes to a given group in Maya.

    This function sets various USD attributes to all objects under a specified
    group in Maya. If the group does not exist, a warning is issued.

    Args:
        group_name (str): The name of the group to set USD attributes for.

    """
    if not pm.objExists(group_name):
        pm.warning(f"Group '{group_name}' non trovato")
        return

    # Configuration dictionary for different group types
    cfg = {
        "geo": ("Scope", "group", "default", False),
        "render": ("Scope", "group", "render", False),
        "proxy": ("Scope", "group", "proxy", False),
        "guide": ("Scope", "group", "guide", False),
        "rig": ("Scope", "assembly", "guide", True),
    }
    # Retrieve configuration for the given group name, default if not found
    type_name, kind, purpose, hidden = cfg.get(
        group_name, ("Xform", "component", "default", False)
    )

    # Set USD attributes to each object in the group
    for obj in pm.ls(group_name):
        set_usd(obj, type_name, kind, purpose, hidden)

import pymel.core as pm


def set_purpose_to_group(group_name, purpose):
    """
    Sets the Purpose to the given group
    Args:
        group_name (string): name of the group
        purpose (string): one of 'render', 'proxy', 'guide'
    """

    if pm.objExists(group_name):
        if not pm.attributeQuery("USD_purpose", node=group_name, exists=True):
            pm.addAttr(group_name, longName="USD_purpose", dataType="string")

        pm.setAttr(group_name + ".USD_purpose", purpose, type="string")


def set_kind_to_group(group_name, kind):
    """
    Sets the Kind to the given group
    Args:
        group_name (string): name of the group
        kind (string): kind to set
    """
    if pm.objExists(group_name):
        if not pm.attributeQuery("USD_kind", node=group_name, exists=True):
            pm.addAttr(group_name, longName="USD_kind", dataType="string")

        pm.setAttr(group_name + ".USD_kind", kind, type="string")


def set_type_name_to_group(group_name, type_name):
    """
    Sets the TypeName to the given group
    Args:
        group_name (string): name of the group
        type_name (string): type name to set
    """
    if pm.objExists(group_name):
        if not pm.attributeQuery("USD_typeName", node=group_name, exists=True):
            pm.addAttr(group_name, longName="USD_typeName", dataType="string")

        pm.setAttr(group_name + ".USD_typeName", type_name, type="string")


def set_usd_attributes_to_group(
    group_name, type_name="xform", kind="component", purpose="default"
):
    """
    Sets USD attributes to the given group
    Args:
        group_name (string): name of the group
        type_name (string): type name to set (default: 'xform')
        kind (string): kind to set (default: 'component')
        purpose (string): purpose to set (default: 'default')
    """
    for obj in pm.ls(group_name):
        if pm.objExists(obj):
            if kind == "component":
                pass

            if group_name == "geo":
                type_name = "Scope"
                kind = ""

            if group_name == "render":
                type_name = "Scope"
                kind = ""
                purpose = "render"

            if group_name == "proxy":
                type_name = "Scope"
                kind = ""
                purpose = "proxy"

            if group_name == "render":
                type_name = "Scope"
                kind = ""
                purpose = "guide"

            set_type_name_to_group(obj.name(), type_name)
            set_kind_to_group(obj.name(), kind)
            set_purpose_to_group(obj.name(), purpose)

import pymel.core as pm

USD_PURPOSES = {"render", "proxy", "guide", "default"}


def ensure_string_attr(node, attr_name):
    if not pm.attributeQuery(attr_name, node=node, exists=True):
        pm.addAttr(node, longName=attr_name, dataType="string")


def ensure_bool_attr(node, attr_name, default=False):
    if not pm.attributeQuery(attr_name, node=node, exists=True):
        pm.addAttr(node, longName=attr_name, attributeType="bool")
    pm.setAttr(f"{node}.{attr_name}", default)
    pm.setAttr(f"{node}.{attr_name}", keyable=True)


def ensure_visibility_attr(node, visibility="inherited"):
    attr = "USD_visibility"
    if not pm.attributeQuery(attr, node=node, exists=True):
        pm.addAttr(node, longName=attr, dataType="string")
    pm.setAttr(f"{node}.{attr}", visibility, type="string")


def set_usd(group_name, type_name="xform", kind="", purpose="default", hidden=False):
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
    if not pm.objExists(group_name):
        pm.warning(f"Group '{group_name}' non trovato")
        return

    cfg = {
        "geo": ("Scope", "group", "default", False),
        "render": ("Scope", "group", "render", False),
        "proxy": ("Scope", "group", "proxy", False),
        "guide": ("Scope", "group", "guide", False),
        "rig": ("Scope", "assembly", "guide", True),
    }
    type_name, kind, purpose, hidden = cfg.get(
        group_name, ("xform", "component", "default", False)
    )

    for obj in pm.ls(group_name):
        set_usd(obj, type_name, kind, purpose, hidden)

"""Serialize and deserialize Houdini node networks to/from JSON.

Captures node types, modified parameters, expressions, keyframes, spare
parameter templates, connections, network boxes, and sticky notes.
Supports recursive subnet traversal.

Usage inside Houdini (Python Shell or Shelf Tool)::

    from houdiniLib.utility.node_serializer import serialize_network, deserialize_network

    # Serialize from explicit node path
    serialize_network("C:/tmp/my_network.json", node_path="/obj/geo1")

    # Serialize from current selection
    serialize_network("C:/tmp/selected.json")

    # Recreate network from JSON
    nodes = deserialize_network("C:/tmp/my_network.json", "/obj/geo1_copy")

Compatibility:
    Tested targeting Houdini 20.x / 21.x.
"""

import contextlib
import json
import logging
from pathlib import Path

import hou

logger = logging.getLogger(__name__)

_SCHEMA_VERSION = 1


# ══════════════════════════════════════════════════════════════════
# Serialization — Parameters
# ══════════════════════════════════════════════════════════════════


def _serialize_keyframes(keyframes):
    """Serialize a tuple of hou.Keyframe objects to a list of dicts.

    Args:
        keyframes: Tuple of hou.Keyframe objects.

    Returns:
        List of dicts with frame, value, slope, and expression data.
    """
    result = []
    for kf in keyframes:
        is_string_kf = isinstance(kf, hou.StringKeyframe)

        kf_data = {"frame": kf.frame()}

        if is_string_kf:
            # StringKeyframe has no value()/slope()/accel() —
            # the "value" is stored as an expression
            kf_data["string_keyframe"] = True
            with contextlib.suppress(hou.OperationFailed):
                kf_data["expression"] = kf.expression()
        else:
            kf_data["value"] = kf.value()
            # Slope/accel may not be set on all keyframes
            for attr, getter in (
                ("slope", "slope"),
                ("in_slope", "inSlope"),
                ("accel", "accel"),
                ("in_accel", "inAccel"),
            ):
                with contextlib.suppress(hou.KeyframeValueNotSet):
                    kf_data[attr] = getattr(kf, getter)()
            try:
                expr = kf.expression()
                if expr:
                    kf_data["expression"] = expr
            except hou.OperationFailed:
                pass

        result.append(kf_data)
    return result


def _serialize_parm(parm, include_keyframes=True):
    """Serialize a single parameter to a dict.

    Args:
        parm: The hou.Parm to serialize.
        include_keyframes: Whether to include keyframe data.

    Returns:
        Dict with 'value' and optional 'expression', 'expression_language',
        'keyframes', 'locked' fields.
    """
    data = {}

    try:
        parm_template = parm.parmTemplate()
        parm_type = parm_template.type()

        # Skip ramp parameters entirely — not serializable in v1
        if parm_type == hou.parmTemplateType.Ramp:
            data["value"] = None
            data["_skipped"] = "ramp"
            return data

        if parm_type in (hou.parmTemplateType.Float, hou.parmTemplateType.Int):
            data["value"] = parm.eval()
        elif parm_type == hou.parmTemplateType.String:
            data["value"] = parm.rawValue()
        elif parm_type == hou.parmTemplateType.Toggle:
            data["value"] = parm.eval()
        else:
            # Fallback: try eval, but ensure JSON-serializable
            val = parm.eval()
            if isinstance(val, int | float | str | bool):
                data["value"] = val
            else:
                data["value"] = parm.rawValue()
    except Exception:
        data["value"] = parm.rawValue()

    # Expression (only if parameter has one)
    try:
        expr = parm.expression()
        if expr:
            data["expression"] = expr
            lang = parm.expressionLanguage()
            if lang == hou.exprLanguage.Python:
                data["expression_language"] = "python"
            else:
                data["expression_language"] = "hscript"
    except hou.OperationFailed:
        pass

    # Keyframes
    if include_keyframes:
        keyframes = parm.keyframes()
        if keyframes:
            data["keyframes"] = _serialize_keyframes(keyframes)

    # Locked state (only if locked)
    if parm.isLocked():
        data["locked"] = True

    return data


def _serialize_parameters(node, include_keyframes=True):
    """Serialize only non-default parameters of a node.

    Args:
        node: The hou.Node to inspect.
        include_keyframes: Whether to include keyframe data.

    Returns:
        Dict mapping parameter names to their serialized data.
    """
    params = {}
    for parm in node.parms():
        # Skip parameters that are at their default value with no
        # expressions or keyframes
        try:
            if parm.isAtDefault() and not parm.keyframes():
                continue
        except (hou.OperationFailed, AttributeError):
            pass

        parm_data = _serialize_parm(parm, include_keyframes)
        params[parm.name()] = parm_data

    return params


# ══════════════════════════════════════════════════════════════════
# Serialization — Spare Parameter Templates
# ══════════════════════════════════════════════════════════════════

_TEMPLATE_TYPE_MAP = {
    hou.parmTemplateType.Float: "Float",
    hou.parmTemplateType.Int: "Int",
    hou.parmTemplateType.String: "String",
    hou.parmTemplateType.Toggle: "Toggle",
    hou.parmTemplateType.Menu: "Menu",
    hou.parmTemplateType.Button: "Button",
    hou.parmTemplateType.Separator: "Separator",
    hou.parmTemplateType.FolderSet: "FolderSet",
    hou.parmTemplateType.Folder: "Folder",
}


def _serialize_parm_template(template):
    """Serialize a single hou.ParmTemplate to a dict.

    Args:
        template: The hou.ParmTemplate to serialize.

    Returns:
        Dict describing the template, or None if the type is unsupported.
    """
    parm_type = template.type()
    type_name = _TEMPLATE_TYPE_MAP.get(parm_type)
    if type_name is None:
        logger.warning("Unsupported parm template type: %s", parm_type)
        return None

    data = {
        "template_type": type_name,
        "name": template.name(),
        "label": template.label(),
    }

    if parm_type in (hou.parmTemplateType.Float, hou.parmTemplateType.Int):
        data["num_components"] = template.numComponents()
        data["default"] = list(template.defaultValue())
        data["min"] = template.minValue()
        data["max"] = template.maxValue()

    elif parm_type == hou.parmTemplateType.String:
        data["num_components"] = template.numComponents()
        data["default"] = list(template.defaultValue())

    elif parm_type == hou.parmTemplateType.Toggle:
        data["default"] = template.defaultValue()

    elif parm_type == hou.parmTemplateType.Menu:
        data["menu_items"] = list(template.menuItems())
        data["menu_labels"] = list(template.menuLabels())
        data["default"] = template.defaultValue()

    elif parm_type in (hou.parmTemplateType.Folder, hou.parmTemplateType.FolderSet):
        data["folder_type"] = str(template.folderType())
        child_templates = []
        # Only FolderParmTemplate has parmTemplates(); FolderSetParmTemplate does not
        if hasattr(template, "parmTemplates"):
            for t in template.parmTemplates():
                serialized = _serialize_parm_template(t)
                if serialized is not None:
                    child_templates.append(serialized)
        data["parm_templates"] = child_templates

    return data


def _serialize_spare_templates(node):
    """Serialize spare (non-built-in) parameter templates.

    Uses hou.Node.spareParms() to reliably identify user-added parameters,
    then serializes their templates (deduplicated by name).

    Args:
        node: The hou.Node to inspect.

    Returns:
        List of serialized template dicts, or empty list.
    """
    try:
        spare_parms = node.spareParms()
    except AttributeError:
        return []

    if not spare_parms:
        return []

    # Collect unique template names from spare parms
    seen = set()
    spare_templates = []
    for parm in spare_parms:
        tpl = parm.parmTemplate()
        # For multi-component parms (e.g. vector3), the tuple shares one
        # template — deduplicate by template name
        if tpl.name() in seen:
            continue
        seen.add(tpl.name())
        serialized = _serialize_parm_template(tpl)
        if serialized is not None:
            spare_templates.append(serialized)

    return spare_templates


# ══════════════════════════════════════════════════════════════════
# Serialization — Flags
# ══════════════════════════════════════════════════════════════════


def _serialize_flags(node):
    """Serialize node flags.

    Args:
        node: The hou.Node to inspect.

    Returns:
        Dict of flag names to boolean values.
    """
    flags = {}
    for flag_name, getter in (
        ("display", "isDisplayFlagSet"),
        ("render", "isRenderFlagSet"),
        ("bypass", "isBypassFlagSet"),
        ("template", "isTemplateFlagSet"),
        ("lock", "isHardLocked"),
    ):
        try:
            flags[flag_name] = getattr(node, getter)()
        except AttributeError:
            flags[flag_name] = False
    return flags


# ══════════════════════════════════════════════════════════════════
# Serialization — Connections
# ══════════════════════════════════════════════════════════════════


def _serialize_connections(parent):
    """Serialize all connections between children of a parent node.

    Handles both regular node-to-node connections and subnet indirect
    inputs (the "pipe" connectors at the top of subnets).

    Args:
        parent: The parent hou.Node whose children's connections to capture.

    Returns:
        List of connection dicts.
    """
    connections = []

    for child in parent.children():
        for conn in child.inputConnections():
            # hou.NodeConnection naming (empirically verified):
            #   inputNode()   = upstream source node
            #   outputNode()  = downstream destination node (== child)
            #   inputIndex()  = INPUT port index on the destination
            #   outputIndex() = OUTPUT port index on the source
            conn_data = {
                "to_node": conn.outputNode().name(),
                "to_index": conn.inputIndex(),
            }

            input_item = conn.inputItem()

            # Trace through network dots to find the real source.
            # Stop at SubnetIndirectInput — don't trace through it.
            traced_item = input_item
            while isinstance(traced_item, hou.NetworkDot):
                next_item = traced_item.inputItem()
                if next_item is None:
                    break
                traced_item = next_item

            # Check if traced to a subnet indirect input
            is_indirect = (
                isinstance(traced_item, hou.SubnetIndirectInput)
                or "SubnetIndirectInput" in type(traced_item).__name__
            )

            if is_indirect:
                conn_data["from_node"] = None
                conn_data["indirect_index"] = traced_item.number()
                conn_data["from_index"] = 0
            else:
                from_node = conn.inputNode()
                from_index = conn.outputIndex()
                # Check if source is a sibling (same parent) or cross-level
                if from_node.parent() == parent:
                    conn_data["from_node"] = from_node.name()
                else:
                    # Cross-level connection: store relative path from parent
                    conn_data["from_node"] = parent.relativePathTo(from_node)
                    conn_data["cross_level"] = True
                conn_data["from_index"] = from_index

            connections.append(conn_data)

    return connections


# ══════════════════════════════════════════════════════════════════
# Serialization — Network Boxes & Sticky Notes
# ══════════════════════════════════════════════════════════════════


def _serialize_network_boxes(parent):
    """Serialize network boxes and their contained items.

    Args:
        parent: The parent hou.Node.

    Returns:
        List of network box dicts.
    """
    boxes = []
    for netbox in parent.networkBoxes():
        color = netbox.color()
        pos = netbox.position()
        size = netbox.size()
        items = [item.name() for item in netbox.items() if hasattr(item, "name")]

        boxes.append(
            {
                "name": netbox.name(),
                "comment": netbox.comment(),
                "color": list(color.rgb()),
                "position": [pos[0], pos[1]],
                "size": [size[0], size[1]],
                "items": items,
            }
        )
    return boxes


def _serialize_sticky_notes(parent):
    """Serialize sticky notes in a network.

    Args:
        parent: The parent hou.Node.

    Returns:
        List of sticky note dicts.
    """
    notes = []
    for note in parent.stickyNotes():
        color = note.color()
        pos = note.position()
        size = note.size()

        notes.append(
            {
                "name": note.name(),
                "text": note.text(),
                "color": list(color.rgb()),
                "position": [pos[0], pos[1]],
                "size": [size[0], size[1]],
            }
        )
    return notes


# ══════════════════════════════════════════════════════════════════
# Serialization — Node (recursive)
# ══════════════════════════════════════════════════════════════════


def _serialize_node(node, include_keyframes=True):
    """Serialize a single node to a dict.

    If the node is a subnet (has children) and is not a locked HDA,
    recursively serializes all children and their internal connections.

    Args:
        node: The hou.Node to serialize.
        include_keyframes: Whether to include keyframe data.

    Returns:
        Dict describing the node.
    """
    pos = node.position()
    color = node.color()

    data = {
        "name": node.name(),
        "type": node.type().name(),
        "position": [pos[0], pos[1]],
        "color": list(color.rgb()),
        "comment": node.comment(),
        "flags": _serialize_flags(node),
        "parameters": _serialize_parameters(node, include_keyframes),
        "spare_parameters": _serialize_spare_templates(node),
    }

    # User data
    user_data = {}
    for key in node.userDataDict():
        user_data[key] = node.userData(key)
    if user_data:
        data["user_data"] = user_data

    # Recursive children for subnets
    children = []
    child_connections = []

    try:
        if len(node.children()) > 0 and not node.isLockedHDA():
            for child in node.children():
                children.append(_serialize_node(child, include_keyframes))
            child_connections = _serialize_connections(node)
    except hou.PermissionError:
        logger.warning("Cannot access children of locked HDA: %s", node.path())

    data["children"] = children
    data["connections"] = child_connections

    return data


# ══════════════════════════════════════════════════════════════════
# Serialization — Public API
# ══════════════════════════════════════════════════════════════════


def _resolve_nodes(node_path=None):
    """Resolve the source nodes to serialize.

    Args:
        node_path: Explicit node path, or None for current selection.

    Returns:
        Tuple of (parent_node, list_of_nodes_to_serialize).

    Raises:
        ValueError: If no nodes found or path is invalid.
    """
    if node_path is not None:
        parent = hou.node(node_path)
        if parent is None:
            raise ValueError(f"Node not found: {node_path!r}")
        return parent, list(parent.children())

    selected = hou.selectedNodes()
    if not selected:
        raise ValueError("No nodes selected and no node_path provided.")

    parent = selected[0].parent()
    return parent, list(selected)


def serialize_network(json_path, node_path=None, include_keyframes=True):
    """Serialize a Houdini node network to a JSON file.

    Captures node types, modified parameters, expressions, keyframes, spare
    parameter templates, connections, network boxes, and sticky notes.
    Supports recursive subnet traversal.

    Args:
        json_path (str | Path): Output JSON file path.
        node_path (str | None): Root node path (e.g. "/obj/geo1").
            If None, serializes the currently selected nodes.
        include_keyframes (bool): Include animation keyframes in output.

    Returns:
        Dict containing the serialized network data.

    Raises:
        ValueError: If no nodes are found to serialize.
    """
    json_path = Path(json_path)
    parent, nodes = _resolve_nodes(node_path)

    node_names = {n.name() for n in nodes}

    # Serialize connections — filter to only those between our nodes
    all_connections = _serialize_connections(parent)
    if node_path is None:
        # Selection mode: only keep connections where both ends are selected
        connections = [
            c
            for c in all_connections
            if (c.get("from_node") is None or c["from_node"] in node_names)
            and c["to_node"] in node_names
        ]
    else:
        connections = all_connections

    network_data = {
        "version": _SCHEMA_VERSION,
        "houdini_version": hou.applicationVersionString(),
        "source_path": parent.path(),
        "nodes": [_serialize_node(n, include_keyframes) for n in nodes],
        "connections": connections,
        "network_boxes": _serialize_network_boxes(parent),
        "sticky_notes": _serialize_sticky_notes(parent),
    }

    json_path.parent.mkdir(parents=True, exist_ok=True)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(network_data, f, indent=2, ensure_ascii=False)

    logger.info("Serialized %d nodes to %s", len(nodes), json_path)
    return network_data


# ══════════════════════════════════════════════════════════════════
# Deserialization — Parameter Templates
# ══════════════════════════════════════════════════════════════════


def _build_parm_template(tpl_data):
    """Build a hou.ParmTemplate from a serialized dict.

    Args:
        tpl_data: Dict describing the template.

    Returns:
        A hou.ParmTemplate instance, or None if the type is unsupported.
    """
    ttype = tpl_data.get("template_type")
    name = tpl_data["name"]
    label = tpl_data.get("label", name)

    if ttype == "Float":
        return hou.FloatParmTemplate(
            name,
            label,
            tpl_data.get("num_components", 1),
            default_value=tuple(tpl_data.get("default", (0.0,))),
            min=tpl_data.get("min", 0.0),
            max=tpl_data.get("max", 1.0),
        )
    elif ttype == "Int":
        return hou.IntParmTemplate(
            name,
            label,
            tpl_data.get("num_components", 1),
            default_value=tuple(tpl_data.get("default", (0,))),
            min=tpl_data.get("min", 0),
            max=tpl_data.get("max", 10),
        )
    elif ttype == "String":
        return hou.StringParmTemplate(
            name,
            label,
            tpl_data.get("num_components", 1),
            default_value=tuple(tpl_data.get("default", ("",))),
        )
    elif ttype == "Toggle":
        return hou.ToggleParmTemplate(
            name,
            label,
            default_value=tpl_data.get("default", False),
        )
    elif ttype == "Menu":
        return hou.MenuParmTemplate(
            name,
            label,
            tuple(tpl_data.get("menu_items", ())),
            menu_labels=tuple(tpl_data.get("menu_labels", ())),
            default_value=tpl_data.get("default", 0),
        )
    elif ttype == "Button":
        return hou.ButtonParmTemplate(name, label)
    elif ttype == "Separator":
        return hou.SeparatorParmTemplate(name)
    elif ttype in ("Folder", "FolderSet"):
        children = [_build_parm_template(t) for t in tpl_data.get("parm_templates", [])]
        children = [c for c in children if c is not None]
        return hou.FolderParmTemplate(
            name,
            label,
            parm_templates=children,
        )
    else:
        logger.warning("Unknown template type: %s", ttype)
        return None


def _apply_spare_templates(node, templates_data):
    """Recreate spare parameter templates on a node.

    Must be called BEFORE _apply_parameters so the spare parms exist
    when values are set.

    Args:
        node: The hou.Node to modify.
        templates_data: List of template dicts from JSON.
    """
    if not templates_data:
        return

    ptg = node.parmTemplateGroup()
    for tpl_data in templates_data:
        template = _build_parm_template(tpl_data)
        if template is not None:
            ptg.append(template)
    node.setParmTemplateGroup(ptg)


# ══════════════════════════════════════════════════════════════════
# Deserialization — Parameters
# ══════════════════════════════════════════════════════════════════


def _apply_expression(parm, parm_data):
    """Set an expression on a parameter.

    Args:
        parm: The hou.Parm to set the expression on.
        parm_data: Dict with 'expression' and optional 'expression_language'.
    """
    lang_str = parm_data.get("expression_language", "hscript")
    lang = hou.exprLanguage.Python if lang_str == "python" else hou.exprLanguage.Hscript

    try:
        parm.setExpression(parm_data["expression"], lang)
    except hou.OperationFailed as e:
        logger.warning("Failed to set expression on %s: %s", parm.path(), e)


def _apply_keyframes(parm, keyframes_data):
    """Recreate keyframes on a parameter.

    Args:
        parm: The hou.Parm to set keyframes on.
        keyframes_data: List of keyframe dicts.
    """
    parm.deleteAllKeyframes()
    for kf_data in keyframes_data:
        if kf_data.get("string_keyframe"):
            kf = hou.StringKeyframe()
            kf.setFrame(kf_data["frame"])
            expr = kf_data.get("expression", "")
            if expr:
                with contextlib.suppress(hou.OperationFailed):
                    kf.setExpression(expr, hou.exprLanguage.Hscript)
        else:
            kf = hou.Keyframe()
            kf.setFrame(kf_data["frame"])
            kf.setValue(kf_data["value"])
            for attr, setter in (
                ("slope", "setSlope"),
                ("in_slope", "setInSlope"),
                ("accel", "setAccel"),
                ("in_accel", "setInAccel"),
            ):
                if attr in kf_data:
                    getattr(kf, setter)(kf_data[attr])

            expr = kf_data.get("expression")
            if expr:
                with contextlib.suppress(hou.OperationFailed):
                    kf.setExpression(expr, hou.exprLanguage.Hscript)

        parm.setKeyframe(kf)


def _apply_parameters(node, params_data):
    """Apply serialized parameter values, expressions, and keyframes to a node.

    Args:
        node: The hou.Node to modify.
        params_data: Dict mapping parameter names to their data dicts.
    """
    for parm_name, parm_data in params_data.items():
        parm = node.parm(parm_name)
        if parm is None:
            logger.warning(
                "Parameter %r not found on %s (type: %s)",
                parm_name,
                node.path(),
                node.type().name(),
            )
            continue

        # Keyframes take priority (they implicitly set values)
        if "keyframes" in parm_data:
            _apply_keyframes(parm, parm_data["keyframes"])
        elif "expression" in parm_data:
            _apply_expression(parm, parm_data)
        else:
            try:
                parm.set(parm_data["value"])
            except (TypeError, hou.OperationFailed) as e:
                logger.warning("Failed to set %s = %r: %s", parm.path(), parm_data["value"], e)

        # Lock state
        if parm_data.get("locked", False):
            parm.lock(True)


# ══════════════════════════════════════════════════════════════════
# Deserialization — Flags
# ══════════════════════════════════════════════════════════════════


def _apply_flags(node, flags_data):
    """Apply serialized flags to a node.

    Called last to avoid premature cooking during deserialization.

    Args:
        node: The hou.Node to modify.
        flags_data: Dict of flag names to boolean values.
    """
    flag_setters = {
        "display": "setDisplayFlag",
        "render": "setRenderFlag",
        "bypass": "setBypassFlag",
        "template": "setTemplateFlag",
        "lock": "setHardLocked",
    }
    for flag_name, value in flags_data.items():
        setter_name = flag_setters.get(flag_name)
        if setter_name is None:
            continue
        with contextlib.suppress(AttributeError):
            getattr(node, setter_name)(value)


def _apply_flags_recursive(parent, nodes_data, name_remap):
    """Recursively apply flags to all nodes including subnet children.

    Args:
        parent: The parent hou.Node.
        nodes_data: List of node data dicts.
        name_remap: Dict mapping original names to actual created names.
    """
    for node_data in nodes_data:
        actual_name = name_remap.get(node_data["name"], node_data["name"])
        node = parent.node(actual_name)
        if node is None:
            continue
        _apply_flags(node, node_data.get("flags", {}))
        # Recurse into children
        children_data = node_data.get("children", [])
        if children_data:
            child_remap = {c.name(): c.name() for c in node.children()}
            _apply_flags_recursive(node, children_data, child_remap)


# ══════════════════════════════════════════════════════════════════
# Deserialization — Connections
# ══════════════════════════════════════════════════════════════════


def _recreate_connections(parent, connections_data, name_remap):
    """Recreate connections between nodes using the name remap dict.

    Handles both regular node-to-node connections and subnet indirect
    inputs (entries with from_node=None).

    Args:
        parent: The parent hou.Node containing the child nodes.
        connections_data: List of connection dicts from JSON.
        name_remap: Dict mapping original names to actual created names.
    """
    if not connections_data:
        logger.debug("No connections to recreate")
        return

    for conn in connections_data:
        to_name = name_remap.get(conn["to_node"], conn["to_node"])
        to_node = parent.node(to_name)
        if to_node is None:
            logger.warning("Connection target not found: %r", conn["to_node"])
            continue

        to_index = conn["to_index"]

        if conn.get("from_node") is None:
            # Subnet indirect input — the "pipe" connectors at subnet top
            indirect_index = conn.get("indirect_index", 0)
            try:
                if not parent.isSubNetwork():
                    logger.debug(
                        "Skipping indirect input for non-subnet %s",
                        parent.path(),
                    )
                    continue
                indirect_inputs = parent.indirectInputs()
                if indirect_index < len(indirect_inputs):
                    to_node.setInput(to_index, indirect_inputs[indirect_index])
                else:
                    logger.warning(
                        "Indirect input index %d out of range (%d available) for %s",
                        indirect_index,
                        len(indirect_inputs),
                        parent.path(),
                    )
            except Exception as e:
                logger.warning(
                    "Failed to wire indirect input %d -> %s: %s",
                    indirect_index,
                    to_name,
                    e,
                )
        else:
            raw_from = conn["from_node"]
            is_cross = conn.get("cross_level", False)

            if is_cross:
                # Cross-level: relative path — resolve from parent
                from_node = parent.node(raw_from)
            else:
                # Same level: use name remap for collision handling
                from_name = name_remap.get(raw_from, raw_from)
                from_node = parent.node(from_name)

            if from_node is None:
                logger.warning(
                    "Connection source not found: %r (cross_level=%s)",
                    raw_from,
                    is_cross,
                )
                continue
            from_index = conn["from_index"]

            try:
                to_node.setInput(to_index, from_node, from_index)
            except Exception as e:
                logger.warning(
                    "Failed to connect %s[%d] -> %s[%d]: %s",
                    raw_from,
                    from_index,
                    to_name,
                    to_index,
                    e,
                )


def _wire_deferred_cross_connections(parent):
    """Wire cross-level connections that were deferred during node creation.

    During recursive deserialization, cross-level connections (where the source
    node is at a different hierarchy level) are stored as user data on the subnet
    node. This function processes them after all nodes exist.

    Args:
        parent: The root parent hou.Node to scan recursively.
    """
    for node in parent.allSubChildren():
        stored = node.userData("_deferred_cross_conns")
        if stored is None:
            continue

        cross_conns = json.loads(stored)
        node.destroyUserData("_deferred_cross_conns")

        for conn in cross_conns:
            to_name = conn["to_node"]
            to_node = node.node(to_name)
            if to_node is None:
                logger.warning("Cross-level target not found: %r in %s", to_name, node.path())
                continue

            from_path = conn["from_node"]
            from_node = node.node(from_path)
            if from_node is None:
                logger.warning("Cross-level source not found: %r from %s", from_path, node.path())
                continue

            try:
                to_node.setInput(conn["to_index"], from_node, conn["from_index"])
            except Exception as e:
                logger.warning(
                    "Failed cross-level connect %s -> %s: %s",
                    from_path,
                    to_name,
                    e,
                )


# ══════════════════════════════════════════════════════════════════
# Deserialization — Network Boxes & Sticky Notes
# ══════════════════════════════════════════════════════════════════


def _recreate_network_boxes(parent, boxes_data, name_remap):
    """Recreate network boxes and add items to them.

    Args:
        parent: The parent hou.Node.
        boxes_data: List of network box dicts from JSON.
        name_remap: Dict mapping original names to actual created names.
    """
    for box_data in boxes_data:
        netbox = parent.createNetworkBox(box_data.get("name", ""))
        netbox.setComment(box_data.get("comment", ""))

        color = box_data.get("color")
        if color:
            netbox.setColor(hou.Color((color[0], color[1], color[2])))

        pos = box_data.get("position")
        if pos:
            netbox.setPosition(hou.Vector2(pos[0], pos[1]))

        size = box_data.get("size")
        if size:
            netbox.setSize(hou.Vector2(size[0], size[1]))

        for item_name in box_data.get("items", []):
            actual_name = name_remap.get(item_name, item_name)
            item = parent.node(actual_name)
            if item is not None:
                netbox.addItem(item)
            else:
                logger.warning("Network box item not found: %r", item_name)


def _recreate_sticky_notes(parent, notes_data):
    """Recreate sticky notes in a network.

    Args:
        parent: The parent hou.Node.
        notes_data: List of sticky note dicts from JSON.
    """
    for note_data in notes_data:
        note = parent.createStickyNote(note_data.get("name", ""))
        note.setText(note_data.get("text", ""))

        color = note_data.get("color")
        if color:
            note.setColor(hou.Color((color[0], color[1], color[2])))

        pos = note_data.get("position", [0, 0])
        note.setPosition(hou.Vector2(pos[0], pos[1]))

        size = note_data.get("size", [3, 1.5])
        note.setSize(hou.Vector2(size[0], size[1]))


# ══════════════════════════════════════════════════════════════════
# Deserialization — Node (recursive)
# ══════════════════════════════════════════════════════════════════


def _deserialize_node(parent, node_data, name_remap):
    """Create a single node from serialized data.

    Creates the node, sets its position, applies spare templates and
    parameters, recurses into children for subnets, and records any
    name remapping due to collisions.

    Args:
        parent: The parent hou.Node to create inside.
        node_data: Dict describing the node.
        name_remap: Dict to populate with original_name -> actual_name mappings.

    Returns:
        The created hou.Node, or None on failure.
    """
    node_type = node_data["type"]
    original_name = node_data["name"]

    try:
        node = parent.createNode(node_type, original_name, run_init_scripts=False)
    except hou.OperationFailed as e:
        logger.error("Failed to create node %r (type %s): %s", original_name, node_type, e)
        return None

    actual_name = node.name()
    name_remap[original_name] = actual_name
    if actual_name != original_name:
        logger.info("Node renamed: %r -> %r (collision)", original_name, actual_name)

    # Position
    pos = node_data.get("position", [0, 0])
    node.setPosition(hou.Vector2(pos[0], pos[1]))

    # Color
    color = node_data.get("color")
    if color:
        node.setColor(hou.Color((color[0], color[1], color[2])))

    # Comment
    comment = node_data.get("comment", "")
    if comment:
        node.setComment(comment)
        node.setGenericFlag(hou.nodeFlag.DisplayComment, True)

    # User data
    for key, value in node_data.get("user_data", {}).items():
        node.setUserData(key, value)

    # Spare templates (BEFORE parameters)
    _apply_spare_templates(node, node_data.get("spare_parameters", []))

    # Parameters
    _apply_parameters(node, node_data.get("parameters", {}))

    # Recursive children
    child_remap = {}
    for child_data in node_data.get("children", []):
        _deserialize_node(node, child_data, child_remap)

    # Internal connections (for subnet children)
    # Split: same-level connections now, cross-level deferred
    child_conns = node_data.get("connections", [])
    if child_conns:
        same_level = [c for c in child_conns if not c.get("cross_level")]
        _recreate_connections(node, same_level, child_remap)

        # Collect cross-level connections for deferred wiring
        cross_level = [c for c in child_conns if c.get("cross_level")]
        if cross_level:
            node.setUserData("_deferred_cross_conns", json.dumps(cross_level))

    return node


# ══════════════════════════════════════════════════════════════════
# Deserialization — Public API
# ══════════════════════════════════════════════════════════════════


def deserialize_network(json_path, parent_path):
    """Recreate a Houdini node network from a JSON file.

    All operations are wrapped in a single undo group for atomic rollback.
    If the target parent already contains nodes with the same names,
    they are auto-renamed and an internal name remap dict ensures
    connections are wired correctly.

    Args:
        json_path (str | Path): Path to the JSON file to read.
        parent_path (str): Parent node path where nodes will be created
            (e.g. "/obj/geo1").

    Returns:
        List of top-level hou.Node objects created.

    Raises:
        ValueError: If the parent node is not found or the JSON version
            is unsupported.
        FileNotFoundError: If the JSON file does not exist.
    """
    json_path = Path(json_path)
    if not json_path.exists():
        raise FileNotFoundError(f"JSON file not found: {json_path}")

    parent = hou.node(parent_path)
    if parent is None:
        raise ValueError(f"Parent node not found: {parent_path!r}")

    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    version = data.get("version", 0)
    if version != _SCHEMA_VERSION:
        raise ValueError(f"Unsupported schema version {version} (expected {_SCHEMA_VERSION})")

    created_nodes = []
    name_remap = {}

    with hou.undos.group("Deserialize Network"):
        # Phase 1: Create all nodes with parameters
        for node_data in data.get("nodes", []):
            node = _deserialize_node(parent, node_data, name_remap)
            if node is not None:
                created_nodes.append(node)

        # Phase 2: Recreate top-level connections
        _recreate_connections(parent, data.get("connections", []), name_remap)

        # Phase 2b: Wire deferred cross-level connections (all nodes exist now)
        _wire_deferred_cross_connections(parent)

        # Phase 3: Network boxes and sticky notes
        _recreate_network_boxes(parent, data.get("network_boxes", []), name_remap)
        _recreate_sticky_notes(parent, data.get("sticky_notes", []))

        # Phase 4: Apply flags recursively (last to avoid premature cooking)
        _apply_flags_recursive(parent, data.get("nodes", []), name_remap)

    logger.info("Deserialized %d nodes into %s", len(created_nodes), parent_path)
    return created_nodes

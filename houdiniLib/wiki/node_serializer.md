# Node Serializer — Houdini

Serialize and deserialize Houdini node networks to/from JSON. Captures the full state of a network including node types, parameters, expressions, keyframes, connections, spare parameters, network boxes, and sticky notes. Supports recursive subnet traversal.

## Quick Start

```python
from houdiniLib.utility.node_serializer import serialize_network, deserialize_network

# Serialize a network to JSON
serialize_network("C:/tmp/my_network.json", node_path="/obj/geo1")

# Recreate it somewhere else
deserialize_network("C:/tmp/my_network.json", "/obj/geo1_copy")
```

## API

### `serialize_network(json_path, node_path=None, include_keyframes=True)`

Serialize a node network to a JSON file.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `json_path` | `str \| Path` | *required* | Output JSON file path |
| `node_path` | `str \| None` | `None` | Root node path (e.g. `"/obj/geo1"`). If `None`, uses current selection |
| `include_keyframes` | `bool` | `True` | Include animation keyframes in output |

**Returns:** `dict` — the serialized network data (also written to file).

#### Mode 1: From Node Path

```python
# Serialize all children of /obj/geo1
data = serialize_network("C:/tmp/geo1.json", node_path="/obj/geo1")
```

Serializes all children of the specified node, including all connections, network boxes, and sticky notes within that network.

#### Mode 2: From Selection

```python
# Select nodes in the Network Editor, then:
data = serialize_network("C:/tmp/selected.json")
```

Serializes only the selected nodes and connections between them. Network boxes and sticky notes from the parent are included.

### `deserialize_network(json_path, parent_path)`

Recreate a node network from a JSON file.

| Parameter | Type | Description |
|-----------|------|-------------|
| `json_path` | `str \| Path` | Input JSON file path |
| `parent_path` | `str` | Parent node path where nodes will be created |

**Returns:** `list[hou.Node]` — top-level nodes created.

```python
# Recreate inside an existing geo node
nodes = deserialize_network("C:/tmp/geo1.json", "/obj/geo1_copy")
print(f"Created {len(nodes)} nodes")
```

## What Gets Serialized

| Data | Serialized | Notes |
|------|-----------|-------|
| Node type & name | Yes | Full type name (e.g. `"box"`, `"Sop/unilo::muscle_sim::1.0"`) |
| Position & color | Yes | Exact network editor position and node color |
| Comment | Yes | Node comment text |
| Modified parameters | Yes | Only parameters that differ from their default value |
| Expressions | Yes | HScript and Python expressions with language tag |
| Keyframes | Optional | Frame, value, slope, accel, expression per keyframe |
| Spare parameters | Yes | Template definition (type, name, label, min, max, default) |
| Connections | Yes | Input/output index pairs between nodes |
| Indirect inputs | Yes | Subnet "pipe" connections (`from_node: null`) |
| Network boxes | Yes | Name, comment, color, bounds, contained items |
| Sticky notes | Yes | Name, text, color, position, size |
| Node flags | Yes | Display, render, bypass, template, lock |
| User data | Yes | `hou.Node.userData()` dictionaries (if non-empty) |
| Subnet children | Yes | Recursive — full depth traversal |

### What Is NOT Serialized (v1)

| Data | Reason |
|------|--------|
| Ramp parameters | Complex multi-parm structure — future version |
| Multi-parm blocks | Dynamic child count — future version |
| HDA definitions | Only the type name is stored; HDA must be installed |
| External path references | Raw string stored; may break if deserialized elsewhere |
| Network dots | Decorative only; recreated by Houdini when wiring |

## JSON Format

The JSON file uses schema version 1:

```json
{
  "version": 1,
  "houdini_version": "21.5.100",
  "source_path": "/obj/geo1",
  "nodes": [
    {
      "name": "box1",
      "type": "box",
      "position": [2.0, -1.5],
      "color": [0.8, 0.8, 0.8],
      "comment": "My box",
      "flags": {"display": false, "render": false, "bypass": false, "template": false, "lock": false},
      "parameters": {
        "sizex": {"value": 2.5},
        "ty": {"value": 3.0, "expression": "$FF * 0.1", "expression_language": "hscript"},
        "locked_parm": {"value": 1.0, "locked": true}
      },
      "spare_parameters": [
        {"template_type": "Float", "name": "my_weight", "label": "Weight", "num_components": 1, "default": [0.5], "min": 0.0, "max": 1.0}
      ],
      "user_data": {"custom_key": "custom_value"},
      "children": [],
      "connections": []
    }
  ],
  "connections": [
    {"from_node": "box1", "from_index": 0, "to_node": "transform1", "to_index": 0}
  ],
  "network_boxes": [],
  "sticky_notes": []
}
```

### Parameter Format

Parameters use a compact format where optional fields appear only when needed:

| Field | When Present | Example |
|-------|-------------|---------|
| `value` | Always | `{"value": 2.5}` |
| `expression` | Has expression | `{"value": 1.5, "expression": "ch('../scale')", "expression_language": "hscript"}` |
| `keyframes` | Has animation | `{"value": 3.0, "keyframes": [{"frame": 1, "value": 0.0, "slope": 0.0, ...}]}` |
| `locked` | Is locked | `{"value": 1.0, "locked": true}` |

### Connection Format

Regular connections between sibling nodes:

```json
{"from_node": "box1", "from_index": 0, "to_node": "transform1", "to_index": 0}
```

Subnet indirect inputs (the "pipe" at the top of a subnet):

```json
{"from_node": null, "indirect_index": 0, "to_node": "rest1", "to_index": 0}
```

### Supported Spare Parameter Types

| Type | `template_type` | Fields |
|------|----------------|--------|
| `hou.FloatParmTemplate` | `"Float"` | num_components, default, min, max |
| `hou.IntParmTemplate` | `"Int"` | num_components, default, min, max |
| `hou.StringParmTemplate` | `"String"` | num_components, default |
| `hou.ToggleParmTemplate` | `"Toggle"` | default |
| `hou.MenuParmTemplate` | `"Menu"` | menu_items, menu_labels, default |
| `hou.ButtonParmTemplate` | `"Button"` | *(none)* |
| `hou.SeparatorParmTemplate` | `"Separator"` | *(none)* |
| `hou.FolderParmTemplate` | `"Folder"` / `"FolderSet"` | folder_type, parm_templates (nested) |

## Deserialization Behavior

### Execution Order

1. Create nodes (with `run_init_scripts=False` for performance)
2. Set node positions and colors
3. Apply spare parameter templates
4. Apply parameter values, expressions, and keyframes
5. Recurse into subnet children
6. Wire connections (using name remap for collision handling)
7. Recreate network boxes and sticky notes
8. Apply flags last (avoids premature cooking)

### Name Collision Handling

When the target parent already contains a node with the same name, Houdini auto-renames it (e.g. `box1` becomes `box2`). The deserializer tracks these renames internally and uses the remapped names when wiring connections, so no connections are lost.

### Atomic Undo

All deserialization is wrapped in `hou.undos.group("Deserialize Network")`. If anything goes wrong, a single **Ctrl+Z** undoes the entire import.

### Logging

The module uses Python's `logging` module. To see warnings (missing HDA types, skipped parameters, renamed nodes):

```python
import logging
logging.basicConfig(level=logging.INFO)
```

## Examples

### Backup a Subnet Before Experimenting

```python
from houdiniLib.utility.node_serializer import serialize_network

# Save current state
serialize_network("C:/tmp/backup_before_experiment.json", "/obj/geo1/my_subnet")

# ... experiment freely ...
# If things go wrong, deserialize the backup
```

### Copy a Network Between Scenes

```python
from houdiniLib.utility.node_serializer import serialize_network, deserialize_network

# In scene A: export
serialize_network("C:/pipeline/shared/lighting_rig.json", "/obj/lights")

# In scene B: import
deserialize_network("C:/pipeline/shared/lighting_rig.json", "/obj")
```

### Export Selected Nodes

```python
from houdiniLib.utility.node_serializer import serialize_network

# Select nodes in the Network Editor, then run:
serialize_network("C:/tmp/my_selection.json")
# Only selected nodes and connections between them are saved
```

### Inspect JSON Without Houdini

The JSON is human-readable and can be opened in any text editor or parsed with standard Python:

```python
import json
with open("C:/tmp/my_network.json") as f:
    data = json.load(f)

print(f"Houdini version: {data['houdini_version']}")
print(f"Nodes: {len(data['nodes'])}")
for node in data["nodes"]:
    print(f"  {node['name']} ({node['type']})")
    for parm, val in node["parameters"].items():
        print(f"    {parm} = {val['value']}")
```

## Limitations

- **Locked HDAs**: Children of locked HDAs cannot be serialized. The HDA type and parameters are captured, but internal nodes are skipped.
- **HDA availability**: The target Houdini session must have the same HDAs installed. If an HDA type is missing, the node creation will fail (logged as error).
- **External path references**: Parameters like Object Merge `objpath1` store raw path strings. These may become invalid when loaded in a different scene hierarchy.
- **Ramp / multi-parm**: Not supported in v1. Will be added if needed.
- **No geometry data**: Only the node graph is serialized, not the computed geometry. The geometry is recooked from the recreated network.

## Compatibility

Tested targeting Houdini 20.x / 21.x (verified on 21.5.631). Uses defensive `try/except` patterns for API methods that may differ across versions.

## Developer Notes

API gotchas discovered during development:

- **`hou.Color` is not subscriptable**: Use `color.rgb()` to get `(r, g, b)` tuple, not `color[0]`.
- **`hou.Keyframe` values may be unset**: `slope()`, `inSlope()`, `accel()`, `inAccel()` raise `hou.KeyframeValueNotSet` if not explicitly set. Always wrap in `try/except`.
- **`hou.NodeConnection` naming is inverted**: For `conn` from `node.inputConnections()`, `conn.inputNode()` returns the **upstream source** (not the receiver), and `conn.outputNode()` returns the **downstream destination**. Think "input/output of the wire", not the node.
- **Spare parameter detection**: Use `node.spareParms()` (not template group comparison) to reliably identify user-added parameters. Comparing `ParmTemplateGroup` entries against the node type's defaults can misidentify built-in folder groups as spare.
- **Network dots hide indirect inputs**: `conn.inputItem()` may return `hou.OpNetworkDot` instead of `hou.SubnetIndirectInput`. Dots must be traced with `dot.inputItem()` (one level only) to find the real source. The class hierarchy is `OpNetworkDot → OpIndirectInput → NetworkDot → IndirectInput`, so use `isinstance(item, hou.NetworkDot)` to match dots specifically without also matching `SubnetIndirectInput`.
- **`hou.StringKeyframe`**: String parameters use `hou.StringKeyframe` which has no `value()` method — the value is stored as an expression. Check `isinstance(kf, hou.StringKeyframe)` before calling `kf.value()`.
- **`hou.Ramp` is not JSON-serializable**: Ramp parameters return `hou.Ramp` objects from `parm.eval()`. Must be detected via `parm.parmTemplate().type() == hou.parmTemplateType.Ramp` and skipped.
- **`FolderSetParmTemplate` has no `parmTemplates()`**: Only `FolderParmTemplate` supports iterating child templates. Check with `hasattr(template, "parmTemplates")`.
- **`NetworkBox` uses `position()`/`size()`**: Not `bounds()` — the documented `bounds()` method does not exist on `OpNetworkBox`.

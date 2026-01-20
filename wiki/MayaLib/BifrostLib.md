# BifrostLib Documentation

BifrostLib provides integration between Maya Bifrost graphs and USD (Universal Scene Description), enabling procedural USD stage creation and manipulation through Bifrost's visual programming system.

---

## Table of Contents

- [Overview](#overview)
- [Module Structure](#module-structure)
- [Bifrost API](#bifrost-api)
- [Stage Builder](#stage-builder)
- [Utility Nodes](#utility-nodes)
- [Usage Examples](#usage-examples)
- [Best Practices](#best-practices)

---

## Overview

BifrostLib bridges Maya's Bifrost procedural graph system with USD workflows. It provides:

- **Low-level Bifrost API**: Functions for creating and manipulating Bifrost graph nodes
- **USD Stage Building**: High-level tools for constructing USD stages from Maya scenes
- **Deformer Integration**: Connecting Bifrost outputs to Maya deformers

### Key Features

- Create and configure Bifrost graphs programmatically
- Build USD stages from Maya geometry
- Connect Bifrost outputs to Maya blend shapes and deformers
- Preview USD stages in Maya
- Export animated USD from rigs

### Module Structure

```
bifrostLib/
├── __init__.py
├── bifrost_api.py         # Low-level Bifrost/USD API
├── bifrost_util_nodes.py  # Utility node builders
└── stage_builder.py       # High-level USD stage composition
```

---

## Bifrost API

The `bifrost_api.py` module provides low-level functions for Bifrost graph manipulation.

### USD Utilities

#### get_maya_usd_stage

Get the USD stage from a Maya USD proxy node.

```python
from mayaLib.bifrostLib import bifrost_api as bifrost

# Get stage shape from proxy
stage_shape = bifrost.get_maya_usd_stage(stage_name="mayaUsdProxy1")
```

#### set_maya_usd_stage_shareable

Enable stage sharing for USD proxy.

```python
bifrost.set_maya_usd_stage_shareable(stage_shape, default_value=True)
```

### Graph Creation

#### create_bifrost_graph

Create a new Bifrost graph in Maya.

```python
# Create a Bifrost graph
bifrost_shape = bifrost.create_bifrost_graph(name="myGraph")
# Returns: "myGraph_bifrostGraphShape"
```

#### create_bifrost_maya_shape

Create a Maya transform/shape for Bifrost output.

```python
# Create output geometry
shape = bifrost.create_bifrost_maya_shape(name="bifrost_output")
```

#### create_bifrost_geo_to_maya_node

Create a conversion node from Bifrost geometry to Maya.

```python
# Create bifrostGeoToMaya node
converter = bifrost.create_bifrost_geo_to_maya_node()
```

### Node Operations

#### bf_create_node

Create a node in the Bifrost graph.

```python
# Create a USD stage node
stage_node = bifrost.bf_create_node(
    bifrost_shape,
    "BifrostGraph,USD::Stage,create_usd_stage",
    parent="/"
)

# Create a mesh definition node
mesh_node = bifrost.bf_create_node(
    bifrost_shape,
    "BifrostGraph,USD::Prim,define_usd_mesh",
    parent="/"
)
```

#### Common Node Types

| Category | Node Type | Description |
|----------|-----------|-------------|
| USD::Stage | create_usd_stage | Create USD stage |
| USD::Prim | define_usd_mesh | Define USD mesh prim |
| USD::Prim | define_usd_xform | Define USD transform |
| Core::Time | time | Get current time |

#### bf_get_node_type

Query the type of a Bifrost node.

```python
node_type = bifrost.bf_get_node_type(bifrost_shape, node_name)
```

#### bf_rename_node

Rename a Bifrost node.

```python
new_name = bifrost.bf_rename_node(bifrost_shape, old_name, new_name)
```

### Port Operations

#### bf_list_all_port

List all ports on a node.

```python
ports = bifrost.bf_list_all_port(
    bifrost_shape,
    node_name,
    input_port=True,
    output_port=True,
    list_port_children=""
)
```

#### bf_get_port_type

Get the data type of a port.

```python
port_type = bifrost.bf_get_port_type(bifrost_shape, node_name, port_name)
```

#### bf_add_input_port

Add an input port to a node.

```python
port = bifrost.bf_add_input_port(
    bifrost_shape,
    node_name,
    port_name="input1",
    port_type="float",
    port_children=""
)
```

#### bf_add_output_port

Add an output port to a node.

```python
port = bifrost.bf_add_output_port(
    bifrost_shape,
    node_name,
    port_name="output1",
    port_type="BifrostUsd::Stage",
    port_children=""
)
```

### Connections

#### bf_connect

Connect two ports.

```python
bifrost.bf_connect(
    bifrost_shape,
    "node1.output",
    "node2.input"
)
```

### Compound Operations

#### bf_create_compound

Create a compound node from existing nodes.

```python
compound = bifrost.bf_create_compound(
    bifrost_shape,
    compound_node_list=["node1", "node2", "node3"],
    compound_name="myCompound",
    parent="/"
)
```

#### bf_feedback_port

Enable feedback between ports in a compound.

```python
bifrost.bf_feedback_port(
    bifrost_shape,
    compound_name,
    source_port="iteration",
    destination_port="next_iteration"
)
```

#### bf_sequence_port

Enable sequence between ports in a loop.

```python
bifrost.bf_sequence_port(
    bifrost_shape,
    compound_name,
    source_port="previous",
    destination_port="current"
)
```

### Node Properties

#### bf_set_node_property

Set a property value on a node.

```python
bifrost.bf_set_node_property(
    bifrost_shape,
    node_name,
    property_name="value",
    value=["1.0"]  # Values as list of strings
)
```

### Mesh Operations

#### bf_add_mesh

Add a Maya mesh to the Bifrost graph.

```python
mesh_node = bifrost.bf_add_mesh(
    bifrost_shape,
    geo="pSphere1",
    parent="/",
    connect_out_mesh=False
)
```

### Layout

#### bf_auto_layout

Auto-layout nodes in the Bifrost graph editor.

```python
bifrost.bf_auto_layout()
```

### Deformer Connections

#### connect_bifrostwgt_to_deformerwgt

Connect Bifrost weight output to a deformer.

```python
bifrost.connect_bifrostwgt_to_deformerwgt(
    "bifrost_node.out_weights",
    "deformer.weights"
)
```

#### connect_bifrost_attribute_to_blendshape

Connect Bifrost output to blend shape targets.

```python
bifrost.connect_bifrost_attribute_to_blendshape(
    bifrost_node,
    blendshape_target
)
```

---

## Stage Builder

The `stage_builder.py` module provides high-level USD stage construction.

### USDCharacterBuild Class

Build complete USD stages from Maya character rigs.

```python
from mayaLib.bifrostLib.stage_builder import USDCharacterBuild

builder = USDCharacterBuild(
    name="character_usd",
    root_node="geo",
    save_usd_file="character",
    file_ext="usdc",
    single_usd=False,
    connect_output=True,
    debug=False
)
```

#### Constructor Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | str | "" | Name for the Bifrost graph |
| `root_node` | str | "geo" | Root group to search for geometry |
| `save_usd_file` | str | "tmp" | USD filename |
| `file_ext` | str | "usdc" | USD file extension (usdc, usda) |
| `single_usd` | bool | False | Use single USD stage |
| `connect_output` | bool | True | Connect Bifrost output ports |
| `debug` | bool | False | Keep debug windows open |

#### Methods

```python
# Set frame range
builder.set_start_frame(1)
builder.set_end_frame(100)

# Access Bifrost components
bifrost_shape = builder.bifrost_shape
bifrost_transform = builder.bifrost_transform
```

### get_all_deformed_and_constrained

Find deformed and static meshes under a group.

```python
from mayaLib.bifrostLib.stage_builder import get_all_deformed_and_constrained

deformed, undeformed = get_all_deformed_and_constrained("geo_grp")
# deformed: List of meshes with deformers/constraints
# undeformed: List of static meshes
```

---

## Utility Nodes

The `bifrost_util_nodes.py` module provides common utility node builders.

### file_type_manager

Create a file type manager compound.

```python
from mayaLib.bifrostLib import bifrost_util_nodes

compound = bifrost_util_nodes.file_type_manager(
    bifrost_shape,
    create_usd_stage_node
)
```

### build_preview_compound

Create a preview compound for USD visualization.

```python
preview = bifrost_util_nodes.build_preview_compound(bifrost_shape)
```

---

## Usage Examples

### Basic USD Stage Creation

```python
from mayaLib.bifrostLib import bifrost_api as bifrost
import maya.cmds as cmds

# Create Bifrost graph
bf_shape = bifrost.create_bifrost_graph("usd_export")

# Create USD stage node
stage_node = bifrost.bf_create_node(
    bf_shape,
    "BifrostGraph,USD::Stage,create_usd_stage"
)

# Create time node
time_node = bifrost.bf_create_node(
    bf_shape,
    "BifrostGraph,Core::Time,time"
)

# Connect time to stage
bifrost.bf_connect(bf_shape, f"{time_node}.frame", f"{stage_node}.time")

print(f"Created USD pipeline in {bf_shape}")
```

### Adding Mesh to USD

```python
from mayaLib.bifrostLib import bifrost_api as bifrost

# Create graph
bf_shape = bifrost.create_bifrost_graph("mesh_to_usd")

# Add mesh from scene
mesh_node = bifrost.bf_add_mesh(
    bf_shape,
    geo="pCube1",
    parent="/",
    connect_out_mesh=False
)

# Create mesh definition node
define_mesh = bifrost.bf_create_node(
    bf_shape,
    "BifrostGraph,USD::Prim,define_usd_mesh"
)

# Connect mesh to definition
bifrost.bf_connect(bf_shape, f"{mesh_node}.mesh", f"{define_mesh}.mesh")
```

### Character USD Export

```python
from mayaLib.bifrostLib.stage_builder import USDCharacterBuild

# Build USD from character rig
builder = USDCharacterBuild(
    name="hero_character",
    root_node="model_GRP",
    save_usd_file="hero",
    file_ext="usdc",
    single_usd=True,
    connect_output=True,
    debug=False
)

# Set animation range
builder.set_start_frame(1)
builder.set_end_frame(120)

# Access USD stage
stage = builder.maya_usd_stage
```

### Bifrost to Blend Shape Connection

```python
from mayaLib.bifrostLib import bifrost_api as bifrost
import pymel.core as pm

# Assuming you have a Bifrost node with weight output
bifrost_node = pm.ls("myBifrostGraph")[0]

# Get blend shape node
blendshape = pm.ls("myBlendShape", type="blendShape")[0]

# Connect Bifrost weights to blend shape
bifrost.connect_bifrost_attribute_to_blendshape(
    bifrost_node,
    blendshape.weight[0]
)
```

### Creating Custom Bifrost Compound

```python
from mayaLib.bifrostLib import bifrost_api as bifrost

# Create graph
bf_shape = bifrost.create_bifrost_graph("custom_setup")

# Create nodes
node1 = bifrost.bf_create_node(bf_shape, "BifrostGraph,Core::Math,add")
node2 = bifrost.bf_create_node(bf_shape, "BifrostGraph,Core::Math,multiply")
node3 = bifrost.bf_create_node(bf_shape, "BifrostGraph,Core::Math,subtract")

# Connect nodes
bifrost.bf_connect(bf_shape, f"{node1}.output", f"{node2}.first")
bifrost.bf_connect(bf_shape, f"{node2}.output", f"{node3}.first")

# Create compound from nodes
compound = bifrost.bf_create_compound(
    bf_shape,
    compound_node_list=[node1, node2, node3],
    compound_name="math_operations",
    parent="/"
)

print(f"Created compound: {compound}")
```

---

## Port Types Reference

Common Bifrost port types:

| Type | Description |
|------|-------------|
| `float` | Single float value |
| `int` | Integer value |
| `bool` | Boolean value |
| `string` | String value |
| `Object` | Generic object |
| `Amino::Array` | Array of values |
| `BifrostUsd::Stage` | USD stage |
| `BifrostUsd::Prim` | USD prim |
| `BifrostGeo::Mesh` | Bifrost mesh |

---

## Best Practices

1. **Name graphs descriptively**: Use clear names like `character_usd_export`
2. **Use compounds**: Organize complex operations into compounds
3. **Set stage shareable**: Enable sharing for USD proxy stages
4. **Close debug windows**: Set `debug=False` in production
5. **Cache heavy operations**: Use Bifrost caching for performance
6. **Separate deformed/static**: Process deformed meshes differently
7. **Use proper file extensions**: `.usdc` for binary, `.usda` for ASCII

---

## Integration with Pipeline

### Prism Pipeline

BifrostLib works with prismLib for pipeline detection:

```python
from prismLib.pipeline import detect_host_app

if detect_host_app() == "Maya":
    from mayaLib.bifrostLib import bifrost_api as bifrost
    # Use Bifrost API
```

### USD Export Workflow

1. Create Bifrost graph with `USDCharacterBuild`
2. Set frame range
3. Play timeline to cache USD
4. Export cached USD file

---

## See Also

- [MayaLib Home](Home.md)
- [PipelineLib](PipelineLib.md) - USD unit coordination
- [RigLib](RigLib.md) - Character rig setup

---

*Last updated: January 2026*

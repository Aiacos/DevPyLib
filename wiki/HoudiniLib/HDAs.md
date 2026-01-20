# HoudiniLib HDAs Documentation

This document provides detailed documentation for Houdini Digital Assets (HDAs) included in HoudiniLib.

---

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Available HDAs](#available-hdas)
- [Intersection Solver](#intersection-solver)
- [Creating Custom HDAs](#creating-custom-hdas)
- [Best Practices](#best-practices)

---

## Overview

Houdini Digital Assets (HDAs) are self-contained procedural tools that encapsulate complex node networks into reusable, shareable assets. HoudiniLib provides a collection of production-ready HDAs.

### HDA Location

```
houdiniLib/HDAs/
└── sop_unilo.Intersection_Solver.1.0.hdalc
```

### File Format

- `.hdalc` - Compiled HDA (non-commercial license compatible)
- `.hdanc` - Non-commercial HDA
- `.hda` - Standard HDA file

---

## Installation

### Method 1: Copy to OTL Scan Path

Copy HDAs to Houdini's standard OTL directory:

**Windows:**
```
%USERPROFILE%\Documents\houdini20.5\otls\
```

**Linux:**
```
~/houdini20.5/otls/
```

**macOS:**
```
~/Library/Preferences/houdini/20.5/otls/
```

### Method 2: Add Custom Scan Path

Add DevPyLib's HDA directory to Houdini's scan path:

**houdini.env:**
```
HOUDINI_OTLSCAN_PATH = "$HOUDINI_OTLSCAN_PATH;/path/to/DevPyLib/houdiniLib/HDAs"
```

### Method 3: Install via Python

```python
import hou

# Install HDA file
hda_path = "/path/to/DevPyLib/houdiniLib/HDAs/sop_unilo.Intersection_Solver.1.0.hdalc"
hou.hda.installFile(hda_path)

# Verify installation
definitions = hou.hda.definitionsInFile(hda_path)
for d in definitions:
    print(f"Installed: {d.nodeTypeName()}")
```

### Method 4: Session-based Loading

Load HDA only for current session:

```python
import hou

hda_path = "/path/to/DevPyLib/houdiniLib/HDAs/sop_unilo.Intersection_Solver.1.0.hdalc"
hou.hda.installFile(hda_path, oplibraries_file="Scanned Asset Library Directories")
```

---

## Available HDAs

| HDA Name | Version | Category | Description |
|----------|---------|----------|-------------|
| `sop_unilo.Intersection_Solver` | 1.0 | SOP | Intersection solving and resolution |

---

## Intersection Solver

### Overview

The Intersection Solver SOP analyzes and resolves intersections in polygon meshes.

### Node Information

| Property | Value |
|----------|-------|
| **Name** | `sop_unilo.Intersection_Solver` |
| **Version** | 1.0 |
| **Category** | SOP (Surface Operators) |
| **Author** | unilo |
| **File** | `sop_unilo.Intersection_Solver.1.0.hdalc` |

### Inputs

| Input | Required | Description |
|-------|----------|-------------|
| 1 | Yes | Primary geometry to analyze |
| 2 | Optional | Secondary geometry for intersection testing |

### Parameters

*Note: Refer to the HDA's built-in help for detailed parameter documentation.*

Common parameters may include:

| Parameter | Type | Description |
|-----------|------|-------------|
| Tolerance | Float | Distance threshold for intersection detection |
| Mode | Menu | Processing mode selection |
| Output | Menu | Output type selection |

### Usage

1. **Create node**:
   - Press Tab in SOP context
   - Search for "Intersection Solver"
   - Place node in network

2. **Connect inputs**:
   ```
   box1 ─────┐
             ├──► intersection_solver1
   sphere1 ──┘
   ```

3. **Configure parameters**:
   - Adjust tolerance for detection sensitivity
   - Select appropriate output mode

4. **View results**:
   - Enable display flag on the node
   - Check geometry spreadsheet for attributes

### Example Network

```
geo1/
├── box1
├── transform1
│   └── (offset the box)
├── sphere1
└── intersection_solver1
    ├── input1: box1
    └── input2: sphere1
```

### Python Usage

```python
import hou

# Get geometry node
geo = hou.node("/obj/geo1")

# Create intersection solver
solver = geo.createNode("sop_unilo::Intersection_Solver::1.0")

# Connect inputs
box = geo.node("box1")
sphere = geo.node("sphere1")

solver.setInput(0, box)
solver.setInput(1, sphere)

# Set parameters (example)
solver.parm("tolerance").set(0.001)

# Display
solver.setDisplayFlag(True)
solver.setRenderFlag(True)
```

---

## Creating Custom HDAs

### Guidelines for DevPyLib HDAs

When creating HDAs for HoudiniLib:

1. **Naming convention**: `sop_unilo.Name.version.hdalc`
2. **Include documentation**: Add help cards for all parameters
3. **Use namespacing**: Prefix with `unilo` or appropriate namespace
4. **Version properly**: Use semantic versioning (1.0, 1.1, 2.0)
5. **Test thoroughly**: Verify with various input types

### Creating an HDA

```python
import hou

# Select nodes to include in HDA
geo = hou.node("/obj/geo1")
nodes = [
    geo.node("node1"),
    geo.node("node2"),
    geo.node("node3")
]

# Create HDA
hda = geo.createNode("subnet")
for node in nodes:
    node.parent().copyItems([node], hda)

# Convert to HDA
hda.createDigitalAsset(
    name="sop_unilo::MyTool",
    hda_file_name="/path/to/output.hdalc",
    description="My Tool Description",
    min_num_inputs=1,
    max_num_inputs=2
)
```

### HDA Structure Best Practices

```
my_hda/
├── Parameters           # User-facing parameters
├── Input/Output        # Define inputs and outputs
├── Internal Network    # Node network
├── Help               # Documentation
└── Scripts            # Event callbacks
```

---

## Best Practices

### Organization

1. **Group by function**: Organize HDAs by category (SOP, OBJ, DOP, etc.)
2. **Version control**: Keep HDAs under version control
3. **Document changes**: Maintain changelog in HDA help

### Performance

1. **Optimize cook times**: Profile and optimize slow operations
2. **Use spare inputs**: For reference geometry that doesn't need cooking
3. **Cache appropriately**: Use cache SOPs for expensive operations

### Compatibility

1. **Test across versions**: Verify HDAs work in target Houdini versions
2. **Handle missing nodes**: Include fallbacks for optional dependencies
3. **Document requirements**: List any required plugins or licenses

### Documentation

1. **Write help cards**: Document every parameter
2. **Include examples**: Provide example networks in help
3. **Add tooltips**: Brief descriptions for parameters

---

## Troubleshooting

### HDA Not Found

**Problem**: HDA doesn't appear in Tab menu

**Solutions**:
1. Verify file exists in scan path
2. Check file permissions
3. Refresh asset library: **Assets > Refresh Asset Libraries**
4. Check Houdini console for errors

### Version Conflicts

**Problem**: Wrong HDA version loads

**Solutions**:
1. Check asset library order
2. Use explicit version in node name
3. Clear old versions from scan paths

### License Issues

**Problem**: HDA won't load due to license

**Solutions**:
1. Use `.hdalc` for non-commercial compatibility
2. Check HDA is built with appropriate license type
3. Verify Houdini license allows HDA usage

---

## See Also

- [HoudiniLib Home](Home.md)
- [DevPyLib Home](../Home.md)
- [Architecture](../Architecture.md)

---

*Last updated: January 2026*

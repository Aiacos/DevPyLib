# HoudiniLib Documentation

Welcome to the **HoudiniLib** documentation. HoudiniLib is the Houdini component of DevPyLib, providing utilities and Houdini Digital Assets (HDAs) for SideFX Houdini.

---

## Table of Contents

- [Overview](#overview)
- [Module Structure](#module-structure)
- [Current Status](#current-status)
- [Houdini Digital Assets](#houdini-digital-assets)
- [Integration with DevPyLib](#integration-with-devpylib)
- [Future Development](#future-development)

---

## Overview

HoudiniLib provides emerging support for Houdini workflows within the DevPyLib ecosystem. While MayaLib is the primary focus of DevPyLib, HoudiniLib offers Houdini Digital Assets and utilities for cross-DCC workflows.

### Key Features

- **Houdini Digital Assets (HDAs)**: Pre-built procedural tools
- **Cross-DCC compatibility**: Works with DevPyLib's multi-DCC detection
- **Pipeline integration**: Prism Pipeline support

### Module Structure

```
houdiniLib/
├── __init__.py        # Package initialization
└── HDAs/              # Houdini Digital Assets
    └── sop_unilo.Intersection_Solver.1.0.hdalc
```

---

## Current Status

HoudiniLib is in **emerging support** status. Current capabilities:

| Feature | Status |
|---------|--------|
| HDA library | Available |
| Python utilities | Planned |
| Pipeline integration | Available via prismLib |
| Documentation | In progress |

---

## Houdini Digital Assets

### Available HDAs

| HDA | Version | Description |
|-----|---------|-------------|
| `sop_unilo.Intersection_Solver` | 1.0 | Intersection solving SOP |

### HDA Location

HDAs are stored in:
```
houdiniLib/HDAs/
```

### Installing HDAs

1. **Copy to Houdini's HDA path**:
   ```
   $HOUDINI_USER_PREF_DIR/otls/
   ```

2. **Or add to HOUDINI_OTLSCAN_PATH**:
   ```bash
   export HOUDINI_OTLSCAN_PATH="$HOUDINI_OTLSCAN_PATH;/path/to/DevPyLib/houdiniLib/HDAs"
   ```

3. **Or install via Python**:
   ```python
   import hou
   hou.hda.installFile("/path/to/DevPyLib/houdiniLib/HDAs/sop_unilo.Intersection_Solver.1.0.hdalc")
   ```

### Using HDAs

Once installed, HDAs appear in Houdini's Tab menu under their category.

For the Intersection Solver:
1. Press Tab in the Network Editor
2. Search for "Intersection Solver"
3. Place the node
4. Connect geometry inputs
5. Configure parameters

---

## Integration with DevPyLib

### Host Application Detection

DevPyLib can detect when running in Houdini:

```python
from prismLib.pipeline import detect_host_app

host = detect_host_app()
if host == "Houdini":
    import hou
    # Run Houdini-specific code
```

### Cross-DCC Workflows

HoudiniLib is designed to work alongside MayaLib for cross-DCC workflows:

1. **Asset preparation** in Houdini (procedural modeling, simulation)
2. **Rigging and animation** in Maya (using MayaLib)
3. **Data exchange** via USD, Alembic, or FBX

---

## Intersection Solver HDA

### Description

The Intersection Solver SOP provides intersection analysis and resolution for polygon meshes.

### Node Category

**SOP** (Surface Operators)

### Parameters

See the HDA's internal documentation for parameter details.

### Usage Example

```
geo1/
├── mesh_input (geometry)
└── intersection_solver (SOP)
    └── output (resolved geometry)
```

---

## Python Integration

### Importing HoudiniLib

```python
import houdiniLib

# HoudiniLib utilities (when available)
```

### Working with Houdini's Python API

```python
import hou

# Get current scene
scene = hou.hipFile.name()

# Create geometry node
obj = hou.node("/obj")
geo = obj.createNode("geo", "procedural_geo")

# Add SOP nodes
box = geo.createNode("box")
```

---

## Future Development

Planned features for HoudiniLib:

### Planned Utilities

| Utility | Description | Status |
|---------|-------------|--------|
| Procedural modeling | Python tools for procedural mesh generation | Planned |
| VEX helpers | Python wrappers for VEX operations | Planned |
| Pipeline utilities | Houdini-specific pipeline tools | Planned |
| HDA builders | Programmatic HDA creation | Planned |

### Planned HDAs

| HDA | Description | Status |
|-----|-------------|--------|
| Character rigging | Procedural rigging tools | Planned |
| Simulation presets | Pre-configured simulation setups | Planned |
| USD utilities | USD stage manipulation tools | Planned |

---

## Best Practices

1. **Use HDAs for repeatable workflows**: Encapsulate procedures in HDAs
2. **Follow naming conventions**: Use descriptive names with version numbers
3. **Document parameters**: Include help text in HDAs
4. **Test cross-DCC compatibility**: Verify exports work in Maya
5. **Use Prism Pipeline**: For consistent project structure

---

## See Also

- [DevPyLib Home](../Home.md)
- [HDAs Documentation](HDAs.md)
- [Architecture](../Architecture.md) - Multi-DCC design
- [Cross-Platform](../Cross-Platform.md)

---

*Last updated: January 2026*

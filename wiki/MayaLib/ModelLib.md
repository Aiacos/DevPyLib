# ModelLib Documentation

ModelLib provides modeling utilities for Maya, including automated quad topology generation, UV tools, and display layer management.

---

## Table of Contents

- [Overview](#overview)
- [Module Structure](#module-structure)
- [Quad Patcher](#quad-patcher)
- [Display Layer Utilities](#display-layer-utilities)
- [Mesh Direct Connection](#mesh-direct-connection)
- [Usage Examples](#usage-examples)

---

## Overview

ModelLib focuses on mesh manipulation and optimization tasks commonly needed in production modeling workflows. The primary tool is the Quad Patcher, which automates quad topology generation.

### Module Structure

```
modelLib/
├── __init__.py
├── base/              # Base modeling classes
├── tools/
│   ├── __init__.py
│   └── quad_patcher.py   # Automated quad topology (~52K bytes)
└── utils/
    ├── __init__.py
    ├── display_layer.py         # Display layer management
    └── mesh_direct_connection.py # Mesh connection utilities
```

---

## Quad Patcher

The Quad Patcher is a comprehensive tool for automatic quad topology generation, useful for retopology workflows and mesh optimization.

### Features

- Automated quad patch generation from input geometry
- Configurable patch density and distribution
- Edge flow optimization
- Support for complex topology

### Location

```
mayaLib/modelLib/tools/quad_patcher.py
```

### Basic Usage

```python
from mayaLib.modelLib.tools import quad_patcher

# See the quad_patcher module for full API documentation
# The tool provides automated quad topology generation
```

---

## Display Layer Utilities

The display layer module provides utilities for managing Maya display layers.

### Location

```
mayaLib/modelLib/utils/display_layer.py
```

### Functions

```python
from mayaLib.modelLib.utils import display_layer

# Display layer management functions
# See module for full API
```

### Common Operations

| Operation | Description |
|-----------|-------------|
| Create layers | Create new display layers |
| Assign objects | Add objects to display layers |
| Toggle visibility | Show/hide layer contents |
| Set display type | Normal, template, or reference |

---

## Mesh Direct Connection

Utilities for creating direct mesh connections, useful for deformation workflows.

### Location

```
mayaLib/modelLib/utils/mesh_direct_connection.py
```

### Purpose

Direct mesh connections allow you to:
- Connect mesh attributes directly between nodes
- Bypass intermediate history
- Create efficient deformation pipelines

### Basic Usage

```python
from mayaLib.modelLib.utils import mesh_direct_connection

# Create direct connections between mesh attributes
# Useful for performance optimization in deformation chains
```

---

## Usage Examples

### Working with Display Layers

```python
import pymel.core as pm
from mayaLib.modelLib.utils import display_layer

# Create a display layer
layer = pm.createDisplayLayer(name="render_geo_layer", empty=True)

# Add objects to layer
geo = pm.ls("*_geo")
for obj in geo:
    pm.editDisplayLayerMembers(layer, obj)

# Set to reference mode (non-selectable)
layer.displayType.set(2)  # 0=normal, 1=template, 2=reference
```

### Mesh Connection Example

```python
import pymel.core as pm

# Create a direct mesh connection
source_mesh = pm.ls("source_mesh")[0]
target_mesh = pm.ls("target_mesh")[0]

# Connect outMesh to inMesh directly
source_shape = source_mesh.getShape()
target_shape = target_mesh.getShape()

pm.connectAttr(
    source_shape.outMesh,
    target_shape.inMesh,
    force=True
)
```

### Organizing Model Groups

```python
import pymel.core as pm

# Create standard model organization
model_grp = pm.group(name="model_GRP", empty=True)
render_grp = pm.group(name="render_GRP", empty=True, parent=model_grp)
proxy_grp = pm.group(name="proxy_GRP", empty=True, parent=model_grp)
collision_grp = pm.group(name="collision_GRP", empty=True, parent=model_grp)

# Create display layers for each
render_layer = pm.createDisplayLayer(name="render_layer")
proxy_layer = pm.createDisplayLayer(name="proxy_layer")
collision_layer = pm.createDisplayLayer(name="collision_layer")
```

---

## Integration with RigLib

ModelLib integrates with RigLib's model group structure:

```
model_GRP/
├── fastModel_GRP      # Low-res display models
├── mediumModel_GRP    # Medium-res models
├── mediumSlowModel_GRP
├── slowModel_GRP      # High-res models
├── allModel_GRP       # All resolution models
└── rigModel_GRP       # Rig-specific geometry (hidden)
```

### Example: Organizing Models for Rig

```python
import pymel.core as pm
from mayaLib.rigLib.base.module import Base

# Create base rig (creates model groups automatically)
rig = Base(character_name="character", scale=1.0)

# Parent geometry to appropriate groups
low_res = pm.ls("character_low_geo")[0]
med_res = pm.ls("character_med_geo")[0]
high_res = pm.ls("character_high_geo")[0]

pm.parent(low_res, rig.fast_model_group)
pm.parent(med_res, rig.medium_model_group)
pm.parent(high_res, rig.slow_model_group)
```

---

## Best Practices

1. **Use display layers** to organize different geometry types
2. **Set reference mode** on render geometry to prevent accidental selection
3. **Create proxy geometry** for animators to work with faster viewport performance
4. **Organize by LOD** (Level of Detail) using the standard model group hierarchy
5. **Use direct connections** sparingly - only when performance requires it

---

## See Also

- [MayaLib Home](Home.md)
- [RigLib](RigLib.md) - Model group integration
- [ShaderLib](ShaderLib.md) - For material assignment

---

*Last updated: January 2026*

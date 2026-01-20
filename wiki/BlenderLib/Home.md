# BlenderLib Documentation

Welcome to the **BlenderLib** documentation. BlenderLib is the Blender component of DevPyLib, providing utilities for Blender 3D workflows.

---

## Table of Contents

- [Overview](#overview)
- [Current Status](#current-status)
- [Module Structure](#module-structure)
- [Integration with DevPyLib](#integration-with-devpylib)
- [Future Development](#future-development)
- [Contributing](#contributing)

---

## Overview

BlenderLib provides support for Blender within the DevPyLib ecosystem. Currently in minimal support status, BlenderLib serves as a foundation for future Blender integration.

### Key Goals

- **Blender Python API utilities**: Simplify common Blender operations
- **Cross-DCC workflows**: Enable asset exchange between Blender and other DCCs
- **Consistent patterns**: Follow DevPyLib's architectural patterns

---

## Current Status

BlenderLib is in **minimal support** status.

| Feature | Status |
|---------|--------|
| Package structure | Available |
| Python utilities | Placeholder |
| Pipeline integration | Planned |
| Rigging tools | Planned |
| Modeling tools | Planned |

### Module Structure

```
blenderLib/
└── __init__.py        # Package initialization (placeholder)
```

---

## Integration with DevPyLib

### Host Application Detection

DevPyLib can detect Blender through prismLib:

```python
from prismLib.pipeline import detect_host_app

host = detect_host_app()
if host == "Blender":
    import bpy
    # Run Blender-specific code
```

*Note: Blender detection may require additional implementation in prismLib.*

### Cross-DCC Workflows

BlenderLib is designed for cross-DCC workflows:

1. **Export from Blender**: USD, Alembic, FBX
2. **Import to Maya**: Use MayaLib for rigging/animation
3. **Round-trip**: Import animated rigs back to Blender

---

## Blender Python Basics

### Blender API Overview

Blender uses Python as its scripting language:

```python
import bpy

# Get active object
obj = bpy.context.active_object

# Create a cube
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))

# Get all mesh objects
meshes = [obj for obj in bpy.data.objects if obj.type == 'MESH']
```

### Common Operations

#### Creating Objects

```python
import bpy

# Create a new mesh
mesh = bpy.data.meshes.new("MyMesh")
obj = bpy.data.objects.new("MyObject", mesh)

# Link to scene
bpy.context.collection.objects.link(obj)
```

#### Creating Materials

```python
import bpy

# Create material
mat = bpy.data.materials.new(name="MyMaterial")
mat.use_nodes = True

# Assign to object
obj.data.materials.append(mat)
```

#### Creating Armatures

```python
import bpy

# Create armature
armature = bpy.data.armatures.new("MyArmature")
armature_obj = bpy.data.objects.new("MyRig", armature)

# Link to scene
bpy.context.collection.objects.link(armature_obj)

# Enter edit mode to add bones
bpy.context.view_layer.objects.active = armature_obj
bpy.ops.object.mode_set(mode='EDIT')

# Add bone
bone = armature.edit_bones.new("bone1")
bone.head = (0, 0, 0)
bone.tail = (0, 1, 0)

bpy.ops.object.mode_set(mode='OBJECT')
```

---

## Future Development

### Planned Modules

| Module | Description | Priority |
|--------|-------------|----------|
| `rigLib` | Rigging utilities | High |
| `modelLib` | Modeling utilities | Medium |
| `shaderLib` | Shader utilities | Medium |
| `animLib` | Animation utilities | Medium |
| `pipelineLib` | Pipeline utilities | Low |

### Planned Features

#### Rigging (rigLib)

- Control creation utilities
- Constraint helpers
- IK/FK systems
- Armature manipulation

#### Modeling (modelLib)

- UV utilities
- Mesh manipulation
- Procedural modeling helpers

#### Shading (shaderLib)

- Node-based shader creation
- Material assignment utilities
- Texture management

#### Animation (animLib)

- Keyframe utilities
- Animation baking
- Motion capture import

### Planned Integrations

| Integration | Description |
|-------------|-------------|
| USD | Universal Scene Description support |
| Alembic | Geometry caching |
| FBX | Game engine exchange |
| Prism Pipeline | Pipeline management |

---

## Contributing

BlenderLib welcomes contributions. Areas where help is needed:

### High Priority

1. **Rigging utilities**: Port MayaLib patterns to Blender
2. **Pipeline detection**: Add Blender support to prismLib
3. **USD integration**: Blender USD import/export helpers

### How to Contribute

1. Fork the DevPyLib repository
2. Create a feature branch
3. Implement functionality following DevPyLib patterns
4. Add documentation
5. Submit a pull request

### Code Style

Follow DevPyLib conventions:
- Use type hints
- Write Google-style docstrings
- Use Black formatting
- Follow PEP 8 naming

### Example Module Structure

```python
"""Blender rigging utilities.

Provides tools for creating and manipulating armatures
and rig controls in Blender.
"""

__author__ = "Your Name"

import bpy


class Control:
    """Build rig controls in Blender.

    Similar to MayaLib's Control class but for Blender.
    """

    def __init__(self, name="control", size=1.0):
        """Initialize the control.

        Args:
            name: Control name
            size: Control size
        """
        self.name = name
        self.size = size
        self.obj = self._create_control()

    def _create_control(self):
        """Create the control curve."""
        # Implementation here
        pass
```

---

## Comparison with MayaLib

| Feature | MayaLib | BlenderLib |
|---------|---------|------------|
| Rigging | Full support | Planned |
| Animation | BVH importer | Planned |
| Modeling | Quad patcher | Planned |
| Shading | Multi-renderer | Planned |
| Fluids | Maya fluids | N/A |
| USD | Bifrost integration | Planned |
| UI | FunctionUI | Planned |

---

## Resources

### Blender Python Documentation

- [Blender Python API](https://docs.blender.org/api/current/)
- [Blender Development](https://developer.blender.org/)
- [Blender Stack Exchange](https://blender.stackexchange.com/)

### Learning Resources

- Blender's built-in Python console
- Scripting workspace in Blender
- Templates in Text Editor > Templates > Python

---

## See Also

- [DevPyLib Home](../Home.md)
- [MayaLib](../MayaLib/Home.md) - Reference implementation
- [Architecture](../Architecture.md) - Design patterns
- [Contributing](../Contributing.md) - Contribution guide

---

*Last updated: January 2026*

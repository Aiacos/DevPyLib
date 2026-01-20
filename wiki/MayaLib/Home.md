# MayaLib Documentation

Welcome to the **MayaLib** documentation. MayaLib is the primary component of DevPyLib, providing comprehensive utilities for Autodesk Maya with approximately 28,000 lines of code covering rigging, animation, modeling, shading, fluid simulation, and pipeline tools.

---

## Table of Contents

- [Overview](#overview)
- [Module Structure](#module-structure)
- [Quick Navigation](#quick-navigation)
- [Getting Started](#getting-started)
- [API Conventions](#api-conventions)

---

## Overview

MayaLib is designed for production use in VFX and animation studios. It uses **PyMEL** (`pymel.core`) as the primary Maya API interface and Qt (PySide2/PySide6) for UI components.

### Key Design Principles

1. **Modular Architecture**: Each submodule can be used independently
2. **Consistent Naming**: Rig objects use standardized suffixes (`_GRP`, `_CTRL`, `_LOC`, `_JNT`)
3. **Professional Hierarchy**: Standardized rig structures for production workflows
4. **Introspective UI**: Automatic UI generation from function signatures
5. **Cross-Platform**: Full compatibility with Windows, Linux, and macOS

---

## Module Structure

```
mayaLib/
├── rigLib/           # Character rigging utilities
│   ├── base/         # Base classes (module, limb, spine, face, neck, ik_chain)
│   ├── utils/        # 31+ utility modules (control, joint, deform, skin, etc.)
│   ├── AdonisFX/     # AdonisFX muscle integration
│   ├── Ziva/         # Ziva Dynamics integration
│   ├── cloth/        # Cloth simulation utilities
│   └── matrix/       # Matrix-based rigging
├── animationLib/     # Animation tools
│   └── bvh_importer.py
├── modelLib/         # Modeling utilities
│   ├── base/         # Base modeling classes
│   ├── tools/        # Quad patcher, etc.
│   └── utils/        # Display layers, mesh connections
├── shaderLib/        # Shader creation
│   ├── base/         # Renderer-specific shaders (Arnold, RenderMan, 3Delight)
│   └── utils/        # Texture utilities
├── fluidLib/         # Fluid simulation
│   ├── base/         # Base fluid, container, emitter classes
│   └── utility/      # Fluid utilities
├── bifrostLib/       # Bifrost/USD integration
├── guiLib/           # UI framework
│   ├── base/         # FunctionUI, menu, shelf
│   └── utils/        # UI utilities
├── pipelineLib/      # Pipeline utilities
│   └── utility/      # Naming, conventions, workspace
├── lunaLib/          # Luna rigging framework integration
│   ├── bridge/       # Bridge utilities
│   ├── components/   # Luna components
│   ├── functions/    # Luna functions
│   └── tools/        # Luna tools
├── lookdevLib/       # Look development utilities
│   └── render/       # Render utilities
├── usdLib/           # USD utilities
├── plugin/           # Maya Python API 2.0 plugins
├── utility/          # General utilities
├── test/             # Integration test scripts
├── icons/            # UI icons
└── MEL/              # MEL script utilities
```

---

## Quick Navigation

### Core Modules

| Module | Description | Documentation |
|--------|-------------|---------------|
| **rigLib** | Character rigging system | [RigLib Documentation](RigLib.md) |
| **animationLib** | Animation tools | [AnimationLib Documentation](AnimationLib.md) |
| **modelLib** | Modeling utilities | [ModelLib Documentation](ModelLib.md) |
| **shaderLib** | Shader/lookdev tools | [ShaderLib Documentation](ShaderLib.md) |
| **fluidLib** | Fluid simulation | [FluidLib Documentation](FluidLib.md) |
| **bifrostLib** | Bifrost/USD integration | [BifrostLib Documentation](BifrostLib.md) |
| **guiLib** | UI framework | [GuiLib Documentation](GuiLib.md) |
| **pipelineLib** | Pipeline utilities | [PipelineLib Documentation](PipelineLib.md) |
| **lunaLib** | Luna integration | [LunaLib Documentation](LunaLib.md) |

### Getting Started

For installation and setup instructions, see [Getting Started](Getting-Started.md).

---

## Getting Started

### Basic Import

```python
# Import the entire library
import mayaLib

# Import specific modules
from mayaLib.rigLib.base.module import Base, Module
from mayaLib.rigLib.utils.control import Control
from mayaLib.shaderLib.shader import TextureShader
from mayaLib.fluidLib.smoke import WispySmoke
```

### Creating a Basic Rig

```python
from mayaLib.rigLib.base.module import Base, Module
from mayaLib.rigLib.utils.control import Control

# Create base rig structure
base_rig = Base(character_name="myCharacter", scale=1.0)

# Access the created groups
print(base_rig.top_group)          # myCharacter_rig_GRP
print(base_rig.model_group)        # model_GRP
print(base_rig.joints_group)       # skeleton_GRP
print(base_rig.modules_group)      # modules_GRP

# Create a module for a specific body part
arm_module = Module(prefix="arm", base_obj=base_rig)

# Create a custom control
arm_ctrl = Control(
    prefix="l_arm",
    scale=1.0,
    translate_to="l_arm_JNT",
    rotate_to="l_arm_JNT",
    shape="circleX",
    lock_channels=["s", "v"],
    do_offset=True,
    do_modify=True
)
```

### Using the Menu System

After installation, the MayaLib menu appears in Maya's main menu bar:

1. Click **MayaLib** in the menu bar
2. Use the search bar to find functions by name
3. Click a function to open its auto-generated UI
4. Use the ">" button to populate fields from Maya selection
5. Toggle "Advanced" to show optional parameters

---

## API Conventions

### Naming Conventions

MayaLib uses consistent naming conventions for rig objects:

| Suffix | Description | Example |
|--------|-------------|---------|
| `_GRP` | Group node | `arm_GRP`, `model_GRP` |
| `_CTRL` | Control curve | `arm_CTRL`, `main_CTRL` |
| `_JNT` | Joint | `arm_JNT`, `shoulder_JNT` |
| `_LOC` | Locator | `target_LOC`, `pole_LOC` |
| `_IKH` | IK Handle | `arm_IKH` |

### Color Coding

Controls are automatically colored based on their prefix:
- **Left side** (`l_`): Blue (color index 6)
- **Right side** (`r_`): Red (color index 13)
- **Center**: Yellow (color index 22)

### PyMEL Usage

MayaLib uses PyMEL (`pymel.core as pm`) as the standard API interface:

```python
import pymel.core as pm

# Create nodes using PyMEL
joint = pm.joint(name="arm_JNT")
group = pm.group(name="arm_GRP", empty=True)

# Access attributes
joint.translateX.set(5)
value = joint.rotateY.get()

# Connections
pm.connectAttr(ctrl.rotate, joint.rotate)
```

### Qt UI Pattern

UI components use PySide2/PySide6 with automatic fallback:

```python
try:
    from PySide6 import QtCore, QtWidgets
except ImportError:
    from PySide2 import QtCore, QtWidgets
```

---

## Standard Rig Hierarchy

MayaLib creates a standardized rig hierarchy:

```
{character}_rig_GRP/
├── global_CTRL
│   └── main_CTRL
│       ├── rig_GRP/
│       │   └── parts_GRP/
│       ├── skeleton_GRP/
│       └── modules_GRP/
│           └── {prefix}Module_GRP/
│               ├── {prefix}Controls_GRP
│               ├── {prefix}secondaryControls_GRP
│               ├── {prefix}Joints_GRP
│               ├── {prefix}Parts_GRP
│               └── {prefix}PartsNoTrans_GRP
└── model_GRP/
    ├── fastModel_GRP
    ├── mediumModel_GRP
    ├── mediumSlowModel_GRP
    ├── slowModel_GRP
    ├── allModel_GRP
    └── rigModel_GRP
```

---

## Further Reading

- [Getting Started](Getting-Started.md) - Installation and setup
- [RigLib](RigLib.md) - Complete rigging documentation
- [Architecture](../Architecture.md) - Design patterns and code organization
- [API Reference](../API-Reference.md) - Full API documentation

---

*Last updated: January 2026*

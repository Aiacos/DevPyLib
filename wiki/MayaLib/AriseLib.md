# AriseLib Documentation

AriseLib is an integration library for the Arise rigging system within MayaLib, providing utilities for setting up production-ready character rigs with HumanIK support, display layers, selection sets, and face rig integration.

---

## Table of Contents

- [Overview](#overview)
- [Base Classes](#base-classes)
- [Initialization Process](#initialization-process)
- [Display Layer Management](#display-layer-management)
- [Selection Sets](#selection-sets)
- [HumanIK Integration](#humanik-integration)
- [Face Rig Integration](#face-rig-integration)
- [Utility Methods](#utility-methods)
- [Examples](#examples)
- [Best Practices](#best-practices)
- [See Also](#see-also)

---

## Overview

AriseLib provides a streamlined workflow for integrating the Arise rigging system with Maya production pipelines. It automates common rigging setup tasks including display layer creation, selection set organization, HumanIK configuration, and face rig connections.

### Module Structure

```
ariseLib/
├── __init__.py    # Module initialization
└── base.py        # BaseRig class and utilities
```

### Key Features

- **Automated Display Layers**: Creates organized display layers for anatomy systems (skeleton, muscle, organs, etc.)
- **Selection Set Management**: Generates standardized selection sets for controls, meshes, and joints
- **HumanIK Integration**: Automatic HumanIK character definition setup with optional T-pose
- **Face Rig Support**: Integration with Advanced Skeleton face rig components
- **Delta Mush Scaling**: Automatic scale connections for delta mush deformers
- **Purpose-Based Visibility**: Driven key setup for render/proxy/guide visibility switching

---

## Base Classes

### BaseRig Class (`base.py::BaseRig`)

The `BaseRig` class is the core of AriseLib, providing methods for setting up display layers, connecting controls, and managing rig components.

```python
from mayaLib.ariseLib.base import BaseRig

# Create base rig setup
rig = BaseRig(
    character_name="Male_Human",  # Name prefix for character
    do_human_ik=True,             # Enable HumanIK setup
    auto_t_pose=False             # Auto-set T-pose for HumanIK
)
```

#### Constructor Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `character_name` | str | "Male_Human" | Name identifier for the character |
| `do_human_ik` | bool | True | Whether to set up HumanIK |
| `auto_t_pose` | bool | False | Whether to automatically set T-pose for HumanIK |

#### Class Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `character_name` | str | The character name for naming conventions |
| `do_human_ik` | bool | HumanIK setup flag |
| `auto_t_pose` | bool | T-pose auto-setup flag |
| `main_set` | PyNode | Main character selection set |

---

## Initialization Process

When a `BaseRig` instance is created, the following setup steps are executed automatically in order:

1. **Connect Purpose**: Links purpose attribute to visibility controls
2. **Geometry Display Setup**: Configures display overrides for geometry
3. **Selection Sets Creation**: Creates organized selection sets
4. **Display Layers Setup**: Creates display layers for guide components
5. **Delta Mush Setup**: Connects scale attributes to delta mush nodes
6. **Face Rig Setup**: Configures Advanced Skeleton face rig connections
7. **Skin Cluster Rename**: Renames skin clusters descriptively
8. **HumanIK Setup**: Initializes HumanIK (if enabled)

---

## Display Layer Management

### create_display_layer()

Creates a display layer with automatic color coding based on layer name.

```python
from mayaLib.ariseLib.base import BaseRig

rig = BaseRig(character_name="myCharacter", do_human_ik=False)

# Create a display layer for skeleton
skeleton_layer = rig.create_display_layer(
    obj_list=["joint1", "joint2", "joint3"],
    layer_name="skeleton",
    idx=0
)
```

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `obj_list` | list | - | List of objects to add to the layer |
| `layer_name` | str | - | Name of the display layer |
| `idx` | int | 0 | Display layer index |

#### Automatic Color Mapping

The method automatically assigns colors and visibility based on the layer name:

| Layer Name Contains | Color Index | Default Visibility |
|--------------------|-------------|-------------------|
| `skeleton` | 25 | Visible |
| `muscle` | 4 | Hidden |
| `organs` | 24 | Hidden |
| `lymphatic` | 28 | Hidden |
| `ligaments` | 30 | Hidden |
| `heart` | 12 | Hidden |
| `veins` | 8 | Hidden |
| `arteries` | 12 | Hidden |
| `nervous_system` | 29 | Hidden |
| `hair` | 0 | Hidden |

### Supported Guide Groups

The system automatically creates display layers for these guide children:

```
guide/
├── skeleton_grp
├── muscle_grp
├── secondary_muscle_grp
├── ligaments_grp
├── heart_grp
├── organs_grp
├── arteries_grp
├── veins_grp
├── lymphatic_grp
├── nervous_system_grp
└── hair_grp
```

---

## Selection Sets

### Created Selection Sets

The `BaseRig` class automatically creates a hierarchy of selection sets:

```
{character_name}_character_set/
├── ctrls_set/
│   ├── body_ctrls_set       # All *_ctrl nodes
│   └── face_ctrls_set       # Face controls (empty by default)
├── model_set/
│   ├── render_model_set     # Objects under "render" group
│   ├── proxy_model_set      # Objects under "proxy" group
│   └── guide_model_set      # Objects under "guide" group
├── joint_set/
│   ├── body_joint_set       # All body joints
│   └── face_joint_set       # Face joints (empty by default)
└── skeletalMesh_set         # Combined render geo and joints
```

### _create_selection_set()

Helper method to create individual selection sets.

```python
# Internal method usage
obj_set = rig._create_selection_set(
    name="custom_set",
    members=["obj1", "obj2", "obj3"],
    parent="parent_set"  # Optional
)
```

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | str | - | Name of the selection set |
| `members` | list | - | List of objects to add |
| `parent` | str/None | None | Optional parent set |

---

## HumanIK Integration

### Automatic HumanIK Setup

When `do_human_ik=True`, the system:

1. Optionally sets T-pose for arm controls (if `auto_t_pose=True`)
2. Creates a HumanIK character definition named `{character_name}_HIK`

```python
from mayaLib.ariseLib.base import BaseRig

# Create rig with HumanIK
rig = BaseRig(
    character_name="hero",
    do_human_ik=True,
    auto_t_pose=True  # Arms will be set parallel to grid
)
# Creates "hero_HIK" HumanIK character
```

### Expected Arm Control Names

For T-pose setup, the system looks for these control names:

**Left Arm:**
- `L_Arm_base_ctrl`
- `L_Arm_fk_root_ctrl`
- `L_Arm_fk_mid_ctrl`
- `L_Arm_fk_tip_ctrl`

**Right Arm:**
- `R_Arm_base_ctrl`
- `R_Arm_fk_root_ctrl`
- `R_Arm_fk_mid_ctrl`
- `R_Arm_fk_tip_ctrl`

---

## Face Rig Integration

### Advanced Skeleton Face Rig Support

The `BaseRig` class provides integration with Advanced Skeleton face rigs:

#### Eye Aim Setup

```python
# Automatic connections when these objects exist:
# - AimEye_M: Middle eye aim target
# - AimEye_L: Left eye aim target
# - AimEye_R: Right eye aim target

# Connected to:
# - M_Eyes_Aim_01_ctrl (or fallback to head joint)
# - L_Eye_eye_aim_at_ctrl
# - R_Eye_eye_aim_at_ctrl
```

#### Face Joint Setup

When `FaceJoint_M` and `M_Head_head_FS_jnt` exist:

1. Parents `FaceJoint_M` under `M_Head_head_FS_jnt`
2. Creates parent constraints for:
   - `FaceMotionSystem`
   - `FaceDeformationFollowHead`
   - `LipFollowHead`
3. Sets up scale connections via `MainAndHeadScaleMultiplyDivide`

---

## Utility Methods

### connect_purpose()

Connects a purpose attribute to control visibility of render/proxy/guide groups using set driven keys.

```python
from mayaLib.ariseLib.base import BaseRig

rig = BaseRig(character_name="myCharacter", do_human_ik=False)

# Connect purpose attribute
rig.connect_purpose(
    source="Base_main_ctrl",
    destination_list=["render", "proxy", "guide"]
)
```

#### Purpose Values

| Purpose Value | Render Visibility | Proxy Visibility | Guide Visibility |
|--------------|------------------|-----------------|-----------------|
| 0 | Hidden | Visible | Hidden |
| 1 | Visible | Hidden | Hidden |
| 2 | Hidden | Hidden | Visible |

### Delta Mush Scale Connection

Automatically connects `Base_main_ctrl.scale` to all delta mush nodes in the scene:

```python
# Internal method - called during initialization
# Connects: Base_main_ctrl.scale -> deltaMush.scale
```

### Skin Cluster Renaming

Renames all skin clusters to follow the pattern `{geometry_name}_skinCluster`:

```python
# Before: skinCluster1, skinCluster2
# After:  body_skinCluster, head_skinCluster
```

---

## Examples

### Basic Rig Setup

```python
import pymel.core as pm
from mayaLib.ariseLib.base import BaseRig

# Ensure required scene objects exist
# - Base_main_ctrl (main control)
# - geo (geometry group)
# - render, proxy, guide (purpose groups)
# - Base_main_FS_jnt (root joint)

# Create rig setup
rig = BaseRig(
    character_name="hero_character",
    do_human_ik=True,
    auto_t_pose=False
)

# Access the main selection set
print(f"Main set: {rig.main_set}")
print(f"Character: {rig.character_name}")
```

### Custom Display Layer Creation

```python
import pymel.core as pm
from mayaLib.ariseLib.base import BaseRig

# Create rig instance
rig = BaseRig(character_name="character", do_human_ik=False)

# Create custom display layers
muscle_objs = pm.ls("*_muscle_*", type="mesh")
muscle_layer = rig.create_display_layer(
    obj_list=muscle_objs,
    layer_name="custom_muscle",
    idx=1
)

# Manually adjust layer settings
pm.setAttr(f"{muscle_layer}.visibility", 1)
pm.setAttr(f"{muscle_layer}.displayType", 2)  # Reference mode
```

### Purpose Switching Example

```python
import pymel.core as pm
from mayaLib.ariseLib.base import BaseRig

# Setup purpose switching
rig = BaseRig(character_name="myChar", do_human_ik=False)

# Now you can switch between purposes via the control attribute:
# Set purpose to 0: Show proxy (fast viewport)
pm.setAttr("Base_main_ctrl.purpose", 0)

# Set purpose to 1: Show render (final quality)
pm.setAttr("Base_main_ctrl.purpose", 1)

# Set purpose to 2: Show guide (anatomy reference)
pm.setAttr("Base_main_ctrl.purpose", 2)
```

### HumanIK with T-Pose

```python
import pymel.core as pm
from mayaLib.ariseLib.base import BaseRig

# Create rig with automatic T-pose
rig = BaseRig(
    character_name="motion_capture_char",
    do_human_ik=True,
    auto_t_pose=True  # Arms will be aligned parallel to world grid
)

# The HumanIK character "motion_capture_char_HIK" is now ready
# for motion capture retargeting
```

---

## Best Practices

1. **Name Your Objects Consistently**: The system expects specific naming conventions:
   - Controls: `*_ctrl`
   - Joints: `*_jnt`
   - Geometry: `*_geo`
   - Groups: `*_grp`

2. **Set Up Scene Structure First**: Ensure these groups exist before initialization:
   - `Base_main_ctrl` - Main control with purpose attribute
   - `geo` - Geometry container
   - `render`, `proxy`, `guide` - Purpose groups
   - `Base_main_FS_jnt` - Root joint

3. **Use Purpose Switching**: Leverage the purpose attribute for:
   - Proxy mode during animation blocking
   - Render mode for final output
   - Guide mode for anatomy reference

4. **Selection Sets for Export**: Use the auto-generated selection sets for:
   - Game engine export (`skeletalMesh_set`)
   - Animation export (`joint_set`)
   - Cloth simulation (`model_set`)

5. **HumanIK Considerations**:
   - Enable `auto_t_pose` only if your rig supports FK arm controls
   - Use consistent naming for HumanIK to work with motion capture data

6. **Display Layer Organization**: The automatic color coding helps quickly identify:
   - Yellow: Skeleton (visible)
   - Magenta: Muscles (hidden by default)
   - Various colors: Organs, veins, etc.

---

## See Also

- [RigLib Documentation](RigLib.md) - Core rigging utilities
- [HumanIK Utilities](RigLib.md#humanik) - HumanIK integration details
- [MayaLib Home](Home.md) - Library overview
- [Architecture](../Architecture.md) - System architecture

---

*Last updated: February 2026*

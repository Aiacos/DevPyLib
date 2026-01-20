# RigLib Documentation

RigLib is the character rigging library within MayaLib, providing professional-grade utilities for creating production-ready character rigs in Maya.

---

## Table of Contents

- [Overview](#overview)
- [Base Classes](#base-classes)
- [Control System](#control-system)
- [Utility Modules](#utility-modules)
- [Limb Rigging](#limb-rigging)
- [Spine and Neck](#spine-and-neck)
- [Face Rigging](#face-rigging)
- [Deformers](#deformers)
- [Skin Utilities](#skin-utilities)
- [External Integrations](#external-integrations)
- [Examples](#examples)

---

## Overview

RigLib follows a modular architecture with foundational base classes that create standardized rig hierarchies. All rig modules inherit from these base classes, ensuring consistent structure across all rigs.

### Module Structure

```
rigLib/
├── base/
│   ├── module.py      # Base and Module classes
│   ├── limb.py        # Limb rig (arms, legs)
│   ├── spine.py       # Spine rig
│   ├── neck.py        # Neck rig
│   ├── face.py        # Face rig
│   └── ik_chain.py    # Generic IK chain
├── utils/             # 31+ utility modules
│   ├── control.py     # Control creation
│   ├── joint.py       # Joint utilities
│   ├── deform.py      # Deformer utilities
│   ├── skin.py        # Skin cluster utilities
│   └── ...
├── AdonisFX/          # AdonisFX muscle integration
├── Ziva/              # Ziva Dynamics integration
├── cloth/             # Cloth simulation
└── matrix/            # Matrix-based rigging
```

---

## Base Classes

### Base Class (`module.py::Base`)

The `Base` class creates the top-level rig structure with global controls.

```python
from mayaLib.rigLib.base.module import Base

# Create base rig structure
rig = Base(
    character_name="myCharacter",  # Name prefix for all nodes
    scale=1.0,                      # Uniform scale for controls
    main_ctrl_attach_obj=""         # Optional attachment point
)
```

#### Created Hierarchy

```
{character}_rig_GRP/
├── global_CTRL                 # World-space control
│   └── main_CTRL               # Main character control
│       ├── rig_GRP/
│       │   ├── scale_LOC       # Scale reference locator
│       │   └── parts_GRP/
│       ├── skeleton_GRP/       # All joints go here
│       └── modules_GRP/        # All rig modules go here
├── rigctrl_GRP/
│   ├── halo_CTRL               # Halo selection aid
│   ├── display_CTRL            # Visibility controls
│   └── ikfk_CTRL               # IK/FK switch display
└── model_GRP/
    ├── fastModel_GRP           # Fast display level
    ├── mediumModel_GRP         # Medium display level
    ├── mediumSlowModel_GRP     # Medium-slow display level
    ├── slowModel_GRP           # Slow display level
    ├── allModel_GRP            # All models
    └── rigModel_GRP            # Rig-specific models (hidden)
```

#### Base Class Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `top_group` | PyNode | Top-level rig group |
| `global_control` | Control | Global control object |
| `main_control` | Control | Main control object |
| `model_group` | PyNode | Model container group |
| `rig_group` | PyNode | Rig components group |
| `joints_group` | PyNode | Skeleton joints group |
| `modules_group` | PyNode | Rig modules group |
| `scale_locator` | PyNode | Scale reference locator |
| `display_control` | Control | Display control object |
| `ikfk_control` | Control | IK/FK display control |

#### Base Class Methods

```python
# Get the scale locator (for world-space scale reference)
scale_loc = rig.get_scale_locator()

# Get the display control
display_ctrl = rig.get_display_control()
```

### Module Class (`module.py::Module`)

The `Module` class creates per-module groups under the base rig.

```python
from mayaLib.rigLib.base.module import Base, Module

# Create base rig
rig = Base(character_name="myCharacter", scale=1.0)

# Create a module for an arm
arm_module = Module(prefix="l_arm", base_obj=rig)
```

#### Module Hierarchy

```
{prefix}Module_GRP/
├── {prefix}Controls_GRP          # Primary controls
├── {prefix}secondaryControls_GRP # Secondary/detail controls
├── {prefix}Joints_GRP            # Module joints
├── {prefix}Parts_GRP             # Helper objects (hidden)
└── {prefix}PartsNoTrans_GRP      # Non-inheriting parts (hidden)
```

#### Module Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `top_group` | PyNode | Module top group |
| `controls_group` | PyNode | Primary controls group |
| `secondary_controls_group` | PyNode | Secondary controls group |
| `joints_group` | PyNode | Module joints group |
| `parts_group` | PyNode | Parts group (hidden) |
| `parts_no_trans_group` | PyNode | Non-inherit transform parts |

---

## Control System

### Control Class (`utils/control.py::Control`)

The `Control` class is central to all rigging, creating controls with consistent hierarchy.

```python
from mayaLib.rigLib.utils.control import Control

# Create a basic control
ctrl = Control(
    prefix="l_arm",           # Name prefix
    scale=1.0,                # Control size
    translate_to="l_arm_JNT", # Position reference
    rotate_to="l_arm_JNT",    # Orientation reference
    parent="controls_GRP",    # Parent node
    shape="circleX",          # Control shape
    lock_channels=["s", "v"], # Channels to lock
    do_offset=True,           # Create offset group
    do_modify=True,           # Create modify group
    do_dynamic_pivot=False    # Create dynamic pivot
)
```

#### Control Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `prefix` | str | "new" | Name prefix for nodes |
| `scale` | float | 1.0 | Control curve scale |
| `translate_to` | str | "" | Object to match position |
| `rotate_to` | str | "" | Object to match rotation |
| `parent` | str | "" | Parent node |
| `shape` | str | "circle" | Control shape type |
| `lock_channels` | list | ["s", "v"] | Channels to lock |
| `do_offset` | bool | True | Create offset group |
| `do_modify` | bool | False | Create modify group |
| `do_dynamic_pivot` | bool | False | Create dynamic pivot |

#### Available Shapes

| Shape Name | Description |
|------------|-------------|
| `circle`, `circleX` | Circle in X axis |
| `circleY` | Circle in Y axis |
| `circleZ` | Circle in Z axis |
| `sphere` | 3D sphere shape |
| `move` | Translation arrows |
| `spine` | Trapezium shape for spine |
| `chest` | Chest control shape |
| `hip` | Hip control shape |
| `head` | Head control shape |
| `display` | Display control shape |
| `ikfk` | IK/FK switch shape |

#### Control Methods

```python
# Get control components
control_node = ctrl.get_control()    # The control curve
offset_grp = ctrl.get_offset_grp()   # Offset group (for constraints)
modify_grp = ctrl.get_modify_grp()   # Modify group (for adjustments)
top_node = ctrl.get_top()            # Top-most node in hierarchy

# Get control scale
scale = ctrl.get_ctrl_scale()
```

#### Control Hierarchy

```
{prefix}Offset_GRP      # Constrained group (if do_offset=True)
└── {prefix}Modify_GRP  # Adjustment group (if do_modify=True)
    └── {prefix}_CTRL   # The actual control curve
```

#### Color Coding

Controls are automatically colored:
- `l_` prefix: Blue (color index 6)
- `r_` prefix: Red (color index 13)
- Other: Yellow (color index 22)

### Control Shapes (`utils/ctrl_shape.py`)

Custom control shape creation functions:

```python
from mayaLib.rigLib.utils import ctrl_shape as ctrl_shape_lib

# Create various control shapes
sphere_ctrl = ctrl_shape_lib.sphereCtrlShape(name="sphere_CTRL", scale=1.0)
move_ctrl = ctrl_shape_lib.moveCtrlShape(name="move_CTRL", scale=1.0)
chest_ctrl = ctrl_shape_lib.chestCtrlShape(name="chest_CTRL", scale=1.0)
hip_ctrl = ctrl_shape_lib.hipCtrlShape(name="hip_CTRL", scale=1.0)
head_ctrl = ctrl_shape_lib.headCtrlShape(name="head_CTRL", scale=1.0)
```

---

## Utility Modules

RigLib includes 31+ utility modules for various rigging tasks:

### Joint Utilities (`utils/joint.py`)

```python
from mayaLib.rigLib.utils import joint

# Joint creation and manipulation utilities
# See source for full API
```

### Transform Utilities (`utils/transform.py`)

```python
from mayaLib.rigLib.utils import transform

# Transform matching and manipulation
# See source for full API
```

### Common Utilities (`utils/common.py`)

```python
from mayaLib.rigLib.utils import common

# Freeze transforms
common.freeze_transform(node)

# Center pivot
common.center_pivot(node)

# Set driven keys
common.set_driven_key(
    driver_attr="ctrl.attr",
    driver_values=[0, 1, 2],
    driven_attr="target.attr",
    driven_values=[0, 0.5, 1]
)
```

### Pole Vector (`utils/pole_vector.py`)

```python
from mayaLib.rigLib.utils import pole_vector

# Calculate pole vector position for IK
# Creates pole vector control with proper placement
```

### IK/FK Switch (`utils/ikfk_switch.py`)

```python
from mayaLib.rigLib.utils import ikfk_switch

# IK/FK blending utilities
# Constraint weight switching
```

### Foot Roll (`utils/foot_roll.py`)

```python
from mayaLib.rigLib.utils import foot_roll

# Reverse foot setup
# Ball, toe, heel pivots
```

### HumanIK (`utils/human_ik.py`)

```python
from mayaLib.rigLib.utils import human_ik

# HumanIK integration
# Character definition setup
```

---

## Limb Rigging

### Limb Class (`base/limb.py::Limb`)

Complete IK/FK limb setup with stretchy IK, pole vector, and optional scapula/clavicle.

```python
from mayaLib.rigLib.base.limb import Limb, Arm

# Create a limb rig (generic)
limb = Limb(
    limb_joints=["l_shoulder_JNT", "l_elbow_JNT", "l_wrist_JNT"],
    top_finger_joints=["l_thumb_01_JNT", "l_index_01_JNT"],
    prefix="l_arm",
    rig_scale=1.0,
    base_rig=base_rig,
    scapula_joint="l_clavicle_JNT"
)

# Or use the Arm convenience class
arm = Arm(...)  # Same parameters
```

### Limb Helper Functions

```python
from mayaLib.rigLib.base.limb import (
    build_simple_scapula,
    build_clavicle,
    build_dynamic_scapula,
    build_fk_controls,
    build_pole_vector,
    build_ik_controls
)

# Build scapula control
scapula_ctrl = build_simple_scapula(
    prefix="l_arm",
    limb_joints=["l_shoulder_JNT", "l_elbow_JNT", "l_wrist_JNT"],
    scapula_joint="l_clavicle_JNT",
    rig_scale=1.0,
    rig_module=module,
    base_attach_group=attach_grp
)

# Build FK controls for limb
fk_ctrls, fk_constraints, finger_ctrls, finger_constraints = build_fk_controls(
    limb_joints=["l_shoulder_JNT", "l_elbow_JNT", "l_wrist_JNT"],
    top_finger_joints=["l_thumb_01_JNT"],
    rig_scale=1.0,
    rig_module=module
)
```

---

## Spine and Neck

### Spine (`base/spine.py`)

```python
from mayaLib.rigLib.base.spine import Spine

# Create spine rig
spine = Spine(
    spine_joints=["spine_01_JNT", "spine_02_JNT", "spine_03_JNT"],
    prefix="spine",
    rig_scale=1.0,
    base_rig=base_rig
)
```

### Neck (`base/neck.py`)

```python
from mayaLib.rigLib.base.neck import Neck

# Create neck rig
neck = Neck(
    neck_joints=["neck_01_JNT", "neck_02_JNT", "head_JNT"],
    prefix="neck",
    rig_scale=1.0,
    base_rig=base_rig
)
```

---

## Face Rigging

### Face Class (`base/face.py`)

```python
from mayaLib.rigLib.base.face import Face

# Create face rig
face = Face(
    face_joints=[...],  # Face joint list
    prefix="face",
    rig_scale=1.0,
    base_rig=base_rig
)
```

### Facial Rig Utilities (`facial_rig.py`)

Additional face rigging utilities for complex facial setups.

---

## Deformers

### Deform Utilities (`utils/deform.py`)

```python
from mayaLib.rigLib.utils import deform

# Remove "Deformed" suffix from shape nodes
deform.remove_shape_deformed()

# Reorder deformers
deform.reorder_deformer(node, geo_list, search_type="skincluster")

# Paint deformer weights
deform.paint_deformer_weights(
    channel="ffd.ffd1.weights",
    vtx_list=["mesh.vtx[0:100]"],
    value=1.0,
    smooth_iteration=3
)
```

### PaintDeformer Class

```python
from mayaLib.rigLib.utils.deform import PaintDeformer

# Interactive weight painting
painter = PaintDeformer(geo="pCube1", channel="ffd.ffd1.weights")
painter.select_all()
painter.replace(vtx_list, value=0.5)
painter.smooth(smooth_iteration=3)
```

### Available Deformer Functions

| Function | Description |
|----------|-------------|
| `create_proximity_wrap()` | Proximity-based deformation |
| `create_blend_shape()` | Blend shape deformer |
| `create_shrink_wrap()` | Shrink wrap deformer |
| `create_delta_mush()` | Delta mush smoothing |
| `create_wrap()` | Wrap deformer |
| `create_soft_mod()` | Soft modification |
| `create_tension_map()` | Tension visualization |
| `create_cmuscle()` | cMuscle system |

---

## Skin Utilities

### Skin Functions (`utils/skin.py`)

```python
from mayaLib.rigLib.utils import skin

# Get objects with skin clusters
skinned_objects = skin.get_skincluster_object()

# Select all skinned objects
skin.select_skin_cluster_object()

# Copy skin weights between meshes
skin.copy_skin_weight_between_mesh(selection=[source, destination])

# Copy bind with options
skin.copy_bind(
    source="source_mesh",
    destination="dest_mesh",
    sa="closestPoint",      # Surface association
    ia="closestJoint"       # Influence association
)

# Disable inherits transform on skin clusters
skin.disable_inherits_transform_on_skin_clusters()
```

### ngSkinTools2 Integration

```python
from mayaLib.rigLib.utils import skin

# Uses ngSkinTools2 API for advanced operations
from ngSkinTools2 import api as ngst_api
from ngSkinTools2.api import InfluenceMappingConfig, VertexTransferMode, init_layers

# Initialize layers on mesh
init_layers(mesh)
```

---

## External Integrations

### Ziva Dynamics (`Ziva/`)

Integration with Ziva Dynamics for tissue simulation:

```python
from mayaLib.rigLib.Ziva import ziva_tools

# Ziva tissue and fascia utilities
# See source for full API
```

### AdonisFX (`AdonisFX/`)

Integration with AdonisFX for muscle simulation:

```python
from mayaLib.rigLib.AdonisFX import adonis_tools

# Muscle simulation setup
# See source for full API
```

### Cloth Simulation (`cloth/`)

Cloth muscle setup utilities:

```python
from mayaLib.rigLib.utils import cloth_muscle_setup

# nCloth-based muscle simulation
# See source for full API
```

---

## Examples

### Complete Arm Rig Example

```python
import pymel.core as pm
from mayaLib.rigLib.base.module import Base, Module
from mayaLib.rigLib.utils.control import Control
from mayaLib.rigLib.base.limb import build_fk_controls, build_ik_controls

# Create base rig
base_rig = Base(character_name="character", scale=1.0)

# Create arm module
arm_module = Module(prefix="l_arm", base_obj=base_rig)

# Define joint chain
arm_joints = ["l_shoulder_JNT", "l_elbow_JNT", "l_wrist_JNT"]

# Build FK controls
fk_ctrls, fk_constraints, _, _ = build_fk_controls(
    limb_joints=arm_joints,
    top_finger_joints=[],
    rig_scale=1.0,
    rig_module=arm_module
)

# Build IK controls
ik_ctrl, pole_ctrl, ik_handle = build_ik_controls(
    limb_joints=arm_joints,
    prefix="l_arm",
    rig_scale=1.0,
    rig_module=arm_module
)

print("Arm rig created successfully!")
```

### Custom Control Example

```python
from mayaLib.rigLib.utils.control import Control
import pymel.core as pm

# Create a custom control with all options
hip_ctrl = Control(
    prefix="c_hip",
    scale=2.0,
    translate_to="hip_JNT",
    rotate_to="hip_JNT",
    parent="controls_GRP",
    shape="hip",
    lock_channels=["s"],
    do_offset=True,
    do_modify=True,
    do_dynamic_pivot=True
)

# Access the control
ctrl_node = hip_ctrl.get_control()
offset_grp = hip_ctrl.get_offset_grp()

# Add custom attributes
pm.addAttr(ctrl_node, ln="ikFkBlend", at="float", min=0, max=1, dv=0, k=True)
pm.addAttr(ctrl_node, ln="stretch", at="float", min=0, max=1, dv=1, k=True)
```

### Skin Weight Transfer Example

```python
from mayaLib.rigLib.utils import skin
import pymel.core as pm

# Select source and destination meshes
source = pm.ls("original_mesh")[0]
destination = pm.ls("new_mesh")[0]

# Copy skin weights
skin.copy_bind(
    source=source,
    destination=destination,
    sa="closestPoint",
    ia="closestJoint"
)

print(f"Skin weights copied from {source} to {destination}")
```

---

## Best Practices

1. **Always use prefixes** to identify side (l_, r_, c_) and body part
2. **Create offset groups** for controls that will be constrained
3. **Create modify groups** for controls that need manual adjustment
4. **Use the Module class** to organize rig components
5. **Lock and hide unused channels** to prevent animator mistakes
6. **Follow the standard hierarchy** for consistency across projects
7. **Use PyMEL** for all Maya operations
8. **Document custom attributes** with descriptive names

---

## See Also

- [MayaLib Home](Home.md)
- [Control Shapes Reference](../API-Reference.md#control-shapes)
- [Architecture](../Architecture.md)

---

*Last updated: January 2026*

# DevPyLib API Reference

This document provides a quick reference for the most commonly used APIs across DevPyLib.

## MayaLib API

### RigLib

#### Control Creation

```python
from mayaLib.rigLib.utils.control import Control

# Create a control
ctl = Control(
    prefix='arm',           # Naming prefix
    scale=1.0,              # Control scale
    translateTo=joint,      # Match translation
    rotateTo=joint,         # Match rotation
    parent=parent_grp,      # Parent transform
    shape='circle',         # Shape type
    lockChannels=['v']      # Channels to lock
)

# Access components
ctl.Off      # Offset group
ctl.Modify   # Modify group
ctl.C        # Control curve
```

**Available Shapes:**
- `circle`, `square`, `cube`, `sphere`
- `arrow`, `cross`, `diamond`
- `pin`, `locator`, `null`

#### Joint Utilities

```python
from mayaLib.rigLib.utils import joint

# Duplicate joint chain
new_chain = joint.duplicateChain(
    start_jnt='arm_01_jnt',
    end_jnt='arm_03_jnt',
    prefix='fk'
)

# Create joints along curve
joints = joint.jointAlongCurve(
    curve='spine_crv',
    num_joints=5,
    prefix='spine'
)

# Orient joints
joint.orientJoints(joint_list, aimAxis='x', upAxis='y')
```

#### Deformation Utilities

```python
from mayaLib.rigLib.utils import deform

# Create cluster
cluster = deform.createCluster(
    geometry='body_geo',
    name='shoulder'
)

# Create blend shape
blendshape = deform.createBlendShape(
    base='body_geo',
    targets=['smile_geo', 'frown_geo'],
    name='facial'
)
```

#### Skin Utilities

```python
from mayaLib.rigLib.utils import skin

# Copy skin weights
skin.copySkinWeights(
    source='body_geo',
    target='body_geo_v2'
)

# Export skin weights
skin.exportSkinWeights(
    geometry='body_geo',
    file_path='/path/to/weights.json'
)

# Import skin weights
skin.importSkinWeights(
    geometry='body_geo',
    file_path='/path/to/weights.json'
)
```

### AnimationLib

#### BVH Importer

```python
from mayaLib.animationLib.bvh import bvh_importer

# Import BVH file
bvh_importer.import_bvh(
    file_path='/path/to/motion.bvh',
    scale=1.0,
    frame_start=0
)
```

### ModelLib

#### UV Utilities

```python
from mayaLib.modelLib.uv import uv

# Unfold UVs
uv.unfoldUVs(
    geometry='body_geo',
    method='legacy'  # or 'unfold3d'
)

# Layout UVs
uv.layoutUVs(
    geometry='body_geo',
    shell_padding=0.01
)
```

### ShaderLib

#### Shader Creation

```python
from mayaLib.shaderLib import shader

# Create Arnold shader
shader.createArnoldShader(
    name='skin_mtl',
    shader_type='aiStandardSurface'
)

# Assign shader
shader.assignShader(
    geometry='body_geo',
    shader='skin_mtl'
)
```

### FluidLib

#### Fluid Simulation

```python
from mayaLib.fluidLib.fire import Fire
from mayaLib.fluidLib.smoke import Smoke

# Create fire effect
fire = Fire(
    name='torch_fire',
    resolution=100,
    emitter='torch_emitter'
)

# Create smoke effect
smoke = Smoke(
    name='chimney_smoke',
    resolution=80,
    emitter='chimney_emitter'
)
```

### BifrostLib

#### Bifrost/USD Integration

```python
from mayaLib.bifrostLib import bifrost_api

# Create Bifrost graph
graph = bifrost_api.create_bifrost_graph(name='scatter')

# Get USD stage
stage = bifrost_api.get_maya_usd_stage()

# Add compound to graph
bifrost_api.add_compound(graph, 'BifrostGraph::Scatter::scatter_points')
```

### GuiLib

#### FunctionUI

```python
from mayaLib.guiLib.base import base_ui

# Auto-generate UI from function
def my_function(name: str = "default", count: int = 10, enabled: bool = True):
    """My function description.

    Args:
        name: Object name
        count: Number of objects
        enabled: Enable feature
    """
    pass

# Create UI
ui = base_ui.FunctionUI(my_function)
ui.show()
```

### PipelineLib

#### Naming Utilities

```python
from mayaLib.pipelineLib.utility import convention

# Validate name
is_valid = convention.validateName('l_arm_01_jnt')

# Parse name components
parts = convention.parseName('l_arm_01_jnt')
# Returns: {'side': 'l', 'name': 'arm', 'index': '01', 'suffix': 'jnt'}

# Generate name
name = convention.generateName(side='l', name='arm', suffix='jnt')
```

### LunaLib

#### Components

```python
from mayaLib.lunaLib.components import (
    create_character,
    create_fk_chain,
    create_ik_chain,
    create_fkik_chain
)

# Create character
char = create_character(name="hero")

# Create FK chain
fk = create_fk_chain(
    start_joint="arm_01_jnt",
    end_joint="arm_03_jnt",
    name="arm",
    side="l"
)

# Create IK chain
ik = create_ik_chain(
    start_joint="leg_01_jnt",
    end_joint="leg_03_jnt",
    name="leg",
    side="l"
)
```

#### Functions

```python
from mayaLib.lunaLib.functions import (
    duplicate_chain,
    joint_chain,
    get_pole_vector,
    generate_name
)

# Duplicate chain
new_chain = duplicate_chain(
    start_joint="spine_01_jnt",
    end_joint="spine_05_jnt",
    new_name="fk",
    new_side="c"
)

# Get pole vector position
pv_loc = get_pole_vector("l_arm_01_jnt", "l_arm_03_jnt")

# Generate Luna-style name
name = generate_name(name="arm", side="l", suffix="jnt")
```

#### Tools

```python
from mayaLib.lunaLib.tools import (
    launch_builder,
    launch_configer,
    launch_anim_baker
)

# Open Luna Builder
launch_builder()

# Open Luna Config
launch_configer()

# Open Animation Baker
launch_anim_baker()
```

## HoudiniLib API

### HDAs

```python
# Houdini Digital Assets are accessed through Houdini's native HDA system
# DevPyLib provides custom HDAs in houdiniLib/HDAs/

# Example usage in Houdini:
import hou

# Load HDA
hou.hda.installFile("/path/to/DevPyLib/houdiniLib/HDAs/custom_scatter.hda")

# Create node from HDA
node = hou.node("/obj").createNode("custom_scatter")
```

## BlenderLib API

### Basic Utilities

```python
# BlenderLib provides minimal utilities
# Future expansion planned

import bpy
from blenderLib import utils

# Example utilities (when implemented)
# utils.create_rig_hierarchy(name="character")
# utils.export_animation(filepath="/path/to/anim.fbx")
```

## Quick Reference Tables

### Control Shapes

| Shape | Description |
|-------|-------------|
| `circle` | Circle curve |
| `square` | Square curve |
| `cube` | 3D cube |
| `sphere` | 3D sphere |
| `arrow` | Arrow pointer |
| `cross` | Cross shape |
| `diamond` | Diamond shape |
| `pin` | Pin locator |

### Naming Suffixes

| Suffix | Type |
|--------|------|
| `_GRP` | Group/Transform |
| `_CTRL` | Control |
| `_JNT` | Joint |
| `_LOC` | Locator |
| `_GEO` | Geometry |
| `_CRV` | Curve |
| `_IKH` | IK Handle |
| `_CLU` | Cluster |

### Side Prefixes

| Prefix | Side |
|--------|------|
| `l_` | Left |
| `r_` | Right |
| `c_` | Center |

## See Also

- [Architecture](Architecture.md) - Design patterns
- [MayaLib/Home](MayaLib/Home.md) - MayaLib details
- [Luna wiki](../luna/docs/wiki/Home.md) - Luna framework docs

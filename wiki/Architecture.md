# DevPyLib Architecture

This document describes the overall architecture and design patterns used in DevPyLib.

## Overview

DevPyLib follows a modular, DCC-agnostic architecture designed to share code and patterns across multiple Digital Content Creation applications while maintaining DCC-specific implementations where necessary.

```
DevPyLib/
├── mayaLib/          # Maya-specific utilities (primary)
├── houdiniLib/       # Houdini-specific utilities
├── blenderLib/       # Blender-specific utilities
├── prismLib/         # Prism Pipeline integration
├── pyfrost/          # Bifrost Python utilities (submodule)
├── luna/             # Luna rigging framework (submodule)
├── scripts/          # Startup scripts
└── wiki/             # Documentation
```

## Design Patterns

### 1. Base Class Pattern

Most submodules follow a layered architecture with foundational base classes:

#### RigLib Base Pattern
```python
# rigLib/base/module.py
class Base:
    """Base class for all rig modules."""

    def __init__(self, prefix='new', scale=1.0, base_rig=None):
        self.topGrp = None
        self.rigGrp = None
        self.modelGrp = None
        self.jointsGrp = None
        self.modulesGrp = None
        # Creates standard hierarchy
```

All rig modules inherit from `Base`:
- `Limb` - Arm/leg components
- `IKChain` - IK systems
- `Spine` - Spine rigs
- `Face` - Facial rigs
- `Neck` - Neck components

#### FluidLib Base Pattern
```python
# fluidLib/base/baseFluid.py
class BaseFluid:
    """Base class for fluid simulations."""

    def __init__(self, fluid_container, emitter):
        self.container = fluid_container
        self.emitter = emitter
```

Concrete implementations:
- `Smoke` - Smoke effects
- `Fire` - Fire effects
- `Explosion` - Explosion effects
- `FireSmoke` - Combined fire/smoke

### 2. Utility Layer Pattern

Heavy use of utility modules for orthogonal concerns:

```
rigLib/utils/
├── joint.py          # Joint operations
├── control.py        # Control creation
├── transform.py      # Transform utilities
├── deform.py         # Deformation tools
├── skin.py           # Skinning utilities
├── dynamic.py        # Dynamics helpers
├── ikfkSwitch.py     # IK/FK switching
└── ... (31+ utilities)
```

### 3. Introspective UI Pattern

The GUI system uses Python introspection to auto-generate UIs:

```python
# guiLib/base/baseUI.py
class FunctionUI:
    """Generates Qt widgets from function signatures."""

    def __init__(self, function):
        self.func = function
        self.params = inspect.signature(function).parameters
        self._build_widgets()

    def _build_widgets(self):
        for name, param in self.params.items():
            widget = self._create_widget_for_type(param.annotation)
            # Automatically handles: bool->checkbox, int/float->lineedit, etc.
```

### 4. Lazy Loading Pattern

Menu system uses lazy imports for performance:

```python
# guiLib/mainMenu.py
def add_recursive_menu(self, up_menu, lib_dict):
    for key, value in lib_dict.items():
        if isinstance(value, dict):
            sub_menu = self.add_sub_menu(up_menu, key)
            self.add_recursive_menu(sub_menu, value)
        else:
            # Lazy import on menu click
            func = self.lib_structure.import_and_exec(module, key)
```

### 5. DCC Detection Pattern

Cross-DCC code uses module detection:

```python
# prismLib/pipeline.py
def detect_host_app():
    """Detect which DCC is running."""
    if "maya.cmds" in sys.modules:
        return "Maya"
    elif "hou" in sys.modules:
        return "Houdini"
    elif "bpy" in sys.modules:
        return "Blender"
    return "Unknown"
```

## Module Communication

### Hierarchical Organization

Standard rig structure from `rigLib/base/module.py`:

```
{character}_rig_GRP/
├── global_CTRL
│   └── main_CTRL
│       ├── rig_GRP/
│       │   └── parts_GRP/
│       ├── skeleton_GRP/
│       └── modules_GRP/
└── model_GRP/
    ├── fastModel_GRP
    ├── mediumModel_GRP
    └── slowModel_GRP
```

### Control System

The `Control` class is central to all rigging:

```python
# rigLib/utils/control.py
class Control:
    """Creates controls with consistent hierarchy."""

    def __init__(self, prefix='new', scale=1.0,
                 translateTo=None, rotateTo=None,
                 parent=None, shape='circle'):
        # Creates: offset_grp > modify_grp > control
        self.Off = self._create_offset_group()
        self.Modify = self._create_modify_group()
        self.C = self._create_control(shape)
```

## Data Flow

### Startup Sequence

```
Maya Launch
    │
    ▼
userSetup.py
    │
    ├── Install requirements (async)
    ├── Add DevPyLib to sys.path
    ├── Import mayaLib
    │
    ▼
MainMenu (deferred)
    │
    ├── Discover functions via introspection
    ├── Build menu structure
    └── Connect to FunctionUI
```

### Function UI Flow

```
User clicks menu item
    │
    ▼
import_and_exec(module, function)
    │
    ▼
FunctionUI(function)
    │
    ├── Parse function signature
    ├── Generate appropriate widgets
    ├── Connect to Maya selection (>)
    │
    ▼
User fills parameters
    │
    ▼
Execute function with args
```

## Plugin Architecture

Maya plugins use Python API 2.0:

```python
# mayaLib/plugin/tensionMap.py
import maya.api.OpenMaya as om

def maya_useNewAPI():
    """Required for API 2.0."""
    pass

class TensionMapNode(om.MPxNode):
    """Custom deformer node."""

    @staticmethod
    def creator():
        return TensionMapNode()

    @staticmethod
    def initialize():
        # Define attributes
        pass

def initializePlugin(plugin):
    plugin_fn = om.MFnPlugin(plugin)
    plugin_fn.registerNode(
        'tensionMap',
        TensionMapNode.id,
        TensionMapNode.creator,
        TensionMapNode.initialize
    )
```

## Integration Points

### Luna Integration

Luna is integrated through the `lunaLib` bridge:

```python
# mayaLib/lunaLib/__init__.py
# Adds Luna path and imports modules

# mayaLib/lunaLib/bridge/
# Provides bidirectional utilities
```

### Bifrost/USD Integration

```python
# bifrostLib/bifrost_api.py
def create_bifrost_graph():
    """Create Bifrost graph node."""

def get_maya_usd_stage():
    """Get USD stage from Maya."""

# bifrostLib/stage_builder.py
class StageBuilder:
    """High-level USD composition."""
```

### Prism Pipeline Integration

```python
# prismLib/pipeline.py
class PrismIntegration:
    """Prism Pipeline hooks."""

    def get_project_path(self):
        """Get current Prism project."""

    def publish_asset(self, asset_type):
        """Publish to Prism."""
```

## Best Practices

1. **Use PyMEL** for Maya operations (`import pymel.core as pm`)
2. **Use pathlib** for cross-platform paths
3. **Use subprocess** instead of `os.system()`
4. **Follow naming conventions**: `_GRP`, `_CTRL`, `_LOC`, `_JNT`
5. **Include docstrings** for UI generation
6. **Check platform** with `platform.system()`

## See Also

- [Cross-Platform](Cross-Platform.md) - Platform compatibility
- [API-Reference](API-Reference.md) - Detailed API docs
- [MayaLib/Home](MayaLib/Home.md) - Maya-specific architecture

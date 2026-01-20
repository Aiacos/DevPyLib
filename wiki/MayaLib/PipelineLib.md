# PipelineLib Documentation

PipelineLib provides pipeline utilities for Maya, including naming conventions, workspace management, function discovery, and USD unit coordination.

---

## Table of Contents

- [Overview](#overview)
- [Module Structure](#module-structure)
- [Naming Convention](#naming-convention)
- [Name Check](#name-check)
- [Workspace Utilities](#workspace-utilities)
- [Space/Unit Utilities](#spaceunit-utilities)
- [Function Discovery](#function-discovery)
- [Library Manager](#library-manager)
- [Documentation Utilities](#documentation-utilities)
- [Type Utilities](#type-utilities)
- [Usage Examples](#usage-examples)

---

## Overview

PipelineLib provides studio pipeline integration utilities that help maintain consistency across projects and integrate with external pipeline systems like USD and Prism.

### Key Features

- **Naming conventions**: Validate and enforce naming standards
- **Workspace management**: Scene organization utilities
- **Function discovery**: Automatic function introspection for UI generation
- **USD integration**: Maya/USD unit coordination
- **Documentation**: Extract docstrings for UI display

### Module Structure

```
pipelineLib/
├── __init__.py
└── utility/
    ├── __init__.py
    ├── convention.py       # Asset naming rules
    ├── name_check.py       # Naming convention validation
    ├── workspace.py        # Workspace utilities
    ├── space_unit.py       # USD/Maya unit coordination
    ├── list_function.py    # Function discovery
    ├── lib_manager.py      # Library installation/update
    ├── docs.py             # Documentation extraction
    └── type_utils.py       # Type utilities
```

---

## Naming Convention

### convention.py

Provides asset naming rules and conventions.

```python
from mayaLib.pipelineLib.utility import convention

# Asset naming utilities
# See module for full API
```

### Standard Naming Conventions

DevPyLib uses consistent naming suffixes:

| Suffix | Description | Example |
|--------|-------------|---------|
| `_GRP` | Group node | `arm_GRP` |
| `_CTRL` | Control curve | `arm_CTRL` |
| `_JNT` | Joint | `arm_JNT` |
| `_LOC` | Locator | `target_LOC` |
| `_IKH` | IK Handle | `arm_IKH` |
| `_geo` | Geometry | `body_geo` |
| `_SG` | Shading group | `lambert1_SG` |

### Prefix Conventions

| Prefix | Description |
|--------|-------------|
| `l_` | Left side |
| `r_` | Right side |
| `c_` | Center |
| `fk_` | FK component |
| `ik_` | IK component |

---

## Name Check

### name_check.py

Validates and corrects naming convention issues.

```python
from mayaLib.pipelineLib.utility import name_check as nc

# Check and fix a name
corrected_name = nc.name_check("myControl*_CTRL")
# Returns: "myControl1_CTRL" (removes invalid characters, adds number)
```

### name_check Function

```python
def name_check(name: str) -> str:
    """Check and correct a node name.

    Args:
        name: The name to check

    Returns:
        Corrected name with proper formatting
    """
```

### Common Fixes

| Input | Output | Fix Applied |
|-------|--------|-------------|
| `my control` | `my_control` | Replace spaces |
| `my-control` | `my_control` | Replace hyphens |
| `MyControl` | `my_control` | Convert to snake_case |
| `ctrl*` | `ctrl1` | Replace wildcards |

---

## Workspace Utilities

### workspace.py

Scene and workspace organization utilities.

```python
from mayaLib.pipelineLib.utility import workspace

# Workspace utilities
# See module for full API
```

### Common Operations

| Operation | Description |
|-----------|-------------|
| Get workspace | Get current Maya workspace path |
| Set workspace | Set Maya workspace |
| Create folders | Create standard folder structure |
| File paths | Resolve file paths relative to workspace |

---

## Space/Unit Utilities

### space_unit.py

Coordinates units between Maya and USD.

```python
from mayaLib.pipelineLib.utility import space_unit

# Configure USD export units based on Maya settings
space_unit.pre_maya_usd_export()
```

### pre_maya_usd_export Function

```python
def pre_maya_usd_export():
    """Configure USD export unit based on Maya settings.

    Ensures USD files are exported with the correct unit scale
    to match the Maya scene's working units.
    """
```

### Unit Mapping

| Maya Unit | USD Unit | Scale |
|-----------|----------|-------|
| cm | cm | 1.0 |
| m | m | 1.0 |
| mm | mm | 1.0 |
| inch | inch | 1.0 |

---

## Function Discovery

### list_function.py

Automatic function discovery for UI generation.

```python
from mayaLib.pipelineLib.utility import list_function as lm

# Create structure manager
import mayaLib
structure = lm.StructureManager(mayaLib)

# Get library structure
lib_dict = structure.get_struct_lib()

# Import and execute a function
func = structure.import_and_exec("mayaLib.rigLib.utils.control", "Control")
```

### StructureManager Class

```python
class StructureManager:
    """Discover and manage library function structure."""

    def __init__(self, package):
        """Initialize with a Python package.

        Args:
            package: The Python package to inspect
        """

    def get_struct_lib(self):
        """Get the library structure as nested dict.

        Returns:
            dict: Nested dictionary of modules and functions
        """

    def import_and_exec(self, module_path, function_name):
        """Import a module and get a function.

        Args:
            module_path: Dot-separated module path
            function_name: Name of the function

        Returns:
            The function object
        """
```

### Attributes

| Attribute | Description |
|-----------|-------------|
| `final_class_list` | List of all discovered functions |

---

## Library Manager

### lib_manager.py

Library installation and update utilities.

```python
from mayaLib.pipelineLib.utility import lib_manager

# Create library installer
lib = lib_manager.InstallLibrary()

# Pull latest from git
lib.pull_from_git()
```

### InstallLibrary Class

```python
class InstallLibrary:
    """Manage DevPyLib installation and updates."""

    def pull_from_git(self):
        """Pull latest changes from git repository."""

    def download(self):
        """Download the library (alternative to git)."""
```

---

## Documentation Utilities

### docs.py

Extract and format docstrings for UI display.

```python
from mayaLib.pipelineLib.utility import docs

def my_function(param1, param2=10):
    """My test function.

    Args:
        param1: First parameter
        param2: Second parameter
    """
    pass

# Get formatted documentation
doc_text = docs.get_docs(my_function)
# Returns: "My test function."
```

### get_docs Function

```python
def get_docs(func):
    """Extract first line of docstring.

    Args:
        func: Function to get docs from

    Returns:
        str: First line of docstring or empty string
    """
```

---

## Type Utilities

### type_utils.py

Type conversion and validation utilities.

```python
from mayaLib.pipelineLib.utility import type_utils

# Type utilities for parameter handling
# See module for full API
```

---

## Usage Examples

### Validating Scene Names

```python
from mayaLib.pipelineLib.utility import name_check as nc
import pymel.core as pm

# Get all transforms
transforms = pm.ls(type="transform")

# Check and report naming issues
for node in transforms:
    name = str(node)
    corrected = nc.name_check(name)
    if name != corrected:
        print(f"Naming issue: {name} -> {corrected}")
```

### Setting Up Workspace

```python
from mayaLib.pipelineLib.utility import workspace
import maya.cmds as cmds

# Set workspace for project
project_path = "/projects/myProject"
cmds.workspace(project_path, openWorkspace=True)

# Get current workspace
current = cmds.workspace(query=True, rootDirectory=True)
print(f"Current workspace: {current}")
```

### USD Export with Correct Units

```python
from mayaLib.pipelineLib.utility import space_unit
import maya.cmds as cmds

# Before USD export, configure units
space_unit.pre_maya_usd_export()

# Now export USD
cmds.mayaUSDExport(
    file="/output/scene.usd",
    selection=True
)
```

### Function Discovery for Custom Tools

```python
from mayaLib.pipelineLib.utility import list_function as lm

# Import your tools package
import myTools

# Create structure manager
structure = lm.StructureManager(myTools)

# Get all available functions
lib_dict = structure.get_struct_lib()

# Print available functions
for module, functions in lib_dict.items():
    print(f"\n{module}:")
    if isinstance(functions, dict):
        for func_name in functions.keys():
            print(f"  - {func_name}")
```

### Getting Documentation for UI

```python
from mayaLib.pipelineLib.utility import docs
from mayaLib.guiLib.base.base_ui import FunctionUI

def smooth_mesh(mesh, iterations=3, preserve_volume=True):
    """Smooth a polygon mesh.

    Applies smoothing to reduce surface noise while
    optionally preserving volume.

    Args:
        mesh: The mesh to smooth
        iterations: Number of smoothing passes
        preserve_volume: Keep original volume

    Returns:
        The smoothed mesh
    """
    pass

# Get docs for tooltip
doc_text = docs.get_docs(smooth_mesh)
print(doc_text)  # "Smooth a polygon mesh."

# Use in FunctionUI
ui = FunctionUI(smooth_mesh)
# Documentation appears in the UI
```

### Library Update Script

```python
from mayaLib.pipelineLib.utility import lib_manager

def update_devpylib():
    """Update DevPyLib to latest version."""
    lib = lib_manager.InstallLibrary()

    try:
        lib.pull_from_git()
        print("DevPyLib updated successfully!")
        print("Please restart Maya to apply changes.")
    except Exception as e:
        print(f"Update failed: {e}")

# Run update
update_devpylib()
```

---

## Integration with Prism Pipeline

PipelineLib works with prismLib for broader pipeline integration:

```python
from prismLib.pipeline import detect_host_app

# Detect current DCC application
host = detect_host_app()

if host == "Maya":
    from mayaLib.pipelineLib.utility import workspace
    # Use Maya-specific pipeline tools
elif host == "Houdini":
    # Use Houdini-specific tools
    pass
```

---

## Best Practices

1. **Use name_check**: Validate names before creating nodes
2. **Configure units early**: Set up USD units before export
3. **Document functions**: Docstrings appear in auto-generated UIs
4. **Update regularly**: Use lib_manager to stay current
5. **Follow conventions**: Use standard suffixes and prefixes
6. **Organize by workspace**: Keep projects in their own workspaces

---

## See Also

- [MayaLib Home](Home.md)
- [GuiLib](GuiLib.md) - Uses function discovery for menus
- [BifrostLib](BifrostLib.md) - USD integration
- [Architecture](../Architecture.md) - Pipeline design

---

*Last updated: January 2026*

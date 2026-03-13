# MayaLib Getting Started Guide

This guide will help you install and configure MayaLib for use in Autodesk Maya.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation Methods](#installation-methods)
- [Configuration](#configuration)
- [Verifying Installation](#verifying-installation)
- [First Steps](#first-steps)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements

- **Maya**: 2024 or later (Python 3.9+)
- **Operating System**: Windows, Linux, or macOS
- **Git**: Required for cloning and submodule management

### Python Dependencies

```
numpy
pymel
GitPython
```

> **Maya 2026**: PyMEL 1.5.0 (PyPI) does not support Maya 2026. Install [pymel 1.6.0rc2](https://github.com/iamsleepy/pymel/releases/tag/1.6.0rc2) instead.

### Optional Dependencies

```
ngSkinTools2       # Advanced skin weighting
Ziva Dynamics      # Tissue simulation
AdonisFX           # Muscle simulation
```

---

## Installation Methods

### Method 1: Installer Script (Recommended)

1. **Clone the repository** with submodules:
   ```bash
   git clone --recursive https://github.com/Aiacos/DevPyLib.git
   cd DevPyLib
   ```

2. **Run the installer** to copy `Maya.env` and `userSetup.py`:

   **Windows:**
   ```batch
   install.bat
   ```

   **Linux/macOS:**
   ```bash
   ./install.sh
   ```

   The installer automatically:
   - Detects installed Maya versions (2024-2026)
   - Copies `Maya.env` to `maya/{version}/Maya.env`
   - Copies `userSetup.py` to `maya/scripts/userSetup.py`

3. **Start Maya** - Dependencies will auto-install on first startup.

### Method 2: Manual Copy

1. **Clone** the repository
2. **Copy** `mayaLib/userSetup.py` to Maya's scripts directory:
   - **Windows**: `%USERPROFILE%\Documents\maya\scripts\`
   - **Linux**: `~/maya/scripts/`
   - **macOS**: `~/Library/Preferences/Autodesk/maya/scripts/`
3. **Copy** `mayaLib/Maya.env` to the Maya version directory:
   - **Windows**: `%USERPROFILE%\Documents\maya\{version}\Maya.env`
   - **Linux**: `~/maya/{version}/Maya.env`
4. **Start Maya**

---

## Configuration

### Maya Scripts Directory Locations

| Platform | Path |
|----------|------|
| **Windows** | `%USERPROFILE%\Documents\maya\scripts\` |
| **Linux** | `~/maya/scripts/` or `~/Documents/maya/scripts/` |
| **macOS** | `~/Library/Preferences/Autodesk/maya/scripts/` |

### userSetup.py Auto-Detection

The `userSetup.py` file automatically detects the DevPyLib location using:

```python
from pathlib import Path
devpylib_path = Path(__file__).parent.resolve()
```

This means you can install DevPyLib anywhere on your system without modifying hardcoded paths.

### Maya.env Configuration

The `mayaLib/Maya.env` file is pre-configured. Key variables:

| Variable | Purpose |
|----------|---------|
| `DEVPYLIB_PATH` | Path to DevPyLib root directory |
| `PYTHONPATH` | Python import path (set to DEVPYLIB_PATH) |
| `BIFROST_LIB_CONFIG_FILES` | Custom Bifrost compound library path |
| `DEVPYLIB_DISABLE_LUNA` | Set to `1` to disable Luna at startup |

### Loading Plugins

To load MayaLib plugins manually:

```python
import maya.cmds as cmds

# Load tension map plugin
cmds.loadPlugin("C:/path/to/DevPyLib/mayaLib/plugin/tension_map.py")

# Load mesh collision plugin
cmds.loadPlugin("C:/path/to/DevPyLib/mayaLib/plugin/mesh_collision.py")
```

---

## Verifying Installation

### Check Import

Open Maya's Script Editor and run:

```python
# Test basic import
import mayaLib
print("MayaLib imported successfully!")

# Test specific modules
from mayaLib.rigLib.base.module import Base
from mayaLib.rigLib.utils.control import Control
from mayaLib.shaderLib.shader import TextureShader
print("All modules imported successfully!")
```

### Check Menu

After Maya starts:
1. Look for **MayaLib** in the main menu bar
2. Click to open the searchable function library
3. Type a search term to find available functions

### Check Plugin Loading

```python
import maya.cmds as cmds

# Check if plugins are available
plugin_path = "C:/path/to/DevPyLib/mayaLib/plugin/tension_map.py"
if cmds.pluginInfo(plugin_path, query=True, loaded=True):
    print("TensionMap plugin loaded!")
else:
    cmds.loadPlugin(plugin_path)
    print("TensionMap plugin loaded manually.")
```

---

## First Steps

### Creating Your First Rig

```python
from mayaLib.rigLib.base.module import Base, Module
from mayaLib.rigLib.utils.control import Control

# Create base rig structure
base_rig = Base(character_name="testCharacter", scale=1.0)

# The base rig creates:
# - Top group: testCharacter_rig_GRP
# - Global control: global_CTRL
# - Main control: main_CTRL
# - Model group: model_GRP
# - Skeleton group: skeleton_GRP
# - Modules group: modules_GRP

print("Created rig groups:")
print(f"  Top Group: {base_rig.top_group}")
print(f"  Model Group: {base_rig.model_group}")
print(f"  Skeleton Group: {base_rig.joints_group}")
print(f"  Modules Group: {base_rig.modules_group}")
```

### Creating Controls

```python
from mayaLib.rigLib.utils.control import Control

# Create a simple control
ctrl = Control(
    prefix="test",
    scale=1.0,
    shape="circle",
    lock_channels=["s", "v"]
)

# Access control components
print(f"Control: {ctrl.get_control()}")
print(f"Offset Group: {ctrl.get_offset_grp()}")
print(f"Modify Group: {ctrl.get_modify_grp()}")
print(f"Top Node: {ctrl.get_top()}")
```

### Creating Fluid Effects

```python
from mayaLib.fluidLib.smoke import WispySmoke

# Create a wispy smoke simulation
smoke = WispySmoke(
    fluid_name="mySmoke",
    base_res=32,
    emit_obj=None  # Will create standalone emitter
)

# Access fluid components
print(f"Fluid Shape: {smoke.get_fluid_shape()}")
print(f"Fluid Emitter: {smoke.get_fluid_emitter()}")
```

### Using the FunctionUI System

```python
from mayaLib.guiLib.base.base_ui import FunctionUI

# Define a function
def my_tool(mesh_name, subdivisions=2, smooth=True):
    """My custom tool.

    Args:
        mesh_name: Name of the mesh to process
        subdivisions: Number of subdivisions
        smooth: Enable smoothing
    """
    print(f"Processing {mesh_name} with {subdivisions} subdivisions")
    if smooth:
        print("Smoothing enabled")

# Create auto-generated UI
ui = FunctionUI(my_tool)
ui.show()
```

---

## Troubleshooting

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'mayaLib'`

**Solution**:
1. Verify PYTHONPATH includes DevPyLib root directory
2. Check that `userSetup.py` is in Maya's scripts directory
3. Verify the symlink is correct (if using symlinks)

### PyMEL Not Found

**Problem**: `ImportError: No module named 'pymel'`

**Solution**:
```bash
mayapy -m pip install pymel
```

### PyMEL Cannot Find Maya Documentation (Maya 2026)

**Problem**: `OSError: Cannot find maya documentation. Expected to find it at ...\docs\Maya2026\en_US`

**Solution**: PyMEL 1.5.0 does not support Maya 2026. Install the community fork:
```bash
mayapy -m pip uninstall pymel
mayapy -m pip install git+https://github.com/iamsleepy/pymel.git@1.6.0rc2
```

### Qt Import Errors

**Problem**: `ImportError: No module named 'PySide2'` or `'PySide6'`

**Solution**: MayaLib uses automatic fallback:
```python
try:
    from PySide6 import QtCore, QtWidgets
except ImportError:
    from PySide2 import QtCore, QtWidgets
```
Ensure you're using a Maya version that includes either PySide2 or PySide6.

### Plugin Loading Failed

**Problem**: Plugin fails to load

**Solution**:
1. Check plugin path is correct
2. Verify plugin contains `maya_useNewAPI()` function
3. Check Maya's Script Editor for error messages
4. Load manually:
   ```python
   import maya.cmds as cmds
   cmds.loadPlugin("/full/path/to/plugin.py", quiet=False)
   ```

### Menu Not Appearing

**Problem**: MayaLib menu doesn't appear in Maya

**Solution**:
1. Check Maya's Script Editor for startup errors
2. Verify `userSetup.py` executed successfully
3. Manually create the menu:
   ```python
   from mayaLib.guiLib.main_menu import MainMenu
   from pathlib import Path

   lib_path = Path("C:/path/to/DevPyLib")
   menu = MainMenu(lib_path, menu_name="MayaLib", auto_update_on_load=False)
   ```

### Git Submodule Issues

**Problem**: `pyfrost/` or `luna/` directories are empty

**Solution**:
```bash
cd /path/to/DevPyLib
git submodule update --init --recursive
```

---

## Next Steps

- [MayaLib Home](Home.md) - Module overview
- [RigLib](RigLib.md) - Rigging documentation
- [GuiLib](GuiLib.md) - UI framework documentation
- [Architecture](../Architecture.md) - Design patterns

---

*Last updated: March 2026*

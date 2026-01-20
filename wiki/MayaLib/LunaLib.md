# LunaLib Documentation

LunaLib provides integration between DevPyLib's MayaLib and the Luna rigging framework, enabling Luna's node-based rig building system to be accessed through DevPyLib's menu system.

---

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Module Structure](#module-structure)
- [Luna Framework](#luna-framework)
- [Integration Features](#integration-features)
- [Usage Examples](#usage-examples)
- [Troubleshooting](#troubleshooting)

---

## Overview

Luna is a rigging system that allows creating rigs via Python or a node-based editor. LunaLib bridges Luna with DevPyLib, making Luna's components, functions, and tools available through the MayaLib menu system.

### Key Features

- **Seamless integration**: Luna tools accessible from MayaLib menu
- **Bridge utilities**: Connect DevPyLib rigs with Luna components
- **Component wrappers**: Expose Luna components through DevPyLib patterns
- **Automatic detection**: Luna availability checked at import time

### Module Structure

```
lunaLib/
├── __init__.py        # Luna availability check
├── bridge/            # Bridge utilities between DevPyLib and Luna
├── components/        # Luna component wrappers
├── functions/         # Luna function exposures
└── tools/             # Luna tool integrations
```

---

## Installation

Luna is included as a git submodule in DevPyLib.

### Prerequisites

- DevPyLib installed and configured
- Git for submodule management

### Steps

1. **Update submodules**:
   ```bash
   cd /path/to/DevPyLib
   git submodule update --init --recursive
   ```

2. **Verify Luna installation**:
   ```python
   from mayaLib.lunaLib import LUNA_AVAILABLE
   print(f"Luna available: {LUNA_AVAILABLE}")
   ```

3. **Enable Luna plugin** (optional):
   - Open Maya Plugin Manager
   - Load `luna_plugin.py` from `luna/plug-ins/`

### Luna Location

Luna is located at:
```
DevPyLib/luna/
├── luna/              # Core Luna module
├── luna_builder/      # Node-based builder
├── luna_configer/     # Configuration utilities
├── luna_rig/          # Rig components
├── plug-ins/          # Maya plugins
├── configs/           # Configuration files
├── docs/              # Luna documentation
├── tests/             # Test files
└── res/               # Resources
```

---

## Module Structure

### __init__.py

The initialization module handles Luna availability detection:

```python
"""Luna rigging framework integration for mayaLib."""

import sys
from pathlib import Path

# Add Luna path to sys.path
_luna_path = Path(__file__).parent.parent.parent / "luna"
if _luna_path.exists() and str(_luna_path) not in sys.path:
    sys.path.insert(0, str(_luna_path))

# Try to import Luna modules
LUNA_AVAILABLE = False
luna = None
luna_rig = None
luna_builder = None

try:
    import luna
    import luna_rig
    import luna_builder
    LUNA_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Luna not available - {e}")

# Only import submodules if Luna is available
if LUNA_AVAILABLE:
    from . import components
    from . import functions
    from . import tools
```

### Checking Availability

```python
from mayaLib.lunaLib import LUNA_AVAILABLE

if LUNA_AVAILABLE:
    from mayaLib.lunaLib import components, functions, tools
    # Use Luna features
else:
    print("Luna not available. Install via git submodule.")
```

### bridge/

Bridge utilities for connecting DevPyLib rigs with Luna:

```python
from mayaLib.lunaLib.bridge import ...

# Bridge utilities between DevPyLib and Luna
```

### components/

Luna component wrappers:

```python
from mayaLib.lunaLib.components import ...

# Luna component exposures
```

### functions/

Luna function exposures:

```python
from mayaLib.lunaLib.functions import ...

# Luna function wrappers
```

### tools/

Luna tool integrations:

```python
from mayaLib.lunaLib.tools import ...

# Luna tool integrations
```

---

## Luna Framework

### Overview

Luna provides:
- **Node-based rig building**: Visual graph editor for rig creation
- **Python API**: Programmatic rig construction
- **Component library**: Pre-built rig components
- **Marking menus**: Selection-based context menus

### Luna Builder

The Luna Builder is a visual graph editor for creating rigs:

![Luna Builder](../../luna/docs/luna_builder.png)

Features:
- Drag-and-drop component creation
- Visual connection between components
- Real-time rig preview
- Save/load rig graphs

### Luna Plugin Menu

When the Luna plugin is loaded, it adds a menu to Maya:

![Luna Menu](../../luna/docs/luna_menu.png)

### Luna Marking Menu

Selection-based context menu for quick access to rig functions:

![Luna Marking Menu](../../luna/docs/luna_marking_menu.png)

### Luna Rig Components

Luna provides pre-built rig components:
- FK chains
- IK chains
- Spline IK
- FKIK switch
- Bendy limbs
- Face components
- And more...

---

## Integration Features

### Menu Integration

Luna appears in the MayaLib menu under the "Luna" discipline:

```
MayaLib
├── Modelling
├── Rigging
├── Animation
├── Vfx
├── Lookdev
└── Luna              # Luna integration
    └── Luna (lunaLib)
        └── [Luna functions...]
```

### Conditional Loading

LunaLib gracefully handles missing Luna installation:

```python
# In main_menu.py
elif discipline == "Luna":
    try:
        from mayaLib.lunaLib import LUNA_AVAILABLE
        if LUNA_AVAILABLE:
            lib_menu = self.add_sub_menu(up_menu, "lunaLib")
            self.add_recursive_menu(lib_menu, self.lib_dict.get("lunaLib", {}))
        else:
            disabled_action = QAction("Luna not available", self)
            disabled_action.setEnabled(False)
            up_menu.addAction(disabled_action)
    except ImportError:
        disabled_action = QAction("Luna not available", self)
        disabled_action.setEnabled(False)
        up_menu.addAction(disabled_action)
```

---

## Usage Examples

### Checking Luna Status

```python
from mayaLib.lunaLib import LUNA_AVAILABLE, luna, luna_rig, luna_builder

if LUNA_AVAILABLE:
    print("Luna version:", luna.__version__ if hasattr(luna, '__version__') else "Unknown")
    print("Luna rig module loaded:", luna_rig is not None)
    print("Luna builder module loaded:", luna_builder is not None)
else:
    print("Luna is not available. Run: git submodule update --init --recursive")
```

### Using Luna with DevPyLib Rig

```python
from mayaLib.rigLib.base.module import Base, Module
from mayaLib.lunaLib import LUNA_AVAILABLE

# Create DevPyLib base rig
base_rig = Base(character_name="myCharacter", scale=1.0)

# If Luna is available, add Luna components
if LUNA_AVAILABLE:
    import luna_rig
    # Use Luna components with DevPyLib structure
    # See Luna documentation for component usage
```

### Opening Luna Builder

```python
from mayaLib.lunaLib import LUNA_AVAILABLE

if LUNA_AVAILABLE:
    import luna_builder
    # Open the Luna Builder window
    # luna_builder.open_builder()
```

---

## Troubleshooting

### Luna Not Available

**Problem**: `LUNA_AVAILABLE` is False

**Solutions**:

1. **Update submodules**:
   ```bash
   cd /path/to/DevPyLib
   git submodule update --init --recursive
   ```

2. **Check Luna directory exists**:
   ```python
   from pathlib import Path
   luna_path = Path("C:/path/to/DevPyLib/luna")
   print(f"Luna exists: {luna_path.exists()}")
   ```

3. **Check for import errors**:
   ```python
   import sys
   sys.path.insert(0, "C:/path/to/DevPyLib/luna")
   try:
       import luna
       print("Luna imported successfully")
   except ImportError as e:
       print(f"Import error: {e}")
   ```

### Plugin Load Failure

**Problem**: Luna plugin fails to load

**Solutions**:

1. **Check plugin path**:
   ```python
   import maya.cmds as cmds
   cmds.loadPlugin("C:/path/to/DevPyLib/luna/plug-ins/luna_plugin.py")
   ```

2. **Check Maya console** for error messages

3. **Verify Maya version compatibility**

### Menu Not Showing Luna

**Problem**: Luna doesn't appear in MayaLib menu

**Solutions**:

1. **Verify LUNA_AVAILABLE**:
   ```python
   from mayaLib.lunaLib import LUNA_AVAILABLE
   print(LUNA_AVAILABLE)
   ```

2. **Reload MayaLib menu**:
   - Click the reload button in the MayaLib menu
   - Or restart Maya

3. **Check for errors** in Script Editor during menu creation

---

## Luna Resources

### Documentation

- Luna README: `luna/README.md`
- Luna Wiki: `luna/WIKI.md`

### Sample Files

- [Luna Sample Files](https://github.com/S0nic014/luna_sample_files) - Python and graph-based rig builds

### Video Tutorials

- [Luna Demo Video](https://www.youtube.com/watch?v=0FLPQ91r0To&)

---

## See Also

- [MayaLib Home](Home.md)
- [RigLib](RigLib.md) - DevPyLib rigging system
- [GuiLib](GuiLib.md) - Menu integration
- [Luna Wiki](../../luna/WIKI.md) - Full Luna documentation

---

*Last updated: January 2026*

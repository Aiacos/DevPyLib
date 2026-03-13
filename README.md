# DevPyLib

[![Build Status](https://github.com/Aiacos/DevPyLib/actions/workflows/ci.yml/badge.svg)](https://github.com/Aiacos/DevPyLib/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/gh/Aiacos/DevPyLib/branch/master/graph/badge.svg)](https://codecov.io/gh/Aiacos/DevPyLib)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![License](https://img.shields.io/github/license/Aiacos/DevPyLib)](https://github.com/Aiacos/DevPyLib/blob/master/LICENSE)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)

**DevPyLib** is a comprehensive development library for DCC (Digital Content Creation) applications, with primary support for **Autodesk Maya** and ongoing development for **Houdini** and **Blender**.

It provides professional-grade tools for rigging, animation, simulations, shading, modeling, and pipeline management for VFX and animation studios.

---

## 🎯 Features

- 🎨 **Advanced Rigging** - Modular system with Ziva VFX and AdonisFX support
- 💧 **Fluid Simulations** - Smoke, fire, explosion with modular base system
- 🔷 **Bifrost/USD Integration** - Full support for Bifrost graphs and USD pipeline
- 🎭 **Animation Tools** - BVH importer and animation utilities
- 🖼️ **Lookdev & Shading** - HDRI compensation, shader utilities
- 🛠️ **Modeling Tools** - UV tools, quad patcher, mesh utilities
- 🚀 **Pipeline Integration** - Naming conventions, workspace management
- 🖥️ **Automatic GUI** - Introspective system to generate UI from Python functions
- 🔌 **Plugin System** - Maya C++ API plugins (tension map, mesh collision)
- 🌍 **Cross-Platform** - Windows, Linux, macOS
- ⚡ **Lazy Loading** - Fast startup with on-demand module loading (93% faster imports)

---

## ⚡ Performance & Lazy Loading

DevPyLib uses **lazy loading** to minimize Maya startup time. Modules are loaded on-demand when first accessed, not during initial import.

### Performance Improvements

- **93.3% faster imports**: `import mayaLib` completes in ~1.3ms (vs. ~18.8ms with eager loading)
- **Reduced memory footprint**: Only loaded modules consume memory
- **Deferred heavy imports**: Ziva, AdonisFX, Bifrost load only when needed

### How It Works

All modules use Python's `__getattr__` pattern for lazy loading:

```python
import mayaLib  # Fast! Only imports the base package (~1.3ms)

# Modules load on first access:
from mayaLib import rigLib  # Loads rigLib now
from mayaLib.fluidLib import fire  # Loads fluidLib, then fire
```

### Backwards Compatibility

**100% backwards compatible** - all existing code works unchanged:

```python
# All import patterns work identically
import mayaLib
from mayaLib import rigLib
import mayaLib.rigLib
from mayaLib.rigLib import base
from mayaLib.rigLib.utils import control
```

### Behavioral Changes

- **First access**: Slightly slower (includes import time)
- **Subsequent access**: Instant (modules are cached)
- **Error messages**: Import failures occur on first access, not at startup

---

## 📋 Requirements

- **Autodesk Maya** 2022-2026
- **Python** 3.9+ (included with Maya)
- **Git** (to clone the repository)

### Python Dependencies

Dependencies are installed automatically on first Maya startup:

```
numpy
pymel
GitPython (optional)
```

> **Note for Maya 2026**: PyMEL 1.5.0 (PyPI) does not support Maya 2026. Install [pymel 1.6.0rc2](https://github.com/iamsleepy/pymel/releases/tag/1.6.0rc2) from iamsleepy's fork instead.

---

## 🚀 Installation

DevPyLib supports **flexible installation** on any operating system without manual configuration.

### 1. Clone the Repository

Clone DevPyLib **anywhere** on your system (the path will be auto-detected):

```bash
# Recommended location
cd ~/Documents/workspace  # Linux/macOS
cd %USERPROFILE%\Documents\workspace  # Windows

# Clone repository
git clone https://github.com/Aiacos/DevPyLib.git
cd DevPyLib

# Update submodules
git submodule update --init --recursive
```

### 2. Install Configuration Files

Use the included installer scripts to copy `Maya.env` and `userSetup.py` to the correct Maya directories:

#### Windows

```batch
cd DevPyLib
install.bat
```

#### Linux / macOS

```bash
cd DevPyLib
./install.sh
```

The installer will:
- Detect installed Maya versions (2024-2026)
- Copy `Maya.env` to each version's directory (`maya/{version}/Maya.env`)
- Copy `userSetup.py` to the shared scripts directory (`maya/scripts/userSetup.py`)
- Ask before overwriting existing files

#### Manual Installation

If you prefer to install manually, copy the files yourself:

| Source | Destination |
|--------|------------|
| `mayaLib/Maya.env` | `~/Documents/maya/{version}/Maya.env` |
| `mayaLib/userSetup.py` | `~/Documents/maya/scripts/userSetup.py` |

### 3. Launch Maya

On Maya startup, you'll see:

```
DevPyLib detected at: /path/to/DevPyLib
All requirements installed successfully!
Added /path/to/DevPyLib to sys.path
Imported mayaLib
Maya command port opened on: 4434
DevPyLib setup complete!
```

The **DevPyLib** menu will appear automatically in Maya's interface! 🎉

---

## 📁 Project Structure

```
DevPyLib/
├── mayaLib/                    # Main Maya library (~28K LOC)
│   ├── animationLib/          # Animation tools
│   ├── ariseLib/              # Arise rig system (HumanIK, face rig)
│   ├── bifrostLib/            # Bifrost graph and USD integration
│   ├── fluidLib/              # Fluid system (smoke, fire, explosion)
│   ├── guiLib/                # Automatic GUI system
│   ├── lookdevLib/            # Lookdev and shading tools
│   ├── modelLib/              # Modeling utilities
│   ├── pipelineLib/           # Pipeline and naming conventions
│   ├── plugin/                # Maya C++ API plugins
│   ├── rigLib/                # Modular rigging system
│   │   ├── base/             # Base modules (Limb, Spine, Face, etc.)
│   │   ├── utils/            # 31+ utility modules
│   │   ├── Ziva/             # Ziva VFX integration
│   │   └── AdonisFX/         # AdonisFX integration
│   ├── shaderLib/            # Shader utilities
│   ├── usdLib/               # USD export/import
│   └── utility/              # General utilities
├── houdiniLib/               # Houdini tools and HDAs
├── blenderLib/               # Blender tools (in development)
├── prismLib/                 # Prism Pipeline integration
├── pyfrost/                  # Bifrost utilities (git submodule)
├── tools/                    # Standalone tools
├── wiki/                     # Complete documentation
│   ├── MayaLib/             # MayaLib documentation
│   ├── HoudiniLib/          # HoudiniLib documentation
│   └── BlenderLib/          # BlenderLib documentation
├── install.bat               # Windows installer (copies Maya.env + userSetup.py)
├── install.sh                # Linux/macOS installer
└── requirements.txt          # Python dependencies
```

---

## 🎓 Basic Usage

### Automatic GUI System

DevPyLib automatically generates UI for Python functions:

```python
import mayaLib.guiLib.main_menu as mm

# Menu is created automatically
# All functions with docstrings appear in the menu
```

### Example: Create Base Rig

```python
from mayaLib.rigLib.base.module import Base

# Create base rig structure
rig = Base(characterName='Character01', scale=1.0)

# Structure is created automatically:
# - Character01_rig_GRP/
#   - global_CTRL
#   - main_CTRL
#   - model_GRP/
#   - rig_GRP/
#   - skeleton_GRP/
```

### Example: Fluids

```python
from mayaLib.fluidLib.smoke import Smoke

# Create smoke system
smoke = Smoke()
```

### Example: Bifrost + USD

```python
from mayaLib.bifrostLib import bifrost_api

# Create Bifrost graph
graph = bifrost_api.create_bifrost_graph(name='myGraph')

# Get USD stage
stage = bifrost_api.get_maya_usd_stage()
```

---

## 🔧 Advanced Configuration

### Environment Variables

The `mayaLib/Maya.env` file configures environment variables per Maya version. Key variables:

| Variable | Purpose |
|----------|---------|
| `DEVPYLIB_PATH` | Path to DevPyLib root directory |
| `PYTHONPATH` | Set to `DEVPYLIB_PATH` for Python imports |
| `BIFROST_LIB_CONFIG_FILES` | Path to custom Bifrost compound libraries |
| `DEVPYLIB_DISABLE_LUNA` | Set to `1` to disable Luna loading at startup |

### Disabling Luna

To prevent Luna from loading at startup (recommended if not using Luna):

```env
# In Maya.env
DEVPYLIB_DISABLE_LUNA=1
```

This blocks Luna at all levels: Python import, menu discovery, and UI button.

### Auto-Update from Git

Uncomment in `userSetup.py` to enable automatic git pull on startup:

```python
# userSetup.py - line 98
git_pull_gitpython(libDir, branch="master")  # Remove comment
```

### Command Port

Maya automatically opens command port `4434` for external connections. To change:

```python
# userSetup.py - line 91
port = "4434"  # Change port number
```

---

## 🧪 Testing

### Verify Installation

1. Open Maya
2. Open Script Editor (Python)
3. Run:

```python
import mayaLib
print(mayaLib.__file__)  # Should show correct path
```

### Test Scripts

Tests are in `mayaLib/test/`:

```python
# In Maya Script Editor
execfile('/path/to/DevPyLib/mayaLib/test/MayaLib.py')
```

---

## 📚 Documentation

### Wiki

Complete documentation is available in the **[wiki/](wiki/)** folder:

| Section | Description |
|---------|-------------|
| [Home](wiki/Home.md) | Overview and navigation |
| [Architecture](wiki/Architecture.md) | Design patterns and structure |
| [API Reference](wiki/API-Reference.md) | Quick API reference |
| [Cross-Platform](wiki/Cross-Platform.md) | Platform compatibility guide |
| [Contributing](wiki/Contributing.md) | Contribution guidelines |

#### MayaLib Documentation
| Page | Description |
|------|-------------|
| [MayaLib Home](wiki/MayaLib/Home.md) | MayaLib overview |
| [Getting Started](wiki/MayaLib/Getting-Started.md) | Setup guide |
| [RigLib](wiki/MayaLib/RigLib.md) | Rigging library |
| [AnimationLib](wiki/MayaLib/AnimationLib.md) | Animation tools |
| [FluidLib](wiki/MayaLib/FluidLib.md) | Fluid simulations |
| [BifrostLib](wiki/MayaLib/BifrostLib.md) | Bifrost/USD integration |
| [GuiLib](wiki/MayaLib/GuiLib.md) | UI framework |

#### Other DCCs
- [HoudiniLib](wiki/HoudiniLib/Home.md) - Houdini tools and HDAs
- [BlenderLib](wiki/BlenderLib/Home.md) - Blender utilities

### Other Documentation

- **CHANGELOG.md** - Version history and changes
- **CLAUDE.md** - Detailed architecture and patterns for developers
- **CROSS_PLATFORM_MIGRATION.md** - Cross-platform migration notes
- **Inline docs** - All functions have complete docstrings

### Online Resources

- **Repository**: https://github.com/Aiacos/DevPyLib
- **Issues**: https://github.com/Aiacos/DevPyLib/issues

---

## 🛠️ Development

### Architecture

DevPyLib uses a layered modular architecture:

- **Base Classes** - Foundations for rigs, fluids, UI (`*/base/`)
- **Utility Layer** - Reusable orthogonal functions (`*/utils/`)
- **Specialized Systems** - Domain-specific implementations
- **GUI Layer** - Automatic UI generation via introspection

See `CLAUDE.md` for complete architecture details.

### Contributing

1. Create a branch for changes: `git checkout -b feature/feature-name`
2. Follow code conventions (see below)
3. Test on at least 2 platforms (Windows/Linux/macOS)
4. Create Pull Request

### Code Style

```python
# Use PyMEL for Maya operations
import pymel.core as pm

# Use pathlib for paths
from pathlib import Path

# Naming conventions
_GRP   # For groups
_CTRL  # For controls
_LOC   # For locators
_JNT   # For joints

# Docstrings for all functions (used by GUI)
def myFunction(param1, param2=True):
    """
    Brief function description.

    Args:
        param1 (str): Parameter description
        param2 (bool): Description with default

    Returns:
        type: Return description
    """
    pass
```

### Cross-Platform Guidelines

- ✅ Always use `pathlib.Path` for path operations
- ✅ Use `subprocess.run()` instead of `os.system()`
- ✅ Use `shutil` instead of shell commands (`rm`, `cp`, etc.)
- ✅ Test on Windows, Linux, and macOS when possible
- ❌ Don't use hardcoded paths
- ❌ Don't use manual path separators (`/` or `\`)

### Branch Protection Rules

To maintain code quality and ensure stable releases, we recommend configuring the following branch protection rules for the `main`/`master` branch:

#### Required Settings

| Rule | Description |
|------|-------------|
| **Require status checks before merging** | All CI jobs (lint, test) must pass before a PR can be merged |
| **Require pull request reviews** | At least 1 reviewer approval required before merging |
| **Require branches to be up to date** | Branch must be current with base branch before merging |

#### Recommended Settings

| Rule | Description |
|------|-------------|
| **Require linear history** | Prevents merge commits, enforces rebase/squash workflow |
| **Require signed commits** | Ensures commit authenticity (optional) |
| **Include administrators** | Applies rules to repository admins as well |

#### How to Configure (GitHub)

1. Go to **Settings** → **Branches** in your repository
2. Under "Branch protection rules", click **Add rule**
3. Enter `main` (or `master`) as the branch name pattern
4. Enable the desired protection rules
5. Click **Create** to save

#### CI Status Checks

The following status checks should be required to pass:

- `lint` - Ruff linting and formatting checks
- `test (3.9)` - pytest on Python 3.9
- `test (3.10)` - pytest on Python 3.10
- `test (3.11)` - pytest on Python 3.11

See `.github/workflows/ci.yml` for the complete CI pipeline configuration.

---

## 🔍 Troubleshooting

### Menu Doesn't Appear

```python
# Check in Script Editor
import sys
print('/path/to/DevPyLib' in sys.path)  # Must be True

import mayaLib.guiLib.main_menu as mm
mm.MainMenu('/path/to/DevPyLib')  # Create menu manually
```

### Missing Dependencies

```bash
# Install manually if needed
mayapy -m pip install -r /path/to/DevPyLib/requirements.txt
```

### GitPython Not Available

GitPython is **optional**. If missing, you'll see:
```
GitPython not available - git operations disabled
```

To install:
```bash
mayapy -m pip install GitPython
```

### Path Not Detected Correctly

Verify the symlink:

```bash
# Linux/macOS
ls -la ~/maya/scripts/userSetup.py

# Windows (PowerShell)
Get-Item $env:USERPROFILE\Documents\maya\scripts\userSetup.py | Select-Object Target
```

---

## 📊 Compatibility

| Operating System | Maya Version | Status |
|------------------|--------------|--------|
| Windows 10/11    | 2022-2026    | ✅ Tested |
| Linux (Ubuntu/CentOS/Rocky) | 2022-2026 | ✅ Tested |
| macOS (Intel)    | 2022-2025    | ✅ Tested |
| macOS (Apple Silicon) | 2022-2026 | ✅ Tested (Rosetta) |

---

## 📝 License

See `LICENSE` file for details.

---

## 👤 Author

**Lorenzo Argentieri**

---

## 📮 Support

- **Issues**: https://github.com/Aiacos/DevPyLib/issues
- **Discussions**: https://github.com/Aiacos/DevPyLib/discussions

---

**Happy creating with DevPyLib! 🎨✨**

# DevPyLib

[![Build Status](https://github.com/Aiacos/DevPyLib/actions/workflows/ci.yml/badge.svg)](https://github.com/Aiacos/DevPyLib/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/gh/Aiacos/DevPyLib/branch/master/graph/badge.svg)](https://codecov.io/gh/Aiacos/DevPyLib)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![License](https://img.shields.io/github/license/Aiacos/DevPyLib)](https://github.com/Aiacos/DevPyLib/blob/master/LICENSE)
[![Python](https://img.shields.io/badge/python-3.7%2B-blue)](https://www.python.org/)

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

---

## 📋 Requirements

- **Autodesk Maya** 2020+ (tested on 2022-2025)
- **Python** 3.7+ (included with Maya)
- **Git** (to clone the repository)

### Python Dependencies

Dependencies are installed automatically on first Maya startup:

```
numpy
pathlib
pymel
GitPython (optional)
```

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

### 2. Create Symlink to userSetup.py

Link `userSetup.py` to your Maya scripts folder for automatic loading.

#### Linux

```bash
# Create directory if it doesn't exist
mkdir -p ~/maya/scripts

# Create symlink (recommended - auto-updates)
ln -s ~/Documents/workspace/DevPyLib/userSetup.py ~/maya/scripts/userSetup.py

# Alternative: if Maya uses ~/Documents/maya
mkdir -p ~/Documents/maya/scripts
ln -s ~/Documents/workspace/DevPyLib/userSetup.py ~/Documents/maya/scripts/userSetup.py
```

#### macOS

```bash
# Create directory if it doesn't exist
mkdir -p ~/Library/Preferences/Autodesk/maya/scripts

# Create symlink
ln -s ~/Documents/workspace/DevPyLib/userSetup.py \
      ~/Library/Preferences/Autodesk/maya/scripts/userSetup.py
```

#### Windows

**Option A: PowerShell (Administrator) - Symlink (Recommended)**

```powershell
# Open PowerShell as Administrator
# Create directory if it doesn't exist
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\Documents\maya\scripts"

# Create symlink (change source path if needed)
New-Item -ItemType SymbolicLink `
         -Path "$env:USERPROFILE\Documents\maya\scripts\userSetup.py" `
         -Target "$env:USERPROFILE\Documents\workspace\DevPyLib\userSetup.py"
```

**Option B: Manual Copy**

If you cannot create symlinks, simply copy the file:

```powershell
Copy-Item "$env:USERPROFILE\Documents\workspace\DevPyLib\userSetup.py" `
          "$env:USERPROFILE\Documents\maya\scripts\userSetup.py"
```

⚠️ **Note**: With manual copy, you'll need to update the file whenever there are changes.

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
├── userSetup.py              # Maya auto-loader
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

### Environment Variables (Optional)

If you want to manually configure `Maya.env`:

**Linux/macOS**: `~/maya/<version>/Maya.env`
**Windows**: `%USERPROFILE%\Documents\maya\<version>\Maya.env`

```bash
# Add to Maya.env
MAYA_APP_DIR = /path/to/DevPyLib
PYTHONPATH = /path/to/DevPyLib
```

⚠️ **Not required** if using userSetup.py (recommended).

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
| Windows 10/11    | 2020-2025    | ✅ Tested |
| Linux (Ubuntu/CentOS/Rocky) | 2020-2025 | ✅ Tested |
| macOS (Intel)    | 2020-2025    | ✅ Tested |
| macOS (Apple Silicon) | 2022-2025 | ✅ Tested (Rosetta) |

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

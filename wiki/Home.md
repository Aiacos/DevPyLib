# DevPyLib Wiki

Welcome to the **DevPyLib** documentation wiki. DevPyLib is a comprehensive development library for Digital Content Creation (DCC) applications, primarily targeting Autodesk Maya with emerging support for Houdini and Blender. It provides professional-grade utilities for rigging, animation, simulation, shading, modeling, and pipeline management used in VFX and animation studio workflows.

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Documentation by DCC Application](#documentation-by-dcc-application)
- [Architecture](#architecture)
- [Additional Resources](#additional-resources)

---

## Overview

DevPyLib is designed to streamline DCC workflows across multiple applications. The library is organized into modular components that can be used independently or together to build complete production pipelines.

### Supported Applications

| Application | Status | Library |
|-------------|--------|---------|
| **Autodesk Maya** | Primary Support (~28K LOC) | [MayaLib](MayaLib/Home.md) |
| **Houdini** | Emerging Support | [HoudiniLib](HoudiniLib/Home.md) |
| **Blender** | Minimal Support | [BlenderLib](BlenderLib/Home.md) |

### Repository Structure

```
DevPyLib/
├── mayaLib/          # Primary Maya utilities (~28K LOC)
│   ├── rigLib/       # Character rigging (Ziva, AdonisFX integration)
│   ├── bifrostLib/   # Bifrost graph/USD integration
│   ├── fluidLib/     # Fluid simulation utilities
│   ├── animationLib/ # Animation tools (BVH importer, etc.)
│   ├── modelLib/     # Modeling utilities (UV, quad patcher)
│   ├── shaderLib/    # Shader/lookdev tools
│   ├── guiLib/       # UI framework with introspection-based widget generation
│   ├── pipelineLib/  # Pipeline utilities (naming conventions, workspace)
│   ├── lunaLib/      # Luna rigging framework integration
│   ├── plugin/       # Maya Python API 2.0 plugins
│   └── test/         # Integration test scripts
├── houdiniLib/       # Houdini utilities
│   └── HDAs/         # Houdini Digital Assets
├── blenderLib/       # Blender utilities (minimal)
├── prismLib/         # Prism Pipeline integration
├── luna/             # Luna rigging framework (git submodule)
└── pyfrost/          # Bifrost Python utilities (git submodule)
```

---

## Key Features

### Rigging (rigLib)
- **Modular rig construction** with base classes for consistent hierarchy
- **IK/FK limb systems** with stretchy IK and pole vector placement
- **Spine, neck, and face rigging** components
- **Control creation** with automatic shape, color, and grouping
- **Skin utilities** including ngSkinTools2 integration
- **External integrations**: Ziva Dynamics, AdonisFX muscle simulation
- **Luna integration** for node-based rig building

### Animation (animationLib)
- **BVH motion capture importer** with retargeting support
- Scale and rotation order options

### Modeling (modelLib)
- **Quad Patcher** for automatic quad topology generation
- **UV utilities** for UV layout and optimization
- Display layer management

### Shading (shaderLib)
- **Multi-renderer support**: Arnold, RenderMan, 3Delight
- **Automatic texture shader creation** from texture directories
- Batch shader building from organized texture folders

### Fluid Simulation (fluidLib)
- **Preset-based fluid creation**: Smoke, Fire, Explosion
- Automatic container and emitter setup
- Shading presets for realistic fluid rendering

### Bifrost/USD (bifrostLib)
- **USD stage building** from Maya scenes
- **Bifrost graph API** for node creation and manipulation
- Integration with Maya USD proxy stages

### UI Framework (guiLib)
- **Introspection-based UI generation** from function signatures
- Automatic widget creation (checkboxes for booleans, line edits for text)
- Dynamic menu system with searchable function library
- Fill-from-selection buttons for Maya integration

### Pipeline (pipelineLib)
- Naming convention validation
- Workspace utilities
- USD/Maya unit coordination
- Documentation extraction for UI tooltips

### Plugins
- **TensionMap**: Mesh deformation visualization via vertex colors
- **MeshCollision**: Collision detection utilities

---

## Quick Start

### Basic Usage in Maya

```python
# Import the main library
import mayaLib

# Create a basic rig structure
from mayaLib.rigLib.base.module import Base
rig = Base(character_name="myCharacter", scale=1.0)

# Create a control
from mayaLib.rigLib.utils.control import Control
ctrl = Control(
    prefix="arm",
    scale=1.0,
    shape="circle",
    lock_channels=["s", "v"]
)

# Create a smoke simulation
from mayaLib.fluidLib.smoke import WispySmoke
smoke = WispySmoke(fluid_name="mySmoke", base_res=32)

# Create a shader from textures
from mayaLib.shaderLib.shader import TextureShader
shader = TextureShader(
    texture_path="/textures/",
    geo_name="character",
    textureset_dict={'diffuse': 'char_diffuse.exr'}
)
```

### Using the Menu System

After installation, DevPyLib adds a **MayaLib** menu to Maya's main menu bar with:
- Searchable function library
- Categorized tools by discipline (Modeling, Rigging, Animation, VFX, Lookdev, Luna)
- Auto-generated UIs for each function

---

## Installation

### Prerequisites
- Maya 2024 or later (Python 3.9+)
- Git (for submodules)

### Dependencies
```
numpy
pathlib
pymel
GitPython
ngSkinTools2 (optional, for advanced skin weighting)
```

### Step-by-Step Installation

1. **Clone the repository** anywhere on your system:
   ```bash
   git clone --recursive https://github.com/your-repo/DevPyLib.git
   ```

2. **Update submodules** (if not using `--recursive`):
   ```bash
   cd DevPyLib
   git submodule update --init --recursive
   ```

3. **Create a symlink or copy** `userSetup.py` to Maya's scripts directory:
   - **Windows**: `%USERPROFILE%\Documents\maya\scripts\`
   - **Linux**: `~/maya/scripts/` or `~/Documents/maya/scripts/`
   - **macOS**: `~/Library/Preferences/Autodesk/maya/scripts/`

4. **Start Maya** - Dependencies auto-install on first startup via pip.

### Environment Variables (Optional)

The `mayaLib/Maya.env` file shows example environment variables:
```
MAYA_APP_DIR = C:/path/to/DevPyLib/mayaLib
PYTHONPATH = C:/path/to/DevPyLib
MAYA_MODULE_PATH = C:/path/to/DevPyLib/mayaLib
MAYA_PLUG_IN_PATH = C:/path/to/DevPyLib/mayaLib/plugin
```

### Auto-Detection

The `userSetup.py` uses `Path(__file__).parent.resolve()` to automatically detect the DevPyLib location, enabling flexible installation paths without hardcoding.

---

## Documentation by DCC Application

### Maya Documentation

| Page | Description |
|------|-------------|
| [MayaLib Home](MayaLib/Home.md) | Overview of MayaLib components |
| [Getting Started](MayaLib/Getting-Started.md) | Installation and setup for Maya |
| [RigLib](MayaLib/RigLib.md) | Character rigging library |
| [AnimationLib](MayaLib/AnimationLib.md) | Animation tools |
| [ModelLib](MayaLib/ModelLib.md) | Modeling utilities |
| [ShaderLib](MayaLib/ShaderLib.md) | Shader and lookdev tools |
| [FluidLib](MayaLib/FluidLib.md) | Fluid simulation utilities |
| [BifrostLib](MayaLib/BifrostLib.md) | Bifrost/USD integration |
| [GuiLib](MayaLib/GuiLib.md) | UI framework documentation |
| [PipelineLib](MayaLib/PipelineLib.md) | Pipeline utilities |
| [LunaLib](MayaLib/LunaLib.md) | Luna rigging framework integration |

### Houdini Documentation

| Page | Description |
|------|-------------|
| [HoudiniLib Home](HoudiniLib/Home.md) | Overview of HoudiniLib |
| [HDAs](HoudiniLib/HDAs.md) | Houdini Digital Assets documentation |

### Blender Documentation

| Page | Description |
|------|-------------|
| [BlenderLib Home](BlenderLib/Home.md) | Overview of BlenderLib |

---

## Architecture

For detailed information about the library's architecture, design patterns, and code organization, see the [Architecture](Architecture.md) page.

Key architectural concepts:
- **Base Class Pattern**: Foundational classes for consistent rig hierarchies
- **Utility Layer**: Modular utilities for orthogonal concerns
- **Introspection-based UI**: Automatic widget generation from function signatures
- **Multi-DCC Support**: Host application detection for DCC-agnostic tools

---

## Additional Resources

| Page | Description |
|------|-------------|
| [Architecture](Architecture.md) | Design patterns and code organization |
| [API Reference](API-Reference.md) | Cross-DCC API reference |
| [Cross-Platform](Cross-Platform.md) | Cross-platform compatibility notes |
| [Contributing](Contributing.md) | How to contribute to DevPyLib |

---

## Code Quality

DevPyLib maintains high code quality standards:
- **Linting**: Ruff with Black-compatible formatting
- **Type Hints**: Modern Python 3.9+ type annotations
- **Docstrings**: Google-style documentation
- **93.9% violation reduction** achieved through comprehensive refactoring

---

## License

DevPyLib is released under the GNU General Public License v3.0.

---

## Support

For issues, feature requests, or contributions, please visit the project repository or open an issue.

---

*Last updated: January 2026*

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

DevPyLib is a comprehensive development library for DCC (Digital Content Creation) applications, primarily targeting Autodesk Maya with emerging support for Houdini and Blender. It provides professional-grade utilities for rigging, animation, simulation, shading, modeling, and pipeline management used in VFX and animation studio workflows.

## Repository Structure

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
│   ├── plugin/       # Maya C++ API plugins (tensionMap, meshCollision)
│   └── test/         # Integration test scripts
├── houdiniLib/       # Houdini utilities
│   └── HDAs/         # Houdini Digital Assets
├── blenderLib/       # Blender utilities (minimal)
├── prismLib/         # Prism Pipeline integration
└── pyfrost/          # Git submodule - Bifrost Python utilities
```

## Development Setup

### Installation

This library is **fully cross-platform** (Windows, Linux, macOS) and uses automatic path detection.

1. Clone repository anywhere on your system (no hardcoded paths required)
2. Create symlink or copy `userSetup.py` to Maya scripts directory:
   - **Linux**: `~/maya/scripts/` or `~/Documents/maya/scripts/`
   - **macOS**: `~/Library/Preferences/Autodesk/maya/scripts/`
   - **Windows**: `%USERPROFILE%\Documents\maya\scripts\`
3. Dependencies auto-install on first Maya startup via `subprocess.run([sys.executable, "-m", "pip", "install", "-r", requirements.txt])`

**Auto-detection**: userSetup.py uses `Path(__file__).parent.resolve()` to detect DevPyLib location automatically, enabling flexible installation paths.

### Dependencies

```
numpy
pathlib
pymel         # PyMEL is the primary Maya API wrapper used throughout
GitPython
```

The codebase uses **PyMEL** (`pymel.core`) as the standard Maya API interface, not `maya.cmds`. Qt UI uses PySide2/PySide6 with automatic fallback.

### Maya Environment

The `mayaLib/Maya.env` file shows example environment variables for Windows:
- Sets `MAYA_APP_DIR` and `PYTHONPATH` to library location
- Configure `MAYA_MODULE_PATH` and `MAYA_PLUG_IN_PATH` as needed

## Architecture Patterns

### Base Class Pattern

Most submodules follow a layered architecture with foundational base classes:

- **rigLib**: `rigLib/base/module.py::Base` creates standard rig hierarchy (topGrp, modelGrp, rigGrp, jointsGrp, modulesGrp)
  - All rig modules inherit and extend this hierarchy
  - Example subclasses: `Limb`, `IKChain`, `Spine`, `Face`, `Neck` in `rigLib/base/`

- **fluidLib**: `fluidLib/base/baseFluid.py::BaseFluid` composes FluidContainer + FlEmitter
  - Concrete implementations: `smoke.py`, `fire.py`, `explosion.py`, `fireSmoke.py`

- **guiLib**: `guiLib/base/baseUI.py::FunctionUI` - Introspective UI generator
  - Uses Python's `inspect` module to auto-generate Qt widgets from function signatures
  - Automatically handles type conversion (bool→checkbox, numeric→lineedit)
  - Bridges Maya selection with UI parameter population

### Utility Layer

Heavy use of utility modules for orthogonal concerns (see `rigLib/utils/` with 31+ utilities):
- Transform utilities: `joint.py`, `control.py`, `transform.py`
- Deformation: `deform.py`, `dynamic.py`, `flexiplane.py`
- Rigging helpers: `ikfkSwitch.py`, `footRoll.py`, `humanIK.py`
- External integrations: Ziva, AdonisFX, nCloth

### GUI System

The `guiLib/mainMenu.py::MainMenu` creates dynamic menus that:
1. Discover available functions via introspection (`pipelineLib/utility/listFunction.py`)
2. Generate UI widgets automatically using `FunctionUI`
3. Load lazily via `importlib` for performance
4. Created deferred on Maya startup (see `userSetup.py:79`)

### Plugin Architecture

Maya plugins in `mayaLib/plugin/` use Maya Python API 2.0:
- Must include `maya_useNewAPI()` function
- Extend `om.MPxNode` or `om.MPxCommand`
- Example: `tensionMap.py` for mesh tension calculation
- Load via `mayaLib/test/MayaLib.py` plugin (registers `MayaLib` command)

### Pipeline Integration

The `pipelineLib/utility/` provides studio pipeline conventions:
- `nameCheck.py` - Naming convention validation
- `convention.py` - Asset naming rules
- `space_unit.py` - USD/Maya unit coordination (see recent commit: "Configures USD export unit based on Maya settings")
- `docs.py` - Documentation extraction for UI tooltips

### Bifrost/USD Integration

`bifrostLib/` bridges Maya Bifrost graphs with USD:
- `bifrost_api.py` - Low-level Bifrost/USD stage creation
- `stage_builder.py` - High-level composition of Bifrost graphs + Maya USD proxy
- Uses `maya.mel` for Bifrost MEL commands, `maya.cmds` for USD integration

### Git Submodule

The `pyfrost/` directory is a git submodule from https://github.com/BenoitGielly/pyfrost.git
- Update with: `git submodule update --init --recursive`

## Testing

Tests are located in `mayaLib/test/` and are integration-style (full scene operations):
- `MayaLib.py` - Plugin registration example
- `Facial3.py`, `rope.py`, `collisionDeformer.py` - Example usage scripts
- No formal unit test framework; tests are example scripts that demonstrate usage

Run tests by executing Python scripts inside Maya:
```python
# In Maya Script Editor
execfile('/path/to/mayaLib/test/MayaLib.py')
```

## Key Technical Details

### Control System
The `rigLib/utils/control.py::Control` class is central to all rigging:
- Creates controls with consistent hierarchy (offset groups, modify groups)
- Shape management via `ctrlShape.py`
- Color coding via `colorControl.py`

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

### Multi-DCC Support
`prismLib/pipeline.py::detect_host_app()` detects Maya vs Houdini by checking `sys.modules`:
- Returns "Maya" if `maya.cmds` loaded
- Returns "Houdini" if `hou` loaded
- Use this pattern when creating DCC-agnostic tools

## Common Workflows

### Creating New Rig Modules
1. Inherit from `rigLib/base/module.py::Base`
2. Override `__init__()` to create module-specific joints/controls
3. Use `rigLib/utils/control.py::Control` for all rig controls
4. Add to `rigLib/utils/` if generic utility, or `rigLib/base/` if structural module

### Adding UI for Functions
The `FunctionUI` system auto-generates UIs:
1. Write function with type-hinted parameters and defaults
2. Add comprehensive docstring (displayed in UI via `docs.py`)
3. UI appears automatically in MainMenu system
4. Use `>` button in UI to populate from Maya selection

### Working with Bifrost
1. Create Bifrost graph: `bifrost_api.create_bifrost_graph()`
2. Create USD stage: `bifrost_api.get_maya_usd_stage()`
3. Use `stage_builder.py` for high-level composition
4. Connect to Maya geometry via `bifrostGeoToMaya` node

### Plugin Development
See `mayaLib/plugin/tensionMap.py` for reference:
1. Include `maya_useNewAPI()` at module level
2. Create node class extending `om.MPxNode`
3. Implement `initializePlugin()` and `uninitializePlugin()`
4. Register with `MFnPlugin.registerNode()`

## Code Style

- **Maya API**: Use PyMEL (`import pymel.core as pm`) for all Maya operations
- **Qt**: PySide2/PySide6 with try/except fallback pattern
- **Naming**: Rig objects use suffixes: `_GRP`, `_CTRL`, `_LOC`, `_JNT`
- **Attributes**: Custom attributes stored as locked strings on top group
- **Documentation**: Include docstrings for all functions (used by UI system)

## Cross-Platform Compatibility

DevPyLib is fully compatible with Windows, Linux, and macOS:

### Path Handling
- Always use `pathlib.Path` for path operations (never hardcode paths)
- Use `Path(__file__).parent` for relative path detection
- Avoid OS-specific path separators (`/` vs `\`) - let pathlib handle it

### Platform Detection
Use `platform.system()` which returns:
- `"Windows"` for Windows
- `"Linux"` for Linux
- `"Darwin"` for macOS (not "OSX")

### Shell Commands
- **Never use** `os.system()` for shell commands
- Use `subprocess.run()` with proper arguments list
- For file operations, prefer `shutil` and `zipfile` over shell commands (`rm`, `unzip`, etc.)

### Example Cross-Platform Code
```python
import platform
import subprocess
import shutil
from pathlib import Path

# Good: Cross-platform path
maya_scripts = Path.home() / "maya" / "scripts"

# Good: Platform-specific logic
if platform.system() == "Darwin":  # macOS
    maya_prefs = Path.home() / "Library" / "Preferences" / "Autodesk" / "maya"

# Good: subprocess instead of os.system
subprocess.run([sys.executable, "-m", "pip", "install", "package"])

# Good: shutil instead of shell commands
shutil.rmtree(directory_path)
```

See `CROSS_PLATFORM_MIGRATION.md` for detailed migration notes.

## Development History

### Refactoring Session (2025-01-06)

Comprehensive code quality improvements and refactoring on the `refactoring` branch:

#### Phase 1: Initial Fixes
- **Commit 04fc518**: Fixed Neovim `.nvim.lua` warnings (undefined global vim)
  - Added `---@diagnostic disable: undefined-global` directive

#### Phase 2: Deep File Analysis
- **Commit 32bae8b**: Fixed `bvh_importer.py` (21 ruff + 4 basedpyright errors)
  - Removed `(object)` inheritance (UP004)
  - Converted % formatting to f-strings (8 instances)
  - Fixed docstrings (D200, D415, D105)
  - Changed `f.next()` → `next(f)` (Python 3)
  - Added None checks for type safety
  - Split long lines (E501)

- **Commit b7b1928**: Fixed `ariseLib/base.py` docstring issues
  - Added missing parameter documentation (D417)
  - Fixed D202 violations

#### Phase 3: Mass Auto-Fix (83 files)
- **Commit ecc44e3**: Applied `ruff check --fix --unsafe-fixes`
  - 769 violations automatically fixed
  - UP004 (object inheritance): 15 fixes
  - UP006 (PEP 585 annotations): 35 fixes
  - UP034 (extraneous parentheses): 27 fixes
  - D202 (blank after docstring): 54 fixes
  - D208 (over-indentation): 42 fixes
  - B010 (setattr constant): 13 fixes

#### Phase 4: Comprehensive Formatting (98 files)
- **Commit 80ce562**: Applied `ruff format` for Black-compatible formatting
  - 98 files reformatted
  - 5954 insertions(+), 4361 deletions(-)
  - E501 line length: 566 → 107 (459 fixes)
  - D415 punctuation: 144 → 7 (137 fixes)
  - UP031 f-strings: 120 → 10 (110 additional fixes)

#### Phase 5: Final Docstring Cleanup
- **Commit 75e62e4**: Fixed empty docstring sections (D414)
  - Fixed 13 functions across 3 files
  - `bifrost_api.py`: Added Returns for bf_rename_node
  - `stage_builder.py`: Fixed 7 functions
  - `skin.py`: Fixed 4 functions

#### Overall Impact
- **Total automated fixes**: 1,236+ violations (59% reduction)
- **Files modified**: 98 files reformatted, 83+ files auto-fixed
- **Violations reduced**: From 2,100+ to 864 remaining
- **Code quality**: Achieved Black-compatible formatting, modern Python idioms
- **Remaining**: 864 violations requiring manual review or architectural decisions

#### Tools & Configuration
- **Linter**: Ruff 0.8.4 with pyproject.toml configuration
- **Line length**: 100 characters
- **Docstring style**: Google format
- **Python version**: 3.9+ (Maya 2024+)

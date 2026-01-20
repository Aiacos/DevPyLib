# Contributing to DevPyLib

Thank you for your interest in contributing to DevPyLib! This guide will help you get started.

## Getting Started

### Prerequisites

- Python 3.9+ (Maya 2024+)
- Git
- Autodesk Maya (for testing)
- Code editor (VS Code recommended)

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/YOUR_USERNAME/DevPyLib.git
   cd DevPyLib
   ```

2. **Initialize Submodules**
   ```bash
   git submodule update --init --recursive
   ```

3. **Install Development Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install ruff  # Linting
   ```

4. **Set Up Maya Environment**
   - Copy/symlink `scripts/userSetup.py` to Maya scripts directory
   - Set `DEVPYLIB_PATH` in `Maya.env`

## Code Style

### Python Style Guide

DevPyLib follows PEP 8 with the following specifications:

- **Line Length**: 100 characters max
- **Indentation**: 4 spaces (no tabs)
- **Quotes**: Double quotes for strings
- **Docstrings**: Google-style format

### Linting with Ruff

```bash
# Check for issues
ruff check .

# Auto-fix issues
ruff check --fix .

# Format code
ruff format .
```

### Naming Conventions

```python
# Functions and variables: snake_case
def create_control():
    control_name = "arm_ctrl"

# Classes: PascalCase
class RigComponent:
    pass

# Constants: UPPER_SNAKE_CASE
DEFAULT_SCALE = 1.0

# Private members: leading underscore
def _internal_function():
    pass

# Maya objects: suffix convention
# _GRP, _CTRL, _JNT, _LOC, _GEO
```

### Import Order

```python
# 1. Standard library
import os
import sys
from pathlib import Path

# 2. Third-party
import numpy as np

# 3. Maya/DCC
import pymel.core as pm
import maya.cmds as cmds

# 4. Local imports
from mayaLib.rigLib.utils import control
from mayaLib.pipelineLib.utility import convention
```

### Maya API Usage

```python
# ✅ Preferred: PyMEL
import pymel.core as pm

joint = pm.createNode('joint', name='arm_01_jnt')
pm.parent(joint, parent_grp)

# ⚠️ Use when necessary: maya.cmds
import maya.cmds as cmds

cmds.file(new=True, force=True)

# ✅ Plugin development: OpenMaya 2.0
import maya.api.OpenMaya as om

def maya_useNewAPI():
    pass
```

## Documentation

### Docstring Format

Use Google-style docstrings:

```python
def create_control(prefix, scale=1.0, shape='circle'):
    """Create a NURBS control curve.

    Creates a control with offset group, modify group, and
    the control curve itself.

    Args:
        prefix: Naming prefix for the control.
        scale: Scale multiplier for the shape. Defaults to 1.0.
        shape: Shape type ('circle', 'square', 'cube'). Defaults to 'circle'.

    Returns:
        Control: A Control object with Off, Modify, and C attributes.

    Raises:
        ValueError: If shape type is not recognized.

    Example:
        >>> ctl = create_control('arm', scale=2.0, shape='cube')
        >>> print(ctl.C)  # The control curve

    """
    pass
```

### Wiki Documentation

- Write in English
- Use clear headings (##, ###)
- Include code examples
- Cross-reference related pages

## Testing

### Manual Testing

```python
# In Maya Script Editor
import mayaLib.rigLib.utils.control as control
reload(control)

# Test your changes
ctl = control.Control(prefix='test', shape='circle')
```

### Test Scripts

Place test scripts in `mayaLib/test/`:

```python
# mayaLib/test/test_control.py
"""Test control creation."""
import pymel.core as pm
from mayaLib.rigLib.utils import control

def test_basic_control():
    """Test basic control creation."""
    pm.newFile(force=True)

    ctl = control.Control(prefix='test')
    assert pm.objExists('test_CTRL')
    assert pm.objExists('test_offset_GRP')

    print("Test passed!")

if __name__ == '__main__':
    test_basic_control()
```

## Pull Request Process

### 1. Create a Branch

```bash
# Feature branch
git checkout -b feature/new-spine-component

# Bug fix branch
git checkout -b fix/skin-export-error

# Documentation branch
git checkout -b docs/update-api-reference
```

### 2. Make Changes

- Follow code style guidelines
- Add/update documentation
- Test your changes in Maya

### 3. Commit Changes

```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "Add ribbon spine component

- Create RibbonSpine class in rigLib/base/
- Add ribbon creation utilities
- Update documentation

Co-Authored-By: Your Name <email@example.com>"
```

### 4. Push and Create PR

```bash
git push origin feature/new-spine-component
```

Then create a Pull Request on GitHub with:
- Clear title describing the change
- Description of what was changed and why
- Reference any related issues
- Screenshots if UI changes

## Project Structure

When adding new features, follow the existing structure:

```
mayaLib/
├── rigLib/
│   ├── base/           # Base classes and rig modules
│   │   └── new_module.py
│   └── utils/          # Utility functions
│       └── new_utility.py
├── animationLib/       # Animation tools
├── modelLib/           # Modeling tools
├── shaderLib/          # Shader tools
├── fluidLib/           # Fluid simulation
├── bifrostLib/         # Bifrost/USD
├── guiLib/             # UI framework
├── pipelineLib/        # Pipeline utilities
├── lunaLib/            # Luna integration
├── plugin/             # Maya plugins
└── test/               # Test scripts
```

## Cross-Platform Guidelines

- Use `pathlib.Path` for all paths
- Use `subprocess.run()` instead of `os.system()`
- Use `shutil` for file operations
- Test on Windows if possible (primary dev platform)

## Getting Help

- **Questions**: Open a GitHub Issue with "Question:" prefix
- **Bugs**: Open a GitHub Issue with reproduction steps
- **Features**: Open a GitHub Issue describing the use case

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on the code, not the person
- Help newcomers get started

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

---

Thank you for contributing to DevPyLib! 🎉

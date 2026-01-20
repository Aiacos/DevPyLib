# GuiLib Documentation

GuiLib provides a UI framework for Maya with automatic widget generation from function signatures and a dynamic menu system for tool discovery.

---

## Table of Contents

- [Overview](#overview)
- [Module Structure](#module-structure)
- [FunctionUI Class](#functionui-class)
- [Main Menu System](#main-menu-system)
- [SearchLineEdit Widget](#searchlineedit-widget)
- [MenuLibWidget](#menulibwidget)
- [Usage Examples](#usage-examples)
- [Customization](#customization)

---

## Overview

GuiLib's key innovation is **introspection-based UI generation**: it uses Python's `inspect` module to automatically generate Qt widgets from function signatures, eliminating the need to manually create UIs for each tool.

### Key Features

- **Automatic UI generation**: Creates widgets from function parameters
- **Type-aware widgets**: Checkboxes for booleans, line edits for text/numbers
- **Maya integration**: Fill-from-selection buttons to populate from Maya selection
- **Dynamic menus**: Searchable function library with categorized access
- **Advanced mode**: Toggle to show/hide optional parameters
- **Documentation display**: Shows function docstrings in the UI

### Module Structure

```
guiLib/
├── __init__.py
├── main_menu.py          # MainMenu, MenuLibWidget classes
├── base/
│   ├── __init__.py
│   ├── base_ui.py        # FunctionUI class
│   ├── menu.py           # Menu utilities
│   └── shelf.py          # Shelf utilities
└── utils/
    └── ...               # UI utilities
```

---

## FunctionUI Class

The core class that generates UIs automatically from function signatures.

### How It Works

1. Inspects the function/class signature using `inspect.signature()`
2. Creates label + widget pairs for each parameter
3. Generates appropriate widget type based on default value type
4. Adds ">" buttons to populate from Maya selection
5. Creates "Execute" button and "Advanced" toggle

### Constructor

```python
from mayaLib.guiLib.base.base_ui import FunctionUI

ui = FunctionUI(func, parent=None)
ui.show()
```

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `func` | function/class | The function or class to create UI for |
| `parent` | QWidget | Optional parent widget |

### Widget Type Mapping

| Python Type | Qt Widget |
|-------------|-----------|
| `bool` | QCheckBox |
| Other types | QLineEdit |
| No default | QLineEdit + ">" button |

### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `function` | callable | The wrapped function |
| `sig` | Signature | Function signature object |
| `layout` | QGridLayout | Main layout |
| `lineedit_list` | list | Input widget list |
| `label_list` | list | Parameter label list |
| `fill_button_list` | list | Fill-from-selection buttons |
| `exec_button` | QPushButton | Execute button |
| `advanced_checkbox` | QCheckBox | Advanced mode toggle |
| `doclabel` | QLabel | Documentation label |

### Methods

#### fill_with_selected

Populates the corresponding line edit with Maya selection.

```python
# Called automatically when ">" button is clicked
# Gets selected objects from Maya and fills the line edit
```

#### get_parameter_list

Returns the function's parameters and default values.

```python
params = ui.get_parameter_list()
# Returns: [('param1', None), ('param2', 10), ('param3', True)]
```

#### toggle_default_parameter

Shows/hides parameters with default values.

```python
ui.toggle_default_parameter(defaultvisible=True)  # Show all
ui.toggle_default_parameter(defaultvisible=False) # Hide defaults
```

#### exec_function

Executes the function with values from the UI.

```python
# Called automatically when "Execute" button is clicked
# Parses widget values and calls the function
```

### Value Parsing

FunctionUI automatically converts string inputs:

| Input Format | Converted Type |
|--------------|----------------|
| `"10"` | int |
| `"10.5"` | float |
| `"True"` / `"False"` | bool |
| `"[1, 2, 3]"` | list |
| `"a, b, c"` | list (comma-separated) |
| `""` | None |

---

## Main Menu System

### MainMenu Class

Creates the main DevPyLib menu in Maya's menu bar.

```python
from mayaLib.guiLib.main_menu import MainMenu
from pathlib import Path

# Create menu
lib_path = Path("C:/path/to/DevPyLib")
menu = MainMenu(
    lib_path=lib_path,
    menu_name="MayaLib",
    parent=None,
    auto_update_on_load=True
)
```

#### Constructor Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `lib_path` | str/Path | Required | Path to DevPyLib |
| `menu_name` | str | "MayaLib" | Menu name in Maya |
| `parent` | QWidget | None | Parent widget |
| `auto_update_on_load` | bool | True | Auto-update library on load |

#### Methods

```python
# Update the widget (reload library)
menu.update_widget(lib_path)

# Force show widget
menu.show_widget()

# Pull latest from git
menu.update_lib()
```

### Menu Structure

The menu organizes tools by discipline:

```
MayaLib
├── Modelling
│   └── Model (modelLib)
│       └── [functions...]
├── Rigging
│   └── Rig (rigLib)
│       └── [functions...]
├── Animation
│   └── Animation (animationLib)
│       └── [functions...]
├── Vfx
│   └── Fluid (fluidLib)
│       └── [functions...]
├── Lookdev
│   ├── Lookdev (lookdevLib)
│   │   └── [functions...]
│   └── Shader (shaderLib)
│       └── [functions...]
└── Luna
    └── Luna (lunaLib)
        └── [functions...]
```

---

## SearchLineEdit Widget

Custom search field with clear button and text transformation.

```python
from mayaLib.guiLib.main_menu import SearchLineEdit

search = SearchLineEdit(icon_file="/path/to/close.png", parent=None)
```

### Features

- Clear button with custom icon
- Emits `speak` signal on text change
- Automatically replaces spaces with asterisks (for glob matching)

### Signals

| Signal | Description |
|--------|-------------|
| `speak(str)` | Emitted when text changes (with transformed text) |

---

## MenuLibWidget

The main library browser widget with search and category menus.

```python
from mayaLib.guiLib.main_menu import MenuLibWidget

widget = MenuLibWidget(lib_path="/path/to/DevPyLib", parent=None)
```

### Components

| Component | Description |
|-----------|-------------|
| Menu bar | Discipline categories (Modelling, Rigging, etc.) |
| Search field | Search for functions by name |
| Button list | Matching functions displayed as list |
| Doc label | Shows function documentation on hover |
| Update button | Pull latest from git |
| Reload button | Reload the library |

### Signals

| Signal | Description |
|--------|-------------|
| `update_widget` | Emitted when reload is requested |

### Methods

```python
# Build button list from search text
widget.build_button_list("control")

# Handle function click
widget.button_clicked(func)

# Download/update library
widget.download()

# Trigger reload
widget.reloaded()
```

---

## Usage Examples

### Creating UI for Custom Function

```python
from mayaLib.guiLib.base.base_ui import FunctionUI
import pymel.core as pm

def create_cube(name, size=1.0, subdivisions=1, center=True):
    """Create a polygon cube.

    Args:
        name: Name for the cube
        size: Size of the cube
        subdivisions: Number of subdivisions
        center: Center at origin
    """
    cube = pm.polyCube(
        name=name,
        width=size,
        height=size,
        depth=size,
        subdivisionsX=subdivisions,
        subdivisionsY=subdivisions,
        subdivisionsZ=subdivisions
    )[0]
    if center:
        pm.move(cube, 0, 0, 0)
    return cube

# Create and show UI
ui = FunctionUI(create_cube)
ui.show()
```

### Creating UI for Class

```python
from mayaLib.guiLib.base.base_ui import FunctionUI

class MyCoolTool:
    """My cool tool for doing cool things."""

    def __init__(self, mesh_name, iterations=5, smooth=True):
        """Initialize the tool.

        Args:
            mesh_name: Target mesh
            iterations: Number of iterations
            smooth: Enable smoothing
        """
        self.mesh = mesh_name
        self.iterations = iterations
        self.smooth = smooth
        self.execute()

    def execute(self):
        print(f"Processing {self.mesh} with {self.iterations} iterations")

# UI will use __init__ signature
ui = FunctionUI(MyCoolTool)
ui.show()
```

### Programmatic Menu Creation

```python
from mayaLib.guiLib.main_menu import MainMenu
from pathlib import Path

# This is typically done in userSetup.py
def create_mayalib_menu():
    """Create the MayaLib menu in Maya."""
    lib_path = Path(__file__).parent.resolve()
    menu = MainMenu(
        lib_path=lib_path,
        menu_name="MayaLib",
        auto_update_on_load=False  # Don't auto-update
    )
    return menu

# Deferred creation (after Maya fully loads)
import maya.cmds as cmds
cmds.evalDeferred(create_mayalib_menu)
```

### Custom Menu Actions

```python
from mayaLib.guiLib.main_menu import MenuLibWidget
from mayaLib.guiLib.base.base_ui import FunctionUI

try:
    from PySide6 import QtWidgets
    from PySide6.QtGui import QAction
except ImportError:
    from PySide2 import QtWidgets
    from PySide2.QtWidgets import QAction

class CustomMenuWidget(MenuLibWidget):
    """Extended menu with custom actions."""

    def add_custom_menu(self, menu):
        """Add custom menu actions."""
        action = QAction("My Custom Tool", self)
        action.triggered.connect(self.run_custom_tool)
        menu.addAction(action)

    def run_custom_tool(self):
        """Run the custom tool."""
        from my_tools import cool_function
        ui = FunctionUI(cool_function)
        ui.show()
```

### Integrating with Shelf

```python
from mayaLib.guiLib.base import shelf

# Shelf utilities for creating shelf buttons
# See module for full API
```

---

## Customization

### Custom Widget Types

To add custom widget types, extend FunctionUI:

```python
from mayaLib.guiLib.base.base_ui import FunctionUI
from PySide6 import QtWidgets

class ExtendedFunctionUI(FunctionUI):
    """FunctionUI with additional widget types."""

    def create_widget_for_param(self, name, default):
        """Create widget based on parameter type."""
        if isinstance(default, list):
            # Create combo box for lists
            widget = QtWidgets.QComboBox()
            widget.addItems([str(x) for x in default])
            return widget
        elif isinstance(default, tuple) and len(default) == 3:
            # Create color picker for RGB tuples
            widget = QtWidgets.QPushButton("Pick Color")
            return widget
        else:
            # Default behavior
            return super().create_widget_for_param(name, default)
```

### Custom Disciplines

To add a new discipline category:

```python
# In MenuLibWidget.add_menu_bar()
discipline = ["Modelling", "Rigging", "Animation", "Vfx", "Lookdev", "Luna", "MyCategory"]

# In MenuLibWidget.add_multiple_menu_action()
elif discipline == "MyCategory":
    lib_menu = self.add_sub_menu(up_menu, "myLib")
    self.add_recursive_menu(lib_menu, self.lib_dict.get("myLib", {}))
```

### Styling

The widgets use Qt stylesheets:

```python
# Example: Custom doc label style
self.doc_label.setStyleSheet(
    "background-color: rgb(90,90,90); "
    "border-radius: 5px; "
    "border: 1px solid rgb(255, 255, 255);"
)
```

---

## Qt Compatibility

GuiLib supports both PySide2 and PySide6:

```python
try:
    from PySide6 import QtCore, QtWidgets, QtGui
    from PySide6.QtGui import QAction
    from shiboken6 import wrapInstance
except ImportError:
    from PySide2 import QtCore, QtWidgets, QtGui
    from PySide2.QtWidgets import QAction
    from shiboken2 import wrapInstance
```

---

## Best Practices

1. **Write good docstrings**: They appear in the UI and help users
2. **Use type hints and defaults**: They determine widget types
3. **Make required params first**: They appear at the top of the UI
4. **Use descriptive parameter names**: They become labels
5. **Provide sensible defaults**: Users can toggle Advanced to change them
6. **Test with Maya selection**: Ensure fill-from-selection works correctly

---

## See Also

- [MayaLib Home](Home.md)
- [PipelineLib](PipelineLib.md) - Function discovery utilities
- [Architecture](../Architecture.md) - UI system design

---

*Last updated: January 2026*

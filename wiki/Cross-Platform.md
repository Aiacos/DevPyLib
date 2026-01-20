# Cross-Platform Compatibility

DevPyLib is designed to be fully cross-platform compatible with Windows, Linux, and macOS.

## Supported Platforms

| Platform | Status | Notes |
|----------|--------|-------|
| Windows 10/11 | ✅ Full Support | Primary development platform |
| Linux (CentOS/Ubuntu) | ✅ Full Support | VFX Reference Platform |
| macOS (Intel/ARM) | ✅ Full Support | Universal binaries |

## Path Handling

### Always Use pathlib

```python
# ✅ Good - Cross-platform
from pathlib import Path

scripts_dir = Path.home() / "maya" / "scripts"
config_file = Path(__file__).parent / "config.json"

# ❌ Bad - OS-specific
scripts_dir = "C:\\Users\\name\\maya\\scripts"  # Windows only
scripts_dir = "/home/name/maya/scripts"          # Linux only
```

### Platform-Specific Paths

```python
import platform
from pathlib import Path

def get_maya_prefs():
    """Get Maya preferences directory."""
    system = platform.system()

    if system == "Windows":
        return Path.home() / "Documents" / "maya"
    elif system == "Darwin":  # macOS
        return Path.home() / "Library" / "Preferences" / "Autodesk" / "maya"
    else:  # Linux
        return Path.home() / "maya"
```

### Path Separators

```python
# ✅ Good - pathlib handles separators automatically
file_path = Path("folder") / "subfolder" / "file.txt"

# ❌ Bad - Hardcoded separators
file_path = "folder\\subfolder\\file.txt"  # Windows only
file_path = "folder/subfolder/file.txt"    # May fail on Windows
```

## Platform Detection

### Using platform.system()

```python
import platform

system = platform.system()
# Returns: "Windows", "Linux", or "Darwin" (macOS)

# Note: macOS returns "Darwin", NOT "OSX" or "macOS"
if system == "Darwin":
    print("Running on macOS")
```

### DCC Detection

```python
# prismLib/pipeline.py
import sys

def detect_host_app():
    """Detect which DCC application is running."""
    if "maya.cmds" in sys.modules:
        return "Maya"
    elif "hou" in sys.modules:
        return "Houdini"
    elif "bpy" in sys.modules:
        return "Blender"
    return "Standalone"
```

## Shell Commands

### Never Use os.system()

```python
import subprocess
import sys

# ✅ Good - subprocess with list arguments
subprocess.run([sys.executable, "-m", "pip", "install", "package"])

# ❌ Bad - os.system (security risk, not portable)
import os
os.system("pip install package")
```

### File Operations

```python
import shutil
from pathlib import Path

# ✅ Good - shutil for file operations
shutil.copy(src, dst)
shutil.rmtree(directory)
shutil.move(src, dst)

# ❌ Bad - Shell commands
os.system("cp src dst")      # Unix only
os.system("copy src dst")    # Windows only
os.system("rm -rf dir")      # Unix only
```

### Archive Operations

```python
import zipfile
import tarfile

# ✅ Good - Python modules
with zipfile.ZipFile("archive.zip", "r") as z:
    z.extractall("destination")

# ❌ Bad - Shell commands
os.system("unzip archive.zip")  # Requires unzip installed
```

## Environment Variables

```python
import os
from pathlib import Path

# ✅ Good - os.environ with defaults
devpylib_path = os.environ.get("DEVPYLIB_PATH", "")

# Setting paths
if devpylib_path:
    sys.path.append(devpylib_path)
```

## Maya-Specific Paths

### Scripts Directory

```python
from pathlib import Path
import platform

def get_maya_scripts_dir(maya_version="2024"):
    """Get Maya scripts directory for current platform."""
    system = platform.system()

    if system == "Windows":
        return Path.home() / "Documents" / "maya" / maya_version / "scripts"
    elif system == "Darwin":
        return Path.home() / "Library" / "Preferences" / "Autodesk" / "maya" / maya_version / "scripts"
    else:  # Linux
        return Path.home() / "maya" / maya_version / "scripts"
```

### Plugin Paths

```python
def get_maya_plugin_dir(maya_version="2024"):
    """Get Maya plug-ins directory."""
    system = platform.system()

    if system == "Windows":
        return Path.home() / "Documents" / "maya" / maya_version / "plug-ins"
    elif system == "Darwin":
        return Path.home() / "Library" / "Preferences" / "Autodesk" / "maya" / maya_version / "plug-ins"
    else:
        return Path.home() / "maya" / maya_version / "plug-ins"
```

## Qt/PySide Compatibility

```python
# ✅ Good - Try PySide6 first, fallback to PySide2
try:
    from PySide6 import QtCore, QtGui, QtWidgets
    from PySide6.QtGui import QAction
    from shiboken6 import wrapInstance
except ImportError:
    from PySide2 import QtCore, QtGui, QtWidgets
    from PySide2.QtWidgets import QAction
    from shiboken2 import wrapInstance
```

## Line Endings

Git handles line endings automatically with proper `.gitattributes`:

```gitattributes
# .gitattributes
* text=auto
*.py text eol=lf
*.md text eol=lf
*.json text eol=lf
```

## Executable Python

```python
import sys

# ✅ Good - sys.executable for current Python
subprocess.run([sys.executable, "-m", "pip", "install", "package"])

# ❌ Bad - Hardcoded python path
subprocess.run(["python", "-m", "pip", "install", "package"])  # May not exist
subprocess.run(["python3", "-m", "pip", "install", "package"]) # May not exist
```

## Testing Cross-Platform Code

```python
import platform
import unittest

class TestCrossPlatform(unittest.TestCase):

    def test_paths_use_pathlib(self):
        """Ensure paths use pathlib."""
        from mayaLib.pipelineLib.utility import file
        # Verify no hardcoded separators

    def test_platform_detection(self):
        """Test platform detection works."""
        system = platform.system()
        self.assertIn(system, ["Windows", "Linux", "Darwin"])
```

## Common Issues

### Issue: Paths with Spaces

```python
# ✅ Good - Quote paths in shell commands
subprocess.run(["python", str(Path("path with spaces") / "script.py")])

# ❌ Bad - Unquoted paths may fail
os.system(f"python {path_with_spaces}/script.py")
```

### Issue: Case Sensitivity

```python
# Windows is case-insensitive, Linux/macOS are case-sensitive
# ✅ Good - Consistent casing
from mayaLib.rigLib.utils import control

# ❌ Bad - May fail on Linux/macOS
from mayaLib.RigLib.Utils import Control
```

### Issue: Permissions

```python
import os
import stat

# ✅ Good - Check/set permissions cross-platform
def make_executable(path):
    """Make file executable on Unix systems."""
    if platform.system() != "Windows":
        current = os.stat(path).st_mode
        os.chmod(path, current | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
```

## See Also

- [Architecture](Architecture.md) - Overall architecture
- [MayaLib/Getting-Started](MayaLib/Getting-Started.md) - Maya setup
- [Contributing](Contributing.md) - Development guidelines

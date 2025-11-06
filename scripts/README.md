# DevPyLib Scripts

Utility scripts for development, testing, and tooling.

## Scripts Overview

### detect_mayapy.py
Auto-detects Maya installation and mayapy path across platforms.

**Usage**:
```bash
# Get mayapy path
python3 scripts/detect_mayapy.py
# Output: /usr/autodesk/maya2024/bin/mayapy

# Get Maya version and Python version
python3 scripts/detect_mayapy.py --version
# Output: maya2024 (Python 3.10.8)

# Get site-packages path
python3 scripts/detect_mayapy.py --site-packages
# Output: /usr/autodesk/maya2024/lib/python3.10/site-packages

# List all Maya installations
python3 scripts/detect_mayapy.py --all-versions

# JSON output
python3 scripts/detect_mayapy.py --json
```

**Features**:
- Cross-platform (Linux, macOS, Windows)
- Auto-detects all Maya versions
- Returns latest version by default
- Validates executable permissions
- JSON output support

### test_with_maya.sh
Runs pytest using mayapy instead of system Python.

**Usage**:
```bash
# Run all tests
./scripts/test_with_maya.sh

# Verbose output
./scripts/test_with_maya.sh -v

# Run specific test
./scripts/test_with_maya.sh -k test_control

# Run only unit tests
./scripts/test_with_maya.sh -m unit

# Run with coverage
./scripts/test_with_maya.sh --cov=mayaLib --cov-report=html

# Run specific file
./scripts/test_with_maya.sh mayaLib/test/test_control.py
```

**Environment Variables**:
```bash
# Use specific Maya version
MAYA_VERSION=2023 ./scripts/test_with_maya.sh

# Override mayapy path
MAYAPY_PATH=/custom/path/mayapy ./scripts/test_with_maya.sh
```

**Features**:
- Auto-detects mayapy
- Colored output
- Verifies pytest installation
- Shows Python version
- Cross-platform support

## Integration with Tools

### Neovim
Use in Neovim LSP configuration:
```lua
local mayapy = vim.fn.system('python3 scripts/detect_mayapy.py'):gsub('\n', '')
```

### CI/CD
Use in GitHub Actions:
```yaml
- name: Detect mayapy
  run: echo "MAYAPY=$(python3 scripts/detect_mayapy.py)" >> $GITHUB_ENV

- name: Run tests
  run: $MAYAPY -m pytest
```

### Pre-commit Hooks
Use in `.pre-commit-config.yaml`:
```yaml
- repo: local
  hooks:
    - id: pytest-mayapy
      name: Run tests with mayapy
      entry: ./scripts/test_with_maya.sh
      language: system
      pass_filenames: false
```

## Adding New Scripts

When adding new scripts to this directory:

1. **Make them executable**:
   ```bash
   chmod +x scripts/new_script.sh
   ```

2. **Add shebang line**:
   ```bash
   #!/bin/bash
   # or
   #!/usr/bin/env python3
   ```

3. **Document in this README**

4. **Follow naming conventions**:
   - Shell scripts: `snake_case.sh`
   - Python scripts: `snake_case.py`

5. **Add help text**:
   - Shell: `--help` flag
   - Python: argparse with description

## Testing Scripts

Test scripts before committing:

```bash
# Test detect_mayapy.py
python3 scripts/detect_mayapy.py
python3 scripts/detect_mayapy.py --all-versions

# Test test_with_maya.sh
./scripts/test_with_maya.sh --help
# (Only run actual tests if Maya is installed)
```

## Troubleshooting

### "Permission denied" error
```bash
chmod +x scripts/*.sh
chmod +x scripts/*.py
```

### "mayapy not found"
```bash
# Check Maya installation
ls -la /usr/autodesk/maya*/bin/mayapy

# Set MAYAPY_PATH manually
export MAYAPY_PATH=/path/to/mayapy
```

### "pytest not found in mayapy"
```bash
# Install pytest in mayapy
/usr/autodesk/maya2024/bin/mayapy -m pip install pytest
```

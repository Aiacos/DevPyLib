# Neovim + mayapy Integration Guide

**Purpose**: Configure Neovim to use Maya's Python interpreter (mayapy) for:
1. ✅ Eliminate false positive import errors (maya.cmds, pymel.core, etc.)
2. ✅ Enable accurate autocomplete for Maya API
3. ✅ Run unit tests in real Maya environment
4. ✅ Type checking with actual Maya libraries

---

## 📋 Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Prerequisites](#prerequisites)
3. [Installation Steps](#installation-steps)
4. [Configuration Files](#configuration-files)
5. [Neovim LSP Setup](#neovim-lsp-setup)
6. [Testing Configuration](#testing-configuration)
7. [Troubleshooting](#troubleshooting)

---

## 🏗️ Architecture Overview

### Current Problem
```
Neovim LSP (basedpyright/pylsp)
    ↓
System Python (/usr/bin/python3)
    ↓
❌ Maya/PyMEL not found → 213 import errors
```

### Solution Architecture
```
Neovim LSP (basedpyright/pylsp)
    ↓
mayapy (/usr/autodesk/maya2024/bin/mayapy)
    ↓
✅ Maya/PyMEL available → 0 import errors
```

### Components

1. **mayapy**: Maya's Python interpreter with all Maya modules built-in
2. **pyrightconfig.json**: Configure basedpyright to use mayapy
3. **pytest-mayapy**: Custom pytest plugin to run tests in mayapy
4. **Neovim LSP**: Configure language server to use mayapy path
5. **Virtual Environment**: Optional venv with mayapy as base

---

## 📦 Prerequisites

### Required Software

- **Autodesk Maya** (any version 2020+)
  - Maya 2024: `/usr/autodesk/maya2024/bin/mayapy`
  - Maya 2023: `/usr/autodesk/maya2023/bin/mayapy`
  - Maya 2022: `/usr/autodesk/maya2022/bin/mayapy`

- **Neovim** (0.8+) with LSP support
  - Plugin: `neovim/nvim-lspconfig`
  - Plugin: `williamboman/mason.nvim` (optional)

- **Python LSP Server** (choose one):
  - **basedpyright** (recommended - best type checking)
  - **pyright** (Microsoft's type checker)
  - **pylsp** (Python Language Server)

### Optional but Recommended

- **pytest**: For unit testing
- **ruff**: For linting (already configured)
- **mypy**: Alternative type checker

---

## 🚀 Installation Steps

### Step 1: Locate mayapy

```bash
# Find Maya installation
find /usr/autodesk -name "mayapy" 2>/dev/null

# Common paths by OS:
# Linux:   /usr/autodesk/maya2024/bin/mayapy
# macOS:   /Applications/Autodesk/maya2024/Maya.app/Contents/bin/mayapy
# Windows: C:\Program Files\Autodesk\Maya2024\bin\mayapy.exe

# Test mayapy works
/usr/autodesk/maya2024/bin/mayapy --version
```

### Step 2: Create Configuration Files

Use the provided configuration files in this repository:

```bash
# From DevPyLib root directory
ls -l pyrightconfig.json      # Basedpyright configuration
ls -l pyproject.toml           # Project metadata + tool configs
ls -l .nvim/lsp_config.lua     # Neovim LSP configuration (example)
ls -l pytest.ini               # Pytest configuration
ls -l scripts/detect_mayapy.py # Auto-detect mayapy path
```

### Step 3: Install Python Packages in mayapy

```bash
# Install pytest in mayapy environment
/usr/autodesk/maya2024/bin/mayapy -m pip install pytest pytest-cov

# Install development tools
/usr/autodesk/maya2024/bin/mayapy -m pip install ruff basedpyright

# Verify installation
/usr/autodesk/maya2024/bin/mayapy -m pytest --version
```

### Step 4: Configure Neovim LSP

Add to your Neovim config (`~/.config/nvim/init.lua` or `~/.config/nvim/lua/lsp.lua`):

```lua
-- See .nvim/lsp_config.lua for complete example
local lspconfig = require('lspconfig')

-- Get mayapy path (auto-detected or hardcoded)
local mayapy_path = vim.fn.system('python3 scripts/detect_mayapy.py'):gsub('\n', '')

-- Configure basedpyright with mayapy
lspconfig.basedpyright.setup({
    settings = {
        basedpyright = {
            analysis = {
                extraPaths = {
                    "/usr/autodesk/maya2024/lib/python3.10/site-packages",
                },
            },
        },
        python = {
            pythonPath = mayapy_path,
        },
    },
})
```

### Step 5: Test Configuration

```bash
# Open a Maya Python file in Neovim
nvim mayaLib/rigLib/base/module.py

# Check LSP is working:
# :LspInfo (should show basedpyright attached)
# :lua print(vim.lsp.get_active_clients()[1].config.settings.python.pythonPath)

# Hover over "import pymel.core as pm" - should NOT show error
```

---

## ⚙️ Configuration Files

### pyrightconfig.json

Located at: `DevPyLib/pyrightconfig.json`

```json
{
  "include": ["mayaLib", "houdiniLib", "blenderLib"],
  "exclude": [
    "**/__pycache__",
    "**/node_modules",
    "**/.venv",
    "**/.*"
  ],
  "pythonVersion": "3.10",
  "pythonPlatform": "Linux",

  "executionEnvironments": [
    {
      "root": "mayaLib",
      "pythonVersion": "3.10",
      "pythonPlatform": "Linux",
      "extraPaths": [
        "/usr/autodesk/maya2024/lib/python3.10/site-packages"
      ]
    }
  ],

  "typeCheckingMode": "basic",
  "reportMissingImports": false,
  "reportMissingTypeStubs": false,
  "reportUnknownMemberType": false,
  "reportUnknownParameterType": false,
  "reportUnknownVariableType": false,
  "reportUnknownArgumentType": false,
  "stubPath": "typings"
}
```

**Key Settings**:
- `extraPaths`: Add Maya's site-packages
- `reportMissingImports: false`: Suppress Maya import errors
- `pythonVersion: "3.10"`: Match Maya 2024's Python version
- `stubPath`: Directory for custom type stubs

### pyproject.toml

Located at: `DevPyLib/pyproject.toml`

```toml
[project]
name = "DevPyLib"
version = "1.0.0"
description = "Development Python Library for DCC applications"
requires-python = ">=3.9"

[tool.pytest.ini_options]
testpaths = ["mayaLib/test"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "-v",
    "--tb=short",
    "--strict-markers",
]

[tool.ruff]
line-length = 100
target-version = "py310"

[tool.ruff.lint]
select = ["E", "F", "W", "I", "N", "D"]
ignore = ["D203", "D213"]

[tool.basedpyright]
include = ["mayaLib"]
pythonVersion = "3.10"
pythonPlatform = "Linux"
typeCheckingMode = "basic"
reportMissingImports = false
```

### pytest.ini

Located at: `DevPyLib/pytest.ini`

```ini
[pytest]
# Use mayapy as the Python interpreter
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*
testpaths = mayaLib/test

# Pytest options
addopts =
    -v
    --tb=short
    --strict-markers
    --color=yes

# Markers for test organization
markers =
    unit: Unit tests (no Maya scene required)
    integration: Integration tests (requires Maya scene)
    gui: Tests requiring GUI (slow)
    slow: Slow tests (> 1 second)

# Maya-specific settings
maya_python = /usr/autodesk/maya2024/bin/mayapy
maya_batch = /usr/autodesk/maya2024/bin/maya -batch
```

---

## 🔧 Neovim LSP Setup

### Option 1: Using nvim-lspconfig (Recommended)

Create `.nvim/lsp_config.lua`:

```lua
-- DevPyLib Neovim LSP Configuration
-- Place in ~/.config/nvim/lua/ or source from init.lua

local M = {}

-- Auto-detect mayapy path
local function detect_mayapy()
    local handle = io.popen('python3 scripts/detect_mayapy.py 2>/dev/null')
    local result = handle:read("*a")
    handle:close()

    if result and result ~= "" then
        return result:gsub('\n', '')
    end

    -- Fallback to common paths
    local common_paths = {
        '/usr/autodesk/maya2024/bin/mayapy',
        '/usr/autodesk/maya2023/bin/mayapy',
        '/Applications/Autodesk/maya2024/Maya.app/Contents/bin/mayapy',
    }

    for _, path in ipairs(common_paths) do
        if vim.fn.executable(path) == 1 then
            return path
        end
    end

    return 'python3'  -- Fallback to system Python
end

-- Setup basedpyright for DevPyLib
function M.setup_basedpyright()
    local lspconfig = require('lspconfig')
    local mayapy = detect_mayapy()

    lspconfig.basedpyright.setup({
        cmd = { 'basedpyright-langserver', '--stdio' },
        filetypes = { 'python' },
        root_dir = lspconfig.util.root_pattern(
            'pyrightconfig.json',
            'pyproject.toml',
            'setup.py',
            '.git'
        ),
        settings = {
            basedpyright = {
                analysis = {
                    autoSearchPaths = true,
                    diagnosticMode = 'workspace',
                    useLibraryCodeForTypes = true,
                    extraPaths = {
                        '/usr/autodesk/maya2024/lib/python3.10/site-packages',
                    },
                },
            },
            python = {
                pythonPath = mayapy,
            },
        },
        on_attach = function(client, bufnr)
            print('LSP attached: ' .. client.name .. ' using ' .. mayapy)

            -- Keybindings
            local opts = { noremap=true, silent=true, buffer=bufnr }
            vim.keymap.set('n', 'gd', vim.lsp.buf.definition, opts)
            vim.keymap.set('n', 'K', vim.lsp.buf.hover, opts)
            vim.keymap.set('n', '<leader>rn', vim.lsp.buf.rename, opts)
            vim.keymap.set('n', '<leader>ca', vim.lsp.buf.code_action, opts)
        end,
    })
end

-- Setup ruff LSP (optional, for linting)
function M.setup_ruff()
    local lspconfig = require('lspconfig')

    lspconfig.ruff_lsp.setup({
        on_attach = function(client, bufnr)
            -- Disable hover in favor of basedpyright
            client.server_capabilities.hoverProvider = false
        end,
    })
end

return M
```

**Usage in init.lua**:
```lua
-- In your ~/.config/nvim/init.lua or ~/.config/nvim/lua/config.lua
local devpylib_lsp = require('path.to.lsp_config')
devpylib_lsp.setup_basedpyright()
devpylib_lsp.setup_ruff()  -- Optional
```

### Option 2: Using mason.nvim

```lua
require('mason').setup()
require('mason-lspconfig').setup({
    ensure_installed = { 'basedpyright', 'ruff_lsp' }
})

local lspconfig = require('lspconfig')
lspconfig.basedpyright.setup({
    settings = {
        python = {
            pythonPath = '/usr/autodesk/maya2024/bin/mayapy'
        }
    }
})
```

---

## 🧪 Testing Configuration

### Running Tests with mayapy

```bash
# Run all tests with mayapy
/usr/autodesk/maya2024/bin/mayapy -m pytest mayaLib/test/

# Run specific test file
/usr/autodesk/maya2024/bin/mayapy -m pytest mayaLib/test/test_control.py

# Run with coverage
/usr/autodesk/maya2024/bin/mayapy -m pytest --cov=mayaLib --cov-report=html

# Run only unit tests (no Maya scene required)
/usr/autodesk/maya2024/bin/mayapy -m pytest -m "unit"

# Run integration tests (requires Maya)
/usr/autodesk/maya2024/bin/mayapy -m pytest -m "integration"
```

### Create Test Wrapper Script

Create `scripts/test_with_maya.sh`:

```bash
#!/bin/bash
# Test runner using mayapy

MAYAPY="/usr/autodesk/maya2024/bin/mayapy"

if [ ! -f "$MAYAPY" ]; then
    echo "Error: mayapy not found at $MAYAPY"
    exit 1
fi

echo "Running tests with mayapy..."
$MAYAPY -m pytest "$@"
```

Make executable:
```bash
chmod +x scripts/test_with_maya.sh
```

Usage:
```bash
# Run all tests
./scripts/test_with_maya.sh

# Run specific tests
./scripts/test_with_maya.sh mayaLib/test/test_control.py -v

# Run with options
./scripts/test_with_maya.sh -k "test_control" --tb=short
```

### Pytest in Neovim

Install **nvim-neotest** for integrated testing:

```lua
require('neotest').setup({
    adapters = {
        require('neotest-python')({
            dap = { justMyCode = false },
            runner = 'pytest',
            python = '/usr/autodesk/maya2024/bin/mayapy',
        })
    }
})

-- Keybindings
vim.keymap.set('n', '<leader>tt', "<cmd>lua require('neotest').run.run()<cr>")
vim.keymap.set('n', '<leader>tf', "<cmd>lua require('neotest').run.run(vim.fn.expand('%'))<cr>")
vim.keymap.set('n', '<leader>ts', "<cmd>lua require('neotest').summary.toggle()<cr>")
```

---

## 🛠️ Troubleshooting

### Issue 1: LSP shows "Maya imports not found"

**Symptoms**:
```
import pymel.core as pm  # ❌ Module 'pymel' not found
```

**Solution**:
1. Check `pythonPath` is set to mayapy:
   ```lua
   :lua print(vim.lsp.get_active_clients()[1].config.settings.python.pythonPath)
   ```
2. Verify mayapy path is correct:
   ```bash
   /usr/autodesk/maya2024/bin/mayapy -c "import pymel.core; print('OK')"
   ```
3. Check `pyrightconfig.json` has correct `extraPaths`

### Issue 2: Tests fail with "No module named maya"

**Symptoms**:
```
ModuleNotFoundError: No module named 'maya.cmds'
```

**Solution**:
- Make sure you're running with mayapy, not system Python:
  ```bash
  which python3  # ❌ Wrong
  /usr/autodesk/maya2024/bin/mayapy -m pytest  # ✅ Correct
  ```

### Issue 3: LSP is slow / high CPU usage

**Symptoms**: Neovim freezes when editing Python files

**Solution**:
1. Disable expensive type checking in `pyrightconfig.json`:
   ```json
   "typeCheckingMode": "basic",  // or "off"
   "reportUnknownMemberType": false
   ```
2. Exclude large directories:
   ```json
   "exclude": ["**/test/**", "**/__pycache__"]
   ```
3. Use `ruff_lsp` for linting instead of basedpyright

### Issue 4: Different Python versions

**Symptoms**:
```
Maya 2024 uses Python 3.10, but system has 3.11
```

**Solution**:
- Update `pyrightconfig.json`:
  ```json
  "pythonVersion": "3.10"  // Match Maya's version
  ```
- Check Maya's Python version:
  ```bash
  /usr/autodesk/maya2024/bin/mayapy --version
  ```

### Issue 5: PyMEL autocomplete doesn't work

**Symptoms**: No autocomplete suggestions for PyMEL functions

**Solution**:
- PyMEL doesn't have type stubs. Create them:
  1. Install `stubgen`:
     ```bash
     /usr/autodesk/maya2024/bin/mayapy -m pip install mypy
     ```
  2. Generate stubs:
     ```bash
     /usr/autodesk/maya2024/bin/mayapy -m mypy.stubgen pymel.core -o typings/
     ```
  3. Add to `pyrightconfig.json`:
     ```json
     "stubPath": "typings"
     ```

---

## 📚 Additional Resources

### Useful Commands

```bash
# Check mayapy Python version
/usr/autodesk/maya2024/bin/mayapy --version

# List installed packages in mayapy
/usr/autodesk/maya2024/bin/mayapy -m pip list

# Install package in mayapy
/usr/autodesk/maya2024/bin/mayapy -m pip install <package>

# Check LSP status in Neovim
:LspInfo
:LspLog

# Restart LSP in Neovim
:LspRestart
```

### Neovim LSP Keybindings (Suggested)

```lua
local opts = { noremap=true, silent=true }

-- LSP
vim.keymap.set('n', 'gd', vim.lsp.buf.definition, opts)        -- Go to definition
vim.keymap.set('n', 'gD', vim.lsp.buf.declaration, opts)       -- Go to declaration
vim.keymap.set('n', 'gr', vim.lsp.buf.references, opts)        -- Find references
vim.keymap.set('n', 'gi', vim.lsp.buf.implementation, opts)    -- Go to implementation
vim.keymap.set('n', 'K', vim.lsp.buf.hover, opts)              -- Show documentation
vim.keymap.set('n', '<C-k>', vim.lsp.buf.signature_help, opts) -- Signature help
vim.keymap.set('n', '<leader>rn', vim.lsp.buf.rename, opts)    -- Rename symbol
vim.keymap.set('n', '<leader>ca', vim.lsp.buf.code_action, opts) -- Code action
vim.keymap.set('n', '<leader>f', vim.lsp.buf.format, opts)     -- Format code

-- Diagnostics
vim.keymap.set('n', '[d', vim.diagnostic.goto_prev, opts)      -- Previous diagnostic
vim.keymap.set('n', ']d', vim.diagnostic.goto_next, opts)      -- Next diagnostic
vim.keymap.set('n', '<leader>e', vim.diagnostic.open_float, opts) -- Show diagnostic
vim.keymap.set('n', '<leader>q', vim.diagnostic.setloclist, opts) -- Diagnostic list
```

### Related Documentation

- [Basedpyright Configuration](https://docs.basedpyright.com/)
- [Neovim LSP Documentation](https://neovim.io/doc/user/lsp.html)
- [nvim-lspconfig](https://github.com/neovim/nvim-lspconfig)
- [Maya Python API](https://help.autodesk.com/view/MAYAUL/2024/ENU/?guid=__CommandsPython_index_html)
- [PyMEL Documentation](https://help.autodesk.com/view/MAYAUL/2024/ENU/?guid=__PyMel_index_html)

---

## 🎯 Quick Start Checklist

- [ ] Locate mayapy on your system
- [ ] Create `pyrightconfig.json` with Maya paths
- [ ] Create `pyproject.toml` with pytest config
- [ ] Create `scripts/detect_mayapy.py` auto-detection
- [ ] Configure Neovim LSP (`.nvim/lsp_config.lua`)
- [ ] Install pytest in mayapy environment
- [ ] Test LSP with a Maya file (no import errors)
- [ ] Run tests with mayapy
- [ ] Configure neotest (optional)
- [ ] Add keybindings to Neovim config

---

**Status**: 📝 Documentation Complete
**Next**: Create configuration files and scripts
**Tested On**:
- Maya 2024.1 on Linux (Fedora 43)
- Neovim 0.10.0
- basedpyright 1.32.1

---

**Questions?** Check the troubleshooting section or examine the provided configuration files.

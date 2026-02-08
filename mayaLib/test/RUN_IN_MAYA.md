# End-to-End Verification in Maya

This document describes how to verify the lazy loading implementation in a live Maya environment.

## Prerequisites

1. Maya 2022+ installed
2. DevPyLib configured with `DEVPYLIB_PATH` in Maya.env
3. userSetup.py properly configured to load DevPyLib on startup

## Verification Methods

### Method 1: Run via Maya Script Editor (Recommended)

1. **Start Maya**
   ```bash
   maya
   ```

2. **Open Script Editor** (Windows > General Editors > Script Editor)

3. **Create new Python tab** (File > New Tab > Python)

4. **Copy and paste the following code:**

   ```python
   import sys
   from pathlib import Path

   # Adjust path to your DevPyLib location
   devpylib_path = Path(r"C:/path/to/DevPyLib")  # Windows
   # devpylib_path = Path("/path/to/DevPyLib")   # Linux/macOS

   test_script = devpylib_path / "mayaLib" / "test" / "verify_maya_e2e.py"

   # Execute the verification script
   exec(open(test_script).read())
   ```

5. **Execute** (Ctrl+Enter or click "Execute" button)

6. **Check Script Editor output** for test results

### Method 2: Run via mayapy (Command Line)

1. **Navigate to DevPyLib directory:**
   ```bash
   cd /path/to/DevPyLib
   ```

2. **Run with mayapy:**

   **Windows:**
   ```cmd
   "C:\Program Files\Autodesk\Maya2024\bin\mayapy.exe" mayaLib\test\verify_maya_e2e.py
   ```

   **Linux:**
   ```bash
   /usr/autodesk/maya2024/bin/mayapy mayaLib/test/verify_maya_e2e.py
   ```

   **macOS:**
   ```bash
   /Applications/Autodesk/maya2024/Maya.app/Contents/bin/mayapy mayaLib/test/verify_maya_e2e.py
   ```

3. **Check console output** for test results

### Method 3: Run during Maya Startup

1. **Add to userSetup.py** (temporarily for testing):

   ```python
   # Add at the end of userSetup.py
   def run_verification():
       import sys
       from pathlib import Path
       test_script = Path(__file__).parent.parent / "mayaLib" / "test" / "verify_maya_e2e.py"
       exec(open(test_script).read())

   cmds.evalDeferred(run_verification, lowestPriority=True)
   ```

2. **Restart Maya** and check Script Editor output

## What the Tests Verify

The verification script tests:

### 1. Basic Import Tests
- ✓ mayaLib imports successfully
- ✓ Import time is measured (should be ~1-2ms with lazy loading)

### 2. Lazy Loading Tests
- ✓ Submodules are NOT loaded on initial import
- ✓ Submodules load on-demand when accessed
- ✓ On-demand loading is fast (<100ms)

### 3. Submodule Access Tests
- ✓ rigLib - Rig tools accessible
- ✓ fluidLib - Fluid simulation tools accessible
- ✓ guiLib - GUI utilities accessible
- ✓ modelLib - Modeling tools accessible
- ✓ shaderLib - Shader utilities accessible
- ✓ pipelineLib - Pipeline utilities accessible
- ✓ utility - General utilities accessible

### 4. Nested Import Tests
- ✓ mayaLib.rigLib.base imports correctly
- ✓ mayaLib.rigLib.utils imports correctly
- ✓ mayaLib.fluidLib.base imports correctly
- ✓ mayaLib.guiLib.base imports correctly
- ✓ mayaLib.modelLib.base imports correctly

### 5. Rig Tools Tests
- ✓ rigLib.base modules accessible
- ✓ rigLib.utils modules accessible
- ✓ Control creation functions work

### 6. Fluid Tools Tests
- ✓ fluidLib.base modules accessible
- ✓ fluidLib.fire module accessible
- ✓ Fluid creation functions work

### 7. GUI System Tests
- ✓ guiLib.main_menu imports successfully
- ✓ MainMenu class is available
- ✓ Menu can be instantiated

### 8. Backwards Compatibility Tests
- ✓ `import mayaLib` works
- ✓ `from mayaLib import rigLib` works
- ✓ `import mayaLib.rigLib` works
- ✓ `from mayaLib.rigLib import base` works

### 9. Special Modules Tests
- ✓ Ziva module has `is_available()` function
- ✓ bifrostLib has `is_available()` function
- ✓ Availability checking works without loading plugins

### 10. Introspection Tests
- ✓ `dir(mayaLib)` returns correct attributes
- ✓ Module discovery works via introspection

## Expected Output

### Successful Run

```
======================================================================
DevPyLib Lazy Loading - End-to-End Verification
======================================================================

✓ Running inside Maya environment

Basic Import Tests:
✓ Library Import - mayaLib imported in 1.25ms

Lazy Loading Tests:
✓ Lazy Loading Behavior - 6/6 submodules not loaded on import
✓ On-Demand Loading - rigLib loaded on access in 45.32ms

Submodule Access Tests:
✓ Access rigLib - Rig tools
✓ Access fluidLib - Fluid simulation tools
✓ Access guiLib - GUI utilities
✓ Access modelLib - Modeling tools
✓ Access shaderLib - Shader utilities
✓ Access pipelineLib - Pipeline utilities
✓ Access utility - General utilities

...

======================================================================
Test Summary
======================================================================
Passed:  32/32
Failed:  0/32
Skipped: 0/32

======================================================================
✓ ALL TESTS PASSED!
======================================================================

✓ Ready for production use in Maya!
```

## Troubleshooting

### Issue: Import errors for Maya modules

**Symptom:** Tests fail with "No module named 'maya.cmds'"

**Solution:** You're running outside Maya. Use mayapy or Maya Script Editor instead.

### Issue: Some tests are skipped

**Symptom:** Tests show "Maya environment required"

**Solution:** This is expected when running with regular Python. Run with mayapy or in Maya.

### Issue: "Maya dependencies required" for all tests

**Symptom:** Many tests skipped due to missing dependencies

**Solution:**
1. Check that Maya is properly installed
2. Verify DEVPYLIB_PATH is set in Maya.env
3. Ensure userSetup.py is loading mayaLib correctly
4. Check Script Editor for import errors on Maya startup

### Issue: Menu system test fails

**Symptom:** "GUI Main Menu - Maya/Qt environment required"

**Solution:**
1. Ensure you're running inside Maya (not mayapy in batch mode)
2. Maya UI must be fully initialized (use evalDeferred for startup tests)
3. Check that PySide2/PySide6 is available

### Issue: Performance not improved

**Symptom:** Import time is still high (>10ms)

**Solution:**
1. Run the benchmark: `python mayaLib/test/benchmark_startup.py`
2. Check that lazy loading is actually active (submodules not loaded on import)
3. Verify no eager imports remain in __init__.py files

## Performance Verification

To measure actual performance improvement:

```python
import time
import sys

# Clean module cache
for key in list(sys.modules.keys()):
    if key.startswith('mayaLib'):
        del sys.modules[key]

# Measure import time
start = time.perf_counter()
import mayaLib
elapsed = (time.perf_counter() - start) * 1000

print(f"Import time: {elapsed:.2f}ms")

# Expected: ~1-2ms with lazy loading (was ~15-20ms with eager loading)
```

## Manual Testing Checklist

After running the automated tests, manually verify:

- [ ] Maya starts without errors
- [ ] DevPyLib menu appears in Maya menu bar
- [ ] Menu items are populated correctly
- [ ] Clicking a menu item opens the correct tool
- [ ] Tool UIs function normally
- [ ] No error messages in Script Editor
- [ ] Startup time feels faster (subjective but noticeable)

## Creating a Rig (Manual Test)

To fully verify rigLib functionality:

```python
# In Maya Script Editor
from mayaLib.rigLib.base import module

# Create a test rig
rig = module.Base(
    character="TestChar",
    module_name="test_module"
)

# Should create rig hierarchy without errors
# Verify in Outliner:
# - TestChar_rig_GRP exists
# - Contains global_CTRL, model_GRP, etc.
```

## Creating Fluid Effects (Manual Test)

To fully verify fluidLib functionality:

```python
# In Maya Script Editor
from mayaLib.fluidLib import fire

# Create a fire effect
fire_effect = fire.Fire(
    name="test_fire"
)

# Should create fluid container and emitter
# Verify in Outliner:
# - test_fire_GRP exists
# - Contains fluidShape and emitter nodes
```

## Success Criteria

The verification is successful when:

1. ✅ All automated tests pass (or show expected skips)
2. ✅ Import time is <5ms (target: 1-2ms)
3. ✅ Menu system loads correctly
4. ✅ No errors in Script Editor during Maya startup
5. ✅ Rig tools work as expected
6. ✅ Fluid tools work as expected
7. ✅ All existing import patterns work (backwards compatible)
8. ✅ Maya startup feels noticeably faster

## Reporting Issues

If tests fail, please report:

1. Maya version (Help > About Maya)
2. Python version (in Script Editor: `import sys; print(sys.version)`)
3. DevPyLib path location
4. Full error message from Script Editor
5. Output from verification script
6. Steps to reproduce the issue

## Next Steps After Verification

Once verification passes:

1. Run the full test suite: `pytest mayaLib/test/`
2. Run the performance benchmark: `python mayaLib/test/benchmark_startup.py`
3. Test with actual production scenes and workflows
4. Collect feedback from artists on startup performance
5. Monitor for any regressions or issues

## Additional Resources

- **Lazy Loading Pattern Documentation:** `.auto-claude/specs/.../LAZY_PATTERN.md`
- **Implementation Plan:** `.auto-claude/specs/.../implementation_plan.json`
- **Performance Benchmark:** `mayaLib/test/benchmark_startup.py`
- **Full Test Suite:** `mayaLib/test/test_lazy_loading_full.py`
- **CLAUDE.md:** Architecture and development guidelines

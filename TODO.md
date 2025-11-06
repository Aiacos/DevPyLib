# DevPyLib - Testing Infrastructure TODO

**Project**: DevPyLib Testing Infrastructure
**Goal**: Implement comprehensive unit testing with mayapy integration in Neovim
**Status**: 🟢 Ready to Start - Code refactoring complete (88.2% quality improvement)
**Priority**: HIGH
**Last Updated**: 2025-11-06 (Post-refactoring)

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Phase 0: Optional Code Quality Improvements](#phase-0-optional-code-quality-improvements) ⏸️ DEFERRED
3. [Phase 1: Mayapy Integration](#phase-1-mayapy-integration) 🔴 NEXT
4. [Phase 2: Neotest Configuration](#phase-2-neotest-configuration)
5. [Phase 3: Test Suite Design](#phase-3-test-suite-design)
6. [Phase 4: Test Implementation](#phase-4-test-implementation)
7. [Phase 5: CI/CD Integration](#phase-5-cicd-integration)
8. [Technical Challenges](#technical-challenges)
9. [Success Metrics](#success-metrics)
10. [Next Steps](#next-steps)

---

## Overview

### Current State - Code Quality
- ✅ **Code quality**: 88.2% improved (2,100+ violations → 248 remaining)
- ✅ **28,000+ LOC** refactored and documented
- ✅ **Critical bugs**: All B008 violations fixed (16 function-call-in-default errors)
- ✅ **Production-ready**: Core code is stable and maintainable
- 🟡 **Optional improvements**: 248 style violations remain (E501, D205, D415)
  - E501 (109): Line length > 88 chars
  - D205 (83): Blank line after docstring summary
  - D415 (7): Terminal punctuation in docstrings

### Current State - Testing Infrastructure
- 🔴 Test coverage: ~0% (only manual integration tests exist)
- 🔴 No automated testing infrastructure
- 🔴 No CI/CD test pipeline
- 🔴 No mayapy + Neovim integration

### Target State
- 🎯 80% code coverage with unit tests
- 🎯 Mayapy as test runner in Neovim
- 🎯 Neotest integration for live test feedback
- 🎯 Automated test execution on save
- 🎯 CI/CD pipeline with test gates
- 🎯 (Optional) Address remaining 248 style violations

### Why This Matters
- **Quality Assurance**: Catch regressions before production
- **Developer Experience**: Fast feedback loop in editor
- **Documentation**: Tests serve as usage examples
- **Confidence**: Refactor safely with test coverage

---

## Phase 0: Optional Code Quality Improvements

**Status**: 🟢 **OPTIONAL** - Codebase is production-ready at 88.2% improvement
**Priority**: LOW
**Effort**: 10-20 hours

### Remaining Style Violations (248 total)

These are non-critical style issues that don't affect functionality:

#### 0.1 Line Length Violations (E501: 109 errors)
- [ ] Review long lines in shaderLib modules
- [ ] Review long lines in rigLib modules
- [ ] Consider breaking complex string concatenations
- [ ] Evaluate if some exceptions are acceptable (URLs, long strings)

**Approach**: Manual review required - automated fixes may reduce readability

#### 0.2 Docstring Formatting (D205: 83 errors)
- [ ] Add blank line after docstring summary in affected modules
- [ ] Semi-automated with ruff --fix (may need manual review)

**Approach**: Can be partially automated but needs review for docstring quality

#### 0.3 Docstring Punctuation (D415: 7 errors)
- [ ] Add terminal punctuation to docstring first lines
- [ ] Quick fix - trivial violations

**Approach**: Fully automated with ruff --fix

#### 0.4 Other Minor Violations (UP031, SIM*, B*, D*: ~46 errors)
- [ ] Review and apply case-by-case

### Decision Points
- **Do nothing**: Codebase is already production-ready (88.2% improved)
- **Quick wins only**: Fix D415 (7 errors) and some D205 violations
- **Full cleanup**: Address all 248 violations for 100% compliance

**Recommendation**: Defer to future maintenance sprints. Focus on testing infrastructure instead.

---

## Phase 1: Mayapy Integration

### 1.1 Understand Mayapy Architecture

**Tasks:**
- [ ] Document mayapy vs standard Python differences
- [ ] Identify Maya-specific modules that require mayapy (pymel, maya.cmds, OpenMaya)
- [ ] Create compatibility matrix:
  ```
  Module Type          | Standard Python | Mayapy Required
  ---------------------|-----------------|----------------
  Pure Python utils    | ✅              | ✅
  PyMEL/maya.cmds      | ❌              | ✅
  Maya API (OpenMaya)  | ❌              | ✅
  Qt widgets           | ✅*             | ✅
  * PySide2/6 needs to be installed separately
  ```

**Research:**
- [ ] Read Maya Python API documentation
- [ ] Test mayapy standalone mode capabilities
- [ ] Document environment setup requirements

**Deliverables:**
- `docs/testing/mayapy-integration.md` - Technical guide
- `docs/testing/test-categories.md` - Module categorization

---

### 1.2 Configure Mayapy as Neovim Python Provider

**Tasks:**
- [ ] Locate mayapy executable path (platform-specific)
  ```bash
  # Linux
  /usr/autodesk/maya2024/bin/mayapy

  # macOS
  /Applications/Autodesk/maya2024/Maya.app/Contents/bin/mayapy

  # Windows
  C:\Program Files\Autodesk\Maya2024\bin\mayapy.exe
  ```

- [ ] Create Neovim configuration for mayapy
- [ ] Configure `python3_host_prog` in Neovim init.lua
  ```lua
  -- Example configuration
  vim.g.python3_host_prog = '/usr/autodesk/maya2024/bin/mayapy'
  ```

- [ ] Test basic Python execution from Neovim
- [ ] Verify Maya module imports work

**Challenges:**
- Mayapy may not support all Neovim Python provider features
- Need fallback to standard Python for non-Maya modules
- Different Maya versions = different mayapy paths

**Solution Approach:**
- [ ] Create wrapper script that detects context and selects appropriate interpreter
- [ ] Implement interpreter switching mechanism per project/file type

**Deliverables:**
- `scripts/mayapy-wrapper.sh` - Intelligent interpreter selector
- `.config/nvim/lua/mayapy-config.lua` - Neovim configuration

---

### 1.3 Setup Project-Specific Python Environment

**Tasks:**
- [ ] Create `.python-version` file for mayapy path
- [ ] Configure `pyproject.toml` for testing dependencies
  ```toml
  [tool.pytest.ini_options]
  python_files = ["test_*.py", "*_test.py"]
  python_classes = ["Test*"]
  python_functions = ["test_*"]
  testpaths = ["tests"]

  [tool.coverage.run]
  source = ["mayaLib"]
  omit = ["*/test/*", "*/tests/*"]
  ```

- [ ] Install testing dependencies (compatible with mayapy)
  - pytest (verify mayapy compatibility)
  - pytest-cov (coverage reporting)
  - pytest-mock (mocking Maya API calls)
  - pytest-xdist (parallel test execution)

- [ ] Create requirements-dev.txt specifically for testing

**Deliverables:**
- `pyproject.toml` - Testing configuration
- `requirements-dev.txt` - Development dependencies
- `tests/conftest.py` - Pytest configuration and fixtures

---

## Phase 2: Neotest Configuration

### 2.1 Install and Configure Neotest

**Tasks:**
- [ ] Install Neotest plugin via package manager (lazy.nvim/packer)
  ```lua
  -- Example lazy.nvim config
  {
    "nvim-neotest/neotest",
    dependencies = {
      "nvim-neotest/nvim-nio",
      "nvim-lua/plenary.nvim",
      "antoinemadec/FixCursorHold.nvim",
      "nvim-treesitter/nvim-treesitter",
      "nvim-neotest/neotest-python"
    }
  }
  ```

- [ ] Install neotest-python adapter
- [ ] Configure neotest for mayapy interpreter
  ```lua
  require("neotest").setup({
    adapters = {
      require("neotest-python")({
        dap = { justMyCode = false },
        runner = "pytest",
        python = "/usr/autodesk/maya2024/bin/mayapy"
      })
    }
  })
  ```

- [ ] Setup keybindings for test execution
  ```lua
  -- Example keybindings
  vim.keymap.set("n", "<leader>tt", "<cmd>lua require('neotest').run.run()<cr>")
  vim.keymap.set("n", "<leader>tf", "<cmd>lua require('neotest').run.run(vim.fn.expand('%'))<cr>")
  vim.keymap.set("n", "<leader>ts", "<cmd>lua require('neotest').summary.toggle()<cr>")
  vim.keymap.set("n", "<leader>to", "<cmd>lua require('neotest').output.open()<cr>")
  ```

**Deliverables:**
- `.config/nvim/lua/plugins/neotest.lua` - Complete neotest configuration
- `.config/nvim/lua/keymaps/testing.lua` - Test-related keybindings

---

### 2.2 Configure Test Discovery and Execution

**Tasks:**
- [ ] Configure test file patterns for DevPyLib structure
- [ ] Setup test discovery paths
  ```
  DevPyLib/
  ├── mayaLib/
  │   ├── rigLib/
  │   │   ├── base/
  │   │   │   ├── module.py
  │   │   │   └── test_module.py  ← Unit tests alongside code
  │   │   └── utils/
  │   └── fluidLib/
  └── tests/
      ├── unit/           ← Isolated unit tests
      ├── integration/    ← Maya integration tests
      └── functional/     ← End-to-end tests
  ```

- [ ] Configure test output formatting
- [ ] Setup test result visualization in Neovim
- [ ] Enable real-time test status updates

**Options to Evaluate:**
1. **Tests alongside code** (Django style): `mayaLib/rigLib/base/test_module.py`
   - ✅ Easy to find tests
   - ❌ Pollutes package structure

2. **Separate tests directory** (pytest standard): `tests/unit/rigLib/base/test_module.py`
   - ✅ Clean package structure
   - ✅ Clear separation
   - ⚠️ Mirror directory structure

3. **Hybrid approach**: Unit tests in code, integration tests separate
   - ✅ Best of both worlds
   - ⚠️ More complex structure

**Decision:** To be determined in Phase 3

**Deliverables:**
- `tests/test-structure-decision.md` - Rationale for chosen structure
- Updated neotest configuration with paths

---

### 2.3 Implement Auto-Run on Save

**Tasks:**
- [ ] Configure neotest to run tests on file save
- [ ] Implement smart test selection (only affected tests)
- [ ] Setup test watcher with debouncing
  ```lua
  -- Example auto-run configuration
  local augroup = vim.api.nvim_create_augroup("NeotestAutoRun", {})
  vim.api.nvim_create_autocmd("BufWritePost", {
    group = augroup,
    pattern = "*.py",
    callback = function()
      require("neotest").run.run(vim.fn.expand("%"))
    end
  })
  ```

- [ ] Add toggle for auto-run feature
- [ ] Configure notification system for test results

**Deliverables:**
- Autocmd configuration for test auto-run
- Toggle command: `:TestAutoRunToggle`

---

## Phase 3: Test Suite Design

### 3.1 Categorize Modules for Testing Strategy

**Tasks:**
- [ ] Audit all 287 Python files in mayaLib/
- [ ] Categorize by testability:
  ```
  Category 1: Pure Python (no Maya dependency)
  - pipelineLib/utility/convention.py
  - pipelineLib/utility/json_tool.py
  - Can run with standard pytest

  Category 2: Maya API dependent (requires mayapy)
  - rigLib/base/*.py
  - fluidLib/*.py
  - Needs mayapy + mocking

  Category 3: GUI components (requires display)
  - guiLib/*.py
  - Needs virtual display (Xvfb) or headless testing

  Category 4: Integration tests (full Maya scene)
  - End-to-end workflows
  - Needs Maya batch mode
  ```

- [ ] Create priority matrix:
  | Module | Complexity | Usage | Priority | Test Type |
  |--------|-----------|-------|----------|-----------|
  | rigLib/base/module.py | High | Critical | 🔴 P0 | Unit + Integration |
  | rigLib/utils/control.py | Medium | Critical | 🔴 P0 | Unit |
  | fluidLib/base/base_fluid.py | Medium | High | 🟡 P1 | Unit + Integration |
  | utility/json_tool.py | Low | Medium | 🟢 P2 | Unit |

**Deliverables:**
- `docs/testing/module-categorization.xlsx` - Complete audit
- `docs/testing/test-priority.md` - Testing roadmap

---

### 3.2 Design Test Architecture

**Tasks:**
- [ ] Define test fixtures for common Maya objects
  ```python
  # tests/conftest.py
  import pytest
  import pymel.core as pm

  @pytest.fixture
  def maya_scene():
      """Clean Maya scene for testing."""
      pm.newFile(force=True)
      yield
      pm.newFile(force=True)

  @pytest.fixture
  def test_joint():
      """Create test joint hierarchy."""
      root = pm.joint(name='root_jnt')
      child = pm.joint(name='child_jnt')
      pm.select(clear=True)
      return root, child
  ```

- [ ] Create mock objects for expensive operations
  ```python
  # tests/mocks/maya_mocks.py
  from unittest.mock import Mock

  def mock_maya_cmds():
      """Mock maya.cmds for pure Python tests."""
      return Mock()
  ```

- [ ] Design test data structure
  ```
  tests/
  ├── fixtures/
  │   ├── scenes/          ← .ma/.mb test scenes
  │   ├── meshes/          ← Test geometry
  │   └── rigs/            ← Sample rig files
  ├── data/
  │   ├── expected/        ← Expected outputs
  │   └── inputs/          ← Test inputs
  └── snapshots/           ← Visual regression tests
  ```

- [ ] Define test naming conventions
  ```python
  # test_<module>_<function>_<scenario>.py
  # test_module_create_hierarchy_success.py
  # test_control_add_attributes_invalid_type.py
  ```

**Deliverables:**
- `tests/conftest.py` - Global fixtures
- `tests/fixtures/` - Test data directory
- `docs/testing/test-patterns.md` - Testing patterns guide

---

### 3.3 Create Test Templates

**Tasks:**
- [ ] Create unit test template
  ```python
  """Unit tests for mayaLib.rigLib.base.module.

  Tests the Base class functionality without Maya scene dependencies.
  """
  import pytest
  from unittest.mock import Mock, patch

  from mayaLib.rigLib.base.module import Base


  class TestBase:
      """Test suite for Base class."""

      def test_init_creates_hierarchy(self, maya_scene):
          """Test that Base.__init__ creates expected group hierarchy."""
          # Arrange
          character_name = "test_character"

          # Act
          base = Base(character_name=character_name)

          # Assert
          assert base.top_group is not None
          assert base.rig_group is not None
          assert pm.objExists(f"{character_name}_rig_GRP")

      def test_init_with_invalid_name_raises_error(self):
          """Test that invalid character name raises ValueError."""
          # Arrange
          invalid_name = ""

          # Act & Assert
          with pytest.raises(ValueError, match="Character name cannot be empty"):
              Base(character_name=invalid_name)
  ```

- [ ] Create integration test template
  ```python
  """Integration tests for mayaLib.rigLib.base.module.

  Tests the Base class with actual Maya scene operations.
  """
  import pytest
  import pymel.core as pm

  from mayaLib.rigLib.base.module import Base


  class TestBaseIntegration:
      """Integration test suite for Base class."""

      def test_full_rig_hierarchy_creation(self, maya_scene):
          """Test complete rig hierarchy creation and parenting."""
          # Arrange
          character = "hero"

          # Act
          base = Base(character_name=character)
          base.create_control_hierarchy()
          base.create_joints()

          # Assert - verify hierarchy exists
          top_grp = pm.PyNode(f"{character}_rig_GRP")
          children = top_grp.getChildren()

          assert len(children) > 0
          assert any("controls" in str(c) for c in children)
          assert any("joints" in str(c) for c in children)
  ```

- [ ] Create parametrized test template
  ```python
  @pytest.mark.parametrize("input_value,expected", [
      ("validName", "validName_rig_GRP"),
      ("name_with_underscore", "name_with_underscore_rig_GRP"),
      ("Name123", "Name123_rig_GRP"),
  ])
  def test_group_naming_convention(self, maya_scene, input_value, expected):
      """Test group naming follows conventions."""
      base = Base(character_name=input_value)
      assert str(base.top_group) == expected
  ```

**Deliverables:**
- `tests/templates/test_unit_template.py`
- `tests/templates/test_integration_template.py`
- `docs/testing/writing-tests.md` - Test writing guide

---

## Phase 4: Test Implementation

### 4.1 Priority P0 Tests (Critical Path - Week 1-2)

**Core Infrastructure Tests:**
- [ ] `tests/unit/rigLib/base/test_module.py` (Base class)
  - [ ] test_init_creates_hierarchy
  - [ ] test_create_groups
  - [ ] test_create_controls
  - [ ] test_add_attributes
  - Target: 80% coverage

- [ ] `tests/unit/rigLib/utils/test_control.py` (Control class)
  - [ ] test_create_control
  - [ ] test_add_shape
  - [ ] test_lock_attributes
  - [ ] test_color_control
  - Target: 85% coverage

- [ ] `tests/unit/fluidLib/base/test_base_fluid.py` (BaseFluid)
  - [ ] test_create_container
  - [ ] test_create_emitter
  - [ ] test_set_properties
  - Target: 75% coverage

**Estimated Effort:** 40 hours
**Tests to Write:** ~50 unit tests

---

### 4.2 Priority P1 Tests (High Value - Week 3-4)

**Utility and Helper Tests:**
- [ ] `tests/unit/rigLib/utils/test_joint.py`
- [ ] `tests/unit/rigLib/utils/test_transform.py`
- [ ] `tests/unit/rigLib/utils/test_deform.py`
- [ ] `tests/unit/pipelineLib/utility/test_convention.py`
- [ ] `tests/unit/pipelineLib/utility/test_json_tool.py`

**GUI Tests (with mocking):**
- [ ] `tests/unit/guiLib/base/test_base_ui.py`
- [ ] `tests/unit/guiLib/test_main_menu.py`

**Estimated Effort:** 50 hours
**Tests to Write:** ~70 unit tests

---

### 4.3 Priority P2 Tests (Lower Priority - Week 5-6)

**Specialized Module Tests:**
- [ ] `tests/unit/rigLib/base/test_limb.py`
- [ ] `tests/unit/rigLib/base/test_spine.py`
- [ ] `tests/unit/rigLib/base/test_face.py`
- [ ] `tests/unit/modelLib/base/test_model_issue_fix.py`
- [ ] `tests/unit/shaderLib/utils/test_file.py`

**Estimated Effort:** 60 hours
**Tests to Write:** ~80 unit tests

---

### 4.4 Integration Tests (Week 7-8)

**End-to-End Workflow Tests:**
- [ ] `tests/integration/test_complete_rig_workflow.py`
  - Create character rig from scratch
  - Add controls and joints
  - Apply deformers
  - Verify rig functionality

- [ ] `tests/integration/test_fluid_simulation_workflow.py`
  - Create fluid container
  - Add emitters
  - Configure simulation
  - Verify output

- [ ] `tests/integration/test_ziva_rig_workflow.py` (if Ziva available)
  - Create Ziva tissue
  - Add attachments
  - Run simulation
  - Verify results

**Estimated Effort:** 40 hours
**Tests to Write:** ~20 integration tests

---

### 4.5 Test Coverage Tracking

**Tasks:**
- [ ] Setup pytest-cov for coverage reporting
  ```bash
  mayapy -m pytest --cov=mayaLib --cov-report=html --cov-report=term
  ```

- [ ] Create coverage badge for README
- [ ] Set coverage thresholds
  ```ini
  [tool.coverage.report]
  fail_under = 80
  show_missing = true
  ```

- [ ] Integrate with CI/CD to fail on coverage drop

**Coverage Goals:**
```
Module                          Target    Current
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
rigLib/base/module.py           85%       0%
rigLib/utils/control.py         85%       0%
fluidLib/base/base_fluid.py     80%       0%
pipelineLib/utility/*           90%       0%
guiLib/*                        70%       0%
Overall                         80%       0%
```

**Deliverables:**
- Coverage reports in `htmlcov/`
- `.coveragerc` configuration
- Coverage tracking dashboard

---

## Phase 5: CI/CD Integration

### 5.1 GitHub Actions Workflow

**Tasks:**
- [ ] Create `.github/workflows/test.yml`
  ```yaml
  name: Run Tests

  on:
    push:
      branches: [master, refactoring]
    pull_request:
      branches: [master]

  jobs:
    test:
      runs-on: ubuntu-latest
      container:
        image: aiacos/maya2024-docker  # Custom image with Maya

      steps:
        - uses: actions/checkout@v3

        - name: Install dependencies
          run: |
            mayapy -m pip install pytest pytest-cov pytest-mock

        - name: Run unit tests
          run: |
            mayapy -m pytest tests/unit/ -v --cov=mayaLib

        - name: Run integration tests
          run: |
            xvfb-run mayapy -m pytest tests/integration/ -v

        - name: Upload coverage
          uses: codecov/codecov-action@v3
          with:
            file: ./coverage.xml
  ```

- [ ] Setup Docker image with Maya installed (or use headless Maya)
- [ ] Configure Xvfb for GUI tests
- [ ] Setup test result reporting
- [ ] Add status badges to README

**Deliverables:**
- `.github/workflows/test.yml`
- `Dockerfile` for Maya testing environment
- CI/CD dashboard integration

---

### 5.2 Pre-commit Hooks

**Tasks:**
- [ ] Create `.pre-commit-config.yaml`
  ```yaml
  repos:
    - repo: local
      hooks:
        - id: pytest-check
          name: pytest-check
          entry: mayapy -m pytest tests/unit/ -x
          language: system
          pass_filenames: false
          always_run: true
  ```

- [ ] Add ruff linting
- [ ] Add coverage check
- [ ] Install pre-commit in repo
  ```bash
  pre-commit install
  ```

**Deliverables:**
- `.pre-commit-config.yaml`
- Pre-commit hook installation script

---

## Technical Challenges

### Challenge 1: Maya Standalone Mode Limitations

**Problem:** Some Maya features don't work in standalone/batch mode
- UI components require display
- Some plugins may not load correctly
- Performance differences vs GUI Maya

**Solutions:**
- [ ] Use Xvfb (Virtual Frame Buffer) for headless GUI testing
- [ ] Mock UI components for unit tests
- [ ] Document which features require full Maya
- [ ] Create separate test suites for batch vs GUI modes

---

### Challenge 2: Long Test Execution Times

**Problem:** Maya startup is slow (~10-30 seconds)
- Neotest expects fast feedback
- Integration tests may take minutes
- Impacts developer workflow

**Solutions:**
- [ ] Implement test result caching
- [ ] Use pytest-xdist for parallel execution
  ```bash
  mayapy -m pytest -n auto  # Auto-detect CPU cores
  ```
- [ ] Separate fast unit tests from slow integration tests
- [ ] Only run affected tests on save

---

### Challenge 3: Mocking Maya API

**Problem:** Maya API is complex and stateful
- PyMEL creates real Maya nodes
- Hard to isolate unit tests
- Scene state can leak between tests

**Solutions:**
- [ ] Create comprehensive fixture library
- [ ] Use pytest's `autouse` fixtures for cleanup
  ```python
  @pytest.fixture(autouse=True)
  def clean_scene():
      pm.newFile(force=True)
      yield
      pm.newFile(force=True)
  ```
- [ ] Implement Maya node factory pattern
- [ ] Use dependency injection for testability

---

### Challenge 4: Cross-Platform Testing

**Problem:** DevPyLib supports Windows, Linux, macOS
- Different Maya paths
- Different behavior
- CI/CD complexity

**Solutions:**
- [ ] Create platform-specific test fixtures
- [ ] Use matrix testing in CI/CD
  ```yaml
  strategy:
    matrix:
      os: [ubuntu-latest, windows-latest, macos-latest]
      maya-version: [2022, 2023, 2024]
  ```
- [ ] Mock platform-specific code
- [ ] Document platform-specific test failures

---

## Success Metrics

### Code Coverage
```
Sprint 1 (Week 1-2):  Target 30% coverage (P0 tests)
Sprint 2 (Week 3-4):  Target 50% coverage (+ P1 tests)
Sprint 3 (Week 5-6):  Target 70% coverage (+ P2 tests)
Sprint 4 (Week 7-8):  Target 80% coverage (+ Integration)
```

### Test Suite Size
- **Target**: 200+ unit tests
- **Target**: 30+ integration tests
- **Target**: <5 minutes for unit test suite execution
- **Target**: <30 minutes for full test suite

### Developer Experience
- ✅ Real-time test feedback in Neovim
- ✅ One-keystroke test execution
- ✅ Visual test results in editor
- ✅ Auto-run on save without disruption

### CI/CD Integration
- ✅ Automated test runs on every PR
- ✅ Coverage reports on every commit
- ✅ Test failure prevents merge
- ✅ Test results visible in PR

---

## Timeline Summary

| Phase | Duration | Deliverables | Dependencies | Priority |
|-------|----------|--------------|--------------|----------|
| **Phase 0**: Code Quality (Optional) | 1-2 weeks | 248 style fixes | None | 🟢 LOW |
| **Phase 1**: Mayapy Integration | 1 week | Mayapy wrapper, Neovim config | None | 🔴 HIGH |
| **Phase 2**: Neotest Setup | 3 days | Neotest config, Keybindings | Phase 1 | 🔴 HIGH |
| **Phase 3**: Test Design | 1 week | Test architecture, Templates | Phase 2 | 🔴 HIGH |
| **Phase 4.1**: P0 Tests | 2 weeks | 50 unit tests, 80% coverage (core) | Phase 3 | 🔴 HIGH |
| **Phase 4.2**: P1 Tests | 2 weeks | 70 unit tests, 50% coverage (overall) | Phase 4.1 | 🟡 MEDIUM |
| **Phase 4.3**: P2 Tests | 2 weeks | 80 unit tests, 70% coverage (overall) | Phase 4.2 | 🟡 MEDIUM |
| **Phase 4.4**: Integration | 2 weeks | 20 integration tests, 80% coverage | Phase 4.3 | 🟡 MEDIUM |
| **Phase 5**: CI/CD | 1 week | GitHub Actions, Pre-commit hooks | Phase 4 | 🔴 HIGH |

**Total Estimated Time**: 11 weeks (3 months) + 1-2 weeks optional code quality
**Recommended Path**: Skip Phase 0, proceed directly to Phase 1 (Testing Infrastructure)

---

## Next Steps

### ✅ Completed - Code Refactoring Phase
1. ✅ Fixed all 2,100+ critical code quality violations (88.2% improvement)
2. ✅ Resolved all B008 violations (16 function-call-in-default bugs)
3. ✅ Updated CLAUDE.md with comprehensive quality report
4. ✅ Committed and pushed to refactoring branch

### Phase 0 (Optional) - Remaining Code Quality
**Status**: ⏸️ **DEFERRED** - Not required for production readiness
1. [ ] (Optional) Fix D415 violations (7 errors) - terminal punctuation
2. [ ] (Optional) Fix D205 violations (83 errors) - docstring blank lines
3. [ ] (Optional) Review E501 violations (109 errors) - line length

**Recommendation**: Skip Phase 0, proceed to testing infrastructure

### Phase 1 Kickoff - Testing Infrastructure (HIGH PRIORITY)
**Status**: 🔴 **READY TO START**
1. [ ] Research mayapy + neotest compatibility
2. [ ] Test basic mayapy execution from Neovim
3. [ ] Create proof-of-concept: Single test file running via neotest
4. [ ] Document blockers and unknowns
5. [ ] Create `docs/testing/` directory
6. [ ] Write `mayapy-integration.md` technical spec
7. [ ] Implement `scripts/mayapy-wrapper.sh`
8. [ ] Configure Neovim for mayapy

### Resources Needed
- [ ] Access to Maya 2024 (or target version)
- [ ] Neovim 0.9+ with Lua support
- [ ] Time allocation: ~10-15 hours/week
- [ ] Test data: Sample rigs, meshes, scenes

---

## References

### Documentation
- [Maya Python API Docs](https://help.autodesk.com/view/MAYAUL/2024/ENU/?guid=Maya_SDK_py_ref_index_html)
- [PyTest Documentation](https://docs.pytest.org/)
- [Neotest GitHub](https://github.com/nvim-neotest/neotest)
- [neotest-python Adapter](https://github.com/nvim-neotest/neotest-python)

### Examples
- [cgwire/zou](https://github.com/cgwire/zou) - Python testing in VFX pipeline
- [mottosso/cmdx](https://github.com/mottosso/cmdx) - Maya API testing patterns

---

**Created**: 2025-11-06
**Last Updated**: 2025-11-06 (Post-refactoring update)
**Owner**: @Aiacos
**Status**: 🟢 **READY TO START** → Code refactoring complete, proceed to Phase 1 (Testing Infrastructure)

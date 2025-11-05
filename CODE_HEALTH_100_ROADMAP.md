# Roadmap to 100% Code Health
**Current Status**: 7.5/10 (93.5% PEP 8 compliance)
**Target**: 10/10 (100% Code Health)
**Gap Analysis**: 2025-11-05

---

## 📊 Current State Analysis

### What We Have ✅
- ✅ 100% Function naming (N802: 0 violations)
- ✅ 100% Parameter naming (N803: 0 violations)
- ✅ 100% Class naming (N801: 0 violations)
- ✅ 100% Import aliases (N813: 0 violations)
- ✅ 0 Critical bugs
- ✅ 0 Typos
- ✅ 0 Legacy aliases
- ✅ Python 3.10+ compatible
- ✅ Cross-platform (Windows/Linux/macOS)

### What's Missing 🔴

| Issue | Count | Impact | Effort | Priority |
|-------|-------|--------|--------|----------|
| **1. Local Variable Naming (N806)** | 130 | -0.5 pts | High | Medium |
| **2. Missing Type Hints** | 303 funcs | -0.5 pts | Very High | Medium |
| **3. Code Complexity (C901)** | 28 funcs | -0.5 pts | High | Low |
| **4. MEL Injection Risk** | 153 calls | -0.3 pts | Medium | High |
| **5. Missing Docstrings** | ~200 funcs | -0.3 pts | High | Low |
| **6. No Unit Tests** | 0 tests | -0.2 pts | Very High | Medium |
| **7. File Encoding** | 4 calls | -0.1 pts | Low | High |
| **8. Global Variables (N816)** | 23 | -0.1 pts | Medium | Low |

**Total Gap**: ~2.5 points to reach 10/10

---

## 🎯 Roadmap to 100%

### PHASE 1: Quick Wins (2-4 hours) 🟢
**Impact**: +0.6 points → 8.1/10

#### 1.1. Fix File Operations Without Encoding ⚡ CRITICAL
**Violations**: 4 occorrences
**Effort**: 15 minutes
**Impact**: +0.1 points

```python
# BEFORE:
with open(file_path, 'r') as f:

# AFTER:
with open(file_path, 'r', encoding='utf-8') as f:
```

**Files to fix**:
```bash
grep -rn "open(" mayaLib/ --include="*.py" --exclude-dir=test | grep -v "encoding="
```

---

#### 1.2. Fix Remaining N806 Local Variables (Priority Files) 🔴
**Violations**: 130 total, fix top 50% (6 files)
**Effort**: 2-3 hours
**Impact**: +0.25 points

**Top 6 files** (65 violations = 50%):
1. `pole_vector.py` - 16 violations
2. `bvh_importer.py` - 14 violations
3. `collision.py` - 14 violations
4. `lib_manager.py` - 11 violations
5. `ziva_build.py` - 10 violations
6. `facial_rig.py` - 9 violations

**Common patterns**:
```python
# BEFORE:
selJoints = ik_handle.getJointList()
newJoints = pm.ls(sl=True)
rigScale = 1.0
myParent = TinyDAG(...)

# AFTER:
sel_joints = ik_handle.getJointList()
new_joints = pm.ls(sl=True)
rig_scale = 1.0
my_parent = TinyDAG(...)
```

---

#### 1.3. Sanitize MEL.eval Calls (Security) 🔐
**Risk**: High - Command injection potential
**Occurrences**: 153 calls
**Effort**: 1 hour
**Impact**: +0.25 points

**Strategy**: Add input validation wrapper
```python
# Create utility function:
def safe_mel_eval(mel_command: str, allowed_commands: list = None) -> Any:
    """Execute MEL command with input validation.

    Args:
        mel_command: MEL command string
        allowed_commands: Whitelist of allowed command prefixes

    Raises:
        ValueError: If command contains dangerous patterns
    """
    # Blacklist dangerous patterns
    dangerous = [';', '&&', '||', '`', '$', 'system', 'exec']
    if any(pattern in mel_command for pattern in dangerous):
        raise ValueError(f"Potentially dangerous MEL command: {mel_command}")

    # Whitelist validation
    if allowed_commands:
        if not any(mel_command.startswith(cmd) for cmd in allowed_commands):
            raise ValueError(f"Command not in whitelist: {mel_command}")

    return pm.mel.eval(mel_command)

# Usage:
# BEFORE:
pm.mel.eval(f"doSomething {user_input}")  # DANGEROUS

# AFTER:
safe_mel_eval(f"doSomething {user_input}", allowed_commands=['doSomething'])
```

**Action**:
1. Create `mayaLib/rigLib/utils/safe_mel.py`
2. Replace critical `mel.eval()` calls (at least in user-facing code)
3. Document remaining safe usages

---

**PHASE 1 TOTAL**: +0.6 points → **8.1/10** ✅

---

### PHASE 2: Medium Effort (1-2 weeks) 🟡
**Impact**: +0.9 points → 9.0/10

#### 2.1. Add Type Hints to Public Functions 📝
**Missing**: ~303 functions without type hints
**Target**: Add to top 100 most-used functions (30% coverage)
**Effort**: 1 week
**Impact**: +0.3 points

**Priority order**:
1. Core utilities (`util.py`, `control.py`, `joint.py`)
2. Deformation tools (`deform.py`, `dynamic.py`)
3. Shader/lookdev (`shader.py`, `texture.py`)
4. Pipeline utilities (`lib_manager.py`, `convention.py`)

**Example**:
```python
# BEFORE:
def create_control(name, shape='circle', color=None):
    pass

# AFTER:
from typing import Optional, Union
from pymel.core.nodetypes import Transform

def create_control(
    name: str,
    shape: str = 'circle',
    color: Optional[Union[int, tuple[float, float, float]]] = None
) -> Transform:
    pass
```

**Tools to help**:
- `mypy` for type checking
- `pyannotate` for auto-generating type hints from runtime traces
- `monkeytype` for runtime type inference

---

#### 2.2. Complete N806 Local Variable Fixes 🔧
**Remaining**: 65 violations in 14+ files
**Effort**: 2-3 days
**Impact**: +0.25 points

Finish fixing all remaining camelCase local variables.

---

#### 2.3. Add Core Docstrings 📚
**Missing**: ~200 functions without proper docstrings
**Target**: Add to all public functions in core modules
**Effort**: 3-4 days
**Impact**: +0.2 points

**Format** (Google style):
```python
def create_ik_handle(
    start_joint: str,
    end_joint: str,
    solver: str = 'ikRPsolver'
) -> tuple[str, str]:
    """Create an IK handle between two joints.

    Args:
        start_joint: Name of the start joint
        end_joint: Name of the end joint
        solver: IK solver type ('ikRPsolver', 'ikSCsolver', 'ikSplineSolver')

    Returns:
        Tuple of (ik_handle, effector) node names

    Raises:
        ValueError: If joints don't form a valid chain
        RuntimeError: If IK creation fails

    Example:
        >>> handle, eff = create_ik_handle('shoulder', 'wrist')
        >>> pm.setAttr(f'{handle}.twist', 45)
    """
    pass
```

---

#### 2.4. Create Unit Test Framework 🧪
**Current**: 0 unit tests (only integration tests)
**Target**: Test framework + 20% coverage of core functions
**Effort**: 1 week
**Impact**: +0.15 points

**Structure**:
```
mayaLib/
├── test/
│   ├── unit/              # NEW: Unit tests
│   │   ├── test_util.py
│   │   ├── test_control.py
│   │   ├── test_deform.py
│   │   └── ...
│   └── integration/       # Existing integration tests
│       └── ...
```

**Framework**: pytest + pytest-maya (for Maya testing)

**Example test**:
```python
# test/unit/test_util.py
import pytest
from mayaLib.rigLib.utils import util

def test_get_distance():
    """Test distance calculation between two transforms."""
    result = util.get_distance([0, 0, 0], [3, 4, 0])
    assert result == 5.0

def test_list_objects_under_group():
    """Test listing objects under a group."""
    # Mock Maya scene...
    pass
```

---

**PHASE 2 TOTAL**: +0.9 points → **9.0/10** ✅

---

### PHASE 3: Long-term (1-2 months) 🔵
**Impact**: +1.0 points → 10.0/10

#### 3.1. Reduce Code Complexity (C901) 🎯
**Violations**: 28 functions with complexity > 10
**Target**: Reduce to < 5 violations
**Effort**: 2-3 weeks
**Impact**: +0.3 points

**Top offenders**:
1. `bvh_importer._read_bvh()` - Complexity 29
2. `human_ik.__init__()` - Complexity 45
3. `flexiplane.__init__()` - Complexity 35
4. `limb.__init__()` - Complexity 28
5. `base_rig._setup_face_rig()` - Complexity 25

**Refactoring strategies**:
- Extract helper methods
- Use strategy pattern for conditionals
- Break initialization into phases
- Use factory methods

**Example**:
```python
# BEFORE (Complexity 45):
def __init__(self, character_name, auto_t_pose=False, ...):
    # 200 lines of initialization
    # Multiple nested if/else
    # Complex setup logic
    pass

# AFTER (Complexity 15):
def __init__(self, character_name, auto_t_pose=False, ...):
    self._validate_inputs(character_name)
    self._setup_joints()
    self._setup_controls()
    if auto_t_pose:
        self._apply_t_pose()
    self._finalize()

def _setup_joints(self):
    # Extracted logic
    pass

def _setup_controls(self):
    # Extracted logic
    pass
```

---

#### 3.2. Complete Type Hints Coverage 📝
**Target**: 80-90% coverage (240+ functions)
**Effort**: 2-3 weeks
**Impact**: +0.2 points

Add type hints to all remaining public functions and methods.

**Use tools**:
- `mypy --strict` for validation
- `pyright` for additional checking
- CI/CD integration for automated checking

---

#### 3.3. Comprehensive Documentation 📖
**Target**: 90%+ docstring coverage
**Effort**: 1-2 weeks
**Impact**: +0.15 points

- Complete all missing docstrings
- Add module-level documentation
- Create usage examples
- Document all exceptions

---

#### 3.4. Full Unit Test Coverage 🧪
**Target**: 60-70% code coverage
**Effort**: 3-4 weeks
**Impact**: +0.2 points

- Test all core utilities
- Test all deformers
- Test all controls
- Mock Maya API for faster tests
- CI/CD integration

---

#### 3.5. Address Remaining N816 Global Variables 🔧
**Violations**: 23 (mostly in test code)
**Effort**: 2-3 days
**Impact**: +0.1 points

Clean up test code and configuration dictionaries.

---

#### 3.6. Code Coverage & CI/CD 🚀
**Current**: No automated testing
**Target**: Full CI/CD pipeline
**Effort**: 1 week
**Impact**: +0.05 points

**Pipeline**:
```yaml
# .github/workflows/test.yml
name: Test Suite
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run linters
        run: |
          ruff check .
          mypy mayaLib/
      - name: Run tests
        run: pytest --cov=mayaLib
```

---

**PHASE 3 TOTAL**: +1.0 points → **10.0/10** ✅

---

## 📋 Prioritized Action Plan

### Immediate (This Week) - Quick Wins
**Effort**: 4 hours | **Gain**: +0.6 points → 8.1/10

1. ✅ Fix 4 file operations without encoding (15 min)
2. ✅ Create `safe_mel_eval()` wrapper (1 hour)
3. ✅ Fix top 6 N806 files (2-3 hours)

### Short-term (This Month) - Medium Effort
**Effort**: 2 weeks | **Gain**: +0.9 points → 9.0/10

4. 📝 Add type hints to top 100 functions (1 week)
5. 🔧 Complete N806 fixes (2-3 days)
6. 📚 Add docstrings to core modules (3-4 days)
7. 🧪 Create unit test framework + 20% coverage (1 week)

### Long-term (Next 2 Months) - Full Coverage
**Effort**: 2 months | **Gain**: +1.0 points → 10.0/10

8. 🎯 Reduce code complexity in top 10 functions (2-3 weeks)
9. 📝 Complete type hints (80-90% coverage) (2-3 weeks)
10. 📖 Complete documentation (90%+ docstrings) (1-2 weeks)
11. 🧪 Full unit test coverage (60-70%) (3-4 weeks)
12. 🔧 Clean up remaining N816 (2-3 days)
13. 🚀 Set up CI/CD pipeline (1 week)

---

## 🎯 Recommended Approach

### Option A: Aggressive (1 month to 9.0/10)
Focus on Phases 1 + 2 only:
- Week 1: Quick wins (8.1/10)
- Week 2-3: Type hints + docstrings
- Week 4: Unit tests

**Pros**: Fast improvement, manageable scope
**Cons**: Won't reach 10/10

### Option B: Balanced (3 months to 10/10) ⭐ RECOMMENDED
Steady progress through all phases:
- Month 1: Phases 1 + 2 (9.0/10)
- Month 2-3: Phase 3 (10/10)

**Pros**: Sustainable pace, complete coverage
**Cons**: Longer timeline

### Option C: Quick Wins Only (1 week to 8.1/10)
Just Phase 1:
- Immediate security improvements
- Fast visible progress
- Low effort

**Pros**: Minimal effort, high impact
**Cons**: Stops at 8.1/10

---

## 💰 Effort Breakdown

| Phase | Tasks | Time | Gain |
|-------|-------|------|------|
| **Phase 1** | Quick wins | 4 hours | +0.6 → 8.1/10 |
| **Phase 2** | Medium effort | 2 weeks | +0.9 → 9.0/10 |
| **Phase 3** | Long-term | 2 months | +1.0 → 10.0/10 |
| **TOTAL** | - | ~2.5 months | +2.5 → 10.0/10 |

---

## 🚀 Getting Started (Next Steps)

### Step 1: Run Phase 1 Quick Wins (4 hours)

```bash
# 1. Fix file encodings (15 min)
grep -rn "open(" mayaLib/ --include="*.py" --exclude-dir=test | grep -v "encoding="
# Add encoding='utf-8' to each

# 2. Create safe_mel wrapper (1 hour)
# Create mayaLib/rigLib/utils/safe_mel.py

# 3. Fix top 6 N806 files (2-3 hours)
python -m ruff check mayaLib/rigLib/utils/pole_vector.py --select N806
# Fix each violation
```

### Step 2: Measure Progress

```bash
# Re-run health checks
python -m ruff check mayaLib/ --exclude test/ --exclude plugin/ --statistics
```

### Step 3: Iterate

Continue with Phase 2 tasks as time allows.

---

## 📊 Expected Final Metrics

After completing all phases:

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| **Code Health** | 7.5/10 | 10.0/10 | 🎯 |
| **PEP 8 Compliance** | 93.5% | 100% | 🎯 |
| **Type Hints** | ~40% | 80-90% | 🎯 |
| **Docstrings** | ~60% | 90%+ | 🎯 |
| **Unit Tests** | 0% | 60-70% | 🎯 |
| **Code Coverage** | 0% | 60-70% | 🎯 |
| **Complexity Violations** | 28 | <5 | 🎯 |
| **Security Issues** | 153 | 0 | 🎯 |

---

## ✅ Success Criteria for 10/10

- ✅ 100% PEP 8 naming compliance (all N8xx rules)
- ✅ 80%+ type hint coverage
- ✅ 90%+ docstring coverage
- ✅ 60%+ unit test coverage
- ✅ <5 high complexity functions (C901)
- ✅ 0 security vulnerabilities
- ✅ 0 file operations without encoding
- ✅ CI/CD pipeline with automated checks
- ✅ All core functions tested
- ✅ Professional documentation

---

**Generated**: 2025-11-05
**Status**: Roadmap Ready
**Next Action**: Execute Phase 1 Quick Wins (4 hours)

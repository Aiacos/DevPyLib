# Limb.py Refactoring Design

**Date**: 2026-02-21
**Branch**: autoclaude
**Approach**: Hybrid (A+B+C) — best of all three

## Guiding principle

- **Distinct domain** -> separate module (from C)
- **Limb-specific orchestration** -> private methods on class (from B)
- **Structured types everywhere** -> NamedTuples for return values (from A)

## Problem

`limb.py` has functions that are too long and use unnamed return types:

- `build_ik_controls` (300 lines) — smart foot roll logic inline (~170 lines)
- `switch_ik_fk` (150 lines) — IK visibility, FK visibility, locator creation mixed
- Return types are raw tuples (4-element from FK, 6-element from IK)
- `Limb.__init__` is ~230 lines of sequential orchestration

## Design

### 1. NamedTuples (from A)

`FKResult` and `IKResult` at module level. NamedTuple preserves positional
unpacking. All internal code uses named fields.

### 2. Smart foot roll -> separate module (from C)

**New file: `rigLib/utils/smart_foot_roll.py`**

The smart foot roll is a self-contained domain: clamp nodes, setRange nodes,
multiplyDivide nodes, driven keys for tilt. It takes a control + foot roll
groups, creates utility node networks. No knowledge of Limb class needed.

```
smart_foot_roll.py
├── build()          — public entry point, wires all foot roll attrs
├── _build_roll()    — heel/toe roll clamp+setRange chain
├── _build_tilt()    — inner/outer tilt driven keys
└── _build_extras()  — lean, toe spin, toe wiggle attrs
```

### 3. IK/FK wiring -> extend ikfk_switch.py (from C)

Add `wire_ikfk_switch()` to existing `ikfk_switch.py`. This is the initial
wiring (attributes, reverse nodes, visibility connections). Distinct from
`IKFKSwitch` class which does runtime snapping.

```
ikfk_switch.py (existing)
├── IKFKSwitch class        — runtime snap (unchanged)
├── install_ikfk()          — scriptNode installer (unchanged)
├── wire_ikfk_switch()      — NEW: initial attribute/visibility wiring
├── _create_switch_locator() — NEW: get/create switchIKFK_LOC
├── _wire_ik_visibility()    — NEW: connect IK side to reverse
└── _wire_fk_visibility()    — NEW: connect FK side to switch attrs
```

### 4. Decompose Limb.__init__ (from B)

The constructor becomes a readable sequence of named phases:

```python
def __init__(self, ...):
    params = self._resolve_params(prefix, limb_joints, legacy_kwargs, ...)
    self._build_scaffold(params.prefix, base_rig)
    fk = self._build_fk(params)
    ik, pv = self._build_ik(params)
    self._setup_switching(params, fk, ik, pv)
    self._setup_scapula_clavicle(params, fk)
    self._store_results(ik)
```

Each phase is a private method of ~20-40 lines.

### 5. Keep free functions as public API

The existing free functions (`build_fk_controls`, `build_ik_controls`, etc.)
stay as the public module API. The class methods delegate to them.
This preserves the current architecture — the class is a stateful orchestrator,
the free functions are stateless builders.

### 6. Migrate API to snake_case

`get_module_dict()` returns snake_case keys with camelCase compat keys.
Update `rig.py` callers to use snake_case.

## File changes

| File | Change |
|------|--------|
| `rigLib/utils/smart_foot_roll.py` | NEW — extracted foot roll wiring |
| `rigLib/utils/ikfk_switch.py` | ADD wire_ikfk_switch + 3 helpers |
| `rigLib/utils/__init__.py` | Register smart_foot_roll |
| `rigLib/base/limb.py` | NamedTuples, decompose __init__, slim build_ik_controls |
| `rigLib/core/rig.py` | Update dict key references to snake_case |

## Final file structure

```
limb.py (~800 lines, was 1160)
├── FKResult (NamedTuple)
├── IKResult (NamedTuple)
├── _build_control_with_ik_handle()   # helper (unchanged)
├── build_simple_scapula()            # free function (unchanged)
├── build_clavicle()                  # free function (unchanged)
├── build_dynamic_scapula()           # free function (unchanged)
├── build_fk_controls() -> FKResult   # return type improved
├── build_pole_vector()               # free function (unchanged)
├── build_ik_controls() -> IKResult   # slimmed (~130 lines, was ~300)
├── class Limb
│   ├── __init__()                    # 5-line orchestrator
│   ├── _resolve_params()             # from B
│   ├── _build_scaffold()             # from B
│   ├── _build_fk()                   # from B
│   ├── _build_ik()                   # from B
│   ├── _setup_switching()            # delegates to ikfk_switch
│   ├── _setup_scapula_clavicle()     # from B
│   ├── get_main_limb_ik()
│   ├── get_main_ik_control()
│   ├── get_module_dict()             # snake_case keys + compat
│   ├── make_*()                      # thin wrappers
│   └── switch_ik_fk()                # delegates to ikfk_switch
├── class Arm(Limb)
└── # Backwards-compat aliases
```

## Constraints

- No behaviour change — identical Maya scene graph output
- 100% backwards compatible (NamedTuple unpacking, dict compat keys, method aliases)
- No new dependencies

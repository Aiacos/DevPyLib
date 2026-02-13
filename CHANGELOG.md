# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- Ongoing documentation improvements and wiki updates

### Changed
- **UV Processing Performance Optimization**: Replaced per-vertex Maya API calls with batch operations in AutoUV class
  - `check_uv_in_boundaries()`, `check_uv_boundaries()`, and `cut_uv_tile()` now use single batch queries instead of per-vertex loops
  - Achieves 69.1x-80.1x speedup for meshes with 10K+ UVs by reducing API call overhead
  - API calls reduced from O(N) to O(1) where N is the number of UVs
  - Eliminates Python-to-C++ marshaling overhead on large UV sets
  - Maintains identical behavior - pure performance optimization with no functional changes
  - Comprehensive test coverage validates correctness and performance improvements

---

## [2.0.0] - 2026-01-22

Major release featuring Luna integration, comprehensive code quality refactoring, and expanded documentation.

### Added
- **Luna Integration**: Full integration of Luna node-based rigging system as submodule (06869f6)
  - Auto-start preference for Luna on Maya startup (326ba4e)
  - Lazy loading for improved performance (681447f)
  - MQtUtil compatibility patches for PyMEL (1caecb1)
  - Namespace module injection for proper import chain (f07b452)
- **Comprehensive Wiki Documentation**: New wiki pages for all modules (2f65392)
- **AriseLib Documentation**: Base rigging class with core functionalities (c30759f)
- **Selection Set Improvements**: Existence checks for BaseRig selection set creation (2998635)

### Changed
- **Luna Submodule Updates**:
  - Quick Start Builder tutorial (5a1be14)
  - Fixed empty node palette issue (b5d05bd)
  - MQtUtil fix and workaround removal (e15ed57)

### Fixed
- Luna import issues by removing auto-created placeholder module (4d21a8a)
- Luna module namespace injection strategy (bf7c863)
- Qt signal/slot warning in main_menu.py (c264e37)

---

## [1.5.0] - 2025-12-19

### Added
- **Eye Aim Setup**: Improved compatibility and fallback mechanisms (eb2cb23, 34b90ba)
- **Object Placement**: New functionality for placing objects along curves (818b4c2)

### Changed
- Updated polyCleanupArgList MEL command strings (7a0474c)
- Refactored Maya.env for cross-platform compatibility (dbc0f12)

### Fixed
- Missing slot_name argument to connect_normal call (1da61b5)

---

## [1.4.0] - 2025-11-07

Major code quality refactoring release achieving 93.9% violation reduction.

### Added
- **Neovim Integration**: Full mayapy integration for LSP and testing support (b9b7944)
  - Automatic neotest configuration (f909e01)
  - AstroNvim support and exrc security info (48296a1)
- **Testing Infrastructure**: Comprehensive roadmap in TODO.md (60b3d8d)
- **Documentation**:
  - 178 function/method/class docstrings (cdf6bb9)
  - 25 missing module docstrings (f94fdef)
  - Built-in shadowing fixes and quality assessment (128bb87)
  - Basedpyright static analysis section (630aabd)

### Changed
- **Code Quality Improvements**:
  - Complete PEP 8 compliance (20cdc45)
  - Black-compatible formatting across entire codebase (80ce562)
  - Auto-fix 769 ruff violations (ecc44e3)
  - 1,311 instance attributes fixed + 56 legacy aliases removed (bcfed64)
  - PEP 8 naming conventions in 59 files (aeb0b6b)
- **Naming Conventions**:
  - Fix N802/N813/N999 violations and configure Maya patterns (6942def)
  - Correct 52 attribute naming and function call errors (065f7b0)
  - Correct parameter naming - baseRig/baseObj to snake_case (dc294b2)
- **Type Safety**:
  - Add type hints to eliminate type checker warnings (a21a074)
  - Type casts for resolve_optional returns (0e2199f)
  - Resolve basedpyright errors (bec526c)

### Fixed
- **B008 Violations**: All function calls in default arguments eliminated (bf8ac41)
- **Docstring Issues**:
  - D205: Blank line after summary (83 fixes)
  - D415: Terminal punctuation (53 fixes)
  - D417: Undocumented parameters (14 fixes)
  - D414: Empty docstring sections (75e62e4)
- **Runtime Errors**: 23 additional runtime errors from incomplete refactoring (0090229)
- Suppress 'undefined-global' warnings for vim in .nvim.lua (04fc518)
- D212 docstring formatting (59cef7f)
- Syntax warnings and potential runtime errors (a61bd68)

### Removed
- Obsolete documentation and duplicate config files (6513188)

---

## [1.3.0] - 2025-09-02

### Added
- **Intersection Solver HDA**: New Houdini Digital Asset (6cc5291)

---

## [1.2.0] - 2025-08-05

### Added
- **USD Stage Builder Module**: High-level composition of Bifrost graphs + Maya USD proxy (305d8bb)
- **USD Export Settings Plugin**: Plugin for configuring USD export (52d7075)
- **Line of Action Tools**: Common utils and line of action tool (c7181ce)
  - Function to create all lines of action (41d9f0b)
- **Space Unit Utilities**: Space unit conversion utilities (2eacd38)
- **Pre-Export Hook**: Pre-export hook functionality (32e5ae6)
- **Character Set Parenting**: New character set parenting functionality (7453df2)

### Changed
- USD export now handles meter units correctly (980ebc6)
- Configure USD export unit based on Maya settings (c6f01e0)
- Refactors parameter retrieval in FunctionUI (14f376e)
- Simplifies scene unit query (30aab73)
- Improves compatibility with different Qt versions (8d21344)
- Corrects function name for Maya 2025 compatibility (139de16)
- Refactors setDrivenKey to set_driven_key (6e152e9)
- Deletes combined skeleton after LOA creation (769fe02)
- Restructures project for modularity (613475e)

### Fixed
- Various USD-related fixes and improvements

---

## [1.1.0] - 2025-07-24

### Added
- **Quad Patcher Tool**: New modeling utility (9fda9c6)
- **Base Rigging Class**: Core functionalities with selection set management (c30759f)
- **Cleanup Utility**: Tool to cleanup unknown Maya nodes (c25bd30)

### Changed
- Enhances base rig functionality and robustness (2b0304e)
- Improves skin weight transfer functionality (e2d277a)

---

## [1.0.0] - 2025-02-24

### Added
- **Deform Library Refactoring**: Added invert shape functionality (515bdc4)
- **Matrix Collision**: New collision system (8d8d064)
- **Auto Update Pipeline**: Automatic library update mechanism (beb9608)
- **UsdLib and BifrostLib**: New library modules (1a77bc1)

### Changed
- **Documentation Improvements**:
  - Docstring for startup (668b487)
  - Docstring for RenameCtrl (f800562)
  - Docstring for ZivaLib (9d2640e)
  - ShaderLib docstring and refactor (b19f6a5)
  - Pipeline Lib docstring and refactor (0d41e28)
  - GUI comments and refactor (c33894f)
  - Comments on BaseUI and HumanIK (900d386)
- Startup control for requirements (668b487)
- Model lib refactor (db97d6c)
- Fluid lib and LookdevLib refactoring (d822f3b)
- Skin.py refactor and comments (7d64b59)

### Fixed
- Various fixes and cleanup (cc47872)

---

## [0.9.0] - 2024-11-13

### Added
- **Muscle Tools**: New muscle-related utilities (f3cf54b)
- **PyFrost Submodule**: Added pyfrost as git submodule (4433ca8)

### Changed
- Skincluster Mirror improvements (5a99800)
- HumanIK updates with finger support (d65fdb2, c764dd1)
- HumanIK with Dict (0f375a4)
- Compatible with Maya 2024 (562390d)

### Fixed
- Load and Save Skincluster (84b1643)
- UE Skeleton naming (5934926)
- Limit joint transform (93f8f73)
- HumanIK check if ctrl exists (53943b3)
- Mirror skin fix (c8df060)

---

## [0.8.0] - 2024-07-24

### Added
- **USD Modeling Tools**: Modelling USD workflow (dd9196a)
- **Requirements.txt**: Added requirements file (a4034c7)
- **Workspace Utility**: New workspace management (0e729ca)

### Changed
- GUI update (db8e323)
- Bindpose Update (9632d1f)
- Human IK update (ce91ed8)
- Documentation improvements (3689551)

### Fixed
- UVs fix (6952130)
- HumanIK fixes (b1db1d3, 3ae39ef)
- Startup and compatibility (3794554)

---

## [0.7.0] - 2024-06-07

### Added
- **USD Improvements**:
  - USD set Specifier Over (df997fa)
  - Full path USD (002fa75)
  - Value clip support (1b5eae3)

### Changed
- USD long name update (c29e8fe)
- Transform attribute update (b1a36b9)
- USD comments and documentation (cbc7f40)

### Fixed
- Duplicate connections (28a3b2f)
- Removed print statements (87a6511)

---

## [0.6.0] - 2024-05-22

### Added
- **Bifrost API**: New Bifrost Python API (73055d7)
- **Ziva Auto GPU**: Automatic GPU acceleration for Ziva (9e9f92c)

### Changed
- Bifrost refactor (37e8a09)
- USD updates and improvements (1098719, 1f788ba)

---

## [0.5.0] - 2024-04-05

### Added
- **Rename Shape Deformed**: New deformer renaming utility (d50f7b1)

### Changed
- Cloth connection update (f653eec)
- Updates for Maya 2024 (36c913f)

---

## [0.4.0] - 2024-02-07

### Added
- **Face Test**: Initial facial rigging tests (32e1c73)

### Changed
- Skincluster save update (72cbcb0)

### Fixed
- Various bug fixes (589538b, 08ab5e2, de484ac)

---

## [0.3.0] - 2023-12-31

### Added
- **Temp Deformer and Cloth**: New deformer and cloth tools (5a7f82a)
- **NgSkinTool Integration**: Batch save/load functionality (d1ea63b)
- **JSON Tools**: Create shaders from JSON (d1ea63b)
- **UDIM File Node**: UDIM texture support (53224de)
- **Shader Converter**: Shader conversion utilities (70ff27b, 4390d09)
- **Colorspace Support**: Added colorspace handling (c66d196)

### Changed
- Human IK and Shaders updates (6775432)
- Texture Tool update (b10e940, db16bc2)
- Refactor object along curve (4a5ac34)
- Shader builder updates (9c96ce0)
- SlidingCloth update (fde0c9c)
- Shader converter names (e8c8cad)

### Fixed
- Flexyplane fix (d10b84d)
- Alpha from diffuse (4697de3)
- Various shader and deformer fixes

---

## [0.2.0] - 2023-09-02

### Added
- **Shader System**: Initial shader building and conversion system
- **Texture Tools**: Texture manipulation utilities

### Changed
- Multiple shader and texture updates

---

## [0.1.0] - 2023-06-26

### Added
- **Initial Release**: Core library structure
- **Cloth System**: Basic cloth simulation utilities
- **Startup System**: Maya startup integration

### Changed
- Refactoring of startup process (025681f, 288e1ea)

---

## Version History Summary

| Version | Date | Highlights |
|---------|------|------------|
| 2.0.0 | 2026-01-22 | Luna integration, wiki documentation, code quality refactoring |
| 1.5.0 | 2025-12-19 | Eye aim setup, cross-platform compatibility |
| 1.4.0 | 2025-11-07 | Major code quality refactoring (93.9% improvement) |
| 1.3.0 | 2025-09-02 | Intersection Solver HDA |
| 1.2.0 | 2025-08-05 | USD stage builder, line of action tools |
| 1.1.0 | 2025-07-24 | Quad patcher, base rigging class |
| 1.0.0 | 2025-02-24 | Documentation improvements, auto-update pipeline |
| 0.9.0 | 2024-11-13 | Muscle tools, PyFrost submodule, Maya 2024 compatibility |
| 0.8.0 | 2024-07-24 | USD modeling tools, HumanIK improvements |
| 0.7.0 | 2024-06-07 | USD improvements, value clip support |
| 0.6.0 | 2024-05-22 | Bifrost API, Ziva auto GPU |
| 0.5.0 | 2024-04-05 | Maya 2024 updates |
| 0.4.0 | 2024-02-07 | Facial rigging tests |
| 0.3.0 | 2023-12-31 | Shader converter, NgSkinTool integration |
| 0.2.0 | 2023-09-02 | Shader system, texture tools |
| 0.1.0 | 2023-06-26 | Initial release |

---

*Last updated: February 2026*

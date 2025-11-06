# DevPyLib - Test Structure Guide

**Document**: Test Directory Organization
**Created**: 2025-11-06
**Status**: PROPOSAL - Needs Approval

---

## Le Tre Opzioni Spiegate

### Opzione 1: Tests Alongside Code (Django Style)

**Struttura:**
```
DevPyLib/
├── mayaLib/
│   ├── rigLib/
│   │   ├── base/
│   │   │   ├── __init__.py
│   │   │   ├── module.py              ← Codice di produzione
│   │   │   ├── test_module.py         ← Test accanto al codice
│   │   │   ├── limb.py
│   │   │   ├── test_limb.py
│   │   │   ├── spine.py
│   │   │   └── test_spine.py
│   │   └── utils/
│   │       ├── control.py
│   │       ├── test_control.py
│   │       ├── joint.py
│   │       └── test_joint.py
│   └── fluidLib/
│       ├── base/
│       │   ├── base_fluid.py
│       │   └── test_base_fluid.py
│       ├── explosion.py
│       └── test_explosion.py
```

**Pro:**
- ✅ Test molto facili da trovare (stessa directory del codice)
- ✅ Quando modifichi `module.py`, il test è subito visibile
- ✅ Meno path da scrivere negli import
- ✅ Usato da Django, Rails, Go standard library

**Contro:**
- ❌ Pollutes il package: i file `test_*.py` vengono distribuiti con il codice
- ❌ Aumenta la dimensione del package installato
- ❌ I test appaiono nei tool di navigazione del codice
- ❌ Può confondere gli utenti che guardano la libreria

**Esempio pratico:**
```python
# In mayaLib/rigLib/base/test_module.py
from mayaLib.rigLib.base.module import Base  # Import facile!

def test_base_init():
    base = Base(character_name="test")
    assert base.top_group is not None
```

---

### Opzione 2: Separate tests/ Directory (PyTest Standard) ⭐ **RACCOMANDATO**

**Struttura:**
```
DevPyLib/
├── mayaLib/                        ← Package di produzione (pulito!)
│   ├── rigLib/
│   │   ├── base/
│   │   │   ├── __init__.py
│   │   │   ├── module.py
│   │   │   ├── limb.py
│   │   │   └── spine.py
│   │   └── utils/
│   │       ├── control.py
│   │       └── joint.py
│   └── fluidLib/
│       └── base/
│           └── base_fluid.py
│
└── tests/                          ← Directory separata per test
    ├── conftest.py                 ← Fixture globali
    ├── __init__.py
    │
    ├── unit/                       ← Test unitari (veloci, isolati)
    │   ├── __init__.py
    │   ├── rigLib/                 ← Rispecchia struttura mayaLib/
    │   │   ├── __init__.py
    │   │   ├── base/
    │   │   │   ├── __init__.py
    │   │   │   ├── test_module.py
    │   │   │   ├── test_limb.py
    │   │   │   └── test_spine.py
    │   │   └── utils/
    │   │       ├── test_control.py
    │   │       └── test_joint.py
    │   └── fluidLib/
    │       └── base/
    │           └── test_base_fluid.py
    │
    ├── integration/                ← Test di integrazione (più lenti)
    │   ├── __init__.py
    │   ├── test_complete_rig_workflow.py
    │   ├── test_fluid_simulation_workflow.py
    │   └── test_ziva_workflow.py
    │
    ├── functional/                 ← Test end-to-end (molto lenti)
    │   ├── __init__.py
    │   └── test_full_character_rig.py
    │
    ├── fixtures/                   ← Dati di test
    │   ├── scenes/
    │   │   ├── test_scene_01.ma
    │   │   └── test_scene_02.mb
    │   ├── meshes/
    │   │   ├── cube.obj
    │   │   └── sphere.obj
    │   └── rigs/
    │       └── simple_rig.ma
    │
    └── mocks/                      ← Mock objects
        ├── __init__.py
        └── maya_mocks.py
```

**Pro:**
- ✅ Package di produzione pulito (mayaLib/ non contiene test)
- ✅ Separazione chiara: codice vs test
- ✅ Organizzazione per tipo di test (unit/integration/functional)
- ✅ Più facile gestire fixture e dati di test
- ✅ Standard PyTest e pytest-cov
- ✅ Test non vengono installati con `pip install`

**Contro:**
- ⚠️ Import paths più lunghi
- ⚠️ Devi "mirrare" la struttura di mayaLib/ in tests/unit/
- ⚠️ Un po' più di navigazione per trovare il test

**Esempio pratico:**
```python
# In tests/unit/rigLib/base/test_module.py
from mayaLib.rigLib.base.module import Base  # Import dal package

def test_base_init():
    base = Base(character_name="test")
    assert base.top_group is not None
```

**Come funziona il mirroring:**
```
mayaLib/rigLib/base/module.py  →  tests/unit/rigLib/base/test_module.py
mayaLib/rigLib/base/limb.py    →  tests/unit/rigLib/base/test_limb.py
mayaLib/fluidLib/explosion.py  →  tests/unit/fluidLib/test_explosion.py
```

---

### Opzione 3: Hybrid Approach (Compromesso)

**Struttura:**
```
DevPyLib/
├── mayaLib/
│   ├── rigLib/
│   │   ├── base/
│   │   │   ├── module.py
│   │   │   ├── test_module.py      ← Unit test accanto al codice
│   │   │   ├── limb.py
│   │   │   └── test_limb.py
│   │   └── utils/
│   │       ├── control.py
│   │       └── test_control.py
│   └── fluidLib/
│       └── base/
│           ├── base_fluid.py
│           └── test_base_fluid.py
│
└── tests/                           ← Solo integration/functional
    ├── conftest.py
    ├── integration/
    │   ├── test_complete_rig_workflow.py
    │   └── test_fluid_simulation_workflow.py
    └── functional/
        └── test_full_character_rig.py
```

**Pro:**
- ✅ Unit test facili da trovare (vicino al codice)
- ✅ Test complessi separati (integration/functional)
- ✅ Bilanciamento tra le due filosofie

**Contro:**
- ⚠️ Due posti dove cercare test
- ⚠️ Unit test distribuiti con il package
- ⚠️ Confusione: "dove metto questo test?"
- ⚠️ Non standard per Python

---

## Raccomandazione per DevPyLib: **Opzione 2** ⭐

### Perché Opzione 2?

1. **Standard della community Python**
   - PyTest, NumPy, Django (quando non embedded), Flask
   - Tutti usano `tests/` separata per librerie distribuite

2. **DevPyLib è una libreria da distribuire**
   - Gli utenti installano via pip/git
   - Non devono ricevere i test (package più leggero)

3. **Separazione per tipo di test**
   ```
   tests/unit/        → Veloci (< 1s), no Maya scene, mockable
   tests/integration/ → Medi (1-10s), Maya scene, workflow completi
   tests/functional/  → Lenti (> 10s), end-to-end, scenari reali
   ```

4. **Facilita CI/CD**
   ```bash
   # Run solo unit test (veloci) su ogni commit
   mayapy -m pytest tests/unit/

   # Run integration solo su PR
   mayapy -m pytest tests/integration/

   # Run functional solo nightly
   mayapy -m pytest tests/functional/
   ```

5. **Gestione fixture e dati centralizzata**
   ```
   tests/fixtures/scenes/    → Scene Maya condivise
   tests/fixtures/meshes/    → Geometrie di test
   tests/conftest.py         → Fixture globali accessibili da tutti
   ```

---

## Struttura Completa Proposta per DevPyLib

```
DevPyLib/
│
├── mayaLib/                          # CODICE PRODUZIONE (pulito!)
│   ├── __init__.py
│   ├── rigLib/
│   │   ├── __init__.py
│   │   ├── base/
│   │   │   ├── __init__.py
│   │   │   ├── module.py             # Base class per rig
│   │   │   ├── limb.py               # Limb rig
│   │   │   ├── spine.py              # Spine rig
│   │   │   ├── face.py               # Face rig
│   │   │   ├── neck.py
│   │   │   └── ik_chain.py
│   │   ├── utils/
│   │   │   ├── control.py            # Control creation
│   │   │   ├── joint.py              # Joint utilities
│   │   │   ├── transform.py
│   │   │   └── deform.py
│   │   └── core/
│   │       └── rig.py                # Main rig class
│   │
│   ├── fluidLib/
│   │   ├── __init__.py
│   │   ├── base/
│   │   │   ├── base_fluid.py         # Base fluid class
│   │   │   ├── base_container.py
│   │   │   └── base_emitter.py
│   │   ├── explosion.py
│   │   ├── smoke.py
│   │   ├── fire.py
│   │   └── fire_smoke.py
│   │
│   ├── guiLib/
│   │   ├── base/
│   │   │   └── base_ui.py
│   │   └── main_menu.py
│   │
│   ├── pipelineLib/
│   │   └── utility/
│   │       ├── convention.py
│   │       ├── json_tool.py
│   │       └── lib_manager.py
│   │
│   └── utility/
│       ├── __init__.py
│       └── b_skin_saver.py
│
└── tests/                            # TUTTO I TEST (separato!)
    ├── __init__.py
    ├── conftest.py                   # Fixture globali per tutti i test
    ├── pytest.ini                    # Configurazione pytest (opzionale)
    │
    ├── unit/                         # TEST UNITARI (veloci, isolati)
    │   ├── __init__.py
    │   ├── conftest.py               # Fixture specifiche per unit test
    │   │
    │   ├── rigLib/                   # Mirror di mayaLib/rigLib/
    │   │   ├── __init__.py
    │   │   │
    │   │   ├── base/
    │   │   │   ├── __init__.py
    │   │   │   ├── test_module.py         # Tests per module.py
    │   │   │   ├── test_limb.py           # Tests per limb.py
    │   │   │   ├── test_spine.py
    │   │   │   ├── test_face.py
    │   │   │   ├── test_neck.py
    │   │   │   └── test_ik_chain.py
    │   │   │
    │   │   ├── utils/
    │   │   │   ├── __init__.py
    │   │   │   ├── test_control.py        # Tests per control.py
    │   │   │   ├── test_joint.py
    │   │   │   ├── test_transform.py
    │   │   │   └── test_deform.py
    │   │   │
    │   │   └── core/
    │   │       ├── __init__.py
    │   │       └── test_rig.py
    │   │
    │   ├── fluidLib/
    │   │   ├── __init__.py
    │   │   ├── base/
    │   │   │   ├── __init__.py
    │   │   │   ├── test_base_fluid.py
    │   │   │   ├── test_base_container.py
    │   │   │   └── test_base_emitter.py
    │   │   ├── test_explosion.py
    │   │   ├── test_smoke.py
    │   │   ├── test_fire.py
    │   │   └── test_fire_smoke.py
    │   │
    │   ├── guiLib/
    │   │   ├── __init__.py
    │   │   ├── base/
    │   │   │   ├── __init__.py
    │   │   │   └── test_base_ui.py
    │   │   └── test_main_menu.py
    │   │
    │   ├── pipelineLib/
    │   │   ├── __init__.py
    │   │   └── utility/
    │   │       ├── __init__.py
    │   │       ├── test_convention.py
    │   │       ├── test_json_tool.py
    │   │       └── test_lib_manager.py
    │   │
    │   └── utility/
    │       ├── __init__.py
    │       └── test_b_skin_saver.py
    │
    ├── integration/                  # TEST INTEGRAZIONE (workflow completi)
    │   ├── __init__.py
    │   ├── conftest.py               # Fixture specifiche per integration
    │   ├── test_complete_rig_workflow.py
    │   ├── test_limb_creation_workflow.py
    │   ├── test_fluid_simulation_workflow.py
    │   ├── test_ziva_muscle_workflow.py
    │   └── test_gui_interaction.py
    │
    ├── functional/                   # TEST END-TO-END (scenari completi)
    │   ├── __init__.py
    │   ├── conftest.py
    │   ├── test_full_character_rig.py
    │   └── test_complete_pipeline.py
    │
    ├── fixtures/                     # DATI DI TEST
    │   ├── scenes/
    │   │   ├── empty_scene.ma
    │   │   ├── test_character.ma
    │   │   └── test_rig_base.mb
    │   ├── meshes/
    │   │   ├── cube.obj
    │   │   ├── sphere.fbx
    │   │   └── character_mesh.ma
    │   ├── rigs/
    │   │   ├── simple_limb_rig.ma
    │   │   └── complete_character.ma
    │   └── data/
    │       ├── test_weights.json
    │       └── expected_outputs.json
    │
    ├── mocks/                        # MOCK OBJECTS
    │   ├── __init__.py
    │   ├── maya_mocks.py             # Mock per Maya API
    │   └── qt_mocks.py               # Mock per Qt widgets
    │
    └── templates/                    # TEMPLATE PER NUOVI TEST
        ├── test_unit_template.py
        ├── test_integration_template.py
        └── test_functional_template.py
```

---

## Come Navigare i Test

### Trovare il test per un modulo

**Regola semplice:** Mirror path, aggiungi `test_` al filename

```
mayaLib/rigLib/base/module.py
   ↓
tests/unit/rigLib/base/test_module.py
```

**Esempi:**
```
mayaLib/rigLib/utils/control.py      → tests/unit/rigLib/utils/test_control.py
mayaLib/fluidLib/explosion.py        → tests/unit/fluidLib/test_explosion.py
mayaLib/guiLib/main_menu.py          → tests/unit/guiLib/test_main_menu.py
mayaLib/pipelineLib/utility/json.py  → tests/unit/pipelineLib/utility/test_json.py
```

### Da Neovim - Keybindings Proposti

```lua
-- Jump tra file e test
vim.keymap.set("n", "<leader>ta", function()
  -- Alterna tra file.py e test_file.py
  local current = vim.fn.expand("%:p")

  if current:match("test_") then
    -- Siamo in un test → vai al file di produzione
    local prod_file = current:gsub("tests/unit/", "mayaLib/"):gsub("test_", "")
    vim.cmd("edit " .. prod_file)
  else
    -- Siamo nel file di produzione → vai al test
    local test_file = current:gsub("mayaLib/", "tests/unit/")
    local dir = test_file:match("(.*/)")
    local file = test_file:match(".*/(.*)%.py$")
    vim.cmd("edit " .. dir .. "test_" .. file .. ".py")
  end
end, { desc = "Toggle between file and test" })
```

**Uso:**
- Sei in `mayaLib/rigLib/base/module.py`
- Premi `<leader>ta`
- Apre `tests/unit/rigLib/base/test_module.py`

---

## Esecuzione Test per Categoria

### Solo Unit Test (veloci)
```bash
# Tutti gli unit test
mayapy -m pytest tests/unit/ -v

# Solo unit test di rigLib
mayapy -m pytest tests/unit/rigLib/ -v

# Solo un modulo specifico
mayapy -m pytest tests/unit/rigLib/base/test_module.py -v

# Solo una funzione specifica
mayapy -m pytest tests/unit/rigLib/base/test_module.py::test_init_creates_hierarchy -v
```

### Solo Integration Test (medi)
```bash
mayapy -m pytest tests/integration/ -v
```

### Solo Functional Test (lenti)
```bash
mayapy -m pytest tests/functional/ -v
```

### Tutti i test
```bash
mayapy -m pytest tests/ -v
```

### Con coverage
```bash
mayapy -m pytest tests/unit/ --cov=mayaLib --cov-report=html
```

---

## Esempio Concreto: Test per module.py

### File di Produzione
```python
# mayaLib/rigLib/base/module.py
class Base:
    """Base class for all rig modules."""

    def __init__(self, character_name, scale=1.0):
        self.character_name = character_name
        self.scale = scale
        self.top_group = None
        self.rig_group = None

    def create_hierarchy(self):
        """Create basic rig hierarchy."""
        import pymel.core as pm

        self.top_group = pm.group(n=f"{self.character_name}_rig_GRP", em=True)
        self.rig_group = pm.group(n="rig_GRP", em=True, p=self.top_group)

        return self.top_group
```

### Unit Test
```python
# tests/unit/rigLib/base/test_module.py
"""Unit tests for mayaLib.rigLib.base.module.

Tests the Base class functionality.
"""
import pytest
import pymel.core as pm

from mayaLib.rigLib.base.module import Base


class TestBase:
    """Test suite for Base class."""

    def test_init_sets_attributes(self):
        """Test __init__ sets instance attributes correctly."""
        # Arrange
        char_name = "hero"
        scale = 2.0

        # Act
        base = Base(character_name=char_name, scale=scale)

        # Assert
        assert base.character_name == char_name
        assert base.scale == scale
        assert base.top_group is None  # Not created yet

    def test_create_hierarchy_creates_groups(self, maya_scene):
        """Test create_hierarchy creates expected group structure."""
        # Arrange
        base = Base(character_name="test")

        # Act
        result = base.create_hierarchy()

        # Assert
        assert result is not None
        assert base.top_group is not None
        assert base.rig_group is not None
        assert pm.objExists("test_rig_GRP")
        assert pm.objExists("rig_GRP")

    def test_create_hierarchy_parents_correctly(self, maya_scene):
        """Test rig_group is parented under top_group."""
        # Arrange
        base = Base(character_name="test")

        # Act
        base.create_hierarchy()

        # Assert
        parent = base.rig_group.getParent()
        assert parent == base.top_group

    def test_init_with_empty_name_raises_error(self):
        """Test empty character_name raises ValueError."""
        # Act & Assert
        with pytest.raises(ValueError, match="Character name cannot be empty"):
            Base(character_name="")
```

### Integration Test
```python
# tests/integration/test_complete_rig_workflow.py
"""Integration tests for complete rig creation workflow."""
import pytest
import pymel.core as pm

from mayaLib.rigLib.base.module import Base
from mayaLib.rigLib.base.limb import Limb


class TestCompleteRigWorkflow:
    """Integration tests for building a complete rig."""

    def test_create_full_arm_rig(self, maya_scene, test_arm_joints):
        """Test creating complete arm rig with controls and constraints."""
        # Arrange
        base = Base(character_name="hero")
        base.create_hierarchy()

        # Act - Create limb rig
        arm = Limb(
            base_rig=base,
            side="L",
            limb_type="arm",
            joint_list=test_arm_joints
        )
        arm.create_controls()
        arm.create_ik_setup()
        arm.create_fk_setup()

        # Assert - Verify complete hierarchy
        assert pm.objExists("hero_rig_GRP")
        assert pm.objExists("L_arm_rig_GRP")
        assert pm.objExists("L_arm_IK_CTRL")
        assert pm.objExists("L_arm_FK_CTRL_01")

        # Verify functionality
        ik_ctrl = pm.PyNode("L_arm_IK_CTRL")
        ik_ctrl.translateX.set(10)
        pm.dgeval()  # Force evaluation

        # Check IK chain moved
        end_joint = pm.PyNode(test_arm_joints[-1])
        assert end_joint.translateX.get() != 0  # Joint moved with control
```

---

## File di Configurazione

### tests/conftest.py
```python
"""Global pytest configuration and fixtures."""
import pytest
import pymel.core as pm


@pytest.fixture(autouse=True)
def maya_scene():
    """Clean Maya scene before and after each test.

    This fixture runs automatically for all tests.
    """
    pm.newFile(force=True)
    yield
    pm.newFile(force=True)


@pytest.fixture
def test_joint_chain():
    """Create a simple 3-joint chain for testing."""
    root = pm.joint(name="root_jnt", position=(0, 0, 0))
    mid = pm.joint(name="mid_jnt", position=(5, 0, 0))
    end = pm.joint(name="end_jnt", position=(10, 0, 0))
    pm.select(clear=True)

    return [root, mid, end]


@pytest.fixture
def test_arm_joints():
    """Create arm joint chain."""
    shoulder = pm.joint(name="L_shoulder_jnt", position=(0, 10, 0))
    elbow = pm.joint(name="L_elbow_jnt", position=(5, 10, 0))
    wrist = pm.joint(name="L_wrist_jnt", position=(10, 10, 0))
    pm.select(clear=True)

    return [shoulder, elbow, wrist]
```

### pyproject.toml
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]

# Markers for test organization
markers = [
    "unit: Unit tests (fast, isolated)",
    "integration: Integration tests (medium, requires Maya scene)",
    "functional: Functional tests (slow, end-to-end)",
    "slow: Tests that take > 5 seconds",
]

# Ignore directories
norecursedirs = [
    ".*",
    "build",
    "dist",
    "*.egg",
    "mayaLib",
]
```

---

## Vantaggi Pratici di Questa Struttura

### 1. Velocità di Esecuzione Differenziata
```bash
# Durante sviluppo - solo unit test (< 5 minuti)
mayapy -m pytest tests/unit/ -v

# Prima di commit - unit + integration (< 15 minuti)
mayapy -m pytest tests/unit/ tests/integration/ -v

# CI/CD nightly - tutti i test (< 30 minuti)
mayapy -m pytest tests/ -v
```

### 2. Coverage Precisa per Categoria
```bash
# Coverage solo del codice di produzione
mayapy -m pytest tests/unit/ --cov=mayaLib --cov-report=term

# Coverage per modulo specifico
mayapy -m pytest tests/unit/rigLib/ --cov=mayaLib.rigLib --cov-report=html
```

### 3. Package di Produzione Pulito
```bash
# Install DevPyLib - NO test files included!
pip install git+https://github.com/Aiacos/DevPyLib.git

# Struttura installata:
site-packages/
└── mayaLib/         ← Solo questo viene installato!
    ├── rigLib/
    ├── fluidLib/
    └── ...
    # NO tests/ directory!
```

### 4. Debugging Facilitato
```bash
# Run un solo test con output dettagliato
mayapy -m pytest tests/unit/rigLib/base/test_module.py::TestBase::test_init_sets_attributes -vv -s

# Run con pdb debugger
mayapy -m pytest tests/unit/rigLib/base/test_module.py --pdb
```

---

## FAQ

### Q: Devo duplicare tutta la struttura di mayaLib/ in tests/unit/?
**A:** No! Solo per i file che hanno test. Se `mayaLib/rigLib/utils/helper.py` non ha test, non serve `tests/unit/rigLib/utils/test_helper.py`.

### Q: Posso mescolare unit e integration test nella stessa directory?
**A:** Tecnicamente sì, ma è sconsigliato. Usa i marker pytest:
```python
@pytest.mark.integration
def test_complete_workflow():
    # Test di integrazione
    pass
```

### Q: Come organizzo test che dipendono da file esterni?
**A:** Usa `tests/fixtures/` e fixture pytest:
```python
@pytest.fixture
def test_scene(tmp_path):
    """Load test scene."""
    scene_path = Path(__file__).parent.parent / "fixtures/scenes/test_rig.ma"
    pm.openFile(str(scene_path), force=True)
    yield
    pm.newFile(force=True)
```

### Q: Neotest funziona con questa struttura?
**A:** Sì! Neotest usa pytest discovery standard. Configurazione:
```lua
require("neotest").setup({
  adapters = {
    require("neotest-python")({
      python = "/path/to/mayapy",
      runner = "pytest",
      args = {"tests/unit/"}  -- Default a unit test
    })
  }
})
```

---

## Prossimi Passi

1. ✅ Approvare questa struttura
2. ✅ Creare directory `tests/` con subdirectory
3. ✅ Creare `conftest.py` con fixture base
4. ✅ Scrivere primo test: `tests/unit/rigLib/base/test_module.py`
5. ✅ Verificare che neotest funzioni
6. ✅ Procedere con test P0

---

**Struttura Raccomandata**: ✅ **Opzione 2 - Separate tests/ Directory**

**Motivo**: Standard Python, package pulito, scalabile, organizzazione per tipo di test

**Prossima Decisione Richiesta**: Approvazione da @Aiacos

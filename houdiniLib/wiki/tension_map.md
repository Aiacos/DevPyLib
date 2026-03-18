# Tension Map HDA — Houdini

Per-vertex tension visualization comparing rest-pose and deformed mesh edge lengths.

## Outputs

| Attribute | Type | Range | Description |
|-----------|------|-------|-------------|
| `@tension` | float | 0-1 | Raw tension (0 = stretch, 0.5 = neutral, 1 = compress) |
| `@stretch` | float | 0-1 | Isolated stretch (1 = maximum stretch) |
| `@compression` | float | 0-1 | Isolated compression (1 = maximum compression) |
| `@Cd` | vector3 | RGB | Color: green = stretch, black = neutral, red = compress |

## Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| Method | Wrangle (VEX) | Switch between Wrangle and VOP implementation (`both` mode only) |
| Sensitivity | 1.0 | Multiplier for the tension response curve |
| Offset | 0.5 | Neutral point — values below = stretch, above = compress |
| Epsilon | 0.0001 | Division safety threshold to avoid zero-division |

## Modes

The builder supports three modes via the `mode` parameter:

| Mode | Default | Description | Nodes created |
|------|---------|-------------|---------------|
| `"both"` | **Yes** | Wrangle + VOP with a Switch SOP to toggle | Rest + Wrangle + VOP + Switch |
| `"wrangle"` | | Single Attribute Wrangle with VEX code | Rest + Wrangle |
| `"vop"` | | Attribute VOP with visual node network | Rest + VOP |

### `both` mode (default)

Creates both implementations in parallel with a **Switch SOP** (`method_switch`)
that lets you toggle between them at any time via a **Method** dropdown menu:

```
capture_rest
├── tension_wrangle  (blue — input 0 of switch)
├── tension_vop      (orange — input 1 of switch)
└── method_switch    ← "Method" menu: Wrangle (VEX) / VOP (Nodes)
```

When used with `as_subnet=True`, the **Method** dropdown is exposed on the
subnet interface alongside Sensitivity, Offset, and Epsilon.

### `wrangle` mode

Creates only the Attribute Wrangle. The entire algorithm is in a single VEX
snippet — compact and easy to modify directly in the parameter editor.

### `vop` mode

Creates only the Attribute VOP with a visual node network (~24 VOP nodes).
Better for learning, debugging, and non-programmers.

## Quick Start

### Option A: Python Script (creates nodes programmatically)

```python
# In Houdini Python Shell:
from houdiniLib.utility.build_tension_map import TensionMapNetwork

# Default: both modes with Switch (toggle in parameter editor)
net = TensionMapNetwork("/obj/geo1")

# Wrangle only
net = TensionMapNetwork("/obj/geo1", mode="wrangle")

# VOP only
net = TensionMapNetwork("/obj/geo1", mode="vop")

# As HDA-ready subnet (exposes Method, Sensitivity, Offset, Epsilon)
net = TensionMapNetwork("/obj/geo1", as_subnet=True)
```

Then in the Attribute Editor: connect your deforming geometry **before** the
`capture_rest` node (so `@rest` is captured at bind pose).

### Option B: Create HDA from Subnet

1. Run the script with `as_subnet=True` (uses `both` mode by default)
2. Right-click the `tension_map` subnet -> **Create Digital Asset...**
3. Set name: `sop_unilo.Tension_Map.1.0`
4. Save to: `houdiniLib/HDAs/`
5. The HDA will appear in the TAB menu with Method / Sensitivity / Offset / Epsilon

### Option C: Manual Node Setup (no Python)

Complete step-by-step guide to build the entire network by hand.

---

#### Step 1 — SOP Level (inside `/obj/geo1`)

1. **TAB** > `Rest Position` — drop a **Rest Position SOP**
   - Wire it after your geometry (e.g. after a Bone Deform or Skin SOP)
   - This captures `@rest` at the current frame
   - **Important**: set the timeline to the rest/bind pose frame before cooking
2. **TAB** > `Attribute VOP` — drop an **Attribute VOP SOP**
   - Wire its input to the Rest Position SOP output
   - In the parameter editor, set **Run Over** → `Points`
3. Double-click the Attribute VOP to **dive inside**

---

#### Step 2 — Inside the Attribute VOP (VOP level)

Delete the default `geometryvopglobal` and `geometryvopoutput` nodes —
we'll build from scratch.

##### 2a. Import attributes (3x Bind VOP)

For each attribute we need to read, create a **Bind** node:

| # | TAB > `Bind` | Name field | Type field | Export |
|---|-------------|------------|------------|--------|
| 1 | `import_P` | `P` | Vector (float3) | **Off** |
| 2 | `import_rest` | `rest` | Vector (float3) | **Off** |
| 3 | `import_ptnum` | `ptnum` | Integer | **Off** |

> **Why Bind instead of Global VOP?**  The `geometryvopglobal` node's output
> indices for `ptnum` shift between Houdini versions (can be 4, 11, or other).
> Bind VOPs look up attributes by name — always reliable.

##### 2b. User parameters (3x Parameter VOP)

| # | TAB > `Parameter` | Name | Label | Type | Default |
|---|-------------------|------|-------|------|---------|
| 1 | `parm_sensitivity` | `sensitivity` | Sensitivity | Float | `1.0` |
| 2 | `parm_offset` | `offset` | Offset | Float | `0.5` |
| 3 | `parm_epsilon` | `epsilon` | Epsilon | Float | `0.0001` |

These will appear as sliders in the Attribute VOP's parameter editor.

##### 2c. Neighbor edge accumulation (1x Inline Code VOP)

This is the **only node with VEX code**. TAB > `Inline Code`.

**Configure Inputs** (parameter editor > Inputs multiparm — click `+` for each):

| # | Name | Type |
|---|------|------|
| 1 | `P` | vector |
| 2 | `rest` | vector |
| 3 | `ptnum` | int |

**Configure Outputs** (parameter editor > Outputs multiparm — click `+` for each):

| # | Name | Type |
|---|------|------|
| 1 | `rest_avg` | float |
| 2 | `def_avg` | float |

**Wire the input connectors**:
- Input 1 (`P`) ← drag from `import_P` output
- Input 2 (`rest`) ← drag from `import_rest` output
- Input 3 (`ptnum`) ← drag from `import_ptnum` output

**Paste this VEX Code** into the **Code** field:

```c
int ncount = neighbourcount(0, ptnum);
float rest_total = 0;
float def_total = 0;

for (int i = 0; i < ncount; i++) {
    int nb = neighbour(0, ptnum, i);
    vector nb_P = point(0, "P", nb);
    vector nb_rest = point(0, "rest", nb);
    def_total += distance(P, nb_P);
    rest_total += distance(rest, nb_rest);
}

float safe_count = max(float(ncount), 1.0);
$rest_avg = rest_total / safe_count;
$def_avg = def_total / safe_count;
```

> **Syntax notes**:
> - `P`, `rest`, `ptnum` (no prefix) = declared inputs, fed from the wire
> - `$rest_avg`, `$def_avg` (with `$`) = declared outputs, Inline Code VOP convention
> - `neighbourcount(0, ptnum)` = number of topological neighbors of point `ptnum`
> - `neighbour(0, ptnum, i)` = point index of the *i*-th neighbor
> - `point(0, "P", nb)` = read attribute `P` from the geometry at point `nb`

##### 2d. Tension formula (6x pure VOP math nodes)

Create each node in order and wire them into a chain:

**1. Max** — `safe_rest`
- Input 1 ← `edge_accumulation` > `rest_avg`
- Input 2 ← `parm_epsilon`
- *Purpose*: avoid division by zero

**2. Subtract** — `edge_diff`
- Input 1 ← `edge_accumulation` > `rest_avg`
- Input 2 ← `edge_accumulation` > `def_avg`
- *Purpose*: `rest_avg - def_avg` (positive = compression)

**3. Divide** — `edge_ratio`
- Input 1 ← `edge_diff`
- Input 2 ← `safe_rest`
- *Purpose*: normalized difference

**4. Multiply** — `scaled`
- Input 1 ← `edge_ratio`
- Input 2 ← `parm_sensitivity`
- *Purpose*: amplify the response

**5. Add** — `tension_raw`
- Input 1 ← `scaled`
- Input 2 ← `parm_offset`
- *Purpose*: shift so 0.5 = neutral

**6. Clamp** — `tension_clamp`
- Input ← `tension_raw`
- Set **Min** = `0`, **Max** = `1`
- *Purpose*: final `@tension` value

##### 2e. Stretch map (2 nodes)

**1. Fit** — `stretch_fit`
- Input ← `tension_clamp`
- **Source Min** = `0.0`, **Source Max** = `0.5`
- **Dest Min** = `1.0`, **Dest Max** = `0.0`
- *Purpose*: low tension (< 0.5) = high stretch

**2. Clamp** — `stretch_clamp`
- Input ← `stretch_fit`
- **Min** = `0`, **Max** = `1`

##### 2f. Compression map (2 nodes)

**1. Fit** — `compress_fit`
- Input ← `tension_clamp`
- **Source Min** = `0.5`, **Source Max** = `1.0`
- **Dest Min** = `0.0`, **Dest Max** = `1.0`
- *Purpose*: high tension (> 0.5) = compression

**2. Clamp** — `compress_clamp`
- Input ← `compress_fit`
- **Min** = `0`, **Max** = `1`

##### 2g. Color composition (2 nodes)

**1. Constant** — `zero_const`
- **Type** = Float, **Value** = `0.0`

**2. Float To Vector** — `color_compose`
- Input 1 (R) ← `compress_clamp` (red = compression)
- Input 2 (G) ← `stretch_clamp` (green = stretch)
- Input 3 (B) ← `zero_const` (blue = 0)

##### 2h. Export attributes (4x Bind VOP with Export ON)

| # | TAB > `Bind` | Name | Type | Export | Wire from |
|---|-------------|------|------|--------|-----------|
| 1 | `export_tension` | `tension` | Float | **On** | `tension_clamp` |
| 2 | `export_stretch` | `stretch` | Float | **On** | `stretch_clamp` |
| 3 | `export_compression` | `compression` | Float | **On** | `compress_clamp` |
| 4 | `export_Cd` | `Cd` | Vector | **On** | `color_compose` |

> **Key**: check the **Export Parameter** checkbox in each Bind node.
> This is what makes the Bind write the attribute back to the geometry.

##### 2i. Output node

1. TAB > `Geometry VOP Output`
2. Wire all 4 Bind Export nodes into its inputs (order doesn't matter)
3. Press **L** to auto-layout the network

---

#### Step 3 — Verify

1. Press **U** to go back up to SOP level
2. Set the **display flag** (blue) on the Attribute VOP node
3. Open **Geometry Spreadsheet** (top menu: Windows > Geometry Spreadsheet)
   - You should see columns: `tension`, `stretch`, `compression`, `Cd`
4. In the viewport, press **D** > **Markers** tab > enable **Point Colors**
   to see the color visualization

#### Step 4 — Promote to HDA (optional)

1. Select both nodes (Rest Position + Attribute VOP)
2. **Shift+C** (Collapse into Subnet)
3. Rename the subnet to `tension_map`
4. Right-click > **Type Properties** > **Parameters** tab
   - Drag `sensitivity`, `offset`, `epsilon` from the Attribute VOP
     into the subnet's parameter interface
5. Right-click > **Create Digital Asset...**
   - Operator Name: `tension_map`
   - Library: `houdiniLib/HDAs/sop_unilo.Tension_Map.1.0.hda`

---

#### Total Node Count (per mode)

| Mode | SOP nodes | VOP nodes | Total |
|------|-----------|-----------|-------|
| `wrangle` | 2 (Rest + Wrangle) | 0 | **2** |
| `vop` | 2 (Rest + VOP) | 24 | **26** |
| `both` | 4 (Rest + Wrangle + VOP + Switch) | 24 | **28** |

## Algorithm

Same as the Bifrost version (`mayaLib.bifrostLib.utilities.build_tension_map`):

```
For each vertex V:
    1. Find all topological neighbours of V
    2. rest_avg  = mean( distance(rest[V], rest[nb]) for each nb )
    3. def_avg   = mean( distance(P[V],    P[nb])    for each nb )
    4. tension   = clamp( (rest_avg - def_avg) / max(rest_avg, eps) * sensitivity + offset, 0, 1 )
    5. stretch   = fit(tension, [0.5, 0.0] -> [0.0, 1.0])
    6. compress  = fit(tension, [0.5, 1.0] -> [0.0, 1.0])
    7. Cd        = (compress, stretch, 0)
```

## Network Diagrams

### `both` mode (default) — SOP level

```
capture_rest ──┬── tension_wrangle (blue)  ──┬── method_switch ──► output
               └── tension_vop (orange)    ──┘       │
                                              "Method" dropdown:
                                              0 = Wrangle (VEX)
                                              1 = VOP (Nodes)
```

### Internal VOP Network (inside `tension_vop`)

The Attribute VOP contains the following node graph:

```
import_P (Bind) ──────────────┐
import_rest (Bind) ───────────┤
import_ptnum (Bind) ──────────┤
                               ▼
                    ┌─────────────────────┐
                    │  edge_accumulation   │  ← Inline Code VOP (only VEX node)
                    │  (neighbour loop)    │
                    └──┬──────────┬───────┘
                 rest_avg      def_avg
                    │            │
 parm_epsilon ──► [max] ◄───────┤
                    │            │
                    ▼            ▼
                 [subtract] ← rest_avg - def_avg
                    │
                 [divide] ← diff / safe_rest
                    │
 parm_sensitivity ► [multiply]
                    │
 parm_offset ────► [add]
                    │
                 [clamp 0..1] ← @tension
                    │
              ┌─────┴─────┐
              ▼           ▼
          [fit+clamp]  [fit+clamp]
          stretch      compression
              │           │
              ▼           ▼
           [floattovec] ← (R=compress, G=stretch, B=0)
              │
              ▼
           @Cd, @tension, @stretch, @compression  (Bind Exports)
```

### Why One Inline Code VOP?

Houdini's VOP system lacks a topological neighbor iterator node.
The `neighbourcount()` and `neighbour()` functions are VEX-only, so the
edge accumulation loop must use an Inline Code VOP.  All other math
(subtract, divide, clamp, fit, etc.) uses pure VOP nodes.

## Comparison with Bifrost Version

| Aspect | Bifrost (`build_tension_map.py`) | Houdini (`build_tension_map.py`) |
|--------|----------------------------------|----------------------------------|
| Lines of code | ~591 | ~370 |
| Nodes in graph | ~40+ (5 sub-compounds) | ~22 (flat VOP network) |
| Nodes with code | 0 (pure Bifrost) | 1 (Inline Code VOP) |
| Outputs | tension + color | tension + stretch + compression + Cd |
| Neighbour iteration | for_each loop + face_vertex mask | `neighbour()` VEX function |
| Parallelism | for_each (serial per vertex) | VEX (auto-parallel over all points) |

## Typical Use Cases

- **Wrinkle maps**: Drive displacement/normal map intensity from `@compression`
- **Shader control**: Use `@stretch` to blend between tight/loose skin shaders
- **Simulation feedback**: Visualize where a cloth/skin sim is stretching
- **Corrective blendshapes**: Trigger correctives based on `@tension` thresholds
- **Debug tool**: Quick visual check of deformation quality via `@Cd`

## Requirements

- Houdini 20.x or later (tested targeting 20.x / 21.x)
- Input geometry must have point positions (`@P`)
- `@rest` attribute is captured automatically by the Rest Position SOP
- For animated meshes, ensure `@rest` is captured at bind/rest pose frame

## File Locations

| File | Purpose |
|------|---------|
| `houdiniLib/utility/build_tension_map.py` | Python builder script |
| `houdiniLib/wiki/tension_map.md` | This documentation (manual + API guide) |
| `mayaLib/bifrostLib/utilities/build_tension_map.py` | Bifrost equivalent |

## Bug Fixes from Research Verification

The following issues were identified via SideFX documentation review and fixed
before release:

1. **ptnum output index**: `geometryvopglobal` output indices shift between
   Houdini versions (ptnum can be at index 4, 11, or elsewhere). Fixed by
   using Bind VOP imports for all attributes (`@P`, `@rest`, `@ptnum`).

2. **Attribute VOP run-over parameter**: Changed from `bindclass` (incorrect)
   to `bindrunover` with integer value `1` (points).

3. **Bind VOP parmtype**: Uses integer menu indices (`0=int`, `1=float`,
   `6=vector`) instead of string names for cross-version compatibility.

4. **Parameter VOP alias**: Fixed `usealiasaliasparm` typo to `usealiasparm`.

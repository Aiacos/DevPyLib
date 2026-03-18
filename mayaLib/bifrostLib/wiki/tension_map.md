# Tension Map — Bifrost Compound Build Guide

## Concetto

Per ogni **face-vertex** (angolo di faccia), calcoliamo la lunghezza dell'edge che parte da quel vertice verso il prossimo nella faccia. Lo facciamo sia per la mesh rest che per la deformed. La differenza percentuale è la tensione.

**Prerequisito:** mesh con facce uniformi (all-quad o all-triangle).

---

## Input/Output del Compound

### Input

| Porta | Tipo | Descrizione |
|-------|------|-------------|
| `rest_mesh` | Object | Mesh in rest pose (bind pose) |
| `deformed_mesh` | Object | Mesh deformata (stessa topologia) |
| `sensitivity` | float (default: 10) | Moltiplicatore per amplificare piccole deformazioni |

### Output

| Porta | Tipo | Descrizione |
|-------|------|-------------|
| `out_mesh` | Object | Mesh deformata con vertex colors applicati |
| `tension_weights` | array&lt;float&gt; | Valori tensione per-face-vertex [0=stretch, 0.5=neutro, 1=compressione] |

---

## FASE 1 — Estrazione dati mesh

### Nodo 1: `get_mesh_structure`

**Tipo:** `Geometry::Mesh::get_mesh_structure`
**Scopo:** Estrae la struttura topologica della mesh rest.

| Input | Collega da |
|-------|-----------|
| `mesh` | porta compound `rest_mesh` |

| Output | Tipo | Cosa contiene |
|--------|------|---------------|
| `point_position` | array&lt;float3&gt; | Posizioni di tutti i vertici nella rest pose |
| `face_vertex` | array&lt;uint&gt; | Array piatto di indici vertice per ogni faccia. Es: 3 quad → [0,1,5,4, 1,2,6,5, 2,3,7,6] |
| `face_vertex_count` | uint | Numero totale di face-vertex (es: 12 per 3 quad) |
| `face_count` | uint | Numero di facce (es: 3) |

### Nodo 2: `get_point_position`

**Tipo:** `Geometry::Properties::get_point_position`
**Scopo:** Estrae le posizioni dei vertici dalla mesh deformata.

| Input | Collega da |
|-------|-----------|
| `geometry` | porta compound `deformed_mesh` |

| Output | Tipo |
|--------|------|
| `point_position` | array&lt;float3&gt; — posizioni deformate |

---

## FASE 2 — Calcolo face_size (vertici per faccia)

### Nodo 3: `divide` ("compute_fs")

**Tipo:** `Core::Math::divide`
**Scopo:** face_vertex_count / face_count = vertici per faccia (es: 12/3 = 4.0 per quad).

| Input | Collega da |
|-------|-----------|
| porta superiore | Nodo 1 `get_mesh_structure` → `face_vertex_count` |
| porta inferiore | Nodo 1 `get_mesh_structure` → `face_count` |

| Output | Valore esempio |
|--------|----------------|
| `output` | 4.0 (float) |

### Nodo 4: `truncate` ("face_size")

**Tipo:** `Core::Math::truncate`
**Scopo:** Converte 4.0 → 4 (intero).

| Input | Collega da |
|-------|-----------|
| `value` | Nodo 3 `divide` → `output` |

| Output | Valore esempio |
|--------|----------------|
| `truncated` | 4 |

---

## FASE 3 — Calcolo indice "next vertex in face"

Per ogni face-vertex, troviamo il prossimo vertice nella stessa faccia, con wrapping (l'ultimo vertice della faccia torna al primo).

### Nodo 5: `get_array_indices` ("fv_indices")

**Tipo:** `Core::Array::get_array_indices`
**Scopo:** Genera [0, 1, 2, 3, 4, 5, ...] — un indice per ogni face-vertex.

| Input | Collega da |
|-------|-----------|
| `array` | Nodo 1 `get_mesh_structure` → `face_vertex` |

| Output | Valore esempio |
|--------|----------------|
| `indices` | [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11] |

### Nodo 6: `divide` ("idx_div_fs")

**Tipo:** `Core::Math::divide`
**Scopo:** indice / face_size — per sapere a quale faccia appartiene ogni face-vertex.

| Input | Collega da |
|-------|-----------|
| porta superiore | Nodo 5 → `indices` |
| porta inferiore | Nodo 4 → `truncated` |

| Output | Valore esempio (face_size=4) |
|--------|------|
| `output` | [0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, ...] |

### Nodo 7: `truncate` ("face_idx")

**Tipo:** `Core::Math::truncate`
**Scopo:** Tronca al numero di faccia intero.

| Input | Collega da |
|-------|-----------|
| `value` | Nodo 6 → `output` |

| Output | Valore esempio |
|--------|----------------|
| `truncated` | [0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2] |

### Nodo 8: `multiply` ("face_start")

**Tipo:** `Core::Math::multiply`
**Scopo:** face_idx × face_size = indice di inizio della faccia nel face_vertex array.

| Input | Collega da |
|-------|-----------|
| porta superiore | Nodo 7 → `truncated` (face_idx) |
| porta inferiore | Nodo 4 → `truncated` (face_size) |

| Output | Valore esempio |
|--------|----------------|
| `output` | [0, 0, 0, 0, 4, 4, 4, 4, 8, 8, 8, 8] |

### Nodo 9: `subtract` ("local_idx")

**Tipo:** `Core::Math::subtract`
**Scopo:** indice locale dentro la faccia = indice_globale - face_start.

| Input | Collega da |
|-------|-----------|
| porta superiore (first) | Nodo 5 → `indices` |
| porta inferiore (second) | Nodo 8 → `output` (face_start) |

| Output | Valore esempio |
|--------|----------------|
| `output` | [0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3] |

### Nodo 10: `add` ("local_plus1")

**Tipo:** `Core::Math::add`
**Scopo:** local_idx + 1.

| Input | Collega da |
|-------|-----------|
| porta superiore | Nodo 9 → `output` (local_idx) |
| porta inferiore | **valore costante `1`** (scrivi 1 nella porta) |

| Output | Valore esempio |
|--------|----------------|
| `output` | [1, 2, 3, 4, 1, 2, 3, 4, 1, 2, 3, 4] |

### Nodo 11: `modulo` ("next_local")

**Tipo:** `Core::Math::modulo`
**Scopo:** (local_idx + 1) % face_size — il 4 diventa 0 (wrapping!).

| Input | Collega da |
|-------|-----------|
| `value` | Nodo 10 → `output` |
| `divisor` | Nodo 4 → `truncated` (face_size) |

| Output | Valore esempio |
|--------|----------------|
| `remainder` | [1, 2, 3, **0**, 1, 2, 3, **0**, 1, 2, 3, **0**] |

### Nodo 12: `add` ("next_fv_idx")

**Tipo:** `Core::Math::add`
**Scopo:** face_start + next_local = indice globale del prossimo face-vertex.

| Input | Collega da |
|-------|-----------|
| porta superiore | Nodo 8 → `output` (face_start) |
| porta inferiore | Nodo 11 → `remainder` (next_local) |

| Output | Valore esempio |
|--------|----------------|
| `output` | [1, 2, 3, **0**, 5, 6, 7, **4**, 9, 10, 11, **8**] |

### Nodo 13: `get_from_array` ("next_vert")

**Tipo:** `Core::Array::get_from_array`
**Scopo:** Lookup dell'indice VERTICE reale dal face_vertex array.

| Input | Collega da |
|-------|-----------|
| `array` | Nodo 1 `get_mesh_structure` → `face_vertex` |
| `index` | Nodo 12 → `output` (next_fv_idx) |

| Output | Descrizione |
|--------|-------------|
| `value` | Per ogni face-vertex, l'indice del vertice SUCCESSIVO nella stessa faccia |

---

## FASE 4 — Lookup posizioni per gli edge

Usiamo `get_from_array` per cercare le posizioni dei vertici. Bifrost auto-broadcasta: se passi un array di indici, ottieni un array di posizioni.

### Nodo 14: `get_from_array` ("rest_fv_pos")

**Scopo:** Posizioni rest del vertice corrente per ogni face-vertex.

| Input | Collega da |
|-------|-----------|
| `array` | Nodo 1 `get_mesh_structure` → `point_position` |
| `index` | Nodo 1 `get_mesh_structure` → `face_vertex` |

| Output |
|--------|
| `value` — array&lt;float3&gt; posizioni rest ordinate per face-vertex |

### Nodo 15: `get_from_array` ("rest_next_pos")

**Scopo:** Posizioni rest del vertice SUCCESSIVO per ogni face-vertex.

| Input | Collega da |
|-------|-----------|
| `array` | Nodo 1 `get_mesh_structure` → `point_position` |
| `index` | Nodo 13 → `value` (next_vert) |

| Output |
|--------|
| `value` — posizioni rest del vertice successivo nell'edge |

### Nodo 16: `get_from_array` ("def_fv_pos")

**Scopo:** Posizioni deformate del vertice corrente.

| Input | Collega da |
|-------|-----------|
| `array` | Nodo 2 `get_point_position` → `point_position` |
| `index` | Nodo 1 `get_mesh_structure` → `face_vertex` |

| Output |
|--------|
| `value` — posizioni deformate ordinate per face-vertex |

### Nodo 17: `get_from_array` ("def_next_pos")

**Scopo:** Posizioni deformate del vertice SUCCESSIVO.

| Input | Collega da |
|-------|-----------|
| `array` | Nodo 2 `get_point_position` → `point_position` |
| `index` | Nodo 13 → `value` (next_vert) |

| Output |
|--------|
| `value` — posizioni deformate del vertice successivo |

---

## FASE 5 — Calcolo lunghezze edge

### Nodo 18: `subtract` ("rest_edge")

**Scopo:** Vettore edge rest = pos_next - pos_corrente.

| Input | Collega da |
|-------|-----------|
| porta superiore | Nodo 15 → `value` (rest_next_pos) |
| porta inferiore | Nodo 14 → `value` (rest_fv_pos) |

| Output |
|--------|
| `output` — array&lt;float3&gt; vettori edge in rest pose |

### Nodo 19: `length` ("rest_len")

**Tipo:** `Core::Math::length`

| Input | Collega da |
|-------|-----------|
| `vector` | Nodo 18 → `output` |

| Output |
|--------|
| `length` — array&lt;float&gt; lunghezze edge in rest pose |

### Nodo 20: `subtract` ("def_edge")

**Scopo:** Vettore edge deformato = pos_next - pos_corrente.

| Input | Collega da |
|-------|-----------|
| porta superiore | Nodo 17 → `value` (def_next_pos) |
| porta inferiore | Nodo 16 → `value` (def_fv_pos) |

| Output |
|--------|
| `output` — vettori edge deformati |

### Nodo 21: `length` ("def_len")

**Tipo:** `Core::Math::length`

| Input | Collega da |
|-------|-----------|
| `vector` | Nodo 20 → `output` |

| Output |
|--------|
| `length` — lunghezze edge deformate |

---

## FASE 6 — Calcolo tensione

### Nodo 22: `max` ("safe_rest")

**Tipo:** `Core::Math::max`
**Scopo:** Evita divisione per zero se un edge ha lunghezza 0.

| Input | Collega da |
|-------|-----------|
| porta superiore | Nodo 19 → `length` (rest_len) |
| porta inferiore | **valore costante `0.0001`** |

| Output |
|--------|
| `maximum` — rest_len ma minimo 0.0001 |

### Nodo 23: `subtract` ("edge_diff")

**Scopo:** rest_len - def_len.

| Input | Collega da |
|-------|-----------|
| porta superiore | Nodo 19 → `length` (rest_len) |
| porta inferiore | Nodo 21 → `length` (def_len) |

| Output |
|--------|
| `output` — differenza lunghezze (positivo = compressione, negativo = stretch) |

### Nodo 24: `divide` ("edge_ratio")

**Scopo:** (rest_len - def_len) / rest_len — variazione percentuale normalizzata.

| Input | Collega da |
|-------|-----------|
| porta superiore | Nodo 23 → `output` (edge_diff) |
| porta inferiore | Nodo 22 → `maximum` (safe_rest) |

| Output |
|--------|
| `output` — ratio tipicamente tra -0.1 e +0.1 per deformazioni normali |

### Nodo 25: `multiply` ("scale_ratio")

**Scopo:** Amplifica il ratio con la sensitivity.

| Input | Collega da |
|-------|-----------|
| porta superiore | Nodo 24 → `output` (edge_ratio) |
| porta inferiore | porta compound `sensitivity` |

| Output |
|--------|
| `output` — ratio amplificato |

### Nodo 26: `add` ("tension_raw")

**Scopo:** Centra il valore su 0.5 (neutro).

| Input | Collega da |
|-------|-----------|
| porta superiore | Nodo 25 → `output` (scale_ratio) |
| porta inferiore | **valore costante `0.5`** |

| Output |
|--------|
| `output` — tensione raw: &lt;0.5 = stretch, 0.5 = neutro, &gt;0.5 = compressione |

### Nodo 27: `clamp` ("tension_clamped")

**Tipo:** `Core::Math::clamp`
**Scopo:** Limita il range a [0, 1].

| Input | Collega da |
|-------|-----------|
| `value` | Nodo 26 → `output` |
| `min` | **valore costante `0`** |
| `max` | **valore costante `1`** |

| Output | Collega a |
|--------|-----------|
| `clamped` | → output compound **`tension_weights`** |

---

## FASE 7 — Colori (verde=stretch, nero=neutro, rosso=compressione)

### Nodo 28: `change_range` ("red_ramp")

**Scopo:** Canale ROSSO — attivo solo sopra 0.5 (compressione).

| Input | Valore/Collega |
|-------|----------------|
| `value` | Nodo 27 → `clamped` |
| `from_start` | costante `0.5` |
| `from_end` | costante `1.0` |
| `to_start` | costante `0.0` |
| `to_end` | costante `1.0` |
| `clamp` | `true` |

| Output |
|--------|
| `result` — 0 sotto 0.5, sale a 1 verso 1.0 |

### Nodo 29: `change_range` ("green_ramp")

**Scopo:** Canale VERDE — attivo solo sotto 0.5 (stretch).

| Input | Valore/Collega |
|-------|----------------|
| `value` | Nodo 27 → `clamped` |
| `from_start` | costante `0.5` |
| `from_end` | costante `0.0` |
| `to_start` | costante `0.0` |
| `to_end` | costante `1.0` |
| `clamp` | `true` |

| Output |
|--------|
| `result` — 0 sopra 0.5, sale a 1 verso 0.0 |

### Nodo 30: `scalar_to_vector3` ("tension_color")

**Tipo:** `Core::Conversion::scalar_to_vector3`

| Input | Collega da |
|-------|-----------|
| `x` | Nodo 28 → `result` (red) |
| `y` | Nodo 29 → `result` (green) |
| `z` | lascia a `0` (niente blu) |

| Output |
|--------|
| `vector3` — colore RGB per ogni face-vertex |

### Nodo 31: `set_geo_property` ("set_color")

**Tipo:** `Geometry::Properties::set_geo_property`
**Scopo:** Scrive i colori sulla mesh deformata.

| Input | Collega/Valore |
|-------|----------------|
| `geometry` | porta compound `deformed_mesh` |
| `data` | Nodo 30 → `vector3` (tension_color) |
| `property` | stringa `"color"` |
| `target` | stringa `"face_vertex_component"` |

| Output | Collega a |
|--------|-----------|
| `out_geometry` | → output compound **`out_mesh`** |

---

## Riepilogo connessioni output compound

| Output compound | Collega da |
|----------------|-----------|
| `out_mesh` | Nodo 31 `set_geo_property` → `out_geometry` |
| `tension_weights` | Nodo 27 `clamp` → `clamped` |

---

## Mappa colori risultante

| Tensione | Valore | Colore |
|----------|--------|--------|
| Stretch massimo | 0.0 | Verde pieno (0,1,0) |
| Stretch medio | 0.25 | Verde scuro (0,0.5,0) |
| Neutro | 0.5 | Nero (0,0,0) |
| Compressione media | 0.75 | Rosso scuro (0.5,0,0) |
| Compressione massima | 1.0 | Rosso pieno (1,0,0) |

---

## Nota: porte dei nodi math variadic

I nodi `add`, `subtract`, `multiply`, `divide`, `max` hanno porte **dinamiche**.
Quando trascini la prima connessione appare la prima porta, quando trascini la seconda ne appare un'altra. Non hanno nomi fissi nell'editor visuale — le porte si creano collegando.

## Nota: limitazione mesh miste

Funziona correttamente per mesh con facce uniformi (tutti quad o tutti triangoli).
Per mesh con facce miste il `face_size = truncate(face_vertex_count / face_count)` produce un valore medio che non corrisponde a tutte le facce.

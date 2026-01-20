# ShaderLib Documentation

ShaderLib provides shader creation and lookdev utilities for Maya, supporting multiple renderers including Arnold, RenderMan, and 3Delight.

---

## Table of Contents

- [Overview](#overview)
- [Module Structure](#module-structure)
- [Renderer Support](#renderer-support)
- [TextureShader Class](#textureshader-class)
- [BuildAllShaders Class](#buildallshaders-class)
- [Shader Base Classes](#shader-base-classes)
- [Texture Utilities](#texture-utilities)
- [Usage Examples](#usage-examples)

---

## Overview

ShaderLib simplifies shader creation by providing high-level classes that automatically handle texture node creation, material property configuration, and renderer-specific settings based on the active renderer.

### Key Features

- **Multi-renderer support**: Arnold, RenderMan, 3Delight
- **Automatic texture node creation**: File nodes with proper color space
- **Batch shader building**: Create shaders for entire texture directories
- **Place2dTexture optimization**: Single node for multiple textures
- **USD Preview Surface**: Support for USD-compatible shaders

### Module Structure

```
shaderLib/
├── __init__.py
├── shader.py              # High-level shader interface
├── shaders_maker.py       # Batch shader creation
├── add_gamma_correct.py   # Gamma correction utilities
├── base/
│   ├── __init__.py
│   ├── shader_base.py     # ShaderBase, UsdPreviewSurface
│   ├── arnold.py          # AiStandardSurface
│   ├── renderman.py       # PxrDisneyBSDF
│   ├── delight.py         # Principled3dl
│   └── texture.py         # Texture node utilities
└── utils/
    └── ...                # Additional utilities
```

---

## Renderer Support

ShaderLib automatically detects the active renderer and creates appropriate shaders:

| Renderer | Shader Type | Module |
|----------|-------------|--------|
| **Arnold** | aiStandardSurface | `base/arnold.py` |
| **RenderMan** | PxrDisneyBSDF | `base/renderman.py` |
| **3Delight** | Principled3dl | `base/delight.py` |
| **USD** | UsdPreviewSurface | `base/shader_base.py` |

### Renderer Detection

```python
import pymel.core as pm

# Get current renderer
renderer = pm.ls("defaultRenderGlobals")[0].currentRenderer.get()
# Returns: "arnold", "renderManRIS", etc.
```

---

## TextureShader Class

The main class for creating shaders from texture files.

### Constructor

```python
from mayaLib.shaderLib.shader import TextureShader

shader = TextureShader(
    texture_path="/path/to/textures/",
    geo_name="character",
    textureset_dict={
        'diffuse': 'char_diffuse.exr',
        'normal': 'char_normal.exr',
        'roughness': 'char_roughness.exr'
    },
    single_place_node=True
)
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `texture_path` | str | Required | Path to texture files directory |
| `geo_name` | str | Required | Name for the shader (usually geometry name) |
| `textureset_dict` | dict | Required | Dictionary mapping texture channels to filenames |
| `single_place_node` | bool | True | Share one place2dTexture node for all textures |

### Texture Channel Names

| Channel | Description | Typical Connection |
|---------|-------------|-------------------|
| `diffuse` | Base color | baseColor (Arnold), subsurfaceColor (PxrDisney) |
| `normal` | Normal map | normalCamera |
| `roughness` | Roughness map | specularRoughness |
| `metalness` | Metallic map | metalness |
| `displacement` | Displacement map | displacementShader |
| `opacity` | Opacity map | opacity |

### Methods

```python
# Get the created shader
shader_node = shader.get_shader()
```

### Attributes

| Attribute | Description |
|-----------|-------------|
| `renderer` | Detected active renderer |
| `shader` | Created shader object |
| `place_node` | Shared place2dTexture node (if single_place_node=True) |
| `filenode_dict` | Dictionary of created file nodes by channel |

---

## BuildAllShaders Class

Batch shader builder for organizing texture directories.

### Constructor

```python
from mayaLib.shaderLib.shader import BuildAllShaders

builder = BuildAllShaders(folder="/path/to/organized/textures/")
```

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `folder` | str | Path to directory containing organized texture files |

### How It Works

1. Scans the folder for texture files
2. Organizes textures by naming convention (e.g., `char_diffuse.exr`, `char_normal.exr`)
3. Creates TextureShader objects for each texture set found
4. Assigns shaders to matching geometry (by name)

---

## Shader Base Classes

### ShaderBase (`base/shader_base.py`)

Abstract base class for renderer-specific shaders.

```python
from mayaLib.shaderLib.base.shader_base import ShaderBase

# Base class for all shader implementations
# Provides common interface for texture connections
```

### UsdPreviewSurface (`base/shader_base.py`)

USD-compatible preview surface shader.

```python
from mayaLib.shaderLib.base.shader_base import UsdPreviewSurface

usd_shader = UsdPreviewSurface(
    shader_name="character_shader",
    file_node_dict=file_nodes
)
```

### AiStandardSurface (`base/arnold.py`)

Arnold aiStandardSurface shader.

```python
from mayaLib.shaderLib.base.arnold import AiStandardSurface

arnold_shader = AiStandardSurface(
    shader_name="character_shader",
    file_node_dict=file_nodes
)
```

### PxrDisneyBSDF (`base/renderman.py`)

RenderMan PxrDisneyBSDF shader.

```python
from mayaLib.shaderLib.base.renderman import PxrDisneyBSDF

pxr_shader = PxrDisneyBSDF(
    shader_name="character_shader",
    file_node_dict=file_nodes
)
```

### Principled3dl (`base/delight.py`)

3Delight Principled shader.

```python
from mayaLib.shaderLib.base.delight import Principled3dl

delight_shader = Principled3dl(
    shader_name="character_shader",
    file_node_dict=file_nodes
)
```

---

## Texture Utilities

### TextureFileNode (`base/texture.py`)

Creates Maya file texture nodes with proper configuration.

```python
from mayaLib.shaderLib.base import texture

# Create a file node
file_node = texture.TextureFileNode(
    path="/textures/",
    filename="diffuse.exr",
    single_place_node=None  # Or pass existing place2dTexture
)

# Access the file node
fn = file_node.filenode
```

### TexturePxrTexture (`base/texture.py`)

Creates RenderMan PxrTexture nodes.

```python
from mayaLib.shaderLib.base import texture

pxr_tex = texture.TexturePxrTexture(
    path="/textures/",
    filename="diffuse.tex"
)
```

---

## Usage Examples

### Creating a Shader for Arnold

```python
from mayaLib.shaderLib.shader import TextureShader
import pymel.core as pm

# Ensure Arnold is active
pm.loadPlugin("mtoa", quiet=True)
pm.setAttr("defaultRenderGlobals.currentRenderer", "arnold", type="string")

# Create shader from textures
shader = TextureShader(
    texture_path="/projects/character/textures/",
    geo_name="body",
    textureset_dict={
        'diffuse': 'body_baseColor.exr',
        'normal': 'body_normal.exr',
        'roughness': 'body_roughness.exr',
        'metalness': 'body_metallic.exr'
    }
)

# Assign to geometry
body_geo = pm.ls("body_geo")[0]
pm.select(body_geo)
pm.hyperShade(assign=shader.get_shader())
```

### Creating Multiple Shaders from Directory

```python
from mayaLib.shaderLib.shader import BuildAllShaders

# Organize textures in folder by material:
# /textures/
#   body_diffuse.exr
#   body_normal.exr
#   body_roughness.exr
#   face_diffuse.exr
#   face_normal.exr
#   ...

# Build all shaders automatically
builder = BuildAllShaders(folder="/projects/character/textures/")
```

### Manual Shader Creation with Base Classes

```python
import pymel.core as pm
from mayaLib.shaderLib.base.arnold import AiStandardSurface
from mayaLib.shaderLib.base import texture

# Create texture file nodes
place_node = pm.shadingNode("place2dTexture", asUtility=True)

diffuse_fn = texture.TextureFileNode(
    path="/textures/",
    filename="diffuse.exr",
    single_place_node=place_node
)

normal_fn = texture.TextureFileNode(
    path="/textures/",
    filename="normal.exr",
    single_place_node=place_node
)

# Create shader with file nodes
file_nodes = {
    'diffuse': diffuse_fn.filenode,
    'normal': normal_fn.filenode
}

shader = AiStandardSurface(
    shader_name="my_shader",
    file_node_dict=file_nodes
)
```

### Adding Gamma Correction

```python
from mayaLib.shaderLib import add_gamma_correct

# Add gamma correction nodes to texture workflow
# See module for specific functions
```

---

## Texture Naming Conventions

ShaderLib expects textures to follow naming conventions:

```
{asset}_{channel}.{ext}

Examples:
- character_diffuse.exr
- character_baseColor.exr
- character_normal.exr
- character_roughness.exr
- character_metallic.exr
- character_displacement.exr
- character_opacity.exr
```

### UDIM Support

For UDIM textures, use the `<UDIM>` token:

```
character_diffuse.<UDIM>.exr
character_normal.<UDIM>.exr
```

---

## Best Practices

1. **Use single place2dTexture** for performance when textures share UV layout
2. **Organize textures by asset** in dedicated folders
3. **Follow naming conventions** for automatic texture detection
4. **Use EXR format** for linear workflow compatibility
5. **Set proper color space** (sRGB for diffuse/albedo, Raw for data maps)
6. **Create USD Preview Surfaces** for pipeline compatibility

---

## Color Space Management

| Texture Type | Color Space |
|--------------|-------------|
| Diffuse/Albedo | sRGB |
| Normal | Raw |
| Roughness | Raw |
| Metalness | Raw |
| Displacement | Raw |
| Opacity | sRGB or Raw |

```python
import pymel.core as pm

# Set color space on file node
file_node = pm.ls("file1")[0]
file_node.colorSpace.set("sRGB")  # or "Raw" for data maps
```

---

## See Also

- [MayaLib Home](Home.md)
- [LookdevLib](Home.md#module-structure) - Additional lookdev tools
- [BifrostLib](BifrostLib.md) - USD integration

---

*Last updated: January 2026*

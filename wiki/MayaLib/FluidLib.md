# FluidLib Documentation

FluidLib provides fluid simulation utilities for Maya, offering preset-based fluid effect creation for smoke, fire, and explosions.

---

## Table of Contents

- [Overview](#overview)
- [Module Structure](#module-structure)
- [Base Classes](#base-classes)
- [Fluid Presets](#fluid-presets)
- [Ramp Utilities](#ramp-utilities)
- [Usage Examples](#usage-examples)
- [Parameter Reference](#parameter-reference)

---

## Overview

FluidLib simplifies Maya fluid simulation workflows by providing pre-configured fluid presets. It uses a composition pattern where `BaseFluid` combines a `FluidContainer` and `FlEmitter` to create complete fluid setups with appropriate settings for different effects.

### Key Features

- **Preset-based creation**: Smoke, fire, and explosion presets
- **Automatic emitter connection**: Emitter automatically connected to container
- **Optimized settings**: Pre-configured solver, shading, and simulation settings
- **Ramp utilities**: Easy opacity and color ramp configuration

### Module Structure

```
fluidLib/
├── __init__.py
├── smoke.py          # WispySmoke, ThickSmoke presets
├── fire.py           # Fire presets
├── fire_smoke.py     # Combined fire and smoke
├── explosion.py      # Explosion presets
├── base/
│   ├── __init__.py
│   ├── base_fluid.py      # BaseFluid class
│   ├── base_container.py  # FluidContainer class
│   ├── base_emitter.py    # FlEmitter class
│   └── ramp_utils.py      # Ramp manipulation utilities
└── utility/
    └── density_color.py   # Color presets for density
```

---

## Base Classes

### BaseFluid (`base/base_fluid.py`)

The core class that combines container and emitter into a complete fluid system.

```python
from mayaLib.fluidLib.base.base_fluid import BaseFluid

fluid = BaseFluid(
    fluid_name="myFluid",   # Name prefix for nodes
    base_res=32,            # Base resolution
    emit_obj=None           # Optional emitter attachment object
)
```

#### Constructor Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `fluid_name` | str | "" | Name prefix for fluid nodes |
| `base_res` | int | 32 | Base resolution of the fluid container |
| `emit_obj` | str | None | Object to attach emitter to |

#### Methods

```python
# Get the fluid shape node
fluid_shape = fluid.get_fluid_shape()

# Get the fluid emitter node
emitter = fluid.get_fluid_emitter()
```

#### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `fluid_shape` | PyNode | The fluid shape node |
| `fluid_emit` | PyNode | The fluid emitter node |
| `fluid_transform` | PyNode | The fluid transform node |

#### Default Container Settings

BaseFluid configures the container with these defaults:

| Setting | Value | Description |
|---------|-------|-------------|
| `baseResolution` | 32 | Base voxel resolution |
| `boundaryX` | 0 | X boundary (open) |
| `boundaryY` | 2 | Y boundary (open top) |
| `boundaryZ` | 0 | Z boundary (open) |
| `highDetailSolve` | 3 | High detail solver |
| `substeps` | 2 | Solver substeps |
| `solverQuality` | 254 | Maximum solver quality |
| `autoResize` | 1 | Enable auto-resize |
| `maxResolution` | base_res^2 | Maximum resolution |
| `autoResizeMargin` | 4 | Resize margin voxels |
| `selfShadowing` | 1 | Enable self-shadowing |

### FluidContainer (`base/base_container.py`)

Creates and configures fluid containers.

```python
from mayaLib.fluidLib.base.base_container import FluidContainer

container = FluidContainer()
fluid_shape = container.get_container()
```

### FlEmitter (`base/base_emitter.py`)

Creates fluid emitters with optional object attachment.

```python
from mayaLib.fluidLib.base.base_emitter import FlEmitter

emitter = FlEmitter(obj="pSphere1")  # Attach to object
emitter_node = emitter.get_emitter()
```

---

## Fluid Presets

### WispySmoke (`smoke.py`)

Light, wispy smoke simulation.

```python
from mayaLib.fluidLib.smoke import WispySmoke

smoke = WispySmoke(
    fluid_name="wispySmoke",
    base_res=32,
    emit_obj=None
)
```

#### Wispy Smoke Settings

| Category | Setting | Value |
|----------|---------|-------|
| **Emitter** | rate | 250 |
| | maxDistance | 0.2 |
| | fluidDensityEmission | 2.5 |
| **Density** | densityScale | 0.65 |
| | densityBuoyancy | 25 |
| | densityDissipation | 0.15 |
| | densityTension | 0.025 |
| | tensionForce | 0.1 |
| | densityGradientForce | 10 |
| **Velocity** | velocitySwirl | 5 |
| **Turbulence** | turbulenceStrength | 5 (frame 1) to 0.1 (frame 12) |
| | turbulenceFrequency | 0.5 |
| | turbulenceSpeed | 0.5 |
| **Shading** | transparency | (0.214, 0.214, 0.214) |
| | edgeDropoff | 0 |
| | colorInput | Constant |
| | opacityInput | Density |

### ThickSmoke (`smoke.py`)

Dense, heavy smoke simulation.

```python
from mayaLib.fluidLib.smoke import ThickSmoke

smoke = ThickSmoke(
    fluid_name="thickSmoke",
    base_res=32,
    emit_obj=None
)
```

### Fire Presets (`fire.py`)

Fire simulation presets.

```python
from mayaLib.fluidLib.fire import Fire  # Example class name

fire = Fire(
    fluid_name="fire",
    base_res=32,
    emit_obj=None
)
```

### FireSmoke (`fire_smoke.py`)

Combined fire and smoke simulation.

```python
from mayaLib.fluidLib.fire_smoke import FireSmoke

fire_smoke = FireSmoke(
    fluid_name="fireSmoke",
    base_res=32,
    emit_obj=None
)
```

### Explosion (`explosion.py`)

Explosion simulation presets.

```python
from mayaLib.fluidLib.explosion import Explosion

explosion = Explosion(
    fluid_name="explosion",
    base_res=64,
    emit_obj=None
)
```

---

## Ramp Utilities

### setup_manual_opacity_ramp

Configure opacity ramp with specific control points.

```python
from mayaLib.fluidLib.base.ramp_utils import setup_manual_opacity_ramp

# Set up opacity ramp with control points
# Format: (position, value, interpolation)
# Interpolation: 1=None, 2=Linear, 3=Smooth, 4=Spline
setup_manual_opacity_ramp(
    fluid_shape,
    [
        (0.0, 0.0, 3),   # Position 0%, value 0, smooth interp
        (0.25, 0.1, 3),  # Position 25%, value 0.1
        (0.5, 0.5, 3),   # Position 50%, value 0.5
        (0.75, 0.1, 3),  # Position 75%, value 0.1
        (1.0, 0.0, 3),   # Position 100%, value 0
    ]
)
```

### setup_repart_opacity_ramp

Configure opacity ramp with even distribution.

```python
from mayaLib.fluidLib.base.ramp_utils import setup_repart_opacity_ramp

# Evenly distributed opacity ramp
setup_repart_opacity_ramp(fluid_shape, num_points=5, max_value=1.0)
```

---

## Density Color Presets

### density_color.py

Provides color presets for different fluid types.

```python
from mayaLib.fluidLib.utility import density_color

# Get wispy smoke color
r, g, b = density_color.wispy_smoke_color()

# Apply to fluid
fluid_shape.color[0].color_Color.set(r, g, b, type="double3")
```

---

## Usage Examples

### Basic Smoke Creation

```python
from mayaLib.fluidLib.smoke import WispySmoke
import pymel.core as pm

# Create smoke simulation
smoke = WispySmoke(fluid_name="campfire_smoke", base_res=48)

# Get fluid components
fluid_shape = smoke.get_fluid_shape()
emitter = smoke.get_fluid_emitter()

print(f"Created fluid: {fluid_shape}")
print(f"Emitter: {emitter}")

# Play simulation
pm.playbackOptions(minTime=1, maxTime=100)
pm.play()
```

### Smoke Attached to Object

```python
from mayaLib.fluidLib.smoke import WispySmoke
import pymel.core as pm

# Create emitter source object
source = pm.polySphere(name="smoke_source")[0]
pm.move(source, 0, 0, 0)

# Create smoke attached to object
smoke = WispySmoke(
    fluid_name="attached_smoke",
    base_res=32,
    emit_obj="smoke_source"
)

# Now emitter follows the sphere
```

### Customizing Fluid Parameters

```python
from mayaLib.fluidLib.smoke import WispySmoke
import pymel.core as pm

# Create smoke
smoke = WispySmoke(fluid_name="custom_smoke", base_res=64)
fluid = smoke.get_fluid_shape()

# Customize density
fluid.densityScale.set(1.0)
fluid.densityBuoyancy.set(50)
fluid.densityDissipation.set(0.05)

# Customize turbulence
fluid.turbulenceStrength.set(10)
fluid.turbulenceFrequency.set(1.0)

# Customize shading
fluid.transparency.set(0.3, 0.3, 0.3, type="double3")
fluid.selfShadowing.set(True)
fluid.shadowOpacity.set(0.5)
```

### Creating Fire Effect

```python
from mayaLib.fluidLib.base.base_fluid import BaseFluid
import pymel.core as pm

# Create base fluid
fire = BaseFluid(fluid_name="fire", base_res=48)
fluid = fire.get_fluid_shape()
emitter = fire.get_fluid_emitter()

# Configure for fire
fluid.densityBuoyancy.set(100)
fluid.temperatureScale.set(1)
fluid.temperatureBuoyancy.set(50)

# Enable temperature
emitter.fluidHeatEmission.set(1)
emitter.heatMethod.set(0)

# Set fire colors using incandescence
fluid.incandescence[0].incandescence_Color.set(1, 0.5, 0, type="double3")
fluid.incandescence[0].incandescence_Position.set(0)
fluid.incandescence[1].incandescence_Color.set(1, 0.2, 0, type="double3")
fluid.incandescence[1].incandescence_Position.set(0.5)
fluid.incandescence[2].incandescence_Color.set(0.5, 0, 0, type="double3")
fluid.incandescence[2].incandescence_Position.set(1)
```

### Explosion Setup

```python
from mayaLib.fluidLib.base.base_fluid import BaseFluid
from mayaLib.fluidLib.base.ramp_utils import setup_manual_opacity_ramp
import pymel.core as pm

# Create explosion fluid
explosion = BaseFluid(fluid_name="explosion", base_res=64)
fluid = explosion.get_fluid_shape()
emitter = explosion.get_fluid_emitter()

# High buoyancy for explosive rise
fluid.densityBuoyancy.set(200)
fluid.densityDissipation.set(0.02)

# Strong initial turbulence that fades
pm.setKeyframe(fluid, attribute="turbulenceStrength", time=1, value=50)
pm.setKeyframe(fluid, attribute="turbulenceStrength", time=20, value=5)

# Burst emission
pm.setKeyframe(emitter, attribute="rate", time=1, value=5000)
pm.setKeyframe(emitter, attribute="rate", time=5, value=0)

# Setup opacity ramp for mushroom cloud effect
setup_manual_opacity_ramp(fluid, [
    (0.0, 0.0, 3),
    (0.3, 0.8, 3),
    (0.7, 0.6, 3),
    (1.0, 0.0, 3),
])
```

---

## Parameter Reference

### Fluid Container Attributes

| Category | Attribute | Description |
|----------|-----------|-------------|
| **Resolution** | baseResolution | Base voxel resolution |
| | maxResolution | Maximum auto-resize resolution |
| **Boundaries** | boundaryX/Y/Z | 0=closed, 1=open, 2=one side open |
| **Solver** | highDetailSolve | Detail solver level |
| | substeps | Solver substeps per frame |
| | solverQuality | Quality (0-254) |
| **Density** | densityScale | Overall density multiplier |
| | densityBuoyancy | Rise speed from density |
| | densityDissipation | Density fade rate |
| | densityTension | Surface tension |
| **Velocity** | velocitySwirl | Swirling motion |
| **Turbulence** | turbulenceStrength | Noise strength |
| | turbulenceFrequency | Noise frequency |
| | turbulenceSpeed | Noise animation speed |
| **Shading** | transparency | Overall transparency |
| | selfShadowing | Enable self-shadowing |

### Emitter Attributes

| Attribute | Description |
|-----------|-------------|
| rate | Emission rate |
| maxDistance | Maximum emission distance |
| fluidDensityEmission | Density emission amount |
| fluidHeatEmission | Heat emission amount |

---

## Best Practices

1. **Start with presets**: Use WispySmoke, ThickSmoke, etc. as starting points
2. **Match resolution to scale**: Higher resolution for close-up effects
3. **Use auto-resize**: Enables efficient simulation of expanding fluids
4. **Keyframe turbulence**: Animate turbulence to control behavior over time
5. **Optimize substeps**: Increase for fast-moving fluids
6. **Cache simulations**: Use fluid caching for playback and rendering

---

## See Also

- [MayaLib Home](Home.md)
- [BifrostLib](BifrostLib.md) - Modern Bifrost fluid workflows
- [RigLib](RigLib.md) - For attaching fluids to rigs

---

*Last updated: January 2026*

# AnimationLib Documentation

AnimationLib provides animation tools for Maya, including motion capture file import and retargeting utilities.

---

## Table of Contents

- [Overview](#overview)
- [BVH Importer](#bvh-importer)
- [Usage Examples](#usage-examples)
- [API Reference](#api-reference)

---

## Overview

AnimationLib focuses on motion capture workflows, providing tools to import BVH (BioVision Hierarchy) files into Maya and retarget them onto existing skeletons.

### Module Structure

```
animationLib/
├── __init__.py
└── bvh_importer.py   # BVH file importer with UI
```

---

## BVH Importer

The BVH Importer is a comprehensive tool for importing BioVision Hierarchy motion capture files into Maya.

### Features

- **UI Dialog**: Interactive Maya window for import configuration
- **Scale Control**: Adjust rig scale to match BVH data
- **Frame Offset**: Specify starting frame for imported animation
- **Rotation Order**: Select rotation order (XYZ, YZX, ZXY, etc.)
- **Skeleton Targeting**: Retarget BVH data onto existing Maya skeletons
- **Debug Mode**: Detailed output for troubleshooting (limited to small frame counts)

### BVH Format

BVH is a common ASCII motion capture format containing:
- **Hierarchy Section**: Skeleton definition with joint names, offsets, and channels
- **Motion Section**: Frame count, frame time, and channel data per frame

### Translation Dictionary

The importer maps BVH channel names to Maya attributes:

| BVH Channel | Maya Attribute |
|-------------|----------------|
| `Xposition` | `translateX` |
| `Yposition` | `translateY` |
| `Zposition` | `translateZ` |
| `Xrotation` | `rotateX` |
| `Yrotation` | `rotateY` |
| `Zrotation` | `rotateZ` |

---

## BVHImporterDialog Class

### Constructor

```python
from mayaLib.animationLib.bvh_importer import BVHImporterDialog

# Create the importer dialog
dialog = BVHImporterDialog(debug=False)
```

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `debug` | bool | False | Enable debug output (WARNING: Don't use with >10 frames) |

### Dialog UI Elements

The dialog provides the following UI controls:

| Control | Description |
|---------|-------------|
| **Rig Scale** | Float field (0.01-2.0) to scale the imported skeleton |
| **Frame Offset** | Integer field to offset the starting frame |
| **Rotation Order** | Dropdown menu with XYZ, YZX, ZXY, XZY, YXZ, ZYX options |
| **Target Root** | Text field to specify the target skeleton's root joint |
| **Browse** | Button to select BVH file |
| **Import** | Button to perform the import |
| **Reload** | Button to reload the BVH file |

### UI Window

```
+-------------------------------------------+
|          BVH Importer v1.0.1              |
+-------------------------------------------+
| Options                                    |
+-------------------------------------------+
| Rig scale       [1.0        ]             |
| Frame offset    [0          ]             |
| Rotation Order  [XYZ      v]              |
+-------------------------------------------+
| Skeleton Targeting                         |
| (Select the hips)                          |
+-------------------------------------------+
| Target root     [           ]             |
| [Browse]  [Import]  [Reload]              |
+-------------------------------------------+
```

---

## TinyDAG Helper Class

A lightweight helper class to track parent-child hierarchy during BVH parsing.

```python
from mayaLib.animationLib.bvh_importer import TinyDAG

# Create a DAG node wrapper
node = TinyDAG(obj="joint1", p_obj=None)

# Get string representation
print(str(node))  # "joint1"

# Get full path
path = node._full_path()  # Returns hierarchical path
```

### Methods

| Method | Description |
|--------|-------------|
| `__str__()` | Returns the object name as string |
| `_full_path()` | Returns full hierarchical path with parent chain |

---

## Usage Examples

### Basic BVH Import

```python
from mayaLib.animationLib.bvh_importer import BVHImporterDialog

# Open the importer dialog
dialog = BVHImporterDialog()

# The dialog will appear in Maya
# 1. Click Browse to select a BVH file
# 2. Adjust scale, frame offset, and rotation order as needed
# 3. Click Import
```

### Import with Scale Adjustment

```python
# For mocap data that doesn't match Maya's unit scale:
# 1. Open dialog: BVHImporterDialog()
# 2. Set Rig Scale to 0.01 (for cm to m conversion)
# 3. Set Frame Offset to 1 (start at frame 1)
# 4. Import the file
```

### Retargeting to Existing Skeleton

```python
# To retarget BVH data onto an existing Maya skeleton:
# 1. Open dialog: BVHImporterDialog()
# 2. Select the hip/root joint of your target skeleton
# 3. Enter the joint name in "Target root" field
# 4. Import the BVH file
# The animation will be applied to your existing joints
```

### Debug Mode (Small Files Only)

```python
# For troubleshooting BVH parsing issues:
dialog = BVHImporterDialog(debug=True)

# WARNING: Debug mode prints extensive output
# Only use with BVH files containing <10 frames
# Otherwise the output becomes unmanageable
```

---

## API Reference

### bvh_importer Module

#### Classes

| Class | Description |
|-------|-------------|
| `TinyDAG` | Helper class for tracking parent hierarchy |
| `BVHImporterDialog` | Main importer UI class |

#### Constants

```python
TRANSLATION_DICT = {
    "Xposition": "translateX",
    "Yposition": "translateY",
    "Zposition": "translateZ",
    "Xrotation": "rotateX",
    "Yrotation": "rotateY",
    "Zrotation": "rotateZ",
}
```

### BVHImporterDialog Methods

| Method | Description |
|--------|-------------|
| `__init__(debug=False)` | Initialize the dialog |
| `setup_ui()` | Create and display the UI window |

### BVHImporterDialog Attributes

| Attribute | Description |
|-----------|-------------|
| `_filename` | Path to the BVH file |
| `_channels` | Parsed motion channels from BVH |
| `_root_node` | Target root joint for retargeting |
| `_debug` | Debug mode flag |

---

## File Format Reference

### BVH File Structure

```
HIERARCHY
ROOT Hips
{
    OFFSET 0.0 0.0 0.0
    CHANNELS 6 Xposition Yposition Zposition Zrotation Xrotation Yrotation
    JOINT Spine
    {
        OFFSET 0.0 10.0 0.0
        CHANNELS 3 Zrotation Xrotation Yrotation
        JOINT Spine1
        {
            ...
        }
    }
}
MOTION
Frames: 100
Frame Time: 0.033333
0.0 90.0 0.0 0.0 0.0 0.0 ...
...
```

### Key Sections

| Section | Description |
|---------|-------------|
| `HIERARCHY` | Skeleton definition |
| `ROOT` | Root joint of the skeleton |
| `JOINT` | Child joints |
| `End Site` | Terminal joints (no children) |
| `OFFSET` | Local offset from parent |
| `CHANNELS` | Animated channels (position and/or rotation) |
| `MOTION` | Animation data |
| `Frames` | Total number of frames |
| `Frame Time` | Duration of each frame in seconds |

---

## Troubleshooting

### Common Issues

**Problem**: Imported skeleton is too large/small

**Solution**: Adjust the "Rig Scale" value. Common conversions:
- cm to m: 0.01
- m to cm: 100
- inches to cm: 2.54

**Problem**: Animation plays too fast/slow

**Solution**: Check the BVH file's "Frame Time" value and adjust Maya's frame rate accordingly.

**Problem**: Joints are rotated incorrectly

**Solution**: Try different rotation order options in the dropdown menu.

**Problem**: Debug output is overwhelming

**Solution**: Only use debug mode with BVH files containing fewer than 10 frames.

---

## Credits

The BVH Importer was originally developed by Jeroen Hoolmans and is released under the GNU General Public License v3.0.

```
Copyright (C) 2012 Jeroen Hoolmans
Email: jhoolmans@gmail.com
License: GPL v3.0
Version: 1.0.1
```

---

## See Also

- [MayaLib Home](Home.md)
- [RigLib](RigLib.md) - For skeleton setup
- [HumanIK Integration](RigLib.md#humanik)

---

*Last updated: January 2026*

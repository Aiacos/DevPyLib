#!/usr/bin/env python
"""Manual Maya Verification Script for Control Shapes.

This script creates visual examples of all control shapes for manual verification
in Maya. Run this script in Maya's Script Editor to verify that all shapes render
correctly.

Usage:
    1. Open Maya
    2. Open Script Editor (Windows > General Editors > Script Editor)
    3. Load and execute this script
    4. Verify that all shapes appear in the viewport
    5. Check that shapes are properly scaled and oriented

Expected Results:
    - 13 control shapes should be created in a grid layout
    - Each shape should be visually distinct and properly scaled
    - Shapes should be named according to their type
    - No errors should appear in the Script Editor
"""

import pymel.core as pm
from mayaLib.rigLib.utils.control import Control


def clear_scene():
    """Clear the Maya scene for fresh testing."""
    pm.newFile(force=True)
    print("Scene cleared.")


def create_all_control_shapes():
    """Create all control shapes in a grid layout for visual inspection.

    Returns:
        dict: Dictionary mapping shape names to Control instances.
    """
    shapes = [
        # Existing shapes (8)
        "sphere",
        "move",
        "spine",      # Uses trapeziumCtrlShape
        "chest",
        "hip",
        "head",
        "display",
        "ikfk",
        # New shapes (5)
        "pin",
        "arrow",
        "cube",
        "cross",
        "square",
    ]

    controls = {}
    spacing = 5.0
    cols = 5

    print("\n" + "="*60)
    print("Creating Control Shapes")
    print("="*60)

    for idx, shape_name in enumerate(shapes):
        row = idx // cols
        col = idx % cols

        x_pos = col * spacing
        z_pos = row * spacing

        try:
            # Create control with specific shape
            ctrl = Control(
                prefix=f"test_{shape_name}",
                shape=shape_name,
                scale=1.0,
                translate_to=None,
                rotate_to=None,
                lock_channels=["s", "v"]
            )

            # Position in grid
            ctrl.C.translateX.set(x_pos)
            ctrl.C.translateZ.set(z_pos)

            # Add text annotation
            annotation = pm.annotate(
                ctrl.C,
                text=shape_name,
                point=(x_pos, 0, z_pos)
            )

            controls[shape_name] = ctrl
            print(f"✓ Created '{shape_name}' control at position ({x_pos}, 0, {z_pos})")

        except Exception as e:
            print(f"✗ FAILED to create '{shape_name}' control: {e}")
            controls[shape_name] = None

    print("\n" + "="*60)
    print(f"Created {len([c for c in controls.values() if c])} / {len(shapes)} shapes successfully")
    print("="*60 + "\n")

    return controls


def test_shape_scaling():
    """Test shape scaling with different scale values."""
    print("\n" + "="*60)
    print("Testing Shape Scaling")
    print("="*60)

    test_shape = "sphere"
    scales = [0.5, 1.0, 2.0]
    spacing = 6.0

    for idx, scale in enumerate(scales):
        try:
            ctrl = Control(
                prefix=f"scale_test_{scale}",
                shape=test_shape,
                scale=scale,
                translate_to=None,
                rotate_to=None,
                lock_channels=["s", "v"]
            )

            # Position horizontally
            ctrl.C.translateX.set(idx * spacing)
            ctrl.C.translateZ.set(-spacing)

            # Add annotation
            pm.annotate(
                ctrl.C,
                text=f"scale={scale}",
                point=(idx * spacing, 0, -spacing)
            )

            print(f"✓ Created '{test_shape}' with scale={scale}")

        except Exception as e:
            print(f"✗ FAILED to create scaled control: {e}")

    print("="*60 + "\n")


def test_shape_direct_functions():
    """Test shape creation using direct function calls."""
    print("\n" + "="*60)
    print("Testing Direct Shape Functions")
    print("="*60)

    from mayaLib.rigLib.utils import ctrl_shape as cs

    direct_shapes = [
        ("sphereCtrlShape", cs.sphereCtrlShape),
        ("moveCtrlShape", cs.moveCtrlShape),
        ("pinCtrlShape", cs.pinCtrlShape),
        ("arrowCtrlShape", cs.arrowCtrlShape),
        ("cubeCtrlShape", cs.cubeCtrlShape),
        ("crossCtrlShape", cs.crossCtrlShape),
        ("squareCtrlShape", cs.squareCtrlShape),
    ]

    spacing = 5.0
    z_offset = spacing * 3

    for idx, (func_name, func) in enumerate(direct_shapes):
        try:
            shape_obj = func(name=f"direct_{func_name}", scale=1.0)
            shape_obj.translateX.set(idx * spacing)
            shape_obj.translateZ.set(z_offset)

            pm.annotate(
                shape_obj,
                text=f"direct_{func_name}",
                point=(idx * spacing, 0, z_offset)
            )

            print(f"✓ Created shape using {func_name}()")

        except Exception as e:
            print(f"✗ FAILED to create shape with {func_name}(): {e}")

    print("="*60 + "\n")


def verify_shape_attributes():
    """Verify that created shapes have expected attributes."""
    print("\n" + "="*60)
    print("Verifying Shape Attributes")
    print("="*60)

    ctrl = Control(
        prefix="attr_test",
        shape="sphere",
        scale=1.5,
        translate_to=None,
        rotate_to=None,
        lock_channels=["s", "v"]
    )

    # Position away from other shapes
    ctrl.C.translateX.set(15)
    ctrl.C.translateZ.set(0)

    checks = [
        ("Control object exists", ctrl.C is not None),
        ("Control has shape node", len(ctrl.C.getShapes()) > 0),
        ("Scale channels locked", ctrl.C.scaleX.isLocked()),
        ("Visibility locked", ctrl.C.visibility.isLocked()),
        ("Translate X unlocked", not ctrl.C.translateX.isLocked()),
    ]

    for check_name, result in checks:
        status = "✓" if result else "✗"
        print(f"{status} {check_name}: {result}")

    print("="*60 + "\n")


def run_full_verification():
    """Run complete manual verification suite."""
    print("\n" + "#"*60)
    print("# MAYA CONTROL SHAPES MANUAL VERIFICATION")
    print("#"*60 + "\n")

    try:
        # Clear scene
        clear_scene()

        # Test 1: Create all control shapes
        controls = create_all_control_shapes()

        # Test 2: Test scaling
        test_shape_scaling()

        # Test 3: Test direct function calls
        test_shape_direct_functions()

        # Test 4: Verify attributes
        verify_shape_attributes()

        # Frame all in viewport
        pm.viewFit(all=True)

        print("\n" + "#"*60)
        print("# VERIFICATION COMPLETE")
        print("#"*60)
        print("\nManual Inspection Required:")
        print("1. Check that all shapes are visually distinct")
        print("2. Verify shapes are properly scaled relative to each other")
        print("3. Confirm no shapes are overlapping (except in grid)")
        print("4. Ensure shape curves are smooth and properly connected")
        print("5. Check that annotations correctly label each shape")
        print("\n" + "#"*60 + "\n")

        return controls

    except Exception as e:
        print(f"\n✗ VERIFICATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        return None


# Entry point
if __name__ == "__main__":
    run_full_verification()

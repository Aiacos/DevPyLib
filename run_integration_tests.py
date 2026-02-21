#!/usr/bin/env python
"""Integration tests for HumanIK refactoring."""

import sys

def test_old_location_imports():
    """Test 1: Import from old location (mayaLib.rigLib.utils.human_ik)."""
    print("\n[Test 1] Import from old location...")
    try:
        from mayaLib.rigLib.utils.human_ik import (
            HumanIK,
            HUMAN_IK_JOINT_MAP,
            HUMAN_IK_CTRL_MAP,
            ARISE_HIK_DATA,
        )
        print("✓ Old import location works")
        print(f"  - HumanIK class: {HumanIK}")
        print(f"  - HUMAN_IK_JOINT_MAP: {len(HUMAN_IK_JOINT_MAP)} entries")
        print(f"  - HUMAN_IK_CTRL_MAP: {len(HUMAN_IK_CTRL_MAP)} entries")
        print(
            f"  - ARISE_HIK_DATA: {'joints' in ARISE_HIK_DATA and 'controls' in ARISE_HIK_DATA}"
        )
        return True
    except Exception as e:
        print(f"✗ FAILED: {e}")
        return False


def test_new_modular_imports():
    """Test 2: Import from new location (mayaLib.rigLib.utils.human_ik submodules)."""
    print("\n[Test 2] Import from new modular structure...")
    try:
        from mayaLib.rigLib.utils.human_ik.constants import (
            HUMAN_IK_JOINT_MAP,
            HUMAN_IK_CTRL_MAP,
        )
        from mayaLib.rigLib.utils.human_ik.rig_templates import (
            ARISE_HIK_DATA,
            ROKOKO_HIK_DATA,
        )
        from mayaLib.rigLib.utils.human_ik.skeleton_mapper import SkeletonMapper
        from mayaLib.rigLib.utils.human_ik.control_mapper import ControlMapper
        from mayaLib.rigLib.utils.human_ik.mel_interface import MelInterface
        from mayaLib.rigLib.utils.human_ik.pose_utils import PoseUtils

        print("✓ New modular imports work")
        print("  - All 6 modules imported successfully")
        print(f"  - SkeletonMapper: {SkeletonMapper}")
        print(f"  - ControlMapper: {ControlMapper}")
        print(f"  - MelInterface: {MelInterface}")
        print(f"  - PoseUtils: {PoseUtils}")
        return True
    except Exception as e:
        print(f"✗ FAILED: {e}")
        return False


def test_humanik_instantiation():
    """Test 3: Instantiate HumanIK class."""
    print("\n[Test 3] HumanIK class instantiation...")
    try:
        from mayaLib.rigLib.utils.human_ik import HumanIK

        h = HumanIK("TestCharacter")
        print("✓ HumanIK instantiation works")
        print(f"  - Instance created: {type(h).__name__}")
        print(f"  - Character name: {h.character_name}")
        print(f"  - Has skeleton_mapper: {hasattr(h, 'skeleton_mapper')}")
        print(f"  - Has control_mapper: {hasattr(h, 'control_mapper')}")
        print(f"  - Has mel_interface: {hasattr(h, 'mel_interface')}")
        print(f"  - Has pose_utils: {hasattr(h, 'pose_utils')}")
        return True
    except Exception as e:
        print(f"✗ FAILED: {e}")
        return False


def test_constants_access():
    """Test 4: Access all constants and maps."""
    print("\n[Test 4] Access all constants and maps...")
    try:
        from mayaLib.rigLib.utils.human_ik import (
            HUMAN_IK_JOINT_MAP,
            HUMAN_IK_CTRL_MAP,
            ARISE_HIK_DATA,
            ROKOKO_HIK_DATA,
            ADVANCED_SKELETON_DATA,
            DEFAULT_REFERENCE,
            DEFAULT_HIP,
            DEFAULT_SPINE,
            DEFAULT_CHEST,
            DEFAULT_NECK,
            DEFAULT_HEAD,
        )

        print("✓ All constants and maps accessible")
        print(f"  - HUMAN_IK_JOINT_MAP: {len(HUMAN_IK_JOINT_MAP)} entries")
        print(f"  - HUMAN_IK_CTRL_MAP: {len(HUMAN_IK_CTRL_MAP)} entries")
        print(f"  - ARISE_HIK_DATA joints: {len(ARISE_HIK_DATA.get('joints', {}))}")
        print(
            f"  - ARISE_HIK_DATA controls: {len(ARISE_HIK_DATA.get('controls', {}))}"
        )
        print(f"  - ROKOKO_HIK_DATA joints: {len(ROKOKO_HIK_DATA.get('joints', {}))}")
        print(
            f"  - ADVANCED_SKELETON_DATA joints: {len(ADVANCED_SKELETON_DATA.get('joints', {}))}"
        )
        print(f"  - DEFAULT_REFERENCE: {DEFAULT_REFERENCE}")
        print(f"  - DEFAULT_HIP: {DEFAULT_HIP}")
        print(f"  - DEFAULT_SPINE: {DEFAULT_SPINE}")
        return True
    except Exception as e:
        print(f"✗ FAILED: {e}")
        return False


def test_ariselib_integration():
    """Test 5: Verify ariseLib still works."""
    print("\n[Test 5] Verify ariseLib integration...")
    try:
        from mayaLib.ariseLib import base

        print("✓ ariseLib import works")
        print(f"  - AriseBase class available: {hasattr(base, 'AriseBase')}")

        # Check that AriseBase has the _setup_human_ik method
        if hasattr(base, "AriseBase"):
            import inspect

            methods = [m for m in dir(base.AriseBase) if not m.startswith("_")]
            print(f"  - AriseBase methods: {len(methods)} public methods")
            has_setup = hasattr(base.AriseBase, "_setup_human_ik")
            print(f"  - Has _setup_human_ik method: {has_setup}")
        return True
    except Exception as e:
        print(f"✗ FAILED: {e}")
        return False


def main():
    """Run all integration tests."""
    print("=" * 70)
    print("HumanIK Refactoring - Integration Test Suite")
    print("=" * 70)

    results = []
    results.append(("Old location imports", test_old_location_imports()))
    results.append(("New modular imports", test_new_modular_imports()))
    results.append(("HumanIK instantiation", test_humanik_instantiation()))
    results.append(("Constants access", test_constants_access()))
    results.append(("ariseLib integration", test_ariselib_integration()))

    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n✓ All integration tests passed!")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())

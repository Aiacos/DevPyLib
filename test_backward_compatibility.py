"""Test backward compatibility of HumanIK imports without Maya."""

import sys

print("=" * 70)
print("BACKWARD COMPATIBILITY VERIFICATION")
print("=" * 70)

# Test 1: Main HumanIK class is importable
print("\n[Test 1] Importing HumanIK class...")
try:
    from mayaLib.rigLib.utils.human_ik import HumanIK
    print("✓ PASS: HumanIK class imported successfully")
except Exception as e:
    print(f"✗ FAIL: {e}")
    sys.exit(1)

# Test 2: Constants are accessible directly
print("\n[Test 2] Importing constants directly...")
try:
    from mayaLib.rigLib.utils.human_ik.constants import HUMAN_IK_JOINT_MAP
    from mayaLib.rigLib.utils.human_ik.constants import HUMAN_IK_CTRL_MAP
    print("✓ PASS: HUMAN_IK_JOINT_MAP imported")
    print("✓ PASS: HUMAN_IK_CTRL_MAP imported")
except Exception as e:
    print(f"✗ FAIL: {e}")
    sys.exit(1)

# Test 3: Constants have expected structure
print("\n[Test 3] Validating constant structure...")
try:
    assert isinstance(HUMAN_IK_JOINT_MAP, dict), "HUMAN_IK_JOINT_MAP should be a dict"
    assert isinstance(HUMAN_IK_CTRL_MAP, dict), "HUMAN_IK_CTRL_MAP should be a dict"
    assert len(HUMAN_IK_JOINT_MAP) > 0, "HUMAN_IK_JOINT_MAP should not be empty"
    print(f"✓ PASS: HUMAN_IK_JOINT_MAP has {len(HUMAN_IK_JOINT_MAP)} entries")
    print(f"✓ PASS: HUMAN_IK_CTRL_MAP has {len(HUMAN_IK_CTRL_MAP)} entries")
except AssertionError as e:
    print(f"✗ FAIL: {e}")
    sys.exit(1)

# Test 4: Rig templates are accessible
print("\n[Test 4] Importing rig templates...")
try:
    from mayaLib.rigLib.utils.human_ik.rig_templates import ARISE_HIK_DATA
    from mayaLib.rigLib.utils.human_ik.rig_templates import ROKOKO_HIK_DATA
    from mayaLib.rigLib.utils.human_ik.rig_templates import ADVANCED_SKELETON_DATA
    print("✓ PASS: ARISE_HIK_DATA imported")
    print("✓ PASS: ROKOKO_HIK_DATA imported")
    print("✓ PASS: ADVANCED_SKELETON_DATA imported")
except Exception as e:
    print(f"✗ FAIL: {e}")
    sys.exit(1)

# Test 5: Rig templates have expected structure
print("\n[Test 5] Validating rig template structure...")
try:
    assert isinstance(ARISE_HIK_DATA, dict), "ARISE_HIK_DATA should be a dict"
    assert 'joints' in ARISE_HIK_DATA, "ARISE_HIK_DATA should have 'joints' key"
    assert 'ctrls' in ARISE_HIK_DATA, "ARISE_HIK_DATA should have 'ctrls' key"
    print("✓ PASS: ARISE_HIK_DATA structure is valid")
    print(f"  - Has {len(ARISE_HIK_DATA.get('joints', {}))} joint mappings")
    print(f"  - Has {len(ARISE_HIK_DATA.get('ctrls', {}))} control mappings")
except AssertionError as e:
    print(f"✗ FAIL: {e}")
    sys.exit(1)

# Test 6: Lazy loading via package __init__
print("\n[Test 6] Testing lazy loading from package...")
try:
    import mayaLib.rigLib.utils.human_ik as hik_pkg
    # Access constants submodule via lazy loading
    constants_module = hik_pkg.constants
    assert constants_module is not None, "constants module should be accessible"
    print("✓ PASS: Lazy loading of constants module works")

    # Access rig_templates submodule via lazy loading
    rig_templates_module = hik_pkg.rig_templates
    assert rig_templates_module is not None, "rig_templates module should be accessible"
    print("✓ PASS: Lazy loading of rig_templates module works")
except Exception as e:
    print(f"✗ FAIL: {e}")
    sys.exit(1)

# Test 7: Verify HumanIK class exists and has correct signature
print("\n[Test 7] Checking HumanIK class signature...")
try:
    import inspect
    sig = inspect.signature(HumanIK.__init__)
    params = list(sig.parameters.keys())

    expected_params = ['self', 'character_name', 'rig_template', 'auto_t_pose',
                       'custom_ctrl_definition', 'use_ik', 'use_hybrid',
                       'skip_reference_joint']

    for param in expected_params:
        assert param in params, f"Expected parameter '{param}' not found"

    print(f"✓ PASS: HumanIK.__init__ has correct signature")
    print(f"  Parameters: {', '.join(params[1:])}")  # Skip 'self'
except Exception as e:
    print(f"✗ FAIL: {e}")
    sys.exit(1)

# Test 8: is_available() function exists
print("\n[Test 8] Testing is_available() function...")
try:
    from mayaLib.rigLib.utils.human_ik import is_available
    print("✓ PASS: is_available() function exists")
    # Note: We can't call it without Maya, but we can verify it exists
except Exception as e:
    print(f"✗ FAIL: {e}")
    sys.exit(1)

# Summary
print("\n" + "=" * 70)
print("ALL TESTS PASSED ✓")
print("=" * 70)
print("\nBackward compatibility verified:")
print("  • HumanIK class can be imported from mayaLib.rigLib.utils.human_ik")
print("  • Constants accessible from human_ik.constants submodule")
print("  • Rig templates accessible from human_ik.rig_templates submodule")
print("  • Lazy loading works correctly")
print("  • API signatures maintained")
print("\nOK")

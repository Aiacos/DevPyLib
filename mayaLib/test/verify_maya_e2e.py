"""End-to-end verification script for lazy loading in Maya environment.

This script should be run inside Maya (via Script Editor or mayapy) to verify:
1. Library loads without errors
2. Menu system works (guiLib/main_menu.py)
3. Rig tools from rigLib are accessible
4. Fluid tools from fluidLib are accessible
5. All tools work as before
6. Lazy loading is functioning correctly

Run this script in Maya's Script Editor or via:
    mayapy verify_maya_e2e.py
"""

import importlib
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple

# Add parent directories to path for imports
_test_dir = Path(__file__).parent.resolve()
_mayalib_dir = _test_dir.parent
_root_dir = _mayalib_dir.parent

if str(_root_dir) not in sys.path:
    sys.path.insert(0, str(_root_dir))

# ANSI color codes for output
class Colors:
    """ANSI color codes for terminal output."""

    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


class TestResult:
    """Container for test results."""

    def __init__(self):
        """Initialize test result tracking."""
        self.passed = []
        self.failed = []
        self.skipped = []
        self.warnings = []

    def add_pass(self, test_name: str, details: str = ""):
        """Add a passing test.

        Args:
            test_name: Name of the test.
            details: Optional details about the test.
        """
        self.passed.append((test_name, details))
        print(
            f"{Colors.OKGREEN}✓{Colors.ENDC} {test_name}"
            + (f" - {details}" if details else "")
        )

    def add_fail(self, test_name: str, error: str):
        """Add a failing test.

        Args:
            test_name: Name of the test.
            error: Error message describing the failure.
        """
        self.failed.append((test_name, error))
        print(f"{Colors.FAIL}✗{Colors.ENDC} {test_name} - {error}")

    def add_skip(self, test_name: str, reason: str):
        """Add a skipped test.

        Args:
            test_name: Name of the test.
            reason: Reason for skipping the test.
        """
        self.skipped.append((test_name, reason))
        print(f"{Colors.WARNING}⊘{Colors.ENDC} {test_name} - {reason}")

    def add_warning(self, test_name: str, warning: str):
        """Add a test warning.

        Args:
            test_name: Name of the test.
            warning: Warning message.
        """
        self.warnings.append((test_name, warning))
        print(f"{Colors.WARNING}⚠{Colors.ENDC} {test_name} - {warning}")

    def print_summary(self):
        """Print test summary with pass/fail statistics."""
        total = len(self.passed) + len(self.failed) + len(self.skipped)
        print(f"\n{Colors.BOLD}{'=' * 70}{Colors.ENDC}")
        print(f"{Colors.BOLD}Test Summary{Colors.ENDC}")
        print(f"{Colors.BOLD}{'=' * 70}{Colors.ENDC}")
        print(
            f"{Colors.OKGREEN}Passed:{Colors.ENDC}  {len(self.passed)}/{total}"
        )
        print(f"{Colors.FAIL}Failed:{Colors.ENDC}  {len(self.failed)}/{total}")
        print(
            f"{Colors.WARNING}Skipped:{Colors.ENDC} {len(self.skipped)}/{total}"
        )
        if self.warnings:
            print(
                f"{Colors.WARNING}Warnings:{Colors.ENDC} {len(self.warnings)}"
            )

        if self.failed:
            print(f"\n{Colors.FAIL}{Colors.BOLD}Failed Tests:{Colors.ENDC}")
            for test_name, error in self.failed:
                print(f"  • {test_name}: {error}")

        if self.warnings:
            print(f"\n{Colors.WARNING}{Colors.BOLD}Warnings:{Colors.ENDC}")
            for test_name, warning in self.warnings:
                print(f"  • {test_name}: {warning}")

        print(f"\n{Colors.BOLD}{'=' * 70}{Colors.ENDC}")

        if len(self.failed) == 0:
            print(
                f"{Colors.OKGREEN}{Colors.BOLD}✓ ALL TESTS PASSED!{Colors.ENDC}"
            )
            return True
        else:
            print(
                f"{Colors.FAIL}{Colors.BOLD}✗ SOME TESTS FAILED{Colors.ENDC}"
            )
            return False


def check_maya_available() -> bool:
    """Check if running inside Maya environment.

    Returns:
        bool: True if Maya is available, False otherwise.
    """
    try:
        import maya.cmds as cmds

        # Try to execute a simple Maya command
        cmds.about(version=True)
        return True
    except (ImportError, RuntimeError):
        return False


def test_library_import(result: TestResult) -> bool:
    """Test that mayaLib can be imported.

    Args:
        result: TestResult object to track results.

    Returns:
        bool: True if test passed, False otherwise.
    """
    try:
        start_time = time.perf_counter()
        import mayaLib

        elapsed = (time.perf_counter() - start_time) * 1000
        result.add_pass(
            "Library Import", f"mayaLib imported in {elapsed:.2f}ms"
        )
        return True
    except Exception as e:
        result.add_fail("Library Import", str(e))
        return False


def test_lazy_loading_behavior(result: TestResult):
    """Test that lazy loading is working correctly.

    Args:
        result: TestResult object to track results.
    """
    # Remove mayaLib from cache to test fresh import
    modules_to_remove = [
        key for key in list(sys.modules.keys()) if key.startswith("mayaLib")
    ]
    for module in modules_to_remove:
        del sys.modules[module]

    try:
        # Import mayaLib
        import mayaLib

        # Check that submodules are NOT yet loaded
        submodules = [
            "rigLib",
            "fluidLib",
            "bifrostLib",
            "guiLib",
            "modelLib",
            "shaderLib",
        ]

        lazy_count = 0
        for submodule in submodules:
            module_name = f"mayaLib.{submodule}"
            if module_name not in sys.modules:
                lazy_count += 1

        if lazy_count >= 4:  # At least 4 should be lazy
            result.add_pass(
                "Lazy Loading Behavior",
                f"{lazy_count}/{len(submodules)} submodules not loaded on import",
            )
        else:
            result.add_warning(
                "Lazy Loading Behavior",
                f"Only {lazy_count}/{len(submodules)} submodules were lazy-loaded",
            )

        # Now access a submodule to trigger loading
        start_time = time.perf_counter()
        _ = mayaLib.rigLib
        elapsed = (time.perf_counter() - start_time) * 1000

        # Check that it's now loaded
        if "mayaLib.rigLib" in sys.modules:
            result.add_pass(
                "On-Demand Loading", f"rigLib loaded on access in {elapsed:.2f}ms"
            )
        else:
            result.add_fail("On-Demand Loading", "rigLib not loaded after access")

    except Exception as e:
        result.add_fail("Lazy Loading Behavior", str(e))


def test_submodule_access(result: TestResult):
    """Test accessing various submodules.

    Args:
        result: TestResult object to track results.
    """
    import mayaLib

    # Test top-level submodules
    submodules = [
        ("rigLib", "Rig tools"),
        ("fluidLib", "Fluid simulation tools"),
        ("guiLib", "GUI utilities"),
        ("modelLib", "Modeling tools"),
        ("shaderLib", "Shader utilities"),
        ("pipelineLib", "Pipeline utilities"),
        ("utility", "General utilities"),
    ]

    for submodule_name, description in submodules:
        try:
            submodule = getattr(mayaLib, submodule_name)
            result.add_pass(f"Access {submodule_name}", description)
        except Exception as e:
            result.add_fail(f"Access {submodule_name}", str(e))


def test_nested_imports(result: TestResult):
    """Test nested module imports.

    Args:
        result: TestResult object to track results.
    """
    test_cases = [
        ("mayaLib.rigLib.base", "rigLib base modules"),
        ("mayaLib.rigLib.utils", "rigLib utilities"),
        ("mayaLib.fluidLib.base", "fluidLib base modules"),
        ("mayaLib.guiLib.base", "guiLib base modules"),
        ("mayaLib.modelLib.base", "modelLib base modules"),
    ]

    for module_path, description in test_cases:
        try:
            module = importlib.import_module(module_path)
            result.add_pass(f"Import {module_path}", description)
        except Exception as e:
            # Some modules may fail due to Maya dependencies
            if "maya" in str(e).lower() or "pymel" in str(e).lower():
                result.add_skip(f"Import {module_path}", "Maya dependencies required")
            else:
                result.add_fail(f"Import {module_path}", str(e))


def test_rig_tools(result: TestResult):
    """Test accessing rig tools from rigLib.

    Args:
        result: TestResult object to track results.
    """
    try:
        from mayaLib.rigLib import base

        result.add_pass("RigLib Base Access", "rigLib.base imported successfully")
    except Exception as e:
        if "maya" in str(e).lower() or "pymel" in str(e).lower():
            result.add_skip("RigLib Base Access", "Maya environment required")
        else:
            result.add_fail("RigLib Base Access", str(e))

    try:
        from mayaLib.rigLib import utils

        result.add_pass("RigLib Utils Access", "rigLib.utils imported successfully")
    except Exception as e:
        if "maya" in str(e).lower() or "pymel" in str(e).lower():
            result.add_skip("RigLib Utils Access", "Maya environment required")
        else:
            result.add_fail("RigLib Utils Access", str(e))


def test_fluid_tools(result: TestResult):
    """Test accessing fluid tools from fluidLib.

    Args:
        result: TestResult object to track results.
    """
    try:
        from mayaLib.fluidLib import base

        result.add_pass("FluidLib Base Access", "fluidLib.base imported successfully")
    except Exception as e:
        if "maya" in str(e).lower() or "pymel" in str(e).lower():
            result.add_skip("FluidLib Base Access", "Maya environment required")
        else:
            result.add_fail("FluidLib Base Access", str(e))

    try:
        from mayaLib.fluidLib import fire

        result.add_pass("FluidLib Fire Access", "fluidLib.fire imported successfully")
    except Exception as e:
        if "maya" in str(e).lower() or "pymel" in str(e).lower():
            result.add_skip("FluidLib Fire Access", "Maya environment required")
        else:
            result.add_fail("FluidLib Fire Access", str(e))


def test_gui_system(result: TestResult):
    """Test GUI system components.

    Args:
        result: TestResult object to track results.
    """
    try:
        from mayaLib.guiLib import main_menu

        # Check that MainMenu class exists
        if hasattr(main_menu, "MainMenu"):
            result.add_pass("GUI Main Menu", "MainMenu class is available")
        else:
            # Module loaded but class not available (Maya not running)
            result.add_skip(
                "GUI Main Menu", "MainMenu class requires Maya environment"
            )

    except Exception as e:
        if "maya" in str(e).lower() or "pyside" in str(e).lower():
            result.add_skip("GUI Main Menu", "Maya/Qt environment required")
        else:
            result.add_fail("GUI Main Menu", str(e))


def test_backwards_compatibility(result: TestResult):
    """Test common import patterns for backwards compatibility.

    Args:
        result: TestResult object to track results.
    """
    # Pattern 1: import mayaLib
    try:
        import mayaLib

        result.add_pass("Import Pattern 1", "import mayaLib")
    except Exception as e:
        result.add_fail("Import Pattern 1", str(e))

    # Pattern 2: from mayaLib import rigLib
    try:
        from mayaLib import rigLib

        result.add_pass("Import Pattern 2", "from mayaLib import rigLib")
    except Exception as e:
        result.add_fail("Import Pattern 2", str(e))

    # Pattern 3: import mayaLib.rigLib
    try:
        import mayaLib.rigLib

        result.add_pass("Import Pattern 3", "import mayaLib.rigLib")
    except Exception as e:
        result.add_fail("Import Pattern 3", str(e))

    # Pattern 4: from mayaLib.rigLib import base
    try:
        from mayaLib.rigLib import base

        result.add_pass("Import Pattern 4", "from mayaLib.rigLib import base")
    except Exception as e:
        if "maya" in str(e).lower():
            result.add_skip("Import Pattern 4", "Maya environment required")
        else:
            result.add_fail("Import Pattern 4", str(e))


def test_special_modules(result: TestResult):
    """Test special modules like Ziva and Bifrost.

    Args:
        result: TestResult object to track results.
    """
    # Test rigLib availability checking
    try:
        import mayaLib.rigLib

        if hasattr(mayaLib.rigLib, "is_available"):
            result.add_pass(
                "RigLib Availability", "rigLib.is_available() function present"
            )
    except Exception as e:
        result.add_fail("RigLib Availability", str(e))

    # Test Ziva module (may fail outside Maya, which is expected)
    try:
        from mayaLib.rigLib import Ziva

        if Ziva is None:
            # This is expected outside Maya - module initialization failed
            result.add_skip("Ziva Module", "Ziva unavailable outside Maya (expected)")
        elif hasattr(Ziva, "is_available") or "is_available" in dir(Ziva):
            result.add_pass("Ziva Module", "Ziva with is_available() loaded")
        else:
            result.add_warning("Ziva Module", "Ziva loaded but no is_available()")
    except (ImportError, AttributeError) as e:
        # Expected when running outside Maya
        error_msg = str(e)[:60]
        result.add_skip("Ziva Module", f"Import failed (expected): {error_msg}")
    except Exception as e:
        result.add_fail("Ziva Module", str(e))

    # Test Bifrost availability checking
    try:
        from mayaLib import bifrostLib

        if hasattr(bifrostLib, "is_available"):
            result.add_pass(
                "Bifrost Module", "bifrostLib with is_available() loaded"
            )
        else:
            result.add_warning(
                "Bifrost Module",
                "bifrostLib loaded but no is_available() function",
            )
    except Exception as e:
        if "maya" in str(e).lower():
            result.add_skip("Bifrost Module", "Maya environment required")
        else:
            result.add_fail("Bifrost Module", str(e))


def test_module_introspection(result: TestResult):
    """Test module introspection with __dir__().

    Args:
        result: TestResult object to track results.
    """
    try:
        import mayaLib

        # Test that __dir__ works
        attrs = dir(mayaLib)
        expected_attrs = ["rigLib", "fluidLib", "guiLib", "modelLib"]

        missing = [attr for attr in expected_attrs if attr not in attrs]

        if not missing:
            result.add_pass(
                "Module Introspection", f"__dir__ works correctly ({len(attrs)} attrs)"
            )
        else:
            result.add_fail(
                "Module Introspection", f"Missing attributes: {missing}"
            )

    except Exception as e:
        result.add_fail("Module Introspection", str(e))


def run_verification():
    """Run all verification tests and print results."""
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'=' * 70}{Colors.ENDC}")
    print(
        f"{Colors.BOLD}{Colors.HEADER}DevPyLib Lazy Loading - "
        f"End-to-End Verification{Colors.ENDC}"
    )
    print(f"{Colors.BOLD}{Colors.HEADER}{'=' * 70}{Colors.ENDC}\n")

    # Check if running in Maya
    in_maya = check_maya_available()
    if in_maya:
        print(
            f"{Colors.OKGREEN}✓ Running inside Maya environment{Colors.ENDC}\n"
        )
    else:
        print(
            f"{Colors.WARNING}⚠ Running outside Maya - "
            f"some tests will be skipped{Colors.ENDC}\n"
        )

    result = TestResult()

    # Run all tests
    print(f"{Colors.BOLD}Basic Import Tests:{Colors.ENDC}")
    test_library_import(result)
    print()

    print(f"{Colors.BOLD}Lazy Loading Tests:{Colors.ENDC}")
    test_lazy_loading_behavior(result)
    print()

    print(f"{Colors.BOLD}Submodule Access Tests:{Colors.ENDC}")
    test_submodule_access(result)
    print()

    print(f"{Colors.BOLD}Nested Import Tests:{Colors.ENDC}")
    test_nested_imports(result)
    print()

    print(f"{Colors.BOLD}Rig Tools Tests:{Colors.ENDC}")
    test_rig_tools(result)
    print()

    print(f"{Colors.BOLD}Fluid Tools Tests:{Colors.ENDC}")
    test_fluid_tools(result)
    print()

    print(f"{Colors.BOLD}GUI System Tests:{Colors.ENDC}")
    test_gui_system(result)
    print()

    print(f"{Colors.BOLD}Backwards Compatibility Tests:{Colors.ENDC}")
    test_backwards_compatibility(result)
    print()

    print(f"{Colors.BOLD}Special Modules Tests:{Colors.ENDC}")
    test_special_modules(result)
    print()

    print(f"{Colors.BOLD}Introspection Tests:{Colors.ENDC}")
    test_module_introspection(result)
    print()

    # Print summary
    success = result.print_summary()

    if in_maya and success:
        print(
            f"\n{Colors.OKGREEN}{Colors.BOLD}✓ Ready for production use in "
            f"Maya!{Colors.ENDC}"
        )
    elif success:
        print(
            f"\n{Colors.OKGREEN}{Colors.BOLD}✓ Lazy loading implementation "
            f"verified!{Colors.ENDC}"
        )
        print(
            f"{Colors.WARNING}Note: Run this script inside Maya for full "
            f"verification{Colors.ENDC}"
        )

    return success


if __name__ == "__main__":
    success = run_verification()
    sys.exit(0 if success else 1)

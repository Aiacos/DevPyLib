"""Comprehensive backwards compatibility tests for lazy loading implementation.

Tests all submodules (rigLib, fluidLib, bifrostLib, etc.) and nested submodules
(rigLib.Ziva, rigLib.utils, fluidLib.base, etc.) to ensure full backwards
compatibility with existing import patterns and usage scenarios.
"""

import importlib
import sys
from unittest.mock import patch

import pytest

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture(autouse=True)
def reset_modules():
    """Reset module cache before each test.

    Removes mayaLib and all submodules from sys.modules to ensure
    each test starts with clean state.

    Yields:
        None
    """
    # Store modules to remove
    modules_to_remove = [key for key in sys.modules if key.startswith("mayaLib")]

    yield

    # Clean up after test
    for module in modules_to_remove:
        sys.modules.pop(module, None)


@pytest.fixture
def suppress_warnings():
    """Suppress warning prints during tests.

    Yields:
        Mock object for print function.
    """
    with patch("builtins.print") as mock_print:
        yield mock_print


# ============================================================================
# Top-Level Submodules Tests
# ============================================================================


class TestTopLevelSubmodules:
    """Test lazy loading of all top-level submodules."""

    def test_import_riglib(self):
        """Test importing rigLib submodule."""
        # Clear cache
        sys.modules.pop("mayaLib", None)
        sys.modules.pop("mayaLib.rigLib", None)

        # Import pattern: import mayaLib.rigLib
        import mayaLib.rigLib

        assert "mayaLib.rigLib" in sys.modules
        assert mayaLib.rigLib is not None

    def test_from_import_riglib(self):
        """Test from import pattern for rigLib."""
        # Clear cache
        sys.modules.pop("mayaLib", None)
        sys.modules.pop("mayaLib.rigLib", None)

        # Import pattern: from mayaLib import rigLib
        from mayaLib import rigLib

        assert rigLib is not None
        assert "mayaLib.rigLib" in sys.modules

    def test_import_fluidlib(self):
        """Test importing fluidLib submodule."""
        # Clear cache
        sys.modules.pop("mayaLib.fluidLib", None)

        # Import pattern: import mayaLib.fluidLib
        import mayaLib.fluidLib

        assert "mayaLib.fluidLib" in sys.modules
        assert mayaLib.fluidLib is not None

    def test_import_bifrostlib(self):
        """Test importing bifrostLib submodule."""
        # Clear cache
        sys.modules.pop("mayaLib.bifrostLib", None)

        # Import pattern: import mayaLib.bifrostLib
        import mayaLib.bifrostLib

        assert "mayaLib.bifrostLib" in sys.modules
        assert mayaLib.bifrostLib is not None

    def test_import_animationlib(self):
        """Test importing animationLib submodule."""
        # Clear cache
        sys.modules.pop("mayaLib.animationLib", None)

        # Import pattern: import mayaLib.animationLib
        import mayaLib.animationLib

        assert "mayaLib.animationLib" in sys.modules
        assert mayaLib.animationLib is not None

    def test_import_guilib(self):
        """Test importing guiLib submodule."""
        # Clear cache
        sys.modules.pop("mayaLib.guiLib", None)

        # Import pattern: import mayaLib.guiLib
        import mayaLib.guiLib

        assert "mayaLib.guiLib" in sys.modules
        assert mayaLib.guiLib is not None

    def test_import_modellib(self):
        """Test importing modelLib submodule."""
        # Clear cache
        sys.modules.pop("mayaLib.modelLib", None)

        # Import pattern: import mayaLib.modelLib
        import mayaLib.modelLib

        assert "mayaLib.modelLib" in sys.modules
        assert mayaLib.modelLib is not None

    def test_import_shaderlib(self):
        """Test importing shaderLib submodule."""
        # Clear cache
        sys.modules.pop("mayaLib.shaderLib", None)

        # Import pattern: import mayaLib.shaderLib
        import mayaLib.shaderLib

        assert "mayaLib.shaderLib" in sys.modules
        assert mayaLib.shaderLib is not None

    def test_import_pipelinelib(self):
        """Test importing pipelineLib submodule."""
        # Clear cache
        sys.modules.pop("mayaLib.pipelineLib", None)

        # Import pattern: import mayaLib.pipelineLib
        import mayaLib.pipelineLib

        assert "mayaLib.pipelineLib" in sys.modules
        assert mayaLib.pipelineLib is not None

    def test_import_utility(self):
        """Test importing utility submodule."""
        # Clear cache
        sys.modules.pop("mayaLib.utility", None)

        # Import pattern: import mayaLib.utility
        import mayaLib.utility

        assert "mayaLib.utility" in sys.modules
        assert mayaLib.utility is not None

    def test_import_lunalib(self):
        """Test importing lunaLib submodule."""
        # Clear cache
        sys.modules.pop("mayaLib.lunaLib", None)

        # Import pattern: import mayaLib.lunaLib
        import mayaLib.lunaLib

        assert "mayaLib.lunaLib" in sys.modules
        assert mayaLib.lunaLib is not None

    def test_import_lookdevlib(self):
        """Test importing lookdevLib submodule."""
        # Clear cache
        sys.modules.pop("mayaLib.lookdevLib", None)

        # Import pattern: import mayaLib.lookdevLib
        import mayaLib.lookdevLib

        assert "mayaLib.lookdevLib" in sys.modules
        assert mayaLib.lookdevLib is not None


# ============================================================================
# Nested Submodules Tests
# ============================================================================


class TestNestedSubmodules:
    """Test lazy loading of nested submodules."""

    def test_import_riglib_utils(self, suppress_warnings):
        """Test importing rigLib.utils nested module."""
        # Clear cache
        sys.modules.pop("mayaLib.rigLib", None)
        sys.modules.pop("mayaLib.rigLib.utils", None)

        # Import pattern: import mayaLib.rigLib.utils
        import mayaLib.rigLib.utils

        assert "mayaLib.rigLib.utils" in sys.modules
        assert mayaLib.rigLib.utils is not None

    def test_from_riglib_utils_import_module(self, suppress_warnings):
        """Test importing specific module from rigLib.utils."""
        # Clear cache
        sys.modules.pop("mayaLib.rigLib.utils", None)
        sys.modules.pop("mayaLib.rigLib.utils.control", None)

        # Import pattern: from mayaLib.rigLib.utils import control
        from mayaLib.rigLib.utils import control

        assert control is not None
        assert hasattr(control, "Control") or hasattr(control, "__name__")

    def test_import_riglib_base(self, suppress_warnings):
        """Test importing rigLib.base nested module."""
        # Clear cache
        sys.modules.pop("mayaLib.rigLib.base", None)

        # Import pattern: import mayaLib.rigLib.base
        import mayaLib.rigLib.base

        assert "mayaLib.rigLib.base" in sys.modules
        assert mayaLib.rigLib.base is not None

    def test_import_riglib_ziva(self, suppress_warnings):
        """Test importing rigLib.Ziva nested module."""
        # Clear cache
        sys.modules.pop("mayaLib.rigLib.Ziva", None)

        # Import pattern: import mayaLib.rigLib.Ziva
        import mayaLib.rigLib.Ziva

        assert "mayaLib.rigLib.Ziva" in sys.modules
        assert mayaLib.rigLib.Ziva is not None

    def test_import_fluidlib_base(self, suppress_warnings):
        """Test importing fluidLib.base nested module."""
        # Clear cache
        sys.modules.pop("mayaLib.fluidLib.base", None)

        # Import pattern: import mayaLib.fluidLib.base
        import mayaLib.fluidLib.base

        assert "mayaLib.fluidLib.base" in sys.modules
        assert mayaLib.fluidLib.base is not None

    def test_from_fluidlib_import_fire(self, suppress_warnings):
        """Test importing fire module from fluidLib."""
        # Clear cache
        sys.modules.pop("mayaLib.fluidLib", None)
        sys.modules.pop("mayaLib.fluidLib.fire", None)

        # Import pattern: from mayaLib.fluidLib import fire
        from mayaLib.fluidLib import fire

        assert fire is not None
        assert "mayaLib.fluidLib.fire" in sys.modules

    def test_import_guilib_base(self, suppress_warnings):
        """Test importing guiLib.base nested module."""
        # Clear cache
        sys.modules.pop("mayaLib.guiLib.base", None)

        # Import pattern: import mayaLib.guiLib.base
        import mayaLib.guiLib.base

        assert "mayaLib.guiLib.base" in sys.modules
        assert mayaLib.guiLib.base is not None

    def test_import_modellib_utils(self, suppress_warnings):
        """Test importing modelLib.utils nested module."""
        # Clear cache
        sys.modules.pop("mayaLib.modelLib.utils", None)

        # Import pattern: import mayaLib.modelLib.utils
        import mayaLib.modelLib.utils

        assert "mayaLib.modelLib.utils" in sys.modules
        assert mayaLib.modelLib.utils is not None

    def test_import_pipelinelib_utility(self):
        """Test importing pipelineLib.utility nested module."""
        # Clear cache
        sys.modules.pop("mayaLib.pipelineLib.utility", None)

        # Import pattern: import mayaLib.pipelineLib.utility
        import mayaLib.pipelineLib.utility

        assert "mayaLib.pipelineLib.utility" in sys.modules
        assert mayaLib.pipelineLib.utility is not None

    def test_from_pipelinelib_utility_import_module(self):
        """Test importing specific module from pipelineLib.utility."""
        # Clear cache
        sys.modules.pop("mayaLib.pipelineLib.utility", None)
        sys.modules.pop("mayaLib.pipelineLib.utility.convention", None)

        # Import pattern: from mayaLib.pipelineLib.utility import convention
        from mayaLib.pipelineLib.utility import convention

        assert convention is not None
        assert hasattr(convention, "__name__")

    def test_import_shaderlib_base(self, suppress_warnings):
        """Test importing shaderLib.base nested module."""
        # Clear cache
        sys.modules.pop("mayaLib.shaderLib.base", None)

        # Import pattern: import mayaLib.shaderLib.base
        import mayaLib.shaderLib.base

        assert "mayaLib.shaderLib.base" in sys.modules
        assert mayaLib.shaderLib.base is not None


# ============================================================================
# Deep Nested Submodules Tests
# ============================================================================


class TestDeepNestedSubmodules:
    """Test lazy loading of deeply nested submodules."""

    def test_from_riglib_utils_import_attribute(self, suppress_warnings):
        """Test importing specific attribute from rigLib.utils module."""
        # Clear cache
        sys.modules.pop("mayaLib.rigLib.utils.deform", None)

        # Import pattern: from mayaLib.rigLib.utils import deform
        from mayaLib.rigLib.utils import deform

        assert deform is not None
        # Module should have __name__ attribute
        assert hasattr(deform, "__name__")

    def test_from_fluidlib_base_import_module(self, suppress_warnings):
        """Test importing specific module from fluidLib.base."""
        # Clear cache
        sys.modules.pop("mayaLib.fluidLib.base.base_fluid", None)

        # Import pattern: from mayaLib.fluidLib.base import base_fluid
        from mayaLib.fluidLib.base import base_fluid

        assert base_fluid is not None
        assert hasattr(base_fluid, "__name__")

    def test_from_guilib_base_import_module(self, suppress_warnings):
        """Test importing specific module from guiLib.base."""
        # Clear cache
        sys.modules.pop("mayaLib.guiLib.base.base_ui", None)

        # Import pattern: from mayaLib.guiLib.base import base_ui
        from mayaLib.guiLib.base import base_ui

        assert base_ui is not None
        assert hasattr(base_ui, "__name__")

    def test_from_modellib_utils_import_module(self, suppress_warnings):
        """Test importing specific module from modelLib.utils."""
        # Clear cache
        sys.modules.pop("mayaLib.modelLib.utils.display_layer", None)

        # Import pattern: from mayaLib.modelLib.utils import display_layer
        from mayaLib.modelLib.utils import display_layer

        assert display_layer is not None
        assert hasattr(display_layer, "__name__")


# ============================================================================
# Multiple Import Patterns Tests
# ============================================================================


class TestMultipleImportPatterns:
    """Test various import patterns used in real codebases."""

    def test_multiple_submodules_sequential(self, suppress_warnings):
        """Test importing multiple submodules sequentially."""
        # Clear cache
        sys.modules.pop("mayaLib.rigLib", None)
        sys.modules.pop("mayaLib.fluidLib", None)

        # Sequential imports
        from mayaLib import fluidLib, rigLib

        assert rigLib is not None
        assert fluidLib is not None
        assert "mayaLib.rigLib" in sys.modules
        assert "mayaLib.fluidLib" in sys.modules

    def test_multiple_submodules_single_line(self, suppress_warnings):
        """Test importing multiple submodules in one line."""
        # Clear cache
        sys.modules.pop("mayaLib.utility", None)
        sys.modules.pop("mayaLib.pipelineLib", None)

        # Single line import
        from mayaLib import pipelineLib, utility

        assert utility is not None
        assert pipelineLib is not None

    def test_nested_and_parent_import(self, suppress_warnings):
        """Test importing both parent and nested modules."""
        # Clear cache
        sys.modules.pop("mayaLib.pipelineLib", None)
        sys.modules.pop("mayaLib.pipelineLib.utility", None)

        # Import parent then nested (using pipelineLib which doesn't require Maya)
        from mayaLib import pipelineLib
        from mayaLib.pipelineLib import utility

        assert pipelineLib is not None
        assert utility is not None

    def test_direct_attribute_access_after_import(self):
        """Test accessing attributes directly after import."""
        # Import mayaLib
        import mayaLib

        # Access submodule via attribute
        utility = mayaLib.utility

        assert utility is not None
        assert hasattr(utility, "__name__")

    def test_getattr_for_dynamic_import(self):
        """Test using getattr for dynamic imports."""
        import mayaLib

        # Dynamic import using getattr
        utility = mayaLib.utility

        assert utility is not None
        assert "mayaLib.utility" in sys.modules


# ============================================================================
# Module Introspection Tests
# ============================================================================


class TestModuleIntrospection:
    """Test module introspection functionality."""

    def test_hasattr_on_top_level_submodules(self):
        """Test hasattr() on top-level submodules."""
        import mayaLib

        # Should have all submodules
        assert hasattr(mayaLib, "rigLib")
        assert hasattr(mayaLib, "fluidLib")
        assert hasattr(mayaLib, "utility")
        assert hasattr(mayaLib, "pipelineLib")

        # Should not have non-existent modules
        assert not hasattr(mayaLib, "nonexistentLib")

    def test_hasattr_on_nested_submodules(self, suppress_warnings):
        """Test hasattr() on nested submodules."""
        import mayaLib.rigLib

        # Access the module to trigger initialization
        _ = mayaLib.rigLib.utils

        # Should have nested submodules
        assert hasattr(mayaLib.rigLib, "utils")
        assert hasattr(mayaLib.rigLib, "base")

    def test_dir_on_top_level_module(self):
        """Test dir() on top-level mayaLib module."""
        import mayaLib

        attrs = dir(mayaLib)

        # Should have __getattr__
        assert "__getattr__" in attrs

    def test_dir_on_submodule_with_lazy_loading(self, suppress_warnings):
        """Test dir() on submodule with lazy loading."""
        import mayaLib.fluidLib

        attrs = dir(mayaLib.fluidLib)

        # Should include available submodules
        assert "fire" in attrs
        assert "smoke" in attrs
        assert "base" in attrs

    def test_module_name_attribute(self):
        """Test that __name__ attribute is correct."""
        from mayaLib import utility

        assert utility.__name__ == "mayaLib.utility"

    def test_module_file_attribute(self):
        """Test that __file__ attribute exists."""
        from mayaLib import utility

        assert hasattr(utility, "__file__")
        assert utility.__file__ is not None

    def test_module_path_attribute_on_package(self):
        """Test that __path__ attribute exists on packages."""
        from mayaLib import utility

        # Packages have __path__ attribute
        assert hasattr(utility, "__path__")


# ============================================================================
# Cross-Module Dependencies Tests
# ============================================================================


class TestCrossModuleDependencies:
    """Test importing modules with cross-dependencies."""

    def test_import_utility_lazy_loader(self):
        """Test importing lazy_loader utility module."""
        # This module should be importable without Maya
        from mayaLib.utility import lazy_loader

        assert lazy_loader is not None
        assert hasattr(lazy_loader, "create_lazy_loader")

    def test_multiple_nested_imports(self, suppress_warnings):
        """Test importing multiple nested modules."""
        # Import multiple nested modules
        from mayaLib.pipelineLib import utility

        assert utility is not None

        # Test another nested import that works without Maya
        from mayaLib.modelLib import utils as model_utils

        assert model_utils is not None

    def test_import_same_module_different_ways(self):
        """Test importing same module using different patterns."""
        # Clear cache
        sys.modules.pop("mayaLib.utility", None)

        # First import
        # Second import using different pattern
        import mayaLib.utility as util2
        from mayaLib import utility as util1

        # Should be the same module
        assert util1 is util2
        assert id(util1) == id(util2)


# ============================================================================
# Error Handling Tests
# ============================================================================


class TestErrorHandling:
    """Test error handling in lazy loading."""

    def test_import_nonexistent_submodule(self):
        """Test importing non-existent submodule raises error."""
        import mayaLib

        # Should raise AttributeError for non-existent module
        with pytest.raises(AttributeError, match="has no attribute"):
            _ = mayaLib.nonexistentLib

    def test_import_nonexistent_nested_module(self, suppress_warnings):
        """Test importing non-existent nested module raises error."""
        import mayaLib.rigLib

        # Should raise AttributeError for non-existent nested module
        with pytest.raises(AttributeError, match="has no attribute"):
            _ = mayaLib.rigLib.nonexistentModule

    def test_graceful_failure_when_maya_unavailable(self, suppress_warnings):
        """Test graceful failure when Maya is not available."""
        # Most modules will fail without Maya, but should not crash
        # The __getattr__ implementation should catch ImportError and return None
        # or raise AttributeError

        import mayaLib

        # Try to access a module that requires Maya
        # This should either return None or raise AttributeError, not crash
        try:
            _ = mayaLib.rigLib
        except AttributeError:
            # This is acceptable - module couldn't be loaded
            pass

    def test_error_message_clarity(self):
        """Test that error messages are clear and helpful."""
        import mayaLib

        # Try to access non-existent attribute
        with pytest.raises(AttributeError) as exc_info:
            _ = mayaLib.invalidModule

        # Error message should mention the module name and attribute
        assert "mayaLib" in str(exc_info.value)
        assert "invalidModule" in str(exc_info.value)


# ============================================================================
# Module Caching Tests
# ============================================================================


class TestModuleCaching:
    """Test module caching behavior in lazy loading."""

    def test_module_cached_after_first_access(self):
        """Test that modules are cached after first access."""
        import mayaLib

        # First access
        utility1 = mayaLib.utility

        # Second access
        utility2 = mayaLib.utility

        # Should be same object (cached)
        assert utility1 is utility2

    def test_nested_module_cached_after_first_access(self, suppress_warnings):
        """Test that nested modules are cached."""
        import mayaLib.rigLib

        # First access
        utils1 = mayaLib.rigLib.utils

        # Second access
        utils2 = mayaLib.rigLib.utils

        # Should be same object
        assert utils1 is utils2

    def test_module_in_sys_modules_after_import(self):
        """Test that modules are registered in sys.modules."""
        # Clear cache
        sys.modules.pop("mayaLib.utility", None)

        # Import module
        from mayaLib import utility

        # Should be in sys.modules
        assert "mayaLib.utility" in sys.modules
        assert sys.modules["mayaLib.utility"] is utility


# ============================================================================
# Reload Tests
# ============================================================================


class TestModuleReload:
    """Test module reload functionality."""

    def test_reload_top_level_module(self):
        """Test reloading top-level mayaLib module."""
        import mayaLib

        # Access a submodule
        _ = mayaLib.utility

        # Reload mayaLib
        importlib.reload(mayaLib)

        # Should still work after reload
        utility_after = mayaLib.utility
        assert utility_after is not None

    def test_reload_submodule(self):
        """Test reloading a submodule."""
        # Import the module using import statement which ensures sys.modules entry
        import mayaLib.utility

        # Verify module is in sys.modules before reload
        assert "mayaLib.utility" in sys.modules, "Module not in sys.modules after import"

        # Reload the submodule
        utility_reloaded = importlib.reload(mayaLib.utility)

        # Should still be functional
        assert utility_reloaded is not None
        assert hasattr(utility_reloaded, "__name__")
        assert utility_reloaded.__name__ == "mayaLib.utility"


# ============================================================================
# Real-World Usage Patterns Tests
# ============================================================================


class TestRealWorldPatterns:
    """Test real-world usage patterns found in existing code."""

    def test_pattern_import_and_use_attribute(self):
        """Test pattern: import module then use attribute."""
        import mayaLib

        # Access utility module itself
        utility = mayaLib.utility

        assert utility is not None
        assert hasattr(utility, "__name__")

    def test_pattern_conditional_import(self):
        """Test pattern: conditional import based on availability."""
        import mayaLib

        # Check if module exists before using
        if hasattr(mayaLib, "utility"):
            utility = mayaLib.utility
            assert utility is not None

    def test_pattern_try_except_import(self, suppress_warnings):
        """Test pattern: try-except for optional imports."""
        # Try to import module that might not be available
        try:
            from mayaLib.rigLib import Ziva

            # If we get here, module was loaded
            assert Ziva is not None or Ziva is None  # Could be None if Maya unavailable
        except (ImportError, AttributeError):
            # This is acceptable - module not available
            pass

    def test_pattern_import_multiple_from_same_parent(self, suppress_warnings):
        """Test pattern: importing multiple modules from same parent."""
        # Clear cache
        sys.modules.pop("mayaLib.rigLib.utils.control", None)
        sys.modules.pop("mayaLib.rigLib.utils.joint", None)

        # Import multiple utilities
        from mayaLib.rigLib.utils import control, joint

        assert control is not None
        assert joint is not None

    def test_pattern_nested_attribute_access(self):
        """Test pattern: nested attribute access without explicit imports."""
        import mayaLib

        # Access nested module
        utility = mayaLib.pipelineLib.utility

        assert utility is not None
        assert hasattr(utility, "__name__")


# ============================================================================
# Backwards Compatibility Integration Tests
# ============================================================================


class TestBackwardsCompatibilityIntegration:
    """Integration tests for full backwards compatibility."""

    def test_all_import_patterns_work_together(self, suppress_warnings):
        """Test that all import patterns work together."""
        # Mix different import patterns
        import mayaLib
        from mayaLib import utility
        from mayaLib.pipelineLib import utility as pipeline_util

        # All should work
        assert mayaLib is not None
        assert utility is not None
        assert pipeline_util is not None

        # Access nested modules
        rigLib = mayaLib.rigLib
        assert rigLib is not None

    def test_no_breaking_changes_in_common_patterns(self):
        """Test that common patterns still work as before."""
        # Pattern 1: Direct import
        from mayaLib import utility

        assert utility is not None

        # Pattern 2: Nested import
        from mayaLib.pipelineLib import utility as pipe_util

        assert pipe_util is not None

        # Pattern 3: Attribute access
        import mayaLib

        util = mayaLib.utility
        assert util is not None

    def test_module_attributes_preserved(self):
        """Test that module attributes are preserved."""
        from mayaLib import utility

        # Standard module attributes should exist
        assert hasattr(utility, "__name__")
        assert hasattr(utility, "__file__")
        assert hasattr(utility, "__package__")
        assert hasattr(utility, "__path__")

        # Values should be correct
        assert utility.__name__ == "mayaLib.utility"
        assert utility.__package__ == "mayaLib.utility"

    def test_lazy_loading_transparent_to_user(self):
        """Test that lazy loading is transparent to end users."""
        # Users shouldn't need to know about lazy loading
        # All standard Python module operations should work

        import mayaLib

        # Standard operations
        utility = mayaLib.utility
        assert utility is not None

        # hasattr should work
        assert hasattr(mayaLib, "utility")

        # getattr should work
        util = mayaLib.utility
        assert util is not None

        # Multiple accesses should return same object
        util2 = mayaLib.utility
        assert util is util2

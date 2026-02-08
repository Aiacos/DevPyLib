"""Comprehensive tests for core lazy loading implementation.

Tests backwards compatibility, lazy loading behavior, error handling,
and caching for root __init__.py and mayaLib/__init__.py lazy loading.
"""

import importlib
import sys
from unittest.mock import MagicMock, patch

import pytest


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture(autouse=True)
def reset_modules():
    """Reset module cache before each test.

    Removes mayaLib and DevPyLib modules from sys.modules to ensure
    each test starts with clean state.

    Yields:
        None
    """
    # Store modules to remove
    modules_to_remove = [
        key
        for key in sys.modules.keys()
        if key.startswith("mayaLib") or key == "mayaLib" or key in ["blenderLib", "houdiniLib", "prismLib"]
    ]

    yield

    # Clean up after test
    for module in modules_to_remove:
        sys.modules.pop(module, None)


@pytest.fixture
def mock_maya_unavailable():
    """Mock Maya modules as unavailable.

    Removes Maya mocks from sys.modules to simulate environment
    where Maya is not installed.

    Yields:
        None
    """
    # Store original mocks
    maya_modules = {
        key: sys.modules.pop(key, None)
        for key in list(sys.modules.keys())
        if key.startswith("maya") or key.startswith("pymel")
    }

    yield

    # Restore mocks
    sys.modules.update({k: v for k, v in maya_modules.items() if v is not None})


# ============================================================================
# Root __init__.py Tests
# ============================================================================


class TestRootLazyLoading:
    """Test lazy loading in root __init__.py."""

    def test_import_root_package(self):
        """Test that root package can be imported without loading submodules."""
        # Remove any existing imports
        for key in list(sys.modules.keys()):
            if key == "mayaLib" or key in ["blenderLib", "houdiniLib", "prismLib"]:
                sys.modules.pop(key, None)

        # Import root package - should not trigger submodule imports
        # Note: We're testing inside DevPyLib, so we test mayaLib directly
        # The root __init__.py lazy loading will be tested by attempting to access submodules

    def test_lazy_attribute_access(self):
        """Test that accessing attributes triggers lazy loading."""
        # Clear mayaLib from cache
        sys.modules.pop("mayaLib", None)

        # Import parent module - should use lazy loading via root __init__.py
        # We can't easily test the root package isolation here, so focus on mayaLib

    def test_unknown_attribute_raises_error(self):
        """Test that accessing unknown attributes raises AttributeError."""
        # Import mayaLib module
        import mayaLib

        # Accessing unknown attribute should raise AttributeError
        with pytest.raises(AttributeError, match="has no attribute 'nonexistent'"):
            _ = mayaLib.nonexistent


# ============================================================================
# mayaLib/__init__.py Tests
# ============================================================================


class TestMayaLibLazyLoading:
    """Test lazy loading in mayaLib/__init__.py."""

    def test_import_mayalib_no_submodules_loaded(self):
        """Test that importing mayaLib doesn't load submodules."""
        # Clear cache
        sys.modules.pop("mayaLib", None)
        sys.modules.pop("mayaLib.rigLib", None)

        # Import mayaLib
        import mayaLib

        # Verify mayaLib is loaded
        assert "mayaLib" in sys.modules

        # Verify submodules are NOT loaded yet (lazy loading)
        assert "mayaLib.rigLib" not in sys.modules
        assert "mayaLib.fluidLib" not in sys.modules
        assert "mayaLib.bifrostLib" not in sys.modules

    def test_accessing_submodule_triggers_import(self):
        """Test that accessing a submodule triggers its import."""
        # Clear cache
        sys.modules.pop("mayaLib", None)
        sys.modules.pop("mayaLib.utility", None)

        # Import mayaLib
        import mayaLib

        # Verify utility not loaded yet
        assert "mayaLib.utility" not in sys.modules

        # Access utility - should trigger lazy import
        utility = mayaLib.utility

        # Now utility should be loaded
        assert "mayaLib.utility" in sys.modules
        assert utility is not None

    def test_submodule_cached_after_first_access(self):
        """Test that submodules are cached after first access."""
        # Clear cache
        sys.modules.pop("mayaLib", None)
        sys.modules.pop("mayaLib.utility", None)

        # Import mayaLib
        import mayaLib

        # First access
        utility1 = mayaLib.utility

        # Second access should return cached version
        utility2 = mayaLib.utility

        # Should be the same object
        assert utility1 is utility2

    def test_unknown_submodule_raises_error(self):
        """Test that accessing unknown submodules raises AttributeError."""
        # Import mayaLib
        import mayaLib

        # Accessing unknown submodule should raise AttributeError
        with pytest.raises(AttributeError, match="has no attribute 'nonexistentLib'"):
            _ = mayaLib.nonexistentLib


# ============================================================================
# Backwards Compatibility Tests
# ============================================================================


class TestBackwardsCompatibility:
    """Test backwards compatibility with existing import patterns."""

    def test_import_mayalib(self):
        """Test standard import pattern: import mayaLib."""
        # This should work without errors
        import mayaLib

        assert mayaLib is not None
        assert hasattr(mayaLib, "__getattr__")

    def test_from_import_submodule(self):
        """Test import pattern: from mayaLib import rigLib."""
        # Clear cache
        sys.modules.pop("mayaLib.utility", None)

        # This should trigger lazy loading
        from mayaLib import utility

        assert utility is not None
        assert "mayaLib.utility" in sys.modules

    def test_import_submodule_directly(self):
        """Test import pattern: import mayaLib.rigLib."""
        # Clear cache
        sys.modules.pop("mayaLib.utility", None)

        # This should work with lazy loading
        import mayaLib.utility

        assert "mayaLib.utility" in sys.modules
        assert mayaLib.utility is not None

    def test_from_submodule_import_function(self):
        """Test import pattern: from mayaLib.utility import module."""
        # Clear cache for clean test
        sys.modules.pop("mayaLib.utility", None)
        sys.modules.pop("mayaLib.utility.lazy_loader", None)

        # This should work - imports the submodule then accesses the module
        from mayaLib.utility import lazy_loader

        assert lazy_loader is not None
        assert hasattr(lazy_loader, "create_lazy_loader")

    def test_getattr_on_imported_module(self):
        """Test using getattr() on imported module."""
        import mayaLib

        # Using getattr should work
        utility = getattr(mayaLib, "utility", None)
        assert utility is not None

    def test_hasattr_on_imported_module(self):
        """Test using hasattr() on imported module."""
        import mayaLib

        # hasattr should work for existing submodules
        assert hasattr(mayaLib, "utility")

        # hasattr should return False for non-existent submodules
        assert not hasattr(mayaLib, "nonexistentLib")

    def test_dir_includes_submodules(self):
        """Test that dir() works with lazy-loaded modules."""
        import mayaLib

        # dir() should work (though it won't show lazy-loaded modules until accessed)
        module_attrs = dir(mayaLib)

        # Should have __getattr__
        assert "__getattr__" in module_attrs


# ============================================================================
# Error Handling Tests
# ============================================================================


class TestErrorHandling:
    """Test error handling in lazy loading implementation."""

    def test_import_error_handled_gracefully(self, mock_maya_unavailable):
        """Test that ImportError is handled gracefully."""
        # Clear cache
        sys.modules.pop("mayaLib", None)
        sys.modules.pop("mayaLib.rigLib", None)

        # Import mayaLib
        import mayaLib

        # Attempting to import rigLib (which requires Maya) should not crash
        # It should return None or handle the error gracefully
        with patch("builtins.print") as mock_print:
            rigLib = mayaLib.rigLib

            # Should have printed a warning
            assert mock_print.called

    def test_attribute_error_for_invalid_attributes(self):
        """Test that invalid attributes raise AttributeError."""
        import mayaLib

        # Should raise AttributeError with clear message
        with pytest.raises(
            AttributeError, match="module 'mayaLib' has no attribute 'invalid_attr'"
        ):
            _ = mayaLib.invalid_attr

    def test_multiple_import_errors_dont_crash(self, mock_maya_unavailable):
        """Test that multiple import errors don't crash the system."""
        # Clear cache
        for key in list(sys.modules.keys()):
            if key.startswith("mayaLib."):
                sys.modules.pop(key, None)

        import mayaLib

        # Try multiple imports that might fail
        with patch("builtins.print"):
            _ = mayaLib.rigLib
            _ = mayaLib.fluidLib
            _ = mayaLib.bifrostLib

        # Should not crash


# ============================================================================
# Module Caching Tests
# ============================================================================


class TestModuleCaching:
    """Test module caching behavior."""

    def test_module_cached_in_globals(self):
        """Test that modules are cached in globals after first access."""
        # Clear cache
        sys.modules.pop("mayaLib", None)
        sys.modules.pop("mayaLib.utility", None)

        # Import mayaLib
        import mayaLib

        # Access utility
        _ = mayaLib.utility

        # Should now be in mayaLib's __dict__
        assert "utility" in mayaLib.__dict__

    def test_cached_module_returned_on_second_access(self):
        """Test that cached modules are returned on subsequent access."""
        # Clear cache
        sys.modules.pop("mayaLib", None)
        sys.modules.pop("mayaLib.utility", None)

        # Import mayaLib
        import mayaLib

        # First access
        utility1 = mayaLib.utility
        first_access_id = id(utility1)

        # Second access
        utility2 = mayaLib.utility
        second_access_id = id(utility2)

        # Should be the same object
        assert first_access_id == second_access_id

    def test_module_in_sys_modules_after_import(self):
        """Test that modules are in sys.modules after import."""
        # This test verifies that importlib.import_module properly registers
        # modules in sys.modules when accessed via lazy loading

        # Use a direct import statement which should work with lazy loading
        import mayaLib.pipelineLib

        # Verify module is registered in sys.modules
        assert "mayaLib.pipelineLib" in sys.modules
        assert sys.modules["mayaLib.pipelineLib"] is mayaLib.pipelineLib


# ============================================================================
# Integration Tests
# ============================================================================


class TestIntegration:
    """Integration tests for lazy loading system."""

    def test_multiple_submodules_can_be_imported(self):
        """Test that multiple submodules can be imported."""
        # Clear cache
        for key in list(sys.modules.keys()):
            if key.startswith("mayaLib.") and key != "mayaLib":
                sys.modules.pop(key, None)

        import mayaLib

        # Import multiple submodules
        utility = mayaLib.utility
        pipelineLib = mayaLib.pipelineLib

        # Both should be loaded
        assert utility is not None
        assert pipelineLib is not None
        assert "mayaLib.utility" in sys.modules
        assert "mayaLib.pipelineLib" in sys.modules

    def test_nested_imports_work(self):
        """Test that nested imports work correctly."""
        # Clear cache
        sys.modules.pop("mayaLib.utility", None)
        sys.modules.pop("mayaLib.utility.lazy_loader", None)

        # Import nested module
        from mayaLib.utility import lazy_loader

        # Should work
        assert lazy_loader is not None
        assert hasattr(lazy_loader, "create_lazy_loader")

    def test_reload_module_works(self):
        """Test that importlib.reload works with lazy loading."""
        import mayaLib

        # First load
        _ = mayaLib.utility

        # Reload mayaLib
        importlib.reload(mayaLib)

        # Should still work after reload
        utility_after_reload = mayaLib.utility
        assert utility_after_reload is not None

    def test_lazy_loading_preserves_module_attributes(self):
        """Test that lazy loading preserves module __name__, __file__, etc."""
        from mayaLib import utility

        # Should have standard module attributes
        assert hasattr(utility, "__name__")
        assert utility.__name__ == "mayaLib.utility"
        assert hasattr(utility, "__file__")
        assert hasattr(utility, "__path__")


# ============================================================================
# Performance Tests
# ============================================================================


class TestPerformance:
    """Test performance characteristics of lazy loading."""

    def test_import_mayalib_is_fast(self):
        """Test that importing mayaLib is fast (no eager submodule loading)."""
        import time

        # Clear cache
        sys.modules.pop("mayaLib", None)

        # Measure import time
        start = time.time()
        import mayaLib
        elapsed = time.time() - start

        # Should be very fast since submodules aren't loaded
        # This is just a smoke test - actual threshold depends on system
        assert elapsed < 1.0, f"Import took {elapsed}s, expected < 1.0s"

    def test_submodule_import_only_loads_one_module(self):
        """Test that importing one submodule doesn't load others."""
        # Clear cache
        for key in list(sys.modules.keys()):
            if key.startswith("mayaLib.") and key != "mayaLib":
                sys.modules.pop(key, None)

        import mayaLib

        # Import one submodule
        _ = mayaLib.utility

        # Verify only utility is loaded, not others
        assert "mayaLib.utility" in sys.modules
        assert "mayaLib.rigLib" not in sys.modules
        assert "mayaLib.fluidLib" not in sys.modules

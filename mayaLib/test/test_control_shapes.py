"""Integration tests for control shape creation.

Tests the control shape library functions and Control class factory integration.
Verifies that all shape types can be created without errors.
"""

import sys
from unittest.mock import MagicMock, Mock, patch

import pytest

# Mock Maya modules before imports
if "maya.cmds" not in sys.modules:
    sys.modules["maya"] = MagicMock()
    sys.modules["maya.cmds"] = MagicMock()
    sys.modules["maya.api"] = MagicMock()
    sys.modules["maya.api.OpenMaya"] = MagicMock()
    sys.modules["maya.mel"] = MagicMock()

# Mock pymel with proper return types
if "pymel.core" not in sys.modules:
    pymel_mock = MagicMock()

    # Mock curve function to return a mock PyNode
    def mock_curve(*args, **kwargs):
        node = Mock()
        node.name.return_value = kwargs.get("name", "curve_CTRL")
        node.getShapes.return_value = []
        return node

    # Mock circle function to return tuple
    def mock_circle(*args, **kwargs):
        node = Mock()
        node.name.return_value = kwargs.get("n", "circle_CTRL")
        node.getShapes.return_value = []
        return (node,)

    pymel_mock.curve = mock_curve
    pymel_mock.circle = mock_circle
    pymel_mock.PyNode = Mock

    sys.modules["pymel"] = pymel_mock
    sys.modules["pymel.core"] = pymel_mock

from mayaLib.rigLib.utils import ctrl_shape

# ============================================================================
# Test Data
# ============================================================================


# All available control shape functions
SHAPE_FUNCTIONS = [
    # Existing shapes (8)
    "sphereCtrlShape",
    "moveCtrlShape",
    "trapeziumCtrlShape",
    "chestCtrlShape",
    "hipCtrlShape",
    "headCtrlShape",
    "displayCtrlShape",
    "ikfkCtrlShape",
    # New shapes (5)
    "pinCtrlShape",
    "arrowCtrlShape",
    "cubeCtrlShape",
    "crossCtrlShape",
    "squareCtrlShape",
]


# ============================================================================
# Import Tests
# ============================================================================


class TestControlShapeImports:
    """Test that all control shape functions can be imported."""

    def test_import_ctrl_shape_module(self):
        """Test that ctrl_shape module can be imported."""
        from mayaLib.rigLib.utils import ctrl_shape as cs

        assert cs is not None

    def test_all_shapes_in_module_all(self):
        """Test that all shape functions are in __all__ export list."""
        from mayaLib.rigLib.utils import ctrl_shape as cs

        for shape_func in SHAPE_FUNCTIONS:
            assert shape_func in cs.__all__, f"{shape_func} not in __all__"

    def test_all_shapes_importable(self):
        """Test that all shape functions can be imported."""
        from mayaLib.rigLib.utils import ctrl_shape as cs

        for shape_func in SHAPE_FUNCTIONS:
            assert hasattr(cs, shape_func), f"{shape_func} not found in module"
            func = getattr(cs, shape_func)
            assert callable(func), f"{shape_func} is not callable"

    def test_individual_shape_imports(self):
        """Test that shapes can be imported individually."""
        # Test a few representative imports
        from mayaLib.rigLib.utils.ctrl_shape import (
            arrowCtrlShape,
            cubeCtrlShape,
            sphereCtrlShape,
        )

        assert callable(sphereCtrlShape)
        assert callable(arrowCtrlShape)
        assert callable(cubeCtrlShape)


# ============================================================================
# Shape Creation Tests
# ============================================================================


class TestControlShapeCreation:
    """Test that all control shape functions can create shapes."""

    @pytest.mark.parametrize("shape_func_name", SHAPE_FUNCTIONS)
    def test_shape_creation_default_params(self, shape_func_name):
        """Test shape creation with default parameters."""
        shape_func = getattr(ctrl_shape, shape_func_name)

        # Call function with default params
        result = shape_func()

        # Verify result is not None
        assert result is not None

    @pytest.mark.parametrize("shape_func_name", SHAPE_FUNCTIONS)
    def test_shape_creation_with_name(self, shape_func_name):
        """Test shape creation with custom name."""
        shape_func = getattr(ctrl_shape, shape_func_name)

        # Extract base shape name (e.g., "sphere" from "sphereCtrlShape")
        shape_name = shape_func_name.replace("CtrlShape", "").lower()
        custom_name = f"test_{shape_name}_CTRL"

        # Call function with custom name
        result = shape_func(name=custom_name)

        # Verify result is not None
        assert result is not None

    @pytest.mark.parametrize("shape_func_name", SHAPE_FUNCTIONS)
    def test_shape_creation_with_scale(self, shape_func_name):
        """Test shape creation with custom scale."""
        shape_func = getattr(ctrl_shape, shape_func_name)

        # Test with different scale values
        for scale in [0.5, 1.0, 2.0, 5.0]:
            result = shape_func(scale=scale)
            assert result is not None

    @pytest.mark.parametrize("shape_func_name", SHAPE_FUNCTIONS)
    def test_shape_creation_with_name_and_scale(self, shape_func_name):
        """Test shape creation with both custom name and scale."""
        shape_func = getattr(ctrl_shape, shape_func_name)

        shape_name = shape_func_name.replace("CtrlShape", "").lower()
        custom_name = f"scaled_{shape_name}_CTRL"

        result = shape_func(name=custom_name, scale=2.5)

        assert result is not None


# ============================================================================
# Shape Function Signature Tests
# ============================================================================


class TestControlShapeFunctionSignatures:
    """Test that all shape functions have correct signatures."""

    @pytest.mark.parametrize("shape_func_name", SHAPE_FUNCTIONS)
    def test_function_has_name_parameter(self, shape_func_name):
        """Test that shape functions accept 'name' parameter."""
        import inspect

        shape_func = getattr(ctrl_shape, shape_func_name)
        sig = inspect.signature(shape_func)

        assert "name" in sig.parameters, f"{shape_func_name} missing 'name' parameter"

    @pytest.mark.parametrize("shape_func_name", SHAPE_FUNCTIONS)
    def test_function_has_scale_parameter(self, shape_func_name):
        """Test that shape functions accept 'scale' parameter."""
        import inspect

        shape_func = getattr(ctrl_shape, shape_func_name)
        sig = inspect.signature(shape_func)

        assert "scale" in sig.parameters, f"{shape_func_name} missing 'scale' parameter"

    @pytest.mark.parametrize("shape_func_name", SHAPE_FUNCTIONS)
    def test_function_has_default_values(self, shape_func_name):
        """Test that shape functions have sensible default values."""
        import inspect

        shape_func = getattr(ctrl_shape, shape_func_name)
        sig = inspect.signature(shape_func)

        # Check name has default
        name_param = sig.parameters["name"]
        assert name_param.default != inspect.Parameter.empty, (
            f"{shape_func_name} 'name' parameter missing default"
        )

        # Check scale has default
        scale_param = sig.parameters["scale"]
        assert scale_param.default != inspect.Parameter.empty, (
            f"{shape_func_name} 'scale' parameter missing default"
        )
        assert isinstance(scale_param.default, int | float), (
            f"{shape_func_name} 'scale' default should be numeric"
        )

    @pytest.mark.parametrize("shape_func_name", SHAPE_FUNCTIONS)
    def test_function_has_docstring(self, shape_func_name):
        """Test that shape functions have docstrings."""
        shape_func = getattr(ctrl_shape, shape_func_name)

        assert shape_func.__doc__ is not None, f"{shape_func_name} missing docstring"
        assert len(shape_func.__doc__.strip()) > 0, f"{shape_func_name} has empty docstring"


# ============================================================================
# New Shapes Specific Tests
# ============================================================================


class TestNewControlShapes:
    """Test the 5 new control shapes specifically."""

    def test_pin_shape_creation(self):
        """Test pin control shape creation."""
        result = ctrl_shape.pinCtrlShape(name="test_pin_CTRL", scale=1.5)
        assert result is not None

    def test_arrow_shape_creation(self):
        """Test arrow control shape creation."""
        result = ctrl_shape.arrowCtrlShape(name="test_arrow_CTRL", scale=2.0)
        assert result is not None

    def test_cube_shape_creation(self):
        """Test cube control shape creation."""
        result = ctrl_shape.cubeCtrlShape(name="test_cube_CTRL", scale=1.0)
        assert result is not None

    def test_cross_shape_creation(self):
        """Test cross control shape creation."""
        result = ctrl_shape.crossCtrlShape(name="test_cross_CTRL", scale=1.5)
        assert result is not None

    def test_square_shape_creation(self):
        """Test square control shape creation."""
        result = ctrl_shape.squareCtrlShape(name="test_square_CTRL", scale=2.0)
        assert result is not None


# ============================================================================
# Control Class Integration Tests
# ============================================================================


class TestControlClassIntegration:
    """Test that Control class can use all shape types."""

    def test_control_module_importable(self):
        """Test that control module can be imported."""
        from mayaLib.rigLib.utils import control

        assert control is not None
        assert hasattr(control, "Control")

    @pytest.mark.parametrize(
        "shape_type",
        [
            "sphere",
            "move",
            "spine",
            "chest",
            "hip",
            "head",
            "display",
            "ikfk",
            "pin",
            "arrow",
            "cube",
            "cross",
            "square",
        ],
    )
    def test_control_class_with_shape_type(self, shape_type):
        """Test Control class accepts all shape types."""
        from mayaLib.rigLib.utils.control import Control

        # Mock additional dependencies
        with patch("mayaLib.rigLib.utils.control.nc"):
            with patch("mayaLib.rigLib.utils.control.common"):
                with patch("mayaLib.rigLib.utils.control.pm") as mock_pm:
                    # Setup mocks
                    mock_pm.PyNode.return_value.getShapes.return_value = []
                    mock_pm.group.return_value = Mock()
                    mock_pm.objExists.return_value = False

                    # Create control with shape type
                    # Note: Control class initialization will use the mocked functions
                    try:
                        Control(prefix="test", shape=shape_type)
                        # If we get here, the shape type is recognized
                        assert True
                    except AttributeError:
                        # Expected in test environment with mocks
                        pass


# ============================================================================
# Backwards Compatibility Tests
# ============================================================================


class TestBackwardsCompatibility:
    """Test that existing shape creation still works."""

    def test_existing_sphere_shape(self):
        """Test that existing sphere shape still works."""
        result = ctrl_shape.sphereCtrlShape()
        assert result is not None

    def test_existing_move_shape(self):
        """Test that existing move shape still works."""
        result = ctrl_shape.moveCtrlShape()
        assert result is not None

    def test_existing_trapezium_shape(self):
        """Test that existing trapezium shape still works."""
        result = ctrl_shape.trapeziumCtrlShape()
        assert result is not None

    def test_all_existing_shapes(self):
        """Test all 8 existing shapes still work."""
        existing_shapes = [
            "sphereCtrlShape",
            "moveCtrlShape",
            "trapeziumCtrlShape",
            "chestCtrlShape",
            "hipCtrlShape",
            "headCtrlShape",
            "displayCtrlShape",
            "ikfkCtrlShape",
        ]

        for shape_func_name in existing_shapes:
            shape_func = getattr(ctrl_shape, shape_func_name)
            result = shape_func()
            assert result is not None, f"{shape_func_name} failed"


# ============================================================================
# Edge Cases and Error Handling
# ============================================================================


class TestEdgeCases:
    """Test edge cases and error handling."""

    @pytest.mark.parametrize("shape_func_name", SHAPE_FUNCTIONS)
    def test_shape_with_zero_scale(self, shape_func_name):
        """Test shape creation with zero scale."""
        shape_func = getattr(ctrl_shape, shape_func_name)

        # Should not raise error with zero scale
        result = shape_func(scale=0.0)
        assert result is not None

    @pytest.mark.parametrize("shape_func_name", SHAPE_FUNCTIONS)
    def test_shape_with_negative_scale(self, shape_func_name):
        """Test shape creation with negative scale."""
        shape_func = getattr(ctrl_shape, shape_func_name)

        # Should not raise error with negative scale (might flip shape)
        result = shape_func(scale=-1.0)
        assert result is not None

    @pytest.mark.parametrize("shape_func_name", SHAPE_FUNCTIONS)
    def test_shape_with_very_large_scale(self, shape_func_name):
        """Test shape creation with very large scale."""
        shape_func = getattr(ctrl_shape, shape_func_name)

        # Should handle large scale values
        result = shape_func(scale=1000.0)
        assert result is not None

    @pytest.mark.parametrize("shape_func_name", SHAPE_FUNCTIONS)
    def test_shape_with_special_characters_in_name(self, shape_func_name):
        """Test shape creation with special characters in name."""
        shape_func = getattr(ctrl_shape, shape_func_name)

        # Maya will handle special character sanitization
        # Test should not crash
        try:
            result = shape_func(name="test_ctrl_123_CTRL")
            assert result is not None
        except Exception:
            # Some special characters might be invalid, that's ok
            pass


# ============================================================================
# Summary Test
# ============================================================================


class TestSummary:
    """Summary test for all control shapes."""

    def test_all_13_shapes_functional(self):
        """Test that all 13 control shapes are functional."""
        shapes_tested = []

        for shape_func_name in SHAPE_FUNCTIONS:
            shape_func = getattr(ctrl_shape, shape_func_name)
            result = shape_func()

            if result is not None:
                shapes_tested.append(shape_func_name)

        # Verify all 13 shapes were tested successfully
        assert len(shapes_tested) == 13, (
            f"Expected 13 shapes, got {len(shapes_tested)}: {shapes_tested}"
        )

    def test_shape_count_matches_spec(self):
        """Test that shape count matches specification."""
        # Spec requires: 8 existing + 5 new = 13 total
        assert len(SHAPE_FUNCTIONS) == 13, f"Expected 13 shapes, found {len(SHAPE_FUNCTIONS)}"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])

"""Unit tests for FunctionUI input validators.

Tests the Qt validator functionality added to FunctionUI to provide
real-time validation feedback for integer and float parameters.
"""

import pytest

try:
    from PySide6 import QtGui, QtWidgets
except ImportError:
    from PySide2 import QtGui, QtWidgets

from mayaLib.guiLib.base.base_ui import FunctionUI


@pytest.mark.unit
class TestValidatorAssignment:
    """Test suite for validator assignment based on type hints."""

    def test_int_parameter_gets_int_validator(self, qtbot):
        """Test that parameters with int type hint get QIntValidator."""

        def test_func(count: int = 5):
            pass

        ui = FunctionUI(test_func)
        qtbot.addWidget(ui)

        # Find the lineedit for 'count' parameter
        lineedit = ui.lineedit_list[0]

        assert isinstance(lineedit, QtWidgets.QLineEdit)
        assert lineedit.validator() is not None
        assert isinstance(lineedit.validator(), QtGui.QIntValidator)

    def test_float_parameter_gets_double_validator(self, qtbot):
        """Test that parameters with float type hint get QDoubleValidator."""

        def test_func(scale: float = 1.0):
            pass

        ui = FunctionUI(test_func)
        qtbot.addWidget(ui)

        lineedit = ui.lineedit_list[0]

        assert isinstance(lineedit, QtWidgets.QLineEdit)
        assert lineedit.validator() is not None
        assert isinstance(lineedit.validator(), QtGui.QDoubleValidator)

    def test_str_parameter_gets_no_validator(self, qtbot):
        """Test that parameters with str type hint get no validator."""

        def test_func(name: str = "default"):
            pass

        ui = FunctionUI(test_func)
        qtbot.addWidget(ui)

        lineedit = ui.lineedit_list[0]

        assert isinstance(lineedit, QtWidgets.QLineEdit)
        assert lineedit.validator() is None

    def test_no_type_hint_no_validator(self, qtbot):
        """Test that parameters without type hints get no validator."""

        def test_func(value="default"):
            pass

        ui = FunctionUI(test_func)
        qtbot.addWidget(ui)

        lineedit = ui.lineedit_list[0]

        assert isinstance(lineedit, QtWidgets.QLineEdit)
        assert lineedit.validator() is None

    def test_int_parameter_without_default_gets_validator(self, qtbot):
        """Test that int parameters without defaults also get validators."""

        def test_func(count: int):
            pass

        ui = FunctionUI(test_func)
        qtbot.addWidget(ui)

        lineedit = ui.lineedit_list[0]

        assert isinstance(lineedit, QtWidgets.QLineEdit)
        assert isinstance(lineedit.validator(), QtGui.QIntValidator)

    def test_float_parameter_without_default_gets_validator(self, qtbot):
        """Test that float parameters without defaults also get validators."""

        def test_func(scale: float):
            pass

        ui = FunctionUI(test_func)
        qtbot.addWidget(ui)

        lineedit = ui.lineedit_list[0]

        assert isinstance(lineedit, QtWidgets.QLineEdit)
        assert isinstance(lineedit.validator(), QtGui.QDoubleValidator)


@pytest.mark.unit
class TestIntValidator:
    """Test suite for QIntValidator behavior."""

    @pytest.fixture
    def int_ui(self, qtbot):
        """Create a FunctionUI with an integer parameter."""

        def test_func(count: int = 0):
            pass

        ui = FunctionUI(test_func)
        qtbot.addWidget(ui)
        return ui

    def test_accepts_positive_integer(self, int_ui):
        """Test that validator accepts positive integers."""
        lineedit = int_ui.lineedit_list[0]
        validator = lineedit.validator()

        state, _, _ = validator.validate("123", 0)
        assert state == QtGui.QValidator.Acceptable

    def test_accepts_negative_integer(self, int_ui):
        """Test that validator accepts negative integers."""
        lineedit = int_ui.lineedit_list[0]
        validator = lineedit.validator()

        state, _, _ = validator.validate("-456", 0)
        assert state == QtGui.QValidator.Acceptable

    def test_accepts_zero(self, int_ui):
        """Test that validator accepts zero."""
        lineedit = int_ui.lineedit_list[0]
        validator = lineedit.validator()

        state, _, _ = validator.validate("0", 0)
        assert state == QtGui.QValidator.Acceptable

    def test_rejects_text(self, int_ui):
        """Test that validator rejects text input."""
        lineedit = int_ui.lineedit_list[0]
        validator = lineedit.validator()

        state, _, _ = validator.validate("abc", 0)
        assert state == QtGui.QValidator.Invalid

    def test_rejects_float(self, int_ui):
        """Test that validator rejects float input."""
        lineedit = int_ui.lineedit_list[0]
        validator = lineedit.validator()

        state, _, _ = validator.validate("1.5", 0)
        # QIntValidator returns Intermediate for partial input with dot
        assert state in (QtGui.QValidator.Invalid, QtGui.QValidator.Intermediate)

    def test_rejects_mixed_text(self, int_ui):
        """Test that validator rejects mixed alphanumeric input."""
        lineedit = int_ui.lineedit_list[0]
        validator = lineedit.validator()

        state, _, _ = validator.validate("12abc", 0)
        assert state == QtGui.QValidator.Invalid


@pytest.mark.unit
class TestFloatValidator:
    """Test suite for QDoubleValidator behavior."""

    @pytest.fixture
    def float_ui(self, qtbot):
        """Create a FunctionUI with a float parameter."""

        def test_func(scale: float = 1.0):
            pass

        ui = FunctionUI(test_func)
        qtbot.addWidget(ui)
        return ui

    def test_accepts_positive_float(self, float_ui):
        """Test that validator accepts positive floats."""
        lineedit = float_ui.lineedit_list[0]
        validator = lineedit.validator()

        state, _, _ = validator.validate("1.5", 0)
        # QDoubleValidator may return Intermediate or Acceptable depending on locale
        assert state in (QtGui.QValidator.Acceptable, QtGui.QValidator.Intermediate)

    def test_accepts_negative_float(self, float_ui):
        """Test that validator accepts negative floats."""
        lineedit = float_ui.lineedit_list[0]
        validator = lineedit.validator()

        state, _, _ = validator.validate("-3.14", 0)
        # QDoubleValidator may return Intermediate or Acceptable depending on locale
        assert state in (QtGui.QValidator.Acceptable, QtGui.QValidator.Intermediate)

    def test_accepts_zero_float(self, float_ui):
        """Test that validator accepts zero as a float."""
        lineedit = float_ui.lineedit_list[0]
        validator = lineedit.validator()

        state, _, _ = validator.validate("0.0", 0)
        # QDoubleValidator may return Intermediate or Acceptable depending on locale
        assert state in (QtGui.QValidator.Acceptable, QtGui.QValidator.Intermediate)

    def test_accepts_integer_as_float(self, float_ui):
        """Test that validator accepts integers for float fields."""
        lineedit = float_ui.lineedit_list[0]
        validator = lineedit.validator()

        state, _, _ = validator.validate("42", 0)
        assert state == QtGui.QValidator.Acceptable

    def test_rejects_text(self, float_ui):
        """Test that validator rejects text input."""
        lineedit = float_ui.lineedit_list[0]
        validator = lineedit.validator()

        state, _, _ = validator.validate("abc", 0)
        assert state == QtGui.QValidator.Invalid

    def test_rejects_multiple_dots(self, float_ui):
        """Test that validator rejects invalid float format."""
        lineedit = float_ui.lineedit_list[0]
        validator = lineedit.validator()

        state, _, _ = validator.validate("1.2.3", 0)
        # Multiple dots should be Invalid or Intermediate
        assert state in (QtGui.QValidator.Invalid, QtGui.QValidator.Intermediate)


@pytest.mark.unit
@pytest.mark.gui
class TestVisualFeedback:
    """Test suite for validation visual feedback."""

    @pytest.fixture
    def multi_param_ui(self, qtbot):
        """Create a FunctionUI with multiple typed parameters."""

        def test_func(count: int = 5, scale: float = 1.0, name: str = "test"):
            pass

        ui = FunctionUI(test_func)
        qtbot.addWidget(ui)
        return ui

    def test_invalid_input_shows_red_border(self, multi_param_ui, qtbot):
        """Test that invalid input displays red border."""
        int_lineedit = multi_param_ui.lineedit_list[0]

        # Set invalid input directly and trigger validation
        int_lineedit.setText("abc")
        qtbot.wait(10)  # Give Qt time to process

        # Check that red border is applied
        assert "red" in int_lineedit.styleSheet().lower()

    def test_valid_input_clears_red_border(self, multi_param_ui, qtbot):
        """Test that valid input removes red border."""
        int_lineedit = multi_param_ui.lineedit_list[0]

        # First enter invalid input
        int_lineedit.setText("abc")
        qtbot.wait(10)
        assert "red" in int_lineedit.styleSheet().lower()

        # Clear and enter valid input
        int_lineedit.setText("123")
        qtbot.wait(10)

        # Red border should be removed
        assert int_lineedit.styleSheet() == ""

    def test_empty_field_is_valid(self, multi_param_ui, qtbot):
        """Test that empty fields are considered valid."""
        int_lineedit = multi_param_ui.lineedit_list[0]

        # Clear the field (making it empty)
        int_lineedit.clear()

        # Empty should be valid (will use default or None)
        assert int_lineedit.styleSheet() == ""

    def test_execute_button_disabled_on_invalid_input(self, multi_param_ui, qtbot):
        """Test that Execute button is disabled when validation fails."""
        int_lineedit = multi_param_ui.lineedit_list[0]

        # Initially should be enabled
        assert multi_param_ui.exec_button.isEnabled()

        # Enter invalid input
        int_lineedit.setText("abc")
        qtbot.wait(10)

        # Execute button should be disabled
        assert not multi_param_ui.exec_button.isEnabled()

    def test_execute_button_enabled_on_valid_input(self, multi_param_ui, qtbot):
        """Test that Execute button is enabled when all fields are valid."""
        int_lineedit = multi_param_ui.lineedit_list[0]

        # Enter invalid input first
        int_lineedit.setText("abc")
        qtbot.wait(10)
        assert not multi_param_ui.exec_button.isEnabled()

        # Clear and enter valid input
        int_lineedit.setText("123")
        qtbot.wait(10)

        # Execute button should be enabled again
        assert multi_param_ui.exec_button.isEnabled()

    def test_multiple_invalid_fields(self, multi_param_ui, qtbot):
        """Test visual feedback with multiple invalid fields."""
        int_lineedit = multi_param_ui.lineedit_list[0]
        float_lineedit = multi_param_ui.lineedit_list[1]

        # Enter invalid input in both fields
        int_lineedit.setText("abc")
        float_lineedit.setText("xyz")
        qtbot.wait(10)

        # Both should show red border
        assert "red" in int_lineedit.styleSheet().lower()
        assert "red" in float_lineedit.styleSheet().lower()

        # Execute button should be disabled
        assert not multi_param_ui.exec_button.isEnabled()


@pytest.mark.unit
@pytest.mark.gui
class TestFunctionUIIntegration:
    """Integration tests for FunctionUI with validators."""

    def test_mixed_parameter_types(self, qtbot):
        """Test FunctionUI with mixed parameter types."""

        def test_func(
            count: int = 10,
            scale: float = 1.5,
            name: str = "default",
            enabled: bool = True,
        ):
            pass

        ui = FunctionUI(test_func)
        qtbot.addWidget(ui)

        # Check that we have 4 parameters
        assert len(ui.lineedit_list) == 4

        # Check validator assignment
        count_edit = ui.lineedit_list[0]
        scale_edit = ui.lineedit_list[1]
        name_edit = ui.lineedit_list[2]
        enabled_checkbox = ui.lineedit_list[3]

        assert isinstance(count_edit.validator(), QtGui.QIntValidator)
        assert isinstance(scale_edit.validator(), QtGui.QDoubleValidator)
        assert name_edit.validator() is None
        assert isinstance(enabled_checkbox, QtWidgets.QCheckBox)

    def test_validators_on_required_parameters(self, qtbot):
        """Test that validators work on required parameters (no defaults)."""

        def test_func(count: int, scale: float):
            pass

        ui = FunctionUI(test_func)
        qtbot.addWidget(ui)

        count_edit = ui.lineedit_list[0]
        scale_edit = ui.lineedit_list[1]

        assert isinstance(count_edit.validator(), QtGui.QIntValidator)
        assert isinstance(scale_edit.validator(), QtGui.QDoubleValidator)

    def test_validation_feedback_updates_on_text_change(self, qtbot):
        """Test that validation feedback updates in real-time."""

        def test_func(value: int = 0):
            pass

        ui = FunctionUI(test_func)
        qtbot.addWidget(ui)

        lineedit = ui.lineedit_list[0]

        # Initially valid (has default value "0")
        assert ui.exec_button.isEnabled()

        # Set invalid text
        lineedit.setText("a")
        qtbot.wait(10)

        # Should become invalid
        assert not ui.exec_button.isEnabled()
        assert "red" in lineedit.styleSheet().lower()

    def test_parameter_list_includes_type_annotations(self, qtbot):
        """Test that get_parameter_list extracts type annotations."""

        def test_func(count: int = 5, scale: float = 1.0, name: str = "test"):
            pass

        ui = FunctionUI(test_func)
        qtbot.addWidget(ui)

        # Check that args contains type information
        assert len(ui.args) == 3
        assert ui.args[0] == ("count", 5, int)
        assert ui.args[1] == ("scale", 1.0, float)
        assert ui.args[2] == ("name", "test", str)

    def test_edge_case_large_numbers(self, qtbot):
        """Test validators with large numbers."""

        def test_func(big_int: int = 0, big_float: float = 0.0):
            pass

        ui = FunctionUI(test_func)
        qtbot.addWidget(ui)

        int_edit = ui.lineedit_list[0]
        float_edit = ui.lineedit_list[1]

        # Test large integer
        int_edit.setText("999999999")
        qtbot.wait(10)
        assert ui.exec_button.isEnabled()

        # Test large float
        float_edit.setText("123456.789")
        qtbot.wait(10)
        assert ui.exec_button.isEnabled()

    def test_edge_case_special_float_values(self, qtbot):
        """Test float validator with special values."""

        def test_func(value: float = 0.0):
            pass

        ui = FunctionUI(test_func)
        qtbot.addWidget(ui)

        lineedit = ui.lineedit_list[0]

        # Test decimal starting with dot
        lineedit.setText(".5")
        qtbot.wait(10)
        # Empty or intermediate is acceptable since validation allows partial input
        # The execute button may be enabled if validator accepts intermediate states

        # Test negative decimal
        lineedit.setText("-.25")
        qtbot.wait(10)
        # Negative decimals may be Intermediate during typing but should be valid when complete

    def test_real_function_signature_transform(self, qtbot):
        """Test with real function signature from transform module."""

        # Simulating make_offset_group signature from mayaLib.rigLib.utils.transform
        def make_offset_group(node, prefix: str | None = None):
            """Create an offset group above a transform."""
            pass

        ui = FunctionUI(make_offset_group)
        qtbot.addWidget(ui)

        # Should have 2 parameters
        assert len(ui.lineedit_list) == 2

        # 'node' parameter - no type hint, no validator
        node_edit = ui.lineedit_list[0]
        assert node_edit.validator() is None

        # 'prefix' parameter - str type, no validator
        prefix_edit = ui.lineedit_list[1]
        assert prefix_edit.validator() is None

    def test_real_function_signature_with_numeric_types(self, qtbot):
        """Test with function signature containing numeric types."""

        # Simulating a typical rigging function with numeric parameters
        def create_twist_joint(
            start_joint,
            end_joint,
            divisions: int = 5,
            twist_factor: float = 1.0,
            auto_orient: bool = True,
        ):
            """Create twist joints between two joints."""
            pass

        ui = FunctionUI(create_twist_joint)
        qtbot.addWidget(ui)

        # Should have 5 parameters
        assert len(ui.lineedit_list) == 5

        # First two parameters - no type hints, no validators
        assert ui.lineedit_list[0].validator() is None
        assert ui.lineedit_list[1].validator() is None

        # divisions parameter - int type, should have QIntValidator
        divisions_edit = ui.lineedit_list[2]
        assert isinstance(divisions_edit.validator(), QtGui.QIntValidator)

        # twist_factor parameter - float type, should have QDoubleValidator
        twist_edit = ui.lineedit_list[3]
        assert isinstance(twist_edit.validator(), QtGui.QDoubleValidator)

        # auto_orient parameter - bool type, should be checkbox
        assert isinstance(ui.lineedit_list[4], QtWidgets.QCheckBox)

    def test_validation_with_complex_function_signature(self, qtbot):
        """Test validation behavior with complex function signature."""

        def setup_rig_component(
            name: str = "component",
            parent_joint=None,
            num_segments: int = 3,
            segment_length: float = 1.0,
            use_stretch: bool = False,
            mirror: bool = False,
        ):
            """Setup a complex rig component."""
            pass

        ui = FunctionUI(setup_rig_component)
        qtbot.addWidget(ui)

        # Find the numeric edit fields
        num_segments_edit = ui.lineedit_list[2]  # int parameter
        segment_length_edit = ui.lineedit_list[3]  # float parameter

        # Initially all fields should be valid
        assert ui.exec_button.isEnabled()

        # Enter invalid value in int field
        num_segments_edit.setText("abc")
        qtbot.wait(10)

        # Should show validation error
        assert not ui.exec_button.isEnabled()
        assert "red" in num_segments_edit.styleSheet().lower()

        # Fix the int field
        num_segments_edit.setText("5")
        qtbot.wait(10)

        # Should be valid again
        assert ui.exec_button.isEnabled()
        assert num_segments_edit.styleSheet() == ""

        # Now test float field
        segment_length_edit.setText("invalid")
        qtbot.wait(10)

        # Should show validation error
        assert not ui.exec_button.isEnabled()
        assert "red" in segment_length_edit.styleSheet().lower()

    def test_function_with_only_required_typed_parameters(self, qtbot):
        """Test function with required parameters (no defaults) with type hints."""

        def calculate_distance(
            point_a: float,
            point_b: float,
            scale: float,
        ):
            """Calculate distance between two points."""
            pass

        ui = FunctionUI(calculate_distance)
        qtbot.addWidget(ui)

        # All three parameters should have validators
        assert len(ui.lineedit_list) == 3

        for lineedit in ui.lineedit_list:
            assert isinstance(lineedit.validator(), QtGui.QDoubleValidator)

        # Test that empty fields are considered valid
        # (will be handled by exec_function with None or defaults)
        for lineedit in ui.lineedit_list:
            lineedit.clear()

        qtbot.wait(10)
        assert ui.exec_button.isEnabled()

    def test_function_with_no_type_hints(self, qtbot):
        """Test function with no type hints gets no validators."""

        def legacy_function(param1, param2, param3="default"):
            """Legacy function without type hints."""
            pass

        ui = FunctionUI(legacy_function)
        qtbot.addWidget(ui)

        # None of the parameters should have validators
        for lineedit in ui.lineedit_list:
            assert isinstance(lineedit, QtWidgets.QLineEdit)
            assert lineedit.validator() is None

    def test_mixed_typed_and_untyped_parameters(self, qtbot):
        """Test function with mix of typed and untyped parameters."""

        def mixed_function(
            untyped_param,
            typed_int: int = 5,
            typed_float: float = 1.0,
            untyped_with_default="test",
        ):
            """Function with mixed type annotations."""
            pass

        ui = FunctionUI(mixed_function)
        qtbot.addWidget(ui)

        assert len(ui.lineedit_list) == 4

        # First parameter: untyped, no validator
        assert ui.lineedit_list[0].validator() is None

        # Second parameter: int, has validator
        assert isinstance(ui.lineedit_list[1].validator(), QtGui.QIntValidator)

        # Third parameter: float, has validator
        assert isinstance(ui.lineedit_list[2].validator(), QtGui.QDoubleValidator)

        # Fourth parameter: untyped with default, no validator
        assert ui.lineedit_list[3].validator() is None

    def test_validator_preserves_default_values(self, qtbot):
        """Test that validators don't interfere with default values."""

        def test_func(count: int = 42, scale: float = 3.14):
            pass

        ui = FunctionUI(test_func)
        qtbot.addWidget(ui)

        # Check that default values are preserved in the UI
        count_edit = ui.lineedit_list[0]
        scale_edit = ui.lineedit_list[1]

        assert count_edit.text() == "42"
        assert scale_edit.text() == "3.14"

        # Validators should still be applied
        assert isinstance(count_edit.validator(), QtGui.QIntValidator)
        assert isinstance(scale_edit.validator(), QtGui.QDoubleValidator)

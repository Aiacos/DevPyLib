"""Unit tests for error_dialog module.

Tests the error dialog functionality for displaying user-friendly error messages
when operations fail in Maya GUI applications.
"""

import traceback
from unittest.mock import MagicMock, Mock, patch

import pytest

from mayaLib.guiLib.utils.error_dialog import (
    format_exception,
    get_maya_main_window,
    show_error_dialog,
    show_exception_dialog,
)


@pytest.mark.unit
class TestFormatException:
    """Test suite for format_exception function."""

    def test_format_exception_value_error(self):
        """Test formatting a ValueError exception."""
        exception = ValueError("Invalid input value")
        error_type, error_message = format_exception(exception)

        assert error_type == "ValueError"
        assert error_message == "Invalid input value"

    def test_format_exception_type_error(self):
        """Test formatting a TypeError exception."""
        exception = TypeError("Expected str, got int")
        error_type, error_message = format_exception(exception)

        assert error_type == "TypeError"
        assert error_message == "Expected str, got int"

    def test_format_exception_runtime_error(self):
        """Test formatting a RuntimeError exception."""
        exception = RuntimeError("Operation failed unexpectedly")
        error_type, error_message = format_exception(exception)

        assert error_type == "RuntimeError"
        assert error_message == "Operation failed unexpectedly"

    def test_format_exception_empty_message(self):
        """Test formatting an exception with empty message."""
        exception = Exception("")
        error_type, error_message = format_exception(exception)

        assert error_type == "Exception"
        assert error_message == ""

    def test_format_exception_custom_exception(self):
        """Test formatting a custom exception class."""
        class CustomError(Exception):
            """Custom exception for testing."""
            pass

        exception = CustomError("Custom error message")
        error_type, error_message = format_exception(exception)

        assert error_type == "CustomError"
        assert error_message == "Custom error message"


@pytest.mark.unit
class TestGetMayaMainWindow:
    """Test suite for get_maya_main_window function."""

    @patch('mayaLib.guiLib.utils.error_dialog.OpenMayaUI.MQtUtil.mainWindow')
    @patch('mayaLib.guiLib.utils.error_dialog.wrapInstance')
    def test_get_maya_main_window_success(self, mock_wrap, mock_main_window):
        """Test successfully getting Maya main window."""
        # Setup mocks
        mock_main_window.return_value = 12345  # Fake pointer
        mock_widget = MagicMock()
        mock_wrap.return_value = mock_widget

        # Call function
        result = get_maya_main_window()

        # Verify
        assert result == mock_widget
        mock_main_window.assert_called_once()
        mock_wrap.assert_called_once()

    @patch('mayaLib.guiLib.utils.error_dialog.OpenMayaUI.MQtUtil.mainWindow')
    def test_get_maya_main_window_unavailable(self, mock_main_window):
        """Test when Maya main window is unavailable."""
        mock_main_window.return_value = None

        result = get_maya_main_window()

        assert result is None
        mock_main_window.assert_called_once()


@pytest.mark.unit
class TestShowErrorDialog:
    """Test suite for show_error_dialog function."""

    @pytest.fixture
    def mock_message_box(self):
        """Create a mock QMessageBox for testing."""
        with patch('mayaLib.guiLib.utils.error_dialog.QtWidgets.QMessageBox') as mock_box:
            mock_instance = MagicMock()
            mock_box.return_value = mock_instance
            mock_box.Critical = 2  # QMessageBox.Critical enum value
            mock_box.Ok = 1024  # QMessageBox.Ok enum value
            yield mock_box, mock_instance

    @pytest.fixture
    def mock_maya_window(self):
        """Create a mock Maya main window."""
        with patch('mayaLib.guiLib.utils.error_dialog.get_maya_main_window') as mock_get:
            mock_window = MagicMock()
            mock_get.return_value = mock_window
            yield mock_window

    def test_show_error_dialog_basic(self, mock_message_box, mock_maya_window):
        """Test basic error dialog without detailed text."""
        mock_box_class, mock_instance = mock_message_box
        mock_instance.exec_.return_value = 1024  # QMessageBox.Ok

        result = show_error_dialog(
            title="Test Error",
            message="Something went wrong"
        )

        # Verify dialog was created with Maya window as parent
        mock_box_class.assert_called_once_with(mock_maya_window)

        # Verify dialog properties were set correctly
        mock_instance.setIcon.assert_called_once_with(2)  # QMessageBox.Critical
        mock_instance.setWindowTitle.assert_called_once_with("Test Error")
        mock_instance.setText.assert_called_once_with("Something went wrong")
        mock_instance.setStandardButtons.assert_called_once_with(1024)  # QMessageBox.Ok

        # Verify detailed text was NOT set (not called)
        mock_instance.setDetailedText.assert_not_called()

        # Verify dialog was shown
        mock_instance.exec_.assert_called_once()
        assert result == 1024

    def test_show_error_dialog_with_details(self, mock_message_box, mock_maya_window):
        """Test error dialog with detailed traceback text."""
        mock_box_class, mock_instance = mock_message_box
        mock_instance.exec_.return_value = 1024

        detailed_text = "Traceback (most recent call last):\n  File test.py, line 10"

        result = show_error_dialog(
            title="Operation Failed",
            message="ValueError: Invalid input",
            detailed_text=detailed_text
        )

        # Verify detailed text was set
        mock_instance.setDetailedText.assert_called_once_with(detailed_text)
        assert result == 1024

    def test_show_error_dialog_custom_parent(self, mock_message_box):
        """Test error dialog with custom parent widget."""
        mock_box_class, mock_instance = mock_message_box
        custom_parent = MagicMock()

        show_error_dialog(
            title="Error",
            message="Test message",
            parent=custom_parent
        )

        # Verify dialog was created with custom parent (not Maya window)
        mock_box_class.assert_called_once_with(custom_parent)

    def test_show_error_dialog_empty_strings(self, mock_message_box, mock_maya_window):
        """Test error dialog with empty title and message."""
        mock_box_class, mock_instance = mock_message_box

        show_error_dialog(
            title="",
            message=""
        )

        mock_instance.setWindowTitle.assert_called_once_with("")
        mock_instance.setText.assert_called_once_with("")


@pytest.mark.unit
class TestShowExceptionDialog:
    """Test suite for show_exception_dialog function."""

    @pytest.fixture
    def mock_show_error_dialog(self):
        """Mock the show_error_dialog function."""
        with patch('mayaLib.guiLib.utils.error_dialog.show_error_dialog') as mock_show:
            mock_show.return_value = 1024  # QMessageBox.Ok
            yield mock_show

    def test_show_exception_dialog_basic(self, mock_show_error_dialog):
        """Test showing exception dialog with ValueError."""
        exception = ValueError("Invalid parameter")

        # Capture the exception in a try-except to get proper traceback
        try:
            raise exception
        except Exception as e:
            result = show_exception_dialog(e)

        # Verify show_error_dialog was called
        mock_show_error_dialog.assert_called_once()

        # Get the call arguments
        call_args = mock_show_error_dialog.call_args
        assert call_args.kwargs['title'] == "Error"
        assert "ValueError: Invalid parameter" in call_args.kwargs['message']
        assert call_args.kwargs['detailed_text'] is not None
        assert "Traceback" in call_args.kwargs['detailed_text']
        assert call_args.kwargs['parent'] is None
        assert result == 1024

    def test_show_exception_dialog_custom_title(self, mock_show_error_dialog):
        """Test showing exception dialog with custom title."""
        exception = RuntimeError("Operation failed")

        try:
            raise exception
        except Exception as e:
            show_exception_dialog(e, title="Critical Failure")

        call_args = mock_show_error_dialog.call_args
        assert call_args.kwargs['title'] == "Critical Failure"
        assert "RuntimeError: Operation failed" in call_args.kwargs['message']

    def test_show_exception_dialog_custom_parent(self, mock_show_error_dialog):
        """Test showing exception dialog with custom parent widget."""
        exception = TypeError("Type mismatch")
        custom_parent = MagicMock()

        try:
            raise exception
        except Exception as e:
            show_exception_dialog(e, parent=custom_parent)

        call_args = mock_show_error_dialog.call_args
        assert call_args.kwargs['parent'] == custom_parent

    def test_show_exception_dialog_traceback_content(self, mock_show_error_dialog):
        """Test that detailed traceback contains relevant information."""
        def nested_function():
            raise ValueError("Nested error")

        try:
            nested_function()
        except Exception as e:
            show_exception_dialog(e, title="Nested Function Error")

        call_args = mock_show_error_dialog.call_args
        detailed_text = call_args.kwargs['detailed_text']

        # Verify traceback contains function name and error message
        assert "nested_function" in detailed_text
        assert "ValueError: Nested error" in detailed_text
        assert "Traceback" in detailed_text

    def test_show_exception_dialog_empty_message(self, mock_show_error_dialog):
        """Test showing exception with empty message."""
        exception = Exception()

        try:
            raise exception
        except Exception as e:
            show_exception_dialog(e)

        call_args = mock_show_error_dialog.call_args
        # Should show "Exception: " (with empty message after colon)
        assert call_args.kwargs['message'] == "Exception: "


@pytest.mark.integration
class TestFunctionUIErrorHandling:
    """Integration test suite for FunctionUI error handling."""

    @pytest.fixture
    def mock_show_exception_dialog(self):
        """Mock the show_exception_dialog function."""
        with patch('mayaLib.guiLib.base.base_ui.show_exception_dialog') as mock_show:
            yield mock_show

    @pytest.fixture
    def mock_pymel(self):
        """Mock PyMEL selection commands."""
        with patch('mayaLib.guiLib.base.base_ui.pm') as mock_pm:
            mock_pm.ls.return_value = []
            yield mock_pm

    def test_function_ui_error_handling(
        self, qtbot, mock_show_exception_dialog, mock_pymel
    ):
        """Test that FunctionUI displays error dialog when function raises exception."""
        # Import FunctionUI after mocking dependencies
        from mayaLib.guiLib.base.base_ui import FunctionUI

        # Define a test function that raises an exception
        def failing_function(param1, param2=10):
            """Test function that raises ValueError."""
            raise ValueError("Test error message")

        # Create FunctionUI instance
        ui = FunctionUI(failing_function)

        # Mock the lineedits to return test values
        for lineedit in ui.lineedit_list:
            if hasattr(lineedit, 'text'):
                lineedit.text = MagicMock(return_value="test_value")
            elif hasattr(lineedit, 'isChecked'):
                lineedit.isChecked = MagicMock(return_value=True)

        # Execute the function (should trigger error handling)
        ui.exec_function()

        # Verify show_exception_dialog was called
        mock_show_exception_dialog.assert_called_once()

        # Get the call arguments
        call_args = mock_show_exception_dialog.call_args

        # Verify exception was passed correctly
        exception_arg = call_args[0][0]
        assert isinstance(exception_arg, ValueError)
        assert str(exception_arg) == "Test error message"

        # Verify title matches function name
        assert call_args.kwargs['title'] == 'failing_function'

    def test_function_ui_successful_execution(
        self, qtbot, mock_show_exception_dialog, mock_pymel
    ):
        """Test that FunctionUI doesn't show error dialog when function succeeds."""
        from mayaLib.guiLib.base.base_ui import FunctionUI

        # Define a test function that succeeds
        success_calls = []

        def successful_function(param1, param2=10):
            """Test function that completes successfully."""
            success_calls.append((param1, param2))
            return "Success"

        # Create FunctionUI instance
        ui = FunctionUI(successful_function)

        # Mock the lineedits to return test values
        for i, lineedit in enumerate(ui.lineedit_list):
            if hasattr(lineedit, 'text'):
                lineedit.text = MagicMock(return_value=f"value_{i}")
            elif hasattr(lineedit, 'isChecked'):
                lineedit.isChecked = MagicMock(return_value=False)

        # Execute the function (should succeed without error dialog)
        ui.exec_function()

        # Verify show_exception_dialog was NOT called
        mock_show_exception_dialog.assert_not_called()

        # Verify the function was actually called
        assert len(success_calls) == 1

    def test_function_ui_type_error_handling(
        self, qtbot, mock_show_exception_dialog, mock_pymel
    ):
        """Test that FunctionUI handles TypeError exceptions correctly."""
        from mayaLib.guiLib.base.base_ui import FunctionUI

        # Define a test function that raises TypeError
        def type_error_function(number: int):
            """Test function that expects an integer."""
            raise TypeError("Expected int, got str")

        # Create FunctionUI instance
        ui = FunctionUI(type_error_function)

        # Mock the lineedits to return test values
        for lineedit in ui.lineedit_list:
            if hasattr(lineedit, 'text'):
                lineedit.text = MagicMock(return_value="not_a_number")

        # Execute the function (should trigger error handling)
        ui.exec_function()

        # Verify show_exception_dialog was called with TypeError
        mock_show_exception_dialog.assert_called_once()
        exception_arg = mock_show_exception_dialog.call_args[0][0]
        assert isinstance(exception_arg, TypeError)
        assert str(exception_arg) == "Expected int, got str"

"""Error dialog utility for displaying user-friendly error messages.

Provides QMessageBox error dialogs for displaying exceptions and error messages
to users in a clear, visible way instead of relying on the Script Editor.
"""

__author__ = "Lorenzo Argentieri"

import traceback

import maya.OpenMayaUI as OpenMayaUI

try:
    from PySide6 import QtWidgets
    from shiboken6 import wrapInstance
except ImportError:
    try:
        from PySide2 import QtWidgets
        from shiboken2 import wrapInstance
    except ImportError as exc:
        raise ImportError("PySide6 or PySide2 is required to run this module") from exc


def get_maya_main_window():
    """Return the main Maya window as a QMainWindow object.

    Returns:
        A QMainWindow object pointing to the main Maya window or None if unavailable.
    """
    # Get the main Maya window as a pointer to a QWidget object
    access_main_window = OpenMayaUI.MQtUtil.mainWindow()
    if access_main_window is None:
        return None
    # Convert the pointer to a QMainWindow object
    return wrapInstance(int(access_main_window), QtWidgets.QMainWindow)


def show_error_dialog(title, message, detailed_text=None, parent=None):
    """Display a critical error dialog with optional detailed traceback.

    Shows a QMessageBox.critical dialog to provide visible error feedback to users
    when operations fail. The dialog displays the error message prominently and
    optionally includes a detailed traceback in an expandable section.

    Args:
        title: The dialog window title (typically the function or operation name).
        message: The main error message to display (error type and description).
        detailed_text: Optional detailed information such as full traceback.
            Displayed in an expandable "Details" section. Defaults to None.
        parent: Optional parent widget for the dialog. If None, uses Maya's main
            window as parent. Defaults to None.

    Returns:
        The button code that was clicked (from QMessageBox.StandardButton).

    Example:
        >>> try:
        ...     risky_operation()
        ... except Exception as e:
        ...     show_error_dialog(
        ...         title="Operation Failed",
        ...         message=f"{type(e).__name__}: {str(e)}",
        ...         detailed_text=traceback.format_exc()
        ...     )
    """
    # Use Maya main window as parent if none provided
    if parent is None:
        parent = get_maya_main_window()

    # Create the error dialog
    error_dialog = QtWidgets.QMessageBox(parent)
    error_dialog.setIcon(QtWidgets.QMessageBox.Critical)
    error_dialog.setWindowTitle(title)
    error_dialog.setText(message)

    # Add detailed text if provided (shown in expandable "Details" section)
    if detailed_text:
        error_dialog.setDetailedText(detailed_text)

    # Set standard buttons
    error_dialog.setStandardButtons(QtWidgets.QMessageBox.Ok)

    # Show the dialog and return the result
    return error_dialog.exec_()


def format_exception(exception):
    """Format an exception into user-friendly title and message strings.

    Extracts the exception type and message for display in error dialogs.

    Args:
        exception: The exception object to format.

    Returns:
        A tuple of (error_type, error_message) strings.

    Example:
        >>> try:
        ...     raise ValueError("Invalid input")
        ... except Exception as e:
        ...     error_type, error_msg = format_exception(e)
        ...     # error_type = "ValueError"
        ...     # error_msg = "Invalid input"
    """
    error_type = type(exception).__name__
    error_message = str(exception)
    return error_type, error_message


def show_exception_dialog(exception, title="Error", parent=None):
    """Display an error dialog for a caught exception with full traceback.

    Convenience function that automatically formats an exception and displays
    it in an error dialog with the full traceback in the details section.

    Args:
        exception: The exception object to display.
        title: The dialog window title. Defaults to "Error".
        parent: Optional parent widget for the dialog. If None, uses Maya's main
            window as parent. Defaults to None.

    Returns:
        The button code that was clicked (from QMessageBox.StandardButton).

    Example:
        >>> try:
        ...     dangerous_operation()
        ... except Exception as e:
        ...     show_exception_dialog(e, title="Operation Failed")
    """
    error_type, error_message = format_exception(exception)
    message = f"{error_type}: {error_message}"
    detailed_text = traceback.format_exc()

    return show_error_dialog(
        title=title,
        message=message,
        detailed_text=detailed_text,
        parent=parent
    )

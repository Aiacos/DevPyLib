"""Qt and Maya window integration utilities.

Provides functions for getting Maya main window and integrating
Qt widgets with Maya's UI system.
"""

__author__ = "Lorenzo Argentieri"

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


class PyQtMayaWindow(QtWidgets.QMainWindow):
    """Qt main window integrated with Maya's UI system.

    Provides a base class for creating PySide/PySide6 windows that integrate seamlessly
    with Maya's main window and UI system. Automatically detects and connects to Maya's
    main window as parent if not specified, allowing custom Qt widgets to be embedded
    in Maya's interface.

    Attributes:
        parent: Parent widget (defaults to Maya main window)
        unique_handle: Unique identifier string for the window

    Example:
        >>> class MyWindow(PyQtMayaWindow):
        ...     def set_window(self):
        ...         # Add custom widgets here
        ...         layout = QtWidgets.QVBoxLayout()
        ...         button = QtWidgets.QPushButton("Click Me")
        ...         self.setCentralWidget(button)
        >>> window = MyWindow()
        >>> window.show()
    """
    def __init__(self, parent=None, unique_handle="PyQtWindow"):
        """Initialize PyQtMayaWindow.

        Args:
            parent: The parent window. Defaults to the main Maya window.
            unique_handle: A unique handle for the window. Defaults to 'PyQtWindow'.

        Returns:
            None
        """
        # Initialize the superclass (QMainWindow)
        super(PyQtMayaWindow, self).__init__(parent or get_maya_main_window())

        # Set the window title
        self.setWindowTitle("PyQt Window")

        # Set the object name for this window so that it can be found with Maya's ui command
        self.setObjectName(unique_handle)

        # Set the window size
        self.resize(400, 200)

        # Add PyQt window controls here in inherited classes
        self.set_window()

    def set_window(self):
        """Set up window controls and layout.

        Override this method in subclasses to add PyQt widgets, layouts,
        and other UI elements to the window.
        """
        # add PyQt window controls here in inherited classes
        pass


if __name__ == "__main__":
    PyQtMayaWindow()

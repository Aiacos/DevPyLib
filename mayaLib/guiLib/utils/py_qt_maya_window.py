__author__ = "Lorenzo Argentieri"

"""Qt and Maya window integration utilities.

Provides functions for getting Maya main window and integrating
Qt widgets with Maya's UI system.
"""

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
    accessMainWindow = OpenMayaUI.MQtUtil.mainWindow()
    if accessMainWindow is None:
        return None
    # Convert the pointer to a QMainWindow object
    return wrapInstance(int(accessMainWindow), QtWidgets.QMainWindow)


class PyQtMayaWindow(QtWidgets.QMainWindow):
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
        # add PyQt window controls here in inherited classes
        pass


if __name__ == "__main__":
    PyQtMayaWindow()

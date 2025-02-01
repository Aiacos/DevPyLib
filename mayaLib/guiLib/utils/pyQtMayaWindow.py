__author__ = 'Lorenzo Argentieri'

import maya.OpenMayaUI as omui
# from PyQt4 import QtCore
# from PyQt4 import QtGui
from PySide2 import QtWidgets
from shiboken2 import wrapInstance


def getMayaMainWindow():
    """Return the main Maya window as a QMainWindow object.

    Returns:
        A QMainWindow object pointing to the main Maya window.
    """
    # Get the main Maya window as a pointer to a QWidget object
    accessMainWindow = omui.MQtUtil.mainWindow()
    # Convert the pointer to a QMainWindow object
    return wrapInstance(int(accessMainWindow), QtWidgets.QMainWindow)


class PyQtMayaWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=getMayaMainWindow(), uniqueHandle='PyQtWindow'):
        """Initialize PyQtMayaWindow.

        Args:
            parent: The parent window. Defaults to the main Maya window.
            uniqueHandle: A unique handle for the window. Defaults to 'PyQtWindow'.

        Returns:
            None
        """
        # Initialize the superclass (QMainWindow)
        super(PyQtMayaWindow, self).__init__(parent)

        # Set the window title
        self.setWindowTitle('PyQt Window')

        # Set the object name for this window so that it can be found with Maya's ui command
        self.setObjectName(uniqueHandle)

        # Set the window size
        self.resize(400, 200)

        # Add PyQt window controls here in inherited classes
        self.setWindow()

    def setWindow(self):
        # add PyQt window controls here in inherited classes
        pass


if __name__ == "__main__":
    PyQtMayaWindow()

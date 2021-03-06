__author__ = 'Lorenzo Argentieri'

#from PyQt4 import QtCore
#from PyQt4 import QtGui
from PySide2 import QtCore, QtWidgets, QtGui
from shiboken2 import wrapInstance
import maya.OpenMayaUI as omui


def getMayaMainWindow():
    accessMainWindow = omui.MQtUtil.mainWindow()
    return wrapInstance(long(accessMainWindow), QtWidgets.QMainWindow)

class PyQtMayaWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=getMayaMainWindow(), uniqueHandle='PyQtWindow'):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.setWindowTitle('PyQt Window')
        self.setObjectName(uniqueHandle)

        self.resize(400, 200)
        self.setWindow()

    def setWindow(self):
        # add PyQt window controls here in inherited classes
        pass

if __name__ == "__main__":
    PyQtMayaWindow()
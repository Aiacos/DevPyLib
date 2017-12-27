__author__ = 'Lorenzo Argentieri'

#from PyQt4 import QtCore
#from PyQt4 import QtGui
from mayaLib.guiLib.Qt import QtCore, QtWidgets
import sip
import maya.OpenMayaUI as omui


def getMayaMainWindow():
    accessMainWindow = omui.MQtUtil.mainWindow()
    return sip.wrapinstance(long(accessMainWindow), QtCore.QObject)

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
    pass
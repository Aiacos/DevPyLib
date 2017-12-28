__author__ = 'Lorenzo Argentieri'

from mayaLib.utility.Qt import QtCore, QtWidgets
from shiboken2 import wrapInstance
import maya.OpenMayaUI as omui
from maya import mel


class MenuLibWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(MenuLibWidget, self).__init__(parent)

        self.layout = QtWidgets.QGridLayout()
        self.setLayout(self.layout)

        # search bar
        self.searchLineEdit = QtWidgets.QLineEdit()
        self.layout.addWidget(self.searchLineEdit)

        # update Button
        #self.updateButton = QtWidgets.QPushButton()

        # reload Button
        #self.reloadButton = QtWidgets.QPushButton()


class MainMenu(QtWidgets.QWidget):
    def __init__(self, menuName='MayaLib', parent=None):
        super(MainMenu, self).__init__(parent)

        self.wAction = QtWidgets.QWidgetAction(self)
        self.libWindow = MenuLibWidget() # ql
        self.wAction.setDefaultWidget(self.libWindow)

        widgetStr = mel.eval('string $tempString = $gMainWindow')
        ptr = omui.MQtUtil.findControl(widgetStr)
        menuWidget = wrapInstance(long(ptr), QtWidgets.QMainWindow)
        self.mayaMenu = menuWidget.menuBar()
        self.libMenu = self.mayaMenu.addMenu(menuName)

        self.libMenu.addAction(self.wAction)


if __name__ == "__main__":
    menuPanel = MainMenu()
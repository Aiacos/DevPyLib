__author__ = 'Lorenzo Argentieri'

from mayaLib.utility.Qt import QtCore, QtWidgets, QtGui
from shiboken2 import wrapInstance
import maya.OpenMayaUI as omui
from maya import mel


class MenuLibWidget(QtWidgets.QWidget):
    def __init__(self, libPath, parent=None):
        super(MenuLibWidget, self).__init__(parent)

        # set layout
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addStretch(1)
        self.setLayout(self.layout)

        # add menu
        self.mainMenu = self.addMenuBar()
        self.layout.addWidget(self.mainMenu)

        # search bar
        self.searchLineEdit = QtWidgets.QLineEdit()
        self.layout.addWidget(self.searchLineEdit)

        # update Button
        self.updateButton = self.addIconButton('update', libPath + '/mayaLib/icons/update.png')
        self.reloadButton = self.addIconButton('reload', libPath + '/mayaLib/icons/reload.png')

        self.layout.addWidget(self.reloadButton)
        self.layout.addWidget(self.updateButton)
        # self.buttonLayout = QtWidgets.QHBoxLayout()
        #self.layout.addlayout(self.buttonLayout)


        self.show()

    def addIconButton(self, name, imgPath):
        icon = QtGui.QPixmap(imgPath)
        button = QtWidgets.QPushButton()
        button.setIcon(icon)
        button.setToolTip(name)

        return button

    def addMenuBar(self):
        mainMenu = QtWidgets.QMenuBar(self)

        discipline = ['Modelling', 'Rigging', 'Animation', 'Vfx', 'Compositing']
        for disci in discipline:
            fileMenu = mainMenu.addMenu('&' + disci)
            fileMenu.addAction(self.addMenuAction(disci))

        return mainMenu

    def addMenuAction(self, discipline):
        extractAction = QtWidgets.QAction('test', self)
        #extractAction.setShortcut("Ctrl+Q")
        #extractAction.setStatusTip('Leave The App')
        #extractAction.triggered.connect(self.close_application)

        return extractAction

    def addFuncButton(self):
        index = self.layout.count()
        self.layout.insertWidget(index-1, self.reloadButton)




class MainMenu(QtWidgets.QWidget):
    def __init__(self, libPath, menuName='MayaLib', parent=None):
        super(MainMenu, self).__init__(parent)

        self.wAction = QtWidgets.QWidgetAction(self)
        self.libWindow = MenuLibWidget(libPath) # ql
        self.wAction.setDefaultWidget(self.libWindow)

        widgetStr = mel.eval('string $tempString = $gMainWindow')
        ptr = omui.MQtUtil.findControl(widgetStr)
        menuWidget = wrapInstance(long(ptr), QtWidgets.QMainWindow)
        self.mayaMenu = menuWidget.menuBar()
        self.libMenu = self.mayaMenu.addMenu(menuName)

        self.libMenu.addAction(self.wAction)


if __name__ == "__main__":
    menuPanel = MainMenu('/Users/lorenzo/Dropbox/3D/Maya/Script_DEF/DevPyLib')
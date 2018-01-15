__author__ = 'Lorenzo Argentieri'

#from mayaLib.utility.Qt import QtCore, QtWidgets, QtGui
from PySide2 import QtCore, QtWidgets, QtGui
from shiboken2 import wrapInstance
import maya.OpenMayaUI as omui
from maya import mel

import mayaLib
from mayaLib.pipelineLib.utility import listFunction as lm
from mayaLib.pipelineLib.utility import docs as doc
from mayaLib.guiLib.base import baseUI as ui

import inspect


class MenuLibWidget(QtWidgets.QWidget):
    def __init__(self, libPath, parent=None):
        super(MenuLibWidget, self).__init__(parent)

        self.libStructure = lm.StructureManager(mayaLib)
        self.libDict = self.libStructure.getStructLib()['mayaLib']

        # set layout
        self.layout = QtWidgets.QVBoxLayout()
        #self.layout.addStretch(1)
        self.setLayout(self.layout)

        # add menu
        self.mainMenu = self.addMenuBar()
        self.layout.addWidget(self.mainMenu)

        # search bar
        self.searchLineEdit = QtWidgets.QLineEdit()
        self.layout.addWidget(self.searchLineEdit)

        # Docs Label
        self.docLabel = QtWidgets.QLabel()
        self.docLabel.setStyleSheet("background-color: rgb(90,90,90); border-radius: 5px; border:1px solid rgb(255, 255, 255); ")
        self.layout.addWidget(self.docLabel)
        self.docLabel.setText('')

        # update Button
        self.updateButton = self.addIconButton('update', libPath + '/mayaLib/icons/update.png')
        self.reloadButton = self.addIconButton('reload', libPath + '/mayaLib/icons/reload.png')

        self.buttonLayout = QtWidgets.QHBoxLayout()
        self.buttonLayout.addWidget(self.reloadButton)
        self.buttonLayout.addWidget(self.updateButton)
        self.layout.addLayout(self.buttonLayout)

        # Connect
        self.reloadButton.clicked.connect(self.reloaded)


        self.show()

    def reloaded(self):
        reload(mayaLib)
        self.docLabel.setText('Lib Reloaded!')

    def addIconButton(self, name, imgPath):
        icon = QtGui.QPixmap(imgPath)
        button = QtWidgets.QPushButton()
        button.setIcon(icon)
        button.setToolTip(name)

        return button

    def addMenuBar(self):
        mainMenu = QtWidgets.QMenuBar(self)

        discipline = ['Modelling', 'Rigging', 'Animation', 'Vfx', 'Lighting']
        for disci in discipline:
            fileMenu = mainMenu.addMenu('&' + disci)
            #fileMenu.addAction(self.addMenuAction(disci))
            for action in self.addMultipleMenuAction(fileMenu, disci):
                fileMenu.addAction(action)

        return mainMenu

    def buttonHover(self, text):
        self.docLabel.setText(text)

    def buttonClicked(self, func):
        self.functionWindow = None
        try:
            self.functionWindow = ui.FunctionUI(func)
            self.functionWindow.show()
        except:
            func()

    def addMenuAction(self, discipline, function):
        extractAction = QtWidgets.QAction(discipline, self)
        #extractAction.setShortcut("Ctrl+Q")
        #extractAction.setStatusTip('Leave The App')


        extractAction.triggered.connect(lambda: self.buttonClicked(function))

        docText = doc.getDocs(function)
        extractAction.hovered.connect(lambda: self.buttonHover(docText))

        return extractAction

    def addSubMenu(self, upMenu, lib):
        libname = lib.replace('Lib', '').title()
        return upMenu.addMenu(libname)

    def addRecursiveMenu(self, upMenu, libDict):
        for key, value in libDict.iteritems():
            if isinstance(value,dict):
                subMenu = self.addSubMenu(upMenu, key)
                self.addRecursiveMenu(subMenu, value)

            else:
                classString = value.split('.')
                module = '.'.join(classString[:-1])
                func = self.libStructure.importAndExec(module, key)
                upMenu.addAction(self.addMenuAction(key, func))

            # ToDo: use subMenu and call importAndExec


    def addMultipleMenuAction(self, upMenu, discipline):
        action_list = []
        if discipline == 'Modelling':
            pass
        elif discipline == 'Rigging':
            pass
        elif discipline == 'animLib':
            pass
        elif discipline == 'Vfx':
            libMenu = self.addSubMenu(upMenu, 'fluidLib')
            self.addRecursiveMenu(libMenu, self.libDict['fluidLib'])

        elif discipline == 'Lighting':
            pass

        return action_list


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

    def __del__(self):
        self.libMenu.deleteLater()


if __name__ == "__main__":
    menuPanel = MainMenu('/Users/lorenzo/Dropbox/3D/Maya/Script_DEF/DevPyLib')

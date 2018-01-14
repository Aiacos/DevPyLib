__author__ = 'Lorenzo Argentieri'

#from mayaLib.utility.Qt import QtCore, QtWidgets, QtGui
from PySide2 import QtCore, QtWidgets, QtGui
from shiboken2 import wrapInstance
import maya.OpenMayaUI as omui
from maya import mel

import mayaLib
import mayaLib.pipelineLib.utility.listFunction as lm


class MenuLibWidget(QtWidgets.QWidget):
    def __init__(self, libPath, parent=None):
        super(MenuLibWidget, self).__init__(parent)

        self.libStructure = lm.StructureManager(mayaLib)
        self.libDict = self.libStructure.getStructLib()

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
        self.docLabel.setText('Test')

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
        print 'Lib Reloaded!'

    def addIconButton(self, name, imgPath):
        icon = QtGui.QPixmap(imgPath)
        button = QtWidgets.QPushButton()
        button.setIcon(icon)
        button.setToolTip(name)

        return button

    def addMenuBar(self):
        mainMenu = QtWidgets.QMenuBar(self)

        libKeys = self.libStructure.getStructLib().iterkeys()
        discipline = ['Modelling', 'Rigging', 'Animation', 'Vfx', 'Lighting']
        for disci in discipline:
            fileMenu = mainMenu.addMenu('&' + disci)
            #fileMenu.addAction(self.addMenuAction(disci))
            for action in self.addMultipleMenuAction(fileMenu, disci):
                fileMenu.addAction(action)

        return mainMenu

    def addMenuAction(self, discipline, function):
        extractAction = QtWidgets.QAction(discipline, self)
        #extractAction.setShortcut("Ctrl+Q")
        #extractAction.setStatusTip('Leave The App')
        extractAction.triggered.connect(function)
        #extractAction.hovered.connect(self.docLabel.setText('CIAO'))

        return extractAction

    def addSubMenu(self, upMenu, lib):
        libname = lib.replace('Lib', '').title()
        return upMenu.addMenu(libname)

    def addItemToMenu(self, dict, subMenu):
        for key, value in dict.iteritems():
            for k, v in value.iteritems():
                if isinstance(v, str):
                    classString = v.split('.')
                    module = '.'.join(classString[:-1])
                    func = self.libStructure.importAndExec(module, k)
                    subMenu.addAction(self.addMenuAction(k, func))

    def addRecursiveMenu(self, upMenu, lib):
        for key, value in self.libDict[lib].iteritems():
            if isinstance(value,dict):
                subMenu = self.addSubMenu(upMenu, key)
                self.addItemToMenu(value, subMenu)

            else:
                action = self.addMenuAction(key, value)
                upMenu.addAction(action)
                print 'aggiunta zione'

        return subMenu

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
            self.addRecursiveMenu(libMenu, 'fluidLib')

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


if __name__ == "__main__":
    menuPanel = MainMenu('/Users/lorenzo/Dropbox/3D/Maya/Script_DEF/DevPyLib')
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


class SearchLineEdit(QtWidgets.QLineEdit):

    #buttonClicked = QtCore.pyqtSignal(bool)
    speak = QtCore.Signal(str)

    def __init__(self, icon_file, parent=None):
        super(SearchLineEdit, self).__init__(parent)

        self.button = QtWidgets.QToolButton(self)
        self.button.setIcon(QtGui.QIcon(icon_file))
        self.button.setStyleSheet('border: 0px; padding: 0px;')
        self.button.setCursor(QtCore.Qt.ArrowCursor)
        self.button.clicked.connect(self.clear) #self.buttonClicked.emit

        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(self.button,0,QtCore.Qt.AlignRight)
        layout.setSpacing(0)
        layout.setMargin(5)

        frameWidth = self.style().pixelMetric(QtWidgets.QStyle.PM_DefaultFrameWidth)
        buttonSize = self.button.sizeHint()

        self.setStyleSheet('QLineEdit {padding-right: %dpx; }' % (buttonSize.width() + frameWidth + 1))
        self.setMinimumSize(max(self.minimumSizeHint().width(), buttonSize.width() + frameWidth*2 + 3),
                            max(self.minimumSizeHint().height(), buttonSize.height() + frameWidth*2 + 3))

        self.textChanged.connect(self.replaceText)

    def replaceText(self):
        text = self.text()
        text_list = text.split(' ')
        newtext = '*'.join(text_list)
        self.setText(newtext)

        self.speak.emit(newtext)


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
        self.searchLineEdit = SearchLineEdit(libPath + '/mayaLib/icons/close.png')
        self.layout.addWidget(self.searchLineEdit)

        # WidgetList
        self.buttonListWidget = QtWidgets.QListWidget()
        self.buttonListWidget.setFocusPolicy(QtCore.Qt.NoFocus)
        self.buttonListWidget.setStyleSheet('background: transparent;')
        self.buttonListWidget.setResizeMode(QtWidgets.QListView.Adjust)
        #self.buttonListWidget.resize(1, 1)

        self.layout.addWidget(self.buttonListWidget)

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
        #self.updateButton.clicked.connect(self.reloaded)
        self.searchLineEdit.speak.connect(lambda: self.buildButtonList(self.searchLineEdit.text()))


        self.show()


    def buildButtonList(self, text):
        if self.buttonListWidget.count() > 0:
            self.buttonListWidget.clear()

        doc_text = []
        text_list = text.split('*')
        for libstr in self.libStructure.finalClassList:
            str_match = [True for match in text_list if match in libstr]

            if True in str_match:
                doc_text.append(libstr)
                tt = '\n'.join(doc_text)
                self.docLabel.setText(tt)
                classString = libstr.split('.')
                module = '.'.join(classString[:-1])
                key = classString[-1]

                button = QtWidgets.QPushButton(key)
                buttonQListWidgetItem = QtWidgets.QListWidgetItem(self.buttonListWidget)
                buttonQListWidgetItem.setSizeHint(button.sizeHint())
                self.buttonListWidget.addItem(buttonQListWidgetItem)
                self.buttonListWidget.setItemWidget(buttonQListWidgetItem, button)

                button.setToolTip(libstr)
                func = self.libStructure.importAndExec(module, key)
                #docText = doc.getDocs(func)
                #button.hovered.connect(lambda: self.buttonHover(docText))

                button.clicked.connect(lambda: self.buttonClicked(func))

        if text == '':
            self.docLabel.setText('')
            if self.buttonListWidget.count() > 0:
                self.buttonListWidget.clear()





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

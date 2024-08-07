__author__ = 'Lorenzo Argentieri'

import os
import types

import maya.OpenMayaUI as omui
import pathlib
# from mayaLib.utility.Qt import QtCore, QtWidgets, QtGui
from PySide2 import QtCore, QtWidgets, QtGui
from PySide2.QtCore import QObject, SIGNAL
from maya import mel
from shiboken2 import wrapInstance

import mayaLib
from mayaLib.guiLib.base import baseUI as ui
from mayaLib.pipelineLib.utility import docs as doc
from mayaLib.pipelineLib.utility import libManager
from mayaLib.pipelineLib.utility import listFunction as lm
import importlib


class SearchLineEdit(QtWidgets.QLineEdit):
    # buttonClicked = QtCore.pyqtSignal(bool)
    speak = QtCore.Signal(str)

    def __init__(self, icon_file, parent=None):
        super(SearchLineEdit, self).__init__(parent)

        self.button = QtWidgets.QToolButton(self)
        self.button.setIcon(QtGui.QIcon(icon_file))
        self.button.setStyleSheet('border: 0px; padding: 0px;')
        self.button.setCursor(QtCore.Qt.ArrowCursor)
        self.button.clicked.connect(self.clear)  # self.buttonClicked.emit

        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(self.button, 0, QtCore.Qt.AlignRight)
        layout.setSpacing(0)
        layout.setMargin(5)

        frameWidth = self.style().pixelMetric(QtWidgets.QStyle.PM_DefaultFrameWidth)
        buttonSize = self.button.sizeHint()

        self.setStyleSheet('QLineEdit {padding-right: %dpx; }' % (buttonSize.width() + frameWidth + 1))
        self.setMinimumSize(max(self.minimumSizeHint().width(), buttonSize.width() + frameWidth * 2 + 3),
                            max(self.minimumSizeHint().height(), buttonSize.height() + frameWidth * 2 + 3))

        self.textChanged.connect(self.replaceText)

    def replaceText(self):
        text = self.text()
        text_list = text.split(' ')
        newtext = '*'.join(text_list)

        if newtext != text:
            self.setText(newtext)

        self.speak.emit(newtext)


class MenuLibWidget(QtWidgets.QWidget):
    updateWidget = QtCore.Signal()

    def __init__(self, libPath, parent=None):
        super(MenuLibWidget, self).__init__(parent)

        libPath = pathlib.Path(libPath)

        close_icon_path = libPath / 'mayaLib' / 'icons' / 'close.png'
        update_icon_path = libPath / 'mayaLib' / 'icons' / 'update.png'
        reload_icon_path = libPath / 'mayaLib' / 'icons' / 'reload.png'

        self.libStructure = lm.StructureManager(mayaLib)
        self.libDict = self.libStructure.getStructLib()['mayaLib']

        # set layout
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        # add menu
        self.mainMenu = self.addMenuBar()
        self.layout.addWidget(self.mainMenu)

        # search bar
        self.searchLineEdit = SearchLineEdit(str(close_icon_path))
        self.layout.addWidget(self.searchLineEdit)

        # WidgetList
        self.buttonItemList = []
        self.buttonListWidget = QtWidgets.QListWidget()
        self.buttonListWidget.setStyleSheet('background: transparent;')
        self.buttonListWidget.setFocusPolicy(QtCore.Qt.NoFocus)
        self.buttonListWidget.adjustSize()
        # self.buttonListWidget.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.buttonListWidget.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding,
                                            QtWidgets.QSizePolicy.MinimumExpanding)
        # self.buttonListWidget.setSizeAdjustPolicy(QtWidgets.QListWidget.AdjustToContents)
        # self.buttonListWidget.setResizeMode(QtWidgets.QListView.Adjust)
        # self.buttonListWidget.setMinimumHeight(75)
        # self.buttonListWidget.setMaximumHeight(100)
        self.layout.addWidget(self.buttonListWidget)

        # Docs Label
        self.docLabel = QtWidgets.QLabel()
        self.docLabel.setStyleSheet(
            "background-color: rgb(90,90,90); border-radius: 5px; border:1px solid rgb(255, 255, 255); ")
        self.layout.addWidget(self.docLabel)
        self.docLabel.setText('')

        # update Button
        self.updateButton = self.addIconButton('update', str(update_icon_path))
        self.reloadButton = self.addIconButton('reload', str(reload_icon_path))

        self.buttonLayout = QtWidgets.QHBoxLayout()
        self.buttonLayout.addWidget(self.reloadButton)
        self.buttonLayout.addWidget(self.updateButton)
        self.layout.addLayout(self.buttonLayout)

        # Connect
        self.reloadButton.clicked.connect(self.reloaded)
        self.updateButton.clicked.connect(self.download)
        self.searchLineEdit.speak.connect(lambda: self.buildButtonList(self.searchLineEdit.text()))
        self.buttonListWidget.itemClicked.connect(self.listWidgetButtonClick)

        self.show()

    def listWidgetButtonClick(self, item):
        libstr = item.toolTip()
        classString = libstr.split('.')
        module = '.'.join(classString[:-1])
        key = classString[-1]
        func = self.libStructure.importAndExec(module, key)
        self.buttonClicked(func)

    def buildButtonList(self, text):
        if self.buttonListWidget.count() > 0 or text == '':
            self.buttonListWidget.clear()
            del self.buttonItemList[:]

        doc_text = []
        text_list = text.split('*')
        for libstr in self.libStructure.finalClassList:
            str_match = [True for match in text_list if match in libstr]

            if True in str_match:
                doc_text.append(libstr)
                tt = '\n'.join(doc_text)
                self.docLabel.setText(tt)
                classString = libstr.split('.')
                key = classString[-1]

                buttonQListWidgetItem = QtWidgets.QListWidgetItem(key)
                buttonQListWidgetItem.setToolTip(libstr)
                self.buttonItemList.append(buttonQListWidgetItem)
                self.buttonListWidget.addItem(self.buttonItemList[-1])

        if text == '':
            self.docLabel.setText('')
            if self.buttonListWidget.count() > 0:
                self.buttonListWidget.clear()

        self.buttonListWidget.adjustSize()

    def reloaded(self):
        self.updateWidget.emit()

    def download(self):
        lib = libManager.InstallLibrary()
        lib.download()

        self.reloaded()

    def addIconButton(self, name, imgPath):
        icon = QtGui.QPixmap(imgPath)
        button = QtWidgets.QPushButton()
        button.setIcon(icon)
        button.setToolTip(name)

        return button

    def addMenuBar(self):
        mainMenu = QtWidgets.QMenuBar(self)

        discipline = ['Modelling', 'Rigging', 'Animation', 'Vfx', 'Lookdev']
        for disci in discipline:
            fileMenu = mainMenu.addMenu('&' + disci)
            # fileMenu.addAction(self.addMenuAction(disci))
            for action in self.addMultipleMenuAction(fileMenu, disci):
                fileMenu.addAction(action)

        return mainMenu

    def buttonHover(self, text):
        self.docLabel.setText(text)

    def buttonClicked(self, func):
        self.functionWindow = None
        # try:
        self.functionWindow = ui.FunctionUI(func)
        self.functionWindow.show()
        self.functionWindow.setFocus()
        # except:
        #    func()

    def addMenuAction(self, discipline, function):
        extractAction = QtWidgets.QAction(discipline, self)
        # extractAction.setShortcut("Ctrl+Q")
        # extractAction.setStatusTip('Leave The App')

        extractAction.triggered.connect(lambda: self.buttonClicked(function))

        docText = doc.getDocs(function)
        extractAction.hovered.connect(lambda: self.buttonHover(docText))

        return extractAction

    def addSubMenu(self, upMenu, lib):
        libname = lib.replace('Lib', '').title()
        return upMenu.addMenu(libname)

    def addRecursiveMenu(self, upMenu, libDict):
        for key, value in libDict.items():
            if isinstance(value, dict):
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
            libMenu = self.addSubMenu(upMenu, 'modelLib')
            self.addRecursiveMenu(libMenu, self.libDict['modelLib'])
        elif discipline == 'Rigging':
            libMenu = self.addSubMenu(upMenu, 'rigLib')
            self.addRecursiveMenu(libMenu, self.libDict['rigLib'])
        elif discipline == 'Animation':
            libMenu = self.addSubMenu(upMenu, 'animationLib')
            self.addRecursiveMenu(libMenu, self.libDict['animationLib'])
        elif discipline == 'Vfx':
            libMenu = self.addSubMenu(upMenu, 'fluidLib')
            self.addRecursiveMenu(libMenu, self.libDict['fluidLib'])
        elif discipline == 'Lookdev':
            libMenu = self.addSubMenu(upMenu, 'lookdevLib')
            self.addRecursiveMenu(libMenu, self.libDict['lookdevLib'])
            libMenu = self.addSubMenu(upMenu, 'shaderLib')
            self.addRecursiveMenu(libMenu, self.libDict['shaderLib'])

        return action_list


class MainMenu(QtWidgets.QWidget):
    def __init__(self, libPath, menuName='MayaLib', parent=None):
        super(MainMenu, self).__init__(parent)

        self.wAction = QtWidgets.QWidgetAction(self)
        self.libWindow = MenuLibWidget(libPath)  # ql
        self.wAction.setDefaultWidget(self.libWindow)

        widgetStr = mel.eval('string $tempString = $gMainWindow')
        ptr = omui.MQtUtil.findControl(widgetStr)
        menuWidget = wrapInstance(int(ptr), QtWidgets.QMainWindow)
        self.mayaMenu = menuWidget.menuBar()

        if menuName not in [m.text for m in self.mayaMenu.actions()]:
            self.libMenu = self.mayaMenu.addMenu(menuName)

            self.libMenu.addAction(self.wAction)

            QObject.connect(self.libWindow, SIGNAL('updateWidget()'), lambda: self.updateWidget(libPath))
            self.libMenu.triggered.connect(self.showWidget)

    def updateWidget(self, libPath):
        reload_package(mayaLib)
        self.libMenu.removeAction(self.wAction)
        self.libWindow.destroy()
        # self.wAction.deleteWidget()
        # self.libMenu.clear()

        self.wAction = QtWidgets.QWidgetAction(self)
        self.libWindow = MenuLibWidget(libPath)  # ql
        self.wAction.setDefaultWidget(self.libWindow)

        self.libMenu.addAction(self.wAction)
        QObject.connect(self.libWindow, SIGNAL('updateWidget()'), lambda: self.updateWidget(libPath))
        self.libMenu.triggered.connect(self.showWidget)
        print('Reloaded MayaLib!')

    def showWidget(self):
        self.libWindow.adjustSize()

    def __del__(self):
        self.libMenu.deleteLater()


def reload_package(package):
    assert (hasattr(package, "__package__"))
    fn = package.__file__
    fn_dir = os.path.dirname(fn) + os.sep
    module_visit = {fn}
    del fn

    def reload_recursive_ex(module):
        # importlib.reload(module)
        importlib.reload(module)

        for module_child in list(vars(module).values()):
            if isinstance(module_child, types.ModuleType):
                fn_child = getattr(module_child, "__file__", None)
                if (fn_child is not None) and fn_child.startswith(fn_dir):
                    if fn_child not in module_visit:
                        # print("reloading:", fn_child, "from", module)
                        module_visit.add(fn_child)
                        reload_recursive_ex(module_child)

    return reload_recursive_ex(package)


if __name__ == "__main__":
    pass

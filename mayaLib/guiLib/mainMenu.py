__author__ = 'Lorenzo Argentieri'

import mayaLib.guiLib.utils.pyQtMayaWindow as qtmw
from mayaLib.utility.Qt import QtCore, QtWidgets


class MainMenu(QtWidgets.QMainWindow):
    def __init__(self, parent=qtmw.getMayaMainWindow()):
        super(MainMenu, self).__init__(parent)
        self.menubar = self.menuBar()
        fileMenu = self.menubar.addMenu('&File')

        self.layout = QtWidgets.QGridLayout()
        self.setLayout(self.layout)

        # search bar
        self.searchLineEdit = QtWidgets.QLineEdit()
        self.layout.addWidget(self.searchLineEdit)

        # update Button
        #self.updateButton = QtWidgets.QPushButton()

        # reload Button
        #self.reloadButton = QtWidgets.QPushButton()

def print_text():
    print 'hello'

if __name__ == "__main__":
    menuPanel = MainMenu()
__author__ = 'Lorenzo Argentieri'

import pymel.core as pm
import mayaLib.guiLib.base.menu as menu
import mayaLib.pipelineLib.docs as doc
from mayaLib.guiLib.Qt import QtCore, QtWidgets


class MainMenu(QtCore.QObject, menu.Menu):
    def __init__(self, func, parent=None):
        super(MainMenu, self).__init__(parent)
        menu.Menu.__init__(menu_name='mayaLib')
        self.parent = menu.Menu.gMainWindow



        # search bar
        self.searchLineEdit = QtWidgets.QLineEdit()

        # update Button
        #self.updateButton = QtWidgets.QPushButton()

        # reload Button
        #self.reloadButton = QtWidgets.QPushButton()


if __name__ == "__main__":
    menuPanel = MainMenu()
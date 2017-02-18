__author__ = 'Lorenzo Argentieri'

import pymel.core as pm
import maya


class Menu():
    gMainWindow = maya.mel.eval('$tmpVar=$gMainWindow')

    def __init__(self, menu_name='test', parent=gMainWindow):
        self.lib_menu = pm.menu(label=menu_name, parent=parent, tearOff=True)
        self.item = []

    def __del__(self):
        self.lib_menu.delete()

    def add_menuitem(self, item_name, fn):
        """
        Bind function to menuItem
        :param item_name: Label for menuItem (String)
        :param fn: pointer to function (es. def x(); y=x; y() <- this call x())
        :return:
        """
        self.item.append(pm.menuItem(item_name, parent=self.lib_menu.name(), command=fn.__name__+'()'))


def print_text():
    print 'hello test'


if __name__ == "__main__":
    menuPanel = Menu('test')
    menuPanel.add_menuitem('testClickCmd', fn=print_text)
    # try:
    #     lib_menu.delete()
    #     print 'deleted'
    # except:
    #     lib_menu = pm.menu(label='test', tearOff=True)
    #     it4 = pm.menuItem('test1', parent=lib_menu.name())
    #     it5 = pm.menuItem('test2', parent=lib_menu.name())
    #     it6 = pm.menuItem('test3', parent=lib_menu.name())
    #     print 'added'

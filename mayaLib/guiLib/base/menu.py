__author__ = 'Lorenzo Argentieri'

import maya
import pymel.core as pm


class Menu():
    gMainWindow = maya.mel.eval('$tmpVar=$gMainWindow')

    def __init__(self, menu_name='test', parent=gMainWindow):
        self.lib_menu = pm.menu(label=menu_name, parent=parent, tearOff=True)
        self.item = {}

    def __del__(self):
        self.lib_menu.delete()

    def add_menuitem(self, item_name, cmd, parent=None, image=None):
        """
        Bind function to menuItem
        :param item_name: Label for menuItem (String)
        :param cmd: pointer to function (es. def x(); y=x; y() <- this call x())
        :param parent: (String)
        :return:
        """
        if parent is None:
            parent = self.lib_menu.name()

        if image is None:
            self.item[item_name] = pm.menuItem(item_name, p=parent, command=cmd.__name__ + '()')
        else:
            self.item[item_name] = pm.menuItem(item_name, p=parent, command=cmd.__name__ + '()', image=image)

        ret_parent = self.item[item_name]
        return ret_parent.rpartition('|')[-1]

    def add_menuCheckBox(self, item_name, cmd, parent=None):
        """
        Bind function to menuItem
        :param item_name: Label for menuItem (String)
        :param cmd: pointer to function (es. def x(); y=x; y() <- this call x())
        :param parent: (String)
        :return:
        """
        if parent is None:
            parent = self.lib_menu.name()

        self.item[item_name] = pm.menuItem(item_name, p=parent, command=cmd.__name__ + '()', checkBox=True)
        ret_parent = self.item[item_name]
        return ret_parent.rpartition('|')[-1]

    def add_submenu(self, submenu_name, parent=None):
        """
        Add sub menu container
        :param submenu_name: Label for Sub_menuItem (String)
        :param parent: (String)
        :return:
        """
        if parent is None:
            parent = self.lib_menu.name()

        self.item[submenu_name] = pm.menuItem(submenu_name, p=parent, subMenu=True, tearOff=True)
        ret_parent = self.item[submenu_name]
        return ret_parent.rpartition('|')[-1]


def print_text():
    print('hello test')


if __name__ == "__main__":
    menuPanel = Menu('test')
    menuPanel.add_menuitem('testClickCmd', cmd=print_text)
    p = menuPanel.add_submenu('testSubMenu')
    menuPanel.add_menuitem('testSubItem', parent=p, cmd=print_text)
    # try:
    #     lib_menu.delete()
    #     print('deleted')
    # except:
    #     lib_menu = pm.menu(label='test', tearOff=True)
    #     it4 = pm.menuItem('test1', parent=lib_menu.name())
    #     it5 = pm.menuItem('test2', parent=lib_menu.name())
    #     it6 = pm.menuItem('test3', parent=lib_menu.name())
    #     print('added')

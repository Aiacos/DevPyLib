__author__ = 'Lorenzo Argentieri'

import maya
import pymel.core as pm


class Menu():
    gMainWindow = maya.mel.eval('$tmpVar=$gMainWindow')

    def __init__(self, menu_name='test', parent=gMainWindow):
        """Construct a Menu Object

        Args:
            menu_name (str): The name of the menu to be created
            parent (str): The name of the parent menu
        """
        self.lib_menu = pm.menu(
            label=menu_name, parent=parent, tearOff=True)
        self.item = {}

    def __del__(self):
        """Delete the menu when the class is deleted

        This method is called when the class is deleted. It removes the menu
        from Maya's menu bar.
        """
        self.lib_menu.delete()

    def add_menuitem(self, item_name, cmd, parent=None, image=None):
        """Add a menu item to the Maya menu.

        Args:
            item_name (str): Label for the menu item.
            cmd (function): Function to be bound to the menu item.
            parent (str, optional): Parent menu item path. Defaults to None.
            image (str, optional): Path to the image for the menu item. Defaults to None.

        Returns:
            str: Last part of the parent path.
        """
        # Set the parent to the library menu if not provided
        if parent is None:
            parent = self.lib_menu.name()

        # Create a menu item with or without an image
        if image is None:
            self.item[item_name] = pm.menuItem(item_name, p=parent, command=cmd.__name__ + '()')
        else:
            self.item[item_name] = pm.menuItem(item_name, p=parent, command=cmd.__name__ + '()', image=image)

        # Return the last part of the parent path
        ret_parent = self.item[item_name]
        return ret_parent.rpartition('|')[-1]

    def add_menuCheckBox(self, item_name, cmd, parent=None):
        """Bind function to menuItem

        Args:
            item_name (str): Label for menuItem
            cmd (function): Pointer to function (es. def x(); y=x; y() <- this call x())
            parent (str, optional): Defaults to None. Parent menu item path

        Returns:
            str: Last part of the parent path
        """
        if parent is None:
            parent = self.lib_menu.name()

        self.item[item_name] = pm.menuItem(
            item_name, p=parent, command=cmd.__name__ + '()', checkBox=True
        )
        ret_parent = self.item[item_name]
        return ret_parent.rpartition('|')[-1]

    def add_submenu(self, submenu_name, parent=None):
        """Add sub menu container

        Args:
            submenu_name (str): Label for Sub_menuItem
            parent (str, optional): Defaults to None. Parent menu item path

        Returns:
            str: Last part of the parent path
        """
        if parent is None:
            parent = self.lib_menu.name()

        self.item[submenu_name] = pm.menuItem(
            submenu_name, p=parent, subMenu=True, tearOff=True
        )
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

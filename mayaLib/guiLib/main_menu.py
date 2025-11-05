__author__ = "Lorenzo Argentieri"

"""Main menu system for DevPyLib tools.

Provides the MainMenu class that creates dynamic menus with
automatic function discovery and UI generation.
"""

import importlib
import os
import pathlib
import types

import maya.OpenMayaUI as OpenMayaUI
from maya import mel

# from mayaLib.utility.Qt import QtCore, QtWidgets, QtGui

try:
    from PySide6 import QtCore, QtGui, QtWidgets
    from PySide6.QtCore import SIGNAL, QObject
    from PySide6.QtGui import QAction
    from shiboken6 import wrapInstance
except ImportError:
    from PySide2 import QtCore, QtGui, QtWidgets
    from PySide2.QtCore import SIGNAL, QObject
    from PySide2.QtWidgets import QAction
    from shiboken2 import wrapInstance


import mayaLib
from mayaLib.guiLib.base import base_ui as ui
from mayaLib.pipelineLib.utility import docs as doc
from mayaLib.pipelineLib.utility import lib_manager
from mayaLib.pipelineLib.utility import list_function as lm


class SearchLineEdit(QtWidgets.QLineEdit):
    """Custom QLineEdit with a clear button and emits a signal on text change."""

    speak = QtCore.Signal(str)

    def __init__(self, icon_file, parent=None):
        """Initialize the SearchLineEdit.

        Args:
            icon_file (str): Path to the icon for the clear button.
            parent (QWidget, optional): Parent widget. Defaults to None.
        """
        super(SearchLineEdit, self).__init__(parent)

        # Setup clear button
        self.button = QtWidgets.QToolButton(self)
        self.button.setIcon(QtGui.QIcon(icon_file))
        self.button.setStyleSheet("border: 0px; padding: 0px;")
        self.button.setCursor(QtCore.Qt.ArrowCursor)
        self.button.clicked.connect(self.clear)

        # Layout configuration
        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(self.button, 0, QtCore.Qt.AlignRight)
        layout.setSpacing(0)
        if hasattr(layout, "setContentsMargins"):
            layout.setContentsMargins(5, 5, 5, 5)
        else:
            layout.setMargin(5)


        frame_width = self.style().pixelMetric(QtWidgets.QStyle.PM_DefaultFrameWidth)
        button_size = self.button.sizeHint()

        self.setStyleSheet(
            "QLineEdit {padding-right: %dpx; }" % (button_size.width() + frame_width + 1)
        )
        self.setMinimumSize(
            max(
                self.minimumSizeHint().width(), button_size.width() + frame_width * 2 + 3
            ),
            max(
                self.minimumSizeHint().height(),
                button_size.height() + frame_width * 2 + 3,
            ),
        )

        self.textChanged.connect(self.replace_text)

    def replace_text(self):
        """Replace spaces in the input text with asterisks and emit the modified text."""
        text = self.text()
        text_list = text.split(" ")
        newtext = "*".join(text_list)

        if newtext != text:
            self.setText(newtext)

        self.speak.emit(newtext)


class MenuLibWidget(QtWidgets.QWidget):
    """Widget that displays a searchable menu library."""

    update_widget = QtCore.Signal()

    def __init__(self, lib_path, parent=None):
        """Initialize the MenuLibWidget.

        Args:
            lib_path (str): Path to the library.
            parent (QWidget, optional): Parent widget. Defaults to None.
        """
        super(MenuLibWidget, self).__init__(parent)

        lib_path = pathlib.Path(lib_path)

        # Icon paths
        close_icon_path = lib_path / "mayaLib" / "icons" / "close.png"
        update_icon_path = lib_path / "mayaLib" / "icons" / "update.png"
        reload_icon_path = lib_path / "mayaLib" / "icons" / "reload.png"

        self.libStructure = lm.StructureManager(mayaLib)
        self.libDict = self.libStructure.get_struct_lib()["mayaLib"]

        # Setup layout
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        # Add menu bar
        self.mainMenu = self.add_menu_bar()
        self.layout.addWidget(self.mainMenu)

        # Search bar
        self.searchLineEdit = SearchLineEdit(str(close_icon_path))
        self.layout.addWidget(self.searchLineEdit)

        # Widget List
        self.buttonItemList = []
        self.buttonListWidget = QtWidgets.QListWidget()
        self.buttonListWidget.setStyleSheet("background: transparent;")
        self.buttonListWidget.setFocusPolicy(QtCore.Qt.NoFocus)
        self.buttonListWidget.adjustSize()
        self.buttonListWidget.setSizePolicy(
            QtWidgets.QSizePolicy.MinimumExpanding,
            QtWidgets.QSizePolicy.MinimumExpanding,
        )
        self.layout.addWidget(self.buttonListWidget)

        # Docs Label
        self.docLabel = QtWidgets.QLabel()
        self.docLabel.setStyleSheet(
            "background-color: rgb(90,90,90); border-radius: 5px; border:1px solid rgb(255, 255, 255); "
        )
        self.layout.addWidget(self.docLabel)
        self.docLabel.setText("")

        # Update and Reload Buttons
        self.updateButton = self.add_icon_button("update", str(update_icon_path))
        self.reloadButton = self.add_icon_button("reload", str(reload_icon_path))

        self.buttonLayout = QtWidgets.QHBoxLayout()
        self.buttonLayout.addWidget(self.reloadButton)
        self.buttonLayout.addWidget(self.updateButton)
        self.layout.addLayout(self.buttonLayout)

        # Connect signals
        self.reloadButton.clicked.connect(self.reloaded)
        self.updateButton.clicked.connect(self.download)
        self.searchLineEdit.speak.connect(
            lambda: self.build_button_list(self.searchLineEdit.text())
        )
        self.buttonListWidget.itemClicked.connect(self.list_widget_button_click)

        self.show()

    def list_widget_button_click(self, item):
        """Handle list widget item click to execute corresponding function.

        Args:
            item (QListWidgetItem): The clicked item.
        """
        libstr = item.toolTip()
        class_string = libstr.split(".")
        module = ".".join(class_string[:-1])
        key = class_string[-1]
        func = self.libStructure.import_and_exec(module, key)
        self.button_clicked(func)

    def build_button_list(self, text):
        """Build the list of buttons based on the search text.

        Args:
            text (str): Search input text.
        """
        if self.buttonListWidget.count() > 0 or text == "":
            self.buttonListWidget.clear()
            del self.buttonItemList[:]

        doc_text = []
        text_list = text.split("*")
        for libstr in self.libStructure.finalClassList:
            str_match = [True for match in text_list if match in libstr]

            if True in str_match:
                doc_text.append(libstr)
                tt = "\n".join(doc_text)
                self.docLabel.setText(tt)
                class_string = libstr.split(".")
                key = class_string[-1]

                button_q_list_widget_item = QtWidgets.QListWidgetItem(key)
                button_q_list_widget_item.setToolTip(libstr)
                self.buttonItemList.append(button_q_list_widget_item)
                self.buttonListWidget.addItem(self.buttonItemList[-1])

        if text == "":
            self.docLabel.setText("")
            if self.buttonListWidget.count() > 0:
                self.buttonListWidget.clear()

        self.buttonListWidget.adjustSize()

    def reloaded(self):
        """Emit the update_widget signal."""
        self.update_widget.emit()

    def download(self):
        """Download the library and reload the widget."""
        lib = lib_manager.InstallLibrary()
        # lib.download()
        lib.pull_from_git()
        self.reloaded()

    def add_icon_button(self, name, img_path):
        """Create a button with an icon.

        Args:
            name (str): Name for the button tooltip.
            img_path (str): Path to the icon image.

        Returns:
            QPushButton: The created button.
        """
        icon = QtGui.QPixmap(img_path)
        button = QtWidgets.QPushButton()
        button.setIcon(icon)
        button.setToolTip(name)

        return button

    def add_menu_bar(self):
        """Create the main menu bar with disciplines.

        Returns:
            QMenuBar: The main menu bar.
        """
        main_menu = QtWidgets.QMenuBar(self)

        discipline = ["Modelling", "Rigging", "Animation", "Vfx", "Lookdev"]
        for disci in discipline:
            file_menu = main_menu.addMenu("&" + disci)
            for action in self.add_multiple_menu_action(file_menu, disci):
                file_menu.addAction(action)

        return main_menu

    def button_hover(self, text):
        """Update the documentation label text when a button is hovered.

        Args:
            text (str): The text to display.
        """
        self.docLabel.setText(text)

    def button_clicked(self, func):
        """Execute a function and display its UI.

        Args:
            func (function): The function to execute.
        """
        self.functionWindow = None
        self.functionWindow = ui.FunctionUI(func)
        self.functionWindow.show()
        self.functionWindow.setFocus()

    def add_menu_action(self, discipline, function):
        """Add an action to the menu.

        Args:
            discipline (str): The discipline name.
            function (function): The function associated with the action.

        Returns:
            QAction: The created action.
        """
        extract_action = QAction(discipline, self)
        extract_action.triggered.connect(lambda: self.button_clicked(function))
        doc_text = doc.get_docs(function)
        extract_action.hovered.connect(lambda: self.button_hover(doc_text))

        return extract_action

    def add_sub_menu(self, up_menu, lib):
        """Add a submenu to the given menu.

        Args:
            up_menu (QMenu): The parent menu.
            lib (str): The library name.

        Returns:
            QMenu: The created submenu.
        """
        libname = lib.replace("Lib", "").title()
        return up_menu.addMenu(libname)

    def add_recursive_menu(self, up_menu, lib_dict):
        """Recursively add submenus and actions to the menu.

        Args:
            up_menu (QMenu): The parent menu.
            lib_dict (dict): The dictionary containing library functions.
        """
        for key, value in lib_dict.items():
            if isinstance(value, dict):
                sub_menu = self.add_sub_menu(up_menu, key)
                self.add_recursive_menu(sub_menu, value)

            else:
                class_string = value.split(".")
                module = ".".join(class_string[:-1])
                func = self.libStructure.import_and_exec(module, key)
                up_menu.addAction(self.add_menu_action(key, func))

    def add_multiple_menu_action(self, up_menu, discipline):
        """Add multiple actions to the menu based on the discipline.

        Args:
            up_menu (QMenu): The parent menu.
            discipline (str): The discipline name.

        Returns:
            list: A list of actions added.
        """
        action_list = []
        if discipline == "Modelling":
            lib_menu = self.add_sub_menu(up_menu, "modelLib")
            self.add_recursive_menu(lib_menu, self.libDict["modelLib"])
        elif discipline == "Rigging":
            lib_menu = self.add_sub_menu(up_menu, "rigLib")
            self.add_recursive_menu(lib_menu, self.libDict["rigLib"])
        elif discipline == "Animation":
            lib_menu = self.add_sub_menu(up_menu, "animationLib")
            self.add_recursive_menu(lib_menu, self.libDict["animationLib"])
        elif discipline == "Vfx":
            lib_menu = self.add_sub_menu(up_menu, "fluidLib")
            self.add_recursive_menu(lib_menu, self.libDict["fluidLib"])
        elif discipline == "Lookdev":
            lib_menu = self.add_sub_menu(up_menu, "lookdevLib")
            self.add_recursive_menu(lib_menu, self.libDict["lookdevLib"])
            lib_menu = self.add_sub_menu(up_menu, "shaderLib")
            self.add_recursive_menu(lib_menu, self.libDict["shaderLib"])

        return action_list


class MainMenu(QtWidgets.QWidget):
    """Main menu widget to display the library in Maya."""

    def __init__(
        self, lib_path, menu_name="MayaLib", parent=None, auto_update_on_load=True
    ):
        """Initialize the MainMenu.

        Args:
            lib_path (str): Path to the library.
            menu_name (str, optional): Name of the menu. Defaults to 'MayaLib'.
            parent (QWidget, optional): Parent widget. Defaults to None.
        """
        super(MainMenu, self).__init__(parent)

        if auto_update_on_load:
            self.update_lib()

        self.wAction = QtWidgets.QWidgetAction(self)
        self.libWindow = MenuLibWidget(lib_path)
        self.wAction.setDefaultWidget(self.libWindow)

        widget_str = mel.eval("string $tempString = $gMainWindow")
        ptr = OpenMayaUI.MQtUtil.findControl(widget_str)
        menu_widget = wrapInstance(int(ptr), QtWidgets.QMainWindow)
        self.mayaMenu = menu_widget.menuBar()

        if menu_name not in [m.text for m in self.mayaMenu.actions()]:
            self.libMenu = self.mayaMenu.addMenu(menu_name)

            self.libMenu.addAction(self.wAction)

            QObject.connect(
                self.libWindow,
                SIGNAL("updateWidget()"),
                lambda: self.update_widget(lib_path),
            )
            self.libMenu.triggered.connect(self.show_widget)

    def update_widget(self, lib_path):
        """Update the widget by reloading the library.

        Args:
            lib_path (str): Path to the library.
        """
        reload_package(mayaLib)
        self.libMenu.removeAction(self.wAction)
        self.libWindow.destroy()

        self.wAction = QtWidgets.QWidgetAction(self)
        self.libWindow = MenuLibWidget(lib_path)
        self.wAction.setDefaultWidget(self.libWindow)

        self.libMenu.addAction(self.wAction)
        try:
            self.libWindow.update_widget.connect(lambda: self.update_widget(lib_path))
        except AttributeError:
            QObject.connect(
                self.libWindow, SIGNAL("updateWidget()"), lambda: self.update_widget(lib_path)
            )
        self.libMenu.triggered.connect(self.show_widget)
        print("Reloaded MayaLib!")

    def show_widget(self):
        """Adjust the size of the library window."""
        self.libWindow.adjustSize()

    def update_lib(self):
        """Pull the latest changes from the MayaLib repository using git."""
        lib = lib_manager.InstallLibrary()
        lib.pull_from_git()

    def __del__(self):
        """Clean up resources when the object is deleted."""
        if hasattr(self, 'libMenu') and self.libMenu is not None:
            self.libMenu.deleteLater()


def reload_package(package):
    """Recursively reload a package and its submodules.

    Args:
        package (module): The package to reload.
    """
    assert hasattr(package, "__package__")
    fn = package.__file__
    fn_dir = os.path.dirname(fn) + os.sep
    module_visit = {fn}
    del fn

    def reload_recursive_ex(module):
        """Helper function to reload modules.

        Args:
            module (module): The module to reload.
        """
        importlib.reload(module)

        for module_child in list(vars(module).values()):
            if isinstance(module_child, types.ModuleType):
                fn_child = getattr(module_child, "__file__", None)
                if (fn_child is not None) and fn_child.startswith(fn_dir):
                    if fn_child not in module_visit:
                        module_visit.add(fn_child)
                        reload_recursive_ex(module_child)

    return reload_recursive_ex(package)


if __name__ == "__main__":
    pass

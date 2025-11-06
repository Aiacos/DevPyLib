"""Main menu system for DevPyLib tools.

Provides the MainMenu class that creates dynamic menus with
automatic function discovery and UI generation.
"""

__author__ = "Lorenzo Argentieri"

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

        self.lib_structure = lm.StructureManager(mayaLib)
        self.lib_dict = self.lib_structure.get_struct_lib()["mayaLib"]

        # Setup layout
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        # Add menu bar
        self.main_menu = self.add_menu_bar()
        self.layout.addWidget(self.main_menu)

        # Search bar
        self.search_line_edit = SearchLineEdit(str(close_icon_path))
        self.layout.addWidget(self.search_line_edit)

        # Widget List
        self.button_item_list = []
        self.button_list_widget = QtWidgets.QListWidget()
        self.button_list_widget.setStyleSheet("background: transparent;")
        self.button_list_widget.setFocusPolicy(QtCore.Qt.NoFocus)
        self.button_list_widget.adjustSize()
        self.button_list_widget.setSizePolicy(
            QtWidgets.QSizePolicy.MinimumExpanding,
            QtWidgets.QSizePolicy.MinimumExpanding,
        )
        self.layout.addWidget(self.button_list_widget)

        # Docs Label
        self.doc_label = QtWidgets.QLabel()
        self.doc_label.setStyleSheet(
            "background-color: rgb(90,90,90); border-radius: 5px; border:1px solid rgb(255, 255, 255); "
        )
        self.layout.addWidget(self.doc_label)
        self.doc_label.setText("")

        # Update and Reload Buttons
        self.update_button = self.add_icon_button("update", str(update_icon_path))
        self.reload_button = self.add_icon_button("reload", str(reload_icon_path))

        self.button_layout = QtWidgets.QHBoxLayout()
        self.button_layout.addWidget(self.reload_button)
        self.button_layout.addWidget(self.update_button)
        self.layout.addLayout(self.button_layout)

        # Connect signals
        self.reload_button.clicked.connect(self.reloaded)
        self.update_button.clicked.connect(self.download)
        self.search_line_edit.speak.connect(
            lambda: self.build_button_list(self.search_line_edit.text())
        )
        self.button_list_widget.itemClicked.connect(self.list_widget_button_click)

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
        func = self.lib_structure.import_and_exec(module, key)
        self.button_clicked(func)

    def build_button_list(self, text):
        """Build the list of buttons based on the search text.

        Args:
            text (str): Search input text.
        """
        if self.button_list_widget.count() > 0 or text == "":
            self.button_list_widget.clear()
            del self.button_item_list[:]

        doc_text = []
        text_list = text.split("*")
        for libstr in self.lib_structure.final_class_list:
            str_match = [True for match in text_list if match in libstr]

            if True in str_match:
                doc_text.append(libstr)
                tt = "\n".join(doc_text)
                self.doc_label.setText(tt)
                class_string = libstr.split(".")
                key = class_string[-1]

                button_q_list_widget_item = QtWidgets.QListWidgetItem(key)
                button_q_list_widget_item.setToolTip(libstr)
                self.button_item_list.append(button_q_list_widget_item)
                self.button_list_widget.addItem(self.button_item_list[-1])

        if text == "":
            self.doc_label.setText("")
            if self.button_list_widget.count() > 0:
                self.button_list_widget.clear()

        self.button_list_widget.adjustSize()

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
        self.doc_label.setText(text)

    def button_clicked(self, func):
        """Execute a function and display its UI.

        Args:
            func (function): The function to execute.
        """
        self.function_window = None
        self.function_window = ui.FunctionUI(func)
        self.function_window.show()
        self.function_window.setFocus()

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
                func = self.lib_structure.import_and_exec(module, key)
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
            self.add_recursive_menu(lib_menu, self.lib_dict["modelLib"])
        elif discipline == "Rigging":
            lib_menu = self.add_sub_menu(up_menu, "rigLib")
            self.add_recursive_menu(lib_menu, self.lib_dict["rigLib"])
        elif discipline == "Animation":
            lib_menu = self.add_sub_menu(up_menu, "animationLib")
            self.add_recursive_menu(lib_menu, self.lib_dict["animationLib"])
        elif discipline == "Vfx":
            lib_menu = self.add_sub_menu(up_menu, "fluidLib")
            self.add_recursive_menu(lib_menu, self.lib_dict["fluidLib"])
        elif discipline == "Lookdev":
            lib_menu = self.add_sub_menu(up_menu, "lookdevLib")
            self.add_recursive_menu(lib_menu, self.lib_dict["lookdevLib"])
            lib_menu = self.add_sub_menu(up_menu, "shaderLib")
            self.add_recursive_menu(lib_menu, self.lib_dict["shaderLib"])

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

        self.w_action = QtWidgets.QWidgetAction(self)
        self.lib_window = MenuLibWidget(lib_path)
        self.w_action.setDefaultWidget(self.lib_window)

        widget_str = mel.eval("string $tempString = $gMainWindow")
        ptr = OpenMayaUI.MQtUtil.findControl(widget_str)
        menu_widget = wrapInstance(int(ptr), QtWidgets.QMainWindow)
        self.maya_menu = menu_widget.menuBar()

        if menu_name not in [m.text for m in self.maya_menu.actions()]:
            self.lib_menu = self.maya_menu.addMenu(menu_name)

            self.lib_menu.addAction(self.w_action)

            QObject.connect(
                self.lib_window,
                SIGNAL("updateWidget()"),
                lambda: self.update_widget(lib_path),
            )
            self.lib_menu.triggered.connect(self.show_widget)

    def update_widget(self, lib_path):
        """Update the widget by reloading the library.

        Args:
            lib_path (str): Path to the library.
        """
        reload_package(mayaLib)
        self.lib_menu.removeAction(self.w_action)
        self.lib_window.destroy()

        self.w_action = QtWidgets.QWidgetAction(self)
        self.lib_window = MenuLibWidget(lib_path)
        self.w_action.setDefaultWidget(self.lib_window)

        self.lib_menu.addAction(self.w_action)
        try:
            self.lib_window.update_widget.connect(lambda: self.update_widget(lib_path))
        except AttributeError:
            QObject.connect(
                self.lib_window, SIGNAL("updateWidget()"), lambda: self.update_widget(lib_path)
            )
        self.lib_menu.triggered.connect(self.show_widget)
        print("Reloaded MayaLib!")

    def show_widget(self):
        """Adjust the size of the library window."""
        self.lib_window.adjustSize()

    def update_lib(self):
        """Pull the latest changes from the MayaLib repository using git."""
        lib = lib_manager.InstallLibrary()
        lib.pull_from_git()

    def __del__(self):
        """Clean up resources when the object is deleted."""
        if hasattr(self, 'lib_menu') and self.lib_menu is not None:
            self.lib_menu.deleteLater()


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

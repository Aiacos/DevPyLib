"""Main menu system for DevPyLib tools.

Provides the MainMenu class that creates dynamic menus with
automatic function discovery and UI generation.
"""

__author__ = "Lorenzo Argentieri"

import importlib
import os
import pathlib
import sys

import maya.OpenMayaUI as OpenMayaUI
from maya import mel

# from mayaLib.utility.Qt import QtCore, QtWidgets, QtGui

try:
    from PySide6 import QtCore, QtGui, QtWidgets
    from PySide6.QtGui import QAction
    from shiboken6 import wrapInstance
except ImportError:
    from PySide2 import QtCore, QtGui, QtWidgets
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
        super().__init__(parent)

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
            f"QLineEdit {{padding-right: {button_size.width() + frame_width + 1}px; }}"
        )
        self.setMinimumSize(
            max(
                self.minimumSizeHint().width(),
                button_size.width() + frame_width * 2 + 3,
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
        super().__init__(parent)

        lib_path = pathlib.Path(lib_path)

        # Icon paths
        close_icon_path = lib_path / "mayaLib" / "icons" / "close.png"
        update_icon_path = lib_path / "mayaLib" / "icons" / "update.png"
        reload_icon_path = lib_path / "mayaLib" / "icons" / "reload.png"
        luna_icon_path = lib_path / "luna" / "res" / "images" / "icons" / "builder.svg"

        # Defer StructureManager creation for lazy initialization
        self.lib_structure = None
        self.lib_dict = None
        self._structure_initialized = False

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

        # Luna, Update, and Reload Buttons
        self.update_button = self.add_icon_button("update", str(update_icon_path))
        self.reload_button = self.add_icon_button("reload", str(reload_icon_path))

        self.button_layout = QtWidgets.QHBoxLayout()

        # Only show Luna button when not disabled
        luna_disabled = os.environ.get("DEVPYLIB_DISABLE_LUNA", "0") == "1"
        if not luna_disabled:
            self.luna_button = self.add_icon_button("Luna Builder", str(luna_icon_path))
            self.button_layout.addWidget(self.luna_button)
            self.luna_button.clicked.connect(self.open_luna_builder)

        self.button_layout.addWidget(self.reload_button)
        self.button_layout.addWidget(self.update_button)
        self.layout.addLayout(self.button_layout)
        self.reload_button.clicked.connect(self.reloaded)
        self.update_button.clicked.connect(self.download)
        self.search_line_edit.speak.connect(
            lambda: self.build_button_list(self.search_line_edit.text())
        )
        self.button_list_widget.itemClicked.connect(self.list_widget_button_click)

        self.show()

    def _ensure_structure_initialized(self):
        """Initialize StructureManager and lib_dict if not already done.

        This method follows the lazy initialization pattern to defer expensive
        introspection until the menu is actually accessed.

        Returns:
            bool: True if initialized successfully.
        """
        if self._structure_initialized:
            return True

        # Create StructureManager (not using lazy=True since we need it now)
        self.lib_structure = lm.StructureManager(mayaLib, lazy=False)

        # Cache the library dictionary structure
        # Unwrap root package level so subpackages (modelLib, rigLib, etc.)
        # are accessible as top-level keys
        full_dict = self.lib_structure.get_struct_lib()
        root_name = self.lib_structure.root_package.__name__
        self.lib_dict = full_dict.get(root_name, full_dict)

        # Mark as initialized
        self._structure_initialized = True

        return True

    def list_widget_button_click(self, item):
        """Handle list widget item click to execute corresponding function.

        Args:
            item (QListWidgetItem): The clicked item.
        """
        self._ensure_structure_initialized()
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
        self._ensure_structure_initialized()
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

    def open_luna_builder(self):
        """Open the Luna Builder visual rig editor."""
        try:
            from mayaLib.lunaLib import LUNA_AVAILABLE

            if LUNA_AVAILABLE:
                from mayaLib.lunaLib.tools import launch_builder

                launch_builder()
            else:
                print("Luna is not available")
        except ImportError as e:
            print(f"Could not open Luna Builder: {e}")

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
            # Connect aboutToShow signal to trigger lazy initialization
            # This ensures StructureManager is created only when menu is opened
            file_menu.aboutToShow.connect(self._ensure_structure_initialized)
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
        self._ensure_structure_initialized()
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
        self._ensure_structure_initialized()
        action_list = []
        discipline_libs = {
            "Modelling": ["modelLib"],
            "Rigging": ["rigLib"],
            "Animation": ["animationLib"],
            "Vfx": ["fluidLib"],
            "Lookdev": ["lookdevLib", "shaderLib"],
        }
        for lib_name in discipline_libs.get(discipline, []):
            if lib_name not in self.lib_dict:
                print(f"Warning: {lib_name} not found in library structure, skipping menu entry")
                continue
            lib_menu = self.add_sub_menu(up_menu, lib_name)
            self.add_recursive_menu(lib_menu, self.lib_dict[lib_name])

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
            auto_update_on_load (bool, optional): Update library on load. Defaults to True.
        """
        super().__init__(parent)

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

            self.lib_window.update_widget.connect(lambda: self.update_widget(lib_path))
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
        self.lib_window.update_widget.connect(lambda: self.update_widget(lib_path))
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
        if hasattr(self, "lib_menu") and self.lib_menu is not None:
            self.lib_menu.deleteLater()


def reload_package(package):
    """Reload a package and all its loaded submodules from sys.modules.

    Uses sys.modules to discover every submodule that was loaded under the
    package prefix, which works reliably with lazy-loading __init__.py files
    (the old vars()-based traversal missed lazily-loaded submodules).

    Submodules are reloaded leaf-first (deepest nesting first) so that parent
    packages always pick up the freshly reloaded children.

    Args:
        package (module): The top-level package to reload.
    """
    pkg_name = package.__name__
    pkg_prefix = pkg_name + "."

    # Collect every loaded submodule under this package
    sub_modules = {
        name: mod
        for name, mod in list(sys.modules.items())
        if (name == pkg_name or name.startswith(pkg_prefix)) and mod is not None
    }

    # Sort deepest-first so leaves reload before parents
    sorted_names = sorted(sub_modules, key=lambda n: n.count("."), reverse=True)

    for name in sorted_names:
        mod = sub_modules[name]
        try:
            importlib.reload(mod)
        except (ModuleNotFoundError, ImportError):
            # Source was removed (e.g. deleted subpackage). Drop the stale entry.
            sys.modules.pop(name, None)
        except Exception as exc:
            print(f"Warning: failed to reload {name}: {exc}")


if __name__ == "__main__":
    pass

__author__ = "Lorenzo Argentieri"

"""Introspective UI generator for Maya functions.

Provides the FunctionUI class that automatically generates Qt widgets
from function signatures using Python's inspect module for dynamic UIs.
"""

import ast
import inspect

import pymel.core as pm

try:
    from PySide6 import QtCore, QtWidgets
except ImportError:
    from PySide2 import QtCore, QtWidgets

import mayaLib.pipelineLib.utility.docs as doc


class FunctionUI(QtWidgets.QWidget):
    """Introspective UI generator for Maya functions and classes.

    Automatically generates Qt widgets from function or class signatures using
    Python's inspect module. Creates input fields for each parameter, with type-aware
    widgets (checkboxes for booleans, line edits for other types) and fill buttons
    to populate from Maya selection. Includes an Execute button and Advanced mode
    toggle to show/hide optional parameters.

    Attributes:
        function: The function or class being wrapped
        sig: The function signature
        layout: The grid layout containing UI elements
        lineedit_list: List of input widgets
        label_list: List of parameter labels
        fillButton_list: List of fill-from-selection buttons
        execButton: The execute button
        advancedCheckBox: Toggle for advanced parameters
        doclabel: Label displaying function documentation

    Example:
        >>> def my_function(param1, param2=10):
        ...     '''My test function.'''
        ...     pass
        >>> ui = FunctionUI(my_function)
        >>> ui.show()
    """
    def __init__(self, func, parent=None):
        """Initializes the FunctionUI widget.

        Args:
            func (function or class): The function or class to inspect and build the UI for.
            parent (QWidget, optional): The parent widget. Defaults to None.
        """
        super(FunctionUI, self).__init__(parent)

        self.function = func
        # Retrieve the function signature using inspect
        if inspect.isclass(func):
            self.sig = inspect.signature(func.__init__)
        else:
            self.sig = inspect.signature(func)

        self.layout = QtWidgets.QGridLayout()

        # Get parameter list
        self.args = self.get_parameter_list()

        self.label_list = []
        self.lineedit_list = []
        self.fillButton_list = []

        row = 0
        for arg in self.args:
            if arg[0] != "self":
                # Create a label for the argument
                labelname = QtWidgets.QLabel(arg[0])
                fill_button = None

                if arg[1] is not None:
                    # Create a line edit or checkbox based on argument type
                    if isinstance(arg[1], bool):
                        lineedit = QtWidgets.QCheckBox("")
                        lineedit.setChecked(arg[1])
                    else:
                        lineedit = QtWidgets.QLineEdit(str(arg[1]))
                        fill_button = QtWidgets.QPushButton(">")
                else:
                    lineedit = QtWidgets.QLineEdit("")
                    fill_button = QtWidgets.QPushButton(">")

                self.layout.addWidget(labelname, row, 0)
                self.label_list.append(labelname)

                if fill_button is not None:
                    self.layout.addWidget(fill_button, row, 1)
                self.fillButton_list.append(fill_button)

                self.layout.addWidget(lineedit, row, 2)
                self.lineedit_list.append(lineedit)

                row += 1

        # Create execute button
        self.execButton = QtWidgets.QPushButton("Execute")
        # Create advanced checkbox
        self.advancedCheckBox = QtWidgets.QCheckBox("Advanced")
        self.advancedCheckBox.setChecked(False)
        self.toggle_default_parameter(False)
        self.layout.addWidget(self.execButton, row, 2)
        self.layout.addWidget(self.advancedCheckBox, row, 0)

        # Display function documentation
        self.doclabel = QtWidgets.QLabel(doc.get_docs(func))
        self.layout.addWidget(self.doclabel, row + 1, 2)
        self.setLayout(self.layout)

        # Connect signals to slots
        self.execButton.clicked.connect(self.exec_function)
        self.advancedCheckBox.stateChanged.connect(self.toggle_default_parameter)

        for button in self.fillButton_list:
            if button is not None:
                button.clicked.connect(self.fill_with_selected)

        # Set window properties
        self.setWindowTitle(func.__name__)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setSizePolicy(
            QtWidgets.QSizePolicy.MinimumExpanding,
            QtWidgets.QSizePolicy.MinimumExpanding,
        )
        self.setFocus()

    def fill_with_selected(self):
        """Fills the line edit associated with the button with the names of the
        selected objects in Maya.

        When a button is clicked, this method is called. It gets the button that
        was clicked, gets the index of the button in the list of buttons, and
        then gets the line edit associated with that button. It then gets the
        selected objects in Maya and sets the text of the line edit to a comma
        separated string of the names of the selected objects.
        """
        # Get the button that was clicked
        button = self.sender()

        # Get the index of the button in the list of buttons
        index = self.fillButton_list.index(button)

        # Get the line edit associated with the button
        lineedit = self.lineedit_list[index]

        # Get the selected objects in Maya
        selection_list = pm.ls(sl=True)

        # Initialize an empty list
        text_list = []

        # Iterate over the selected objects
        for item in selection_list:
            # Append the name of the object as a string to the list
            text_list.append(str(item))

        # Set the text of the line edit to a comma separated string of the
        # names of the selected objects
        lineedit.setText(", ".join(text_list))

    def get_parameter_list(self):
        """Returns a list of parameters for the UI.

        This method returns a list of tuples, where the first element of each
        tuple is the name of a parameter and the second element is the default
        value for that parameter, if it exists.

        Returns:
            list: A list of tuples, where each tuple contains a parameter name
                and its default value.
        """
        result = []
        for name, param in self.sig.parameters.items():
            default = None
            if param.default is not inspect.Parameter.empty:
                # If the parameter has a default value, store it
                default = param.default
            result.append((name, default))
        return result

    # SLOTS
    def toggle_default_parameter(self, defaultvisible=False):
        """Toggle the visibility of default parameters.

        This method iterates over the arguments and either shows or hides
        the corresponding labels, line edits, and fill buttons based on
        the `defaultvisible` flag.

        Args:
            defaultvisible (bool): If True, show the default parameters;
                                   if False, hide them.
        """
        counter = 0
        for arg in self.args:
            if arg[0] != "self":
                if defaultvisible:
                    # Show related widgets if the argument has a default value
                    if arg[1] is not None:
                        self.label_list[counter].show()
                        self.lineedit_list[counter].show()
                        if self.fillButton_list[counter] is not None:
                            self.fillButton_list[counter].show()
                else:
                    # Hide related widgets if the argument has a default value
                    if arg[1] is not None:
                        self.label_list[counter].hide()
                        self.lineedit_list[counter].hide()
                        if self.fillButton_list[counter] is not None:
                            self.fillButton_list[counter].hide()

                counter += 1

    def exec_function(self):
        """Execute the function with the parameters from the lineedits.

        Iterate over the lineedits and fill a list with the parameters.
        The parameters can be a string, an int, a float, a list or a boolean.
        """
        param_list = []

        for param in self.lineedit_list:
            value = param.text()

            # Check if the parameter is a boolean
            if isinstance(param, QtWidgets.QCheckBox):
                if param.isChecked():
                    q_check_box_value = True
                else:
                    q_check_box_value = False
                value = q_check_box_value
                param_list.append(value)

            # Check if the parameter is a list
            elif "[" in value and "]" in value:
                value = (
                    value.replace("[", "")
                    .replace("]", "")
                    .replace("'", "")
                    .replace(" ", "")
                    .split(",")
                )
                param_list.append(value)

            # Check if the parameter is a numeric value
            elif value.replace(".", "", 1).isdigit():
                value = ast.literal_eval(value)
                param_list.append(value)

            # Check if the parameter is a string
            elif value == "True":
                value = True
                param_list.append(value)
            elif value == "False":
                value = False
                param_list.append(value)
            elif value == "":
                value = None
                param_list.append(value)

            # Check if the parameter is a string with comma separated values
            elif ", " in value:
                value = value.split(", ")
                param_list.append(value)

            # If the parameter is a string without comma separated values
            else:
                param_list.append(value)

        self.wrapper(param_list)

    def wrapper(self, args):
        """Wrapper around the function to execute.

        Args:
            args (list): List of arguments to pass to the function.
        """
        self.function(*args)


if __name__ == "__main__":
    # Example usage:
    # app = QtWidgets.QApplication.instance()
    # button = QtWidgets.QPushButton("Hello World")
    # button.show()
    # app.exec_()
    # t = FunctionUI(your_function_here)
    # t.show()
    pass

"""Introspective UI generator for Maya functions.

Provides the FunctionUI class that automatically generates Qt widgets
from function signatures using Python's inspect module for dynamic UIs.
"""

__author__ = "Lorenzo Argentieri"

import ast
import inspect

import pymel.core as pm

try:
    from PySide6 import QtCore, QtGui, QtWidgets
except ImportError:
    from PySide2 import QtCore, QtGui, QtWidgets

import mayaLib.pipelineLib.utility.docs as doc
from mayaLib.guiLib.utils.error_dialog import show_exception_dialog


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
        fill_button_list: List of fill-from-selection buttons
        exec_button: The execute button
        advanced_checkbox: Toggle for advanced parameters
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
        super().__init__(parent)

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
        self.fill_button_list = []

        row = 0
        for arg in self.args:
            if arg[0] != "self":
                # Create a label for the argument
                labelname = QtWidgets.QLabel(arg[0])
                fill_button = None

                # Get parameter annotation for placeholder text generation
                param_annotation = self.sig.parameters[arg[0]].annotation

                if arg[1] is not None:
                    # Create a line edit or checkbox based on argument type
                    if isinstance(arg[1], bool):
                        lineedit = QtWidgets.QCheckBox("")
                        lineedit.setChecked(arg[1])
                    else:
                        lineedit = QtWidgets.QLineEdit(str(arg[1]))
                        fill_button = QtWidgets.QPushButton(">")
                        placeholder = self.generate_placeholder_text(
                            arg[0], param_annotation, arg[1]
                        )
                        lineedit.setPlaceholderText(placeholder)
                        self._apply_validator(lineedit, param_annotation)
                else:
                    lineedit = QtWidgets.QLineEdit("")
                    fill_button = QtWidgets.QPushButton(">")
                    placeholder = self.generate_placeholder_text(arg[0], param_annotation, None)
                    lineedit.setPlaceholderText(placeholder)
                    self._apply_validator(lineedit, param_annotation)

                self.layout.addWidget(labelname, row, 0)
                self.label_list.append(labelname)

                if fill_button is not None:
                    self.layout.addWidget(fill_button, row, 1)
                self.fill_button_list.append(fill_button)

                self.layout.addWidget(lineedit, row, 2)
                self.lineedit_list.append(lineedit)

                row += 1

        # Create execute button
        self.exec_button = QtWidgets.QPushButton("Execute")
        # Create advanced checkbox
        self.advanced_checkbox = QtWidgets.QCheckBox("Advanced")
        self.advanced_checkbox.setChecked(False)
        self.toggle_default_parameter(False)
        self.layout.addWidget(self.exec_button, row, 2)
        self.layout.addWidget(self.advanced_checkbox, row, 0)

        # Display function documentation
        self.doclabel = QtWidgets.QLabel(doc.get_docs(func))
        self.layout.addWidget(self.doclabel, row + 1, 2)
        self.setLayout(self.layout)

        # Connect signals to slots
        self.exec_button.clicked.connect(self.exec_function)
        self.advanced_checkbox.stateChanged.connect(self.toggle_default_parameter)

        for button in self.fill_button_list:
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
        """Fill the line edit with selected Maya object names.

        When a button is clicked, this method gets the button that was clicked,
        finds the corresponding line edit, and populates it with a comma-separated
        string of the currently selected objects in Maya.
        """
        # Get the button that was clicked
        button = self.sender()

        # Get the index of the button in the list of buttons
        index = self.fill_button_list.index(button)

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

    def generate_placeholder_text(self, param_name, param_annotation, default_value):
        """Generate placeholder text based on parameter type and name.

        Analyzes the parameter annotation and name to provide context-aware
        placeholder text that helps users understand what input is expected.

        Args:
            param_name (str): The name of the parameter.
            param_annotation: The type annotation of the parameter (if available).
            default_value: The default value of the parameter (if available).

        Returns:
            str: Appropriate placeholder text for the parameter.
        """
        param_lower = param_name.lower()

        # Check type annotation first if available
        if param_annotation is not inspect.Parameter.empty:
            annotation_str = str(param_annotation)
            if "int" in annotation_str.lower():
                return "Enter integer value"
            elif "float" in annotation_str.lower():
                return "Enter float value"
            elif "str" in annotation_str.lower():
                return "Enter text"
            elif "list" in annotation_str.lower():
                return "Enter comma-separated values"
            elif "bool" in annotation_str.lower():
                return ""

        # Rigging-specific reference parameters
        if param_lower.endswith("_to") or param_lower in [
            "parent",
            "target",
            "driver",
            "driven",
        ]:
            return "Select reference object"

        # Maya object-related parameters
        elif any(
            keyword in param_lower
            for keyword in ["mesh", "obj", "node", "transform", "geo", "geometry"]
        ):
            return "Select Maya object(s)"
        elif any(keyword in param_lower for keyword in ["ctrl", "control", "curve"]):
            return "Select control object(s)"
        elif any(keyword in param_lower for keyword in ["joint", "jnt", "bone"]):
            return "Select joint(s)"
        elif any(keyword in param_lower for keyword in ["vertex", "vert", "vtx"]):
            return "Select vertex/vertices"
        elif any(keyword in param_lower for keyword in ["edge"]):
            return "Select edge(s)"
        elif any(keyword in param_lower for keyword in ["face", "poly"]):
            return "Select face(s)"

        # Shape/type selection parameters
        elif "shape" in param_lower or "type" in param_lower:
            if default_value and isinstance(default_value, str):
                return f"Enter shape type (e.g., {default_value})"
            return "Enter shape type"

        # Channel parameters
        elif "channel" in param_lower or "attr" in param_lower:
            if default_value is None or isinstance(default_value, list | tuple):
                return "Enter channels (e.g., t,r,s,v)"
            return "Enter channel name"

        # Naming parameters
        elif any(keyword in param_lower for keyword in ["name", "label"]):
            return "Enter name"
        elif "prefix" in param_lower:
            return "Enter prefix (e.g., l_, r_, c_)"
        elif "suffix" in param_lower:
            return "Enter suffix (e.g., _CTRL, _GRP)"

        # File/path parameters
        elif any(keyword in param_lower for keyword in ["path", "file", "directory", "dir"]):
            return "Enter file path"

        # Numeric parameters
        elif "scale" in param_lower:
            return "Enter scale value (e.g., 1.0)"
        elif any(keyword in param_lower for keyword in ["count", "number", "num", "index", "idx"]):
            return "Enter integer"
        elif any(keyword in param_lower for keyword in ["value", "val", "amount"]):
            return "Enter numeric value"
        elif any(keyword in param_lower for keyword in ["factor", "weight", "blend"]):
            return "Enter value (0.0-1.0)"
        elif any(keyword in param_lower for keyword in ["radius", "distance", "dist", "length"]):
            return "Enter distance value"
        elif any(keyword in param_lower for keyword in ["angle", "rotation", "rot"]):
            return "Enter angle (degrees)"

        # Color parameters
        elif "color" in param_lower:
            return "Enter color (R,G,B)"

        # Axis parameters
        elif "axis" in param_lower:
            return "Enter axis (X, Y, or Z)"

        # Based on default value type
        elif default_value is not None:
            if isinstance(default_value, int):
                return "Enter integer value"
            elif isinstance(default_value, float):
                return "Enter float value"
            elif isinstance(default_value, list | tuple):
                return "Enter comma-separated values"
            elif isinstance(default_value, str) and default_value == "":
                return "Enter text (optional)"

        return "Enter value"

    def _apply_validator(self, lineedit, param_annotation):
        """Apply a Qt validator to a QLineEdit based on type annotation.

        Sets QIntValidator for int annotations and QDoubleValidator for float
        annotations. Connects textChanged signal for real-time visual feedback.

        Args:
            lineedit (QLineEdit): The line edit widget to apply the validator to.
            param_annotation: The type annotation from the function signature.
        """
        if param_annotation is inspect.Parameter.empty:
            return

        if param_annotation is int:
            lineedit.setValidator(QtGui.QIntValidator())
            lineedit.textChanged.connect(self._validate_input)
        elif param_annotation is float:
            lineedit.setValidator(QtGui.QDoubleValidator())
            lineedit.textChanged.connect(self._validate_input)

    def _validate_input(self):
        """Validate all line edits and update visual feedback.

        Called when any validated field's text changes. Sets a red border on
        invalid fields and disables the Execute button if any field is invalid.
        """
        all_valid = True
        for lineedit in self.lineedit_list:
            if not isinstance(lineedit, QtWidgets.QLineEdit):
                continue
            validator = lineedit.validator()
            if validator is None:
                continue
            text = lineedit.text()
            if text == "":
                # Empty is valid (uses default or None)
                lineedit.setStyleSheet("")
            else:
                state, _, _ = validator.validate(text, 0)
                if state == QtGui.QValidator.Acceptable:
                    lineedit.setStyleSheet("")
                else:
                    lineedit.setStyleSheet("border: 1px solid red;")
                    all_valid = False
        self.exec_button.setEnabled(all_valid)

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
                        if self.fill_button_list[counter] is not None:
                            self.fill_button_list[counter].show()
                else:
                    # Hide related widgets if the argument has a default value
                    if arg[1] is not None:
                        self.label_list[counter].hide()
                        self.lineedit_list[counter].hide()
                        if self.fill_button_list[counter] is not None:
                            self.fill_button_list[counter].hide()

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
                q_check_box_value = bool(param.isChecked())
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

        Executes the wrapped function with error handling. If the function
        raises an exception, displays a user-friendly error dialog with the
        exception details and full traceback.

        Args:
            args (list): List of arguments to pass to the function.
        """
        try:
            self.function(*args)
        except Exception as e:
            # Display error dialog with exception details and traceback
            show_exception_dialog(e, title=self.function.__name__, parent=self)


if __name__ == "__main__":
    # Example usage:
    # app = QtWidgets.QApplication.instance()
    # button = QtWidgets.QPushButton("Hello World")
    # button.show()
    # app.exec_()
    # t = FunctionUI(your_function_here)
    # t.show()
    pass

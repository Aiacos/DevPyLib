__author__ = "Lorenzo Argentieri"

import ast
import inspect

import pymel.core as pm

try:
    from PySide6 import QtCore, QtWidgets
except:
    from PySide2 import QtCore, QtWidgets

import mayaLib.pipelineLib.utility.docs as doc


class FunctionUI(QtWidgets.QWidget):
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
        self.args = self.getParameterList()

        self.label_list = []
        self.lineedit_list = []
        self.fillButton_list = []

        row = 0
        for arg in self.args:
            if arg[0] != "self":
                # Create a label for the argument
                labelname = QtWidgets.QLabel(arg[0])

                if arg[1] is not None:
                    # Create a line edit or checkbox based on argument type
                    if isinstance(arg[1], bool):
                        lineedit = QtWidgets.QCheckBox("")
                        lineedit.setChecked(arg[1])
                    else:
                        lineedit = QtWidgets.QLineEdit(str(arg[1]))
                        fillButton = QtWidgets.QPushButton(">")
                else:
                    lineedit = QtWidgets.QLineEdit("")
                    fillButton = QtWidgets.QPushButton(">")

                self.layout.addWidget(labelname, row, 0)
                self.label_list.append(labelname)

                if fillButton:
                    self.layout.addWidget(fillButton, row, 1)
                    self.fillButton_list.append(fillButton)

                self.layout.addWidget(lineedit, row, 2)
                self.lineedit_list.append(lineedit)

                row += 1

        # Create execute button
        self.execButton = QtWidgets.QPushButton("Execute")
        # Create advanced checkbox
        self.advancedCheckBox = QtWidgets.QCheckBox("Advanced")
        self.advancedCheckBox.setChecked(False)
        self.toggleDefaultParameter(False)
        self.layout.addWidget(self.execButton, row, 2)
        self.layout.addWidget(self.advancedCheckBox, row, 0)

        # Display function documentation
        self.doclabel = QtWidgets.QLabel(doc.get_docs(func))
        self.layout.addWidget(self.doclabel, row + 1, 2)
        self.setLayout(self.layout)

        # Connect signals to slots
        self.execButton.clicked.connect(self.execFunction)
        self.advancedCheckBox.stateChanged.connect(self.toggleDefaultParameter)

        for button in self.fillButton_list:
            button.clicked.connect(self.fillWithSelected)

        # Set window properties
        self.setWindowTitle(func.__name__)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setSizePolicy(
            QtWidgets.QSizePolicy.MinimumExpanding,
            QtWidgets.QSizePolicy.MinimumExpanding,
        )
        self.setFocus()

    def fillWithSelected(self):
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

    def getParameterList(self):
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
    def toggleDefaultParameter(self, defaultvisible=False):
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
                        self.fillButton_list[counter].show()
                else:
                    # Hide related widgets if the argument has a default value
                    if arg[1] is not None:
                        self.label_list[counter].hide()
                        self.lineedit_list[counter].hide()
                        self.fillButton_list[counter].hide()

                counter += 1

    def execFunction(self):
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
                    qCheckBoxValue = True
                else:
                    qCheckBoxValue = False
                value = qCheckBoxValue
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
    # app = QtWidgets.QApplication.instance()
    # button = QtWidgets.QPushButton("Hello World")
    # button.show()
    # app.exec_()
    # print(inspect.getargspec(Prova))
    t = FunctionUI(Prova)
    t.show()

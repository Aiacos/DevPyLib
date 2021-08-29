__author__ = 'Lorenzo Argentieri'

import ast
import inspect

import pymel.core as pm
from PySide2 import QtCore, QtWidgets

import mayaLib.pipelineLib.utility.docs as doc


def test(a, b, c, d='ciao', e='stronzo', f=1):
    """
    Test Function
    :param a:
    :param b:
    :param c:
    :param d:
    :param e:
    :param f:
    :return:
    """
    print(a, b, c, d, e, f)


class Prova():
    def __init__(self, ciccia, pupu=2048):
        print('Questa e una prova')

    def motodo(self):
        print('test method')


class FunctionUI(QtWidgets.QWidget):
    def __init__(self, func, parent=None):
        super(FunctionUI, self).__init__(parent)

        self.function = func
        if inspect.isclass(func):
            self.sig = inspect.getargspec(func.__init__)
        else:
            self.sig = inspect.getargspec(func)

        self.layout = QtWidgets.QGridLayout()

        self.args = self.getParameterList()

        self.label_list = []
        self.lineedit_list = []
        self.fillButton_list = []

        row = 0
        for arg in self.args:
            if arg[0] != 'self':
                labelname = QtWidgets.QLabel(arg[0])

                if arg[1] != None:
                    if isinstance(arg[1], bool):
                        lineedit = QtWidgets.QCheckBox('')
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

                row = row + 1

        self.execButton = QtWidgets.QPushButton("Execute")
        self.advancedCheckBox = QtWidgets.QCheckBox("Advanced")
        self.advancedCheckBox.setChecked(False)
        self.toggleDefaultParameter(False)
        self.layout.addWidget(self.execButton, row, 2)
        self.layout.addWidget(self.advancedCheckBox, row, 0)

        self.doclabel = QtWidgets.QLabel(doc.getDocs(func))
        self.layout.addWidget(self.doclabel, row + 1, 2)
        self.setLayout(self.layout)

        # self.connect(self.execButton, QtCore.Signal("clicked()"), self.execFunction) # Deprecated
        self.execButton.clicked.connect(self.execFunction)
        self.advancedCheckBox.stateChanged.connect(self.toggleDefaultParameter)

        for button in self.fillButton_list:
            button.clicked.connect(self.fillWithSelected)

        self.setWindowTitle(func.__name__)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        self.setFocus()

    def fillWithSelected(self):
        button = self.sender()
        selection_list = pm.ls(sl=True)

        index = self.fillButton_list.index(button)
        lineedit = self.lineedit_list[index]

        text_list = []
        for item in selection_list:
            text_list.append(str(item))

        lineedit.setText(', '.join(text_list))

    def getParameterList(self):
        args = self.sig.args

        if len(args) == 0:
            return []

        varargs = self.sig.varargs
        keywords = self.sig.keywords
        defaults = self.sig.defaults

        if not defaults:
            defaults = []

        argspairs = []
        argslen = len(args)
        deflen = len(defaults)

        counter = 0
        defcount = 0
        for arg in args:
            if counter < (argslen - deflen):
                defval = None
            else:
                defval = defaults[defcount]
                defcount = defcount + 1

            counter = counter + 1
            pair = [arg, defval]
            argspairs.append(pair)

        return argspairs

    # SLOTS
    def toggleDefaultParameter(self, defaultvisible=False):
        counter = 0
        for arg in self.args:
            if arg[0] != 'self':
                if defaultvisible:
                    # show
                    if arg[1] != None:
                        self.label_list[counter].show()
                        self.lineedit_list[counter].show()
                        self.fillButton_list[counter].show()
                else:
                    # hide
                    if arg[1] != None:
                        self.label_list[counter].hide()
                        self.lineedit_list[counter].hide()
                        self.fillButton_list[counter].hide()

                counter = counter + 1

    def execFunction(self):
        param_list = []

        for param in self.lineedit_list:
            value = param.text()

            if isinstance(param, QtWidgets.QCheckBox):
                if param.isChecked():
                    qCheckBoxValue = True
                else:
                    qCheckBoxValue = False
                value = qCheckBoxValue
                param_list.append(value)
            elif '[' in value and ']' in value:
                value = value.replace('[', '').replace(']', '').replace("'", "").replace(' ', '').split(',')
                param_list.append(value)
            elif value.replace('.', '', 1).isdigit():
                value = ast.literal_eval(value)
                param_list.append(value)
            elif value == 'True':
                value = True
                param_list.append(value)
            elif value == 'False':
                value = False
                param_list.append(value)
            elif value == '':
                value = None
                param_list.append(value)
            elif ', ' in value:
                value = value.split(', ')
                param_list.append(value)
            else:
                param_list.append(value)

        self.wrapper(param_list)

    def wrapper(self, args):
        self.function(*args)


if __name__ == "__main__":
    # app = QtWidgets.QApplication.instance()
    # button = QtWidgets.QPushButton("Hello World")
    # button.show()
    # app.exec_()
    # print(inspect.getargspec(Prova))
    t = FunctionUI(Prova)
    t.show()

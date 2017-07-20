__author__ = 'Lorenzo Argentieri'

import pymel.core as pm
import inspect
import ast
import mayaLib.pipelineLib.docs as doc
from mayaLib.guiLib.Qt import QtCore, QtWidgets


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
    print a,b,c,d,e,f


class Prova():
    def __init__(self, ciccia, pupu=2048):
        print 'Questa e una prova'

    def motodo(self):
        print 'test method'


class FunctionUI(QtWidgets.QWidget):
    def __init__(self, func, parent=None):
        super(FunctionUI, self).__init__(parent)

        self.function = func
        self.sig = inspect.getargspec(func)

        self.layout = QtWidgets.QGridLayout()

        self.args = self.getParameterList()

        self.label_list = []
        self.lineedit_list = []

        row = 0
        for arg in self.args:
            labelname = QtWidgets.QLabel(arg[0])

            if arg[1]:
                lineedit = QtWidgets.QLineEdit(str(arg[1]))
            else:
                lineedit = QtWidgets.QLineEdit("")

            self.layout.addWidget(labelname, row, 0)
            self.label_list.append(labelname)

            self.layout.addWidget(lineedit, row, 1)
            self.lineedit_list.append(lineedit)

            row = row + 1

        self.execButton = QtWidgets.QPushButton("Execute")
        self.advancedCheckBox = QtWidgets.QCheckBox("Advanced")
        self.layout.addWidget(self.execButton, row, 1)
        self.layout.addWidget(self.advancedCheckBox, row, 0)

        self.doclabel = QtWidgets.QLabel(doc.getDocs(func))
        self.layout.addWidget(self.doclabel, row+1, 1)
        self.setLayout(self.layout)

        #self.connect(self.execButton, QtCore.Signal("clicked()"), self.execFunction) # Deprecated
        self.execButton.clicked.connect(self.execFunction)
        self.advancedCheckBox.stateChanged.connect(self.toggleDefaultParameter)

        self.setWindowTitle(func.__name__)

    def getParameterList(self):
        args = self.sig.args
        varargs = self.sig.varargs
        keywords = self.sig.keywords
        defaults = self.sig.defaults

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
            if defaultvisible:
                # show
                if arg[1]:
                    self.label_list[counter].show()
                    self.lineedit_list[counter].show()
            else:
                # hide
                if arg[1]:
                    self.label_list[counter].hide()
                    self.lineedit_list[counter].hide()

            counter = counter + 1

    def execFunction(self):
        param_list = []

        for param in self.lineedit_list:
            value = param.text()
            if value.replace('.','',1).isdigit():
                value = ast.literal_eval(value)
                param_list.append(value)
            elif value == 'True':
                value = True
                param_list.append(value)
            elif value == 'False':
                value = False
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
    t = FunctionUI(test)
    t.show()

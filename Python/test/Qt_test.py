from __future__ import division
from Qt import QtCore, QtWidgets
import sys
from math import *

__author__ = 'lorenzoargentieri'


# WORKING BASIC TEST
# app = QtWidgets.QApplication.instance()
# button = QtWidgets.QPushButton("Hello World")
# button.show()
# app.exec_()

class Form(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)
        self.browser = QtWidgets.QTextBrowser()
        self.lineedit = QtWidgets.QLineEdit("Type Expression")
        self.lineedit.selectAll()
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.browser)
        layout.addWidget(self.lineedit)
        self.setLayout(layout)
        self.lineedit.setFocus()
        self.connect(self.lineedit, QtCore.Signal("returnPressed()"), self.updateUi)
        self.setWindowTitle("Calcola")

    def updateUi(self):
        try:
            text = unicode(self.lineedit.text())
            self.browser.append("%s = <b>%s</b>" % (text, eval(text)))
        except:
            self.browser.append("<font color=red>%s is invalid!</font>" % text)


app = QtWidgets.QApplication.instance()
form = Form()
form.show()
app.exec_()

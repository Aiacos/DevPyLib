from __future__ import division
from PySide import QtCore, QtGui
import sys
from math import *

__author__ = 'lorenzoargentieri'


# app = QtGui.QApplication(sys.argv)
# window = QtGui.QMainWindow
# container = QtGui.QWidget()
#
# button = QtGui.QPushButton("Cliccami!",container)
#
# container.resize(320, 240)
# container.setWindowTitle("Mi Scappa la Cacca!")
# container.show()
#
# sys.exit(app.exec_())

class Form(QtGui.QDialog):
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)
        self.browser = QtGui.QTextBrowser()
        self.lineedit = QtGui.QLineEdit("Type Expression")
        self.lineedit.selectAll()
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.browser)
        layout.addWidget(self.lineedit)
        self.setLayout(layout)
        self.lineedit.setFocus()
        self.connect(self.lineedit, QtCore.SIGNAL("returnPressed()"), self.updateUi)
        self.setWindowTitle("Calcola")

    def updateUi(self):
        try:
            text = unicode(self.lineedit.text())
            self.browser.append("%s = <b>%s</b>" % (text, eval(text)))
        except:
            self.browser.append("<font color=red>%s is invalid!</font>" % text)



app = QtGui.QApplication.instance()
form = Form()
form.show()
app.exec_()


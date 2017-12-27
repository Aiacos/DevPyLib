__author__ = 'Lorenzo Argentieri'

import sys
import os.path
import os
import time
from PyQt4.QtGui import QWidget, QApplication
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import urllib


class InstallLibrary(QObject):
    def __init__(self, devMode=False, parent=None):
        super(InstallLibrary, self).__init__(parent)

        self.libUrl = 'https://github.com/Aiacos/DevPyLib/archive/master.zip'
        self.homeUser = os.getenv("HOME")
        self.mayaScriptPath = self.homeUser + '/Library/Preferences/Autodesk/maya/scripts/'

        self.port = ':7005'
        self.libName = 'mayaLib'

        self.updateDevMode(devMode)


    def updateDevMode(self, devMode=False):
        #
        self.devMode = devMode

        if devMode:
            self.libDir = self.homeUser + '/Dropbox/3D/Maya/Script_DEF/DevPyLib'
        else:
            self.libDir = self.homeUser + '/Library/Preferences/Autodesk/maya/scripts/DevPyLib-master'

        self.installCommand = \
"""
# Install mayaLib
import sys
import maya.cmds as cmds

libDir = '""" + self.libDir + """'
port = '""" + self.port + """'
libName = '""" + self.libName + """'

# Open Maya port
if not cmds.commandPort(port, q=True):
    cmds.commandPort(n=port)

# Add develpment PATH
if not libDir in sys.path:
    sys.path.append(libDir)
    __import__(libName)
else:
    reload(__import__(libName))
"""

    def installInMayaUserSetup(self):
        userSetup_path = self.mayaScriptPath
        fileName = 'userSetup.py'
        filePath = userSetup_path + fileName
        if os.path.isdir(userSetup_path):
            if os.path.exists(filePath):
                # append
                f = open(filePath, 'a')
                f.write('\n')
                f.write(self.installCommand)

                f.close()
            else:
                # create and append
                f = open(filePath, 'w')
                f.write(self.installCommand)
                f.close()
        else:
            print 'ERROR: Directory not exist!'

    def install(self):
        if not self.devMode:
            self.download()
        self.installInMayaUserSetup()

    def uninstall(self):
        userSetup_path = self.mayaScriptPath
        fileName = 'userSetup.py'
        filePath = userSetup_path + fileName
        if os.path.isdir(userSetup_path):
            if os.path.exists(filePath):
                f = open(filePath, 'r')
                script = f.read()
                f.close()

                f = open(filePath, 'w')
                script = script.replace(self.installCommand, '')
                f.write(script)
                f.close()

        self.delete()

    def reporthook(self, count, block_size, total_size):
        global start_time
        if count == 0:
            start_time = time.time()
            return
        duration = time.time() - start_time
        progress_size = int(count * block_size)
        speed = int(progress_size / (1024 * duration))
        percent = int(count * block_size * 100 / total_size)
        sys.stdout.write("\r...%d%%, %d MB, %d KB/s, %d seconds passed\n" %
                         (percent, progress_size / (1024 * 1024), speed, duration))
        sys.stdout.flush()

    def download(self, zipFilename='master.zip'):
        cd_cmd = 'cd ' + self.mayaScriptPath + ' && '

        if os.path.isdir(self.mayaScriptPath + 'DevPyLib-master'):
            rm_cmd = cd_cmd + 'rm -R ' + 'DevPyLib-master'
            os.system(rm_cmd)

        # download
        urllib.urlretrieve(self.libUrl, self.mayaScriptPath + zipFilename, self.reporthook)

        # unzip
        unzip_cmd = cd_cmd + 'unzip ' + zipFilename
        os.system(unzip_cmd)

        # remove
        rm_cmd = cd_cmd + 'rm -R ' + zipFilename
        os.system(rm_cmd)

    def delete(self):
        cd_cmd = 'cd ' + self.mayaScriptPath + ' && '
        # remove
        if os.path.isdir(self.mayaScriptPath + 'DevPyLib-master'):
            rm_cmd = cd_cmd + 'rm -R DevPyLib-master'
            os.system(rm_cmd)

class InstallWindow(QWidget):
    def __init__(self, devMode=False, parent=None):
        super(InstallWindow, self).__init__(parent)
        self.libManager = InstallLibrary(devMode=devMode)

        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.setWindowTitle('Install Maya Library')

        # browse install path
        self.installDirLabel = QLabel('Install Directory')
        self.installDirLineEdit = QLineEdit(self.libManager.mayaScriptPath)
        self.installDirButton = QPushButton('Select Folder')
        self.layout.addWidget(self.installDirLabel, 0, 0)
        self.layout.addWidget(self.installDirLineEdit, 0, 1)
        self.layout.addWidget(self.installDirButton, 0, 2)

        # install button
        self.installButton = QPushButton('Install')
        self.layout.addWidget(self.installButton, 1, 2)

        self.installDirButton.clicked.connect(self.selectFile)
        self.installButton.clicked.connect(self.installLib)

    def selectFile(self):
        self.installDirLineEdit.setText(QFileDialog.getExistingDirectory(self, "Select Directory"))

    def installLib(self):
        self.libManager.install()



def main(devMode=False):
    app = QApplication(sys.argv)

    w = InstallWindow(devMode=devMode)
    w.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main(devMode=False)

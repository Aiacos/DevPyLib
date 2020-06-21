__author__ = 'Lorenzo Argentieri'

import sys
from sys import platform as _platform
import os.path
import os
#import pip
import time
import urllib
import mayaLib.installCmd as installCmd


# import installCmd
def buildInstallCmd(libDir, libName, port):
    installCommand = \
"""
# Install mayaLib
import sys
import maya.cmds as cmds
import maya.utils

libDir = '""" + libDir + """'
port = '""" + str(port) + """'
libName = '""" + libName + """'

# Open Maya port
if not cmds.commandPort(port, q=True):
    cmds.commandPort(n=port)

# Add develpment PATH
if not libDir in sys.path:
    sys.path.append(libDir)
    __import__(libName)
else:
    reload(__import__(libName))

import mayaLib.guiLib.mainMenu as mm
cmds.evalDeferred("libMenu = mm.MainMenu('""" + libDir + """')")
"""

    return installCommand

class InstallLibrary():
    def __init__(self, devMode=False, parent=None, libDir=None):
        super(InstallLibrary, self).__init__(parent)

        self.libUrl = 'https://github.com/Aiacos/DevPyLib/archive/master.zip'
        self.homeUser = os.getenv("HOME")
        self.winPath = ''
        self.linuxPath = ''
        self.osxPath = '/Library/Preferences/Autodesk'
        self.mayaScriptPath = '/maya/scripts/'

        self.port = ':4434'
        self.libName = 'mayaLib'

        if _platform == "linux" or _platform == "linux2":
            # linux
            self.mayaScriptPath = self.homeUser + self.linuxPath + self.mayaScriptPath
        elif _platform == "darwin":
            # MAC OS X
            self.mayaScriptPath = self.homeUser + self.osxPath + self.mayaScriptPath
        elif _platform == "win32" or _platform == "win64":
            # Windows
            self.mayaScriptPath = self.homeUser + self.linuxPath + self.mayaScriptPath

        print(self.mayaScriptPath)

    def updateDevMode(self, devPath=False):
        self.devMode = True if devPath != '' else False

        if devPath:
            self.libDir = devPath

        self.installCommand = buildInstallCmd(self.libDir, self.libName, self.port)

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
            print('ERROR: Directory not exist!')

    def install(self):
        self.uninstall()
        if not self.devMode:
            self.download()
        self.installInMayaUserSetup()

        # install dependency pkg
        #pip.main(['install', 'numpy'])

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


if __name__ == "__main__":
    pass

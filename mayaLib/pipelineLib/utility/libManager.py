__author__ = 'Lorenzo Argentieri'

import os
import os.path
# import pip
import pathlib
import platform
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

import git


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


class InstallLibrary:
    def __init__(self, devMode=False, parent=None, libDir=None):
        """
        Initialize the InstallLibrary.

        Args:
            devMode (bool, optional): Install in development mode. Defaults to False.
            parent (QWidget, optional): Parent widget. Defaults to None.
            libDir (pathlib.Path, optional): Path to the library installation. Defaults to None.

        Attributes:
            libUrl (str): URL of the zip library file.
            homeUser (pathlib.Path): Path to the user home.
            winPath (str): Path to the windows maya script directory.
            linuxPath (str): Path to the linux maya script directory.
            osxPath (str): Path to the osx maya script directory.
            mayaScriptPath (pathlib.Path): Path to the maya script directory.
            wokspace_path (pathlib.Path): Path to the workspace directory.
            port (str): Maya command port.
            libName (str): Name of the library.
            libDir (pathlib.Path): Path to the library installation.
        """

        self.libUrl = 'https://github.com/Aiacos/DevPyLib/archive/master.zip'
        self.homeUser = pathlib.Path.home()
        self.winPath = "Documents"
        self.linuxPath = "Documents"
        self.osxPath = '/Library/Preferences/Autodesk'
        self.mayaScriptPath = '/maya/scripts/'
        self.wokspace_path = self.homeUser / "Documents" / "workspace"

        self.port = ':4434'
        self.libName = 'mayaLib'

        if platform.system() == "Linux":
            self.mayaScriptPath = self.homeUser / self.linuxPath / self.mayaScriptPath
        elif platform.system() == "OSX":
            self.mayaScriptPath = self.homeUser / self.osxPath / self.mayaScriptPath
        elif platform.system() == "Windows":
            self.mayaScriptPath = self.homeUser / self.linuxPath / self.mayaScriptPath

        self.libDir = self.wokspace_path / 'DevPyLib'


    def installFromGit(self, gitUrl='https://github.com/Aiacos/DevPyLib'):
        """
        Install the library by cloning the git repository.

        Args:
            gitUrl (str, optional): The git repository URL. Defaults to 'https://github.com/Aiacos/DevPyLib'.

        Returns:
            bool: True if successful, False if not.
        """

        try:
            print("Cloning: ", gitUrl, " in folder: ", self.libDir)
            repo = git.Repo.clone_from(gitUrl, self.libDir)
            print("Clone Complete")
            return True
        except:
            print("Clone Failed")
            return False

    def pullFromGit(self):
        """
        Pull the latest changes from the git repository.

        Returns:
            bool: True if successful, False if not.
        """
        try:
            print('Pulling: ', self.libDir)
            repo = git.Repo(self.libDir)
            repo.remotes.origin.pull()
            print("Pull Complete")
            return True
        except:
            print("Pull Failed")
            return False

    def updateDevMode(self, devPath=False):
        """
        Update the development mode settings for the library.

        Args:
            devPath (str, optional): The development path to set. Defaults to False.

        Sets:
            self.devMode (bool): True if devPath is provided, otherwise False.
            self.libDir (str): The development path if devPath is provided.
            self.installCommand (str): The installation command constructed based on the library directory, name, and port.
        """

        self.devMode = True if devPath != '' else False

        if devPath:
            self.libDir = devPath

        self.installCommand = buildInstallCmd(self.libDir, self.libName, self.port)

    def installInMayaUserSetup(self):
        """
        Install the library in Maya user setup.

        This method writes the installation command into Maya user setup file.
        If the file does not exist, it creates a new one.
        If the file exists, it appends the command to the end of the file.

        Args:
            None

        Returns:
            None

        """
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
        """
        Install the library by performing the following actions:

        1. Uninstall any existing installation.
        2. Download the library if not in development mode.
        3. Install the library in the Maya user setup.

        Note:
            This method currently does not install dependency packages,
            but a placeholder for installing 'numpy' is included.

        Args:
            None

        Returns:
            None
        """

        self.uninstall()
        if not self.devMode:
            self.download()
        self.installInMayaUserSetup()

        # install dependency pkg
        # pip.main(['install', 'numpy'])

    def uninstall(self):
        """
        Uninstall the library by performing the following actions:

        1. Remove the line in the Maya user setup script
           that imports the library.
        2. Delete the library directory.

        Args:
            None

        Returns:
            None
        """
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
        """
        Report hook for urlretrieve that prints the percentage of the
        file downloaded to the console.

        Args:
            count (int): The number of blocks transferred so far.
            block_size (int): The size of each block in bytes.
            total_size (int): The total size of the file in bytes.

        Returns:
            None
        """
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
        """
        Download the library from the given URL.

        This method will download the library to the given path, unzip it,
        and then remove the zip file.

        Args:
            zipFilename (str): The name of the zip file to download.

        Returns:
            None
        """

        cd_cmd = 'cd ' + self.mayaScriptPath + ' && '

        if os.path.isdir(self.mayaScriptPath + 'DevPyLib-master'):
            rm_cmd = cd_cmd + 'rm -R ' + 'DevPyLib-master'
            os.system(rm_cmd)

        # download
        urllib.request.urlretrieve(self.libUrl, self.mayaScriptPath + zipFilename, self.reporthook)

        # unzip
        unzip_cmd = cd_cmd + 'unzip ' + zipFilename
        os.system(unzip_cmd)

        # remove
        rm_cmd = cd_cmd + 'rm -R ' + zipFilename
        os.system(rm_cmd)

    def delete(self):
        """
        Delete the DevPyLib-master directory from the Maya script path.

        This method constructs a command to navigate to the Maya script path
        and remove the 'DevPyLib-master' directory if it exists.

        Args:
            None

        Returns:
            None
        """

        cd_cmd = 'cd ' + self.mayaScriptPath + ' && '
        # remove
        if os.path.isdir(self.mayaScriptPath + 'DevPyLib-master'):
            rm_cmd = cd_cmd + 'rm -R DevPyLib-master'
            os.system(rm_cmd)


if __name__ == "__main__":
    pass

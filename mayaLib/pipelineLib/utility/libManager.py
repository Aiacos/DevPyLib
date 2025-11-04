__author__ = 'Lorenzo Argentieri'

import os
import os.path
# import pip
import pathlib
import platform
import shutil
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from textwrap import dedent

import git
import pymel.core as pm


# import installCmd
def buildInstallCmd(libDir, libName, port):
    lib_dir_literal = repr(libDir)
    port_literal = repr(str(port))
    lib_name_literal = repr(libName)
    installCommand = dedent(
        f"""
        # Install mayaLib
        import sys
        import importlib
        import maya.cmds as cmds
        import maya.utils

        libDir = {lib_dir_literal}
        port = {port_literal}
        libName = {lib_name_literal}

        # Open Maya port
        if not cmds.commandPort(port, q=True):
            cmds.commandPort(n=port)

        # Add development PATH
        if libDir not in sys.path:
            sys.path.append(libDir)
            __import__(libName)
        else:
            importlib.reload(__import__(libName))

        import mayaLib.guiLib.mainMenu as mm
        cmds.evalDeferred(f"libMenu = mm.MainMenu({lib_dir_literal})")
        """
    )

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

        # Cross-platform Maya script paths
        self.port = ':4434'
        self.libName = 'mayaLib'

        # Detect platform and set appropriate paths
        current_platform = platform.system()

        if current_platform == "Linux":
            # Linux: ~/maya/scripts or ~/Documents/maya/scripts
            self.mayaScriptPath = self.homeUser / "maya" / "scripts"
            if not self.mayaScriptPath.exists():
                self.mayaScriptPath = self.homeUser / "Documents" / "maya" / "scripts"
            self.workspace_path = self.homeUser / "workspace"
            if not self.workspace_path.exists():
                self.workspace_path = self.homeUser / "Documents" / "workspace"

        elif current_platform == "Darwin":  # macOS
            # macOS: ~/Library/Preferences/Autodesk/maya/scripts
            self.mayaScriptPath = self.homeUser / "Library" / "Preferences" / "Autodesk" / "maya" / "scripts"
            self.workspace_path = self.homeUser / "Documents" / "workspace"

        elif current_platform == "Windows":
            # Windows: %USERPROFILE%\Documents\maya\scripts
            self.mayaScriptPath = self.homeUser / "Documents" / "maya" / "scripts"
            self.workspace_path = self.homeUser / "Documents" / "workspace"
        else:
            # Fallback for unknown platforms
            self.mayaScriptPath = self.homeUser / "Documents" / "maya" / "scripts"
            self.workspace_path = self.homeUser / "Documents" / "workspace"

        self.libDir = self.workspace_path / 'DevPyLib'


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
            git.Repo.clone_from(gitUrl, self.libDir)
            print("Clone Complete")
            return True
        except Exception as e:
            print(f"Clone Failed: {e}")
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
        except Exception as e:
            print(f"Pull Failed: {e}")
            return False

    def copyToMayaEnv(self):
        """
        Copy the library paths to the Maya environment file (Maya.env) for the current user.

        This function ensures that the specified library directory is added to the Maya environment
        by checking if the entries for `MAYA_APP_DIR` and `PYTHONPATH` are already present in the
        Maya.env file. If not present, it appends these entries to the file.

        Returns:
            bool: True if the entries were successfully added, False if the entries already exist or
                  if there was any error during the process.
        """

        # Cross-platform Maya.env path detection
        maya_version = str(pm.about(version=True))
        current_platform = platform.system()

        if current_platform == "Linux":
            # Linux: ~/maya/<version>/Maya.env
            mayaEnvPath = self.homeUser / "maya" / maya_version / "Maya.env"
            if not mayaEnvPath.parent.exists():
                mayaEnvPath = self.homeUser / "Documents" / "maya" / maya_version / "Maya.env"
        elif current_platform == "Darwin":  # macOS
            # macOS: ~/Library/Preferences/Autodesk/maya/<version>/Maya.env
            mayaEnvPath = self.homeUser / "Library" / "Preferences" / "Autodesk" / "maya" / maya_version / "Maya.env"
        else:  # Windows
            # Windows: %USERPROFILE%\Documents\maya\<version>\Maya.env
            mayaEnvPath = self.homeUser / "Documents" / "maya" / maya_version / "Maya.env"

        maya_app_dir = "MAYA_APP_DIR = " + str(self.libDir)
        python_path = "PYTHONPATH = " + str(self.libDir)

        try:
            if os.path.exists(mayaEnvPath):
                with open(mayaEnvPath, 'r') as f:
                    lines = f.readlines()
                    if maya_app_dir in lines:
                        print("string " + maya_app_dir + " already present in Maya.env")
                        return False
                    if python_path in lines:
                        print("string " + python_path + " already present in Maya.env")
                        return False
            else:
                print("Maya.env file not found")
                return False
        except Exception as e:
            print(f"Error while reading Maya.env: {e}")
            return False

        try:
            if os.path.exists(mayaEnvPath):
                with open(mayaEnvPath, 'a') as f:
                    f.write(maya_app_dir + "\n")
                    f.write(python_path + "\n")
                return True
            else:
                print("Maya.env file not found")
                return False
        except Exception as e:
            print(f"Error while writing to Maya.env: {e}")
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
        filePath = pathlib.Path(userSetup_path) / fileName
        if userSetup_path.is_dir():
            if filePath.exists():
                with filePath.open('a', encoding='utf-8') as handle:
                    handle.write('\n')
                    handle.write(self.installCommand)
            else:
                filePath.write_text(self.installCommand, encoding='utf-8')
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
        filePath = pathlib.Path(userSetup_path) / fileName
        if userSetup_path.is_dir():
            if filePath.exists():
                script = filePath.read_text(encoding='utf-8')
                filePath.write_text(script.replace(self.installCommand, ''), encoding='utf-8')

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
        and then remove the zip file. Cross-platform implementation using zipfile.

        Args:
            zipFilename (str): The name of the zip file to download.

        Returns:
            None
        """

        download_dir = pathlib.Path(self.mayaScriptPath)
        zip_path = download_dir / zipFilename
        extracted_dir = download_dir / 'DevPyLib-master'

        # Remove existing directory if present
        if extracted_dir.exists():
            try:
                shutil.rmtree(extracted_dir)
                print(f"Removed existing directory: {extracted_dir}")
            except Exception as e:
                print(f"Error removing directory: {e}")

        # Download
        try:
            urllib.request.urlretrieve(self.libUrl, str(zip_path), self.reporthook)
            print(f"Downloaded to: {zip_path}")
        except Exception as e:
            print(f"Error downloading file: {e}")
            return

        # Unzip using zipfile module (cross-platform)
        try:
            with zipfile.ZipFile(str(zip_path), 'r') as zip_ref:
                zip_ref.extractall(str(download_dir))
            print(f"Extracted to: {download_dir}")
        except Exception as e:
            print(f"Error extracting zip file: {e}")
            return

        # Remove zip file
        try:
            zip_path.unlink()
            print(f"Removed zip file: {zip_path}")
        except Exception as e:
            print(f"Error removing zip file: {e}")

    def delete(self):
        """
        Delete the DevPyLib-master directory from the Maya script path.

        Cross-platform implementation using shutil.

        Args:
            None

        Returns:
            None
        """

        delete_dir = pathlib.Path(self.mayaScriptPath) / 'DevPyLib-master'

        if delete_dir.exists():
            try:
                shutil.rmtree(delete_dir)
                print(f"Deleted directory: {delete_dir}")
            except Exception as e:
                print(f"Error deleting directory: {e}")


if __name__ == "__main__":
    pass

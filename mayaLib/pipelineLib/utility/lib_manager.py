__author__ = 'Lorenzo Argentieri'

"""Library and module management utilities.

Provides tools for managing Python library paths and module
imports in Maya.
"""

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
def build_install_cmd(lib_dir, lib_name, port):
    """Build Python installation command for remote Maya execution.

    Generates a self-contained Python script string that can be sent to
    a running Maya instance via commandPort to install and initialize a library.

    Args:
        lib_dir: Directory path containing the library to install
        lib_name: Name of the library module to import
        port: Maya commandPort number to connect to

    Returns:
        str: Multi-line Python script ready for remote execution

    Example:
        >>> cmd = build_install_cmd('/path/to/DevPyLib', 'mayaLib', 7001)
        >>> # Send cmd to Maya via commandPort
    """
    lib_dir_literal = repr(lib_dir)
    port_literal = repr(str(port))
    lib_name_literal = repr(lib_name)
    install_command = dedent(
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

        import mayaLib.guiLib.main_menu as mm
        cmds.evalDeferred(f"libMenu = mm.MainMenu({lib_dir_literal})")
        """
    )

    return install_command


class InstallLibrary:
    """Library installation and management for Maya environments.

    Handles cross-platform installation, updating, and configuration of the DevPyLib
    library. Manages Python paths, Maya environment variables, and plugin loading
    across Windows, macOS, and Linux platforms. Supports both development and
    production installation modes.

    Attributes:
        libUrl: URL to the library zip file
        homeUser: User home directory path
        mayaScriptPath: Platform-specific Maya scripts directory
        workspace_path: Workspace directory path
        libDir: Installation directory path
        libName: Library module name
        dev_mode: Whether in development mode

    Example:
        >>> installer = InstallLibrary(lib_dir='/path/to/DevPyLib')
        >>> installer.install_from_git()
        >>> installer.install_in_maya_user_setup()
    """
    def __init__(self, dev_mode=False, parent=None, lib_dir=None):
        """
        Initialize the InstallLibrary.

        Args:
            dev_mode (bool, optional): Install in development mode. Defaults to False.
            parent (QWidget, optional): Parent widget. Defaults to None.
            lib_dir (pathlib.Path, optional): Path to the library installation. Defaults to None.

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

        self.lib_url = 'https://github.com/Aiacos/DevPyLib/archive/master.zip'
        self.home_user = pathlib.Path.home()

        # Cross-platform Maya script paths
        self.port = ':4434'
        self.lib_name = 'mayaLib'

        # Detect platform and set appropriate paths
        current_platform = platform.system()

        if current_platform == "Linux":
            # Linux: ~/maya/scripts or ~/Documents/maya/scripts
            self.maya_script_path = self.home_user / "maya" / "scripts"
            if not self.maya_script_path.exists():
                self.maya_script_path = self.home_user / "Documents" / "maya" / "scripts"
            self.workspace_path = self.home_user / "workspace"
            if not self.workspace_path.exists():
                self.workspace_path = self.home_user / "Documents" / "workspace"

        elif current_platform == "Darwin":  # macOS
            # macOS: ~/Library/Preferences/Autodesk/maya/scripts
            self.maya_script_path = self.home_user / "Library" / "Preferences" / "Autodesk" / "maya" / "scripts"
            self.workspace_path = self.home_user / "Documents" / "workspace"

        elif current_platform == "Windows":
            # Windows: %USERPROFILE%\Documents\maya\scripts
            self.maya_script_path = self.home_user / "Documents" / "maya" / "scripts"
            self.workspace_path = self.home_user / "Documents" / "workspace"
        else:
            # Fallback for unknown platforms
            self.maya_script_path = self.home_user / "Documents" / "maya" / "scripts"
            self.workspace_path = self.home_user / "Documents" / "workspace"

        self.lib_dir = self.workspace_path / 'DevPyLib'

        if lib_dir:
            self.lib_dir = lib_dir

        self.dev_mode = dev_mode

    def install_from_git(self, git_url='https://github.com/Aiacos/DevPyLib'):
        """
        Install the library by cloning the git repository.

        Args:
            git_url (str, optional): The git repository URL. Defaults to 'https://github.com/Aiacos/DevPyLib'.

        Returns:
            bool: True if successful, False if not.
        """

        try:
            print("Cloning: ", git_url, " in folder: ", self.lib_dir)
            git.Repo.clone_from(git_url, self.lib_dir)
            print("Clone Complete")
            return True
        except (git.GitCommandError, OSError) as e:
            print(f"Clone Failed: {e}")
            return False

    def pull_from_git(self):
        """
        Pull the latest changes from the git repository.

        Returns:
            bool: True if successful, False if not.
        """
        try:
            print('Pulling: ', self.lib_dir)
            repo = git.Repo(self.lib_dir)
            repo.remotes.origin.pull()
            print("Pull Complete")
            return True
        except (git.GitCommandError, OSError) as e:
            print(f"Pull Failed: {e}")
            return False

    def copy_to_maya_env(self):
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
            maya_env_path = self.home_user / "maya" / maya_version / "Maya.env"
            if not maya_env_path.parent.exists():
                maya_env_path = self.home_user / "Documents" / "maya" / maya_version / "Maya.env"
        elif current_platform == "Darwin":  # macOS
            # macOS: ~/Library/Preferences/Autodesk/maya/<version>/Maya.env
            maya_env_path = self.home_user / "Library" / "Preferences" / "Autodesk" / "maya" / maya_version / "Maya.env"
        else:  # Windows
            # Windows: %USERPROFILE%\Documents\maya\<version>\Maya.env
            maya_env_path = self.home_user / "Documents" / "maya" / maya_version / "Maya.env"

        maya_app_dir = "MAYA_APP_DIR = " + str(self.lib_dir)
        python_path = "PYTHONPATH = " + str(self.lib_dir)

        try:
            if os.path.exists(maya_env_path):
                with open(maya_env_path, 'r', encoding='utf-8') as f:
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
        except (IOError, OSError) as e:
            print(f"Error while reading Maya.env: {e}")
            return False

        try:
            if os.path.exists(maya_env_path):
                with open(maya_env_path, 'a', encoding='utf-8') as f:
                    f.write(maya_app_dir + "\n")
                    f.write(python_path + "\n")
                return True
            else:
                print("Maya.env file not found")
                return False
        except (IOError, OSError) as e:
            print(f"Error while writing to Maya.env: {e}")
            return False

    def update_dev_mode(self, dev_path=False):
        """
        Update the development mode settings for the library.

        Args:
            dev_path (str, optional): The development path to set. Defaults to False.

        Sets:
            self.dev_mode (bool): True if dev_path is provided, otherwise False.
            self.lib_dir (str): The development path if dev_path is provided.
            self.install_command (str): The installation command constructed based on the library directory, name, and port.
        """

        self.dev_mode = True if dev_path != '' else False

        if dev_path:
            self.lib_dir = dev_path

        self.install_command = build_install_cmd(self.lib_dir, self.lib_name, self.port)

    def install_in_maya_user_setup(self):
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
        user_setup_path = self.maya_script_path
        file_name = 'userSetup.py'
        file_path = pathlib.Path(user_setup_path) / file_name
        if user_setup_path.is_dir():
            if file_path.exists():
                with file_path.open('a', encoding='utf-8') as handle:
                    handle.write('\n')
                    handle.write(self.install_command)
            else:
                file_path.write_text(self.install_command, encoding='utf-8')
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
        if not self.dev_mode:
            self.download()
        self.install_in_maya_user_setup()

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
        user_setup_path = self.maya_script_path
        file_name = 'userSetup.py'
        file_path = pathlib.Path(user_setup_path) / file_name
        if user_setup_path.is_dir():
            if file_path.exists():
                script = file_path.read_text(encoding='utf-8')
                file_path.write_text(script.replace(self.install_command, ''), encoding='utf-8')

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

    def download(self, zip_filename='master.zip'):
        """
        Download the library from the given URL.

        This method will download the library to the given path, unzip it,
        and then remove the zip file. Cross-platform implementation using zipfile.

        Args:
            zip_filename (str): The name of the zip file to download.

        Returns:
            None
        """

        download_dir = pathlib.Path(self.maya_script_path)
        zip_path = download_dir / zip_filename
        extracted_dir = download_dir / 'DevPyLib-master'

        # Remove existing directory if present
        if extracted_dir.exists():
            try:
                shutil.rmtree(extracted_dir)
                print(f"Removed existing directory: {extracted_dir}")
            except (OSError, PermissionError) as e:
                print(f"Error removing directory: {e}")

        # Download
        try:
            urllib.request.urlretrieve(self.lib_url, str(zip_path), self.reporthook)
            print(f"Downloaded to: {zip_path}")
        except (urllib.error.URLError, IOError) as e:
            print(f"Error downloading file: {e}")
            return

        # Unzip using zipfile module (cross-platform)
        try:
            with zipfile.ZipFile(str(zip_path), 'r') as zip_ref:
                zip_ref.extractall(str(download_dir))
            print(f"Extracted to: {download_dir}")
        except (zipfile.BadZipFile, IOError) as e:
            print(f"Error extracting zip file: {e}")
            return

        # Remove zip file
        try:
            zip_path.unlink()
            print(f"Removed zip file: {zip_path}")
        except (OSError, PermissionError) as e:
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

        delete_dir = pathlib.Path(self.maya_script_path) / 'DevPyLib-master'

        if delete_dir.exists():
            try:
                shutil.rmtree(delete_dir)
                print(f"Deleted directory: {delete_dir}")
            except (OSError, PermissionError) as e:
                print(f"Error deleting directory: {e}")


if __name__ == "__main__":
    pass

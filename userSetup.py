import importlib
import os
import sys
from pathlib import Path

import maya.cmds as cmds


def install_requirements(requiremensts_dir):
    """
    Installs the Python packages listed in the requirements.txt file located in the specified directory.

    Args:
        requiremensts_dir (str): The directory path where the requirements.txt file is located.

    Raises:
        Exception: If an error occurs during the installation process, an exception is caught and its message is printed.
    """
    try:
        os.system("pip install -r " + requiremensts_dir + "/requirements.txt")
        print("All requirements installed successfully!")
    except Exception as e:
        print(f"An error occurred: {e}")


libDir = (Path.home() / "Documents" / "workspace" / "DevPyLib").as_posix()
port = "4434"
libName = "mayaLib"

install_requirements(libDir)

# Open Maya port
try:
    if not cmds.commandPort(port, q=True):
        cmds.commandPort(n=port)
except:
    pass

# Add develpment PATH
if not libDir in sys.path:
    sys.path.append(libDir)
    __import__(libName)
else:
    importlib.reload(__import__(libName))
    # reload(__import__(libName))


command = str(
    "import mayaLib.guiLib.mainMenu as mm; libmenu = mm.MainMenu('" + str(libDir) + "')"
)
cmds.evalDeferred(command, lowestPriority=True)

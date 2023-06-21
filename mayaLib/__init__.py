import mayaLib.animationLib
import mayaLib.fluidLib
import mayaLib.guiLib
import mayaLib.lookdevLib
import mayaLib.modelLib
import mayaLib.pipelineLib
import mayaLib.rigLib
import mayaLib.shaderLib
import mayaLib.utility


import sys
from pathlib import Path
import importlib
import pip
import maya.cmds as cmds

# Install mayaLib
REQUIRED = {'pathlib', 'numpy'}

def install(package):
    # subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    pip.main(['install', package])


def install_required(REQUIRED):
    for mod in REQUIRED:
        install(mod)


libDir = (Path.home() / 'workspace' / 'DevPyLib').as_posix()
port = '4434'
libName = 'mayaLib'

# Open Maya port
if not cmds.commandPort(port, q=True):
    cmds.commandPort(n=port)


import mayaLib.guiLib.mainMenu as mm
command = str("libmenu = mayaLib.guiLib.MainMenu('" + str(libDir) + "')")
if 'libmenu' not in locals():
    cmds.evalDeferred(command, lowestPriority=True)

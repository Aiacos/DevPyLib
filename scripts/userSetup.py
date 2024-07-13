import os
import sys
from pathlib import Path
import subprocess
import importlib
import pip
import maya.cmds as cmds
import maya.utils

# Install mayaLib
REQUIRED = {'pymel', 'pathlib', 'numpy'}

def install(package):
    #subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    pip.main(['install', package])


def install_required(REQUIRED):
    for mod in REQUIRED:
        install(mod)
        
#install_required(REQUIRED)

libDir = (Path.home() / 'Documents' / 'workspace' / 'DevPyLib').as_posix()
port = '4434'
libName = 'mayaLib'

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

import mayaLib.guiLib.mainMenu as mm
command = str("libmenu = mm.MainMenu('" + str(libDir) + "')")
cmds.evalDeferred(command, lowestPriority=True)

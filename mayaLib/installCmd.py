__author__ = 'Lorenzo Argentieri'



def buildInstallCmd(libDir, libName, port):
    installCommand = \
"""
# Install mayaLib
import os
import sys
import subprocess
import pip
import maya.cmds as cmds
import maya.utils

def install(package):
    #subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    pip.main(['install', package])

REQUIRED = {'pathlib', 'numpy'}
for mod in REQUIRED:
    install(mod)

import pathlib

libDir = str(pathlib.Path.home() / 'Documents' / 'workspace' / 'DevPyLib')
port = '4434'
libName = 'mayaLib'

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
cmds.evalDeferred("libMenu = mm.MainMenu('libDir')")
"""

    return installCommand
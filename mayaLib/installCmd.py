__author__ = 'Lorenzo Argentieri'



def buildInstallCmd(libDir, libName, port):
    installCommand = \
"""
# Install mayaLib
import sys
import maya.cmds as cmds
import maya.utils

libDir = '""" + libDir + """'
port = '""" + port + """'
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
cmds.evalDeferred('libMenu = mm.MainMenu()')
"""

    return installCommand
__author__ = 'Lorenzo Argentieri'

import sys
import maya.cmds as cmds

libDir = '/Users/lorenzoargentieri/Dropbox/3D/Maya/Script_DEF/DevPyLib'
port = ':5000'
libName = 'mayaLib'

# Wing IDE
wingide_stub = '/Users/lorenzoargentieri/Dropbox/3D/Maya/Script_DEF/DevPyLib/wingIDE'
if wingide_stub not in sys.path: sys.path.append(wingide_stub)

import wingdbstub
wingdbstub.Ensure()

# Open Maya port
if not cmds.commandPort(port, q=True):
    cmds.commandPort(n=port)

# Add develpment PATH
if not libDir in sys.path:
    sys.path.append(libDir)
else:
    reload(__import__(libName))
    print 'Module: "' + libName + '" reloaded'

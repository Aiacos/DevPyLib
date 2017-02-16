__author__ = 'Lorenzo Argentieri'

import maya.cmds as cmds

## Var ##

filename = '/home/user/somefile'
newExtension = '.tx'
newPath = path = cmds.workspace(q=True, dir=True)+''
oldPath = ''
## def ##

def replacePath(fileName, oldPath, newPath):
    newString = fileName.replace(oldPath,newPath)
    return newString

def changeExtension(filename,newExtension):
    (prefix, sep, suffix) = filename.rpartition('.')
    return prefix + newExtension

print changeExtension(filename,newExtension)

## Main ##

# Gets all 'file' nodes in maya
fileList = cmds.ls(type='file')
#fileList = cmds.listConnections(type='file')

# For each file node..
for f in fileList:
    # Get the name of the image attached to it
    texture_filename = cmds.getAttr(f + '.fileTextureName')
    newTex = changeExtension(texture_filename,newExtension)#extension
    #newTex = replacePath(texture_filename, oldPath, newPath)#path
    cmds.setAttr(f + '.fileTextureName',newTex,type="string")
    print newTex


# -- ToDo
# - Gui
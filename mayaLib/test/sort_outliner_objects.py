import pymel.core as pm
import maya.cmds as cmd
import maya.mel as mel

muscle_list = cmd.ls(sl=True)

muscle_list.sort()
for m in muscle_list:
    cmd.parent(m, 'sort_grp')
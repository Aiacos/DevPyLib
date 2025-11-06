"""Outliner sorting utilities test.

Example script for organizing and sorting Maya outliner
hierarchy programmatically.
"""

import maya.cmds as cmd

muscle_list = cmd.ls(sl=True)

muscle_list.sort()
for m in muscle_list:
    cmd.parent(m, "sort_grp")

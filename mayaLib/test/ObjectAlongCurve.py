## Duplicate Object Along Curve

import maya.cmds as cmds

## Var ##
pointsNumber = 5

curve = cmds.ls(sl=True)
nameBuilder_locator = curve[0] + "_loc"  # in function, lacal variables
nameBuilder_joint = curve[0] + "_jnt"  # in function, local variables

spacing = 1.0 / (pointsNumber - 1)


## Main --wip

def deleteConnection(plug):
    # """ Equivalent of MEL: CBdeleteConnection """

    if cmds.connectionInfo(plug, isDestination=True):
        plug = cmds.connectionInfo(plug, getExactDestination=True)
        readOnly = cmds.ls(plug, ro=True)
        # delete -icn doesn't work if destination attr is readOnly
        if readOnly:
            source = cmds.connectionInfo(plug, sourceFromDestination=True)
            cmds.disconnectAttr(source, plug)
        else:
            cmds.delete(plug, icn=True)


def pointMode():
    for p in range(1, pointsNumber):
        if p == 1:
            cmds.spaceLocator(p=cmds.pointOnCurve(curve, pr=0.0, p=True), n=nameBuilder_locator + str(p))
            # joint
        cmds.spaceLocator(p=cmds.pointOnCurve(curve, pr=spacing * p, p=True), n=nameBuilder_locator + str(p))
        # joint


def pathMode(path):
    nameBuilder_locator = path + "_loc"
    nameBuilder_joint = path + "_jnt"
    locatorList = []
    for p in range(1, pointsNumber):
        if p == 1:
            locator = cmds.spaceLocator(n=nameBuilder_locator + str(p))
            motionPath = cmds.pathAnimation(locator[0], c=path, f=True)
            deleteConnection(motionPath + '.u')
            cmds.setAttr(motionPath + '.uValue', 0)
            locatorList.append(locator[0])
            # joint
        locator = cmds.spaceLocator(n=nameBuilder_locator + str(p))
        motionPath = cmds.pathAnimation(locator[0], c=path, f=True)
        deleteConnection(motionPath + '.u')
        cmds.setAttr(motionPath + '.uValue', spacing * p)
        locatorList.append(locator[0])
        # joint
        # -gruppa i locator
    return locatorList


locList = []
for cv in curve:
    print(cv)
    locList.extend(pathMode(cv))
cmds.group(locList, n='locator_grp')
## --ToDo

# gui
# object oriented
# multithreading

# docstring not working. why?

__author__ = 'Lorenzo Argentieri'

import pymel.core as pm

from mayaLib.rigLib.utils import common
from mayaLib.rigLib.utils import deform

import os
import json
import re
import functools

from maya import cmds as mc, OpenMaya as om


SHAPE_LIBRARY_PATH = "C:/PATH_TO_LIBRARY"
SHELF_NAME = "Custom"
ICON_PATH = "C:/PATH_TO_ICONS"


def validatePath(path=None):
    '''Checks if the file already exists and provides a dialog to overwrite or not'''
    if os.path.isfile(path):
        confirm = mc.confirmDialog(title='Overwrite file?',
                                   message='The file ' + path + ' already exists.Do you want to overwrite it?',
                                   button=['Yes', 'No'],
                                   defaultButton='Yes',
                                   cancelButton='No',
                                   dismissString='No')
        if confirm == "No":
            mc.warning("The file " + path + " was not saved")
            return 0
    return 1


def loadData(path=None):
    '''Loads raw JSON data from a file and returns it as a dict'''
    if os.path.isfile(path):
        f = open(path, "r")
        data = json.loads(f.read())
        f.close()
        return data
    else:
        mc.error("The file " + path + " doesn't exist")


def saveData(path=None, data=None):
    '''Saves a dictionary as JSON in a file'''
    if validatePath(path):
        f = open(path, "w")
        f.write(json.dumps(data, sort_keys=1, indent=4, separators=(",", ":")))
        f.close()
        return 1
    return 0


def getKnots(crvShape=None):
    mObj = om.MObject()
    sel = om.MSelectionList()
    sel.add(crvShape)
    sel.getDependNode(0, mObj)

    fnCurve = om.MFnNurbsCurve(mObj)
    tmpKnots = om.MDoubleArray()
    fnCurve.getKnots(tmpKnots)

    return [tmpKnots[i] for i in range(tmpKnots.length())]


def getShape(crv=None):
    '''Returns a dictionary containing all the necessery information for rebuilding the passed in crv.'''
    crvShapes = validateCurve(crv)

    crvShapeList = []

    for crvShape in crvShapes:
        crvShapeDict = {
            "points": [],
            "knots": [],
            "form": mc.getAttr(crvShape + ".form"),
            "degree": mc.getAttr(crvShape + ".degree"),
            "colour": mc.getAttr(crvShape + ".overrideColor")
        }
        points = []

        for i in range(mc.getAttr(crvShape + ".controlPoints", s=1)):
            points.append(mc.getAttr(crvShape + ".controlPoints[%i]" % i)[0])

        crvShapeDict["points"] = points
        crvShapeDict["knots"] = getKnots(crvShape)

        crvShapeList.append(crvShapeDict)

    return crvShapeList


def setShape(crv, crvShapeList):
    '''Creates a new shape on the crv transform, using the properties in the crvShapeDict.'''
    crvShapes = validateCurve(crv)

    oldColour = mc.getAttr(crvShapes[0] + ".overrideColor")
    mc.delete(crvShapes)

    for i, crvShapeDict in enumerate(crvShapeList):
        tmpCrv = mc.curve(p=crvShapeDict["points"], k=crvShapeDict["knots"], d=crvShapeDict["degree"], per=bool(crvShapeDict["form"]))
        newShape = mc.listRelatives(tmpCrv, s=1)[0]
        mc.parent(newShape, crv, r=1, s=1)

        mc.delete(tmpCrv)
        newShape = mc.rename(newShape, crv + "Shape" + str(i + 1).zfill(2))

        mc.setAttr(newShape + ".overrideEnabled", 1)

        if "colour" in crvShapeDict.keys():
            setColour(newShape, crvShapeDict["colour"])
        else:
            setColour(newShape, oldColour)


def validateCurve(crv=None):
    '''Checks whether the transform we are working with is actually a curve and returns it's shapes'''
    if mc.nodeType(crv) == "transform" and mc.nodeType(mc.listRelatives(crv, c=1, s=1)[0]) == "nurbsCurve":
        crvShapes = mc.listRelatives(crv, c=1, s=1)
    elif mc.nodeType(crv) == "nurbsCurve":
        crvShapes = mc.listRelatives(mc.listRelatives(crv, p=1)[0], c=1, s=1)
    else:
        mc.error("The object " + crv + " passed to validateCurve() is not a curve")
    return crvShapes


def loadFromLib(shape=None):
    '''Loads the shape data from the shape file in the SHAPE_LIBRARY_PATH directory'''
    path = os.path.join(SHAPE_LIBRARY_PATH, shape + ".json")
    data = loadData(path)
    return data


def saveToLib(crv=None, shapeName=None):
    '''Saves the shape data to a shape file in the SHAPE_LIBRARY_PATH directory'''
    crvShape = getShape(crv=crv)
    path = os.path.join(SHAPE_LIBRARY_PATH, re.sub("\s", "", shapeName) + ".json")
    for shapeDict in crvShape:
        shapeDict.pop("colour", None)
    saveData(path, crvShape)


def setColour(crv, colour):
    '''Sets the overrideColor of a curve'''
    if mc.nodeType(crv) == "transform":
        crvShapes = mc.listRelatives(crv)
    else:
        crvShapes = [crv]
    for crv in crvShapes:
        mc.setAttr(crv + ".overrideColor", colour)


def getColour(crv):
    '''Returns the overrideColor of a curve'''
    if mc.nodeType(crv) == "transform":
        crv = mc.listRelatives(crv)[0]
    return mc.getAttr(crv + ".overrideColor")


def getAvailableControlShapes():
    '''Returns a list of the available control shapes in the specified library. Each element
    of the list is a tuple containing the label (name) of the controlShape and a reference
    to the command to assign that shape via functools.partial'''
    lib = SHAPE_LIBRARY_PATH
    return [(x.split(".")[0], functools.partial(assignControlShape, x.split(".")[0])) for x in os.listdir(lib)]


def getAvailableColours():
    '''Returns a list of the available 32 colours for overrideColor in maya. Each element
    of the list is a tuple containig the label, reference to the command which assigns the
    colour and the name of an image to be used as an icon'''
    return [("index" + str(i).zfill(2), functools.partial(assignColour, i), "shapeColour" + str(i).zfill(2) + ".png") for i in range(32)]


def assignColour(*args):
    '''Assigns args[0] as the overrideColor of the selected curves'''
    for each in mc.ls(sl=1, fl=1):
        setColour(each, args[0])


def assignControlShape(*args):
    '''Assigns args[0] as the shape of the selected curves'''
    sel = mc.ls(sl=1, fl=1)
    for each in sel:
        setShape(each, loadFromLib(args[0]))
    mc.select(sel)


def saveCtlShapeToLib(*args):
    '''Saves the selected shape in the defined control shape library'''
    result = mc.promptDialog(title="Save Control Shape to Library",
                             m="Control Shape Name",
                             button=["Save", "Cancel"],
                             cancelButton="Cancel",
                             dismissString="Cancel")
    if result == "Save":
        name = mc.promptDialog(q=1, t=1)
        saveToLib(mc.ls(sl=1, fl=1)[0], name)
    rebuildUI()


def mirrorCtlShapes_OLD(*args):
    '''Mirrors the selected control's shape to the other control on the other side'''
    sel = mc.ls(sl=1, fl=1)
    for ctl in sel:
        if ctl[0] not in ["L", "R"]:
            continue
        search = "R_"
        replace = "L_"
        if ctl[0] == "L":
            search = "L_"
            replace = "R_"
        shapes = getShape(ctl)
        for shape in shapes:
            shape.pop("colour")
        setShape(ctl.replace(search, replace), shapes)
        _flipCtlShape(ctl.replace(search, replace))
    mc.select(sel)


def mirrorCtlShapes(ctrl, mode='x'):
    sides = ['_L', '_R']
    for s in sides:
        if s in ctrl:
            side = s
            other_side = ''
            if side == '_L':
                other_side = '_R'
            else:
                other_side = '_L'

        ctrl = pm.ls(ctrl)[-1]
        shape_list = ctrl.getShapes()
        for shape in shape_list:
            for cv in shape.cv[:]:
                pos = pm.xform(cv, q=1, ws=1, t=1)
                cv_dest = pm.ls(str(cv.name()).replace(side, other_side))[-1]
                if pm.objExists(cv_dest):
                    if mode == 'x': pm.xform(cv_dest, ws=1, t=[pos[0] * (-1), pos[1], pos[2]])
                    if mode == 'z': pm.xform(cv_dest, ws=1, t=[pos[0], pos[1], pos[2] * (-1)])


def copyCtlShape(*args):
    '''Copies the selected control's shape to a global variable for pasting'''
    global ctlShapeClipboard
    ctlShapeClipboard = getShape(mc.ls(sl=1, fl=1)[0])
    for ctlShape in ctlShapeClipboard:
        ctlShape.pop("colour")


def pasteCtlShape(*args):
    '''Assigns the control shape from the ctlShapeClipboard global variable
    to the selected controls'''
    sel = mc.ls(sl=1, fl=1)
    for each in sel:
        setShape(each, ctlShapeClipboard)
    mc.select(sel)


def flipCtlShape(*args):
    '''Flips the selected control shapes to the other side in all axis'''
    sel = mc.ls(sl=1, fl=1)
    for each in sel:
        _flipCtlShape(each)
    mc.select(sel)


def flipCtlShapeX(*args):
    '''Flips the selected control shapes to the other side in X'''
    sel = mc.ls(sl=1, fl=1)
    for each in sel:
        _flipCtlShape(each, [-1, 1, 1])
    mc.select(sel)


def flipCtlShapeY(*args):
    '''Flips the selected control shapes to the other side in Y'''
    sel = mc.ls(sl=1, fl=1)
    for each in sel:
        _flipCtlShape(each, [1, -1, 1])
    mc.select(sel)


def flipCtlShapeZ(*args):
    '''Flips the selected control shapes to the other side in Z'''
    sel = mc.ls(sl=1, fl=1)
    for each in sel:
        _flipCtlShape(each, [1, 1, -1])
    mc.select(sel)


def _flipCtlShape(crv=None, axis=[-1, -1, -1]):
    '''Scales the points of the crv argument by the axis argument. This function is not meant to be
    called directly. Look at the flipCtlShape instead.'''
    shapes = getShape(crv)
    newShapes = []
    for shape in shapes:
        for i, each in enumerate(shape["points"]):
            shape["points"][i] = [each[0] * axis[0], each[1] * axis[1], each[2] * axis[2]]
        newShapes.append(shape)
    setShape(crv, newShapes)
    mc.select(crv)


def rebuildUI(*args):
    '''Rebuilds the UI defined in managerUI.py'''
    mc.evalDeferred("""
import controlShapeManager
reload(controlShapeManager)
""")

################################# OLD #################################
def copyShape(source, destination, mode=''):
    """
    Copy Shape from source to destination transform
    :param source: obj
    :param destination: obj
    :return:
    """
    if mode == 'blendShape':
        blendshapeNode = pm.blendShape([source], destination, frontOfChain=True, weight=(0, 1))
        pm.delete(blendshapeNode, ch=True)
    else:
        sourceShapes = pm.ls(source)[0].getShapes()
        destinationShapes = pm.ls(destination)[0].getShapes()
        pm.delete(destinationShapes)

        pm.parent(sourceShapes, destination, r=True, s=True)
        pm.delete(source)


def extractCtrlShape():
    controlShapeGrp = pm.group(n='controlShapes_GRP', em=True)
    ctrlList = pm.ls('*_CTRL')
    for ctrl in ctrlList:
        ctrlShape = pm.duplicate(ctrl, rr=True)[0]
        deleteList = pm.listRelatives(ctrlShape, c=True, type='transform')
        pm.delete(deleteList)
        pm.parent(ctrlShape, controlShapeGrp)
        newName = str(ctrlShape.name()).replace('_CTRL1', '_CTRL')
        pm.rename(ctrlShape, newName)


class CtrlShape():
    shapes = {
        'circle': 'CircleX',
        'circleX': 'CircleX',
        'circleY': 'CircleY',
        'circleZ': 'CircleZ',
        'sphere': 'Sphere',
        'move': 'Move',
        'trapezium': 'Trapezium',
        'chest': 'Chest',
        'hip': 'Hip',
        'head': 'Head',
        'display': 'Display',
        'ikfk': 'IKFK'
    }

    def __init__(self, name, scale, shape='circle', normalDirection=[0, 0, 0]):
        pass

        if shape in ['circle', 'circleX']:
            circleNormal = [1, 0, 0]
            ctrlObject = circleCtrlShape(name, normalDirection=circleNormal, scale=scale)

        elif shape == 'circleY':
            circleNormal = [0, 1, 0]
            ctrlObject = circleCtrlShape(name, normalDirection=circleNormal, scale=scale)

        elif shape == 'circleZ':
            circleNormal = [0, 0, 1]
            ctrlObject = circleCtrlShape(name, normalDirection=circleNormal, scale=scale)

        elif shape == 'sphere':
            ctrlObject = sphereCtrlShape(name=name, scale=scale)

        elif shape == 'move':
            ctrlObject = moveCtrlShape(name=name, scale=scale)

        elif shape == 'spine':
            ctrlObject = trapeziumCtrlShape(name=name, scale=scale)
            ctrlObject.translateY.set(3 * scale)
            common.freezeTranform(ctrlObject)

        elif shape == 'chest':
            ctrlObject = chestCtrlShape(name=name, scale=scale)

        elif shape == 'hip':
            ctrlObject = hipCtrlShape(name=name, scale=scale)

        elif shape == 'head':
            ctrlObject = headCtrlShape(name=name, scale=scale)

        elif shape == 'display':
            ctrlObject = displayCtrlShape(name=name, scale=scale)

        elif shape == 'ikfk':
            ctrlObject = ikfkCtrlShape(name=name, scale=scale)

        ctrl = ''
        self.transformCtrl(ctrl, normalDirection=normalDirection, scale=scale)

    def transformCtrl(self, ctrl, normalDirection=[0, 0, 0], scale=1):
        if normalDirection[0] == 1:
            pm.rotate(ctrl, [90, 0, 0])
        elif normalDirection[0] == -1:
            pm.rotate(ctrl, [-90, 0, 0])

        if normalDirection[1] == 1:
            pm.rotate(ctrl, [0, 90, 0])
        elif normalDirection[1] == -1:
            pm.rotate(ctrl, [0, -90, 0])

        if normalDirection[2] == 1:
            pm.rotate(ctrl, [0, 0, 90])
        elif normalDirection[2] == -1:
            pm.rotate(ctrl, [0, 0, -90])

        ctrlGrp = pm.group(ctrl, name=ctrl.getName() + 'CtrlScale_TEMP_GRP')
        ctrlGrp.scale.set(scale, scale, scale)
        common.freezeTranform(ctrlGrp)
        pm.parent(ctrl, w=True)
        pm.delete(ctrlGrp)

        return ctrl


def circleCtrlShape(name, normalDirection=[1, 0, 0], scale=1):
    ctrlObject = pm.circle(n=name, ch=False, normal=normalDirection, radius=scale)[0]

    return ctrlObject


def sphereCtrlShape(name, scale=1):
    ctrlObject = pm.circle(n=name, ch=False, normal=[1, 0, 0], radius=scale)[0]
    addShape = pm.circle(n=name, ch=False, normal=[0, 0, 1], radius=scale)[0]
    pm.parent(pm.listRelatives(addShape, s=1), ctrlObject, r=1, s=1)
    pm.delete(addShape)

    common.deleteHistory(ctrlObject)
    common.freezeTranform(ctrlObject)
    return ctrlObject


def moveCtrlShape(name, scale):
    cv = pm.curve(n=name, d=1,
                  p=[(1, 0, -3), (2, 0, -3), (0, 0, -5), (-2, 0, -3), (-1, 0, -3), (-1, 0, -2), (-1, 0.5, -1.5),
                     (-1.35, 0.5, -1.35), (-1.5, 0.5, -1), (-2, 0, -1), (-3, 0, -1), (-3, 0, -2), (-5, 0, 0),
                     (-3, 0, 2), (-3, 0, 1), (-2, 0, 1), (-1.5, 0.5, 1), (-1.35, 0.5, 1.35), (-1, 0.5, 1.5), (-1, 0, 2),
                     (-1, 0, 3), (-2, 0, 3), (0, 0, 5), (2, 0, 3), (1, 0, 3), (1, 0, 2), (1, 0.5, 1.5),
                     (1.35, 0.5, 1.35), (1.5, 0.5, 1), (2, 0, 1), (3, 0, 1), (3, 0, 2), (5, 0, 0), (3, 0, -2),
                     (3, 0, -1), (2, 0, -1), (1.5, 0.5, -1), (1.35, 0.5, -1.35), (1, 0.5, -1.5), (1, 0, -2),
                     (1, 0, -3)],
                  k=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26,
                     27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40])
    scale = scale * 0.1666666667
    cv.scale.set(scale, scale, scale)
    common.freezeTranform(cv)
    return cv


def trapeziumCtrlShape(name, normalDirection=[0, 0, 0], scale=1):
    pm.mel.eval('softSelect -sse off;')

    bottomSquare = pm.nurbsSquare(c=[0, 0, 0], nr=[0, 1, 0], d=1, ch=False)
    topSquare = pm.nurbsSquare(c=[0, 1, 0], nr=[0, 1, 0], d=1, ch=False)

    leftSquare = pm.nurbsSquare(c=[-0.5, 0.5, 0], nr=[1, 0, 0], d=1, ch=False)
    rightSquare = pm.nurbsSquare(c=[0.5, 0.5, 0], nr=[1, 0, 0], d=1, ch=False)

    squareList = [bottomSquare, topSquare, leftSquare, rightSquare]

    for square in squareList:
        segmentList = pm.listRelatives(square, ad=1, type='transform')
        pm.attachCurve(segmentList[0], segmentList[1], ch=False, rpo=True, kmk=False, m=0, bb=0, bki=False, p=0.1)
        pm.attachCurve(segmentList[2], segmentList[3], ch=False, rpo=True, kmk=False, m=0, bb=0, bki=False, p=0.1)
        pm.attachCurve(segmentList[0], segmentList[2], ch=False, rpo=True, kmk=False, m=0, bb=0, bki=False, p=0.1)

        pm.delete(segmentList[1:])

    cubePartsShape = [pm.listRelatives(square, ad=1, type='transform')[0].getShape() for square in squareList]
    for shape in cubePartsShape:
        pm.parent(shape, cubePartsShape[0].getParent(), r=1, s=1)

    # scale upper Box
    ctrl = pm.listRelatives(bottomSquare, ad=1, type='transform')[0]
    pm.parent(ctrl, w=True)
    pm.delete(squareList)
    ctrlShapesList = ctrl.getShapes()
    for shape in ctrlShapesList:
        pm.rebuildCurve(shape, ch=False, rpo=True, rt=1, end=1, kr=0, kcp=False, kep=True, kt=False, s=0, d=1, tol=0.01)
    vertSelection = pm.select(ctrlShapesList[3].cv[0:1], ctrlShapesList[1].cv[0:3], ctrlShapesList[2].cv[0:1])
    pm.scale(vertSelection, [0.5, 0.5, 0.5], r=True)
    allVertSelection = pm.select([shape.cv[:] for shape in ctrlShapesList])
    pm.scale(allVertSelection, [4, 1, 1], r=True)
    pm.select(cl=True)

    if normalDirection[0] == 1:
        pm.rotate(ctrl, [90, 0, 0])
    elif normalDirection[0] == -1:
        pm.rotate(ctrl, [-90, 0, 0])

    if normalDirection[1] == 1:
        pm.rotate(ctrl, [0, 90, 0])
    elif normalDirection[1] == -1:
        pm.rotate(ctrl, [0, -90, 0])

    if normalDirection[2] == 1:
        pm.rotate(ctrl, [0, 0, 90])
    elif normalDirection[2] == -1:
        pm.rotate(ctrl, [0, 0, -90])

    pm.rename(ctrl, name)
    ctrl.scale.set(scale, scale, scale)
    common.freezeTranform(ctrl)

    return ctrl


def chestCtrlShape(name, normalDirection=[1, 1, 0], scale=1):
    ctrl = pm.circle(n=name, s=10, nr=[0, 0, 1])[0]

    pm.move(0, 0, 1, ctrl.cv[3:4], ctrl.cv[8:9], r=True, os=True)
    pm.scale([ctrl.cv[3:4], ctrl.cv[8:9]], [1, 3, 1], r=True, p=[0, 0, 1])
    pm.scale([ctrl.cv[0], ctrl.cv[2], ctrl.cv[5], ctrl.cv[7]], [1.75, 1.35, 1], r=True, p=[0, 0, 0])
    pm.move(0, 0, -0.75, ctrl.cv[0], ctrl.cv[2], ctrl.cv[5], ctrl.cv[7], r=True, os=True)
    pm.move(0, 0, -1, ctrl.cv[1], ctrl.cv[6], r=True, os=True)
    pm.move(0, -0.75, 0, ctrl.cv[1], r=True, os=True)
    pm.move(0, 0.25, 0, ctrl.cv[0], ctrl.cv[2], r=True, os=True)
    # pm.xform(ctrl, ws=True, pivots=[0, 0, -0.35])

    if normalDirection[0] == 1:
        pm.rotate(ctrl.cv[:], [90, 0, 0])
    elif normalDirection[0] == -1:
        pm.rotate(ctrl.cv[:], [-90, 0, 0])

    if normalDirection[1] == 1:
        pm.rotate(ctrl.cv[:], [0, 90, 0])
    elif normalDirection[1] == -1:
        pm.rotate(ctrl.cv[:], [0, -90, 0])

    if normalDirection[2] == 1:
        pm.rotate(ctrl.cv[:], [0, 0, 90])
    elif normalDirection[2] == -1:
        pm.rotate(ctrl.cv[:], [0, 0, -90])

    ctrl.scale.set(scale, scale, scale)
    common.deleteHistory(ctrl)
    common.freezeTranform(ctrl)

    return ctrl


def hipCtrlShape(name, normalDirection=[0, -1, 1], scale=1):
    ctrl = pm.circle(n=name, s=10, nr=[0, 0, 1])[0]

    pm.move(0, 0, 1, ctrl.cv[3:4], ctrl.cv[8:9], r=True, os=True)
    pm.scale([ctrl.cv[3:4], ctrl.cv[8:9]], [1, 3, 1], r=True, p=[0, 0, 1])
    pm.scale([ctrl.cv[0], ctrl.cv[2], ctrl.cv[5], ctrl.cv[7]], [1.75, 1.35, 1], r=True, p=[0, 0, 0])
    pm.move(0, 0, -0.75, ctrl.cv[0], ctrl.cv[2], ctrl.cv[5], ctrl.cv[7], r=True, os=True)
    pm.move(0, 0, -1, ctrl.cv[1], ctrl.cv[6], r=True, os=True)
    pm.scale(ctrl.cv[:], [1, 0.5, 1], r=True, p=[0, 0, 0])
    # pm.xform(ctrl, ws=True, pivots=[0, 0, -0.15])

    if normalDirection[0] == 1:
        pm.rotate(ctrl.cv[:], [90, 0, 0])
    elif normalDirection[0] == -1:
        pm.rotate(ctrl.cv[:], [-90, 0, 0])

    if normalDirection[1] == 1:
        pm.rotate(ctrl.cv[:], [0, 90, 0])
    elif normalDirection[1] == -1:
        pm.rotate(ctrl.cv[:], [0, -90, 0])

    if normalDirection[2] == 1:
        pm.rotate(ctrl.cv[:], [0, 0, 90])
    elif normalDirection[2] == -1:
        pm.rotate(ctrl.cv[:], [0, 0, -90])

    ctrl.scale.set(scale, scale, scale)
    common.deleteHistory(ctrl)
    common.freezeTranform(ctrl)

    return ctrl


def headCtrlShape(name, normalDirection=[0, -1, 1], scale=1):
    return hipCtrlShape(name, normalDirection, scale)


def displayCtrlShape(name='display', normalDirection=[0, 1, 0], scale=1):
    ctrl = pm.circle(n=name, s=10, nr=[0, 0, 1])[0]
    pm.delete(ctrl.getShape())

    # create text and snap to displayCtrl group
    textGrp = pm.textCurves(t='Display', n=name)[0]
    common.centerPivot(textGrp)
    common.freezeTranform(textGrp)

    # parent al text shape under displayCTrl
    shapeList = pm.ls(textGrp, dag=True, leaf=True, type='nurbsCurve')
    pm.parent(shapeList, ctrl, r=1, s=1)
    pm.delete(textGrp)
    common.centerPivot(ctrl)

    # rotate shape
    for shape in shapeList:
        if normalDirection[0] == 1:
            pm.rotate(shape.cv[:], [90, 0, 0])
        elif normalDirection[0] == -1:
            pm.rotate(shape.cv[:], [-90, 0, 0])

        if normalDirection[1] == 1:
            pm.rotate(shape.cv[:], [0, 90, 0])
        elif normalDirection[1] == -1:
            pm.rotate(shape.cv[:], [0, -90, 0])

        if normalDirection[2] == 1:
            pm.rotate(shape.cv[:], [0, 0, 90])
        elif normalDirection[2] == -1:
            pm.rotate(shape.cv[:], [0, 0, -90])

    pm.scale(ctrl, [scale, scale, scale], r=True)
    common.centerPivot(ctrl)
    common.freezeTranform(ctrl)

    return ctrl


def ikfkCtrlShape(name='ikfk', normalDirection=[0, 1, 0], scale=1):
    ctrl = pm.circle(n=name, s=10, nr=[0, 0, 1])[0]
    pm.delete(ctrl.getShape())

    # create text and snap to displayCtrl group
    textGrp = pm.textCurves(t='IKFK', n=name)[0]
    common.centerPivot(textGrp)
    common.freezeTranform(textGrp)

    # parent al text shape under displayCTrl
    shapeList = pm.ls(textGrp, dag=True, leaf=True, type='nurbsCurve')
    pm.parent(shapeList, ctrl, r=1, s=1)
    pm.delete(textGrp)
    common.centerPivot(ctrl)

    # rotate shape
    for shape in shapeList:
        if normalDirection[0] == 1:
            pm.rotate(shape.cv[:], [90, 0, 0])
        elif normalDirection[0] == -1:
            pm.rotate(shape.cv[:], [-90, 0, 0])

        if normalDirection[1] == 1:
            pm.rotate(shape.cv[:], [0, 90, 0])
        elif normalDirection[1] == -1:
            pm.rotate(shape.cv[:], [0, -90, 0])

        if normalDirection[2] == 1:
            pm.rotate(shape.cv[:], [0, 0, 90])
        elif normalDirection[2] == -1:
            pm.rotate(shape.cv[:], [0, 0, -90])

    pm.scale(ctrl, [scale, scale, scale], r=True)
    common.centerPivot(ctrl)
    common.freezeTranform(ctrl)

    return ctrl


def controlShapeAdaptive(controlList, geoList, ctrlSmooth=6, scaleConstant=1.5, rebuildCV=32):
    adaptiveShapeBuildGrp = pm.group(n='daptiveShapeBuild_GRP', em=True)
    geoList = pm.ls(geoList)
    dupliGeo = pm.duplicate(geoList)
    geoCombined = pm.polyUnite(dupliGeo, ch=False, name='tmpAdaptiveRef_GEO')[0]
    pm.parent(geoCombined, adaptiveShapeBuildGrp)

    ctrlList = pm.ls(controlList)
    for ctrl in ctrlList:
        ctrlShapeBuildGrp = pm.group(n=ctrl.name() + '_GRP', em=True, p=adaptiveShapeBuildGrp)

        dupliCtrl = pm.duplicate(ctrl, n='tmpCtrl')[0]
        pm.delete(pm.ls(dupliCtrl, dagObjects=True, exactType='transform')[1:])
        pm.rebuildCurve(dupliCtrl, ch=False, s=rebuildCV)
        pm.parent(dupliCtrl, ctrlShapeBuildGrp)

        # extrusion
        extrudeCircle = pm.circle(r=0.1, ch=0)[0]
        pm.parent(extrudeCircle, ctrlShapeBuildGrp)
        motionPathNode = \
            pm.ls(pm.pathAnimation(extrudeCircle, curve=dupliCtrl, fractionMode=True, follow=True, followAxis='z',
                                   upAxis='y', worldUpType='vector', worldUpVector=[0, 1, 0], inverseUp=False,
                                   inverseFront=False, bank=False))[0]

        pm.disconnectAttr(extrudeCircle.tx)
        pm.disconnectAttr(extrudeCircle.ty)
        pm.disconnectAttr(extrudeCircle.tz)
        pm.disconnectAttr(extrudeCircle.rx)
        pm.disconnectAttr(extrudeCircle.ry)
        pm.disconnectAttr(extrudeCircle.rz)
        pm.disconnectAttr(motionPathNode.u)
        pm.delete(motionPathNode)

        extrudedSurface = \
            pm.extrude(extrudeCircle, dupliCtrl, ch=False, rn=False, po=0, et=2, ucp=0, fpt=1, upn=0, rotation=0,
                       scale=1,
                       rsp=1)[0]
        pm.parent(extrudedSurface, ctrlShapeBuildGrp)
        nurbsToPoly = pm.nurbsToPoly(extrudedSurface, ch=False, polygonType=1, chr=0.9)
        pm.parent(nurbsToPoly, ctrlShapeBuildGrp)

        # add deformer
        wrapNode = deform.wrapDeformer(dupliCtrl, nurbsToPoly)
        shrinkWrapNode = deform.shrinkWrapDeformer(nurbsToPoly, geoCombined)

        shrinkWrapNode.projection.set(4)
        shrinkWrapNode.targetSmoothLevel.set(ctrlSmooth)

        # delete history
        common.deleteHistory(nurbsToPoly)
        common.deleteHistory(dupliCtrl)
        pm.scale(dupliCtrl.cv[:], [scaleConstant, scaleConstant, scaleConstant])

        copyShape(dupliCtrl, ctrl)

    pm.delete(adaptiveShapeBuildGrp)


if __name__ == "__main__":

    # Building the UI
    if SHELF_NAME and mc.shelfLayout(SHELF_NAME, ex=1):
        children = mc.shelfLayout(SHELF_NAME, q=1, ca=1) or []
        for each in children:
            try:
                label = mc.shelfButton(each, q=1, l=1)
            except:
                continue
            if label == "ctlShapeManager":
                mc.deleteUI(each)

        mc.setParent(SHELF_NAME)
        mc.shelfButton(l="ctlShapeManager", i="commandButton.png", width=37, height=37, iol="CTL")
        popup = mc.popupMenu(b=1)
        mc.menuItem(p=popup, l="Save to library", c=saveCtlShapeToLib)

        sub = mc.menuItem(p=popup, l="Assign from library", subMenu=1)

        for each in getAvailableControlShapes():
            mc.menuItem(p=sub, l=each[0], c=each[1])

        mc.menuItem(p=popup, l="Copy", c=copyCtlShape)
        mc.menuItem(p=popup, l="Paste", c=pasteCtlShape)

        sub = mc.menuItem(p=popup, l="Set colour", subMenu=1)

        for each in getAvailableColours():
            mc.menuItem(p=sub, l=each[0], c=each[1], i=ICON_PATH + each[2])

        mc.menuItem(p=popup, l="Flip", c=flipCtlShape)
        mc.menuItem(p=popup, l="Mirror", c=mirrorCtlShapes)

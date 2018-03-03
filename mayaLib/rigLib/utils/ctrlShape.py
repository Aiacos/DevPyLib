__author__ = 'Lorenzo Argentieri'

import pymel.core as pm
from mayaLib.rigLib.utils import common


def copyShape(source, destination):
    """
    Copy Shape from source to destination transform
    :param source: obj
    :param destination: obj
    :return:
    """
    sourceShapes = pm.ls(source)[0].getShapes()
    destinationShapes = pm.ls(destination)[0].getShapes()
    pm.delete(destinationShapes)
    pm.parent(sourceShapes, destination, r=True, s=True)
    pm.delete(source)

def sphereCtrlShape(name, scale=1):
    ctrlObject = pm.circle(n=name, ch=False, normal=[1, 0, 0], radius=scale)[0]
    addShape = pm.circle(n=name, ch=False, normal=[0, 0, 1], radius=scale)[0]
    pm.parent(pm.listRelatives(addShape, s=1), ctrlObject, r=1, s=1)
    pm.delete(addShape)

    common.deleteHistory(ctrlObject)
    common.freezeTranform(ctrlObject)
    return ctrlObject

def moveCtrlShape(name, scale):
    cv = pm.curve(n=name, d=1, p=[(1, 0, -3), (2, 0, -3), (0, 0, -5), (-2, 0, -3), (-1, 0, -3), (-1, 0, -2), (-1, 0.5, -1.5), (-1.35, 0.5, -1.35), (-1.5, 0.5, -1), (-2, 0, -1), (-3, 0, -1), (-3, 0, -2), (-5, 0, 0), (-3, 0, 2), (-3, 0, 1), (-2, 0, 1), (-1.5, 0.5, 1), (-1.35, 0.5, 1.35), (-1, 0.5, 1.5), (-1, 0, 2), (-1, 0, 3), (-2, 0, 3), (0, 0, 5), (2, 0, 3), (1, 0, 3), (1, 0, 2), (1, 0.5, 1.5), (1.35, 0.5, 1.35), (1.5, 0.5, 1), (2, 0, 1), (3, 0, 1), (3, 0, 2), (5, 0, 0), (3, 0, -2), (3, 0, -1), (2, 0, -1), (1.5, 0.5, -1), (1.35, 0.5, -1.35), (1, 0.5, -1.5), (1, 0, -2), (1, 0, -3)], k=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40])
    scale = scale * 0.1666666667
    cv.scale.set(scale, scale, scale)
    common.freezeTranform(cv)
    return cv

def trapeziumCtrlShape(name, normalDirection=[0,1,0], scale=1):
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

def chestCtrlShape(name, normalDirection=[1,0,0], scale=1):
    ctrl = pm.circle(n=name, s=10, nr=[0, 0, 1])[0]

    pm.move(0, 0, 1, ctrl.cv[3:4], ctrl.cv[8:9], r=True, os=True)
    pm.scale([ctrl.cv[3:4], ctrl.cv[8:9]], [1, 3, 1], r=True, p=[0, 0, 1])
    pm.scale([ctrl.cv[0], ctrl.cv[2], ctrl.cv[5], ctrl.cv[7]], [1.75, 1.35, 1], r=True, p=[0, 0, 0])
    pm.move(0, 0, -0.75, ctrl.cv[0], ctrl.cv[2], ctrl.cv[5], ctrl.cv[7], r=True, os=True)
    pm.move(0, 0, -1, ctrl.cv[1], ctrl.cv[6], r=True, os=True)
    pm.move(0, -0.75, 0, ctrl.cv[1], r=True, os=True)
    pm.move(0, 0.25, 0, ctrl.cv[0], ctrl.cv[2], r=True, os=True)
    #pm.xform(ctrl, ws=True, pivots=[0, 0, -0.35])

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

def hipCtrlShape(name, normalDirection=[1,0,0], scale=1):
    ctrl = pm.circle(n=name, s=10, nr=[0, 0, 1])[0]

    pm.move(0, 0, 1, ctrl.cv[3:4], ctrl.cv[8:9], r=True, os=True)
    pm.scale([ctrl.cv[3:4], ctrl.cv[8:9]], [1, 3, 1], r=True, p=[0, 0, 1])
    pm.scale([ctrl.cv[0], ctrl.cv[2], ctrl.cv[5], ctrl.cv[7]], [1.75, 1.35, 1], r=True, p=[0, 0, 0])
    pm.move(0, 0, -0.75, ctrl.cv[0], ctrl.cv[2], ctrl.cv[5], ctrl.cv[7], r=True, os=True)
    pm.move(0, 0, -1, ctrl.cv[1], ctrl.cv[6], r=True, os=True)
    pm.scale(ctrl.cv[:], [1, 0.5, 1], r=True, p=[0, 0, 0])
    #pm.xform(ctrl, ws=True, pivots=[0, 0, -0.15])

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

def headCtrlShape(name, normalDirection=[1,0,0], scale=1):
    return hipCtrlShape(name, normalDirection, scale)

def displayCtrlShape(name, normalDirection=[1,0,0], scale=1):
    pass

def ikfkCtrlShape(name, normalDirection=[1,0,0], scale=1):
    pass

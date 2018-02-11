__author__ = 'Lorenzo Argentieri'

import pymel.core as pm
from mayaLib.rigLib.utils import common

def moveCtrlShape(name, scale):
    cv = pm.curve(n=name, d=1, p=[(1, 0, -3), (2, 0, -3), (0, 0, -5), (-2, 0, -3), (-1, 0, -3), (-1, 0, -2), (-1, 0.5, -1.5), (-1.35, 0.5, -1.35), (-1.5, 0.5, -1), (-2, 0, -1), (-3, 0, -1), (-3, 0, -2), (-5, 0, 0), (-3, 0, 2), (-3, 0, 1), (-2, 0, 1), (-1.5, 0.5, 1), (-1.35, 0.5, 1.35), (-1, 0.5, 1.5), (-1, 0, 2), (-1, 0, 3), (-2, 0, 3), (0, 0, 5), (2, 0, 3), (1, 0, 3), (1, 0, 2), (1, 0.5, 1.5), (1.35, 0.5, 1.35), (1.5, 0.5, 1), (2, 0, 1), (3, 0, 1), (3, 0, 2), (5, 0, 0), (3, 0, -2), (3, 0, -1), (2, 0, -1), (1.5, 0.5, -1), (1.35, 0.5, -1.35), (1, 0.5, -1.5), (1, 0, -2), (1, 0, -3)], k=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40])
    scale = scale * 0.1666666667
    cv.scale.set(scale, scale, scale)
    common.freezeTranform(cv)
    return cv

def trapeziumCtrlShape(name, scale=1):
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

    pm.rename(ctrl, name)
    ctrl.scale.set(scale, scale, scale)
    common.freezeTranform(ctrl)

    return ctrl

__author__ = 'Lorenzo Argentieri'

import pymel.core as pm
from mayaLib.rigLib.utils import common
from mayaLib.rigLib.utils import deform


def copyShape(source, destination, mode=''):
    """
    Copy Shape from source to destination transform
    :param source: obj
    :param destination: obj
    :return:
    """
    if mode == 'blendShape':
        blendshapeNode = pm.blendShape([source], destination, frontOfChain=True, weight=(0,1))
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

    def __init__(self, name, scale, shape='circle', normalDirection=[0,0,0]):
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

    def transformCtrl(self, ctrl, normalDirection=[0,0,0], scale=1):
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

        ctrlGrp = pm.group(ctrl, name=ctrl.getName()+'CtrlScale_TEMP_GRP')
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
    cv = pm.curve(n=name, d=1, p=[(1, 0, -3), (2, 0, -3), (0, 0, -5), (-2, 0, -3), (-1, 0, -3), (-1, 0, -2), (-1, 0.5, -1.5), (-1.35, 0.5, -1.35), (-1.5, 0.5, -1), (-2, 0, -1), (-3, 0, -1), (-3, 0, -2), (-5, 0, 0), (-3, 0, 2), (-3, 0, 1), (-2, 0, 1), (-1.5, 0.5, 1), (-1.35, 0.5, 1.35), (-1, 0.5, 1.5), (-1, 0, 2), (-1, 0, 3), (-2, 0, 3), (0, 0, 5), (2, 0, 3), (1, 0, 3), (1, 0, 2), (1, 0.5, 1.5), (1.35, 0.5, 1.35), (1.5, 0.5, 1), (2, 0, 1), (3, 0, 1), (3, 0, 2), (5, 0, 0), (3, 0, -2), (3, 0, -1), (2, 0, -1), (1.5, 0.5, -1), (1.35, 0.5, -1.35), (1, 0.5, -1.5), (1, 0, -2), (1, 0, -3)], k=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40])
    scale = scale * 0.1666666667
    cv.scale.set(scale, scale, scale)
    common.freezeTranform(cv)
    return cv

def trapeziumCtrlShape(name, normalDirection=[0,0,0], scale=1):
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

def chestCtrlShape(name, normalDirection=[1,1,0], scale=1):
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

def hipCtrlShape(name, normalDirection=[0,-1,1], scale=1):
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

def headCtrlShape(name, normalDirection=[0,-1,1], scale=1):
    return hipCtrlShape(name, normalDirection, scale)

def displayCtrlShape(name='display', normalDirection=[0,1,0], scale=1):
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

def ikfkCtrlShape(name='ikfk', normalDirection=[0,1,0], scale=1):
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
        pm.extrude(extrudeCircle, dupliCtrl, ch=False, rn=False, po=0, et=2, ucp=0, fpt=1, upn=0, rotation=0, scale=1,
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

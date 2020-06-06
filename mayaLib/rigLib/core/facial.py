__author__ = 'Lorenzo Argentieri'

import pymel.core as pm
from maya import mel

from mayaLib.rigLib.utils import name


def createFollicle(geo, u, v, prefix):
    follicleShape = pm.createNode('follicle', n=prefix+'_FLCShape')
    geoShape = geo.getShape()
    follicle = follicleShape.getParent()
    follicle.rename(prefix + '_FLC')

    pm.connectAttr(geoShape.outMesh, follicleShape.inputMesh)
    pm.connectAttr(geoShape.worldMatrix, follicleShape.inputWorldMatrix)

    pm.connectAttr(follicleShape.outRotate, follicle.rotate)
    pm.connectAttr(follicleShape.outTranslate, follicle.translate)

    follicleShape.parameterU.set(u)
    follicleShape.parameterV.set(v)

    return follicle

def findClosestUVCoordinate(geo, obj):
    closestPointOnMesh = pm.createNode("closestPointOnMesh")
    geoShape = geo.getShape()
    pm.connectAttr(geoShape.worldMesh, closestPointOnMesh.inMesh)
    pm.connectAttr(geoShape.worldMatrix, closestPointOnMesh.inputMatrix)
    loc = pm.spaceLocator(n=name.removeSuffix(geo.name())+'_LOC')
    pm.matchTransform(loc, obj)
    pm.connectAttr(loc.translate, closestPointOnMesh.inPosition)

    u = closestPointOnMesh.result.parameterU.get()
    v = closestPointOnMesh.result.parameterV.get()

    pm.delete(closestPointOnMesh, loc)

    return u, v

def makeControlFollowSkin(geo, ctrlTop):
    geo = pm.ls(geo)[0]
    ctrlTop = pm.ls(ctrlTop)[0]
    uv = findClosestUVCoordinate(geo, ctrlTop)
    prefix = name.removeSuffix(ctrlTop.name())
    follicle = createFollicle(geo, uv[0], uv[1], prefix)

    followGrp = pm.group(ctrlTop, n=prefix + 'Follow_GRP')
    compensateGrp = pm.group(ctrlTop, n=prefix + 'Compensate_GRP')

    pm.pointConstraint(follicle, followGrp, mo=True)

    multDivideNode = pm.createNode('multiplyDivide', n=prefix+'CompensateNode')
    pm.connectAttr(followGrp.translate, multDivideNode.input1)
    pm.connectAttr(multDivideNode.output, compensateGrp.translate)
    multDivideNode.input2X.set(-1)
    multDivideNode.input2Y.set(-1)
    multDivideNode.input2Z.set(-1)

    return followGrp, follicle
    
    
makeControlFollowSkin('Cape_Mesh', 'capeC6Offset_GRP')

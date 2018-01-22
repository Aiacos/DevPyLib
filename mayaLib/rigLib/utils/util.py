__author__ = 'Lorenzo Argentieri'

import pymel.core as pm
import pymel.core.runtime as runtime
import maya.mel as mel
import mayaLib.pipelineLib.utility.nameCheck as nc


def getDriverDrivenFromConstraint(constraint):
    driver = pm.listConnections(constraint+'.target[0].targetParentMatrix', destination=False)
    driven = pm.listConnections(constraint, source=False)[0]

    return driver, driven

def getSide(obj):
    pass
    side = ''
    return side

def makeCurvesDynamic(curve, grpName='dynamicCurve*_GRP'):
    grpName = nc.nameCheck(grpName)
    pm.select(curve)
    mel.eval('makeCurvesDynamic 2 { "1", "0", "1", "1", "0"};')

    dynamicObj_list = pm.ls('hairSystem*', 'nucleus*')
    # nucleus
    nucleus = pm.ls('nucleus*')

    # select last created hairSystem
    hairSystem = pm.ls('hairSystem*')[-1]

    if pm.objExists(grpName):
        pm.parent(hairSystem, grpName)
    else:
        pm.group(hairSystem, n=grpName)

    outputGrp = pm.ls('hairSystem*OutputCurves')[-1]
    follicleGrp = pm.ls('hairSystem*Follicles')[-1]
    outputCurve = pm.listRelatives(outputGrp, children=True)[0]

    # disable inheritTransform on follicle
    follicle = pm.listRelatives(follicleGrp, children=True)[0]
    pm.setAttr(follicle + '.inheritsTransform', 0)

    # regroup
    systemGrp = 'system_GRP'
    if pm.objExists(systemGrp):
        #pm.parent(nucleus, systemGrp)
        pass
    else:
        pm.group(nucleus, n=systemGrp)

    mainGrpName = 'dynamicSystem_GRP'
    if pm.objExists(mainGrpName):
        pm.parent(grpName, mainGrpName)
    else:
        pm.group(grpName, n=mainGrpName)

    pm.parent(systemGrp, mainGrpName)
    pm.parent(pm.ls(outputGrp, follicleGrp), grpName)

    return outputCurve, grpName, follicleGrp

def moveShape(source, destination):
    pn = pm.PyNode
    if isinstance(source, pn):
        pm.parent(source, destination[0], r=True, s=True)
    else:
        pm.parent(pm.PyNode(source[0]).getShape(), destination, r=True, s=True)

def get_distance(obj1, obj2):
    """
    Return distance between two objects
    :param obj1:
    :param obj2:
    :return: distance
    """

    loc0 = pm.spaceLocator()
    loc1 = pm.spaceLocator()
    constraint0 = pm.pointConstraint(obj1, loc0)
    constraint1 = pm.pointConstraint(obj2, loc1)

    def ctr_dist(objA, objB):
        Ax, Ay, Az = objA.getTranslation(space="world")
        Bx, By, Bz = objB.getTranslation(space="world")
        return ((Ax - Bx) ** 2 + (Ay - By) ** 2 + (Az - Bz) ** 2) ** 0.5

    distance = ctr_dist(loc0, loc1)
    # distance = pm.distanceDimension(loc0, loc1)
    pm.delete(constraint0, constraint1, loc0, loc1)
    return distance


# function to lock and hide attributes
def lock_and_hide_all(node):
    """
    lock and hide all transform attributes of selected node
    :param node: node to be affected
    """
    node.tx.set(l=1, k=0, cb=0)
    node.ty.set(l=1, k=0, cb=0)
    node.tz.set(l=1, k=0, cb=0)
    node.rx.set(l=1, k=0, cb=0)
    node.ry.set(l=1, k=0, cb=0)
    node.rz.set(l=1, k=0, cb=0)
    node.sx.set(l=1, k=0, cb=0)
    node.sy.set(l=1, k=0, cb=0)
    node.sz.set(l=1, k=0, cb=0)

# function to unlock and unhide attributes
def unlock_and_unhide_all(node):
    """
    unlock and unhide all transform attributes of selected node
    :param node: node to be affected
    """
    node.tx.set(l=0, k=1, cb=0)
    node.ty.set(l=0, k=1, cb=0)
    node.tz.set(l=0, k=1, cb=0)
    node.rx.set(l=0, k=1, cb=0)
    node.ry.set(l=0, k=1, cb=0)
    node.rz.set(l=0, k=1, cb=0)
    node.sx.set(l=0, k=1, cb=0)
    node.sy.set(l=0, k=1, cb=0)
    node.sz.set(l=0, k=1, cb=0)

# function to make surface not render
def no_render(tgt):
    """
    makes selected node non-renderable
    :param tgt: node to be affected
    """
    tgt.castsShadows.set(0)
    tgt.receiveShadows.set(0)
    tgt.motionBlur.set(0)
    tgt.primaryVisibility.set(0)
    tgt.smoothShading.set(0)
    tgt.visibleInReflections.set(0)
    tgt.visibleInRefractions.set(0)

def invertSelection():
    mel.eval('InvertSelection;')
    #runtime.InvertSelection()
    return pm.ls(sl=True)

def copyBind(source, destination):
    # Get Shape and skin from Object
    shape = pm.ls(source)[0].getShape()
    skinCluster = pm.listConnections(shape + '.inMesh', destination=False)
    if len(skinCluster) > 0:
        skin = pm.PyNode(skinCluster[0])
    else:
        print 'Missing source SkinCluster'

    # Get joint influence of the skin
    influnces = skin.getInfluence(q=True)  # influences is joint

    # Bind destination Mesh
    #pm.select(influnces[0])
    #pm.select(destination, add=True)
    #mel.eval('SmoothBindSkin;')
    pm.skinCluster(influnces[0], destination, dr=4.0)

    # copy skin wheights form source
    pm.select(source)
    pm.select(destination, add=True)
    pm.copySkinWeights(noMirror=True, surfaceAssociation='closestPoint', influenceAssociation='closestJoint')
    pm.select(cl=True)

__author__ = 'Lorenzo Argentieri'

import pymel.core as pm
import maya.mel as mel


def getDriverDrivenFromConstraint(constraint):
    driver = pm.listConnections(constraint + '.target[0].targetParentMatrix', destination=False)
    driven = pm.listConnections(constraint, source=False)[0]

    return driver, driven


def returnDriverObject(attribute, skipConversionNodes=False):
    """
    Returns the driver of an attribute if there is one
    :param attribute: pymel obj
    :param skipConversionNodes: bool
    :return: obj
    """
    objectBuffer = pm.listConnections(attribute, scn=skipConversionNodes, d=False, s=True, plugs=False)
    return pm.ls(objectBuffer[0])[0]


def returnDrivenAttribute(attribute, skipConversionNodes=False):
    """
    Returns the drivenAttribute of an attribute if there is one
    :param attribute: pymel obj
    :param skipConversionNodes: bool
    :return: list || False
    """
    if (pm.connectionInfo(attribute, isSource=True)) == True:
        destinationBuffer = pm.listConnections(attribute, scn=skipConversionNodes, s=False, d=True, plugs=True)
        if not destinationBuffer:
            destinationBuffer = pm.connectionInfo(attribute, destinationFromSource=True)
        if destinationBuffer:
            returnList = []
            for lnk in destinationBuffer:
                returnList.append(str(pm.ls(lnk)[0]))
            return returnList
        return False
    return False


def returnDrivenObject(attribute, skipConversionNodes=True):
    """
    Returns the driven object of an attribute if there is one
    :param attribute: pymel obj
    :param skipConversionNodes: bool
    :return: list || False
    """
    objectBuffer = pm.listConnections(attribute, scn=skipConversionNodes, s=False, d=True, plugs=False)
    if not objectBuffer:
        return False
    if attribute in objectBuffer:
        objectBuffer.remove(attribute)

    returnList = []
    for lnk in objectBuffer:
        returnList.append(str(pm.ls(lnk)[0]))
    return returnList


def getAllObjectUnderGroup(group, type='mesh'):
    """
    Return all object of given type under group
    :param group: str, group name
    :param type: str, object type
    :return: object list
    """
    objList = None

    if type == 'mesh':
        objList = [pm.listRelatives(o, p=1)[0] for o in pm.listRelatives(group, ad=1, type=type)]

    if type == 'transform':
        geoList = [pm.listRelatives(o, p=1)[0] for o in pm.listRelatives(group, ad=1, type='mesh')]
        objList = [o for o in pm.listRelatives(group, ad=1, type=type) if o not in geoList]

    return objList


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


def get_distance_from_coords(bboxMin, bboxMax):
    """
    Return distance between two points
    :param bboxMin: list, Ax, Ay, Az
    :param bboxMax: list, Bx, By, Bz
    :return:
    """
    Ax, Ay, Az = bboxMin
    Bx, By, Bz = bboxMax
    distance = ((Ax - Bx) ** 2 + (Ay - By) ** 2 + (Az - Bz) ** 2) ** 0.5

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
    # runtime.InvertSelection()
    return pm.ls(sl=True)

def getPlanarRadiusBBOXFromTransform(transform, radiusFactor=2):
    """
    Returns the bounding box radius in XZ
    :param transform: str, transform node
    :return: float
    """
    transform = pm.ls(transform)[0]
    BBox = transform.getBoundingBox()
    xmin, ymin, zmin = BBox[0]
    xmax, ymax, zmax = BBox[1]
    hypotenuse = get_distance_from_coords([xmin, 0, zmin], [xmax, 0, zmax])
    c1 = get_distance_from_coords([xmin, 0, 0], [xmax, 0, 0])
    c2 = get_distance_from_coords([0, 0, zmin], [0, 0, zmax])
    radius = hypotenuse / radiusFactor

    return radius

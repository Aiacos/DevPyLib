__author__ = "Lorenzo Argentieri"

import maya.mel as mel
import pymel.core as pm


def getDriverDrivenFromConstraint(constraint):
    """Returns the driver and driven objects from a given constraint


    Args:
        constraint (pm.nodetypes.Constraint): The constraint object

    Returns:
        tuple: (driver, driven)
    """
    # Get the driver object from the constraint
    driver = pm.listConnections(
        constraint + ".target[0].targetParentMatrix", destination=False
    )

    # Get the driven object from the constraint
    driven = pm.listConnections(constraint, source=False)[0]

    return driver, driven


def returnDriverObject(attribute, skipConversionNodes=False):
    """
    Returns the driver of an attribute if there is one
    :param attribute: pymel obj
    :param skipConversionNodes: bool
    :return: obj
    """
    objectBuffer = pm.listConnections(
        attribute, scn=skipConversionNodes, d=False, s=True, plugs=False
    )
    return pm.ls(objectBuffer[0])[0]


def returnDrivenAttribute(attribute, skipConversionNodes=False):
    """
    Returns the drivenAttribute of an attribute if there is one
    :param attribute: pymel obj
    :param skipConversionNodes: bool
    :return: list || False
    """
    if (pm.connectionInfo(attribute, isSource=True)) == True:
        destinationBuffer = pm.listConnections(
            attribute, scn=skipConversionNodes, s=False, d=True, plugs=True
        )
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
    objectBuffer = pm.listConnections(
        attribute, scn=skipConversionNodes, s=False, d=True, plugs=False
    )
    if not objectBuffer:
        return False
    if attribute in objectBuffer:
        objectBuffer.remove(attribute)

    returnList = []
    for lnk in objectBuffer:
        returnList.append(str(pm.ls(lnk)[0]))
    return returnList


def getAllObjectUnderGroup(group, type="mesh", full_path=True):
    """
    Return all object of given type under group
    Args:
        group (string): group name
        type (string): object type

    Returns:
        (pm.Mesh[]): object list

    """

    objList = None

    if type == "mesh":
        objList = [
            pm.listRelatives(o, p=1)[0]
            for o in pm.listRelatives(group, ad=1, type=type)
        ]

    if type == "nurbsSurface":
        objList = [
            pm.listRelatives(o, p=1)[0]
            for o in pm.listRelatives(group, ad=1, type=type)
        ]

    if type == "transform":
        geoList = [
            pm.listRelatives(o, p=1)[0]
            for o in pm.listRelatives(group, ad=1, type="mesh")
        ]
        objList = [
            o for o in pm.listRelatives(group, ad=1, type=type) if o not in geoList
        ]

    objList = list(set(objList))
    objList.sort()

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
    nodeList = pm.ls(node)

    for node in nodeList:
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
    nodeList = pm.ls(node)

    for node in nodeList:
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
    mel.eval("InvertSelection;")
    # runtime.InvertSelection()
    return pm.ls(sl=True)


def getPlanarRadiusBBOXFromTransform(transform, radiusFactor=2):
    """
    Returns radius bounding box as a dict for: planarX, planarY, planarZ, 3D;
    where X, Y, Z is the upvector plane n world space
    :param transform: str, transform node
    :return: dict(float)
    """
    transform = pm.ls(transform)[0]
    BBox = transform.getBoundingBox()
    xmin, ymin, zmin = BBox[0]
    xmax, ymax, zmax = BBox[1]

    hypotenuseX = get_distance_from_coords([0, ymin, zmin], [0, ymin, zmax])
    hypotenuseY = get_distance_from_coords([xmin, 0, zmin], [xmax, 0, zmax])
    hypotenuseZ = get_distance_from_coords([xmin, ymin, 0], [xmax, ymin, 0])
    hypotenuseXYZ = get_distance_from_coords([xmin, ymin, zmin], [xmax, ymax, zmax])

    cX = get_distance_from_coords([xmin, 0, 0], [xmax, 0, 0])
    cY = get_distance_from_coords([0, ymin, 0], [0, ymax, 0])
    cZ = get_distance_from_coords([0, 0, zmin], [0, 0, zmax])

    radiusDict = {
        "planarX": hypotenuseX / radiusFactor,
        "planarY": hypotenuseY / radiusFactor,
        "planarZ": hypotenuseZ / radiusFactor,
        "3D": hypotenuseXYZ / radiusFactor,
    }

    return radiusDict


def matrixConstrain(
    driver, driven, parent=None, translate=True, rotate=True, scale=False
):
    driver = pm.ls(driver)[0]
    driven = pm.ls(driven)[0]

    if not parent:
        parent = driven.getParent()

    mulMatrix = pm.shadingNode("multMatrix", asUtility=True)
    decomposeMatrix = pm.shadingNode("decomposeMatrix", asUtility=True)

    pm.connectAttr(mulMatrix.matrixSum, decomposeMatrix.inputMatrix)
    pm.connectAttr(driver.worldMatrix[0], mulMatrix.matrixIn[0])
    pm.connectAttr(parent.worldInverseMatrix[0], mulMatrix.matrixIn[1])

    if translate:
        pm.connectAttr(decomposeMatrix.outputTranslate, driven.translate)
    if rotate:
        pm.connectAttr(decomposeMatrix.outputRotate, driven.rotate)
    if scale:
        pm.connectAttr(decomposeMatrix.outputScale, driven.scale)

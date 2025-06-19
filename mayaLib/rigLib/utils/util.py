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
    Returns the driver object of an attribute if there is one.

    Args:
        attribute (pm.PyNode): The attribute to query
        skipConversionNodes (bool): If True, skips any conversion nodes

    Returns:
        pm.PyNode: The driver object
    """
    # Get the driver object from the attribute
    # We use the listConnections command to get the driver object
    # We pass in the attribute as the source and set the destination flag to False
    # We also set the skipConversionNodes flag to the value passed in
    # We get the first element of the list returned by listConnections
    # We use the pm.ls command to get the actual PyNode object
    objectBuffer = pm.listConnections(
        attribute, scn=skipConversionNodes, d=False, s=True, plugs=False
    )
    return pm.ls(objectBuffer[0])[0]


def returnDrivenAttribute(attribute, skipConversionNodes=False):
    """
    Returns the drivenAttribute of an attribute if there is one

    Args:
        attribute (pm.PyNode): The attribute to query
        skipConversionNodes (bool): If True, skips any conversion nodes

    Returns:
        list: A list of pm.PyNode objects that are connected to the given attribute
        False: If the attribute is not connected to any nodes
    """
    if pm.connectionInfo(attribute, isSource=True):
        # Get the destination attributes connected to the given attribute
        destinationBuffer = pm.listConnections(
            attribute, scn=skipConversionNodes, s=False, d=True, plugs=True
        )
        if not destinationBuffer:
            # If the attribute is not connected to any nodes, get the destination
            # using the connectionInfo command
            destinationBuffer = pm.connectionInfo(attribute, destinationFromSource=True)
        if destinationBuffer:
            # If the attribute is connected to some nodes, return a list of those nodes
            returnList = []
            for lnk in destinationBuffer:
                returnList.append(str(pm.ls(lnk)[0]))
            return returnList
        # If the attribute is not connected to any nodes, return False
        return False


def returnDrivenObject(attribute, skipConversionNodes=True):
    """
    Returns the driven object of an attribute if there is one

    Args:
        attribute (pm.PyNode): The attribute to query
        skipConversionNodes (bool): If True, skips any conversion nodes

    Returns:
        list: A list of pm.PyNode objects that are connected to the given attribute
        False: If the attribute is not connected to any nodes
    """
    # Get the destination objects connected to the given attribute
    objectBuffer = pm.listConnections(
        attribute, scn=skipConversionNodes, s=False, d=True, plugs=False
    )

    # If the attribute is not connected to any nodes, return False
    if not objectBuffer:
        return False

    # If the attribute is connected to some nodes, return a list of those nodes
    returnList = []
    for lnk in objectBuffer:
        # If the attribute is connected to itself, skip it
        if attribute == lnk:
            continue
        # Get the actual PyNode object from the connection
        returnList.append(str(pm.ls(lnk)[0]))
    return returnList


def getAllObjectUnderGroup(group, type="mesh", full_path=True):
    """
    Return all objects of a given type under a specified group in Maya.

    Args:
        group (str): Name of the group node.
        type (str): Type of objects to retrieve. Options are 'mesh', 'nurbsSurface', or 'transform'.
        full_path (bool): Whether to return the full path of the objects.

    Returns:
        list: A sorted list of unique object names.

    """
    objList = None

    # Retrieve all mesh objects under the group
    if type == "mesh":
        objList = [
            pm.listRelatives(o, p=1, fullPath=full_path)[0]
            for o in pm.listRelatives(group, ad=1, type=type, fullPath=full_path)
        ]

    # Retrieve all nurbsSurface objects under the group
    elif type == "nurbsSurface":
        objList = [
            pm.listRelatives(o, p=1, fullPath=full_path)[0]
            for o in pm.listRelatives(group, ad=1, type=type, fullPath=full_path)
        ]

    # Retrieve all transform objects under the group excluding geometries
    elif type == "transform":
        geoList = [
            pm.listRelatives(o, p=1, fullPath=full_path)[0]
            for o in pm.listRelatives(group, ad=1, type="mesh", fullPath=full_path)
        ]
        objList = [
            o
            for o in pm.listRelatives(group, ad=1, type=type, fullPath=full_path)
            if o not in geoList
        ]

    # Remove duplicates and sort the list
    objList = list(set(objList))
    objList.sort()

    return objList


def moveShape(source, destination):
    """
    Move the shape from the source to the destination.

    Args:
        source (list or pm.PyNode): The source object or a list with the source object.
        destination (list or pm.PyNode): The destination object or a list with the destination object.

    Returns:
        None
    """
    pn = pm.PyNode
    if isinstance(source, pn):
        # If source is a PyNode, parent it directly
        pm.parent(source, destination[0], r=True, s=True)
    else:
        # If source is a list, get the shape and parent it
        pm.parent(pn(source[0]).getShape(), destination, r=True, s=True)


def get_distance(obj1, obj2):
    """
    Return the distance between two objects.

    Args:
        obj1 (str or pm.PyNode): The first object.
        obj2 (str or pm.PyNode): The second object.

    Returns:
        float: The distance between the two objects.
    """
    # Create two temporary locators
    loc0 = pm.spaceLocator()
    loc1 = pm.spaceLocator()

    # Create two point constraints, one for each object
    constraint0 = pm.pointConstraint(obj1, loc0)
    constraint1 = pm.pointConstraint(obj2, loc1)

    # Define a function to calculate the distance between two objects
    def ctr_dist(objA, objB):
        """
        Calculate the Euclidean distance between two objects in world space.

        Args:
            objA (pm.PyNode): The first object, represented as a PyNode.
            objB (pm.PyNode): The second object, represented as a PyNode.

        Returns:
            float: The Euclidean distance between the two objects.
        """
        # Get the world space translation of the first object
        Ax, Ay, Az = objA.getTranslation(space="world")
        # Get the world space translation of the second object
        Bx, By, Bz = objB.getTranslation(space="world")
        # Calculate and return the Euclidean distance between the two objects
        return ((Ax - Bx) ** 2 + (Ay - By) ** 2 + (Az - Bz) ** 2) ** 0.5

    # Calculate the distance between the two locators
    distance = ctr_dist(loc0, loc1)

    # Delete the temporary locators and constraints
    pm.delete(constraint0, constraint1, loc0, loc1)

    # Return the distance
    return distance


def get_distance_from_coords(bboxMin, bboxMax):
    """
    Return the Euclidean distance between two points in 3D space.

    Args:
        bboxMin (list): The coordinates of the first point, represented as a list of three floats.
        bboxMax (list): The coordinates of the second point, represented as a list of three floats.

    Returns:
        float: The Euclidean distance between the two points.
    """
    Ax, Ay, Az = bboxMin
    Bx, By, Bz = bboxMax
    # Calculate and return the Euclidean distance between the two points
    distance = ((Ax - Bx) ** 2 + (Ay - By) ** 2 + (Az - Bz) ** 2) ** 0.5

    return distance


# function to lock and hide attributes
def lock_and_hide_all(node):
    """
    Lock and hide all transform attributes of the specified node.

    Args:
        node (str or list of str): The node(s) to be affected.
    """
    nodeList = pm.ls(node)

    for node in nodeList:
        # Lock and hide translation attributes
        node.tx.set(lock=True, keyable=False, channelBox=False)
        node.ty.set(lock=True, keyable=False, channelBox=False)
        node.tz.set(lock=True, keyable=False, channelBox=False)

        # Lock and hide rotation attributes
        node.rx.set(lock=True, keyable=False, channelBox=False)
        node.ry.set(lock=True, keyable=False, channelBox=False)
        node.rz.set(lock=True, keyable=False, channelBox=False)

        # Lock and hide scale attributes
        node.sx.set(lock=True, keyable=False, channelBox=False)
        node.sy.set(lock=True, keyable=False, channelBox=False)
        node.sz.set(lock=True, keyable=False, channelBox=False)


# function to unlock and unhide attributes
def unlock_and_unhide_all(node):
    """
    Unlock and unhide all transform attributes of the selected node.

    Args:
        node (str or list of str): The node(s) to be affected.
    """
    nodeList = pm.ls(node)

    for node in nodeList:
        # Unlock and unhide translation attributes
        # l: lock, k: keyable, cb: channel box
        node.tx.set(l=0, k=1, cb=1)
        node.ty.set(l=0, k=1, cb=1)
        node.tz.set(l=0, k=1, cb=1)

        # Unlock and unhide rotation attributes
        node.rx.set(l=0, k=1, cb=1)
        node.ry.set(l=0, k=1, cb=1)
        node.rz.set(l=0, k=1, cb=1)

        # Unlock and unhide scale attributes
        node.sx.set(l=0, k=1, cb=1)
        node.sy.set(l=0, k=1, cb=1)
        node.sz.set(l=0, k=1, cb=1)


def no_render(tgt):
    """
    Makes selected node non-renderable.

    This function sets various visibility and shadow attributes to 0.
    This is useful for making a node non-renderable in a scene.

    Parameters
    ----------
    tgt : str or list of str
        The node(s) to be affected.
    """
    tgt = pm.ls(tgt)

    # set visibility attributes
    tgt.castsShadows.set(0)
    tgt.receiveShadows.set(0)
    tgt.motionBlur.set(0)
    tgt.primaryVisibility.set(0)
    tgt.smoothShading.set(0)
    tgt.visibleInReflections.set(0)
    tgt.visibleInRefractions.set(0)


def invertSelection():
    """
    Invert the current selection in the scene.

    This function uses the MEL command 'InvertSelection' to invert the selection
    of components or objects in the scene and returns the new selection list.

    Returns
    -------
    list
        A list of currently selected objects after inversion.
    """
    # Execute the MEL command to invert the current selection
    mel.eval("InvertSelection;")

    # Return the list of selected objects
    return pm.ls(sl=True)


def getPlanarRadiusBBOXFromTransform(transform, radiusFactor=2):
    """
    Calculate the radius of the bounding box for a given transform node.

    This function returns a dictionary containing the radius of the bounding
    box for three planar directions (X, Y, Z) and the 3D hypotenuse. The
    radius is calculated based on the bounding box dimensions and a specified
    radius factor.

    Args:
        transform (str): The transform node.
        radiusFactor (float, optional): The factor by which the radius is divided.
            Defaults to 2.

    Returns:
        dict: A dictionary containing the radius for 'planarX', 'planarY', 'planarZ', and '3D'.
    """
    # Get the first matching transform node
    transform = pm.ls(transform)[0]

    # Retrieve the bounding box as a tuple of min and max coordinates
    BBox = transform.getBoundingBox()
    xmin, ymin, zmin = BBox[0]
    xmax, ymax, zmax = BBox[1]

    # Calculate hypotenuse distances for each planar direction
    hypotenuseX = get_distance_from_coords([0, ymin, zmin], [0, ymin, zmax])
    hypotenuseY = get_distance_from_coords([xmin, 0, zmin], [xmax, 0, zmax])
    hypotenuseZ = get_distance_from_coords([xmin, ymin, 0], [xmax, ymin, 0])
    hypotenuseXYZ = get_distance_from_coords([xmin, ymin, zmin], [xmax, ymax, zmax])

    # Calculate center distances for each axis
    cX = get_distance_from_coords([xmin, 0, 0], [xmax, 0, 0])
    cY = get_distance_from_coords([0, ymin, 0], [0, ymax, 0])
    cZ = get_distance_from_coords([0, 0, zmin], [0, 0, zmax])

    # Create a dictionary of radii divided by the radius factor
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
    """
    Constrain a driven transform to a driver transform using a matrix multiply.

    This function creates a multiply matrix node and a decompose matrix node to
    multiply the driver's world matrix with the parent's world inverse matrix.
    The resulting matrix is then fed into the decompose matrix node which
    separates the translation, rotation, and scale components of the matrix.
    These components are then connected to the corresponding attributes of the
    driven transform.

    Args:
        driver (str): The node that drives the constraint.
        driven (str): The node that is constrained.
        parent (str, optional): The parent of the driven node. Defaults to None.
        translate (bool, optional): Whether to constrain the translation. Defaults to True.
        rotate (bool, optional): Whether to constrain the rotation. Defaults to True.
        scale (bool, optional): Whether to constrain the scale. Defaults to False.
    """
    driver = pm.ls(driver)[0]
    driven = pm.ls(driven)[0]

    if not parent:
        parent = driven.getParent()

    # Create a multiply matrix node and a decompose matrix node
    mulMatrix = pm.shadingNode("multMatrix", asUtility=True)
    decomposeMatrix = pm.shadingNode("decomposeMatrix", asUtility=True)

    # Connect the driver's world matrix with the parent's world inverse matrix
    pm.connectAttr(mulMatrix.matrixSum, decomposeMatrix.inputMatrix)
    pm.connectAttr(driver.worldMatrix[0], mulMatrix.matrixIn[0])
    pm.connectAttr(parent.worldInverseMatrix[0], mulMatrix.matrixIn[1])

    # Connect the decomposed matrix components to the driven transform
    if translate:
        pm.connectAttr(decomposeMatrix.outputTranslate, driven.translate)
    if rotate:
        pm.connectAttr(decomposeMatrix.outputRotate, driven.rotate)
    if scale:
        pm.connectAttr(decomposeMatrix.outputScale, driven.scale)

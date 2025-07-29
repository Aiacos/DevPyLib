__author__ = "Lorenzo Argentieri"

import maya.mel as mel
import pymel.core as pm


def centerPivot(obj, targetPivot=None):
    """Centers the pivot of the given object.

    This function centers the pivot of the specified object. If a target pivot
    is provided, the object's pivot is set to the target's pivot position.

    Args:
        obj (str): The name of the object whose pivot will be centered.
        targetPivot (Optional[str]): The name of the target object whose pivot
            position will be used. Defaults to None, in which case the object's
            pivot is centered.

    Returns:
        None
    """
    if targetPivot is None:
        # Center the pivot of the object
        pm.xform(obj, cp=1)
    else:
        # Query the target pivot's position and set it to the object's pivot
        pivotTranslate = pm.xform(targetPivot, q=True, ws=True, rotatePivot=True)
        pm.xform(obj, ws=True, pivots=pivotTranslate)


def freezeTransform(obj):
    """Freeze the transformation of the given object.

    This command is like the Maya "Freeze Transformations" menu item.
    It will make sure that the transformation (translate, rotate, scale) of the
    object is zeroed out, and that the object is moved to its own pivot point.

    Args:
        obj: str, the object to freeze the transformation of

    Returns:
        None
    """
    pm.makeIdentity(obj, apply=True, t=1, r=1, s=1, n=0)


def deleteHistory(obj):
    """Delete all history in the given object.

    Args:
        obj: str, the object to delete history from

    Returns:
        None
    """
    pm.delete(obj, ch=True)


def delete_non_deformer_history(obj):
    """Delete all non-deformer history in the given object.

    Args:
        obj: str, the object to delete history from

    Returns:
        None
    """
    pm.bakePartialHistory(obj, pre=True)


def deleteConnection(objAttrList):
    """Delete the given connections.

    Args:
        objAttrList: list, of strings, the plug names (ctrl.attr) to delete

    Returns:
        None
    """
    objAttrList = pm.ls(objAttrList)
    for objAttr in objAttrList:
        mel.eval("CBdeleteConnection " + str(objAttr.name()) + ";")


def delete_connection(plug):
    """Equivalent of MEL: CBdeleteConnection

    Deletes the given connection.

    Args:
        plug: str, the plug name (ctrl.attr)

    Returns:
        None
    """
    if pm.connectionInfo(plug, isDestination=True):
        plug = pm.connectionInfo(plug, getExactDestination=True)
        read_only = pm.ls(plug, ro=True)
        # delete -icn doesn't work if destination attr is readOnly
        if read_only:
            source = pm.connectionInfo(plug, sourceFromDestination=True)
            pm.disconnectAttr(source, plug)
        else:
            pm.delete(plug, icn=True)


def set_driven_key(
    driver, driver_value_list, driven, driven_value_list, cv_type="linear"
):
    """
    Set Driven Key utility

    Sets driven key using the given lists of values for the driver and driven
    attributes.

    Args:
        driver: str, driver + driving attribute (ctrl.attr)
        driver_value_list: list, value list
        driven: str, driven + driven attribute (ctrl.attr)
        driven_value_list: list, value list
        cv_type: str, auto, clamped, fast, flat, linear, plateau, slow, spline,
            step, and stepnext
    """
    for driver_v, driven_v in zip(driver_value_list, driven_value_list):
        pm.setDrivenKeyframe(
            driven,
            currentDriver=driver,
            driverValue=driver_v,
            value=driven_v,
            inTangentType=cv_type,
            outTangentType=cv_type,
        )


def delete_unknow_nodes():
    """Delete unknown nodes in the Maya scene.

    This function identifies and deletes nodes of type 'unknown', 'unknownDag',
    and 'unknownTransform'. These are typically nodes that have lost their
    plugin references or are otherwise unidentified.

    Note:
        Ensure that no important nodes are deleted by mistake.

    """
    # List all unknown nodes in the scene
    unknow_list = pm.ls(
        mel.eval("ls -type unknown -type unknownDag -type unknownTransform")
    )

    # Iterate over the list and delete each node
    while unknow_list:
        for node in unknow_list:
            # Unlock the node to allow deletion
            pm.lockNode(node, lock=False)
            # Delete the node
            pm.delete(node)
        # Update the list of unknown nodes
        unknow_list = pm.ls(
            mel.eval("ls -type unknown -type unknownDag -type unknownTransform")
        )


def remove_shapeDeformed():
    """
    Remove the suffix "Deformed" from all deformed geometry shape nodes.

    When the deformer is applied, Maya will create a new shape node with the
    suffix "Deformed". This method will find all the deformed shape nodes and
    rename them to remove the suffix, so they will have the same name as the
    original shape node.
    """
    # Get all shape nodes
    shape_node_list = pm.ls("*Shape", type="mesh", long=True)
    # Rename all shape nodes to add "_Original" at the end
    for s in shape_node_list:
        pm.rename(s.name(), s.name() + "_Original")

    # Get all deformed shape nodes
    deformed_shapes = pm.ls("*ShapeDeformed", type="mesh", long=True)
    # Rename all deformed shape nodes to remove the suffix "Deformed"
    for s in deformed_shapes:
        new_name = str(s.name()).replace("ShapeDeformed", "Shape")
        pm.rename(s, new_name)

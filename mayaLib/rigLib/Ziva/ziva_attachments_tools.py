import maya.mel as mel
import pymel.core as pm


def getAllObjectUnderGroup(group, type='mesh'):
    """
    Return all object of given type under group

    Args:
        group (string): group name
        type (string): object type

    Returns:
        (pm.PyNode[]): object list
    """
    objList = None

    if type == 'mesh':
        objList = [pm.listRelatives(o, p=1)[0] for o in pm.listRelatives(group, ad=1, type=type)]

    if type == 'transform':
        geoList = [pm.listRelatives(o, p=1)[0] for o in pm.listRelatives(group, ad=1, type='mesh')]
        objList = [o for o in pm.listRelatives(group, ad=1, type=type) if o not in geoList]

    objList = list(set(objList))
    objList.sort()

    return objList


def zivaFixedAttachment(stiffness=8):
    """
    Create a fixed Ziva attachment with specified stiffness.

    Args:
        stiffness (int, optional): The stiffness exponent to set for the attachment. Default is 8.

    Returns:
        pm.nt.DagNode: The created Ziva attachment node.
    """
    zAttachment = pm.ls(mel.eval('ziva -a;'))[0]
    zAttachment.stiffnessExp.set(stiffness)

    return zAttachment


def zivaSlidingAttachment(stiffness=8):
    """
    Create a sliding Ziva attachment with specified stiffness.

    Args:
        stiffness (int, optional): The stiffness exponent to set for the attachment. Default is 8.

    Returns:
        pm.nt.DagNode: The created Ziva attachment node.
    """
    zAttachment = pm.ls(mel.eval('ziva -a;'))[0]
    zAttachment.attachmentMode.set(2)
    zAttachment.stiffnessExp.set(stiffness)

    return zAttachment


def paintProximity(zAttachement, min=0.0001, max=1):
    """
    Paint a Ziva attachment based on proximity.

    Args:
        zAttachement (pm.nt.DagNode): The Ziva attachment node to paint.
        min (float, optional): The minimum proximity value. Default is 0.0001.
        max (float, optional): The maximum proximity value. Default is 1.

    Returns:
        None
    """
    pm.select(zAttachement)
    mel.eval('zPaintAttachmentsByProximity -min ' + str(min) + ' -max ' + str(max) + ';')


def addAttachment(source, dest, value, fixed=True):
    """
    Create a Ziva attachment between the source and destination objects.

    Args:
        source (pm.PyNode): The source object for the attachment.
        dest (pm.PyNode): The destination object for the attachment.
        value (float): The maximum proximity value for painting the attachment.
        fixed (bool, optional): If True, create a fixed attachment. If False, create a sliding attachment. Default is True.

    Returns:
        None
    """
    pm.select(source)
    pm.select(dest, add=True)

    if fixed:
        current_zAttachemnt = zivaFixedAttachment()
    else:
        current_zAttachemnt = zivaSlidingAttachment(6)

    paintProximity(current_zAttachemnt, 0.0001, value)


if __name__ == "__main__":
    source, dest = pm.ls(sl=True)
    addAttachment(source, dest, 0.5, fixed=False)

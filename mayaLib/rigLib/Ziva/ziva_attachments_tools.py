"""Ziva VFX attachment creation and management tools.

Provides utilities for creating and configuring Ziva attachments
between tissues, bones, and muscles.
"""

import maya.mel as mel
import pymel.core as pm

from mayaLib.rigLib.utils.util import list_objects_under_group


def ziva_fixed_attachment(stiffness=8):
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


def ziva_sliding_attachment(stiffness=8):
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


def paint_proximity(z_attachement, min=0.0001, max=1):
    """
    Paint a Ziva attachment based on proximity.

    Args:
        zAttachement (pm.nt.DagNode): The Ziva attachment node to paint.
        min (float, optional): The minimum proximity value. Default is 0.0001.
        max (float, optional): The maximum proximity value. Default is 1.

    Returns:
        None
    """
    pm.select(z_attachement)
    mel.eval('zPaintAttachmentsByProximity -min ' + str(min) + ' -max ' + str(max) + ';')


def add_attachment(source, dest, value, fixed=True):
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
        current_zAttachemnt = ziva_fixed_attachment()
    else:
        current_zAttachemnt = ziva_sliding_attachment(6)

    paint_proximity(current_zAttachemnt, 0.0001, value)


if __name__ == "__main__":
    source, dest = pm.ls(sl=True)
    add_attachment(source, dest, 0.5, fixed=False)

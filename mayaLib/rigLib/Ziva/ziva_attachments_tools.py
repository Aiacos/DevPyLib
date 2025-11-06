"""Ziva VFX attachment creation and management tools.

Provides utilities for creating and configuring Ziva attachments
between tissues, bones, and muscles.
"""

import maya.mel as mel
import pymel.core as pm


def ziva_fixed_attachment(stiffness=8):
    """Create a fixed Ziva attachment with specified stiffness.

    Args:
        stiffness (int, optional): The stiffness exponent to set for the attachment. Default is 8.

    Returns:
        pm.nt.DagNode: The created Ziva attachment node.
    """
    z_attachment = pm.ls(mel.eval("ziva -a;"))[0]
    z_attachment.stiffnessExp.set(stiffness)

    return z_attachment


def ziva_sliding_attachment(stiffness=8):
    """Create a sliding Ziva attachment with specified stiffness.

    Args:
        stiffness (int, optional): The stiffness exponent to set for the attachment. Default is 8.

    Returns:
        pm.nt.DagNode: The created Ziva attachment node.
    """
    z_attachment = pm.ls(mel.eval("ziva -a;"))[0]
    z_attachment.attachmentMode.set(2)
    z_attachment.stiffnessExp.set(stiffness)

    return z_attachment


def paint_proximity(z_attachement, min_value=0.0001, max_value=1):
    """Paint a Ziva attachment based on proximity.

    Args:
        zAttachement (pm.nt.DagNode): The Ziva attachment node to paint.
        min_value (float, optional): The minimum proximity value. Default is 0.0001.
        max_value (float, optional): The maximum proximity value. Default is 1.

    Returns:
        None
    """
    pm.select(z_attachement)
    mel.eval(
        "zPaintAttachmentsByProximity -min " + str(min_value) + " -max " + str(max_value) + ";"
    )


def add_attachment(source, dest, value, fixed=True):
    """Create a Ziva attachment between the source and destination objects.

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

    current_z_attachment = ziva_fixed_attachment() if fixed else ziva_sliding_attachment(6)

    paint_proximity(current_z_attachment, 0.0001, value)


if __name__ == "__main__":
    source, dest = pm.ls(sl=True)
    add_attachment(source, dest, 0.5, fixed=False)

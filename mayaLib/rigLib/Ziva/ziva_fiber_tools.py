"""Ziva VFX fiber creation and editing tools.

Provides utilities for creating and manipulating muscle fibers
for Ziva VFX simulations.
"""

import maya.mel as mel
import pymel.core as pm

from mayaLib.rigLib.utils.util import list_objects_under_group


def add_ziva_fiber(obj):
    """Add Ziva fiber to the given object

    Args:
        obj (str): Object name

    Returns:
        The zFiber node
    """
    pm.select(obj)
    z_fiber = pm.ls(mel.eval('ziva -f;'))[0]
    return z_fiber


def create_loa_curve(obj):
    """Create a curve for Line of Action

    Args:
        obj (str): Object name

    Returns:
        The created curve
    """
    obj = pm.ls(obj)[-1]
    pm.select(obj)
    curve = pm.ls(mel.eval('zLineOfActionUtil;'))[0].getParent()

    cv_name = str(obj.name()) + '_CV'
    pm.rename(curve, cv_name)
    curve = pm.ls(cv_name)[-1]

    return curve


def rivet_curve(curve, skeleton):
    """Rivet the curve to the given skeleton

    Args:
        curve (str): Curve name
        skeleton (str): Skeleton name

    Returns:
        A list of zRivet nodes
    """
    rivet_list = []
    for cv, n in zip(curve.cv[:], list(range(0, len(pm.ls(curve.cv[:])) + 1))):
        pm.select(cv)
        pm.select(skeleton, add=True)
        z_rivet = pm.ls(mel.eval('zRivetToBone;'))[-1]

        rivet_name = str(curve.name()).replace('_CV', '') + '_' + str(n) + '_rivet'
        pm.rename(z_rivet, rivet_name)
        z_rivet = pm.ls(rivet_name)[-1]

        rivet_list.append(z_rivet)

    return rivet_list


def add_loa(curve, obj):
    """Add Line of Action to the given object

    Args:
        curve (str): Curve name
        obj (str): Object name

    Returns:
        The zLineOfAction node
    """
    pm.select(curve)
    pm.select(obj, add=True)

    z_line_of_action = pm.ls(mel.eval('ziva -loa;'))[-1]
    return z_line_of_action


def create_line_of_action(obj, skeleton):
    """Create Line of Action for the given object

    Args:
        obj (str): Object name
        skeleton (str): Skeleton name

    Returns:
        The created curve and a list of zRivet nodes
    """
    add_ziva_fiber(obj)
    curve = create_loa_curve(obj)
    rivets = rivet_curve(curve, skeleton)
    add_loa(curve, obj)

    return curve, rivets


if __name__ == '__main__':
    for geo in list_objects_under_group('muscles_grp'):
        create_line_of_action(geo, 'C_charBison_skeleton_GEO')

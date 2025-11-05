"""Ziva VFX general utilities and helpers.

Provides common utility functions for working with Ziva VFX
nodes and attributes.
"""

import pymel.core as pm

from mayaLib.rigLib.utils import common, deform


def mirror_geo(geo_list):
    """
    Mirror a list of geometries.

    Args:
        geo_list: List of geometries to mirror.

    Returns:
        None
    """
    geo_list = pm.ls(geo_list)
    
    mirror_geo_list = []
    for geo in geo_list:
        # Create a duplicate of the geometry with the opposite side name
        geo_name = str(geo.name()).replace('L_', 'R_') + '_mirror'
        duplicate_geo = pm.duplicate(geo, n=geo_name)[-1]
        pm.parent(duplicate_geo, w=True)
        mirror_geo_list.append(duplicate_geo)
        
    # Create a group for the mirrored geometries
    duplicate_grp = pm.group(mirror_geo_list)
    # Mirror the group in the X axis
    duplicate_grp.scaleX.set(-1)
    # Freeze the transformation of the group
    common.freezeTranform(duplicate_grp)
    # Delete the history of the group
    common.deleteHistory(duplicate_grp)
    
    # Iterate over the mirrored geometries and blendShape them with the original
    for geo in mirror_geo_list:
        # Get the name of the original geometry
        mirror_geo_name = str(geo.name()).replace('_mirror', '')
        # BlendShape the original geometry with the mirrored one
        deform.blend_shape_deformer(mirror_geo_name, [geo], mirror_geo_name + '_tmp_BS')
        # Delete the history of the original geometry
        common.deleteHistory(mirror_geo_name)
        
    # Delete the group
    pm.delete(duplicate_grp)

"""
Utility functions to get all Maya objects of a given type
"""

__author__ = 'Lorenzo Argentieri'

import pymel.core as pm


def get_all_groups():
    """Return all groups in the scene"""
    geo_list = [pm.listRelatives(o, p=1)[0] for o in pm.listRelatives(type='mesh')]
    grp_list = [o for o in pm.listRelatives(type='transform') if o not in geo_list]
    return grp_list


def get_all_locators():
    """Return all locators in the scene"""
    loc_list = [l.getParent() for l in pm.ls(type='locator')]
    return loc_list


def get_all_mesh():
    """Return all mesh objects in the scene"""
    mesh_list = [pm.listRelatives(o, p=1)[0] for o in pm.listRelatives(type='mesh')]
    return mesh_list


def get_all_curves():
    """Return all nurbsCurves in the scene"""
    curve_list = [cv.getParent() for cv in pm.ls(type='nurbsCurve')]
    return curve_list


def get_all_joints():
    """Return all joints in the scene"""
    jnt_list = pm.ls(type='joint')
    return jnt_list


def get_all_ik_handles():
    """Return all ikHandles in the scene"""
    ikh_list = pm.ls(type='ikHandle')
    return ikh_list


def get_all_lights():
    """Return all lights in the scene"""
    lgt_list = pm.ls(lights=True)
    return lgt_list


def get_all_materials():
    """Return all materials in the scene"""
    mat_list = pm.ls(materials=True)
    return mat_list


def get_all_textures():
    """Return all textures in the scene"""
    tex_list = pm.ls(textures=True)
    return tex_list
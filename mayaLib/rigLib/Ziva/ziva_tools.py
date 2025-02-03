"""
Utilities for Ziva dynamics
"""

import maya.mel as mel
import pymel.core as pm

if pm.about(version=True) == '2022':
    import zBuilder.builders.ziva as zva
    import zBuilder.commands as zva_cmds


def zPolyCombine(geos):
    """
    Combine multiple geometry objects into a single one using Ziva's command.

    Args:
        geos (list): A list of geometry objects to combine.

    Returns:
        The resulting combined geometry object.
    """
    pm.select(pm.ls(geos))
    zPolyCombine_node, zPolyCombine_mesh = pm.ls(mel.eval('zPolyCombine;'))

    return zPolyCombine_mesh


def harmonic_warp(source, destination, transfer_geos, tet_size=1):
    """
    Warp a source geometry to a destination geometry using Ziva's harmonic warp
    command.

    Args:
        source (str): The name of the source geometry.
        destination (str): The name of the destination geometry.
        transfer_geos (list): A list of geometry objects to transfer between
            the source and destination.
        tet_size (int): The size of the tetrahedral mesh.

    Returns:
        The resulting harmonic warp node.
    """
    source_string = str(pm.ls(source)[-1].name())
    destination_string = str(pm.ls(destination)[-1].name())
    transfer_list = []
    for geo in pm.ls(transfer_geos):
        name = str(geo.name())
        transfer_list.append(name)
    transfer_string = ' '.join(transfer_list)

    zArmonicWarp = pm.ls(mel.eval('zHarmonicWarp ' + source_string + ' ' +
                                 destination_string + ' ' + transfer_string +
                                 ';'))[0]
    zArmonicWarp.maxResolution.set(512)
    zArmonicWarp.tetSize.set(tet_size)

    return zArmonicWarp


def bone_warp(source, destination, transfer_geos, tet_size=1):
    """
    Warp a source geometry to a destination geometry using Ziva's bone warp
    command.

    Args:
        source (str): The name of the source geometry.
        destination (str): The name of the destination geometry.
        transfer_geos (list): A list of geometry objects to transfer between
            the source and destination.
        tet_size (int): The size of the tetrahedral mesh.

    Returns:
        The resulting bone warp node.
    """
    source_string = str(pm.ls(source)[-1].name())
    destination_string = str(pm.ls(destination)[-1].name())
    transfer_list = []
    for geo in pm.ls(transfer_geos):
        name = str(geo.name())
        transfer_list.append(name)
    transfer_string = ' '.join(transfer_list)

    zBoneWarp = pm.ls(mel.eval('zBoneWarp ' + source_string + ' ' + destination_string + ' ' + transfer_string + ';'))[0]
    zBoneWarp.maxResolution.set(512)
    zBoneWarp.tetSize.set(tet_size)

    return zBoneWarp


def ziva_check_intersection(geo1, geo2):
    """
    Check for intersection between two geometry objects using Ziva's command.

    Args:
        geo1 (str): The name of the first geometry object.
        geo2 (str): The name of the second geometry object.

    Returns:
        A list of objects that intersect between the two geometry objects.
    """
    pm.select(geo1, geo2)
    mel.eval('ZivaSelectIntersections;')

    return pm.ls(sl=True, o=True)


# Rename
def zivaRenameAll():
    """
    Rename all Ziva nodes in the scene.
    """
    zva_cmds.rename_ziva_nodes()


# Mirror
def zivaMirror(from_side='L_', to_side='R_', suffix='_GEO'):
    """
    Mirror a Ziva setup from one side of the body to the other.

    Args:
        from_side (str): The side of the body to copy from.
        to_side (str): The side of the body to copy to.
        suffix (str): The suffix to add to the end of the node names.
    """
    pm.select(pm.ls(from_side + '*' + suffix))
    zObj = zva.Ziva()

    if pm.ls(sl=True):
        zObj.retrieve_from_scene_selection()
    else:
        zObj.retrieve_from_scene()

    zObj.string_replace('^' + from_side, to_side)
    zObj.build()


if __name__ == "__main__":
    zivaRenameAll()
    zivaMirror('R_', 'L_')
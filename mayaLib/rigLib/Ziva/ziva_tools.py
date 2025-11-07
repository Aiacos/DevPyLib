"""Utilities for Ziva dynamics."""

import maya.mel as mel
import pymel.core as pm

try:
    import zBuilder.builders.ziva as zva
    import zBuilder.commands as zva_cmds
except ImportError:
    zva = None  # type: ignore[assignment]
    zva_cmds = None  # type: ignore[assignment]


def z_poly_combine(geos):
    """Combine multiple geometry objects into a single one using Ziva's command.

    Args:
        geos (list): A list of geometry objects to combine.

    Returns:
        The resulting combined geometry object.
    """
    pm.select(pm.ls(geos))
    z_poly_combine_node, z_poly_combine_mesh = pm.ls(mel.eval("zPolyCombine;"))

    return z_poly_combine_mesh


def harmonic_warp(source, destination, transfer_geos, tet_size=1):
    """Warp a source geometry to a destination geometry using Ziva's harmonic warp command.

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
    transfer_string = " ".join(transfer_list)

    z_armonic_warp = pm.ls(
        mel.eval(
            "zHarmonicWarp "
            + source_string
            + " "
            + destination_string
            + " "
            + transfer_string
            + ";"
        )
    )[0]
    z_armonic_warp.maxResolution.set(512)
    z_armonic_warp.tetSize.set(tet_size)

    return z_armonic_warp


def bone_warp(source, destination, transfer_geos, tet_size=1):
    """Warp a source geometry to a destination geometry using Ziva's bone warp command.

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
    transfer_string = " ".join(transfer_list)

    z_bone_warp = pm.ls(
        mel.eval(
            "zBoneWarp " + source_string + " " + destination_string + " " + transfer_string + ";"
        )
    )[0]
    z_bone_warp.maxResolution.set(512)
    z_bone_warp.tetSize.set(tet_size)

    return z_bone_warp


def ziva_check_intersection(geo1, geo2):
    """Check for intersection between two geometry objects using Ziva's command.

    Args:
        geo1 (str): The name of the first geometry object.
        geo2 (str): The name of the second geometry object.

    Returns:
        A list of objects that intersect between the two geometry objects.
    """
    pm.select(geo1, geo2)
    mel.eval("ZivaSelectIntersections;")

    return pm.ls(sl=True, o=True)


# Rename
def ziva_rename_all():
    """Rename all Ziva nodes in the scene."""
    zva_cmds.rename_ziva_nodes()


# Mirror
def ziva_mirror(from_side="L_", to_side="R_", suffix="_GEO"):
    """Mirror a Ziva setup from one side of the body to the other.

    Args:
        from_side (str): The side of the body to copy from.
        to_side (str): The side of the body to copy to.
        suffix (str): The suffix to add to the end of the node names.
    """
    pm.select(pm.ls(from_side + "*" + suffix))
    z_obj = zva.Ziva()

    if pm.ls(sl=True):
        z_obj.retrieve_from_scene_selection()
    else:
        z_obj.retrieve_from_scene()

    z_obj.string_replace("^" + from_side, to_side)
    z_obj.build()


if __name__ == "__main__":
    ziva_rename_all()
    ziva_mirror("R_", "L_")

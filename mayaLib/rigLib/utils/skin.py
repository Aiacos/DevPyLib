__author__ = "Lorenzo Argentieri"

import os
from pathlib import Path

import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm
from ngSkinTools2 import api as ngst_api
from ngSkinTools2.api import InfluenceMappingConfig, VertexTransferMode
from ngSkinTools2.api import init_layers, Layers

from mayaLib.utility import bSkinSaver


def get_skincluster_object():
    """
    Selects and returns a list of objects with skin clusters.

    This function identifies all objects in the scene that have skin clusters,
    selects them, and returns a list of these objects.

    Returns:
        list: A list of PyNode objects that have skin clusters.
    """

    object_list = []
    skin_cluster_list = pm.ls(type="skinCluster")
    for skin_cluster in skin_cluster_list:
        obj_shape = pm.skinCluster(skin_cluster, q=True, geometry=True)
        obj = pm.listRelatives(obj_shape, p=True)[0]
        object_list.append(obj)

    return object_list


def select_skin_cluster_object():
    """
    Selects and returns a list of objects with skin clusters.

    This function identifies all objects in the scene that have skin clusters,
    selects them, and returns a list of these objects.

    Returns:
        list: A list of PyNode objects that have skin clusters.
    """

    object_list = get_skincluster_object()

    pm.select(object_list)
    return object_list


def disable_inherits_transform_on_skin_clusters():
    """
    Disable InheritsTransform on all skinCluster object
    :return:
    """
    obj_list = select_skin_cluster_object()
    for obj in obj_list:
        obj.inheritsTransform.set(0)


def copy_skin_weight_between_mesh(selection=pm.ls(sl=True)):
    """
    Copy skin weight to mirrored mesh
    """

    source_mesh = selection[0]
    destination_mesh = selection[1]

    source_skin_cluster = mel.eval("findRelatedSkinCluster " + source_mesh)
    destination_skin_cluster = mel.eval("findRelatedSkinCluster " + destination_mesh)

    pm.copySkinWeights(
        ss=source_skin_cluster,
        ds=destination_skin_cluster,
        mirrorMode="YZ",
        surfaceAssociation="closestPoint",
        influenceAssociation="closestJoint",
    )


def copy_bind(source, destination, sa="closestPoint", ia="closestJoint"):
    """
    Bind and Copy skincluster to destination GEO
    :param source: mesh str
    :param destination: mesh str
    :return:
    """
    # Get Shape and skin from Object
    skin_cluster = find_related_skin_cluster(source)
    if skin_cluster:
        skin = skin_cluster
    else:
        print("Missing source SkinCluster")

    # Get joint influence of the skin
    influnces = skin.getInfluence(q=True)  # influences is joint

    # Bind destination Mesh
    # pm.select(influnces[0])
    # pm.select(destination, add=True)
    # mel.eval('SmoothBindSkin;')
    pm.skinCluster(influnces[0], destination, dr=4.0)

    # copy skin wheights form source
    pm.select(source)
    pm.select(destination, add=True)
    pm.copySkinWeights(noMirror=True, surfaceAssociation=sa, influenceAssociation=ia)
    pm.select(cl=True)


def copy_bind_selected(selection_list):
    """
    Bind and Copy skincluster to destination GEO selected in maya.
    First selection is the source mesh, the others are the destination mesh.
    :param selection_list: list of str, maya selection
    :return: None
    """
    source = selection_list[0]
    destination_list = selection_list[1:]

    for destination in destination_list:
        copy_bind(source, destination, sa="rayCast")


def find_related_skin_cluster(geo):
    """
    Find the related skinCluster for the given geometry.

    Args:
        geo (str): The name of the geometry for which to find the skinCluster.

    Returns:
        PyNode or None: The found skinCluster node, or None if no skinCluster is found.
    """

    skincluster = mel.eval("findRelatedSkinCluster " + geo)
    if skincluster == "" or len(pm.ls(skincluster, type="skinCluster")) == 0:
        skincluster = pm.ls(pm.listHistory(geo), type="skinCluster")
        if len(skincluster) == 0:
            return None

    return pm.ls(skincluster)[0]


def mirror_skincluster_to_opposite_object(source_obj, destination_object):
    """
    Mirror Skincluster to the opposite Object
    Args:
        source_obj (string): Source Geo
        destination_object (string):  Destination Geo

    Returns:

    """

    geo_skincluster = find_related_skin_cluster(source_obj)
    r_geo_skincluster = find_related_skin_cluster(destination_object)

    pm.copySkinWeights(
        ss=geo_skincluster, ds=r_geo_skincluster, mirrorMode="YZ", mirrorInverse=True
    )


def mirror_all_skincluster_to_object(source_list, left_side="L_", r_side="R_"):
    """
    Mirror Skincluster to opposite Object
    Args:
        source_list (string[]): Objects list
        left_side (string): Left pattern
        r_side (string): Right Pattern

    Returns:

    """

    for geo in pm.ls(source_list):
        r_geo = pm.ls(str(geo.name()).replace("L_", "R_"))[-1]

        mirror_skincluster_to_opposite_object(geo, r_geo)


def save_skin_weights(
    geo_list,
    project_path=Path(cmds.file(q=True, sn=True)).parent.as_posix(),
    sw_ext=".swt",
    do_directory=True,
):
    """
    save weights for character geometry objects
    Args:
        geo_list (string[]): Objects list
        project_path (string): file path
        sw_ext (string): file extension
        do_directory (bool): create directory

    Returns:

    """

    # check folder
    directory = Path(project_path) / "weights" / "skinCluster"
    if not directory.exists():
        if do_directory:
            os.makedirs(str(directory))
        else:
            print("Path to save SkinCluster not found!")
            return

    if not isinstance(geo_list, list):
        geo_list = pm.ls(geo_list)

    for obj in geo_list:
        # weights file
        file = str(obj + sw_ext).replace(":", "__")
        wt_file = directory / file
        print("file to write: ", wt_file)
        # wt_file = os.path.join(project_path, skinWeightsDir, obj + sw_ext)

        # save skin weight file
        pm.select(obj)
        bSkinSaver.bSaveSkinValues(wt_file)


def load_skin_weights(
    geo_list,
    project_path=Path(cmds.file(q=True, sn=True)).parent.as_posix(),
    sw_ext=".swt",
):
    """
    load weights for character geometry objects
    Args:
        geo_list (string[]): Objects list
        project_path (string): file path
        sw_ext (string): file extension

    Returns:

    """
    # check folder
    directory = Path(project_path) / "weights" / "skinCluster"
    if not directory.exists():
        print("Path to load SkinCluster not found!")
        return

    geo_list = pm.ls(geo_list)

    for geo in geo_list:
        wt_file = str(geo.name()) + sw_ext
        fullpath_wt_file = directory / wt_file
        if fullpath_wt_file.exists():
            print("file to read: ", fullpath_wt_file)
            bSkinSaver.bLoadSkinValues(
                loadOnSelection=False, inputFile=fullpath_wt_file
            )


def ng_batch_export(geo_list, path):
    """
    Export skin weights for a list of geos to a directory.

    Args:
        geo_list (list of str): List of geometry names to export.
        path (str): Directory path to export to. Will create the directory if it doesn't exist.

    """
    full_path = Path(path)

    for geo in pm.ls(geo_list):
        file_name = str(geo.name()) + ".json"
        file_name = file_name.replace(":", "-")
        output_file_name = full_path / file_name

        skincluster = find_related_skin_cluster(geo)
        layers = init_layers(str(skincluster.name()))
        layer_base = layers.add("base weights")

        ngst_api.export_json(str(geo.name()), file=str(output_file_name))


def ng_batch_import(geo_list, path, influence_list=pm.ls("*_FS_jnt")):
    """
    Import skin weights for a list of geos from a directory.

    Args:
        geo_list (list of str): List of geometry names to import.
        path (str): Directory path to import from. Will create the directory if it doesn't exist.
        influence_list (list of str): List of influence names to bind to. Defaults to all joints ending in '_FS_jnt'.

    """
    full_path = Path(path)

    for geo in pm.ls(geo_list):
        pm.skinCluster(influence_list, geo, dr=4.0)

        file_name = str(geo.name()) + ".json"
        input_file_name = full_path / file_name

        skincluster = find_related_skin_cluster(geo)
        layers = init_layers(str(skincluster.name()))
        layer_base = layers.add("base weights")

        # configure how influences described in a file will be matched against the scene
        config = InfluenceMappingConfig()
        config.use_distance_matching = True
        config.use_name_matching = False

        # run the import
        ngst_api.import_json(
            str(geo.name()),
            file=str(input_file_name),
            vertex_transfer_mode=VertexTransferMode.vertexId,
            influences_mapping_config=config,
        )


if __name__ == "__main__":
    copy_skin_weight_between_mesh()
    print("Done!")

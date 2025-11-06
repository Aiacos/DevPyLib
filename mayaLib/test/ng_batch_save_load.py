"""ngSkinTools batch save/load test.

Example script for batch saving and loading skin weights
using ngSkinTools2 integration.
"""

from pathlib import Path

import pymel.core as pm
from maya import mel
from ngSkinTools2 import api as ngst_api
from ngSkinTools2.api import InfluenceMappingConfig, VertexTransferMode, init_layers

from mayaLib.rigLib.utils.util import list_objects_under_group


def findRelatedSkinCluster(geo):
    """Find related skincluster of geo
    :param geo: str
    :return: str.
    """
    skincluster = mel.eval('findRelatedSkinCluster ' + geo)
    if skincluster == '' or len(pm.ls(skincluster, type='skinCluster')) == 0:
        skincluster = pm.ls(pm.listHistory(geo), type='skinCluster')
        if len(skincluster) == 0:
            return None

    return pm.ls(skincluster)[0]


def ng_batch_export(geo_list, path):
    """Export ngSkinTools weights for multiple geometries.

    Args:
        geo_list: List of geometry objects to export weights from.
        path: Directory path to save weight files.
    """
    full_path = Path(path)

    for geo in pm.ls(geo_list):
        file_name = str(geo.name()) + '.json'
        output_file_name = full_path / file_name

        skincluster = findRelatedSkinCluster(geo)
        layers = init_layers(str(skincluster.name()))
        layers.add("base_weights_export")

        ngst_api.export_json(str(geo.name()), file=str(output_file_name))


def ng_batch_import(geo_list, path):
    """Import ngSkinTools weights for multiple geometries.

    Args:
        geo_list: List of geometry objects to import weights to.
        path: Directory path containing weight files.
    """
    full_path = Path(path)

    for geo in pm.ls(geo_list):
        file_name = str(geo.name()) + '.json'
        input_file_name = full_path / file_name

        skincluster = findRelatedSkinCluster(geo)
        layers = init_layers(str(skincluster.name()))
        layers.add("base_weights_import")

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
    export_dir = 'C:/Users/lorenzo.argentieri/Desktop/SamTeen_ng'
    geo_list = list_objects_under_group('x_geo_mdl_grp')
    # ng_batch_export(geo_list, export_dir)
    ng_batch_import(geo_list, export_dir)

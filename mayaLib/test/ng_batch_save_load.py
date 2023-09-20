from pathlib import Path

import pymel.core as pm
from maya import mel

import os

from ngSkinTools2 import api as ngst_api
from ngSkinTools2.api import init_layers, Layers
from ngSkinTools2.api import InfluenceMappingConfig, VertexTransferMode


def findRelatedSkinCluster(geo):
    """
    find related skincluster of geo
    :param geo: str
    :return: str
    """
    skincluster = mel.eval('findRelatedSkinCluster ' + geo)
    if skincluster == '' or len(pm.ls(skincluster, type='skinCluster')) == 0:
        skincluster = pm.ls(pm.listHistory(geo), type='skinCluster')
        if len(skincluster) == 0:
            return None

    return pm.ls(skincluster)[0]


def getAllObjectUnderGroup(group, type='mesh'):
    """
    Return all object of given type under group
    :param group: str, group name
    :param type: str, object type
    :return: object list
    """
    objList = None

    if type == 'mesh':
        objList = [pm.listRelatives(o, p=1)[0] for o in pm.listRelatives(group, ad=1, type=type)]

    if type == 'nurbsSurface':
        objList = [pm.listRelatives(o, p=1)[0] for o in pm.listRelatives(group, ad=1, type=type)]

    if type == 'transform':
        geoList = [pm.listRelatives(o, p=1)[0] for o in pm.listRelatives(group, ad=1, type='mesh')]
        objList = [o for o in pm.listRelatives(group, ad=1, type=type) if o not in geoList]

    objList = list(set(objList))
    objList.sort()

    return objList


def ng_batch_export(geo_list, path):
    full_path = Path(path)

    for geo in pm.ls(geo_list):
        file_name = str(geo.name()) + '.json'
        output_file_name = full_path / file_name

        skincluster = findRelatedSkinCluster(geo)
        layers = init_layers(str(skincluster.name()))
        layer_base = layers.add("base_weights_export")

        ngst_api.export_json(str(geo.name()), file=str(output_file_name))


def ng_batch_import(geo_list, path):
    full_path = Path(path)

    for geo in pm.ls(geo_list):
        file_name = str(geo.name()) + '.json'
        input_file_name = full_path / file_name

        skincluster = findRelatedSkinCluster(geo)
        layers = init_layers(str(skincluster.name()))
        layer_base = layers.add("base weights_import")

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


export_dir = 'C:/Users/lorenzo.argentieri/Desktop/SamTeen_ng'
geo_list = getAllObjectUnderGroup('x_geo_mdl_grp')
# ng_batch_export(geo_list, export_dir)
ng_batch_import(geo_list, export_dir)
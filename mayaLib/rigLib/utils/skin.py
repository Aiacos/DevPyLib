__author__ = 'Lorenzo Argentieri'

import os
from pathlib import Path

import maya.mel as mel
import maya.cmds as cmds
import pymel.core as pm

from mayaLib.utility import bSkinSaver

from ngSkinTools2 import api as ngst_api
from ngSkinTools2.api import init_layers, Layers
from ngSkinTools2.api import InfluenceMappingConfig, VertexTransferMode


def selectSkinClusterObject():
    """
    Select all skinCluster object
    :return: list(str), geo transform
    """
    objectList = []
    skinClusterList = pm.ls(type='skinCluster')
    for skinCluster in skinClusterList:
        objShape = pm.skinCluster(skinCluster, q=True, geometry=True)
        obj = pm.listRelatives(objShape, p=True)[0]
        objectList.append(obj)

    pm.select(objectList)
    return objectList


def disableInheritsTransformOnSkinClusters():
    """
    Disable InheritsTransform on all skinCluster object
    :return:
    """
    objList = selectSkinClusterObject()
    for obj in objList:
        obj.inheritsTransform.set(0)


def copySkinWeightBetweenMesh(selection=pm.ls(sl=True)):
    """
    Copy skin weight to mirrored mesh
    """

    sourceMesh = selection[0]
    destinationMesh = selection[1]

    sourceSkinCluster = mel.eval('findRelatedSkinCluster ' + sourceMesh)
    destinationSkinCluster = mel.eval('findRelatedSkinCluster ' + destinationMesh)

    pm.copySkinWeights(ss=sourceSkinCluster, ds=destinationSkinCluster, mirrorMode='YZ',
                       surfaceAssociation='closestPoint', influenceAssociation='closestJoint')


def copyBind(source, destination, sa='closestPoint', ia='closestJoint'):
    """
    Bind and Copy skincluster to destination GEO
    :param source: mesh str
    :param destination: mesh str
    :return: 
    """
    # Get Shape and skin from Object
    skinCluster = findRelatedSkinCluster(source)
    if skinCluster:
        skin = skinCluster
    else:
        print('Missing source SkinCluster')

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


def copyBindSelected(selectionList):
    """
    Copy SkinCluster (rayCast) from A to B,C,D...
    :param selectionList: list
    :return:
    """
    source = selectionList[0]
    destinationList = selectionList[1:]

    for destination in destinationList:
        copyBind(source, destination, sa='rayCast')


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

def mirror_skincluster_to_opposite_object(source_obj, destination_object):
    """
    Mirror Skincluster to the opposite Object
    Args:
        source_obj (string): Source Geo
        destination_object (string):  Destination Geo

    Returns:

    """

    geo_skincluster = findRelatedSkinCluster(source_obj)
    r_geo_skincluster = findRelatedSkinCluster(destination_object)

    pm.copySkinWeights(ss=geo_skincluster, ds=r_geo_skincluster, mirrorMode='YZ', mirrorInverse=True)

def mirror_all_skincluster_to_object(source_list, left_side='L_', r_side='R_'):
    """
    Mirror Skincluster to opposite Object
    Args:
        source_list (string[]): Objects list
        left_side (string): Left pattern
        r_side (string): Right Pattern

    Returns:

    """
    
    for geo in pm.ls(source_list):
        r_geo = pm.ls(str(geo.name()).replace('L_', 'R_'))[-1]

        mirror_skincluster_to_opposite_object(geo, r_geo)


def saveSkinWeights(geoList,
                    projectPath=str('/'.join(cmds.file(q=True, sn=True).split('/')[:-1]) + '/'),
                    swExt='.swt',
                    doDirectory=True):
    """
    save weights for character geometry objects
    """

    # check folder
    directory = Path(projectPath) / 'weights' / 'skinCluster'
    if not directory.exists():
        if doDirectory:
            os.makedirs(directory)
        else:
            print('Path to save SkinCluster not found!')
            return

    if not isinstance(geoList, list):
        geoList = pm.ls(geoList)

    for obj in geoList:
        # weights file
        file = str(obj + swExt).replace(':', '__')
        wtFile = directory / file
        print('file to write: ', wtFile)
        #wtFile = os.path.join(projectPath, skinWeightsDir, obj + swExt)

        # save skin weight file
        pm.select(obj)
        bSkinSaver.bSaveSkinValues(wtFile)


def loadSkinWeights(geoList,
                    projectPath=str('/'.join(cmds.file(q=True, sn=True).split('/')[:-1]) + '/'),
                    swExt='.swt'):
    """
    load skin weights for character geometry objects
    """

    # check folder
    directory = Path(projectPath) / 'weights' / 'skinCluster'
    if not directory.exists():
        print('Path to load SkinCluster not found!')
        return

    if not isinstance(geoList, list):
        geoList = pm.ls(geoList)

    # weights folders
    wtDir = directory
    wtFiles = os.listdir(wtDir)

    # load skin weights
    for wtFile in wtFiles:
        extRes = os.path.splitext(wtFile)

        # check extension format
        if not len(extRes) > 1:
            continue

        # check skin weight file
        if not extRes[1] == swExt:
            continue

        # check geometry list
        #if geoList:
        #    print('skip2')
        #    continue

        # check if objects exist
        if not pm.objExists(str(extRes[0]).replace('__', ':')):
            continue

        fullpathWtFile = str(os.path.join(wtDir, wtFile))
        print('file to read: ', fullpathWtFile)
        bSkinSaver.bLoadSkinValues(loadOnSelection=False, inputFile=fullpathWtFile)


def ng_batch_export(geo_list, path):
    full_path = Path(path)

    for geo in pm.ls(geo_list):
        file_name = str(geo.name()) + '.json'
        output_file_name = full_path / file_name

        skincluster = findRelatedSkinCluster(geo)
        layers = init_layers(str(skincluster.name()))
        layer_base = layers.add("base weights")

        ngst_api.export_json(str(geo.name()), file=str(output_file_name))


def ng_batch_import(geo_list, path, influence_list=pm.ls('*_FS_jnt')):
    full_path = Path(path)

    for geo in pm.ls(geo_list):
        pm.skinCluster(influence_list, geo, dr=4.0)

        file_name = str(geo.name()) + '.json'
        input_file_name = full_path / file_name

        skincluster = findRelatedSkinCluster(geo)
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
    copySkinWeightBetweenMesh()
    print('Done!')

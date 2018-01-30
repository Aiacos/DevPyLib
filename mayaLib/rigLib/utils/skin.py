__author__ = 'Lorenzo Argentieri'

import os
import pymel.core as pm
import maya.mel as mel
from mayaLib.utility import bSkinSaver


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
    shape = pm.ls(source)[0].getShape()
    skinCluster = pm.listConnections(shape + '.inMesh', destination=False)
    if len(skinCluster) > 0:
        skin = pm.PyNode(skinCluster[0])
    else:
        print 'Missing source SkinCluster'

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
    return skincluster


def saveSkinWeights(characterName, geoList,
                    projectPath=str(pm.workspace(q=True, dir=True, rd=True) + 'scenes/')+'rig/',
                    skinWeightsDir='weights/skinCluster', swExt='.swt',
                    doDirectory=True):
    """
    save weights for character geometry objects
    """
    # check folder
    directory = os.path.join(projectPath, characterName, skinWeightsDir)
    if not os.path.exists(directory):
        if doDirectory:
            os.makedirs(directory)
        else:
            print 'Path to save SkinCluster not found!'
            return

    if not isinstance(geoList, list):
        geoList = pm.ls(geoList)

    for obj in geoList:
        # weights file
        wtFile = os.path.join(projectPath, characterName, skinWeightsDir, obj + swExt)

        # save skin weight file
        pm.select(obj)
        bSkinSaver.bSaveSkinValues(wtFile)

def loadSkinWeights(characterName, geoList,
                    projectPath=str(pm.workspace(q=True, dir=True, rd=True) + 'scenes/')+'rig/',
                    skinWeightsDir='weights/skinCluster', swExt='.swt'):
    """
    load skin weights for character geometry objects
    """
    # check folder
    directory = os.path.join(projectPath, characterName, skinWeightsDir)
    if not os.path.exists(directory):
        print 'Path to load SkinCluster not found!'
        return

    if not isinstance(geoList, list):
        geoList = pm.ls(geoList)

    # weights folders
    wtDir = os.path.join(projectPath, characterName, skinWeightsDir)
    wtFiles = os.listdir(wtDir)

    # load skin weights
    for wtFile in wtFiles:
        extRes = os.path.splitext(wtFile)

        # check extension format
        if not extRes > 1:
            continue

        # check skin weight file
        if not extRes[1] == swExt:
            continue

        # check geometry list
        if geoList and not extRes[0] in geoList:
            continue

        # check if objects exist
        if not pm.objExists(extRes[0]):
            continue

        fullpathWtFile = os.path.join(wtDir, wtFile)
        bSkinSaver.bLoadSkinValues(loadOnSelection=False, inputFile=fullpathWtFile)


if __name__ == "__main__":
    copySkinWeightBetweenMesh()
    print 'Done!'

import pymel.core as pm
import maya.mel as mel


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
    #pm.select(influnces[0])
    #pm.select(destination, add=True)
    #mel.eval('SmoothBindSkin;')
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

if __name__ == "__main__":
    copySkinWeightBetweenMesh()
    print 'Done!'
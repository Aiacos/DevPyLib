import pymel.core as pm
import maya.mel as mel


# function to unlock and unhide attributes
def unlock_and_unhide_all(node):
    """
    unlock and unhide all transform attributes of selected node
    :param node: node to be affected
    """
    node.tx.set(l=0, k=1, cb=0)
    node.ty.set(l=0, k=1, cb=0)
    node.tz.set(l=0, k=1, cb=0)
    node.rx.set(l=0, k=1, cb=0)
    node.ry.set(l=0, k=1, cb=0)
    node.rz.set(l=0, k=1, cb=0)
    node.sx.set(l=0, k=1, cb=0)
    node.sy.set(l=0, k=1, cb=0)
    node.sz.set(l=0, k=1, cb=0)
    
def mergeDuplicatedVertex(geo, threshold=0.001, only2Vertex=False):
    pm.polyMergeVertex(geo, am=only2Vertex, ch=False, distance=threshold)
    
def fixFaceWithMoreThan4Sides(geo, query=True):
    pm.select(geo)
    if query:
        return pm.ls(mel.eval('polyCleanupArgList 4 { "0","2","0","0","1","0","0","0","0","1e-05","0","1e-05","0","1e-05","0","-1","0","0" };'))
    else:
        return pm.ls(mel.eval('polyCleanupArgList 4 { "0","1","0","0","1","0","0","0","0","1e-05","0","1e-05","0","1e-05","0","-1","0","0" };'))
    
def fixConcaveFaces(geo, query=True):
    pm.select(geo)
    if query:
        return pm.ls(mel.eval('polyCleanupArgList 4 { "0","2","0","0","0","1","0","0","0","1e-05","0","1e-05","0","1e-05","0","-1","0","0" };'))
    else:
        return pm.ls(mel.eval('polyCleanupArgList 4 { "0","1","0","0","0","1","0","0","0","1e-05","0","1e-05","0","1e-05","0","-1","0","0" };'))
    
def fixFaceWithHoles(geo, query=True):
    pm.select(geo)
    if query:
        return pm.ls(mel.eval('polyCleanupArgList 4 { "0","2","0","0","0","0","1","0","0","1e-05","0","1e-05","0","1e-05","0","-1","0","0" };'))
    else:
        return pm.ls(mel.eval('polyCleanupArgList 4 { "0","1","0","0","0","0","1","0","0","1e-05","0","1e-05","0","1e-05","0","-1","0","0" };'))

def fixNonPlanarFaces(geo, query=True):
    pm.select(geo)
    if query:
        return pm.ls(mel.eval('polyCleanupArgList 4 { "0","2","0","0","0","0","0","1","0","1e-05","0","1e-05","0","1e-05","0","-1","0","0" };'))
    else:
        return pm.ls(mel.eval('polyCleanupArgList 4 { "0","1","0","0","0","0","0","1","0","1e-05","0","1e-05","0","1e-05","0","-1","0","0" };'))
    
def removeLaminaFaces(geo, query=True):
    pm.select(geo)
    if query:
        return pm.ls(mel.eval('polyCleanupArgList 4 { "0","2","0","0","0","0","0","0","0","1e-05","0","1e-05","0","1e-05","0","-1","1","0" }; '))
    else:
        return pm.ls(mel.eval('polyCleanupArgList 4 { "0","1","0","0","0","0","0","0","0","1e-05","0","1e-05","0","1e-05","0","-1","1","0" }; '))
    
def removeNonmanifoldGeometry(geo, query=True):
    pm.select(geo)
    if query:
        return pm.ls(mel.eval('polyCleanupArgList 4 { "0","2","0","0","0","0","0","0","0","1e-05","0","1e-05","0","1e-05","0","1","0","0" };'))
    else:
        return pm.ls(mel.eval('polyCleanupArgList 4 { "0","1","0","0","0","0","0","0","0","1e-05","0","1e-05","0","1e-05","0","1","0","0" };'))
    
def removeEdgesWithZeroLenght(geo, query=True):    
    pm.select(geo)
    if query:
        return pm.ls(mel.eval('polyCleanupArgList 4 { "0","2","0","0","0","0","0","0","0","1e-05","1","1e-05","0","1e-05","0","-1","0","0" };'))
    else:
        return pm.ls(mel.eval('polyCleanupArgList 4 { "0","1","0","0","0","0","0","0","0","1e-05","1","1e-05","0","1e-05","0","-1","0","0" };'))
    
def removeFacesWithZeroGeometryArea(geo, query=True):
    pm.select(geo)
    if query:
        return pm.ls(mel.eval('polyCleanupArgList 4 { "0","2","0","0","0","0","0","0","1","1e-05","0","1e-05","0","1e-05","0","-1","0","0" };'))
    else:
        return pm.ls(mel.eval('polyCleanupArgList 4 { "0","1","0","0","0","0","0","0","1","1e-05","0","1e-05","0","1e-05","0","-1","0","0" };'))
    
def removeFacesWithZeroMapArea(geo, query=True):
    pm.select(geo)
    if query:
        return pm.ls(mel.eval('polyCleanupArgList 4 { "0","2","0","0","0","0","0","0","0","1e-05","0","1e-05","1","1e-05","0","-1","0","0" };'))
    else:
        return pm.ls(mel.eval('polyCleanupArgList 4 { "0","1","0","0","0","0","0","0","0","1e-05","0","1e-05","1","1e-05","0","-1","0","0" };'))
    
def removeInvalidComponents(geo, query=True):
    pm.select(geo)
    if query:
        return pm.ls(mel.eval('polyCleanupArgList 4 { "0","2","0","0","0","0","0","0","0","1e-05","0","1e-05","0","1e-05","0","-1","0","1" };'))
    else:
        return pm.ls(mel.eval('polyCleanupArgList 4 { "0","1","0","0","0","0","0","0","0","1e-05","0","1e-05","0","1e-05","0","-1","0","1" };'))
    
    
def fixGeoIssue(geo=pm.ls(sl=True)[0]):
    unlock_and_unhide_all(geo)
    
    mergeDuplicatedVertex(geo)
    
    fixFaceWithMoreThan4Sides(geo)
    fixConcaveFaces(geo)
    fixFaceWithHoles(geo)
    fixNonPlanarFaces(geo)
    removeLaminaFaces(geo)
    removeNonmanifoldGeometry(geo)
    removeEdgesWithZeroLenght(geo)
    removeFacesWithZeroGeometryArea(geo)
    removeFacesWithZeroMapArea(geo)
    removeInvalidComponents(geo)

    pm.makeIdentity(geo, apply=True, t=1, r=1, s=1, n=0)
    pm.delete(geo, ch=1)
    pm.xform(geo, ws=True, pivots=[0,0,0])
    
if __name__ == "__main__":
    geoList = pm.ls(sl=True)
    for geo in geoList:
        print geo.name()
        print fixGeoIssue(geo)
    
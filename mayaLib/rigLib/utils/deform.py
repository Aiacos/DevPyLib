__author__ = 'Lorenzo Argentieri'

import pymel.core as pm
from maya import mel


def wrapDeformer(wrappedObjs, wrapperObj):
    """
    Apply Wrap Deformer on selected mesh
    :param wrappedObjs: list(str)
    :param wrapperObj: str
    :return: deformer node
    """
    pm.select(wrappedObjs)
    pm.select(wrapperObj, add=1)
    #deformerNode = pm.deformer(type='wrap')
    deformerNode = mel.eval('doWrapArgList "7" { "1","0","1", "2", "1", "1", "0", "0" }')
    return deformerNode

def deltaMushDeformer(geo):
    """
    Apply Mush Deformer
    :param geo: str
    :return: deformer node
    """
    deformerNode = pm.deltaMush(geo, smoothingIterations=25)[0]
    return deformerNode

def shrinkWrapDeformer(wrappedObj, wrapperObj):
    """
    Apply ShrinkWrap Deformer on selected mesh
    :param wrappedObjs: str
    :param wrapperObj: str
    :return: deformer node
    """
    shrinkWrapNode = pm.deformer(wrappedObj, type='shrinkWrap')[0]
    pm.PyNode(wrapperObj).worldMesh[0] >> shrinkWrapNode.targetGeom
    shrinkWrapNode.closestIfNoIntersection.set(True)
    return shrinkWrapNode

if __name__ == "__main__":
    pass
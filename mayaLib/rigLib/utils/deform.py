__author__ = 'Lorenzo Argentieri'

import pymel.core as pm
from maya import mel


def blendShapeDeformer(base, blendshapeList, nodeName, defaultValue=[1, ], frontOfChain=False):
    """
    Apply BlendShape on selected mesh or curve
    :param base: str
    :param blendshapeList: list(str)
    :param frontOfChain: bool
    :return: deformer node
    """

    w = (0, float(defaultValue[0]))
    if isinstance(blendshapeList, list):
        for i, df in zip(list(range(0, len(blendshapeList))), defaultValue):
            w = (i, float(df))

    blendshapeNode = pm.blendShape(blendshapeList, base, n=nodeName, frontOfChain=frontOfChain,
                                   weight=w)

    return blendshapeNode


def wrapDeformer(wrappedObjs, wrapperObj):
    """
    Apply Wrap Deformer on selected mesh
    :param wrappedObjs: list(str)
    :param wrapperObj: str
    :return: deformer node
    """
    pm.select(wrappedObjs)
    pm.select(wrapperObj, add=1)
    # deformerNode = pm.deformer(type='wrap')
    deformerNode = mel.eval('doWrapArgList "7" { "1","0","1", "2", "1", "1", "0", "0" }')
    return pm.ls(deformerNode)[0]


def deltaMushDeformer(geo, smoothingIterations=10, smoothingStep=0.5):
    """
    Apply Mush Deformer
    :param geo: str
    :param smoothingIterations: float
    :param smoothingStep: float
    :return: deformer node
    """
    deformerNode = pm.deltaMush(geo, smoothingIterations=smoothingIterations, smoothingStep=smoothingStep)[0]
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


def cMuscleSystemDeformer(obj, relativeSticky=True):
    """
    Apply cMuscleSystem Deformer on selected mesh
    :param obj: str
    :return: deformer node
    """
    deformerNode = None

    if relativeSticky:
        pm.select(obj)
        d = mel.eval('cMuscle_makeMuscleSystem(1);')
        deformerNode = pm.ls(d)[0]
    else:
        deformerNode = pm.deformer(obj, type='cMuscleSystem')[0]

    return deformerNode


def cMuscleConnectMuscle(muscleMainObj, muscleObjList):
    """
    Connect Muscle to Mesh
    :param muscleMainObj: str
    :param muscleObjList: list(str)
    :return: None
    """
    pm.select(muscleObjList)
    pm.select(muscleMainObj, add=1)
    mel.eval('cMuscle_connectToSystem();')


def softModDeformer(vertex):
    deformerNode = pm.softMod(vertex)[0]
    deformerNode.falloffMasking.set(0)

    return deformerNode


def meshCollision(deformer, deformed):
    """
    Mesh Collision Solver
    :param deformer: deforming mesh
    :param deformed: deformed mesh
    :return: deformer node
    """
    deformer = pm.ls(deformer)[0]
    deformed = pm.ls(deformed)[0]

    pm.select(deformer)
    pm.select(deformed, add=1)
    mel.eval('collisionDeformer()')

    deformerNode = pm.listConnections(deformer.worldMesh[0], c=True, p=False)[-1][1]

    pm.select(cl=True)

    return deformerNode


if __name__ == "__main__":
    pass

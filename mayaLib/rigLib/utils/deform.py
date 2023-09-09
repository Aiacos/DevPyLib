__author__ = 'Lorenzo Argentieri'

import pymel.core as pm
from maya import mel

import maya.cmds as cmds
import maya.internal.nodes.proximitywrap.node_interface as node_interface


def createProximityWrap(source, target_list):
    """
    Creates a proximity with the given source and target transforms.
    Args:
        source (pm.nodetypes.Transform): Transform with skinned mesh that will drive given target.
        target (pm.nodetypes.Transform): Transform with mesh shape that will be driven by given source.
    Returns:
        (pm.nodetypes.ProximityWrap): Proximity wrap node created.
    """
    # implementing with maya.cmds since PyMel raises the following warning for every attribute set.
    # Warning: pymel.core.general : Could not create desired MFn. Defaulting to MFnDependencyNode.
    target_names_list = [geo.name() for geo in pm.ls(target_list)]
    deformer = cmds.deformer(target_names_list, type='proximityWrap', name=target_list[0].name(stripNamespace=True) + '_pWrap')[0]

    proximity_interface = node_interface.NodeInterface(deformer)
    proximity_interface.addDriver(source.getShapes()[-1].name())  # last shape should be the deformed shape

    return deformer

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


def tensionMap(obj):
    obj = pm.ls(obj)[-1]
    shape = obj.getShape()
    shapeOrig = pm.ls(str(shape.name()) + 'Orig')[-1]
    shape_input = pm.listConnections(shape.inMesh, source=True, destination=False, plugs=True)[-1]

    # Create Tension map node
    tensionmap_node = pm.createNode('tensionMap')

    # Connections
    pm.connectAttr(shapeOrig.worldMesh[0], tensionmap_node.orig, f=True)
    pm.connectAttr(shape_input, tensionmap_node.deform, f=True)
    pm.connectAttr(tensionmap_node.out, shape.inMesh, f=True)

    return tensionmap_node


if __name__ == "__main__":
    pass

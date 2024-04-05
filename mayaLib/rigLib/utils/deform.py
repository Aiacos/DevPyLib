__author__ = 'Lorenzo Argentieri'

import pymel.core as pm
from maya import mel

import maya.cmds as cmds
import maya.internal.nodes.proximitywrap.node_interface as node_interface


def remove_shapeDeformed():
    shapeDeformed_node_list = pm.ls('*ShapeDeformed', '*:*ShapeDeformed')

    for shape in shapeDeformed_node_list:
        shape_old_name = str(shape.name())
        new_name = shape_old_name.replace('Deformed', '')
        pm.rename(shape, new_name)

def reorder_deformer(node, geo_list, search_type='skincluster'):
    for geo in geo_list:
        deformer_history_list = pm.listHistory(geo, type='ffd')
        pm.reorderDeformers(deformer_history_list[-1], node, geo)

def paintDeformerWeights(channel, vtx_list, value, smoothIteration=1):
    channel = 'inputAttract'
    mel.eval('artSetToolAndSelectAttr("artAttrCtx", "ffd.ffd1.weights");')
    pm.select(vtx_list)

    # set value
    mel.eval('artAttrCtx -e -value ' + str(value) + ' `currentCtx`;')

    # replace
    mel.eval('artAttrPaintOperation artAttrCtx Replace;')
    mel.eval('artAttrCtx -e -clear `currentCtx`;')

    # smooth
    for i in range(0, smoothIteration):
        mel.eval('artAttrPaintOperation artAttrCtx Smooth;')
        mel.eval('artAttrCtx -e -clear `currentCtx`;')

    pm.select(cl=True)


class PaintDeformer(object):
    def __init__(self, geo, channel):
        pm.select(geo)
        mel.eval('artSetToolAndSelectAttr("artAttrCtx", "' + channel + '");')
        mel.eval('artAttrInitPaintableAttr;')
        mel.eval('artAttrPaintMenu( "artAttrListPopupMenu" );')
        mel.eval('artAttrValues artAttrContext;')
        mel.eval('toolPropertyShow;')
        mel.eval('dR_contextChanged;')
        mel.eval('currentCtx;')

        #mel.eval('changeSelectMode -component;')

    def select(self, vtx_list):
        pm.select(vtx_list)

    def select_all(self):
        mel.eval('SelectAll;')

    def invert_selection(self):
        mel.eval('invertSelection;')

    def grow_selection(self, growSelection):
        for i in range(growSelection):
            mel.eval('select `ls -sl`;PolySelectTraverse 1;select `ls -sl`;')

    def replace(self, vtx_list, value):
        pm.select(vtx_list)
        mel.eval('artAttrCtx - e - value ' + str(value) + ' `currentCtx`;')

        mel.eval('artAttrPaintOperation artAttrCtx Replace;')
        mel.eval('artAttrCtx -e -clear `currentCtx`;')

    def smooth(self, smoothIteration=1):
        for i in range(0, smoothIteration):
            mel.eval('artAttrPaintOperation artAttrCtx Smooth;')
            mel.eval('artAttrCtx -e -clear `currentCtx`;')

    def __del__(self):
        mel.eval('setToolTo $gMove;')
        pm.select(cl=True)

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
    deformer = cmds.deformer(target_names_list, type='proximityWrap', name=pm.ls(target_list)[0].name(stripNamespace=True) + '_pWrap')[0]

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

def save_deformer_weights():
    pass

def load_deformer_weights(geoList, projectPath=str('/'.join(cmds.file(q=True, sn=True).split('/')[:-1]) + '/'), skinWeightsDir='weights/deformer'):
    """
    load deformer weights for character geometry objects
    """
    # check folder
    directory = os.path.join(projectPath, skinWeightsDir)
    if not os.path.exists(directory):
        print('Path to load Deformer Weights not found!')
        return

    if not isinstance(geoList, list):
        geoList = pm.ls(geoList)

    # weights folders
    wtDir = os.path.join(projectPath, skinWeightsDir)
    wtFiles = os.listdir(wtDir)

    # load skin weights
    for wtFile in wtFiles:
        extRes = os.path.splitext(wtFile)

        # check extension format
        if not len(extRes) > 1:
            continue

        # check skin weight file
        if not extRes[1] == '.json':
            continue

        # check geometry list
        if geoList and not extRes[0] in geoList:
            continue

        # check if objects exist
        if not pm.objExists(extRes[0]):
            continue

        fullpathWtFile = os.path.join(wtDir, wtFile)

if __name__ == "__main__":
    pass

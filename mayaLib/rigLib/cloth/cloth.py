import maya.mel as mel
import pymel.core as pm


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
    if type == 'transform':
        geoList = [pm.listRelatives(o, p=1)[0] for o in pm.listRelatives(group, ad=1, type='mesh')]
        objList = [o for o in pm.listRelatives(group, ad=1, type=type) if o not in geoList]
    objList = list(set(objList))
    objList.sort()
    return objList


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


def clothPaintInputAttract(clothNode, vtxList, value, smoothIteration=1):
    channel = 'inputAttract'
    clothOutput = pm.listConnections(clothNode.outputMesh, sh=True)[0]

    mel.eval('setNClothMapType("' + channel + '","' + clothOutput + '",1); artAttrNClothToolScript 4 ' + channel + ';')
    pm.select(vtxList)

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


class ClothFeather:
    def __init__(self, geo_list, collision_geo_list):
        self.cloth_system_grp = pm.group(n='ClothSystem_grp', em=True)

        # tmp rename
        for geo in geo_list:
            name = str(geo.name()) + '_tmpgeo'
            pm.rename(geo, name)

        self.clothShapeList, self.sim_geo_list, self.nucleus = self.createNCloth(geo_list)

        # setup Nucleus
        pm.rename(self.nucleus, 'clothSystem_nucleus')
        pm.parent(self.nucleus, self.cloth_system_grp)

        self.nucleus.enable.set(0)

        # setup Colliders
        # self.collisionSetup(collision_geo_list)

        for geo, clothShape in zip(geo_list, self.clothShapeList):
            self.connect_inputMesh_restShape(geo, clothShape)

        # remove tmp rename
        for geo in geo_list:
            name = str(geo.name()).replace('_tmpgeo', '')
            pm.rename(geo, name)

        sim_geo_list = getAllObjectUnderGroup(pm.ls('clothOut_grp')[-1])
        deltaMushDeformer(sim_geo_list)

    def paintQuills(self, p_quill=0.75, p_feather=0.1):
        for clothShape in self.clothShapeList:
            print('Paint: ', clothShape)
            if 'Primaries' in str(clothShape.name()):
                self.paintInputAttract(clothShape, quill=p_quill, feather=p_feather)
            elif 'Secondaries' in str(clothShape.name()):
                self.paintInputAttract(clothShape, quill=0.75, feather=0.1)
            else:
                self.paintInputAttract(clothShape, quill=0.75, feather=0.45)

    def createNCloth(self, featherList):
        clothShapeList = []
        sim_geo_list = []
        clothSimGrp = pm.group(n='clothSim_grp', p=self.cloth_system_grp, em=True)
        clothOutGrp = pm.group(n='clothOut_grp', p=self.cloth_system_grp, em=True)

        for geo in featherList:
            geo_name = str(geo.name()).replace('_tmpgeo', '_SIM')
            out_name = str(geo.name()).replace('_tmpgeo', '_out_SIM_GEO')
            sim_geo = pm.duplicate(geo, n=geo_name)[0]
            out_geo = pm.duplicate(geo, n=out_name)[0]
            pm.parent(sim_geo, clothSimGrp)
            pm.parent(out_geo, clothOutGrp)
            outBlendshape = blendShapeDeformer(out_geo, [sim_geo], geo_name + '_BS')[-1]
            outBlendshape.origin.set(0)

            pm.select(sim_geo)
            clothShape = pm.ls(mel.eval('createNCloth 0;'))[-1]
            clothShape.isDynamic.set(0)

            # clothSimGeo = pm.listConnections(cloth.outputMesh)[0]
            pm.rename(clothShape.getParent(), str(sim_geo.name()) + '_nCloth')
            pm.parent(clothShape.getParent(), sim_geo)

            clothShape.selfCollide.set(0)

            clothShapeList.append(clothShape)
            sim_geo_list.append(sim_geo)

        nucleus = pm.ls('nucleus1')[-1]  # pm.listConnections(clothShape, type='nucleus')[0]

        return clothShapeList, sim_geo_list, nucleus

    def connect_inputMesh_restShape(self, geo, clothShape):
        """
        connect inputmeshShape and restShape
        """
        bs_name = str(geo.name()).replace('_tmpgeo', '_SIM_BS')
        print(bs_name)
        bs_node = pm.ls(bs_name)[-1]

        pm.connectAttr(geo.getShape().worldMesh[0], clothShape.inputMesh, f=True)
        pm.connectAttr(geo.getShape().worldMesh[0], clothShape.restShapeMesh, f=True)

        intermediate_geo = pm.listConnections(clothShape.outputMesh, d=True, sh=True)[-1]
        pm.connectAttr(intermediate_geo.outMesh, bs_node.input[0].inputGeometry, f=True)
        pm.connectAttr(intermediate_geo.outMesh,
                       bs_node.inputTarget[0].inputTargetGroup[0].inputTargetItem[6000].inputGeomTarget, f=True)

    def createCollision(self, geo):
        # pm.select(geo)
        # collisionShapeList = pm.ls(mel.eval('makeCollideNCloth;'))

        timerNode = pm.ls('time1')[0]
        colliderNode = pm.createNode('nRigid', n=geo.name() + '_collider' + '_Shape')
        pm.rename(colliderNode.getParent(), geo.name() + '_collider')

        pm.connectAttr(timerNode.outTime, colliderNode.currentTime, f=True)
        pm.connectAttr(geo.getShape().worldMesh[0], colliderNode.inputMesh, f=True)

        pm.connectAttr(colliderNode.currentState, self.nucleus.inputPassive[0], f=True)
        pm.connectAttr(colliderNode.startState, self.nucleus.inputPassiveStart[0], f=True)

        pm.parent(colliderNode, geo)

        colliderNode.thickness.set(0.005)
        # colliderNode.trappedCheck.set(1)
        # colliderNode.pushOut.set(0)
        # colliderNode.pushOutRadius.set(0.5)

        return colliderNode

    def collisionSetup(self, collision_geo_list):
        for collisionGeo in collision_geo_list:
            self.createCollision(collisionGeo)

    def paintInputAttract(self, clothNode, quill=1, feather=0.35, growSelection=0):
        face_list = [3, 4, 11, 12, 19, 20, 27, 28, 35, 36, 43, 44, 51, 52, 59, 60, 64, 65, 69,
                     70]  # [3, 10, 17, 24, 31, 38, 45, 49, 53]#

        geo = pm.listConnections(clothNode.inputMesh, s=True)[0]
        print(('PAINT: ', geo))

        # Feather
        pm.select(geo)
        mel.eval('changeSelectMode -component;')
        mel.eval('SelectAll;')
        vtxList = pm.ls(sl=True)
        clothPaintInputAttract(clothNode, vtxList, feather, smoothIteration=0)

        # Quill
        self.selectVtx(geo, face_list)
        vtxList = pm.ls(sl=True)
        clothPaintInputAttract(clothNode, vtxList, quill, smoothIteration=0)

        mel.eval('changeSelectMode -object;')

    def updateSettings(self):
        # setup nCloth
        for clothShape in self.clothShapeList:
            # Collision
            clothShape.thickness.set(0.1)
            clothShape.selfCollideWidthScale.set(0)

            # Dynamic Properties
            # clothShape.stretchResistance.set(10)
            # clothShape.bendResistance.set(5)
            clothShape.inputMeshAttract.set(1)
            clothShape.inputAttractMethod.set(0)

            # Quality Settings
            clothShape.collideLastThreshold.set(0.2)
            clothShape.sortLinks.set(1)

            # clothShape.evaluationOrder.set(1)
            clothShape.bendSolver.set(2)

            clothShape.trappedCheck.set(1)
            clothShape.selfTrappedCheck.set(1)

            clothShape.pushOut.set(0.05)
            clothShape.pushOutRadius.set(1)

            clothShape.isDynamic.set(1)

        self.nucleus.enable.set(1)

    def selectVtx(self, geo, vertices):
        vertex_select_list = []
        for vertex in vertices:
            try:
                vertex_select_list.append("{0}.vtx[{1}]".format(geo, vertex))
            except:
                print('Skip vtx: ', vertex)

        pm.select(vertex_select_list)


def wrap_components(feather_geo_list):
    for geo in feather_geo_list:
        geo_name = str(geo.name())
        print(geo_name)

        # Wrap Nurbs Plane
        nurbs_plane = pm.ls(geo_name + '_NURBS')[-1]
        print('-------- ', nurbs_plane)

        # Nurbs plane wrap Quill

        # Nurbs plane wraps barbs


#### main
# wing_model_grp = pm.ls('*:prp_main_wings_default', 'prp_main_wings_default')[-1]
# if pm.objExists('rig_root_grp'):
#    pm.parent(wing_model_grp, 'geometry_grp')

feather_grp = pm.ls('*:GRP_feathers', 'GRP_feathers')[-1]
feather_geo_list = getAllObjectUnderGroup(feather_grp)
collision_geo_list = pm.ls('model:MSH_skin', 'MSH_skin')

cSolver = ClothFeather(feather_geo_list, collision_geo_list)
cSolver.updateSettings()
# pm.evalDeferred("cSolver.paintQuills(p_quill=0.75, p_feather=0.1)")

# pm.delete('rig_model_grp')

# wrap_components(feather_geo_list)
import maya.mel as mel
import pymel.core as pm

from mayaLib.rigLib.utils import dynamic

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


class ClothMuscle:
    def __init__(self, geo_list, collision_geo_list):
        self.cloth_system_grp = pm.group(n='ClothSystem_grp', em=True)
        self.cloth_geo_grp = pm.group(n='cloth_geo_grp', em=True, p=self.cloth_system_grp)

        self.cloth_data_list, self.nucleus = self.createNCloth(geo_list)

        # setup Nucleus
        pm.rename(self.nucleus, 'clothSystem_nucleus')
        pm.parent(self.nucleus, self.cloth_system_grp)

        # self.nucleus.enable.set(0)

        # setup Colliders
        collision_data_list = self.collisionSetup(collision_geo_list)

        # sim_geo_list = util.getAllObjectUnderGroup(pm.ls('clothOut_grp')[-1])
        # deform.deltaMushDeformer(sim_geo_list)

    def createNCloth(self, geo_list):
        cloth_data_list = []
        nucleus = None

        for geo in geo_list:
            cloth_geo, geo_cloth_shape, clothShape, nucleus = dynamic.setup_nCloth(geo, rest_mesh=geo)
            pm.parent(cloth_geo, self.cloth_geo_grp)
            cloth_data_list.append([geo, cloth_geo, geo_cloth_shape, clothShape])

        return cloth_data_list, nucleus

    def collisionSetup(self, collision_geo_list):
        collision_data_list = []

        for geo in collision_geo_list:
            collider = dynamic.create_collider(geo, self.nucleus)

            collision_data_list.append([geo, collider])

        return collision_data_list

    def paintInputAttract(self, clothNode, growSelection=5):
        geo = pm.listConnections(clothNode.inputMesh, s=True)[0]
        print(('PAINT: ', geo))

        # paint middle
        pm.select(geo)
        mel.eval('changeSelectMode -component;')
        mel.eval('SelectAll;')
        mel.eval('polySelectConstraint -pp 3;')
        edges = pm.ls(sl=True)
        # mel.eval('polySelectContraint -dis;')

        for i in range(growSelection):
            mel.eval('select `ls -sl`;PolySelectTraverse 1;select `ls -sl`;')

        mel.eval('invertSelection;')

        vtxList = pm.ls(sl=True)

        dynamic.clothPaintInputAttract(clothNode, vtxList, 0.4, smoothIteration=3)

    def updateSettings(self):
        # setup nCloth
        for data in self.cloth_data_list:
            cloth = data[0]
            # Set Default Value
            # Collision
            cloth.thickness.set(0.01)
            cloth.selfCollideWidthScale.set(1)

            # Dynamic Properties
            cloth.stretchResistance.set(10)
            cloth.bendResistance.set(5)
            cloth.inputMeshAttract.set(1)
            cloth.inputAttractMethod.set(0)

            # Pressure
            cloth.pressureMethod.set(1)

            # Collision
            cloth.thickness.set(0.01)
            cloth.selfCollideWidthScale.set(1)

            # Quality Settings
            cloth.collideLastThreshold.set(0.2)
            cloth.sortLinks.set(1)

            # clothShape.evaluationOrder.set(1)
            cloth.bendSolver.set(2)

            # trap checked
            cloth.trappedCheck.set(1)
            cloth.selfTrappedCheck.set(1)

            cloth.pushOut.set(0.05)
            cloth.pushOutRadius.set(1)

            cloth.isDynamic.set(1)

        self.nucleus.enable.set(1)

    def selectVtx(self, geo, vertices):
        vertex_select_list = []
        for vertex in vertices:
            try:
                vertex_select_list.append("{0}.vtx[{1}]".format(geo, vertex))
            except:
                print('Skip vtx: ', vertex)

        pm.select(vertex_select_list)

    def runSolve(self):
        # setup nCloth
        for clothShape in self.clothShapeList:
            # Collisions
            clothShape.collisionFlag.set(3)
            clothShape.selfCollisionFlag.set(4)
            clothShape.thickness.set(0.001)

            # Dynamic Properties
            clothShape.inputMeshAttract.set(1)

            # Paint Dynmaic
            self.paintInputAttract(clothShape)

            # Pressure
            # setPressure(clothShape)

            # Quality Settings
            clothShape.collideLastThreshold.set(1)

            clothShape.evaluationOrder.set(1)
            clothShape.bendSolver.set(2)

            clothShape.trappedCheck.set(1)
            clothShape.selfTrappedCheck.set(1)

            clothShape.pushOut.set(0.05)
            clothShape.pushOutRadius.set(1)

        # for muscleGeo in muscleList:
        #    deltaMushSetup(muscleGeo)

        # setupCollider
        # collisionSetup('skeleton_grp')

        self.nucleus.enable.set(1)


if __name__ == "__main__":
    # mel.eval('file -f -options "v=0;"  -ignoreVersion  -typ "mayaAscii" -o "/Users/lorenzoargentieri/Qsync/Project/Warewolf/scenes/00_model/anatomy_reference.ma";addRecentFile("/Users/lorenzoargentieri/Qsync/Project/Warewolf/scenes/00_model/anatomy_reference.ma", "mayaAscii");')

    cSolver = ClothMuscle()
    # cSolver.runSolve()

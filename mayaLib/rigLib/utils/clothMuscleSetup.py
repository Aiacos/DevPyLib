import pymel.core as pm
import maya.mel as mel


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
    
    
class ClothMuscle:
    def __init__(self):
        try:
            self.muscleGrp = pm.ls('muscle_GRP')[0]
            self.skeletonGrp = pm.ls('skeleton_GRP')[0]
            #self.skinGrp = pm.ls('skin_GRP')[0]
        except:
            pass
        
        self.muscleSystemGrp = pm.group(n='muscleSystem_GRP', em=True)
        pm.parent(self.muscleGrp, self.muscleSystemGrp)
        pm.parent(self.skeletonGrp, self.muscleSystemGrp)
            
        muscleList = getAllObjectUnderGroup(self.muscleGrp)
        self.clothShapeList, self.nucleus = self.createNCloth(muscleList)
    
        # setup Nucleus
        pm.rename(self.nucleus, 'muscleSystem_nucleus')
        pm.parent(self.nucleus, self.muscleSystemGrp)
        
        self.nucleus.enable.set(1)
        self.nucleus.spaceScale.set(0.01)
        self.nucleus.subSteps.set(12)
        
        # setup Colliders
        self.collisionSetup(self.skeletonGrp)
        
        for clothShape in self.clothShapeList:
            self.paintInputAttract(clothShape)
            
             
    def createNCloth(self, muscleList):
        # duplicate muscle (musSim)
        muscleSim = pm.duplicate(muscleList)
        muscleSimGrp = pm.group(muscleSim, n='muscleSim_GRP', p=self.muscleSystemGrp)
        
        for mus in muscleSim:
            pm.rename(mus, str(mus.name()).replace('_GEO1', '_SIM'))
        
        
        pm.select(muscleSim)
        clothShapeList = pm.ls(mel.eval('createNCloth 0;'))
        nucleus = pm.listConnections(clothShapeList[0], type='nucleus')[0]
        
        for cloth in clothShapeList:
            muscleSimGeo = pm.listConnections(cloth.outputMesh)[0]
            pm.rename(cloth.getParent(), str(muscleSimGeo.name()) + '_nCloth')
            pm.parent(cloth.getParent(), muscleSimGeo)
            
            # connect inputmeshShape and restShape
            print('###############################################')
            print(str(muscleSimGeo.name()).replace('_SIM', '_GEO'))
            muscleGeo = pm.ls(str(muscleSimGeo.name()).replace('_SIM', '_GEO'))[0]
            pm.connectAttr(muscleGeo.getShape().worldMesh[0], cloth.inputMesh, f=True)
            pm.connectAttr(muscleGeo.getShape().worldMesh[0], cloth.restShapeMesh, f=True)
               
            # Set Default Value
            # Collision
            cloth.thickness.set(0.01)
            cloth.selfCollideWidthScale.set(1)
            
            # Dynamic Properties
            cloth.stretchResistance.set(10)
            cloth.bendResistance.set(5)
            cloth.inputMeshAttract.set(1)
            cloth.inputAttractMethod.set(1)
            
            # Pressure
            cloth.pressureMethod.set(1)
            
            # trap checked
            
        return clothShapeList, nucleus
    
    def createCollision(self, geo):
        #pm.select(geo)
        #collisionShapeList = pm.ls(mel.eval('makeCollideNCloth;'))
        
        timerNode = pm.ls('time1')[0]
        colliderNode = pm.createNode('nRigid', n=geo.name() + '_collider' + '_Shape')
        pm.rename(colliderNode.getParent(), geo.name() + '_collider')
        
        pm.connectAttr(timerNode.outTime, colliderNode.currentTime, f=True)
        pm.connectAttr(geo.getShape().worldMesh[0], colliderNode.inputMesh, f=True)
        
        pm.connectAttr(colliderNode.currentState, self.nucleus.inputPassive[0], f=True)
        pm.connectAttr(colliderNode.startState, self.nucleus.inputPassiveStart[0], f=True)

        pm.parent(colliderNode, geo)
        
        colliderNode.thickness.set(0.005)
        #colliderNode.trappedCheck.set(1)
        #colliderNode.pushOut.set(0)
        #colliderNode.pushOutRadius.set(0.5)
            
        return colliderNode
    
    def collisionSetup(self, collisionGrp):
        collisionGrp = pm.ls(collisionGrp)[0]
        collisionGeoList = getAllObjectUnderGroup(collisionGrp)
        
        for collisionGeo in collisionGeoList:
            self.createCollision(collisionGeo)
        
    def paintInputAttract(self, clothNode, growSelection=5):
        geo = pm.listConnections(clothNode.inputMesh, s=True)[0]
        print('PAINT: ', geo)

        # paint middle
        pm.select(geo)
        mel.eval('changeSelectMode -component;')
        mel.eval('SelectAll;')
        mel.eval('polySelectConstraint -pp 3;')
        edges = pm.ls(sl=True)
        #mel.eval('polySelectContraint -dis;')
        
        for i in range(growSelection):
            mel.eval('select `ls -sl`;PolySelectTraverse 1;select `ls -sl`;')        
            
        mel.eval('invertSelection;')
        
        vtxList = pm.ls(sl=True)
        
        clothPaintInputAttract(clothNode, vtxList, 0.4, smoothIteration=3)
        
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
            #setPressure(clothShape)
            
            # Quality Settings
            clothShape.collideLastThreshold.set(1)
            
            clothShape.evaluationOrder.set(1)
            clothShape.bendSolver.set(2)
            
            clothShape.trappedCheck.set(1)
            clothShape.selfTrappedCheck.set(1)
            
            clothShape.pushOut.set(0.05)
            clothShape.pushOutRadius.set(1)
            
        #for muscleGeo in muscleList:
        #    deltaMushSetup(muscleGeo)
            
        # setupCollider
        #collisionSetup('skeleton_grp')
        
        self.nucleus.enable.set(1)

if __name__ == "__main__":    
    #mel.eval('file -f -options "v=0;"  -ignoreVersion  -typ "mayaAscii" -o "/Users/lorenzoargentieri/Qsync/Project/Warewolf/scenes/00_model/anatomy_reference.ma";addRecentFile("/Users/lorenzoargentieri/Qsync/Project/Warewolf/scenes/00_model/anatomy_reference.ma", "mayaAscii");')
    
    cSolver = ClothMuscle()
    #cSolver.runSolve()
__author__ = 'Lorenzo Argentieri'

import maya.mel as mel
import pymel.core as pm

from mayaLib.rigLib.utils import util
from mayaLib.rigLib.utils import deform


def create_collider(geo, nucleus='nucleus1', collider_thickness=0.005):
    nucleus = pm.ls(nucleus)[-1]

    timerNode = pm.ls('time1')[0]
    colliderNode = pm.createNode('nRigid', n=geo.name() + '_collider' + '_Shape')
    pm.rename(colliderNode.getParent(), geo.name() + '_collider')

    pm.connectAttr(timerNode.outTime, colliderNode.currentTime, f=True)
    pm.connectAttr(geo.getShape().worldMesh[0], colliderNode.inputMesh, f=True)

    pm.connectAttr(colliderNode.currentState, nucleus.inputPassive[0], f=True)
    pm.connectAttr(colliderNode.startState, nucleus.inputPassiveStart[0], f=True)

    pm.parent(colliderNode, geo)

    colliderNode.thickness.set(collider_thickness)
    # colliderNode.trappedCheck.set(1)
    # colliderNode.pushOut.set(0)
    # colliderNode.pushOutRadius.set(0.5)

    return colliderNode


def create_nCloth(geo, collider_thickness=0.005):
    pm.select(geo)
    clothShape = pm.ls(mel.eval('createNCloth 0;'))[-1]
    nucleus = pm.listConnections(clothShape, type='nucleus')[0]

    cloth_geo = pm.listConnections(clothShape.outputMesh)[0]
    pm.rename(clothShape.getParent(), str(geo.name()) + '_nCloth')
    pm.parent(clothShape.getParent(), geo)

    # connect inputmeshShape and restShape
    # muscleGeo = pm.ls(str(muscleSimGeo.name()).replace('_SIM', '_GEO'))[0]
    # pm.connectAttr(muscleGeo.getShape().worldMesh[0], clothShape.inputMesh, f=True)
    # pm.connectAttr(muscleGeo.getShape().worldMesh[0], clothShape.restShapeMesh, f=True)

    # Set Default Value
    # Collision
    clothShape.thickness.set(collider_thickness)

    geo_cloth_shape = geo.getShapes()[-1]

    return clothShape, nucleus, geo_cloth_shape

def setup_nCloth(geo):
    geo = pm.ls(geo)[-1]
    cloth_name = str(geo.name()).replace('_geo', '_cloth_geo')
    source_geo = pm.duplicate(geo, n=cloth_name)[-1]

    blendshapeNode = deform.blendShapeDeformer(geo, source_geo, 'cloth_BS', defaultValue=[1, ], frontOfChain=False)
    clothShape, nucleus, geo_cloth_shape = create_nCloth(geo, collider_thickness=0.005)

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
    

class DynamicCurve():
    def __init__(self, curve, prefix='new', baseRig=None):
        # create main dynamic grp under rigGrp
        mainGrpName = 'dynamicSystem_GRP'
        if not pm.objExists(mainGrpName):
            self.dynamicSystemGrp = pm.group(n=mainGrpName, em=1)
        else:
            self.dynamicSystemGrp = pm.ls(mainGrpName)[0]
        if baseRig:
            pm.parent(self.dynamicSystemGrp, baseRig.rigGrp)

        # dynamic Curve
        self.follicleGrp, self.follicle, self.inputCrv, self.outputCrvGrp, self.outputCrv, self.hairSystem = self.makeCurveDynamic(
            curve, prefix)

        # nucleus
        self.nucleus = pm.listConnections(self.hairSystem.getShape().currentState, destination=True)
        try:
            pm.parent(self.nucleus, self.dynamicSystemGrp)
        except:
            pass

        # regroup
        self.systemGrp = pm.group(self.hairSystem, self.follicleGrp, self.outputCrvGrp, n=prefix + 'Dynamic_GRP',
                                  p=self.dynamicSystemGrp)

    def makeCurveDynamic(self, crv, name):
        crvInfo = []
        pm.select(crv)
        mel.eval('makeCurvesDynamic 2 { "1", "0", "1", "1", "0"};')

        follicleOldNameBuffer = pm.listRelatives(crv, parent=True)
        follicleBuffer = pm.rename(follicleOldNameBuffer[0], (name + '_follicle'))
        shapeBuffer = pm.listRelatives(follicleBuffer, shapes=True)
        inputCurveOldNameBuffer = util.returnDriverObject(shapeBuffer[0] + '.startPosition')
        inputCurveBuffer = pm.rename(inputCurveOldNameBuffer, (name + '_input_CRV'))

        # curve transform node
        outputCurveShapeBuffer = util.returnDrivenObject(shapeBuffer[0] + '.outCurve')
        outputCurveBuffer = pm.rename(outputCurveShapeBuffer, (name + '_output_CRV'))

        # output crv group
        outputCurveOldNameBuffer = pm.listRelatives(outputCurveBuffer, parent=True)
        outputCrvsGroup = pm.rename(outputCurveOldNameBuffer, (name + 'OutputCrvs_GRP'))

        # hair system
        hairSystemOldNameBuffer = util.returnDriverObject(shapeBuffer[0] + '.currentPosition')
        hairSystemBuffer = pm.rename(hairSystemOldNameBuffer, (name + '_hairSystem'))

        # follice
        oldFolicleGroupBuffer = (pm.listRelatives(follicleBuffer, parent=True))
        folicleGroup = pm.rename(oldFolicleGroupBuffer[0], (name + 'follicles_GRP'))

        crvInfo.append(folicleGroup)
        crvInfo.append(follicleBuffer)
        # crvInfo.append(shapeBuffer[0])
        crvInfo.append(inputCurveBuffer)
        crvInfo.append(outputCrvsGroup)
        crvInfo.append(outputCurveBuffer)
        crvInfo.append(hairSystemBuffer)
        # crvInfo.append(hairSystemBuffer.getShape())

        return crvInfo

    def getOutputCurve(self):
        return self.outputCrv

    def getInputCurve(self):
        return self.inputCrv

    def getSystemGrp(self):
        return self.systemGrp

    def getFollicleGrp(self):
        return self.follicleGrp


if __name__ == "__main__":
    DynamicCurve('curve1')

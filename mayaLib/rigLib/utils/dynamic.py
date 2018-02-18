__author__ = 'Lorenzo Argentieri'

import pymel.core as pm
import maya.mel as mel
from mayaLib.rigLib.base import module
from mayaLib.rigLib.utils import common
from mayaLib.rigLib.utils import util
import mayaLib.pipelineLib.utility.nameCheck as nc

class DynamicCurve():
    def __init__(self, curve, prefix='new', baseRig=None):
        # make rig module
        self.rigmodule = module.Module(prefix=prefix, baseObj=baseRig)
        if baseRig:
            pm.parent(self.dynamicSystemGrp, baseRig.rigGrp)

        # create main dynamic grp under rigGrp
        mainGrpName = 'dynamicSystem_GRP'
        if not pm.objExists(mainGrpName):
            self.dynamicSystemGrp = pm.group(n=mainGrpName, em=1)
        else:
            self.dynamicSystemGrp = pm.ls(mainGrpName)[0]
        if baseRig:
            pm.parent(self.dynamicSystemGrp, baseRig.rigGrp)

        # dynamic Curve
        self.follicleGrp, self.follicle, self.inputCrv, self.outputCrvGrp, self.outputCrv, self.hairSystem = self.makeCurveDynamic(curve, prefix)

        # nucleus
        self.nucleus = pm.listConnections(self.hairSystem.getShape().currentState, destination=True)
        try:
            pm.parent(self.nucleus, self.dynamicSystemGrp)
        except:
            pass

        # regroup
        pm.group(self.hairSystem, self.follicleGrp, self.outputCrvGrp, n=prefix + 'Dynamic_GRP', p=self.dynamicSystemGrp)

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
        #crvInfo.append(shapeBuffer[0])
        crvInfo.append(inputCurveBuffer)
        crvInfo.append(outputCrvsGroup)
        crvInfo.append(outputCurveBuffer)
        crvInfo.append(hairSystemBuffer)
        #crvInfo.append(hairSystemBuffer.getShape())

        return crvInfo


def makeCurvesDynamic(curve, grpName='dynamicCurve*_GRP'):
    grpName = nc.nameCheck(grpName)
    pm.select(curve)
    mel.eval('makeCurvesDynamic 2 { "1", "0", "1", "1", "0"};')

    dynamicObj_list = pm.ls('hairSystem*', 'nucleus*')
    # nucleus
    nucleus = pm.ls('nucleus*')

    # select last created hairSystem
    hairSystem = pm.ls('hairSystem*')[-1]

    if pm.objExists(grpName):
        pm.parent(hairSystem, grpName)
    else:
        pm.group(hairSystem, n=grpName)

    outputGrp = pm.ls('hairSystem*OutputCurves')[-1]
    follicleGrp = pm.ls('hairSystem*Follicles')[-1]
    outputCurve = pm.listRelatives(outputGrp, children=True)[0]

    # disable inheritTransform on follicle
    follicle = pm.listRelatives(follicleGrp, children=True)[0]
    pm.setAttr(follicle + '.inheritsTransform', 0)

    # regroup
    systemGrp = 'system_GRP'
    if pm.objExists(systemGrp):
        #pm.parent(nucleus, systemGrp)
        pass
    else:
        pm.group(nucleus, n=systemGrp)

    mainGrpName = 'dynamicSystem_GRP'
    if pm.objExists(mainGrpName):
        pm.parent(grpName, mainGrpName)
    else:
        pm.group(grpName, n=mainGrpName)

    pm.parent(systemGrp, mainGrpName)
    pm.parent(pm.ls(outputGrp, follicleGrp), grpName)

    return outputCurve, grpName, follicleGrp

class IkDynamicChain():
    def __init__(self, startJnt, curve, name='ikChain'):
        # get childern of shoulder
        tipJnt = pm.listRelatives(startJnt, type='joint', children=True, allDescendents=True)[0]
        # make curve dinamic
        dynamicCurve, self.systemGrp, follicleGrp = makeCurvesDynamic(curve)
        # create ik
        ikhandle = pm.ikHandle(n=name, sj=startJnt, ee=tipJnt, c=dynamicCurve, sol='ikSplineSolver', ccv=False,
                               roc=False, pcv=False, snc=True)
        # create control locator
        self.ctrlLocator = pm.spaceLocator(n=name + 'Ctrl_LOC')
        # group ik and dynamicSystem
        self.chainGrp = pm.group(self.ctrlLocator, ikhandle[0], self.systemGrp, n=name + '_GRP')
        common.centerPivot(self.chainGrp, startJnt)

        pm.parent(startJnt, self.chainGrp)
        # return ctrlLocator, chainGrp


if __name__ == "__main__":
    IkDynamicChain('joint1', 'curve1')
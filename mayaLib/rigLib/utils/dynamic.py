__author__ = 'Lorenzo Argentieri'

import maya.mel as mel
import pymel.core as pm

from mayaLib.rigLib.utils import util


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

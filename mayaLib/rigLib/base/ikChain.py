"""
ikChain @ rig
"""

import pymel.core as pm
from mayaLib.rigLib.utils import name
from mayaLib.rigLib.base import module
from mayaLib.rigLib.base import control
from mayaLib.rigLib.utils import dynamic
from mayaLib.rigLib.utils import deform


class IKChain():
    def __init__(self, 
                 chainJoints,
                 prefix='tail',
                 rigScale=1.0,
                 doDynamic=False,
                 smallestScalePercent=0.1,
                 fkParenting=True,
                 baseRig=None
                 ):
        """
        :param chainJoints: list( str ), list of chain joints
        :param prefix: str, prefix to name new objects
        :param rigScale: float, scale factor for size of controls
        :param smallestScalePercent: float, scale of smallest control at the end of chain compared to rigScale
        :param doDynamic: bool, setup dynamic curve
        :param fkParenting: bool, parent each control to previous one to make FK chain
        :param baseRig: instance of base.module.Base class
        :return: dictionary with rig module objects
        """
        # :param chainCurve: str, name of chain cubic curve
    
        # make rig module
        self.rigmodule = module.Module(prefix=prefix, baseObj=baseRig)

        # collision point
        collisionPoint = int(len(chainJoints))

        # make IK handle
        chainIk, effector, chainCurve = pm.ikHandle(n=prefix + '_IKH', sol='ikSplineSolver', sj=chainJoints[0], ee=chainJoints[-1], # -2
                                                    createCurve=True, numSpans=collisionPoint)

        # rename curve
        pm.rename(chainCurve, prefix+'_CRV')

        # create ctrlCurve
        ctrlCurve = pm.duplicate(chainCurve, n=prefix+'Ctrl_CRV')[0]

        # make chain curve clusters
        chainCurveCVs = pm.ls(ctrlCurve + '.cv[*]', fl=1)
        numChainCVs = len(chainCurveCVs)
        chainCurveClusters = []

        for i in range(numChainCVs):
            cls = pm.cluster(chainCurveCVs[i], n=prefix + 'Cluster%d' % (i + 1))[1]
            chainCurveClusters.append(cls)

        pm.hide(chainCurveClusters)

        # parent chain curve
        pm.parent(chainCurve, self.rigmodule.partsNoTransGrp)
        pm.parent(ctrlCurve, self.rigmodule.partsNoTransGrp)

        # make attach groups
        self.baseAttachGrp = pm.group(n=prefix + 'BaseAttach_GRP', em=1, p=self.rigmodule.partsGrp)

        pm.delete(pm.pointConstraint(chainJoints[0], self.baseAttachGrp))

        # make controls
        chainControls = []
        controlScaleIncrement = (1.0 - smallestScalePercent) / numChainCVs
        mainCtrlScaleFactor = 1.0 # 5.0

        for i in range(numChainCVs):
            ctrlScale = rigScale * mainCtrlScaleFactor * (1.0 - (i * controlScaleIncrement))
            ctrl = control.Control(prefix=prefix + '%d' % (i + 1), translateTo=chainCurveClusters[i],
                                   scale=ctrlScale, parent=self.rigmodule.controlsGrp, shape='sphere')

            chainControls.append(ctrl)

        # parent controls
        if fkParenting:
            for i in range(numChainCVs):
                if i == 0:
                    continue
                pm.parent(chainControls[i].Off, chainControls[i - 1].C)

        # attach clusters
        for i in range(numChainCVs):
            pm.parent(chainCurveClusters[i], chainControls[i].C)

        # attach controls
        pm.parentConstraint(self.baseAttachGrp, chainControls[0].Off, mo=1)

        pm.hide(chainIk)
        pm.parent(chainIk, self.rigmodule.partsNoTransGrp)

        # add twist attribute
        twistAt = 'twist'
        pm.addAttr(chainControls[-1].C, ln=twistAt, k=1)
        pm.connectAttr(chainControls[-1].C + '.' + twistAt, chainIk + '.twist')

        # save class attribute
        self.chainCurve = chainCurve
        self.controlCurve = ctrlCurve

        if doDynamic:
            self.dynCurve = self.makeDynamic(prefix, baseRig, self.rigmodule, chainControls, chainCurveClusters)

            deform.blendShapeDeformer(self.dynCurve.getInputCurve(), [self.controlCurve], nodeName=prefix+'BlendShape', frontOfChain=True)
            deform.blendShapeDeformer(self.chainCurve, [self.dynCurve.getOutputCurve()], nodeName=prefix+'BlendShape', frontOfChain=True)
        else:
            deform.blendShapeDeformer(self.chainCurve, [self.controlCurve], nodeName=prefix+'BlendShape', frontOfChain=True)



    def getModuleDict(self):
        return {'module': self.rigmodule, 'baseAttachGrp': self.baseAttachGrp}

    def makeDynamic(self, prefix, baserig, basemodule, chainControls, chainCurveClusters):
        # duplicate ikChain curve and make dynamic
        dynamicCurveName = name.removeSuffix(pm.ls(self.chainCurve)[0].shortName()) + '_CRV'
        dynCurvebase = pm.duplicate(self.chainCurve, n=dynamicCurveName)
        pm.parent(dynCurvebase, w=True)

        dynCurve = dynamic.DynamicCurve(dynCurvebase, prefix=prefix, baseRig=baserig)

        # reparent
        pm.parent(dynCurve.getSystemGrp(), basemodule.partsNoTransGrp)

	return dynCurve
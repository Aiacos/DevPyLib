"""
ikChain @ rig
"""

import pymel.core as pm
from mayaLib.rigLib.base import module
from mayaLib.rigLib.base import control


class IKChain():
    def __init__(self, 
                 chainJoints,
                 chainCurve,
                 prefix='tail',
                 rigScale=1.0,
                 smallestScalePercent=0.5,
                 fkParenting=True,
                 baseRig=None
                 ):
        """
        :param chainJoints: list( str ), list of chain joints
        :param chainCurve: str, name of chain cubic curve
        :param prefix: str, prefix to name new objects
        :param rigScale: float, scale factor for size of controls
        :param smallestScalePercent: float, scale of smallest control at the end of chain compared to rigScale
        :param fkParenting: bool, parent each control to previous one to make FK chain
        :param baseRig: instance of base.module.Base class
        :return: dictionary with rig module objects
        """
    
        # make rig module
        self.rigmodule = module.Module(prefix=prefix, baseObj=baseRig)
    
        # make chain curve clusters
        chainCurveCVs = pm.ls(chainCurve + '.cv[*]', fl=1)
        numChainCVs = len(chainCurveCVs)
        chainCurveClusters = []
    
        for i in range(numChainCVs):
            cls = pm.cluster(chainCurveCVs[i], n=prefix + 'Cluster%d' % (i + 1))[1]
            chainCurveClusters.append(cls)
    
        pm.hide(chainCurveClusters)
    
        # parent chain curve
        pm.parent(chainCurve, self.rigmodule.partsNoTransGrp)
    
        # make attach groups
        self.baseAttachGrp = pm.group(n=prefix + 'BaseAttach_GRP', em=1, p=self.rigmodule.partsGrp)
    
        pm.delete(pm.pointConstraint(chainJoints[0], self.baseAttachGrp))
    
        # make controls
        chainControls = []
        controlScaleIncrement = (1.0 - smallestScalePercent) / numChainCVs
        mainCtrlScaleFactor = 5.0
    
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
    
        # make IK handle
        chainIk = pm.ikHandle(n=prefix + '_IKH', sol='ikSplineSolver', sj=chainJoints[0], ee=chainJoints[-1],
                              c=chainCurve, ccv=0, parentCurve=0)[0]
    
        pm.hide(chainIk)
        pm.parent(chainIk, self.rigmodule.partsNoTransGrp)
    
        # add twist attribute
        twistAt = 'twist'
        pm.addAttr(chainControls[-1].C, ln=twistAt, k=1)
        pm.connectAttr(chainControls[-1].C + '.' + twistAt, chainIk + '.twist')


    def getModuleDict(self):
        return {'module': self.rigmodule, 'baseAttachGrp': self.baseAttachGrp}

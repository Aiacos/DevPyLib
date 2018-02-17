"""
spine @ rig
"""

import maya.cmds as mc

from ..base import module
from ..base import control

def build(
          spineJoints,
          rootJnt,
          spineCurve,
          bodyLocator,
          chestLocator,
          pelvisLocator,
          prefix = 'spine',
          rigScale = 1.0,
          baseRig = None
          ):
    
    """
    @param spineJoints: list( str ), list of 6 spine joints
    @param rootJnt: str, root joint
    @param spineCurve: str, name of spine cubic curve with 5 CVs matching first 5 spine joints
    @param bodyLocator: str, reference transform for position of body control
    @param chestLocator: str, reference transform for position of chest control
    @param pelvisLocator: str, reference transform for position of pelvis control
    @param prefix: str, prefix to name new objects
    @param rigScale: float, scale factor for size of controls
    @param baseRig: instance of base.module.Base class
    @return: dictionary with rig module objects 
    """
    
    # make rig module
    
    rigmodule = module.Module( prefix = prefix, baseObj = baseRig )
    
    # make spine curve clusters
    
    spineCurveCVs = mc.ls( spineCurve + '.cv[*]', fl = 1 )
    numSpineCVs = len( spineCurveCVs )
    spineCurveClusters = []
    
    for i in range( numSpineCVs ):
        
        cls = mc.cluster( spineCurveCVs[i], n = prefix + 'Cluster%d' % ( i + 1 ) )[1]
        spineCurveClusters.append( cls )
    
    mc.hide( spineCurveClusters )
    
    # parent spine curve
    
    mc.parent( spineCurve, rigmodule.partsNoTransGrp )
    
    
    # make controls
    
    bodyCtrl = control.Control( prefix = prefix + 'Body', translateTo = bodyLocator, scale = rigScale * 4,
                                parent = rigmodule.controlsGrp )
    
    chestCtrl = control.Control( prefix = prefix + 'Chest', translateTo = chestLocator, scale = rigScale * 6,
                                parent = bodyCtrl.C, shape = 'circleZ' )
    
    pelvisCtrl = control.Control( prefix = prefix + 'Pelvis', translateTo = pelvisLocator, scale = rigScale * 6,
                                parent = bodyCtrl.C, shape = 'circleZ' )
    
    middleCtrl = control.Control( prefix = prefix + 'Middle', translateTo = spineCurveClusters[2], scale = rigScale * 3,
                                parent = bodyCtrl.C, shape = 'circleZ' )
    
    _adjustBodyCtrlShape( bodyCtrl, spineJoints, rigScale )
    
    # attach controls
    
    mc.parentConstraint( chestCtrl.C, pelvisCtrl.C, middleCtrl.Off, sr = ['x', 'y', 'z'], mo = 1 )
    
    # attach clusters
    
    mc.parent( spineCurveClusters[3:], chestCtrl.C )
    mc.parent( spineCurveClusters[2], middleCtrl.C )
    mc.parent( spineCurveClusters[:2], pelvisCtrl.C )
    
    # attach chest joint
    
    mc.orientConstraint( chestCtrl.C, spineJoints[-2], mo = 1 )
    
    # make IK handle
    
    spineIk = mc.ikHandle( n = prefix + '_ikh', sol = 'ikSplineSolver', sj = spineJoints[0], ee = spineJoints[-2],
                           c = spineCurve, ccv = 0, parentCurve = 0 )[0]
    
    mc.hide( spineIk )
    mc.parent( spineIk, rigmodule.partsNoTransGrp )
    
    # setup IK twist
    
    mc.setAttr( spineIk + '.dTwistControlEnable', 1 )
    mc.setAttr( spineIk + '.dWorldUpType', 4 )
    mc.connectAttr( chestCtrl.C + '.worldMatrix[0]', spineIk + '.dWorldUpMatrixEnd' )
    mc.connectAttr( pelvisCtrl.C + '.worldMatrix[0]', spineIk + '.dWorldUpMatrix' )
    
    # attach root joint
    
    mc.parentConstraint( pelvisCtrl.C, rootJnt, mo = 1 )
    
    return { 'module':rigmodule, 'bodyCtrl':bodyCtrl }
    


def _adjustBodyCtrlShape( bodyCtrl, spineJoints, rigScale ):
    
    """
    offset body control along spine Y axis
    """
    
    offsetGrp = mc.group( em = 1, p = bodyCtrl.C )
    mc.parent( offsetGrp, spineJoints[2] )
    ctrlCls = mc.cluster( mc.listRelatives( bodyCtrl.C, s = 1 ) )[1]
    mc.parent( ctrlCls, offsetGrp )
    mc.move( 10 * rigScale, offsetGrp, moveY = 1, relative = 1, objectSpace = 1 )
    mc.delete( bodyCtrl.C, ch = 1 )
    
    

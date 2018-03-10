"""
leg @ rig
"""

import maya.cmds as mc

from ..base import module
from ..base import control

from ..utils import joint
from ..utils import name

def build(
          legJoints,
          topToeJoints,
          pvLocator,
          scapulaJnt = '',
          prefix = 'l_leg',
          rigScale = 1.0,
          baseRig = None
          ):
    
    """
    @param legJoints: list( str ), shoulder - elbow - hand - toe - end toe
    @param topToeJoints: list( str ), top metacarpal toe joints
    @param pvLocator: str, reference locator for position of Pole Vector control
    @param scapulaJnt: str, optional, scapula joint, parent of top leg joint
    @param prefix: str, prefix to name new objects
    @param rigScale: float, scale factor for size of controls
    @param baseRig: baseRig: instance of base.module.Base class
    @return: dictionary with rig module objects
    """
    
    # make rig module
    
    rigmodule = module.Module( prefix = prefix, baseObj = baseRig )
    
    # make attach groups
    
    bodyAttachGrp = mc.group( n = prefix + 'BodyAttach_grp', em = 1, p = rigmodule.partsGrp )
    baseAttachGrp = mc.group( n = prefix + 'BaseAttach_grp', em = 1, p = rigmodule.partsGrp )
    
    # make controls
    
    if scapulaJnt:
        
        scapulaCtrl = control.Control( prefix = prefix + 'Scapula', translateTo = scapulaJnt, rotateTo = scapulaJnt,
                                       scale = rigScale * 3, parent = rigmodule.controlsGrp, shape= 'sphere',
                                       lockChannels = ['ty', 'rx', 'rz', 's', 'v'] )
        
    footCtrl = control.Control( prefix = prefix + 'Foot', translateTo = legJoints[2], scale = rigScale * 3,
                                parent = rigmodule.controlsGrp, shape = 'circleY' )
    
    ballCtrl = control.Control( prefix = prefix + 'Ball', translateTo = legJoints[3], rotateTo = legJoints[3],
                                       scale = rigScale * 2, parent = footCtrl.C, shape = 'circleZ' )
    
    poleVectorCtrl = control.Control( prefix = prefix + 'PV', translateTo = pvLocator, scale = rigScale,
                                parent = rigmodule.controlsGrp, shape = 'sphere' )
    
    
    toeIkControls = []
    
    
    for topToeJnt in topToeJoints:
        
        toePrefix = name.removeSuffix( topToeJnt )[:-1]
        toeEndJnt = mc.listRelatives( topToeJnt, ad = 1, type = 'joint' )[0]
        
        toeIkCtrl = control.Control( prefix = toePrefix, translateTo = toeEndJnt, scale = rigScale,
                                     parent = footCtrl.C, shape = 'circleY' )
        
        toeIkControls.append( toeIkCtrl )
        
    
    # make IK handles
    
    if scapulaJnt:
        
        scapulaIk = mc.ikHandle( n = prefix + 'Scapula_ikh', sol = 'ikSCsolver', sj = scapulaJnt, ee = legJoints[0] )[0]
        mc.hide( scapulaIk )
    
    legIk = mc.ikHandle( n = prefix + 'Main_ikh', sol = 'ikRPsolver', sj = legJoints[0], ee = legJoints[2] )[0]
    ballIk = mc.ikHandle( n = prefix + 'Ball_ikh', sol = 'ikSCsolver', sj = legJoints[2], ee = legJoints[3] )[0]
    mainToeIk = mc.ikHandle( n = prefix + 'MainToe_ikh', sol = 'ikSCsolver', sj = legJoints[3], ee = legJoints[4] )[0]
    
    mc.hide( legIk, ballIk, mainToeIk )
    
    for i, topToeJnt in enumerate( topToeJoints ):
        
        toePrefix = name.removeSuffix( topToeJnt )[:-1]
        toeJoints = joint.listHierarchy( topToeJnt )
        
        toeIk = mc.ikHandle( n = toePrefix + '_ikh', sol = 'ikSCsolver', sj = toeJoints[1], ee = toeJoints[-1] )[0]
        mc.hide( toeIk )
        mc.parent( toeIk, toeIkControls[i].C )
    
    # attach controls
    
    mc.parentConstraint( bodyAttachGrp, poleVectorCtrl.Off, mo = 1 )
    
    if scapulaJnt:
        
        mc.parentConstraint( baseAttachGrp, scapulaCtrl.Off, mo = 1 )
    
    # attach objects to controls
    
    mc.parent( legIk, ballCtrl.C )
    mc.parent( ballIk, mainToeIk, footCtrl.C )
    
    mc.poleVectorConstraint( poleVectorCtrl.C, legIk )
    
    if scapulaJnt:
        
        mc.parent( scapulaIk, scapulaCtrl.C )
        mc.pointConstraint( scapulaCtrl.C, scapulaJnt )
    
    # make pole vector connection line
    
    pvLinePos1 = mc.xform( legJoints[1], q = 1, t = 1, ws = 1 )
    pvLinePos2 = mc.xform( pvLocator, q = 1, t = 1, ws = 1 )
    poleVectorCrv = mc.curve( n = prefix + 'Pv_crv', d = 1, p = [ pvLinePos1, pvLinePos2 ] )
    mc.cluster( poleVectorCrv + '.cv[0]', n = prefix + 'Pv1_cls', wn = [ legJoints[1], legJoints[1] ], bs = True )
    mc.cluster( poleVectorCrv + '.cv[1]', n = prefix + 'Pv2_cls', wn = [ poleVectorCtrl.C, poleVectorCtrl.C ], bs = True )
    mc.parent( poleVectorCrv, rigmodule.controlsGrp )
    mc.setAttr( poleVectorCrv + '.template', 1 )
    mc.setAttr( poleVectorCrv + '.it', 0 )
    
    
    return { 'module':rigmodule, 'baseAttachGrp':baseAttachGrp, 'bodyAttachGrp':bodyAttachGrp }
    
    

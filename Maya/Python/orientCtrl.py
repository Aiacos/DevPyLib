__author__ = 'Lorenzo Argentieri'

import pymel.core as pm

def renameCtrl(joint, control):
    jointName = joint
    controlName = jointName.replace('_jnt', '_ctrl')
    print controlName
    return control.rename(controlName)

def orientCtrl_constrain(control, joint):
    control_name = renameCtrl(joint, control)
    control_group = pm.group(control, n=control_name + '_grp')
    control_group.rotateZ.set(90)
    pm.makeIdentity(control_group, apply=True)
    parentConstraint = pm.parentConstraint(joint, control_group)
    pm.delete(parentConstraint)

def orientCtrl_parent(control, joint):
    control_name = renameCtrl(joint, control)
    joint_pivot = joint.getTranslation(worldSpace=True)
    #set PivotPoint to Joint location
    control_group = pm.group(control, n=control_name + '_grp')
    control.setPivots(joint_pivot, worldSpace=True)
    control_group.setPivots(joint_pivot, worldSpace=True)
    pm.parent(control_group, joint)
    pm.delete(control_group, constructionHistory=True)
    pm.makeIdentity(control_group, apply=True)#translate=True, rotate=True, scale=True)
    pm.parent(control_group, world=True)

def main_orientCtrl():
    '''
    Select Control and Joint in order
    '''

    sel1, sel2 = pm.ls(sl=True)

    print sel2.nodeType()

    if sel2.nodeType() == 'joint':
        print 'parent'
        orientCtrl_parent(sel1, sel2)
    else:
        print 'costrain'
        orientCtrl_constrain(sel2, sel1)



main_orientCtrl()
#!/usr/bin/env python
# -*- coding: utf-8 -*-

#********************************
# Copyright 2021 Toshi Kosaka
#
# GORIOSHI SCRIPTS
#********************************
'''****************************************************************************
*** MuscleTool_v1.0.py
***
*** Scripted in Maya 2018/2022
*** 
*** Please do not copy, distribute, or modify without permission of the author.
****************************************************************************'''

import maya.cmds as mc
import maya.mel as mel

def applyCollisionSolveValues(arg=None):
    mc.floatField('clothThickness', e=True, v=0.01)
    mc.intField('stretchResistance', e=True, v=20)
    mc.floatField('rigidity', e=True, v=0)
    mc.intField('pressure', e=True, v=0)
    mc.floatField('pushOut', e=True, v=1)
    nClothList = mc.ls(type='nCloth', fl=True)
    for each in nClothList:
        mc.setAttr(each + '.thickness', mc.floatField('clothThickness', q=True, v=True))
        mc.setAttr(each + '.stretchResistance', mc.intField('stretchResistance', q=True, v=True))
        mc.setAttr(each + '.rigidity', mc.floatField('rigidity', q=True, v=True))
        mc.setAttr(each + '.pressure', mc.intField('pressure', q=True, v=True))
        mc.setAttr(each + '.pushOut', mc.floatField('pushOut', q=True, v=True))
        mc.setAttr(each + '.compressionResistance', 0)
        mc.setAttr(each + '.bendResistance', 0)
        mc.setAttr(each + '.lift', 0)
        mc.setAttr(each + '.drag', 2)
        mc.setAttr(each + '.tangentialDrag', 1)
        mc.setAttr(each + '.damp', 10)
        mc.setAttr(each + '.stretchDamp', 10)
        mc.setAttr(each + '.trappedCheck', 1)
        mc.setAttr(each + '.selfTrappedCheck', 1)
        mc.setAttr(each + '.crossoverPush', 1)
        mc.setAttr(each + '.selfCrossoverPush', 1)
        mc.setAttr(each + '.restLengthScale', 1)
    mc.checkBox('restLengthScale', e=True, en=False, v=False)


def applyFillValues(arg=None):
    mc.floatField('clothThickness', e=True, v=0.01)
    mc.intField('stretchResistance', e=True, v=1)
    mc.floatField('rigidity', e=True, v=0)
    mc.intField('pressure', e=True, v=2)
    mc.floatField('pushOut', e=True, v=1)
    nClothList = mc.ls(type='nCloth', fl=True)
    for each in nClothList:
        mc.setAttr(each + '.thickness', mc.floatField('clothThickness', q=True, v=True))
        mc.setAttr(each + '.stretchResistance', mc.intField('stretchResistance', q=True, v=True))
        mc.setAttr(each + '.rigidity', mc.floatField('rigidity', q=True, v=True))
        mc.setAttr(each + '.pressure', mc.intField('pressure', q=True, v=True))
        mc.setAttr(each + '.pushOut', mc.floatField('pushOut', q=True, v=True))
        mc.setAttr(each + '.compressionResistance', 0)
        mc.setAttr(each + '.bendResistance', 0)
        mc.setAttr(each + '.lift', 0)
        mc.setAttr(each + '.drag', 2)
        mc.setAttr(each + '.tangentialDrag', 1)
        mc.setAttr(each + '.damp', 10)
        mc.setAttr(each + '.stretchDamp', 10)
        mc.setAttr(each + '.trappedCheck', 1)
        mc.setAttr(each + '.selfTrappedCheck', 1)
        mc.setAttr(each + '.crossoverPush', 1)
        mc.setAttr(each + '.selfCrossoverPush', 1)
        mc.setAttr(each + '.restLengthScale', 1)
    mc.checkBox('restLengthScale', e=True, en=True, v=False)

def applyValues(arg=None):
    nClothList = mc.ls(type='nCloth', fl=True)
    for each in nClothList:
        mc.setAttr(each + '.thickness', mc.floatField('clothThickness', q=True, v=True))
        mc.setAttr(each + '.stretchResistance', mc.intField('stretchResistance', q=True, v=True))
        mc.setAttr(each + '.rigidity', mc.floatField('rigidity', q=True, v=True))
        mc.setAttr(each + '.pressure', mc.intField('pressure', q=True, v=True))
        mc.setAttr(each + '.pushOut', mc.floatField('pushOut', q=True, v=True))
        mc.setAttr(each + '.compressionResistance', 0)
        mc.setAttr(each + '.bendResistance', 0)
        mc.setAttr(each + '.lift', 0)
        mc.setAttr(each + '.drag', 2)
        mc.setAttr(each + '.tangentialDrag', 1)
        mc.setAttr(each + '.damp', 10)
        mc.setAttr(each + '.stretchDamp', 10)
        mc.setAttr(each + '.trappedCheck', 1)
        mc.setAttr(each + '.selfTrappedCheck', 1)
        mc.setAttr(each + '.crossoverPush', 1)
        mc.setAttr(each + '.selfCrossoverPush', 1)
        mc.setAttr(each + '.inputMotionDrag', 1)
    if mc.checkBox('restLengthScale', q=True, v=True) == True:
        mc.setAttr(each + '.restLengthScale', 0)
    else:
        mc.setAttr(each + '.restLengthScale', 1)
        
    if mc.getAttr(each + '.pressure') > 0 and mc.getAttr(each + '.stretchResistance') < 2:
        mc.checkBox('restLengthScale', e=True, en=True)
    else:
        mc.checkBox('restLengthScale', e=True, en=False, v=False)
        mc.setAttr(each + '.restLengthScale', 1)

def applyValuesRigid(arg=None):
    nRigidList = mc.ls(type='nRigid', fl=True)
    for each in nRigidList:
        mc.setAttr(each + '.thickness', mc.floatField('rigidThickness', q=True, v=True))
        mc.setAttr(each + '.pushOut', mc.floatField('pushOutRigid', q=True, v=True))
        mc.setAttr(each + '.crossoverPush', mc.intField('crossoverPushRigid', q=True, v=True))
        mc.setAttr(each + '.pushOutRadius', 1)

def clearNCloth(arg=None):
    sel = mc.ls(sl=True, fl=True)
    remove = []
    for each in sel:
        currentShapes = mc.listRelatives(each, type='mesh')
        if len(currentShapes) > 1 and mc.getAttr(currentShapes[0] + '.intermediateObject') == False:
            mc.delete(mc.listConnections(currentShapes[0], type='nCloth'))
            mc.delete(currentShapes[1])
            remove.append(each)
            
    for each in remove:
        sel.remove(each)
    for each in sel:
        nClothName = mc.listConnections(mc.listRelatives(each), type='nCloth')[0]
        inputMeshName = mc.listRelatives(each)[0]
        
        if any('blendShape' in x for x in mc.listConnections(mc.listRelatives(each, c=True))) == True:
            bsDelete = mc.listConnections(mc.listConnections(mc.listRelatives(each, c=True), type='blendShape')[0] +'.inputTarget')
            mc.delete(each, ch=True)
            mc.delete(bsDelete)
        else:
            mc.delete(each, ch=True)
        
        if mc.objExists(nClothName):
            mc.delete(nClothName)
            if mc.objExists(inputMeshName):
                mc.delete(inputMeshName)
            mc.rename(mc.listRelatives(each, c=True), inputMeshName)
            mc.hyperShade(a='initialShadingGroup')
        else:
            mc.delete(inputMeshName)
            mc.rename(mc.listRelatives(each, c=True), inputMeshName)
            mc.hyperShade(a='initialShadingGroup')
    
def clearNRigid(arg=None):
    sel = mc.ls(sl=True, fl=True)
    for each in sel:
        selChildren = mc.listRelatives(each, c=True)
        if len(selChildren) < 2:
            selConnections = mc.listConnections(selChildren)
            for this in selConnections:
                if 'nRigid' in this:
                    mc.delete(this)
                    mc.sets(sel, e=True, fe='initialShadingGroup')

def resetUI(arg=None):
    muscleTool()

def makeShaders():
    shaderName = 'rigidLambert'
    if mc.objExists(shaderName) == 0:
        mc.shadingNode('lambert', asShader=True, n=shaderName)
        mc.sets(renderable=True, noSurfaceShader=True, empty=True, name=shaderName + 'SG')
        mc.connectAttr(shaderName + '.outColor', shaderName + 'SG.surfaceShader', f=True)
    mc.setAttr(shaderName + '.color', 0.1, 0.1, 0.1)
    mc.setAttr(shaderName + '.transparency', 0.5, 0.5, 0.5)

    shaderName2 = 'muscleLambert'
    if mc.objExists(shaderName2) == 0:
        mc.shadingNode('lambert', asShader=True, n=shaderName2)
        mc.sets(renderable=True, noSurfaceShader=True, empty=True, name=shaderName2 + 'SG')
        mc.connectAttr(shaderName2 + '.outColor', shaderName2 + 'SG.surfaceShader', f=True)
    mc.setAttr(shaderName2 + '.color', 1, .5, .5)

def makeRigid(arg=None):
    selRigids = mc.ls(sl=True, fl=True)
    makeShaders()
    for this in selRigids:
        if len(mc.listRelatives(this)) > 1:
            selRigids.remove(this)
    makePassiveCollider = 'makeCollideNCloth'
    nodes = mel.eval(makePassiveCollider)
    for each in nodes:
        mc.setAttr('nRigid' + each.split('RigidShape')[1] + '.visibility', 0)
    nucleusNode = mc.ls(type='nucleus')
    if len(nucleusNode) > 1:
        mc.promptDialog(m='Use only one nucleus.  It\'s confusing...')
    mc.setAttr(nucleusNode[0] + '.gravity', 0)
    mc.select(selRigids)
    mc.sets(e=True, fe='rigidLambertSG')
    applyValuesRigid()

def makeMuscle(arg=None):
    selMuscles = mc.ls(sl=True, fl=True)
    makeShaders()
    for this in selMuscles:
        if len(mc.listConnections(mc.listRelatives(this, c=True))) > 1:
            selMuscles.remove(this)
    makeNCloth = 'createNCloth 0;'
    nodes = mel.eval(makeNCloth)
    for each in nodes:
        mc.setAttr('nCloth' + each.split('ClothShape')[1] + '.visibility', 0)
    nucleusNode = mc.ls(type='nucleus')
    if len(nucleusNode) > 1:
        mc.promptDialog(m='Use only one nucleus.  It\'s confusing...')
    mc.setAttr(nucleusNode[0] + '.gravity', 0)
    mc.select(selMuscles)
    mc.sets(e=True, fe='muscleLambertSG')
    applyValues()

def reverseNormal(arg=None):
    selRigids = mc.ls(sl=True, fl=True)
    mc.polyNormal(selRigids, nm=0, unm=1, ch=0)

def selectNRigid(arg=None):
    selRigid = mc.ls(type='nRigid')
    sel = []
    for each in selRigid:
        con = mc.listConnections(each)
        sel.append(con[len(con)-1])
    mc.select(sel)

def selectNCloth(arg=None):
    selnCloth = mc.ls(type='nCloth')
    sel = []
    for each in selnCloth:
        con = mc.listConnections(each, type='mesh')
        sel.append(con[len(con)-2])
    mc.select(sel)

def relaxEdges(arg=None):
    sel = mc.ls(sl=True, o=True, fl=True)
    for each in sel:
        mc.polyMoveEdge(each, ch=0, ran=0, lc=0, lsx=0)
        mc.DeleteHistory()
    mc.select(sel)

def moveAlongNormal(arg=None):
    sel = mc.ls(sl=True, o=True, fl=True)
    for each in sel:
        mc.polyMoveVertex(each, ch=0, ran=0, ltz=.01)
        mc.DeleteHistory()
    mc.select(sel)

def timeReset(arg=None):
    mc.currentTime(1)
def timeNext(arg=None):
    mc.currentTime(mc.currentTime(q=True) +1)
def timeStop(arg=None):
    mc.play(st=False)
def timePlay(arg=None):
    if mc.play(q=True, st=True) == True:
        mc.play(st=False)
    else:
        mc.play(st=True)
        
def freezeSetup(arg=None):
    connections = mc.listConnections(mc.listRelatives(mc.ls(sl=True, fl=True)))

    if any('nCloth' in s for s in connections) == True and any('blendShape' not in k for k in connections) == True:
        sel = mc.ls(sl=True, fl=True)
        for each in sel:
            bs = mc.duplicate(each)[0]
            mc.setAttr(bs + '.hiddenInOutliner', 1)
            mc.setAttr(bs + '.visibility', 0)
            bsShapes = mc.listRelatives(bs, c=True)
            mc.delete(bs + '|' + bsShapes[1])
            mc.setAttr(bsShapes[0] + '.intermediateObject', 0)
            bsNode = mc.blendShape(bs, each)[0]
            mc.setAttr(bsNode + '.' + bs, 1)
        mc.select(sel)
        mc.ArtPaintBlendShapeWeightsTool(sel)
            
def paintWeight(arg=None):
    if mc.listConnections(mc.listRelatives(mc.ls(sl=True, fl=True))[0], type='blendShape') != None:
        mc.ArtPaintBlendShapeWeightsTool()

def fixShapeName(arg=None):
    sel = mc.ls(sl=True, fl=True)
    for this in sel:
        shapes = mc.listRelatives(this, c=True)
        if len(shapes) >= 2:
            mc.warning('There are more than 1 shapes')
        else:
            for each in sel:
                mc.rename(mc.listRelatives(each, c=True)[0], each + 'Shape')

def toggleIO(arg=None):
    sel = mc.ls(sl=True, fl=True)
    for each in sel:
        shapes = mc.listRelatives(each, c=True)
        if len(shapes) == 2:
            if mc.getAttr(shapes[0] + '.intermediateObject') == 1:
                mc.setAttr(shapes[0] + '.intermediateObject', 0)
                mc.setAttr(shapes[1] + '.intermediateObject', 1)
            else:
                mc.setAttr(shapes[0] + '.intermediateObject', 1)
                mc.setAttr(shapes[1] + '.intermediateObject', 0)

def deleteIO(arg=None):
    sel = mc.ls(sl=True, fl=True)[0]
    shapes = mc.listRelatives(sel, c=True)
    
    if len(shapes) == 2:
        if mc.getAttr(shapes[0] + '.intermediateObject') == 1:
            if mc.listConnections(shapes[0], type='nCloth') != None:
                mc.delete(mc.listConnections(shapes[0], type='nCloth'))
                mc.delete(shapes[0])
            else:
                mc.delete(shapes[0])
        else:
            if mc.listConnections(shapes[0], type='nCloth') != None:
                mc.delete(mc.listConnections(shapes[0], type='nCloth'))
                mc.delete(shapes[1])
            else:
                mc.delete(shapes[1])
        mc.rename(mc.listRelatives(sel, c=True)[0], sel + 'Shape')
    
def transformConstraint(arg=None):
    sel = mc.ls(sl=True, o=True)
    mc.nConstraintTransform()
    mc.select(mc.listRelatives(sel, p=True))
    
def removeConstraint(arg=None):
    sel = mc.listRelatives(mc.ls(sl=True, fl=True), c=True, type='mesh')
    for each in sel:
        if mc.getAttr(each + '.intermediateObject') == False:
            sel.remove(each)
    allNComponents = mc.ls(type='nComponent')
    for this in sel:
        for each in allNComponents:
            if mc.objExists(each) == True:
                if this in mc.listHistory(each):
                    mc.delete(each)
    
def restLengthScaleBox(arg=None):
    if mc.checkBox('restLengthScale', q=True, v=True) == 1:
        nClothList = mc.ls(type='nCloth', fl=True)
        for each in nClothList:
            mc.setAttr(each + '.restLengthScale', 0)
    else:
        nClothList = mc.ls(type='nCloth', fl=True)
        for each in nClothList:
            mc.setAttr(each + '.restLengthScale', 1)
    applyValues()
    
def muscleTool(arg=None):
    windowName = "Muscle_Tool"
    windowSize = (310, 360)
    if (mc.window(windowName , exists=True)):
        mc.deleteUI(windowName)
    window = mc.window( windowName, title= windowName, widthHeight=(windowSize[0], windowSize[1]) )

    mc.columnLayout( "mainColumn", adjustableColumn=True) 

    mc.rowLayout(nc=3)
    mc.button(l='Make Rigid', w=100, bgc=(0,.3,0.2), c=makeRigid)
    mc.button(l='Remove nRigid', w=100, bgc=(.3,0,0), c=clearNRigid)
    mc.button(l='Select Rigids', w=100, c=selectNRigid)
    mc.setParent('..')
    mc.rowLayout(nc=3)
    mc.button(l='Make Muscle', w=100, bgc=(0,.3,0.2), c=makeMuscle)
    mc.button(l='Remove nCloth', w=100, bgc=(.3,0,0), c=clearNCloth)
    mc.button(l='Select Cloths', w=100, c=selectNCloth)
    mc.setParent('..')

    mc.rowLayout(w=350, nc=2, rowAttach=(2, 'top', 0))
    mc.columnLayout()
    mc.text(l='---------------nCloth-----------')
    mc.button(l='Collision Solve Preset', c=applyCollisionSolveValues)
    mc.button(l='Expand and Fill Preset', c=applyFillValues)

    mc.rowLayout(nc=2)
    mc.floatField('clothThickness', v=.01, w=40, pre=3, min=0, cc=applyValues)
    mc.text(l='Thickness')
    mc.setParent('..')

    mc.rowLayout(nc=2)
    mc.intField('stretchResistance', v=20, w=40, min=0, cc=applyValues)
    mc.text(l='Stretch Resistance')
    mc.setParent('..')

    mc.rowLayout(nc=2)
    mc.floatField('rigidity', v=0, w=40, pre=1, min=0, cc=applyValues)
    mc.text(l='Rigidity')
    mc.setParent('..')

    mc.rowLayout(nc=3)
    mc.intField('pressure', v=0, w=40, cc=applyValues)
    mc.text(l='Pressure     ')
    mc.checkBox('restLengthScale', l='Alt', cc=restLengthScaleBox)
    if mc.checkBox('restLengthScale', q=True, v=True) == 0:
        mc.checkBox('restLengthScale', e=True, en=False)
    mc.setParent('..')

    mc.rowLayout(nc=2)
    mc.floatField('pushOut', v=1, w=40, pre=1, min=0, cc=applyValues)
    mc.text(l='Push Out')
    mc.setParent('..')
    
    mc.rowLayout(nc=2)
    mc.text(l='---------------nRigid------------')
    mc.setParent('..')
    
    mc.rowLayout(nc=2)
    mc.floatField('rigidThickness', v=.01, w=40, pre=3, min=0, cc=applyValuesRigid)
    mc.text(l='Rigid Thickness')
    mc.setParent('..')

    mc.rowLayout(nc=2)
    mc.floatField('pushOutRigid', v=1, w=40, pre=1, min=0, cc=applyValuesRigid)
    mc.text(l='Push Out')
    mc.setParent('..')

    mc.rowLayout(nc=2)
    mc.intField('crossoverPushRigid', v=1, w=40, min=0, cc=applyValuesRigid)
    mc.text(l='Crossover Push')
    mc.setParent('..')
    
    mc.rowLayout(nc=2)
    mc.text(l='------------------------------------')
    mc.setParent('..')

    mc.rowLayout(nc=2)
    mc.button(l='Relax Edges', c=relaxEdges)
    mc.button(l='Inflate Edges', c=moveAlongNormal)
    mc.setParent('..')
    mc.setParent('..')
    
    
    mc.columnLayout()
    mc.text(l='---------------Skin-------------')
    mc.rowLayout(nc=1)
    mc.button(l='Reverse Normal', w=100, c=reverseNormal)
    mc.setParent('..')
    
    mc.columnLayout()
    mc.text(l='-------------Freeze-------------')
    mc.rowLayout(nc=2)
    mc.button(l=' BlendShape ', bgc=(.1,.4,.4), c=freezeSetup)
    mc.button(l=' Paint Weight ', bgc=(.1,.3,.3), c=paintWeight)
    mc.setParent('..')
    mc.rowLayout(nc=1)
    mc.button(l=' Transform Constraint', bgc=(0,.3,0.2), c=transformConstraint)
    mc.setParent('..')
    mc.rowLayout(nc=1)
    mc.button(l=' Remove Constraint', bgc=(.3,0,0), c=removeConstraint)
    mc.setParent('..')
    
    mc.columnLayout()
    mc.text(l='---------------Time-------------')
    mc.rowLayout(nc=2)
    mc.button(l='<<- RESET', c=timeReset)
    mc.button(l='NEXT FRAME >', bgc=(0,.5,0.3), c=timeNext)
    mc.setParent('..')
    mc.rowLayout(nc=2)
    mc.button('playButton', l=' PLAY >> ', bgc=(0,.3,0.2), c=timePlay)
    mc.button(l=' > STOP < ', bgc=(.3,0,0), c=timeStop)
    mc.setParent('..')

    mc.columnLayout()
    mc.text(l='-------------Shapes-------------')
    mc.rowLayout(nc=1)
    mc.button(l='Toggle Input/nCloth Mesh', bgc=(.1,.3,0.3), c=toggleIO)
    mc.setParent('..')
    mc.rowLayout(nc=1)
    mc.button(l='Delete Intermediate Object', bgc=(.3,0,0), c=deleteIO)
    mc.setParent('..')
    mc.rowLayout(nc=1)
    mc.button(l='Fix Shape Name', bgc=(.2,.2,0.2), c=fixShapeName)
    mc.setParent('..')
    
    mc.showWindow( windowName )
    gMainWindow = mel.eval('$tmpVar=$gMainWindow')
    mc.window( windowName, edit=True, widthHeight=(windowSize[0], windowSize[1]) )
muscleTool()

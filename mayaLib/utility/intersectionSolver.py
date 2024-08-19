#!/usr/bin/env python
# -*- coding: utf-8 -*-

#********************************
# Copyright 2021 Toshi Kosaka
#
# GORIOSHI SCRIPTS
#********************************
'''****************************************************************************
*** intersectionSolver.py
*** v1.1 - added Fix NaN Verts button
***
*** Scripted in Maya 2018/2022
*** 
*** Please do not copy, distribute, or modify without permission of the author.
****************************************************************************'''

import maya.cmds as mc
import maya.mel as mel
import time
windowName = 'intersectionSolver'

def createPfxToon(arg=None):
    sel = mc.ls(mc.listRelatives(c=True), fl=True)
    if mc.objExists('pfxToon_set') !=True:
        mc.sets(sel, n='pfxToon_set')
    else:
        mc.sets(sel, e=True, fe='pfxToon_set')
    target = mc.sets('pfxToon_set', q=True)
    
    if mc.objExists('pfxToonCollisionDetectShape') != True:
        pfxToonNode = mc.createNode('pfxToon', n='pfxToonCollisionDetectShape', p='pfxToonCollisioneDetect')
        mc.setAttr(pfxToonNode +'.profileLines', 0)
        mc.setAttr(pfxToonNode +'.creaseLines', 0)
        mc.setAttr(pfxToonNode +'.intersectionLines', 1)
        mc.setAttr(pfxToonNode +'.displayPercent', 100)
        mc.setAttr(pfxToonNode +'.intersectionColor',1,0,0, type='double3')
        mc.setAttr(pfxToonNode +'.selfIntersect', 1)
    else:
        pfxToonNode = 'pfxToonCollisionDetectShape'

    i=0
    for each in target:
        mc.connectAttr(each + '.outMesh', pfxToonNode + '.inputSurface[' + str(i) + '].surface', f=True)
        mc.connectAttr(each + '.worldMatrix[0]', pfxToonNode + '.inputSurface[' + str(i) + '].inputWorldMatrix', f=True)
        i+=1

def removePfxToon(arg=None):
    if mc.objExists('pfxToon_set') == True:
        mc.delete('pfxToon_set')
    if mc.objExists('pfxToonCollisionDetect') == True:
        mc.delete('pfxToonCollisionDetect')

def nearClipChange(arg=None):
    clipVal = mc.floatSlider('nearClipSlider', q=True, v=True)
    curCam = 'perspShape'
    for each in mc.getPanel(type='modelPanel'):
        curCam = mc.modelEditor(each, q=True, av=True, cam=True)
    mc.setAttr(curCam + '.nearClipPlane', clipVal)
    mc.text('nearClipValue', e=True, l=str(round(clipVal,3)))

def displayWidthFieldChange(arg=None):
    val = mc.floatField('lineWidth', q=True, v=True)
    mc.setAttr('pfxToonCollisionDetectShape.lineWidth', val)
    mc.floatSlider('displayWidthSlider', e=True, v=val)
    
def displayWidthSliderChange(arg=None):
    val = mc.floatSlider('displayWidthSlider', q=True, v=True)
    mc.setAttr('pfxToonCollisionDetectShape.lineWidth', val)
    mc.floatField('lineWidth', e=True, v=val)

def findCollision(null):
    sel = mc.ls(sl=True, fl=True)
    for each in sel:
        mc.polyTriangulate(each, ch=1)
    mc.ls(sel)
    rigidBodyStr = mc.rigidBody(sel, active=True, m=1, dp=0, sf=0.2, df=0.2, b=0.6, l=0, tf=200, iv=(0,0,0), iav=(0,0,0), c=0, pc=0, i=(0,0,0), imp=(0,0,0), si=(0,0,0), sio='none')

    mc.setAttr('rigidSolver.collisionTolerance', 0.0001)
    mc.select(cl=True)
    mc.currentTime(1);
    mc.currentTime(2);
    mc.currentTime(1);

    global collisionResults
    collisionResults = mc.ls(sl=True)

    mc.delete('rigidBody*')
    mc.delete('rigidSolver')
    mc.delete('polyTriangulate*')
    mc.select(sel)
    mc.DeleteHistory()

    mc.select(collisionResults, r=True)

def selectResults(null):
    global collisionResults
    mc.select(collisionResults)

def applyCollision(none):
    flushCBB()

    start = time.time()

    selOrig = mc.ls(sl=True, fl=True)
    selDup = []
    for each in selOrig:
        selDup.append(mc.duplicate(each, n=each+'_cbbdup')[0])

    dummyPlane = mc.polyPlane(n='dummy_plane', ch=1, o=1, w=1, h=1, sw=1, sh=1, cuv=2)
    mc.setAttr(dummyPlane[0] + '.ty', 999999)
    selDup.insert(0, dummyPlane[0])

    setsList = []
    for each in selDup:
        setsList.append(mc.sets(mc.polyListComponentConversion(each, tf=True), n=each+'_setsCBB'))

    boolMeshName = 'tempMeshBool'
    mc.polyCBoolOp(selDup, op=1, ch=1, n=boolMeshName)

    newSetsList = []
    for i in range(0, len(setsList)):
        newSetsList.append(mc.sets(setsList[i], q=True))
        newSetsList[i] = [x for x in newSetsList[i] if not 'transform' in x]

    mc.select(cl=True)

    #evaluate if selected are full or partial shell, and separate
    for each in newSetsList:
        mc.select(each)
        check1 = mc.polyEvaluate(fc=True)
        mc.ConvertSelectionToShell()
        check2 = mc.polyEvaluate(fc=True)
        if check1 != check2:
            mc.polyChipOff(each, ch=1, kft=1, dup=0, off=0)
    mc.polySeparate(boolMeshName, ch=1)

    #update new sets list
    newSetsList = []
    for i in range(0, len(setsList)):
        newSetsList.append(mc.sets(setsList[i], q=True))
        newSetsList[i] = [x for x in newSetsList[i] if not 'transform' in x]

    mc.DeleteHistory()

    for j in range(0, len(setsList)):
        target = newSetsList[j][0]
        mc.rename(target.split('.')[0], setsList[j].split('_setsCBB')[0])

    mc.delete(dummyPlane[0])
    setsList.pop(0)
    selDup.pop(0)
    allEdges = mc.polyListComponentConversion(te=True)

    fillFaces = []
    for each in allEdges:
        currentFace = mc.polyEvaluate(each.split('.')[0], f=True)
        mc.polyCloseBorder(each, ch=0)
        updatedFace = mc.polyEvaluate(each.split('.')[0], f=True)
        filledFaceNum = updatedFace - currentFace
        mc.select(cl=True)
        for i in range(1, filledFaceNum+1):
            fillFaces.append(each.split('.')[0] + '.f[' + str(updatedFace-i) + ']')

    gapDistanceFloat = mc.floatField('gapDistanceFloat', q=True, v=True)*-1
    for each in fillFaces:
        mc.select(each)
        mc.ConvertSelectionToVertices()
        mc.GrowPolygonSelectionRegion()
        verts = mc.ls(sl=True, fl=True)
        vertsMoveDist = []
        for i in range(0, len(verts)):
            vertsMoveDist.append(gapDistanceFloat)
        mc.moveVertexAlongDirection(verts, n=(vertsMoveDist))

    for i in range(0, len(selOrig)):
        mc.transferAttributes(selDup[i], selOrig[i], pos=1, nml=0, uvs=2, col=2, spa=0, sus='map1', tus='map1', sm=3, fuv=0, clb=1)

    mc.select(selOrig)
    mc.DeleteHistory()
    mc.delete(boolMeshName)

    end = time.time() - start

def relaxBrush(arg=None):
    mel.eval('setMeshSculptTool "Relax";')
    mel.eval('sculptMeshCacheCtx -e -constrainToSurface true sculptMeshCacheContext;')

def relaxFlood(arg=None):
    mel.eval('setMeshSculptTool "Relax";')
    mel.eval('sculptMeshCacheCtx -e -constrainToSurface true sculptMeshCacheContext;')
    mel.eval('sculptMeshFlood; sculptMeshFlood; sculptMeshFlood;')
    mel.eval('SelectToolOptionsMarkingMenu;')
    mel.eval('buildSelectMM; SelectToolOptionsMarkingMenuPopDown;')

def flushCBB(arg=None):
    if mc.objExists('tempMeshBool*'):
        mc.DeleteHistory('tempMeshBool*')
        mc.delete('tempMeshBool*')
    if mc.objExists('dummy_plane*'):
        mc.delete('dummy_plane*')
    if mc.objExists('*_setsCBB*'):
        mc.delete('*_setsCBB*')
    if mc.objExists('*_cbbdup*'):
        mc.delete('*_cbbdup*')
    if mc.objExists('rigidBody*'):
        mc.delete('rigidBody*')
    if mc.objExists('rigidSolver'):
        mc.delete('rigidSolver')

def fixNanVerts(arg=None):
    sel = mc.listRelatives(mc.ls(sl=True, fl=True), c=True, type='mesh')
    selVerts = mc.ls(mc.polyListComponentConversion(sel, tv=True), fl=True)
    for each in selVerts:
        if str(mc.xform(each.split('.vtx[')[0] + '.pnts[' + each.split('.vtx[')[1], q=True, t=True)[0]) == 'nan':
            mc.setAttr(each.split('.vtx[')[0] + '.pnts[' + each.split('.vtx[')[1], 0, 0, 0)
            
def intersectionSolver():
    global windowName
    global isFaceMode
    
    isFaceMode = 0
    windowSize = (250, 320)
    if (mc.window(windowName , exists=True)):
        mc.deleteUI(windowName)
    IS_window = mc.window( windowName, title='Intersection_Solver', widthHeight=(windowSize[0], windowSize[1]) )
    
    mc.frameLayout('Intersection Solver v1.0', w=250, bgc=(.1,.1,.1))
    mc.columnLayout( "mainColumn", adjustableColumn=True )
    mc.rowLayout(parent='mainColumn', nc=3)

    curCam = 'perspShape'
    for each in mc.getPanel(type='modelPanel'):
        curCam = mc.modelEditor(each, q=True, av=True, cam=True)
    ncVal = mc.getAttr(curCam + '.nearClipPlane')
    
    mc.text(l='Cam Near Clip : ')
    mc.floatSlider('nearClipSlider', w=100, min=0.001, max=100, value=ncVal, s=0.001, dc=nearClipChange)
    mc.text('nearClipValue', l=str(round(ncVal,3)))
    mc.setParent('..')
    mc.text(l='=================================', parent="mainColumn")
    mc.setParent('..')
    mc.rowLayout(p='mainColumn', nc=1)
    mc.button(l='Show Intersections on Selected', c=createPfxToon, bgc=(0,.3,0.2))
    mc.setParent('..')
    mc.rowLayout(p='mainColumn', nc=3)
    mc.text(l='Diplay Width: ')
    mc.floatField('lineWidth', w=30, min=0, max=100, v=1, pre=2, cc=displayWidthFieldChange)
    mc.floatSlider('displayWidthSlider', w=100, min=0.001, max=100, value=0.001, dc=displayWidthSliderChange)
    mc.setParent('..')
    mc.button(l='Remove pfxToon', c=removePfxToon, bgc=(.3,0,0))
    
    mc.columnLayout( "mainColumn", rowSpacing=0, columnWidth=250,)
    mc.text(l='=================================', parent="mainColumn")
    mc.text(l='Make sure UV is clean, history is deleted')
    
    mc.rowLayout("nameRowLayout04", numberOfColumns = 3, parent = "mainColumn")
    mc.button(l='Inspect Selected', parent = "nameRowLayout04", command=findCollision, bgc=(0,.3,0.2))
    mc.button('Select Results', parent='nameRowLayout04', command=selectResults)
    
    mc.rowLayout("nameRowLayout01", numberOfColumns = 2, parent = "mainColumn")
    mc.text(l='Gap Distance: ')
    mc.floatField('gapDistanceFloat', w=40, v=.1, pre=2, parent='nameRowLayout01')
    
    mc.rowLayout(numberOfColumns = 2, parent = "mainColumn")
    mc.button( label='Solve Intersection', h=30, command = applyCollision, bgc=(0,.2,.4))
    mc.button(l='Clean up junk Caused by Error', command=flushCBB, bgc=(.3,0,0))

    mc.text(l='=================================', parent="mainColumn")
    mc.rowLayout("nameRowLayout03", numberOfColumns = 3, parent = "mainColumn")
    mc.button( label='Relax Brush', parent = "nameRowLayout03", command = relaxBrush)
    mc.button( label='Relax Flood', parent = "nameRowLayout03", command = relaxFlood)
    mc.button( label='Fix NaN Verts', parent = "nameRowLayout03", command = fixNanVerts)
    
    mc.showWindow(IS_window)
    
if __name__ == "__main__":
    intersectionSolver()
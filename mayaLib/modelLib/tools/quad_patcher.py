#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ********************************
# Copyright 2021 Toshi Kosaka
#
# GORIOSHI SCRIPTS
# ********************************
"""****************************************************************************
*** quad_patcher.py
***
*** version: 1.0
*** Scripted in Maya 2020
*** Tested in Maya 2020 and 2022
*** 
*** Please do not copy, distribute, or modify without permission of the author.
****************************************************************************"""

import maya.cmds as mc
import maya.mel as mel
import maya.OpenMaya as om
import random

windowName = "quadPatcher"


def faceChecker(arg=None):
    sel = mc.ls(sl=True, fl=True)
    if mc.polyEvaluate(sel, ec=True) or mc.polyEvaluate(sel, vc=True) > 0 > 0:
        mc.error("No Faces are selected")
    if mc.polyEvaluate(sel, fc=True) == 0:
        mc.error("No faces are selected")
    mc.select(sel)
    for each in mc.ls(mc.polyListComponentConversion(sel, te=True), fl=True):
        currentEdge = []
        currentEdge = mc.polySelect(eb=int(each.split("[")[1].split("]")[0]), q=True)
        if currentEdge != None:
            mc.error("Face cannot be adjacent to the border")
    mc.ConvertSelectionToEdgePerimeter()
    if len(mc.ls(sl=True, fl=True)) % 2 != 0:
        mc.select(sel)
        mc.error("Selection edge perimeter count is odd. Needs even for quads.")
    mc.select(sel)


def edgeChecker(arg=None):
    sel = mc.ls(sl=True, fl=True)
    if mc.polyEvaluate(sel, fc=True) or mc.polyEvaluate(sel, vc=True) > 0:
        mc.error("None edges selected for Edge Border Mode")
    if mc.polyEvaluate(sel, ec=True) == 0:
        mc.error("No Edges are selected for Edge Boder Mode")
    if len(
        mc.ls(
            mc.polySelect(q=True, eb=int(sel[0].split("[")[1].split("]")[0]), ass=True),
            fl=True,
        )
    ) != len(sel):
        mc.error("Complete edge border is not selected")
    if len(sel) % 2 != 0:
        mc.error("Edge count is odd. Needs even for quads.")


def quadPatchInit(arg=None):
    if isFaceMode == 0:
        edgeChecker()
    mc.button("edgeBorderMode", label="Edge Border Mode", en=0, e=True)
    mc.button("faceMode", label="Face Mode", en=0, e=True)
    mc.button("extrudeMode", label="Extrude Mode", en=0, e=True)
    mc.intSliderGrp("extrudeSlider", en=0, e=True)
    # mc.button('resetButton', en=0, e=True)
    global objNameDup
    global objNameOrig
    global sideABridgeNode
    global sideBBridgeNode
    global sideCBridgeNode
    global orderedEdges
    global orderedEdgeComponents
    global sideAEdges
    global orderedEdgesExtended
    global orderedEdgesComponentsExtended
    global sideAEdgeComponents
    global sideALen
    global sideBLen
    global sideBRemoveSet
    global sideCRemoveSet
    global divOffset
    global dupBaseVerts
    global dupEdgesSet
    global newCreatedVerts
    global insetNode
    global relaxNodes
    global smoothNodesOrig
    global smoothNodes
    global dupFacesToHide
    global selEdgesOrig
    global FMtransferAttributesNode
    global wrapBaseMesh

    # Source object
    selEdgesOrig = mc.ls(sl=True, fl=True)
    selVertsOrig = mc.polyListComponentConversion(selEdgesOrig, tv=True)
    selFacesOrig = mc.polyListComponentConversion(selVertsOrig, tf=True)
    objNameOrig = selEdgesOrig[0].split(".")[0]
    allFacesOrig = mc.polyListComponentConversion(objNameOrig, tf=True)
    # Duplicate
    objNameDup = mc.duplicate(
        objNameOrig,
        n="quadPatcher" + str(random.randint(1000, 9999)) + "_" + objNameOrig,
    )[0]
    selEdges = []
    for each in selEdgesOrig:
        selEdges.append(objNameDup + "." + each.split(".")[1])
    mc.select(selEdges)
    dupEdgesSet = mc.sets(
        n="quadPatcher" + str(random.randint(1000, 9999)) + "_" + "dupSet"
    )
    selVerts = mc.ls(mc.polyListComponentConversion(selEdges, tv=True), fl=True)
    selFaces = mc.ls(mc.polyListComponentConversion(selVerts, tf=True), fl=True)
    dupFaceDeleteSet = [
        x
        for x in mc.ls(mc.polyListComponentConversion(objNameDup, tf=True), fl=True)
        if x not in selFaces
    ]
    mc.delete(dupFaceDeleteSet)
    mc.select(dupEdgesSet)
    selEdges = mc.ls(sl=True, fl=True)
    dupBaseVerts = mc.ls(mc.polyListComponentConversion(objNameDup, tv=True), fl=True)

    sideALen = int(len(selEdges) / 4)
    sideBLen = int((len(selEdges) - (sideALen * 2)) / 2)
    if len(selEdges) == 12:
        sideALen = 1
        sideBLen = 5
    if len(selEdges) == 10:
        sideALen = 1
        sideBLen = 4
    if len(selEdges) == 8:
        sideALen = 1
        sideBLen = 3

    orderedEdges = initiate(selEdges)
    orderedEdgeComponents = []
    for each in orderedEdges:
        orderedEdgeComponents.append(objNameDup + ".e[" + str(each) + "]")

    # Wrap dup edges to original obj
    mc.select(selEdges, objNameOrig)
    mc.CreateWrap()
    wrapNode = mc.listConnections(objNameOrig, type="wrap")[0]
    wrapBaseMesh = mc.listConnections(wrapNode + ".basePoints")
    mc.setAttr(wrapNode + ".weightThreshold", 0)
    mc.setAttr(wrapNode + ".maxDistance", 1)
    mc.setAttr(wrapNode + ".autoWeightThreshold", 1)
    mc.setAttr(wrapNode + ".exclusiveBind", 0)

    # SideA
    orderedEdgesExtended = orderedEdges + orderedEdges + orderedEdges
    orderedEdgesComponentsExtended = (
        orderedEdgeComponents + orderedEdgeComponents + orderedEdgeComponents
    )

    mc.intSliderGrp("rotationSlider", e=True, v=sideALen)
    offsetNum = sideALen * 2
    mc.intSliderGrp("rotationSlider", e=True, v=offsetNum)
    sideAEdges = (
        orderedEdgesExtended[0 + offsetNum : sideALen + offsetNum]
        + orderedEdgesExtended[
            sideALen + sideBLen + offsetNum : sideALen * 2 + sideBLen + offsetNum
        ]
    )
    sideAEdgeComponents = (
        orderedEdgesComponentsExtended[0 + offsetNum : sideALen + offsetNum]
        + orderedEdgesComponentsExtended[
            sideALen + sideBLen + offsetNum : sideALen * 2 + sideBLen + offsetNum
        ]
    )

    # SideB
    sideBRemove = [
        orderedEdgesComponentsExtended[0 + offsetNum + sideALen],
        orderedEdgesComponentsExtended[sideALen + offsetNum + sideBLen - 1],
    ]
    mc.select(sideBRemove)
    sideBRemoveSet = mc.sets(
        n="quadPatcher" + str(random.randint(1000, 9999)) + "_" + "sideBRemoveSet"
    )

    # SideC
    sideCRemove = [
        orderedEdgesComponentsExtended[0 + offsetNum + (2 * sideALen) + sideBLen],
        orderedEdgesComponentsExtended[(2 * sideALen) + offsetNum + (2 * sideBLen) - 1],
    ]
    mc.select(sideCRemove)
    sideCRemoveSet = mc.sets(
        n="quadPatcher" + str(random.randint(1000, 9999)) + "_" + "sideCRemoveSet"
    )

    # Transform Component
    smoothNodes = []
    for i in range(0, 3):
        smoothNodes.append(
            mc.polyMoveEdge(selEdgesOrig, ch=1, random=0, localCenter=0, lsx=1)[0]
        )

    # Make SideA Bridge
    mc.select(sideAEdgeComponents, r=True)
    sideABridgeNode = mc.polyBridgeEdge(
        divisions=sideBLen - 3,
        ch=True,
        twist=0,
        taper=1,
        curveType=0,
        smoothingAngle=30,
    )

    # Make SideB Bridge
    sideBEdgeLoop = mc.ls(
        mc.polySelect(q=True, eb=orderedEdgesExtended[offsetNum + sideALen], ass=True),
        fl=True,
    )
    sideBEdgeRemove = mc.sets(sideBRemoveSet, q=True)
    sideBEdgeComponents = [x for x in sideBEdgeLoop if x not in sideBEdgeRemove]
    mc.select(sideBEdgeComponents, r=True)
    sideBBridgeNode = mc.polyBridgeEdge(
        divisions=0, ch=True, twist=0, taper=1, curveType=0, smoothingAngle=30
    )

    # Make SideC Bridge
    sideCEdgeLoop = mc.ls(
        mc.polySelect(
            q=True,
            eb=orderedEdgesExtended[offsetNum + (2 * sideALen) + sideBLen],
            ass=True,
        ),
        fl=True,
    )
    sideCEdgeRemove = mc.sets(sideCRemoveSet, q=True)
    sideCEdgeComponents = [x for x in sideCEdgeLoop if x not in sideCEdgeRemove]
    mc.select(sideCEdgeComponents, r=True)
    sideCBridgeNode = mc.polyBridgeEdge(
        divisions=0, ch=True, twist=0, taper=1, curveType=0, smoothingAngle=30
    )

    mc.select(cl=True)
    mc.intSliderGrp(
        "rotationSlider", e=True, v=sideALen * 2, max=len(orderedEdges), min=0
    )
    mc.intSliderGrp(
        "divisionSlider",
        e=True,
        v=mc.getAttr(sideABridgeNode[0] + ".divisions"),
        max=(sideBLen - 2) * 2 - (sideBLen - sideALen),
    )
    divOffset = 0

    # new verts faces
    newCreatedVerts = [
        x
        for x in mc.ls(mc.polyListComponentConversion(objNameDup, tv=True), fl=True)
        if x not in dupBaseVerts
    ]
    newCreatedFaces = mc.ls(
        mc.polyListComponentConversion(newCreatedVerts, tf=True), fl=True
    )

    # inset Extrude
    insetNode = mc.polyExtrudeFacet(newCreatedFaces, nds=1, off=0, d=0)

    # Average Vertex
    relaxNodes = []
    for i in range(0, 10):
        relaxNodes.append(mc.polyAverageVertex(newCreatedVerts, i=10, ch=1)[0])

    # Transfer Attributes FACE MODE
    if isFaceMode == 1:
        FMtransferAttributesNode = mc.transferAttributes(
            liveObj,
            objNameDup,
            pos=1,
            nml=0,
            uvs=1,
            suv="map1",
            tuv="map1",
            col=2,
            spa=0,
            sus="map1",
            tus="map1",
            sm=0,
            fuv=0,
            clb=1,
        )
        mc.transferAttributes(
            liveObj,
            selEdgesOrig,
            pos=1,
            nml=0,
            uvs=1,
            suv="map1",
            tuv="map1",
            col=2,
            spa=0,
            sus="map1",
            tus="map1",
            sm=3,
            fuv=0,
            clb=1,
        )

    dupFacesToHide = [
        x
        for x in mc.ls(mc.polyListComponentConversion(objNameDup, tf=True), fl=True)
        if x not in newCreatedFaces
    ]
    mc.select(dupFacesToHide)
    mc.HideSelectedObjects()
    mc.select(cl=True)


def rotateSlider(arg=None):
    mc.undoInfo(swf=False)

    offsetNum = mc.intSliderGrp("rotationSlider", q=True, v=True)

    # Node state off B and C bridges and inset
    mc.setAttr(sideBBridgeNode[0] + ".nodeState", 1)
    mc.setAttr(sideCBridgeNode[0] + ".nodeState", 1)
    mc.setAttr(insetNode[0] + ".nodeState", 1)
    if isFaceMode == 1:
        mc.setAttr(FMtransferAttributesNode[0] + ".nodeState", 0)

    # sideA Bridge First
    sideAEdges = (
        orderedEdgesExtended[0 + offsetNum : sideALen + offsetNum + divOffset]
        + orderedEdgesExtended[
            sideALen
            + sideBLen
            + offsetNum : sideALen * 2
            + sideBLen
            + offsetNum
            + divOffset
        ]
    )
    sideAEdgeComponents = (
        orderedEdgesComponentsExtended[0 + offsetNum : sideALen + offsetNum]
        + orderedEdgesComponentsExtended[
            sideALen + sideBLen + offsetNum : sideALen * 2 + sideBLen + offsetNum
        ]
    )
    sideAEdgesString = ""
    for each in sideAEdges:
        sideAEdgesString = sideAEdgesString + " " + '"e[' + str(each) + ']"'
    inputComponentStrA = (
        'setAttr -type "componentList" ( "'
        + sideABridgeNode[0]
        + '.inputComponents" ) '
        + str(len(sideAEdges))
        + " "
        + sideAEdgesString
    )

    mel.eval(inputComponentStrA)

    # sideB Adjust
    sideBEdgeRemove = [
        orderedEdgesComponentsExtended[0 + offsetNum + sideALen + divOffset],
        orderedEdgesComponentsExtended[sideALen + offsetNum + sideBLen - 1],
    ]
    sideBEdgeLoop = mc.ls(
        mc.polySelect(
            objNameDup,
            q=True,
            eb=orderedEdgesExtended[offsetNum + sideALen + divOffset],
            ass=True,
        ),
        fl=True,
    )
    sideBEdgeComponents = [x for x in sideBEdgeLoop if x not in sideBEdgeRemove]
    sideBEdgesString = ""
    for each in sideBEdgeComponents:
        sideBEdgesString = sideBEdgesString + " " + '"' + each.split(".")[1] + '"'
    inputComponentStrB = (
        'setAttr -type "componentList" ( "'
        + sideBBridgeNode[0]
        + '.inputComponents" ) '
        + str(len(sideBEdgeComponents))
        + " "
        + sideBEdgesString
    )

    # sideC Adjust
    sideCEdgeRemove = [
        orderedEdgesComponentsExtended[
            0 + offsetNum + (2 * sideALen) + sideBLen + divOffset
        ],
        orderedEdgesComponentsExtended[(2 * sideALen) + offsetNum + (2 * sideBLen) - 1],
    ]
    sideCEdgeLoop = mc.ls(
        mc.polySelect(
            objNameDup,
            q=True,
            eb=orderedEdgesExtended[
                offsetNum + (2 * sideALen) + sideBLen + 1 + divOffset
            ],
            ass=True,
        ),
        fl=True,
    )
    sideCEdgeComponents = [x for x in sideCEdgeLoop if x not in sideCEdgeRemove]
    sideCEdgesString = ""
    for each in sideCEdgeComponents:
        sideCEdgesString = sideCEdgesString + " " + '"' + each.split(".")[1] + '"'
    inputComponentStrC = (
        'setAttr -type "componentList" ( "'
        + sideCBridgeNode[0]
        + '.inputComponents" ) '
        + str(len(sideCEdgeComponents))
        + " "
        + sideCEdgesString
    )

    # Execute Adjustment
    mel.eval(inputComponentStrB)
    mc.setAttr(sideBBridgeNode[0] + ".nodeState", 0)
    mel.eval(inputComponentStrC)
    mc.setAttr(sideCBridgeNode[0] + ".nodeState", 0)
    # Inset status check
    insetStatus = mc.checkBox("insetCheckbox", q=True, v=True)
    if insetStatus == 1:
        mc.setAttr(insetNode[0] + ".nodeState", 0)
    if isFaceMode == 1:
        mc.setAttr(FMtransferAttributesNode[0] + ".nodeState", 0)


def divideSlider(arg=None):
    global divOffset
    mc.undoInfo(swf=False)

    divNum = mc.intSliderGrp("divisionSlider", q=True, v=True)
    offsetNum = mc.intSliderGrp("rotationSlider", q=True, v=True)

    # Node state off B and C bridges and inset
    mc.setAttr(sideBBridgeNode[0] + ".nodeState", 1)
    mc.setAttr(sideCBridgeNode[0] + ".nodeState", 1)
    mc.setAttr(insetNode[0] + ".nodeState", 1)

    # sideA Bridge divisions set
    mc.setAttr(sideABridgeNode[0] + ".divisions", divNum)

    divOffset = sideALen - 3 - divNum + (sideBLen - sideALen)

    sideAEdges = (
        orderedEdgesExtended[0 + offsetNum : sideALen + offsetNum + divOffset]
        + orderedEdgesExtended[
            sideALen
            + sideBLen
            + offsetNum : sideALen * 2
            + sideBLen
            + offsetNum
            + divOffset
        ]
    )
    sideAEdgeComponents = (
        orderedEdgesComponentsExtended[0 + offsetNum : sideALen + offsetNum]
        + orderedEdgesComponentsExtended[
            sideALen + sideBLen + offsetNum : sideALen * 2 + sideBLen + offsetNum
        ]
    )
    sideAEdgesString = ""
    for each in sideAEdges:
        sideAEdgesString = sideAEdgesString + " " + '"e[' + str(each) + ']"'
    inputComponentStrA = (
        'setAttr -type "componentList" ( "'
        + sideABridgeNode[0]
        + '.inputComponents" ) '
        + str(len(sideAEdges))
        + " "
        + sideAEdgesString
    )

    mel.eval(inputComponentStrA)

    # sideB Bridge divisions
    sideBEdgeRemove = [
        orderedEdgesComponentsExtended[0 + offsetNum + sideALen + divOffset],
        orderedEdgesComponentsExtended[sideALen + offsetNum + sideBLen - 1],
    ]
    sideBEdgeLoop = mc.ls(
        mc.polySelect(
            objNameDup,
            q=True,
            eb=orderedEdgesExtended[offsetNum + sideALen + divOffset],
            ass=True,
        ),
        fl=True,
    )
    sideBEdgeComponents = [x for x in sideBEdgeLoop if x not in sideBEdgeRemove]
    sideBEdgesString = ""
    for each in sideBEdgeComponents:
        sideBEdgesString = sideBEdgesString + " " + '"' + each.split(".")[1] + '"'
    inputComponentStrB = (
        'setAttr -type "componentList" ( "'
        + sideBBridgeNode[0]
        + '.inputComponents" ) '
        + str(len(sideBEdgeComponents))
        + " "
        + sideBEdgesString
    )

    # sideC Bridge divisions
    sideCEdgeRemove = [
        orderedEdgesComponentsExtended[
            0 + offsetNum + (2 * sideALen) + sideBLen + divOffset
        ],
        orderedEdgesComponentsExtended[(2 * sideALen) + offsetNum + (2 * sideBLen) - 1],
    ]
    sideCEdgeLoop = mc.ls(
        mc.polySelect(
            objNameDup,
            q=True,
            eb=orderedEdgesExtended[
                offsetNum + (2 * sideALen) + sideBLen + 1 + divOffset
            ],
            ass=True,
        ),
        fl=True,
    )
    sideCEdgeComponents = [x for x in sideCEdgeLoop if x not in sideCEdgeRemove]
    sideCEdgesString = ""
    for each in sideCEdgeComponents:
        sideCEdgesString = sideCEdgesString + " " + '"' + each.split(".")[1] + '"'
    inputComponentStrC = (
        'setAttr -type "componentList" ( "'
        + sideCBridgeNode[0]
        + '.inputComponents" ) '
        + str(len(sideCEdgeComponents))
        + " "
        + sideCEdgesString
    )

    mel.eval(inputComponentStrB)
    mc.setAttr(sideBBridgeNode[0] + ".nodeState", 0)
    mel.eval(inputComponentStrC)
    mc.setAttr(sideCBridgeNode[0] + ".nodeState", 0)
    # Inset status check
    insetStatus = mc.checkBox("insetCheckbox", q=True, v=True)
    if insetStatus == 1:
        mc.setAttr(insetNode[0] + ".nodeState", 0)
    updateRelax()
    updateInset()


def relaxSlider(arg=None):
    mc.undoInfo(swf=False)
    relaxNum = mc.intSliderGrp("relaxSlider", q=True, v=True)
    for each in relaxNodes:
        mc.setAttr(each + ".iterations", relaxNum)


def smoothBorderSlider(arg=None):
    mc.undoInfo(swf=False)
    smoothNum = (mc.floatSliderGrp("smoothBorderSlider", q=True, v=True) - 1) * -1
    for each in smoothNodes:
        mc.setAttr(each + ".localScaleX", smoothNum)


def activateInset(arg=None):
    mc.undoInfo(swf=False)
    updateInset()
    insetStatus = mc.checkBox("insetCheckbox", q=True, v=True)

    if insetStatus == 1:
        mc.setAttr(insetNode[0] + ".nodeState", 0)
        mc.setAttr(insetNode[0] + ".offset", 0)
        mc.setAttr(insetNode[0] + ".divisions", 1)
    else:
        mc.setAttr(insetNode[0] + ".nodeState", 1)

    updateRelax()
    mc.undoInfo(swf=True)


def insetDivMinus(arg=None):
    mc.undoInfo(swf=False)
    currentDivNum = mc.getAttr(insetNode[0] + ".divisions")

    if currentDivNum > 1:
        mc.setAttr(insetNode[0] + ".divisions", currentDivNum - 1)

    updateRelax()
    mc.undoInfo(swf=True)


def insetDivPlus(arg=None):
    mc.undoInfo(swf=False)
    currentDivNum = mc.getAttr(insetNode[0] + ".divisions")

    mc.setAttr(insetNode[0] + ".divisions", currentDivNum + 1)

    updateRelax()
    mc.undoInfo(swf=True)


def updateRelax(arg=None):
    newCreatedVerts = [
        x
        for x in mc.ls(mc.polyListComponentConversion(objNameDup, tv=True), fl=True)
        if x not in dupBaseVerts
    ]
    newVertsString = ""
    for each in newCreatedVerts:
        newVertsString = newVertsString + " " + '"' + each.split(".")[1] + '"'
    for each in relaxNodes:
        inputComponentString = (
            'setAttr -type "componentList" ( "'
            + each
            + '.inputComponents" ) '
            + str(len(newCreatedVerts))
            + " "
            + newVertsString
        )
        mel.eval(inputComponentString)


def updateInset(arg=None):
    newCreatedVerts = [
        x
        for x in mc.ls(mc.polyListComponentConversion(objNameDup, tv=True), fl=True)
        if x not in dupBaseVerts
    ]
    newCreatedFaces = mc.ls(
        mc.polyListComponentConversion(newCreatedVerts, tf=True), fl=True
    )
    newFacesString = ""
    for each in newCreatedFaces:
        newFacesString = newFacesString + " " + '"' + each.split(".")[1] + '"'
    inputComponentString = (
        'setAttr -type "componentList" ( "'
        + insetNode[0]
        + '.inputComponents" ) '
        + str(len(newCreatedFaces))
        + " "
        + newFacesString
    )
    mel.eval(inputComponentString)


def undoInfoON(arg=None):
    mc.undoInfo(swf=True)


def initiate(edges):
    mc.select(edges)
    sel = om.MSelectionList()
    om.MGlobal.getActiveSelectionList(sel)

    dag = om.MDagPath()
    component = om.MObject()
    sel.getDagPath(0, dag, component)

    mItEdge = om.MItMeshEdge(dag, component)

    checkedEdge = [int(mItEdge.index())]
    currentEdge = mItEdge.index()
    orderedList = [mItEdge.index()]
    for count in range(mItEdge.count()):
        while not mItEdge.isDone():
            if mItEdge.connectedToEdge(currentEdge):
                if mItEdge.index() not in checkedEdge:
                    orderedList.append(mItEdge.index())
                    currentEdge = mItEdge.index()
                    checkedEdge.append(int(mItEdge.index()))
                    break
            mItEdge.next()
        mItEdge.reset()
    return orderedList


def patchIt(arg=None):
    mc.delete(dupFacesToHide)
    facesOrig = mc.ls(mc.polyListComponentConversion(objNameDup, tf=True), fl=True)

    edgesToMerge = []
    for each in selEdgesOrig:
        edgesToMerge.append(each.split(".")[1])
    mergedObj = mc.polyUnite(
        [objNameOrig, objNameDup], ch=1, mergeUVSets=1, centerPivot=True
    )[0]
    objNameNew = mc.rename(mergedObj, objNameOrig)
    for each in mc.sets(dupEdgesSet, q=True):
        if each != "transform*":
            edgesToMerge.append(each.split(".")[1])
    if mc.objExists("quadPatcher*_*Set"):
        mc.delete("quadPatcher*_*Set")
    mc.DeleteHistory()
    vertsToMerge = []

    for each in edgesToMerge:
        vertsToMerge.append(objNameNew + "." + each)
    mc.polyMergeVertex(vertsToMerge, d=0.001, am=1, ch=1)

    if isFaceMode == 1:
        mc.delete(liveObj)
    if mc.objExists(wrapBaseMesh[0]):
        mc.delete(wrapBaseMesh)
    if mc.objExists("mergedObjSet"):
        mc.delete("mergedObjeSet")
    mc.DeleteHistory()
    mc.select(objNameNew)

    resetUI(windowName)


def resetUI(windw, *args):
    allwindows = mc.lsUI(type="window")
    for win in allwindows:
        if win == windw:
            mc.deleteUI(win)
    mc.evalDeferred(quadPatcherUI)


def faceModeInit(arg=None):
    faceChecker()
    mc.button("edgeBorderMode", label="Edge Border Mode", en=0, e=True)
    mc.button("faceMode", label="Face Mode", en=0, e=True)
    mc.button("extrudeMode", label="Extrude Mode", en=0, e=True)
    mc.intSliderGrp("extrudeSlider", en=0, e=True)
    # mc.button('resetButton', en=0, e=True)
    global liveObj
    global faceModeEdgeComponentsOrigSet
    global isFaceMode
    isFaceMode = 1

    selFacesOrig = mc.ls(sl=True, fl=True)
    objNameOrig = selFacesOrig[0].split(".")[0]

    liveObj = mc.duplicate(
        objNameOrig, n="quadPatcher" + str(random.randint(1000, 9999)) + "_live"
    )
    liveObjFaces = []
    for each in selFacesOrig:
        liveObjFaces.append(liveObj[0] + "." + each.split(".")[1])
    mc.delete(
        [
            x
            for x in mc.ls(mc.polyListComponentConversion(liveObj, tf=True), fl=True)
            if x not in liveObjFaces
        ]
    )
    mc.hide(liveObj)
    mc.ConvertSelectionToEdgePerimeter()
    faceModeEdgeComponentsOrigSet = mc.sets(
        n="quadPatcher" + str(random.randint(1000, 9999)) + "_" + objNameOrig + "Set"
    )

    mc.delete(selFacesOrig)
    mc.select(faceModeEdgeComponentsOrigSet)
    quadPatchInit()


def extrudeSlider(arg=None):
    mc.undoInfo(swf=False)
    endOffset = mc.intSliderGrp("extrudeSlider", q=True, v=True)

    mc.setAttr(closeSideABridgeNode[0] + ".nodeState", 1)
    mc.setAttr(closeSideBBridgeNode[0] + ".nodeState", 1)
    mc.setAttr(closeSideCBridgeNode[0] + ".nodeState", 1)

    divNumII = endOffset - 1

    # initial bridge
    sideAEdgesString = (
        '"'
        + str(sideB1Edges[endOffset].split(".")[1])
        + '" "'
        + str(sideC1Edges[endOffset].split(".")[1])
        + '"'
    )
    inputComponentStrI = (
        'setAttr -type "componentList" ( "'
        + closeBridgeNode[0]
        + '.inputComponents" ) '
        + "2"
        + " "
        + sideAEdgesString
    )
    mel.eval(inputComponentStrI)

    # side A
    newWholeBorder = mc.ls(
        mc.polySelect(selObj, q=True, eb=orderedEdges[0], ass=True), fl=True
    )
    tempXEdges = sideB1Edges[0:endOffset] + sideC1Edges[0:endOffset]
    tempXEdges = mc.ls(
        mc.polyListComponentConversion(
            mc.polyListComponentConversion(tempXEdges, tv=True), te=True
        ),
        fl=True,
    )
    newBridgeEdges = [x for x in newWholeBorder if x not in tempXEdges]
    sideAEdgesString = ""
    for each in newBridgeEdges:
        sideAEdgesString = sideAEdgesString + " " + '"' + each.split(".")[1] + '"'
    inputComponentStrA = (
        'setAttr -type "componentList" ( "'
        + closeSideABridgeNode[0]
        + '.inputComponents" ) '
        + str(len(newBridgeEdges))
        + " "
        + sideAEdgesString
    )

    mel.eval(inputComponentStrA)
    mc.setAttr(closeSideABridgeNode[0] + ".divisions", divNumII)
    mc.setAttr(closeSideABridgeNode[0] + ".nodeState", 0)

    # Side B
    extSideBEdgesI = sideB1Edges[0:endOffset]
    extSideBEdgesWhole = mc.ls(
        mc.polySelect(
            selObj,
            q=True,
            eb=int(extSideBEdgesI[0].split("[")[1].split("]")[0]),
            ass=True,
        ),
        fl=True,
    )
    extSideBRemove = mc.ls(
        mc.polyListComponentConversion(
            mc.polyListComponentConversion(extSideBEdgesI, tv=True), te=True
        ),
        fl=True,
    )
    extSideBEdgesII = [x for x in extSideBEdgesWhole if x not in extSideBRemove]
    sideBEdgeComponents = extSideBEdgesI + extSideBEdgesII
    sideBEdgesString = ""
    for each in sideBEdgeComponents:
        sideBEdgesString = sideBEdgesString + " " + '"' + each.split(".")[1] + '"'
    sideBEdgesString = (
        'setAttr -type "componentList" ( "'
        + closeSideBBridgeNode[0]
        + '.inputComponents" ) '
        + str(len(sideBEdgeComponents))
        + " "
        + sideBEdgesString
    )
    mel.eval(sideBEdgesString)
    mc.setAttr(closeSideBBridgeNode[0] + ".nodeState", 0)

    # Side C
    extSideCEdgesI = sideC1Edges[0:endOffset]
    extSideCEdgesWhole = mc.ls(
        mc.polySelect(
            selObj,
            q=True,
            eb=int(extSideCEdgesI[0].split("[")[1].split("]")[0]),
            ass=True,
        ),
        fl=True,
    )
    extSideCRemove = mc.ls(
        mc.polyListComponentConversion(
            mc.polyListComponentConversion(extSideCEdgesI, tv=True), te=True
        ),
        fl=True,
    )
    extSideCEdgesII = [x for x in extSideCEdgesWhole if x not in extSideCRemove]
    sideCEdgeComponents = extSideCEdgesI + extSideCEdgesII
    sideCEdgesString = ""
    for each in sideCEdgeComponents:
        sideCEdgesString = sideCEdgesString + " " + '"' + each.split(".")[1] + '"'
    sideCEdgesString = (
        'setAttr -type "componentList" ( "'
        + closeSideCBridgeNode[0]
        + '.inputComponents" ) '
        + str(len(sideCEdgeComponents))
        + " "
        + sideCEdgesString
    )
    mel.eval(sideCEdgesString)
    mc.setAttr(closeSideCBridgeNode[0] + ".nodeState", 0)


def extrudeModeInit(arg=None):
    mc.button("edgeBorderMode", label="Edge Border Mode", en=0, e=True)
    mc.button("faceMode", label="Face Mode", en=0, e=True)
    mc.button("extrudeMode", label="Extrude Mode", en=0, e=True)
    mc.intSliderGrp("rotationSlider", en=0, e=True)
    mc.intSliderGrp("divisionSlider", en=0, e=True)
    mc.intSliderGrp("relaxSlider", en=0, e=True)
    mc.floatSliderGrp("smoothBorderSlider", en=0, e=True)
    # mc.intSliderGrp('extrudeSlider', en=0, e=True)
    mc.checkBox("insetCheckbox", en=0, e=True)
    mc.button("minusButton", l="-", en=0, e=True)
    mc.button("plusButton", l="+", en=0, e=True)
    mc.button("patchItButton", l="Patch It!", en=0, e=True)
    global selEdges
    global selObj
    global endOffset
    global orderedwholeBorderComponents
    global orderedwholeBorderComponentsExt
    global orderedEdges
    global orderedEdgeComponents
    global wholeBorder
    global orderedwholeBorder
    global orderedwholeBorderComponents
    global closeBridgeNode
    global endAOrig
    global endBOrig
    global closeSideABridgeNode
    global closeSideBBridgeNode
    global closeSideCBridgeNode
    global sideB1Edges
    global sideC1Edges

    selEdges = mc.ls(sl=True, fl=True)
    selObj = selEdges[0].split(".")[0]
    orderedEdges = initiate(selEdges)
    if len(orderedEdges) < len(selEdges):
        for i in range(0, len(selEdges) - len(orderedEdges)):
            options = mc.ls(
                mc.polyListComponentConversion(
                    mc.polyListComponentConversion(
                        selObj + ".e[" + str(orderedEdges[0]) + "]", tv=True
                    ),
                    te=True,
                ),
                fl=True,
            )

            orderedEdgeComponents = []
            for each in orderedEdges:
                orderedEdgeComponents.append(
                    selEdges[0].split(".")[0] + ".e[" + str(each) + "]"
                )

            key = [x for x in selEdges if x not in orderedEdgeComponents]
            selected = [x for x in options if x in key]
            orderedEdges.insert(0, int(selected[0].split("[")[1].split("]")[0]))

    orderedEdgeComponents = []
    for each in orderedEdges:
        orderedEdgeComponents.append(
            selEdges[0].split(".")[0] + ".e[" + str(each) + "]"
        )

    wholeBorder = mc.polySelect(q=True, eb=orderedEdges[0], ass=True)
    orderedwholeBorder = initiate(wholeBorder)
    orderedwholeBorderComponents = []
    for each in orderedwholeBorder:
        orderedwholeBorderComponents.append(
            selEdges[0].split(".")[0] + ".e[" + str(each) + "]"
        )
    orderedwholeBorderComponentsExt = (
        orderedwholeBorderComponents
        + orderedwholeBorderComponents
        + orderedwholeBorderComponents
    )

    mc.intSliderGrp(
        "extrudeSlider",
        e=True,
        min=1,
        max=(len(orderedwholeBorder) - (len(selEdges))) / 2 - 2,
    )

    if orderedwholeBorderComponents[0] == orderedEdgeComponents[0]:
        if orderedwholeBorderComponents.index(orderedEdgeComponents[1]) == 1:
            sideB1StartIndex = (
                orderedwholeBorderComponents.index(
                    orderedEdgeComponents[len(orderedEdgeComponents) - 1]
                )
                + 1
            )
        else:
            sideB1StartIndex = (
                orderedwholeBorderComponents.index(orderedEdgeComponents[0]) + 1
            )
    elif orderedwholeBorderComponents.index(
        orderedEdgeComponents[len(orderedEdgeComponents) - 1]
    ) > orderedwholeBorderComponents.index(orderedEdgeComponents[0]):
        if orderedwholeBorderComponents[0] in orderedEdgeComponents:
            sideB1StartIndex = (
                orderedwholeBorderComponents.index(orderedEdgeComponents[0]) + 1
            )
        else:
            sideB1StartIndex = (
                orderedwholeBorderComponents.index(
                    orderedEdgeComponents[len(orderedEdgeComponents) - 1]
                )
                + 1
            )
    else:
        if (
            orderedwholeBorderComponents.index(orderedEdgeComponents[0])
            == len(orderedwholeBorderComponents) - 1
        ):
            if orderedwholeBorderComponents[0] in orderedEdgeComponents:
                sideB1StartIndex = (
                    orderedwholeBorderComponents.index(
                        orderedEdgeComponents[len(orderedEdgeComponents) - 1]
                    )
                    + 1
                )
            else:
                sideB1StartIndex = 0
        elif orderedwholeBorderComponents[0] in orderedEdgeComponents:
            sideB1StartIndex = (
                orderedwholeBorderComponents.index(
                    orderedEdgeComponents[len(orderedEdgeComponents) - 1]
                )
                + 1
            )
        else:
            sideB1StartIndex = (
                orderedwholeBorderComponents.index(orderedEdgeComponents[0]) + 1
            )
    sideB1Edges = []
    for i in range(
        sideB1StartIndex,
        sideB1StartIndex + len(orderedwholeBorderComponents) - len(selEdges),
    ):
        if i < len(orderedwholeBorderComponents):
            sideB1Edges.append(orderedwholeBorderComponents[i])
        else:
            sideB1Edges.append(
                orderedwholeBorderComponents[i - len(orderedwholeBorderComponents)]
            )
    sideC1Edges = sideB1Edges[::-1]

    # initial Bridge
    divNum = len(selEdges) - 1
    endAOrig = orderedEdgeComponents[0]
    endBOrig = orderedEdgeComponents[len(selEdges) - 1]
    endOffset = mc.intSliderGrp("extrudeSlider", q=True, v=True)
    divNumII = endOffset - 1

    initBridgeEdges = [sideB1Edges[endOffset], sideC1Edges[endOffset]]
    mc.select(initBridgeEdges)
    closeBridgeNode = mc.polyBridgeEdge(
        divisions=divNum, ch=True, twist=0, taper=1, curveType=0, smoothingAngle=30
    )

    # Side A bridge
    newWholeBorder = mc.ls(
        mc.polySelect(selObj, q=True, eb=orderedEdges[0], ass=True), fl=True
    )
    tempXEdges = sideB1Edges[0:endOffset] + sideC1Edges[0:endOffset]
    tempXEdges = mc.ls(
        mc.polyListComponentConversion(
            mc.polyListComponentConversion(tempXEdges, tv=True), te=True
        ),
        fl=True,
    )
    newBridgeEdges = [x for x in newWholeBorder if x not in tempXEdges]
    mc.select(newBridgeEdges, orderedEdgeComponents[1 : len(selEdges) - 1])
    closeSideABridgeNode = mc.polyBridgeEdge(
        divisions=divNumII, ch=True, twist=0, taper=1, curveType=0, smoothingAngle=30
    )

    # Side B bridge
    extSideBEdgesI = sideB1Edges[0:endOffset]
    extSideBEdgesWhole = mc.ls(
        mc.polySelect(
            q=True, eb=int(extSideBEdgesI[0].split("[")[1].split("]")[0]), ass=True
        ),
        fl=True,
    )
    extSideBRemove = mc.ls(
        mc.polyListComponentConversion(
            mc.polyListComponentConversion(extSideBEdgesI, tv=True), te=True
        ),
        fl=True,
    )
    extSideBEdgesII = [x for x in extSideBEdgesWhole if x not in extSideBRemove]
    mc.select(extSideBEdgesI, extSideBEdgesII)
    closeSideBBridgeNode = mc.polyBridgeEdge(
        divisions=0, ch=True, twist=0, taper=1, curveType=0, smoothingAngle=30
    )

    # Side C bridge
    extSideCEdgesI = sideC1Edges[0:endOffset]
    extSideCEdgesWhole = mc.ls(
        mc.polySelect(
            q=True, eb=int(extSideCEdgesI[0].split("[")[1].split("]")[0]), ass=True
        ),
        fl=True,
    )
    extSideCRemove = mc.ls(
        mc.polyListComponentConversion(
            mc.polyListComponentConversion(extSideCEdgesI, tv=True), te=True
        ),
        fl=True,
    )
    extSideCEdgesII = [x for x in extSideCEdgesWhole if x not in extSideCRemove]
    mc.select(extSideCEdgesI, extSideCEdgesII)
    closeSideCBridgeNode = mc.polyBridgeEdge(
        divisions=0, ch=True, twist=0, taper=1, curveType=0, smoothingAngle=30
    )

    mc.select(cl=True)


def quadPatcherUI():
    global windowName
    global isFaceMode

    isFaceMode = 0
    windowSize = (400, 200)
    if mc.window(windowName, exists=True):
        mc.deleteUI(windowName)
    quad_window = mc.window(
        windowName, title="Quad Patcher", widthHeight=(windowSize[0], windowSize[1])
    )
    mc.columnLayout("mainColumn", adjustableColumn=True)
    mc.rowLayout(parent="mainColumn", nc=3)
    mc.button("edgeBorderMode", label="Edge Border Mode", c=quadPatchInit)
    mc.button("faceMode", label="Face Mode", c=faceModeInit)
    mc.button("extrudeMode", label="Extrude Mode", c=extrudeModeInit)

    mc.rowLayout(parent="mainColumn", nc=2)
    mc.text(l="Rotation: ", w=80, al="left")
    mc.intSliderGrp(
        "rotationSlider",
        field=True,
        dc=rotateSlider,
        w=310,
        min=0,
        max=1,
        value=0,
        cc=undoInfoON,
    )
    mc.rowLayout(parent="mainColumn", nc=2)
    mc.text(l="Proportion: ", w=80, al="left")
    mc.intSliderGrp(
        "divisionSlider",
        field=True,
        dc=divideSlider,
        w=310,
        min=1,
        max=2,
        value=0,
        cc=undoInfoON,
    )

    mc.rowLayout(parent="mainColumn", nc=2)
    mc.text(l="Relax: ", w=80, al="left")
    mc.intSliderGrp(
        "relaxSlider",
        field=True,
        dc=relaxSlider,
        w=310,
        min=0,
        max=10,
        value=10,
        cc=undoInfoON,
    )
    mc.rowLayout(parent="mainColumn", nc=2)
    mc.text(l="Smooth Border: ", w=80, al="left")
    mc.floatSliderGrp(
        "smoothBorderSlider",
        field=True,
        dc=smoothBorderSlider,
        w=310,
        min=0,
        max=1,
        value=0,
        cc=undoInfoON,
    )
    mc.rowLayout(parent="mainColumn", nc=2)
    mc.text(l="Extrude Mode: ", w=80, al="left")
    mc.intSliderGrp(
        "extrudeSlider",
        field=True,
        dc=extrudeSlider,
        w=310,
        min=0,
        max=1,
        value=1,
        cc=undoInfoON,
    )

    mc.rowLayout(parent="mainColumn", nc=2)
    mc.text(l="Inset: ")
    mc.checkBox("insetCheckbox", l="", cc=activateInset)
    mc.rowLayout(parent="mainColumn", nc=3)
    mc.text(l="Inset Divisions:")
    mc.button("minusButton", l="-", w=20, c=insetDivMinus)
    mc.button("plusButton", l="+", w=20, c=insetDivPlus)

    mc.rowLayout(parent="mainColumn", nc=2)
    mc.button("patchItButton", l="Patch It!", c=patchIt)
    mc.button("resetButton", l="RESET", c=resetUI)

    mc.showWindow(quad_window)


if __name__ == "__main__":
    quadPatcherUI()

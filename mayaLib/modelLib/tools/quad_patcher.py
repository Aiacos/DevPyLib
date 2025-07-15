#!/usr/bin/env python

"""****************************************************************************
*** quad_patcher.py
***
*** version: 1.0
*** Scripted in Maya 2020
*** Tested in Maya 2020 and 2022
***
****************************************************************************"""

import maya.cmds as mc
import maya.mel as mel
import maya.OpenMaya as om
import random

windowName = "quadPatcher"


def faceChecker(arg=None):
    """
    Checks the selected faces in Maya for various conditions:

    1. Ensures faces are selected.
    2. Checks that no face is adjacent to a border edge.
    3. Ensures the selection edge perimeter count is even.

    Args:
        arg: Optional argument, not used in the function.
    """
    sel = mc.ls(sl=True, fl=True)

    # Check if any faces are selected
    if mc.polyEvaluate(sel, ec=True) or mc.polyEvaluate(sel, vc=True) > 0:
        mc.error("No Faces are selected")
    if mc.polyEvaluate(sel, fc=True) == 0:
        mc.error("No faces are selected")

    mc.select(sel)

    # Check for adjacency to border edges
    for each in mc.ls(mc.polyListComponentConversion(sel, te=True), fl=True):
        currentEdge = mc.polySelect(eb=int(each.split("[")[1].split("]")[0]), q=True)
        if currentEdge is not None:
            mc.error("Face cannot be adjacent to the border")

    mc.ConvertSelectionToEdgePerimeter()

    # Ensure the selection edge perimeter count is even
    if len(mc.ls(sl=True, fl=True)) % 2 != 0:
        mc.select(sel)
        mc.error("Selection edge perimeter count is odd. Needs even for quads.")

    mc.select(sel)


def edgeChecker(arg=None):
    """
    Checks the selected edges in Maya for various conditions:

    1. Ensures edges are selected.
    2. Verifies that the complete edge border is selected.
    3. Ensures the selection count is even.

    Args:
        arg: Optional argument, not used in the function.
    """
    sel = mc.ls(sl=True, fl=True)

    # Check if any edges are selected
    if mc.polyEvaluate(sel, fc=True) or mc.polyEvaluate(sel, vc=True) > 0:
        mc.error("None edges selected for Edge Border Mode")
    if mc.polyEvaluate(sel, ec=True) == 0:
        mc.error("No Edges are selected for Edge Border Mode")

    # Verify that the complete edge border is selected
    first_edge_index = int(sel[0].split("[")[1].split("]")[0])
    complete_border_edges = mc.polySelect(q=True, eb=first_edge_index, ass=True)
    if len(mc.ls(complete_border_edges, fl=True)) != len(sel):
        mc.error("Complete edge border is not selected")

    # Ensure the selection count is even
    if len(sel) % 2 != 0:
        mc.error("Edge count is odd. Needs even for quads.")


def quadPatchInit(arg=None):
    """Initializes the quad patching process by duplicating the selected object,
    creating edge bridges, and setting up the UI components.

    Args:
        arg: Optional argument, not used in the function.
    """
    if isFaceMode == 0:
        edgeChecker()
    # Disable buttons and sliders in the UI
    mc.button("edgeBorderMode", label="Edge Border Mode", en=0, e=True)
    mc.button("faceMode", label="Face Mode", en=0, e=True)
    mc.button("extrudeMode", label="Extrude Mode", en=0, e=True)
    mc.intSliderGrp("extrudeSlider", en=0, e=True)

    # Declare global variables
    global objNameDup, objNameOrig, sideABridgeNode, sideBBridgeNode
    global sideCBridgeNode, orderedEdges, orderedEdgeComponents, sideAEdges
    global orderedEdgesExtended, orderedEdgesComponentsExtended, sideAEdgeComponents
    global sideALen, sideBLen, sideBRemoveSet, sideCRemoveSet, divOffset
    global dupBaseVerts, dupEdgesSet, newCreatedVerts, insetNode
    global relaxNodes, smoothNodesOrig, smoothNodes, dupFacesToHide
    global selEdgesOrig, FMtransferAttributesNode, wrapBaseMesh

    # Source object
    selEdgesOrig = mc.ls(sl=True, fl=True)
    selVertsOrig = mc.polyListComponentConversion(selEdgesOrig, tv=True)
    selFacesOrig = mc.polyListComponentConversion(selVertsOrig, tf=True)
    objNameOrig = selEdgesOrig[0].split(".")[0]
    allFacesOrig = mc.polyListComponentConversion(objNameOrig, tf=True)

    # Duplicate the original object
    objNameDup = mc.duplicate(
        objNameOrig,
        n="quadPatcher" + str(random.randint(1000, 9999)) + "_" + objNameOrig,
    )[0]

    # Prepare the duplicated edges
    selEdges = [objNameDup + "." + each.split(".")[1] for each in selEdgesOrig]
    mc.select(selEdges)
    dupEdgesSet = mc.sets(
        n="quadPatcher" + str(random.randint(1000, 9999)) + "_" + "dupSet"
    )
    selVerts = mc.ls(mc.polyListComponentConversion(selEdges, tv=True), fl=True)
    selFaces = mc.ls(mc.polyListComponentConversion(selVerts, tf=True), fl=True)

    # Remove unnecessary faces from the duplicated object
    dupFaceDeleteSet = [
        x
        for x in mc.ls(mc.polyListComponentConversion(objNameDup, tf=True), fl=True)
        if x not in selFaces
    ]
    mc.delete(dupFaceDeleteSet)
    mc.select(dupEdgesSet)

    selEdges = mc.ls(sl=True, fl=True)
    dupBaseVerts = mc.ls(mc.polyListComponentConversion(objNameDup, tv=True), fl=True)

    # Calculate side lengths
    sideALen = int(len(selEdges) / 4)
    sideBLen = int((len(selEdges) - (sideALen * 2)) / 2)
    if len(selEdges) == 12:
        sideALen = 1
        sideBLen = 5
    elif len(selEdges) == 10:
        sideALen = 1
        sideBLen = 4
    elif len(selEdges) == 8:
        sideALen = 1
        sideBLen = 3

    # Order edges for processing
    orderedEdges = initiate(selEdges)
    orderedEdgeComponents = [
        objNameDup + ".e[" + str(each) + "]" for each in orderedEdges
    ]

    # Wrap duplicated edges to the original object
    mc.select(selEdges, objNameOrig)
    mc.CreateWrap()
    wrapNode = mc.listConnections(objNameOrig, type="wrap")[0]
    wrapBaseMesh = mc.listConnections(wrapNode + ".basePoints")
    mc.setAttr(wrapNode + ".weightThreshold", 0)
    mc.setAttr(wrapNode + ".maxDistance", 1)
    mc.setAttr(wrapNode + ".autoWeightThreshold", 1)
    mc.setAttr(wrapNode + ".exclusiveBind", 0)

    # Setup for SideA
    orderedEdgesExtended = orderedEdges * 3
    orderedEdgesComponentsExtended = orderedEdgeComponents * 3

    mc.intSliderGrp("rotationSlider", e=True, v=sideALen)
    offsetNum = sideALen * 2
    mc.intSliderGrp("rotationSlider", e=True, v=offsetNum)

    sideAEdges = (
        orderedEdgesExtended[offsetNum : sideALen + offsetNum]
        + orderedEdgesExtended[
            sideALen + sideBLen + offsetNum : sideALen * 2 + sideBLen + offsetNum
        ]
    )
    sideAEdgeComponents = (
        orderedEdgesComponentsExtended[offsetNum : sideALen + offsetNum]
        + orderedEdgesComponentsExtended[
            sideALen + sideBLen + offsetNum : sideALen * 2 + sideBLen + offsetNum
        ]
    )

    # Remove edges for SideB
    sideBRemove = [
        orderedEdgesComponentsExtended[offsetNum + sideALen],
        orderedEdgesComponentsExtended[sideALen + offsetNum + sideBLen - 1],
    ]
    mc.select(sideBRemove)
    sideBRemoveSet = mc.sets(
        n="quadPatcher" + str(random.randint(1000, 9999)) + "_" + "sideBRemoveSet"
    )

    # Remove edges for SideC
    sideCRemove = [
        orderedEdgesComponentsExtended[offsetNum + (2 * sideALen) + sideBLen],
        orderedEdgesComponentsExtended[(2 * sideALen) + offsetNum + (2 * sideBLen) - 1],
    ]
    mc.select(sideCRemove)
    sideCRemoveSet = mc.sets(
        n="quadPatcher" + str(random.randint(1000, 9999)) + "_" + "sideCRemoveSet"
    )

    # Transform components
    smoothNodes = [
        mc.polyMoveEdge(selEdgesOrig, ch=1, random=0, localCenter=0, lsx=1)[0]
        for _ in range(3)
    ]

    # Create edge bridges
    mc.select(sideAEdgeComponents, r=True)
    sideABridgeNode = mc.polyBridgeEdge(
        divisions=sideBLen - 3,
        ch=True,
        twist=0,
        taper=1,
        curveType=0,
        smoothingAngle=30,
    )

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

    # Configure UI sliders
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

    # Identify newly created vertices and faces
    newCreatedVerts = [
        x
        for x in mc.ls(mc.polyListComponentConversion(objNameDup, tv=True), fl=True)
        if x not in dupBaseVerts
    ]
    newCreatedFaces = mc.ls(
        mc.polyListComponentConversion(newCreatedVerts, tf=True), fl=True
    )

    # Apply inset extrusion to new faces
    insetNode = mc.polyExtrudeFacet(newCreatedFaces, nds=1, off=0, d=0)

    # Relax vertices by averaging
    relaxNodes = [
        mc.polyAverageVertex(newCreatedVerts, i=10, ch=1)[0] for _ in range(10)
    ]

    # Transfer attributes in face mode
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

    # Hide faces to be hidden
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
    """Adjust the divisions and rotation offsets for bridge nodes.

    Args:
        arg: Optional argument, not used in the function.
    """
    global divOffset
    mc.undoInfo(swf=False)

    divNum = mc.intSliderGrp("divisionSlider", q=True, v=True)
    offsetNum = mc.intSliderGrp("rotationSlider", q=True, v=True)

    # Turn off node state for B and C bridges and inset
    mc.setAttr(sideBBridgeNode[0] + ".nodeState", 1)
    mc.setAttr(sideCBridgeNode[0] + ".nodeState", 1)
    mc.setAttr(insetNode[0] + ".nodeState", 1)

    # Set divisions for sideA bridge
    mc.setAttr(sideABridgeNode[0] + ".divisions", divNum)

    # Calculate division offset
    divOffset = sideALen - 3 - divNum + (sideBLen - sideALen)

    # Prepare sideA edges for input
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
    sideAEdgesString = " ".join(f'"e[{each}]"' for each in sideAEdges)
    inputComponentStrA = (
        'setAttr -type "componentList" ( "'
        + sideABridgeNode[0]
        + '.inputComponents" ) '
        + str(len(sideAEdges))
        + " "
        + sideAEdgesString
    )

    mel.eval(inputComponentStrA)

    # Prepare sideB edges for input
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
    sideBEdgesString = " ".join(
        f'"{each.split(".")[1]}"' for each in sideBEdgeComponents
    )
    inputComponentStrB = (
        'setAttr -type "componentList" ( "'
        + sideBBridgeNode[0]
        + '.inputComponents" ) '
        + str(len(sideBEdgeComponents))
        + " "
        + sideBEdgesString
    )

    # Prepare sideC edges for input
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
    sideCEdgesString = " ".join(
        f'"{each.split(".")[1]}"' for each in sideCEdgeComponents
    )
    inputComponentStrC = (
        'setAttr -type "componentList" ( "'
        + sideCBridgeNode[0]
        + '.inputComponents" ) '
        + str(len(sideCEdgeComponents))
        + " "
        + sideCEdgesString
    )

    # Execute adjustments for sideB and sideC
    mel.eval(inputComponentStrB)
    mc.setAttr(sideBBridgeNode[0] + ".nodeState", 0)
    mel.eval(inputComponentStrC)
    mc.setAttr(sideCBridgeNode[0] + ".nodeState", 0)

    # Check and update inset status
    insetStatus = mc.checkBox("insetCheckbox", q=True, v=True)
    if insetStatus == 1:
        mc.setAttr(insetNode[0] + ".nodeState", 0)

    updateRelax()
    updateInset()


def relaxSlider(arg=None):
    """
    Adjust the relaxation iterations for each node in relaxNodes based on the slider value.

    This function retrieves the current value from the "relaxSlider" integer slider group
    and sets the "iterations" attribute of each node in the relaxNodes list to this value.

    Args:
        arg: Optional argument, not used in the function.
    """
    mc.undoInfo(swf=False)  # Disable undo queue flushing
    relaxNum = mc.intSliderGrp("relaxSlider", q=True, v=True)  # Get slider value

    for each in relaxNodes:
        # Set the iterations attribute for each node
        mc.setAttr(each + ".iterations", relaxNum)


def smoothBorderSlider(arg=None):
    """Adjusts the smooth border scale for each node in smoothNodes based on the slider value.

    This function retrieves the current value from the "smoothBorderSlider" float slider
    group, converts it to a negative value, and sets the "localScaleX" attribute of each
    node in the smoothNodes list to this value.

    Args:
        arg: Optional argument, not used in the function.
    """
    mc.undoInfo(swf=False)  # Disable undo queue flushing
    smoothNum = (mc.floatSliderGrp("smoothBorderSlider", q=True, v=True) - 1) * -1
    # Set the localScaleX attribute for each node
    for each in smoothNodes:
        mc.setAttr(each + ".localScaleX", smoothNum)


def activateInset(arg=None):
    """Toggle inset node activation and update the relaxation and inset settings.

    This function is called when the inset checkbox is toggled. It updates the
    inset node's state and offset attributes, and calls the updateRelax and
    updateInset functions to update the relaxation and inset settings.

    Args:
        arg: Optional argument, not used in the function.
    """
    mc.undoInfo(swf=False)
    updateInset()
    insetStatus = mc.checkBox("insetCheckbox", q=True, v=True)

    if insetStatus == 1:
        # Activate inset node and set offset and divisions to 0 and 1
        mc.setAttr(insetNode[0] + ".nodeState", 0)
        mc.setAttr(insetNode[0] + ".offset", 0)
        mc.setAttr(insetNode[0] + ".divisions", 1)
    else:
        # Deactivate inset node
        mc.setAttr(insetNode[0] + ".nodeState", 1)

    # Update relaxation settings
    updateRelax()
    mc.undoInfo(swf=True)


def insetDivMinus(arg=None):
    """Decrease the number of inset divisions by one.

    This function is called when the user clicks the inset division minus button.
    It decreases the number of inset divisions by one, and updates the relaxation
    settings using the updateRelax function.

    Args:
        arg: Optional argument, not used in the function.
    """
    mc.undoInfo(swf=False)
    current_div_num = mc.getAttr(insetNode[0] + ".divisions")

    if current_div_num > 1:
        mc.setAttr(insetNode[0] + ".divisions", current_div_num - 1)

    updateRelax()
    mc.undoInfo(swf=True)


def insetDivPlus(arg=None):
    """Increase the number of inset divisions by one.

    This function is called when the user clicks the inset division plus button.
    It increases the number of inset divisions by one, and updates the relaxation
    settings using the updateRelax function.

    Args:
        arg: Optional argument, not used in the function.
    """
    mc.undoInfo(swf=False)  # Disable undo queue flushing
    currentDivNum = mc.getAttr(insetNode[0] + ".divisions")

    # Increase the number of inset divisions
    mc.setAttr(insetNode[0] + ".divisions", currentDivNum + 1)

    # Update relaxation settings
    updateRelax()
    mc.undoInfo(swf=True)  # Enable undo queue flushing


def updateRelax(arg=None):
    """Updates the input components of each node in relaxNodes to the newly created vertices.

    This function retrieves the newly created vertices by comparing the current vertex list
    with the original vertex list. It then sets the "inputComponents" attribute of each node
    in the relaxNodes list to the new vertices.

    Args:
        arg: Optional argument, not used in the function.
    """
    # Get the new vertices
    new_created_verts = [
        x
        for x in mc.ls(mc.polyListComponentConversion(objNameDup, tv=True), fl=True)
        if x not in dupBaseVerts
    ]

    # Create a string of the new vertices
    new_verts_string = ""
    for each in new_created_verts:
        new_verts_string += " " + '"' + each.split(".")[1] + '"'

    # Update the input components of each node in relaxNodes
    for each in relaxNodes:
        input_component_string = (
            'setAttr -type "componentList" ( "'
            + each
            + '.inputComponents" ) '
            + str(len(new_created_verts))
            + " "
            + new_verts_string
        )
        mel.eval(input_component_string)


def updateInset(arg=None):
    """Updates the input components of the inset node with the newly created faces.

    This function retrieves the newly created vertices and faces by comparing the
    current vertex and face lists with the original lists. It then sets the
    "inputComponents" attribute of the inset node to the new faces.

    Args:
        arg: Optional argument, not used in the function.
    """
    # Get the new vertices
    new_created_verts = [
        x
        for x in mc.ls(mc.polyListComponentConversion(objNameDup, tv=True), fl=True)
        if x not in dupBaseVerts
    ]

    # Get the new faces
    new_created_faces = mc.ls(
        mc.polyListComponentConversion(new_created_verts, tf=True), fl=True
    )

    # Create a string of the new faces
    new_faces_string = ""
    for each in new_created_faces:
        new_faces_string = new_faces_string + " " + '"' + each.split(".")[1] + '"'

    # Update the input components of the inset node
    input_component_string = (
        'setAttr -type "componentList" ( "'
        + insetNode[0]
        + '.inputComponents" ) '
        + str(len(new_created_faces))
        + " "
        + new_faces_string
    )
    mel.eval(input_component_string)


def undoInfoON(arg=None):
    """Enable undo queue flushing.

    Args:
        arg: Optional argument, not used in the function.
    """
    mc.undoInfo(swf=True)


def initiate(edges):
    """Get the ordered list of edges in a mesh.

    Takes an MSelectionList of edges and returns an ordered list of the edges.

    Args:
        edges (MSelectionList): The list of edges to traverse.

    Returns:
        list: The ordered list of edge indices.
    """
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
            # Check if the edge is connected to the current edge
            if mItEdge.connectedToEdge(currentEdge):
                if mItEdge.index() not in checkedEdge:
                    # Add the edge to the ordered list and mark it as checked
                    orderedList.append(mItEdge.index())
                    currentEdge = mItEdge.index()
                    checkedEdge.append(int(mItEdge.index()))
                    break
            mItEdge.next()
        mItEdge.reset()
    return orderedList


def patchIt(arg=None):
    """Patch the duplicated edges and merge the two objects.

    Delete the faces to hide and select the merged object.
    """
    # Delete the faces to hide
    mc.delete(dupFacesToHide)
    # Get the original faces
    facesOrig = mc.ls(mc.polyListComponentConversion(objNameDup, tf=True), fl=True)

    edgesToMerge = []
    # Iterate over the original edges and get their indices
    for each in selEdgesOrig:
        edgesToMerge.append(each.split(".")[1])
    # Unite the two objects, merge UV sets and center the pivot
    mergedObj = mc.polyUnite(
        [objNameOrig, objNameDup], ch=1, mergeUVSets=1, centerPivot=True
    )[0]
    # Rename the new object
    objNameNew = mc.rename(mergedObj, objNameOrig)
    # Iterate over the duplicated edges and get their indices
    for each in mc.sets(dupEdgesSet, q=True):
        if each != "transform*":
            edgesToMerge.append(each.split(".")[1])
    # Delete the set if it exists
    if mc.objExists("quadPatcher*_*Set"):
        mc.delete("quadPatcher*_*Set")
    # Delete history
    mc.DeleteHistory()
    vertsToMerge = []

    # Iterate over the edges to merge and get their vertices
    for each in edgesToMerge:
        vertsToMerge.append(objNameNew + "." + each)
    # Merge the vertices
    mc.polyMergeVertex(vertsToMerge, d=0.001, am=1, ch=1)

    # Delete the live object if it exists
    if isFaceMode == 1:
        mc.delete(liveObj)
    # Delete the wrap base mesh if it exists
    if mc.objExists(wrapBaseMesh[0]):
        mc.delete(wrapBaseMesh)
    # Delete the merged object set if it exists
    if mc.objExists("mergedObjSet"):
        mc.delete("mergedObjeSet")
    # Delete history
    mc.DeleteHistory()
    # Select the new object
    mc.select(objNameNew)

    # Reset the UI
    resetUI(windowName)


def resetUI(window_name):
    """Reset the UI by deleting the current window and opening a new one.

    Args:
        window_name (str): The name of the window to reset.
    """
    # Get all the windows of type "window"
    all_windows = mc.lsUI(type="window")
    # Iterate over each window and if it matches the window name,
    # delete it
    for win in all_windows:
        if win == window_name:
            mc.deleteUI(win)
    # Eval deferred to open a new instance of the UI
    mc.evalDeferred(quadPatcherUI)


def faceModeInit(arg=None):
    """Initialize face mode for quad patching.

    This function sets up the environment for face mode by performing the
    following tasks:
    - Checks the selected faces.
    - Disables certain UI buttons.
    - Duplicates the selected object and prepares it for quad patching.
    - Converts the selection to an edge perimeter and creates a set of edge
      components.
    - Initiates the quad patching process.

    Args:
        arg: Optional argument, not used in the function.
    """
    # Ensure that faces are selected and meet necessary conditions
    faceChecker()

    # Disable specific UI buttons for edge and extrude modes
    mc.button("edgeBorderMode", label="Edge Border Mode", en=0, e=True)
    mc.button("faceMode", label="Face Mode", en=0, e=True)
    mc.button("extrudeMode", label="Extrude Mode", en=0, e=True)
    mc.intSliderGrp("extrudeSlider", en=0, e=True)

    # Declare global variables
    global liveObj
    global faceModeEdgeComponentsOrigSet
    global isFaceMode
    isFaceMode = 1

    # Get the original selected faces and object name
    selFacesOrig = mc.ls(sl=True, fl=True)
    objNameOrig = selFacesOrig[0].split(".")[0]

    # Duplicate the original object for live manipulation
    liveObj = mc.duplicate(
        objNameOrig, n="quadPatcher" + str(random.randint(1000, 9999)) + "_live"
    )

    # Prepare the duplicated object by keeping only the selected faces
    liveObjFaces = [liveObj[0] + "." + each.split(".")[1] for each in selFacesOrig]
    mc.delete(
        [
            x
            for x in mc.ls(mc.polyListComponentConversion(liveObj, tf=True), fl=True)
            if x not in liveObjFaces
        ]
    )

    # Hide the duplicated object
    mc.hide(liveObj)

    # Convert the selection to an edge perimeter and create a set
    mc.ConvertSelectionToEdgePerimeter()
    faceModeEdgeComponentsOrigSet = mc.sets(
        n="quadPatcher" + str(random.randint(1000, 9999)) + "_" + objNameOrig + "Set"
    )

    # Delete the original selected faces and select the edge component set
    mc.delete(selFacesOrig)
    mc.select(faceModeEdgeComponentsOrigSet)

    # Initiate the quad patching process
    quadPatchInit()


def extrudeSlider(arg=None):
    """
    Adjust the number of extrusions for the extrusion mode.

    Args:
        arg: Optional argument, not used in the function.
    """
    mc.undoInfo(swf=False)
    endOffset = mc.intSliderGrp("extrudeSlider", q=True, v=True)

    # Set the node state for the closing bridge nodes
    mc.setAttr(closeSideABridgeNode[0] + ".nodeState", 1)
    mc.setAttr(closeSideBBridgeNode[0] + ".nodeState", 1)
    mc.setAttr(closeSideCBridgeNode[0] + ".nodeState", 1)

    # Calculate the number of divisions for the closing bridge
    divNumII = endOffset - 1

    # Set the initial bridge
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

    # Side A
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
    """Initialize the extrude mode by setting up UI components and creating bridge nodes.

    Args:
        arg: Optional argument, not used in the function.
    """
    # Disable UI components for extrude mode
    mc.button("edgeBorderMode", label="Edge Border Mode", en=0, e=True)
    mc.button("faceMode", label="Face Mode", en=0, e=True)
    mc.button("extrudeMode", label="Extrude Mode", en=0, e=True)
    mc.intSliderGrp("rotationSlider", en=0, e=True)
    mc.intSliderGrp("divisionSlider", en=0, e=True)
    mc.intSliderGrp("relaxSlider", en=0, e=True)
    mc.floatSliderGrp("smoothBorderSlider", en=0, e=True)
    mc.checkBox("insetCheckbox", en=0, e=True)
    mc.button("minusButton", l="-", en=0, e=True)
    mc.button("plusButton", l="+", en=0, e=True)
    mc.button("patchItButton", l="Patch It!", en=0, e=True)

    # Declare global variables
    global selEdges, selObj, endOffset, orderedwholeBorderComponents
    global orderedwholeBorderComponentsExt, orderedEdges, orderedEdgeComponents
    global wholeBorder, orderedwholeBorder, closeBridgeNode, endAOrig
    global endBOrig, closeSideABridgeNode, closeSideBBridgeNode, closeSideCBridgeNode
    global sideB1Edges, sideC1Edges

    # Get the selected edges and object name
    selEdges = mc.ls(sl=True, fl=True)
    selObj = selEdges[0].split(".")[0]

    # Initialize ordered edges
    orderedEdges = initiate(selEdges)
    if len(orderedEdges) < len(selEdges):
        for _ in range(len(selEdges) - len(orderedEdges)):
            options = mc.ls(
                mc.polyListComponentConversion(
                    mc.polyListComponentConversion(
                        selObj + ".e[" + str(orderedEdges[0]) + "]", tv=True
                    ),
                    te=True,
                ),
                fl=True,
            )

            orderedEdgeComponents = [
                selEdges[0].split(".")[0] + ".e[" + str(each) + "]"
                for each in orderedEdges
            ]

            # Find the key edge that needs to be added
            key = [x for x in selEdges if x not in orderedEdgeComponents]
            selected = [x for x in options if x in key]
            orderedEdges.insert(0, int(selected[0].split("[")[1].split("]")[0]))

    orderedEdgeComponents = [
        selEdges[0].split(".")[0] + ".e[" + str(each) + "]" for each in orderedEdges
    ]

    # Retrieve and extend the whole border edges
    wholeBorder = mc.polySelect(q=True, eb=orderedEdges[0], ass=True)
    orderedwholeBorder = initiate(wholeBorder)
    orderedwholeBorderComponents = [
        selEdges[0].split(".")[0] + ".e[" + str(each) + "]"
        for each in orderedwholeBorder
    ]
    orderedwholeBorderComponentsExt = orderedwholeBorderComponents * 3

    # Set extrudeSlider range
    mc.intSliderGrp(
        "extrudeSlider",
        e=True,
        min=1,
        max=(len(orderedwholeBorder) - len(selEdges)) / 2 - 2,
    )

    # Determine the start index for sideB1 edges
    if orderedwholeBorderComponents[0] == orderedEdgeComponents[0]:
        if orderedwholeBorderComponents.index(orderedEdgeComponents[1]) == 1:
            sideB1StartIndex = (
                orderedwholeBorderComponents.index(orderedEdgeComponents[-1]) + 1
            )
        else:
            sideB1StartIndex = (
                orderedwholeBorderComponents.index(orderedEdgeComponents[0]) + 1
            )
    elif orderedwholeBorderComponents.index(
        orderedEdgeComponents[-1]
    ) > orderedwholeBorderComponents.index(orderedEdgeComponents[0]):
        if orderedwholeBorderComponents[0] in orderedEdgeComponents:
            sideB1StartIndex = (
                orderedwholeBorderComponents.index(orderedEdgeComponents[0]) + 1
            )
        else:
            sideB1StartIndex = (
                orderedwholeBorderComponents.index(orderedEdgeComponents[-1]) + 1
            )
    else:
        if (
            orderedwholeBorderComponents.index(orderedEdgeComponents[0])
            == len(orderedwholeBorderComponents) - 1
        ):
            if orderedwholeBorderComponents[0] in orderedEdgeComponents:
                sideB1StartIndex = (
                    orderedwholeBorderComponents.index(orderedEdgeComponents[-1]) + 1
                )
            else:
                sideB1StartIndex = 0
        elif orderedwholeBorderComponents[0] in orderedEdgeComponents:
            sideB1StartIndex = (
                orderedwholeBorderComponents.index(orderedEdgeComponents[-1]) + 1
            )
        else:
            sideB1StartIndex = (
                orderedwholeBorderComponents.index(orderedEdgeComponents[0]) + 1
            )

    # Define sideB1 and sideC1 edges
    sideB1Edges = [
        orderedwholeBorderComponents[i % len(orderedwholeBorderComponents)]
        for i in range(
            sideB1StartIndex,
            sideB1StartIndex + len(orderedwholeBorderComponents) - len(selEdges),
        )
    ]
    sideC1Edges = sideB1Edges[::-1]

    # Initial bridge setup
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

    # Create side A bridge
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

    # Create side B bridge
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

    # Create side C bridge
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

    # Clear selection
    mc.select(cl=True)


def quadPatcherUI():
    """Create the Quad Patcher UI in Maya.

    This function initializes and displays a UI window for the Quad Patcher tool,
    allowing users to switch modes and adjust various parameters for quad patching.
    """
    global windowName
    global isFaceMode

    # Initialize the face mode
    isFaceMode = 0
    windowSize = (400, 200)

    # Delete existing window if present
    if mc.window(windowName, exists=True):
        mc.deleteUI(windowName)

    # Create the main window
    quad_window = mc.window(
        windowName, title="Quad Patcher", widthHeight=(windowSize[0], windowSize[1])
    )
    mc.columnLayout("mainColumn", adjustableColumn=True)

    # Add buttons for mode selection
    mc.rowLayout(parent="mainColumn", nc=3)
    mc.button("edgeBorderMode", label="Edge Border Mode", c=quadPatchInit)
    mc.button("faceMode", label="Face Mode", c=faceModeInit)
    mc.button("extrudeMode", label="Extrude Mode", c=extrudeModeInit)

    # Rotation slider
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

    # Proportion slider
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

    # Relax slider
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

    # Smooth Border slider
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

    # Extrude Mode slider
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

    # Inset checkbox
    mc.rowLayout(parent="mainColumn", nc=2)
    mc.text(l="Inset: ")
    mc.checkBox("insetCheckbox", l="", cc=activateInset)

    # Inset Divisions control
    mc.rowLayout(parent="mainColumn", nc=3)
    mc.text(l="Inset Divisions:")
    mc.button("minusButton", l="-", w=20, c=insetDivMinus)
    mc.button("plusButton", l="+", w=20, c=insetDivPlus)

    # Patch and Reset buttons
    mc.rowLayout(parent="mainColumn", nc=2)
    mc.button("patchItButton", l="Patch It!", c=patchIt)
    mc.button("resetButton", l="RESET", c=resetUI)

    # Display the window
    mc.showWindow(quad_window)


if __name__ == "__main__":
    quadPatcherUI()

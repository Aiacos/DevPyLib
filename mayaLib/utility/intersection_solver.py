#!/usr/bin/env python

# ********************************
# Copyright 2021 Toshi Kosaka
#
# GORIOSHI SCRIPTS
# ********************************
"""Intersection solver UI utilities for detecting and fixing mesh interpenetration.

Original tool author: Toshi Kosaka (Gorioshi Scripts).
This module keeps the original behaviour but modernises style for lint compliance.
"""

from __future__ import annotations

import time

import maya.cmds as mc
from maya import mel

# pylint: disable=too-many-lines,missing-function-docstring,invalid-name
# pylint: disable=line-too-long,unused-argument,global-variable-undefined
# pylint: disable=superfluous-parens,global-variable-not-assigned
# pylint: disable=too-many-locals,too-many-statements,consider-using-enumerate

WINDOW_NAME = "intersectionSolver"


def create_pfx_toon(arg=None):
    """Create pfxToon node for intersection visualization.

    Creates a pfxToon deformer that displays intersection lines on selected
    meshes in red, useful for detecting interpenetration.

    Args:
        arg (None): Unused callback argument.
    """
    sel = mc.ls(mc.listRelatives(c=True), fl=True)
    if not mc.objExists("pfxToon_set"):
        mc.sets(sel, n="pfxToon_set")
    else:
        mc.sets(sel, e=True, fe="pfxToon_set")
    target = mc.sets("pfxToon_set", q=True)

    if not mc.objExists("pfxToonCollisionDetectShape"):
        pfx_toon_node = mc.createNode(
            "pfxToon", n="pfxToonCollisionDetectShape", p="pfxToonCollisioneDetect"
        )
        mc.setAttr(pfx_toon_node + ".profileLines", 0)
        mc.setAttr(pfx_toon_node + ".creaseLines", 0)
        mc.setAttr(pfx_toon_node + ".intersectionLines", 1)
        mc.setAttr(pfx_toon_node + ".displayPercent", 100)
        mc.setAttr(pfx_toon_node + ".intersectionColor", 1, 0, 0, type="double3")
        mc.setAttr(pfx_toon_node + ".selfIntersect", 1)
    else:
        pfx_toon_node = "pfxToonCollisionDetectShape"

    for i, each in enumerate(target):
        mc.connectAttr(
            each + ".outMesh", pfx_toon_node + ".inputSurface[" + str(i) + "].surface", f=True
        )
        mc.connectAttr(
            each + ".worldMatrix[0]",
            pfx_toon_node + ".inputSurface[" + str(i) + "].inputWorldMatrix",
            f=True,
        )


def remove_pfx_toon(arg=None):
    """Remove pfxToon node and its associated set.

    Args:
        arg (None): Unused callback argument.
    """
    if mc.objExists("pfxToon_set"):
        mc.delete("pfxToon_set")
    if mc.objExists("pfxToonCollisionDetect"):
        mc.delete("pfxToonCollisionDetect")


def near_clip_change(arg=None):
    """Update camera near clip plane value from slider.

    Args:
        arg (None): Unused callback argument.
    """
    clip_val = mc.floatSlider("nearClipSlider", q=True, v=True)
    cur_cam = "perspShape"
    for each in mc.getPanel(type="modelPanel"):
        cur_cam = mc.modelEditor(each, q=True, av=True, cam=True)
    mc.setAttr(cur_cam + ".nearClipPlane", clip_val)
    mc.text("nearClipValue", e=True, l=str(round(clip_val, 3)))


def display_width_field_change(arg=None):
    """Update intersection line width from text field input.

    Args:
        arg (None): Unused callback argument.
    """
    val = mc.floatField("lineWidth", q=True, v=True)
    mc.setAttr("pfxToonCollisionDetectShape.lineWidth", val)
    mc.floatSlider("displayWidthSlider", e=True, v=val)


def display_width_slider_change(arg=None):
    """Update intersection line width from slider input.

    Args:
        arg (None): Unused callback argument.
    """
    val = mc.floatSlider("displayWidthSlider", q=True, v=True)
    mc.setAttr("pfxToonCollisionDetectShape.lineWidth", val)
    mc.floatField("lineWidth", e=True, v=val)


def find_collision(null):
    """Detect mesh interpenetrations using rigid body simulation.

    Triangulates selected meshes, simulates rigid body collision, and
    selects meshes where interpenetration was detected.

    Args:
        null: Unused callback argument.
    """
    sel = mc.ls(sl=True, fl=True)
    for each in sel:
        mc.polyTriangulate(each, ch=1)
    mc.ls(sel)
    mc.rigidBody(
        sel,
        active=True,
        m=1,
        dp=0,
        sf=0.2,
        df=0.2,
        b=0.6,
        l=0,
        tf=200,
        iv=(0, 0, 0),
        iav=(0, 0, 0),
        c=0,
        pc=0,
        i=(0, 0, 0),
        imp=(0, 0, 0),
        si=(0, 0, 0),
        sio="none",
    )

    mc.setAttr("rigidSolver.collisionTolerance", 0.0001)
    mc.select(cl=True)
    mc.currentTime(1)
    mc.currentTime(2)
    mc.currentTime(1)

    global collisionResults
    collisionResults = mc.ls(sl=True)

    mc.delete("rigidBody*")
    mc.delete("rigidSolver")
    mc.delete("polyTriangulate*")
    mc.select(sel)
    mc.DeleteHistory()

    mc.select(collisionResults, r=True)


def select_results(null):
    """Select meshes with detected collisions.

    Args:
        null: Unused callback argument.
    """
    global collisionResults
    mc.select(collisionResults)


def apply_collision(none):
    """Apply boolean operation to separate intersecting mesh faces.

    Uses Polygon Boolean Operation to identify and separate intersecting
    geometry, then relaxes resulting vertices.

    Args:
        none: Unused callback argument.
    """
    flush_cbb()

    time.time()

    sel_orig = mc.ls(sl=True, fl=True)
    sel_dup = []
    for each in sel_orig:
        sel_dup.append(mc.duplicate(each, n=each + "_cbbdup")[0])

    dummy_plane = mc.polyPlane(n="dummy_plane", ch=1, o=1, w=1, h=1, sw=1, sh=1, cuv=2)
    mc.setAttr(dummy_plane[0] + ".ty", 999999)
    sel_dup.insert(0, dummy_plane[0])

    sets_list = []
    for each in sel_dup:
        sets_list.append(
            mc.sets(mc.polyListComponentConversion(each, tf=True), n=each + "_setsCBB")
        )

    bool_mesh_name = "tempMeshBool"
    mc.polyCBoolOp(sel_dup, op=1, ch=1, n=bool_mesh_name)

    new_sets_list = []
    for i in range(0, len(sets_list)):
        new_sets_list.append(mc.sets(sets_list[i], q=True))
        new_sets_list[i] = [x for x in new_sets_list[i] if "transform" not in x]

    mc.select(cl=True)

    # evaluate if selected are full or partial shell, and separate
    for each in new_sets_list:
        mc.select(each)
        check1 = mc.polyEvaluate(fc=True)
        mc.ConvertSelectionToShell()
        check2 = mc.polyEvaluate(fc=True)
        if check1 != check2:
            mc.polyChipOff(each, ch=1, kft=1, dup=0, off=0)
    mc.polySeparate(bool_mesh_name, ch=1)

    # update new sets list
    new_sets_list = []
    for i in range(0, len(sets_list)):
        new_sets_list.append(mc.sets(sets_list[i], q=True))
        new_sets_list[i] = [x for x in new_sets_list[i] if "transform" not in x]

    mc.DeleteHistory()

    for j in range(0, len(sets_list)):
        target = new_sets_list[j][0]
        mc.rename(target.split(".")[0], sets_list[j].split("_setsCBB")[0])

    mc.delete(dummy_plane[0])
    sets_list.pop(0)
    sel_dup.pop(0)
    all_edges = mc.polyListComponentConversion(te=True)

    fill_faces = []
    for each in all_edges:
        current_face = mc.polyEvaluate(each.split(".")[0], f=True)
        mc.polyCloseBorder(each, ch=0)
        updated_face = mc.polyEvaluate(each.split(".")[0], f=True)
        filled_face_num = updated_face - current_face
        mc.select(cl=True)
        for i in range(1, filled_face_num + 1):
            fill_faces.append(each.split(".")[0] + ".f[" + str(updated_face - i) + "]")

    gap_distance_float = mc.floatField("gapDistanceFloat", q=True, v=True) * -1
    for each in fill_faces:
        mc.select(each)
        mc.ConvertSelectionToVertices()
        mc.GrowPolygonSelectionRegion()
        verts = mc.ls(sl=True, fl=True)
        verts_move_dist = []
        for _i in range(0, len(verts)):
            verts_move_dist.append(gap_distance_float)
        mc.moveVertexAlongDirection(verts, n=(verts_move_dist))

    for i in range(0, len(sel_orig)):
        mc.transferAttributes(
            sel_dup[i],
            sel_orig[i],
            pos=1,
            nml=0,
            uvs=2,
            col=2,
            spa=0,
            sus="map1",
            tus="map1",
            sm=3,
            fuv=0,
            clb=1,
        )

    mc.select(sel_orig)
    mc.DeleteHistory()
    mc.delete(bool_mesh_name)


def relax_brush(arg=None):
    """Activate mesh relax sculpt tool with surface constraint.

    Args:
        arg (None): Unused callback argument.
    """
    mel.eval('setMeshSculptTool "Relax";')
    mel.eval("sculptMeshCacheCtx -e -constrainToSurface true sculptMeshCacheContext;")


def relax_flood(arg=None):
    """Activate mesh relax sculpt tool and apply flood operation.

    Args:
        arg (None): Unused callback argument.
    """
    mel.eval('setMeshSculptTool "Relax";')
    mel.eval("sculptMeshCacheCtx -e -constrainToSurface true sculptMeshCacheContext;")
    mel.eval("sculptMeshFlood; sculptMeshFlood; sculptMeshFlood;")
    mel.eval("SelectToolOptionsMarkingMenu;")
    mel.eval("buildSelectMM; SelectToolOptionsMarkingMenuPopDown;")


def flush_cbb(arg=None):
    """Clean up temporary geometry created by collision solving process.

    Deletes temporary boolean mesh, dummy planes, and constraint nodes
    left over from intersection solving operations.

    Args:
        arg (None): Unused callback argument.
    """
    if mc.objExists("tempMeshBool*"):
        mc.DeleteHistory("tempMeshBool*")
        mc.delete("tempMeshBool*")
    if mc.objExists("dummy_plane*"):
        mc.delete("dummy_plane*")
    if mc.objExists("*_setsCBB*"):
        mc.delete("*_setsCBB*")
    if mc.objExists("*_cbbdup*"):
        mc.delete("*_cbbdup*")
    if mc.objExists("rigidBody*"):
        mc.delete("rigidBody*")
    if mc.objExists("rigidSolver"):
        mc.delete("rigidSolver")


def fix_nan_verts(arg=None):
    """Replace NaN vertex coordinates with valid positions (0, 0, 0).

    Args:
        arg (None): Unused callback argument.
    """
    sel = mc.listRelatives(mc.ls(sl=True, fl=True), c=True, type="mesh")
    sel_verts = mc.ls(mc.polyListComponentConversion(sel, tv=True), fl=True)
    for each in sel_verts:
        if (
            str(
                mc.xform(
                    each.split(".vtx[")[0] + ".pnts[" + each.split(".vtx[")[1], q=True, t=True
                )[0]
            )
            == "nan"
        ):
            mc.setAttr(each.split(".vtx[")[0] + ".pnts[" + each.split(".vtx[")[1], 0, 0, 0)


def intersection_solver():
    """Create and display the intersection solver UI window.

    Provides tools for detecting and resolving mesh interpenetrations
    including visualization, collision solving, and mesh relaxation.
    """
    global isFaceMode

    isFaceMode = 0
    window_size = (250, 320)
    if mc.window(WINDOW_NAME, exists=True):
        mc.deleteUI(WINDOW_NAME)
    is_window = mc.window(
        WINDOW_NAME,
        title="Intersection_Solver",
        widthHeight=(window_size[0], window_size[1]),
    )

    mc.frameLayout("Intersection Solver v1.0", w=250, bgc=(0.1, 0.1, 0.1))
    mc.columnLayout("mainColumn", adjustableColumn=True)
    mc.rowLayout(parent="mainColumn", nc=3)

    cur_cam = "perspShape"
    for each in mc.getPanel(type="modelPanel"):
        cur_cam = mc.modelEditor(each, q=True, av=True, cam=True)
    nc_val = mc.getAttr(cur_cam + ".nearClipPlane")

    mc.text(l="Cam Near Clip : ")
    mc.floatSlider(
        "nearClipSlider", w=100, min=0.001, max=100, value=nc_val, s=0.001, dc=near_clip_change
    )
    mc.text("nearClipValue", l=str(round(nc_val, 3)))
    mc.setParent("..")
    mc.text(l="=================================", parent="mainColumn")
    mc.setParent("..")
    mc.rowLayout(p="mainColumn", nc=1)
    mc.button(l="Show Intersections on Selected", c=create_pfx_toon, bgc=(0, 0.3, 0.2))
    mc.setParent("..")
    mc.rowLayout(p="mainColumn", nc=3)
    mc.text(l="Diplay Width: ")
    mc.floatField("lineWidth", w=30, min=0, max=100, v=1, pre=2, cc=display_width_field_change)
    mc.floatSlider(
        "displayWidthSlider", w=100, min=0.001, max=100, value=0.001, dc=display_width_slider_change
    )
    mc.setParent("..")
    mc.button(l="Remove pfxToon", c=remove_pfx_toon, bgc=(0.3, 0, 0))

    mc.columnLayout(
        "mainColumn",
        rowSpacing=0,
        columnWidth=250,
    )
    mc.text(l="=================================", parent="mainColumn")
    mc.text(l="Make sure UV is clean, history is deleted")

    mc.rowLayout("nameRowLayout04", numberOfColumns=3, parent="mainColumn")
    mc.button(
        l="Inspect Selected", parent="nameRowLayout04", command=find_collision, bgc=(0, 0.3, 0.2)
    )
    mc.button("Select Results", parent="nameRowLayout04", command=select_results)

    mc.rowLayout("nameRowLayout01", numberOfColumns=2, parent="mainColumn")
    mc.text(l="Gap Distance: ")
    mc.floatField("gapDistanceFloat", w=40, v=0.1, pre=2, parent="nameRowLayout01")

    mc.rowLayout(numberOfColumns=2, parent="mainColumn")
    mc.button(label="Solve Intersection", h=30, command=apply_collision, bgc=(0, 0.2, 0.4))
    mc.button(l="Clean up junk Caused by Error", command=flush_cbb, bgc=(0.3, 0, 0))

    mc.text(l="=================================", parent="mainColumn")
    mc.rowLayout("nameRowLayout03", numberOfColumns=3, parent="mainColumn")
    mc.button(label="Relax Brush", parent="nameRowLayout03", command=relax_brush)
    mc.button(label="Relax Flood", parent="nameRowLayout03", command=relax_flood)
    mc.button(label="Fix NaN Verts", parent="nameRowLayout03", command=fix_nan_verts)

    mc.showWindow(is_window)


if __name__ == "__main__":
    intersection_solver()

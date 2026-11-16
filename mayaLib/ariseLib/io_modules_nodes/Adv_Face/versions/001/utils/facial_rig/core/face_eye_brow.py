"""Build step EyeBrow (parita' asFaceEyeBrow, MEL:33674-34022).

Apre chiudendo la cage (asFaceFaceCageFinish). I controller delle
sopracciglia esistono gia' (li crea FaceCage): qui nascono il controller di
regione `EyeBrowRegion_R/L`, i follow dei controller intermedi, il follow
di `EyeBrowCenter_M` fra i due lati, i collegamenti degli slider `ctrlBrow`
(su/giu', inner, squeeze, outerUpDown), la pulizia dei pesi al centro e
l'hammer fra sopracciglio e palpebra; infine le geometrie delle sopracciglia
copiano i pesi dal viso.

Divergenze (docs/gap-analysis.md §5l): multiSkinClusters non portato;
oggetti assenti = skip con warning.
"""

import maya.cmds as cmds

from .build_utils import as_align, as_face_hide_controllers
from .ctrl_box import create_face_controller, place_ctrl_by_projection
from .driving_system import ds_sdk, ensure_output_blend_weighted
from .face_cage_to_skin import face_face_cage_finish
from .face_ctrl_pp import face_add_constrained, face_half_moon_curve, weight_hammer_verts_ms
from .fit_options import FIT_SKELETON, get_fit_option
from .fitting import get_face_fit_selection

_SIDES = (("_R", "", 1), ("_L", "Left", -1))
_MIDS = ("EyeBrowMid1", "EyeBrowMid2", "EyeBrowMid3")


def _ws(node):
    return cmds.xform(node, query=True, worldSpace=True, translation=True)


def _selected():
    return cmds.ls(selection=True, flatten=True) or []


def _select_fit(fit_object):
    text = get_face_fit_selection(fit_object)
    if text.strip():
        cmds.select(text.split())
    else:
        cmds.select(clear=True)
    return _selected()


def _smoothstep(edge0, edge1, x):
    t = max(0.0, min(1.0, (x - edge0) / float(edge1 - edge0)))
    return t * t * (3 - 2 * t)


def _add_brow_attr(side, attr):
    ctrl = "ctrlBrow" + side
    cmds.addAttr(
        ctrl,
        longName=attr,
        keyable=True,
        attributeType="double",
        softMaxValue=10,
        hasSoftMaxValue=True,
        softMinValue=0,
        hasMinValue=True,
    )
    ensure_output_blend_weighted("{}.{}".format(ctrl, attr))


def _outer_up_down_target():
    """Punto verso cui sale l'esterno del sopracciglio: a meta' fra
    EyeBrowOuter e il 65% del contorno della fronte (MEL:33713-33726)."""
    if cmds.objExists("tempPointOnCurveInfo"):
        cmds.delete("tempPointOnCurveInfo")
    poci = cmds.createNode("pointOnCurveInfo", name="tempPointOnCurveInfo")
    cmds.setAttr(poci + ".turnOnPercentage", 1)
    cmds.connectAttr("ForeHeadTopToSideCurve.worldSpace[0]", poci + ".inputCurve", force=True)
    cmds.setAttr(poci + ".parameter", 0.65)
    pos = cmds.getAttr(poci + ".position")[0]
    temp = cmds.createNode("transform", name="TempPos")
    temp2 = cmds.createNode("transform", name="TempPos2")
    cmds.xform(temp, worldSpace=True, translation=pos)
    cmds.delete(cmds.pointConstraint("EyeBrowOuter", temp, temp2))
    target = _ws(temp2)
    cmds.delete(temp, temp2, poci)
    return target


def _build_regions(scale):
    for side, left, b in _SIDES:
        region = "EyeBrowRegion" + side
        offset = "EyeBrowRegionOffset" + side
        create_face_controller("EyeBrowRegion", side, 4)
        face_half_moon_curve(region, 90)
        cmds.delete("EyeBrowRegionJoint" + side)
        cmds.parent(offset, "SideReverse" + side)
        cmds.xform(offset, objectSpace=True, rotation=(0, 0, 0), scale=(1, 1, 1))
        cmds.setAttr(offset + ".s", 1, 1, 1, type="float3")
        pos_a, pos_b = _ws("EyeBrowInner"), _ws("EyeBrowOuter")
        pos = [
            (pos_a[0] + pos_b[0]) / (2.0 * b),
            (pos_a[1] + pos_b[1]) / 2.0,
            (pos_a[2] + pos_b[2]) / 2.0,
        ]
        cmds.xform(offset, worldSpace=True, translation=pos)
        dist = pos_a[0] - pos_b[0]
        cmds.scale(
            scale / dist,
            scale / (dist * 2),
            scale / dist,
            region + ".cv[0:7]",
            relative=True,
            pivot=pos,
        )
        place_ctrl_by_projection(region)
        constrain_to = cmds.createNode("transform", name="EyeBrowRegionConstrainTo" + side)
        constrain_to = cmds.parent(constrain_to, region)[0]
        cmds.xform(constrain_to, objectSpace=True, translation=(0, 0, 0), scale=(1, 1, 1))
        cmds.xform(constrain_to, worldSpace=True, translation=_ws("EyeBrowInner" + left))

    for side, _left, _b in _SIDES:
        region = "EyeBrowRegion" + side
        inner, outer = "EyeBrowInner" + side, "EyeBrowOuter" + side
        if cmds.objExists("EyeBrowMid1" + side):
            face_add_constrained("EyeBrowMid1" + side, inner, region, 3)
        if cmds.objExists("EyeBrowMid3" + side):
            face_add_constrained("EyeBrowMid3" + side, outer, region, 3)
            # con un Mid3 anche il Mid2 segue, per un comportamento uniforme
            face_add_constrained("EyeBrowMid2" + side, outer, region, 1)
        elif cmds.objExists("EyeBrowMid2" + side):
            face_add_constrained("EyeBrowMid2" + side, outer, region, 3)
        cmds.parent("EyeBrowInnerOffset" + side, "EyeBrowOuterOffset" + side, region)
        cmds.scale(0.6, 0.6, 0.6, inner + ".cv[0:99]", relative=True, pivot=_ws(inner))


def _build_center_follow():
    """EyeBrowCenter_M resta a meta' fra i due EyeBrowInner."""
    cmds.addAttr(
        "EyeBrowCenter_M",
        keyable=True,
        longName="follow",
        attributeType="double",
        minValue=0,
        maxValue=10,
        defaultValue=10,
    )
    follow = cmds.createNode(
        "transform", name="EyeBrowCenterFollow_M", parent="EyeBrowCenterOffset_M"
    )
    conversion = cmds.createNode("unitConversion", name="EyeBrowCenterFollowUnitConversion")
    cmds.setAttr(conversion + ".conversionFactor", 0.1)
    cmds.connectAttr("EyeBrowCenter_M.follow", conversion + ".input")
    cmds.parent("SDKEyeBrowCenter_M", follow)
    for side in ("_R", "_L"):
        pma = cmds.createNode("plusMinusAverage", name="EyeBrowCenterBlenderPMA" + side)
        sources = ("EyeBrowInner", "SDKEyeBrowInner", "EyeBrowRegion", "SDKEyeBrowRegion")
        for index, source in enumerate(sources):
            cmds.connectAttr(source + side + ".t", "{}.input3D[{}]".format(pma, index))
    pma_m = cmds.createNode("plusMinusAverage", name="EyeBrowCenterBlenderPMA_M")
    cmds.setAttr(pma_m + ".operation", 3)
    cmds.connectAttr("EyeBrowCenterBlenderPMA_R.output3D", pma_m + ".input3D[0]")
    cmds.connectAttr("EyeBrowCenterBlenderPMA_L.output3D", pma_m + ".input3D[1]")
    mpd = cmds.createNode("multiplyDivide", name="EyeBrowCenterBlenderMPD_M")
    for axis in ("Y", "Z"):
        cmds.connectAttr(
            "{}.output3D{}".format(pma_m, axis.lower()), "{}.input1{}".format(mpd, axis)
        )
        cmds.connectAttr(conversion + ".output", "{}.input2{}".format(mpd, axis))
        cmds.connectAttr("{}.output{}".format(mpd, axis), "{}.t{}".format(follow, axis.lower()))


def _build_slider_sdk(ctrl_scale):
    pos_a, pos_b = _ws("EyeBrowInner"), _ws("FitEyeBall")
    dist = max(0.25, min(1.0, ((pos_a[1] - pos_b[1]) / ctrl_scale) / 2.0))
    for side in ("_R", "_L"):
        brow = "ctrlBrow" + side
        if cmds.objExists("EyeBrowInner_R"):
            ds_sdk(brow + ".ty", "SDKEyeBrowRegion" + side + ".ty", 1, dist)
            ds_sdk(brow + ".ty", "SDKEyeBrowRegion" + side + ".ty", -1, dist * -1)
            ds_sdk(brow + ".tx", "SDKEyeBrowInner" + side + ".ty", 1, dist)
            ds_sdk(brow + ".tx", "SDKEyeBrowInner" + side + ".ty", -1, dist * -1)
        for mid, factor in (("EyeBrowMid1", 0.3), ("EyeBrowMid2", 0.25)):
            if cmds.objExists(mid + "_R"):
                ds_sdk(brow + ".tx", "SDK" + mid + side + ".ty", 1, dist * factor)
                ds_sdk(brow + ".tx", "SDK" + mid + side + ".ty", -1, dist * -factor)
        if cmds.objExists("NoseCrease_M"):
            ds_sdk(brow + ".tx", "SDKNoseCrease_M.ty", 1, dist * 0.02)
            ds_sdk(brow + ".ty", "SDKNoseCrease_M.ty", 1, dist * 0.02)


def _build_squeeze(ctrl_scale):
    """Attributo squeeze: i controller scorrono lungo la curva del
    sopracciglio verso il centro (MEL:33843-33901)."""
    points = [_ws("EyeBrowCenter"), _ws("EyeBrowInner")]
    points += [_ws(mid + "_R") for mid in _MIDS if cmds.objExists(mid + "_R")]
    points.append(_ws("EyeBrowOuter"))
    curve = cmds.curve(name="EyeBrowCurve", degree=1, point=points)
    cmds.rebuildCurve(
        curve,
        constructionHistory=0,
        replaceOriginal=1,
        rebuildType=0,
        endKnots=1,
        keepRange=0,
        keepControlPoints=0,
        keepEndPoints=0,
        keepTangents=0,
        spans=0,
        degree=3,
        tolerance=0.01,
    )
    temp = cmds.createNode("transform", name="TempPos")
    path = cmds.createNode("motionPath", name="tempMotionPath")
    cmds.setAttr(path + ".fractionMode", 1)
    cmds.connectAttr(curve + ".worldSpace", path + ".geometryPath")
    cmds.connectAttr(path + ".allCoordinates", temp + ".t")
    cmds.connectAttr(path + ".rotate", temp + ".rotate")
    for attr, value in (("worldUpType", 0), ("upAxis", 1), ("frontAxis", 0), ("inverseFront", 1)):
        cmds.setAttr("{}.{}".format(path, attr), value)
    npc = cmds.createNode("nearestPointOnCurve", name="tempNearestPointOnCurve")
    cmds.connectAttr(curve + ".worldSpace[0]", npc + ".inputCurve", force=True)
    temp2 = cmds.createNode("transform", name="TempPos2")
    cmds.connectAttr(temp2 + ".t", npc + ".inPosition")

    for side in ("_R", "_L"):
        _add_brow_attr(side, "squeeze")
        squeeze = "ctrlBrow" + side + ".squeeze"
        inner_x = _ws("EyeBrowInner_R")[0] / ctrl_scale
        ds_sdk(squeeze, "SDKEyeBrowInner" + side + ".tx", 10, inner_x * 0.50)
        ds_sdk(squeeze, "SDKEyeBrowInner" + side + ".ty", 10, inner_x * 0.25)
        for name in _MIDS + ("EyeBrowOuter",):
            if not cmds.objExists(name + side):
                continue
            ctrl = name + "_R"
            as_align(temp2, ctrl, translate=True)
            cmds.delete(cmds.geometryConstraint(curve, temp2))
            percentage = cmds.getAttr(npc + ".parameter")
            cmds.setAttr(path + ".uValue", percentage)
            rot_y = cmds.getAttr(temp + ".ry")
            cmds.setAttr(path + ".uValue", percentage - 0.1)
            rot_y -= cmds.getAttr(temp + ".ry")
            cmds.xform(ctrl, worldSpace=True, translation=_ws(temp))
            pos = cmds.getAttr(ctrl + ".t")[0]
            cmds.setAttr(ctrl + ".t", 0, 0, 0)
            sdk = "SDK" + name + side
            for axis, value in zip("xyz", pos):
                ds_sdk(squeeze, "{}.t{}".format(sdk, axis), 10, value)
            ds_sdk(squeeze, sdk + ".ry", 10, rot_y)
    cmds.delete(temp, temp2, npc, curve)


def _build_outer_up_down(target):
    for side in ("_R", "_L"):
        _add_brow_attr(side, "outerUpDown")
        cmds.xform("EyeBrowOuter_R", worldSpace=True, translation=target)
        pos = cmds.getAttr("EyeBrowOuter_R.t")[0]
        cmds.setAttr("EyeBrowOuter_R.t", 0, 0, 0)
        for i, name in enumerate(("EyeBrowInner",) + _MIDS + ("EyeBrowOuter",)):
            if not cmds.objExists(name + side):
                continue
            percentage = _smoothstep(0, 1, 0.2 * (i + 1))
            for axis, value in zip("xyz", pos):
                ds_sdk(
                    "ctrlBrow" + side + ".outerUpDown",
                    "SDK{}{}.t{}".format(name, side, axis),
                    10,
                    value * percentage,
                )


def _clean_weights(geometry, skin_cluster, head_joint):
    """Vertici al centro quasi tutti sulla testa -> tutti sulla testa; poi
    hammer fra il loop Outer della palpebra e il sopracciglio."""
    cmds.skinCluster(skin_cluster, edit=True, selectInfluenceVerts="EyeBrowCenterJoint_M")
    for vtx in _selected():
        if "." not in vtx:
            continue
        if cmds.skinPercent(skin_cluster, vtx, transform=head_joint, query=True) > 0.99:
            cmds.skinPercent(skin_cluster, vtx, transformValue=(head_joint, 1))

    for _side, left, _b in _SIDES:
        inner_vtx = (_select_fit("EyeBrowInner" + left) or [""])[0]
        outer_vtx = (_select_fit("EyeBrowOuter" + left) or [""])[0]
        forehead = _select_fit("ForeHeadAreaMesh" + left)
        cmds.select(geometry + ".vtx[*]")  # asInvertSelection
        if forehead:
            cmds.select(forehead, deselect=True)
        outside = cmds.ls(selection=True)
        lid_vtxs = _select_fit("upperEyeLidOuterCurve" + left)
        rings = 25
        for i in range(25):
            current = _selected()
            if inner_vtx in current or outer_vtx in current:
                rings = i
                break
            cmds.polySelectConstraint(propagate=1, type=0x0001)
            if outside:
                cmds.select(outside, deselect=True)
        _select_fit("upperEyeLidOuterCurve" + left)
        for _ in range(rings - 1):
            cmds.polySelectConstraint(propagate=1, type=0x0001)
            if outside:
                cmds.select(outside, deselect=True)
        if lid_vtxs:
            cmds.select(lid_vtxs, deselect=True)
        weight_hammer_verts_ms(5, skin_cluster)


def _skin_cluster_of(geo):
    for node in cmds.listHistory(geo) or []:
        if cmds.nodeType(node) == "skinCluster":
            return node
    return ""


def _attach_brow_geometry(geometry, skin_cluster, head_joint):
    """Le geometrie delle sopracciglia copiano i pesi dal viso."""
    for geo in (get_fit_option("Eyebrow") or "").split():
        sc = _skin_cluster_of(geo)
        if not sc:
            cmds.warning('Did not find skinCluster on eyeBrow object:"{}"'.format(geo))
            continue
        if sc == skin_cluster:  # sopracciglia come facce della mesh del viso
            cmds.select("asCage", geo)
            cmds.copySkinWeights(
                noMirror=True,
                surfaceAssociation="closestPoint",
                influenceAssociation="closestJoint",
            )
            continue
        joints = ["EyeBrowCenterJoint_M"]
        for side in ("_R", "_L"):
            for name in ("EyeBrowInner", "EyeBrowOuter") + _MIDS:
                if cmds.objExists(name + "Joint" + side):
                    joints.append(name + "Joint" + side)
        cmds.skinCluster(
            sc, edit=True, dropoffRate=4, lockWeights=False, weight=0, addInfluence=joints
        )
        cmds.skinPercent(sc, geo, transformValue=(head_joint, 0))
        cmds.select(geometry, geo)
        cmds.copySkinWeights(
            noMirror=True, surfaceAssociation="closestPoint", influenceAssociation="closestJoint"
        )
        cmds.select(geo)


def face_eye_brow() -> bool:
    """Costruisce le sopracciglia (asFaceEyeBrow).

    Returns:
        True anche quando lo step e' saltato per assenza di `EyeBrowInner`
        (gate MEL); False con warning se manca un prerequisito.
    """
    face_face_cage_finish()
    if not cmds.objExists("EyeBrowInner"):
        return True
    geometry = get_fit_option("Face") or ""
    head_joint = get_fit_option("HeadJoint") or ""
    skin_cluster = get_fit_option("SkinCluster") or ""
    required = [geometry, head_joint, skin_cluster, FIT_SKELETON, "EyeBrowOuter", "EyeBrowCenter"]
    required += ["ForeHeadTopToSideCurve", "EyeBrowInner_R", "EyeBrowInner_L", "EyeBrowOuter_R"]
    required += ["EyeBrowCenter_M", "ctrlBrow_R", "ctrlBrow_L", "EyeBrowCenterJoint_M"]
    missing = [node for node in required if not node or not cmds.objExists(node)]
    if missing:
        cmds.warning("face_eye_brow: missing {}".format(", ".join(missing) or "options"))
        return False
    if get_fit_option("MultiSkinClusters"):
        cmds.warning("face_eye_brow: multiSkinClusters is not ported yet")
    ctrl_scale = cmds.getAttr("OnFacecontrols.sx")
    scale = cmds.getAttr(FIT_SKELETON + ".faceScale")

    as_face_hide_controllers(True)
    for node in cmds.listRelatives("OnFacecontrols", allDescendents=True, type="transform") or []:
        if node.startswith("EyeBrow") and "Offset_" in node:
            cmds.setAttr(node + ".v", 1)
    cmds.setAttr("ctrlBoxBrow_R.v", 1)
    cmds.setAttr("ctrlBoxBrow_L.v", 1)
    if cmds.objExists("NoseCreaseOffset_M"):
        cmds.setAttr("NoseCreaseOffset_M.v", 1)
    cmds.setAttr("ctrlBox.RegionsCtrlVis", 1)

    target = _outer_up_down_target()
    _build_regions(scale)
    _build_center_follow()
    _build_slider_sdk(ctrl_scale)
    _build_squeeze(ctrl_scale)
    _build_outer_up_down(target)
    _clean_weights(geometry, skin_cluster, head_joint)
    _attach_brow_geometry(geometry, skin_cluster, head_joint)
    cmds.select(clear=True)
    return True

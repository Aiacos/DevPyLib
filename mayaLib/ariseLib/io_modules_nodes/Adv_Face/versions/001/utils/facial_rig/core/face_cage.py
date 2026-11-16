"""Build step FaceCage (parita' asFaceFaceCage, MEL:32870-33385).

Crea i controller "cage" di guance, naso, mento e sopracciglia (asCreatePP
sui locator fittati) e una mesh a facce triangolari `asCage` che li unisce
ai loop Outer di labbra e palpebre e al contorno della fronte. La cage e'
skinnata ai joint dei controller: lo step CageToSkin ne trasferisce i pesi
sul viso. Costruisce anche il controller NoseRegion_M.

Divergenze (docs/gap-analysis.md §5k):
- multiSkinClusters non portato (MEL:32899, 33046-33057);
- il MEL scrive la stima `numSmoo` nell'intField `faceCageIntField` della
  UI, da cui CageToSkin la rilegge: qui `guess_cage_smooth()` e' una
  funzione che CageToSkin richiama;
- oggetti fit assenti = facce saltate, come fa asFacet nel MEL.
"""

import maya.cmds as cmds

from .build_utils import as_face_hide_controllers, as_opm_scale_reset
from .ctrl_box import create_face_controller
from .face_ctrl_pp import create_pp
from .fit_options import FIT_SKELETON, get_fit_option
from .fitting import (
    _select_least_edges_path,
    get_face_fit_selection,
    remove_fit_animations_from_on_face_ctrls,
)

_SIDES = (("_R", "", 1), ("_L", "Left", -1))
_MIDDLE = ("NoseBridge", "Nose", "NoseUnder", "ChinCrease", "EyeBrowCenter")
_PPS = (
    "CheekBone",
    "NoseSide",
    "NoseBridge",
    "NoseCorner",
    "NoseUnder",
    "FrownBulge",
    "SmileBulge",
    "Cheek",
    "ChinCrease",
    "Nose",
    "Nostril",
)


def _ws(node):
    return cmds.xform(node, query=True, worldSpace=True, translation=True)


def _selected():
    return cmds.ls(selection=True, flatten=True) or []


def _cv(curve, index):
    """Componente CV; come nel MEL un indice frazionario viene troncato e
    uno oltre la fine ricade sull'ultimo CV."""
    return "{}.cv[{}]".format(curve, int(index))


def _round_half_up(value):
    """asRoundFloatToInt."""
    return int(value) + (1 if value % 1 >= 0.5 else 0)


def guess_cage_smooth() -> int:
    """Stima delle iterazioni di smooth della cage (campo "faceCage" della UI
    MEL) dalla densita' della mesh: quanti anelli di vertici separano la
    guancia dall'angolo della bocca (MEL:32922-32940)."""
    if not cmds.objExists("upperLipMainCurve") or not cmds.objExists("Cheek"):
        return 0
    cheek = get_face_fit_selection("Cheek").split()
    corner = get_face_fit_selection("upperLipOuterCurve.cv[99]").split()
    if not cheek or not corner:
        return 0
    cmds.select(cheek[0])
    rings = 20
    for i in range(20):
        cmds.polySelectConstraint(propagate=1, type=0x0001)
        if corner[0] in _selected():
            rings = i
            break
    cmds.select(clear=True)
    if rings > 10:
        return 2
    return 1 if rings > 1 else 0


def _facet(obj_a, obj_b, obj_c):
    """Triangolo della cage fra tre oggetti/componenti (asFacet)."""
    if not (cmds.objExists(obj_a) and cmds.objExists(obj_b) and cmds.objExists(obj_c)):
        return
    facet = cmds.polyCreateFacet(
        constructionHistory=False, name="asCageFacet", point=[_ws(obj_a), _ws(obj_b), _ws(obj_c)]
    )
    if any(obj.endswith("Left") for obj in (obj_a, obj_b, obj_c)):
        cmds.polyNormal(facet[0], constructionHistory=False, normalMode=0, userNormalMode=0)


def _create_cage_controllers(pps):
    """Controller + joint su ogni locator fittato. Ritorna i joint cage."""
    cage_joints = []
    for name in pps:
        for side, left, _b in _SIDES:
            if name in _MIDDLE:
                if side == "_L":
                    continue
                side = "_M"
            ctrl_type = 3
            if name.startswith("EyeBrow"):
                ctrl_type = 1
            if name == "EyeBrowInner":
                ctrl_type = 2
            if not cmds.objExists(name + left):
                continue
            cmds.xform("TempPos", worldSpace=True, translation=_ws(name + left))
            create_pp("TempPos", name, side, ctrl_type, True, False, False)
            if name.startswith("EyeBrow"):
                cmds.xform(
                    name + side + ".cv[0:99]",
                    relative=True,
                    objectSpace=True,
                    scale=(1.5, 1.5, 1.5),
                )
            cage_joints.append(name + "Joint" + side)
    return cage_joints


def _nose_crease_position(geometry, has_above_eye, nose_cv_nr):
    if has_above_eye:  # dal fit della fronte, se c'e'
        return _ws(_cv("ForeHeadCurve", nose_cv_nr))
    # altrimenti il vertice piu' centrale sul percorso fra le due palpebre
    start = get_face_fit_selection("upperEyeLidOuterCurve.cv[0]")
    end = get_face_fit_selection("upperEyeLidOuterCurveLeft.cv[0]")
    _select_least_edges_path(
        geometry, int(start.split("[")[1].rstrip("]")), int(end.split("[")[1].rstrip("]"))
    )
    cmds.select(cmds.polyListComponentConversion(toVertex=True))
    vtxs = _selected()
    if not vtxs:  # palpebre su shell separate (es. "Max")
        pos = _ws("upperEyeLidOuterCurve.cv[0]")
        locator = cmds.rename(cmds.spaceLocator()[0], "TempLocator")
        cmds.xform(locator, worldSpace=True, translation=(0, pos[1], pos[2]))
        vtxs = [get_face_fit_selection(locator)]
        cmds.delete(locator)
    return _ws(min(vtxs, key=lambda v: abs(_ws(v)[0])))


def _build_side_facets(left, spans, forehead, num_brow_mid, state):
    """Triangoli della cage di un lato (MEL:33083-33230)."""

    def n(name):
        return name + left

    upper_lip, lower_lip = n("upperLipOuterCurve"), n("lowerLipOuterCurve")
    upper_lid, lower_lid = n("upperEyeLidOuterCurve"), n("lowerEyeLidOuterCurve")
    forehead_curve = n("ForeHeadCurve")
    top_cv, outer_eye, side_cv, nose_cv = forehead

    for a, b, c in (
        ("SmileBulge", "Cheek", "FrownBulge"),
        ("Cheek", "SmileBulge", "CheekBone"),
        ("CheekRaiser", "SmileBulge", "NoseSide"),
        ("NoseCorner", "NoseSide", "SmileBulge"),
        ("SmileBulge", "CheekRaiser", "CheekBone"),
        ("Cheek", "CheekBone", "JawPivot"),
        ("Cheek", "JawPivot", "JawCorner"),
        ("Cheek", "JawCorner", "JawLine"),
        ("Cheek", "JawLine", "FrownBulge"),
    ):
        _facet(n(a), n(b), n(c))
    _facet(n("FrownBulge"), n("JawLine"), "Jaw")
    _facet("Jaw", "ChinCrease", n("FrownBulge"))

    # labbro inferiore
    _facet(n("SmileBulge"), n("FrownBulge"), _cv(upper_lip, 99))
    lower_spans = spans["lowerLip"]
    for i in range(lower_spans + 1):
        target = "ChinCrease" if i < lower_spans // 2 else n("FrownBulge")
        _facet(target, _cv(lower_lip, i), _cv(lower_lip, i + 1))
    _facet(n("FrownBulge"), "ChinCrease", _cv(lower_lip, lower_spans // 2))

    # labbro superiore e naso
    upper_spans = spans["upperLip"]
    split_1, split_2 = _round_half_up(upper_spans * 0.3), _round_half_up(upper_spans * 0.6)
    for i in range(upper_spans + 1):
        if i < split_1:
            target = "NoseUnder"
        elif i < split_2:
            target = n("NoseCorner")
        else:
            target = n("SmileBulge")
        _facet(_cv(upper_lip, i), target, _cv(upper_lip, i + 1))
    _facet(n("NoseCorner"), n("SmileBulge"), _cv(upper_lip, split_2))
    _facet(n("NoseCorner"), _cv(upper_lip, split_1), "NoseUnder")
    _facet(n("NoseCorner"), "NoseUnder", n("Nostril"))
    _facet("NoseUnder", "Nose", n("Nostril"))
    _facet(n("NoseSide"), n("NoseCorner"), n("Nostril"))
    _facet(n("NoseSide"), n("Nostril"), "Nose")
    _facet("NoseBridge", n("NoseSide"), "Nose")
    _facet(_cv(lower_lid, 0), n("NoseSide"), "NoseBridge")
    _facet(_cv(lower_lid, 0), "NoseBridge", _cv("ForeHeadCurve", nose_cv))

    # palpebra inferiore: il CV piu' vicino al CheekRaiser divide i target
    npc = cmds.createNode("nearestPointOnCurve", name="tempNearestPointOnCurve")
    cmds.connectAttr(lower_lid + ".worldSpace[0]", npc + ".inputCurve", force=True)
    if cmds.objExists(n("CheekRaiser")):
        state["pos"] = _ws(n("CheekRaiser"))
    pos = state["pos"]
    cmds.setAttr(npc + ".inPosition", pos[0], pos[1], pos[2], type="float3")
    u = cmds.getAttr(npc + ".result.parameter")
    # il MEL cancella per nome (MEL:33155): se Lip ha lasciato in scena il
    # suo `tempNearestPointOnCurve` sparisce quello, e resta questo (che Maya
    # ha chiamato ...1). Stesso nodo residuo del rig MEL.
    cmds.delete("tempNearestPointOnCurve")
    for i in range(spans["lowerLid"] + 1):
        if i < u / 2:
            target = n("NoseSide")
        elif i < u:
            target = n("CheekRaiser")
        else:
            target = n("CheekBone")
        _facet(target, _cv(lower_lid, i), _cv(lower_lid, i + 1))
    _facet(n("CheekRaiser"), n("NoseSide"), _cv(lower_lid, u / 2 + 1))
    _facet(n("CheekBone"), n("CheekRaiser"), _cv(lower_lid, u + 1))

    # stessa divisione che posiziona lowerLidOuter
    midway = side_cv + (outer_eye - side_cv) // 2
    _facet(n("JawPivot"), _cv(forehead_curve, midway), _cv(forehead_curve, side_cv))
    _facet(n("JawPivot"), n("CheekBone"), _cv(forehead_curve, midway))
    _facet(_cv(forehead_curve, outer_eye), _cv(forehead_curve, midway), n("CheekBone"))

    # sopra l'occhio
    _facet(_cv("ForeHeadCurve", nose_cv), "EyeBrowCenter", _cv(upper_lid, 0))
    _facet("EyeBrowCenter", n("EyeBrowInner"), _cv(upper_lid, 0))
    upper_lid_spans = spans["upperLid"]
    fraction = upper_lid_spans // (2 + num_brow_mid)
    for i in range(upper_lid_spans + 1):
        if i < fraction:
            state["target"] = n("EyeBrowInner")
        elif i < fraction * 2 and cmds.objExists("EyeBrowMid1"):
            state["target"] = n("EyeBrowMid1")
        elif i < fraction * 3 and cmds.objExists("EyeBrowMid2"):
            state["target"] = n("EyeBrowMid2")
        elif i < fraction * 4 and cmds.objExists("EyeBrowMid3"):
            state["target"] = n("EyeBrowMid3")
        elif i < fraction * 5:
            state["target"] = n("EyeBrowOuter")
        target = state["target"]
        _facet(_cv(upper_lid, i), target, _cv(upper_lid, i + 1))
        if target != state["previous"] and i > 0:
            _facet(state["previous"], target, _cv(upper_lid, i))
        state["previous"] = target

    # contorno della fronte ricostruito dalla cima al lato
    top_to_side = n("ForeHeadTopToSideCurve")
    if cmds.objExists("EyeBrowInner"):
        points = [_ws(_cv(forehead_curve, i)) for i in range(top_cv, side_cv + 1)]
        cmds.curve(name=top_to_side, degree=1, point=points)
        cmds.rebuildCurve(
            top_to_side,
            constructionHistory=0,
            replaceOriginal=1,
            rebuildType=0,
            endKnots=1,
            keepRange=0,
            keepControlPoints=0,
            keepEndPoints=0,
            keepTangents=0,
            spans=4 + num_brow_mid,
            degree=1,
            tolerance=0.01,
        )
        cmds.parent(top_to_side, "FaceBuildInProgressHidden")

    _facet("EyeBrowCenter", _cv(top_to_side, 0), n("EyeBrowInner"))
    _facet(_cv(top_to_side, 0), _cv(top_to_side, 1), n("EyeBrowInner"))
    cv_nr = 1
    state["previous"] = n("EyeBrowInner")
    for i in range(1, num_brow_mid + 2):
        target = n("EyeBrowMid{}".format(i))
        if i == num_brow_mid + 1:
            target = n("EyeBrowOuter")
        _facet(_cv(top_to_side, cv_nr), _cv(top_to_side, cv_nr + 1), target)
        _facet(_cv(top_to_side, cv_nr), target, state["previous"])
        state["previous"] = target
        cv_nr += 1
    last = 4 + num_brow_mid
    _facet(_cv(top_to_side, last - 1), _cv(top_to_side, last), _cv(forehead_curve, midway))
    _facet(_cv(top_to_side, last - 2), _cv(top_to_side, last - 1), n("EyeBrowOuter"))
    _facet(_cv(top_to_side, last - 1), _cv(forehead_curve, midway), n("EyeBrowOuter"))
    _facet(_cv(forehead_curve, midway), _cv(forehead_curve, outer_eye), n("EyeBrowOuter"))


def _closest_cage_vertices(curves):
    vtxs = []
    for curve in curves:
        if not cmds.objExists(curve):
            continue
        for i in range(cmds.getAttr(curve + ".spans") + 1):
            pos = _ws(_cv(curve, i))
            cmds.setAttr("closestSampler.inPosition", pos[0], pos[1], pos[2], type="float3")
            index = cmds.getAttr("closestSampler.result.closestVertexIndex")
            vtxs.append("asCage.vtx[{}]".format(index))
    return vtxs


def _bind_cage(geometry, skin_cluster, head_joint, cage_joints, simpler, has_below_eye, scale):
    """Unisce i triangoli in `asCage`, la skinna ai joint cage e prepara i
    pesi di bordo (palpebre copiate dal viso, labbra su cageOffJoint)."""
    cmds.polyUnite(
        cmds.ls("asCageFacet*"), constructionHistory=False, mergeUVSets=True, name="asCage"
    )
    cmds.polyMergeVertex(
        "asCage", constructionHistory=False, distance=scale / 345.5418, alwaysMergeTwoVertices=True
    )
    cmds.polyNormal("asCage", constructionHistory=False, normalMode=2, userNormalMode=0)
    cmds.sets("asCage", edit=True, forceElement="asRedSG")

    sc = cmds.skinCluster(
        [head_joint] + cage_joints,
        "asCage",
        toSelectedBones=True,
        maximumInfluences=3,
        dropoffRate=4,
        removeUnusedInfluence=False,
    )[0]
    cmds.rename(sc, "asCageSC")
    cmds.skinPercent("asCageSC", "asCage", transformValue=(head_joint, 1))
    joint_pos = [(joint, _ws(joint)) for joint in cage_joints]
    for i in range(cmds.polyEvaluate("asCage", vertex=True)):
        vtx = "asCage.vtx[{}]".format(i)
        pos_a = _ws(vtx)
        for joint, pos_b in joint_pos:
            if sum((pos_a[k] - pos_b[k]) ** 2 for k in range(3)) ** 0.5 < 0.01:
                cmds.skinPercent("asCageSC", vtx, transformValue=(joint, 1))

    for joint in cage_joints:
        if simpler and joint.startswith("lowerLidOuterJoint_"):  # gia' influenza
            continue
        cmds.skinCluster(
            skin_cluster, edit=True, dropoffRate=4, lockWeights=False, weight=0, addInfluence=joint
        )

    cmds.createNode("closestPointOnMesh", name="closestSampler")
    cmds.connectAttr("asCage.outMesh", "closestSampler.inMesh", force=True)
    lip_vtxs = _closest_cage_vertices(
        [
            "upperLipOuterCurve",
            "upperLipOuterCurveLeft",
            "lowerLipOuterCurve",
            "lowerLipOuterCurveLeft",
        ]
    )
    lid_vtxs = _closest_cage_vertices(
        ["upperEyeLidOuterCurve", "upperEyeLidOuterCurveLeft", "lowerEyeLidOuterCurve",
         "lowerEyeLidOuterCurveLeft"]
    )  # fmt: skip
    cmds.delete("closestSampler")

    # i bordi della cage sulle palpebre copiano i pesi del viso
    border_joints = []
    if has_below_eye:
        border_joints += cmds.listRelatives("LipJoints_M", allDescendents=True, type="joint") or []
    if simpler:
        border_joints += ["lowerLidOuterJoint_R", "lowerLidOuterJoint_L"]
    else:
        border_joints += (
            cmds.listRelatives("EyeLidJoints_M", allDescendents=True, type="joint") or []
        )
    for joint in border_joints:
        if simpler and joint.startswith("lowerLidOuterJoint_"):
            continue
        cmds.skinCluster("asCageSC", edit=True, lockWeights=False, weight=0, addInfluence=joint)
    cmds.select(geometry + ".vtx[0:99999]", lid_vtxs)
    cmds.copySkinWeights(
        noMirror=True, surfaceAssociation="closestPoint", influenceAssociation="closestJoint"
    )

    # i bordi sulle labbra vanno su un joint "spento"
    cmds.select(clear=True)
    cmds.joint(name="cageOffJoint")
    cmds.parent("cageOffJoint", "FaceBuildInProgressHidden")
    cmds.skinCluster(
        "asCageSC", edit=True, lockWeights=False, weight=0, addInfluence="cageOffJoint"
    )
    if lip_vtxs:
        cmds.skinPercent("asCageSC", lip_vtxs, transformValue=("cageOffJoint", 1))
    # serve anche sul viso, per la copia dei pesi
    cmds.skinCluster(
        skin_cluster, edit=True, lockWeights=False, weight=0, addInfluence="cageOffJoint"
    )

    cmds.sets(cage_joints, name="asCageJoints")
    cmds.sets("asCageJoints", add="FaceBuildingSets")


def _build_nose_region():
    """NoseRegion_M: serve prima di asFaceNose (lo usa LipSide)."""
    pos_a, pos_b = _ws("Nose"), _ws("NoseCorner")
    create_face_controller("NoseRegion", "_M", 4)
    cmds.delete("NoseRegionJoint_M")
    cmds.parent("NoseRegionOffset_M", "SideReverse_M")
    cmds.setAttr("NoseRegionOffset_M.s", 1, 1, 1, type="float3")
    cmds.scale(6, 6, 6, "NoseRegion_M.cv[0:7]", relative=True, pivot=(0, 0, 0))
    cmds.xform(
        "NoseRegionOffset_M",
        worldSpace=True,
        translation=(0, pos_a[1], (pos_a[2] + pos_b[2]) / 2.0),
    )

    def cv(index):
        return "NoseRegion_M.cv[{}]".format(index)

    def set_cv(index, x, y, z):
        cmds.xform(cv(index), worldSpace=True, translation=(x, y, z))

    pos_a, pos_b, pos_c = _ws(cv(1)), _ws("NoseCorner"), _ws("Nose")
    set_cv(1, 0, pos_c[1] - pos_b[0] * 1.5, pos_a[2])
    pos_a, pos_b, pos_c = _ws(cv(5)), _ws("NoseUnder"), _ws("NoseCorner")
    set_cv(5, 0, pos_b[1], pos_a[2])
    set_cv(4, pos_c[0] / 2.0, pos_b[1], pos_a[2])
    set_cv(6, pos_c[0] / -2.0, pos_b[1], pos_a[2])
    pos_a, pos_b = _ws(cv(3)), _ws("NoseCorner")
    set_cv(3, pos_b[0] * 1.2, pos_b[1] + pos_b[0] / -5.0, pos_a[2])
    set_cv(7, pos_b[0] * -1.2, pos_b[1] + pos_b[0] / -5.0, pos_a[2])
    set_cv(2, pos_b[0] * 0.65, pos_b[1] + pos_b[0] / -2.0, pos_a[2])
    set_cv(0, pos_b[0] * -0.65, pos_b[1] + pos_b[0] / -2.0, pos_a[2])
    cmds.parent(
        "NostrilOffset_R",
        "NostrilOffset_L",
        "NoseSideOffset_R",
        "NoseSideOffset_L",
        "NoseOffset_M",
        "NoseUnderOffset_M",
        "NoseBridgeOffset_M",
        "NoseCornerOffset_R",
        "NoseCornerOffset_L",
        "NoseRegion_M",
    )


def face_face_cage() -> bool:
    """Costruisce i controller cage e la mesh `asCage` (asFaceFaceCage).

    Returns:
        True anche quando lo step e' saltato perche' mancano sia il fit
        delle labbra sia quello delle sopracciglia (gate MEL); False con
        warning se manca un prerequisito del build.
    """
    if not cmds.objExists(FIT_SKELETON):
        cmds.warning("face_face_cage: FaceFitSkeleton not found")
        return False
    remove_fit_animations_from_on_face_ctrls()
    as_face_hide_controllers(True)
    has_above_eye = cmds.objExists("EyeBrowInner")
    has_below_eye = cmds.objExists("upperLipMainCurve")
    if not has_above_eye and not has_below_eye:
        return True

    geometry = get_fit_option("Face") or ""
    head_joint = get_fit_option("HeadJoint") or ""
    skin_cluster = get_fit_option("SkinCluster") or ""
    required = [geometry, head_joint, skin_cluster, "FaceJoint_M", "FaceBuildInProgressHidden"]
    required += ["FaceBuildingSets", "EyeLidJoints_M", "upperEyeLidOuterCurve"]
    required += ["lowerEyeLidOuterCurve", "lowerLidOuterJoint_R", "lowerLidOuterJoint_L"]
    missing = [node for node in required if not node or not cmds.objExists(node)]
    if missing:
        cmds.warning("face_face_cage: missing {}".format(", ".join(missing) or "options"))
        return False
    if get_fit_option("MultiSkinClusters"):
        cmds.warning("face_face_cage: multiSkinClusters is not ported yet")

    simpler = bool(get_fit_option("SimplerEyeLid"))
    scale = cmds.getAttr(FIT_SKELETON + ".faceScale")
    spans = {
        "upperLid": cmds.getAttr("upperEyeLidOuterCurve.spans"),
        "lowerLid": cmds.getAttr("lowerEyeLidOuterCurve.spans"),
        "upperLip": 0,
        "lowerLip": 0,
    }
    if has_below_eye:
        spans["upperLip"] = cmds.getAttr("upperLipOuterCurve.spans")
        spans["lowerLip"] = cmds.getAttr("lowerLipOuterCurve.spans")
    num_brow_mid = 0
    nose_cv_nr = 0
    pps = list(_PPS)
    if has_above_eye:
        nose_cv_nr = cmds.getAttr("FaceFitForeHead.noseCvNr")
        brows = ["EyeBrowInner"]
        for i in range(1, 4):
            if cmds.objExists("EyeBrowMid{}".format(i)):
                num_brow_mid = i
                brows.append("EyeBrowMid{}".format(i))
        brows.append("EyeBrowOuter")
        if cmds.objExists("EyeBrowCenter"):
            brows.append("EyeBrowCenter")
        pps += brows

    cmds.createNode("transform", name="TempPos")
    cage_joints = _create_cage_controllers(pps)
    if has_below_eye:
        pos = _nose_crease_position(geometry, has_above_eye, nose_cv_nr)
        cmds.xform("TempPos", worldSpace=True, translation=pos)
        create_pp("TempPos", "NoseCrease", "_M", 3, True, False, False)
        cage_joints.append("NoseCreaseJoint_M")

    # anche il lowerLidOuter fa parte della cage
    cage_joints += ["lowerLidOuterJoint_R", "lowerLidOuterJoint_L"]
    if not simpler:
        cmds.parent("lowerLidOuterJoint_R", "lowerLidOuterJoint_L", "FaceJoint_M")
        for side in ("_R", "_L"):
            joint = "lowerLidOuterJoint" + side
            cmds.connectAttr(
                "FaceJoint_M.worldInverseMatrix",
                "lowerLidOuterJointMM" + side + ".matrixIn[2]",
                force=True,
            )
            cmds.xform(joint, objectSpace=True, translation=(0, 0, 0))
            as_opm_scale_reset(joint)
    cmds.delete("TempPos")

    if has_below_eye:  # segnaposto del CheekRaiser
        for side, left, _b in _SIDES:
            holder = cmds.createNode(
                "transform", name="CheekRaiser" + left, parent="FaceBuildInProgressHidden"
            )
            cmds.xform(holder, worldSpace=True, translation=_ws("lowerLidOuter" + side))

    state = {"pos": [0.0, 0.0, 0.0], "target": "", "previous": ""}  # variabili MEL mai azzerate
    for _side, left, _b in _SIDES:
        forehead = (0, 0, 0, nose_cv_nr)
        if has_above_eye:
            fit = "FaceFitForeHead" + left
            forehead = (
                cmds.getAttr("FaceFitForeHead.topCvNr"),
                cmds.getAttr(fit + ".outerEyeCnrNr"),
                cmds.getAttr(fit + ".sideCvNr"),
                cmds.getAttr(fit + ".noseCvNr"),
            )
        _build_side_facets(left, spans, forehead, num_brow_mid, state)

    _bind_cage(geometry, skin_cluster, head_joint, cage_joints, simpler, has_below_eye, scale)
    if has_below_eye:
        _build_nose_region()

    # i controller delle sopracciglia restano nascosti per ora
    for node in cmds.listRelatives("OnFacecontrols", allDescendents=True, type="transform") or []:
        if node.startswith("EyeBrow") and "Offset_" in node:
            cmds.setAttr(node + ".v", 0)
    cmds.setAttr(geometry + ".v", 0)
    cmds.select(clear=True)
    return True

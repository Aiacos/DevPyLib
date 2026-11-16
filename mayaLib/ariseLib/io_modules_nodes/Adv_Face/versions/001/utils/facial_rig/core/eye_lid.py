"""Build della palpebra (parita' asFaceEyeLid, MEL:29843-31030).

La procedura piu' lunga del build. Nell'ordine del MEL:

1. gerarchia LidSetup/LidJoints, EyeLidJoints_M, LidSetup<side> che segue
   EyeRegion<side>, e un FaceControlOrient dedicato alle palpebre;
2. set di area eyeLidArea / eyeLidOuterArea (crescita della selezione fra i
   loop fittati Outer, Main, Inner);
3. per lato e per upper/lower, sulle fit-curve Main e Outer: curve di
   deformazione (Curve, CurveTweak, Fleshy, Blink, UnClosed/Closed), joint
   per-CV con la rete aim (loc su pointOnCurveInfo -> aimMatrix -> Aim ->
   AimEnd -> joint), LidOut, blendShape delle curve, controller
   (inner/outer, Lid1-4, Lid) con asCreatePP e skinCluster della CurveTweak;
4. curve "fleshy" (seguono la rotazione dell'occhio) e blendShape di blink;
5. attributi blink / blinkCenter / lidOut / fleshy sui controller;
6. pesatura della mesh: joint per-CV come influenze, peso pieno sul loop
   Main, weight hammer delle aree, sfumatura per riga Main->Outer;
7. dual quaternion sull'area palpebra, set eyeLidMainArea.

Divergenze (docs/gap-analysis.md §5h), tutte con warning e skip:
- multiSkinClusters (MEL:29877, 30239-30249, 30310-30320);
- eyeBrow su shell separata dalla palpebra (asTempSingleShellFace,
  MEL:30032-30049);
- nonSphericalEye (MEL:30267-30281);
- eyelash (asFaceAttachEyeLashes, MEL:30960-30964);
- il progressBar della UI non esiste in batch e non e' replicato.
"""

import re

import maya.cmds as cmds

from .build_utils import (
    as_align,
    as_face_hide_controllers,
    as_matrix_connect_attr,
    as_opm_scale_reset,
    as_parent_constraint,
)
from .ctrl_box import create_face_controller, place_ctrl_by_projection
from .driving_system import ensure_output_blend_weighted, unit_convert_and_reverse
from .face_ctrl_pp import (
    create_pp,
    face_add_constrained,
    face_half_moon_curve,
    set_rgb_override_color,
    weight_hammer_verts_ms,
)
from .face_prep import include_below_eyes
from .fit_options import FIT_SKELETON, get_fit_option
from .fitting import _select_least_edges_path, get_face_fit_selection

_SIDES = (("_R", "", 1), ("_L", "Left", -1))
_UPPER_LOWER = (("upper", 1), ("lower", -1))
_OUTER_MAIN = (("Main", "", True), ("Outer", "Outer", False))
_CORNERS = ("inner", "upper", "outer", "lower")
_GREEN = (0.147, 0.578, 0.147)
_BLUE = (0.0, 0.27, 1.0)


def _selected():
    return cmds.ls(selection=True, flatten=True) or []


def _select_fit(fit_object):
    """Seleziona i vertici campionati da un oggetto fit; ritorna la lista."""
    text = get_face_fit_selection(fit_object)
    if text.strip():
        cmds.select(text.split())
    else:
        cmds.select(clear=True)
    return _selected()


def _fit_vtxs(fit_object):
    return get_face_fit_selection(fit_object).split()


def _grow():
    cmds.polySelectConstraint(propagate=1, type=0x0001)


def _grow_by_edges():
    """ConvertSelectionToEdges + ConvertSelectionToVertices."""
    cmds.select(cmds.polyListComponentConversion(toEdge=True))
    cmds.select(cmds.polyListComponentConversion(toVertex=True))


def _vtx_nr(component):
    return int(component.split("[")[1].split("]")[0])


def _smoothstep(edge0, edge1, x):
    t = max(0.0, min(1.0, (x - edge0) / float(edge1 - edge0)))
    return t * t * (3 - 2 * t)


def _new_skin_cluster(joints, geometry, name, max_influences=3):
    sc = cmds.skinCluster(
        list(joints),
        geometry,
        toSelectedBones=True,
        maximumInfluences=max_influences,
        dropoffRate=4,
        removeUnusedInfluence=False,
    )[0]
    return cmds.rename(sc, name)


def _add_slider_attr(node, attr, default=0):
    """addAttr -k 1 -at double -smx 10 -hsx 1 -smn 0 -hnv 1."""
    cmds.addAttr(
        node,
        longName=attr,
        keyable=True,
        attributeType="double",
        softMaxValue=10,
        hasSoftMaxValue=True,
        softMinValue=0,
        hasMinValue=True,
        defaultValue=default,
    )


def _aim_matrix(name):
    am = cmds.createNode("aimMatrix", name=name)
    cmds.setAttr(am + ".primaryInputAxis", 1, 0, 0, type="float3")
    cmds.setAttr(am + ".secondaryMode", 2)
    cmds.setAttr(am + ".secondaryInputAxis", 0, 1, 0, type="float3")
    cmds.setAttr(am + ".secondaryTargetVector", 0, 1, 0, type="float3")
    return am


def _skip_lower(upper_lower, i, num_lid):
    """Il lower non ripete i punti di inizio/fine, condivisi con l'upper."""
    return upper_lower == "lower" and (i == 0 or i == num_lid - 1)


# ---------------------------------------------------------------------------
# 1. base
# ---------------------------------------------------------------------------


def _build_base(skin_cluster):
    for ctrl in ("ctrlEye_L", "ctrlEye_R"):
        cmds.setAttr(ctrl + ".tx", 0)
        cmds.setAttr(ctrl + ".ty", 0)
    as_face_hide_controllers(True)
    for node in ("ctrlBoxEye_R", "ctrlBoxEye_L", "EyeRegionOffset_R", "EyeRegionOffset_L"):
        cmds.setAttr(node + ".v", 1)

    cmds.createNode("transform", name="LidSetup", parent="FaceDeformationSystem")
    cmds.createNode("transform", name="LidJoints", parent="LidSetup")
    cmds.createNode("transform", name="TempPos")
    cmds.createNode("transform", name="FaceBuildEyeLidCurves", parent="FaceBuildInProgress")

    cmds.select("FaceJoint_M")
    cmds.joint(name="EyeLidJoints_M")
    pos = cmds.xform("Eye_R", query=True, worldSpace=True, translation=True)
    cmds.xform("EyeLidJoints_M", worldSpace=True, translation=(0, pos[1], pos[2]))
    cmds.setAttr("EyeLidJoints_M.drawStyle", 2)
    cmds.skinCluster(
        skin_cluster,
        edit=True,
        dropoffRate=4,
        lockWeights=False,
        weight=0,
        addInfluence="EyeLidJoints_M",
    )

    for side, _left, _b in _SIDES:
        cmds.createNode("transform", name="LidSetup" + side)
        as_align("LidSetup" + side, "Eye" + side, translate=True, rotate=True)
        as_parent_constraint("EyeRegion" + side, "LidSetup" + side)
        cmds.parent("LidSetup" + side, "LidSetup")
        cmds.parent("EyeRegionJoint" + side, "LidJoints")


def _build_lid_control_orient(scale):
    """FaceControlOrient dedicato alle palpebre: un piano a 3 fasce i cui
    bordi seguono gli angoli degli occhi (MEL:29907-29940)."""
    cmds.rename("FaceControlOrient", "FaceControlSuspended")
    plane = "FaceControlOrient"
    shape = "FaceControlOrientShape"

    def ws(component):
        return cmds.xform(component, query=True, worldSpace=True, translation=True)

    pos_a = ws("upperEyeLidMainCurve.cv[99]")
    pos_b = ws("upperEyeLidMainCurve.cv[0]")
    cmds.polyPlane(
        name=plane,
        width=1,
        height=1,
        subdivisionsX=3,
        subdivisionsY=1,
        axis=(0, 1, 0),
        createUVs=2,
        constructionHistory=False,
    )
    cmds.sets(plane, edit=True, forceElement="asRedSG")
    cmds.polySoftEdge(plane, angle=0, constructionHistory=False)
    cmds.xform(
        plane,
        worldSpace=True,
        translation=(0, (pos_a[1] + pos_b[1]) / 2.0, (pos_a[2] + pos_b[2]) / 2.0),
    )
    cmds.setAttr(plane + ".rx", 90)
    cmds.setAttr(plane + ".s", scale, scale, scale, type="float3")

    def snap(vtx, pos):
        component = "{}.vtx[{}]".format(shape, vtx)
        cmds.xform(component, worldSpace=True, translation=(pos[0], ws(component)[1], pos[2]))

    for vtx, pos in ((4, pos_a), (0, pos_a), (5, pos_b), (1, pos_b)):
        snap(vtx, pos)
    pos_a = ws("upperEyeLidMainCurveLeft.cv[99]")
    pos_b = ws("upperEyeLidMainCurveLeft.cv[0]")
    for vtx, pos in ((7, pos_a), (3, pos_a), (6, pos_b), (2, pos_b)):
        snap(vtx, pos)
    # palpebre dalla forma strana possono "sforare" in X oltre gli angoli
    cmds.scale(
        1.1,
        1.1,
        1,
        plane + ".vtx[0]",
        plane + ".vtx[3:4]",
        plane + ".vtx[7]",
        relative=True,
        objectCenterPivot=True,
    )
    cmds.scale(
        0.7, 1.1, 1, plane + ".vtx[1:2]", plane + ".vtx[5:6]", relative=True, objectCenterPivot=True
    )
    cmds.parent(plane, "FaceBuildInProgressHidden")


# ---------------------------------------------------------------------------
# 2. aree
# ---------------------------------------------------------------------------


def _build_lid_area_sets():
    """eyeLidArea(+Left): tutto cio' che sta fra i loop Outer e Inner."""
    for _side, left, _b in _SIDES:
        outer_vtxs = _select_fit("FaceFitEyeLidOuterCurve" + left)
        main_vtxs = _select_fit("FaceFitEyeLidMainCurve" + left)
        inner_vtxs = _select_fit("FaceFitEyeLidInnerCurve" + left)
        cmds.select(main_vtxs)
        for _ in range(20):
            _grow()
            cmds.select(outer_vtxs, inner_vtxs, deselect=True)
        cmds.select(main_vtxs, add=True)
        cmds.sets(name="eyeLidArea" + left)
        cmds.sets("eyeLidArea" + left, add="FaceAreas")


def _build_lid_outer_area_sets(geometry):
    """eyeLidOuterArea(+Left): dal loop Outer verso il sopracciglio.
    Ritorna il numero di righe di crescita dell'ultimo lato (serve al ramo
    simplerEyeLid, come la variabile $numGrow del MEL)."""
    num_grow = 0
    below_eyes = include_below_eyes()
    for side, left, _b in _SIDES:
        area = "eyeLidOuterArea" + left
        cmds.sets(name=area, empty=True)
        cmds.sets(area, add="FaceAreas")

        if cmds.objExists("EyeBrowInner" + left):  # assente in modalita' skip-above-eyes
            _select_fit("EyeBrowInner" + left)
        cmds.refresh()
        brow_inner = (_selected() or [""])[0]
        if cmds.objExists("EyeBrowOuter" + left):
            _select_fit("EyeBrowOuter" + left)
        cmds.refresh()
        brow_outer = (_selected() or [""])[0]

        _select_fit("FaceFitEyeLidOuterCurve" + left)
        cmds.ConvertSelectionToShell()
        if brow_inner not in _selected() and cmds.objExists("EyeBrowInner"):
            cmds.warning(
                "face_eye_lid: the eyebrow is on a different mesh shell than the eyelid "
                "(side {}); the nearest-vertex fallback is not ported, eyeLidOuterArea may "
                "grow too far".format(side)
            )

        cheek_vtx = nose_vtx = ""
        if below_eyes:
            cheek_vtx = (_select_fit("CheekBone" + left) or [""])[0]
            nose_vtx = (_select_fit("NoseCorner" + left) or [""])[0]

        _select_fit("FaceFitEyeLidOuterCurve" + left)
        ring = []
        for i in range(25):
            num_grow = i + 1
            _grow()
            cmds.select("eyeLidArea" + left, deselect=True)
            if ring:
                cmds.select(ring, deselect=True)
            ring = _selected()
            if brow_inner in ring or brow_outer in ring:
                break
            if not cmds.objExists("EyeBrowInner") and i == 1:
                break
            # mesh fitta fra Main e Outer ma rada oltre Outer: non esagerare
            if cheek_vtx in ring or nose_vtx in ring:
                num_grow -= 2
                if side == "_R":
                    print(
                        "// EyeLid mesh highly more dense between Main and Outer, than beyond "
                        "Outer, so reducing eyeLidOuterArea to: {} edgeRows.".format(num_grow)
                    )
                break

        _select_fit("FaceFitEyeLidOuterCurve" + left)
        for _ in range(num_grow):
            _grow()
            cmds.select("eyeLidArea" + left, deselect=True)
        if _selected():
            cmds.sets(_selected(), add=area)
        cmds.refresh()
    return num_grow


# ---------------------------------------------------------------------------
# 3. curve, joint per-CV, controller
# ---------------------------------------------------------------------------


def _build_curves(upper_lower, outer_main, side, left, non_symmetrical):
    """Curve di deformazione duplicate dalla fit-curve (MEL:30149-30181)."""
    fit_curve = "{}EyeLid{}Curve{}".format(upper_lower, outer_main, left)
    curve = "{}Lid{}Curve{}".format(upper_lower, outer_main, side)
    cmds.duplicate(fit_curve, name=curve)
    cmds.rebuildCurve(
        curve,
        constructionHistory=0,
        replaceOriginal=1,
        rebuildType=0,
        endKnots=1,
        keepRange=0,
        keepControlPoints=0,
        keepEndPoints=1,
        keepTangents=0,
        spans=5,
        degree=3,
        tolerance=0.004,
    )
    if side == "_L" and not non_symmetrical:
        # la fit-curve Left auto-generata ha sx=-1: congelala
        cmds.parent(curve, world=True)
        cmds.refresh()
        cmds.makeIdentity(curve, apply=True, translate=True, rotate=True, scale=True)
    cmds.parent(curve, "LidCurves" + side)

    cmds.duplicate(curve, name="{}Lid{}CurveTweak{}".format(upper_lower, outer_main, side))
    if outer_main == "Main":
        cmds.duplicate(curve, name="{}LidCurveFleshy{}".format(upper_lower, side))
        cmds.duplicate(curve, name="{}LidCurveBlink{}".format(upper_lower, side))
        cmds.duplicate(curve, name="{}UnClosedLidCurve{}".format(upper_lower, side))
        # la curva "chiusa" di una palpebra e' la forma dell'altra
        opposite = "lower" if upper_lower == "upper" else "upper"
        cmds.duplicate(curve, name="{}ClosedLidCurve{}".format(opposite, side))
        # la curva Main segue la regione dell'occhio
        _new_skin_cluster(
            ["EyeRegionJoint" + side], curve, "{}Lid{}SC{}".format(upper_lower, outer_main, side)
        )
    return fit_curve, curve


def _build_cv_joint(prefix, i, side, pos, curve, scale, npc):
    """Joint per-CV con la rete aim che lo tiene sulla curva
    (MEL:30184-30237). `prefix` = "<upperLower>Lid<outerMain>"."""
    joint = "{}{}{}".format(prefix, i, side)
    cmds.select(clear=True)
    cmds.joint(name=joint)
    cmds.setAttr(joint + ".segmentScaleCompensate", 0)
    cmds.setAttr(joint + ".radius", 0.1)
    cmds.xform(joint, worldSpace=True, translation=pos)
    cmds.parent(joint, "EyeLidJoints_M")

    loc = "{}Loc{}{}".format(prefix, i, side)
    cmds.spaceLocator(name=loc)
    cmds.setAttr(loc + ".localScale", scale / 100.0, scale / 100.0, scale / 100.0, type="float3")
    cmds.parent(loc, "LidLocs" + side)
    poci = cmds.createNode("pointOnCurveInfo", name="{}Poci{}{}".format(prefix, i, side))
    cmds.setAttr(npc + ".inPosition", pos[0], pos[1], pos[2], type="float3")
    cmds.setAttr(poci + ".parameter", cmds.getAttr(npc + ".parameter"))
    cmds.connectAttr(poci + ".position", loc + ".translate")
    cmds.connectAttr(curve + "Shape.worldSpace[0]", poci + ".inputCurve")

    aim = cmds.createNode("transform", name="{}{}Aim{}".format(prefix, i, side))
    cmds.parent(aim, "LidSetup" + side)
    cmds.setAttr(aim + ".t", 0, 0, 0, type="float3")
    cmds.setAttr(aim + ".r", 0, 0, 0, type="float3")
    am = _aim_matrix("{}Loc{}AimAM{}".format(prefix, i, side))
    cmds.connectAttr(loc + ".worldMatrix[0]", am + ".primaryTargetMatrix")
    cmds.connectAttr("LidSetup" + side + ".worldMatrix[0]", am + ".secondaryTargetMatrix")
    cmds.connectAttr("EyeRegion" + side + ".worldMatrix[0]", am + ".inputMatrix")
    mm = cmds.createNode("multMatrix", name="{}{}AimMM{}".format(prefix, i, side))
    cmds.connectAttr(am + ".outputMatrix", mm + ".matrixIn[1]")
    cmds.connectAttr("LidSetup" + side + ".worldInverseMatrix[0]", mm + ".matrixIn[2]")
    pm = cmds.createNode("pickMatrix", name="{}Loc{}AimPM{}".format(prefix, i, side))
    for flag in ("useTranslate", "useScale", "useShear"):
        cmds.setAttr("{}.{}".format(pm, flag), 0)
    cmds.connectAttr(mm + ".matrixSum", pm + ".inputMatrix")
    as_matrix_connect_attr(pm + ".outputMatrix", aim + ".offsetParentMatrix")

    aim_end = cmds.createNode("transform", name="{}{}AimEnd{}".format(prefix, i, side), parent=aim)
    cmds.xform(aim_end, worldSpace=True, translation=pos)
    as_parent_constraint(
        aim_end, joint, maintain_offset=True, include_pick_matrix=True, force_mult_matrix=True
    )
    joint_pm = "{}{}PM{}".format(prefix, i, side)
    cmds.setAttr(joint_pm + ".useScale", 0)
    cmds.setAttr(joint_pm + ".useShear", 0)


def _build_lid_out(upper_lower, i, num_lid, side, scale):
    """Spinta in fuori del joint (attr LidSetup.<upperLower>LidOut),
    massima al centro della palpebra (MEL:30258-30286)."""
    mult = cmds.createNode("multiplyDivide", name="{}LidOutMult{}{}".format(upper_lower, i, side))
    if i < num_lid // 2:
        factor = _smoothstep(0, num_lid, i)
    else:
        factor = _smoothstep(0, num_lid, num_lid - 1 - i)
    cmds.setAttr(mult + ".input1X", factor * (scale / 3.0))
    cmds.connectAttr("LidSetup{}.{}LidOut".format(side, upper_lower), mult + ".input2X")

    aim_end = "{}LidMain{}AimEnd{}".format(upper_lower, i, side)
    pma = cmds.createNode("plusMinusAverage", name="{}LidOut{}{}".format(upper_lower, i, side))
    cmds.setAttr(pma + ".input1D[0]", cmds.getAttr(aim_end + ".tx"))
    cmds.connectAttr(mult + ".outputX", pma + ".input1D[1]")
    cmds.connectAttr(pma + ".output1D", aim_end + ".tx")


def _detach_outer_from_eye_curvature(upper_lower, i, side):
    """I joint Outer non seguono la curvatura dell'occhio: via la rete aim,
    seguono solo la posizione della loc (MEL:30296-30311)."""
    joint = "{}LidOuter{}{}".format(upper_lower, i, side)
    pos = cmds.xform(joint, query=True, worldSpace=True, translation=True)
    cmds.delete("{}LidOuter{}Aim{}".format(upper_lower, i, side))
    mm = "{}LidOuter{}MM{}".format(upper_lower, i, side)
    if cmds.objExists(mm):
        cmds.delete(mm)  # porta via anche PM e DM
    cmds.xform(joint, worldSpace=True, translation=pos)
    as_parent_constraint(
        "{}LidOuterLoc{}{}".format(upper_lower, i, side),
        joint,
        include_pick_matrix=True,
        force_mult_matrix=True,
    )
    pm = "{}LidOuter{}PM{}".format(upper_lower, i, side)
    for flag in ("useRotate", "useScale", "useShear"):
        cmds.setAttr("{}.{}".format(pm, flag), 0)


def _eye_lid_attach_pp(name, side):
    """Inserisce un controller PP nel setup della palpebra
    (asEyeLidAttachPP, MEL:42834-42903)."""
    left = "Left" if side == "_L" else ""
    is_outer = name.endswith("Outer")
    upper_lower = "lower" if name.startswith("lower") else "upper"

    if not re.search(r"Lid[0-9]", name):
        cmds.parent(name + "Offset" + side, "EyeRegion" + side)

    joint = name + "Joint" + side
    joint_mm = name + "JointMM" + side
    if cmds.objExists(name + "JointOffset" + side):
        cmds.parent(name + "JointOffset" + side, "LidJoints")
    elif cmds.objExists(joint):
        cmds.parent(joint, "LidJoints")
        cmds.connectAttr("LidJoints.worldInverseMatrix", joint_mm + ".matrixIn[2]", force=True)
        cmds.xform(
            joint, objectSpace=True, translation=(0, 0, 0), rotation=(0, 0, 0), scale=(1, 1, 1)
        )
        matrix = cmds.xform("FaceGroup", query=True, objectSpace=True, matrix=True)
        cmds.setAttr(joint_mm + ".matrixIn[0]", matrix, type="matrix")
    if is_outer:
        return

    # aggancia il controller all'AimEnd piu' vicino della curva Main
    num_lid = cmds.getAttr("{}EyeLidMainCurve{}.spans".format(upper_lower, left)) + 1
    pos_a = cmds.xform(name + side, query=True, worldSpace=True, translation=True)
    attach_to, min_dist = "", 999.0
    for i in range(num_lid):
        aim_end = "{}LidMain{}AimEnd{}".format(upper_lower, i, side)
        if not cmds.objExists(aim_end):
            continue
        pos_b = cmds.xform(aim_end, query=True, worldSpace=True, translation=True)
        dist = sum((pos_a[k] - pos_b[k]) ** 2 for k in range(3)) ** 0.5
        if dist < min_dist:
            min_dist, attach_to = dist, aim_end
    as_parent_constraint(
        attach_to,
        name + "Attach" + side,
        maintain_offset=True,
        include_pick_matrix=True,
        force_mult_matrix=True,
    )
    pm = name + "AttachPM" + side
    for flag in ("useRotate", "useScale", "useShear"):
        cmds.setAttr("{}.{}".format(pm, flag), 0)


def _build_controllers(upper_lower, factor, outer_main, out_name, attacher, side, scale):
    """Controller della curva (MEL:30330-30395): inner/outer (solo nel giro
    upper), Lid1-4, Lid centrale; skinCluster e pesi della CurveTweak."""
    curve = "{}Lid{}Curve{}".format(upper_lower, outer_main, side)
    tweak = "{}Lid{}CurveTweak{}".format(upper_lower, outer_main, side)

    if upper_lower == "upper":
        for corner, cv in (("inner", 0), ("outer", 7)):
            name = corner + "Lid" + out_name
            create_pp("upperLid{}Curve{}.cv[{}]".format(outer_main, side, cv), name, side, 2,
                      True, False, attacher)  # fmt: skip
            _eye_lid_attach_pp(name, side)

    for d in range(1, 5):
        name = "{}Lid{}{}".format(upper_lower, d, out_name)
        create_pp("{}.cv[{}]".format(curve, d + 1), name, side, 1, True, False, attacher)
        _eye_lid_attach_pp(name, side)
        cmds.move(0, 0, scale / 200.0, name + side + ".cv[0:99]",
                  relative=True, objectSpace=True, worldSpaceDistance=True)  # fmt: skip

    lid = upper_lower + "Lid" + out_name
    cmds.delete(
        cmds.pointConstraint(
            "{}Lid2{}{}".format(upper_lower, out_name, side),
            "{}Lid3{}{}".format(upper_lower, out_name, side),
            "TempPos",
        )
    )
    create_pp("TempPos", lid, side, 2, True, False, attacher)
    _eye_lid_attach_pp(lid, side)
    cmds.move(0, 0, scale / 100.0, lid + side + ".cv[0:99]",
              relative=True, objectSpace=True, worldSpaceDistance=True)  # fmt: skip

    if outer_main == "Outer":
        # Main guida i controller piccoli via curva; Outer usa il follow
        for d, corner, value in ((1, "inner", 6.5), (2, "inner", 10), (3, "outer", 10),
                                 (4, "outer", 6.5)):  # fmt: skip
            face_add_constrained(
                "{}Lid{}{}{}".format(upper_lower, d, out_name, side),
                lid + side,
                corner + "Lid" + out_name + side,
                value,
            )

    inner_joint = "innerLid{}Joint{}".format(out_name, side)
    outer_joint = "outerLid{}Joint{}".format(out_name, side)
    lid_joints = ["{}Lid{}{}Joint{}".format(upper_lower, d, out_name, side) for d in range(1, 5)]
    tweak_sc = _new_skin_cluster(
        [outer_joint, inner_joint] + lid_joints,
        tweak,
        "{}Lid{}CurveTweakSC{}".format(upper_lower, outer_main, side),
    )
    cmds.skinPercent(tweak_sc, tweak + ".cv[0]", transformValue=(inner_joint, 1))
    cmds.skinPercent(tweak_sc, tweak + ".cv[7]", transformValue=(outer_joint, 1))
    for d in range(2, 6):
        cmds.skinPercent(
            tweak_sc, "{}.cv[{}]".format(tweak, d), transformValue=(lid_joints[d - 2], 1)
        )

    # cv 1 e 6 bilanciati (il MEL lo applica sempre alla curva Main)
    main_tweak = "{}LidMainCurveTweak{}".format(upper_lower, side)
    main_sc = "{}LidMainCurveTweakSC{}".format(upper_lower, side)
    for cv, corner, d in ((1, "inner", 1), (6, "outer", 4)):
        component = "{}.cv[{}]".format(main_tweak, cv)
        cmds.skinPercent(main_sc, component, transformValue=(corner + "LidJoint" + side, 1))
        cmds.skinPercent(
            main_sc, component, transformValue=("{}Lid{}Joint{}".format(upper_lower, d, side), 0.33)
        )

    face_half_moon_curve(lid + side, 90 * factor)
    if upper_lower == "upper":
        face_half_moon_curve("innerLid" + out_name + side, 180)
        face_half_moon_curve("outerLid" + out_name + side, 0)


def _build_side_lids(side, left, scale, simpler, non_symmetrical, npc):
    for attr in ("upperLidOut", "lowerLidOut"):
        cmds.addAttr(
            "LidSetup" + side,
            keyable=True,
            longName=attr,
            attributeType="double",
            defaultValue=0,
            softMinValue=0,
            hasSoftMinValue=True,
            softMaxValue=1,
            hasSoftMaxValue=True,
        )
    cmds.createNode("transform", name="LidLocs" + side)
    cmds.setAttr("LidLocs" + side + ".inheritsTransform", 0)
    cmds.parent("LidLocs" + side, "LidSetup")
    cmds.createNode("transform", name="LidCurves" + side)
    cmds.parent("LidCurves" + side, "FaceDeformationSystem")

    for upper_lower, factor in _UPPER_LOWER:
        for outer_main, out_name, attacher in _OUTER_MAIN:
            if simpler and outer_main == "Outer":
                continue
            prefix = "{}Lid{}".format(upper_lower, outer_main)
            fit_curve, curve = _build_curves(upper_lower, outer_main, side, left, non_symmetrical)
            num_lid = cmds.getAttr(fit_curve + ".spans") + 1
            indices = [i for i in range(num_lid) if not _skip_lower(upper_lower, i, num_lid)]

            cmds.connectAttr(curve + ".worldSpace[0]", npc + ".inputCurve", force=True)
            for i in indices:
                pos = cmds.xform(
                    "{}.cv[{}]".format(fit_curve, i), query=True, worldSpace=True, translation=True
                )
                _build_cv_joint(prefix, i, side, pos, curve, scale, npc)

            tweak = prefix + "CurveTweak" + side
            if outer_main == "Main":  # spinta in fuori e chiusura solo sul Main
                for i in indices:
                    if 0 < i < num_lid - 1:
                        _build_lid_out(upper_lower, i, num_lid, side, scale)
                cmds.blendShape(
                    tweak,
                    upper_lower + "LidCurveBlink" + side,
                    upper_lower + "LidCurveFleshy" + side,
                    curve,
                    name=prefix + "BS" + side,
                    frontOfChain=True,
                    weight=[(0, 1), (1, 1), (2, 1)],
                )
            else:
                for i in indices:
                    _detach_outer_from_eye_curvature(upper_lower, i, side)
                cmds.blendShape(
                    tweak, curve, name=prefix + "BS" + side, frontOfChain=True, weight=[(0, 1)]
                )

            _build_controllers(upper_lower, factor, outer_main, out_name, attacher, side, scale)

        if not simpler:
            set_rgb_override_color("{}LidOuter{}Shape".format(upper_lower, side), _GREEN)
            for d in range(1, 5):
                set_rgb_override_color("{}Lid{}Outer{}Shape".format(upper_lower, d, side), _BLUE)
            if upper_lower == "upper":
                set_rgb_override_color("innerLidOuter" + side + "Shape", _GREEN)
                set_rgb_override_color("outerLidOuter" + side + "Shape", _GREEN)


# ---------------------------------------------------------------------------
# 4. fleshy e blink
# ---------------------------------------------------------------------------


def _build_fleshy_curves(side):
    """Curve "fleshy": gli AimEnd dei 4 controller principali skinnano la
    curva Fleshy, cosi' gli angoli muovono la curva in modo ampio
    (MEL:30423-30513)."""
    cmds.createNode("transform", name="LidSetupFleshy" + side, parent="LidSetup")
    cmds.createNode("transform", name="LidFleshyAimAt" + side, parent="LidSetup")
    for corner in _CORNERS:
        lid_joint = corner + "LidJoint" + side
        aimer = cmds.createNode(
            "transform", name=corner + "LidFleshyAimer" + side, parent="LidSetup" + side
        )
        cmds.parent(aimer, "LidSetupFleshy" + side)
        aim_at_offset = cmds.createNode(
            "transform", name=corner + "LidFleshyAimAtOffset" + side, parent=lid_joint
        )
        cmds.parent(aim_at_offset, "LidFleshyAimAt" + side)
        aim_at = cmds.createNode(
            "transform", name=corner + "LidFleshyAimAt" + side, parent=aim_at_offset
        )
        cmds.connectAttr(lid_joint + ".tx", aim_at + ".tx")
        cmds.connectAttr(lid_joint + ".tz", aim_at + ".tz")

        am = _aim_matrix(corner + "LidFleshyAimerAM" + side)
        cmds.connectAttr(aim_at + ".worldMatrix[0]", am + ".primaryTargetMatrix")
        matrix = cmds.xform(aimer, query=True, objectSpace=True, matrix=True)
        cmds.setAttr(am + ".inputMatrix", matrix, type="matrix")
        cmds.xform(
            aimer, objectSpace=True, translation=(0, 0, 0), rotation=(0, 0, 0), scale=(1, 1, 1)
        )
        as_matrix_connect_attr(am + ".outputMatrix", aimer + ".offsetParentMatrix")

        aim_end = cmds.createNode(
            "joint", name=corner + "LidFleshyAimEnd" + side, parent=corner + "Lid" + side
        )
        cmds.parent(aim_end, aimer)
        # la PMA dei controller somma solo le traslazioni: la rotazione qui
        pma_r = cmds.createNode("plusMinusAverage", name=corner + "LidJointPMAr" + side)
        cmds.connectAttr(corner + "Lid" + side + ".r", pma_r + ".input3D[0]")
        cmds.connectAttr("SDK" + corner + "Lid" + side + ".r", pma_r + ".input3D[1]")
        cmds.connectAttr(pma_r + ".output3D", aim_end + ".r")

    inner_end, outer_end = "innerLidFleshyAimEnd" + side, "outerLidFleshyAimEnd" + side
    for upper_lower, _factor in _UPPER_LOWER:
        fleshy = upper_lower + "LidCurveFleshy" + side
        sc = _new_skin_cluster(
            [upper_lower + "LidFleshyAimEnd" + side, inner_end, outer_end],
            fleshy,
            upper_lower + "LidCurveFleshySC" + side,
            max_influences=2,
        )
        for cv, joint, weight in ((6, outer_end, 0.867), (5, outer_end, 0.6), (4, outer_end, 0.2),
                                  (3, inner_end, 0.2), (2, inner_end, 0.6), (1, inner_end, 0.867)):  # fmt: skip
            cmds.skinPercent(sc, "{}.cv[{}]".format(fleshy, cv), transformValue=(joint, weight))

    # gli angoli guidano la curva Fleshy invece della Tweak (effetto piu' ampio)
    for corner in ("inner", "outer"):
        pma_t = corner + "LidJointPMAt" + side
        cmds.disconnectAttr(pma_t + ".output3D", corner + "LidJoint" + side + ".t")
        for axis in "xyz":
            cmds.connectAttr(
                "{}.output3D.output3D{}".format(pma_t, axis),
                "{}LidFleshyAimAt{}.t{}".format(corner, side, axis),
                force=True,
            )


def _build_blink_attrs(upper_lower, factor, side):
    """Attributi blink/blinkCenter/lidOut del controller Lid
    (MEL:30536-30607)."""
    lid = upper_lower + "Lid" + side
    if not cmds.attributeQuery("blink", node=lid, exists=True):
        _add_slider_attr(lid, "blink")
        ensure_output_blend_weighted(lid + ".blink")
    bw_blink = "bw{}_blink.output".format(lid)

    if upper_lower == "upper":
        _add_slider_attr(lid, "blinkCenter", default=2)
        ensure_output_blend_weighted(lid + ".blinkCenter")
        bw_center = "bw{}_blinkCenter.output".format(lid)
        sr = cmds.createNode("setRange", name="upperblinkCenterSR" + side)
        cmds.setAttr(sr + ".oldMax", 10, 10, 10, type="float3")
        cmds.connectAttr(bw_blink, sr + ".valueX")
        pma = cmds.createNode("plusMinusAverage", name="upperblinkCenterPMA" + side)
        cmds.setAttr(pma + ".input1D[0]", 10)
        cmds.setAttr(pma + ".operation", 2)
        cmds.connectAttr(bw_center, pma + ".input1D[1]")
        cmds.connectAttr(pma + ".output1D", sr + ".maxX")
        cmds.connectAttr(bw_center, sr + ".maxY")
    else:
        cmds.connectAttr(bw_blink, "upperblinkCenterSR" + side + ".valueY")

    # anche il ty del controller chiude la palpebra
    temp = cmds.createNode("transform", name="tempTransform", parent="upperLid" + side)
    temp = cmds.parent(temp, "lowerLid" + side)[0]
    ty_to_close = cmds.getAttr(temp + ".ty")
    cmds.delete(temp)
    mpd = cmds.createNode("multiplyDivide", name=upper_lower + "blinkBlendMPD1" + side)
    cmds.setAttr(mpd + ".operation", 2)
    blend_pma = cmds.createNode("plusMinusAverage", name=upper_lower + "blinkBlendPMA" + side)
    # il collegamento diretto del solo ty non valuta in Parallel se ci sono
    # chiavi su tx: si passa da una PMA che legge tutti e tre gli assi
    force_pma = cmds.createNode(
        "plusMinusAverage", name=upper_lower + "blinkBlendForceParallelEvalPMA" + side
    )
    for axis in "xyz":
        cmds.connectAttr(
            "{}.t{}".format(lid, axis), "{}.input3D[0].input3D{}".format(force_pma, axis)
        )
    cmds.connectAttr(force_pma + ".output3D.output3Dy", blend_pma + ".input3D[0].input3Dy")
    cmds.connectAttr("SDK" + lid + ".ty", blend_pma + ".input3D[1].input3Dy")
    cmds.connectAttr(blend_pma + ".output3D.output3Dy", mpd + ".input1Y")
    cmds.setAttr(mpd + ".input2Y", ty_to_close / -10.0 * factor)
    bw = cmds.createNode("blendWeighted", name=upper_lower + "LidBlendWeighted" + side)
    out_value = "outValueX" if upper_lower == "upper" else "outValueY"
    cmds.connectAttr("upperblinkCenterSR{}.{}".format(side, out_value), bw + ".input[0]")
    cmds.connectAttr(mpd + ".outputY", bw + ".input[1]")

    blend = upper_lower + "blinkBlend" + side
    unit_convert_and_reverse(blend, bw + ".output")
    blink_bs = upper_lower + "LidCurveBlinkBS" + side
    cmds.connectAttr(
        blend + "UnitConversion.output", "{}.{}ClosedLidCurve{}".format(blink_bs, upper_lower, side)
    )
    cmds.connectAttr(
        blend + "Reverse.outputX", "{}.{}UnClosedLidCurve{}".format(blink_bs, upper_lower, side)
    )

    lid_out = upper_lower + "lidOutBlend" + side
    if not cmds.attributeQuery("lidOut", node=lid, exists=True):
        _add_slider_attr(lid, "lidOut")
        ensure_output_blend_weighted(lid + ".lidOut")
        unit_convert_and_reverse(lid_out, "bw{}_lidOut.output".format(lid))
    cmds.connectAttr(
        lid_out + "UnitConversion.output", "LidSetup{}.{}LidOut".format(side, upper_lower)
    )
    cmds.delete(lid_out + "Reverse")  # il reverse non serve


def _build_fleshy_eye(corner, out_name, is_main, side, b):
    """Attributo `fleshy`: il controller segue la rotazione dell'occhio
    (MEL:30616-30673, ramo non-OPM)."""
    default = 7.0
    if corner in ("inner", "outer"):
        default = 1.0
    if corner == "lower":
        default = 3.0
    if not is_main:
        default /= 5.0
    base = corner + "Lid" + out_name
    ctrl = base + side
    fleshy = cmds.createNode(
        "transform", name=base + "Fleshy" + side, parent=base + "Offset" + side
    )
    if cmds.objExists(base + "Attach" + side):  # Main, non Outer
        cmds.parent(fleshy, base + "Attach" + side)
    cmds.parent("SDK" + ctrl, fleshy)
    _add_slider_attr(ctrl, "fleshy", default=default)
    mpd = cmds.createNode("multiplyDivide", name=ctrl + "FleshyMPD")
    tx_conv = cmds.createNode("unitConversion", name=ctrl + "FleshyTXConversion")
    ty_conv = cmds.createNode("unitConversion", name=ctrl + "FleshyTYConversion")
    cmds.setAttr(tx_conv + ".conversionFactor", -0.125 * b)
    cmds.setAttr(ty_conv + ".conversionFactor", -0.130)
    cmds.connectAttr("EyeJoint" + side + ".ry", tx_conv + ".input")
    cmds.connectAttr("EyeJoint" + side + ".rx", ty_conv + ".input")
    cmds.connectAttr(tx_conv + ".output", mpd + ".input1X")
    cmds.connectAttr(ty_conv + ".output", mpd + ".input1Y")
    cmds.connectAttr(ctrl + ".fleshy", mpd + ".input2X")
    cmds.connectAttr(ctrl + ".fleshy", mpd + ".input2Y")
    cmds.connectAttr(mpd + ".outputX", fleshy + ".tx")
    cmds.connectAttr(mpd + ".outputY", fleshy + ".ty")
    if is_main:  # guida anche il blink e rientra nella sottrazione
        blend_pma = corner + "blinkBlendPMA" + side
        if cmds.objExists(blend_pma):
            cmds.connectAttr(fleshy + ".ty", blend_pma + ".input3D[2].input3Dy")
        pma_t = corner + "LidJointPMAt" + side
        if cmds.objExists(pma_t):
            cmds.connectAttr(fleshy + ".t", pma_t + ".input3D[3]", force=True)
        cmds.connectAttr(fleshy + ".t", base + "PMA" + side + ".input3D[2]")


def _build_attributes(side, b, simpler):
    for upper_lower, factor in _UPPER_LOWER:
        _build_blink_attrs(upper_lower, factor, side)
    for outer_main, out_name, _attacher in _OUTER_MAIN:  # fleshy su Main e Outer
        if simpler and outer_main == "Outer":
            continue
        for corner in _CORNERS:
            _build_fleshy_eye(corner, out_name, outer_main == "Main", side, b)
    eye_ctrl = "ctrlEye" + side
    for attr in cmds.listAttr(eye_ctrl, keyable=True) or []:
        if not cmds.getAttr("{}.{}".format(eye_ctrl, attr), lock=True):
            ensure_output_blend_weighted("{}.{}".format(eye_ctrl, attr))


# ---------------------------------------------------------------------------
# 6. pesatura
# ---------------------------------------------------------------------------


def _lid_curve_specs(simpler):
    """(side, left, upper_lower, outer_main, num_lid) per ogni fit-curve."""
    specs = []
    for side, left, _b in _SIDES:
        for upper_lower, _factor in _UPPER_LOWER:
            for outer_main, _out_name, _attacher in _OUTER_MAIN:
                if simpler and outer_main == "Outer":
                    continue
                fit_curve = "{}EyeLid{}Curve{}".format(upper_lower, outer_main, left)
                num_lid = cmds.getAttr(fit_curve + ".spans") + 1
                specs.append((side, left, upper_lower, outer_main, num_lid))
    return specs


def _weight_main_loops(geometry, skin_cluster, simpler, cyclops, sampler):
    """Joint per-CV come influenze e peso pieno sul vertice di ogni CV
    (MEL:30689-30800)."""
    specs = [s for s in _lid_curve_specs(simpler) if not (cyclops and s[0] == "_R")]
    influences = []
    for side, _left, upper_lower, outer_main, num_lid in specs:
        for i in range(num_lid):
            if not _skip_lower(upper_lower, i, num_lid):
                influences.append("{}Lid{}{}{}".format(upper_lower, outer_main, i, side))
    cmds.skinCluster(skin_cluster, edit=True, addInfluence=influences, lockWeights=False, weight=0)

    def weight(vtx, joint):
        pos = cmds.xform(vtx, query=True, worldSpace=True, translation=True)
        cmds.setAttr(sampler + ".inPosition", pos[0], pos[1], pos[2], type="float3")
        index = cmds.getAttr(sampler + ".result.closestVertexIndex")
        cmds.skinPercent(
            skin_cluster, "{}.vtx[{}]".format(geometry, index), transformValue=(joint, 1)
        )

    num_lid = 0
    for side, left, upper_lower, outer_main, num_lid in specs:
        vtxs = _fit_vtxs("{}EyeLid{}Curve{}".format(upper_lower, outer_main, left))
        for i, vtx in enumerate(vtxs):
            joint = "{}Lid{}{}{}".format(upper_lower, outer_main, i, side)
            if _skip_lower(upper_lower, i, num_lid) or not cmds.objExists(joint):
                continue
            weight(vtx, joint)
        # Main2: secondo loop Main opzionale, pesato sugli stessi joint
        if outer_main != ("Main" if simpler else "Outer"):
            continue
        if not cmds.objExists(upper_lower + "EyeLidMain2Curve"):
            continue
        for i, vtx in enumerate(_fit_vtxs("{}EyeLidMain2Curve{}".format(upper_lower, left))):
            joint = "{}LidMain{}{}".format(upper_lower, i, side)
            if _skip_lower(upper_lower, i, num_lid) or not cmds.objExists(joint):
                continue
            weight(vtx, joint)


def _hammer_areas(skin_cluster, left):
    has_main2 = cmds.objExists("upperEyeLidMain2Curve")
    # fra Main e Outer
    cmds.select("eyeLidArea" + left)
    cmds.select(_fit_vtxs("FaceFitEyeLidMainCurve" + left), deselect=True)
    if has_main2:
        cmds.select(_fit_vtxs("FaceFitEyeLidMain2Curve" + left), deselect=True)
    weight_hammer_verts_ms(5, skin_cluster)
    # da Outer fin verso il sopracciglio
    cmds.select("eyeLidOuterArea" + left)
    cmds.select(_fit_vtxs("FaceFitEyeLidOuterCurve" + left), deselect=True)
    weight_hammer_verts_ms(5, skin_cluster)


def _weight_rows(geometry, skin_cluster, left, state):
    """Sfumatura per riga di vertici dal loop Main verso Outer (z=0) e peso
    pieno da Main a Inner (z=1), per evitare che upper e lower si
    contaminino (MEL:30825-30905)."""
    outer_vtxs = main_vtxs = inner_vtxs = main2_vtxs = []
    for z in range(2):
        outer_vtxs = _select_fit("FaceFitEyeLidOuterCurve" + left)
        main_vtxs = _select_fit("FaceFitEyeLidMainCurve" + left)
        inner_vtxs = _select_fit("FaceFitEyeLidInnerCurve" + left)
        if cmds.objExists("FaceFitEyeLidMain2"):
            main2_vtxs = _select_fit("FaceFitEyeLidMain2Curve" + left)
        target_vtxs = set(outer_vtxs if z == 0 else inner_vtxs)
        if z == 1 and inner_vtxs and inner_vtxs[0] in main_vtxs:
            break  # stesso edge loop usato per Main e Inner

        # percorrere le righe e' lento sui modelli densi: oltre 500 vertici
        # si lascia fare al weight hammer
        cmds.select("eyeLidArea" + left)
        if len(_selected()) > 500:
            print("// eyeLidArea exceed 500 verticies, using simplified skinning for this area.")
            break

        for main_vtx in main_vtxs:
            cmds.select(main_vtx)
            for _ in range(99):
                _grow_by_edges()
                cmds.select(main_vtxs, deselect=True)
                hit = [v for v in _selected() if v in target_vtxs]
                if hit:
                    _select_least_edges_path(geometry, _vtx_nr(main_vtx), _vtx_nr(hit[0]))
                    cmds.select(cmds.polyListComponentConversion(toVertex=True))
                    cmds.select(main_vtx, deselect=True)
                    if z == 0:  # l'ultima riga, se e' Outer, non va pesata
                        cmds.select(list(target_vtxs), deselect=True)
                    state["row"] = _selected()
                    break
            row = state["row"]
            infs = cmds.skinPercent(
                skin_cluster, main_vtx, query=True, ignoreBelow=0.001, transform=None
            )
            state["weighted"].extend(row)
            if not infs:
                continue
            if z == 1:
                if row:
                    cmds.skinPercent(skin_cluster, row, transformValue=(infs[0], 1))
                continue

            cmds.select(main_vtx)
            previous = []
            for a in range(len(row)):
                _grow_by_edges()
                grown = _selected()
                if previous:
                    cmds.select(previous, deselect=True)
                previous = grown
                value = 1 - (1.0 / (len(row) + 1)) * (a + 1)
                for vtx in _selected():
                    if vtx in row:
                        cmds.skinPercent(skin_cluster, vtx, transformValue=(infs[0], value))

    # weight hammer su quel che resta dell'area interna
    _select_fit("EyeLidInnerAreaMesh" + left)
    rest = state["weighted"] + main_vtxs + main2_vtxs + outer_vtxs + inner_vtxs
    if rest:
        cmds.select(rest, deselect=True)
    weight_hammer_verts_ms(5, skin_cluster)


def _dual_quaternion_lids(geometry, skin_cluster):
    """Dual quaternion solo sull'area delle palpebre (MEL:30920-30932)."""
    cmds.setAttr(skin_cluster + ".skinningMethod", 2)
    num_vtx = cmds.polyEvaluate(geometry, vertex=True)
    for i in range(num_vtx):
        cmds.setAttr("{}.bw[{}]".format(skin_cluster, i), 0)
    cmds.select("eyeLidArea", "eyeLidAreaLeft")
    for vtx in _selected():
        cmds.setAttr("{}.bw[{}]".format(skin_cluster, _vtx_nr(vtx)), 1)


def _build_simpler_cheek_raiser(geometry, skin_cluster, num_grow, sampler):
    """simplerEyeLid: crea un CheekRaiser automatico (lowerLidOuter)
    (MEL:30967-30999)."""
    for side, left, _b in _SIDES:
        cv = (cmds.getAttr("lowerEyeLidOuterCurve.spans") + 1) // 2
        pos = cmds.xform(
            "lowerEyeLidOuterCurve{}.cv[{}]".format(left, cv),
            query=True,
            worldSpace=True,
            translation=True,
        )
        cmds.xform("TempPos", worldSpace=True, translation=pos)
        create_pp("TempPos", "lowerLidOuter", side, 3, True, False, False)
        joint = "lowerLidOuterJoint" + side
        cmds.skinCluster(
            skin_cluster, edit=True, dropoffRate=4, lockWeights=False, weight=0, addInfluence=joint
        )
        cmds.setAttr(sampler + ".inPosition", pos[0], pos[1], pos[2], type="float3")
        vtx = "{}.vtx[{}]".format(geometry, cmds.getAttr(sampler + ".result.closestVertexIndex"))
        cmds.skinPercent(skin_cluster, vtx, transformValue=(joint, 1))
        cmds.select(vtx)
        for _ in range(num_grow):
            _grow()
        cmds.select("eyeLidArea" + left, vtx, deselect=True)
        weight_hammer_verts_ms(5, skin_cluster)
        cmds.select(vtx)
        weight_hammer_verts_ms(5, skin_cluster)
        cmds.skinPercent(skin_cluster, vtx, transformValue=(joint, 0.5))


# ---------------------------------------------------------------------------
# entry point
# ---------------------------------------------------------------------------

_REQUIRED = (
    FIT_SKELETON,
    "FaceDeformationSystem",
    "FaceJoint_M",
    "FaceBuildInProgress",
    "FaceBuildInProgressHidden",
    "FaceControlOrient",
    "FaceAreas",
    "OnFacecontrols",
    "Eye_R",
    "Eye_L",
    "EyeRegion_R",
    "EyeRegion_L",
    "ctrlEye_R",
    "ctrlEye_L",
)
_REQUIRED_FIT = ("FaceFitEyeLidOuterCurve", "FaceFitEyeLidMainCurve", "FaceFitEyeLidInnerCurve")


def _build_eye_sockets(skin_cluster):
    """Opzione EyeSocket (MEL:29972-30016): per lato, il set
    `eyeSocketArea` (tutto cio' che sta dentro il loop Inner della palpebra)
    e il controller `EyeSocket` col suo joint, a cui l'area e' pesata per
    intero."""
    for side, left, _b in _SIDES:
        inner = _select_fit("FaceFitEyeLidInnerCurve" + left)
        if not inner:
            cmds.warning("face_eye_lid: no inner lid loop for the EyeSocket of side " + side)
            continue
        lid_area = set(cmds.ls(cmds.sets("eyeLidArea" + left, query=True), flatten=True))
        cmds.select(inner[0])
        _grow()
        for vtx in _selected():
            if vtx in lid_area:
                continue
            # primo vertice oltre il loop: da li' si allarga a tutto l'interno
            cmds.select(vtx)
            for _ in range(99):
                _grow()
                cmds.select("eyeLidArea" + left, deselect=True)
            break
        cmds.sets(name="eyeSocketArea" + left)
        cmds.sets("eyeSocketArea" + left, add="FaceAreas")

        ctrl, joint, offset = "EyeSocket" + side, "EyeSocketJoint" + side, "EyeSocketOffset" + side
        create_face_controller("EyeSocket", side, 4)
        cmds.parent(joint, "FaceDeformationSystem")
        as_parent_constraint(ctrl, joint, force_mult_matrix=True)
        pos = cmds.xform("Eye" + side, query=True, worldSpace=True, translation=True)
        cmds.xform(offset, worldSpace=True, translation=pos)
        cmds.scale(5, 5, 5, ctrl + ".cv[0:7]", relative=True, pivot=pos)
        cmds.parent(offset, "EyeRegion" + side)
        cmds.xform(offset, objectSpace=True, rotation=(0, 0, 0), scale=(1, 1, 1))
        as_opm_scale_reset(joint)
        place_ctrl_by_projection(ctrl)

        cmds.skinCluster(
            skin_cluster, edit=True, dropoffRate=4, lockWeights=False, weight=0, addInfluence=joint
        )
        members = cmds.sets("eyeSocketArea" + left, query=True) or []
        if members:
            cmds.skinPercent(skin_cluster, members, transformValue=(joint, 1))
        cmds.select(clear=True)


def _warn_unsupported():
    for option, what in (
        ("MultiSkinClusters", "multiSkinClusters"),
        ("Eyelash", "eyelash attachment"),
    ):
        if get_fit_option(option):
            cmds.warning("face_eye_lid: {} is not ported yet, skipping it".format(what))
    if cmds.attributeQuery("nonSphericalEye", node="FitEyeBall", exists=True):
        cmds.warning("face_eye_lid: non-spherical eye lid-out setup is not ported yet")


def face_eye_lid() -> bool:
    """Costruisce le palpebre (asFaceEyeLid).

    Presuppone Prep, CtrlBox ed EyeBall eseguiti e il fitting delle palpebre
    completo (loop Outer, Main, Inner, anche Left). Ritorna False con
    warning se manca un prerequisito; nessuna eccezione per oggetti assenti.
    """
    required = list(_REQUIRED) + [f + left for f in _REQUIRED_FIT for left in ("", "Left")]
    for upper_lower in ("upper", "lower"):
        required.append(upper_lower + "EyeLidMainCurve")
    missing = [node for node in required if not cmds.objExists(node)]
    if missing:
        cmds.warning("face_eye_lid: missing {}".format(", ".join(missing)))
        return False
    geometry = get_fit_option("Face") or ""
    skin_cluster = get_fit_option("SkinCluster") or ""
    if not cmds.objExists(geometry) or not cmds.objExists(skin_cluster):
        cmds.warning("face_eye_lid: face geometry or skinCluster not found")
        return False

    simpler = bool(get_fit_option("SimplerEyeLid"))
    cyclops = bool(get_fit_option("Cyclops"))
    non_symmetrical = bool(get_fit_option("NonSym"))
    scale = cmds.getAttr(FIT_SKELETON + ".faceScale")
    _warn_unsupported()

    _build_base(skin_cluster)
    if not cyclops:
        _build_lid_control_orient(scale)
    _build_lid_area_sets()
    if get_fit_option("EyeSocket"):
        _build_eye_sockets(skin_cluster)
    num_grow = _build_lid_outer_area_sets(geometry)

    npc = cmds.createNode("nearestPointOnCurve", name="tempNearestPointOnCurve")
    for side, left, _b in _SIDES:
        _build_side_lids(side, left, scale, simpler, non_symmetrical, npc)
    for side, _left, _b in _SIDES:
        _build_fleshy_curves(side)
    for side, _left, _b in _SIDES:
        for upper_lower, _factor in _UPPER_LOWER:
            cmds.blendShape(
                upper_lower + "UnClosedLidCurve" + side,
                upper_lower + "ClosedLidCurve" + side,
                upper_lower + "LidCurveBlink" + side,
                name=upper_lower + "LidCurveBlinkBS" + side,
                frontOfChain=True,
                weight=[(0, 1.0), (1, 0.0)],
            )
    for side, _left, b in _SIDES:
        _build_attributes(side, b, simpler)

    # un modello asimmetrico puo' far "scappare" eyeLidAreaLeft
    count = len(cmds.ls(cmds.sets("eyeLidArea", query=True), flatten=True))
    count_left = len(cmds.ls(cmds.sets("eyeLidAreaLeft", query=True), flatten=True))
    if count != count_left:
        cmds.warning(
            "eyeLidArea has {} verts, but eyeLidAreaLeft has {} verts, probably model is "
            "asymmetrical.".format(count, count_left)
        )

    if cmds.objExists("closestSampler"):
        cmds.delete("closestSampler")
    sampler = cmds.createNode("closestPointOnMesh", name="closestSampler")
    cmds.connectAttr(geometry + ".outMesh", sampler + ".inMesh", force=True)
    _weight_main_loops(geometry, skin_cluster, simpler, cyclops, sampler)
    for _side, left, _b in _SIDES:
        _hammer_areas(skin_cluster, left)
    state = {"row": [], "weighted": []}  # $rowVtxs / $rowWeightedVtxs: mai azzerati nel MEL
    for _side, left, _b in _SIDES:
        _weight_rows(geometry, skin_cluster, left, state)
    cmds.select(clear=True)
    cmds.delete("FaceBuildEyeLidCurves")

    if not get_fit_option("GameEngine"):
        _dual_quaternion_lids(geometry, skin_cluster)

    cmds.select(clear=True)
    for _side, left, _b in _SIDES:
        cmds.select(_fit_vtxs("FaceFitEyeLidMainCurve" + left), add=True)
        if cmds.objExists("upperEyeLidMain2Curve"):
            cmds.select(_fit_vtxs("FaceFitEyeLidMain2Curve" + left), add=True)
    cmds.sets(name="eyeLidMainArea")
    cmds.sets("eyeLidMainArea", add="FaceAreas")

    if simpler:
        _build_simpler_cheek_raiser(geometry, skin_cluster, num_grow, sampler)

    for node in ("closestSampler", "TempPos", "tempNearestPointOnCurve"):
        if cmds.objExists(node):
            cmds.delete(node)
    if not cyclops:  # ripristina il FaceControlOrient generale
        cmds.setAttr("FaceControlOrient.v", 0)
        cmds.rename("FaceControlOrient", "FaceControlOrientEye")
        cmds.rename("FaceControlSuspended", "FaceControlOrient")
    else:
        for child in cmds.listRelatives("SideReverse_R", children=True, type="transform") or []:
            if "Lid" in child and child.endswith("_R"):
                cmds.setAttr(child + ".overrideEnabled", 1)
                cmds.setAttr(child + ".overrideVisibility", 0)

    cmds.select(clear=True)
    return True

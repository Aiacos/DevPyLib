"""Build delle labbra (parita' asFaceLip, MEL:31132-32566).

La procedura piu' grande del build. Le sezioni seguono l'ordine del MEL e
vivono in funzioni `_s<N>_*` che condividono un contesto `_Ctx` (le
variabili locali del MEL che attraversano le sezioni).

Divergenze: vedi docs/gap-analysis.md §5i.
"""

import maya.cmds as cmds

from .build_utils import as_face_hide_controllers, as_parent_constraint
from .ctrl_box import create_face_controller
from .driving_system import ensure_output_blend_weighted
from .face_eye_wide import face_eye_wide_finish
from .fit_options import FIT_SKELETON, get_fit_option
from .fitting import get_face_fit_selection

_SIDES = (("_R", "", 1), ("_L", "Left", -1))
_UPPER_LOWER = (("upper", 1), ("lower", -1))


class _Ctx:
    """Variabili del MEL condivise fra le sezioni."""

    def __init__(self):
        self.geometry = get_fit_option("Face") or ""
        self.skin_cluster = get_fit_option("SkinCluster") or ""
        self.head_joint = get_fit_option("HeadJoint") or ""
        self.non_overridden_head_joint = self.head_joint
        self.non_symmetrical = bool(get_fit_option("NonSym"))
        self.long_snout = bool(get_fit_option("LongSnout"))
        self.scale = cmds.getAttr(FIT_SKELETON + ".faceScale")
        self.ctrl_scale = cmds.getAttr("OnFacecontrols.sx")
        self.lip_ctrls = 12
        self.end = 3
        self.ribbon_spans_u = 5
        option = get_fit_option("LipCtrls")
        if option:
            self.lip_ctrls = int(option)
            self.end = self.lip_ctrls // 4
            self.ribbon_spans_u = (self.lip_ctrls // 2) - 1
        self.main_num_cv = 0
        self.lip_area = []
        self.right_cnr_vtxs = []
        self.left_cnr_vtxs = []


def _ws(node):
    return cmds.xform(node, query=True, worldSpace=True, translation=True)


def _selected():
    return cmds.ls(selection=True, flatten=True) or []


def _grow_by_edges():
    """ConvertSelectionToEdges + ConvertSelectionToVertices."""
    cmds.select(cmds.polyListComponentConversion(toEdge=True))
    cmds.select(cmds.polyListComponentConversion(toVertex=True))


def _add_lips_attr(attr):
    """addAttr -k 1 -at double -smx 10 -hsx 1 -smn -10 -hnv 1 su ctrlLips_M."""
    cmds.addAttr(
        "ctrlLips_M",
        longName=attr,
        keyable=True,
        attributeType="double",
        softMaxValue=10,
        hasSoftMaxValue=True,
        softMinValue=-10,
        hasMinValue=True,
    )
    ensure_output_blend_weighted("ctrlLips_M." + attr)


# ---------------------------------------------------------------------------
# 1. base, LipRegion, curve di build e joint per-CV (MEL:31181-31385)
# ---------------------------------------------------------------------------


def _s1_base(ctx):
    cmds.select(get_face_fit_selection("LipInnerAreaMesh").split())
    ctx.lip_area = _selected()
    cmds.createNode("objectSet", name="lipArea")
    cmds.sets("lipArea", add="FaceAreas")
    cmds.sets(ctx.lip_area, add="lipArea")

    cmds.createNode("transform", name="LipSetup")
    cmds.parent("LipSetup", "FaceDeformationSystem")
    for child in (
        "LipRibbon",
        "LipFollicles",
        "LipRibbonJoints",
        "LipRibbonLocs",
        "LipRibbonFleshy",
        "LipRibbonFleshyJoints",
        "LipSlider",
    ):
        cmds.createNode("transform", name=child, parent="LipSetup")
    cmds.createNode("transform", name="LipFollowHead", parent="LipSetup")
    as_parent_constraint(ctx.non_overridden_head_joint, "LipFollowHead", force_mult_matrix=True)
    cmds.createNode("transform", name="LipFollowHeadConstrained")
    cmds.parent("LipRibbonJoints", "LipFollicles", "LipFollowHeadConstrained", "LipFollowHead")

    if cmds.objExists("closestSampler"):
        cmds.delete("closestSampler")
    cmds.createNode("closestPointOnMesh", name="closestSampler")
    cmds.connectAttr(ctx.geometry + ".outMesh", "closestSampler.inMesh")
    cmds.createNode("closestPointOnSurface", name="closestNurbsSampler")
    cmds.createNode("transform", name="LipConstruction")

    cmds.select("FaceJoint_M")
    cmds.joint(name="LipJoints_M")
    cmds.setAttr("LipJoints_M.segmentScaleCompensate", 0)
    cmds.setAttr("LipJoints_M.drawStyle", 2)
    pos, pos_a = _ws("upperLipOuterCurve.cv[0]"), _ws("lowerLipOuterCurve.cv[0]")
    cmds.xform(
        "LipJoints_M",
        worldSpace=True,
        translation=(0, (pos[1] + pos_a[1]) / 2.0, max(pos[2], pos_a[2])),
    )

    for kind in ("Press", "Squeeze", "Roll", "Pucker"):
        for upper_lower, _factor in _UPPER_LOWER:
            _add_lips_attr(upper_lower + kind)


def _s1_lip_region(ctx):
    """Controller di regione delle labbra, sagomato sui loop Outer."""
    pos_a, pos_b = _ws("upperLipMainCurve.cv[0]"), _ws("lowerLipMainCurve.cv[0]")
    pos = (0, (pos_a[1] + pos_b[1]) / 2.0, (pos_a[2] + pos_b[2]) / 2.0)

    create_face_controller("LipRegion", "_M", 4)
    cmds.delete("LipRegionJoint_M")
    cmds.parent("LipRegionOffset_M", "SideReverse_M")
    cmds.setAttr("LipRegionOffset_M.s", 1, 1, 1, type="float3")
    cmds.scale(6, 6, 6, "LipRegion_M.cv[0:7]", relative=True, pivot=(0, 0, 0))
    cmds.xform("LipRegionOffset_M", worldSpace=True, translation=pos)
    cmds.move(0, 0, ctx.scale / 25.0, "LipRegion_M.cv[0:99]", relative=True)

    def cv(index):
        return "LipRegion_MShape.cv[{}]".format(index)

    def set_cv(index, x, y, z):
        cmds.xform(cv(index), worldSpace=True, translation=(x, y, z))

    pos_b = _ws("upperLipOuterCurve.cv[0]")
    pos_a = _ws(cv(1))
    set_cv(1, pos_a[0], pos_b[1], pos_a[2])
    pos_a = _ws(cv(2))
    set_cv(2, pos_a[0], pos_b[1], pos_a[2])
    set_cv(0, pos_a[0] * -1, pos_b[1], pos_a[2])

    pos_b = _ws("lowerLipOuterCurve.cv[0]")
    pos_a = _ws(cv(5))
    set_cv(5, pos_a[0], pos_b[1], pos_a[2])
    pos_a = _ws(cv(4))
    set_cv(4, pos_a[0], pos_b[1], pos_a[2])
    set_cv(6, pos_a[0] * -1, pos_b[1], pos_a[2])

    pos_a, pos_b = _ws(cv(3)), _ws("upperLipOuterCurve.cv[99]")
    set_cv(3, pos_b[0] * 1.2, pos_b[1], pos_a[2])
    pos_a, pos_b = _ws(cv(7)), _ws("upperLipOuterCurveLeft.cv[99]")
    set_cv(7, pos_b[0] * 1.2, pos_b[1], pos_a[2])


def _build_curve(upper_lower, in_out_main, left):
    """Curva lineare che percorre in ordine i vertici del loop fittato
    (MEL:31288-31319)."""
    text = get_face_fit_selection("{}Lip{}Curve{}".format(upper_lower, in_out_main, left))
    cmds.select(text.split())
    loop_vtxs = _selected()
    loop_set = set(loop_vtxs)
    completed = []
    points = []
    cmds.select(text.split()[0])
    for _ in range(len(loop_vtxs)):
        current = _selected()
        if not current:
            continue
        completed.extend(current)
        points.append(_ws(current[0]))
        _grow_by_edges()
        outside = [v for v in _selected() if v not in loop_set]
        if outside:
            cmds.select(outside, deselect=True)
        cmds.select(completed, deselect=True)
    name = "{}Lip{}BuildCurve{}".format(upper_lower, in_out_main, left)
    curve = cmds.rename(cmds.curve(degree=1, point=points), name)
    cmds.parent(curve, "LipConstruction")
    return curve


def _s1_build_curves_and_joints(ctx):
    cmds.createNode("transform", name="asTempNodes")
    path = cmds.createNode("motionPath", name="asTempMotionPath")
    temp = cmds.createNode("transform", name="asTempTransform")
    cmds.connectAttr(path + ".allCoordinates", temp + ".translate", force=True)
    cmds.connectAttr(path + ".r", temp + ".r", force=True)
    for attr, value in (("fractionMode", 0), ("worldUpType", 0), ("frontAxis", 0),
                        ("upAxis", 1), ("inverseFront", 1)):  # fmt: skip
        cmds.setAttr("{}.{}".format(path, attr), value)

    for side, left, _b in _SIDES:
        if side == "_L":
            cmds.setAttr(path + ".inverseFront", 0)
        for upper_lower, _factor in _UPPER_LOWER:
            for in_out_main in ("Inner", "Outer", "Main"):
                _build_curve(upper_lower, in_out_main, left)
            main_build = "{}LipMainBuildCurve{}".format(upper_lower, left)
            ctx.main_num_cv = cmds.getAttr(main_build + ".spans") + 1

            for i in range(ctx.main_num_cv):
                cmds.select("LipJoints_M")
                joint = cmds.joint(name="{}LipJoint{}{}".format(upper_lower, i, side))
                cmds.setAttr(joint + ".segmentScaleCompensate", 0)
                cmds.setAttr(joint + ".radius", 0.1)
                cmds.xform(
                    joint, worldSpace=True, translation=_ws("{}.cv[{}]".format(main_build, i))
                )
            # asse Y orientato alla topologia, per il roll localizzato
            rebuilt = "{}LipMainReBuiltCurve{}".format(upper_lower, left)
            cmds.duplicate("{}LipMainCurve{}".format(upper_lower, left), name=rebuilt)
            cmds.rebuildCurve(
                rebuilt,
                constructionHistory=0,
                replaceOriginal=1,
                rebuildType=0,
                endKnots=1,
                keepRange=1,
                keepControlPoints=1,
                keepEndPoints=1,
                keepTangents=0,
                spans=0,
                degree=3,
                tolerance=0.01,
            )
            cmds.parent(rebuilt, "asTempNodes")
            cmds.connectAttr(rebuilt + ".worldSpace[0]", path + ".geometryPath", force=True)
            for i in range(ctx.main_num_cv):
                u_value = i if i in (0, ctx.main_num_cv - 1) else i - 1
                cmds.setAttr(path + ".uValue", u_value)
                if i > 0:
                    cmds.setAttr(
                        "{}LipJoint{}{}.ry".format(upper_lower, i, side),
                        cmds.getAttr(temp + ".ry"),
                    )
    cmds.delete(path, temp, "asTempNodes")

    for upper_lower, _factor in _UPPER_LOWER:
        cmds.rename(upper_lower + "LipJoint0_R", upper_lower + "LipJoint0_M")
        cmds.delete(upper_lower + "LipJoint0_L")
    # primo e ultimo joint lower coincidono con quelli upper
    last = ctx.main_num_cv - 1
    cmds.delete("lowerLipJoint{}_R".format(last), "lowerLipJoint{}_L".format(last))


# ---------------------------------------------------------------------------
# 2. lipSlideSurface, curve e superfici del ribbon (MEL:31387-31592)
# ---------------------------------------------------------------------------


def _slide_cv(u, v):
    return "lipSlideSurface.cv[{}][{}]".format(u, v)


def _skin(joints, geometry, name, max_influences=3):
    """newSkinCluster "-toSelectedBones -mi N -dr 4 -rui false" + rename."""
    sc = cmds.skinCluster(
        joints,
        geometry,
        toSelectedBones=True,
        maximumInfluences=max_influences,
        dropoffRate=4,
        removeUnusedInfluence=False,
    )[0]
    return cmds.rename(sc, name)


def _s2_slide_surface(ctx):
    """Superficie che avvolge la bocca: non vincola piu' nulla, serve da
    FaceControlOrient per allineare i controller delle labbra."""
    jaw_pivot = _ws("JawPivot")
    pos_a, pos_b = _ws("FitEyeBall"), _ws("upperEyeLidMainCurve.cv[99]")
    eye_cnr = [(pos_a[i] + pos_b[i]) / 2.0 for i in range(3)]
    mid_lip = _ws("upperLipMainCurve.cv[0]")
    nose_under = _ws("NoseUnder")
    all_cvs = "lipSlideSurface.cv[0:99][0:99]"

    cmds.nurbsPlane(
        name="lipSlideSurface",
        pivot=(0, 0, 0),
        axis=(0, 0, 1),
        width=1,
        lengthRatio=1,
        degree=3,
        patchesU=2,
        patchesV=4,
        constructionHistory=False,
    )
    cmds.rotate(0, 0, -90, all_cvs, relative=True, pivot=(0, 0, 0), objectSpace=True)
    s = (nose_under[1] - mid_lip[1]) * 2
    cmds.scale(s, s, s, all_cvs, relative=True)
    cmds.move(mid_lip[0], mid_lip[1], mid_lip[2], all_cvs, relative=True)

    # allunga la riga 0 fino all'angolo dell'occhio (e in parte la 1)
    pos = _ws(_slide_cv(0, 0))
    s = (eye_cnr[1] - mid_lip[1]) / (pos[1] - mid_lip[1])
    cmds.scale(1, s, 1, "lipSlideSurface.cv[0:4][0]", relative=True, pivot=mid_lip)
    cmds.scale(1, s * 0.85, 1, "lipSlideSurface.cv[0:4][1]", relative=True, pivot=mid_lip)
    cmds.xform(_slide_cv(0, 0), worldSpace=True, translation=eye_cnr)
    for u in range(1, 5):
        pos = _ws(_slide_cv(u, 0))
        cmds.xform(_slide_cv(u, 0), worldSpace=True, translation=(eye_cnr[0], pos[1], eye_cnr[2]))

    # tira cv[2][0] verso il JawPivot, e in parte i vicini
    pos_a = _ws(_slide_cv(2, 0))
    pos = [(jaw_pivot[0] + pos_a[0]) / 2.0, mid_lip[1], (jaw_pivot[2] + pos_a[2]) / 2.0]
    cmds.xform(_slide_cv(2, 0), worldSpace=True, translation=pos)
    for u in (1, 3):
        near = _ws(_slide_cv(u, 0))
        cmds.xform(
            _slide_cv(u, 0),
            worldSpace=True,
            translation=((pos[0] + near[0]) / 2.0, near[1], (pos[2] + near[2]) / 2.0),
        )

    # le righe 2 e 1 passano per il 25% e il 75% della curva del labbro
    path = cmds.createNode("motionPath", name="asTempMotionPath")
    temp = cmds.createNode("transform", name="asTempTransform")
    cmds.connectAttr("upperLipMainBuildCurve.worldSpace[0]", path + ".geometryPath", force=True)
    cmds.connectAttr(path + ".allCoordinates", temp + ".translate", force=True)
    cmds.setAttr(path + ".fractionMode", 1)
    for u_value, row in ((0.25, 2), (0.75, 1)):
        cmds.setAttr(path + ".uValue", u_value)
        pos_a = _ws(temp)
        for u in range(5):
            pos = _ws(_slide_cv(u, row))
            cmds.xform(_slide_cv(u, row), worldSpace=True, translation=(pos_a[0], pos[1], pos_a[2]))
    cmds.delete(temp, path)

    # il lato sinistro specchia il destro
    for u in range(5):
        for v in range(3):
            pos = _ws(_slide_cv(u, v))
            cmds.xform(
                _slide_cv(u, 6 - v), worldSpace=True, translation=(pos[0] * -1, pos[1], pos[2])
            )

    # allarga le righe 1 e 5 finche' la superficie raggiunge l'angolo della bocca
    temp = cmds.createNode("transform", name="asTempTransform")
    pos_a = _ws("upperLipMainCurve.cv[99]")
    cmds.xform(temp, worldSpace=True, translation=pos_a)
    rows = [_slide_cv(u, v) for u in range(5) for v in (1, 5)]
    prev_dist = 99.0
    reached = False
    for _ in range(99):
        constraint = cmds.geometryConstraint("lipSlideSurface", temp)
        pos_b = _ws(temp)
        dist = sum((pos_a[i] - pos_b[i]) ** 2 for i in range(3)) ** 0.5
        if dist > prev_dist:
            reached = True
            break
        prev_dist = dist
        cmds.delete(constraint)
        cmds.xform(temp, worldSpace=True, translation=pos_a)
        cmds.scale(1.05, 1, 1, rows, relative=True, pivot=(0, 0, 0))
    if not reached:  # fallito: annulla (1.05^99 = 130.477, 1/x = 0.00766)
        cmds.scale(0.00766, 1, 1, rows, relative=True, pivot=(0, 0, 0))

    # potrebbe aver superato la riga finale
    pos_a, pos_b = _ws(_slide_cv(2, 1)), _ws(_slide_cv(2, 0))
    if pos_a[0] < pos_b[0]:
        cmds.scale(
            (pos_a[0] / pos_b[0]) * 1.2,
            1,
            1,
            "lipSlideSurface.cv[0:4][0]",
            "lipSlideSurface.cv[0:4][6]",
            relative=True,
            pivot=(0, 0, 0),
        )
    cmds.delete(temp)

    cmds.parent("lipSlideSurface", "LipSlider")
    _skin(["FaceJoint_M"], "lipSlideSurface", "lipSlideSurfaceSC")
    cmds.setAttr("lipSlideSurface.v", 0)

    # FaceControlOrient dedicato alle labbra
    cmds.rename("FaceControlOrient", "FaceControlSuspended")
    cmds.duplicate("lipSlideSurface", name="FaceControlOrient")
    cmds.sets("FaceControlOrient", edit=True, forceElement="asRedSG")
    cmds.parent("FaceControlOrient", "FaceBuildInProgressHidden")


def _rebuild(curve, **overrides):
    flags = dict(
        constructionHistory=0,
        replaceOriginal=1,
        rebuildType=0,
        endKnots=1,
        keepRange=0,
        keepControlPoints=0,
        keepEndPoints=1,
        keepTangents=0,
        spans=0,
        degree=3,
        tolerance=0.01,
    )
    flags.update(overrides)
    return cmds.rebuildCurve(curve, **flags)


def _s2_ribbon_curves(ctx):
    """Curva che passa per i joint del labbro, da sinistra a destra, e la
    sua gemella "Shaped" con la forma reale della bocca."""
    upper_last = cmds.getAttr("upperLipMainBuildCurve.spans")
    for upper_lower, _factor in _UPPER_LOWER:
        ctx.main_num_cv = cmds.getAttr(upper_lower + "LipMainBuildCurve.spans") + 1
        points = []
        joint_nr = ctx.main_num_cv - 1
        joint_side = "_L"
        for i in range(ctx.main_num_cv * 2 - 1):
            if joint_nr == 0:
                joint_side = "_M"
            joint = "{}LipJoint{}{}".format(upper_lower, joint_nr, joint_side)
            if joint_nr == 0:
                joint_side = "_R"
            if not cmds.objExists(joint):  # il lower non ha primo/ultimo: usa l'upper
                joint = "upperLipJoint{}{}".format(upper_last, joint_side)
            if not cmds.objExists(joint):
                raise RuntimeError(
                    "Joint: {} not found. This probably means the model is not symmetrical.".format(
                        joint
                    )
                )
            points.append(_ws(joint))
            joint_nr += -1 if i < ctx.main_num_cv - 1 else 1
        ribbon_curve = upper_lower + "LipRibbonCurve"
        cmds.curve(name=ribbon_curve, degree=3, point=points)
        cmds.rename(cmds.listRelatives(ribbon_curve, shapes=True)[0], ribbon_curve + "Shape")
        cmds.reverseCurve(ribbon_curve, constructionHistory=False, replaceOriginal=True)

        joints = cmds.ls(upper_lower + "LipJoint*_*")
        if upper_lower == "lower":
            joints += ["upperLipJoint{}{}".format(upper_last, side) for side in ("_R", "_L")]
        _skin(joints, ribbon_curve, ribbon_curve + "SC")

        build = upper_lower + "LipMainBuildCurve"
        shaped = upper_lower + "LipRibbonCurveShaped"
        cmds.duplicate(build, name=build + "Shaped")
        cmds.duplicate(build + "Left", name=build + "ShapedLeft")
        cmds.attachCurve(
            build + "Shaped",
            build + "ShapedLeft",
            constructionHistory=False,
            replaceOriginal=True,
            keepMultipleKnots=True,
            method=0,
            blendBias=0.5,
            blendKnotInsertion=False,
            parameter=0.1,
        )
        cmds.rename(build + "Shaped", shaped)
        cmds.delete(build + "ShapedLeft")
        cmds.parent(shaped, world=True)
        _rebuild(shaped, keepControlPoints=1)
        _rebuild(shaped, constructionHistory=1, replaceOriginal=0, keepEndPoints=0)


def _s2_ribbon_surfaces(ctx):
    """Superfici NURBS (ribbon) upper e lower su cui scorrono i follicoli."""
    pos_a, pos_b = _ws("upperLipMainCurve.cv[0]"), _ws("upperLipMainCurve.cv[99]")
    profile = "tempLoftProfile"
    points = [(pos_b[0], pos_a[1], pos_b[2]), (0, pos_a[1], pos_a[2])]
    points.append((pos_b[0] * -1, pos_a[1], pos_b[2]))
    cmds.curve(name=profile, degree=1, point=points, knot=[0, 1, 2])
    _rebuild(profile, spans=5)
    dist = pos_a[2] - pos_b[2]
    pivot = (0, pos_b[1], pos_b[2])
    inner = [profile + ".cv[1]", profile + ".cv[6]"]
    outer = [profile + ".cv[2]", profile + ".cv[5]"]
    cmds.scale(1.06, 1, 1.06, inner, relative=True, pivot=pivot)
    cmds.scale(1.2, 1, 1.2, outer, relative=True, pivot=pivot)
    cmds.move(0, 0, dist / 20.0, inner, relative=True, objectSpace=True, worldSpaceDistance=True)
    cmds.move(0, 0, dist / 4.0, outer, relative=True, objectSpace=True, worldSpaceDistance=True)
    cmds.extrude(
        profile,
        name="upperLipRibbon",
        constructionHistory=False,
        range=False,
        polygon=0,
        extrudeType=0,
        useProfileNormal=False,
        direction=(0, 1, 0),
        length=ctx.scale / 200.0,
        rotation=0,
        scale=1,
        degreeAlongLength=3,
    )
    cmds.delete(profile)

    # orienta il ribbon per le bocche "inclinate" (es. rana che sorride)
    cmds.select("upperLipRibbon")
    cluster, handle = cmds.cluster(envelope=1)
    cmds.rename(cluster, "anglerCluster")
    handle = cmds.rename(handle, "anglerClusterHandle")
    cmds.xform(handle, pivots=(0, pos_a[1], pos_a[2]))
    target = cmds.createNode("transform", name="tempXform")
    cmds.xform(target, pivots=(0, pos_b[1], pos_b[2]))
    cmds.delete(
        cmds.aimConstraint(
            target,
            handle,
            offset=(0, 0, 0),
            weight=1,
            aimVector=(0, 0, -1),
            upVector=(1, 0, 0),
            worldUpType="vector",
            worldUpVector=(1, 0, 0),
        )
    )
    cmds.delete(target)
    pos_c = _ws("upperLipRibbon.cv[0][0]")
    cmds.setAttr(handle + ".sz", (pos_a[2] - pos_b[2]) / (pos_a[2] - pos_c[2]))
    cmds.delete("upperLipRibbon", constructionHistory=True)

    if ctx.lip_ctrls != 12:
        cmds.rebuildSurface(
            "upperLipRibbon",
            constructionHistory=0,
            replaceOriginal=1,
            rebuildType=0,
            endKnots=1,
            keepRange=0,
            keepControlPoints=0,
            keepCorners=0,
            spansU=ctx.ribbon_spans_u,
            degreeU=3,
            spansV=0,
            degreeV=1,
            tolerance=0.01,
            fitRebuild=0,
            direction=2,
        )
    cmds.duplicate("upperLipRibbon", name="lowerLipRibbon")
    cmds.move(
        0,
        ctx.scale / -200.0,
        0,
        "lowerLipRibbon.cv[0:99][0:99]",
        relative=True,
        objectSpace=True,
        worldSpaceDistance=True,
    )
    cmds.xform("LipFollicles", worldSpace=True, translation=_ws("LipJoints_M"))
    cmds.createNode("closestPointOnSurface", name="tempClosestPointOnSurface")

    for side, _left, _b in _SIDES:
        holder = cmds.createNode("transform", name="PlaceHolderStickyLip" + side)
        cmds.addAttr(
            holder,
            keyable=True,
            longName="sticky",
            attributeType="double",
            minValue=0,
            maxValue=10,
            defaultValue=0,
        )


# ---------------------------------------------------------------------------
# 3. follicoli, sticky, bind e pesi dei joint per-CV (MEL:31594-31830)
# ---------------------------------------------------------------------------


def _lip_joint_ids(upper_lower, main_num_cv):
    """(i, side, b) dei joint per-CV nell'ordine del MEL: _M per i==0 (solo
    nel giro destro), il lower senza l'ultimo (coincide con l'upper)."""
    ids = []
    for b in (1, -1):
        for i in range(main_num_cv):
            if i == 0 and b == -1:
                continue
            if upper_lower == "lower" and i == main_num_cv - 1:
                continue
            side = "_M" if i == 0 else ("_R" if b == 1 else "_L")
            ids.append((i, side, b))
    return ids


def _s3_follicles(ctx):
    """Ogni joint del labbro segue un follicolo del ribbon; l'offset fra
    follicolo e joint e' sommato da una PMA. Con lo sticky il blendColors
    porta il joint sulla posizione del labbro opposto."""
    from .build_utils import as_create_mult_dl

    sampler = "tempClosestPointOnSurface"
    for upper_lower, _factor in _UPPER_LOWER:
        ctx.main_num_cv = cmds.getAttr(upper_lower + "LipMainBuildCurve.spans") + 1
        ribbon = upper_lower + "LipRibbon"
        cmds.connectAttr(ribbon + "Shape.worldSpace[0]", sampler + ".inputSurface", force=True)
        for i, side, _b in _lip_joint_ids(upper_lower, ctx.main_num_cv):
            tag = "{}{}".format(i, side)
            joint = "{}LipJoint{}".format(upper_lower, tag)
            shape = cmds.createNode("follicle")
            follicle = cmds.rename(
                cmds.listRelatives(shape, parent=True)[0], "{}follicle{}".format(upper_lower, tag)
            )
            cmds.parent(follicle, "LipFollicles")
            cmds.setAttr(follicle + ".collide", 0)
            cmds.connectAttr(ribbon + ".local", follicle + ".inputSurface")
            cmds.connectAttr(
                "LipFollicles.worldInverseMatrix[0]", follicle + ".inputWorldMatrix", force=True
            )
            cmds.connectAttr(follicle + ".outTranslate", follicle + ".t", force=True)
            cmds.connectAttr(follicle + ".outRotate", follicle + ".r", force=True)

            # U dal punto del ribbon piu' vicino al joint
            pos = _ws(joint)
            cmds.setAttr(sampler + ".inPosition", pos[0], pos[1], pos[2], type="float3")
            u = cmds.getAttr(sampler + ".result.parameterU")
            cmds.setAttr(follicle + ".parameterU", u)
            cmds.setAttr(follicle + ".parameterV", 0.5)

            pma = cmds.createNode("plusMinusAverage", name="{}LipPMA{}".format(upper_lower, tag))
            cmds.connectAttr(follicle + ".t", pma + ".input3D[0]")
            pos_a = cmds.getAttr(follicle + ".t")[0]
            pos_b = cmds.getAttr(joint + ".t")[0]
            cmds.setAttr(
                pma + ".input3D[1]", *[pos_b[k] - pos_a[k] for k in range(3)], type="float3"
            )

            bc = cmds.createNode("blendColors", name="{}LipBC{}".format(upper_lower, tag))
            cmds.setAttr(bc + ".blender", 1)
            cmds.connectAttr(pma + ".output3D", bc + ".color1")
            cmds.connectAttr(pma + ".output3D", bc + ".color2")
            if upper_lower == "lower":  # color2 = posizione del labbro opposto
                if cmds.objExists("upperLipBC" + tag):
                    cmds.connectAttr(pma + ".output3D", "upperLipBC" + tag + ".color2", force=True)
                if cmds.objExists("upperLipPMA" + tag):
                    cmds.connectAttr("upperLipPMA" + tag + ".output3D", bc + ".color2", force=True)
            for channel, axis in zip("RGB", "xyz"):
                cmds.connectAttr("{}.output{}".format(bc, channel), "{}.t{}".format(joint, axis))

            sr = cmds.createNode("setRange", name="{}LipSR{}".format(upper_lower, tag))
            cmds.setAttr(sr + ".min", 1, 1, 0, type="float3")
            cmds.setAttr(sr + ".max", 0.5, 0.5, 0, type="float3")
            cmds.setAttr(sr + ".oldMin", u * 8, 10 - (u * 8 + 2), 0, type="float3")
            cmds.setAttr(sr + ".oldMax", u * 8 + 2, 10 - (u * 8), 0, type="float3")
            cmds.connectAttr("PlaceHolderStickyLip_R.sticky", sr + ".valueX")
            cmds.connectAttr("PlaceHolderStickyLip_L.sticky", sr + ".valueY")
            mdl = as_create_mult_dl("{}LipMDL{}".format(upper_lower, tag))  # miscela R/L
            cmds.connectAttr(sr + ".outValueX", mdl + ".input1")
            cmds.connectAttr(sr + ".outValueY", mdl + ".input2")
            clamp = cmds.createNode("clamp", name="{}LipClamp{}".format(upper_lower, tag))
            cmds.setAttr(clamp + ".minR", 0.5)
            cmds.setAttr(clamp + ".maxR", 1.0)
            cmds.connectAttr(mdl + ".output", clamp + ".inputR")
            cmds.connectAttr(clamp + ".outputR", bc + ".blender")

    # l'upper puo' avere piu' span del lower: i joint upper senza
    # corrispondente lower seguono l'ultimo lower
    upper_num = cmds.getAttr("upperLipMainBuildCurve.spans") + 1
    last_lower = cmds.getAttr("lowerLipMainBuildCurve.spans") - 1
    for side in ("_R", "_L"):
        for i in range(1, upper_num):
            if not cmds.objExists("lowerLipJoint{}{}".format(i, side)):
                cmds.connectAttr(
                    "lowerLipPMA{}{}.output3D".format(last_lower, side),
                    "upperLipBC{}{}.color2".format(i, side),
                    force=True,
                )


def _s3_bind_and_weights(ctx):
    """Joint delle labbra come influenze, peso pieno sui vertici dei loop
    Inner/Outer/Main e sui percorsi che li uniscono, hammer del resto."""
    from .face_ctrl_pp import weight_hammer_verts_ms
    from .fitting import _select_least_edges_path

    geometry, skin = ctx.geometry, ctx.skin_cluster
    joints = [
        j
        for j in cmds.listRelatives("FaceJoint_M", allDescendents=True, type="joint") or []
        if "Lip" in j and j != "MultiSkinClustersFaceLipJoint_M"
    ]
    # piu' veloce aggiungerle bloccate e poi sbloccarle
    cmds.skinCluster(
        skin, edit=True, dropoffRate=4, lockWeights=True, weight=0, addInfluence=joints
    )
    for joint in joints:
        cmds.setAttr(joint + ".lockInfluenceWeights", 0)

    def weigh_selection(joint):
        try:  # catchQuiet nel MEL
            cmds.skinPercent(skin, transformValue=(joint, 1))
        except RuntimeError:
            pass

    vtx_nr = {"Inner": {}, "Outer": {}, "Main": {}}  # $innerVtxNr ecc.: mai azzerati
    for upper_lower, _factor in _UPPER_LOWER:
        ctx.main_num_cv = cmds.getAttr(upper_lower + "LipMainBuildCurve.spans") + 1
        ids = _lip_joint_ids(upper_lower, ctx.main_num_cv)
        for b in (1, -1):
            side_ids = [(i, side) for i, side, bb in ids if bb == b]
            for in_out_main in ("Inner", "Outer", "Main"):
                curve = "{}Lip{}BuildCurve".format(upper_lower, in_out_main)
                left_cvs = cmds.getAttr(curve + "Left.spans") + cmds.getAttr(curve + "Left.degree")
                for i, side in side_ids:
                    pos = _ws("{}.cv[{}]".format(curve, i))
                    if side == "_L" and i < left_cvs:
                        pos = _ws("{}Left.cv[{}]".format(curve, i))
                        pos[0] *= -1
                    cmds.setAttr(
                        "closestSampler.inPosition", pos[0] * b, pos[1], pos[2], type="float3"
                    )
                    index = cmds.getAttr("closestSampler.result.closestVertexIndex")
                    cmds.select("{}.vtx[{}]".format(geometry, index))
                    weigh_selection("{}LipJoint{}{}".format(upper_lower, i, side))
                    vtx_nr[in_out_main][i] = index

            # vertici sul percorso piu' corto Outer->Main e Inner->Main
            for i, side in side_ids:
                joint = "{}LipJoint{}{}".format(upper_lower, i, side)
                is_corner = i == ctx.main_num_cv - 1
                for start in ("Outer", "Inner"):
                    cmds.select(geometry)
                    _select_least_edges_path(geometry, vtx_nr[start][i], vtx_nr["Main"][i])
                    cmds.select(cmds.polyListComponentConversion(toVertex=True))
                    if is_corner:
                        corner = ctx.right_cnr_vtxs if b == 1 else ctx.left_cnr_vtxs
                        if start == "Outer":
                            del corner[:]
                        corner.extend(cmds.ls(selection=True) or [])
                    weigh_selection(joint)
    cmds.delete("closestSampler")

    # hammer dei vertici dell'area rimasti tutti sull'HeadJoint
    leftovers = [
        v
        for v in ctx.lip_area
        if cmds.skinPercent(
            skin, v, transform=ctx.head_joint, ignoreBelow=1, query=True, value=True
        )
    ]
    cmds.select(clear=True)
    if leftovers:
        cmds.select(leftovers)
        weight_hammer_verts_ms(5, skin)


# ---------------------------------------------------------------------------
# 4. controller del ribbon, controller verdi, sticky, joint fleshy
#    (MEL:31832-32150)
# ---------------------------------------------------------------------------


def _letter(number):
    """asNrToLetter: 1 -> A, 2 -> B, ..."""
    return chr(ord("A") + number - 1)


def _extrude_curve(curve, name, length):
    cmds.extrude(
        curve,
        name=name,
        constructionHistory=False,
        range=False,
        polygon=0,
        extrudeType=0,
        useProfileNormal=True,
        length=length,
        rotation=0,
        scale=1,
        degreeAlongLength=3,
    )


def _move_y(distance, *nodes):
    cmds.move(0, distance, 0, *nodes, relative=True, objectSpace=True, worldSpaceDistance=True)


def _attach_to_loc(ctrl, side):
    """Attach del controller alla loc sulla curva del ribbon: solo la
    traslazione, con l'offset iniziale tolto da una PMA (MEL:31941-31972)."""
    attach = ctrl + "Attach" + side
    as_parent_constraint(
        ctrl + "Loc" + side, attach, include_pick_matrix=True, force_mult_matrix=True
    )
    pm, dm = ctrl + "AttachPM" + side, ctrl + "AttachDM" + side
    for flag in ("useRotate", "useScale", "useShear"):
        cmds.setAttr("{}.{}".format(pm, flag), 0)
    for axis, upper, shear in (("x", "X", "xy"), ("y", "Y", "xz"), ("z", "Z", "yz")):
        cmds.disconnectAttr("{}.outputRotate{}".format(dm, upper), "{}.r{}".format(attach, axis))
        cmds.disconnectAttr("{}.outputScale{}".format(dm, upper), "{}.s{}".format(attach, axis))
        cmds.disconnectAttr("{}.outputShear{}".format(dm, upper), "{}.sh{}".format(attach, shear))
    pma = cmds.createNode("plusMinusAverage", name=ctrl + "OffsetPMA" + side)
    cmds.connectAttr(dm + ".outputTranslate", pma + ".input3D[0]")
    cmds.setAttr(pma + ".operation", 2)
    for axis in "xyz":
        cmds.setAttr(
            "{}.input3D[1].input3D{}".format(pma, axis),
            cmds.getAttr("{}.input3D[0].input3D{}".format(pma, axis)),
        )
        cmds.connectAttr(
            "{}.output3D{}".format(pma, axis), "{}.t{}".format(attach, axis), force=True
        )


def _s4_ribbon_controllers(ctx):
    """Controller piccoli (LipA, LipB, ... cornerLip): ognuno guida un
    RibbonJoint che skinna una colonna di CV del ribbon."""
    from .face_ctrl_pp import create_pp

    npc = cmds.createNode("nearestPointOnCurve", name="tempNearestPointOnCurve")
    cmds.createNode("transform", name="TempPos")
    # il MEL ricrea un nodo con questo nome senza cancellare il primo: Maya
    # lo rinomina (…1) e resta orfano in scena. Replicato per parita' del DG.
    cmds.createNode("closestPointOnSurface", name="tempClosestPointOnSurface")
    sampler = "tempClosestPointOnSurface"
    uniform = cmds.createNode("closestPointOnSurface", name="tempClosestPointOnSurfaceUniform")
    path = cmds.createNode("motionPath", name="asTempMotionPath")
    temp = cmds.createNode("transform", name="asTempTransform")
    cmds.connectAttr(path + ".r", temp + ".r", force=True)
    cmds.setAttr(path + ".frontAxis", 0)
    cmds.setAttr(path + ".upAxis", 1)
    cmds.connectAttr(path + ".ro", temp + ".ro")
    cmds.setAttr(path + ".ro", 1)

    end = ctx.end
    for upper_lower, factor in _UPPER_LOWER:
        ribbon = upper_lower + "LipRibbon"
        ribbon_curve = upper_lower + "LipRibbonCurve"
        shaped_rebuilt = upper_lower + "LipRibbonCurveShapedrebuiltCurve1"
        cmds.connectAttr(ribbon_curve + "Shape.worldSpace[0]", npc + ".inputCurve", force=True)
        _extrude_curve(ribbon_curve, ribbon_curve + "Extruded", ctx.scale / 100)
        cmds.rebuildSurface(
            ribbon_curve + "Extruded",
            constructionHistory=0,
            replaceOriginal=1,
            rebuildType=0,
            endKnots=1,
            keepRange=0,
            keepControlPoints=0,
            keepCorners=0,
            spansU=0,
            degreeU=3,
            spansV=0,
            degreeV=3,
            tolerance=0.01,
            fitRebuild=0,
            direction=0,
        )
        # dalla v6.5351 entrambi i sampler leggono l'estrusione della curva Shaped
        _extrude_curve(shaped_rebuilt, shaped_rebuilt + "Extruded", ctx.scale / 100)
        for node in (sampler, uniform):
            cmds.connectAttr(
                shaped_rebuilt + "Extruded.worldSpace[0]", node + ".inputSurface", force=True
            )

        for side, _left, _b in _SIDES:
            u_int = ctx.ribbon_spans_u // 2 + (2 if side == "_R" else 1)
            for i in range(end + 1):
                u_int += -1 if side == "_R" else 1
                ctrl = upper_lower + "Lip" + _letter(i + 1)
                if i == end:
                    if upper_lower == "lower":
                        continue
                    ctrl = "cornerLip"

                # parametro U piu' vicino ai CV controllati
                pos = _ws("{}.cv[{}][1]".format(ribbon, u_int))
                for node in (sampler, uniform):
                    cmds.setAttr(node + ".inPosition", pos[0], pos[1], pos[2], type="float3")
                on_uniform = cmds.getAttr(uniform + ".result.parameterU")
                poci = cmds.createNode("pointOnCurveInfo", name=ctrl + "POCI" + side)
                cmds.connectAttr(
                    shaped_rebuilt + ".worldSpace[0]", poci + ".inputCurve", force=True
                )
                cmds.setAttr(poci + ".turnOnPercentage", 1)
                cmds.setAttr(poci + ".parameter", on_uniform)
                pos = cmds.getAttr(poci + ".position")[0]

                cmds.xform("TempPos", worldSpace=True, translation=pos)
                dist = ctx.ctrl_scale * 0.2 * factor
                if i == end - 1:
                    dist /= 2.0
                if i == end:
                    dist = 0
                # creato alla posizione "Offset" per proiettarlo bene, poi
                # l'Offset torna giu' e la shape risale
                _move_y(dist, "TempPos")
                create_pp("TempPos", ctrl, side, 1, True, False, True)
                _move_y(dist * -1, ctrl + "Offset" + side, ctrl + "JointOffset" + side)
                cmds.setAttr(ctrl + "Joint" + side + ".radius", 0.25)
                cmds.addAttr(
                    ctrl + side,
                    keyable=False,
                    longName="parameterOnUniform",
                    attributeType="double",
                    defaultValue=on_uniform,
                )
                loc = cmds.createNode("transform", name=ctrl + "Loc" + side, parent="LipRibbonLocs")
                cmds.connectAttr(poci + ".position", loc + ".t")

                # la loc passa dalla curva Shaped alla curva del ribbon
                cmds.connectAttr(ribbon_curve + ".worldSpace[0]", poci + ".inputCurve", force=True)
                cmds.setAttr(npc + ".inPosition", pos[0], pos[1], pos[2], type="float3")
                cmds.setAttr(poci + ".turnOnPercentage", 0)
                cmds.setAttr(poci + ".parameter", cmds.getAttr(npc + ".result.parameter"))
                _attach_to_loc(ctrl, side)

                ribbon_joint = cmds.rename(ctrl + "Joint" + side, ctrl + "RibbonJoint" + side)
                joint_offset = cmds.rename(
                    ctrl + "JointOffset" + side, ctrl + "RibbonJointOffset" + side
                )
                cmds.parent(joint_offset, "LipRibbonJoints")  # non e' un joint di bind diretto
                _move_y(dist, ctrl + side + ".cv[0:99]")

                ribbon_sc = ribbon + "SC"
                if i == 0 and side == "_R":
                    _skin([ribbon_joint], ribbon, ribbon_sc)
                else:
                    cmds.skinCluster(
                        ribbon_sc,
                        edit=True,
                        dropoffRate=4,
                        lockWeights=False,
                        weight=0,
                        addInfluence=ribbon_joint,
                    )
                cmds.skinPercent(
                    ribbon_sc,
                    "{}.cv[{}][0:1]".format(ribbon, u_int),
                    transformValue=(ribbon_joint, 1),
                )

    cmds.delete("TempPos", npc, sampler, uniform, path, temp)
    for upper_lower, _factor in _UPPER_LOWER:
        ribbon_curve = upper_lower + "LipRibbonCurve"
        shaped = upper_lower + "LipRibbonCurveShaped"
        cmds.delete(ribbon_curve + "Extruded", shaped, shaped + "rebuiltCurve1")
        if cmds.objExists(shaped + "rebuiltCurve1Extruded"):
            cmds.delete(shaped + "rebuiltCurve1Extruded")
        cmds.parent(ribbon_curve, upper_lower + "LipRibbon", "LipRibbon")

    # il cornerLip muove anche l'estremita' del ribbon lower
    for side, u_int in (("_R", 0), ("_L", end * 2 + 1)):
        joint = "cornerLipRibbonJoint" + side
        cmds.skinCluster(
            "lowerLipRibbonSC", edit=True, dropoffRate=4, lockWeights=False, weight=0,
            addInfluence=joint,
        )  # fmt: skip
        cmds.skinPercent(
            "lowerLipRibbonSC",
            "lowerLipRibbon.cv[{}][0:1]".format(u_int),
            transformValue=(joint, 1),
        )


def _s4_green_controllers(ctx):
    """Controller principali: Lip_R/L (angoli), upper/lowerLip_M e
    upper/lowerLip_R/L (meta' labbro)."""
    from .face_ctrl_pp import create_pp, face_half_moon_curve

    cmds.createNode("transform", name="TempPos")
    specs = (
        ("_R", "", 0, "cornerLip_R", 2),
        ("_L", "", 0, "cornerLip_L", 2),
        ("_M", "upper", 1, "upperLipA_R", 2),
        ("_M", "lower", -1, "lowerLipA_R", 2),
        ("_R", "upper", 1, "upperLipA_R", 3),
        ("_R", "lower", -1, "lowerLipA_R", 3),
        ("_L", "upper", 1, "upperLipA_L", 3),
        ("_L", "lower", -1, "lowerLipA_L", 3),
    )
    for index, (side, upper_lower, factor, align_to, ctrl_type) in enumerate(specs):
        b = 1 if side == "_R" else -1
        ctrl = upper_lower + "Lip"
        pos = _ws(align_to)
        if side == "_M":
            pos[0] = 0
        cmds.xform("TempPos", worldSpace=True, translation=pos)
        lift = ctx.ctrl_scale * 0.2 * factor
        if side == "_M":
            _move_y(lift, "TempPos")
        if index > 3:  # meta' labbro: a un terzo del loop Outer
            temp_curve = cmds.rebuildCurve(
                upper_lower + "LipOuterBuildCurve",
                name="asLipTempCurve",
                constructionHistory=1,
                replaceOriginal=0,
                rebuildType=0,
                endKnots=1,
                keepRange=0,
                keepControlPoints=0,
                keepEndPoints=1,
                keepTangents=0,
                spans=2,
                degree=3,
                tolerance=0.01,
            )[0]
            pos = _ws(temp_curve + ".cv[2]")
            cmds.xform("TempPos", worldSpace=True, translation=(pos[0] * b, pos[1], pos[2]))
            cmds.delete(temp_curve)
        create_pp("TempPos", ctrl, side, ctrl_type, False, False, False)
        if side == "_M":
            _move_y(lift * -1, ctrl + "Offset" + side)
    cmds.delete("TempPos")

    face_half_moon_curve("upperLip_M", 90)
    face_half_moon_curve("lowerLip_M", -90)
    face_half_moon_curve("Lip_R", 0)
    face_half_moon_curve("Lip_L", 0)

    for side in ("_R", "_L"):
        lip = "Lip" + side
        cmds.addAttr(
            lip,
            keyable=True,
            longName="sticky",
            attributeType="double",
            minValue=0,
            maxValue=10,
            defaultValue=0,
        )
        ensure_output_blend_weighted(lip + ".sticky")
        holder = "PlaceHolderStickyLip" + side
        for plug in (
            cmds.listConnections(holder + ".sticky", source=False, destination=True, plugs=True)
            or []
        ):
            cmds.connectAttr("bw{}_sticky.output".format(lip), plug, force=True)
        cmds.delete(holder)

    for upper_lower, factor in _UPPER_LOWER:
        cvs = upper_lower + "Lip_M.cv[0:99]"
        _move_y(ctx.ctrl_scale * 0.2 * factor, cvs)
        # il MEL legge il pivot dal manipolatore Move (non disponibile in
        # batch): centro del bounding box dei CV
        bb = cmds.exactWorldBoundingBox(cvs)
        pivot = [(bb[k] + bb[k + 3]) / 2.0 for k in range(3)]
        cmds.scale(2, 2, 2, cvs, relative=True, pivot=pivot)


def _s4_fleshy_joints(ctx):
    """Joint "fleshy" che seguono la traslazione dei controller verdi nello
    spazio della testa (ruotati da LipRegion)."""
    for name in ("Lip_R", "Lip_L", "upperLip_M", "lowerLip_M", "upperLip_R", "upperLip_L",
                 "lowerLip_R", "lowerLip_L"):  # fmt: skip
        ctrl, side = name.split("_")[0], "_" + name.split("_")[1]
        cmds.select("LipRibbonFleshyJoints")
        joint = cmds.joint(name=ctrl + "JointFleshy" + side)
        constrained = cmds.createNode(
            "transform", name=ctrl + "ConstrainedFleshy" + side, parent="LipFollowHeadConstrained"
        )
        dm = cmds.createNode("decomposeMatrix", name=ctrl + "ConstrainedFleshyDM" + side)
        mm = cmds.createNode("multMatrix", name=ctrl + "ConstrainedFleshyMM" + side)
        cmds.connectAttr(name + ".worldMatrix", mm + ".matrixIn[0]")
        cmds.connectAttr("LipFollowHeadConstrained.worldInverseMatrix", mm + ".matrixIn[1]")
        cmds.connectAttr(mm + ".matrixSum", dm + ".inputMatrix")
        cmds.connectAttr(dm + ".outputTranslate", constrained + ".t")
        if not cmds.objExists("LipRegionDM_M"):
            cmds.createNode("decomposeMatrix", name="LipRegionDM_M")
            cmds.createNode("multMatrix", name="LipRegionMM_M")
            cmds.connectAttr("LipRegion_M.worldMatrix", "LipRegionMM_M.matrixIn[0]")
            cmds.connectAttr(
                "LipFollowHeadConstrained.worldInverseMatrix", "LipRegionMM_M.matrixIn[1]"
            )
            cmds.connectAttr("LipRegionMM_M.matrixSum", "LipRegionDM_M.inputMatrix")
        cmds.connectAttr("LipRegionDM_M.outputRotate", constrained + ".r")
        cmds.connectAttr(constrained + ".t", joint + ".t")


# ---------------------------------------------------------------------------
# 5. curva fleshy del ribbon, scala/rotazione dei joint (MEL:32192-32385)
# ---------------------------------------------------------------------------


def _smoothstep(edge0, edge1, x):
    if edge1 == edge0:
        return 0.0 if x < edge0 else 1.0
    t = max(0.0, min(1.0, (x - edge0) / float(edge1 - edge0)))
    return t * t * (3 - 2 * t)


def _ribbon_ctrl_names(upper_lower, end):
    """(i, ctrl, letter) dei controller del ribbon di un lato; l'ultimo
    dell'upper e' il cornerLip, il lower non lo ha."""
    names = []
    for i in range(end + 1):
        letter = _letter(i + 1)
        if i == end:
            if upper_lower == "lower":
                continue
            names.append((i, "cornerLip", letter))
        else:
            names.append((i, upper_lower + "Lip" + letter, letter))
    return names


def _s5_fleshy_ribbon_curve(ctx):
    """I RibbonJoint seguono una curva "fleshy" skinnata ai joint dei
    controller verdi; `fractionMode` miscela posizione parametrica e
    frazionaria lungo la curva."""
    from .driving_system import unit_convert_and_reverse

    npc = cmds.createNode("nearestPointOnCurve", name="tempNearestPointOnCurve")
    for upper_lower, _factor in _UPPER_LOWER:
        lip_m = upper_lower + "Lip_M"
        cmds.addAttr(
            lip_m,
            keyable=True,
            longName="fractionMode",
            attributeType="double",
            minValue=0,
            maxValue=10,
            defaultValue=10,
        )
        ensure_output_blend_weighted(lip_m + ".fractionMode")
        fraction = upper_lower + "LipFractionMode_M"
        unit_convert_and_reverse(fraction, "bw{}_fractionMode.output".format(lip_m))

        fleshy = upper_lower + "LipRibbonCurveFleshy"
        cmds.duplicate(upper_lower + "LipRibbonCurve", name=fleshy)
        cmds.parent(fleshy, "LipRibbonFleshy")
        for shape in cmds.listRelatives(fleshy, shapes=True, fullPath=True) or []:
            if cmds.getAttr(shape + ".intermediateObject"):
                cmds.delete(shape)
        _rebuild(fleshy, spans=4)

        up_r, up_l = upper_lower + "LipJointFleshy_R", upper_lower + "LipJointFleshy_L"
        sc = _skin(
            ["LipJointFleshy_R", "LipJointFleshy_L", up_r, up_l],
            fleshy,
            fleshy + "SC",
            max_influences=2,
        )
        cmds.setAttr(sc + ".maintainMaxInfluences", 1)
        for cvs, joint, weight in (
            ("0:2", up_r, 1),
            ("4:6", up_l, 1),
            ("0", "LipJointFleshy_R", 1),
            ("1", "LipJointFleshy_R", 0.670),
            ("2", "LipJointFleshy_R", 0.100),
            ("3", up_r, 1.0),
            ("3", up_l, 0.5),
            ("4", "LipJointFleshy_L", 0.100),
            ("5", "LipJointFleshy_L", 0.670),
            ("6", "LipJointFleshy_L", 1),
        ):
            cmds.skinPercent(sc, "{}.cv[{}]".format(fleshy, cvs), transformValue=(joint, weight))
        cmds.connectAttr(fleshy + ".worldSpace[0]", npc + ".inputCurve", force=True)

        for side, _left, _b in _SIDES:
            for i, ctrl, letter in _ribbon_ctrl_names(upper_lower, ctx.end):
                if i == ctx.end:
                    parameter = 0 if side == "_R" else 1
                else:
                    pos = _ws("{}Lip{}{}".format(upper_lower, letter, side))
                    cmds.setAttr(npc + ".inPosition", pos[0], pos[1], pos[2], type="float3")
                    parameter = cmds.getAttr(npc + ".result.parameter")

                # motionPath invece di poci, per l'opzione parametrica
                bc = cmds.createNode(
                    "blendColors", name=ctrl + "FleshyFractionalBlendColors" + side
                )
                cmds.connectAttr(fraction + "Reverse.outputX", bc + ".blender")
                joint_offset = ctrl + "RibbonJointOffset" + side
                for a in (1, 2):
                    follower = cmds.createNode(
                        "transform",
                        name="{}Lip{}RibbonJointFleshy{}{}".format(upper_lower, letter, a, side),
                        parent="LipRibbonFleshy",
                    )
                    path = cmds.createNode(
                        "motionPath", name="{}FleshyMotionPath{}{}".format(ctrl, a, side)
                    )
                    cmds.setAttr(path + ".fractionMode", a - 1)
                    cmds.connectAttr(fleshy + ".worldSpace[0]", path + ".geometryPath", force=True)
                    cmds.setAttr(path + ".uValue", parameter)
                    cmds.connectAttr(path + ".allCoordinates", follower + ".t")
                    # fleshy + offset -> Offset del joint
                    pma = cmds.createNode(
                        "plusMinusAverage", name="{}FleshyAddPMA{}{}".format(ctrl, a, side)
                    )
                    cmds.connectAttr(path + ".allCoordinates", pma + ".input3D[0]")
                    pos_a = cmds.getAttr(path + ".allCoordinates")[0]
                    pos_b = cmds.getAttr(joint_offset + ".t")[0]
                    cmds.setAttr(
                        pma + ".input3D[1]", *[pos_b[k] - pos_a[k] for k in range(3)], type="float3"
                    )
                    cmds.connectAttr(pma + ".output3D", "{}.color{}".format(bc, a))
                cmds.connectAttr(bc + ".output", joint_offset + ".t")


def _s5_joint_scale_and_rotation(ctx):
    """Ogni joint per-CV ruota in X come i due controller del ribbon piu'
    vicini (pesati per distanza) piu' il controller verde, e scala come il
    controller verde (via multMatrix/decomposeMatrix)."""
    quarter, half = ctx.lip_ctrls // 4, ctx.lip_ctrls // 2
    closest_1 = closest_2 = ""  # $closestCtrl1/2: mai azzerati nel MEL
    for upper_lower, _factor in _UPPER_LOWER:
        ctx.main_num_cv = cmds.getAttr(upper_lower + "LipMainBuildCurve.spans") + 1
        lip_m = upper_lower + "Lip_M"
        mm = cmds.createNode("multMatrix", name=upper_lower + "LipMM_M")
        dm = cmds.createNode("decomposeMatrix", name=upper_lower + "LipDM_M")
        cmds.connectAttr(mm + ".matrixSum", dm + ".inputMatrix")
        cmds.connectAttr(lip_m + ".matrix", mm + ".matrixIn[0]")
        cmds.connectAttr("SDK" + lip_m + ".matrix", mm + ".matrixIn[1]")
        if upper_lower == "upper":
            cmds.connectAttr("LipRegion_M.matrix", mm + ".matrixIn[2]")
            cmds.connectAttr("SDKLipRegion_M.matrix", mm + ".matrixIn[3]")

        ctrls = ["cornerLip_L"]
        ctrls += [
            upper_lower + "Lip" + _letter(quarter - y + 1) + "_L" for y in range(1, quarter + 1)
        ]
        ctrls += [
            upper_lower + "Lip" + _letter(y - quarter) + "_R" for y in range(quarter + 1, half + 1)
        ]
        ctrls += ["cornerLip_R"]

        for i, side, _b in _lip_joint_ids(upper_lower, ctx.main_num_cv):
            joint = "{}LipJoint{}{}".format(upper_lower, i, side)
            joint_parameter = cmds.getAttr("{}follicle{}{}.parameterU".format(upper_lower, i, side))
            min_1 = min_2 = 999.0
            for ctrl in ctrls:
                dist = joint_parameter - cmds.getAttr(ctrl + ".parameterOnUniform")
                if 0 < dist < min_1:
                    min_1, closest_1 = dist, ctrl
                if dist < 0 and -dist < min_2:
                    min_2, closest_2 = -dist, ctrl

            bw = cmds.createNode("blendWeighted", name="{}LipBW{}{}".format(upper_lower, i, side))
            sources = (
                closest_1,
                closest_2,
                "SDK" + closest_1,
                "SDK" + closest_2,
                lip_m,
                "SDK" + lip_m,
            )
            for index, source in enumerate(sources):
                cmds.connectAttr(source + ".rx", "{}.input[{}]".format(bw, index))
            red = max(0.0, min(1.0, _smoothstep(0, min_1 + min_2, min_2)))
            green = _smoothstep(0, 0.7, 1 - (1.0 / ctx.main_num_cv) * i)
            for index, weight in enumerate((red, 1 - red, red, 1 - red, green, green)):
                cmds.setAttr("{}.weight[{}]".format(bw, index), weight)
            cmds.connectAttr(bw + ".output", joint + ".rx")
            cmds.connectAttr(dm + ".outputScale", joint + ".s", force=True)


# ---------------------------------------------------------------------------
# 6. SDK press/squeeze/roll/pucker, LipsTogether, chiusura (MEL:32387-32563)
# ---------------------------------------------------------------------------


def _key_pose(nodes, values):
    """Chiave di riposo al frame 0 sui nodi, chiavi di posa al frame 30."""
    cmds.setKeyframe(nodes, time=0)
    for plug, value in values:
        cmds.setKeyframe(plug, time=30, value=value)


def _s6_lips_attrs_sdk(ctx):
    """Collega gli attributi di ctrlLips_M (press, squeeze, roll, pucker)
    a pose dei controller verdi, convertite in SDK da face_ds_finish."""
    from .driving_system import face_ds_finish

    for upper_lower, factor in _UPPER_LOWER:
        lip = upper_lower + "Lip_M"

        _key_pose(lip, [(lip + ".sz", 0.2)])
        face_ds_finish("ctrlLips", "_M", upper_lower + "Press", 10)

        pos_a, pos_b = _ws(lip), _ws(upper_lower + "LipMainCurve.cv[0]")
        squeeze_ty = ((pos_b[1] - pos_a[1]) / ctx.ctrl_scale) * 0.5
        _key_pose(lip, [(lip + ".sy", 0.3), (lip + ".ty", squeeze_ty)])
        face_ds_finish("ctrlLips", "_M", upper_lower + "Squeeze", 10)

        _key_pose(lip, [(lip + ".tz", 0.05), (lip + ".rx", -30 * factor)])
        face_ds_finish("ctrlLips", "_M", upper_lower + "Roll", 10)
        _key_pose(lip, [(lip + ".tz", -0.35)])
        face_ds_finish("ctrlLips", "_M", upper_lower + "Roll", -10)

        pos_a, pos_b = _ws("upperLipOuterCurve.cv[0]"), _ws("upperLipMainCurve.cv[0]")
        thickness = pos_a[1] - pos_b[1]  # relativo allo spessore del labbro
        _key_pose(
            lip, [(lip + ".ty", 0.15 * factor), (lip + ".tz", 0.25), (lip + ".rx", -30 * factor)]
        )
        face_ds_finish("ctrlLips", "_M", upper_lower + "Pucker", 10)
        narrow = (thickness / ctx.ctrl_scale) * -0.3
        _key_pose(["Lip_R", "Lip_L"], [("Lip_R.tx", narrow), ("Lip_L.tx", narrow)])
        face_ds_finish("ctrlLips", "_M", upper_lower + "Pucker", 10)


def _temp_under_fleshy():
    """tempTransform sotto upperLipConstrainedFleshy_M con la scala di
    OnFacecontrols, e un figlio tempTransform2."""
    temp = cmds.createNode("transform", name="tempTransform", parent="upperLipConstrainedFleshy_M")
    cmds.delete(cmds.scaleConstraint("OnFacecontrols", temp))
    return temp, cmds.createNode("transform", name="tempTransform2", parent=temp)


def _pick_matrix(name, *disabled):
    pm = cmds.createNode("pickMatrix", name=name)
    for flag in disabled:
        cmds.setAttr("{}.{}".format(pm, flag), 0)
    return pm


def _lips_together(upper_lower, side):
    """Attributo `lipsTogether` di upper/lowerLip_R/L: il controller scivola
    verso il punto medio fra upperLip_M e lowerLip_M (MEL:32455-32547)."""
    from .build_utils import as_align, as_matrix_connect_attr

    base = upper_lower + "Lip"
    ctrl = base + side
    fleshy_m = upper_lower + "LipConstrainedFleshy_M"
    static = cmds.createNode(
        "transform", name=upper_lower + "LipsTogetherStatic" + side, parent=ctrl
    )
    static = cmds.parent(static, fleshy_m)[0]
    cmds.xform(static, objectSpace=True, scale=(1, 1, 1))
    follow = cmds.duplicate(static, name=upper_lower + "LipsTogetherFollow" + side)[0]
    lip_follow = cmds.createNode(
        "transform", name=base + "Follow" + side, parent=base + "Offset" + side
    )
    cmds.parent("SDK" + ctrl, lip_follow)

    bm = cmds.createNode("blendMatrix", name=upper_lower + "LipsTogetherFollowBM" + side)
    cmds.connectAttr("upperLip_M.worldMatrix", bm + ".inputMatrix")
    cmds.connectAttr("lowerLip_M.worldMatrix", bm + ".target[0].targetMatrix")
    cmds.setAttr(bm + ".target[0].weight", 0.5)
    mm = cmds.createNode("multMatrix", name=upper_lower + "LipsTogetherFollowMM" + side)
    temp, temp2 = _temp_under_fleshy()
    as_align(temp2, ctrl, translate=True)
    cmds.setAttr(mm + ".matrixIn[0]", cmds.getAttr(temp2 + ".matrix"), type="matrix")
    cmds.delete(temp)
    temp, temp2 = _temp_under_fleshy()
    cmds.pointConstraint("upperLip_M", "lowerLip_M", temp2)
    cmds.setAttr(mm + ".matrixIn[1]", cmds.getAttr(temp2 + ".inverseMatrix"), type="matrix")
    cmds.delete(temp)

    pm = _pick_matrix(upper_lower + "LipsTogetherFollowPM" + side, "useScale", "useShear")
    cmds.connectAttr(mm + ".matrixSum", pm + ".inputMatrix")
    as_matrix_connect_attr(pm + ".outputMatrix", follow + ".offsetParentMatrix")
    # PM1: creato e collegato dal MEL ma non piu' usato a valle (v6.5821)
    pm1 = _pick_matrix(base + "FollowPM1" + side, "useRotate", "useScale", "useShear")
    cmds.connectAttr(bm + ".outputMatrix", pm1 + ".inputMatrix")
    cmds.connectAttr(bm + ".outputMatrix", mm + ".matrixIn[2]")
    cmds.connectAttr(fleshy_m + ".worldInverseMatrix", mm + ".matrixIn[3]")
    cmds.xform(follow, objectSpace=True, translation=(0, 0, 0), rotation=(0, 0, 0), scale=(1, 1, 1))
    cmds.delete(cmds.pointConstraint(static, follow))

    follow_bm = cmds.createNode("blendMatrix", name=base + "FollowBM" + side)
    cmds.connectAttr(static + ".worldMatrix", follow_bm + ".inputMatrix")
    cmds.connectAttr(follow + ".worldMatrix", follow_bm + ".target[0].targetMatrix")
    follow_mm = cmds.createNode("multMatrix", name=base + "FollowMM" + side)
    cmds.connectAttr(follow_bm + ".outputMatrix", follow_mm + ".matrixIn[0]")
    cmds.connectAttr(base + "Offset" + side + ".worldInverseMatrix", follow_mm + ".matrixIn[1]")
    pm2 = _pick_matrix(base + "FollowPM2" + side, "useRotate", "useScale", "useShear")
    cmds.connectAttr(follow_mm + ".matrixSum", pm2 + ".inputMatrix")
    as_matrix_connect_attr(pm2 + ".outputMatrix", lip_follow + ".offsetParentMatrix")

    cmds.addAttr(
        ctrl,
        keyable=True,
        longName="lipsTogether",
        attributeType="double",
        minValue=0,
        maxValue=10,
        defaultValue=0,
    )
    ensure_output_blend_weighted(ctrl + ".lipsTogether")
    conversion = cmds.createNode(
        "unitConversion", name=upper_lower + "LipsTogether" + side + "UnitConversion"
    )
    cmds.setAttr(conversion + ".conversionFactor", 0.1)
    cmds.connectAttr("bw{}_lipsTogether.output".format(ctrl), conversion + ".input")
    cmds.connectAttr(conversion + ".output", follow_bm + ".target[0].weight")


def _s6_finish(ctx):
    # l'ultimo joint upper di ogni lato e' l'angolo della bocca
    last = cmds.getAttr("upperLipMainCurve.spans")
    for side in ("_R", "_L"):
        cmds.rename("upperLipJoint{}{}".format(last, side), "cornerLipJoint" + side)
    cmds.parent("upperLipOffset_M", "lowerLipOffset_M", "LipOffset_R", "LipOffset_L", "LipRegion_M")
    cmds.rename("FaceControlOrient", "FaceControlOrientLip")
    cmds.rename("FaceControlSuspended", "FaceControlOrient")

    for side in ("_R", "_L"):
        for upper_lower, _factor in _UPPER_LOWER:
            _lips_together(upper_lower, side)

    # il MEL fa `select -add` senza svuotare la selezione: nel set entra
    # anche l'ultimo nodo creato (replicato, i nomi dei set sono un'API)
    cmds.select(get_face_fit_selection("FaceFitLipMainCurve").split(), add=True)
    cmds.sets(name="lipMainArea")
    cmds.sets("lipMainArea", add="FaceAreas")

    cmds.delete("LipConstruction")
    if cmds.objExists("closestNurbsSampler"):
        cmds.delete("closestNurbsSampler")
    cmds.setAttr("ctrlBoxLips_M.v", 1)
    cmds.setAttr("ctrlLips_M.tx", lock=True, keyable=False)
    cmds.setAttr("ctrlLips_M.ty", lock=True, keyable=False)


# ---------------------------------------------------------------------------
# entry point
# ---------------------------------------------------------------------------

_SECTIONS = [
    _s1_base,
    _s1_lip_region,
    _s1_build_curves_and_joints,
    _s2_slide_surface,
    _s2_ribbon_curves,
    _s2_ribbon_surfaces,
    _s3_follicles,
    _s3_bind_and_weights,
    _s4_ribbon_controllers,
    _s4_green_controllers,
    _s4_fleshy_joints,
    _s5_fleshy_ribbon_curve,
    _s5_joint_scale_and_rotation,
    _s6_lips_attrs_sdk,
    _s6_finish,
]


def face_lip() -> bool:
    """Costruisce le labbra (asFaceLip). No-op (True) senza
    upperLipMainCurve, come il gate del MEL (MEL:31175)."""
    if not cmds.objExists(FIT_SKELETON):
        cmds.warning("FaceFitSkeleton not found")
        return False

    face_eye_wide_finish()
    as_face_hide_controllers(True)
    if cmds.objExists("ctrlBox.RegionsCtrlVis"):
        cmds.setAttr("ctrlBox.RegionsCtrlVis", 0)
    if not cmds.objExists("upperLipMainCurve"):
        return True

    ctx = _Ctx()
    for section in _SECTIONS:
        section(ctx)
    cmds.select(clear=True)
    return True

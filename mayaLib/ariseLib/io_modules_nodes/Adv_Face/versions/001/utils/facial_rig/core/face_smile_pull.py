"""Build step SmilePull (parita' asFaceSmilePull MEL:34121-34352 e
asFaceSmilePullFinish MEL:34354-34384), piu' asCreateCustomBlendedAttribute
(MEL:61567-61652).

Apre con asFaceSquintFinish. Costruisce un "muscolo" di guida
(ZygomaticusMajor: tre profili loftati dal punto sullo zigomo all'angolo
della bocca) che, accorciandosi fra i frame 0 e 30, tira l'angolo della
bocca lungo la superficie del viso. La posizione tirata di Lip_R,
SmileBulge_R e FrownBulge_R diventa la posa "smile" (fit-anim su
ctrlMouthCorner tx=1, ty=1). Crea anche gli attributi miscelati
smile/frown/narrowSmile/narrowFrown su ctrlMouthCorner_R/L.

Il finish salva la posa in `SmileValues`, cancella il muscolo e converte
la posa in SDK (ds_finish ctrlMouthCorner _RL smile 1).

Divergenze (docs/gap-analysis.md §5m): il ciclo MEL che scorre i frame per
mostrare il muscolo nel viewport (MEL:34200-34209) e' solo visivo e non e'
replicato; oggetti assenti = warning + False.
"""

import maya.cmds as cmds

from .build_utils import as_align, as_face_hide_controllers, as_lock_attr
from .driving_system import ensure_output_blend_weighted, face_ds_finish, mirror_connect_ctrls
from .face_squint import face_squint_finish
from .fit_options import FIT_SKELETON, get_fit_option
from .fitting import face_fit_anim, remove_fit_anim_from_ctrl_box

_DRIVEN = ("Lip", "SmileBulge", "FrownBulge", "lowerLidOuter", "CheekBone", "Cheek", "NoseCorner")
_BLENDED = (("smile", 1, 1), ("frown", 1, -1), ("narrowSmile", -1, 1), ("narrowFrown", -1, -1))


def _ws(node):
    return cmds.xform(node, query=True, worldSpace=True, translation=True)


def create_custom_blended_attribute(drivers, attr_name):
    """Attributo che vale 0-10 quando i due driver sono entrambi ai valori
    correnti (asCreateCustomBlendedAttribute).

    Args:
        drivers: due plug "nodo.attr" dello stesso nodo, gia' impostati ai
            valori (+1 o -1) che definiscono la posa.
        attr_name: nome dell'attributo creato sul nodo dei driver.

    Returns:
        Il nome dell'attributo.
    """
    selection = cmds.ls(selection=True)
    node = drivers[0].split(".")[0]
    attrs = [d.split(".")[1] for d in drivers]
    values = [cmds.getAttr(d) for d in drivers]
    q_rotates_cmd = ""
    for driver in drivers:
        fk = "FK" + driver.replace("qRotate", "rotate", 1)
        if cmds.objExists(fk):
            q_rotates_cmd += "setAttr {} {};".format(fk, cmds.getAttr(fk))

    def restore_selection():
        if selection:
            cmds.select(selection)
        else:
            cmds.select(clear=True)

    if cmds.attributeQuery(attr_name, node=node, exists=True):
        restore_selection()
        return attr_name

    plug = "{}.{}".format(node, attr_name)
    cmds.addAttr(node, keyable=False, longName=attr_name, attributeType="double")
    cmds.setAttr(plug, edit=True, channelBox=True)
    if not node.startswith("FK") and cmds.objExists("FK" + node):
        cmds.addAttr("FK" + node, keyable=False, longName=attr_name, attributeType="double")
        cmds.setAttr("FK" + plug, edit=True, channelBox=True)
        cmds.connectAttr(plug, "FK" + plug)

    base = node + attr_name
    mpd = cmds.createNode("multiplyDivide", name=base + "MPD")
    # i driver sono letti dal loro blendWeighted
    for bw_attr, axis in zip(attrs, "XY"):
        bw = ensure_output_blend_weighted("{}.{}".format(node, bw_attr))
        cmds.connectAttr(bw + ".output", "{}.input1{}".format(mpd, axis))
    if values[0] == -1:
        cmds.setAttr(mpd + ".input2X", -1)
    if values[1] == -1:
        cmds.setAttr(mpd + ".input2Y", -1)
    pma = cmds.createNode("plusMinusAverage", name=base + "PlusMinusAverage")
    cmds.connectAttr(mpd + ".outputX", pma + ".input1D[0]")
    cmds.connectAttr(mpd + ".outputY", pma + ".input1D[1]")
    sr = cmds.createNode("setRange", name=base + "SetRange")
    cmds.connectAttr(pma + ".output1D", sr + ".valueX", force=True)
    cmds.setAttr(sr + ".max", 100, 100, 100, type="float3")
    cmds.setAttr(sr + ".oldMax", 200, 200, 200, type="float3")
    for name, attr in (("dvX", attrs[0]), ("dvY", attrs[1])):
        cmds.addAttr(
            sr,
            keyable=True,
            longName=name,
            attributeType="double",
            defaultValue=cmds.getAttr("{}.{}".format(node, attr)),
        )
    cmds.addAttr(sr, longName="setQRotatesCmd", dataType="string")
    cmds.setAttr(sr + ".setQRotatesCmd", q_rotates_cmd, type="string")

    clamp = cmds.createNode("clamp", name=base + "Clamp")
    cmds.connectAttr(sr + ".outValueX", clamp + ".inputR")
    cmds.addAttr(
        node,
        keyable=False,
        longName=attr_name + "MaxValue",
        attributeType="double",
        defaultValue=10,
    )
    cmds.connectAttr(plug + "MaxValue", clamp + ".maxR")
    cmds.connectAttr(clamp + ".outputR", plug)
    ensure_output_blend_weighted(plug)
    restore_selection()
    return attr_name


def _build_muscle(geometry, scale):
    """ZygomaticusMajor: loft di tre profili dallo zigomo all'angolo della
    bocca, con la scala animata che tira Lip_R (MEL:34139-34198)."""
    if not cmds.objExists("FaceMuscles"):
        cmds.createNode("transform", name="FaceMuscles", parent="FaceBuildInProgress")
    if not cmds.objExists("FaceMusclesLayer"):
        cmds.createDisplayLayer(name="FaceMusclesLayer")
    muscle = cmds.createNode("transform", name="ZygomaticusMajor", parent="FaceMuscles")
    circle = cmds.circle(
        center=(0, 0, 0),
        normal=(0, 0, 1),
        sweep=360,
        radius=scale / 25.0,
        degree=3,
        useTolerance=False,
        tolerance=0.000393701,
        sections=8,
        constructionHistory=False,
    )[0]
    curve1 = cmds.rename(circle, "ZygomaticusMajor_curve1")
    cmds.setAttr(curve1 + ".v", 0)
    pos_b = _ws("upperEyeLidOuterCurve.cv[99]")
    pos1 = cmds.spaceLocator(name="ZygomaticusMajorPosition1")[0]
    cmds.parent(pos1, muscle)
    cmds.setAttr(pos1 + ".v", 0)
    cmds.setAttr(pos1 + ".overrideEnabled", 1)
    cmds.setAttr(pos1 + ".overrideColor", 17)
    cmds.setAttr(pos1 + "Shape.localScale", scale / 15.0, scale / 15.0, scale / 15.0, type="float3")

    # dall'angolo dell'occhio verso il JawPivot, sulla superficie, fino a 45 gradi
    temp = cmds.createNode("transform", name="tempXform", parent="Lip_R")
    temp2 = cmds.createNode("transform", name="tempXform2")
    cmds.xform(temp2, worldSpace=True, translation=pos_b)
    constraint = cmds.pointConstraint(temp2, "JawPivot", temp)[0]
    cmds.geometryConstraint(geometry, temp)
    cmds.setAttr(temp + ".displayLocalAxis", 1)
    for i in range(101):
        cmds.setAttr(constraint + ".tempXform2W0", 1 - i / 100.0)
        cmds.setAttr(constraint + ".JawPivotW1", i / 100.0)
        cmds.refresh()
        if cmds.getAttr(temp + ".tx") > cmds.getAttr(temp + ".ty"):
            break
    pos_b = _ws(temp)
    cmds.delete(temp, temp2)

    cmds.xform(pos1, worldSpace=True, translation=pos_b)
    cmds.parent(curve1, pos1, relative=True)
    cmds.delete(
        cmds.aimConstraint(
            "Lip_R",
            pos1,
            offset=(0, 0, 0),
            weight=1,
            aimVector=(0, 0, 1),
            upVector=(0, 0, 1),
            worldUpType="objectrotation",
            worldUpObject="Lip_R",
        )
    )
    for index in (2, 3):
        dup = cmds.duplicate(pos1, name="ZygomaticusMajorPosition{}".format(index))[0]
        cmds.rename(dup + "|ZygomaticusMajor_curve1", "ZygomaticusMajor_curve{}".format(index))
    cmds.setAttr("ZygomaticusMajor_curve1.scaleX", 0)
    cmds.setAttr("ZygomaticusMajor_curve2.scaleX", 0.5)
    cmds.setAttr("ZygomaticusMajor_curve3.scaleX", 0)
    pos_a, pos_b = _ws("ZygomaticusMajorPosition2"), _ws("Lip_R")
    cmds.xform(
        "ZygomaticusMajorPosition2",
        worldSpace=True,
        translation=[(pos_a[k] + pos_b[k]) / 2.0 for k in range(3)],
    )
    cmds.xform("ZygomaticusMajorPosition3", worldSpace=True, translation=pos_b)
    cmds.loft(
        "ZygomaticusMajor_curve1",
        "ZygomaticusMajor_curve2",
        "ZygomaticusMajor_curve3",
        name="ZygomaticusMajor_loft",
        constructionHistory=True,
        uniform=True,
        close=False,
        autoReverse=False,
        degree=3,
        sectionSpans=1,
        range=False,
        polygon=0,
        reverseSurfaceNormals=True,
    )
    if cmds.objExists("asFaceRedSG"):
        cmds.sets("ZygomaticusMajor_loft", edit=True, forceElement="asFaceRedSG")
    cmds.parent("ZygomaticusMajor_loft", muscle)
    scaler = cmds.createNode("transform", name="ZygomaticusMajorScale", parent=pos1)
    cmds.setKeyframe(scaler + ".s", time=0, value=1)
    cmds.setKeyframe(scaler + ".s", time=30, value=0.75)
    cmds.setKeyframe("ZygomaticusMajorPosition2.s", time=0, value=1)
    cmds.setKeyframe("ZygomaticusMajorPosition2.s", time=30, value=1.3)
    cmds.currentTime(0)
    cmds.parentConstraint(scaler, "ZygomaticusMajorPosition3", maintainOffset=True)
    cmds.parentConstraint(pos1, "ZygomaticusMajorPosition3", "ZygomaticusMajorPosition2")
    cmds.parentConstraint(scaler, "Lip_R", maintainOffset=True)
    cmds.setAttr("FaceMusclesLayer.v", 0)
    cmds.currentTime(0)


def _pulled_positions():
    """Posizioni di Lip/SmileBulge/FrownBulge quando il muscolo e' contratto
    (frame 30), nello spazio dei rispettivi SDK (MEL:34240-34262)."""
    for name, parent in (("LipPulled", "Lip_R"), ("SmileBulgePulled", "SmileBulge_R"),
                         ("FrownBulgePulled", "FrownBulge_R")):  # fmt: skip
        cmds.createNode("transform", name=name, parent=parent)
    cmds.parent("LipPulled", "SmileBulgePulled", "FrownBulgePulled", "ZygomaticusMajorScale")
    as_face_hide_controllers(True)
    mirror_connect_ctrls(True)

    cmds.currentTime(30)
    cmds.parent("LipPulled", "SDKLip_R")
    cmds.parent("SmileBulgePulled", "SDKSmileBulge_R")
    cmds.parent("FrownBulgePulled", "SDKFrownBulge_R")
    # l'angolo tirato e agganciato alla superficie: letto dall'Attach
    temp = cmds.createNode("transform", name="tempTransform", parent="cornerLipAttach_R")
    temp = cmds.parent(temp, "cornerLipOffset_R")[0]
    lip = cmds.getAttr(temp + ".t")[0]
    cmds.delete(temp)
    smile = cmds.getAttr("SmileBulgePulled.t")[0]
    frown = cmds.getAttr("FrownBulgePulled.t")[0]
    cmds.delete("Lip_R_parentConstraint1")
    cmds.currentTime(0)
    return lip, smile, frown


def face_smile_pull() -> bool:
    """Posa "smile" tirata dal muscolo zigomatico (asFaceSmilePull).

    Returns:
        True anche quando lo step e' saltato per assenza di
        `upperLipMainCurve` (gate MEL); False con warning se manca un
        prerequisito.
    """
    face_squint_finish()
    if not cmds.objExists("upperLipMainCurve"):
        return True
    geometry = get_fit_option("Face") or ""
    head_joint = get_fit_option("HeadJoint") or ""
    required = [geometry, head_joint, FIT_SKELETON, "FaceBuildInProgress", "JawPivot", "LipSetup"]
    required += ["Lip_R", "SmileBulge_R", "FrownBulge_R", "SmileBulge", "cornerLipAttach_R"]
    required += ["ctrlMouthCorner_R", "ctrlMouthCorner_L", "upperEyeLidOuterCurve"]
    missing = [node for node in required if not node or not cmds.objExists(node)]
    if missing:
        cmds.warning("face_smile_pull: missing {}".format(", ".join(missing) or "options"))
        return False
    scale = cmds.getAttr(FIT_SKELETON + ".faceScale")

    _build_muscle(geometry, scale)

    joints = cmds.listRelatives("FaceJoint_M", allDescendents=True, type="joint") or []
    for joint in joints + ["Face_M", head_joint]:
        if cmds.objExists(joint + ".lockInfluenceWeights"):
            cmds.setAttr(joint + ".lockInfluenceWeights", 0)

    # segnaposto del fit "Lip" (conserva il raggio di falloff)
    if not cmds.objExists("Lip"):
        pos_a, pos_b = _ws("Lip_R"), _ws("SmileBulge")
        radius = sum((pos_a[k] - pos_b[k]) ** 2 for k in range(3)) ** 0.5
        cmds.createNode("transform", name="Lip", parent="LipSetup")
        as_align("Lip", "Lip_R", translate=True)
        cmds.addAttr(
            "Lip",
            keyable=True,
            longName="falloffRadius",
            attributeType="double",
            defaultValue=radius,
        )
        if get_fit_option("NonSym"):
            cmds.duplicate("Lip", name="LipLeft")
            as_align("LipLeft", "Lip_L", translate=True)

    lip, smile, frown = _pulled_positions()
    pull_dist = sum(v * v for v in lip) ** 0.5

    cmds.setAttr("ctrlBoxMouthCorner_R.v", 1)
    cmds.setAttr("ctrlBoxMouthCorner_L.v", 1)
    # attributi miscelati di ctrlMouthCorner X/Y
    for side in ("_R", "_L"):
        tx, ty = "ctrlMouthCorner" + side + ".tx", "ctrlMouthCorner" + side + ".ty"
        for name, x, y in _BLENDED:
            cmds.setAttr(tx, x)
            cmds.setAttr(ty, y)
            create_custom_blended_attribute([tx, ty], name)
        cmds.setAttr(tx, 0)
        cmds.setAttr(ty, 0)
    cmds.setAttr("ctrlMouthCorner_R.tx", 1)
    cmds.setAttr("ctrlMouthCorner_R.ty", 1)

    poses = [("ctrlMouthCorner_R.tx", 1), ("ctrlMouthCorner_R.ty", 1)]
    poses += [("ctrlMouthCorner_L.tx", 1), ("ctrlMouthCorner_L.ty", 1)]
    poses += [("Lip_R", 0), ("Lip_R.tx", lip[0]), ("Lip_R.ty", lip[1]), ("Lip_R.tz", lip[2])]
    poses += [("SmileBulge_R", 0), ("SmileBulge_R.tx", smile[0] * 0.8)]
    poses += [("SmileBulge_R.ty", smile[1] * 0.8), ("SmileBulge_R.tz", 0.33 * pull_dist)]
    poses += [("FrownBulge_R", 0), ("FrownBulge_R.tx", frown[0] * 0.7)]
    poses += [("FrownBulge_R.ty", frown[1] * 0.7), ("FrownBulge_R.tz", 0.212 * pull_dist)]
    if cmds.objExists("lowerLidOuter_R"):
        poses += [("lowerLidOuter_R", 0), ("lowerLidOuter_R.tx", frown[0] * 0.0075)]
        poses += [("lowerLidOuter_R.ty", frown[1] * 0.025), ("lowerLidOuter_R.tz", 0.1 * pull_dist)]
    poses += [("CheekBone_R", 0), ("CheekBone_R.tx", frown[0] * 0.025)]
    poses += [("CheekBone_R.ty", frown[1] * 0.1), ("CheekBone_R.tz", 0.1 * pull_dist)]
    poses += [("Cheek_R", 0), ("Cheek_R.tx", frown[0] * 0.1)]
    poses += [("Cheek_R.ty", frown[1] * 0.25), ("Cheek_R.tz", 0.3 * pull_dist)]
    poses += [("NoseCorner_R", 0), ("NoseCorner_R.tx", frown[0] * 0.1)]
    poses += [("NoseCorner_R.ty", frown[1] * 0.1)]
    for plug, value in poses:
        face_fit_anim(plug, value)

    cmds.playbackOptions(minTime=0, maxTime=30, animationStartTime=0, animationEndTime=30)
    cmds.currentTime(30)
    cmds.select(clear=True)
    return True


def face_smile_pull_finish():
    """Salva la posa smile in `SmileValues`, cancella il muscolo e converte
    la posa in SDK (asFaceSmilePullFinish). Idempotente via
    FaceBuildInProgress.SmilePullFinish."""
    if not cmds.objExists("FaceBuildInProgress"):
        cmds.warning("face_smile_pull_finish: FaceBuildInProgress not found")
        return
    if cmds.attributeQuery("SmilePullFinish", node="FaceBuildInProgress", exists=True):
        return
    cmds.addAttr(
        "FaceBuildInProgress",
        longName="SmilePullFinish",
        attributeType="bool",
        defaultValue=True,
        keyable=False,
    )
    for node in ("Lip", "FaceMuscles", "FaceMusclesLayer"):
        if cmds.objExists(node):
            cmds.delete(node)
    mirror_connect_ctrls(False)
    remove_fit_anim_from_ctrl_box()

    cmds.currentTime(30)
    cmds.createNode("transform", name="SmileValues", parent="FaceBuildInProgress")
    as_lock_attr("SmileValues", True, True, True, True)
    for name in _DRIVEN:
        ctrl = name + "_R"
        if not cmds.objExists(ctrl):
            continue
        for trs in "trs":
            for axis in "xyz":
                cmds.addAttr(
                    "SmileValues",
                    keyable=True,
                    longName="{}_{}{}".format(ctrl, trs, axis),
                    attributeType="double",
                    defaultValue=cmds.getAttr("{}.{}{}".format(ctrl, trs, axis)),
                )
    face_ds_finish("ctrlMouthCorner", "_RL", "smile", 1)
    as_face_hide_controllers(True)
    for box in ("ctrlBoxMouthCorner_R", "ctrlBoxMouthCorner_L"):
        if cmds.objExists(box):
            cmds.setAttr(box + ".v", 1)

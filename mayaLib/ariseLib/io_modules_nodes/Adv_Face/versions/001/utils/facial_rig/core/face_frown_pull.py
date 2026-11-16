"""Build step FrownPull (parita' asFaceFrownPull MEL:34386-34419,
asFaceFrownPullFinish MEL:34421-34435, asFaceNarrowSmileAndFrown
MEL:34437-34542, asFaceSmilePullController MEL:34544-34602) e step Cheek
(asFaceCheek MEL:34604-34639).

FrownPull chiude SmilePull e posa il "frown" come lo smile con ty e rz
invertiti. Il suo finish (chiamato da Cheek) converte la posa in SDK e poi
costruisce il controller `SmilePull_R/L` e le pose narrowSmile/narrowFrown
(lo smile con tx invertito e senza tz). Cheek e' la posa della guancia
gonfia su ctrlCheek.tx.

Divergenze (docs/gap-analysis.md §5m): oggetti assenti = warning + False.
"""

import maya.cmds as cmds

from .build_utils import as_face_hide_controllers, as_lock_attr
from .ctrl_box import create_face_controller, place_ctrl_by_projection
from .driving_system import (
    ds_sdk,
    ensure_output_blend_weighted,
    face_ds_finish,
    mirror_connect_ctrls,
)
from .face_ctrl_pp import face_half_moon_curve
from .face_smile_pull import face_smile_pull_finish
from .fitting import (
    face_fit_anim,
    remove_fit_anim_from_ctrl_box,
    remove_fit_animations_from_on_face_ctrls,
)


def _smile_values():
    """(plug, valore) dalla posa salvata in SmileValues ("Lip_R_tx" ->
    "Lip_R.tx")."""
    out = []
    for name in cmds.listAttr("SmileValues", userDefined=True) or []:
        tokens = name.split("_")
        out.append((tokens[0] + "_" + tokens[1], tokens[2], cmds.getAttr("SmileValues." + name)))
    return out


def _show_mouth_corner_boxes():
    as_face_hide_controllers(True)
    for box in ("ctrlBoxMouthCorner_R", "ctrlBoxMouthCorner_L"):
        cmds.setAttr(box + ".v", 1)


def _end_pose():
    cmds.playbackOptions(minTime=0, maxTime=30, animationStartTime=0, animationEndTime=30)
    cmds.currentTime(30)
    cmds.select(clear=True)


def face_frown_pull() -> bool:
    """Posa "frown": lo smile con ty e rz invertiti (asFaceFrownPull)."""
    if not cmds.objExists("upperLipMainCurve"):
        return True
    face_smile_pull_finish()
    if not cmds.objExists("SmileValues"):
        cmds.warning("face_frown_pull: SmileValues not found (run SmilePull first)")
        return False
    for plug, value in (("ctrlMouthCorner_R.tx", 1), ("ctrlMouthCorner_R.ty", -1),
                        ("ctrlMouthCorner_L.tx", 1), ("ctrlMouthCorner_L.ty", -1)):  # fmt: skip
        face_fit_anim(plug, value)
    for obj, attr, value in _smile_values():
        if attr in ("ty", "rz"):
            value *= -1
        face_fit_anim("{}.{}".format(obj, attr), value)
    _end_pose()
    return True


def face_smile_pull_controller():
    """Controller `SmilePull_R/L` sull'angolo della bocca: i suoi tx/ty
    guidano ctrlMouthCorner (asFaceSmilePullController)."""
    auto_key = cmds.autoKeyframe(query=True, state=True)
    if auto_key:
        cmds.autoKeyframe(state=False)
    temp = cmds.createNode("transform", name="tempXform", parent="LipOffset_R")
    temp = cmds.parent(temp, "SideReverse_R")[0]
    rot_y = cmds.getAttr(temp + ".ry")
    cmds.delete(temp)

    tx = ty = 0.0
    for side in ("_R", "_L"):
        ctrl, offset = "SmilePull" + side, "SmilePullOffset" + side
        create_face_controller("SmilePull", side, 2)
        cmds.setAttr(ctrl + "Shape.overrideColor", 17)
        pos = cmds.xform("Lip" + side, query=True, worldSpace=True, translation=True)
        cmds.scale(1.8, 1.8, 1.8, ctrl + ".cv[0:99]", relative=True, pivot=(0, 0, 0))
        cmds.xform(offset, worldSpace=True, translation=pos)
        cmds.parent(offset, "SideReverse" + side)
        cmds.setAttr(offset + ".s", 1, 1, 1, type="float3")
        face_half_moon_curve(ctrl, 0)
        cmds.setAttr(offset + ".ry", rot_y)
        as_lock_attr(ctrl, True, True, True, True)
        cmds.setAttr(ctrl + ".tx", keyable=True, lock=False)
        cmds.setAttr(ctrl + ".ty", keyable=True, lock=False)
        place_ctrl_by_projection(ctrl)

        # quanto deve muoversi SmilePull per equivalere a ctrlMouthCorner=1
        if side == "_R":
            probe = cmds.createNode("transform", name="tempTransform1", parent="SmilePull_R")
            cmds.pointConstraint("Lip_R", probe)
            cmds.setAttr("ctrlMouthCorner_R.tx", 1)
            tx = cmds.getAttr(probe + ".tx")
            cmds.setAttr("ctrlMouthCorner_R.tx", 0)
            cmds.setAttr("ctrlMouthCorner_R.ty", 1)
            ty = cmds.getAttr(probe + ".ty")
            cmds.setAttr("ctrlMouthCorner_R.ty", 0)
            cmds.delete(probe)

        ensure_output_blend_weighted(ctrl + ".tx")
        ensure_output_blend_weighted(ctrl + ".ty")
        ds_sdk(ctrl + ".tx", "bwctrlMouthCorner{}_translateX.input".format(side), tx, 1.0)
        ds_sdk(ctrl + ".ty", "bwctrlMouthCorner{}_translateY.input".format(side), ty, 0.5)
    if auto_key:
        cmds.autoKeyframe(state=True)


def face_narrow_smile_and_frown():
    """Controller SmilePull, restringimento automatico delle labbra e pose
    narrowSmile / narrowFrown (asFaceNarrowSmileAndFrown)."""
    mirror_connect_ctrls(False)
    remove_fit_anim_from_ctrl_box()
    remove_fit_animations_from_on_face_ctrls()
    face_smile_pull_controller()

    narrow = cmds.getAttr("SmileValues.Lip_R_tx") / -2.0
    for side in ("_R", "_L"):
        for upper_lower in ("upper", "lower"):
            sdk = "SDK{}Lip{}".format(upper_lower, side)
            ds_sdk("ctrlMouthCorner" + side + ".tx", sdk + ".tx", -1, narrow)
            if cmds.objExists(sdk + "_translateX"):
                cmds.setAttr(sdk + "_translateX.postInfinity", 1)

    for attr_name, flip in (("narrowSmile", ("tx",)), ("narrowFrown", ("tx", "ty"))):
        for obj, attr, value in _smile_values():
            if attr == "tz":
                continue
            if attr in flip:
                value *= -1
            face_fit_anim("{}.{}".format(obj, attr), value)
        face_fit_anim("ctrlMouthCorner_R.tx", -1)
        face_fit_anim("ctrlMouthCorner_R.ty", 1 if attr_name == "narrowSmile" else -1)
        remove_fit_anim_from_ctrl_box()
        face_ds_finish("ctrlMouthCorner", "_RL", attr_name, 1)

    _show_mouth_corner_boxes()
    cmds.setAttr("SmilePullOffset_R.v", 1)
    cmds.setAttr("SmilePullOffset_L.v", 1)
    # ctrlMouth_M.tx si innesta su ctrlMouthCorner.tx
    for side in ("_R", "_L"):
        cmds.connectAttr(
            "bwctrlMouth_M_translateX.output",
            "bwctrlMouthCorner{}_translateX.input[2]".format(side),
        )


def face_frown_pull_finish():
    """Converte il frown in SDK e costruisce le pose narrow
    (asFaceFrownPullFinish). Idempotente via
    FaceBuildInProgress.FrownPullFinish."""
    if not cmds.objExists("FaceBuildInProgress"):
        cmds.warning("face_frown_pull_finish: FaceBuildInProgress not found")
        return
    if cmds.attributeQuery("FrownPullFinish", node="FaceBuildInProgress", exists=True):
        return
    if not cmds.objExists("SmileValues") or not cmds.objExists("ctrlBoxMouthCorner_R"):
        cmds.warning("face_frown_pull_finish: SmilePull/FrownPull were not built, skipping")
        return
    cmds.addAttr(
        "FaceBuildInProgress",
        longName="FrownPullFinish",
        attributeType="bool",
        defaultValue=True,
        keyable=False,
    )
    mirror_connect_ctrls(False)
    remove_fit_anim_from_ctrl_box()
    face_ds_finish("ctrlMouthCorner", "_RL", "frown", 1)
    _show_mouth_corner_boxes()
    face_narrow_smile_and_frown()


def face_cheek() -> bool:
    """Posa della guancia gonfia su ctrlCheek.tx (asFaceCheek)."""
    if not cmds.objExists("upperLipMainCurve"):
        return True
    face_frown_pull_finish()
    if not cmds.objExists("Cheek_R"):
        cmds.warning("face_cheek: Cheek_R not found (run FaceCage first)")
        return False
    as_face_hide_controllers(True)
    mirror_connect_ctrls(True)
    for plug, value in (("ctrlCheek_R.tx", 1), ("ctrlCheek_L.tx", 1), ("Cheek_R", 0),
                        ("Cheek_R.tz", 1.0), ("Cheek_R.sx", 1.2), ("Cheek_R.sy", 1.2),
                        ("Cheek_R.sz", 1.2)):  # fmt: skip
        face_fit_anim(plug, value)
    _end_pose()
    return True

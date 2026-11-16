"""Build step EyeBlink (parita' asFaceEyeBlink MEL:31032 e
asFaceEyeBlinkFinish MEL:31088).

Aggiunge gli attributi blink/wide agli eye controller, la rete FleshyBlinkMPD
che sfuma il fleshy durante il blink, posa il blink via fit-anim e converte
le pose in SDK (finish). simplerEyeLid e' letto da get_fit_option invece del
checkBox MEL (coerente col port della UI Pre).
"""

import maya.cmds as cmds

from .build_utils import as_face_hide_controllers
from .driving_system import (
    ensure_output_blend_weighted,
    face_ds_finish,
    mirror_connect_ctrls,
    unit_convert_and_reverse,
)
from .fit_options import get_fit_option
from .fitting import face_fit_anim, remove_fit_anim_from_ctrl_box


def face_eye_blink():
    """Setup blink/wide + rete fleshy + pose fit-anim (asFaceEyeBlink).
    Ritorna bool. Nessuna eccezione."""
    for side in ("_R", "_L"):
        if not cmds.objExists("ctrlEye" + side):
            cmds.warning("face_eye_blink: ctrlEye{} not found".format(side))
            return False

    simpler = bool(get_fit_option("SimplerEyeLid"))

    for side in ("_R", "_L"):
        ctrl = "ctrlEye" + side
        for attr in ("wide", "blink"):
            if not cmds.attributeQuery(attr, node=ctrl, exists=True):
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
        ensure_output_blend_weighted(ctrl + ".wide")
        ensure_output_blend_weighted(ctrl + ".blink")

        unit_convert_and_reverse(
            "bwctrlEye" + side + "_blink", "bwctrlEye" + side + "_blink.output"
        )

        for ul in ("upper", "lower"):
            lid = ul + "Lid" + side
            mpd = cmds.createNode("multiplyDivide", name=lid + "FleshyBlinkMPD")
            cmds.connectAttr(lid + ".fleshy", mpd + ".input1Y")
            cmds.connectAttr("bwctrlEye" + side + "_blinkReverse.outputX", mpd + ".input2Y")
            cmds.connectAttr(mpd + ".outputY", lid + "FleshyMPD.input2Y", force=True)

    as_face_hide_controllers(True)
    mirror_connect_ctrls(True)

    face_fit_anim("ctrlEye_R.blink", 10)
    face_fit_anim("ctrlEye_L.blink", 10)
    face_fit_anim("upperLid_R.blink", 10)
    face_fit_anim("lowerLid_R.blink", 10)
    face_fit_anim("upperLid_R.tx", -0.2)
    face_fit_anim("lowerLid_R.tx", -0.2)
    face_fit_anim("outerLid_R.tx", -0.1)
    if not simpler:
        face_fit_anim("upperLidOuter_R.tx", -0.05)
        face_fit_anim("upperLidOuter_R.ty", -0.07)
        face_fit_anim("lowerLidOuter_R.tx", -0.1)
        face_fit_anim("lowerLidOuter_R.ty", 0.1)

    cmds.playbackOptions(minTime=0, maxTime=30, animationStartTime=0, animationEndTime=30)
    cmds.currentTime(30)
    cmds.select(clear=True)
    print("// EyeBlink applied")
    return True


def face_eye_blink_finish():
    """Converte le pose blink in SDK (asFaceEyeBlinkFinish). Idempotente
    via FaceBuildInProgress.EyeBlinkFinish. Nessuna eccezione."""
    if not cmds.objExists("FaceBuildInProgress"):
        cmds.warning("face_eye_blink_finish: FaceBuildInProgress not found")
        return
    if cmds.attributeQuery("EyeBlinkFinish", node="FaceBuildInProgress", exists=True):
        return
    cmds.addAttr(
        "FaceBuildInProgress",
        longName="EyeBlinkFinish",
        attributeType="bool",
        defaultValue=True,
        keyable=False,
    )

    mirror_connect_ctrls(False)
    remove_fit_anim_from_ctrl_box()
    face_ds_finish("ctrlEye", "_RL", "blink", 10)
    as_face_hide_controllers(True)
    for side in ("_R", "_L"):
        box = "ctrlBoxEye" + side
        if cmds.objExists(box):
            cmds.setAttr(box + ".v", 1)

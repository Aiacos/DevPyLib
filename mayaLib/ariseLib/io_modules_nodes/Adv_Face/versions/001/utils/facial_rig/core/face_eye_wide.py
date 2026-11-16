"""Build step EyeWide (parita' asFaceEyeWide MEL:31102 e
asFaceEyeWideFinish MEL:31118).

Lo step apre convertendo le pose blink in SDK (asFaceEyeBlinkFinish, MEL:31104),
posa il "wide" via fit-anim sui lid e — al finish — converte la posa wide in SDK.
L'attributo `wide` sui ctrlEye e' gia' creato dallo step EyeBlink. Nel MEL il
finish viene invocato dallo step successivo (asFaceLip); qui il dispatch del
builder lo esegue in auto-finish (vedi docs/gap-analysis.md), idempotente via il
guard FaceBuildInProgress.EyeWideFinish.
"""

import maya.cmds as cmds

from .build_utils import as_face_hide_controllers
from .driving_system import face_ds_finish, mirror_connect_ctrls
from .face_eye_blink import face_eye_blink_finish
from .fitting import face_fit_anim, remove_fit_anim_from_ctrl_box


def face_eye_wide():
    """Finish blink + posa wide via fit-anim (asFaceEyeWide).
    Ritorna bool. Nessuna eccezione."""
    for side in ("_R", "_L"):
        if not cmds.objExists("ctrlEye" + side):
            cmds.warning("face_eye_wide: ctrlEye{} not found".format(side))
            return False

    face_eye_blink_finish()

    as_face_hide_controllers(True)
    mirror_connect_ctrls(True)

    face_fit_anim("upperLid_R.ty", 0.3)
    face_fit_anim("lowerLid_R.ty", -0.1)

    cmds.playbackOptions(minTime=0, maxTime=30, animationStartTime=0, animationEndTime=30)
    cmds.currentTime(30)
    cmds.select(clear=True)
    print("// EyeWide applied")
    return True


def face_eye_wide_finish():
    """Converte la posa wide in SDK (asFaceEyeWideFinish). Idempotente
    via FaceBuildInProgress.EyeWideFinish. Nessuna eccezione."""
    if not cmds.objExists("FaceBuildInProgress"):
        cmds.warning("face_eye_wide_finish: FaceBuildInProgress not found")
        return
    if cmds.attributeQuery("EyeWideFinish", node="FaceBuildInProgress", exists=True):
        return
    cmds.addAttr(
        "FaceBuildInProgress",
        longName="EyeWideFinish",
        attributeType="bool",
        defaultValue=True,
        keyable=False,
    )

    mirror_connect_ctrls(False)
    remove_fit_anim_from_ctrl_box()
    face_ds_finish("ctrlEye", "_RL", "wide", 10)
    as_face_hide_controllers(True)
    for side in ("_R", "_L"):
        box = "ctrlBoxEye" + side
        if cmds.objExists(box):
            cmds.setAttr(box + ".v", 1)

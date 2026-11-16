"""Build step JawOpen (parita' asFaceJawOpen MEL:35216 e
asFaceJawOpenFinish MEL:35258).

Step di puro driving: posa `ctrlMouth_M` (slider del board) e alcuni controller
di regione via fit-anim, poi (finish) converte la posa in SDK
(`ds_finish ctrlMouth _M ty -1`). Gate su `upperLipMainCurve`.

Come nel MEL, `face_jaw_open` apre con `face_jaw_weighing_finish`
(MEL:35232), che copia sul viso i pesi della mascella e la fa seguire da
labbra e guance.

Divergenze (vedi docs/gap-analysis.md §5e): `cmds.select` filtrato sugli
oggetti esistenti (no-exceptions).
"""

import maya.cmds as cmds

from .build_utils import as_face_hide_controllers, as_show_layer
from .driving_system import face_ds_finish, mirror_connect_ctrls
from .fitting import face_fit_anim, remove_fit_anim_from_ctrl_box
from .jaw_weighing import face_jaw_weighing_finish


def face_jaw_open():
    """Posa mascella aperta via fit-anim (asFaceJawOpen). Ritorna bool;
    salta (True) senza `upperLipMainCurve`. Nessuna eccezione."""
    if not cmds.objExists("upperLipMainCurve"):
        return True  # skip fedele al MEL

    face_jaw_weighing_finish()
    as_face_hide_controllers(True)
    as_show_layer("Normal")
    mirror_connect_ctrls(True)

    face_fit_anim("ctrlMouth_M.ty", -1)
    face_fit_anim("Cheek_R", 0)
    face_fit_anim("Cheek_R.tz", -0.3)
    face_fit_anim("Lip_R", 0)
    face_fit_anim("Lip_R.tx", -0.4)
    face_fit_anim("NoseCorner_R", 0)
    face_fit_anim("NoseCorner_R.ty", -0.2)
    face_fit_anim("NoseUnder_M", 0)
    face_fit_anim("NoseUnder_M.ty", -0.05)

    cmds.playbackOptions(minTime=0, maxTime=30, animationStartTime=0, animationEndTime=30)
    cmds.currentTime(30)
    cmds.select(clear=True)
    print("// JawOpen applied")
    return True


def face_jaw_open_finish():
    """Converte la posa jaw-open in SDK (asFaceJawOpenFinish). Idempotente
    via FaceBuildInProgress.JawOpenFinish. Nessuna eccezione."""
    if not cmds.objExists("FaceBuildInProgress"):
        cmds.warning("face_jaw_open_finish: FaceBuildInProgress not found")
        return
    if cmds.attributeQuery("JawOpenFinish", node="FaceBuildInProgress", exists=True):
        return
    cmds.addAttr(
        "FaceBuildInProgress",
        longName="JawOpenFinish",
        attributeType="bool",
        defaultValue=True,
        keyable=False,
    )

    mirror_connect_ctrls(False)
    remove_fit_anim_from_ctrl_box()
    face_ds_finish("ctrlMouth", "_M", "ty", -1)
    as_face_hide_controllers(True)
    if cmds.objExists("ctrlBoxMouth_M"):
        cmds.setAttr("ctrlBoxMouth_M.v", 1)
    cmds.select(clear=True)

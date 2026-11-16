"""Build step LipUp (parita' asFaceLipUp MEL:35272 e
asFaceLipUpFinish MEL:35345).

Step di puro driving: apre con asFaceJawOpenFinish (MEL:35279), sblocca
ctrlLips_M.tx/ty, posa ctrlLips_M + i controller di regione della faccia bassa
via fit-anim, raccoglie i controller posati nel set `LipUpControls` (usato dagli
step LipDown/LipSide), poi (finish) converte in SDK (ds_finish ctrlLips _M ty 1).
Gate su `upperLipMainCurve`.

Divergenze (vedi docs/gap-analysis.md §5e): `cmds.select`/set filtrati sugli
oggetti esistenti (no-exceptions); i controller di regione nascono dagli step
mesh, quindi la posa e' fedele ma completa solo su asset reale.
"""

import maya.cmds as cmds

from .build_utils import as_face_hide_controllers
from .driving_system import face_ds_finish, mirror_connect_ctrls
from .face_jaw_open import face_jaw_open_finish
from .fitting import face_fit_anim, remove_fit_anim_from_ctrl_box


def _existing(names):
    return [n for n in names if cmds.objExists(n)]


def face_lip_up():
    """Posa 'lip up' via fit-anim + set LipUpControls (asFaceLipUp).
    Ritorna bool; salta (True) senza `upperLipMainCurve`. Nessuna eccezione."""
    if not cmds.objExists("upperLipMainCurve"):
        return True  # skip fedele al MEL

    face_jaw_open_finish()

    as_face_hide_controllers(True)
    mirror_connect_ctrls(True)
    for attr in ("ctrlLips_M.tx", "ctrlLips_M.ty"):
        if cmds.objExists(attr):
            cmds.setAttr(attr, lock=False, keyable=True)

    face_fit_anim("ctrlLips_M.ty", 1)
    for upper_lower in ("upper", "lower"):
        lip = upper_lower + "Lip_M"
        face_fit_anim(lip, 0)
        face_fit_anim(lip + ".ty", 0.8)
        face_fit_anim(lip + ".sy", 0.8)

    face_fit_anim("Lip_R", 0)
    face_fit_anim("Lip_R.tx", 0.1)
    face_fit_anim("Lip_R.ty", 0.7)
    face_fit_anim("SmileBulge_R", 0)
    face_fit_anim("SmileBulge_R.ty", 0.2)
    face_fit_anim("SmileBulge_R.tz", 0.75)
    face_fit_anim("FrownBulge_R", 0)
    face_fit_anim("FrownBulge_R.ty", 0.2)
    face_fit_anim("CheekBone_R", 0)
    face_fit_anim("CheekBone_R.tx", 0.1)
    face_fit_anim("CheekBone_R.ty", 0.1)
    face_fit_anim("NoseCorner_R", 0)
    face_fit_anim("NoseCorner_R.ty", 0.3)
    face_fit_anim("NoseSide_R", 0)
    face_fit_anim("NoseSide_R.ty", 0.2)
    face_fit_anim("Nostril_R.tx", 0.05)
    face_fit_anim("Nostril_R.ty", 0.1)
    face_fit_anim("Nose_M", 0)
    face_fit_anim("Nose_M.ty", 0.05)
    face_fit_anim("NoseBridge_M", 0)
    face_fit_anim("NoseBridge_M.ty", 0.04)
    face_fit_anim("NoseUnder_M", 0)
    face_fit_anim("NoseUnder_M.ty", 0.3)
    face_fit_anim("ChinCrease_M", 0)
    face_fit_anim("ChinCrease_M.ty", 0.75)
    face_fit_anim("ChinCrease_M.tz", 0.25)

    # set dei controller posati (usato da LipDown/LipSide)
    members = _existing(
        ["upperLip_M", "lowerLip_M", "Nose_M", "NoseBridge_M", "NoseUnder_M", "ChinCrease_M"]
    )
    for side in ("_R", "_L"):
        members += _existing(
            [
                b + side
                for b in (
                    "Lip",
                    "SmileBulge",
                    "FrownBulge",
                    "CheekBone",
                    "NoseCorner",
                    "NoseSide",
                    "Nostril",
                )
            ]
        )
    if not cmds.objExists("LipUpControls"):
        cmds.sets(members, name="LipUpControls")
        if cmds.objExists("FaceBuildingSets"):
            cmds.sets("LipUpControls", add="FaceBuildingSets")

    cmds.playbackOptions(minTime=0, maxTime=30, animationStartTime=0, animationEndTime=30)
    cmds.currentTime(30)
    cmds.select(clear=True)
    print("// LipUp applied")
    return True


def face_lip_up_finish():
    """Converte la posa lip-up in SDK (asFaceLipUpFinish). Idempotente
    via FaceBuildInProgress.LipUpFinish. Nessuna eccezione."""
    if not cmds.objExists("FaceBuildInProgress"):
        cmds.warning("face_lip_up_finish: FaceBuildInProgress not found")
        return
    if cmds.attributeQuery("LipUpFinish", node="FaceBuildInProgress", exists=True):
        return
    cmds.addAttr(
        "FaceBuildInProgress",
        longName="LipUpFinish",
        attributeType="bool",
        defaultValue=True,
        keyable=False,
    )

    mirror_connect_ctrls(False)
    remove_fit_anim_from_ctrl_box()
    face_ds_finish("ctrlLips", "_M", "ty", 1)
    as_face_hide_controllers(True)
    if cmds.objExists("ctrlBoxLips_M"):
        cmds.setAttr("ctrlBoxLips_M.v", 1)

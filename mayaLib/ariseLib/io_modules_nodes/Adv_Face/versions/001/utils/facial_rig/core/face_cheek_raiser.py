"""Build step CheekRaiser (parita' asFaceCheekRaiser MEL:34654 e
asFaceCheekRaiserFinish MEL:34692) + il finish puro dello step Cheek
(asFaceCheekFinish MEL:34640).

CheekRaiser e' driving puro: apre con asFaceCheekFinish, posa `ctrlCheek` + i
lid inferiori/CheekBone/NoseSide via fit-anim, poi (finish) converte in SDK
(`ds_finish ctrlCheek _RL ty 1`). Gate su `upperLipMainCurve`.

`face_cheek_finish` (asFaceCheekFinish) e' il finish dello step Cheek (15), il
cui corpo di weighting e' mesh-dipendente (shell `components/cheek.py`); il
finish e' pero' puro driving (`ds_finish ctrlCheek _RL tx 1`) e vive qui perche'
CheekRaiser e' il suo unico consumatore nel port.

Divergenze (vedi docs/gap-analysis.md §5f):
- Il MEL calcola `$lowerLidTy` (pointConstraint innerLid/outerLid) ma NON lo usa
  (la fit-anim usa 0.5 hardcoded): codice morto omesso.
- Valore funzionale completo solo su asset reale (i controller di regione
  nascono dagli step mesh).
"""

import maya.cmds as cmds

from .build_utils import as_face_hide_controllers
from .driving_system import face_ds_finish, mirror_connect_ctrls
from .fitting import face_fit_anim, remove_fit_anim_from_ctrl_box


def face_cheek_finish():
    """Converte la posa cheek (tx) in SDK (asFaceCheekFinish). Idempotente
    via FaceBuildInProgress.CheekFinish. Nessuna eccezione."""
    if not cmds.objExists("FaceBuildInProgress"):
        cmds.warning("face_cheek_finish: FaceBuildInProgress not found")
        return
    if cmds.attributeQuery("CheekFinish", node="FaceBuildInProgress", exists=True):
        return
    cmds.addAttr(
        "FaceBuildInProgress",
        longName="CheekFinish",
        attributeType="bool",
        defaultValue=True,
        keyable=False,
    )

    mirror_connect_ctrls(False)
    remove_fit_anim_from_ctrl_box()
    face_ds_finish("ctrlCheek", "_RL", "tx", 1)
    as_face_hide_controllers(True)
    for side in ("_R", "_L"):
        box = "ctrlBoxCheek" + side
        if cmds.objExists(box):
            cmds.setAttr(box + ".v", 1)


def face_cheek_raiser():
    """Posa 'cheek raiser' via fit-anim (asFaceCheekRaiser). Ritorna bool;
    salta (True) senza `upperLipMainCurve`. Nessuna eccezione."""
    if not cmds.objExists("upperLipMainCurve"):
        return True  # skip fedele al MEL

    face_cheek_finish()

    # NB: $lowerLidTy (pointConstraint innerLid/outerLid) omesso — inutilizzato
    # nel MEL (la fit-anim di lowerLid_R.ty usa 0.5 hardcoded).
    as_face_hide_controllers(True)
    mirror_connect_ctrls(True)

    face_fit_anim("ctrlCheek_R.ty", 1)
    face_fit_anim("ctrlCheek_L.ty", 1)
    face_fit_anim("lowerLid_R.ty", 0.5)
    face_fit_anim("lowerLidOuter_R.ty", 0.45)
    face_fit_anim("lowerLidOuter_R.tz", 0.1)
    face_fit_anim("CheekBone_R.ty", 0.1)
    face_fit_anim("NoseSide_R.ty", 0.2)

    cmds.playbackOptions(minTime=0, maxTime=30, animationStartTime=0, animationEndTime=30)
    cmds.currentTime(30)
    cmds.select(clear=True)
    print("// CheekRaiser applied")
    return True


def face_cheek_raiser_finish():
    """Converte la posa cheek-raiser (ty) in SDK (asFaceCheekRaiserFinish).
    Idempotente via FaceBuildInProgress.CheekRaiserFinish. Nessuna eccezione."""
    if not cmds.objExists("FaceBuildInProgress"):
        cmds.warning("face_cheek_raiser_finish: FaceBuildInProgress not found")
        return
    if cmds.attributeQuery("CheekRaiserFinish", node="FaceBuildInProgress", exists=True):
        return
    cmds.addAttr(
        "FaceBuildInProgress",
        longName="CheekRaiserFinish",
        attributeType="bool",
        defaultValue=True,
        keyable=False,
    )

    mirror_connect_ctrls(False)
    remove_fit_anim_from_ctrl_box()
    face_ds_finish("ctrlCheek", "_RL", "ty", 1)
    as_face_hide_controllers(True)
    for side in ("_R", "_L"):
        box = "ctrlBoxCheek" + side
        if cmds.objExists(box):
            cmds.setAttr(box + ".v", 1)

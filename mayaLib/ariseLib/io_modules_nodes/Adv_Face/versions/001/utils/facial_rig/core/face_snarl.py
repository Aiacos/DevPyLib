"""Build step Snarl (parita' asFaceSnarl MEL:35591-35682 e
asFaceSnarlFinish MEL:35684-35710).

Posa "snarl" su ctrlNose.ty: apre con asFaceLipSideFinish (MEL:35601),
misura sulla mesh di quanto devono salire il lato e l'angolo del naso
(verso la palpebra superiore) e posa naso, narici e SmileBulge. Il finish
(chiamato da Tongue, MEL:35728) converte la posa in SDK e aggiunge la posa
su ctrlNose.tx (narice che si allarga).

Divergenze (docs/gap-analysis.md §5o):
- `$upperLipBPos` e' calcolato dal MEL ma usato solo in codice commentato:
  omesso;
- prerequisiti mancanti = warning + False, mai eccezioni.
"""

import maya.cmds as cmds

from .build_utils import as_face_hide_controllers
from .driving_system import face_ds_finish, mirror_connect_ctrls
from .face_lip_side import face_lip_side_finish
from .fit_options import get_fit_option
from .fitting import face_fit_anim, remove_fit_anim_from_ctrl_box


def _snap_to_mesh(geometry, node):
    cmds.delete(cmds.geometryConstraint(geometry, node))


def _measure_nose_poses(geometry):
    """Posizione di posa (nello spazio dei rispettivi offset) del lato e
    dell'angolo del naso: un quarto della strada da NoseSide_R verso la
    palpebra superiore, sulla mesh (MEL:35606-35627)."""
    temp = cmds.createNode("transform", name="TempPos", parent="upperLidMain0_R")
    _snap_to_mesh(geometry, temp)
    temp = cmds.parent(temp, "NoseSide_R")[0]
    cmds.setAttr(temp + ".tx", 0)
    cmds.setAttr(temp + ".tz", 0)
    _snap_to_mesh(geometry, temp)
    temp2 = cmds.createNode("transform", name="TempPos2")
    cmds.pointConstraint(temp, "NoseSide_R", temp2, weight=0.25)
    cmds.delete(cmds.pointConstraint("NoseSide_R", temp2, weight=0.75))
    _snap_to_mesh(geometry, temp2)
    temp2 = cmds.parent(temp2, "NoseSideOffset_R")[0]
    nose_side = cmds.getAttr(temp2 + ".t")[0]
    cmds.delete(cmds.pointConstraint("NoseCorner_R", "NoseSide_R", temp2))
    temp2 = cmds.parent(temp2, "NoseCornerOffset_R")[0]
    nose_corner = cmds.getAttr(temp2 + ".t")[0]
    cmds.delete(temp, temp2)
    return nose_side, nose_corner


def face_snarl() -> bool:
    """Posa "snarl" via fit-anim (asFaceSnarl). Salta (True) senza
    `upperLipMainCurve`."""
    if not cmds.objExists("upperLipMainCurve"):
        return True
    face_lip_side_finish()
    geometry = get_fit_option("Face") or ""
    as_face_hide_controllers(True)
    mirror_connect_ctrls(True)

    nose_side, nose_corner = (0.0, 0.25, 0.0), (0.0, 0.5, 0.0)
    if cmds.objExists("NoseSide_R"):
        needed = (
            geometry,
            "upperLidMain0_R",
            "NoseSideOffset_R",
            "NoseCorner_R",
            "NoseCornerOffset_R",
        )
        missing = [n for n in needed if not n or not cmds.objExists(n)]
        if missing:
            cmds.warning("face_snarl: missing {}".format(", ".join(missing) or "Face"))
            return False
        nose_side, nose_corner = _measure_nose_poses(geometry)

    up = nose_corner[1]
    for plug, value in (
        ("ctrlNose_R.ty", 1),
        ("ctrlNose_L.ty", 1),
        ("NoseCorner_R", 0),
        ("NoseCorner_R.ty", up * 1.0),
        ("NoseSide_R", 0),
        ("NoseSide_R.tx", nose_side[0]),
        ("NoseSide_R.ty", nose_side[1]),
        ("NoseSide_R.tz", nose_side[2]),
        ("NoseUnder_M.ty", up * 0.2),
        ("Nostril_R.ty", up * 0.25),
        ("Nose_M.ty", up * 0.075),
        ("NoseBridge_M.ty", up * 0.04),
        ("SmileBulge_R.ty", up * 0.3),
    ):
        face_fit_anim(plug, value)

    cmds.playbackOptions(minTime=0, maxTime=30, animationStartTime=0, animationEndTime=30)
    cmds.currentTime(30)
    cmds.select(clear=True)
    return True


def face_snarl_finish():
    """Converte lo snarl in SDK su ctrlNose.ty e aggiunge la posa su
    ctrlNose.tx (asFaceSnarlFinish). Idempotente via
    FaceBuildInProgress.SnarlFinish."""
    if not cmds.objExists("FaceBuildInProgress"):
        cmds.warning("face_snarl_finish: FaceBuildInProgress not found")
        return
    if cmds.attributeQuery("SnarlFinish", node="FaceBuildInProgress", exists=True):
        return
    if not cmds.objExists("ctrlNose_R"):
        cmds.warning("face_snarl_finish: ctrlNose_R not found, skipping")
        return
    cmds.addAttr(
        "FaceBuildInProgress",
        longName="SnarlFinish",
        attributeType="bool",
        defaultValue=True,
        keyable=False,
    )
    mirror_connect_ctrls(False)
    remove_fit_anim_from_ctrl_box()
    face_ds_finish("ctrlNose", "_RL", "ty", 1)

    up = 0.0
    if cmds.objExists("SDKNoseCorner_R"):
        cmds.setAttr("ctrlNose_R.ty", 1)
        up = cmds.getAttr("SDKNoseCorner_R.t")[0][1]
        cmds.setAttr("ctrlNose_R.ty", 0)
    for plug, value in (
        ("NoseSide_R.ty", up * -0.05),
        ("NoseCorner_R.tx", up * 0.1),
        ("Nostril_R.tx", up * 0.2),
        ("Nostril_R.tz", up * 0.2),
    ):
        face_fit_anim(plug, value)
    face_ds_finish("ctrlNose", "_RL", "tx", 1)

    as_face_hide_controllers(True)
    for box in ("ctrlBoxNose_R", "ctrlBoxNose_L"):
        if cmds.objExists(box):
            cmds.setAttr(box + ".v", 1)
    cmds.select(clear=True)

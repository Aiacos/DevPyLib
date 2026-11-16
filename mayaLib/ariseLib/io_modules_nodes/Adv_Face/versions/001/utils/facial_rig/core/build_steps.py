"""Stato e sequenza del build a step (parita' asStepBuildPrep MEL
27835, asStepBuildComplete 27872, asFaceResetBuildStep 37363).

La sequenza BUILD_STEPS e' quella della UI MEL (righe 1760-1794):
30 step da Prep a RebuildRestore. L'avanzamento vive in
FaceFitSkeleton.buildStep (attributo long): asStepBuildComplete lo
scrive dopo ogni step, asStepBuildPrep fa da guard di sequenza per il
"Step Builder" manuale (rifiuta gli step saltati, tipicamente dopo un
Undo) e azzera i controlli che l'utente puo' aver mosso per testare.

Divergenze sanzionate: l'azzeramento dei ctrl ignora i transform
lockati (Phonemes/Emotions, dove anche il MEL fallirebbe in silenzio);
asConvertAllSoftModBackToControl non e' ancora a parita' (warning).
"""

import maya.cmds as cmds

from .fit_options import FIT_SKELETON

# sequenza canonica del build MEL (UI 1760-1794)
BUILD_STEPS = (
    "Prep",
    "CtrlBox",
    "EyeBall",
    "EyeLid",
    "EyeBlink",
    "EyeWide",
    "Lip",
    "LipFalloff",
    "FaceCage",
    "CageToSkin",
    "EyeBrow",
    "Squint",
    "SmilePull",
    "FrownPull",
    "Cheek",
    "CheekRaiser",
    "JawWeighing",
    "JawOpen",
    "LipUp",
    "LipDown",
    "LipSide",
    "Snarl",
    "Tongue",
    "Regions",
    "EyeAim",
    "UpMidLo",
    "Phonemes",
    "Emotions",
    "Finish",
    "RebuildRestore",
)


def ensure_build_step_attr():
    """Aggiunge FaceFitSkeleton.buildStep se assente."""
    if not cmds.objExists(FIT_SKELETON):
        return
    if not cmds.attributeQuery("buildStep", node=FIT_SKELETON, exists=True):
        cmds.addAttr(FIT_SKELETON, longName="buildStep", attributeType="long", defaultValue=0)


def step_build_prep(step: int) -> bool:
    """Guard di sequenza + azzeramento ctrl prima di uno step manuale
    (parita' asStepBuildPrep). Ritorna False sullo step saltato."""
    if step == 0:
        return True
    if cmds.objExists(FIT_SKELETON) and cmds.attributeQuery(
        "buildStep", node=FIT_SKELETON, exists=True
    ):
        current = cmds.getAttr(FIT_SKELETON + ".buildStep")
        if current != step - 1:
            print(
                "// Step:{} attempted executed, however previously executed step was:{}".format(
                    step, current
                )
            )
            print("// Possibly caused by a Undo of previous step.")
            cmds.warning("Detected skipped step, please try again")
            return False

    # azzera i ctrl: l'utente puo' aver testato senza tornare a zero
    auto_key = cmds.autoKeyframe(query=True, state=True)
    if auto_key:
        cmds.autoKeyframe(state=False)
    shapes = []
    if cmds.objExists("OnFacecontrols"):
        shapes += cmds.listRelatives("OnFacecontrols", allDescendents=True, type="nurbsCurve") or []
    if cmds.objExists("ctrlBox"):  # i ctrl di ctrlBox2 hanno valori
        shapes += cmds.listRelatives("ctrlBox", allDescendents=True, type="nurbsCurve") or []
    for shape in shapes:
        ctrl = (cmds.listRelatives(shape, parent=True) or [""])[0]
        if ctrl.startswith("ctrlBox"):
            continue
        try:
            cmds.xform(
                ctrl, objectSpace=True, translation=(0, 0, 0), rotation=(0, 0, 0), scale=(1, 1, 1)
            )
        except RuntimeError:
            pass  # ctrl con transform lockati (Phonemes/Emotions)
    if auto_key:
        cmds.autoKeyframe(state=True)
    return True


def step_build_complete(step: int):
    """Registra il completamento di uno step (parita'
    asStepBuildComplete)."""
    if step == 0:
        return
    if cmds.ls("convertedSoftMod_*", type="softMod"):
        cmds.warning(
            "convertedSoftMod_* found: "
            "asConvertAllSoftModBackToControl is not ported "
            "yet, complete the softMod-weighting manually."
        )
    if cmds.objExists(FIT_SKELETON):
        ensure_build_step_attr()
        cmds.setAttr(FIT_SKELETON + ".buildStep", step)
    print("// Face step:{} complete.".format(step))


def reset_build_step():
    """Toggle dello stato di build (parita' asFaceResetBuildStep):
    0 -> ultimo step prima di RebuildRestore (abilita il Restore
    manuale), altrimenti -> 0."""
    if not cmds.objExists(FIT_SKELETON):
        return
    ensure_build_step_attr()
    new_step = 0
    if cmds.getAttr(FIT_SKELETON + ".buildStep") == 0:
        new_step = len(BUILD_STEPS) - 1  # Finish
    cmds.setAttr(FIT_SKELETON + ".buildStep", new_step)

"""Build step Emotions (parita' asFaceEmotions MEL:36525-36677).

Step di puro driving: aggiunge a `ctrlEmotions_M` un attributo 0-10 per
ognuna delle 7 emozioni e lo collega (asDsSdk) agli slider del board
(tramite i loro blendWeighted `bw<ctrl>_<attr>.input`) e ad alcuni gruppi
SDK dei controller on-face.

Divergenze (docs/gap-analysis.md §5q):
- `setAttr driver 10; refresh; setAttr driver 0` dopo ogni emozione
  (MEL:36567...) e' un'anteprima nel viewport: non replicata;
- i canali guidati assenti sono saltati con un warning unico (il MEL li
  controlla solo per Nostril e lowerLidOuter); prerequisiti mancanti =
  warning + False.
"""

import maya.cmds as cmds

from .build_utils import as_face_hide_controllers
from .driving_system import ds_sdk, ensure_output_blend_weighted
from .fit_options import FIT_SKELETON

EMOTIONS = ("happy", "angry", "sad", "surprise", "fear", "disgust", "contempt")
_CTRL = "ctrlEmotions_M"

# emozione -> (canali per lato, canali centrali); "{s}" e' il lato
_POSES = {
    "happy": (
        (
            ("SDKEyeBrowOuter{s}.ty", -0.1),
            ("bwctrlMouthCorner{s}_translateX.input", 1),
            ("bwctrlMouthCorner{s}_translateY.input", 1),
            ("bwctrlEye{s}_blink.input", 3),
        ),
        (
            ("SDKupperLip_M.ty", 0.1),
            ("SDKlowerLip_M.ty", 0.1),
            ("SDKNoseRegion_M.tz", -0.1),
            ("SDKNoseRegion_M.rx", 5),
        ),
    ),
    "angry": (
        (
            ("bwctrlBrow{s}_translateX.input", -0.5),
            ("bwctrlBrow{s}_translateY.input", -0.5),
            ("bwctrlBrow{s}_squeeze.input", 8),
            ("bwctrlMouthCorner{s}_translateX.input", -0.5),
            ("bwctrlEye{s}_blink.input", 3),
            ("bwctrlEye{s}_squint.input", 3),
            ("SDKNostril{s}.tx", 0.2),
        ),
        (("bwctrlLips_M_upperSqueeze.input", 5), ("bwctrlLips_M_lowerSqueeze.input", 5)),
    ),
    "sad": (
        (
            ("bwctrlBrow{s}_translateX.input", 0.5),
            ("bwctrlBrow{s}_translateY.input", -0.5),
            ("bwctrlBrow{s}_squeeze.input", 5),
            ("bwctrlMouthCorner{s}_translateX.input", 0.5),
            ("bwctrlMouthCorner{s}_translateY.input", -0.5),
            ("bwctrlEye{s}_blink.input", 3),
            ("bwctrlEye{s}_squint.input", 3),
        ),
        (("bwctrlLips_M_upperSqueeze.input", 3), ("bwctrlLips_M_lowerSqueeze.input", 3)),
    ),
    "surprise": (
        (
            ("bwctrlBrow{s}_translateY.input", 0.75),
            ("bwctrlEye{s}_wide.input", 3),
            ("bwctrlEye{s}_squint.input", -1),
        ),
        (("bwctrlMouth_M_translateY.input", -1),),
    ),
    "fear": (
        (
            ("bwctrlBrow{s}_translateX.input", 1.0),
            ("bwctrlBrow{s}_squeeze.input", 7),
            ("bwctrlMouthCorner{s}_translateX.input", 0.4),
            ("bwctrlMouthCorner{s}_translateY.input", -0.25),
            ("SDKNoseCorner{s}.ty", -0.1),
            ("SDKlowerLidOuter{s}.ty", -0.1),
            ("SDKupperLid{s}.ty", 0.1),
            ("SDKlowerLid{s}.ty", -0.1),
        ),
        (
            ("bwctrlMouth_M_translateY.input", -0.75),
            ("bwctrlLips_M_upperSqueeze.input", 3),
            ("bwctrlLips_M_lowerSqueeze.input", 3),
        ),
    ),
    "disgust": (
        (
            ("bwctrlBrow{s}_squeeze.input", 5),
            ("bwctrlEye{s}_squint.input", 3),
            ("bwctrlNose{s}_translateY.input", 0.75),
            ("bwctrlCheek{s}_translateY.input", 1),
            ("bwctrlMouthCorner{s}_translateX.input", 0.25),
            ("bwctrlMouthCorner{s}_translateY.input", -0.25),
        ),
        (("SDKlowerLip_M.ty", -0.5),),
    ),
    "contempt": (
        (
            ("bwctrlMouthCorner{s}_translateX.input", 0.6),
            ("bwctrlMouthCorner{s}_translateY.input", 0.3),
        ),
        (),
    ),
}


def face_emotions() -> bool:
    """Attributi delle emozioni su ctrlEmotions_M (asFaceEmotions). Salta
    (True) con l'opzione Emotions spenta o senza `upperLipMainCurve`."""
    if cmds.objExists(FIT_SKELETON) and cmds.attributeQuery(
        "Emotions", node=FIT_SKELETON, exists=True
    ):
        if not cmds.getAttr(FIT_SKELETON + ".Emotions"):
            return True
    if not cmds.objExists("upperLipMainCurve"):
        return True
    missing = [n for n in (_CTRL, "ctrlBoxEmotions_M", "ControlsSetup") if not cmds.objExists(n)]
    if missing:
        cmds.warning("face_emotions: missing {}".format(", ".join(missing)))
        return False
    if cmds.attributeQuery(EMOTIONS[0], node=_CTRL, exists=True):
        cmds.warning("face_emotions: emotions already built")
        return False

    as_face_hide_controllers(True)
    cmds.setAttr("ctrlBoxEmotions_M.v", 1)
    for emotion in EMOTIONS:
        cmds.addAttr(
            _CTRL,
            keyable=True,
            longName=emotion,
            attributeType="double",
            softMinValue=0,
            hasSoftMinValue=True,
            softMaxValue=10,
            hasSoftMaxValue=True,
        )
        ensure_output_blend_weighted("{}.{}".format(_CTRL, emotion))

    skipped = []
    for emotion in EMOTIONS:
        per_side, central = _POSES[emotion]
        channels = [(c.format(s=side), v) for side in ("_R", "_L") for c, v in per_side]
        for driven, value in channels + list(central):
            if not cmds.objExists(driven):
                skipped.append(driven)
                continue
            ds_sdk("{}.{}".format(_CTRL, emotion), driven, 10, value)
    if skipped:
        cmds.warning(
            "face_emotions: skipped missing channels: {}".format(", ".join(sorted(set(skipped))))
        )
    cmds.select(clear=True)
    return True

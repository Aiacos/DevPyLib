"""Sync UI<->FaceFitSkeleton ed enable policy.

- initialize_pre_options: crea su FaceFitSkeleton tutti gli attributi del
  frame Pre coi default (parita' del ramo write di asFaceUpdateInfo,
  MEL AdvancedSkeleton.mel:42626-42645; il motore e' fit_options.ensure_option_attr).
- control_enabled: enable policy 'mostra-ma-disabilita' per i controlli le
  cui feature di build non sono ancora portate in Python
  (parita' di intento con asUpdateButtonEnables, MEL:50434).
"""

from ..fit_options import ensure_option_attr

# Opzioni del frame Pre (ordine MEL), escluse le ausiliarie di build.
PRE_OPTIONS = (
    "Mask",
    "Face",
    "AllHead",
    "RightEye",
    "LeftEye",
    "UpperTeeth",
    "LowerTeeth",
    "Tongue",
    "Eyebrow",
    "Eyelash",
    "Extras",
    "HeadJoint",
    "SkinCluster",
    "RigType",
    "Include",
    "LipCtrls",
    "NonSym",
    "NonSymSide",
    "SimplerEyeLid",
    "EyeBase",
    "EyeSocket",
    "Cyclops",
    "GameEngine",
    "MultiSkinClusters",
    "LongSnout",
    "Phonemes",
    "Emotions",
    "ARKit",
    "SnapChat",
    "RobloxHead",
    "UseMaxInf",
    "MaxInf",
    "LegacyFaceJointOrient",
)

# Controlli con backend Python gia' portato: restano attivi. Gli altri sono
# visibili ma disabilitati (decisione utente). Aggiornare man mano che i
# componenti di build raggiungono la parita'.
_PORTED = {
    "Mask",
    "Face",
    "AllHead",
    "RightEye",
    "LeftEye",
    "UpperTeeth",
    "LowerTeeth",
    "Tongue",
    "Eyebrow",
    "Eyelash",
    "Extras",
    "HeadJoint",
    "SkinCluster",
    "RigType",
    "Include",
    "LipCtrls",
    "NonSym",
}


def initialize_pre_options():
    """Crea gli attributi del frame Pre con i default (write iniziale)."""
    for name in PRE_OPTIONS:
        ensure_option_attr(name)


def control_enabled(option_name):
    """True se il controllo deve essere abilitato (backend disponibile)."""
    return option_name in _PORTED

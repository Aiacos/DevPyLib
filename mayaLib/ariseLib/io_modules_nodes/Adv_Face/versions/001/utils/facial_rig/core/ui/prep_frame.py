"""Frame 'Pre' della UI asFace (parita' MEL AdvancedSkeleton.mel:1430-1564).

Ordine, controlli, callback e immagini di help replicano il MEL. La logica
e' delegata a inputs/sync/model_check; qui si costruisce solo il layout.

Divergenze intenzionali:
- I controlli UseMaxInf, MaxInf, LegacyFaceJointOrient sono mostrati ma
  disabilitati (backend non ancora portato); il MEL li abilitava sempre.
- Il bottone AutoFit e' disabilitato (asNameMatcherAutoFaceFitting non portato).
"""

import maya.cmds as cmds

from ..fit_options import get_fit_option, set_fit_option
from . import inputs as _inputs
from . import sync as _sync
from .model_check import model_check
from .widgets import checkbox_row, help_button, input_row, option_row

# (label, option_name, help_region) nell'ordine MEL del loop input (1433).
_INPUTS = [
    ("Mask", "Mask", "facePreMask"),
    ("Face", "Face", "facePreFace"),
    ("All Head", "AllHead", "facePreAllHead"),
    ("Right Eye", "RightEye", "facePreRightEye"),
    ("Left Eye", "LeftEye", "facePreLeftEye"),
    ("Upper Teeth", "UpperTeeth", "facePreUpperTeeth"),
    ("Lower Teeth", "LowerTeeth", "facePreLowerTeeth"),
    ("Tongue", "Tongue", "facePreTongue"),
    ("Eyebrow", "Eyebrow", "facePreEyebrow"),
    ("Eyelash", "Eyelash", "facePreEyelash"),
    ("Extras", "Extras", "facePreExtras"),
]

# (label, option_name, help_region, items) — optionMenu nell'ordine MEL.
_OPTION_MENUS = [
    ("rig-type:", "RigType", "facePreRigType", ["Joints", "BlendShapes", "Mixed"]),
    (
        "include :",
        "Include",
        "facePreInclude",
        ["Complete", "Skip Above Eyes", "Skip Below Eyes", "Skip Above+Below Eyes"],
    ),
    ("lip-ctrls :", "LipCtrls", "facePreLipCtrls", ["12", "16", "20", "24"]),
]

# (label, option_name, help_region) — checkbox nell'ordine MEL (1483-1534).
_CHECKBOXES = [
    ("non symmetrical", "NonSym", "facePreNonSym"),
    ("simpler eyeLid", "SimplerEyeLid", "asSimplerEyeLid"),
    ("eye base", "EyeBase", "asEyeBase"),
    ("eye socket", "EyeSocket", "asEyeSocket"),
    ("cyclops", "Cyclops", "faceCyclops"),
    ("game engine", "GameEngine", "facePreGameEngine"),
    ("multi skinclusters", "MultiSkinClusters", "faceMultiSkinClusters"),
    ("long snout", "LongSnout", "faceLongSnout"),
    ("phonemes", "Phonemes", "asPhonemes"),
    ("emotions", "Emotions", "asEmotions"),
    ("apple arkit", "ARKit", "facePreARKit"),
    ("snap chat", "SnapChat", "facePreSnapChat"),
    ("roblox head", "RobloxHead", "faceRobloxHead"),
]


def _maya_supports_multi_skin():
    """multi skinclusters richiede Maya >= 2024 (MEL:1508)."""
    try:
        return float(cmds.about(version=True).split()[0]) >= 2024
    except (ValueError, AttributeError):
        return True


def _enabled(option_name):
    """Enable policy: backend portato E (se MultiSkinClusters) Maya>=2024."""
    enabled = _sync.control_enabled(option_name)
    # MultiSkinClusters: il guard versione (MEL:1508) diventa attivo quando
    # l'opzione entrera' in _PORTED; ora control_enabled e' gia' False.
    if option_name == "MultiSkinClusters":
        enabled = enabled and _maya_supports_multi_skin()
    return enabled


def _on_option_change(menu, option_name):
    set_fit_option(option_name, cmds.optionMenu(menu, query=True, value=True))


def _on_checkbox_change(box, option_name):
    set_fit_option(option_name, cmds.checkBox(box, query=True, value=True))


def _build_advanced_block(fitting):
    """Replica MEL:1537-1563 — sezione 'advanced' collassabile.

    Struttura layout (fedele al MEL):
      rowLayout (checkbox 'advanced' + help_button)
      textField NonSymSide (hidden, MEL:1541)
      separator
      columnLayout adv (manage=False — visibile solo se checkbox ON)
        columnLayout gameEngineInner
          checkBox UseMaxInf
          optionMenu MaxInf (no help_button nel MEL:1546)
          setParent..
        separator
        text
        text
        separator
        rowLayout (Choose Head Joint button + HeadJoint textField)
          setParent..
        text SkinCluster
        textField SkinCluster (read-only, display only)
        checkBox LegacyFaceJointOrient
        text
        button AutoFit (disabled)
      setParent.. (chiude columnLayout adv)
    """
    # Riga checkbox "advanced" + help (MEL:1537-1540).
    cmds.rowLayout(numberOfColumns=2, columnWidth2=(222, 15))
    adv_box = cmds.checkBox(label="advanced")
    help_button("facePreAdvanced")
    cmds.setParent("..")

    # textField NonSymSide nascosto (MEL:1541 — non nel loop principale).
    cmds.textField(manage=False)

    cmds.separator(height=10)

    # columnLayout avanzato, nascosto di default (MEL:1543).
    adv = cmds.columnLayout(adjustableColumn=True, manage=False)

    # Callback toggle: onCommand/offCommand editano manage del columnLayout.
    cmds.checkBox(
        adv_box,
        edit=True,
        onCommand=lambda *_: cmds.columnLayout(adv, edit=True, manage=True),
        offCommand=lambda *_: cmds.columnLayout(adv, edit=True, manage=False),
    )

    # Inner columnLayout per UseMaxInf + MaxInf (MEL:1544-1549).
    cmds.columnLayout(
        adjustableColumn=True, manage=False
    )  # MEL:1544 -m 0 (nascosto come il parent)
    cmds.checkBox(
        label="use max influences:", enable=_enabled("UseMaxInf"), changeCommand=lambda *_: None
    )  # non portato
    cmds.optionMenu(
        label="max influences:", enable=_enabled("MaxInf")
    )  # MaxInf: non ancora portato (read-only)
    for item in ["4", "8"]:
        cmds.menuItem(label=item)
    cmds.setParent("..")  # chiude columnLayout gameEngineInner

    cmds.separator(height=15)
    cmds.text(label="For creating FaceSetup,")
    cmds.text(label="without AdvancedSkeleton body rig:")
    cmds.separator(height=5)

    # HeadJoint row (MEL:1554-1557) — il textField e' dentro il rowLayout.
    cmds.rowLayout(numberOfColumns=2, columnWidth2=(120, 100))
    cmds.button(
        width=120,
        label="Choose Head Joint",
        enable=_enabled("HeadJoint"),
        command=lambda *_: _inputs.choose_input("HeadJoint", fitting),
    )
    head_field = cmds.textField(width=100, editable=False)
    cmds.setParent("..")  # chiude rowLayout HeadJoint

    # Popola il campo con il valore corrente (MEL:1556 -tx "Head_M").
    current_head = get_fit_option("HeadJoint") or ""
    if current_head:
        cmds.textField(head_field, edit=True, text=current_head)

    # SkinCluster display (MEL:1558-1559) — read-only, solo visualizzazione.
    cmds.text(label="SkinCluster found on Face Geo:")
    skin_val = get_fit_option("SkinCluster") or ""
    cmds.textField(width=150, editable=False, text=skin_val)

    # Legacy FaceJoint Orient (MEL:1561).
    cmds.rowLayout(numberOfColumns=2, columnWidth2=(222, 15))
    leg_box = cmds.checkBox(
        label="Legacy FaceJoint Orient",
        enable=_enabled("LegacyFaceJointOrient"),
        value=bool(get_fit_option("LegacyFaceJointOrient")),
        changeCommand=lambda *_: _on_checkbox_change(leg_box, "LegacyFaceJointOrient"),
    )
    help_button("facePreAdvanced")
    cmds.setParent("..")  # chiude rowLayout Legacy

    # CharacterCreator / MetaHuman (MEL:1562-1563).
    cmds.text(label="For CharacterCreator or MetaHuman:")
    cmds.button(label="AutoFit", enable=False, annotation="non ancora portato")

    cmds.setParent("..")  # chiude columnLayout adv


def build_prep_frame(fitting):
    """Costruisce il frame Pre; inizializza le opzioni su FaceFitSkeleton.

    Parita' MEL AdvancedSkeleton.mel:1430-1564.

    Args:
        fitting: istanza FacialFitting.

    Returns:
        Il nome del frameLayout creato.
    """
    # Inizializza opzioni PRIMA di costruire la UI (garantisce assert headless).
    if cmds.objExists(fitting.fit_skeleton_grp):
        _sync.initialize_pre_options()

    frame = cmds.frameLayout(label=" Pre", collapsable=True, collapse=True)
    cmds.columnLayout(adjustableColumn=True)

    cmds.separator(height=7, style="none")

    # Sezione Polygons + Objects + Optional con i relativi input_row.
    cmds.text(label="Polygons:", align="left")
    for label, opt, region in _INPUTS:
        if opt == "Face":
            cmds.separator(height=7, style="none")
            cmds.text(label="Objects:", align="left")
        if opt == "UpperTeeth":
            cmds.separator(height=7, style="none")
            cmds.text(label="Optional:", align="left")
        input_row(
            label,
            on_choose=lambda o=opt: _inputs.choose_input(o, fitting),
            on_reselect=lambda o=opt: _inputs.reselect(o),
            region=region,
            enabled=_enabled(opt),
        )

    cmds.separator(height=10)
    cmds.rowLayout(numberOfColumns=2, height=20)
    cmds.separator(width=80, style="none")
    cmds.button(label="Model Check", command=lambda *_: model_check())
    cmds.setParent("..")  # chiude rowLayout Model Check
    cmds.separator(height=10)

    # optionMenu rows (MEL:1455-1481).
    for label, opt, region, items in _OPTION_MENUS:
        option_row(
            label,
            items,
            region,
            on_change=lambda menu, o=opt: _on_option_change(menu, o),
            default_index=0,
            enabled=_enabled(opt),
        )

    # checkbox rows (MEL:1482-1535).
    for label, opt, region in _CHECKBOXES:
        checkbox_row(
            label,
            region,
            on_change=lambda box, o=opt: _on_checkbox_change(box, o),
            value=bool(get_fit_option(opt)),
            enabled=_enabled(opt),
        )

    # Sezione avanzata (MEL:1536-1563).
    cmds.separator(height=5, style="none")
    _build_advanced_block(fitting)

    cmds.setParent("..")  # chiude columnLayout interno del frame
    cmds.setParent("..")  # chiude frameLayout
    return frame

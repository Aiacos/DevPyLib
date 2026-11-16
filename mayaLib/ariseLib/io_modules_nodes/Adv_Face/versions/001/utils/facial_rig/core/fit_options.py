"""Contratto opzioni di FaceFitSkeleton (parita' asFaceUpdateInfo).

In MEL ogni widget asFace<Nome><Tipo> della tab Face persiste un attributo
omonimo su FaceFitSkeleton (string per textField, bool per checkBox, enum
per optionMenu), aggiunto on-demand; un attributo assente vale il default.
Qui la tabella FIT_OPTIONS e' la fonte di verita': la persistenza scena e
la futura UI PySide (Fase 4) derivano entrambe da qui, mai dalla view.

I nomi attributo, i tipi e le stringhe enum sono un contratto di
interoperabilita' con i tool AdvancedSkeleton: non rinominarli.
"""

from dataclasses import dataclass
from typing import Tuple, Union

import maya.cmds as cmds

FIT_SKELETON = "FaceFitSkeleton"


@dataclass(frozen=True)
class FitOption:
    name: str  # nome attributo (esatto MEL)
    attr_type: str  # "string" | "bool" | "enum" | "long"
    default: Union[str, bool, int]  # per enum: indice di default
    enum_values: Tuple[str, ...] = ()  # solo per attr_type == "enum"

    def __post_init__(self):
        assert self.attr_type in ("string", "bool", "enum", "long"), (
            "Invalid attr_type for {}: {}".format(self.name, self.attr_type)
        )
        if self.attr_type == "enum":
            assert self.enum_values, "Enum option {} has no values".format(self.name)


FIT_OPTIONS = {
    opt.name: opt
    for opt in [
        # Input geometrie (sezione "Pre" della tab Face)
        FitOption("Mask", "string", ""),
        FitOption("Face", "string", ""),
        FitOption("AllHead", "string", ""),
        FitOption("RightEye", "string", ""),
        FitOption("LeftEye", "string", ""),
        FitOption("UpperTeeth", "string", ""),
        FitOption("LowerTeeth", "string", ""),
        FitOption("Tongue", "string", ""),
        FitOption("Eyebrow", "string", ""),
        FitOption("Eyelash", "string", ""),
        FitOption("Extras", "string", ""),
        FitOption("HeadJoint", "string", "Head_M"),
        FitOption("SkinCluster", "string", ""),
        # Opzioni di rig
        FitOption("RigType", "enum", 0, ("Joints", "BlendShapes", "Mixed")),
        FitOption(
            "Include",
            "enum",
            0,
            ("Complete", "Skip Above Eyes", "Skip Below Eyes", "Skip Above+Below Eyes"),
        ),
        FitOption("LipCtrls", "enum", 0, ("12", "16", "20", "24")),
        FitOption("NonSym", "bool", False),
        FitOption("NonSymSide", "string", ""),
        FitOption("SimplerEyeLid", "bool", False),
        FitOption("EyeBase", "bool", False),
        FitOption("EyeSocket", "bool", False),
        FitOption("Cyclops", "bool", False),
        FitOption("GameEngine", "bool", False),
        FitOption("MultiSkinClusters", "bool", False),
        FitOption("LongSnout", "bool", False),
        FitOption("Phonemes", "bool", True),
        FitOption("Emotions", "bool", True),
        FitOption("ARKit", "bool", False),
        FitOption("SnapChat", "bool", False),
        FitOption("RobloxHead", "bool", False),
        FitOption("UseMaxInf", "bool", False),
        FitOption("MaxInf", "enum", 0, ("4", "8")),
        FitOption("LegacyFaceJointOrient", "bool", False),
        # Ausiliari di build (asFaceUpdateInfo li aggiunge se assenti)
        FitOption("vtxsFromLipToNose", "long", 3),
        FitOption("preRebuildScript", "string", ""),
        FitOption("postRebuildScript", "string", ""),
    ]
}

# Come le checkbox MEL: attivarne una spegne l'altra.
_MUTUALLY_EXCLUSIVE = {"ARKit": "SnapChat", "SnapChat": "ARKit"}


def ensure_option_attr(name: str, node: str = FIT_SKELETON) -> bool:
    """Aggiunge l'attributo opzione al nodo se assente (come asFaceUpdateInfo)."""
    if name not in FIT_OPTIONS:
        cmds.warning("Unknown fit option: {}".format(name))
        return False
    if not cmds.objExists(node):
        cmds.warning("{} not found".format(node))
        return False
    if cmds.attributeQuery(name, node=node, exists=True):
        return True
    opt = FIT_OPTIONS[name]
    plug = "{}.{}".format(node, name)
    if opt.attr_type == "string":
        cmds.addAttr(node, longName=name, dataType="string")
        if opt.default:
            cmds.setAttr(plug, opt.default, type="string")
    elif opt.attr_type == "bool":
        cmds.addAttr(node, longName=name, attributeType="bool", defaultValue=int(opt.default))
        cmds.setAttr(plug, int(opt.default))
    elif opt.attr_type == "enum":
        cmds.addAttr(
            node,
            longName=name,
            attributeType="enum",
            enumName=":".join(opt.enum_values),
            defaultValue=opt.default,
        )
    elif opt.attr_type == "long":
        cmds.addAttr(node, longName=name, attributeType="long", defaultValue=opt.default)
        cmds.setAttr(plug, opt.default)
    return True


def set_fit_option(name: str, value, node: str = FIT_SKELETON) -> bool:
    """Scrive un'opzione su FaceFitSkeleton, creando l'attributo se serve."""
    opt = FIT_OPTIONS.get(name)
    if opt is None:
        cmds.warning("Unknown fit option: {}".format(name))
        return False
    if opt.attr_type == "enum":
        if isinstance(value, str):
            if value not in opt.enum_values:
                cmds.warning("Invalid value for {}: {}".format(name, value))
                return False
            value = opt.enum_values.index(value)
        elif not 0 <= value < len(opt.enum_values):
            cmds.warning("Invalid value for {}: {}".format(name, value))
            return False
    if not ensure_option_attr(name, node):
        return False
    plug = "{}.{}".format(node, name)
    if opt.attr_type == "string":
        cmds.setAttr(plug, value, type="string")
    else:
        cmds.setAttr(plug, value)
    other = _MUTUALLY_EXCLUSIVE.get(name)
    if other and bool(value):
        if ensure_option_attr(other, node):
            cmds.setAttr("{}.{}".format(node, other), 0)
    return True


def get_fit_option(name: str, node: str = FIT_SKELETON):
    """Legge un'opzione; attributo assente => default (convenzione MEL)."""
    opt = FIT_OPTIONS.get(name)
    if opt is None:
        cmds.warning("Unknown fit option: {}".format(name))
        return None
    exists = cmds.objExists(node) and cmds.attributeQuery(name, node=node, exists=True)
    if opt.attr_type == "enum":
        index = cmds.getAttr("{}.{}".format(node, name)) if exists else opt.default
        if not 0 <= index < len(opt.enum_values):
            cmds.warning("Out-of-range enum value for {}: {}".format(name, index))
            index = opt.default
        return opt.enum_values[index]
    if not exists:
        return opt.default
    value = cmds.getAttr("{}.{}".format(node, name))
    if opt.attr_type == "string":
        return value or ""
    if opt.attr_type == "bool":
        return bool(value)
    return value


def get_left_suffix(node: str = FIT_SKELETON) -> str:
    """ "Left" se il fitting corrente lavora sul lato sinistro, altrimenti "".

    Replica la convenzione leftSuffix letta da NonSymSide in tutte le proc
    MEL di fitting.
    """
    return "Left" if get_fit_option("NonSymSide", node) == "Left" else ""

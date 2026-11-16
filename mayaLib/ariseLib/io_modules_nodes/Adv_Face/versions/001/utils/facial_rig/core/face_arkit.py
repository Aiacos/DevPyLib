"""Controller ARKit / SnapChat (parita' asConnectARKit MEL:13921-14200, nel
modo "create ctrl" con cui asFaceFinish lo chiama, MEL:36819-36825).

Con l'opzione ARKit (o SnapChat) il CtrlBox crea `ctrlARKit_M`
(`ctrlSnapChat_M`); qui il controller riceve un attributo 0-10 per ognuna
delle 52 shape ARKit (49 + 2 per SnapChat) e ogni attributo e' collegato
(asDsSdk) agli slider del board e ad alcuni gruppi SDK del rig. Un'app di
face capture, o l'animatore, guida cosi' il rig a joint con i nomi ARKit.

Divergenze (docs/gap-analysis.md §5s):
- portato solo il modo "create ctrl". I modi che partono da un blendShape
  scelto nella UI ("connect to ctrl" e "quick connect"), Audio2Face,
  disconnect e bake non sono portati;
- i canali guidati assenti sono saltati con un unico warning (asDsSdk nel
  MEL li salta uno a uno);
- prerequisiti mancanti = warning + False, mai eccezioni.
"""

import maya.cmds as cmds

from .driving_system import ds_sdk, ensure_output_blend_weighted
from .fit_options import get_fit_option

# https://developer.apple.com/documentation/arkit/arfaceanchor/blendshapelocation
ARKIT_SHAPES = (
    "eyeBlinkLeft", "eyeLookDownLeft", "eyeLookInLeft", "eyeLookOutLeft", "eyeLookUpLeft",
    "eyeSquintLeft", "eyeWideLeft", "eyeBlinkRight", "eyeLookDownRight", "eyeLookInRight",
    "eyeLookOutRight", "eyeLookUpRight", "eyeSquintRight", "eyeWideRight", "jawForward",
    "jawLeft", "jawRight", "jawOpen", "mouthClose", "mouthFunnel", "mouthPucker", "mouthLeft",
    "mouthRight", "mouthSmileLeft", "mouthSmileRight", "mouthFrownLeft", "mouthFrownRight",
    "mouthDimpleLeft", "mouthDimpleRight", "mouthStretchLeft", "mouthStretchRight",
    "mouthRollLower", "mouthRollUpper", "mouthShrugLower", "mouthShrugUpper", "mouthPressLeft",
    "mouthPressRight", "mouthLowerDownLeft", "mouthLowerDownRight", "mouthUpperUpLeft",
    "mouthUpperUpRight", "browDownLeft", "browDownRight", "browInnerUp", "browOuterUpLeft",
    "browOuterUpRight", "cheekPuff", "cheekSquintLeft", "cheekSquintRight", "noseSneerLeft",
    "noseSneerRight", "tongueOut",
)  # fmt: skip
# https://docs.snap.com/api/lens-studio/Classes/OtherClasses/#Expressions
SNAPCHAT_SHAPES = (
    "EyeBlinkLeft", "EyeDownLeft", "EyeInLeft", "EyeOutLeft", "EyeUpLeft", "EyeSquintLeft",
    "EyeOpenLeft", "EyeBlinkRight", "EyeDownRight", "EyeInRight", "EyeOutRight", "EyeUpRight",
    "EyeSquintRight", "EyeOpenRight", "JawForward", "JawLeft", "JawRight", "JawOpen",
    "MouthClose", "LipsFunnel", "LipsPucker", "MouthLeft", "MouthRight", "MouthSmileLeft",
    "MouthSmileRight", "MouthFrownLeft", "MouthFrownRight", "MouthDimpleLeft",
    "MouthDimpleRight", "MouthStretchLeft", "MouthStretchRight", "LowerLipClose",
    "UpperLipClose", "LowerLipRaise", "UpperLipRaise", "LowerLipDownLeft", "LowerLipDownRight",
    "UpperLipUpLeft", "UpperLipUpRight", "BrowsDownLeft", "BrowsDownRight", "BrowsUpCenter",
    "BrowsUpLeft", "BrowsUpRight", "Puff", "CheekSquintLeft", "CheekSquintRight", "SneerLeft",
    "SneerRight", "MouthUpLeft", "MouthUpRight",
)  # fmt: skip
_NOT_IN_SNAPCHAT = ("mouthPressLeft", "mouthPressRight", "tongueOut")

# shape per lato: prefisso ARKit -> [(canale, valore)]. "{s}" e' il lato del
# rig (_R/_L); un valore callable riceve b (+1 destra, -1 sinistra).
_SIDED = {
    "eyeBlink": (("ctrlEye{s}.blink", 10),),
    "eyeLookDown": (("ctrlEye{s}.ty", -1),),
    "eyeLookIn": (("ctrlEye{s}.tx", lambda b: 1 * b),),
    "eyeLookOut": (("ctrlEye{s}.tx", lambda b: -1 * b),),
    "eyeLookUp": (("ctrlEye{s}.ty", 1),),
    "eyeSquint": (("ctrlEye{s}.squint", 10),),
    "eyeWide": (("ctrlEye{s}.wide", 10),),
    "mouthDimple": (("ctrlMouthCorner{s}.tx", 0.3),),
    "browOuterUp": (("ctrlBrow{s}.outerUpDown", 7.5),),
    "noseSneer": (("ctrlNose{s}.ty", 0.5),),
    "mouthSmile": (("ctrlMouthCorner{s}.tx", 0.75), ("ctrlMouthCorner{s}.ty", 0.75)),
    "mouthFrown": (("ctrlMouthCorner{s}.tx", 0.25), ("ctrlMouthCorner{s}.ty", -0.25)),
    "mouthStretch": (("ctrlMouthCorner{s}.tx", 0.5), ("ctrlMouthCorner{s}.ty", -0.5)),
    "mouthPress": (("ctrlMouthCorner{s}.ty", 0.25),),
    "mouthLowerDown": (("SDKlowerLipA{s}.ty", -0.4), ("SDKlowerLip_M.ty", -0.3)),
    "mouthUpperUp": (("SDKupperLipA{s}.ty", 0.4), ("SDKupperLip_M.ty", 0.3)),
    "browDown": (("ctrlBrow{s}.ty", -0.75), ("ctrlBrow{s}.squeeze", 7.5)),
    "cheekSquint": (("ctrlEye{s}.squint", 3), ("SDKCheek{s}.ty", 0.1)),
}
# shape laterali che guidano un controller centrale
_SIDED_TO_CENTER = {"mouthRight": (("ctrlLips_M.tx", -1),), "mouthLeft": (("ctrlLips_M.tx", 1),)}
# il MEL esegue questo blocco a ogni giro del ciclo sui lati (MEL:14095):
# sugli slider del board ogni chiamata aggiunge un contributo, quindi lo
# squeeze vale il doppio. Replicato.
_MOUTH_PRESS_COMMON = (
    ("ctrlLips_M.upperSqueeze", 1.5),
    ("ctrlLips_M.lowerSqueeze", 1.5),
    ("SDKLipRegion_M.ty", 0.1),
)
_CENTER = {
    "jawOpen": (("ctrlMouth_M.ty", -1),),
    "mouthPucker": (("ctrlLips_M.upperPucker", 10), ("ctrlLips_M.lowerPucker", 10)),
    "mouthFunnel": (
        ("ctrlLips_M.upperPucker", 10),
        ("ctrlLips_M.lowerPucker", 10),
        ("SDKupperLip_M.ty", 0.3),
        ("SDKlowerLip_M.ty", -0.3),
    ),
    "mouthRollUpper": (("ctrlLips_M.upperRoll", -5),),
    "mouthRollLower": (("ctrlLips_M.lowerRoll", -5),),
    "mouthShrugUpper": (("SDKupperLip_M.ty", 0.3),),
    "mouthShrugLower": (("SDKlowerLip_M.ty", 0.3),),
    "browInnerUp": (("ctrlBrow_R.tx", 1), ("ctrlBrow_L.tx", 1)),
    "cheekPuff": (("ctrlCheek_R.tx", 0.4), ("ctrlCheek_L.tx", 0.4), ("ctrlMouth_M.tx", -0.2)),
    "tongueOut": (("SDKTongue0_M.tx", 1.5), ("SDKTongue0_M.rz", 15)),
}
# solo se ctrlMouth_M ha jawForward (rig >= 5.750)
_JAW = {
    "jawForward": (("ctrlMouth_M.jawForward", 5),),
    "jawRight": (("ctrlMouth_M.jawSide", -5),),
    "jawLeft": (("ctrlMouth_M.jawSide", 5),),
}


def _mouth_close_offset():
    """Di quanto deve salire il labbro inferiore per richiudere la bocca a
    mascella aperta (MEL:14141-14148): mouthClose, sommato a jawOpen, da' le
    labbra incollate."""
    cmds.setAttr("ctrlMouth_M.ty", 0)
    closed = cmds.xform("lowerLip_M", query=True, worldSpace=True, translation=True)
    cmds.setAttr("ctrlMouth_M.ty", -1)
    opened = cmds.xform("lowerLip_M", query=True, worldSpace=True, translation=True)
    cmds.xform("lowerLip_M", worldSpace=True, translation=(opened[0], closed[1], opened[2]))
    offset = cmds.getAttr("lowerLip_M.t")[0][1]
    cmds.setAttr("ctrlMouth_M.ty", 0)
    cmds.setAttr("lowerLip_M.t", 0, 0, 0, type="float3")
    return offset


def _channels_for(shape):
    """[(canale, valore)] guidati da una shape ARKit, nell'ordine del MEL."""
    out = []
    for side, word, b in (("_R", "Right", 1), ("_L", "Left", -1)):
        if shape in ("mouthPressRight", "mouthPressLeft"):
            out += _MOUTH_PRESS_COMMON
        for prefix, channels in _SIDED.items():
            if shape == prefix + word:
                for channel, value in channels:
                    value = value(b) if callable(value) else value
                    out.append((channel.format(s=side), value))
        if shape == "mouth" + word:
            out += _SIDED_TO_CENTER[shape]
    if shape in _JAW and cmds.attributeQuery("jawForward", node="ctrlMouth_M", exists=True):
        out += _JAW[shape]
    out += _CENTER.get(shape, ())
    return out


def connect_arkit() -> bool:
    """Aggiunge a `ctrlARKit_M` (o `ctrlSnapChat_M`) gli attributi delle
    shape e li collega al rig (asConnectARKit, modo "create ctrl"). Ritorna
    False con un warning se il controller manca o e' gia' collegato."""
    snapchat = bool(get_fit_option("SnapChat"))
    ctrl = "ctrlSnapChat_M" if snapchat else "ctrlARKit_M"
    missing = [n for n in ("FaceControlSet", ctrl, "ctrlMouth_M") if not cmds.objExists(n)]
    if missing:
        cmds.warning("connect_arkit: missing {}".format(", ".join(missing)))
        return False
    if cmds.attributeQuery("createCtrlMode", node=ctrl, exists=True):
        cmds.warning("connect_arkit: {} is already connected".format(ctrl))
        return False

    shapes = [s for s in ARKIT_SHAPES if not (snapchat and s in _NOT_IN_SNAPCHAT)]
    names = list(SNAPCHAT_SHAPES) if snapchat else shapes
    cmds.addAttr(ctrl, keyable=False, longName="createCtrlMode", attributeType="bool")
    for name in names[: len(shapes)]:
        cmds.addAttr(
            ctrl,
            keyable=True,
            longName=name,
            attributeType="double",
            softMinValue=0,
            hasSoftMinValue=True,
            softMaxValue=10,
            hasSoftMaxValue=True,
        )
        ensure_output_blend_weighted("{}.{}".format(ctrl, name))

    cmds.currentTime(0)
    auto_key = cmds.autoKeyframe(query=True, state=True)
    if auto_key:
        cmds.autoKeyframe(state=False)
    skipped = []
    for shape, name in zip(shapes, names):
        driver = "{}.{}".format(ctrl, name)
        channels = _channels_for(shape)
        if shape == "mouthClose" and cmds.objExists("lowerLip_M"):
            offset = _mouth_close_offset()
            channels += [("SDKlowerLip_M.ty", offset / 2.0), ("SDKupperLip_M.ty", offset / -2.0)]
        for driven, value in channels:
            if not cmds.objExists(driven):
                skipped.append(driven)
                continue
            ds_sdk(driver, driven, 10, value)
    if auto_key:
        cmds.autoKeyframe(state=True)
    cmds.dgdirty(allPlugs=True)
    if skipped:
        cmds.warning(
            "connect_arkit: skipped missing channels: {}".format(", ".join(sorted(set(skipped))))
        )
    print("// ARKit connected.")
    cmds.select(clear=True)
    return True

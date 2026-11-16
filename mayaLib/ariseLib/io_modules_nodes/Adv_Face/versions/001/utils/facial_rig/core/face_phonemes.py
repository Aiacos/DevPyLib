"""Build step Phonemes (parita' asFacePhonemes MEL:36245-36523).

Step di puro driving: aggiunge a `ctrlPhonemes_M` un attributo 0-10 per
ognuno dei 16 fonemi e lo collega (asDsSdk) a pose gia' esistenti del rig:
apertura della mascella (campionata da ctrlMouth_M.ty), bocca stretta/larga
(campionata da ctrlMouth_M.tx), angoli della bocca, labbra, roll delle
labbra (campionato da ctrlLips_M.upperRoll/lowerRoll) e lingua. I
moltiplicatori `jaw` e `lip` scalano il peso di ogni contributo.

Divergenze (docs/gap-analysis.md §5q):
- `$frownBulgeTowardsVtx` (MEL:36300-36313) e i due `tempXform` sono
  calcolati/creati dal MEL ma mai usati: omessi;
- i canali guidati assenti (es. controller della cage non fittata) sono
  saltati con un warning unico; prerequisiti mancanti = warning + False.
"""

import maya.cmds as cmds

from .build_utils import as_face_hide_controllers, as_show_layer
from .driving_system import ds_sdk, ensure_output_blend_weighted
from .fit_options import FIT_SKELETON

PHONEMES = (
    "aaa", "eh", "ahh", "ohh", "uuu", "iee", "rrr", "www",
    "sss", "fff", "tth", "mbp", "ssh", "schwa", "gk", "lntd",
)  # fmt: skip
_CTRL = "ctrlPhonemes_M"
_MOUTH_WIDE_CTRLS = ("SDKLip", "SmileBulge", "FrownBulge", "Cheek", "NoseCorner")

# apertura della mascella, come frazione di ctrlMouth_M.ty = -1
_JAW_OPEN = {
    "aaa": 0.9, "eh": 0.5, "ahh": 1.0, "ohh": 0.75, "uuu": 0.25, "iee": 0.25, "rrr": 0.5,
    "www": 0.4, "mbp": 0.4, "fff": 0.2, "tth": 0.2, "schwa": 0.5, "gk": 0.5, "lntd": 0.5,
}  # fmt: skip
_JAW_FORWARD = {"ohh": 0.1, "sss": 0.1, "ssh": 0.1}
# bocca stretta (<0) / larga (>0): valore di ctrlMouth_M.tx da campionare
_NARROW_WIDE = {
    "aaa": 0.3, "eh": 0.5, "ohh": -0.65, "uuu": -0.75, "iee": 0.5, "www": -1, "sss": -0.15,
    "fff": 0.2, "ssh": -0.4,
}  # fmt: skip
_CORNER_UP = {"iee": 0.2, "fff": 0.2}  # frazione della posa smile
# (ty, tz) di SDKupperLip_M / SDKlowerLip_M
_UPPER_LIP = {
    "ohh": (0, 0.25), "uuu": (0, 0.45), "iee": (0.1, 0), "rrr": (0.1, 0.1), "mbp": (-0.45, -0.45),
    "sss": (0.1, 0), "ssh": (0.1, 0.25),
}  # fmt: skip
_LOWER_LIP = {
    "ohh": (0, 0.25), "uuu": (0, 0.45), "iee": (-0.45, 0), "rrr": (-0.1, 0.1),
    "mbp": (0.25, -0.25), "sss": (-0.45, 0), "fff": (0, -0.25), "ssh": (-0.25, 0.25),
}  # fmt: skip
_UPPER_ROLL = {"ohh": 3, "uuu": 6, "rrr": 3, "www": 3, "mbp": -6, "sss": 1.5, "tth": 2, "ssh": 5}
_LOWER_ROLL = {
    "ohh": 3, "uuu": 6, "rrr": 3, "www": 3, "mbp": -4, "sss": 3, "fff": -5, "tth": 2, "ssh": 5,
}  # fmt: skip
# rz di Tongue1/2/3. Il MEL legge i valori con indice 1..3 su un array di
# tre elementi: Tongue1 prende il secondo, Tongue2 il terzo, Tongue3 zero.
_TONGUE = {"rrr": (17, 17, 17), "tth": (10, 10, 10), "gk": (0, 40, -80), "lntd": (0, 10, 40)}

_REQUIRED = (
    "ctrlBox", "ctrlBox2", "ctrlBoxPhonemes_M", _CTRL, "ctrlMouth_M", "ctrlMouthCorner_R",
    "ctrlLips_M", "SDKLip_R", "SDKJaw_M", "SDKupperLip_M", "SDKlowerLip_M",
)  # fmt: skip


class _Driver:
    """asDsSdk dal controller dei fonemi, saltando i canali assenti."""

    def __init__(self):
        self.skipped = []

    def drive(self, phoneme, driven, value):
        if not cmds.objExists(driven):
            self.skipped.append(driven)
            return
        ds_sdk("{}.{}".format(_CTRL, phoneme), driven, 10, value)


def _add_attributes():
    for phoneme in PHONEMES:
        cmds.addAttr(
            _CTRL,
            keyable=True,
            longName=phoneme,
            attributeType="double",
            softMinValue=0,
            hasSoftMinValue=True,
            softMaxValue=10,
            hasSoftMaxValue=True,
        )
        ensure_output_blend_weighted("{}.{}".format(_CTRL, phoneme))
    cmds.addAttr(_CTRL, keyable=True, longName="multipliers")
    cmds.setAttr(_CTRL + ".multipliers", lock=True)
    for multiplier in ("jaw", "lip"):
        cmds.addAttr(
            _CTRL,
            keyable=True,
            longName=multiplier,
            attributeType="double",
            softMinValue=0,
            hasSoftMinValue=True,
            softMaxValue=2,
            hasSoftMaxValue=True,
            defaultValue=1,
        )
        ensure_output_blend_weighted("{}.{}".format(_CTRL, multiplier))


def _sample(plug, value, node):
    """t e r di `node` con `plug` portato a `value` (poi riazzerato)."""
    cmds.setAttr(plug, value)
    pos, rot = cmds.getAttr(node + ".t")[0], cmds.getAttr(node + ".r")[0]
    cmds.setAttr(plug, 0)
    return pos, rot


def _jaw_and_mouth_width(driver):
    for phoneme in PHONEMES:
        if phoneme in _JAW_OPEN:
            pos, rot = _sample("ctrlMouth_M.ty", -1 * _JAW_OPEN[phoneme], "SDKJaw_M")
            driver.drive(phoneme, "SDKJaw_M.ty", pos[1])
            driver.drive(phoneme, "SDKJaw_M.tz", pos[2])
            driver.drive(phoneme, "SDKJaw_M.rx", rot[0])
    for phoneme in PHONEMES:
        if phoneme in _JAW_FORWARD:
            driver.drive(phoneme, "SDKJaw_M.tz", _JAW_FORWARD[phoneme])
    for phoneme in PHONEMES:
        if phoneme not in _NARROW_WIDE:
            continue
        for side in ("_R", "_L"):
            for name in _MOUTH_WIDE_CTRLS:
                node = name + side
                if not cmds.objExists(node):
                    driver.skipped.append(node)
                    continue
                pos, _ = _sample("ctrlMouth_M.tx", _NARROW_WIDE[phoneme], node)
                for axis, value in zip("xyz", pos):
                    driver.drive(phoneme, "{}.t{}".format(node, axis), value)


def _lips_and_tongue(driver, smile_ty):
    for phoneme in PHONEMES:
        plug = "{}.{}".format(_CTRL, phoneme)
        cmds.setAttr(plug, 10)
        if phoneme in _CORNER_UP:
            for side in ("_R", "_L"):
                driver.drive(phoneme, "SDKLip{}.ty".format(side), smile_ty * _CORNER_UP[phoneme])
        for lip, table in (("SDKupperLip_M", _UPPER_LIP), ("SDKlowerLip_M", _LOWER_LIP)):
            if phoneme in table:
                driver.drive(phoneme, lip + ".ty", table[phoneme][0])
                driver.drive(phoneme, lip + ".tz", table[phoneme][1])
        for lip, attr, table in (
            ("SDKupperLip_M", "upperRoll", _UPPER_ROLL),
            ("SDKlowerLip_M", "lowerRoll", _LOWER_ROLL),
        ):
            if phoneme not in table or not cmds.objExists("ctrlLips_M." + attr):
                continue
            pos, rot = _sample("ctrlLips_M." + attr, table[phoneme], lip)
            for axis, value in zip("xyz", pos):
                driver.drive(phoneme, "{}.t{}".format(lip, axis), value)
            for axis, value in zip("xyz", rot):
                driver.drive(phoneme, "{}.r{}".format(lip, axis), value)
        if phoneme in _TONGUE and cmds.objExists("Tongue3_M"):
            values = _TONGUE[phoneme] + (0,)
            for index in (1, 2, 3):
                driver.drive(phoneme, "SDKTongue{}_M.rz".format(index), values[index])
        cmds.setAttr(plug, 0)


def _connect_multipliers():
    """Il peso di ogni contributo dei fonemi e' il moltiplicatore `jaw`
    (canali della mascella) o `lip` (MEL:36494-36517)."""
    for bw in (
        cmds.listConnections(_CTRL, source=False, destination=True, type="blendWeighted") or []
    ):
        for curve in (
            cmds.listConnections(bw, source=False, destination=True, type="animCurve") or []
        ):
            nodes = cmds.listConnections(
                curve, source=False, destination=True, type="blendWeighted"
            )
            plugs = cmds.listConnections(
                curve, source=False, destination=True, plugs=True, type="blendWeighted"
            )
            if not nodes or not plugs:
                continue
            input_nr = plugs[0].split("[")[1].replace("]", "")
            for target in nodes:
                jaw = "Jaw_M" in target or target == "bwctrlMouth_M_translateY"
                source = "bwctrlPhonemes_M_{}.output".format("jaw" if jaw else "lip")
                weight = "{}.weight[{}]".format(target, input_nr)
                if not cmds.isConnected(source, weight):
                    cmds.connectAttr(source, weight)


def face_phonemes() -> bool:
    """Attributi dei fonemi su ctrlPhonemes_M (asFacePhonemes). Salta
    (True) con l'opzione Phonemes spenta o senza `upperLipMainCurve`."""
    if cmds.objExists(FIT_SKELETON) and cmds.attributeQuery(
        "Phonemes", node=FIT_SKELETON, exists=True
    ):
        if not cmds.getAttr(FIT_SKELETON + ".Phonemes"):
            return True
    if not cmds.objExists("upperLipMainCurve"):
        return True
    missing = [n for n in _REQUIRED if not cmds.objExists(n)]
    if missing:
        cmds.warning("face_phonemes: missing {}".format(", ".join(missing)))
        return False
    if cmds.attributeQuery(PHONEMES[0], node=_CTRL, exists=True):
        cmds.warning("face_phonemes: phonemes already built")
        return False

    as_face_hide_controllers(True)
    cmds.setAttr("ctrlBox2.v", 0)
    cmds.setAttr("ctrlBox.AimCtrlVis", 0)
    cmds.setAttr("ctrlBoxPhonemes_M.v", 1)
    as_show_layer("Normal")
    for locator in ("upperFaceLocator_M", "lowerFaceLocator_M", "underFaceLocator_M"):
        if cmds.objExists(locator):
            cmds.delete(locator)

    # posa smile dell'angolo della bocca, come posizione di SDKLip_R
    cmds.xform("ctrlMouthCorner_R", objectSpace=True, translation=(1, 1, 0))
    values = cmds.createNode("transform", name="LipSmileValues", parent="SDKLip_R")
    cmds.parent(values, cmds.listRelatives("SDKLip_R", parent=True)[0])
    cmds.xform("ctrlMouthCorner_R", objectSpace=True, translation=(0, 0, 0))

    _add_attributes()
    driver = _Driver()
    _jaw_and_mouth_width(driver)
    _lips_and_tongue(driver, cmds.getAttr("LipSmileValues.ty"))
    _connect_multipliers()
    if driver.skipped:
        cmds.warning(
            "face_phonemes: skipped missing channels: {}".format(
                ", ".join(sorted(set(driver.skipped)))
            )
        )
    cmds.select(clear=True)
    return True

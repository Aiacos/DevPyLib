"""Build step LipSide (parita' asFaceLipSide MEL:35436 e
asFaceLipSideFinish MEL:35508).

Step di puro driving: apre con asFaceLipDownFinish (MEL:35443), blocca alcuni
canali di LipRegion_M (per evitare ambiguita' di mirroring), posa
ctrlLips_M.tx a -1 con pose asimmetriche dei lati R e L e raccoglie i
controller nel set `LipSideControls`.

Il finish memorizza la posa (frame 30) dei controller _L nel nodo
`LipLeftValues`, converte in SDK (ds_finish ctrlLips _M tx -1) e poi aggiunge
le chiavi del lato opposto: sui canali _R il driver a +1 riceve il valore
memorizzato del controller _L, e sui canali _L il driver a -1 riceve lo
stesso valore (MEL:35555-35583). Gate su `upperLipMainCurve`.

Divergenze (vedi docs/gap-analysis.md §5f): controller, set e nodi bw assenti
vengono saltati invece di sollevare errori (no-exceptions); il valore
funzionale e' completo solo su asset reale, perche' i controller di regione
nascono dagli step mesh.
"""

import maya.cmds as cmds

from .build_utils import as_face_hide_controllers, as_lock_attr
from .driving_system import face_ds_finish, mirror_connect_ctrls
from .face_lip_down import face_lip_down_finish
from .fitting import face_fit_anim, remove_fit_anim_from_ctrl_box

_SOURCE_BW = "bwctrlLips_M_translateX"
_REGION_TEMP_LOCKS = ("ty", "tz", "rx", "rz", "sy")
_TRS = ("translate", "rotate", "scale")
_XYZ = ("X", "Y", "Z")

# (plug o oggetto, valore) nell'ordine del MEL:35451-35492
_POSES = (
    ("ctrlLips_M.tx", -1),
    ("LipRegion_M", 0),
    ("LipRegion_M.tx", -1.2),
    ("LipRegion_M.ry", -25),
    ("LipRegion_M.sx", 0.8),
    ("LipRegion_M.sz", 0.8),
    ("NoseRegion_M", 0),
    ("NoseRegion_M.tx", -0.3),
    ("NoseRegion_M.ty", -0.05),
    ("NoseRegion_M.ry", -5),
    ("NoseRegion_M.rz", -5),
    # Right
    ("SmileBulge_R", 0),
    ("SmileBulge_R.tx", 0.35),
    ("SmileBulge_R.ty", 0.2),
    ("SmileBulge_R.tz", 0.7),
    ("FrownBulge_R", 0),
    ("FrownBulge_R.tx", 0.35),
    ("FrownBulge_R.ty", -0.2),
    ("FrownBulge_R.tz", 0.7),
    ("CheekBone_R", 0),
    ("CheekBone_R.tx", 0.25),
    ("CheekBone_R.ty", 0.25),
    # Left
    ("SmileBulge_L", 0),
    ("SmileBulge_L.tx", -0.35),
    ("SmileBulge_L.ty", -0.05),
    ("SmileBulge_L.tz", -0.1),
    ("FrownBulge_L", 0),
    ("FrownBulge_L.tx", -0.35),
    ("FrownBulge_L.ty", 0.05),
    ("FrownBulge_L.tz", -0.1),
    ("CheekBone_L", 0),
    ("CheekBone_L.tx", -0.25),
    ("CheekBone_L.ty", -0.1),
    ("ChinCrease_M", 0),
    ("ChinCrease_M.tx", -0.5),
)


def _existing(names):
    return [n for n in names if cmds.objExists(n)]


def face_lip_side():
    """Posa 'lip side' via fit-anim + set LipSideControls (asFaceLipSide).

    Returns:
        True anche quando lo step viene saltato per assenza di
        `upperLipMainCurve` (skip fedele al MEL). Nessuna eccezione.
    """
    if not cmds.objExists("upperLipMainCurve"):
        return True

    face_lip_down_finish()
    as_face_hide_controllers(True)
    if cmds.objExists("ctrlBox.RegionsCtrlVis"):
        cmds.setAttr("ctrlBox.RegionsCtrlVis", 1)

    if cmds.objExists("LipRegion_M"):
        for attr in _REGION_TEMP_LOCKS:
            cmds.setAttr("LipRegion_M." + attr, lock=True)

    for obj_attr, value in _POSES:
        face_fit_anim(obj_attr, value)

    members = _existing(["LipRegion_M", "NoseRegion_M", "ChinCrease_M"])
    for side in ("_R", "_L"):
        members += _existing([b + side for b in ("SmileBulge", "FrownBulge", "CheekBone")])
    if not cmds.objExists("LipSideControls"):
        cmds.sets(members, name="LipSideControls")
        if cmds.objExists("FaceBuildingSets"):
            cmds.sets("LipSideControls", add="FaceBuildingSets")

    cmds.playbackOptions(minTime=0, maxTime=30, animationStartTime=0, animationEndTime=30)
    cmds.currentTime(30)
    cmds.select(clear=True)
    print("// LipSide applied")
    return True


def _store_lip_left_values():
    """Crea `LipLeftValues` con la posa (frame 30) di ogni controller on-face
    _L che ha una fit-anim (MEL:35521-35539)."""
    cmds.currentTime(30)
    driven = []
    for shape in cmds.listRelatives("OnFacecontrols", allDescendents=True, type="nurbsCurve") or []:
        ctrl = (cmds.listRelatives(shape, parent=True) or [""])[0]
        if not ctrl.endswith("_L") or ctrl in driven:
            continue
        if cmds.listConnections(ctrl, source=True, destination=False, type="animCurve"):
            driven.append(ctrl)

    cmds.createNode("transform", name="LipLeftValues", parent="FaceBuildInProgress")
    as_lock_attr("LipLeftValues", True, True, True, True)
    for ctrl in driven:
        for trs in _TRS:
            for xyz in _XYZ:
                cmds.addAttr(
                    "LipLeftValues",
                    longName="{}_{}{}".format(ctrl, trs, xyz),
                    attributeType="double",
                    defaultValue=cmds.getAttr("{}.{}{}".format(ctrl, trs, xyz)),
                    keyable=True,
                )


def _set_linear_sdk(driver_plug, driven_plug, driver_value, value):
    cmds.setDrivenKeyframe(
        driven_plug,
        currentDriver=driver_plug,
        driverValue=driver_value,
        value=value,
        inTangentType="linear",
        outTangentType="linear",
    )


def _add_opposite_side_keys():
    """Aggiunge le chiavi del lato opposto sugli SDK guidati da
    ctrlLips_M.tx (MEL:35548-35583)."""
    if not cmds.objExists(_SOURCE_BW):
        return
    source_plug = _SOURCE_BW + ".output"

    # caso speciale: comportamento "Left" delle scale di LipRegion_M
    for bw in ("bwSDKLipRegion_M_scaleX", "bwSDKLipRegion_M_scaleZ"):
        if cmds.objExists(bw):
            _set_linear_sdk(source_plug, bw + ".input[0]", 1, 0.8)

    for sdk_curve in cmds.listConnections(source_plug, source=False, destination=True) or []:
        tokens = sdk_curve.split("_")
        if len(tokens) < 3 or tokens[1] != "R":
            continue
        ctrl = tokens[0].replace("SDK", "", 1) + "_R"
        attr = tokens[2].rstrip("0123456789")
        left_attr = "{}_{}".format(ctrl.replace("_R", "_L", 1), attr)
        if not cmds.attributeQuery(left_attr, node="LipLeftValues", exists=True):
            continue
        targets = cmds.listConnections(
            sdk_curve + ".output", source=False, destination=True, plugs=True
        )
        if not targets:
            continue
        target_plug = targets[0]
        value = cmds.getAttr("LipLeftValues." + left_attr)
        _set_linear_sdk(source_plug, target_plug, 1, value)
        # e -1 anche per il Left (il driver _M non ha lato da sostituire)
        left_target = target_plug.replace("_R", "_L", 1)
        if cmds.objExists(left_target.split(".", 1)[0]):
            _set_linear_sdk(source_plug, left_target, -1, value)


def face_lip_side_finish():
    """Memorizza le pose _L, converte la posa lip-side in SDK e aggiunge le
    chiavi del lato opposto (asFaceLipSideFinish). Idempotente via
    FaceBuildInProgress.LipSideFinish. Nessuna eccezione.
    """
    if not cmds.objExists("FaceBuildInProgress"):
        cmds.warning("face_lip_side_finish: FaceBuildInProgress not found")
        return
    if cmds.attributeQuery("LipSideFinish", node="FaceBuildInProgress", exists=True):
        return
    if not cmds.objExists("OnFacecontrols"):
        cmds.warning("face_lip_side_finish: OnFacecontrols not found")
        return
    cmds.addAttr(
        "FaceBuildInProgress",
        longName="LipSideFinish",
        attributeType="bool",
        defaultValue=True,
        keyable=False,
    )

    _store_lip_left_values()

    mirror_connect_ctrls(False)
    remove_fit_anim_from_ctrl_box()
    face_ds_finish("ctrlLips", "_M", "tx", -1)

    # sblocca i lock temporanei
    if cmds.objExists("LipRegion_M"):
        as_lock_attr("LipRegion_M", False, False, False, False)

    _add_opposite_side_keys()

    as_face_hide_controllers(True)
    if cmds.objExists("ctrlBox.RegionsCtrlVis"):
        cmds.setAttr("ctrlBox.RegionsCtrlVis", 0)
    if cmds.objExists("ctrlBoxLips_M"):
        cmds.setAttr("ctrlBoxLips_M.v", 1)

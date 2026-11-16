"""Build step LipDown (parita' asFaceLipDown MEL:35358 e
asFaceLipDownFinish MEL:35410).

Step di puro driving: apre con asFaceLipUpFinish (MEL:35366), posa
ctrlLips_M.ty a -1, poi per ogni controller del set `LipUpControls` muta i
canali SDK creati da LipUp e ne riapplica il valore (campionato al frame 30)
come fit-anim sul controller, con le scale specchiate attorno a 1
(MEL:35374-35394). Il finish smuta gli SDK e converte in SDK la nuova posa
(ds_finish ctrlLips _M ty -1). Gate su `upperLipMainCurve`.

Divergenze (vedi docs/gap-analysis.md §5f): controller/set/gruppi SDK assenti
vengono saltati invece di sollevare errori (no-exceptions); il valore
funzionale e' completo solo su asset reale, perche' i controller di regione
nascono dagli step mesh.
"""

import maya.cmds as cmds

from .build_utils import as_face_hide_controllers
from .driving_system import face_ds_finish, mirror_connect_ctrls
from .face_lip_up import face_lip_up_finish
from .fitting import face_fit_anim, remove_fit_anim_from_ctrl_box

_LIP_UP_SET = "LipUpControls"


def _lip_up_sdk_groups():
    """Coppie (ctrl, gruppo SDK) dei controller posati da LipUp."""
    if not cmds.objExists(_LIP_UP_SET):
        return []
    pairs = []
    for ctrl in cmds.sets(_LIP_UP_SET, query=True) or []:
        sdk = "SDK" + ctrl
        if cmds.objExists(sdk):
            pairs.append((ctrl, sdk))
    return pairs


def _mute_and_reapply_lip_up():
    """Muta gli SDK di LipUp e ne riapplica il valore come fit-anim
    (MEL:35374-35394). I controller _L sono mutati ma non posati."""
    cmds.currentTime(0)
    for ctrl, sdk in _lip_up_sdk_groups():
        for attr in cmds.listAttr(sdk, keyable=True) or []:
            plug = "{}.{}".format(sdk, attr)
            if not cmds.listConnections(plug, source=True, destination=False):
                continue
            value = cmds.getAttr(plug, time=30)
            if attr.startswith("scale"):
                value = 1 - (value - 1)
            cmds.mute(plug)
            if not ctrl.endswith("_L"):
                face_fit_anim("{}.{}".format(ctrl, attr), value)


def face_lip_down():
    """Posa 'lip down' via fit-anim (asFaceLipDown).

    Returns:
        True anche quando lo step viene saltato per assenza di
        `upperLipMainCurve` (skip fedele al MEL). Nessuna eccezione.
    """
    if not cmds.objExists("upperLipMainCurve"):
        return True

    face_lip_up_finish()

    as_face_hide_controllers(True)
    mirror_connect_ctrls(True)

    face_fit_anim("ctrlLips_M.ty", -1)
    _mute_and_reapply_lip_up()

    # chiave di riposo esplicita: asFaceFitAnim riconosce le scale solo dal
    # nome corto ("*.s[a-z]"), quindi con "scaleY" ha keyato 0 al frame 0
    rest_plugs = [
        p
        for p in ("upperLip_M.sy", "upperLip_M.sz", "lowerLip_M.sy", "lowerLip_M.sz")
        if cmds.objExists(p)
    ]
    if rest_plugs:
        cmds.setKeyframe(rest_plugs, time=0, value=1)

    face_fit_anim("SmileBulge_R.tz", 0.1)
    face_fit_anim("FrownBulge_R.tz", 0.1)
    face_fit_anim("ChinCrease_M.ty", -0.3)
    face_fit_anim("ChinCrease_M.tz", 0.1)

    cmds.playbackOptions(minTime=0, maxTime=30, animationStartTime=0, animationEndTime=30)
    cmds.currentTime(30)
    cmds.select(clear=True)
    print("// LipDown applied")
    return True


def face_lip_down_finish():
    """Smuta gli SDK di LipUp e converte la posa lip-down in SDK
    (asFaceLipDownFinish). Idempotente via FaceBuildInProgress.LipDownFinish.
    Nessuna eccezione.
    """
    if not cmds.objExists("FaceBuildInProgress"):
        cmds.warning("face_lip_down_finish: FaceBuildInProgress not found")
        return
    if cmds.attributeQuery("LipDownFinish", node="FaceBuildInProgress", exists=True):
        return
    cmds.addAttr(
        "FaceBuildInProgress",
        longName="LipDownFinish",
        attributeType="bool",
        defaultValue=True,
        keyable=False,
    )

    mirror_connect_ctrls(False)
    remove_fit_anim_from_ctrl_box()

    cmds.currentTime(0)
    for _ctrl, sdk in _lip_up_sdk_groups():
        try:
            cmds.mute(sdk, disable=True)
        except RuntimeError:
            # nessun canale mutato su questo gruppo (LipUp non lo guidava)
            pass

    face_ds_finish("ctrlLips", "_M", "ty", -1)
    as_face_hide_controllers(True)
    if cmds.objExists("ctrlBoxLips_M"):
        cmds.setAttr("ctrlBoxLips_M.v", 1)

"""Build step Squint (parita' asFaceSquint MEL:34024 e
asFaceSquintFinish MEL:34102).

Aggiunge l'attributo `squint` agli eye controller, costruisce la rete
`eyeLidBlinkSquintMPD/SR` che mixa blink e squint reiniettandola nel
blendWeighted del blink, posa lo squint via fit-anim (relativo all'altezza di
apertura dell'occhio, $factor) e — al finish — converte la posa in SDK.

Divergenze (vedi docs/gap-analysis.md §5e):
- `simplerEyeLid`/`cyclops` letti da get_fit_option invece dei checkBox MEL.
- `include_above_eyes()` da core.face_prep al posto di asFaceIncludeAboveEyes.
- Guard di resilienza (no-exceptions): la reiniezione nel blendWeighted del
  blink e il set di ctrlBox.RegionsCtrlVis avvengono solo se i nodi esistono.
"""

import maya.cmds as cmds

from .build_utils import as_face_hide_controllers
from .driving_system import ensure_output_blend_weighted, face_ds_finish, mirror_connect_ctrls
from .face_prep import include_above_eyes
from .fit_options import get_fit_option
from .fitting import face_fit_anim, remove_fit_anim_from_ctrl_box


def face_squint():
    """Setup squint + rete mix blink/squint + pose fit-anim (asFaceSquint).
    Ritorna bool. Nessuna eccezione."""
    for side in ("_R", "_L"):
        if not cmds.objExists("ctrlEye" + side):
            cmds.warning("face_squint: ctrlEye{} not found".format(side))
            return False

    simpler = bool(get_fit_option("SimplerEyeLid"))
    cyclops = bool(get_fit_option("Cyclops"))
    not_cyclops = 0 if cyclops else 1

    # altezza di apertura dell'occhio: lo squint e' relativo a questa
    ctrl_scale = (
        cmds.getAttr("OnFacecontrols.sx") if cmds.objExists("OnFacecontrols") else 1.0
    ) or 1.0
    pos_a = cmds.xform("upperLid_R", query=True, worldSpace=True, translation=True)
    pos_b = cmds.xform("lowerLid_R", query=True, worldSpace=True, translation=True)
    dist = sum((a - b) ** 2 for a, b in zip(pos_a, pos_b)) ** 0.5
    factor = (dist / ctrl_scale) * 0.75

    for side in ("_R", "_L"):
        ctrl = "ctrlEye" + side
        if not cmds.attributeQuery("squint", node=ctrl, exists=True):
            cmds.addAttr(
                ctrl,
                longName="squint",
                keyable=True,
                attributeType="double",
                softMaxValue=10,
                hasSoftMaxValue=True,
                softMinValue=0,
                hasMinValue=True,
                defaultValue=0,
            )
        ensure_output_blend_weighted(ctrl + ".squint")

    # moltiplica blink & squint cosi' si mixano se applicati entrambi
    for side in ("_R", "_L"):
        mpd = cmds.createNode("multiplyDivide", name="eyeLidBlinkSquintMPD" + side)
        cmds.connectAttr("ctrlEye" + side + ".blink", mpd + ".input1X")
        cmds.connectAttr("ctrlEye" + side + ".squint", mpd + ".input2X")
        sr = cmds.createNode("setRange", name="eyeLidBlinkSquintSR" + side)
        cmds.setAttr(sr + ".maxX", -7.3)
        cmds.setAttr(sr + ".oldMaxX", 100)
        cmds.connectAttr(mpd + ".outputX", sr + ".valueX")
        bw = "bwctrlEye" + side + "_blink"
        if cmds.objExists(bw):
            # prossimo slot libero del blendWeighted (MEL: getAttr -s .input;
            # in cmds gli elementi solo-connessi non contano in size=True,
            # quindi si usa il massimo indice esistente +1)
            indices = cmds.getAttr(bw + ".input", multiIndices=True) or []
            idx = (max(indices) + 1) if indices else 0
            cmds.connectAttr(sr + ".outValueX", "{}.input[{}]".format(bw, idx))

    as_face_hide_controllers(True)
    mirror_connect_ctrls(True)

    face_fit_anim("ctrlEye_R.squint", 10)
    face_fit_anim("ctrlEye_L.squint", 10)
    if include_above_eyes():
        face_fit_anim("EyeRegion_R.sy", 0.75)
        face_fit_anim("EyeBrowRegion_R.ty", -0.75 * factor)
    face_fit_anim("upperLid_R.ty", -0.4 * factor)
    face_fit_anim("lowerLid_R.tx", -0.4 * factor * not_cyclops)
    face_fit_anim("lowerLid_R.ty", 0.525 * factor)
    face_fit_anim("outerLid_R.tx", -0.15 * factor * not_cyclops)
    if not simpler:
        face_fit_anim("upperLidOuter_R.ty", -0.2 * factor)
        face_fit_anim("outerLidOuter_R.sy", 0.5)
        face_fit_anim("innerLidOuter_R.sy", 0.5)
    face_fit_anim("lowerLidOuter_R.tx", -0.07 * factor * not_cyclops)
    face_fit_anim("lowerLidOuter_R.ty", 0.07 * factor)

    cmds.playbackOptions(minTime=0, maxTime=30, animationStartTime=0, animationEndTime=30)
    cmds.currentTime(30)
    cmds.select(clear=True)
    print("// Squint applied")
    return True


def face_squint_finish():
    """Converte la posa squint in SDK (asFaceSquintFinish). Idempotente
    via FaceBuildInProgress.SquintFinish. Nessuna eccezione."""
    if not cmds.objExists("FaceBuildInProgress"):
        cmds.warning("face_squint_finish: FaceBuildInProgress not found")
        return
    if cmds.attributeQuery("SquintFinish", node="FaceBuildInProgress", exists=True):
        return
    cmds.addAttr(
        "FaceBuildInProgress",
        longName="SquintFinish",
        attributeType="bool",
        defaultValue=True,
        keyable=False,
    )
    cyclops = bool(get_fit_option("Cyclops"))

    mirror_connect_ctrls(False)
    remove_fit_anim_from_ctrl_box()
    face_ds_finish("ctrlEye", "_RL", "squint", 10)
    if cyclops and cmds.objExists("bwctrlEye_L_squint") and cmds.objExists("bwctrlEye_R_squint"):
        cmds.connectAttr("bwctrlEye_L_squint.output", "bwctrlEye_R_squint.input[0]", force=True)

    as_face_hide_controllers(True)
    for side in ("_R", "_L"):
        box = "ctrlBoxEye" + side
        if cmds.objExists(box):
            cmds.setAttr(box + ".v", 1)
    # evita che l'utente provi a fare SDK sui RegionCtrl negli step successivi
    if cmds.objExists("ctrlBox") and cmds.attributeQuery(
        "RegionsCtrlVis", node="ctrlBox", exists=True
    ):
        cmds.setAttr("ctrlBox.RegionsCtrlVis", 0)

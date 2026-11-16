"""Frame 'Build' e 'Build...' della UI asFace
(parita' MEL AdvancedSkeleton.mel:1725-1919).

La logica di gating degli step replica asFaceUpdateInfo (MEL 42675-42708):
guidata dal solo intero FaceFitSkeleton.buildStep. La UI orchestra il
backend esistente (FacialRigBuilder, build_steps); non reimplementa il build.
"""

import maya.cmds as cmds

from ...builder import IMPLEMENTED_STEPS, FacialRigBuilder
from ..build_steps import reset_build_step
from ..config import FacialRigConfig
from ..fit_options import get_fit_option
from ..fitting import toggle_fit_face
from .widgets import step_row


def step_button_enabled(step_index, build_step):
    """True se il bottone Build dello step e' attivo: solo il prossimo
    step (build_step+1), come il MEL (header abilitato per nextStep)."""
    return step_index == build_step + 1


def step_visible(step_index, build_step):
    """True se la riga dello step e' visibile: gli step gia' completati
    prima del corrente sono nascosti (MEL: $i > nextStep-2 => i >= buildStep)."""
    return step_index >= build_step


def _face_scale():
    if cmds.objExists("FaceFitSkeleton") and cmds.attributeQuery(
        "faceScale", node="FaceFitSkeleton", exists=True
    ):
        return cmds.getAttr("FaceFitSkeleton.faceScale")
    return 1.0


def config_from_scene():
    """Costruisce un FacialRigConfig dalle opzioni di FaceFitSkeleton.

    Onora le scelte del frame Pre (geometrie + flag + lip-ctrls). Le
    geometrie/joint/skinCluster sono richieste da FacialRigBuilder; il
    resto e' caricato da build() via load_fit_data.
    """
    all_head = get_fit_option("AllHead") or ""
    lip_ctrls = get_fit_option("LipCtrls")  # enum -> stringa "12".."24"
    return FacialRigConfig(
        geometry=get_fit_option("Face") or "",
        all_head_geo=all_head.split(),
        head_joint=get_fit_option("HeadJoint") or "Head_M",
        skin_cluster=get_fit_option("SkinCluster") or "",
        right_eye=get_fit_option("RightEye") or "",
        left_eye=get_fit_option("LeftEye") or "",
        upper_teeth=get_fit_option("UpperTeeth") or "",
        lower_teeth=get_fit_option("LowerTeeth") or "",
        tongue=get_fit_option("Tongue") or "",
        eyelash=get_fit_option("Eyelash") or "",
        eyebrow_geo=get_fit_option("Eyebrow") or "",
        non_symmetrical=bool(get_fit_option("NonSym")),
        game_engine=bool(get_fit_option("GameEngine")),
        simpler_eyelid=bool(get_fit_option("SimplerEyeLid")),
        eye_socket=bool(get_fit_option("EyeSocket")),
        long_snout=bool(get_fit_option("LongSnout")),
        multi_skin_clusters=bool(get_fit_option("MultiSkinClusters")),
        arkit=bool(get_fit_option("ARKit")),
        snapchat=bool(get_fit_option("SnapChat")),
        lip_controls=int(lip_ctrls) if lip_ctrls else 12,
        face_scale=_face_scale(),
    )


def _make_builder():
    """Costruisce un FacialRigBuilder dalle opzioni di scena."""
    return FacialRigBuilder(config_from_scene())


def _build_step_index(step_name):
    return FacialRigBuilder.BUILD_ORDER.index(step_name) + 1


def step_label(step_index, step_name):
    """Etichetta 'N : Nome' con '*' se lo step non e' ancora a parita'."""
    mark = "" if step_name in IMPLEMENTED_STEPS else " *"
    return "{} : {}{}".format(step_index, step_name, mark)


def _current_build_step():
    if cmds.objExists("FaceFitSkeleton") and cmds.attributeQuery(
        "buildStep", node="FaceFitSkeleton", exists=True
    ):
        return cmds.getAttr("FaceFitSkeleton.buildStep")
    return 0


def _run_full_build(manually_restore):
    builder = _make_builder()
    try:
        builder.build(manually_run_restore_step=manually_restore)
    except Exception as exc:  # contratto: mai propagare
        cmds.warning("Build failed: {}".format(exc))


def _run_step(step_name):
    builder = _make_builder()
    try:
        builder.build_component(step_name)
    except Exception as exc:
        cmds.warning("Step '{}' failed: {}".format(step_name, exc))


def build_full_frame(fitting):
    """Frame ' Build' (MEL 1725-1795). Returns il nome del frameLayout."""
    frame = cmds.frameLayout(label=" Build", collapsable=True, collapse=True)
    cmds.columnLayout(adjustableColumn=True)

    cmds.button(label="Delete Adv", enable=False, annotation="non ancora portato")
    for keep in (
        "Keep All",
        "keep Skin weights",
        "keep HeadSquash",
        "keep DrivingSystems",
        "keep BlendShapes",
        "keep CorrectiveShapes",
        "keep shape and color of controls",
        "keep CustomControls",
        "keep customized control orientations",
    ):
        cmds.checkBox(label=keep, enable=False)
    restore_box = cmds.checkBox(label="manually run Restore Step")

    cmds.button(label="Toggle Fit/Adv", command=lambda *_: toggle_fit_face())
    cmds.button(
        label="Build AdvancedFace",
        command=lambda *_: _run_full_build(cmds.checkBox(restore_box, query=True, value=True)),
    )

    cmds.setParent("..")
    cmds.setParent("..")
    return frame


def build_steps_frame(fitting):
    """Frame ' Build...' (MEL 1796-1919). Returns il nome del frameLayout."""
    frame = cmds.frameLayout(label=" Build ...", collapsable=True, collapse=True)
    cmds.columnLayout(adjustableColumn=True)
    cmds.text(label="Step Builder", font="boldLabelFont", align="left")

    build_step = _current_build_step()
    for step_name in FacialRigBuilder.BUILD_ORDER:
        i = _build_step_index(step_name)
        step_row(
            label=step_label(i, step_name),
            on_build=(lambda s=step_name: _run_step(s)),
            enabled=step_button_enabled(i, build_step),
            visible=step_visible(i, build_step),
        )

    cmds.button(height=15, label="reset steps", command=lambda *_: reset_build_step())
    cmds.setParent("..")
    cmds.setParent("..")
    return frame

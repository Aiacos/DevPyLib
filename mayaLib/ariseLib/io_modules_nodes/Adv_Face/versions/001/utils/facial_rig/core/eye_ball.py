"""Build dell'occhio (parita' asFaceEyeBall, MEL 29063-29467).

Primo componente vero del rig. Slice 1 (occhio sferico):
- gerarchia EyeSetup/EyeAimSetup sotto FaceDeformationSystem, col
  master aim AimEye_M ancorato all'HeadJoint via follow blend;
- per lato EyeRegion (ctrl + EyeRegionJoint sotto FaceDeformationSystem),
  Eye (ctrl + EyeJoint sotto FaceJoint_M, rotateOrder 2, orient da
  FitEyeBall) e la rete aim (AimEye<side> duplicato + EyeAim<side> con
  aimConstraint sul ramo non-OPM);
- le 4 SDK del look: lo slider ctrlEye<side>.tx/ty guida SDKEye<side>.ry/rx;
- skinning della geo occhio sull'EyeJoint.

EyeRegion usa asFacePlaceCtrlByProjection (proiezione dei CV sulla
mesh) ora a parita'. EyeBase (opzionale, fit option EyeBase, default off,
MEL 29170-29399) e' a parita': controller-base proiettato che diventa il
parent di EyeRegion + rete a matrici (EyeBaseMM/DM, EyeBaseFollowTS/R) che
fa seguire l'aim. Pupil/Iris (asFacePupilIris, MEL:29470) sta in
core/face_pupil_iris.py ed e' chiamata in coda quando esiste FaceFitPupil o
FaceFitIris. Rinviati (documentati): multiSkinClusters (EyeBallSC),
lattice degli occhi non-sferici (asDeformer non baka in batch).

Divergenza sanzionata: il ramo aim usa aimConstraint (non-OPM); il
ramo aimMatrix OPM (EyeAimAM/MM) non e' coperto in questo slice.
"""

import maya.cmds as cmds

from .build_utils import (
    as_align,
    as_face_hide_controllers,
    as_opm_scale_reset,
    as_parent_constraint,
    as_parent_constraint_blend,
)
from .ctrl_box import create_face_controller, place_ctrl_by_projection
from .driving_system import ds_sdk
from .fit_options import FIT_SKELETON, get_fit_option


def _new_skin_cluster(joint: str, geometry: str, name: str) -> str:
    """newSkinCluster MEL (tsb, mi3, dr4, no removeUnused)."""
    sc = cmds.skinCluster(
        joint,
        geometry,
        toSelectedBones=True,
        maximumInfluences=3,
        dropoffRate=4,
        removeUnusedInfluence=False,
    )[0]
    return cmds.rename(sc, name)


def _get_skin_cluster(geometry: str) -> str:
    """Ultimo skinCluster non-prefix nella history (esclude i rig
    archiviati dal rebuild)."""
    found = ""
    for node in cmds.listHistory(geometry) or []:
        if cmds.nodeType(node) == "skinCluster" and not node.startswith("prefix_"):
            found = node
    return found


def _skin_eye_geo(eye_geos, eye_joint: str, side: str):
    """Skinning della geo occhio sull'EyeJoint (MEL 29275-29318, ramo
    single-skinCluster)."""
    for geo in eye_geos:
        existing = _get_skin_cluster(geo)
        if existing:
            influences = cmds.skinCluster(existing, query=True, influence=True) or []
            if eye_joint not in influences:
                cmds.skinCluster(
                    existing, edit=True, lockWeights=True, weight=0, addInfluence=eye_joint
                )
                if cmds.attributeQuery("lockInfluenceWeights", node=eye_joint, exists=True):
                    cmds.setAttr(eye_joint + ".lockInfluenceWeights", 0)
                cmds.skinPercent(existing, geo, transformValue=(eye_joint, 1))
        else:
            cmds.select(eye_joint, geo)
            _new_skin_cluster(eye_joint, geo, "eyeSC" + side)


def _build_aim_master(head_joint: str, face_fit_scale: float, eye_ball_pos):
    """EyeAimSetup + master AimEye_M (MEL 29114-29152)."""
    cmds.createNode("transform", name="EyeAimSetup", parent="EyeSetup")
    cmds.createNode("transform", name="EyeAimFollowHead", parent="EyeAimSetup")
    cmds.createNode("transform", name="EyeAimStatic", parent="EyeAimSetup")
    as_parent_constraint(head_joint, "EyeAimFollowHead", force_mult_matrix=True)
    as_align("EyeAimStatic", head_joint, translate=True, rotate=True)

    # curva a croce del master aim
    curve = cmds.curve(
        degree=1,
        point=[(0, 1, 0), (0, -1, 0), (0, 0, 0), (1, 0, 0), (-1, 0, 0)],
        knot=[0, 1, 2, 3, 4],
    )
    cmds.rename(curve, "AimEye_M")
    shape = cmds.listRelatives("AimEye_M", shapes=True)[0]
    if shape != "AimEye_MShape":
        cmds.rename(shape, "AimEye_MShape")
    cmds.setAttr("AimEye_MShape.overrideEnabled", 1)
    cmds.connectAttr("ctrlBox.AimCtrlVis", "AimEye_MShape.overrideVisibility")
    cmds.setAttr("AimEye_MShape.overrideColor", 17)
    cmds.sets("AimEye_M", add="FaceControlSet")

    cmds.createNode("transform", name="AimAimAt", parent="EyeAimSetup")
    cmds.xform("AimAimAt", worldSpace=True, translation=(0, eye_ball_pos[1], eye_ball_pos[2]))
    cmds.createNode("transform", name="AimEyeOffset_M")
    cmds.createNode("transform", name="AimEyeFollow_M")
    cmds.parent("AimEyeFollow_M", "Aimcontrols")
    as_align("AimEyeFollow_M", head_joint, translate=True, rotate=True)
    cmds.parent("AimEye_M", "AimEyeOffset_M")
    cmds.setAttr(
        "AimEyeOffset_M.s",
        face_fit_scale / 10.0,
        face_fit_scale / 10.0,
        face_fit_scale / 10.0,
        type="float3",
    )
    as_align("AimEyeOffset_M", "AimEyeFollow_M", translate=True)
    cmds.parent("AimEyeOffset_M", "AimEyeFollow_M")
    cmds.xform(
        "AimEyeOffset_M",
        worldSpace=True,
        translation=(0, eye_ball_pos[1], eye_ball_pos[2] + face_fit_scale),
    )
    cmds.createNode("transform", name="AimEyeUpVec")
    cmds.parent("AimEyeUpVec", "EyeAimFollowHead")

    as_parent_constraint_blend("AimEye_M", "AimEyeFollow_M", "EyeAimFollowHead")


def _build_side(
    side: str,
    b: int,
    eye_ball_pos,
    face_fit_scale: float,
    eye_geos,
    opm: bool,
    eye_base: bool = False,
):
    """Costruzione di un lato dell'occhio (MEL 29154-29453, slice 1).

    eye_base attiva il controller-base opzionale (MEL 29170-29399): parent di
    EyeRegion + rete a matrici che fa seguire l'aim al controller EyeBase.
    """
    pos = list(eye_ball_pos)
    if side == "_L":
        if cmds.objExists("FitEyeBallLeft"):
            pos = cmds.xform("FitEyeBallLeft", query=True, worldSpace=True, translation=True)
        else:
            pos[0] = eye_ball_pos[0] * -1

    # EyeBase (opzionale, MEL 29170-29181): controller-base proiettato sulla
    # mesh, diventera' il parent di EyeRegion
    if eye_base:
        create_face_controller("EyeBase", side, 4)
        cmds.delete("EyeBaseJoint" + side)
        cmds.xform("EyeBaseOffset" + side, worldSpace=True, translation=pos)
        cmds.scale(8, 8, 8, "EyeBase" + side + ".cv[0:7]", relative=True, pivot=pos)
        cmds.setAttr("EyeBase" + side + "Shape.overrideColor", 17)
        cmds.parent("EyeBaseOffset" + side, "SideReverse" + side)
        cmds.xform("EyeBaseOffset" + side, objectSpace=True, rotation=(0, 0, 0), scale=(1, 1, 1))
        place_ctrl_by_projection("EyeBase" + side)

    # EyeRegion
    create_face_controller("EyeRegion", side, 4)
    cmds.parent("EyeRegionJoint" + side, "FaceDeformationSystem")
    as_parent_constraint("EyeRegion" + side, "EyeRegionJoint" + side, force_mult_matrix=True)
    cmds.xform("EyeRegionOffset" + side, worldSpace=True, translation=pos)
    cmds.scale(6, 6, 6, "EyeRegion" + side + ".cv[0:7]", relative=True, pivot=pos)
    cmds.parent(
        "EyeRegionOffset" + side, ("EyeBase" + side) if eye_base else ("SideReverse" + side)
    )
    cmds.xform("EyeRegionOffset" + side, objectSpace=True, rotation=(0, 0, 0), scale=(1, 1, 1))
    as_opm_scale_reset("EyeRegionJoint" + side)
    place_ctrl_by_projection("EyeRegion" + side)

    # Eye
    create_face_controller("Eye", side, 3)
    cmds.setAttr("Eye" + side + ".rotateOrder", 2)
    cmds.setAttr("EyeOffset" + side + ".s", 1, 1, 1, type="float3")
    cmds.xform("EyeOffset" + side, worldSpace=True, translation=pos)
    ctrl_pos = cmds.xform("Eye" + side, query=True, worldSpace=True, translation=True)
    cmds.scale(2.16, 2.16, 2.16, "Eye" + side + ".cv[0:7]", relative=True, pivot=ctrl_pos)
    cmds.setAttr("Eye" + side + "Shape.overrideColor", 18)
    cmds.connectAttr("ctrlBox.EyeCtrlVis", "Eye" + side + "Shape.overrideVisibility", force=True)

    # EyeJoint sotto FaceJoint_M
    cmds.select("FaceJoint_M")
    cmds.joint(name="EyeJoint" + side)
    cmds.setAttr("EyeJoint" + side + ".rotateOrder", 2)
    cmds.xform(
        "EyeJoint" + side,
        worldSpace=True,
        translation=(eye_ball_pos[0] * b, eye_ball_pos[1], eye_ball_pos[2]),
    )
    if not cmds.objExists("EyeControls"):
        cmds.createNode("transform", name="EyeControls", parent="OnFacecontrols")
        cmds.parent("EyeControls", "ControlsSetup")
        cmds.xform("EyeControls", scale=(1, 1, 1))
    cmds.parent("EyeOffset" + side, "EyeControls")
    cmds.xform("EyeOffset" + side, objectSpace=True, rotation=(0, 0, 0), scale=(1, 1, 1))
    # orient snapshot da FitEyeBall
    constraint = cmds.orientConstraint("FitEyeBall", "EyeOffset" + side)
    cmds.delete(constraint)
    if side == "_L":
        cmds.setAttr("EyeOffset_L.ry", cmds.getAttr("EyeOffset_L.ry") * -1)

    # snapshot della posa del ctrl nel joint, freeze rotazione
    snap = cmds.parentConstraint("Eye" + side, "EyeJoint" + side)
    cmds.delete(snap)
    cmds.makeIdentity("EyeJoint" + side, apply=True, translate=False, rotate=True, scale=False)
    as_parent_constraint("Eye" + side, "EyeJoint" + side)
    cmds.setAttr("EyeJoint" + side + ".segmentScaleCompensate", 0)
    eye_joint = "EyeJoint" + side

    # geo occhio
    if eye_geos:
        cmds.select(eye_geos[0])
        bb = cmds.xform(query=True, worldSpace=True, boundingBox=True)
        cmds.move(
            0,
            0,
            (bb[5] * 1.1) - pos[2],
            "Eye" + side + ".cv[0:7]",
            relative=True,
            objectSpace=True,
            worldSpaceDistance=True,
        )
        _skin_eye_geo(eye_geos, eye_joint, side)

    # SDK del look: slider -> rotazione occhio
    ds_sdk("ctrlEye" + side + ".tx", "SDKEye" + side + ".ry", 1, 30)
    ds_sdk("ctrlEye" + side + ".tx", "SDKEye" + side + ".ry", -1, -30)
    ds_sdk("ctrlEye" + side + ".ty", "SDKEye" + side + ".rx", 1, -30)
    ds_sdk("ctrlEye" + side + ".ty", "SDKEye" + side + ".rx", -1, 30)

    # AimEye duplicato per lato
    cmds.createNode("transform", name="AimOffsetEye" + side, parent="AimEye_M")
    cmds.setAttr("AimOffsetEye" + side + ".tx", -1 * b)
    cmds.duplicate("AimEye_M", name="AimEye" + side)
    children = (
        cmds.listRelatives("AimEye" + side, children=True, type="transform", fullPath=True) or []
    )
    if children:
        cmds.delete(children)
    cmds.parent("AimEye" + side, "AimOffsetEye" + side, relative=True)
    cmds.connectAttr("ctrlBox.AimCtrlVis", "AimEye" + side + "Shape.overrideVisibility")

    # rete aim
    cmds.createNode("transform", name="EyeAim" + side, parent="EyeOffset" + side)
    if opm:
        cmds.warning(
            "aimMatrix OPM branch for the eye is not ported yet; OPM is off in this build."
        )
    cmds.aimConstraint(
        "AimEye" + side,
        "EyeAim" + side,
        maintainOffset=True,
        aimVector=(0, 0, 1),
        worldUpType="objectrotation",
        worldUpObject="AimEyeUpVec",
        worldUpVector=(0, 1, 0),
    )
    cmds.parent("SDKEye" + side, "EyeAim" + side)

    # EyeBase follow (opzionale, MEL 29374-29401): l'aim segue il controller
    # EyeBase via multMatrix(worldMatrix EyeBase * worldInverse EyeOffset) ->
    # decomposeMatrix -> EyeBaseFollowTS(t,s)/EyeBaseFollowR(r)
    if eye_base:
        cmds.createNode("transform", name="EyeBaseFollowTS" + side, parent="EyeOffset" + side)
        cmds.parent("EyeAim" + side, "EyeBaseFollowTS" + side)
        cmds.createNode("transform", name="EyeBaseFollowR" + side, parent="EyeAim" + side)
        cmds.parent("SDKEye" + side, "EyeBaseFollowR" + side)
        mm = cmds.createNode("multMatrix", name="EyeBaseMM" + side)
        cmds.connectAttr("EyeBase" + side + ".worldMatrix", mm + ".matrixIn[2]")
        cmds.connectAttr("EyeOffset" + side + ".worldInverseMatrix", mm + ".matrixIn[3]")
        dm = cmds.createNode("decomposeMatrix", name="EyeBaseDM" + side)
        cmds.connectAttr(mm + ".matrixSum", dm + ".inputMatrix")
        cmds.connectAttr(dm + ".outputTranslate", "EyeBaseFollowTS" + side + ".t")
        cmds.connectAttr(dm + ".outputScale", "EyeBaseFollowTS" + side + ".s")
        cmds.connectAttr(dm + ".outputRotate", "EyeBaseFollowR" + side + ".r")
        # matrici statiche di offset SideReverse<->EyeOffset via temp transform
        temp = cmds.createNode("transform", name="tempMatrixTransform")
        cmds.parent(temp, "SideReverse" + side)
        cmds.xform(temp, objectSpace=True, translation=(0, 0, 0))
        m = cmds.xform(temp, query=True, objectSpace=True, matrix=True)
        cmds.setAttr(mm + ".matrixIn[1]", *m, type="matrix")
        cmds.parent(temp, "EyeOffset" + side)
        cmds.xform(temp, objectSpace=True, translation=(0, 0, 0))
        m = cmds.getAttr(temp + ".inverseMatrix")
        cmds.setAttr(mm + ".matrixIn[0]", *m, type="matrix")
        cmds.delete(temp)


def face_eye_ball() -> bool:
    """Costruisce l'occhio (parita' asFaceEyeBall, slice 1).

    Presuppone prep + ctrlBox eseguiti (FaceJoint_M, ctrlBox, gli slider
    ctrlEye_R/_L). Ritorna False con warning se manca FitEyeBall o la
    base.
    """
    for node in (FIT_SKELETON, "FaceDeformationSystem", "ctrlBox", "FaceJoint_M", "FaceControlSet"):
        if not cmds.objExists(node):
            cmds.warning("{} not found: run the build prep and ctrlBox first".format(node))
            return False
    if not cmds.objExists("FitEyeBall"):
        cmds.warning("FitEyeBall not found: complete the eye fitting")
        return False

    from .build_utils import as_get_opm

    opm = as_get_opm()
    cyclops = bool(get_fit_option("Cyclops"))
    eye_base = bool(get_fit_option("EyeBase"))
    head_joint = get_fit_option("HeadJoint") or ""
    face_fit_scale = cmds.getAttr(FIT_SKELETON + ".faceScale")

    as_face_hide_controllers(True)
    if cmds.objExists("ctrlBox2"):
        cmds.setAttr("ctrlBox2.v", 0)
    for box in ("ctrlBoxEye_R", "ctrlBoxEye_L"):
        if cmds.objExists(box):
            cmds.setAttr(box + ".v", 1)

    cmds.createNode("transform", name="EyeSetup", parent="FaceDeformationSystem")
    eye_ball_pos = cmds.xform("FitEyeBall", query=True, worldSpace=True, translation=True)

    _build_aim_master(head_joint, face_fit_scale, eye_ball_pos)

    for b in (1, -1):
        side = "_R" if b == 1 else "_L"
        eye_geo_str = (get_fit_option("RightEye") if b == 1 else get_fit_option("LeftEye")) or ""
        eye_geos = [g for g in eye_geo_str.split() if cmds.objExists(g)]
        _build_side(side, b, eye_ball_pos, face_fit_scale, eye_geos, opm, eye_base)

    # Pupil/Iris (MEL:29455)
    if cmds.objExists("FaceFitPupil") or cmds.objExists("FaceFitIris"):
        from .face_pupil_iris import face_pupil_iris

        face_pupil_iris()

    if cyclops:
        for node in ("EyeOffset_R", "EyeRegionOffset_R"):
            cmds.setAttr(node + ".overrideEnabled", 1)
            cmds.setAttr(node + ".overrideVisibility", 0)

    cmds.select(clear=True)
    return True

"""Step di chiusura del build (parita' asFaceFinish, MEL 36735).

Finalizza il rig dopo tutti i componenti: visibilita' di default,
prune dei pesi piccoli, raggio dei joint, spostamento dei constraint
in DeformJointConstraints, FaceControlOrient riportato a FitElement
(FaceFitControlOrient), cancellazione dei nodi temporanei e dei fitter
Left, merge di eyeLidArea, snapshot della build-pose
(faceBuildPose.udAttr), versione su FaceGroup, buildCompleted,
popolamento di FaceAllSet (tutto cio' che il build ha creato, escluso
allBeforeFaceBuild) e rinomina degli unitConversion in *UC.

Include asFaceDsSdk (36679, extra jaw DS che salta senza lip curve) e
asSetIsHistoricallyInteresting (50074). Rinviati (cross-proc o
interattivi, documentati): asFaceExtras (pesatura geo extra, config
senza campo), hook Roblox (ARKit e SnapChat sono collegati qui, via
face_arkit.connect_arkit), reorderDeformers multiSkin, asGoToBuildPose,
asBSConvertDStoBS (RigType BlendShapes), postRebuildScript.

Versione: asGetScriptVersion legge l'header del MEL; qui e' la costante
FACE_RIG_VERSION (target v6.661) usata dai gate di migrazione.
"""

import maya.cmds as cmds

from .build_utils import as_face_hide_controllers
from .driving_system import ds_sdk, ensure_output_blend_weighted
from .face_arkit import connect_arkit
from .fit_options import FIT_SKELETON, get_fit_option

FACE_RIG_VERSION = 6.661

_TEMP_OBJECTS = (
    "tempLocFlip",
    "FaceBuildInProgress",
    "DeformationLayers",
    "SmileBulgePulled",
    "FrownBulgePulled",
)


def face_ds_sdk():
    """Extra DrivingSystem del jaw (parita' asFaceDsSdk, MEL 36679):
    jawForward/jawSide su ctrlMouth_M. Salta senza upperLipMainCurve
    (jaw/lip non costruiti)."""
    if not cmds.objExists("upperLipMainCurve"):
        return
    for attr, sdk, value in (("jawForward", "SDKJaw_M.tz", 2), ("jawSide", "SDKJaw_M.ry", 15)):
        if not cmds.attributeQuery(attr, node="ctrlMouth_M", exists=True):
            cmds.addAttr(
                "ctrlMouth_M",
                keyable=True,
                longName=attr,
                attributeType="double",
                softMaxValue=10,
                hasSoftMaxValue=True,
                softMinValue=-10,
                hasMaxValue=True,
            )
        ensure_output_blend_weighted("ctrlMouth_M." + attr)
        ds_sdk("ctrlMouth_M." + attr, sdk, 10, value)


def set_is_historically_interesting(control_set: str):
    """Marca non-interessanti le history dei membri del set che sono in
    FaceAllSet (parita' asSetIsHistoricallyInteresting, MEL 50074)."""
    all_set = "FaceAllSet" if control_set == "FaceControlSet" else "AllSet"
    if not cmds.objExists(all_set):
        return
    for member in cmds.sets(control_set, query=True) or []:
        history = (
            cmds.listHistory(
                member, future=False, leaf=False, interestLevel=1, pruneDagObjects=True
            )
            or []
        )
        for node in history:
            if not cmds.sets(node, isMember=all_set):
                continue
            if cmds.getAttr(node + ".isHistoricallyInteresting"):
                cmds.setAttr(node + ".isHistoricallyInteresting", 0)


def _set_joint_radii():
    joints = cmds.listRelatives("FaceJoint_M", allDescendents=True, type="joint") or []
    joints.append("FaceJoint_M")
    for joint in joints:
        radius = 0.2
        if "LidMain" in joint or "LipJoint" in joint:
            radius = 0.1
        if cmds.attributeQuery("radius", node=joint, exists=True):
            cmds.setAttr(joint + ".radius", radius)


def _keep_control_orient_as_fit():
    if not cmds.objExists("FaceControlOrient"):
        return
    if not cmds.objExists("FaceFitControlOrient"):
        cmds.createNode("transform", name="FaceFitControlOrient", parent=FIT_SKELETON)
    cmds.parent("FaceControlOrient", "FaceFitControlOrient")
    cmds.setAttr("FaceControlOrient.v", 0)


def _mel_value(value):
    """Il valore come lo scriverebbe il MEL concatenandolo a una stringa:
    bool come 1/0, float senza decimali superflui (6 cifre significative)."""
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, float):
        return "{:.6g}".format(value)
    return value


def _capture_build_pose():
    """faceBuildPose.udAttr = comandi setAttr per ogni attr keyable
    sbloccato dei membri del FaceControlSet (MEL 36834-36844)."""
    if not cmds.objExists("faceBuildPose"):
        return
    commands = []
    # come il MEL: l'ordine e' quello della selezione, non quello del set
    cmds.select(cmds.sets("FaceControlSet", query=True) or [])
    for member in cmds.ls(selection=True) or []:
        for attr in cmds.listAttr(member, keyable=True, shortNames=True) or []:
            plug = "{}.{}".format(member, attr)
            if not cmds.objExists(plug):
                continue
            if cmds.getAttr(plug, lock=True):
                continue
            try:
                value = cmds.getAttr(plug)
            except RuntimeError:
                continue
            commands.append("setAttr {} {};".format(plug, _mel_value(value)))
    cmds.setAttr("faceBuildPose.udAttr", "".join(commands), type="string")


def _update_face_all_set(geometry: str):
    """Popola FaceAllSet con tutto cio' che il build ha creato (MEL
    36854-36868): tutti i nodi meno set/partition/intermediate/
    discendenti del FaceFitSkeleton/membri di allBeforeFaceBuild, piu' i
    set FaceAreas."""
    nodes = set(cmds.ls() or [])
    nodes -= set(cmds.ls(type="objectSet") or [])
    nodes -= set(cmds.ls(type="partition") or [])
    nodes -= set(cmds.ls(type="mesh", intermediateObjects=True) or [])
    nodes -= set(cmds.listRelatives(FIT_SKELETON, allDescendents=True) or [])
    if cmds.objExists("allBeforeFaceBuild"):
        nodes -= set(cmds.sets("allBeforeFaceBuild", query=True) or [])

    members = [n for n in nodes if cmds.objExists(n)]
    members += cmds.sets("FaceAreas", query=True) or []
    if cmds.objExists("FaceAreas"):
        members.append("FaceAreas")
    if members:
        cmds.sets(members, add="FaceAllSet")

    # smonta FaceBuildingSets e i suoi membri
    if cmds.objExists("FaceBuildingSets"):
        if cmds.objExists("allBeforeFaceBuild"):
            cmds.sets("allBeforeFaceBuild", remove="FaceBuildingSets")
        for member in cmds.sets("FaceBuildingSets", query=True) or []:
            if cmds.objExists(member):
                cmds.delete(member)


def _rename_unit_conversions():
    """unitConversion auto-generati in FaceAllSet -> <dest>_UC (MEL
    36870-36877)."""
    for node in cmds.ls(type="unitConversion") or []:
        if not node.startswith("unitConversion"):
            continue
        if not cmds.sets(node, isMember="FaceAllSet"):
            continue
        dest = cmds.listConnections(node, source=True, destination=False, plugs=True) or []
        if dest:
            new_name = dest[0].replace(".", "_") + "UC"
            cmds.rename(node, new_name)


def face_finish() -> bool:
    """Esegue la finalizzazione del build (parita' asFaceFinish).

    Presuppone i componenti costruiti (FaceControlSet, FaceJoint_M,
    allBeforeFaceBuild). Ritorna True a fine corsa.
    """
    if not cmds.objExists(FIT_SKELETON):
        cmds.warning("FaceFitSkeleton not found")
        return False

    non_sym = bool(get_fit_option("NonSym"))
    geometry = get_fit_option("Face") or ""
    skin_cluster = get_fit_option("SkinCluster") or ""

    face_ds_sdk()
    # asFaceExtras (pesatura geo extra) rinviato

    # visibilita' di default
    as_face_hide_controllers(False)
    if cmds.objExists("ctrlBox2"):
        cmds.setAttr("ctrlBox2.v", 1)
    if cmds.objExists("ctrlBox"):
        if cmds.attributeQuery("EyeCtrlVis", node="ctrlBox", exists=True):
            cmds.setAttr("ctrlBox.EyeCtrlVis", 0)
        if cmds.attributeQuery("AimCtrlVis", node="ctrlBox", exists=True):
            cmds.setAttr("ctrlBox.AimCtrlVis", 1)

    # asFaceLockWeights 0
    from .face_prep import _lock_all_influence_weights

    _lock_all_influence_weights(False)

    # prune pesi piccoli
    if skin_cluster and cmds.objExists(skin_cluster) and cmds.objExists(geometry):
        try:
            cmds.skinPercent(skin_cluster, geometry, pruneWeights=0.01)
        except RuntimeError:
            pass

    _set_joint_radii()

    # constraint sotto DeformJointConstraints
    constraints = cmds.listRelatives("FaceJoint_M", allDescendents=True, type="constraint") or []
    if constraints and cmds.objExists("DeformJointConstraints"):
        cmds.parent(constraints, "DeformJointConstraints")

    _keep_control_orient_as_fit()

    for node in _TEMP_OBJECTS:
        if cmds.objExists(node):
            cmds.delete(node)

    # fitter Left temporanei (solo in modalita' simmetrica)
    if not non_sym:
        for child in cmds.listRelatives(FIT_SKELETON, children=True, type="transform") or []:
            if child.endswith("Left"):
                cmds.delete(child)

    # merge eyeLidArea & eyeLidAreaLeft
    if cmds.objExists("eyeLidAreaLeft"):
        members = cmds.sets("eyeLidAreaLeft", query=True) or []
        if members and cmds.objExists("eyeLidArea"):
            cmds.sets(members, add="eyeLidArea")
        cmds.delete("eyeLidAreaLeft")

    # controller ARKit / SnapChat (MEL:36819-36825); RobloxHead non portato
    if get_fit_option("ARKit") or get_fit_option("SnapChat"):
        connect_arkit()
    if get_fit_option("RobloxHead"):
        cmds.warning("face_finish: RobloxHead (asFaceRobloxHead) is not ported")

    _capture_build_pose()

    # versione
    if not cmds.attributeQuery("version", node="FaceGroup", exists=True):
        cmds.addAttr("FaceGroup", longName="version", attributeType="double")
    cmds.setAttr("FaceGroup.version", lock=False)
    cmds.setAttr("FaceGroup.version", FACE_RIG_VERSION)
    cmds.setAttr("FaceGroup.version", lock=True)

    try:
        cmds.setAttr(FIT_SKELETON + ".buildCompleted", 1)
    except RuntimeError:
        pass

    _update_face_all_set(geometry)
    _rename_unit_conversions()

    # asGoToBuildPose rinviato

    # ripristina eventuali deltaMush
    for node in cmds.listHistory(geometry) or []:
        if cmds.nodeType(node) == "deltaMush":
            cmds.setAttr(node + ".envelope", 1)

    set_is_historically_interesting("FaceControlSet")

    # RigType BlendShapes / postRebuildScript rinviati

    try:
        cmds.cycleCheck(evaluation=True)
    except (RuntimeError, TypeError):
        pass

    if cmds.objExists("allBeforeFaceBuild"):
        cmds.sets(clear="allBeforeFaceBuild")
        cmds.delete("allBeforeFaceBuild")

    cmds.select(clear=True)
    print("// Advanced Face created")
    return True

"""Prep del build facciale (parita' asFacePrep, righe MEL 27941-28554).

Tutto cio' che il build presuppone prima del primo componente:
validazioni d'ingresso, migrazioni dei fitting legacy, pulizia dei
residui di build falliti, duplicazione del fitting a sinistra,
rigenerazione dello skinCluster, il set allBeforeFaceBuild, la base
strutturale (ensure_advanced_base), FaceJoint_M, i teethSets, il
cilindro FaceControlOrient e il percorso di rebuild (rinomina del rig
esistente in prefix_* + asFaceSkinWeightsHolder per il recupero pesi).

Gli `error` del MEL diventano warning + return False (contratto del
repo). Divergenze sanzionate rispetto al MEL:
- il weights holder del rebuild nasce da `duplicate` della Face invece
  del giro connectAttr/refresh/disconnectAttr (che non baka in batch);
- la duplicazione a sinistra salta i figli gia' suffissati "Left"
  (il MEL su un build fallito creerebbe doppioni *LeftLeft);
- FaceMotionSystem/FaceDeformationSystem/FaceJoint_M vengono rinominati
  prefix_* esplicitamente: nel MEL accade via FaceAllSet, popolato da
  asFaceFinish che non e' ancora a parita';
- la migrazione ForeHead senza directionChecked emette un warning e
  prosegue (il MEL ricostruisce il fit via UI re-select);
- i passaggi solo-UI (asModelChecker, dialog Maya LT, checkbox OPM)
  sono omessi o ridotti all'effetto persistito in scena.
"""

from typing import List, Optional

import maya.cmds as cmds

from .advanced_base import ensure_advanced_base
from .build_utils import as_align, as_lock_attr
from .fit_options import FIT_SKELETON, get_fit_option, set_fit_option

# figli di FaceFitSkeleton di mezzeria: mai duplicati a sinistra
_MIDDLE_FITS = (
    "FaceFitNose",
    "FaceFitNoseUnder",
    "FaceFitNoseBridge",
    "FaceFitJaw",
    "FaceFitChinCrease",
    "FaceFitThroat",
)

_REQUIRED_BASE = ["FitEyeBall", "FaceFitEyeLidOuter", "FaceFitEyeLidMain", "FaceFitEyeLidInner"]
_REQUIRED_BELOW_EYES = [
    "FaceFitLipOuter",
    "FaceFitLipMain",
    "FaceFitLipInner",
    "FaceFitJawPivot",
    "FaceFitJawCorner",
    "FaceFitJawLine",
    "FaceFitJaw",
    "FaceFitChinCrease",
    "FaceFitThroat",
    "FaceFitCheek",
    "FaceFitCheekBone",
    "FaceFitSmileBulge",
    "FaceFitFrownBulge",
    "FaceFitNose",
    "FaceFitNoseUnder",
    "FaceFitNoseCorner",
    "FaceFitNoseSide",
    "FaceFitNoseBridge",
    "FaceFitNostril",
]
_REQUIRED_ABOVE_EYES = [
    "FaceFitEyeBrowInner",
    "FaceFitEyeBrowOuter",
    "FaceFitEyeBrowCenter",
    "FaceFitForeHead",
]

# residui di un build fallito, rimossi quando buildCompleted e' a 0
_LEFTOVER_NODES = (
    "FaceAllSet",
    "FaceControlSet",
    "FaceAreas",
    "FaceBuildingSets",
    "eyeLidArea",
    "eyeLidAreaLeft",
    "lipArea",
    "lipFalloffArea",
    "lipFalloffAreaMax",
    "lowerTeethSet",
    "upperTeethSet",
    "FaceMusclesLayer",
    "lowerOS2WSTG_L",
    "lowerOS2WSTG_R",
    "allBeforeFaceBuild",
    "FaceMotionSystem",
    "FaceDeformationSystem",
    "FaceBuildInProgress",
    "FaceJoint_M",
)

# nomi che il build creera': devono essere liberi
_RESERVED_NAMES = ("Nose_M", "Eye_R", "Eye1_R", "Eye_L", "Eye1_L")


def include_above_eyes() -> bool:
    """Parita' asFaceIncludeAboveEyes."""
    return get_fit_option("Include") not in ("Skip Above Eyes", "Skip Above+Below Eyes")


def include_below_eyes() -> bool:
    """Parita' asFaceIncludeBelowEyes."""
    return get_fit_option("Include") not in ("Skip Below Eyes", "Skip Above+Below Eyes")


def get_max_influences() -> int:
    """Parita' asFaceGetMaxInfluences: 4/8 se GameEngine+UseMaxInf."""
    if get_fit_option("GameEngine") and get_fit_option("UseMaxInf"):
        return int(get_fit_option("MaxInf"))
    return 0


def set_fixed_wrap_options():
    """Parita' asSetFixedWrapOptions: optionVar per i wrap del build."""
    cmds.optionVar(intValue=("autoWeightThreshold", 1))
    cmds.optionVar(intValue=("exclusiveBind", 0))
    cmds.optionVar(intValue=("renderInfl", 1))
    cmds.optionVar(stringValue=("falloffMode", "volume"))


def _get_skin_cluster(obj: str) -> str:
    """Parita' asGetSkinCluster: ultimo skinCluster nella history."""
    found = ""
    for node in cmds.listHistory(obj, pruneDagObjects=True, interestLevel=2) or []:
        if cmds.nodeType(node) == "skinCluster":
            found = node
    return found


def _lock_all_influence_weights(lock: bool):
    """Parita' asFaceLockWeights: su TUTTI i joint della scena."""
    for joint in cmds.ls(type="joint") or []:
        if cmds.attributeQuery("lockInfluenceWeights", node=joint, exists=True):
            cmds.setAttr(joint + ".lockInfluenceWeights", int(lock))


def _remove_unused_influences(skin_cluster: str):
    """removeUnusedForSkin ridotto: stacca le influence a peso zero."""
    if not skin_cluster or not cmds.objExists(skin_cluster):
        return
    weighted = set(cmds.skinCluster(skin_cluster, query=True, weightedInfluence=True) or [])
    for influence in cmds.skinCluster(skin_cluster, query=True, influence=True) or []:
        if influence not in weighted:
            try:
                cmds.skinCluster(skin_cluster, edit=True, removeInfluence=influence)
            except RuntimeError:
                pass


def _delete_intermediate_shapes(node: str):
    for shape in cmds.listRelatives(node, shapes=True, fullPath=True) or []:
        if cmds.getAttr(shape + ".intermediateObject"):
            cmds.delete(shape)


def _delete_unused_intermediate_shapes(geometry: str):
    """Shape intermedie non collegate a deformer: via (MEL 28261-28283)."""
    for shape in cmds.listRelatives(geometry, shapes=True, fullPath=True) or []:
        if not cmds.getAttr(shape + ".intermediateObject"):
            continue
        connected_to_deformer = False
        for node in cmds.listConnections(shape) or []:
            if cmds.nodeType(node) not in ("shadingEngine", "objectSet"):
                connected_to_deformer = True
                break
        if not connected_to_deformer:
            print('// Removing un-used intermediate shape:"{}"'.format(shape))
            cmds.delete(shape)


def _required_fits(non_symmetrical: bool) -> List[str]:
    required = list(_REQUIRED_BASE)
    if include_below_eyes():
        required += _REQUIRED_BELOW_EYES
    if include_above_eyes():
        required += _REQUIRED_ABOVE_EYES
    if non_symmetrical:
        # nel MEL la lista Left dipende dallo stato della UI; in headless
        # si richiede il lato sinistro per ogni fit non di mezzeria
        for obj in list(required):
            if obj.endswith("Center") or obj in _MIDDLE_FITS:
                continue
            required.append(obj + "Left")
    return required


def _validate(
    geometry: str,
    all_face_geo: List[str],
    right_eye: str,
    left_eye: str,
    non_symmetrical: bool,
    tongue: str,
) -> bool:
    """Le validazioni d'ingresso (error nel MEL -> warning+False)."""
    if not cmds.attributeQuery("faceScale", node=FIT_SKELETON, exists=True):
        cmds.warning('Mask not defined. Choose "Mask" in the Pre section, by selecting polygons.')
        return False
    if not geometry:
        cmds.warning('"Face" object not choosen')
        return False
    if not all_face_geo:
        cmds.warning('"All Head" objects not choosen')
        return False
    if not right_eye:
        cmds.warning('"Right Eye" object not choosen')
        return False
    if not left_eye:
        cmds.warning('"Left Eye" object not choosen')
        return False
    if cmds.objExists("prefix_FaceGroup"):
        cmds.warning(
            'Object "prefix_FaceGroup" found, which means a '
            "previous build failed. Try to Undo previous build, "
            "to restore functional FaceSetup"
        )
        return False

    # v5.9414: NoseCenter -> NoseBridge (prima del check dei richiesti)
    if cmds.objExists("FaceFitNoseCenter"):
        print(
            "// FaceFitNoseCenter detected, as of v5.9414, this is "
            "called NoseBridge, now automatically renaming this."
        )
        for node in cmds.ls("*NoseCenter*", type="transform") or []:
            cmds.rename(node, node.replace("NoseCenter", "NoseBridge"))

    for obj in _required_fits(non_symmetrical):
        if not cmds.objExists(obj):
            cmds.warning(
                'Object:"{}" does not exists, the Face>Fit section must be completed.'.format(obj)
            )
            return False

    if (
        non_symmetrical
        and cmds.objExists("upperLipOuterCurve")
        and not cmds.objExists("upperLipOuterCurveLeft")
    ):
        cmds.warning(
            "Lip-Fitting was done before Non-Symmetrical was "
            "turned On. Delete the current lip-Fitting and re-do "
            "the Fitting for Non-Symmetrical model."
        )
        return False

    if tongue and not cmds.objExists("Tongue0"):
        cmds.warning(
            "Tongue geometry chosen, But Tongue Locators are "
            'missing. Open the "*Optional tongue" section, and '
            'click the "Tongue" button.'
        )
        return False

    if "decomposeMatrix" not in (cmds.allNodeTypes() or []):
        try:
            cmds.loadPlugin("matrixNodes", quiet=True)
        except RuntimeError:
            pass
        if "decomposeMatrix" not in (cmds.allNodeTypes() or []):
            cmds.warning(
                "AdvancedSkeleton FaceSetup required Node Type "
                '"decomposeMatrix": turn On the '
                '"matrixNodes.mll" plugin.'
            )
            return False
    return True


def _migrate_legacy_fits(rig_type: str, non_symmetrical: bool, geometry: str):
    """Migrazioni dei fitting legacy (MEL 28048-28095)."""
    if rig_type == "BlendShapes" and cmds.objExists("FaceFitUpMidLo"):
        cmds.warning('Current selected RigType does not work with "UpMidLo", now removing this.')
        cmds.delete("FaceFitUpMidLo")

    # v>5.9212 SmileLine e v>5.9418 CheekRaiser non si usano piu'
    for name in (
        "FaceFitSmileLine",
        "FaceFitSmileLineLeft",
        "FaceFitCheekRaiser",
        "FaceFitCheekRaiserLeft",
    ):
        if cmds.objExists(name):
            cmds.delete(name)

    pre_rebuild = get_fit_option("preRebuildScript")
    if pre_rebuild:
        try:
            import maya.mel as mel

            mel.eval(pre_rebuild)
        except RuntimeError as exc:
            cmds.warning("preRebuildScript failed: {}".format(exc))

    # 5.9414: direzione curva richiesta; il MEL ricostruisce il fit via
    # re-select UI, qui si segnala soltanto (divergenza documentata)
    if cmds.objExists("FaceFitForeHead") and not cmds.attributeQuery(
        "directionChecked", node="FaceFitForeHead", exists=True
    ):
        cmds.warning(
            "FaceFitForeHead was made with an older version "
            'without "direction" requirements: re-do the '
            "ForeHead fitting before building."
        )

    # comando run vagante: da non tenere se non esiste un rig completo
    if not cmds.objExists("FaceMotionSystem"):
        if cmds.attributeQuery("run", node=FIT_SKELETON, exists=True):
            cmds.setAttr(FIT_SKELETON + ".run", "", type="string")


def _cleanup_previous_attempt(all_face_geo: List[str]) -> bool:
    """Residui di build falliti via, se buildCompleted e' a 0.

    Ritorna True se il build precedente risultava completato."""
    if not cmds.attributeQuery("buildCompleted", node=FIT_SKELETON, exists=True):
        cmds.addAttr(
            FIT_SKELETON,
            keyable=False,
            longName="buildCompleted",
            attributeType="bool",
            defaultValue=0,
        )
    if cmds.getAttr(FIT_SKELETON + ".buildCompleted"):
        return True

    found_leftover = False
    for name in _LEFTOVER_NODES:
        if cmds.objExists(name):
            if not found_leftover:
                print(
                    "// Detected leftover nodes from previous FaceBuild "
                    "attempt, now removing these:"
                )
            print(name)
            cmds.delete(name)
            found_leftover = True
    if found_leftover:
        for geo in all_face_geo:
            sc = _get_skin_cluster(geo)
            if sc:
                cmds.select(geo)
                cmds.skinPercent(sc, normalize=True)
                cmds.dgdirty(allPlugs=True)
    return False


def _duplicate_fitting_to_left():
    """Specchia il fitting a sinistra (MEL 28238-28259)."""
    children = cmds.listRelatives(FIT_SKELETON, children=True, type="transform") or []
    for child in children:
        if child.endswith("Center") or child in _MIDDLE_FITS:
            continue
        if child.endswith("Left"):  # evita doppioni *LeftLeft
            continue
        if cmds.objExists(child + "Left"):
            cmds.delete(child + "Left")
        cmds.duplicate(child, name=child + "Left")
        cmds.setAttr(child + "Left.sx", -1 * cmds.getAttr(child + ".sx"))
        descendants = (
            cmds.listRelatives(child + "Left", allDescendents=True, type="transform", fullPath=True)
            or []
        )
        # dal piu' profondo: la rinomina non invalida i path successivi
        for path in sorted(descendants, key=lambda p: p.count("|"), reverse=True):
            cmds.rename(path, path.split("|")[-1] + "Left")


def _new_skin_cluster(joints: List[str], geometry: str, name: Optional[str] = None) -> str:
    """newSkinCluster MEL: tsb, maxInf 3, dropoff 4, no removeUnused."""
    kwargs = dict(
        toSelectedBones=True, maximumInfluences=3, dropoffRate=4, removeUnusedInfluence=False
    )
    if name:
        kwargs["name"] = name
    return cmds.skinCluster(joints + [geometry], **kwargs)[0]


def _regenerate_skin_cluster(geometry: str, skin_cluster: str) -> str:
    """Ricrea lo skinCluster della Face (MEL 28425-28447): il vecchio puo'
    avere .bindPreMatrix di taglia sbagliata da build precedenti."""
    cmds.duplicate(geometry, name="newSkinClusterLayer")
    as_lock_attr("newSkinClusterLayer", False, False, False, False)
    cmds.sets("newSkinClusterLayer", edit=True, forceElement="initialShadingGroup")
    _delete_intermediate_shapes("newSkinClusterLayer")
    influences = (
        cmds.listConnections(skin_cluster + ".matrix", source=True, destination=False, type="joint")
        or []
    )
    layer_sc = _new_skin_cluster(influences, "newSkinClusterLayer", name="newSkinClusterSC")
    cmds.copySkinWeights(
        sourceSkin=skin_cluster,
        destinationSkin=layer_sc,
        noMirror=True,
        surfaceAssociation="closestPoint",
        influenceAssociation="closestJoint",
    )
    cmds.delete(skin_cluster)
    new_sc = _new_skin_cluster(influences, geometry)
    new_sc = cmds.rename(new_sc, skin_cluster)
    cmds.copySkinWeights(
        sourceSkin=layer_sc,
        destinationSkin=new_sc,
        noMirror=True,
        surfaceAssociation="closestPoint",
        influenceAssociation="closestJoint",
    )
    cmds.delete("newSkinClusterLayer")
    if cmds.objExists("asFaceDeltaMush"):
        try:
            cmds.reorderDeformers("asFaceDeltaMush", new_sc, geometry)
        except RuntimeError:
            pass
    return new_sc


def _prepare_rebuild(
    geometry: str,
    all_face_geo: List[str],
    head_joint: str,
    skin_cluster: str,
    keep_all: bool,
    keep_custom_controls: bool,
):
    """Percorso rebuild (MEL 28304-28417): accantona il rig esistente in
    prefix_* e conserva i pesi in asFaceSkinWeightsHolder."""
    # asGoToBuildPose non ancora a parita' (catchQuiet anche nel MEL)

    cmds.createNode("transform", name="prefix_FaceGroup")
    cmds.setAttr("prefix_FaceGroup.v", 0)
    cmds.addAttr("prefix_FaceGroup", longName="version", attributeType="double")
    version = 0.0
    if cmds.attributeQuery("version", node="FaceGroup", exists=True):
        version = cmds.getAttr("FaceGroup.version")
    cmds.setAttr("prefix_FaceGroup.version", version)
    cmds.setAttr("prefix_FaceGroup.version", lock=True)

    # SkinWeightsHolder: copia della Face (il giro connect/refresh/
    # disconnect del MEL non baka la mesh in batch)
    cmds.duplicate(geometry, name="asFaceSkinWeightsHolder")
    as_lock_attr("asFaceSkinWeightsHolder", False, False, False, False)
    _delete_intermediate_shapes("asFaceSkinWeightsHolder")
    # il MEL crea l'holder come polySphere (MEL:28315): la shape si chiama
    # come il transform, non come la shape della Face duplicata
    for shape in cmds.listRelatives("asFaceSkinWeightsHolder", shapes=True, fullPath=True) or []:
        cmds.rename(shape, "asFaceSkinWeightsHolderShape")
    influences = (
        cmds.listConnections(skin_cluster + ".matrix", source=True, destination=False, type="joint")
        or []
    )
    holder_sc = _new_skin_cluster(
        influences, "asFaceSkinWeightsHolder", name="asFaceSkinWeightsHolderSC"
    )
    cmds.parent("asFaceSkinWeightsHolder", "prefix_FaceGroup")
    cmds.copySkinWeights(
        sourceSkin=skin_cluster,
        destinationSkin=holder_sc,
        noMirror=True,
        surfaceAssociation="closestPoint",
        influenceAssociation="closestJoint",
    )

    if (keep_all or keep_custom_controls) and cmds.objExists("FaceCustomSystem"):
        cmds.parent("FaceCustomSystem", world=True)

    # cambio RigType da BlendShapes a Joints: BS e holder non servono
    if get_fit_option("RigType") == "Joints":
        face_bs = cmds.ls("asFaceBS*", type="blendShape") or []
        if face_bs:
            cmds.delete(face_bs)
            cmds.delete("asFaceSkinWeightsHolder")

    # ripesa i vecchi FaceJoints sull'HeadJoint
    _lock_all_influence_weights(True)
    if cmds.attributeQuery("lockInfluenceWeights", node=head_joint, exists=True):
        cmds.setAttr(head_joint + ".lockInfluenceWeights", 0)
    for node in cmds.listConnections(skin_cluster + ".matrix") or []:
        if cmds.objExists("FaceAllSet") and cmds.sets(node, isMember="FaceAllSet"):
            cmds.setAttr(node + ".lockInfluenceWeights", 0)
    try:
        cmds.skinPercent(skin_cluster, geometry, transformValue=(head_joint, 1.0))
    except RuntimeError:
        pass
    _remove_unused_influences(skin_cluster)
    _lock_all_influence_weights(False)
    for geo in all_face_geo:
        if geo == geometry:
            continue
        sc = _get_skin_cluster(geo)
        if not sc:
            continue
        try:
            cmds.skinPercent(sc, geo, transformValue=(head_joint, 1.0))
        except RuntimeError:
            pass
        _remove_unused_influences(sc)

    # bwSDK creati con "Drive From Selected": le animCurve in FaceAllSet
    for bw in cmds.ls("bwSDK*") or []:
        if cmds.objExists("AllSet") and cmds.sets(bw, isMember="AllSet"):
            continue  # DrivingSystem del body
        dest = cmds.listConnections(bw, source=False, destination=True) or []
        if dest:
            long_name = (cmds.ls(dest[0], long=True) or [""])[0]
            if long_name.startswith("|Group|MotionSystem|"):
                continue  # parte del MotionSystem del body
        if cmds.objExists("FaceAllSet") and cmds.sets(bw, isMember="FaceAllSet"):
            continue
        for curve in (
            cmds.listConnections(
                bw, skipConversionNodes=True, source=True, destination=False, type="animCurve"
            )
            or []
        ):
            if not cmds.sets(curve, isMember="FaceAllSet"):
                cmds.sets(curve, add="FaceAllSet")

    if cmds.objExists("SquashSetup"):
        cmds.createNode("transform", name="prefix_SquashSetup", parent="prefix_FaceGroup")
        if cmds.attributeQuery("optimizedSquash", node="SquashSetup", exists=True):
            cmds.addAttr(
                "prefix_SquashSetup",
                keyable=False,
                longName="optimizedSquash",
                attributeType="bool",
                defaultValue=True,
            )
        if cmds.objExists("SquashSet"):
            cmds.warning(
                "SquashSetup found: asDeleteHeadSquash not ported yet, leaving squash in place."
            )
        else:  # vecchio squash (pre 5.750)
            for node in ("SquashSetup", "SquashControls", "squashFfd"):
                if cmds.objExists(node):
                    cmds.delete(node)

    # rinomina in prefix_*: i membri di FaceAllSet, i set stessi e i nodi
    # top del rig (nel MEL questi ultimi arrivano via FaceAllSet)
    members = cmds.sets("FaceAllSet", query=True) or []
    members += ["FaceAllSet", "FaceControlSet", "FaceAreas"]
    for member in members:
        if cmds.objExists(member) and not member.startswith("prefix_"):
            cmds.rename(member, "prefix_" + member)
    for node in ("FaceMotionSystem", "FaceDeformationSystem", "FaceJoint_M"):
        if cmds.objExists(node):
            cmds.rename(node, "prefix_" + node)
    cmds.parent("prefix_FaceMotionSystem", "prefix_FaceDeformationSystem", "prefix_FaceGroup")
    descendants = (
        cmds.listRelatives("prefix_FaceGroup", allDescendents=True, type="transform", fullPath=True)
        or []
    )
    for path in sorted(descendants, key=lambda p: p.count("|"), reverse=True):
        short = path.split("|")[-1]
        if not short.startswith("prefix_"):
            cmds.rename(path, "prefix_" + short)

    # i nodi DG del rig archiviato (MM/DM del follow, scala globale): nel
    # MEL arrivano via FaceAllSet, qui si raggiungono dalle connessioni;
    # senza rinomina il nuovo build aggancerebbe i vecchi nodi omonimi
    dg_nodes = set()
    if cmds.objExists("MainAndHeadScaleMultiplyDivide"):
        dg_nodes.add("MainAndHeadScaleMultiplyDivide")
    transforms = (
        cmds.listRelatives("prefix_FaceGroup", allDescendents=True, type="transform", fullPath=True)
        or []
    )
    for trans in transforms:
        for node in cmds.listConnections(trans, source=True, destination=False) or []:
            if cmds.nodeType(node) in ("multMatrix", "decomposeMatrix"):
                dg_nodes.add(node)
                for upstream in cmds.listConnections(node, source=True, destination=False) or []:
                    if cmds.nodeType(upstream) == "multMatrix":
                        dg_nodes.add(upstream)
    for node in dg_nodes:
        if not node.startswith("prefix_"):
            cmds.rename(node, "prefix_" + node)


def _create_face_joint(head_joint: str, scale: float, multi_skin_clusters: bool):
    """FaceJoint_M (MEL 28471-28487)."""
    cmds.select(clear=True)
    cmds.joint(name="FaceJoint_M")
    cmds.setAttr("FaceJoint_M.drawStyle", 2)  # none: meno rumore visivo
    as_align("FaceJoint_M", head_joint, translate=True)
    cmds.move(0, 0, scale * 0.1, "FaceJoint_M", relative=True)
    if multi_skin_clusters:
        cmds.parent("FaceJoint_M", "DeformationSystem")
        cmds.setAttr("FaceJoint_M.inheritsTransform", 0)
        cmds.setAttr("FaceJoint_M.inheritsTransform", lock=True)
        if cmds.objExists("Main") and cmds.attributeQuery("jointVis", node="Main", exists=True):
            cmds.connectAttr("Main.jointVis", "FaceJoint_M.v")
    else:
        cmds.parent("FaceJoint_M", head_joint)
    cmds.setAttr("FaceJoint_M.segmentScaleCompensate", 0)


def _create_teeth_sets(upper_teeth: str, lower_teeth: str):
    """upperTeethSet/lowerTeethSet per il tracking dei denti cut-out."""
    cmds.sets(name="upperTeethSet", empty=True)
    cmds.sets(name="lowerTeethSet", empty=True)
    cmds.sets("upperTeethSet", "lowerTeethSet", add="FaceBuildingSets")
    if upper_teeth:
        cmds.sets(upper_teeth.split(), add="upperTeethSet")
    if lower_teeth:
        cmds.sets(lower_teeth.split(), add="lowerTeethSet")


def _create_control_orient(scale: float):
    """Cilindro FaceControlOrient (MEL 28523-28542)."""
    if not cmds.objExists("FaceControlOrient"):
        cmds.cylinder(
            name="FaceControlOrient",
            pivot=(0, 0, 0),
            axis=(0, 1, 0),
            startSweep=0,
            endSweep=180,
            radius=1,
            heightRatio=2,
            degree=3,
            useTolerance=False,
            tolerance=0.01,
            sections=8,
            spans=1,
            constructionHistory=False,
        )
        if cmds.objExists("asRedSG"):
            cmds.sets("FaceControlOrient", edit=True, forceElement="asRedSG")
        cmds.scale(
            0.5, 0.5, 0.5, "FaceControlOrient.cv[0:99][0:99]", relative=True, pivot=(0, 0, 0)
        )
        cmds.move(
            0,
            0.5,
            0,
            "FaceControlOrient.cv[0:99][0:99]",
            relative=True,
            objectSpace=True,
            worldSpaceDistance=True,
        )
        pos_a = cmds.xform(
            "FaceFitSkeletonCircleShape.cv[0]", query=True, worldSpace=True, translation=True
        )
        pos_b = cmds.xform(
            "FaceFitSkeletonHeightShape.cv[0]", query=True, worldSpace=True, translation=True
        )
        if cmds.objExists("JawPivot"):
            pos_c = cmds.xform("JawPivot", query=True, worldSpace=True, translation=True)
        else:
            pos_c = cmds.xform(
                "FaceFitSkeletonCircleShape.cv[5]", query=True, worldSpace=True, translation=True
            )
        if cmds.objExists("NoseUnder"):
            pos_d = cmds.xform("NoseUnder", query=True, worldSpace=True, translation=True)
        else:
            pos_d = cmds.xform(
                "FaceFitSkeletonCircleShape.cv[6]", query=True, worldSpace=True, translation=True
            )
        cmds.xform("FaceControlOrient", worldSpace=True, translation=(0, pos_a[1], pos_c[2]))
        cmds.scale(
            pos_c[0] * 2,
            pos_b[1] - pos_a[1],
            (pos_d[2] - pos_c[2]) * 2,
            "FaceControlOrient",
            relative=True,
        )
    else:
        try:
            cmds.parent("FaceControlOrient", world=True)
        except RuntimeError:
            pass
    cmds.refresh()
    cmds.parent("FaceControlOrient", "FaceBuildInProgressHidden")


def face_prep(keep_all: bool = False, keep_custom_controls: bool = False) -> bool:
    """Esegue il prep del build (parita' asFacePrep).

    Args:
        keep_all: conserva tutto il custom del rig precedente (rebuild).
        keep_custom_controls: conserva FaceCustomSystem (rebuild).

    Returns:
        True se il prep e' andato a buon fine.
    """
    if not cmds.objExists(FIT_SKELETON):
        cmds.warning("FaceFitSkeleton not found: run the fitting first")
        return False

    geometry = get_fit_option("Face") or ""
    all_face_geo = (get_fit_option("AllHead") or "").split()
    right_eye = get_fit_option("RightEye") or ""
    left_eye = get_fit_option("LeftEye") or ""
    upper_teeth = get_fit_option("UpperTeeth") or ""
    lower_teeth = get_fit_option("LowerTeeth") or ""
    tongue = get_fit_option("Tongue") or ""
    head_joint = get_fit_option("HeadJoint") or ""
    skin_cluster = get_fit_option("SkinCluster") or ""
    non_symmetrical = bool(get_fit_option("NonSym"))
    multi_skin_clusters = bool(get_fit_option("MultiSkinClusters"))
    rig_type = get_fit_option("RigType")

    if not _validate(geometry, all_face_geo, right_eye, left_eye, non_symmetrical, tongue):
        return False

    _migrate_legacy_fits(rig_type, non_symmetrical, geometry)

    scale = cmds.getAttr(FIT_SKELETON + ".faceScale")

    if not cmds.objExists(head_joint):
        cmds.warning(
            'headJoint:"{}" does not exist, you need to "Choose Head Joint".'.format(head_joint)
        )
        return False
    if not cmds.objExists(skin_cluster):
        cmds.warning(
            'skinCluster:"{}" does not exist, you might need re-choose the "Face" object.'.format(
                skin_cluster
            )
        )
        return False
    if not cmds.listConnections(head_joint + ".worldMatrix"):
        cmds.warning(
            'headJoint:"{}" is not connected to a SkinCluster, '
            "choose the correct headJoint (the joint that is "
            "skin-weighted to the face)".format(head_joint)
        )
        return False

    if multi_skin_clusters:
        # nel MEL accende la checkbox OPM del body e salva il prep
        print(
            '// OffsetParentMatrix required for "multiSkinClusters", '
            "now turing ON OffsetParentMatrix."
        )
        if cmds.objExists("FitSkeleton"):
            if not cmds.attributeQuery("useOffsetParentMatrix", node="FitSkeleton", exists=True):
                cmds.addAttr(
                    "FitSkeleton",
                    longName="useOffsetParentMatrix",
                    attributeType="bool",
                    defaultValue=1,
                )
            cmds.setAttr("FitSkeleton.useOffsetParentMatrix", 1)

    # assist del fitting rimasti in scena
    for name in ("upperTempSoftModHandle", "lowerTempSoftModHandle"):
        if cmds.objExists(name):
            cmds.delete(name)

    for geo in all_face_geo:
        if "|" in geo:
            cmds.warning(
                'Selected object: "{}" does not have a unique '
                "name, rename to a unique name.".format(geo)
            )
            return False
        if not cmds.objExists(geo):
            cmds.warning(
                'Did not find All-Head object:"{}", you need to re-choose AllHead objects.'.format(
                    geo
                )
            )
            return False
        if not _get_skin_cluster(geo):
            cmds.warning('Did not find skinCluster on All-Head object:"{}"'.format(geo))
            return False

    try:
        cmds.softSelect(edit=True, softSelectEnabled=False)
        if cmds.symmetricModelling(query=True, symmetry=True):
            cmds.symmetricModelling(edit=True, symmetry=False)
    except RuntimeError:
        pass

    # niente smooth-preview: piu' veloce e meno memoria
    cmds.select(all_face_geo)
    try:
        cmds.displaySmoothness(
            divisionsU=0, divisionsV=0, pointsWire=4, pointsShaded=1, polygonObject=1
        )
    except RuntimeError:
        pass
    cmds.select(clear=True)

    _cleanup_previous_attempt(all_face_geo)

    if cmds.getAttr(skin_cluster + ".maintainMaxInfluences"):
        cmds.setAttr(skin_cluster + ".maintainMaxInfluences", 0)
    if cmds.getAttr(skin_cluster + ".normalizeWeights") != 1:
        cmds.setAttr(skin_cluster + ".normalizeWeights", 1)

    if cmds.objExists("Main") and cmds.attributeQuery("jointVis", node="Main", exists=True):
        cmds.setAttr("Main.jointVis", 0)

    # specchia il fitting a sinistra (o mostra entrambi i lati)
    if non_symmetrical:
        children = cmds.listRelatives(FIT_SKELETON, children=True, type="transform") or []
        for child in children:
            cmds.setAttr(child + ".v", 1)
    else:
        _duplicate_fitting_to_left()

    _delete_unused_intermediate_shapes(geometry)

    # cached-playback off (Maya 2019+)
    try:
        cmds.evaluator(name="cache", enable=False)
        cmds.cacheEvaluator(flushCache="destroy")
    except (RuntimeError, TypeError):
        pass

    # potrebbe essere blendWeighted, da un FaceSetup precedente
    cmds.setAttr(skin_cluster + ".skinningMethod", 0)

    if not cmds.objExists("FaceMotionSystem"):
        for name in _RESERVED_NAMES:
            if cmds.objExists(name):
                cmds.select(cmds.ls(name))
                cmds.warning(
                    'A object with the name:"{}" already '
                    "exists, rename this to something else, "
                    "before running the Build.".format(name)
                )
                return False

    if cmds.objExists("FaceMotionSystem"):
        _prepare_rebuild(
            geometry, all_face_geo, head_joint, skin_cluster, keep_all, keep_custom_controls
        )

    # assist softmod residui di Lip/Lid
    for name in (
        "upperTempSoftModHandle1",
        "lowerTempSoftModHandle1",
        "upperTempSoftModHandle2",
        "lowerTempSoftModHandle2",
    ):
        if cmds.objExists(name):
            cmds.delete(name)

    skin_cluster = _regenerate_skin_cluster(geometry, skin_cluster)

    # tutto cio' che esiste prima del build (per il teardown/undo)
    excluded = set(cmds.ls(type="objectSet") or [])
    excluded.update(cmds.ls(type="partition") or [])
    before_build = [node for node in cmds.ls() or [] if node not in excluded]
    cmds.sets(before_build, name="allBeforeFaceBuild")
    cmds.select(clear=True)

    set_fixed_wrap_options()
    if not ensure_advanced_base():
        return False

    if (keep_all or keep_custom_controls) and cmds.objExists("|FaceCustomSystem"):
        cmds.parent("|FaceCustomSystem", "FaceMotionSystem")

    # la scala su cui "operano" i controlli on-face
    for node in ("OnFacecontrols", "ConstrainedSetup"):
        cmds.setAttr(node + ".s", scale / 14.4300, scale / 14.4300, scale / 14.4300, type="float3")

    _create_face_joint(head_joint, scale, multi_skin_clusters)

    # lo skinCluster definito potrebbe essere cambiato
    for node in cmds.listHistory(geometry) or []:
        if cmds.nodeType(node) == "skinCluster" and node != skin_cluster:
            print(
                '// Updated SkinCluster info, used to be:"{}", now it is:"{}".'.format(
                    skin_cluster, node
                )
            )
            skin_cluster = node
            set_fit_option("SkinCluster", skin_cluster)

    for node in cmds.listHistory(geometry) or []:
        if cmds.nodeType(node) == "deltaMush":
            cmds.setAttr(node + ".envelope", 0)

    _create_teeth_sets(upper_teeth, lower_teeth)

    if cmds.objExists("DeformSet"):
        for joint in cmds.sets("DeformSet", query=True) or []:
            if cmds.attributeQuery("lockInfluenceWeights", node=joint, exists=True):
                if cmds.getAttr(joint + ".lockInfluenceWeights"):
                    cmds.setAttr(joint + ".lockInfluenceWeights", 0)

    _create_control_orient(scale)

    if get_max_influences():
        # il MEL fissa comunque 4 (quirk preservato)
        cmds.skinCluster(geometry, edit=True, maximumInfluences=4)
        cmds.setAttr(skin_cluster + ".maxInfluences", 4)
        cmds.setAttr(skin_cluster + ".maintainMaxInfluences", 1)

    cmds.select(clear=True)
    return True

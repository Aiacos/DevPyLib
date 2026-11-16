"""BlendShapes: conversione del viso a joint ("driving system") in
blendShape (frame " BlendShapes" del pannello Face, bottone Convert, MEL
AdvancedSkeleton.mel 2126-2148).

Port di:
- asBSConvertDStoBS        (MEL 39582-40935) -> convert_to_blend_shapes
- asBlendShapeFrontOfChain (MEL 39574-39580) -> _blend_shape_front_of_chain
- asFaceCreateSkinLayer    (MEL 39494-39526) -> _create_skin_layer
- asFaceIsBlendedAttr      (MEL 60451-60461) -> _is_blended_attr
- asSetBlendedAttribute    (MEL 61654-61729) -> _set_blended_attribute
- asGoToBuildPose          (MEL 12172-12243, solo il ramo viso) ->
  _go_to_build_pose
- asCreateWrap             (MEL 7281-7305)   -> _create_wrap
- helper: asGetSkinCluster (7817), asRemoveInfluence (43576),
  asDisconnectMatrixAttr (42352), asVersionRequirementCheck (58560);
  asGetOpm, asLockAttr, asParentConstraint e asShowLayer sono quelli di
  build_utils, la build pose si riscrive con face_finish.

Tre modalita', come nel MEL:
- keep_joints=False: RigType "BlendShapes". Un target per ogni attributo
  dei controlli del ctrlBox, guidato da una driven key; joint e controlli
  on-face vengono cancellati e la pelle torna al joint della testa.
- keep_joints=True: RigType "Mixed". I joint restano e deformano una copia
  della geometria (FaceJointsLayer_<geo>) che entra nel blendShape come
  target sempre attivo; i controlli on-face vengono sdoppiati (<ctrl> e
  <ctrl>Layered) e agganciati alla pelle con un wrap.
- keep_joints=True con FaceFitSkeleton.GameEngine: i joint restano ma
  senza layer (ramo MEL "$keepJoints && $gameEngine").

I textField e le due checkBox della UI diventano le opzioni omonime di
FaceFitSkeleton (fit_options) e i due argomenti.

Divergenze intenzionali (da riportare in docs/gap-analysis.md):
- i prerequisiti mancanti danno cmds.warning + False prima di toccare la
  scena, invece dell'errore MEL a meta' procedura; un errore a
  conversione avviata da' comunque warning + False ma la scena resta
  convertita a meta' (come nel MEL: la conversione cancella nodi e non e'
  annullabile da qui). Salvare la scena prima di convertire;
- niente progressBar e niente asUpdateButtonEnables (UI); `refresh` e'
  affiancato da una valutazione esplicita della mesh, perche' in mayapy
  non c'e' viewport che la forzi;
- se la conversione fallisce a meta', il set temporaneo
  allBeforeConvertToBS viene rimosso (nel MEL resta in scena);
- asGoToBuildPose non passa per `eval`: di faceBuildPose.udAttr si
  eseguono solo i comandi "setAttr <plug> <numero>", gli altri sono
  segnalati e saltati; niente namespace, T-pose e modificatori di tastiera;
- gli envelope di deltaMush/blendShape si ripristinano da una lista, non
  da una stringa MEL passata a `eval`;
- asSetBlendedAttribute: i driver "qRotate" (solo body rig) non sono
  gestiti, perche' il MEL li imposta eseguendo una stringa letta dalla
  scena;
- asCreateWrap/AddWrapInfluence sono riscritti con cmds (deformer wrap +
  connessioni di doWrapArgList): nessun mel.eval;
- newSkinCluster, removeUnusedForSkin e removeUnusedInfluences sono le
  chiamate cmds equivalenti; asSmoothFlood e' quello numerico di
  jaw_weighing e le due selezioni di polySelectConstraint (MEL
  40382-40385) sono calcolate dalle posizioni, come in face_up_mid_lo;
- "skinCluster -selectInfluenceVerts" + asInvertSelection (MEL
  40405-40410) sono calcolati dai pesi, senza selezione;
- i valori letti a bocca aperta da lowerTeethFollow_M/Tongue0Follow_M
  (MEL 40069-40099) servono solo a un blocco commentato: resta il solo
  giro ctrlMouth_M.ty -1 -> 0;
- il riassegnamento della pelle delle geometrie secondarie alla testa
  (MEL 40168-40190) e' dentro un ciclo che lo ripete identico per ogni
  controllo: qui si fa una volta;
- dove il MEL andrebbe in errore su un nodo opzionale assente
  (bwctrlEye_*_blink, EyeLidJoints_M, JawFollow_*, SmilePull_*,
  SmilePullOffset_*, LipAttach_*, <ctrl>MM<side>TGXform,
  lowerTeethOffset_M, EyeBrowCenterJoint_M e le altre sorgenti degli
  attacher, una geometria senza skinCluster) il passo viene saltato;
- HeadMatrixInverter_M segue "Head_M" come nel MEL, o il joint
  dell'opzione HeadJoint se Head_M non esiste;
- il secondo controllo "gia' convertito" (attributo convertedToBlendShapes
  su asFaceBS, MEL 39642) non e' portato: e' irraggiungibile, il primo
  (asFaceBS esiste) esce prima;
- keep_joints con l'opzione GameEngine segue il ramo MEL senza layer ma
  aggiunge un warning: la UI di AdvancedSkeleton non offre "Mixed" con
  GameEngine (MEL 50625-50627) e il risultato non e' un rig coerente.
"""

import fnmatch

import maya.cmds as cmds

from .build_utils import as_get_opm, as_lock_attr, as_parent_constraint, as_show_layer
from .face_finish import _capture_build_pose
from .fit_options import FIT_SKELETON, get_fit_option, set_fit_option
from .jaw_weighing import _Mesh, _smooth_flood

_BS = "asFaceBS"
_TARGETS_GROUP = "asBlendShapes"
_TEMP_TARGET = "tempRenamingBlendShapeTarget"
_BEFORE_SET = "allBeforeConvertToBS"
_UP_MID_LO = ("upper", "middle", "lower")
_SIDES = ("_R", "_L", "_M")
_MIN_VERSION = 5.791  # asVersionRequirementCheck face 5.791 (MEL 39638)

# nodi che asBSConvertDStoBS usa senza controllarli
_REQUIRED_NODES = (
    "ctrlBox.limits",
    "OnFacecontrols",
    "FaceGroup",
    "FaceDeformationSystem",
    "FaceJoint_M",
    "FaceAllSet",
    "FaceControlSet",
    "faceBuildPose.udAttr",
)
_REQUIRED_FOR_LAYERS = ("ControlsSetup", "ConstrainedSetup", "DeformJointConstraints")

# nome del target per controllo senza lato e (attributo, verso) (MEL 39892-39934)
_TARGET_NAMES = {
    "ctrlBrow": {
        ("translateX", 1): "brow_innerRaiser",
        ("translateX", -1): "brow_innerlower",
        ("translateY", 1): "brow_raiser",
        ("translateY", -1): "brow_lower",
        ("squeeze", 1): "brow_squeeze",
        ("outerUpDown", 1): "brow_outerUpDown",
    },
    "ctrlCheek": {
        ("translateX", 1): "cheek_out",
        ("translateX", -1): "cheek_in",
        ("translateY", 1): "cheek_raiser",
    },
    "ctrlNose": {
        ("translateX", 1): "nose_wide",
        ("translateX", -1): "nose_narrow",
        ("translateY", 1): "nose_raiser",
    },
    "ctrlMouthCorner": {
        ("translateX", 1): "mouth_wide",
        ("translateX", -1): "mouth_narrow",
        ("translateY", 1): "mouth_raiser",
        ("translateY", -1): "mouth_lower",
        ("txPos_tyPos", 1): "mouth_smileBulge",
        ("txPos_tyNeg", 1): "mouth_frownBulge",
    },
    "ctrlEye": {
        ("translateX", 1): "eye_left",
        ("translateX", -1): "eye_right",
        ("translateY", 1): "eye_up",
        ("translateY", -1): "eye_down",
        ("blink", 1): "blink",
        ("squint", 1): "squint",
    },
}
_LIPS_NAMES = {
    ("translateX", 1): "lip_left",
    ("translateX", -1): "lip_right",
    ("translateY", 1): "lip_up",
    ("translateY", -1): "lip_down",
}
_MOUTH_NAMES = {
    ("translateX", 1): "mouth_wide",
    ("translateX", -1): "mouth_narrow",
    ("translateY", 1): "mouth_close",
    ("translateY", -1): "mouth_open",
}

_KEEP_SDKS = ("SDKEye_*", "SDKIris_*", "SDKPupil_*")  # MEL 40060
_KEEP_JOINTS = ("EyeJoint_R", "EyeJoint_L")  # MEL 40198
_KEEP_CONTROLS = ("EyeOffset_R", "EyeOffset_L")  # MEL 40209
# controlli che guidano un joint fuori dalla testa (MEL 40457)
_JOINT_CTRLS = (
    "Eye", "Iris", "Pupil", "Jaw", "upperTeeth", "lowerTeeth",
    "Tongue0", "Tongue1", "Tongue2", "Tongue3",
)  # fmt: skip
# controlli agganciati alla pelle senza un joint omonimo (MEL 40587-40591)
_TACK_ON_CTRLS = (
    "EyeBrowRegion_R", "EyeBrowRegion_L", "EyeRegion_R", "EyeRegion_L",
    "NoseRegion_M", "LipRegion_M", "SmilePull_R", "SmilePull_L",
    "upperLip_R", "lowerLip_R", "upperLip_L", "lowerLip_L",
    "upperFace_M", "middleFace_M", "lowerFace_M",
)  # fmt: skip
# joint senza attacher (MEL 40600-40605)
_NO_ATTACHER = (
    "Tongue0Joint_M", "LipJoints_M", "JawJoint_M", "upperTeethJoint_M", "lowerTeethJoint_M",
    "upperFaceJoint_M", "middleFaceJoint_M", "lowerFaceJoint_M",
)  # fmt: skip
# controlli senza il nodo che sottrae la loro traslazione (MEL 40718-40719)
_NO_SUBTRACT = (
    "upperTeeth_M", "lowerTeeth_M", "Tongue0_M", "upperFace_M", "middleFace_M", "lowerFace_M",
)  # fmt: skip
# dove sta l'attacher di un controllo quando non e' sul suo joint (MEL
# 40621-40631); l'ultima regola che combacia vince, come la catena di if
_ATTACHER_SOURCES = (
    ("upperLip_M", "upperLipOuterCurve.cv[0]"),
    ("lowerLip_M", "lowerLipOuterCurve.cv[0]"),
    ("NoseRegion_M", "NoseJoint_M"),
    ("LipRegion_M", "upperLipOuterCurve.cv[0]"),
    ("upperTeeth_M", "upperLipOuterCurve.cv[0]"),
    ("lowerTeeth_M", "lowerLipOuterCurve.cv[0]"),
    ("Jaw_M", "Jaw"),
    ("upperFace_M", "EyeBrowCenterJoint_M"),
    ("middleFace_M", "NoseUnderJoint_M"),
    ("Tongue*_M", "lowerLipOuterCurve.cv[0]"),
)
# controlli con la shape sul ctrlBox2 (MEL 40768)
_BOX2_CTRLS = (
    "EyeBrowRegion", "EyeRegion", "NoseRegion", "LipRegion", "upperFace", "middleFace", "lowerFace",
)  # fmt: skip
_IDENTITY = (1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1)


# -- helper generici ------------------------------------------------------


def _ws(node):
    return cmds.xform(node, query=True, worldSpace=True, translation=True)


def _children(node, node_type="transform"):
    return cmds.listRelatives(node, children=True, type=node_type, path=True) or []


def _parent_of(node):
    return (cmds.listRelatives(node, parent=True, path=True) or [None])[0]


def _existing(nodes):
    return [node for node in nodes if cmds.objExists(node)]


def _delete_existing(*nodes):
    nodes = _existing(nodes)
    if nodes:
        cmds.delete(nodes)


def _in_face_all_set(node):
    return bool(cmds.sets(node, isMember="FaceAllSet"))


def _matches(name, patterns):
    return any(fnmatch.fnmatchcase(name, pattern) for pattern in patterns)


def _skin_cluster_of(obj):
    """asGetSkinCluster (MEL 7817-7825): ultimo skinCluster nella history."""
    found = ""
    for node in cmds.listHistory(obj, pruneDagObjects=True, interestLevel=2) or []:
        if cmds.nodeType(node) == "skinCluster":
            found = node
    return found


def _influences(skin, joints_only=False):
    """I nodi collegati a <skin>.matrix, nell'ordine degli indici."""
    kwargs = {"type": "joint"} if joints_only else {}
    return cmds.listConnections(skin + ".matrix", source=True, destination=False, **kwargs) or []


def _set_weight_lock(joint, lock):
    if cmds.attributeQuery("lockInfluenceWeights", node=joint, exists=True):
        cmds.setAttr(joint + ".lockInfluenceWeights", int(bool(lock)))


def _skin_percent(skin, components, joint):
    """`catchQuiet (skinPercent -tv <joint> 1 ...)`: senza errore se il
    joint non e' un'influence o i pesi sono tutti bloccati."""
    try:
        cmds.skinPercent(skin, components, transformValue=(joint, 1))
    except RuntimeError:
        pass


def _new_skin_cluster(influences, geometry, name):
    """newSkinCluster "-toSelectedBones -mi 3 -dr 4 -rui false" + rename."""
    skin = cmds.skinCluster(
        list(influences) + [geometry],
        toSelectedBones=True,
        maximumInfluences=3,
        dropoffRate=4,
        removeUnusedInfluence=False,
    )[0]
    return cmds.rename(skin, name)


def _copy_skin_weights(source, destination):
    cmds.select(source, destination)
    cmds.copySkinWeights(
        noMirror=True, surfaceAssociation="closestPoint", influenceAssociation="closestJoint"
    )


def _remove_unused_influences(skin):
    """removeUnusedForSkin <skin> 0 (script di Maya: skinCluster -e -rui 1)."""
    if skin and cmds.objExists(skin):
        try:
            cmds.skinCluster(skin, edit=True, removeUnusedInfluence=True)
        except RuntimeError:
            pass


def _remove_influence(joint, skin):
    """asRemoveInfluence (MEL 43576-43588)."""
    if not cmds.objExists(skin):
        return
    influences = _influences(skin)
    if joint in influences:
        cmds.skinCluster(skin, edit=True, removeInfluence=joint)
        if len(influences) == 1:
            cmds.delete(skin)


def _disconnect_matrix_attr(xform, reset):
    """asDisconnectMatrixAttr (MEL 42352-42388): stacca cio' che guida il
    transform (l'offsetParentMatrix con l'OPM, altrimenti t/r/s/sh)."""
    opm = as_get_opm()
    plugs = ["offsetParentMatrix"] if opm else ["t", "r", "s", "sh"]
    for attr in plugs:
        plug = "{}.{}".format(xform, attr)
        source = cmds.listConnections(plug, source=True, destination=False, plugs=True) or []
        if source:
            cmds.disconnectAttr(source[0], plug)
    if reset and opm:
        cmds.setAttr(xform + ".offsetParentMatrix", _IDENTITY, type="matrix")


def _layer_suffix(geo):
    """ "_" + nome della geometria col primo ":" sostituito (MEL `substitute`)."""
    return "_" + geo.replace(":", "_", 1)


def _layer_bs(geo, geometry):
    """Il blendShape di una geometria AllHead nei rami a layer (MEL
    39694-39697): asFaceBS per la Face, asFaceBS_<geo> per le altre."""
    return _BS if geo == geometry else _BS + _layer_suffix(geo)


def _whole_objects(text):
    """I token di un textField che sono oggetti interi, non componenti."""
    return [token for token in text.split() if "." not in token]


# -- blendShape e target --------------------------------------------------


def _blend_shape_front_of_chain(geo, name):
    """asBlendShapeFrontOfChain (MEL 39574-39580): -suppressDialog evita il
    dialogo sull'ordine dei deformer (es. con l'HeadSquash)."""
    try:
        cmds.blendShape(geo, name=name, frontOfChain=True, suppressDialog=True)
    except (RuntimeError, TypeError):
        cmds.blendShape(geo, name=name, frontOfChain=True)


def _add_target(blend_shape, geo, target):
    """`blendShape -e -tc 0 -t <geo> <getAttr -s .w> <target> 1 <bs>`."""
    index = cmds.getAttr(blend_shape + ".w", size=True)
    cmds.blendShape(blend_shape, edit=True, topologyCheck=False, target=(geo, index, target, 1.0))


def _is_blended_attr(obj, attr):
    """asFaceIsBlendedAttr (MEL 60451-60461)."""
    if not cmds.getAttr("{}.{}".format(obj, attr), settable=True) and "_" in attr:
        return True
    return obj.startswith("ctrlMouthCorner_") and attr in (
        "smile",
        "frown",
        "narrowSmile",
        "narrowFrown",
    )


def _first_source(plug, plugs=False):
    found = cmds.listConnections(
        plug, source=True, destination=False, skipConversionNodes=True, plugs=plugs
    )
    return found[0] if found else ""


def _set_blended_attribute(obj, attr, value):
    """asSetBlendedAttribute con getDriversMode 0 (MEL 61654-61729): porta
    i due driver di un attributo "blended" ai valori che lo fanno valere
    `value` (1 = posa piena, 0 = riposo)."""
    plug = "{}.{}".format(obj, attr)
    drivers, driver_values = [], []
    while True:
        node = _first_source(plug)
        if not node:
            break
        node_type = cmds.objectType(node)
        if node_type == "multiplyDivide":
            plug = node + ".input1X"
            continue
        if node_type == "setRange":
            driver_values = [cmds.getAttr(node + ".dvX"), cmds.getAttr(node + ".dvY")]
            mpd = _first_source(_first_source(node + ".valueX") + ".input1D[0]")
            for axis in "XY":
                source = _first_source("{}.input1{}".format(mpd, axis))
                if source and cmds.objectType(source) == "blendWeighted":
                    drivers.append(_first_source(source + ".input[0]", plugs=True))
                else:
                    drivers.append(_first_source("{}.input1{}".format(mpd, axis), plugs=True))
        break
    if value < 1:
        driver_values = [(dv * dv * value) ** 0.5 for dv in driver_values]
    for driver, driver_value in zip(drivers, driver_values):
        if not driver:
            continue
        if ".qRotate" in driver:
            cmds.warning(
                "convert_to_blend_shapes: blended angle driver {} is not supported".format(driver)
            )
            continue
        cmds.setAttr("FK" + driver if cmds.objExists("FK" + driver) else driver, driver_value)


def _go_to_build_pose():
    """asGoToBuildPose faceSetup (MEL 12172-12243), senza `eval`: di
    faceBuildPose.udAttr (+ udExtraAttr) si eseguono i soli setAttr numerici."""
    text = cmds.getAttr("faceBuildPose.udAttr") or ""
    if cmds.attributeQuery("udExtraAttr", node="faceBuildPose", exists=True):
        text += cmds.getAttr("faceBuildPose.udExtraAttr") or ""
    for command in text.split(";"):
        tokens = command.split()
        if not tokens:
            continue
        try:
            if len(tokens) != 3 or tokens[0] != "setAttr":
                raise ValueError(command)
            cmds.setAttr(tokens[1], float(tokens[2]))
        except (RuntimeError, ValueError):
            cmds.warning("Failed: " + command)


def _deformed_shape(geo):
    shapes = cmds.listRelatives(geo, shapes=True, noIntermediate=True, path=True) or []
    return shapes[0] if shapes else geo


def _snapshot(geo, name):
    """Fotografa la geometria deformata in una mesh nuova chiamata `name`
    (MEL 39990-40000). Il MEL non duplica: il duplicato confonderebbe i
    wrap dei controlli on-face."""
    if cmds.objExists(name):
        cmds.rename(name, _TEMP_TARGET)
    shape = cmds.createNode("mesh")
    target = cmds.rename(cmds.listRelatives(shape, parent=True, path=True)[0], name)
    source = _deformed_shape(geo) + ".outMesh"
    cmds.connectAttr(source, target + ".inMesh")
    cmds.sets(target, edit=True, forceElement="initialShadingGroup")
    cmds.refresh()
    cmds.polyEvaluate(target, vertex=True)  # in batch `refresh` non valuta la mesh
    cmds.disconnectAttr(source, target + ".inMesh")
    return target


def _target_name(obj, side_less, side, attr, value, pos_neg, keep_joints, ud_attrs):
    """Il nome del target di (controllo, attributo, verso), o None se la
    coppia non va convertita (MEL 39890-39960)."""
    name = side_less + attr + pos_neg + side
    prefix = _TARGET_NAMES.get(side_less, {}).get((attr, value))
    if side_less == "ctrlEye":
        if attr in ("iris", "pupil"):
            return None
        if attr in ("translateX", "translateY") and keep_joints:
            return None  # i FleshyEyes restano a joint nel rig "Mixed"
    if prefix:
        name = prefix + side
    if obj == "ctrlLips_M":
        if (attr, value) in _LIPS_NAMES:
            name = _LIPS_NAMES[(attr, value)] + side
        if attr in ud_attrs:
            name = "lip_" + attr + pos_neg + side
    if obj == "ctrlMouth_M":
        if (attr, value) in _MOUTH_NAMES:
            name = _MOUTH_NAMES[(attr, value)] + side
        else:
            name = "mouth_" + attr + ("In" if value == 1 else "Out") + side
    if obj in ("ctrlPhonemes_M", "ctrlEmotions_M"):
        name = attr + side
    if obj == "ctrlARKit_M":
        name = attr
    return name


def _key_target(blend_shape, name, obj, attr, value, driving_value, blended, soft_min, side):
    """Driven key controllo -> peso del target (MEL 40030-40045)."""
    plug = "{}.{}".format(blend_shape, name)
    driver = "{}.{}".format(obj, attr)
    for driver_value, weight in ((0, 0), (driving_value, 1)):
        cmds.setDrivenKeyframe(
            plug,
            inTangentType="linear",
            outTangentType="linear",
            driverValue=driver_value,
            value=weight,
            currentDriver=driver,
        )
    curve = "{}_{}".format(blend_shape, name)
    created = cmds.listConnections(plug, source=True, destination=False, type="animCurve") or []
    if created and created[0] != curve:
        curve = cmds.rename(created[0], curve)
    cmds.setAttr(curve + ".preInfinity", 4)
    cmds.setAttr(curve + ".postInfinity", 4)
    if attr in ("translateX", "translateY") or blended or soft_min < 0:
        if value > 0:
            cmds.setAttr(curve + ".preInfinity", 1)  # niente peso negativo sotto zero
        else:
            cmds.setAttr(curve + ".postInfinity", 0)  # niente peso negativo sopra zero
    if obj.startswith("ctrlMouthCorner_"):
        cmds.connectAttr(
            "bwctrlMouthCorner{}_{}.output".format(side, attr), curve + ".input", force=True
        )


def _convert_attribute(obj, attr, value, name, geos, soft_min, keep_targets, offset_x, side):
    """Un target per geometria, per un (controllo, attributo, verso) (MEL
    39962-40050)."""
    plug = "{}.{}".format(obj, attr)
    for index, geo in enumerate(geos):
        blend_shape = _BS if index == 0 else "{}_{}".format(_BS, geo.replace(":", "_"))
        if not cmds.objExists(blend_shape):
            _blend_shape_front_of_chain(geo, blend_shape)
        blended = _is_blended_attr(obj, attr)
        if attr in ("translateX", "translateY") or blended:
            driving_value = value
        elif attr in ("rotateX", "rotateY"):
            driving_value = 30 * value
        else:
            driving_value = 10 * value

        if blended:
            _set_blended_attribute(obj, attr, 1)
        else:
            cmds.setAttr(plug, driving_value)
        cmds.refresh()

        target = _snapshot(geo, name)
        target = cmds.parent(target, _TARGETS_GROUP)[0]
        _add_target(blend_shape, geo, target)
        if keep_targets:
            if index > 0:
                target = cmds.rename(target, "{}_{}".format(name, geo.replace(":", "_")))
            if cmds.objExists(_TEMP_TARGET):
                cmds.rename(_TEMP_TARGET, name)
            as_lock_attr(target, False, False, False, False)
            cmds.move(offset_x, 0, 0, target, relative=True)

        if blended:
            _set_blended_attribute(obj, attr, 0)
        else:
            cmds.setAttr(plug, 0)

        # gli altri blendShape riusano la curva del primo
        if blend_shape != _BS:
            cmds.connectAttr("{}.{}".format(_BS, name), "{}.{}".format(blend_shape, name))
            continue
        _key_target(_BS, name, obj, attr, value, driving_value, blended, soft_min, side)
        if not keep_targets:
            cmds.delete(target)


def _convert_controllers(objs, geos, keep_joints, keep_targets, cheek_x):
    """Il ciclo principale (MEL 39829-40052): ogni attributo keyable e
    sbloccato dei controlli diventa uno o due target (verso positivo e
    negativo)."""
    side_steps = {"left": 0, "right": 0}
    for obj in objs:
        side, side_less = obj[-2:], obj[:-2]
        ud_attrs = cmds.listAttr(obj, userDefined=True) or []
        for attr in cmds.listAttr(obj, keyable=True) or []:
            plug = "{}.{}".format(obj, attr)
            if attr in ("visibility", "jaw", "lip") or cmds.getAttr(plug, lock=True):
                continue
            for value in (1, -1):
                pos_neg = "Pos" if value == 1 else "Neg"
                soft_min = 0.0  # il MEL legge $softLimits[0] di un array svuotato
                positive_only = False
                if attr in ud_attrs and cmds.attributeQuery(attr, node=obj, softMinExists=True):
                    soft_min = cmds.attributeQuery(attr, node=obj, softMin=True)[0]
                    positive_only = soft_min != -10
                if positive_only:
                    if value == -1:
                        continue
                    pos_neg = ""
                limits = cmds.transformLimits(obj, query=True, translationY=True)
                if attr == "translateY" and value == -1 and limits[0] == 0:
                    continue

                key = "left" if side == "_L" else "right"
                side_steps[key] += 1
                side_factor = -1 if side == "_L" else 1
                offset_x = cheek_x * 2.5 * side_factor * side_steps[key]

                name = _target_name(
                    obj, side_less, side, attr, value, pos_neg, keep_joints, ud_attrs
                )
                if name is None:
                    continue
                _convert_attribute(
                    obj, attr, value, name, geos, soft_min, keep_targets, offset_x, side
                )


# -- rig "Mixed": layer di deformazione -----------------------------------


def _create_template_layer(geo, suffix):
    """Copia pulita della geometria (MEL 39700-39716): senza figli, shape
    intermedie e appartenenza ai set *Area."""
    template = "TemplateLayer" + suffix
    cmds.duplicate(geo, name=template)
    as_lock_attr(template, False, False, False, False)
    cmds.parent(template, "TemplateLayer")
    cmds.sets(template, edit=True, forceElement="initialShadingGroup")
    for child in _children(template):
        cmds.delete(child)
    for shape in cmds.listRelatives(template, shapes=True, fullPath=True) or []:
        if cmds.getAttr(shape + ".intermediateObject"):
            cmds.delete(shape)
    shapes = cmds.listRelatives(template, shapes=True, fullPath=True) or []
    if shapes:
        # come nel MEL (ciclo senza graffe), conta solo l'ultima shape
        conns = (
            cmds.listConnections(
                shapes[-1],
                source=False,
                destination=True,
                plugs=True,
                connections=True,
                type="objectSet",
            )
            or []
        )
        for source, destination in zip(conns[0::2], conns[1::2]):
            if fnmatch.fnmatchcase(destination, "*Area.*"):
                cmds.disconnectAttr(source, destination)
    return template


def _create_face_joints_layers(geometry, all_face_geo):
    """Prima meta' del ramo a layer (MEL 39667-39751): FaceJoint_M passa
    sotto FaceDeformationSystem e ogni geometria AllHead riceve una copia
    skinnata ai soli joint del viso, target del suo blendShape."""
    cmds.setAttr("FaceDeformationSystem.v", lock=False)
    cmds.setAttr("FaceDeformationSystem.v", 1)
    for child in _children("FaceDeformationSystem"):
        cmds.setAttr(child + ".v", 0)
        cmds.setAttr(child + ".v", lock=True)
    cmds.parent("FaceJoint_M", "FaceDeformationSystem")
    cmds.setAttr("FaceJoint_M.v", lock=False)
    if cmds.objExists("Main") and cmds.attributeQuery("jointVis", node="Main", exists=True):
        cmds.connectAttr("Main.jointVis", "FaceJoint_M.v")
    cmds.createNode("transform", name="DeformationLayers", parent="FaceDeformationSystem")
    for layer in ("TemplateLayer", "FaceJointsLayer"):
        cmds.createNode("transform", name=layer, parent="DeformationLayers")
        cmds.setAttr(layer + ".v", 0)

    up_mid_lo = cmds.objExists("upperFaceJoint_M")
    for geo in all_face_geo:
        suffix = _layer_suffix(geo)
        blend_shape = _layer_bs(geo, geometry)
        skin = _skin_cluster_of(geo)
        template = _create_template_layer(geo, suffix)
        layer = "FaceJointsLayer" + suffix
        cmds.duplicate(template, name=layer)
        cmds.parent(layer, "FaceJointsLayer")
        layer_skin = _new_skin_cluster(_influences(skin, joints_only=True), layer, layer + "SC")
        _copy_skin_weights(geo, layer)

        # il layer resta legato ai soli joint del viso: il peso di testa e
        # collo passa a FaceJoint_M, che non si muove
        for joint in _influences(layer_skin):
            _set_weight_lock(joint, _in_face_all_set(joint))
        if up_mid_lo:  # le fasce UpMidLo stanno su un layer a parte
            for band in _UP_MID_LO:
                cmds.setAttr(band + "FaceJoint_M.liw", 0)
        if "FaceJoint_M" not in _influences(layer_skin):
            cmds.skinCluster(
                layer_skin,
                edit=True,
                dropoffRate=4,
                lockWeights=False,
                weight=0,
                addInfluence="FaceJoint_M",
            )
        _skin_percent(layer_skin, layer, "FaceJoint_M")
        if up_mid_lo:
            for band in _UP_MID_LO:  # nome senza "Face", come nel MEL
                _remove_influence(band + "Joint_M", layer_skin)

        _blend_shape_front_of_chain(geo, blend_shape)
        _add_target(blend_shape, geo, layer)
        cmds.aliasAttr("FaceJointsLayer", blend_shape + ".w[0]")

    if cmds.objExists("upperSideReverse_R"):
        _create_skin_layer("UpMidLo")


def _create_skin_layer(layer):
    """asFaceCreateSkinLayer (MEL 39494-39526): un altro layer, copia di
    TemplateLayer, come target sempre attivo dei blendShape."""
    group = layer + "Layer"
    cmds.duplicate("TemplateLayer", name=group)
    for child in cmds.listRelatives(group, children=True, type="transform") or []:
        name = child.replace("TemplateLayer_", "", 1)
        in_layer = "{}_{}".format(group, name)
        cmds.rename("{}|{}".format(group, child), in_layer)
        shapes = cmds.listRelatives("FaceJointsLayer_" + name, shapes=True, path=True) or []
        blend_shape = cmds.listConnections(
            shapes[0], source=False, destination=True, type="blendShape"
        )[0]
        geo = ""
        for node in cmds.listHistory(blend_shape, future=True) or []:
            if cmds.objectType(node) == "mesh":
                geo = cmds.listRelatives(node, parent=True, path=True)[0]
                break
        _add_target(blend_shape, geo, in_layer)
        cmds.setAttr("{}.{}".format(blend_shape, in_layer), 1)


def _bind_main_skin_to_head(geometry, all_face_geo, head_joint):
    """Le geometrie tornano legate al solo joint della testa: i joint del
    viso ora agiscono dal layer (MEL 40265-40282)."""
    for geo in all_face_geo:
        skin = _skin_cluster_of(geo)
        for joint in _influences(skin):
            _set_weight_lock(joint, not _in_face_all_set(joint))
        cmds.setAttr(head_joint + ".liw", 0)
        _skin_percent(skin, geo, head_joint)
        _remove_unused_influences(skin)
        cmds.setAttr(_layer_bs(geo, geometry) + ".FaceJointsLayer", 1)


def _create_layered_hierarchy():
    """I controlli on-face originali restano fermi sotto
    FaceMotionSystemStatic; i nuovi andranno sotto OnFacecontrolsLayered,
    che segue la testa (MEL 40284-40299)."""
    _delete_existing(
        "FaceDeformationFollowHead_pointConstraint1",
        "FaceDeformationFollowHead_orientConstraint1",
        "FaceDeformationFollowHead_parentConstraint1",
    )
    cmds.createNode("transform", name="FaceMotionSystemStatic", parent="FaceGroup")
    cmds.reorder("FaceMotionSystemStatic", relative=-1)
    cmds.parent("OnFacecontrols", "FaceMotionSystemStatic")
    cmds.createNode("transform", name="OnFacecontrolsLayered", parent="OnFacecontrols")
    cmds.parent("OnFacecontrolsLayered", "ControlsSetup")
    cmds.parent("ConstrainedSetup", "FaceMotionSystemStatic")
    for side in _SIDES:
        cmds.createNode(
            "transform", name="SideReverseLayered" + side, parent="OnFacecontrolsLayered"
        )
    cmds.setAttr("SideReverseLayered_R.sx", -1)


def _eye_geometries():
    """(lato, geometrie intere dell'occhio) per i lati con il lattice
    dell'occhio non sferico (MEL 40306-40317, 40412-40423)."""
    if not cmds.objExists("squashEyeFfd1Set_R"):
        return []
    return [
        ("_R", _whole_objects(get_fit_option("RightEye") or "")),
        ("_L", _whole_objects(get_fit_option("LeftEye") or "")),
    ]


def _move_eye_lattices_to_layers():
    """Occhio non sferico: i lattice deformano il layer dei joint invece
    della geometria (MEL 40301-40326)."""
    _delete_existing(
        "EyeLattice2_R_parentConstraint1",
        "EyeLattice2_R_scaleConstraint1",
        "EyeLattice2_L_parentConstraint1",
        "EyeLattice2_L_scaleConstraint1",
    )
    for side, eye_geos in _eye_geometries():
        for geo in eye_geos:
            layer = "FaceJointsLayer_" + geo
            cmds.sets(geo, remove="squashEyeFfd1Set" + side)
            cmds.sets(geo, remove="squashEyeFfd2Set" + side)
            cmds.sets(layer, add="squashEyeFfd1Set" + side)
            cmds.reorderDeformers(layer + "SC", "squashEyeFfd1" + side, layer)
            cmds.sets(layer, add="squashEyeFfd2Set" + side)


def _up_mid_lo_as_layer(geometry, skin_cluster, head_joint):
    """Le fasce upper/middle/lower diventano un layer a se' (MEL
    40328-40432): i controlli tornano sotto SideReverse_* e le copie
    UpMidLoLayer_<geo> sono pesate sulle tre fasce."""
    cmds.parent("EyeOffset_R", "EyeOffset_L", "EyeControls")
    for band in _UP_MID_LO:
        for side in _SIDES:
            reverse = band + "SideReverse" + side
            children = _children(reverse)
            if children:
                cmds.parent(children, "SideReverse" + side)
            cmds.delete(reverse)

    main_layer = "UpMidLoLayer_" + geometry.replace(":", "_", 1)
    main_skin = main_layer + "SC"
    bands = [band + "FaceJoint_M" for band in _UP_MID_LO]
    as_show_layer("UpMidLo")
    layers = cmds.listRelatives("UpMidLoLayer", children=True, type="transform") or []
    for layer in layers:
        influences = bands + ["FaceJoint_M"]
        if layer == main_layer:
            influences += [
                joint
                for joint in _influences(skin_cluster, joints_only=True)
                if joint not in influences
            ]
        _new_skin_cluster(influences, layer, layer + "SC")
        cmds.skinPercent(layer + "SC", layer, transformValue=("middleFaceJoint_M", 1))

    # prima la copia dei pesi, per la sfumatura fra la fascia bassa e il collo
    _copy_skin_weights(geometry, main_layer)
    joints = _influences(main_skin, joints_only=True)

    def lock_all(lock):
        for joint in joints:
            _set_weight_lock(joint, lock)

    lock_all(True)
    _set_weight_lock(head_joint, False)
    _skin_percent(main_skin, main_layer, "middleFaceJoint_M")
    lock_all(False)
    for joint in bands:
        _set_weight_lock(joint, True)
    _skin_percent(main_skin, main_layer, "FaceJoint_M")
    lock_all(True)
    for joint in bands:
        _set_weight_lock(joint, False)

    mesh = _Mesh(main_layer)
    upper_y, lower_y = _ws("upperFace_M")[1], _ws("lowerFace_M")[1]
    upper = [i for i, point in enumerate(mesh.points) if upper_y <= abs(point.y) <= 9999]
    if upper:
        cmds.skinPercent(main_skin, mesh.vtxs(upper), transformValue=("upperFaceJoint_M", 1))
    lower = [i for i, point in enumerate(mesh.points) if abs(point.y) <= lower_y]
    if lower:
        _skin_percent(main_skin, mesh.vtxs(lower), "lowerFaceJoint_M")
    every = set(range(len(mesh.points)))
    _smooth_flood(main_skin, mesh, every, "upperFaceJoint_M", "middleFaceJoint_M", 10)
    _smooth_flood(main_skin, mesh, every, "lowerFaceJoint_M", "middleFaceJoint_M", 10)
    lock_all(False)  # asSmoothFlood lascia tutto sbloccato
    _remove_unused_influences(main_skin)

    for layer in layers:
        if layer != main_layer:
            _copy_skin_weights(main_layer, layer)

    # dove la pelle non e' pesata sulla testa (collo) il layer non agisce
    off_head = [
        index
        for index in range(len(mesh.points))
        if cmds.skinPercent(
            skin_cluster,
            "{}.vtx[{}]".format(geometry, index),
            query=True,
            transform=head_joint,
        )
        <= 0.0
    ]
    if off_head and len(off_head) < len(mesh.points):
        cmds.skinPercent(main_skin, mesh.vtxs(off_head), transformValue=("FaceJoint_M", 1))

    for _side, eye_geos in _eye_geometries():
        for geo in eye_geos:
            eye_layer = "UpMidLoLayer_" + geo.replace(":", "_", 1)
            cmds.skinPercent(eye_layer + "SC", eye_layer, transformValue=("upperFaceJoint_M", 1))
    as_show_layer("Normal")


def _ensure_head_matrix_inverter(head_joint, opm):
    """Transform che segue la testa: il suo inverso toglie il moto della
    testa dai joint guidati dai controlli (MEL 40514-40521)."""
    if cmds.objExists("HeadMatrixInverter_M"):
        return
    cmds.createNode("transform", name="HeadMatrixInverter_M", parent="FaceDeformationSystem")
    head = "Head_M" if cmds.objExists("Head_M") else head_joint
    # con l'OPM l'inverseMatrix non risente dell'offsetParentMatrix: serve
    # il vincolo classico anche li'
    if opm:
        cmds.setAttr("FitSkeleton.useOffsetParentMatrix", 0)
    try:
        as_parent_constraint(head, "HeadMatrixInverter_M", maintain_offset=True)
    finally:
        if opm:
            cmds.setAttr("FitSkeleton.useOffsetParentMatrix", 1)


def _drive_joints_from_controls(head_joint, ctrl_scale, opm):
    """Occhi, mascella, denti e lingua: il joint (ora fuori dalla testa)
    segue il suo controllo, al netto del moto della testa (MEL 40455-40537)."""
    if cmds.objExists("EyeBaseOffset_R"):
        cmds.parent("EyeBaseOffset_R", "EyeBaseOffset_L", "EyeControls")
    for ctrl in _JOINT_CTRLS:
        for side in _SIDES:
            joint = ctrl + "Joint" + side
            if not cmds.objExists(joint):
                continue
            offset = ctrl + "Offset" + side
            long_name = (cmds.ls(offset, long=True) or [""])[0]
            scaled = "|SideReverse" in long_name
            if scaled:
                if not fnmatch.fnmatchcase(ctrl, "Tongue[1-9]"):
                    cmds.parent(offset, "SideReverseLayered" + side)
                mpd = cmds.createNode("multiplyDivide", name=ctrl + "ScaledMPD" + side)
                cmds.setAttr(mpd + ".input2", ctrl_scale, ctrl_scale, ctrl_scale, type="float3")
            constraints = cmds.listConnections(
                joint, source=True, destination=False, type="constraint"
            )
            if constraints:
                cmds.delete(list(set(constraints)))

            mm = cmds.createNode("multMatrix", name=ctrl + side + "_mm")
            if opm:
                cmds.connectAttr(mm + ".matrixSum", joint + ".offsetParentMatrix", force=True)
            else:
                dm = cmds.createNode("decomposeMatrix", name=ctrl + side + "_dm")
                cmds.connectAttr(mm + ".matrixSum", dm + ".inputMatrix")
                for short, long_attr in (("t", "Translate"), ("r", "Rotate"), ("s", "Scale")):
                    for axis in "XYZ":
                        cmds.connectAttr(
                            "{}.output{}{}".format(dm, long_attr, axis),
                            "{}.{}{}".format(joint, short, axis.lower()),
                            force=True,
                        )
            cmds.connectAttr(ctrl + side + ".worldMatrix", mm + ".matrixIn[1]")
            if ctrl.startswith("Tongue"):
                cmds.setAttr(joint + ".jointOrient", 0, 0, 0, type="float3")

            _ensure_head_matrix_inverter(head_joint, opm)
            cmds.connectAttr("HeadMatrixInverter_M.inverseMatrix", mm + ".matrixIn[2]", force=True)
            cmds.connectAttr(_parent_of(joint) + ".worldInverseMatrix", mm + ".matrixIn[3]")
            if scaled:
                inverse = 1.0 / ctrl_scale
                matrix = [inverse, 0, 0, 0, 0, inverse, 0, 0, 0, 0, inverse, 0, 0, 0, 0, 1]
                cmds.setAttr(mm + ".matrixIn[0]", matrix, type="matrix")


def _localize_lip_and_jaw_follow():
    """LipFollowHead e JawFollow_* non seguono piu' la testa (MEL
    40539-40550)."""
    _delete_existing(
        "LipFollowHead_parentConstraint1",
        "LipFollowHead_scaleConstraint1",
        "LipFollowHeadMM_LipFollowHead",
    )
    follows = _existing("JawFollow" + side for side in _SIDES)
    if not follows or not cmds.objExists("JawJoint_M"):
        return
    constraints = cmds.listRelatives(follows, children=True, type="constraint", path=True)
    if constraints:
        cmds.delete(constraints)
    for follow in follows:
        cmds.parentConstraint("JawJoint_M", follow, maintainOffset=True)
        cmds.scaleConstraint("JawJoint_M", follow, maintainOffset=True)


def _attacher_items():
    """I joint e i controlli che ricevono un attacher (MEL 40578-40594)."""
    items = [
        joint
        for joint in _children("FaceJoint_M", "joint")
        if joint not in ("EyeLidJoints_M", "LipJoints_M")
    ]
    groups = _existing(("LidJoints", "LipRibbonJoints"))
    if groups:
        items += [
            joint
            for joint in cmds.listRelatives(groups, allDescendents=True, type="joint") or []
            if joint not in ("EyeRegionJoint_R", "EyeRegionJoint_L")
        ]
    items += ["LipJoint_R", "LipJoint_L", "upperLip_M", "lowerLip_M"]
    items += _existing(_TACK_ON_CTRLS)
    return [
        item
        for item in items
        if item not in _NO_ATTACHER and not _matches(item, ("EyeJoint_*", "Tongue*Joint_M"))
    ]


def _attacher_position(item, ctrl, side, previous):
    """Dove nasce l'attacher (MEL 40616-40631). Se `item` non esiste (es.
    LipJoint_R) vale la posizione dell'elemento precedente, come nel MEL."""
    pos = _ws(item) if cmds.objExists(item) else previous
    if _matches(item, ("EyeRegion_*", "Eye_*", "Iris_*", "Pupil_*")):
        pos = _ws("innerLidJoint" + side)
    if fnmatch.fnmatchcase(item, "*LipJoint_*"):
        pos = _ws(ctrl + side)
    for pattern, source in _ATTACHER_SOURCES:
        # senza la sorgente (es. EyeBrowCenterJoint_M su un viso senza
        # sopracciglia) il MEL va in errore: qui resta la posizione trovata
        if fnmatch.fnmatchcase(item, pattern) and cmds.objExists(source):
            pos = _ws(source)
    return pos


def _dissolve(node, delete_mm=False):
    """Toglie un transform Attach/Subtract gia' presente (rig v6, MEL
    40642-40658 e 40678-40687): i figli passano al padre."""
    constraints = _children(node, "constraint")
    if constraints:
        cmds.delete(constraints)
    children = _children(node)
    if children:
        cmds.parent(children, _parent_of(node))
    cmds.delete(node)
    if delete_mm:
        tokens = node.split("_")
        _delete_existing("{}MM_{}".format(tokens[0], tokens[1]))


def _layer_controller(ctrl, side, item, opm):
    """Sdoppia un controllo on-face (MEL 40635-40725): l'originale diventa
    <ctrl>Layered e continua a guidare i joint; il nuovo <ctrl>, sotto
    Attach/Offset/Subtract, segue la pelle e lo pilota per connessione."""
    name = ctrl + side
    attacher, attach = ctrl + "Attacher" + side, ctrl + "Attach" + side
    offset, subtract, layered = ctrl + "Offset" + side, ctrl + "Subtract" + side, ctrl + "Layered"
    layered += side

    if cmds.objExists(attach):
        if cmds.listConnections(attach + ".offsetParentMatrix", source=True, destination=False):
            _disconnect_matrix_attr(attach, True)
        _dissolve(attach, delete_mm=True)
    cmds.createNode("transform", name=attach, parent="SideReverseLayered" + side)
    if opm:
        as_parent_constraint(attacher, attach, force_mult_matrix=True, include_pick_matrix=True)
        for attr in ("useRotate", "useScale", "useShear"):
            cmds.setAttr("{}AttachPM{}.{}".format(ctrl, side, attr), 0)
    else:
        cmds.pointConstraint(attacher, attach)

    cmds.rename(offset, ctrl + "OffsetLayered" + side)
    cmds.createNode("transform", name=offset, parent=attach)
    cmds.delete(cmds.orientConstraint(name, offset))
    if cmds.objExists(subtract):
        _dissolve(subtract)
    cmds.createNode("transform", name=subtract, parent=offset)

    # il "nuovo" controllo
    cmds.rename(name, layered)
    cmds.sets(layered, remove="FaceControlSet")
    cmds.createNode("transform", name=name, parent=subtract)
    cmds.sets(name, add="FaceControlSet")
    for attr in ("t", "r", "s"):
        cmds.connectAttr("{}.{}".format(name, attr), "{}.{}".format(layered, attr))
    for shape in cmds.listRelatives(layered, shapes=True, path=True) or []:
        cmds.parent(shape, name, add=True, shape=True)
    cmds.parent("{0}|{0}Shape".format(layered), removeObject=True, shape=True)
    cmds.rename(layered + "Shape", name + "Shape")
    # nodeCast avvisa sugli oggetti istanziati: si saltano
    shapes = cmds.listRelatives(layered, shapes=True, path=True) or []
    instanced = bool(shapes) and len(cmds.listRelatives(shapes[0], allParents=True) or []) > 1
    if not instanced:
        cmds.nodeCast(layered, name, swapNames=True)  # porta gli attributi aggiunti

    if item not in _NO_SUBTRACT:
        mpd = cmds.createNode("multiplyDivide", name=ctrl + "SubtractMultiplyDivide" + side)
        cmds.setAttr(mpd + ".input2", -1, -1, -1, type="float3")
        cmds.connectAttr(name + ".t", mpd + ".input1")
        cmds.connectAttr(mpd + ".output", subtract + ".t")


def _create_wrap(name, deformed, driver):
    """asCreateWrap(name, 0, 0, 1, 0, 0) (MEL 7281-7305) con
    AddWrapInfluence di Maya (doWrapArgList.mel, driver mesh) riscritto in
    cmds: `deformed` segue la superficie di `driver`."""
    wrap = cmds.deformer(deformed, name=name, type="wrap")[0]
    cmds.setAttr(wrap + ".weightThreshold", 0)
    cmds.setAttr(wrap + ".maxDistance", 0)
    cmds.setAttr(wrap + ".exclusiveBind", 1)
    cmds.setAttr(wrap + ".autoWeightThreshold", 0)
    cmds.setAttr(wrap + ".falloffMode", 0)

    driver_shape = _deformed_shape(driver)
    base = cmds.duplicate(driver, name=driver.split("|")[-1].split(":")[-1] + "Base")[0]
    for shape in cmds.listRelatives(base, shapes=True, fullPath=True) or []:
        if cmds.getAttr(shape + ".intermediateObject"):
            cmds.delete(shape)
    cmds.hide(base)
    base_shape = cmds.listRelatives(base, shapes=True, path=True)[0]
    if not cmds.attributeQuery("dropoff", node=driver, exists=True):
        cmds.addAttr(
            driver, shortName="dr", longName="dropoff", defaultValue=4.0, minValue=0.0, maxValue=20
        )
        cmds.setAttr(driver + ".dr", keyable=True)
    if not cmds.attributeQuery("smoothness", node=driver, exists=True):
        cmds.addAttr(driver, shortName="smt", longName="smoothness", defaultValue=0.0, minValue=0.0)
        cmds.setAttr(driver + ".smt", keyable=True)
    if not cmds.attributeQuery("inflType", node=driver, exists=True):
        cmds.addAttr(
            driver,
            attributeType="short",
            shortName="ift",
            longName="inflType",
            defaultValue=2,
            minValue=1,
            maxValue=2,
        )
        infl_type = cmds.optionVar(query="inflType") if cmds.optionVar(exists="inflType") else 2
        cmds.setAttr(driver + ".inflType", infl_type)
    index = len(cmds.listConnections(wrap + ".driverPoints", connections=True) or []) // 2
    cmds.connectAttr(driver_shape + ".worldMesh", "{}.driverPoints[{}]".format(wrap, index))
    cmds.connectAttr(base_shape + ".worldMesh", "{}.basePoints[{}]".format(wrap, index))
    cmds.connectAttr(driver + ".inflType", "{}.inflType[{}]".format(wrap, index))
    cmds.connectAttr(driver + ".smoothness", "{}.smoothness[{}]".format(wrap, index))
    cmds.connectAttr(driver + ".dropoff", "{}.dropoff[{}]".format(wrap, index))
    return wrap


def _create_skin_attach_ctrls(geometry, ctrl_scale, opm):
    """I controlli on-face seguono la pelle (MEL 40574-40765): ognuno ha un
    attacher su AttacherCurve, curva con un punto per controllo, wrappata
    sulla geometria del viso."""
    cmds.createNode("transform", name="SkinAttachCtrls", parent="FaceDeformationSystem")
    cmds.setAttr("SkinAttachCtrls.v", 0)
    cmds.setAttr("SkinAttachCtrls.v", lock=True)

    points, attachers = [], []
    pos = [0.0, 0.0, 0.0]
    for item in _attacher_items():
        tokens = item.split("_")
        ctrl = tokens[0].replace("Joint", "", 1).replace("Ribbon", "", 1)
        side = "_" + tokens[1]
        attacher = cmds.createNode(
            "transform", name=ctrl + "Attacher" + side, parent="SkinAttachCtrls"
        )
        pos = _attacher_position(item, ctrl, side, pos)
        points.append(tuple(pos))
        attachers.append(attacher)
        _layer_controller(ctrl, side, item, opm)

    curve = cmds.curve(degree=1, name="AttacherCurve", point=points)
    cmds.rename(cmds.listRelatives(curve, shapes=True, path=True)[0], "AttacherCurveShape")
    cmds.parent(curve, "SkinAttachCtrls")
    cmds.setAttr("AttacherCurveShape.dispGeometry", 0)
    for index, attacher in enumerate(attachers):
        poci = cmds.createNode("pointOnCurveInfo", name="AttacherCurvePoci" + attacher)
        cmds.connectAttr("AttacherCurve.worldSpace[0]", poci + ".inputCurve", force=True)
        cmds.setAttr(poci + ".turnOnPercentage", 0)
        cmds.setAttr(poci + ".parameter", index)
        cmds.connectAttr(poci + ".position", attacher + ".t", force=True)
    _create_wrap("SkinAttachCtrlsWrap", "AttacherCurve", geometry)

    # i controlli "tack on" non stanno sul loro attacher: offset di compenso
    for item in _existing(_TACK_ON_CTRLS):
        tokens = item.split("_")
        ctrl, side = tokens[0], "_" + tokens[1]
        mirror = -1 if side == "_R" else 1
        delta = [
            (a - b) / ctrl_scale
            for a, b in zip(_ws(ctrl + "OffsetLayered" + side), _ws(ctrl + "Attach" + side))
        ]
        delta[0] *= mirror
        if opm:
            matrix = list(_IDENTITY[:12]) + delta + [1]
            cmds.setAttr("{}AttachMM{}.matrixIn[2]".format(ctrl, side), matrix, type="matrix")
        else:
            cmds.setAttr(
                "{}Attach{}_pointConstraint1.offset".format(ctrl, side), *delta, type="float3"
            )


def _finish_layered_controls():
    """Chiusura del ramo a layer (MEL 40767-40829): controlli del ctrlBox2,
    lingua e denti sotto la mascella, SmilePull, EyeBase, constraint."""
    for ctrl in _BOX2_CTRLS:
        for side in _SIDES:
            if not cmds.objExists(ctrl + side):
                continue
            cmds.setAttr(ctrl + "Layered" + side + ".v", 0)
            cmds.setAttr(ctrl + "Layered" + side + ".v", lock=True)
            tg_xform = "{}MM{}TGXform".format(ctrl, side)
            if cmds.objExists(tg_xform):
                cmds.connectAttr(
                    ctrl + side + ".worldMatrix", tg_xform + ".matrixIn[0]", force=True
                )

    # lingua e denti inferiori ora seguono sempre la mascella
    if cmds.objExists("Tongue0FollowDM_M"):
        _delete_existing("Tongue0FollowDM_M", "lowerTeethFollowDM_M")
    if cmds.objExists("Tongue0BM_M"):
        _delete_existing("Tongue0BM_M", "lowerTeethBM_M")
    if cmds.objExists("Tongue0Offset_M"):
        cmds.parent(_existing(("lowerTeethOffset_M", "Tongue0Offset_M")), "Jaw_M")
    for ctrl in ("Tongue0_M", "lowerTeeth_M"):
        if cmds.objExists(ctrl + ".followJawFollow_M"):
            cmds.deleteAttr(ctrl + ".followJawFollow_M")
    # e SmilePull segue la testa
    for side in ("_R", "_L"):
        if cmds.objExists("SmilePullOffset" + side):
            cmds.parent("SmilePullOffset" + side, "SideReverseLayered" + side)

    if cmds.objExists("EyeBase_R"):
        for side in ("_R", "_L"):
            cmds.parent("EyeRegionOffsetLayered" + side, "SideReverse" + side)
            from_base = cmds.createNode(
                "transform",
                name="EyeRegionFromEyeBase" + side,
                parent="EyeRegionOffsetLayered" + side,
            )
            for attr in ("t", "r", "s"):
                cmds.connectAttr("EyeBase{}.{}".format(side, attr), "{}.{}".format(from_base, attr))
            cmds.parent("SDKEyeRegion" + side, from_base)

    constraints = cmds.listRelatives(
        "FaceJoint_M", allDescendents=True, type="constraint", path=True
    )
    if constraints:
        cmds.parent(constraints, "DeformJointConstraints")
    for side in ("_R", "_L"):
        if cmds.objExists("SmilePullOffset" + side) and cmds.objExists("LipAttach" + side):
            cmds.parent("SmilePullOffset" + side, "LipAttach" + side)


# -- pulizia dopo la conversione ------------------------------------------


def _remove_joint_driving_system():
    """Rig "Mixed" (MEL 40062-40163): le forme passano ai blendShape, quindi
    spariscono le SDK dei controlli on-face; restano quelle di occhi, iride
    e pupilla."""
    cmds.parent("JawSetup", "FaceDeformationSystem")  # la testa non ruota le labbra
    _delete_existing("JawFollowMM_M")
    if cmds.objExists("ctrlMouth_M"):
        cmds.setAttr("ctrlMouth_M.ty", -1)
        cmds.setAttr("ctrlMouth_M.ty", 0)
    cmds.dgdirty(allPlugs=True)
    cmds.refresh()

    for node in cmds.ls("bwSDK*_*_*", type="blendWeighted") or []:
        keep = not _in_face_all_set(node) or _matches(node, ["bw" + p for p in _KEEP_SDKS])
        if not keep:
            cmds.delete(node)
    for node in cmds.ls("SDK*_*_*", type="animCurve") or []:
        if not cmds.objExists(node):
            continue
        if _in_face_all_set(node) and not _matches(node, _KEEP_SDKS):
            cmds.delete(node)
    # via lipRoller e lipPucker
    for node in cmds.ls("*LipJoint*_*RollPMA") or []:
        if _in_face_all_set(node):
            cmds.delete(node)
    _delete_existing("bwctrlEye_R_blink", "bwctrlEye_L_blink")  # niente doppio blink


def _remove_joints(geometry, geos, skin_cluster, head_joint):
    """Rig "BlendShapes" (MEL 40165-40226): tutta la pelle torna al joint
    della testa, joint e controlli on-face vengono cancellati."""
    for geo in geos:
        if geo == geometry:
            continue
        skin = _skin_cluster_of(geo)
        if not skin:
            continue
        _skin_percent(skin, geo, head_joint)
        _remove_unused_influences(skin)

    for joint in _influences(skin_cluster):
        cmds.setAttr(joint + ".liw", 1)
    cmds.setAttr(head_joint + ".lockInfluenceWeights", 0)
    for joint in _children("FaceJoint_M", "joint"):
        if joint not in _KEEP_JOINTS:
            cmds.delete(joint)
    cmds.skinPercent(skin_cluster, geometry, transformValue=(head_joint, 1))
    for joint in _influences(skin_cluster):
        cmds.setAttr(joint + ".liw", 0)

    reverses = ["SideReverse" + side for side in _SIDES]
    if cmds.objExists("upperFace_M"):
        reverses += [band + "SideReverse" + side for band in _UP_MID_LO for side in _SIDES]
        cmds.setAttr("ctrlBox.UpMidLoCtrlVis", 0)
    reverses = _existing(reverses)
    controls = cmds.listRelatives(reverses, children=True, type="transform") if reverses else []
    for control in controls or []:
        if control not in _KEEP_CONTROLS and cmds.objExists(control):
            cmds.delete(control)


def _detach_emotions_from_driving_system():
    """Emotions (e ARKit) guidano solo i loro target, non piu' il miscuglio
    di altri controlli, tranne la mascella (MEL 40228-40253)."""
    blend_weighteds = []
    if cmds.objExists("ctrlEmotions_M"):
        blend_weighteds += (
            cmds.listConnections(
                "ctrlEmotions_M", source=False, destination=True, type="blendWeighted"
            )
            or []
        )
    if cmds.objExists("ctrlARKit_M"):
        for node in (
            cmds.listConnections(
                "ctrlARKit_M", source=False, destination=True, type="blendWeighted"
            )
            or []
        ):
            if node.startswith("bwctrlARKit_M_eyeLook") or node == "bwctrlARKit_M_tongueOut":
                continue
            blend_weighteds.append(node)
    for node in blend_weighteds:
        if not cmds.objExists(node):
            continue
        curves = cmds.listConnections(node, source=False, destination=True, type="animCurve")
        for curve in curves or []:
            if not cmds.objExists(curve) or not _in_face_all_set(curve):
                continue
            if not curve.startswith("bwctrlMouth_M_translateY"):
                cmds.delete(curve)


def _clean_arkit(geometry):
    """Occhi o lingua parte della mesh del viso: via le SDK di ARKit che li
    ruoterebbero due volte (MEL 40862-40872)."""
    if not cmds.objExists("ctrlARKit_M"):
        return
    if (get_fit_option("RightEye") or "").startswith(geometry + "."):
        nodes = [
            "bwctrlARKit_M_eyeLook{}{}".format(direction, eye)
            for eye in ("Left", "Right")
            for direction in ("Up", "Down", "Out", "In")
        ]
        curves = cmds.listConnections(
            _existing(nodes), source=False, destination=True, type="animCurve"
        )
        if curves:
            cmds.delete(curves)
    if (get_fit_option("Tongue") or "").startswith(geometry + ".") and cmds.objExists("SDKJaw_M"):
        blend_weighteds = cmds.listConnections(
            "SDKJaw_M",
            skipConversionNodes=True,
            source=True,
            destination=False,
            type="blendWeighted",
        )
        if blend_weighteds:
            cmds.delete(blend_weighteds)


def _clean_driven_keys():
    """Via le animCurve rimaste senza driver, e ogni blendWeighted che
    guida un target tiene il solo primo ingresso (MEL 40880-40903)."""
    for node in cmds.listHistory(_BS) or []:
        if not cmds.objExists(node) or not cmds.ls(node, type="animCurve"):
            continue
        if not cmds.listConnections(node, source=True, destination=False):
            cmds.delete(node)
    curves = cmds.listConnections(_BS, source=True, destination=False, type="animCurve") or []
    for curve in curves:
        for node in (
            cmds.listConnections(curve, source=True, destination=False, type="blendWeighted") or []
        ):
            conns = (
                cmds.listConnections(
                    node, source=True, destination=False, plugs=True, connections=True
                )
                or []
            )
            for destination, source in list(zip(conns[0::2], conns[1::2]))[1:]:
                if cmds.isConnected(source, destination):
                    cmds.disconnectAttr(source, destination)


def _select_all_nodes():
    """Seleziona ogni nodo della scena tranne set e partition, senza
    espandere nulla (MEL 39652-39654 e 40908-40910)."""
    cmds.select(cmds.ls(objectsOnly=True), noExpand=True)
    for node_type in ("objectSet", "partition"):
        nodes = cmds.ls(type=node_type)
        if nodes:
            cmds.select(nodes, deselect=True, noExpand=True)


def _snapshot_scene():
    """Il set allBeforeConvertToBS con tutto cio' che esiste prima della
    conversione (MEL 39652-39656). E' un set vero, come nel MEL, e non un
    elenco di nomi: i controlli on-face vengono ricreati con lo stesso
    nome e scambiati con nodeCast, e solo l'appartenenza al set dice quali
    nodi sono nuovi."""
    _select_all_nodes()
    cmds.sets(name=_BEFORE_SET)
    cmds.select(clear=True)


def _add_new_nodes_to_face_all_set():
    """Tutto cio' che non era in allBeforeConvertToBS entra nel FaceAllSet:
    senza, il ReBuild non riconosce i nodi nuovi (MEL 40905-40915)."""
    _select_all_nodes()
    cmds.select(_BEFORE_SET, deselect=True)
    if cmds.ls(selection=True):
        cmds.sets(add="FaceAllSet")
    cmds.select(clear=True)
    cmds.sets(clear=_BEFORE_SET)
    cmds.delete(_BEFORE_SET)


# -- procedura ------------------------------------------------------------


def _controllers(keep_joints):
    """I controlli da convertire (MEL 39758-39770): il primo figlio di ogni
    gruppo del ctrlBox, piu' SmilePull_* nel rig "Mixed"."""
    objs = []
    for group in cmds.listRelatives("ctrlBox", children=True, type="transform") or []:
        children = cmds.listRelatives(group, children=True, type="transform") or []
        if children:
            objs.append(children[0])
    if keep_joints:
        objs += _existing(("SmilePull_R", "SmilePull_L"))
    return objs


def _target_geometries(geometry):
    """Le geometrie che ricevono i target (MEL 39775-39795): Face,
    sopracciglia, ciglia, extra, denti e lingua; non i bulbi oculari."""
    tokens = [geometry]
    for option in ("Eyebrow", "Eyelash", "Extras", "UpperTeeth", "LowerTeeth", "Tongue"):
        tokens += (get_fit_option(option) or "").split()
    geos = []
    for node in cmds.ls(tokens, objectsOnly=True) or []:
        if cmds.objectType(node) == "mesh":
            node = cmds.listRelatives(node, parent=True)[0]
        if node not in geos:
            geos.append(node)
    return geos


def _missing_prerequisite(geometry, head_joint, skin_cluster, all_face_geo, use_skin_layers):
    """Il primo prerequisito mancante, o ""."""
    if not cmds.objExists(FIT_SKELETON):
        return FIT_SKELETON
    required = list(_REQUIRED_NODES)
    if use_skin_layers:
        required += _REQUIRED_FOR_LAYERS
    for node in required:
        if not cmds.objExists(node):
            return node
    for label, node in (
        ("Face geometry", geometry),
        ("head joint", head_joint),
        ("skinCluster", skin_cluster),
    ):
        if not node or not cmds.objExists(node):
            return '{} "{}"'.format(label, node)
    if cmds.nodeType(skin_cluster) != "skinCluster":
        return 'skinCluster "{}"'.format(skin_cluster)
    if not cmds.objExists("JawPivot") and not cmds.objExists("outerLid_R"):
        return "JawPivot"
    tokens = []
    for option in ("Eyebrow", "Eyelash", "Extras", "UpperTeeth", "LowerTeeth", "Tongue"):
        tokens += (get_fit_option(option) or "").split()
    for token in tokens:
        if not cmds.objExists(token):
            return 'geometry "{}"'.format(token)
    if use_skin_layers:
        for geo in all_face_geo:
            if not cmds.objExists(geo):
                return 'All-Head object "{}"'.format(geo)
            if not _skin_cluster_of(geo):
                return 'skinCluster of "{}"'.format(geo)
    return ""


def _convert(keep_joints, keep_targets, use_skin_layers, geometry, head_joint, skin_cluster):
    opm = as_get_opm()
    all_face_geo = (get_fit_option("AllHead") or "").split()
    limits_status = cmds.getAttr("ctrlBox.limits")
    ctrl_scale = cmds.getAttr("OnFacecontrols.sx")
    # JawPivot manca nei face setup parziali (MEL 39647-39650)
    cheek_x = _ws("JawPivot" if cmds.objExists("JawPivot") else "outerLid_R")[0]
    _snapshot_scene()

    # asFaceUpdateInfo senza UI: resta il solo valore sul FaceFitSkeleton
    set_fit_option("RigType", 2 if keep_joints else 1)

    if use_skin_layers:
        _create_face_joints_layers(geometry, all_face_geo)
    else:
        _blend_shape_front_of_chain(geometry, _BS)

    objs = _controllers(keep_joints)
    if limits_status:
        cmds.setAttr("ctrlBox.limits", 0)
    geos = _target_geometries(geometry)
    _go_to_build_pose()

    # deltaMush e blendShape spenti mentre si fotografano i target
    envelopes = []
    for node in cmds.listHistory(geometry) or []:
        if cmds.objectType(node) in ("deltaMush", "blendShape"):
            envelopes.append((node, cmds.getAttr(node + ".envelope")))
            cmds.setAttr(node + ".envelope", 0)

    cmds.select(clear=True)
    if cmds.objExists(_TARGETS_GROUP):
        children = cmds.listRelatives(_TARGETS_GROUP, children=True, path=True)
        if children:
            cmds.move(0, cheek_x * -2.5, 0, children, relative=True)
    else:
        cmds.createNode("transform", name=_TARGETS_GROUP)

    # l'EyeBase non esiste nel rig a soli blendShape (MEL 39817-39827)
    if not use_skin_layers:
        for side in ("_R", "_L"):
            for node, child, parent in (
                ("EyeBaseFollowTS", "EyeAim", "EyeOffset"),
                ("EyeBaseFollowR", "SDKEye", "EyeAim"),
                ("EyeBaseOffset", "EyeRegionOffset", "SideReverse"),
            ):
                if cmds.objExists(node + side):
                    cmds.parent(child + side, parent + side)
                    cmds.delete(node + side)

    _convert_controllers(objs, geos, keep_joints, keep_targets, cheek_x)
    if limits_status:
        cmds.setAttr("ctrlBox.limits", 1)

    if keep_joints:
        _remove_joint_driving_system()
    else:
        _remove_joints(geometry, geos, skin_cluster, head_joint)
    _detach_emotions_from_driving_system()

    if not use_skin_layers:
        for child in _children("FaceDeformationSystem"):
            if child != "EyeSetup":
                cmds.delete(child)
    else:
        _bind_main_skin_to_head(geometry, all_face_geo, head_joint)
        _create_layered_hierarchy()
        _move_eye_lattices_to_layers()
        if cmds.objExists("upperSideReverse_R"):
            _up_mid_lo_as_layer(geometry, skin_cluster, head_joint)
        _drive_joints_from_controls(head_joint, ctrl_scale, opm)
        _localize_lip_and_jaw_follow()
        _create_skin_attach_ctrls(geometry, ctrl_scale, opm)
        _finish_layered_controls()

    # ctrlPhonemes_M: i moltiplicatori raddoppierebbero l'effetto (MEL 40833-40839)
    if cmds.objExists("ctrlPhonemes_M") and cmds.objExists("bwctrlPhonemes_M_lip"):
        for attr, value in (("lip", 0), ("jaw", 1)):
            cmds.setAttr("ctrlPhonemes_M." + attr, value)
            cmds.setAttr("ctrlPhonemes_M." + attr, lock=True, keyable=False)
        cmds.setAttr("ctrlPhonemes_M.multipliers", keyable=False)

    if keep_joints:
        # FaceJoint_M non segue piu' la testa: i FleshyEyes restano relativi a lei
        for side in ("_R", "_L"):
            if cmds.objExists("EyeJointMM" + side):
                cmds.connectAttr(
                    "FaceDeformationFollowHead.worldInverseMatrix[0]",
                    "EyeJointMM{}.matrixIn[1]".format(side),
                    force=True,
                )
        # le fasce UpMidLo non hanno bisogno dell'attacher
        if cmds.objExists("SideReverseLayered_M"):
            for band in _UP_MID_LO:
                if cmds.objExists(band + "FaceOffset_M"):
                    cmds.parent(band + "FaceOffset_M", "SideReverseLayered_M")
                    cmds.delete(band + "FaceAttach_M")

    if not keep_targets:
        _delete_existing(_TARGETS_GROUP)
    for node, value in envelopes:
        if cmds.objExists(node):
            cmds.setAttr(node + ".envelope", value)

    _clean_arkit(geometry)
    for geo in all_face_geo:
        skin = _skin_cluster_of(geo) if cmds.objExists(geo) else ""
        if skin:
            try:
                cmds.skinPercent(skin, geo, normalize=True)
            except RuntimeError:
                pass
    _clean_driven_keys()

    _add_new_nodes_to_face_all_set()
    _capture_build_pose()  # MEL 40917-40928


def convert_to_blend_shapes(keep_joints=False, keep_targets=False):
    """Converte il viso da joint a blendShape (parita' asBSConvertDStoBS,
    MEL 39582-40935).

    Per ogni attributo dei controlli del ctrlBox fotografa la geometria
    deformata, la aggiunge come target ad asFaceBS (e ad asFaceBS_<geo>
    per sopracciglia, ciglia, extra, denti e lingua) e collega il target
    al controllo con una driven key.

    Args:
        keep_joints: checkBox "keep joints". False = rig "BlendShapes":
            joint e controlli on-face cancellati. True = rig "Mixed": i
            joint restano su un layer di deformazione.
        keep_targets: checkBox "keep blendShape target objects": le mesh
            dei target restano sotto asBlendShapes, affiancate.

    Ritorna bool. I prerequisiti mancanti lasciano la scena intatta; un
    errore a conversione avviata la lascia convertita a meta'.
    """
    geometry = get_fit_option("Face") or ""
    head_joint = get_fit_option("HeadJoint") or ""
    skin_cluster = get_fit_option("SkinCluster") or ""
    all_face_geo = (get_fit_option("AllHead") or "").split()
    use_skin_layers = bool(keep_joints) and not get_fit_option("GameEngine")

    if cmds.objExists(_BS):
        cmds.warning("convert_to_blend_shapes: Already converted to BlendShapes.")
        return False
    missing = _missing_prerequisite(
        geometry, head_joint, skin_cluster, all_face_geo, use_skin_layers
    )
    if missing:
        cmds.warning("convert_to_blend_shapes: {} not found, build the face first".format(missing))
        return False
    if (
        use_skin_layers
        and cmds.attributeQuery("version", node="FaceGroup", exists=True)
        and cmds.getAttr("FaceGroup.version") < _MIN_VERSION
    ):
        cmds.warning(
            "convert_to_blend_shapes: face-rig version older than v{} detected, "
            "rebuild the face first".format(_MIN_VERSION)
        )
        return False
    if keep_joints and not use_skin_layers:
        cmds.warning(
            "convert_to_blend_shapes: keep_joints with the GameEngine option builds no skin "
            "layers (as in AdvancedSkeleton, whose UI does not offer this combination)"
        )

    auto_key = cmds.autoKeyframe(query=True, state=True)
    if auto_key:
        cmds.autoKeyframe(state=False)
    try:
        _convert(
            bool(keep_joints),
            bool(keep_targets),
            use_skin_layers,
            geometry,
            head_joint,
            skin_cluster,
        )
    except (RuntimeError, TypeError, ValueError, IndexError) as exc:
        cmds.warning(
            "convert_to_blend_shapes: failed, the scene is left half converted: {}".format(exc)
        )
        if cmds.objExists(_BEFORE_SET):
            cmds.delete(_BEFORE_SET)
        return False
    finally:
        if auto_key:
            cmds.autoKeyframe(state=True)
    cmds.select(clear=True)
    cmds.dgdirty(allPlugs=True)  # alcuni skinCluster si normalizzano solo cosi'
    print("// Converted DrivingSystems to BlendShapes.")
    return True

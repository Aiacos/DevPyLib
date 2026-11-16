"""HeadSquash: squash & stretch della testa con un lattice guidato da una
spline IK (frame " HeadSquash" del pannello Face, MEL AdvancedSkeleton.mel
2024-2040).

Port di:
- asAdvancedSquash   (MEL 44397-44681) -> create_head_squash
- asDeleteHeadSquash (MEL 44683-44691) -> delete_head_squash
- asOptimizeSquash   (MEL 44693-44750) -> optimize_head_squash
- asAddToHeadSquash  (MEL 44752-44756) -> add_to_head_squash
- helper: asDeformer (MEL 38770-38794), asGetOpm (MEL 23474, gia' in
  build_utils), asInvertSelection (MEL 67304-67326, solo il ramo vtx).

I textField della UI (asFaceHeadJointTextField, asFaceFaceTextField,
asFaceSkinClusterTextField, asFaceAllHeadTextField) si leggono dalle
opzioni omonime di FaceFitSkeleton (fit_options).

Divergenze intenzionali (dettaglio in docs/gap-analysis.md, sezione 5v):
- i prerequisiti mancanti danno cmds.warning + False invece dell'errore
  MEL a meta' procedura; se la costruzione fallisce i nodi gia' creati
  vengono rimossi;
- create_head_squash rifiuta di costruire un secondo squash (il MEL non
  controlla e lascia nodi rinominati a meta');
- SquashSet si calcola per differenza degli UUID dei nodi invece che con
  il set temporaneo allBeforeSquashBuild: il contenuto e' lo stesso;
- il lattice si crea con cmds.lattice (deformer-set legacy forzati come
  asDeformer) e cluster/skinCluster con cmds, senza i wrapper MEL
  newCluster/newSkinCluster: nessun mel.eval;
- niente waitCursor e niente progressBar (quindi niente annullamento a
  meta') in optimize_head_squash;
- delete_head_squash/add_to_head_squash segnalano con warning + False i
  casi in cui il MEL esce in silenzio o va in errore.
"""

from contextlib import contextmanager

import maya.cmds as cmds

from .build_utils import as_get_opm
from .face_finish import _mel_value
from .fit_options import FIT_SKELETON, get_fit_option

_SQUASH_SETUP = "SquashSetup"
_SQUASH_SET = "SquashSet"
_FFD = "squashFfd"
_FFD_SET = "squashFfdSet"
_LATTICE = "squashFfdLattice"
_FFD_BASE = "squashFfdBase"
_SKIN = "squashIKSC"
_CONTROLS = ("squashTop_M", "squashMiddle_M", "squashBottom_M", "squashBase_M")
_YELLOW = 17  # overrideColor dei controlli on-face

# cubo wireframe dei controlli (MEL 44430)
_CUBE_POINTS = (
    (1, 1, 1),
    (1, -1, 1),
    (-1, -1, 1),
    (-1, 1, 1),
    (1, 1, 1),
    (1, 1, -1),
    (1, -1, -1),
    (1, -1, 1),
    (1, -1, -1),
    (-1, -1, -1),
    (-1, 1, -1),
    (1, 1, -1),
    (-1, 1, -1),
    (-1, 1, 1),
    (-1, -1, 1),
    (-1, -1, -1),
)

# nodi e plug che asAdvancedSquash usa senza controllarli
_REQUIRED_NODES = (
    "FaceFitSkeletonHeightShape",
    "FaceFitSkeletonShape",
    "FaceDeformationSystem",
    "FaceMotionSystem",
    "FaceControlSet",
    "FaceAllSet",
    "OnFacecontrols",
    "faceBuildPose.udAttr",
    "ctrlBox.SquashCtrlVis",
)


@contextmanager
def _legacy_deformer_sets():
    """Forza i deformer-set legacy per i deformer creati nel blocco (parita'
    asDeformer, MEL 38770-38794): squashFfdSet deve essere un objectSet
    vero, perche' asOptimizeSquash/asAddToHeadSquash ne cambiano i membri.
    Senza preferenze utente (mayapy) l'optionVar non esiste e Maya usa i
    component tags: va forzata anche li', e rimossa dopo."""
    name = "deformationUseComponentTags"
    existed = bool(cmds.optionVar(exists=name))
    restore_tags = bool(cmds.optionVar(query=name)) if existed else True
    if restore_tags:
        cmds.optionVar(intValue=(name, 0))
    try:
        yield
    finally:
        if not existed:
            cmds.optionVar(remove=name)
        elif restore_tags:
            cmds.optionVar(intValue=(name, 1))


def _lock_hide(node, attrs):
    for attr in attrs:
        cmds.setAttr("{}.{}".format(node, attr), lock=True, keyable=False)


def _missing_prerequisite(head_joint, all_face_geo):
    """Il primo prerequisito mancante di create_head_squash, o ""."""
    if not cmds.objExists(FIT_SKELETON) or not cmds.attributeQuery(
        "faceScale", node=FIT_SKELETON, exists=True
    ):
        return FIT_SKELETON + ".faceScale"
    for node in _REQUIRED_NODES:
        if not cmds.objExists(node):
            return node
    if not head_joint or not cmds.objExists(head_joint):
        return 'head joint "{}"'.format(head_joint)
    for geo in all_face_geo:
        if not cmds.objExists(geo):
            return 'All-Head object "{}"'.format(geo)
    return ""


def _create_controls(scale, top_y, base_y):
    """Controlli squashTop/Middle/Bottom/Base e relativi offset (MEL
    44429-44469)."""
    cmds.createNode("transform", name=_SQUASH_SETUP, parent="FaceDeformationSystem")
    curve = cmds.curve(degree=1, point=_CUBE_POINTS, knot=list(range(len(_CUBE_POINTS))))
    cmds.rename(curve, "squashTop_M")
    cmds.setAttr("squashTop_MShape.overrideEnabled", 1)
    cmds.setAttr("squashTop_MShape.overrideColor", 13)
    cmds.createNode("transform", name="squashTopOffset")
    cmds.parent("squashTop_M", "squashTopOffset")
    cmds.xform("squashTopOffset", worldSpace=True, translation=(0, top_y, 0))
    cmds.xform("squashTop_M", worldSpace=True, scale=(scale / 0.75, scale / 5.0, scale / 5.0))
    cmds.makeIdentity("squashTop_M", apply=True, translate=True, rotate=True, scale=True, normal=0)
    cmds.sets("squashTop_M", add="FaceControlSet")

    cmds.duplicate("squashTopOffset", name="SquashControls")
    cmds.rename("SquashControls|squashTop_M", "squashBase_M")
    cmds.xform("SquashControls", worldSpace=True, translation=(0, base_y, 0))

    cmds.duplicate("squashTopOffset", name="squashMiddleOffset")
    cmds.rename("squashMiddleOffset|squashTop_M", "squashMiddle_M")
    cmds.xform("squashMiddleOffset", worldSpace=True, translation=(0, (base_y + top_y) / 2, 0))
    cmds.scale(1.5, 1, 1, "squashMiddle_M", relative=True)
    cmds.makeIdentity(
        "squashMiddle_M", apply=True, translate=True, rotate=True, scale=True, normal=0
    )

    cmds.duplicate("squashTopOffset", name="squashBottomOffset")
    cmds.rename("squashBottomOffset|squashTop_M", "squashBottom_M")
    cmds.xform("squashBottomOffset", worldSpace=True, translation=(0, base_y, 0))
    cmds.scale(1.5, 0.1, 1.5, "squashBottom_M", relative=True)
    cmds.makeIdentity(
        "squashBottom_M", apply=True, translate=True, rotate=True, scale=True, normal=0
    )

    cmds.parent("squashTopOffset", "squashMiddleOffset", "squashBottomOffset", "squashBase_M")

    cmds.addAttr(
        "squashTop_M",
        keyable=True,
        longName="volume",
        attributeType="double",
        softMinValue=0,
        hasSoftMinValue=True,
        softMaxValue=10,
        hasSoftMaxValue=True,
        defaultValue=10,
    )
    cmds.createNode("unitConversion", name="squashTopVolumeUC")
    cmds.setAttr("squashTopVolumeUC.conversionFactor", 0.1)
    cmds.connectAttr("squashTop_M.volume", "squashTopVolumeUC.input")

    _lock_hide("squashTop_M", ("rx", "ry", "rz", "sx", "sy", "sz", "v"))
    _lock_hide("squashMiddle_M", ("rx", "ry", "rz", "sx", "sy", "sz", "v"))
    _lock_hide("squashBase_M", ("sx", "sy", "sz", "v"))


def _lattice_targets(all_face_geo):
    """Cosa entra nel lattice (MEL 44471-44491): le geometrie AllHead senza
    wrap/wire nella history (es. sopracciglia wrappate) e le shape dei
    controlli on-face, tranne quelle generate da un nodo *_*TG."""
    targets = []
    for geo in all_face_geo:
        history = cmds.listHistory(geo, future=False, pruneDagObjects=True, levels=4) or []
        if any(cmds.nodeType(node) in ("wrap", "wire") for node in history):
            continue
        if geo not in targets:
            targets.append(geo)
    shapes = (
        cmds.listRelatives(
            "OnFacecontrols", allDescendents=True, type=("nurbsCurve", "nurbsSurface")
        )
        or []
    )
    for shape in shapes:
        creators = cmds.listConnections(shape + ".create") or [""]
        tokens = creators[0].split("_")
        if len(tokens) > 1 and tokens[-1].endswith("TG"):  # gmatch "*_*TG"
            continue
        targets.append(shape)
    return targets


def _create_lattice(targets, top_y, base_y):
    """Lattice 2x11x2 centrato fra base e sommita' della testa (MEL
    44494-44507)."""
    with _legacy_deformer_sets():
        created = cmds.lattice(
            targets, divisions=(2, 11, 2), objectCentered=True, ldivisions=(2, 2, 2)
        )
    cmds.rename(created[0], _FFD)
    cmds.rename(created[1], _LATTICE)
    cmds.rename(created[2], _FFD_BASE)
    deformer_sets = cmds.listConnections(_FFD + ".message", type="objectSet") or []
    if not deformer_sets:
        raise RuntimeError("the lattice has no deformer set")
    cmds.rename(deformer_sets[0], _FFD_SET)
    height = top_y - base_y
    for node in (_LATTICE, _FFD_BASE):
        cmds.xform(node, worldSpace=True, translation=(0, (top_y + base_y) / 2, 0))
    for node in (_LATTICE, _FFD_BASE):
        cmds.xform(node, scale=(height, height, height))
    for node in (_LATTICE, _FFD_BASE):
        cmds.scale(1.25, 1.25, 1.25, node, relative=True)
    cmds.setAttr(_FFD + ".outsideLattice", 1)
    cmds.parent(_FFD_BASE, "squashBase_M")


def _lattice_row_height(row):
    return cmds.xform(
        "{}.pt[0][{}][1]".format(_LATTICE, row), query=True, worldSpace=True, translation=True
    )[1]


def _create_ik_spline(scale):
    """Catena squashIKX0..9 lungo il lattice, spline IK con 5 cluster e skin
    del lattice sulla catena (MEL 44508-44558)."""
    cmds.createNode("transform", name="squashXup")
    cmds.setAttr("squashXup.r", 90, 0, 90, type="float3")
    cmds.select("squashXup")
    cmds.joint(name="squashIKX0", position=(0, _lattice_row_height(1), 0))
    cmds.select("squashXup")
    for i in range(1, 10):
        cmds.joint(name="squashIKX{}".format(i), position=(0, _lattice_row_height(i), 0))
    cmds.setAttr("squashIKX1.segmentScaleCompensate", 0)
    handle = cmds.ikHandle(
        name="squashIKHandle",
        createCurve=True,
        numSpans=2,
        solver="ikSplineSolver",
        startJoint="squashIKX1",
        endEffector="squashIKX9",
    )
    cmds.rename(handle[1], "squashIKEffector")
    cmds.rename(handle[2], "squashIKECurve")
    for i in range(5):
        cluster = cmds.cluster("squashIKECurve.cv[{}]".format(i), envelope=1)
        cmds.rename(cluster[0], "squashIKCluster{}".format(i))
        cmds.rename(cluster[1], "squashIKClusterHandle{}".format(i))

    joints = ["squashIKX{}".format(i) for i in range(10)]
    skin = cmds.skinCluster(
        joints + [_LATTICE],
        toSelectedBones=True,
        maximumInfluences=3,
        dropoffRate=4,
        removeUnusedInfluence=False,
    )
    cmds.rename(skin[0], _SKIN)
    # squashIKX1 resta senza punti: la base e' di squashIKX0
    cmds.skinPercent(_SKIN, _LATTICE + ".pt[0:1][0:1][0:1]", transformValue=[("squashIKX0", 1)])
    for i in range(2, 9):
        cmds.skinPercent(
            _SKIN,
            "{}.pt[0:1][{}][0:1]".format(_LATTICE, i),
            transformValue=[("squashIKX{}".format(i), 1)],
        )
    cmds.skinPercent(_SKIN, _LATTICE + ".pt[0:1][9:10][0:1]", transformValue=[("squashIKX9", 1)])

    cmds.delete(cmds.pointConstraint("squashIKClusterHandle4", "squashIKClusterHandle3"))
    cmds.parent("squashIKClusterHandle3", "squashIKClusterHandle4")
    cmds.move(0, scale * -0.1, 0, "squashIKClusterHandle3", relative=True)

    cmds.delete(cmds.pointConstraint("squashIKClusterHandle0", "squashIKClusterHandle1"))
    cmds.parent("squashIKClusterHandle1", "squashIKClusterHandle0")
    cmds.move(0, scale * 0.1, 0, "squashIKClusterHandle1", relative=True)

    cmds.parent("squashIKClusterHandle4", "squashTop_M")
    cmds.parent("squashIKClusterHandle2", "squashMiddle_M")
    cmds.parent("squashIKClusterHandle0", "squashIKClusterHandle1", "squashIKX0", "squashBottom_M")


def _create_stretch_network(head_joint):
    """Stretch della catena dalla lunghezza della curva e compensazione del
    volume (MEL 44560-44611)."""
    cmds.createNode("curveInfo", name="squashIKCurveInfo")
    cmds.connectAttr("squashIKECurveShape.worldSpace[0]", "squashIKCurveInfo.inputCurve")

    cmds.createNode("multiplyDivide", name="squashIKCurveInfoNormalize")
    cmds.setAttr("squashIKCurveInfoNormalize.operation", 2)
    cmds.connectAttr("squashIKCurveInfo.arcLength", "squashIKCurveInfoNormalize.input1X")
    cmds.setAttr(
        "squashIKCurveInfoNormalize.input2X", cmds.getAttr("squashIKCurveInfoNormalize.input1X")
    )
    cmds.createNode("multiplyDivide", name="squashIKScale")

    # compensa la scala del controllo Main
    cmds.createNode("multiplyDivide", name="squashIKCurveInfoMainScale")
    cmds.setAttr("squashIKCurveInfoMainScale.operation", 2)
    cmds.connectAttr("squashIKCurveInfoNormalize.outputX", "squashIKCurveInfoMainScale.input1X")
    if cmds.objExists("MainScaleMultiplyDivide"):  # assente nei face setup senza body
        cmds.connectAttr("MainScaleMultiplyDivide.outputY", "squashIKCurveInfoMainScale.input2X")

    cmds.connectAttr("squashIKCurveInfoMainScale.outputX", "squashIKScale.input1X")
    cmds.createNode("multiplyDivide", name="squashIKStretch")
    cmds.connectAttr("squashIKScale.outputX", "squashIKStretch.input2X")
    cmds.setAttr("squashIKStretch.input1X", cmds.getAttr("squashIKX2.tx"))

    if as_get_opm():
        cmds.createNode("decomposeMatrix", name="squashIKCurveInfoMainScaleDM")
        cmds.connectAttr(
            head_joint + ".offsetParentMatrix", "squashIKCurveInfoMainScaleDM.inputMatrix"
        )
        cmds.connectAttr("squashIKCurveInfoMainScaleDM.outputScaleX", "squashIKScale.input2X")
    else:
        cmds.connectAttr(head_joint + ".sx", "squashIKScale.input2X")

    cmds.setAttr("squashIKScale.operation", 2)
    for i in range(1, 10):
        cmds.connectAttr("squashIKStretch.outputX", "squashIKX{}.tx".format(i))
    cmds.createNode("multiplyDivide", name="squashVolume1Over")
    cmds.connectAttr("squashIKScale.outputX", "squashVolume1Over.input2X")
    cmds.setAttr("squashVolume1Over.input1X", 1)
    cmds.setAttr("squashVolume1Over.operation", 2)
    cmds.createNode("multiplyDivide", name="squashVolumePow")
    cmds.connectAttr("squashVolume1Over.outputX", "squashVolumePow.input1X")
    cmds.setAttr("squashVolumePow.operation", 3)
    cmds.setAttr("squashVolumePow.input2X", 0.5)
    cmds.createNode("blendTwoAttr", name="squashBlendTwo")
    cmds.setAttr("squashBlendTwo.input[0]", 1)
    cmds.connectAttr("squashVolumePow.outputX", "squashBlendTwo.input[1]")
    cmds.connectAttr("squashTopVolumeUC.output", "squashBlendTwo.attributesBlender")
    for i in range(2, 9):
        cmds.connectAttr("squashBlendTwo.output", "squashIKX{}.sy".format(i))
        cmds.connectAttr("squashBlendTwo.output", "squashIKX{}.sz".format(i))


def _place_in_rig(head_joint):
    """Gerarchia finale e nodi nascosti (MEL 44613-44625)."""
    cmds.parent(_LATTICE, "squashIKECurve", "squashIKHandle", _SQUASH_SETUP)
    cmds.parent("squashIKX1", "FaceMotionSystem")
    cmds.parent("SquashControls", "FaceMotionSystem")
    cmds.parentConstraint(head_joint, "SquashControls", maintainOffset=True)
    cmds.delete("squashXup")

    hidden = ["squashIKX1", _FFD_BASE, "squashIKHandle", "squashIKX0"]
    hidden += ["squashIKClusterHandle{}".format(i) for i in range(5)]
    for node in hidden:
        cmds.setAttr(node + ".v", 0, lock=True)


def _include_on_face_controls(face_control_set_members):
    """Aggiunge al lattice le shape gialle dei controlli on-face (MEL
    44636-44649), saltando quelle del ctrlBox e gli AimEye."""
    for member in face_control_set_members:
        long_name = (cmds.ls(member, long=True) or [""])[0]
        if "|ctrlBox|" in long_name or member.startswith("AimEye_"):
            continue
        shapes = cmds.listRelatives(member, shapes=True, fullPath=True) or []
        if not shapes:
            continue
        if cmds.getAttr(shapes[0] + ".overrideColor") != _YELLOW:
            continue
        cmds.sets(shapes[0], add=_FFD_SET)


def _update_build_pose():
    """Accoda a faceBuildPose.udAttr i setAttr dei controlli dello squash
    (MEL 44652-44663)."""
    commands = []
    for control in _CONTROLS:
        for attr in cmds.listAttr(control, keyable=True, shortNames=True) or []:
            plug = "{}.{}".format(control, attr)
            if cmds.getAttr(plug, lock=True):
                continue
            commands.append("setAttr {} {};".format(plug, _mel_value(cmds.getAttr(plug))))
    existing = cmds.getAttr("faceBuildPose.udAttr") or ""
    cmds.setAttr("faceBuildPose.udAttr", existing + "".join(commands), type="string")


def _new_nodes(uuids_before, with_sets):
    """I nodi nati dopo lo snapshot `uuids_before` (nomi lunghi)."""
    new_uuids = [uuid for uuid in cmds.ls(uuid=True) if uuid not in uuids_before]
    nodes = cmds.ls(new_uuids, long=True) if new_uuids else []
    if with_sets:
        return nodes
    excluded = set(cmds.ls(type=("objectSet", "partition"), long=True) or [])
    return [node for node in nodes if node not in excluded]


def _build_head_squash(head_joint, all_face_geo, uuids_before):
    face_control_set_members = cmds.sets("FaceControlSet", query=True) or []
    scale = cmds.getAttr(FIT_SKELETON + ".faceScale") / 3.0
    top_y = cmds.xform(
        "FaceFitSkeletonHeightShape.cv[0]", query=True, worldSpace=True, translation=True
    )[1]
    base_y = cmds.xform(
        "FaceFitSkeletonShape.cv[0]", query=True, worldSpace=True, translation=True
    )[1]

    _create_controls(scale, top_y, base_y)
    _create_lattice(_lattice_targets(all_face_geo), top_y, base_y)
    _create_ik_spline(scale)
    _create_stretch_network(head_joint)
    _place_in_rig(head_joint)
    _include_on_face_controls(face_control_set_members)
    _update_build_pose()

    for control in ("squashTop_M", "squashMiddle_M", "squashBase_M"):
        cmds.connectAttr("ctrlBox.SquashCtrlVis", control + "Shape.overrideVisibility")

    # SquashSet: tutto cio' che e' nato qui, tranne set e partition (MEL
    # 44669-44677); e' cio' che delete_head_squash cancella
    cmds.select(_new_nodes(uuids_before, with_sets=False), noExpand=True)
    cmds.sets(name=_SQUASH_SET)
    cmds.sets(_SQUASH_SET, add="FaceAllSet")
    cmds.select("squashTop_M")


def create_head_squash():
    """Crea lo squash della testa (parita' asAdvancedSquash, MEL
    44397-44681): controlli squashTop/Middle/Bottom/Base_M sotto
    SquashControls, lattice squashFfd sulle geometrie AllHead e sui
    controlli on-face, catena squashIKX* con spline IK che skinna il
    lattice, e il set SquashSet con tutti i nodi creati.

    Ritorna bool. Nessuna eccezione: se qualcosa fallisce i nodi creati
    vengono rimossi."""
    head_joint = get_fit_option("HeadJoint") or ""
    all_face_geo = (get_fit_option("AllHead") or "").split()
    if cmds.objExists(_SQUASH_SETUP) or cmds.objExists(_SQUASH_SET):
        cmds.warning("create_head_squash: HeadSquash already exists, delete it first")
        return False
    missing = _missing_prerequisite(head_joint, all_face_geo)
    if missing:
        cmds.warning("create_head_squash: {} not found, build the face first".format(missing))
        return False

    try:
        cmds.setToolTo("selectSuperContext")
    except RuntimeError:
        pass  # nessun tool context in batch
    uuids_before = set(cmds.ls(uuid=True))
    try:
        _build_head_squash(head_joint, all_face_geo, uuids_before)
    except RuntimeError as exc:
        leftovers = [n for n in _new_nodes(uuids_before, with_sets=True) if cmds.objExists(n)]
        for node in leftovers:
            if cmds.objExists(node):
                try:
                    cmds.delete(node)
                except RuntimeError:
                    pass
        cmds.warning("create_head_squash: failed and rolled back: {}".format(exc))
        return False
    print("// HeadSquash created")
    return True


def delete_head_squash():
    """Elimina lo squash della testa (parita' asDeleteHeadSquash, MEL
    44683-44691): cancella i membri di SquashSet. Ritorna bool."""
    if not cmds.objExists(_SQUASH_SET):
        cmds.warning("delete_head_squash: {} not found".format(_SQUASH_SET))
        return False
    if cmds.objExists("squashIKCurveInfo"):
        # per primo, per evitare "No valid NURBS curve"
        cmds.delete("squashIKCurveInfo")
    cmds.select(_SQUASH_SET)
    cmds.delete()
    print("// HeadSquash deleted")
    return True


def _head_joints(head_joint, skin_cluster):
    """I joint che contano come "testa" per asOptimizeSquash (MEL
    44709-44719). Come nel MEL, basta un joint di FaceDeformationSystem
    collegato allo skinCluster per includerli tutti (il MEL concatena
    l'intera lista a ogni riscontro)."""
    joints = set(cmds.listRelatives(head_joint, allDescendents=True, type="joint") or [])
    face_joints = (
        cmds.listRelatives("FaceDeformationSystem", allDescendents=True, type="joint") or []
        if cmds.objExists("FaceDeformationSystem")
        else []
    )
    for joint in face_joints:
        if (cmds.listConnections(joint + ".worldMatrix") or [""])[0] == skin_cluster:
            joints.update(face_joints)
            break
    for region in ("EyeRegion_R", "EyeRegion_L"):
        if cmds.objExists(region):
            joints.add(region)
    joints.add(head_joint)
    return joints


def optimize_head_squash():
    """Toglie dal lattice i vertici della Face che non sono pesati su alcun
    joint della testa (parita' asOptimizeSquash, MEL 44693-44750), cosi' lo
    squash non tocca il resto del corpo. Lascia selezionati i vertici che
    restano nello squash. Ritorna bool."""
    head_joint = get_fit_option("HeadJoint") or ""
    geometry = get_fit_option("Face") or ""
    skin_cluster = get_fit_option("SkinCluster") or ""
    if not cmds.objExists(_SQUASH_SETUP) or not cmds.objExists(_FFD_SET):
        cmds.warning("optimize_head_squash: SquashSetup not found, Create HeadSquash first.")
        return False
    for label, node in (
        ("Face geometry", geometry),
        ("skinCluster", skin_cluster),
        ("head joint", head_joint),
    ):
        if not node or not cmds.objExists(node):
            cmds.warning('optimize_head_squash: {} "{}" not found'.format(label, node))
            return False
    if cmds.nodeType(skin_cluster) != "skinCluster":
        cmds.warning('optimize_head_squash: "{}" is not a skinCluster'.format(skin_cluster))
        return False

    if not cmds.attributeQuery("optimizedSquash", node=_SQUASH_SETUP, exists=True):
        cmds.addAttr(
            _SQUASH_SETUP,
            keyable=False,
            longName="optimizedSquash",
            attributeType="bool",
            defaultValue=True,
        )

    head_joints = _head_joints(head_joint, skin_cluster)
    outside = []
    try:
        for index in range(cmds.polyEvaluate(geometry, vertex=True)):
            vtx = "{}.vtx[{}]".format(geometry, index)
            influences = (
                cmds.skinPercent(skin_cluster, vtx, query=True, transform=None, ignoreBelow=0.001)
                or []
            )
            if not any(influence in head_joints for influence in influences):
                outside.append(vtx)
        cmds.select(clear=True)
        if outside:
            cmds.sets(outside, remove=_FFD_SET)
            # asInvertSelection, ramo vtx (MEL 67309-67313)
            cmds.select(geometry + ".vtx[0:999999]")
            cmds.select(outside, deselect=True)
    except (RuntimeError, TypeError) as exc:
        cmds.warning("optimize_head_squash: failed: {}".format(exc))
        return False
    print("// Optimize complete, now only these selected vtx`s are affected by Squash")
    return True


def add_to_head_squash(objects=None):
    """Include oggetti (es. i capelli) nella deformazione dello squash
    (parita' asAddToHeadSquash, MEL 44752-44756). `objects` None = la
    selezione corrente. Ritorna bool."""
    if not cmds.objExists(_FFD_SET):
        cmds.warning("add_to_head_squash: {} not found, Create HeadSquash first.".format(_FFD_SET))
        return False
    if objects is None:
        objects = cmds.ls(selection=True) or []
    elif isinstance(objects, str):
        objects = [objects]
    objects = list(objects)
    if not objects:
        cmds.warning("add_to_head_squash: nothing selected")
        return False
    missing = [obj for obj in objects if not cmds.objExists(obj)]
    if missing:
        cmds.warning("add_to_head_squash: {} not found".format(", ".join(missing)))
        return False
    try:
        cmds.sets(objects, add=_FFD_SET)
    except RuntimeError as exc:
        cmds.warning("add_to_head_squash: failed: {}".format(exc))
        return False
    print("// Added selected object to be included in HeadSquash deformation")
    return True

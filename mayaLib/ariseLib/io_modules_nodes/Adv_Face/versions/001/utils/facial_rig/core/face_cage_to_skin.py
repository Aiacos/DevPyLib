"""Build step CageToSkin (parita' asFaceCageToSkin MEL:33387-33478 e
asFaceCheekCageSmoothUpdate MEL:33480-33646, piu' asFaceCageWeightsRemove
MEL:33648 e asFaceFaceCageFinish MEL:33656).

Trasferisce sul viso i pesi della mesh `asCage`: copia dei pesi della cage
su `CageLayer`, smooth per ogni joint cage, copia sul viso (escluse labbra
e palpebre), poi ripristino dell'area di falloff delle labbra dai pesi
salvati su `LipFalloffLayer`. I pesi di partenza restano su
`PreCageWeights` per `face_cage_weights_remove`.

Divergenze (docs/gap-analysis.md §5k):
- lo smooth del MEL e' il flood "smooth" del Paint Skin Weights Tool
  (artisan), che in mayapy non esiste. `_smooth_influence` ne applica la
  regola, ricavata eseguendo il vero tool in Maya su mesh di prova;
- il MEL sfuma i joint della cage nell'ordine di `sets -q asCageJoints`,
  che cambia da una sessione di Maya all'altra: poiche' il risultato
  dipende dall'ordine, il MEL stesso da' pesi diversi a ogni build (sulla
  demo chubby 300-480 vertici oltre 0.01 fra due giri). Il port usa
  l'ordine alfabetico, per avere build riproducibili; `CAGE_JOINT_ORDER`
  permette di imporre l'ordine di una sessione MEL per il confronto di
  parita' (con lo stesso ordine restano 12 vertici diversi su ~8000);
- quei vertici residui sono quelli pesati per intero sul joint che si sta
  sfumando: artisan cede il peso perso ai joint piu' vicini, e il criterio
  esatto con cui li sceglie non e' del tutto ricostruito (il port usa i
  `maxInfluences` joint piu' vicini, in proporzione a 1/distanza);
- le iterazioni di smooth (intField `faceCageIntField` della UI) sono un
  parametro, con default la stima di `guess_cage_smooth()`;
- multiSkinClusters non portato.
"""

import maya.api.OpenMaya as om
import maya.api.OpenMayaAnim as oma
import maya.cmds as cmds

from .face_cage import guess_cage_smooth
from .face_prep import include_above_eyes, include_below_eyes
from .fit_options import FIT_SKELETON, get_fit_option
from .fitting import get_face_fit_selection

_KEEP = 1e-6

# Ordine dei joint della cage per lo smooth. None = alfabetico. Il confronto
# di parita' lo imposta con l'ordine `sets -q asCageJoints` della sessione MEL
# di riferimento (tools/parity), da cui il risultato del MEL dipende.
CAGE_JOINT_ORDER = None


def _cast(components, dest_obj):
    """asobjSetCast: gli stessi componenti su un altro oggetto."""
    if not components:
        return []
    source = components[0].split(".")[0]
    return [c.replace(source, dest_obj, 1) for c in components]


def _skin_layer(name, joints):
    cmds.duplicate("templateLayer", name=name)
    sc = cmds.skinCluster(
        joints,
        name,
        toSelectedBones=True,
        maximumInfluences=3,
        dropoffRate=4,
        removeUnusedInfluence=False,
    )[0]
    return cmds.rename(sc, name + "SC")


def _copy_weights(*selection):
    cmds.select(*selection)
    cmds.copySkinWeights(
        noMirror=True, surfaceAssociation="closestPoint", influenceAssociation="closestJoint"
    )


def _unique(nodes):
    seen = []
    for node in nodes or []:
        if node not in seen:
            seen.append(node)
    return seen


class _SkinWeights:
    """Pesi di uno skinCluster in forma sparsa, con lettura/scrittura in
    blocco via API (un vertice alla volta con skinPercent sarebbe lento)."""

    def __init__(self, skin, mesh):
        sel = om.MSelectionList()
        sel.add(skin)
        sel.add(mesh)
        self.fn = oma.MFnSkinCluster(sel.getDependNode(0))
        self.dag = sel.getDagPath(1)
        self.dag.extendToShape()
        self.names = [p.partialPathName() for p in self.fn.influenceObjects()]
        self.count = om.MFnMesh(self.dag).numVertices
        component = om.MFnSingleIndexedComponent()
        self.component = component.create(om.MFn.kMeshVertComponent)
        component.addElements(list(range(self.count)))
        flat, self.width = self.fn.getWeights(self.dag, self.component)
        self.rows = []
        for vtx in range(self.count):
            base = vtx * self.width
            self.rows.append(
                {k: flat[base + k] for k in range(self.width) if flat[base + k] > _KEEP}
            )
        self.around = []
        it = om.MItMeshVertex(self.dag)
        while not it.isDone():
            self.around.append(list(it.getConnectedVertices()) + [it.index()])
            it.next()
        self.points = om.MFnMesh(self.dag).getPoints(om.MSpace.kWorld)
        self.max_influences = max(1, cmds.getAttr(skin + ".maxInfluences"))
        self.joint_points = [
            om.MPoint(cmds.xform(name, query=True, worldSpace=True, translation=True))
            for name in self.names
        ]
        self.locked = [
            cmds.attributeQuery("lockInfluenceWeights", node=name, exists=True)
            and bool(cmds.getAttr(name + ".lockInfluenceWeights"))
            for name in self.names
        ]

    def inverse_distances(self, vtx, skip):
        """{influenza: 1/distanza dal vertice} per le influenze sbloccate
        piu' vicine (al massimo `maxInfluences`), esclusa `skip`."""
        point = self.points[vtx]
        nearest = []
        for key, joint_point in enumerate(self.joint_points):
            if key == skip or self.locked[key]:
                continue
            distance = point.distanceTo(joint_point)
            if distance > _KEEP:
                nearest.append((distance, key))
        nearest.sort()
        return {key: 1.0 / distance for distance, key in nearest[: self.max_influences]}

    def write(self):
        flat = om.MDoubleArray(self.count * self.width, 0.0)
        for vtx, row in enumerate(self.rows):
            base = vtx * self.width
            for k, value in row.items():
                flat[base + k] = value
        indices = om.MIntArray(list(range(self.width)))
        self.fn.setWeights(self.dag, self.component, indices, flat, False)


def _smooth_influence(weights, joint):
    """Una passata del flood "smooth" di artisan sul peso di `joint`, su
    tutta la mesh. La regola e' stata ricavata eseguendo il vero tool in
    Maya su una mesh di prova (docs/gap-analysis.md §5k):

    - il peso del joint diventa la media fra il vertice e i suoi adiacenti
      (valori letti prima della passata);
    - le altre influenze sbloccate sono riscalate in proporzione;
    - se il vertice non ha altro peso da riscalare, quello perso va alle
      altre influenze sbloccate in proporzione inversa alla distanza fra il
      vertice e ciascun joint.
    """
    if joint not in weights.names:
        return
    k = weights.names.index(joint)
    rows = weights.rows
    column = [row.get(k, 0.0) for row in rows]
    for vtx, near in enumerate(weights.around):
        if not near:
            continue
        old = column[vtx]
        new = sum(column[n] for n in near) / len(near)
        if abs(new - old) < _KEEP:
            continue
        row = rows[vtx]
        locked = sum(value for key, value in row.items() if key != k and weights.locked[key])
        new = min(new, 1.0 - locked)
        rest_old = sum(value for key, value in row.items() if key != k and not weights.locked[key])
        rest_new = 1.0 - locked - new
        if rest_old > _KEEP:
            scale = rest_new / rest_old
            for key in list(row):
                if key != k and not weights.locked[key]:
                    row[key] *= scale
        elif rest_new > _KEEP:
            shares = weights.inverse_distances(vtx, skip=k)
            total = sum(shares.values())
            if not total:
                continue
            for key, share in shares.items():
                row[key] = row.get(key, 0.0) + rest_new * share / total
        if new > _KEEP:
            row[k] = new
        else:
            row.pop(k, None)


def _mask_vertices_without_perimeter():
    """Vertici della maschera del viso, esclusi il bordo e (se saltate) le
    zone sopra/sotto gli occhi (MEL:33506-33537)."""
    cmds.select(cmds.getAttr(FIT_SKELETON + ".Mask").split())
    eyelash = get_fit_option("Eyelash") or ""
    if eyelash:
        cmds.select(eyelash.split(), deselect=True)
    cmds.select(cmds.polyListComponentConversion(toVertex=True))
    inside = cmds.ls(selection=True)
    cmds.ConvertSelectionToVertexPerimeter()
    perimeter = cmds.ls(selection=True)
    cmds.select(inside)
    if perimeter:
        cmds.select(perimeter, deselect=True)
    vtxs = cmds.ls(selection=True)

    if not include_below_eyes():
        cmds.select(get_face_fit_selection("ForeHeadAreaMesh").split())
        cmds.select(get_face_fit_selection("ForeHeadAreaMeshLeft").split(), add=True)
        vtxs = cmds.ls(selection=True)
    if not include_above_eyes():  # salta tutto sopra l'angolo dell'occhio
        eye_y = cmds.xform(
            "upperEyeLidMainCurve.cv[0]", query=True, worldSpace=True, translation=True
        )[1]
        cmds.select(vtxs)
        above = [
            v
            for v in cmds.ls(selection=True, flatten=True)
            if cmds.xform(v, query=True, worldSpace=True, translation=True)[1] > eye_y
        ]
        if above:
            cmds.select(above, deselect=True)
        vtxs = cmds.ls(selection=True)
    return vtxs


def _restore_lip_falloff(skin_cluster):
    """Nell'area di falloff delle labbra i pesi tornano quelli salvati su
    LipFalloffLayer (senza il joint "spento") (MEL:33608-33631)."""
    if not cmds.objExists("lipFalloffArea"):
        return
    vtxs = cmds.ls(cmds.sets("lipFalloffArea", query=True) or [], flatten=True)
    for vtx, layer_vtx in zip(vtxs, _cast(vtxs, "LipFalloffLayer")):
        infs = cmds.skinPercent(
            "LipFalloffLayerSC", layer_vtx, query=True, ignoreBelow=0.01, transform=None
        )
        values = cmds.skinPercent(
            "LipFalloffLayerSC", layer_vtx, query=True, ignoreBelow=0.01, value=True
        )
        pairs = [("cageOffJoint", 0)]
        pairs += [
            (inf, value) for inf, value in zip(infs or [], values or []) if inf != "lipOffJoint"
        ]
        cmds.skinPercent(skin_cluster, vtx, transformValue=pairs)


def face_cheek_cage_smooth_update(smooth=None) -> bool:
    """Trasferisce (o aggiorna) i pesi della cage sul viso
    (asFaceCheekCageSmoothUpdate).

    Args:
        smooth: passate di smooth per joint cage; None = stima automatica.
    """
    geometry = get_fit_option("Face") or ""
    skin_cluster = get_fit_option("SkinCluster") or ""
    for node in (geometry, skin_cluster, "asCage", "CageLayer", "asCageJoints", "cageOffJoint"):
        if not node or not cmds.objExists(node):
            cmds.warning("face_cheek_cage_smooth_update: {} not found".format(node or "option"))
            return False
    if smooth is None:
        smooth = guess_cage_smooth()
    cage_joints = cmds.sets("asCageJoints", query=True) or []
    if CAGE_JOINT_ORDER:
        cage_joints = [j for j in CAGE_JOINT_ORDER if j in cage_joints]
    else:
        cage_joints = sorted(cage_joints)
    selection = cmds.ls(selection=True)

    mask_vtxs = _mask_vertices_without_perimeter()
    layer_vtxs = cmds.ls(_cast(mask_vtxs, "CageLayer"), flatten=True)
    if not layer_vtxs:
        cmds.warning("face_cheek_cage_smooth_update: no face vertices to transfer the cage to")
        return False

    # cage -> CageLayer, poi smooth sul layer
    _copy_weights("asCage", layer_vtxs)
    smooth_joints = [j for j in cage_joints if not j.startswith("EyeBrow")]
    if smooth:
        weights = _SkinWeights("CageLayerSC", "CageLayer")
        for _ in range(smooth):
            for joint in smooth_joints:
                _smooth_influence(weights, joint)
        weights.write()
    cmds.setAttr("CageLayer.v", 0)

    # CageLayer -> viso, escluse labbra e palpebre
    cmds.select(_cast(mask_vtxs, "CageLayer"))
    cmds.select(mask_vtxs, add=True)
    for area in ("lipArea", "eyeLidArea", "eyeLidAreaLeft", "eyeSocketArea", "eyeSocketAreaLeft"):
        if cmds.objExists(area):
            cmds.select(area, deselect=True)
    cmds.copySkinWeights(
        noMirror=True, surfaceAssociation="closestPoint", influenceAssociation="closestJoint"
    )
    _restore_lip_falloff(skin_cluster)
    # fuori dalle aree puo' restare del peso sul joint "spento": azzeralo
    cmds.skinPercent(skin_cluster, geometry, transformValue=("cageOffJoint", 0))

    if selection:
        cmds.select(selection)
    else:
        cmds.select(clear=True)
    return True


def _build_brow_sets(skin_cluster):
    cmds.select(clear=True)
    cmds.sets(name="eyeBrowArea", empty=True)
    cmds.sets(name="eyeBrowLineArea", empty=True)
    cmds.sets("eyeBrowLineArea", "eyeBrowArea", add="FaceAreas")
    for side, left in (("_R", ""), ("_L", "Left")):
        names = ["EyeBrowInner", "EyeBrowOuter"]
        names += ["EyeBrowMid{}".format(i) for i in range(1, 4)]
        for name in names:
            joint = name + "Joint" + side
            if name.startswith("EyeBrowMid") and not cmds.objExists(joint):
                continue
            cmds.skinCluster(skin_cluster, edit=True, selectInfluenceVerts=joint)
            influenced = cmds.ls(selection=True)
            if influenced:
                cmds.sets(influenced, add="eyeBrowArea")
            line = get_face_fit_selection(name + left).split()
            if line:
                cmds.sets(line, add="eyeBrowLineArea")


def face_cage_to_skin(smooth=None) -> bool:
    """Trasferisce i pesi della cage sul viso (asFaceCageToSkin).

    Returns:
        True anche quando lo step e' saltato per assenza dei fit di labbra
        e sopracciglia (gate MEL); False con warning se manca un
        prerequisito.
    """
    has_above_eye = cmds.objExists("EyeBrowInner")
    has_below_eye = cmds.objExists("upperLipMainCurve")
    if not has_above_eye and not has_below_eye:
        return True
    geometry = get_fit_option("Face") or ""
    skin_cluster = get_fit_option("SkinCluster") or ""
    required = [geometry, skin_cluster, "asCage", "templateLayer", "cageOffJoint", "asCageJoints"]
    missing = [node for node in required if not node or not cmds.objExists(node)]
    if missing:
        cmds.warning("face_cage_to_skin: missing {}".format(", ".join(missing) or "options"))
        return False
    if get_fit_option("MultiSkinClusters"):
        cmds.warning("face_cage_to_skin: multiSkinClusters is not ported yet")

    cmds.setAttr(geometry + ".v", 1)
    cmds.setAttr("asCage.v", 0)

    # copia di sicurezza dei pesi, per face_cage_weights_remove
    joints = _unique(
        cmds.listConnections(skin_cluster + ".matrix", source=True, destination=False, type="joint")
    )
    _skin_layer("PreCageWeights", joints)
    _copy_weights(geometry, "PreCageWeights")

    joints = _unique(
        cmds.listConnections(skin_cluster, source=True, destination=False, type="joint")
    )
    if has_below_eye:
        lip_joints = cmds.listRelatives("LipJoints_M", allDescendents=True, type="joint") or []
        joints = [j for j in joints if j not in lip_joints]
    joints = [j for j in joints if j != "cageOffJoint"] + ["cageOffJoint"]
    _skin_layer("CageLayer", joints)
    cmds.parent("CageLayer", world=True)
    _copy_weights(geometry, "CageLayer")

    if not face_cheek_cage_smooth_update(smooth):
        return False

    if has_above_eye:
        _build_brow_sets(skin_cluster)
    if has_below_eye:
        for node in ("LipRegionOffset_M", "LipOffset_R", "LipOffset_L", "upperLipOffset_M",
                     "lowerLipOffset_M"):  # fmt: skip
            cmds.setAttr(node + ".v", 1)
    cmds.select(clear=True)
    return True


def face_cage_weights_remove() -> bool:
    """Ripristina i pesi precedenti alla cage (asFaceCageWeightsRemove)."""
    geometry = get_fit_option("Face") or ""
    if not cmds.objExists("PreCageWeights") or not cmds.objExists(geometry):
        cmds.warning("face_cage_weights_remove: PreCageWeights or face geometry not found")
        return False
    _copy_weights("PreCageWeights", geometry)
    return True


def face_face_cage_finish():
    """Chiude gli step della cage: la mesh va fra i nodi nascosti del build
    e i layer temporanei vengono cancellati (asFaceFaceCageFinish).
    Idempotente via FaceBuildInProgress.FaceCageFinish."""
    if not cmds.objExists("upperLipMainCurve") and not cmds.objExists("EyeBrowInner"):
        return
    if not cmds.objExists("FaceBuildInProgress"):
        cmds.warning("face_face_cage_finish: FaceBuildInProgress not found")
        return
    if cmds.attributeQuery("FaceCageFinish", node="FaceBuildInProgress", exists=True):
        return
    cmds.addAttr(
        "FaceBuildInProgress",
        longName="FaceCageFinish",
        attributeType="bool",
        defaultValue=True,
        keyable=False,
    )
    if cmds.objExists("asCage"):
        cmds.parent("asCage", "FaceBuildInProgressHidden")
    for node in ("CageLayer", "LipFalloffLayer"):
        if cmds.objExists(node):
            cmds.delete(node)

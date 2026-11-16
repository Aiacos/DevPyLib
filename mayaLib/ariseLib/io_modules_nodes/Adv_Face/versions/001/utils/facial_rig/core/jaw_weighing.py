"""Build step JawWeighing (parita' asFaceJawWeighing MEL:34706-34987 e
asFaceJawWeighingFinish MEL:34989-35214), con le procedure di supporto
asShowLayer (MEL:39528, in build_utils), asSkinTeeth (MEL:39267),
asFaceDesignMouthOpen (MEL:26186), asFaceWeightLips (MEL:38332),
asFaceUpdateJawCurvesWeights (MEL:38463), asSelectCurveVtx (MEL:39404) e
asWsPickWalk (MEL:38728).

In AdvancedSkeleton `Jaw_M` e' il CONTROLLER e `JawJoint_M` il joint. Lo
step crea controller e joint della mascella e dei denti, poi calcola i pesi
della mascella su una mesh di servizio (`JawOpenLayer`, skinnata solo a
FaceJoint_M e JawJoint_M):

- labbra: lo spostamento prodotto da un softMod centrato sul labbro
  inferiore (`mouthOpenSoftMod`) diventa il peso di JawJoint_M;
- resto del viso: i vertici sotto `JawCurve` valgono 1, quelli sotto
  `JawCurveMid` 0.5, l'area fra `JawCurveTop` e `JawCurveBottom`
  (`jawArea`) viene interpolata e sfumata.

Lascia la posa "bocca aperta" al frame 30 per il controllo a vista. Il
finish (chiamato da JawOpen, MEL:35232) copia i pesi sul viso, fa seguire
la mascella a labbra e guance e converte la posa in SDK su ctrlMouth_M.ty.

Divergenze (docs/gap-analysis.md §5n):
- asSmoothFlood (flood "smooth" del Paint Skin Weights Tool) non esiste in
  mayapy: `_smooth_flood` ne e' l'equivalente numerico, come in CageToSkin;
- le iterazioni di smooth (intField `asFaceNumJawSmooths`, default 50) sono
  un parametro della funzione;
- `copySkinWeights -ss -ds ...` (MEL:38621 e 38719) passa "-ds" come nome
  dello skin sorgente: Maya lo ignora e specchia i vertici selezionati.
  Il port chiama il mirror sulla selezione, senza skin espliciti;
- "transfer to JawLayer - from:LipDeform" (MEL:38681-38684): `asobjSetCast`
  seleziona il set come effetto collaterale, quindi la sorgente reale e'
  `lipArea` sulla Face (non LipDeform). Il port copia da li';
- ramo multiSkinClusters non portato;
- oggetti assenti = warning + False, mai eccezioni.
"""

import maya.api.OpenMaya as om
import maya.api.OpenMayaAnim as oma
import maya.cmds as cmds

from .build_utils import (
    as_align,
    as_face_hide_controllers,
    as_get_opm,
    as_opm_scale_reset,
    as_parent_constraint,
    as_show_layer,
)
from .ctrl_box import create_face_controller
from .driving_system import ds_sdk
from .face_cheek_raiser import face_cheek_raiser_finish
from .face_ctrl_pp import face_add_constrained, face_half_moon_curve
from .fit_options import FIT_SKELETON, get_fit_option
from .fitting import FacialFitting, _as_deformer, get_face_fit_selection

NUM_JAW_SMOOTHS_DEFAULT = 50  # intField asFaceNumJawSmooths (MEL:1879)

_LAYER = "JawOpenLayer"
_LAYER_SC = "JawOpenLayerSC"
_MIRROR = {
    "mirrorMode": "YZ",
    "mirrorInverse": True,
    "surfaceAssociation": "closestPoint",
    "influenceAssociation": "closestJoint",
}


# -- helper ---------------------------------------------------------------


def _ws(node):
    return cmds.xform(node, query=True, worldSpace=True, translation=True)


def _flat(items):
    return cmds.ls(items, flatten=True) if items else []


def _index(vtx):
    return int(vtx.rsplit("[", 1)[1][:-1])


def _cast(components, dest_obj):
    """asobjSetCast: gli stessi componenti su un altro oggetto."""
    if not components:
        return []
    source = components[0].split(".")[0]
    return [c.replace(source, dest_obj, 1) for c in components]


def _set_vtxs(set_name, dest_obj):
    """Membri (flatten) di un set di vertici, riportati su `dest_obj`."""
    if not cmds.objExists(set_name):
        return []
    return _flat(_cast(_flat(cmds.sets(set_name, query=True) or []), dest_obj))


def _fit_vtxs(fit_object, dest_obj):
    """Vertici campionati da un oggetto fit, riportati su `dest_obj`."""
    text = get_face_fit_selection(fit_object) or ""
    return _flat(_cast(text.split(), dest_obj))


def _new_skin_cluster(influences, geometry, name, max_influences=3):
    """newSkinCluster "-toSelectedBones -mi N -dr 4 -rui false"."""
    sc = cmds.skinCluster(
        influences,
        geometry,
        toSelectedBones=True,
        maximumInfluences=max_influences,
        dropoffRate=4,
        removeUnusedInfluence=False,
    )[0]
    return cmds.rename(sc, name)


def _skin_cluster_in_history(obj):
    """Ultimo skinCluster trovato da `listHistory -pdo 1 -il 2` (MEL:39325)."""
    found = ""
    for node in cmds.listHistory(obj, pruneDagObjects=True, interestLevel=2) or []:
        if cmds.nodeType(node) == "skinCluster":
            found = node
    return found


def _add_influence(skin, joint):
    """skinCluster -e -lw false -wt 0 -ai (senza errore se gia' presente)."""
    if joint in (cmds.skinCluster(skin, query=True, influence=True) or []):
        return
    cmds.skinCluster(skin, edit=True, lockWeights=False, weight=0, addInfluence=joint)


def _skin_percent(skin, components, joint, value):
    """skinPercent -tv dentro catchQuiet: i pesi fuori da [0, 1] o i
    componenti non skinnati sono ignorati come nel MEL."""
    try:
        cmds.skinPercent(skin, components, transformValue=(joint, value))
    except RuntimeError:
        pass


def _jaw_weight(vtx):
    return cmds.skinPercent(_LAYER_SC, vtx, query=True, transform="JawJoint_M")


def _restore_selection(selection):
    if selection:
        cmds.select(selection)
    else:
        cmds.select(clear=True)


def _lock_weights(lock):
    """asFaceLockWeights (MEL:37882): tutti i joint della scena."""
    for joint in cmds.ls(type="joint"):
        if cmds.attributeQuery("lockInfluenceWeights", node=joint, exists=True):
            cmds.setAttr(joint + ".lockInfluenceWeights", lock)


def _weight_hammer():
    """weightHammerVerts sui vertici selezionati: lo script di Maya
    (doHammerWeightsArgList -> doSmoothSkinWeightsArgList 5 {0,5,0,2,1,0})
    si riduce a uno smoothWeights a 5 iterazioni piu' normalizzazione."""
    vtxs = [item for item in cmds.ls(selection=True) or [] if ".vtx[" in item]
    if not vtxs:
        return
    cmds.select(vtxs)
    for obj in cmds.ls(selection=True, objectsOnly=True):
        for skin in cmds.ls(cmds.listHistory(obj, pruneDagObjects=True), type="skinCluster"):
            cmds.skinCluster(
                skin,
                edit=True,
                smoothWeights=0.0,
                smoothWeightsMaxIterations=5,
                obeyMaxInfluences=bool(cmds.getAttr(skin + ".maintainMaxInfluences")),
            )
            cmds.skinCluster(skin, edit=True, forceNormalizeWeights=True)


def _mirror_layer_weights():
    cmds.copySkinWeights(sourceSkin=_LAYER_SC, destinationSkin=_LAYER_SC, **_MIRROR)


def _mirror_selected_vertices():
    """`copySkinWeights -ss -ds -mirrorMode YZ ...` del MEL: il nome "-ds"
    non e' uno skin valido e Maya specchia i vertici selezionati."""
    if cmds.ls(selection=True):
        cmds.copySkinWeights(**_MIRROR)


class _Mesh:
    """Posizioni world e adiacenze di una mesh, lette in blocco."""

    def __init__(self, mesh):
        sel = om.MSelectionList()
        sel.add(mesh)
        self.name = mesh
        self.dag = sel.getDagPath(0)
        self.dag.extendToShape()
        self.points = om.MFnMesh(self.dag).getPoints(om.MSpace.kWorld)
        self.around = []
        it = om.MItMeshVertex(self.dag)
        while not it.isDone():
            self.around.append(list(it.getConnectedVertices()))
            it.next()

    def vtx(self, index):
        return "{}.vtx[{}]".format(self.name, index)

    def vtxs(self, indices):
        return [self.vtx(i) for i in sorted(indices)]


def _smooth_flood(skin, mesh, vtx_ids, inf_a, inf_b, iterations):
    """Equivalente numerico di asSmoothFlood (MEL:39228) con solo `inf_a` e
    `inf_b` sbloccate: a ogni passata il peso di inf_a sui vertici dati
    diventa la media fra il vertice e i suoi adiacenti, inf_b riceve il
    resto."""
    if not vtx_ids or iterations < 1:
        return
    sel = om.MSelectionList()
    sel.add(skin)
    fn = oma.MFnSkinCluster(sel.getDependNode(0))
    names = [p.partialPathName() for p in fn.influenceObjects()]
    if inf_a not in names or inf_b not in names:
        return
    pair = om.MIntArray([names.index(inf_a), names.index(inf_b)])
    count = len(mesh.around)
    component = om.MFnSingleIndexedComponent()
    obj = component.create(om.MFn.kMeshVertComponent)
    component.addElements(list(range(count)))
    flat = fn.getWeights(mesh.dag, obj, pair)
    w_a = [flat[i * 2] for i in range(count)]
    w_b = [flat[i * 2 + 1] for i in range(count)]
    vtx_ids = sorted(vtx_ids)
    for _ in range(iterations):
        new = {}
        for vtx in vtx_ids:
            near = mesh.around[vtx]
            average = (w_a[vtx] + sum(w_a[n] for n in near)) / (len(near) + 1)
            new[vtx] = min(average, w_a[vtx] + w_b[vtx])
        for vtx, value in new.items():
            w_b[vtx] = w_a[vtx] + w_b[vtx] - value
            w_a[vtx] = value
    out = om.MDoubleArray()
    for vtx in range(count):
        out.append(w_a[vtx])
        out.append(w_b[vtx])
    fn.setWeights(mesh.dag, obj, pair, out, False)


# -- asSkinTeeth ----------------------------------------------------------


def _to_vertices(text):
    """La geometria (oggetti o componenti) come lista di vertici."""
    items = [item for item in text.split() if cmds.objExists(item)]
    if not items:
        return []
    return cmds.polyListComponentConversion(items, toVertex=True) or []


def skin_teeth() -> bool:
    """Skinna denti e lingua ai loro joint (asSkinTeeth). La lingua e'
    legata a JawJoint_M solo provvisoriamente, per pesare la mascella."""
    geometry = get_fit_option("Face") or ""
    skin_cluster = get_fit_option("SkinCluster") or ""
    lower_teeth = get_fit_option("LowerTeeth") or ""
    tongue = get_fit_option("Tongue") or ""
    teeth_in_main_mesh = lower_teeth.startswith(geometry) and "." in lower_teeth

    teeth_sc = skin_cluster
    for upper_lower in ("upper", "lower"):
        vtxs = _to_vertices(get_fit_option(upper_lower.capitalize() + "Teeth") or "")
        joint = upper_lower + "TeethJoint_M"
        if not vtxs or not cmds.objExists(joint):
            continue
        for obj in cmds.ls(vtxs, objectsOnly=True):
            found = _skin_cluster_in_history(obj)
            if found:
                teeth_sc = found
            if not found:
                _new_skin_cluster([joint], obj, upper_lower + "TeethSC")
            elif teeth_in_main_mesh:
                _add_influence(skin_cluster, joint)
                _skin_percent(skin_cluster, vtxs, joint, 1)
            else:
                _add_influence(teeth_sc, joint)
                _skin_percent(teeth_sc, vtxs, joint, 1)

    # lingua: se e' una selezione di componenti i pesi stanno su JawLayer
    vtxs = _to_vertices(tongue)
    if vtxs and "." not in tongue:
        obj = cmds.ls(vtxs, objectsOnly=True)[0]
        found = _skin_cluster_in_history(obj)
        if not found:
            _new_skin_cluster(["JawJoint_M"], obj, "TongueSC")
        else:
            _add_influence(found, "JawJoint_M")
            _skin_percent(found, vtxs, "JawJoint_M", 1)
    cmds.select(clear=True)
    return True


# -- asFaceDesignMouthOpen ------------------------------------------------


def _closest_vertex(sampler, mesh, pos):
    cmds.setAttr(sampler + ".inPosition", pos[0], pos[1], pos[2], type="float3")
    return "{}.vtx[{}]".format(mesh, cmds.getAttr(sampler + ".result.closestVertexIndex"))


def face_design_mouth_open() -> bool:
    """Crea `LipDeform` col softMod `mouthOpenSoftMod` (la forma con cui le
    labbra seguono la mascella) e la posa "bocca aperta" al frame 30
    (asFaceDesignMouthOpen)."""
    scale = cmds.getAttr(FIT_SKELETON + ".faceScale")
    last_cv = cmds.getAttr("lowerLipMainCurve.spans") + 1
    pos_a = _ws("lowerLipMainCurve.cv[0]")
    pos_b = _ws("lowerLipMainCurve.cv[{}]".format(last_cv))
    soft, handle = "mouthOpenSoftMod", "mouthOpenSoftModHandle"

    cmds.createNode("transform", name="LipDeformations", parent="FaceBuildInProgressHidden")
    cmds.duplicate("templateLayer", name="LipDeform")
    cmds.sets("LipDeform", edit=True, forceElement="initialShadingGroup")

    cmds.select("LipDeform", replace=True)
    created = _as_deformer("softMod")
    cmds.rename(created[0], soft)
    cmds.rename(created[1], handle)
    deformer_set = cmds.listConnections(soft + ".message") or []
    if deformer_set:
        cmds.rename(deformer_set[0], "mouthOpenSoftModSet")
    cmds.setAttr(handle + "Shape.origin", pos_a[0], pos_a[1], pos_a[2], type="float3")
    cmds.setAttr(soft + ".falloffCenter", pos_a[0], pos_a[1], pos_a[2])
    cmds.xform(handle, pivots=pos_a)
    cmds.setAttr(soft + ".falloffMode", 1)
    cmds.setAttr(soft + ".falloffRadius", (0 - pos_b[0]) * 2)

    # vertice in cima al labbro e all'angolo, prima di muovere il softMod
    sampler = cmds.createNode("closestPointOnMesh", name="closestSampler2")
    cmds.connectAttr("LipDeform.outMesh", sampler + ".inMesh", force=True)
    top_vtx = _closest_vertex(sampler, "LipDeform", _ws("upperLipOuterCurve.cv[0]"))
    corner_vtx = _closest_vertex(sampler, "LipDeform", pos_b)
    pos_c = _ws(corner_vtx)
    cmds.delete(sampler)

    def ramp(index, attr, value):
        cmds.setAttr("{}.falloffCurve[{}].falloffCurve_{}".format(soft, index, attr), value)

    cmds.setAttr(handle + ".ty", scale / -10.0)
    ramp(1, "FloatValue", 1)

    # allarga il raggio finche' il vertice in cima al labbro non si muove
    cmds.setAttr(soft + ".falloffRadius", 0)
    pos_a = _ws(top_vtx)
    radius = (0 - pos_b[0]) * 2
    cmds.setAttr(soft + ".falloffRadius", radius)
    for i in range(99):
        if _ws(top_vtx)[1] - pos_a[1] != 0:
            break
        radius += (scale / 1000.0) * i
        cmds.setAttr(soft + ".falloffRadius", radius)
    ramp(1, "FloatValue", 0.05)
    ramp(0, "FloatValue", 0.95)

    # a che percentuale del falloff sta l'angolo della bocca (non sempre 50%)
    corner = 1.0 - ((pos_c[1] - _ws(corner_vtx)[1]) / (scale / 10.0))
    ramp(2, "Position", corner)
    ramp(2, "FloatValue", 0.5)
    ramp(3, "Position", corner - 0.15)
    ramp(3, "FloatValue", 0.8)
    ramp(4, "Position", corner + 0.15)
    ramp(4, "FloatValue", 0.2)
    for i in range(5):
        ramp(i, "Interp", 3)

    # LipDeform tiene solo le facce delle labbra
    lip_vtxs = _set_vtxs("lipArea", "LipDeform")
    if lip_vtxs:
        keep = cmds.polyListComponentConversion(
            lip_vtxs, fromVertex=True, toFace=True, internal=True
        )
        cmds.select("LipDeform.f[*]")
        if keep:
            cmds.select(keep, deselect=True)
        if cmds.ls(selection=True):
            cmds.delete()

    cmds.setAttr(handle + ".ty", 0)
    cmds.parentConstraint("Jaw_M", handle, maintainOffset=True)
    cmds.scaleConstraint("Jaw_M", handle, maintainOffset=True)

    cmds.playbackOptions(minTime=0, maxTime=30, animationStartTime=0, animationEndTime=30)
    for plug, value in (("ctrlMouth_M.ty", -1), ("Jaw_M.ty", -0.5), ("Jaw_M.tz", 0.5),
                        ("Jaw_M.rx", 15)):  # fmt: skip
        cmds.setKeyframe(plug, value=0, time=0)
        cmds.setKeyframe(plug, value=value, time=30)
    for axis in "xyz":
        cmds.setKeyframe("Jaw_M.s" + axis, value=1, time=0)
    for attr in ("tx", "ry", "rz"):
        cmds.setAttr("Jaw_M." + attr, lock=True)
    return True


# -- asFaceWeightLips -----------------------------------------------------


def _copy_from_lip_main(vtxs, main_ids, mesh):
    """Ogni vertice prende il peso del vertice del loop Main piu' vicino
    lungo la mesh (crescita della selezione, MEL:38398-38440)."""
    for vtx in vtxs:
        ring = {_index(vtx)}
        for _ in range(99):
            for index in list(ring):
                ring.update(mesh.around[index])
            hits = sorted(ring & main_ids)
            if hits:
                _skin_percent(_LAYER_SC, vtx, "JawJoint_M", _jaw_weight(mesh.vtx(hits[-1])))
                break


def face_weight_lips() -> bool:
    """Peso di JawJoint_M sulle labbra di `JawOpenLayer`: lo spostamento
    prodotto dal softMod quando la sua maniglia sale di 1 (asFaceWeightLips)."""
    geometry = get_fit_option("Face") or ""
    handle = "mouthOpenSoftModHandle"
    sel = cmds.ls(selection=True)
    has_delete = cmds.objExists("JawOpenLayerDeleteComponent")
    if has_delete:
        cmds.setAttr("JawOpenLayerDeleteComponent.nodeState", 1)
    current_time = cmds.currentTime(query=True)
    cmds.currentTime(0)

    cmds.skinPercent(_LAYER_SC, _LAYER + ".vtx[*]", transformValue=("FaceJoint_M", 1))

    cmds.duplicate(geometry, name="lipWeighter")
    for shape in cmds.listRelatives("lipWeighter", shapes=True, fullPath=True) or []:
        if cmds.getAttr(shape + ".intermediateObject"):
            cmds.delete(shape)
    cmds.sets("lipWeighter.vtx[*]", remove="lipArea")
    cmds.sets("lipWeighter", add="mouthOpenSoftModSet")
    cmds.sets("JawCurveMid.cv[1:4]", add="mouthOpenSoftModSet")
    if not cmds.objExists("lipAreaJawOpenLayer"):
        cmds.createNode("objectSet", name="lipAreaJawOpenLayer")
        cmds.sets("lipAreaJawOpenLayer", add="FaceBuildingSets")

    lip_area = _set_vtxs("lipArea", _LAYER)
    if lip_area:
        weighter = _cast(lip_area, "lipWeighter")
        cmds.setAttr(handle + ".ty", 0)
        rest = cmds.xform(weighter, query=True, worldSpace=True, translation=True)
        cmds.setAttr(handle + ".ty", 1)
        moved = cmds.xform(weighter, query=True, worldSpace=True, translation=True)
        cmds.setAttr(handle + ".ty", 0)
        cmds.sets(lip_area, add="lipAreaJawOpenLayer")
        for i, vtx in enumerate(lip_area):
            _skin_percent(_LAYER_SC, vtx, "JawJoint_M", moved[i * 3 + 1] - rest[i * 3 + 1])
    cmds.delete("lipWeighter")

    # il softMod (falloff di superficie) accartoccia un po' le labbra: i
    # loop Outer e Inner prendono il peso del loop Main, il resto e' smussato
    mesh = _Mesh(_LAYER)
    main = _fit_vtxs("FaceFitLipMainCurve", _LAYER)
    outer = _fit_vtxs("FaceFitLipOuterCurve", _LAYER)
    inner = _fit_vtxs("FaceFitLipInnerCurve", _LAYER)
    main_ids = {_index(v) for v in main}
    _copy_from_lip_main(outer, main_ids, mesh)
    _copy_from_lip_main(inner, main_ids, mesh)

    loops = main_ids | {_index(v) for v in outer} | {_index(v) for v in inner}
    hammer = [
        i for i in (_index(v) for v in lip_area)
        if i not in loops and mesh.points[i].x <= -0.001
    ]  # fmt: skip
    if hammer:
        cmds.select(mesh.vtxs(hammer))
        _weight_hammer()
    cmds.select(_LAYER)
    if not get_fit_option("NonSym"):
        _mirror_layer_weights()

    if has_delete:
        cmds.setAttr("JawOpenLayerDeleteComponent.nodeState", 0)
    cmds.currentTime(current_time)
    _restore_selection(sel)
    return True


# -- asFaceUpdateJawCurvesWeights -----------------------------------------


def _curve_vtxs(curve, geometry):
    """Indici dei vertici della Face lungo una curva: il vertice piu'
    vicino a 101 campioni della curva (asSelectCurveVtx). Come nel MEL il
    confronto col campione precedente parte da 0, quindi un primo campione
    sul vertice 0 e' saltato."""
    temps = ("tempLocator", "tempPointOnCurveInfo", "samplerMesh", "closestSampler")
    for node in temps:
        if cmds.objExists(node):
            cmds.delete(node)
    shape = cmds.listRelatives(curve, shapes=True)[0]
    cmds.spaceLocator(name="tempLocator")
    info = cmds.createNode("pointOnCurveInfo", name="tempPointOnCurveInfo")
    cmds.connectAttr(shape + ".worldSpace[0]", info + ".inputCurve", force=True)
    cmds.setAttr(info + ".turnOnPercentage", 1)
    cmds.connectAttr(info + ".position", "tempLocator.t")

    # copia della geometria con le trasformazioni congelate (asCreateSamplerMesh)
    cmds.duplicate(geometry, name="samplerMesh")
    for attr in ("t", "r", "s"):
        for axis in "xyz":
            cmds.setAttr("samplerMesh.{}{}".format(attr, axis), lock=False)
    if cmds.listRelatives("samplerMesh", parent=True):
        cmds.parent("samplerMesh", world=True)
    for shape in cmds.listRelatives("samplerMesh", shapes=True, fullPath=True) or []:
        if cmds.getAttr(shape + ".intermediateObject"):
            cmds.delete(shape)
    cmds.makeIdentity("samplerMesh", apply=True, translate=True, rotate=True, scale=True)
    sampler = cmds.createNode("closestPointOnMesh", name="closestSampler")
    cmds.connectAttr("samplerMesh.outMesh", sampler + ".inMesh")
    cmds.connectAttr("tempLocator.worldPosition", sampler + ".inPosition")

    found, previous = [], 0
    for i in range(101):
        cmds.setAttr(info + ".parameter", 0.01 * i)
        index = cmds.getAttr(sampler + ".result.closestVertexIndex")
        if index != previous and index not in found:
            found.append(index)
        previous = index
    for node in temps:
        if cmds.objExists(node):
            cmds.delete(node)
    return found


def _taper_towards_pivot(vtxs, far_point, factor):
    """Sfuma i pesi verso JawPivot in base alla distanza (MEL:38509-38531)."""
    pivot = om.MVector(_ws("JawPivot"))
    max_dist = (pivot - om.MVector(far_point)).length()
    if not max_dist:
        return
    for vtx in vtxs:
        dist = (pivot - om.MVector(_ws(vtx))).length()
        if dist < max_dist / 2.0:
            _skin_percent(_LAYER_SC, vtx, "JawJoint_M", (dist / max_dist) * factor)


def _jaw_area(mesh):
    """Indici dei vertici di `jawArea`: quelli compresi fra JawCurveTop e
    JawCurveBottom, portate sul piano di simmetria (MEL:38533-38612).

    Il MEL usa tre polySelectConstraint "distanza da un piano" (la distanza
    e' assoluta, quindi ogni vincolo e' una fascia) sui bounding box delle
    due curve, e per i vertici nella fascia alta controlla che stiano sotto
    JawCurveTop.
    """
    scale = cmds.getAttr(FIT_SKELETON + ".faceScale")
    top = cmds.duplicate("JawCurveTop", name="JawCurveTopSampler")[0]
    bottom = cmds.duplicate("JawCurveBottom", name="JawCurveBottomSampler")[0]
    cmds.move(0, top + ".cv[0:6]", bottom + ".cv[0:5]", x=True)
    cmds.move(0, -0.001, 0, bottom + ".cv[5]", relative=True)  # includi il vertice Jaw
    jaw, throat = _ws("Jaw"), _ws("Throat")
    if jaw[1] < throat[1]:  # mento piu' basso della gola
        cmds.xform(bottom + ".cv[5]", worldSpace=True, translation=(0, jaw[1], jaw[2]))
        cv4 = _ws(bottom + ".cv[4]")
        cmds.xform(
            bottom + ".cv[4]",
            worldSpace=True,
            translation=(0, jaw[1] - (scale / 10.0), (jaw[2] + cv4[2]) / 2.0),
        )
    bb_top = cmds.xform(top, query=True, worldSpace=True, boundingBox=True)
    bb_bot = cmds.xform(bottom, query=True, worldSpace=True, boundingBox=True)

    def band(axis, centre, half):
        return {
            i for i, p in enumerate(mesh.points) if abs((p.y if axis == "y" else p.z) - centre) <= half
        }  # fmt: skip

    def behind(z):  # MEL: -db 0 100 -dp 0 0 (z-100)
        return band("z", z - 100.0, 100.0)

    every = set(range(len(mesh.points)))
    y_top, y_top_min, y_bot = bb_top[4], bb_top[1], bb_bot[1]
    inside_outer = band("y", (y_top + y_bot) / 2.0, (y_top - y_bot) / 1.99) - behind(bb_bot[2])
    outside_outer = every - inside_outer
    inside_inner = band("y", (y_top_min + y_bot) / 2.0, (y_top_min - y_bot) / 2.0) - behind(
        bb_bot[5]
    )
    on_bounds = band("y", (y_top + y_top_min) / 2.0, (y_top - y_top_min) / 2.0) | band(
        "z", (bb_bot[5] + bb_bot[2]) / 2.0, ((bb_bot[5] - bb_bot[2]) / 2.0) * 1.001
    )
    on_bounds -= outside_outer

    # "sotto JawCurveTop": un locator vincolato alla curva (geometry + point
    # constraint) figlio di uno posato sul vertice. Si usano gli stessi nodi
    # del MEL, nello stesso ordine di visita e con la stessa valutazione: il
    # geometryConstraint parte dalla soluzione precedente, quindi sul bordo
    # un calcolo geometrico diretto darebbe un'area diversa.
    cmds.spaceLocator(name="samplerLocator")
    cmds.spaceLocator(name="samplerLocatorTop")
    cmds.spaceLocator(name="samplerLocatorBottom")
    cmds.parent("samplerLocatorTop", "samplerLocatorBottom", "samplerLocator")
    cmds.geometryConstraint(top, "samplerLocatorTop", weight=1)
    cmds.pointConstraint("samplerLocator", "samplerLocatorTop")
    cmds.geometryConstraint(bottom, "samplerLocatorBottom", weight=1)
    cmds.pointConstraint("samplerLocator", "samplerLocatorBottom")
    below_top = set()
    for index in sorted(on_bounds):
        point = mesh.points[index]
        cmds.xform("samplerLocator", worldSpace=True, translation=(point.x, point.y, point.z))
        # il `refresh` del MEL: valuta le matrici world dei due locator
        cmds.getAttr("samplerLocatorTop.worldMatrix")
        cmds.getAttr("samplerLocatorBottom.worldMatrix")
        if cmds.getAttr("samplerLocatorTop.ty") > 0:
            below_top.add(index)
    area = below_top | inside_inner
    cmds.delete("samplerLocator")
    cmds.delete(top, bottom)
    return area


def _ws_pick_walk_up(mesh, index):
    """asWsPickWalk 0 1 0: il vertice adiacente piu' "verticale" verso
    l'alto; se non ce n'e' nessuno, il primo della selezione allargata."""
    here = mesh.points[index]
    best, max_weight = None, 0.0
    for near in sorted(mesh.around[index]):
        there = mesh.points[near]
        if there.y < here.y:
            continue
        dx, dy, dz = abs(there.x - here.x), abs(there.y - here.y), abs(there.z - here.z)
        if not dx + dy + dz:
            continue
        if dy / (dx + dy + dz) > max_weight:
            max_weight, best = dy / (dx + dy + dz), near
    return min(mesh.around[index] + [index]) if best is None else best


def _fade_above_upper_lip(mesh, lip_ids):
    """Sfuma il peso sopra il labbro superiore, per `vtxsFromLipToNose`
    vertici verso il naso (MEL:38629-38659)."""
    steps = get_fit_option("vtxsFromLipToNose") or 3
    for vtx in _fit_vtxs("upperLipOuterCurve", _LAYER):
        values = cmds.skinPercent(_LAYER_SC, vtx, query=True, ignoreBelow=0.001, value=True) or []
        on_lip = values[1] if len(values) > 1 else 0.0
        index = _index(vtx)
        for step in range(steps):
            index = _ws_pick_walk_up(mesh, index)
            if index in lip_ids:
                continue
            _skin_percent(
                _LAYER_SC, mesh.vtx(index), "JawJoint_M", on_lip - ((on_lip / steps) * step)
            )


def _components_on_main_mesh(text, geometry):
    """Vertici di `JawOpenLayer` per denti/lingua che sono una selezione di
    componenti della Face (MEL:38693-38712)."""
    if not (text.startswith(geometry) and "." in text):
        return []
    return _flat(_cast(_to_vertices(text), _LAYER))


def face_update_jaw_curves_weights(num_jaw_smooths=NUM_JAW_SMOOTHS_DEFAULT) -> bool:
    """Pesa la mascella su `JawOpenLayer` a partire dalle quattro curve di
    `FaceFitJawCurves` (asFaceUpdateJawCurvesWeights). Si puo' richiamare
    dopo aver ritoccato le curve."""
    geometry = get_fit_option("Face") or ""
    non_symmetrical = bool(get_fit_option("NonSym"))
    sel = cmds.ls(selection=True)
    current_time = cmds.currentTime(query=True)
    cmds.currentTime(0)
    has_delete = cmds.objExists("JawOpenLayerDeleteComponent")
    if has_delete:
        cmds.setAttr("JawOpenLayerDeleteComponent.nodeState", 1)
    for old in ("jawArea", "jawCurveVtxs"):
        if cmds.objExists(old):
            cmds.delete(old)

    mesh = _Mesh(_LAYER)
    curve_ids = _curve_vtxs("JawCurve", geometry)
    mid_ids = _curve_vtxs("JawCurveMid", geometry)
    curve_vtxs, mid_vtxs = mesh.vtxs(curve_ids), mesh.vtxs(mid_ids)
    cmds.sets(curve_vtxs, name="jawCurveVtxs")
    cmds.sets("jawCurveVtxs", add="FaceBuildingSets")
    if curve_vtxs:
        cmds.skinPercent(_LAYER_SC, curve_vtxs, transformValue=("JawJoint_M", 1))
    if mid_vtxs:
        cmds.skinPercent(_LAYER_SC, mid_vtxs, transformValue=("JawJoint_M", 0.5))
    _taper_towards_pivot(curve_vtxs, _ws("Jaw"), 2.0)
    last_cv = cmds.getAttr("upperLipOuterCurve.spans") + 1
    _taper_towards_pivot(mid_vtxs, _ws("upperLipOuterCurve.cv[{}]".format(last_cv)), 1.0)

    lip_ids = {_index(v) for v in _flat(cmds.sets("lipAreaJawOpenLayer", query=True) or [])}
    area = _jaw_area(mesh) - lip_ids
    cmds.sets(mesh.vtxs(area), name="jawArea")
    cmds.sets("jawArea", add="FaceBuildingSets")
    hammer = area - set(curve_ids) - set(mid_ids)
    if hammer:
        cmds.select(mesh.vtxs(hammer))
        _weight_hammer()
        _mirror_selected_vertices()

    cmds.select(_LAYER, "JawCurve")
    cmds.copySkinWeights(
        noMirror=True, surfaceAssociation="closestPoint", influenceAssociation="closestJoint"
    )

    _fade_above_upper_lip(mesh, lip_ids)
    if not non_symmetrical:
        _mirror_layer_weights()

    cmds.currentTime(30)
    _smooth_flood(
        _LAYER_SC, mesh, area - set(curve_ids), "FaceJoint_M", "JawJoint_M", num_jaw_smooths
    )
    if not non_symmetrical:
        _mirror_layer_weights()
    if has_delete:
        cmds.setAttr("JawOpenLayerDeleteComponent.nodeState", 0)

    # JawLayer riparte da zero: l'area puo' essersi ridotta ritoccando le curve
    cmds.skinPercent("JawLayerSC", "JawLayer", transformValue=("JawJoint_M", 0))
    _copy_face_lips_to_jaw_layer()

    falloff = _set_vtxs("lipFalloffArea", _LAYER)
    if falloff:
        cmds.select(falloff)
        _weight_hammer()

    for option in ("LowerTeeth", "Tongue"):
        vtxs = _components_on_main_mesh(get_fit_option(option) or "", geometry)
        if vtxs:
            cmds.skinPercent(_LAYER_SC, vtxs, transformValue=("JawJoint_M", 1))

    cmds.currentTime(0)
    if cmds.objExists("FaceFitLipMainLeft"):  # labbra fittate per lato: restano com'e'
        cmds.select(mesh.vtxs(set(range(len(mesh.points))) - lip_ids))
        _mirror_selected_vertices()
    else:
        _mirror_layer_weights()

    cmds.currentTime(current_time)
    _restore_selection(sel)
    return True


def _copy_face_lips_to_jaw_layer():
    """Copia su JawLayer i pesi dell'area labbra (MEL:38681-38684).

    Il commento del MEL dice "from:LipDeform", ma `asobjSetCast lipArea`
    riseleziona il set a ogni chiamata: quando parte copySkinWeights la
    selezione e' `lipArea` sulla Face piu' gli stessi vertici su JawLayer,
    quindi la sorgente e' lo skinCluster del viso. Con closestJoint i joint
    delle labbra ricadono su JawJoint_M.
    """
    source = _flat(cmds.sets("lipArea", query=True) or [])
    dest = _cast(source, "JawLayer")
    if not source:
        return
    cmds.select(source)
    cmds.select(dest, add=True)
    try:
        cmds.copySkinWeights(
            noMirror=True, surfaceAssociation="closestPoint", influenceAssociation="closestJoint"
        )
    except RuntimeError as exc:
        cmds.warning("face_update_jaw_curves_weights: lips not copied to JawLayer ({})".format(exc))


# -- asFaceJawWeighing ----------------------------------------------------


def _teeth_bounding_box(teeth):
    """Bounding box world della geometria dei denti; con piu' oggetti il
    MEL li duplica sotto un gruppo temporaneo (MEL:34897-34911)."""
    cmds.select(teeth.split())
    cmds.showHidden(above=True)
    objs = cmds.ls(selection=True, objectsOnly=True)
    if len(objs) > 1:
        copies = cmds.duplicate(returnRootsOnly=True)
        copies = [
            cmds.parent(c, world=True)[0] if cmds.listRelatives(c, parent=True) else c
            for c in copies
        ]
        group = cmds.group(copies, name="BoundingBoxGroup")
        bb = cmds.xform(group, query=True, worldSpace=True, boundingBox=True)
        cmds.delete(group)
        return bb
    return cmds.xform(cmds.ls(selection=True), query=True, worldSpace=True, boundingBox=True)


def _build_teeth_controller(upper_lower, teeth, scale):
    """Controller e joint dei denti, dimensionati sul bounding box
    (MEL:34895-34938)."""
    name = upper_lower + "Teeth"
    ctrl, joint, offset = name + "_M", name + "Joint_M", name + "Offset_M"
    bb = _teeth_bounding_box(teeth)
    cmds.select(teeth.split())
    as_show_layer("Jaw")

    create_face_controller(name, "_M", 4)
    cmds.parent(joint, "FaceJoint_M")
    cmds.parent(offset, "SideReverse_M")
    cmds.setAttr(offset + ".s", 1, 1, 1, type="float3")
    cmds.rotate(-90, 0, 0, ctrl + ".cv[0:7]", relative=True, pivot=(0, 0, 0), objectSpace=True)
    unit = scale * 0.03
    cmds.scale((bb[3] - bb[0]) / unit, 1, (bb[5] - bb[2]) / unit, ctrl + ".cv[0:7]")
    cmds.xform(
        offset, worldSpace=True, translation=(0, (bb[1] + bb[4]) / 2.0, (bb[2] + bb[5]) / 2.0)
    )
    cmds.move(0, 0, scale / -10.0, ctrl + ".cv[0:99]", relative=True)
    cmds.connectAttr("ctrlBox.TeethCtrlVis", ctrl + "Shape.overrideVisibility", force=True)

    if upper_lower == "lower":
        face_add_constrained("lowerTeeth_M", "JawFollow_M", "JawStatic_M", 10)
    if as_get_opm():
        as_parent_constraint(ctrl, joint)
        as_opm_scale_reset(joint)
    else:
        cmds.parentConstraint(ctrl, joint)
        cmds.scaleConstraint(ctrl, joint, maintainOffset=True)


def _jaw_rotate_x_plug():
    """Il plug con la rotazione X della mascella: in OPM il joint e' guidato
    da un multMatrix, quindi serve un decomposeMatrix (MEL:34837-34846)."""
    if not as_get_opm():
        return "JawJoint_M.rx"
    if not cmds.objExists("JawJointDM_M"):
        cmds.createNode("decomposeMatrix", name="JawJointDM_M")
        cmds.connectAttr("JawJointMM_M.matrixSum", "JawJointDM_M.inputMatrix")
    return "JawJointDM_M.outputRotateX"


def _build_long_snout():
    """Opzione LongSnout (MEL:34785-34868): su un muso lungo il labbro
    inferiore deve ruotare con la mascella. I joint del ribbon, i
    controller del labbro inferiore e il controller blu `lowerLip_R/L`
    passano sotto gruppi che seguono la rotazione di JawJoint_M, e i joint
    delle labbra prendono la posizione da un offset sul follicolo."""
    opm = as_get_opm()
    for i in range(1, 20):
        ctrl = "lowerLip" + chr(ord("A") + i - 1)
        for side in ("_R", "_L"):
            joint_offset = ctrl + "RibbonJointOffset" + side
            if not cmds.objExists(joint_offset):
                break
            follow = cmds.createNode(
                "transform", name=ctrl + "LongSnoutFollowJaw" + side, parent=joint_offset
            )
            if opm:  # decomposeMatrix anche in OPM
                cmds.setAttr("FitSkeleton.useOffsetParentMatrix", 0)
            as_parent_constraint(
                "JawJoint_M", follow, force_mult_matrix=True, include_pick_matrix=True
            )
            if opm:
                cmds.setAttr("FitSkeleton.useOffsetParentMatrix", 1)
            pick = ctrl + "LongSnoutFollowJawPM" + side
            for attr in ("useTranslate", "useScale", "useShear"):
                cmds.setAttr("{}.{}".format(pick, attr), 0)
            revert = cmds.createNode(
                "transform", name=ctrl + "LongSnoutFollowRevertJaw" + side, parent=joint_offset
            )
            cmds.parent(revert, follow)
            cmds.parent(ctrl + "RibbonJoint" + side, revert)

            # ... e il controller
            attach = ctrl + "Attach" + side
            attach_follow = cmds.createNode(
                "transform", name=ctrl + "AttachLongSnoutFollowJaw" + side, parent=attach
            )
            cmds.connectAttr(follow + ".r", attach_follow + ".r")
            attach_revert = cmds.createNode(
                "transform", name=ctrl + "AttachLongSnoutFollowRevertJaw" + side, parent=attach
            )
            cmds.parent(attach_revert, attach_follow)
            cmds.setAttr(ctrl + "OffsetPMA" + side + ".input3D[1]", 0, 0, 0, type="float3")
            rot_offset = cmds.createNode(
                "transform",
                name=ctrl + "AttachLongSnoutFollowRotOffsetJaw" + side,
                parent=attach_revert,
            )
            as_align(rot_offset, ctrl + "Offset" + side, translate=True)
            cmds.parent("SDK" + ctrl + side, rot_offset, relative=True)

    # controller blu del labbro
    for side in ("_R", "_L"):
        follow_parent = "lowerLipFollow" + side
        if not cmds.objExists(follow_parent):
            continue
        to_ws = cmds.createNode(
            "transform", name="lowerLipAttachLongSnoutFollowJawToWs" + side, parent=follow_parent
        )
        to_ws = cmds.parent(to_ws, world=True)[0]
        cmds.setAttr(to_ws + ".r", 0, 0, 0, type="float3")
        if side == "_R":
            cmds.setAttr(to_ws + ".ry", 180)
        to_ws = cmds.parent(to_ws, follow_parent)[0]
        follow = cmds.createNode(
            "transform", name="lowerLipAttachLongSnoutFollowJaw" + side, parent=to_ws
        )
        revert = cmds.createNode(
            "transform", name="lowerLipAttachLongSnoutFollowJawRevert" + side, parent=follow_parent
        )
        cmds.parent(revert, follow)
        cmds.connectAttr(_jaw_rotate_x_plug(), follow + ".rx")
        cmds.parent("SDKlowerLip" + side, revert)

    for follicle in cmds.listRelatives("LipFollicles", children=True) or []:
        if not follicle.startswith("lower"):
            continue
        tokens = follicle.split("_")
        nr, side = tokens[0].replace("lowerfollicle", "", 1), "_" + tokens[1]
        offset = cmds.createNode(
            "transform", name="lowerLongSnoutOffset{}{}".format(nr, side), parent=follicle
        )
        as_align(offset, "lowerLipJoint{}{}".format(nr, side), translate=True)
        mm = cmds.createNode("multMatrix", name="lowerLongSnoutOffsetMM{}{}".format(nr, side))
        dm = cmds.createNode("decomposeMatrix", name="lowerLongSnoutOffsetDM{}{}".format(nr, side))
        cmds.connectAttr(offset + ".worldMatrix", mm + ".matrixIn[0]")
        cmds.connectAttr("LipFollicles.worldInverseMatrix", mm + ".matrixIn[1]")
        cmds.connectAttr(mm + ".matrixSum", dm + ".inputMatrix")
        cmds.connectAttr(
            dm + ".outputTranslate", "lowerLipBC{}{}.color1".format(nr, side), force=True
        )


def _long_snout_finish():
    """Opzione LongSnout nel finish (MEL:35116-35146): i joint del labbro
    inferiore ruotano con la mascella (orientConstraint, con la rotazione
    originale come offset) e cosi' il sistema "fleshy". Si perde la
    rotazione del labbro inferiore da LipRegion_M."""
    for joint in cmds.listRelatives("LipJoints_M", children=True) or []:
        if not joint.startswith("lowerLipJoint"):
            continue
        source = cmds.listConnections(joint + ".rx", source=True, destination=False, plugs=True)
        if not source:
            continue
        cmds.disconnectAttr(source[0], joint + ".rx")
        cmds.orientConstraint("JawJoint_M", joint, maintainOffset=True)
        cmds.connectAttr(source[0], joint + "_orientConstraint1.offsetX")
    cmds.connectAttr(
        "lowerLipConstrainedFleshyDM_M.outputRotate",
        "lowerLipConstrainedFleshy_M.rotate",
        force=True,
    )
    rotate_x = _jaw_rotate_x_plug()
    for side in ("_R", "_L"):
        cmds.connectAttr(rotate_x, "lowerLipJointFleshy{}.rotateX".format(side))


def _build_jaw_controller():
    """Controller Jaw_M e joint JawJoint_M (qui perche' SmileLineDown segue
    in parte la mascella), piu' JawMix_M per lingua e denti (MEL:34749-34887)."""
    create_face_controller("Jaw", "_M", 2)
    cmds.select("FaceJoint_M")
    cmds.joint(name="JawJoint_M")
    cmds.setAttr("JawJoint_M.segmentScaleCompensate", 0)
    pos = _ws("JawPivot")
    cmds.xform("JawOffset_M", worldSpace=True, translation=(0, pos[1], pos[2]))
    as_align("JawJoint_M", "Jaw_M", translate=True)
    cmds.parent("JawOffset_M", "SideReverse_M")
    cmds.setAttr("JawOffset_M.s", 1, 1, 1, type="float3")
    as_parent_constraint("Jaw_M", "JawJoint_M", maintain_offset=True)

    face_half_moon_curve("Jaw_M", -90)
    cvs = "Jaw_M.cv[0:99]"
    cmds.move(0, 0.25, 0, cvs, relative=True, objectSpace=True)
    cmds.scale(5, 5, 5, cvs, relative=True, pivot=(0, pos[1], pos[2]))
    jaw = _ws("Jaw")
    cmds.move(0, jaw[1] - pos[1], (jaw[2] - pos[2]) * 1.1, cvs, relative=True)

    if get_fit_option("LongSnout"):
        _build_long_snout()

    cmds.createNode("transform", name="JawMix_M", parent="JawOffset_M")
    for letter, attr in (("T", "t"), ("R", "r")):
        pma = cmds.createNode("plusMinusAverage", name="JawMix{}PMA".format(letter))
        cmds.connectAttr("Jaw_M." + attr, pma + ".input3D[0]")
        cmds.connectAttr("SDKJaw_M." + attr, pma + ".input3D[1]")
        cmds.connectAttr(pma + ".output3D", "JawMix_M." + attr)
    cmds.createNode("multiplyDivide", name="JawMixSMPD")
    cmds.connectAttr("Jaw_M.s", "JawMixSMPD.input1")
    cmds.connectAttr("SDKJaw_M.s", "JawMixSMPD.input2")
    cmds.connectAttr("JawMixSMPD.output", "JawMix_M.s")

    as_parent_constraint("Jaw_M", "JawFollow_M", maintain_offset=True)


_REQUIRED = (
    "templateLayer", "DeformationLayers", "FaceJoint_M", "SideReverse_M", "JawFollow_M",
    "JawPivot", "Jaw", "Throat", "FaceBuildInProgress", "FaceBuildInProgressHidden",
    "FaceBuildingSets", "lipArea", "ctrlMouth_M", "lowerLipMainCurve", "upperLipOuterCurve",
)  # fmt: skip


def face_jaw_weighing(num_jaw_smooths=NUM_JAW_SMOOTHS_DEFAULT) -> bool:
    """Controller della mascella e dei denti e pesi della mascella su
    `JawOpenLayer` (asFaceJawWeighing). Salta (True) senza
    `upperLipMainCurve`, come il MEL.

    Args:
        num_jaw_smooths: passate di smooth dell'area della mascella
            (intField `asFaceNumJawSmooths` della UI MEL).
    """
    if not cmds.objExists(FIT_SKELETON):
        cmds.warning("FaceFitSkeleton not found")
        return False
    if not cmds.objExists("upperLipMainCurve"):
        return True
    geometry = get_fit_option("Face") or ""
    head_joint = get_fit_option("HeadJoint") or ""
    missing = [n for n in (geometry, head_joint) + _REQUIRED if not n or not cmds.objExists(n)]
    if missing:
        cmds.warning("face_jaw_weighing: missing {}".format(", ".join(missing) or "Face/HeadJoint"))
        return False

    face_cheek_raiser_finish()

    # le curve erano uno step di fitting: si creano qui se mancano (e
    # restano un elemento di fit)
    if not cmds.objExists("FaceFitJawCurves") and not FacialFitting(geometry).fit_jaw_curves():
        return False
    scale = cmds.getAttr(FIT_SKELETON + ".faceScale")

    # JawLayer (weight-by-softmod ignora i pesi bloccati)
    if not cmds.getAttr(geometry + ".v", lock=True):
        cmds.setAttr(geometry + ".v", 0)
    for layer in cmds.listRelatives("DeformationLayers", children=True) or []:
        cmds.setAttr(layer + ".v", 0)
    cmds.duplicate("templateLayer", name="JawLayer")
    _new_skin_cluster([head_joint], "JawLayer", "JawLayerSC")
    as_show_layer("Jaw")
    as_face_hide_controllers(True)

    _build_jaw_controller()
    for upper_lower in ("upper", "lower"):
        teeth = get_fit_option(upper_lower.capitalize() + "Teeth") or ""
        if teeth and all(cmds.objExists(item) for item in teeth.split()):
            _build_teeth_controller(upper_lower, teeth, scale)
    for joint in ("JawJoint_M", "upperTeethJoint_M", "lowerTeethJoint_M"):
        if cmds.objExists(joint):
            cmds.setAttr(joint + ".segmentScaleCompensate", 0)
    for offset in ("upperTeethOffset_M", "lowerTeethOffset_M"):
        if cmds.objExists(offset):
            cmds.setAttr(offset + ".v", 0)

    _add_influence("JawLayerSC", "JawJoint_M")
    _new_skin_cluster(["FaceJoint_M", "JawJoint_M"], "JawCurve", "JawCurveSC", 1)

    # JawOpenLayer: la mesh su cui si pesano FaceJoint_M e JawJoint_M
    cmds.duplicate("templateLayer", name=_LAYER)
    cmds.parent(_LAYER, "FaceBuildInProgress")
    cmds.setAttr("JawLayer.v", 0)
    cmds.setAttr(_LAYER + ".v", 1)
    cmds.sets(_LAYER, edit=True, forceElement="initialShadingGroup")
    _new_skin_cluster(["FaceJoint_M", "JawJoint_M"], _LAYER, _LAYER_SC, 1)
    cmds.skinPercent(_LAYER_SC, _LAYER + ".vtx[*]", transformValue=("FaceJoint_M", 1))
    cmds.sets(_set_vtxs("lipArea", _LAYER), name="lipAreaJawOpenLayer")
    cmds.sets("lipAreaJawOpenLayer", add="FaceBuildingSets")

    _lock_weights(0)
    skin_teeth()
    face_design_mouth_open()
    face_weight_lips()
    face_update_jaw_curves_weights(num_jaw_smooths)

    cmds.setAttr("JawLayer.v", 0)
    cmds.parent("FaceFitJawCurves", "FaceBuildInProgress")
    cmds.parent("mouthOpenSoftModHandle", "FaceBuildInProgressHidden")
    cmds.currentTime(30)
    cmds.select(clear=True)
    return True


# -- asFaceJawWeighingFinish ----------------------------------------------


def _add_constrained(target, source_a, source_b, value):
    if all(cmds.objExists(n) for n in (target, source_a, source_b)):
        face_add_constrained(target, source_a, source_b, value)
    else:
        cmds.warning("face_jaw_weighing_finish: {} cannot follow the jaw".format(target))


def _under_lip_region(offset, multiply_nodes):
    """In OPM un nodo "constrained" non puo' stare sotto un controller
    mobile (LipRegion_M): la matrice inversa si prende da un gemello
    dell'offset messo sotto LipRegionOffset_M (MEL:35055-35079)."""
    twin = offset.replace("Offset", "OffsetUnderLipRegion")
    if not cmds.objExists(twin):
        cmds.createNode("transform", name=twin, parent=offset)
        cmds.parent(twin, "LipRegionOffset_M")
    for node in multiply_nodes:
        if cmds.objExists(node):
            cmds.connectAttr(twin + ".worldInverseMatrix", node + ".matrixIn[2]", force=True)


def _jaw_follow_on_lip_joints(long_snout):
    """La rotazione di JawFollow entra nel setup `.rx` dei joint delle
    labbra: piena sul labbro inferiore, a meta' sugli angoli
    (MEL:35084-35114). Con LongSnout il MEL crea solo il decomposeMatrix:
    la rotazione arriva dall'orientConstraint di `_long_snout_finish`."""
    for joint in cmds.listRelatives("LipJoints_M", children=True) or []:
        source = cmds.listConnections(
            joint + ".rx", skipConversionNodes=True, source=True, destination=False
        )
        if not source:
            continue
        bw = source[0]
        if not cmds.objExists("lowerLipFollowRXDM_M"):
            cmds.createNode("decomposeMatrix", name="lowerLipFollowRXDM_M")
            cmds.connectAttr("lowerLipBM_M.outputMatrix", "lowerLipFollowRXDM_M.inputMatrix")
        if long_snout:
            continue
        cmds.connectAttr("lowerLipFollowRXDM_M.outputRotateX", bw + ".input[6]")
        weight = 0.5 + min(max(cmds.getAttr(bw + ".weight[5]"), 0.0), 1.0) * 0.5
        if bw.startswith("upper"):
            weight = 1 - weight
        if joint.startswith("cornerLipJoint"):
            weight = 0.5
        cmds.setAttr(bw + ".weight[6]", weight)


def _copy_jaw_weights_to_face(geometry, skin_cluster, head_joint):
    """Copia sul viso il peso di JawJoint_M di JawOpenLayer, togliendolo al
    solo joint della testa (MEL:35161-35186)."""
    _add_influence(skin_cluster, "JawJoint_M")
    face_joints = cmds.listRelatives("FaceJoint_M", allDescendents=True, type="joint") or []
    for joint in face_joints + ["FaceJoint_M"]:
        if cmds.attributeQuery("lockInfluenceWeights", node=joint, exists=True):
            cmds.setAttr(joint + ".lockInfluenceWeights", 1)
    cmds.setAttr("JawJoint_M.lockInfluenceWeights", 0)
    cmds.setAttr(head_joint + ".lockInfluenceWeights", 0)

    cmds.select(_LAYER)
    cmds.skinCluster(_LAYER_SC, edit=True, selectInfluenceVerts="JawJoint_M")
    for vtx in cmds.ls(selection=True, flatten=True):
        if "." not in vtx:
            continue
        _skin_percent(
            skin_cluster, vtx.replace(_LAYER, geometry, 1), "JawJoint_M", _jaw_weight(vtx)
        )
    _lock_weights(0)


def face_jaw_weighing_finish():
    """Chiude JawWeighing (asFaceJawWeighingFinish): pesi sul viso, labbra
    e guance che seguono la mascella, posa convertita in SDK su
    ctrlMouth_M.ty. Idempotente via FaceBuildInProgress.JawWeighingFinish."""
    if not cmds.objExists("upperLipMainCurve"):
        return
    if not cmds.objExists("FaceBuildInProgress"):
        cmds.warning("face_jaw_weighing_finish: FaceBuildInProgress not found")
        return
    if cmds.attributeQuery("JawWeighingFinish", node="FaceBuildInProgress", exists=True):
        return
    geometry = get_fit_option("Face") or ""
    skin_cluster = get_fit_option("SkinCluster") or ""
    head_joint = get_fit_option("HeadJoint") or ""
    required = (geometry, skin_cluster, head_joint, _LAYER, "JawCurveSC", "Jaw_M", "ctrlMouth_M")
    if not all(n and cmds.objExists(n) for n in required):
        cmds.warning("face_jaw_weighing_finish: JawWeighing was not built, skipping")
        return
    cmds.addAttr(
        "FaceBuildInProgress",
        longName="JawWeighingFinish",
        attributeType="bool",
        defaultValue=True,
        keyable=False,
    )

    cmds.currentTime(0)
    cmds.delete("JawCurveSC")
    cmds.parent(_LAYER, "DeformationLayers")
    cmds.parent("FaceFitJawCurves", FIT_SKELETON)
    as_show_layer("Normal")
    for offset in ("LipRegionOffset_M", "lowerLipOffset_M"):
        if cmds.objExists(offset):
            cmds.setAttr(offset + ".v", 1)

    _add_constrained("upperLip_M", "JawFollow_M", "lowerFaceStatic_M", 0)
    _add_constrained("lowerLip_M", "JawFollow_M", "lowerFaceStatic_M", 10)
    _add_constrained("ChinCrease_M", "JawFollow_M", "lowerFaceStatic_M", 10)
    for side in ("_R", "_L"):
        follow = "JawFollow" + side
        as_parent_constraint("Jaw_M", follow, maintain_offset=True)
        if cmds.objExists("LipOffset" + side):
            cmds.setAttr("LipOffset" + side + ".v", 1)
        _add_constrained("Lip" + side, follow, "lowerFaceStatic" + side, 5)
        for name, value in (("Cheek", 5), ("FrownBulge", 8), ("SmileBulge", 2), ("CheekBone", 1)):
            _add_constrained(name + side, follow, "middleFaceStatic" + side, value)
        if cmds.objExists("LipOffset" + side) and cmds.objExists("LipRegionOffset_M"):
            _under_lip_region("LipOffset" + side, ["LipMMA" + side, "LipMMB" + side])
            if side == "_L":
                for upper_lower in ("upper", "lower"):
                    if cmds.objExists(upper_lower + "LipOffset_M"):
                        _under_lip_region(
                            upper_lower + "LipOffset_M",
                            [upper_lower + "LipMMA_M", upper_lower + "LipMMB_M"],
                        )
    cmds.dgdirty(allPlugs=True)

    long_snout = bool(get_fit_option("LongSnout"))
    if cmds.objExists("LipJoints_M") and cmds.objExists("lowerLipBM_M"):
        _jaw_follow_on_lip_joints(long_snout)
        if long_snout:
            _long_snout_finish()
    _copy_jaw_weights_to_face(geometry, skin_cluster, head_joint)

    # la posa della mascella passa al DrivingSystem
    cmds.currentTime(30)
    for attr in ("ty", "tz", "rx"):
        ds_sdk("ctrlMouth_M.ty", "SDKJaw_M." + attr, -1, cmds.getAttr("Jaw_M." + attr))
    for node in ("Jaw_M", "ctrlMouth_M"):
        curves = cmds.listConnections(node, source=True, destination=False, type="animCurve")
        if curves:
            cmds.delete(curves)
    cmds.setAttr("ctrlMouth_M.ty", 0)
    for attr in ("tx", "ry", "rz"):
        cmds.setAttr("Jaw_M." + attr, lock=False)
    cmds.xform(
        "Jaw_M", objectSpace=True, translation=(0, 0, 0), rotation=(0, 0, 0), scale=(1, 1, 1)
    )

    as_face_hide_controllers(True)
    if cmds.objExists("ctrlBoxMouth_M"):
        cmds.setAttr("ctrlBoxMouth_M.v", 1)

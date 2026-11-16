"""
Facial Fitting Module - Interactive selection of facial landmarks.

This module handles the interactive selection of vertex loops and points
that define the facial regions (eyes, lips, nose, etc.).
Based on AdvancedSkeleton's asCreateFaceFit workflow.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Dict, List, Optional, Tuple

import maya.cmds as cmds
import maya.mel as mel

from .fit_options import get_fit_option, get_left_suffix, set_fit_option
from .shaders import ensure_fit_shaders

# Versione AdvancedSkeleton di riferimento per la parita' (header MEL):
# scritta sugli oggetti fit che nel MEL ricevono asGetScriptVersion.
_AS_SCRIPT_VERSION = 6.661


class FitType(Enum):
    """Type of fitting selection."""

    VERTEX = "vertex"  # Single vertex
    EDGE_LOOP = "edge_loop"  # Edge loop (converted to vertices)
    VERTEX_LOOP = "vertex_loop"  # Ordered vertex selection
    VERTEX_LOOP_HALF = "vertex_loop_half"  # Half loop (upper/lower lip, eyelid)
    FACE_AREA = "face_area"  # Polygon face area
    CURVE = "curve"  # Curve from ordered vertices
    NO_SELECTION = "no_selection"  # Region created without selection (Tongue, UpMidLo)


@dataclass
class FitRegion:
    """Definition of a facial fit region."""

    name: str
    display_name: str
    fit_type: FitType
    color: int  # Maya override color index
    required: bool = True
    mirrored: bool = True  # Has left side counterpart
    has_upper_lower: bool = False  # Has upper/lower variants (lips, eyelids)
    description: str = ""
    order: int = 0  # Build order
    parent_region: str = ""  # Parent region group
    shading_group: str = ""  # Shading group for visual
    is_sphere: bool = False  # MEL $isSphere: landmark sferico con falloff
    mid: bool = False  # MEL $mid: regione di mezzeria (disabilitata nel fitting Left)


@dataclass
class FitData:
    """Stores the fitting data for a region."""

    region_name: str
    vertices: List[str] = field(default_factory=list)
    positions: List[Tuple[float, float, float]] = field(default_factory=list)
    curve: Optional[str] = None
    locator: Optional[str] = None
    selection_string: str = ""


def _lock_main_attrs(node: str):
    """Equivalente di asLockAttr <node> 1 1 1 0: locka t/r/s, lascia v."""
    for attr in ("tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz"):
        cmds.setAttr("{}.{}".format(node, attr), lock=True)


def _deselect_lowest_half_of_vtx():
    """Parita' asFaceDeselectLowestHalfOfVtx: mantiene selezionati solo i
    vertici con Y sopra la media (port-spec par.6). Opera sulla selezione
    Maya corrente; usata per LipOuter prima della scelta di startVtx.

    Algoritmo (righe MEL 27553-27569):
      tys_average = mean(pos.y for v in selected_vtxs)
      keep only vtxs where pos.y > tys_average
    """
    vtxs = cmds.ls(selection=True, flatten=True)
    if not vtxs:
        return

    tys = []
    for v in vtxs:
        pos = cmds.xform(v, query=True, worldSpace=True, translation=True)
        tys.append(pos[1])

    tys_average = sum(tys) / float(len(tys))

    cmds.select(clear=True)
    for i, v in enumerate(vtxs):
        if tys[i] > tys_average:
            cmds.select(v, add=True)


def face_fit_reselect(section: str, part: str = ""):
    """Seleziona i componenti salvati di una regione (parita'
    asFaceFitReSelect, righe MEL 38271-38285).

    Il nodo sorgente e' FaceFit<section><part><leftSuffix>, dove
    leftSuffix deriva da FaceFitSkeleton.NonSymSide. Un suffisso "_R"
    su section forza il lato destro anche in modalita' Left (convenzione
    MEL per le chiamate dal build).

    Nodo o attributo selection assenti: nessuna azione (come nel MEL).
    """
    left_suffix = ""
    if section.endswith("_R"):
        section = section.replace("_R", "", 1)
    elif get_left_suffix() == "Left":
        left_suffix = "Left"

    fit_node = "FaceFit{}{}{}".format(section, part, left_suffix)
    print("// ReSelecting: {} : {}{}".format(section, part, left_suffix))
    if not cmds.objExists(fit_node):
        return
    if not cmds.attributeQuery("selection", node=fit_node, exists=True):
        return
    stored = cmds.getAttr(fit_node + ".selection") or ""
    if stored.split():
        cmds.select(stored.split(), replace=True)


def face_fit_swap_upper_lower(section: str, part: str = ""):
    """Scambia upper e lower di un fit loop (parita'
    asFaceFitSwapUpperLower, righe MEL 38287-38308).

    Rinomina incrociata di curve e cilindri tramite il nome temporaneo
    *Swapping, poi riassegna gli shading group cosi' che la convenzione
    (asGreenSG sull'upper, asGreen2SG sul lower) segua la posizione e
    non la mesh. Come nel MEL, opera sui nomi senza suffisso Left.
    """
    upper_cyl = "upper{}Cylinder{}".format(section, part)
    lower_cyl = "lower{}Cylinder{}".format(section, part)
    upper_crv = "upper{}{}Curve".format(section, part)
    lower_crv = "lower{}{}Curve".format(section, part)
    for node in (upper_cyl, lower_cyl, upper_crv, lower_crv):
        if not cmds.objExists(node):
            cmds.warning("face_fit_swap_upper_lower: {} not found".format(node))
            return

    cmds.rename(upper_cyl, upper_cyl + "Swapping")
    cmds.rename(lower_cyl, upper_cyl)
    cmds.rename(upper_cyl + "Swapping", lower_cyl)
    cmds.rename(upper_crv, upper_crv + "Swapping")
    cmds.rename(lower_crv, upper_crv)
    cmds.rename(upper_crv + "Swapping", lower_crv)

    upper_sg = (
        cmds.listConnections(upper_cyl + "Shape.instObjGroups[0]", source=False, destination=True)
        or [None]
    )[0]
    lower_sg = (
        cmds.listConnections(lower_cyl + "Shape.instObjGroups[0]", source=False, destination=True)
        or [None]
    )[0]
    if upper_sg and lower_sg:
        cmds.sets(upper_cyl, edit=True, forceElement=lower_sg)
        cmds.sets(lower_cyl, edit=True, forceElement=upper_sg)

    print("// Swapped Upper and Lower for: {}{}".format(section, part))


def face_fit_delete(region: str):
    """Cancella il fit di una regione (parita' asFaceDeleteFromCheckBox,
    righe MEL 39193-39216, senza la confirmDialog che resta alla view).

    Cancella FaceFit<region><leftSuffix> (leftSuffix da NonSymSide);
    per le regioni Lip* cancella anche il lato Left, creato in coppia
    dall'auto-fit non-symmetrical.
    """
    left_suffix = get_left_suffix()
    fit_node = "FaceFit{}{}".format(region, left_suffix)
    if cmds.objExists(fit_node):
        cmds.delete(fit_node)
        print("// Deleted {}".format(fit_node))
    if region.startswith("Lip") and cmds.objExists("FaceFit{}Left".format(region)):
        cmds.delete("FaceFit{}Left".format(region))
        print("// Deleted FaceFit{}Left".format(region))


def face_fit_hide(sections: str, parts: str = ""):
    """Toggle di visibilita' di un gruppo fit (parita' asFaceFitHide,
    righe MEL 39218-39226). Il suffisso Left deriva da NonSymSide."""
    fit_node = "FaceFit{}{}{}".format(sections, parts, get_left_suffix())
    if not cmds.objExists(fit_node):
        cmds.warning("face_fit_hide: {} not found".format(fit_node))
        return
    vis = cmds.getAttr(fit_node + ".v")
    cmds.setAttr(fit_node + ".v", not vis)


def face_fit_anim(obj_attr: str, value: float):
    """Keyframe di preview per la modalita' animate-fit (parita'
    asFaceFitAnim, righe MEL 37608-37652).

    Con "obj.attr": chiave a t0 sul default (1 per le scale, 0 per il
    resto) e a t30 sul valore. Con il solo oggetto: chiave tutti i 9
    canali t/r/s ai default a t0 e t30 (posa di riposo). L'oggetto
    viene reso visibile (showHidden -above).
    """
    obj = obj_attr.split(".", 1)[0] if "." in obj_attr else obj_attr
    if not cmds.objExists(obj):
        return
    cmds.select(obj)
    cmds.showHidden(above=True)

    if not cmds.objExists(obj_attr):
        return
    if "." in obj_attr:
        attr = obj_attr.split(".", 1)[1]
        default_value = 1.0 if (len(attr) == 2 and attr[0] == "s" and attr[1].isalpha()) else 0.0
        cmds.setKeyframe(obj_attr, shape=False, time=0, value=default_value)
        cmds.setKeyframe(obj_attr, shape=False, time=30, value=value)
    else:
        for trs in ("t", "r", "s"):
            default_value = 1.0 if trs == "s" else 0.0
            for xyz in ("x", "y", "z"):
                plug = "{}.{}{}".format(obj, trs, xyz)
                cmds.setKeyframe(plug, shape=False, time=0, value=default_value)
                cmds.setKeyframe(plug, shape=False, time=30, value=default_value)


def remove_fit_anim_from_ctrl_box():
    """Rimuove l'animazione di fit dagli slider del ctrlBox (parita'
    asFaceRemoveFitAnimFromCtrlBox, righe MEL 37562-37581): cancella le
    animCurve in ingresso e azzera gli attributi keyable non lockati di
    ogni discendente, saltando i nodi cornice ctrlBox*."""
    if not cmds.objExists("ctrlBox"):
        cmds.warning("ctrlBox not found (face rig not built)")
        return
    for ctrl in cmds.listRelatives("ctrlBox", allDescendents=True, type="transform") or []:
        if ctrl.startswith("ctrlBox"):
            continue
        for curve in (
            cmds.listConnections(ctrl, source=True, destination=False, type="animCurve") or []
        ):
            cmds.delete(curve)
        for attr in cmds.listAttr(ctrl, keyable=True) or []:
            plug = "{}.{}".format(ctrl, attr)
            if not cmds.getAttr(plug, lock=True):
                cmds.setAttr(plug, 0)


def toggle_fit_face():
    """Commuta la visibilita' fit-skeleton <-> rig (parita'
    asToggleFitFace, MEL 50701): inverte FaceFitSkeleton.v (lockato) e
    porta FaceMotionSystem.v al valore precedente del fit."""
    if not cmds.objExists("FaceFitSkeleton"):
        cmds.warning("FaceFitSkeleton not found")
        return
    fit_vis = cmds.getAttr("FaceFitSkeleton.v")
    cmds.setAttr("FaceFitSkeleton.v", lock=False)
    cmds.setAttr("FaceFitSkeleton.v", 0 if fit_vis else 1)
    cmds.setAttr("FaceFitSkeleton.v", lock=True)
    if cmds.objExists("FaceMotionSystem"):
        try:
            cmds.setAttr("FaceMotionSystem.v", fit_vis)
        except RuntimeError:
            pass


def remove_fit_animations_from_on_face_ctrls():
    """Rimuove l'animazione di fit dai controlli on-face (parita'
    asFaceRemoveFitAnimationsFromOnFaceCtrls, righe MEL 37583-37606):
    per ogni gruppo *Offset_* ripulisce le animCurve del controllo
    corrispondente e ne azzera la trasformazione; cancella i transform
    di servizio *Values_<lettera>."""
    if not cmds.objExists("OnFacecontrols"):
        cmds.warning("OnFacecontrols not found (face rig not built)")
        return
    descendents = cmds.listRelatives("OnFacecontrols", allDescendents=True, type="transform") or []
    for node in descendents:
        if "Offset_" not in node:
            continue
        ctrl = node.replace("Offset", "", 1)
        if not cmds.objExists(ctrl):
            continue
        curves = cmds.listConnections(ctrl, source=True, destination=False, type="animCurve") or []
        if curves:
            cmds.delete(curves)
        cmds.xform(
            ctrl, objectSpace=True, translation=(0, 0, 0), rotation=(0, 0, 0), scale=(1, 1, 1)
        )
    for node in cmds.listRelatives("OnFacecontrols", allDescendents=True, type="transform") or []:
        if len(node) > 7 and node[-1].isupper() and node.endswith("Values_" + node[-1]):
            cmds.delete(node)


def get_face_fit_selection(fit_object: str, geometry: str = "") -> str:
    """Ricostruisce la selezione vertici dalla posizione CORRENTE di un
    oggetto fit (parita' asGetFaceFitSelection, righe MEL 38158-38246).

    Contratto chiave fitting->build: l'utente puo' spostare locator e CV
    dopo il fit, quindi il build non legge l'attributo selection salvato
    ma ricampiona con closestPointOnMesh sulla geometria Face.

    Args:
        fit_object: locator (es. "EyeBrowInner"), componente cv
            (es. "upperLipOuterCurve.cv[0]"), curva, gruppo di curve
            (es. "FaceFitEyeLidMainCurve") o mesh (AreaMesh).
        geometry: mesh su cui campionare; default: opzione "Face" di
            FaceFitSkeleton (equivalente del textField MEL).

    Returns:
        "geo.vtx[N]" per locator/cv (senza spazio finale), oppure
        "geo.vtx[A] geo.vtx[B] ... " per curve e mesh (uno per CV o
        vertice, con spazio dopo ogni entry). "" su input non valido.
    """
    sel = cmds.ls(selection=True) or []

    if not geometry:
        geometry = get_fit_option("Face") or ""
    # la geometry puo' essere un componente (es. facce eyeBall del main
    # mesh): si campiona sull'oggetto sottostante
    if "." in geometry:
        objs = cmds.ls(geometry, objectsOnly=True) or []
        geometry = objs[0] if objs else ""
    if not geometry or not cmds.objExists(geometry):
        cmds.warning("get_face_fit_selection: face geometry not found ({!r})".format(geometry))
        return ""

    object_type = ""
    shapes = []
    if "." in fit_object:
        # componente esplicito (es. cv di una curva): campionato come
        # posizione singola, stesso ramo del locator (parita' MEL)
        object_type = "locator"
    elif not cmds.objExists(fit_object):
        cmds.warning("get_face_fit_selection: {} not found".format(fit_object))
        return ""
    else:
        shapes = cmds.listRelatives(fit_object, shapes=True) or []
        if shapes:
            object_type = cmds.objectType(shapes[0])

    if cmds.objExists("closestSamplerFitSelection2"):
        cmds.delete("closestSamplerFitSelection2")
    sampler = cmds.createNode("closestPointOnMesh", name="closestSamplerFitSelection2")
    cmds.connectAttr(geometry + ".outMesh", sampler + ".inMesh", force=True)

    def _closest_vtx(pos):
        cmds.setAttr(sampler + ".inPosition", pos[0], pos[1], pos[2], type="float3")
        return cmds.getAttr(sampler + ".result.closestVertexIndex")

    selection = ""
    curves = []
    if object_type == "locator":
        pos = cmds.xform(fit_object, query=True, worldSpace=True, translation=True)
        selection = "{}.vtx[{}]".format(geometry, _closest_vtx(pos))
    elif object_type == "mesh":
        # AreaMesh: bypass temporaneo dell'estrusione per campionare la
        # superficie non offsettata
        extrude = fit_object + "PolyExtrudeFacet"
        if cmds.objExists(extrude):
            cmds.setAttr(extrude + ".nodeState", 1)
        num_vtx = cmds.polyEvaluate(fit_object, vertex=True)
        for i in range(num_vtx):
            pos = cmds.xform(
                "{}.vtx[{}]".format(fit_object, i), query=True, worldSpace=True, translation=True
            )
            selection += "{}.vtx[{}] ".format(geometry, _closest_vtx(pos))
        if cmds.objExists(extrude):
            cmds.setAttr(extrude + ".nodeState", 0)
    elif not shapes:
        # gruppo (es. FaceFitLipMainCurve): campiona le curve figlie,
        # saltando i profili dei cilindri
        for child in cmds.listRelatives(fit_object, children=True) or []:
            if "Profile" in child:
                continue
            if cmds.listRelatives(child, shapes=True):
                curves.append(child)
    else:
        curves = [fit_object]

    for curve in curves:
        num_cvs = cmds.getAttr(curve + ".spans") + cmds.getAttr(curve + ".degree")
        # caso speciale MEL: lievi asimmetrie del modello disallineano
        # facilmente il num CV Right vs Left per il Lip
        if "Lip" in curve:
            face_fit_reselect("Lip", "Main")
        for y in range(num_cvs):
            pos = cmds.xform(
                "{}.cv[{}]".format(curve, y), query=True, worldSpace=True, translation=True
            )
            selection += "{}.vtx[{}] ".format(geometry, _closest_vtx(pos))

    cmds.delete(sampler)
    if sel:
        cmds.select(sel, replace=True)
    else:
        cmds.select(clear=True)
    return selection


def get_face_fit_selection_other_object(fit_object: str, other_object: str, side: str = "") -> str:
    """Campiona un oggetto fit su una geometria diversa dalla Face
    (parita' asGetFaceFitSelectionOtherObject, righe MEL 38145-38156).

    Usata dal build per Pupil/Iris, campionati sulla mesh dell'occhio.
    Il parametro side esiste per parita' di firma: e' inutilizzato anche
    nel MEL.
    """
    return get_face_fit_selection(fit_object, geometry=other_object)


def _as_deformer(deformer):
    """Crea un deformer con i deformer-set legacy (parita' asDeformer,
    righe MEL 38770-38794): Maya >= 2022 va forzato a non usare i
    component tags, perche' il fitting/build AS legge i set.

    Senza preferenze utente (mayapy) l'optionVar non esiste e Maya usa
    comunque i component tags: va quindi forzata anche in quel caso, e
    rimossa dopo.
    """
    name = "deformationUseComponentTags"
    existed = bool(cmds.optionVar(exists=name))
    restore_tags = bool(cmds.optionVar(query=name)) if existed else True
    if restore_tags:
        cmds.optionVar(intValue=(name, 0))
    try:
        if deformer == "softMod":
            result = cmds.softMod(falloffMode=1, falloffAroundSelection=0)
        elif deformer == "cluster":
            result = cmds.cluster(envelope=1)
        else:
            result = mel.eval(deformer)
    finally:
        if not existed:
            cmds.optionVar(remove=name)
        elif restore_tags:
            cmds.optionVar(intValue=(name, 1))
    return result


def _curve_offset_mesh(curve, geometry, offset):
    """Offsetta una curva sulla superficie di una mesh (parita'
    asCurveOffsetMesh, righe MEL 38796-38821).

    Rebuild temporaneo a 20 spans degree 3, poi ogni CV viene proiettato
    sulla superficie (geometryConstraint) e spostato di offset lungo la
    normale (normalConstraint con asse X + locator figlio a tx=offset);
    rebuild finale agli spans originali e ripristino degli estremi
    (cv[0] e cv[99], che clampa all'ultimo CV - idioma MEL).
    """
    spans = cmds.getAttr(curve + ".spans")
    start_pos = cmds.xform(curve + ".cv[0]", query=True, worldSpace=True, translation=True)
    end_pos = cmds.xform(curve + ".cv[99]", query=True, worldSpace=True, translation=True)
    cmds.rebuildCurve(
        curve,
        constructionHistory=0,
        replaceOriginal=1,
        rebuildType=0,
        endKnots=1,
        keepRange=0,
        keepControlPoints=0,
        keepEndPoints=1,
        keepTangents=0,
        spans=20,
        degree=3,
        tolerance=0.01,
    )
    loc = cmds.spaceLocator(name="constraintLoc")[0]
    loc2 = cmds.spaceLocator(name="constraintLoc2")[0]
    cmds.parent(loc2, loc)
    cmds.setAttr("constraintLoc2.tx", offset)
    cmds.geometryConstraint(geometry, loc, weight=1)
    cmds.normalConstraint(
        geometry,
        loc,
        weight=1,
        aimVector=(1, 0, 0),
        upVector=(0, 1, 0),
        worldUpType="vector",
        worldUpVector=(0, 1, 0),
    )
    for i in range(23):
        pos_a = cmds.xform(
            "{}.cv[{}]".format(curve, i), query=True, worldSpace=True, translation=True
        )
        cmds.xform(loc, worldSpace=True, translation=pos_a)
        pos_b = cmds.xform("constraintLoc2", query=True, worldSpace=True, translation=True)
        cmds.xform("{}.cv[{}]".format(curve, i), worldSpace=True, translation=pos_b)
    cmds.rebuildCurve(
        curve,
        constructionHistory=0,
        replaceOriginal=1,
        rebuildType=0,
        endKnots=1,
        keepRange=0,
        keepControlPoints=0,
        keepEndPoints=1,
        keepTangents=0,
        spans=int(spans),
        degree=3,
        tolerance=0.01,
    )
    cmds.delete(loc)
    cmds.xform(curve + ".cv[0]", worldSpace=True, translation=start_pos)
    cmds.xform(curve + ".cv[99]", worldSpace=True, translation=end_pos)


def _select_least_edges_path(geometry, start_vtx_nr, end_vtx_nr):
    """Seleziona il percorso di edge "con meno edge" tra due vertici
    (parita' asSelectLeastEdgesPath, righe MEL 27571-27643).

    Preferisce edgeLoop/edgeRing (percorsi topologici) allo
    shortestEdgePath, ma torna allo shortest se il loop/ring non
    contiene entrambi i vertici o e' piu' lungo di oltre 3 edge.
    Lascia il percorso selezionato; selezione vuota = nessun percorso.
    """
    start_comp = "{}.vtx[{}]".format(geometry, start_vtx_nr)
    end_comp = "{}.vtx[{}]".format(geometry, end_vtx_nr)

    # vertici adiacenti: le Loop/Ring Utilities estenderebbero invece di
    # restare contenute, quindi si usa direttamente lo shortest path
    cmds.select(start_comp)
    cmds.polySelectConstraint(propagate=1, type=0x0001)
    grown = cmds.ls(selection=True, flatten=True) or []
    cmds.select(end_comp)
    end_flat = (cmds.ls(selection=True, flatten=True) or [""])[0]
    if end_flat in grown:
        path = (
            cmds.polySelect(
                geometry,
                query=True,
                asSelectString=True,
                shortestEdgePath=(start_vtx_nr, end_vtx_nr),
            )
            or []
        )
        if path:
            cmds.select(path)
        else:
            cmds.select(clear=True)
        return

    cmds.select(geometry)
    # prima loop, poi ring; il percorso deve contenere start e end
    cmds.select(start_comp, end_comp)
    loop_ring = cmds.polySelectSp(query=True, loop=True) or []
    if loop_ring:
        cmds.select(loop_ring)
        loop_ring = cmds.ls(selection=True, flatten=True) or []
        if start_comp not in loop_ring or end_comp not in loop_ring:
            cmds.select(clear=True)
            loop_ring = []
    if not loop_ring:
        # parita' MEL: il query ring lavora sulla selezione corrente
        # (vuota se il ramo loop ha appena azzerato)
        loop_ring = cmds.polySelectSp(query=True, ring=True) or []
    if loop_ring:
        cmds.select(loop_ring)
        loop_ring = cmds.ls(selection=True, flatten=True) or []
        if end_comp not in loop_ring:
            cmds.select(clear=True)
            loop_ring = []

    # un loop/ring molto piu' lungo dello shortest e' una deviazione
    cmds.select(geometry)
    path = (
        cmds.polySelect(
            geometry, query=True, asSelectString=True, shortestEdgePath=(start_vtx_nr, end_vtx_nr)
        )
        or []
    )
    if path:
        cmds.select(path)
    else:
        cmds.select(clear=True)
    shortest = cmds.ls(selection=True, flatten=True) or []
    if len(loop_ring) > len(shortest) + 3:
        loop_ring = []

    if loop_ring:
        cmds.select(loop_ring)
        cmds.ConvertSelectionToContainedEdges()
    else:
        cmds.select(geometry)
        if path:
            cmds.select(path)
        else:
            cmds.select(clear=True)


def _scan_min_max_vtxs(vtxs, tol):
    """Scansione min/max con tolleranza X (port-spec par.1 passo 7).

    Ritorna un dict: {"minX": (vtx, pos), "maxX": ..., "minY": ...,
    "maxY": ..., "minZ": ..., "maxZ": ...}.

    ATTENZIONE: il filtro pos.x < tol si applica a TUTTI i max
    (X, Y e Z), come nel MEL (righe 26620-26628).
    minX/minY/minZ non hanno il filtro.

    Args:
        vtxs: lista di stringhe componente (vertici flatten).
        tol:  soglia X per i max. 0.001 = lato destro (esclude X>0);
              9999 = nessun filtro (lato sinistro o cyclops).

    Returns:
        dict con chiavi minX/maxX/minY/maxY/minZ/maxZ.
        Ogni valore e' una tupla (vtx_name, [x, y, z]).
        vtx_name puo' essere None: sempre, se vtxs e' vuota; per i campi
        max, se NESSUN vertice passa il filtro pos.x < tol. I chiamanti
        devono verificarlo prima di usare il nome come componente.
    """
    if not vtxs:
        cmds.warning("_scan_min_max_vtxs: empty vertex list")
    # Inizializza con sentinelle: min a +inf, max (tol-filtrati) a -inf.
    # I campi max usano None come nome finche' nessun vertice supera il
    # filtro pos.x < tol (parita' MEL: maxPos = {-999,-999,-999}, name="").
    _INF = float("inf")
    result = {
        "minX": (None, [_INF, _INF, _INF]),
        "maxX": (None, [-_INF, -_INF, -_INF]),
        "minY": (None, [_INF, _INF, _INF]),
        "maxY": (None, [-_INF, -_INF, -_INF]),
        "minZ": (None, [_INF, _INF, _INF]),
        "maxZ": (None, [-_INF, -_INF, -_INF]),
    }

    for v in vtxs:
        pos = cmds.xform(v, query=True, worldSpace=True, translation=True)
        x, y, z = pos[0], pos[1], pos[2]

        # minX: no filter
        if x < result["minX"][1][0]:
            result["minX"] = (v, pos[:])

        # minY: no filter
        if y < result["minY"][1][1]:
            result["minY"] = (v, pos[:])

        # minZ: no filter
        if z < result["minZ"][1][2]:
            result["minZ"] = (v, pos[:])

        # maxX, maxY, maxZ: apply tol filter on X (MEL parity)
        if x < tol:
            if x > result["maxX"][1][0]:
                result["maxX"] = (v, pos[:])
            if y > result["maxY"][1][1]:
                result["maxY"] = (v, pos[:])
            if z > result["maxZ"][1][2]:
                result["maxZ"] = (v, pos[:])

    return result


def _find_dead_end_vtxs(vtxs):
    """Vertici con meno di 2 vicini dentro la selezione (port-spec
    par.1 passo 8). Ritorna lista (0 per loop chiusi, 2 per catene aperte).

    Algoritmo (righe MEL 26630-26644):
      per ogni vtx:
        select vtx
        ConvertSelectionToEdges
        ConvertSelectionToVertices
        deselect vtx
        neighbors = ls -sl -fl
        numNeighOnCurve = count(n in vtxs for n in neighbors)
        se numNeighOnCurve < 2: aggiungi a deadEndVtxs

    Args:
        vtxs: lista di stringhe componente (vertici flatten).

    Returns:
        Lista di vertici dead-end (solitamente 0 o 2).
    """
    vtx_set = set(vtxs)
    dead_end_vtxs = []

    for v in vtxs:
        cmds.select(v)
        cmds.ConvertSelectionToEdges()
        cmds.ConvertSelectionToVertices()
        cmds.select(v, deselect=True)
        neighbors = cmds.ls(selection=True, flatten=True) or []

        num_neigh_on_curve = sum(1 for n in neighbors if n in vtx_set)
        if num_neigh_on_curve < 2:
            dead_end_vtxs.append(v)

    cmds.select(clear=True)
    return dead_end_vtxs


def _pick_start_edges(start_vtx, sel_edges, left_suffix):
    """Sceglie edge1/edge2 uscenti da start_vtx dentro sel_edges
    (port-spec §3 "Inizializzazione di edge1/edge2", righe MEL 26822-26848).

    edge1 e' il passo verso sinistra (X media minore per il lato destro;
    invertito per left_suffix=="Left"). Ritorna (edge1, edge2);
    edge2 puo' essere "" se start_vtx e' un dead-end (un solo edge).

    Algoritmo MEL:
        select startVtx
        ConvertSelectionToEdges
        rimuovi edge non in sel_edges
        edge1 = tempString[0]
        edge2 = tempString[1]  (o "" se non esiste)
        se edge2 != "":
            posA = xform(edge1, q, ws, t)  # 6-float: [x0,y0,z0, x1,y1,z1]
            posB = xform(edge2, q, ws, t)
            condition = (posA[0]+posA[3]) > (posB[0]+posB[3])
            se leftSuffix=="Left": condition = !condition
            se condition: swap(edge1, edge2)
        # edge1 e' ora il passo verso sinistra (X minore)
    """
    sel_set = set(sel_edges)

    cmds.select(start_vtx)
    cmds.ConvertSelectionToEdges()
    all_edges = cmds.ls(selection=True, flatten=True) or []

    # filtra: solo edge in sel_edges
    filtered = [e for e in all_edges if e in sel_set]

    edge1 = filtered[0] if len(filtered) > 0 else ""
    edge2 = filtered[1] if len(filtered) > 1 else ""

    if edge2 != "":
        pos_a = cmds.xform(edge1, query=True, worldSpace=True, translation=True)
        pos_b = cmds.xform(edge2, query=True, worldSpace=True, translation=True)
        # X media di edge1 e edge2 (6-float: [x0,y0,z0,x1,y1,z1])
        x_a = pos_a[0] + pos_a[3]
        x_b = pos_b[0] + pos_b[3]
        condition = x_a > x_b
        if left_suffix == "Left":
            condition = not condition
        if condition:
            edge1, edge2 = edge2, edge1

    return edge1, edge2


def _walk_loop(sel_edges, start_vtx, end_vtx, exclude_edge, max_steps=199):
    """Edge-walk fedele al MEL (port-spec §3 "Edge-walk ramo 1",
    righe MEL 26850-26909).

    Cammina da start_vtx lungo sel_edges escludendo exclude_edge, fino
    a end_vtx oppure — se end_vtx e' "" — finche' tutti gli edge della
    selezione sono coperti (loop chiuso).

    Ritorna la lista ordinata di vertici (start_vtx incluso come primo).
    Per loop chiusi start_vtx NON viene ri-aggiunto qui: lo fa il
    chiamante (Task 3 / port-spec §3 dopo il walk, riga 26902-26906).
    Ritorna [] se la catena si interrompe (selezione non contigua).

    NOTA max_steps: il default 199 replica il cap del ramo 1 MEL; il
    ramo 2 MEL usa un cap di 499 — il chiamante del secondo ramo DEVE
    passare max_steps=499. La selezione Maya viene azzerata a ogni
    uscita.

    Algoritmo MEL fedele (incluso coveredEdges che accumula tempString[0]
    — il primo edge selezionato — a ogni iterazione):
        select startVtx
        prevVtxs = [startVtx]
        vtxs1 = [startVtx]
        coveredEdges = []
        around = False

        per i in 0..max_steps-1:
            ConvertSelectionToEdges
            rimuovi edge non in sel_edges
            rimuovi exclude_edge (se != "")
            coveredEdges.append(tempString[0])  # primo edge corrente
            ConvertSelectionToVertices
            tempString = ls -sl -fl

            se end_vtx == "":
                se len(coveredEdges) == len(sel_edges): around = True
            altrimenti:
                se end_vtx in tempString: around = True

            deselect prevVtxs
            prevVtxs = tempString
            tempString2 = ls -sl -fl (vtx rimasti)
            se tempString2 vuoto: return []  # catena interrotta

            vtxs1.append(tempString2[0])
            select tempString  # ri-seleziona il set corrente
            se around: break

        return vtxs1
    """
    sel_set = set(sel_edges)

    cmds.select(start_vtx)
    prev_vtxs = [start_vtx]
    vtxs1 = [start_vtx]
    covered_edges = []
    around = False

    for _i in range(max_steps):
        # ConvertSelectionToEdges
        cmds.ConvertSelectionToEdges()
        all_edges = cmds.ls(selection=True, flatten=True) or []

        # filtra: rimuovi edge non in sel_edges
        filtered = [e for e in all_edges if e in sel_set]

        # filtra: rimuovi exclude_edge
        if exclude_edge and exclude_edge in filtered:
            filtered.remove(exclude_edge)

        if not filtered:
            # Nessun edge valido nella selezione corrente.
            # Per catene aperte: selezione non contigua → errore.
            # Per loop chiusi (end_vtx == ""): il cammino si e' chiuso
            # senza trovare altri edge → ritorna vtxs1 corrente.
            if end_vtx != "":
                cmds.select(clear=True)
                return []
            break

        # accumula il primo edge della selezione corrente (parita' MEL).
        # NON rimuovere: pilota la terminazione dei loop chiusi.
        covered_edges.append(filtered[0])

        # seleziona solo gli edge filtrati e converti in vertici
        cmds.select(filtered)
        cmds.ConvertSelectionToVertices()
        temp_string = cmds.ls(selection=True, flatten=True) or []

        # controlla condizione di arrivo
        if end_vtx == "":
            # loop chiuso: finito quando tutti gli edge sono coperti
            if len(covered_edges) >= len(sel_edges):
                around = True
        else:
            if end_vtx in temp_string:
                around = True

        # deselect dei vertici precedenti
        for v in prev_vtxs:
            if cmds.objExists(v):
                cmds.select(v, deselect=True)

        prev_vtxs = list(temp_string)
        temp_string2 = cmds.ls(selection=True, flatten=True) or []

        if not temp_string2:
            # MEL: se tempString2[0] == "": break
            # Per catene aperte (end_vtx != "") senza aver trovato end_vtx
            # → selezione non contigua → ritorna [] come segnale di errore.
            # Per loop chiusi (end_vtx == "") → abbiamo completato il giro
            # (tutti i vtx gia' visitati) → break normale, ritorna vtxs1.
            if end_vtx != "" and not around:
                cmds.select(clear=True)
                return []
            break

        vtxs1.append(temp_string2[0])

        # ri-seleziona il set corrente di vertici per il prossimo passo
        cmds.select(temp_string)

        if around:
            break

    cmds.select(clear=True)
    return vtxs1


class FacialFitting:
    """
    Manages the interactive fitting process for facial rigging.

    This class handles:
    - Definition of all facial regions to be fitted
    - Interactive selection and storage
    - Creation of fit curves and locators
    - Validation of selections
    - Mirroring for symmetrical faces

    Usage:
        fitting = FacialFitting("head_geo")
        fitting.create_fit_skeleton()

        # Select vertices on mesh, then:
        fitting.fit_region("EyeLidMain")

        # Or use the UI (la mesh si sceglie dentro la finestra):
        from facial_rig import show_fitting_ui
        show_fitting_ui()
    """

    # Maya color indices
    COLOR_RED = 13
    COLOR_GREEN = 14
    COLOR_BLUE = 6
    COLOR_YELLOW = 17
    COLOR_CYAN = 18
    COLOR_MAGENTA = 31
    COLOR_ORANGE = 21
    COLOR_WHITE = 16
    COLOR_LIGHT_BLUE = 15

    # Routing map: region_name -> (section, part, up_and_lo)
    # Used by fit_region to delegate EyeLid*/Lip*/Pupil/Iris/EyeLidMain2
    # directly to create_face_fit (MEL-parity loop path).
    _LOOP_ROUTING = {
        "EyeLidOuter": ("EyeLid", "Outer", True),
        "EyeLidMain": ("EyeLid", "Main", True),
        "EyeLidInner": ("EyeLid", "Inner", True),
        "EyeLidMain2": ("EyeLidMain2", "", True),
        "LipOuter": ("Lip", "Outer", True),
        "LipMain": ("Lip", "Main", True),
        "LipInner": ("Lip", "Inner", True),
        "Pupil": ("Pupil", "", False),
        "Iris": ("Iris", "", False),
    }

    # All facial regions that need to be fitted
    REGIONS: Dict[str, FitRegion] = {}

    @classmethod
    def _init_regions(cls):
        """Initialize all region definitions."""
        if cls.REGIONS and "Pupil" in cls.REGIONS:
            return
        cls.REGIONS = {}

        # === EYE REGIONS ===
        cls.REGIONS["EyeBall"] = FitRegion(
            name="EyeBall",
            display_name="Eye Ball",
            fit_type=FitType.VERTEX,
            color=cls.COLOR_WHITE,
            required=True,
            mirrored=True,
            description="Select center vertex of eyeball or eyeball geometry",
            order=1,
            parent_region="Eye",
        )

        for loop_type, color, order in [
            ("Outer", cls.COLOR_RED, 10),
            ("Main", cls.COLOR_GREEN, 11),
            ("Inner", cls.COLOR_BLUE, 12),
        ]:
            cls.REGIONS[f"EyeLid{loop_type}"] = FitRegion(
                name=f"EyeLid{loop_type}",
                display_name=f"Eye Lid {loop_type} Loop",
                fit_type=FitType.VERTEX_LOOP_HALF,
                color=color,
                required=True,
                mirrored=True,
                has_upper_lower=True,
                description=f"Select the {loop_type.lower()} eyelid loop (upper half, start from inner corner)",
                order=order,
                parent_region="EyeLid",
                shading_group=f"as{['Red', 'Green', 'Blue'][['Outer', 'Main', 'Inner'].index(loop_type)]}SG",
            )

        # === LIP REGIONS ===
        for loop_type, color, order in [
            ("Outer", cls.COLOR_RED, 20),
            ("Main", cls.COLOR_GREEN, 21),
            ("Inner", cls.COLOR_BLUE, 22),
        ]:
            cls.REGIONS[f"Lip{loop_type}"] = FitRegion(
                name=f"Lip{loop_type}",
                display_name=f"Lip {loop_type} Loop",
                fit_type=FitType.VERTEX_LOOP_HALF,
                color=color,
                required=True,
                mirrored=True,
                has_upper_lower=True,
                description=f"Select the {loop_type.lower()} lip loop (upper half, from center to corner)",
                order=order,
                parent_region="Lip",
                shading_group=f"as{['Red', 'Green', 'Blue'][['Outer', 'Main', 'Inner'].index(loop_type)]}SG",
            )

        # === EYEBROW REGIONS ===
        cls.REGIONS["EyeBrowCenter"] = FitRegion(
            name="EyeBrowCenter",
            display_name="Eyebrow Center",
            fit_type=FitType.VERTEX,
            color=cls.COLOR_YELLOW,
            required=True,
            mirrored=False,
            description="Select the center point between eyebrows (glabella)",
            order=30,
            parent_region="EyeBrow",
        )

        cls.REGIONS["EyeBrowInner"] = FitRegion(
            name="EyeBrowInner",
            display_name="Eyebrow Inner",
            fit_type=FitType.VERTEX,
            color=cls.COLOR_YELLOW,
            required=True,
            mirrored=True,
            description="Select the inner eyebrow vertex (near nose)",
            order=31,
            parent_region="EyeBrow",
        )

        cls.REGIONS["EyeBrowOuter"] = FitRegion(
            name="EyeBrowOuter",
            display_name="Eyebrow Outer",
            fit_type=FitType.VERTEX,
            color=cls.COLOR_YELLOW,
            required=True,
            mirrored=True,
            description="Select the outer eyebrow vertex (temple side)",
            order=32,
            parent_region="EyeBrow",
        )

        for i in range(1, 4):
            cls.REGIONS[f"EyeBrowMid{i}"] = FitRegion(
                name=f"EyeBrowMid{i}",
                display_name=f"Eyebrow Mid {i}",
                fit_type=FitType.VERTEX,
                color=cls.COLOR_ORANGE,
                required=False,
                mirrored=True,
                description=f"Optional: Eyebrow control point {i}",
                order=33 + i,
                parent_region="EyeBrow",
            )

        # === NOSE REGIONS ===
        cls.REGIONS["Nose"] = FitRegion(
            name="Nose",
            display_name="Nose Tip",
            fit_type=FitType.VERTEX,
            color=cls.COLOR_CYAN,
            required=True,
            mirrored=False,
            description="Select the nose tip vertex",
            order=40,
            parent_region="Nose",
        )

        cls.REGIONS["NoseUnder"] = FitRegion(
            name="NoseUnder",
            display_name="Nose Under",
            fit_type=FitType.VERTEX,
            color=cls.COLOR_CYAN,
            required=True,
            mirrored=False,
            description="Select the center vertex under the nose (philtrum)",
            order=41,
            parent_region="Nose",
        )

        cls.REGIONS["NoseBridge"] = FitRegion(
            name="NoseBridge",
            display_name="Nose Bridge",
            fit_type=FitType.VERTEX,
            color=cls.COLOR_CYAN,
            required=True,
            mirrored=False,
            description="Select the nose bridge vertex (between eyes)",
            order=42,
            parent_region="Nose",
        )

        cls.REGIONS["NoseCorner"] = FitRegion(
            name="NoseCorner",
            display_name="Nose Corner",
            fit_type=FitType.VERTEX,
            color=cls.COLOR_CYAN,
            required=True,
            mirrored=True,
            description="Select the nose corner vertex (where nostril meets cheek)",
            order=43,
            parent_region="Nose",
        )

        cls.REGIONS["NoseSide"] = FitRegion(
            name="NoseSide",
            display_name="Nose Side",
            fit_type=FitType.VERTEX,
            color=cls.COLOR_CYAN,
            required=True,
            mirrored=True,
            description="Select the side of nose vertex",
            order=44,
            parent_region="Nose",
        )

        cls.REGIONS["Nostril"] = FitRegion(
            name="Nostril",
            display_name="Nostril",
            fit_type=FitType.VERTEX,
            color=cls.COLOR_CYAN,
            required=True,
            mirrored=True,
            description="Select the nostril vertex",
            order=45,
            parent_region="Nose",
        )

        # === JAW REGIONS ===
        cls.REGIONS["JawPivot"] = FitRegion(
            name="JawPivot",
            display_name="Jaw Pivot",
            fit_type=FitType.VERTEX,
            color=cls.COLOR_MAGENTA,
            required=True,
            mirrored=True,
            description="Select the jaw pivot point (near ear, where jaw rotates)",
            order=50,
            parent_region="Jaw",
        )

        cls.REGIONS["JawCorner"] = FitRegion(
            name="JawCorner",
            display_name="Jaw Corner",
            fit_type=FitType.VERTEX,
            color=cls.COLOR_MAGENTA,
            required=True,
            mirrored=True,
            description="Select the jaw corner vertex (angle of mandible)",
            order=51,
            parent_region="Jaw",
        )

        cls.REGIONS["JawLine"] = FitRegion(
            name="JawLine",
            display_name="Jaw Line",
            fit_type=FitType.VERTEX,
            color=cls.COLOR_MAGENTA,
            required=True,
            mirrored=True,
            description="Select vertex along jaw line between corner and chin",
            order=52,
            parent_region="Jaw",
        )

        cls.REGIONS["Jaw"] = FitRegion(
            name="Jaw",
            display_name="Chin",
            fit_type=FitType.VERTEX,
            color=cls.COLOR_MAGENTA,
            required=True,
            mirrored=False,
            description="Select the chin center vertex",
            order=53,
            parent_region="Jaw",
        )

        cls.REGIONS["ChinCrease"] = FitRegion(
            name="ChinCrease",
            display_name="Chin Crease",
            fit_type=FitType.VERTEX,
            color=cls.COLOR_MAGENTA,
            required=True,
            mirrored=False,
            description="Select the chin crease vertex (mentolabial fold)",
            order=54,
            parent_region="Jaw",
        )

        cls.REGIONS["Throat"] = FitRegion(
            name="Throat",
            display_name="Throat",
            fit_type=FitType.VERTEX,
            color=cls.COLOR_MAGENTA,
            required=True,
            mirrored=False,
            description="Select the throat/neck vertex under chin",
            order=55,
            parent_region="Jaw",
        )

        # === CHEEK REGIONS ===
        cls.REGIONS["Cheek"] = FitRegion(
            name="Cheek",
            display_name="Cheek",
            fit_type=FitType.VERTEX,
            color=cls.COLOR_ORANGE,
            required=True,
            mirrored=True,
            description="Select the cheek vertex (mid-cheek area)",
            order=60,
            parent_region="Cheek",
        )

        cls.REGIONS["CheekBone"] = FitRegion(
            name="CheekBone",
            display_name="Cheek Bone",
            fit_type=FitType.VERTEX,
            color=cls.COLOR_ORANGE,
            required=True,
            mirrored=True,
            description="Select the cheekbone/zygomatic vertex",
            order=61,
            parent_region="Cheek",
        )

        cls.REGIONS["SmileBulge"] = FitRegion(
            name="SmileBulge",
            display_name="Smile Bulge",
            fit_type=FitType.VERTEX,
            color=cls.COLOR_ORANGE,
            required=True,
            mirrored=True,
            description="Select where the smile creates a bulge (nasolabial area)",
            order=62,
            parent_region="Cheek",
        )

        cls.REGIONS["FrownBulge"] = FitRegion(
            name="FrownBulge",
            display_name="Frown Bulge",
            fit_type=FitType.VERTEX,
            color=cls.COLOR_ORANGE,
            required=True,
            mirrored=True,
            description="Select the frown/depressor area vertex",
            order=63,
            parent_region="Cheek",
        )

        # === FOREHEAD ===
        cls.REGIONS["ForeHead"] = FitRegion(
            name="ForeHead",
            display_name="Forehead",
            fit_type=FitType.VERTEX,
            color=cls.COLOR_YELLOW,
            required=True,
            mirrored=True,
            description="Select 3 vertices: side (temple), top (hairline) "
            "and nose (between eyebrows)",
            order=70,
            parent_region="ForeHead",
        )

        # === ALLINEAMENTO ALLA TABELLA $sections DELLA UI MEL (v6.661) ===
        # nome -> (shading_group, mid) per le regioni sferiche attive.
        # EyeBall e' esclusa deliberatamente: in MEL ha isSphere=1 ma
        # asCreateFaceFit devia su asBuildFitEyeBall prima del ramo sfera
        # (port in Fase 1c/1d) - qui resta sul percorso legacy.
        sphere_table = {
            "EyeBrowInner": ("asGreenSG", False),
            "EyeBrowOuter": ("asRedSG", False),
            "EyeBrowCenter": ("asBlueSG", True),
            "EyeBrowMid1": ("asRedSG", False),
            "EyeBrowMid2": ("asRedSG", False),
            "EyeBrowMid3": ("asRedSG", False),
            "JawPivot": ("asBlue2SG", False),
            "JawCorner": ("asBlue2SG", False),
            "JawLine": ("asBlue2SG", False),
            "Jaw": ("asBlue2SG", True),
            "ChinCrease": ("asBlueSG", True),
            "Throat": ("asBlue2SG", True),
            "Cheek": ("asGreenSG", False),
            "CheekBone": ("asBlue2SG", False),
            "SmileBulge": ("asBlueSG", False),
            "FrownBulge": ("asBlueSG", False),
            "Nose": ("asGreenSG", True),
            "NoseUnder": ("asBlueSG", True),
            "NoseCorner": ("asRedSG", False),
            "NoseSide": ("asBlueSG", False),
            "NoseBridge": ("asBlueSG", True),
            "Nostril": ("asBlueSG", False),
        }
        for region_name, (sg, mid) in sphere_table.items():
            region = cls.REGIONS[region_name]
            region.is_sphere = True
            region.shading_group = sg
            region.mid = mid

        cls.REGIONS["Pupil"] = FitRegion(
            name="Pupil",
            display_name="Pupil",
            fit_type=FitType.EDGE_LOOP,
            color=cls.COLOR_RED,
            required=False,
            mirrored=True,
            description="Closed edge loop around the pupil",
            order=15,
            parent_region="Eye",
            shading_group="asRedSG",
        )
        cls.REGIONS["Iris"] = FitRegion(
            name="Iris",
            display_name="Iris",
            fit_type=FitType.EDGE_LOOP,
            color=cls.COLOR_GREEN,
            required=False,
            mirrored=True,
            description="Closed edge loop around the iris",
            order=16,
            parent_region="Eye",
            shading_group="asGreenSG",
        )
        cls.REGIONS["EyeLidMain2"] = FitRegion(
            name="EyeLidMain2",
            display_name="Eye Lid Main 2",
            fit_type=FitType.VERTEX_LOOP_HALF,
            color=cls.COLOR_GREEN,
            required=False,
            mirrored=True,
            has_upper_lower=True,
            description="Secondary eyelid loop (between Main and Outer)",
            order=13,
            parent_region="EyeLid",
            shading_group="asGreenSG",
        )

        cls.REGIONS["JawCurves"] = FitRegion(
            name="JawCurves",
            display_name="Jaw Weight Curves",
            fit_type=FitType.NO_SELECTION,
            color=cls.COLOR_YELLOW,
            required=False,
            mirrored=False,
            description="Jaw weight curves built from the Jaw/Cheek/Nose/"
            "Throat, Lip Outer and EyeLid Outer fits "
            "(no selection needed)",
            order=56,
            parent_region="Jaw",
            mid=True,
        )

        cls.REGIONS["Tongue"] = FitRegion(
            name="Tongue",
            display_name="Tongue",
            fit_type=FitType.NO_SELECTION,
            color=cls.COLOR_RED,
            required=False,
            mirrored=False,
            description="Tongue fit curve with 5 locators (no selection needed)",
            order=90,
            parent_region="Tongue",
            shading_group="asBlueSG",
            mid=True,
        )

        cls.REGIONS["UpMidLo"] = FitRegion(
            name="UpMidLo",
            display_name="Up/Mid/Lo Face",
            fit_type=FitType.NO_SELECTION,
            color=cls.COLOR_GREEN,
            required=False,
            mirrored=False,
            description="Upper/middle/lower face split locators "
            "(requires JawPivot, eyelid and NoseUnder fits)",
            order=91,
            parent_region="Face",
            shading_group="asGreenSG",
            mid=True,
        )

    def __init__(self, geometry: str = "", non_symmetrical: bool = False):
        """
        Initialize the fitting manager.

        Args:
            geometry: The face mesh to fit. Vuoto = UI aperta senza mesh
                (la mesh si sceglie dopo via choose_input, parita' MEL).
            non_symmetrical: Whether face is non-symmetrical (fit both sides independently)
        """
        self._init_regions()

        self.geometry = geometry
        self.non_symmetrical = non_symmetrical
        self.fit_data: Dict[str, FitData] = {}
        self.fit_skeleton_grp = "FaceFitSkeleton"
        self.face_group = "FaceGroup"

        # Geometria opzionale: senza mesh la UI puo' aprirsi a vuoto.
        if geometry:
            if not cmds.objExists(geometry):
                raise ValueError(f"Geometry '{geometry}' does not exist")
            self.skin_cluster = self._get_skin_cluster(geometry)
        else:
            self.skin_cluster = None

        # Callbacks
        self._on_fit_complete: Optional[Callable] = None

    def _get_skin_cluster(self, geometry: str) -> Optional[str]:
        """Get skin cluster from geometry."""
        shapes = cmds.listRelatives(geometry, shapes=True, noIntermediate=True)
        if not shapes:
            return None

        history = cmds.listHistory(shapes[0], pruneDagObjects=True)
        if not history:
            return None

        skin_clusters = cmds.ls(history, type="skinCluster")
        return skin_clusters[0] if skin_clusters else None

    def create_fit_skeleton(self) -> str:
        """Crea FaceGroup e FaceFitSkeleton (parita' asCreateFaceFitSkeleton).

        Nodi transform con t/r/s lockati; nessuna shape e nessun attributo
        di mask qui: la mask arriva da create_fit_mask(), le opzioni da
        set_fit_option(). Preserva la selezione corrente.

        Returns:
            Nome del nodo FaceFitSkeleton.
        """
        selection = cmds.ls(selection=True)

        self._ensure_shaders()

        if not cmds.objExists(self.face_group):
            cmds.createNode("transform", name=self.face_group)
            _lock_main_attrs(self.face_group)
            if cmds.objExists("|Group"):
                cmds.parent(self.face_group, "|Group")

        if cmds.objExists(self.fit_skeleton_grp):
            cmds.delete(self.fit_skeleton_grp)
        cmds.createNode("transform", name=self.fit_skeleton_grp, parent=self.face_group)
        _lock_main_attrs(self.fit_skeleton_grp)

        set_fit_option("Face", self.geometry)
        set_fit_option("AllHead", self.geometry)
        set_fit_option("SkinCluster", self.skin_cluster or "")
        if self.non_symmetrical:
            self.switch_side("Right")

        if selection:
            cmds.select(selection)
        else:
            cmds.select(clear=True)
        return self.fit_skeleton_grp

    def switch_side(self, side: str) -> bool:
        """Attiva/disattiva il fitting non-symmetrical (parita' asFaceSwitchSide).

        Args:
            side: "Left", "Right" oppure "" per tornare simmetrico.

        Persiste NonSym/NonSymSide su FaceFitSkeleton e aggiorna la
        visibilita' dei figli: in modalita' Left sono visibili solo i nodi
        `*Left`; in modalita' Right e off sono visibili gli altri.

        Nota: viene chiamato anche da create_fit_skeleton (flag
        non_symmetrical del costruttore): deve restare privo di interazioni
        UI o modifiche alla selezione.
        """
        if side not in ("Left", "Right", ""):
            cmds.warning("Invalid side: {!r} (use 'Left', 'Right' or '')".format(side))
            return False
        if not cmds.objExists(self.fit_skeleton_grp):
            cmds.warning("FaceFitSkeleton not found")
            return False

        set_fit_option("NonSym", side != "")
        set_fit_option("NonSymSide", side)

        show_left = side == "Left"
        children = cmds.listRelatives(self.fit_skeleton_grp, children=True, type="transform") or []
        for child in children:
            is_left = child.endswith("Left")
            cmds.setAttr(child + ".v", 1 if is_left == show_left else 0)
        return True

    def show_both_sides(self) -> bool:
        """Mostra tutti i figli di FaceFitSkeleton (parita' asFaceShowBothSides)."""
        if not cmds.objExists(self.fit_skeleton_grp):
            cmds.warning("FaceFitSkeleton not found")
            return False
        children = cmds.listRelatives(self.fit_skeleton_grp, children=True, type="transform") or []
        for child in children:
            cmds.setAttr(child + ".v", 1)
        return True

    MASK_SHAPE_NAMES = (
        "FaceFitSkeletonShape",
        "FaceFitSkeletonHeightShape",
        "FaceFitSkeletonCircleShape",
        "FaceFitSkeletonHeightCircleShape",
    )

    def create_fit_mask(self) -> bool:
        """Crea la mask del fitting (parita' asCreateFaceFitMask).

        Dalla selezione corrente di poly-facce: 4 shape circle su
        FaceFitSkeleton scalate/posizionate sul bounding box della
        selezione, attributo faceScale, persistenza della selezione
        nell'opzione Mask. Richiede up-axis Y; forza le unita' a cm.

        Returns:
            True se la mask e' stata creata.
        """
        selection = cmds.ls(selection=True, flatten=True)

        if cmds.upAxis(query=True, axis=True) == "z":
            cmds.warning("Z-up axis detected: switch to Y-up before creating the FaceSetup mask")
            return False
        if not selection or ".f[" not in selection[0]:
            cmds.warning("No poly-faces selected: select the polygons of the character's face")
            return False
        if not cmds.objExists(self.fit_skeleton_grp):
            cmds.warning("FaceFitSkeleton not found: run create_fit_skeleton() first")
            return False
        if cmds.currentUnit(query=True, fullName=True) != "centimeter":
            cmds.warning("AdvancedSkeleton FaceSetup requires cm: switching working units")
            cmds.currentUnit(linear="cm")

        old_shapes = cmds.listRelatives(self.fit_skeleton_grp, shapes=True) or []
        if old_shapes:
            cmds.delete(old_shapes)

        for shape_name in self.MASK_SHAPE_NAMES:
            circle = cmds.circle(
                center=(0, 0, 0),
                normal=(0, 1, 0),
                sweep=360,
                radius=0.5,
                degree=3,
                sections=8,
                constructionHistory=False,
            )[0]
            shape = cmds.listRelatives(circle, shapes=True)[0]
            shape = cmds.rename(shape, shape_name)
            cmds.parent(shape, self.fit_skeleton_grp, addObject=True, shape=True)
            cmds.delete(circle)
            cmds.setAttr(shape_name + ".overrideEnabled", 1)
            cmds.setAttr(shape_name + ".overrideColor", 13)
            cmds.rotate(
                0,
                -90,
                0,
                shape_name + ".cv[0:99]",
                relative=True,
                pivot=(0, 0, 0),
                objectSpace=True,
            )
            if "Height" in shape_name:
                cmds.move(0, 1.0, 0, shape_name + ".cv[0:99]", relative=True, objectSpace=True)

        cmds.select(selection)
        bb = cmds.xform(query=True, worldSpace=True, boundingBox=True)
        for shape_name in self.MASK_SHAPE_NAMES:
            cmds.scale(
                bb[3] - bb[0],
                bb[4] - bb[1],
                bb[5] - bb[2],
                shape_name + ".cv[0:99]",
                relative=True,
                pivot=(0, 0, 0),
            )
            cmds.move(
                0,
                bb[1],
                (bb[2] + bb[5]) / 2.0,
                shape_name + ".cv[0:99]",
                relative=True,
                objectSpace=True,
                worldSpaceDistance=True,
            )

        face_scale = bb[4] - bb[1]
        if not cmds.attributeQuery("faceScale", node=self.fit_skeleton_grp, exists=True):
            cmds.addAttr(self.fit_skeleton_grp, longName="faceScale", attributeType="double")
        cmds.setAttr("{}.faceScale".format(self.fit_skeleton_grp), face_scale)

        set_fit_option("Mask", " ".join(selection))
        print("// Mask stored.")
        return True

    def _ensure_shaders(self):
        """Crea gli shader del fitting (parita' asFitModeEnsureShaders)."""
        ensure_fit_shaders()

    # sezioni MEL il cui locator viene forzato a X=0 al placement
    _X_ZERO_SECTIONS = ("Nose", "Jaw", "ChinCrease", "NoseUnder", "Throat")

    def create_face_fit(
        self,
        section: str,
        part: str = "",
        is_sphere: bool = False,
        up_and_lo: bool = False,
        main_and_outer: bool = False,
        shading_group: str = "",
    ) -> bool:
        """Crea il fit di una regione (parita' asCreateFaceFit).

        Copre: regioni sferiche con falloff, Tongue, UpMidLo e tutte le
        regioni loop (EyeLid, Lip, Pupil, Iris, *Line, EyeLidMain2).

        Args:
            section:       Sezione MEL (es. "EyeLid", "Lip", "Pupil").
            part:          Parte (es. "Main", "Outer", "Inner") o "".
            is_sphere:     True per regioni con locator+sfera di falloff.
            up_and_lo:     True per sezioni con split upper/lower
                           (EyeLid*, Lip*, EyeLidMain2).
            main_and_outer: Inerte in Fase 1c (usato dalla UI MEL per
                            generare piu' parti; non altera il singolo fit).
            shading_group: SG da applicare per Pupil/Iris/*Line.

        Il suffisso Left deriva da FaceFitSkeleton.NonSymSide (switch_side).

        Returns:
            True se il fit e' stato creato.
        """
        no_selection_sections = ("Tongue", "UpMidLo")

        left_suffix = get_left_suffix()
        # parita' MEL 26374: durante la ricorsione Lip non-symmetrical
        # si lavora sempre sul lato Left, qualunque sia NonSymSide
        if cmds.objExists("asRunningFaceLipLeft"):
            left_suffix = "Left"
        fit_name = "FaceFit{}{}{}".format(section, part, left_suffix)

        if cmds.objExists(fit_name):
            cmds.warning("{} Already Exists".format(fit_name))
            return False
        if not cmds.objExists(self.fit_skeleton_grp):
            cmds.warning("FaceFitSkeleton not found: run create_fit_skeleton() first")
            return False
        if not cmds.attributeQuery("faceScale", node=self.fit_skeleton_grp, exists=True):
            cmds.warning("Mask not defined. Create the fit mask first (create_fit_mask)")
            return False
        scale = cmds.getAttr("{}.faceScale".format(self.fit_skeleton_grp))

        # parita' MEL (26386): la sezione EyeBall devia su asBuildFitEyeBall
        if section == "EyeBall":
            return self.build_fit_eyeball()

        if section == "UpMidLo" and get_fit_option("RigType") == "BlendShapes":
            cmds.warning('Rig-type "BlendShapes" does not work with UpMidLo')
            return False

        if section in no_selection_sections:
            selection = []
            cmds.select(clear=True)
        else:
            selection = cmds.ls(selection=True, flatten=True) or []

        edge_sel = any(".e[" in comp for comp in selection)
        vtx_sel = any(".vtx[" in comp for comp in selection)
        face_sel = any(".f[" in comp for comp in selection)
        if section not in no_selection_sections and not (edge_sel or vtx_sel or face_sel):
            cmds.warning("No edge or vertex selected")
            return False

        self._ensure_shaders()

        template_loc = cmds.spaceLocator(name="templateLoc")[0]
        template_shape = cmds.listRelatives(template_loc, shapes=True)[0]
        cmds.setAttr(
            template_shape + ".localScale",
            0.035 * scale,
            0.035 * scale,
            0.035 * scale,
            type="float3",
        )
        cmds.setAttr(template_shape + ".overrideEnabled", 1)
        cmds.setAttr(template_shape + ".overrideColor", 17)

        cmds.createNode("transform", name=fit_name, parent=self.fit_skeleton_grp)
        for sub in ("Geo", "Curve", "Loc"):
            cmds.createNode(
                "transform",
                name="FaceFit{}{}{}{}".format(section, part, sub, left_suffix),
                parent=fit_name,
            )

        if is_sphere:
            loc = cmds.duplicate(template_loc, name=section + left_suffix)[0]
            cmds.parent(loc, "FaceFit{}{}Loc{}".format(section, part, left_suffix))
            sphere = cmds.sphere(
                name="{}Sphere{}".format(section, left_suffix),
                pivot=(0, 0, 0),
                axis=(0, 1, 0),
                startSweep=0,
                endSweep=360,
                radius=0.02 * scale,
                degree=3,
                useTolerance=False,
                tolerance=0.01,
                sections=8,
                spans=4,
                constructionHistory=False,
            )[0]
            cmds.parent(sphere, "FaceFit{}{}Geo{}".format(section, part, left_suffix))
            for channel in ("t", "r", "s"):
                cmds.connectAttr("{}.{}".format(loc, channel), "{}.{}".format(sphere, channel))
            sphere_shape = cmds.listRelatives(sphere, shapes=True)[0]
            cmds.setAttr(sphere_shape + ".overrideEnabled", 1)
            cmds.setAttr(sphere_shape + ".overrideDisplayType", 2)
            cmds.addAttr(
                loc,
                longName="falloffRadius",
                attributeType="double",
                minValue=0,
                defaultValue=1,
                keyable=True,
            )
            cmds.addAttr(
                loc,
                longName="falloffMode",
                attributeType="enum",
                enumName="volume:surface",
                defaultValue=1,
                keyable=True,
            )

        if section == "Tongue":
            if not self._create_tongue_fit(template_loc, scale):
                cmds.delete(template_loc)
                cmds.delete(fit_name)
                return False
        if section == "UpMidLo":
            if not self._create_upmidlo_fit(template_loc, scale):
                cmds.delete(template_loc)
                cmds.delete(fit_name)
                return False

        cmds.delete(template_loc)

        if edge_sel or vtx_sel or face_sel:
            cmds.addAttr(fit_name, longName="selection", dataType="string")
            cmds.setAttr("{}.selection".format(fit_name), " ".join(selection) + " ", type="string")

        if not edge_sel and not vtx_sel:
            return True

        # placement del landmark sferico: come nel loop MEL, l'ultimo
        # componente corrispondente della selezione determina la posizione
        if is_sphere:
            pos = None
            for comp in selection:
                if not vtx_sel and ".e[" in comp:
                    cmds.select(comp)
                    cmds.ConvertSelectionToVertices()
                    converted = cmds.ls(selection=True, flatten=True)
                    if converted:
                        pos = cmds.xform(
                            converted[0], query=True, worldSpace=True, translation=True
                        )
                if vtx_sel and ".vtx[" in comp:
                    pos = cmds.xform(comp, query=True, worldSpace=True, translation=True)
            if pos is None:
                cmds.warning(
                    "Could not derive a position from the "
                    "selection: move the {} locator manually".format(loc)
                )
                cmds.select(clear=True)
                return True
            if section in self._X_ZERO_SECTIONS:
                pos[0] = 0.0
            cmds.xform(loc, worldSpace=True, translation=pos)
            if shading_group and cmds.objExists(shading_group):
                cmds.sets(sphere, edit=True, forceElement=shading_group)
            cmds.select(clear=True)

        # --- Ramo loop: EyeLid, Lip, Pupil, Iris, *Line, EyeLidMain2,
        #     ForeHead (percorso speciale da 3 vertici) ---
        if not is_sphere:
            if section == "ForeHead":
                # il bordo costruito dai 4 percorsi diventa la selezione
                # usata dall'AreaMesh (il MEL riassegna $sel)
                area_selection = self._create_forehead_fit(part, left_suffix, selection, scale)
                if area_selection is None:
                    cmds.delete(fit_name)
                    return False
            else:
                if not self._create_loop_fit(
                    section,
                    part,
                    left_suffix,
                    selection,
                    scale,
                    up_and_lo,
                    main_and_outer,
                    shading_group,
                ):
                    cmds.delete(fit_name)
                    return False
                area_selection = selection

            # parita' MEL (27392): mesh di area per ForeHead e per gli
            # anelli Inner di EyeLid/Lip
            if (
                section == "ForeHead"
                or (section == "EyeLid" and part == "Inner")
                or (section == "Lip" and part == "Inner")
            ):
                if not self._create_area_mesh(section, part, left_suffix, area_selection, scale):
                    cmds.delete(fit_name)
                    return False

        # parita' MEL 27459: in modalita' non-symmetrical il fit Lip del
        # lato corrente innesca l'auto-fit del lato Left via ricorsione
        if (
            section == "Lip"
            and get_fit_option("NonSym")
            and not cmds.objExists("asRunningFaceLipLeft")
        ):
            if not self._run_lip_left_recursion(part, up_and_lo, main_and_outer, shading_group):
                return False

        # parita' MEL 27524: chiusura della ricorsione (gira nel ramo
        # interno, dove il nodo temporaneo esiste ancora): cleanup del
        # flag + verifica del match dei CV destra/sinistra
        if section == "Lip" and cmds.objExists("asRunningFaceLipLeft"):
            if not self._finish_lip_left_recursion(part, selection):
                return False

        print("// Fitted FaceFit{}{}{}".format(section, part, left_suffix))
        return True

    def _run_lip_left_recursion(self, part, up_and_lo, main_and_outer, shading_group) -> bool:
        """Prepara e lancia l'auto-fit del Lip lato Left (parita'
        asCreateFaceFit, righe MEL 27459-27523).

        Dalle curve destre appena costruite ricava i due vertici di
        mezzeria (closest di upperLip<part>Curve.cv[0] e
        lowerLip<part>Curve.cv[0]) e stima il corner sinistro
        percorrendo il loop labbra per nr passi di grow (nr = spans
        della curva upper destra), cosi' che il lato Left abbia lo
        stesso numero di CV. I tre vertici vengono persistiti sul nodo
        temporaneo asRunningFaceLipLeft (startVtx/endVtx/
        righLowerStartVtx) e asCreateFaceFit viene richiamata: il nodo
        forza il suffisso Left e guida start/end e filtro del ramo 2.
        """
        upper_curve = "upperLip{}Curve".format(part)
        lower_curve = "lowerLip{}Curve".format(part)
        if not cmds.objExists(upper_curve) or not cmds.objExists(lower_curve):
            cmds.warning(
                "Lip left auto-fit requires the right-side curves ({}/{})".format(
                    upper_curve, lower_curve
                )
            )
            return False

        if cmds.objExists("closestSampler"):
            cmds.delete("closestSampler")
        sampler = cmds.createNode("closestPointOnMesh", name="closestSampler")
        cmds.connectAttr(self.geometry + ".outMesh", sampler + ".inMesh")

        def _closest_vtx(curve_cv):
            pos = cmds.xform(curve_cv, query=True, worldSpace=True, translation=True)
            cmds.setAttr(sampler + ".inPosition", pos[0], pos[1], pos[2], type="float3")
            return "{}.vtx[{}]".format(
                self.geometry, cmds.getAttr(sampler + ".result.closestVertexIndex")
            )

        center_upper = _closest_vtx(upper_curve + ".cv[0]")
        # (il MEL campiona anche cv[1], ma il valore viene subito
        # sovrascritto dal closest di lowerLip<part>Curve.cv[0])
        righ_lower_start_vtx = _closest_vtx(lower_curve + ".cv[0]")
        cmds.delete(sampler)

        # selezione per il lato Left: gli edge salvati + i 2 vtx centrali
        face_fit_reselect("Lip", part)
        cmds.select(self.geometry + ".vtx[0:999999]", deselect=True)
        cmds.select([center_upper, righ_lower_start_vtx], add=True)
        left_lip_selection = cmds.ls(selection=True)

        nr = cmds.getAttr(upper_curve + ".spans")

        # vtx del loop NON coperti dalle curve destre = meta' sinistra
        resampled = get_face_fit_selection("FaceFitLip{}Curve".format(part)).split()
        face_fit_reselect("Lip", part)
        cmds.ConvertSelectionToVertices()
        lip_vtxs = cmds.ls(selection=True, flatten=True) or []
        # inversione esplicita (asInvertSelection richiede la UI)
        cmds.select(self.geometry + ".vtx[*]")
        cmds.select(lip_vtxs, deselect=True)
        non_lip_vtxs = cmds.ls(selection=True)
        face_fit_reselect("Lip", part)
        cmds.ConvertSelectionToVertices()
        if resampled:
            cmds.select(resampled, deselect=True)
        left_side_vtxs = cmds.ls(selection=True, flatten=True) or []

        # corner sinistro = vertice del loop a distanza topologica nr
        # dal centro (stesso CV count del lato destro)
        cmds.select(center_upper)
        for _ in range(nr - 1):
            cmds.polySelectConstraint(propagate=1, type=0x0001)
            cmds.select(non_lip_vtxs, deselect=True)
        grown = cmds.ls(selection=True, flatten=True) or []
        cmds.polySelectConstraint(propagate=1, type=0x0001)
        grown_plus = cmds.ls(selection=True, flatten=True) or []
        left_corner = None
        for v in grown_plus:
            if v not in left_side_vtxs:
                continue
            if v in grown:
                continue
            left_corner = v
        if left_corner is None:
            cmds.warning("Could not locate the left lip corner for the non-symmetrical auto-fit")
            return False

        flag = cmds.createNode("transform", name="asRunningFaceLipLeft")
        for attr in ("startVtx", "endVtx", "righLowerStartVtx"):
            cmds.addAttr(flag, longName=attr, dataType="string")
        cmds.setAttr(flag + ".startVtx", center_upper, type="string")
        cmds.setAttr(flag + ".endVtx", left_corner, type="string")
        cmds.setAttr(flag + ".righLowerStartVtx", righ_lower_start_vtx, type="string")

        cmds.select([left_corner] + left_lip_selection)
        success = self.create_face_fit(
            "Lip",
            part=part,
            up_and_lo=up_and_lo,
            main_and_outer=main_and_outer,
            shading_group=shading_group,
        )
        if cmds.objExists("asRunningFaceLipLeft"):
            cmds.delete("asRunningFaceLipLeft")
        return success

    def _finish_lip_left_recursion(self, part, selection) -> bool:
        """Chiusura della ricorsione Lip Left (parita' asCreateFaceFit,
        righe MEL 27524-27547): elimina il nodo temporaneo e verifica
        che destra e sinistra abbiano lo stesso numero di CV; in caso
        contrario cancella entrambi i fit e riseleziona solo gli edge
        originali, lasciando l'utente nelle condizioni di rifare il fit.
        """
        cmds.delete("asRunningFaceLipLeft")
        upper_r = cmds.getAttr("upperLip{}Curve.spans".format(part))
        upper_l = cmds.getAttr("upperLip{}CurveLeft.spans".format(part))
        lower_r = cmds.getAttr("lowerLip{}Curve.spans".format(part))
        lower_l = cmds.getAttr("lowerLip{}CurveLeft.spans".format(part))
        if upper_r == upper_l and lower_r == lower_l:
            return True

        face_fit_reselect("Lip", part)
        cmds.delete("FaceFitLip" + part, "FaceFitLip" + part + "Left")
        edges = [c for c in selection if ".e[" in c]
        if edges:
            cmds.select(edges)
        else:
            cmds.select(clear=True)
        cmds.warning(
            "Number of CV's of the Left and Right side is not "
            "matching. upperRight={} upperLeft={} lowerRight={} "
            "lowerLeft={}".format(upper_r, upper_l, lower_r, lower_l)
        )
        return False

    def update_fit_face(self) -> bool:
        """Migrazione dei fit legacy (parita' asFaceUpdateFitFace,
        righe MEL 27753-27790).

        Blocco v5.351->5.352 (solo se FaceGroup.version < 5.352):
        rimuove FaceFitEyeBrowOuter quando esiste la vecchia
        EyeBrowOuterCurve, FaceFitEyeBrowMain e FaceFitAnimateFit;
        ricrea EyeLidInner e LipInner dalle selezioni salvate (il
        formato delle curve Inner e' cambiato in 5.352). Blocco v5.355:
        le regioni con il nome lowercase (cheek/line/cheekRaiser/
        noseCorner) vengono ricreate come sfere con il nome attuale.

        La migrazione ben piu' invasiva dei fit <= 5.743
        (asFaceUpgradeFaceFitCheck) dipende dal teardown del build
        (asDeleteAdvancedFace) ed e' rinviata alla Fase 2.
        """
        # v5.351 -> v5.352
        if (
            cmds.objExists("FaceGroup")
            and cmds.attributeQuery("version", node="FaceGroup", exists=True)
            and cmds.getAttr("FaceGroup.version") < 5.352
            and _AS_SCRIPT_VERSION >= 5.352
        ):
            if cmds.objExists("FaceFitEyeBrowOuter") and cmds.objExists("EyeBrowOuterCurve"):
                cmds.delete("FaceFitEyeBrowOuter")
            if cmds.objExists("FaceFitEyeBrowMain"):
                cmds.delete("FaceFitEyeBrowMain")
            if cmds.objExists("FaceFitEyeLidInner"):
                face_fit_reselect("EyeLid", "Inner")
                cmds.delete("FaceFitEyeLidInner")
                self.create_face_fit(
                    "EyeLid",
                    part="Inner",
                    up_and_lo=True,
                    main_and_outer=True,
                    shading_group="asGreenSG",
                )
            if cmds.objExists("FaceFitLipInner"):
                face_fit_reselect("Lip", "Inner")
                cmds.delete("FaceFitLipInner")
                self.create_face_fit(
                    "Lip",
                    part="Inner",
                    up_and_lo=True,
                    main_and_outer=True,
                    shading_group="asGreenSG",
                )
            if cmds.objExists("FaceFitAnimateFit"):
                cmds.delete("FaceFitAnimateFit")

        # v5.354 -> v5.355: rinomina delle regioni lowercase
        if _AS_SCRIPT_VERSION >= 5.355:
            renames = (
                ("cheek", "Cheek"),
                ("line", "Line"),
                ("cheekRaiser", "CheekRaiser"),
                ("noseCorner", "NoseCorner"),
            )
            for old_name, new_name in renames:
                if not cmds.objExists("FaceFit" + old_name):
                    continue
                face_fit_reselect(old_name, "")
                cmds.delete("FaceFit" + old_name)
                self.create_face_fit(new_name, is_sphere=True, shading_group="asGreenSG")
        cmds.select(clear=True)
        return True

    def create_fit_joint(self, name: str, radius: float, color: int) -> Optional[str]:
        """Joint singolo del workflow FaceFitFromSoftMods (parita'
        asFaceCreateFitJoint, righe MEL 42479-42504).

        Crea il joint sotto FaceFitFromSoftMods (a sua volta sotto
        FaceFitSkeleton) con attr falloffRadius/falloffMode/
        interpolation; default surface+smooth, tranne i nomi
        upper/lowerEye* e upper/lowerLip* (volume+none) e *Sculpt*
        (volume forzato).
        """
        if cmds.objExists(name):
            cmds.warning("{} Already Exists".format(name))
            return None
        if not cmds.objExists("FaceFitFromSoftMods"):
            cmds.createNode("transform", name="FaceFitFromSoftMods", parent=self.fit_skeleton_grp)
        cmds.select("FaceFitFromSoftMods")
        joint = cmds.joint(name=name)
        cmds.setAttr(joint + ".overrideEnabled", 1)
        cmds.setAttr(joint + ".overrideColor", color)
        cmds.addAttr(
            joint,
            longName="falloffRadius",
            attributeType="double",
            minValue=0,
            defaultValue=radius,
            keyable=True,
        )
        cmds.addAttr(
            joint,
            longName="falloffMode",
            attributeType="enum",
            enumName="volume:surface:",
            keyable=True,
        )
        cmds.addAttr(
            joint,
            longName="interpolation",
            attributeType="enum",
            enumName="none:linear:smooth:spline:",
            keyable=True,
        )
        is_eye_lip = any(
            name.startswith(prefix) for prefix in ("lowerEye", "upperEye", "lowerLip", "upperLip")
        )
        if not is_eye_lip:
            cmds.setAttr(joint + ".falloffMode", 1)
            cmds.setAttr(joint + ".interpolation", 2)
        if "Sculpt" in name:
            cmds.setAttr(joint + ".falloffMode", 0)
        return joint

    def create_face_fit_joints(self, region: str, size: float, color: int) -> bool:
        """Fit joint dalla selezione di vertici (parita'
        asCreateFaceFitJoint, righe MEL 42423-42460, senza i refresh
        UI/repeatLast).

        Un joint per vertice selezionato: nome <region> con un solo
        vertice, <region><N> (dal primo numero libero) con piu'
        vertici. Le regioni di mezzeria richiedono il primo vertice a
        X=0 (tolleranza 0.001). Le catene eyeBrow<N> propagano il
        falloffRadius alla creazione (asAutoEyeBrowFalloff).
        """
        sel = cmds.ls(selection=True, flatten=True) or []
        if not sel:
            cmds.warning("No vertices selected for {}".format(region))
            return False
        pos = cmds.xform(sel[0], query=True, worldSpace=True, translation=True)
        center_error_margin = 0.001
        is_mid = region in (
            "mouthUpper",
            "mouthLower",
            "eyeBrow0",
            "noseTip",
            "noseLower",
        ) or region.endswith("Middle")
        if is_mid and abs(pos[0]) > center_error_margin:
            cmds.warning("{} needs to be in the center, currently: {}".format(region, pos[0]))
            return False

        joint_number = 1
        for i in range(1, 99):
            joint_number = i
            if not cmds.objExists("{}{}".format(region, i)):
                break
        for component in sel:
            joint_name = region
            if len(sel) > 1:
                joint_name = "{}{}".format(region, joint_number)
            joint_number += 1
            joint = self.create_fit_joint(joint_name, size, color)
            if joint is None:
                return False
            pos = cmds.xform(component, query=True, worldSpace=True, translation=True)
            cmds.xform(joint, worldSpace=True, translation=pos)

        cmds.select(sel)
        if region.startswith("eyeBrow") and len(region) == 8 and region[7].isdigit():
            self._auto_eyebrow_falloff(region)
        return True

    def _auto_eyebrow_falloff(self, region: str):
        """Propaga il falloffRadius lungo la catena eyeBrow<N> (parita'
        asAutoEyeBrowFalloff, righe MEL 42462-42477): il raggio e' la
        distanza dal joint precedente, che viene allargato se serve
        (eyeBrow0 sempre)."""
        nr = int(region[7])
        previous = "eyeBrow{}".format(nr - 1)
        if not cmds.objExists(previous):
            return
        pos_a = cmds.xform(region, query=True, worldSpace=True, translation=True)
        pos_b = cmds.xform(previous, query=True, worldSpace=True, translation=True)
        mag = sum((a - b) ** 2 for a, b in zip(pos_a, pos_b)) ** 0.5
        cmds.setAttr(region + ".falloffRadius", mag)
        previous_rad = cmds.getAttr(previous + ".falloffRadius")
        if mag > previous_rad or previous == "eyeBrow0":
            cmds.setAttr(previous + ".falloffRadius", mag)

    def face_assist(self, section: str) -> bool:
        """SoftMod temporanei di assistenza alla selezione (parita'
        asFaceAssist, righe MEL 26295-26352).

        Gonfia labbra o palpebre con due softMod (upper/lower) centrati
        sulla curva Main gia' fittata (Outer per Lip; cv mediano, o
        cv[0] per Lip), raggio dalla distanza X centro-corner e
        spostamento (0, +/-faceScale/30, faceScale/10). In modalita'
        Left le posizioni vengono specchiate in X (le curve lette sono
        quelle di destra). Una seconda chiamata rimuove l'assist.
        """
        part = "Outer" if section == "Lip" else "Main"
        left_suffix = get_left_suffix()

        if cmds.objExists("upperTempSoftModHandle"):
            cmds.delete("upperTempSoftModHandle")
            if cmds.objExists("lowerTempSoftModHandle"):
                cmds.delete("lowerTempSoftModHandle")
            print("// assist removed.")
            return True

        if not cmds.attributeQuery("faceScale", node=self.fit_skeleton_grp, exists=True):
            cmds.warning("Mask not defined. Create the fit mask first (create_fit_mask)")
            return False
        scale = cmds.getAttr("{}.faceScale".format(self.fit_skeleton_grp))
        for upper_lower in ("upper", "lower"):
            if not cmds.objExists("{}{}{}Curve".format(upper_lower, section, part)):
                cmds.warning(
                    "face_assist requires the {}{}{}Curve fit first".format(
                        upper_lower, section, part
                    )
                )
                return False

        sel = cmds.ls(selection=True) or []
        for factor, upper_lower in ((1, "upper"), (-1, "lower")):
            curve = "{}{}{}Curve".format(upper_lower, section, part)
            num_cvs = cmds.getAttr(curve + ".spans") + cmds.getAttr(curve + ".degree")
            middle_cv = int((num_cvs - 1) / 2)
            pos_a = cmds.xform(
                "{}.cv[{}]".format(curve, middle_cv), query=True, worldSpace=True, translation=True
            )
            if section == "Lip":
                pos_a = cmds.xform(curve + ".cv[0]", query=True, worldSpace=True, translation=True)
            pos_b = cmds.xform(
                "{}.cv[{}]".format(curve, num_cvs - 1),
                query=True,
                worldSpace=True,
                translation=True,
            )
            if left_suffix == "Left":
                pos_a[0] *= -1
                pos_b[0] *= -1

            cmds.select(self.geometry, replace=True)
            mod, handle = _as_deformer("softMod")[:2]
            mod = cmds.rename(mod, upper_lower + "TempSoftMod")
            handle = cmds.rename(handle, upper_lower + "TempSoftModHandle")
            cmds.setAttr(handle + "Shape.origin", pos_a[0], pos_a[1], pos_a[2], type="float3")
            cmds.setAttr(mod + ".falloffCenter", pos_a[0], pos_a[1], pos_a[2])
            cmds.xform(handle, pivots=pos_a)
            cmds.setAttr(mod + ".falloffMode", 1)
            cmds.setAttr(mod + ".falloffRadius", abs(pos_a[0] - pos_b[0]))
            cmds.move(0, scale / 30.0 * factor, scale / 10.0, handle, relative=True)
            cmds.setAttr(mod + ".falloffCurve[3].falloffCurve_FloatValue", 1)
            cmds.setAttr(mod + ".falloffCurve[3].falloffCurve_Position", 0.5)
            cmds.setAttr(mod + ".falloffCurve[3].falloffCurve_Interp", 2)

        if sel:
            cmds.select(sel)
        else:
            cmds.select(clear=True)
        print("// assist added.")
        return True

    def fit_jaw_curves(self) -> bool:
        """Crea le curve di peso della mandibola (parita'
        asFaceFitJawCurves, righe MEL 26089-26184).

        FaceFitJawCurves sotto FaceFitSkeleton con 4 curve costruite dai
        landmark sferici e offsettate sulla superficie della Face di
        faceScale/150 (asCurveOffsetMesh):
          - JawCurve (gialla, 14): JawPivot->JawCorner->Jaw, rebuild a 3
            spans con cv ritoccati su JawPivot/Cheek/Jaw;
          - JawCurveMid (13): JawPivot->Cheek->corner del LipOuter;
          - JawCurveTop (6): JawPivot->blend->CheekBone->NoseCorner->
            mezzeria sotto il naso;
          - JawCurveBottom (6): JawPivot->sotto cv[1]->sotto il mento->
            Throat.

        E' uno step di fitting (curve editabili pre-build); il build le
        ricrea solo se assenti (MEL 34733).
        """
        required = (
            "JawPivot",
            "JawCorner",
            "Jaw",
            "Cheek",
            "CheekBone",
            "NoseCorner",
            "NoseUnder",
            "Throat",
            "upperLipOuterCurve",
            "lowerEyeLidOuterCurve",
        )
        for node in required:
            if not cmds.objExists(node):
                cmds.warning(
                    "fit_jaw_curves requires {}: complete the "
                    "Jaw/Cheek/Nose/Throat, Lip Outer and EyeLid "
                    "Outer fits first".format(node)
                )
                return False
        if cmds.objExists("FaceFitJawCurves"):
            cmds.warning("FaceFitJawCurves Already Exists")
            return False
        if not cmds.attributeQuery("faceScale", node=self.fit_skeleton_grp, exists=True):
            cmds.warning("Mask not defined. Create the fit mask first (create_fit_mask)")
            return False
        scale = cmds.getAttr("{}.faceScale".format(self.fit_skeleton_grp))

        cmds.createNode("transform", name="FaceFitJawCurves", parent=self.fit_skeleton_grp)

        def _pos(node):
            return cmds.xform(node, query=True, worldSpace=True, translation=True)

        def _make_curve(name, points, color):
            curve = cmds.curve(degree=1, point=points)
            cmds.rename(cmds.listRelatives(curve, shapes=True)[0], name + "Shape")
            cmds.rename(curve, name)
            cmds.setAttr(name + "Shape.overrideEnabled", 1)
            cmds.setAttr(name + "Shape.overrideColor", color)
            return name

        # JawCurve: pivot -> angolo mandibola -> mento
        _make_curve("JawCurve", [_pos("JawPivot"), _pos("JawCorner"), _pos("Jaw")], 14)
        cmds.rebuildCurve(
            "JawCurve",
            constructionHistory=0,
            replaceOriginal=1,
            rebuildType=0,
            endKnots=1,
            keepRange=0,
            keepControlPoints=0,
            keepEndPoints=1,
            keepTangents=0,
            spans=3,
            degree=3,
            tolerance=0.01,
        )
        pos_a = _pos("JawPivot")
        pos_b = cmds.xform("JawCurve.cv[1]", query=True, worldSpace=True, translation=True)
        cmds.xform("JawCurve.cv[1]", worldSpace=True, translation=(pos_a[0], pos_b[1], pos_a[2]))
        pos_a = _pos("Cheek")
        pos_b = cmds.xform("JawCurve.cv[3]", query=True, worldSpace=True, translation=True)
        cmds.xform("JawCurve.cv[3]", worldSpace=True, translation=(pos_a[0], pos_b[1], pos_a[2]))
        pos_a = _pos("Jaw")
        pos_b = cmds.xform("JawCurve.cv[4]", query=True, worldSpace=True, translation=True)
        cmds.xform("JawCurve.cv[4]", worldSpace=True, translation=(pos_b[0], pos_b[1], pos_a[2]))
        _curve_offset_mesh("JawCurve", self.geometry, scale / 150.0)

        # JawCurveMid: pivot -> guancia -> corner labbra (cv[spans+1]
        # clampa all'ultimo CV - idioma MEL)
        num_up = cmds.getAttr("upperLipOuterCurve.spans") + 1
        corner = cmds.xform(
            "upperLipOuterCurve.cv[{}]".format(num_up),
            query=True,
            worldSpace=True,
            translation=True,
        )
        _make_curve("JawCurveMid", [_pos("JawPivot"), _pos("Cheek"), corner], 13)
        cmds.rebuildCurve(
            "JawCurveMid",
            constructionHistory=0,
            replaceOriginal=1,
            rebuildType=0,
            endKnots=1,
            keepRange=0,
            keepControlPoints=0,
            keepEndPoints=1,
            keepTangents=0,
            spans=2,
            degree=3,
            tolerance=0.01,
        )
        _curve_offset_mesh("JawCurveMid", self.geometry, scale / 150.0)

        # JawCurveTop: pivot -> blend pivot/guancia -> zigomo -> angolo
        # naso -> mezzeria sotto il naso
        pos_a = _pos("JawPivot")
        pos_c = _pos("Cheek")
        pos_d = _pos("CheekBone")
        nose_corner = _pos("NoseCorner")
        nose_under = _pos("NoseUnder")
        _make_curve(
            "JawCurveTop",
            [
                pos_a,
                (
                    (pos_a[0] + pos_c[0]) / 2.0,
                    (pos_a[1] + pos_d[1]) / 2.0,
                    (pos_a[2] + pos_c[2]) / 2.0,
                ),
                pos_d,
                nose_corner,
                (0.0, nose_under[1], nose_under[2]),
            ],
            6,
        )
        _curve_offset_mesh("JawCurveTop", self.geometry, scale / 150.0)

        # JawCurveBottom: pivot -> sotto cv[1] -> sotto il mento -> gola
        cv1 = cmds.xform("JawCurve.cv[1]", query=True, worldSpace=True, translation=True)
        jaw_pos = _pos("Jaw")
        pivot_pos = _pos("JawPivot")
        _make_curve(
            "JawCurveBottom",
            [
                pivot_pos,
                (cv1[0], cv1[1], cv1[2] - scale / 20.0),
                (pivot_pos[0], jaw_pos[1], cv1[2] - scale / 20.0),
                _pos("Throat"),
            ],
            6,
        )
        _curve_offset_mesh("JawCurveBottom", self.geometry, scale / 150.0)

        cmds.parent("JawCurve", "JawCurveMid", "JawCurveTop", "JawCurveBottom", "FaceFitJawCurves")
        cmds.select(clear=True)
        print("// Fitted FaceFitJawCurves")
        return True

    def _create_forehead_fit(self, part, left_suffix, selection, scale):
        """Fit ForeHead da 3 vertici (parita' asCreateFaceFit,
        righe MEL 26912-27143).

        L'utente seleziona side, top e nose; la curva ForeHeadCurve
        nasce dall'unione di 4 percorsi di edge (asSelectLeastEdgesPath):
        lidInner->nose, nose->top, top->side, side->lidOuter, con i
        corner palpebrali campionati da upperEyeLidOuterCurve
        cv[0]/cv[99]. Gli edge presenti in piu' percorsi (deviazioni)
        vengono rimossi da entrambi. La curva e' costruita per-edge con
        duplicateCurve + attachCurve + rebuildCurve (replica del runtime
        command DuplicateCurve, che in MEL esegue duplicateCurve per
        singolo item), poi orientata: se il corner interno cade a
        parametro > 2 la curva viene invertita.

        Nota parita': directionChecked viene aggiunto SEMPRE (il MEL lo
        aggiunge solo quando inverte, e asFacePrep ricostruisce il fit
        a ogni build quando manca - bug MEL). Il workflow alternativo
        ForeHeadFromEdges (bordo edge manuale + 3 vtx) e' rinviato.

        Returns:
            La selezione bordo (lista edge) da passare all'AreaMesh,
            oppure None su errore (il chiamante cancella fit_name).
        """
        fit_name = "FaceFitForeHead{}{}".format(part, left_suffix)
        eyelid_curve = "upperEyeLidOuterCurve" + left_suffix

        if any(".e[" in c for c in selection):
            cmds.warning(
                "ForeHead from edges (ForeHeadFromEdges) is not "
                "ported yet: select only the 3 vertices "
                "(side, top, nose)"
            )
            return None
        three_vtxs = [c for c in selection if ".vtx[" in c]
        if len(three_vtxs) != 3:
            cmds.warning(
                "ForeHead requires exactly 3 vertices (side, top, nose), got {}".format(
                    len(three_vtxs)
                )
            )
            return None
        if not cmds.objExists(eyelid_curve):
            cmds.warning(
                "ForeHead requires the EyeLid Outer fit first ({} not found)".format(eyelid_curve)
            )
            return None

        comp_nrs, pos_xs, pos_ys = [], [], []
        for v in three_vtxs:
            comp_nrs.append(int(v.split("[")[1].rstrip("]")))
            pos = cmds.xform(v, query=True, worldSpace=True, translation=True)
            pos_xs.append(pos[0])
            pos_ys.append(pos[1])

        # side: estremo X del lato corrente. Parita' MEL: la soglia parte
        # da 0, quindi il vertice side deve stare oltre la mezzeria
        side_nr = None
        threshold = 0.0
        for i in range(3):
            if left_suffix == "" and pos_xs[i] < threshold:
                side_nr = comp_nrs[i]
                threshold = pos_xs[i]
            if left_suffix == "Left" and pos_xs[i] > threshold:
                side_nr = comp_nrs[i]
                threshold = pos_xs[i]
        # top: Y massima tra i restanti (soglia 0 come nel MEL)
        top_nr = None
        max_y = 0.0
        for i in range(3):
            if comp_nrs[i] == side_nr:
                continue
            if pos_ys[i] > max_y:
                top_nr = comp_nrs[i]
                max_y = pos_ys[i]
        # nose: il rimanente
        nose_nr = None
        for i in range(3):
            if comp_nrs[i] not in (side_nr, top_nr):
                nose_nr = comp_nrs[i]
        if side_nr is None or top_nr is None or nose_nr is None:
            cmds.warning(
                "Could not classify the 3 ForeHead vertices "
                "(side must be past the midline, top above 0)"
            )
            return None

        # corner palpebrali dal closest sulla Face
        if cmds.objExists("closestSampler"):
            cmds.delete("closestSampler")
        sampler = cmds.createNode("closestPointOnMesh", name="closestSampler")
        cmds.connectAttr(self.geometry + ".outMesh", sampler + ".inMesh")

        def _closest_vtx(pos):
            cmds.setAttr(sampler + ".inPosition", pos[0], pos[1], pos[2], type="float3")
            return cmds.getAttr(sampler + ".result.closestVertexIndex")

        spans = cmds.getAttr(eyelid_curve + ".spans")
        lid_inner_nr = _closest_vtx(
            cmds.xform(eyelid_curve + ".cv[0]", query=True, worldSpace=True, translation=True)
        )
        lid_outer_nr = _closest_vtx(
            cmds.xform(
                eyelid_curve + ".cv[{}]".format(spans),
                query=True,
                worldSpace=True,
                translation=True,
            )
        )

        # 4 percorsi di edge tra i landmark
        segments = []
        for seg_start, seg_end in (
            (lid_inner_nr, nose_nr),
            (nose_nr, top_nr),
            (top_nr, side_nr),
            (side_nr, lid_outer_nr),
        ):
            _select_least_edges_path(self.geometry, seg_start, seg_end)
            edges = cmds.ls(selection=True, flatten=True) or []
            if not edges:
                cmds.delete(sampler)
                cmds.warning(
                    "Unable to determine ForeHead area, try a "
                    "different vertex selection (no edge path "
                    "{} -> {})".format(seg_start, seg_end)
                )
                return None
            segments.append(edges)
        cmds.delete(sampler)

        # edge presenti in piu' percorsi = deviazioni superflue: via da
        # entrambi (4/3/2-way check del MEL)
        for a in range(len(segments)):
            for b in range(a + 1, len(segments)):
                common = set(segments[a]) & set(segments[b])
                if common:
                    segments[a] = [e for e in segments[a] if e not in common]
                    segments[b] = [e for e in segments[b] if e not in common]

        border = []
        for seg in segments:
            border.extend(seg)
        if not border:
            cmds.warning("ForeHead border is empty after removing overlapping edge paths")
            return None
        cmds.select(border)
        border = cmds.ls(selection=True, flatten=True) or []

        # curva dal bordo: una curva 2-CV per edge (come il runtime
        # DuplicateCurve), attach in faceLoopCurve1, rebuild degree 1
        edge_items = cmds.filterExpand(expand=True, selectionMask=32) or []
        seg_curves = []
        for edge in edge_items:
            seg_curves.append(
                cmds.duplicateCurve(edge, constructionHistory=True, range=0, local=0)[0]
            )
        if len(seg_curves) < 2:
            cmds.delete(seg_curves)
            cmds.warning("ForeHead border has too few edges to build the curve")
            return None
        try:
            cmds.attachCurve(
                seg_curves,
                name="faceLoopCurve1",
                constructionHistory=True,
                replaceOriginal=0,
                keepMultipleKnots=1,
                method=1,
                blendBias=0.5,
                blendKnotInsertion=0,
                parameter=0.1,
            )
        except RuntimeError:
            pass
        cmds.delete(seg_curves)
        if not cmds.objExists("faceLoopCurve1"):
            cmds.warning("Could not attach the ForeHead border curve")
            return None
        cmds.rebuildCurve(
            "faceLoopCurve1",
            constructionHistory=0,
            replaceOriginal=1,
            rebuildType=0,
            endKnots=1,
            keepRange=2,
            keepControlPoints=1,
            keepEndPoints=0,
            keepTangents=0,
            spans=0,
            degree=1,
            tolerance=0.01,
        )

        npc = cmds.createNode("nearestPointOnCurve", name="tempNearestPointOnCurve")
        cmds.connectAttr("faceLoopCurve1.worldSpace[0]", npc + ".inputCurve", force=True)

        def _param_at(pos):
            cmds.setAttr(npc + ".inPosition", pos[0], pos[1], pos[2], type="float3")
            return cmds.getAttr(npc + ".result.parameter")

        # direzione coerente: il corner interno deve stare a inizio curva
        inner_pos = cmds.xform(
            eyelid_curve + ".cv[0]", query=True, worldSpace=True, translation=True
        )
        if _param_at(inner_pos) > 2:
            cmds.reverseCurve("faceLoopCurve1", constructionHistory=0, replaceOriginal=1)
        if not cmds.attributeQuery("directionChecked", node=fit_name, exists=True):
            cmds.addAttr(
                fit_name,
                longName="directionChecked",
                attributeType="bool",
                defaultValue=1,
                keyable=False,
            )

        # ancoraggio dei landmark alla curva (sopravvive ai ritocchi CV)
        for attr_name, pos in (
            (
                "noseCvNr",
                cmds.xform(
                    "{}.vtx[{}]".format(self.geometry, nose_nr),
                    query=True,
                    worldSpace=True,
                    translation=True,
                ),
            ),
            (
                "topCvNr",
                cmds.xform(
                    "{}.vtx[{}]".format(self.geometry, top_nr),
                    query=True,
                    worldSpace=True,
                    translation=True,
                ),
            ),
            (
                "sideCvNr",
                cmds.xform(
                    "{}.vtx[{}]".format(self.geometry, side_nr),
                    query=True,
                    worldSpace=True,
                    translation=True,
                ),
            ),
            ("innerEyeCnrNr", inner_pos),
            (
                "outerEyeCnrNr",
                cmds.xform(eyelid_curve + ".cv[99]", query=True, worldSpace=True, translation=True),
            ),
        ):
            parameter = _param_at(pos)
            # asRoundFloatToInt: round half-up
            cmds.addAttr(
                fit_name,
                longName=attr_name,
                attributeType="long",
                defaultValue=int(parameter + 0.5),
            )
        cmds.delete(npc)

        # rename, colore, parent, makeIdentity (come il ramo !upAndLo)
        curve_name = "ForeHead{}Curve{}".format(part, left_suffix)
        shape = cmds.listRelatives("faceLoopCurve1", shapes=True)[0]
        cmds.rename(shape, curve_name + "Shape")
        cmds.rename("faceLoopCurve1", curve_name)
        shape = cmds.listRelatives(curve_name, shapes=True)[0]
        cmds.setAttr(shape + ".overrideEnabled", 1)
        cmds.setAttr(shape + ".overrideColor", 17)
        cmds.parent(curve_name, "FaceFitForeHead{}Curve{}".format(part, left_suffix))
        cmds.makeIdentity(fit_name, apply=True, translate=True, rotate=True, scale=True)

        if not self._create_loop_cylinders("ForeHead", part, left_suffix, scale, False, ""):
            return None
        return border

    def _create_area_mesh(self, section, part, left_suffix, selection, scale) -> bool:
        """Mesh di area per ForeHead / EyeLidInner / LipInner (parita'
        asCreateFaceFit, righe MEL 27392-27456).

        Flood-fill di vertici dal seed (meta' della curva Main, o il
        locator EyeBrowInner per ForeHead) delimitato dal bordo: loop
        Outer (reselect) + selezione corrente del fit. Le facce trovate
        diventano <sec><part>AreaMesh<left>, copia della topologia Face
        (outMesh->inMesh) ridotta alle sole facce dell'area; il
        duplicato <...>AreaMeshExtrude<left> con polyExtrudeFacet
        (history <...>AreaMeshPolyExtrudeFacet<left>) e' il feedback a
        schermo, offsettato in fuori di scale/500.

        Prerequisiti mancanti (Outer/Main non fittati): warning e False
        con cleanup a monte (hardening sanzionato: il MEL flooderebbe
        l'intera testa).

        Nota parita': il loft tempLoft del MEL (27406) e' creato con
        ch=0 e cancellato senza essere mai usato: nessun effetto scena,
        non viene replicato.
        """
        area_mesh = "{}{}AreaMesh{}".format(section, part, left_suffix)

        if section == "ForeHead":
            area_mesh_shader = "asGreenSG"
            grow_start_pos = "EyeBrowInner" + left_suffix
            border_sources = ("FaceFitEyeLidOuter" + left_suffix, grow_start_pos)
        else:
            area_mesh_shader = "asRedSG"
            main_curve = "upper{}MainCurve{}".format(section, left_suffix)
            grow_start_pos = None
            if cmds.objExists(main_curve):
                mid_cv = int(cmds.getAttr(main_curve + ".spans") / 2)
                grow_start_pos = "{}.cv[{}]".format(main_curve, mid_cv)
            border_sources = ("FaceFit{}Outer{}".format(section, left_suffix), main_curve)
        for required in border_sources:
            if not required or not cmds.objExists(required):
                cmds.warning(
                    "AreaMesh for {}{} requires {}: fit the Outer/Main loops first".format(
                        section, part, required
                    )
                )
                return False

        # bordo = loop Outer (reselect) + selezione del fit corrente
        cmds.select(selection)
        original = cmds.ls(selection=True, flatten=True)
        if section == "ForeHead":
            cmds.sets(
                "{}Cylinder{}{}".format(section, part, left_suffix),
                edit=True,
                forceElement="asGreenSG",
            )
            face_fit_reselect("EyeLid", "Outer")
        else:
            face_fit_reselect(section, "Outer")
        cmds.select(original, add=True)
        cmds.ConvertSelectionToVertices()
        border_vtxs = cmds.ls(selection=True, flatten=True)

        if cmds.objExists("closestSampler"):
            cmds.delete("closestSampler")
        sampler = cmds.createNode("closestPointOnMesh", name="closestSampler")
        cmds.connectAttr(self.geometry + ".outMesh", sampler + ".inMesh")
        pos = cmds.xform(grow_start_pos, query=True, worldSpace=True, translation=True)
        cmds.setAttr(sampler + ".inPosition", pos[0], pos[1], pos[2], type="float3")
        seed = cmds.getAttr(sampler + ".result.closestVertexIndex")
        cmds.select("{}.vtx[{}]".format(self.geometry, seed))

        num_sel = 0
        for _ in range(199):
            cmds.polySelectConstraint(propagate=1, type=0x0001)
            cmds.select(border_vtxs, deselect=True)
            previous_num_sel = num_sel
            num_sel = len(cmds.ls(selection=True, flatten=True))
            if num_sel == previous_num_sel:
                break
        cmds.delete(sampler)
        cmds.ConvertSelectionToFaces()
        area_faces = cmds.ls(selection=True, flatten=True)

        cmds.polyCube(
            name=area_mesh,
            width=1,
            height=1,
            depth=1,
            subdivisionsX=1,
            subdivisionsY=1,
            subdivisionsZ=1,
            axis=(0, 1, 0),
            createUVs=4,
            constructionHistory=False,
        )
        cmds.sets(area_mesh, edit=True, forceElement=area_mesh_shader)
        # copia della topologia Face nella shape: il MEL usa
        # connect+refresh+disconnect, che dipende dalla valutazione della
        # viewport (in standalone la shape resterebbe il cubo); il
        # delete -ch baka l'input in modo deterministico
        cmds.connectAttr(self.geometry + ".outMesh", area_mesh + ".inMesh")
        cmds.delete(area_mesh, constructionHistory=True)
        cmds.parent(area_mesh, "FaceFit{}{}Geo{}".format(section, part, left_suffix))
        # tieni solo le facce dell'area (cast asobjSetCast + inversione
        # esplicita: InvertSelection richiede la UI)
        cast = [f.replace(self.geometry, area_mesh, 1) for f in area_faces]
        cmds.select(area_mesh + ".f[*]", replace=True)
        cmds.select(cast, deselect=True)
        cmds.delete()

        # offset "in fuori" con polyExtrude sul duplicato visibile
        extrude_mesh = "{}{}AreaMeshExtrude{}".format(section, part, left_suffix)
        cmds.duplicate(area_mesh, name=extrude_mesh)
        cmds.setAttr(area_mesh + ".v", 0)
        extrude_node = cmds.polyExtrudeFacet(
            extrude_mesh + ".f[*]",
            constructionHistory=True,
            localTranslateZ=scale / 500.0,
            keepFacesTogether=True,
            divisions=1,
            twist=0,
            taper=1,
            offset=0,
            thickness=0,
            smoothingAngle=30,
        )[0]
        cmds.rename(
            extrude_node, "{}{}AreaMeshPolyExtrudeFacet{}".format(section, part, left_suffix)
        )
        for shape in cmds.listRelatives(extrude_mesh, shapes=True) or []:
            if cmds.getAttr(shape + ".intermediateObject"):
                cmds.rename(shape, extrude_mesh + "OrigShape")
        cmds.refresh()
        return True

    def build_fit_eyeball(self) -> bool:
        """Crea il fit dell'occhio (parita' asBuildFitEyeBall, MEL 43664).

        Locator FitEyeBall<Left> (rotateOrder zxy, rz lockato, attr
        version) con sfera proxy FitEyeSphere<Left> (bianca, pupilla
        nera, reference display) sotto FaceFitEyeBall<Left>; posizione e
        scala stimate dalla geometria occhio (opzione RightEye, oppure
        LeftEye in modalita' Left). L'opzione puo' contenere componenti
        del main mesh: in tal caso si duplica l'oggetto e si tengono
        solo le facce occhio (asDuplicatedEye).

        Il ramo MEL di sostituzione degli occhi del body-rig
        (Eye_R/Eye_M: rimozione influence, FK ctrl, buildPose) dipende
        dal body-setup e viene rinviato alla Fase 2: qui ci si ferma con
        warning per non lasciare il body-rig in stato incoerente.
        """
        head_joint = get_fit_option("HeadJoint")
        left_suffix = get_left_suffix()
        eye_geo_text = get_fit_option("LeftEye" if left_suffix == "Left" else "RightEye") or ""
        fit_eyeball = "FitEyeBall" + left_suffix

        if not eye_geo_text:
            cmds.warning("No Eye Geometry choosen")
            return False
        if cmds.objExists(fit_eyeball):
            cmds.warning("{} already exists".format(fit_eyeball))
            return False
        if cmds.objExists("Eye_R") or cmds.objExists("Eye_M"):
            cmds.warning(
                "Body-setup Eye replacement is not ported yet "
                "(Fase 2): remove the body Eye setup first"
            )
            return False
        if not cmds.objExists(head_joint):
            cmds.warning('HeadJoint "{}" does not exist'.format(head_joint))
            return False

        height = 10.0
        if cmds.objExists("Main") and cmds.attributeQuery("height", node="Main", exists=True):
            height = cmds.getAttr("Main.height")
        self._ensure_shaders()

        cmds.spaceLocator(name=fit_eyeball)
        cmds.addAttr(fit_eyeball, longName="version", attributeType="double")
        cmds.setAttr(fit_eyeball + ".version", _AS_SCRIPT_VERSION, lock=True)
        cmds.setAttr(fit_eyeball + ".rotateOrder", 2)
        cmds.setAttr(fit_eyeball + ".rz", lock=True)
        cmds.setAttr(fit_eyeball + "Shape.localScale", 1.5, 1.5, 1.5, type="float3")
        cmds.createNode(
            "transform", name="FaceFitEyeBall" + left_suffix, parent=self.fit_skeleton_grp
        )
        cmds.parent(fit_eyeball, "FaceFitEyeBall" + left_suffix)

        sphere = "FitEyeSphere" + left_suffix
        cmds.polySphere(
            name=sphere,
            radius=0.5,
            subdivisionsX=8,
            subdivisionsY=8,
            axis=(0, 1, 0),
            createUVs=2,
            constructionHistory=False,
        )
        cmds.setAttr(sphere + ".overrideEnabled", 1)
        cmds.setAttr(sphere + ".overrideDisplayType", 2)
        cmds.parent(sphere, fit_eyeball)
        cmds.sets(sphere, edit=True, forceElement="asWhiteSG")
        cmds.sets(sphere + ".f[56:63]", edit=True, forceElement="asBlackSG")
        cmds.setAttr(sphere + ".r", 90, 0, 0, type="float3")
        cmds.setAttr(
            fit_eyeball + ".s", 0.025 * height, 0.025 * height, 0.025 * height, type="float3"
        )

        # piazzamento di partenza stimato dal head joint (ramo !hadBodyEye)
        pos = cmds.xform(head_joint, query=True, worldSpace=True, translation=True)
        cmds.xform(fit_eyeball, worldSpace=True, translation=pos)
        cmds.setAttr(
            fit_eyeball + ".t", pos[1] / -50.0, pos[1] / 15.0, pos[1] / 15.0, type="float3"
        )

        # raffina posizione e scala dalla prima geometria occhio
        tokens = eye_geo_text.split()
        eye_geos = [t for t in tokens if "." not in t]
        if not eye_geos and "." in eye_geo_text:
            # occhio = componenti del main mesh: duplica l'oggetto e
            # tieni solo le facce occhio
            # asobjSetCast deriva il nome sorgente dal componente, non
            # da ls -o (che risolve alla shape)
            src_name = tokens[0].split(".")[0]
            src_objs = cmds.ls(tokens[0], objectsOnly=True) or []
            if src_objs:
                dup = cmds.duplicate(src_objs[0])[0]
                cmds.rename(dup, "asDuplicatedEye")
                cast = [t.replace(src_name, "asDuplicatedEye", 1) for t in tokens]
                # inversione esplicita (il runtime command InvertSelection
                # del MEL richiede la UI e fallisce in standalone)
                cmds.select("asDuplicatedEye.f[*]", replace=True)
                cmds.select(cast, deselect=True)
                cmds.delete()
                eye_geos = ["asDuplicatedEye"]
                tokens[0] = "asDuplicatedEye"
        if eye_geos:
            if "." not in tokens[0]:
                cmds.setAttr(tokens[0] + ".v", 1)
            temp = cmds.duplicate(eye_geos[0], name="tempEye")[0]
            if cmds.listRelatives(temp, parent=True):
                temp = cmds.parent(temp, world=True)[0]
            eye_vis = cmds.getAttr(temp + ".v")
            cmds.xform(temp, centerPivots=True)
            if not eye_vis:
                cmds.setAttr(temp + ".v", 0)
            piv = cmds.xform(temp, query=True, worldSpace=True, pivots=True)
            bb = cmds.xform(temp, query=True, worldSpace=True, boundingBox=True)
            cmds.delete(temp)
            if piv[1] > 0:
                cmds.parent(fit_eyeball, world=True)
                cmds.xform(fit_eyeball, worldSpace=True, translation=piv[:3])
                size = bb[4] - bb[1]
                cmds.xform(fit_eyeball, objectSpace=True, scale=(size, size, size))
                cmds.parent(fit_eyeball, "FaceFitEyeBall" + left_suffix)
            if cmds.objExists("asDuplicatedEye"):
                cmds.delete("asDuplicatedEye")

        # dal primo fit in poi FaceFitSkeleton non si tocca piu' (MEL:
        # asLockAttr FaceFitSkeleton 1 1 1 0)
        _lock_main_attrs(self.fit_skeleton_grp)

        cmds.select(fit_eyeball)
        print(
            "// {} created, place this to match the eye-ball of your character".format(fit_eyeball)
        )
        return True

    def _create_loop_fit(
        self, section, part, left_suffix, selection, scale, up_and_lo, main_and_outer, shading_group
    ):
        """Orchestrazione ramo loop di asCreateFaceFit (port-spec §1-§3).

        Costruisce le curve ordinate da edge-walk (fedelta' MEL).
        Gestisce Pupil/Iris (loop chiusi), EyeLid (up_and_lo), Lip (up_and_lo
        con filtro X>0.001 sul ramo 2), *Line (catena aperta).

        Args:
            section:      Sezione MEL (es. "EyeLid", "Lip", "Pupil").
            part:         Parte (es. "Main", "Outer", "Inner") o "".
            left_suffix:  "" o "Left".
            selection:    Lista componenti come da cmds.ls(sl=True, fl=True).
            scale:        Valore faceScale dalla mask.
            up_and_lo:    True => crea entrambi i rami upper/lower.
            main_and_outer: Inerte in 1c.
            shading_group: SG per Pupil/Iris/*Line (stringa, puo' essere "").

        Returns:
            True se le curve sono state create, False con warning su errore.
            Il chiamante si occupa di cancellare fit_name su False.
        """
        fit_name = "FaceFit{}{}{}".format(section, part, left_suffix)

        # ----------------------------------------------------------------
        # Passo 1: Validazione vtx espliciti per Lip
        # ----------------------------------------------------------------
        vtx_sel_components = [c for c in selection if ".vtx[" in c]
        num_vtx_sel = len(vtx_sel_components)
        if section == "Lip" and num_vtx_sel not in (0, 3):
            cmds.warning(
                "Lip Vertex Selection detected, but {} vertices selected (expected 0 or 3)".format(
                    num_vtx_sel
                )
            )
            return False
        running_lip_left = cmds.objExists("asRunningFaceLipLeft")

        # ----------------------------------------------------------------
        # Passo 2: ConvertSelectionToVertices; LipOuter → deselectLowestHalf;
        #          *Line → filtro lato
        # ----------------------------------------------------------------
        cmds.select(selection)
        cmds.ConvertSelectionToVertices()
        vtxs = cmds.ls(selection=True, flatten=True) or []

        if section == "Lip" and part == "Outer":
            _deselect_lowest_half_of_vtx()
            vtxs = cmds.ls(selection=True, flatten=True) or []

        if section.endswith("Line"):
            filtered_vtxs = []
            for v in vtxs:
                x = cmds.xform(v, query=True, worldSpace=True, translation=True)[0]
                if left_suffix == "" and x > 0.001:
                    continue
                if left_suffix == "Left" and x < -0.001:
                    continue
                filtered_vtxs.append(v)
            cmds.select(filtered_vtxs if filtered_vtxs else [])
            vtxs = filtered_vtxs

        if not vtxs:
            cmds.warning("No vertices after filtering for {}{}".format(section, part))
            return False

        # ----------------------------------------------------------------
        # Passo 3: tol
        # ----------------------------------------------------------------
        tol = 0.001
        if left_suffix == "Left":
            tol = 9999
        elif get_fit_option("Cyclops") and section == "EyeLid":
            tol = 9999

        # ----------------------------------------------------------------
        # Passo 4: scan min/max; dead-ends
        # ----------------------------------------------------------------
        scan = _scan_min_max_vtxs(vtxs, tol)
        dead_ends = _find_dead_end_vtxs(vtxs)

        # ----------------------------------------------------------------
        # Passo 5: start/end vtx
        # ----------------------------------------------------------------
        # Caso base
        start_vtx = scan["maxX"][0]
        end_vtx = scan["minX"][0]
        if left_suffix == "Left":
            start_vtx = scan["minX"][0]
            end_vtx = scan["maxX"][0]

        # Ricorsione Lip lato Left: start/end dal nodo temporaneo
        # (parita' MEL 26657-26660)
        if running_lip_left:
            start_vtx = cmds.getAttr("asRunningFaceLipLeft.startVtx")
            end_vtx = cmds.getAttr("asRunningFaceLipLeft.endVtx")

        # *Line: ordina dead-ends per Y (start=alto, end=basso)
        if section.endswith("Line"):
            if len(dead_ends) >= 2:
                y0 = cmds.xform(dead_ends[0], query=True, worldSpace=True, translation=True)[1]
                y1 = cmds.xform(dead_ends[1], query=True, worldSpace=True, translation=True)[1]
                if y0 >= y1:
                    start_vtx = dead_ends[0]
                    end_vtx = dead_ends[1]
                else:
                    start_vtx = dead_ends[1]
                    end_vtx = dead_ends[0]
            # else: catena strana, resta il caso base
        # Pupil / Iris: loop chiuso
        elif section in ("Pupil", "Iris"):
            end_vtx = ""

        # EyeLid: start/end con traversal $around (port-spec §2)
        elif section == "EyeLid":
            # Recupera vtx espliciti dalla selezione originale
            explicit_vtxs = [c for c in selection if ".vtx[" in c]
            if explicit_vtxs:
                first_explicit = explicit_vtxs[0]
                second_explicit = explicit_vtxs[1] if len(explicit_vtxs) > 1 else None
                # Prima assegnazione greedy (come MEL righe 26722-26729)
                # start = primo vtx esplicito
                start_vtx = first_explicit
                if second_explicit:
                    end_vtx = second_explicit
                # garanzia non-swap (port-spec §2 righe 26731-26744)
                if end_vtx and end_vtx != "":
                    pa = cmds.xform(start_vtx, query=True, worldSpace=True, translation=True)
                    pb = cmds.xform(end_vtx, query=True, worldSpace=True, translation=True)
                    cond = pa[0] < pb[0]
                    if left_suffix == "Left":
                        cond = not cond
                    if cond:
                        start_vtx, end_vtx = end_vtx, start_vtx

            # Traversal $around per trovare endVtx (port-spec §2, riga 26746-26773)
            if start_vtx and end_vtx == scan["minX"][0]:
                # Risalcola end_vtx tramite grow
                # Filtra gli edge della selezione
                cmds.select(selection)
                cmds.ConvertSelectionToEdges()
                sel_edges_all = cmds.ls(selection=True, flatten=True) or []
                # rimuovi vtx components se presenti
                sel_edges_all = [e for e in sel_edges_all if ".e[" in e]
                num_sel_edges = len(sel_edges_all)

                cmds.select(start_vtx)
                prev_vtxs_around = [start_vtx]
                found_end = None
                for _y in range(99):
                    cmds.ConvertSelectionToEdges()
                    cur_edges = cmds.ls(selection=True, flatten=True) or []
                    cur_edges = [e for e in cur_edges if e in set(sel_edges_all)]
                    if not cur_edges:
                        break
                    around_flag = len(cur_edges) >= num_sel_edges
                    cmds.select(cur_edges)
                    cmds.ConvertSelectionToVertices()
                    cur_vtxs = cmds.ls(selection=True, flatten=True) or []
                    if around_flag:
                        for v in prev_vtxs_around:
                            if cmds.objExists(v):
                                cmds.select(v, deselect=True)
                        remaining = cmds.ls(selection=True, flatten=True) or []
                        if remaining:
                            found_end = remaining[0]
                        break
                    prev_vtxs_around = list(cur_vtxs)
                    cmds.select(cur_vtxs)

                cmds.select(clear=True)
                if found_end:
                    end_vtx = found_end

        # Lip: corner specificati (parita' MEL 26776-26820). Con la
        # ricorsione attiva i corner vengono dal nodo temporaneo; con 3
        # vtx selezionati il corner sinistro e' il piu' a sinistra (minX)
        # e lo start e' il piu' alto dei restanti; lipStartVtxs guida il
        # filtro del ramo 2 (skip finche' non si tocca il secondo corner).
        lip_start_vtxs = []
        if section == "Lip":
            if running_lip_left:
                start_vtx = cmds.getAttr("asRunningFaceLipLeft.startVtx")
                lip_start_vtxs = [start_vtx, cmds.getAttr("asRunningFaceLipLeft.righLowerStartVtx")]
            else:
                min_px = 999.0
                for c in vtx_sel_components:
                    if c == start_vtx:
                        continue
                    px = cmds.xform(c, query=True, worldSpace=True, translation=True)[0]
                    if px < min_px:
                        min_px = px
                        end_vtx = c
                lip_start_vtxs = [c for c in vtx_sel_components if c != end_vtx]
            if len(lip_start_vtxs) == 1:
                lip_start_vtxs = []
            if len(lip_start_vtxs) > 1:
                max_py = -999.0
                for c in lip_start_vtxs:
                    py = cmds.xform(c, query=True, worldSpace=True, translation=True)[1]
                    if py > max_py:
                        max_py = py
                        start_vtx = c

        # Guard: start None (nessun vertice passa il filtro tol)
        if start_vtx is None:
            cmds.warning(
                "Could not determine startVtx for {}{}{}".format(section, part, left_suffix)
            )
            return False

        # ----------------------------------------------------------------
        # Passo 6: recupera edge list; _pick_start_edges; ramo 1
        # ----------------------------------------------------------------
        # parita' MEL: il walk filtra contro $sel (selezione originale),
        # quindi contano solo gli edge letteralmente selezionati; i vtx
        # espliciti (corner Lip/EyeLid) NON portano con se' i loro edge
        # incidenti
        cmds.select(selection)
        all_sel_flat = cmds.ls(selection=True, flatten=True) or []
        sel_edges = [e for e in all_sel_flat if ".e[" in e]

        if not sel_edges:
            cmds.warning("No edges found for {}{}{}".format(section, part, left_suffix))
            return False

        edge1, edge2 = _pick_start_edges(start_vtx, sel_edges, left_suffix)

        chain1 = _walk_loop(sel_edges, start_vtx, end_vtx, edge2)

        if not chain1:
            cmds.warning("Not a complete edgeloop for {}{}{}".format(section, part, left_suffix))
            return False

        # ----------------------------------------------------------------
        # Passo 7: loop chiusi → append start in coda
        # ----------------------------------------------------------------
        is_closed = end_vtx == ""
        pts1 = []
        for v in chain1:
            pos = cmds.xform(v, query=True, worldSpace=True, translation=True)
            pts1.append(pos)
        if is_closed:
            pts1.append(pts1[0])  # chiude la curva ripetendo il primo punto

        # ----------------------------------------------------------------
        # Passo 8: curva faceLoopCurve1
        # ----------------------------------------------------------------
        curve1 = cmds.curve(name="faceLoopCurve1", degree=1, point=pts1)

        # ----------------------------------------------------------------
        # Passo 9: ramo 2 (up_and_lo)
        # ----------------------------------------------------------------
        pts2 = None
        curve2 = None
        if up_and_lo:
            # Il walk parte sempre da start_vtx; per Lip il punto di
            # start viene poi escluso dalla curva (skip i==0 piu' sotto,
            # port-spec ramo 2). NOTA per la fase Lip non-symmetrical:
            # il filtro x>0.001 qui sotto vale SOLO per il caso simmetrico
            # (niente lipStartVtxs/asRunningFaceLipLeft).
            cmds.select(start_vtx)

            chain2_raw = _walk_loop(sel_edges, start_vtx, end_vtx, edge1, max_steps=499)
            if not chain2_raw:
                # cleanup completo
                if cmds.objExists("faceLoopCurve1"):
                    cmds.delete("faceLoopCurve1")
                cmds.warning(
                    "Not a complete edgeloop (ramo 2) for {}{}{}".format(section, part, left_suffix)
                )
                return False

            pts2 = []
            hit_second_lip_start = False
            for i, v in enumerate(chain2_raw):
                pos = cmds.xform(v, query=True, worldSpace=True, translation=True)
                # Lip ramo 2 (parita' MEL 27186-27203): il primo punto
                # NON e' mai start; con lipStartVtxs si saltano i punti
                # finche' il walk non tocca il secondo corner (incluso);
                # senza, si tiene il solo lato destro (x <= 0.001).
                # chain2_raw[0] = start_vtx, quindi l'indice MEL e' i-1
                # (la guardia $i>0 del MEL diventa i > 1).
                if section == "Lip" and i == 0:
                    continue
                if lip_start_vtxs:
                    if i > 1 and v in lip_start_vtxs:
                        hit_second_lip_start = True
                    if not hit_second_lip_start:
                        continue
                elif section == "Lip" and pos[0] > 0.001 and not running_lip_left:
                    continue
                pts2.append(pos)

            if not pts2:
                if cmds.objExists("faceLoopCurve1"):
                    cmds.delete("faceLoopCurve1")
                cmds.warning(
                    "Lip ramo 2 empty after X filter for {}{}{}".format(section, part, left_suffix)
                )
                return False

            curve2 = cmds.curve(name="faceLoopCurve2", degree=1, point=pts2)

        # ----------------------------------------------------------------
        # Passo 10: determinazione upper/lower
        # ----------------------------------------------------------------
        # Raccoglie i vertici del ramo 1 tramite edges1
        cmds.select(sel_edges)
        cmds.ConvertSelectionToVertices()
        all_vtxs_sel = cmds.ls(selection=True, flatten=True) or []
        cmds.select(clear=True)

        # maxYVtx dell'intera selezione
        scan_all = _scan_min_max_vtxs(all_vtxs_sel, 9999)
        max_y_vtx = scan_all["maxY"][0]

        one_is_upper = True  # default: ramo 1 e' upper
        if up_and_lo:
            # Caso base: maxYVtx nel ramo 1?
            chain1_set = set(chain1)
            one_is_upper = max_y_vtx in chain1_set

            # Override LipOuter: Y del primo punto dei due rami
            if section == "Lip" and part == "Outer":
                y1_first = pts1[0][1]
                y2_first = pts2[0][1] if pts2 else 0.0
                one_is_upper = y1_first > y2_first

            # Override LipMain: grow da upperLipOuterCurve<Left>.cv[0]
            elif section == "Lip" and part == "Main":
                ref_curve = "upperLipOuterCurve" + left_suffix
                if cmds.objExists(ref_curve):
                    one_is_upper = self._grow_upper_check(ref_curve, chain1, chain2_raw or [], 18)

            # Override LipInner: grow da upperLipMainCurve<Left>.cv[0]
            elif section == "Lip" and part == "Inner":
                ref_curve = "upperLipMainCurve" + left_suffix
                if cmds.objExists(ref_curve):
                    one_is_upper = self._grow_upper_check(ref_curve, chain1, chain2_raw or [], 10)

        # ----------------------------------------------------------------
        # Passo 11: rename, colori, parent, makeIdentity
        # ----------------------------------------------------------------
        # Colore in base alla parte
        color_map = {"Inner": 15, "Main": 13, "Outer": 14}
        curve_color = color_map.get(part, 17)

        curve_parent_grp = "FaceFit{}{}Curve{}".format(section, part, left_suffix)

        if up_and_lo:
            upper_name = "upper{}{}Curve{}".format(section, part, left_suffix)
            lower_name = "lower{}{}Curve{}".format(section, part, left_suffix)

            if one_is_upper:
                # rename shape then transform (MEL parity)
                shape1 = cmds.listRelatives(curve1, shapes=True)[0]
                cmds.rename(shape1, upper_name + "Shape")
                curve1 = cmds.rename(curve1, upper_name)
                shape2 = cmds.listRelatives(curve2, shapes=True)[0]
                cmds.rename(shape2, lower_name + "Shape")
                curve2 = cmds.rename(curve2, lower_name)
            else:
                shape1 = cmds.listRelatives(curve1, shapes=True)[0]
                cmds.rename(shape1, lower_name + "Shape")
                curve1 = cmds.rename(curve1, lower_name)
                shape2 = cmds.listRelatives(curve2, shapes=True)[0]
                cmds.rename(shape2, upper_name + "Shape")
                curve2 = cmds.rename(curve2, upper_name)

            for cname in (upper_name, lower_name):
                shape = cmds.listRelatives(cname, shapes=True)[0]
                cmds.setAttr(shape + ".overrideEnabled", 1)
                cmds.setAttr(shape + ".overrideColor", curve_color)
                cmds.parent(cname, curve_parent_grp)
        else:
            no_ul_name = "{}{}Curve{}".format(section, part, left_suffix)
            # MEL: rename shape first then transform (righe 27307-27312)
            shape = cmds.listRelatives(curve1, shapes=True)[0]
            cmds.rename(shape, no_ul_name + "Shape")
            cmds.rename(curve1, no_ul_name)
            shape = cmds.listRelatives(no_ul_name, shapes=True)[0]
            cmds.setAttr(shape + ".overrideEnabled", 1)
            cmds.setAttr(shape + ".overrideColor", curve_color)
            cmds.parent(no_ul_name, curve_parent_grp)

        # makeIdentity sul gruppo fit root
        cmds.makeIdentity(fit_name, apply=True, translate=True, rotate=True, scale=True)

        # ----------------------------------------------------------------
        # Passo 12: cilindri (stub Task 4)
        # ----------------------------------------------------------------
        if not self._create_loop_cylinders(
            section, part, left_suffix, scale, up_and_lo, shading_group
        ):
            return False

        return True

    def _grow_upper_check(self, ref_curve, chain1, chain2, max_steps):
        """Determina quale ramo e' upper tramite grow da ref_curve.cv[0].

        Usa closestPointOnMesh + grow ConvertSelectionToEdges/Vertices
        per massimo max_steps passi, finche' tocca chain1[0] o chain2[0].

        Returns:
            True se il ramo 1 e' upper (cioe' si tocca chain1[0] prima).
        """
        geo = get_fit_option("Face")
        if not geo or not cmds.objExists(geo):
            cmds.warning(
                "_grow_upper_check: Face geometry not available, assuming branch 1 is upper"
            )
            return True

        cv0_pos = cmds.xform(ref_curve + ".cv[0]", query=True, worldSpace=True, translation=True)

        # Trova il vertice piu' vicino sulla mesh tramite closestPoint
        # Creiamo un nodo temporaneo closestPointOnMesh
        cpm = cmds.createNode("closestPointOnMesh")
        geo_shape = (cmds.listRelatives(geo, shapes=True, noIntermediate=True) or [geo])[0]
        cmds.connectAttr(geo_shape + ".outMesh", cpm + ".inMesh")
        cmds.setAttr(cpm + ".inPosition", cv0_pos[0], cv0_pos[1], cv0_pos[2], type="double3")
        seed_idx = cmds.getAttr(cpm + ".closestVertexIndex")
        cmds.delete(cpm)

        seed_vtx = "{}.vtx[{}]".format(geo, seed_idx)
        target1 = chain1[0] if chain1 else None
        target2 = chain2[0] if chain2 else None

        cmds.select(seed_vtx)
        for _step in range(max_steps):
            current_sel = cmds.ls(selection=True, flatten=True) or []
            if target1 and target1 in current_sel:
                cmds.select(clear=True)
                return True
            if target2 and target2 in current_sel:
                cmds.select(clear=True)
                return False
            # grow
            cmds.ConvertSelectionToEdges()
            cmds.ConvertSelectionToVertices()

        cmds.select(clear=True)
        return True  # fallback

    def _create_loop_cylinders(self, section, part, left_suffix, scale, up_and_lo, shading_group):
        """Crea i cilindri estrusi per il fit loop (port-spec par.4).

        Per ogni fattore upper/lower (solo upper se !up_and_lo): crea un
        profilo circolare, lo estrude lungo la curva corrispondente, cancella
        il profilo, imposta display/override, fa parent sotto il gruppo Geo,
        verifica le normali tramite cv[6][0] vs cv[6][1] e applica il SG.

        Mappatura kwargs Python di cmds.extrude equivalenti al MEL:
            -ch 0       -> constructionHistory=False
            -rn false   -> range=False
            -po 0       -> polygon=0
            -et 2       -> extrudeType=2
            -ucp 1      -> useComponentPivot=1
            -fpt 1      -> fixedPath=True
            -upn 1      -> useProfileNormal=True
            -rotation 0 -> rotation=0
            -scale 1    -> scale=1
            -rsp 0      -> reverseSurfaceIfPathReversed=False
        """
        geo_grp = "FaceFit{}{}Geo{}".format(section, part, left_suffix)
        curve_grp = "FaceFit{}{}Curve{}".format(section, part, left_suffix)
        profile_radius = scale / 400.0

        # Determina quali fattori upper/lower processare
        factors = ["upper", "lower"] if up_and_lo else [""]
        created_cylinders = []

        def _fail_cleanup(node=None):
            """Cancella profilo/cilindri parziali prima del return False."""
            if node and cmds.objExists(node):
                cmds.delete(node)
            for cyl in created_cylinders:
                if cmds.objExists(cyl):
                    cmds.delete(cyl)
            return False

        for factor in factors:
            # Nome profilo temporaneo: <Section>Profile<Part><Left>
            profile_name = "{}Profile{}{}".format(section, part, left_suffix)
            # Nome cilindro: <upperLower><Section>Cylinder<Part><Left>
            #   o <Section>Cylinder<Part><Left> se !up_and_lo
            cyl_name = "{}{}Cylinder{}{}".format(factor, section, part, left_suffix)
            # Nome curva da cui estrude: <factor><Section><Part>Curve<Left>
            #   o <Section><Part>Curve<Left> se !up_and_lo
            curve_name = "{}{}{}Curve{}".format(factor, section, part, left_suffix)

            # 1. Profilo circolare
            profile = cmds.circle(
                center=(0, 0, 0),
                normal=(0, 1, 0),
                sweep=360,
                radius=profile_radius,
                degree=3,
                ut=0,
                tolerance=0.000393701,
                sections=8,
                constructionHistory=False,
            )[0]
            profile_name = cmds.rename(profile, profile_name)
            cmds.parent(profile_name, curve_grp)

            # 2. Estrude il profilo lungo la curva
            if not cmds.objExists(curve_name):
                cmds.warning("_create_loop_cylinders: curve not found: {}".format(curve_name))
                return _fail_cleanup(profile_name)

            cyl_result = cmds.extrude(
                profile_name,
                curve_name,
                name=cyl_name,
                constructionHistory=False,
                range=False,
                polygon=0,
                extrudeType=2,
                useComponentPivot=1,
                fixedPath=True,
                useProfileNormal=True,
                rotation=0,
                scale=1,
                reverseSurfaceIfPathReversed=False,
            )
            # extrude restituisce lista; il primo elemento e' il nodo surface
            if not cyl_result:
                cmds.warning("_create_loop_cylinders: extrude failed for {}".format(cyl_name))
                return _fail_cleanup(profile_name)
            cyl_node = cyl_result[0]
            created_cylinders.append(cyl_node)

            # 3. Cancella il profilo (usa-e-getta)
            if cmds.objExists(profile_name):
                cmds.delete(profile_name)

            # 4. Display overrides sulla shape
            shapes = cmds.listRelatives(cyl_node, shapes=True) or []
            if shapes:
                shape = shapes[0]
                cmds.setAttr(shape + ".overrideEnabled", 1)
                cmds.setAttr(shape + ".overrideDisplayType", 2)
                cmds.setAttr(shape + ".curvePrecisionShaded", 4)

            # 5. Parent sotto il gruppo Geo
            cmds.parent(cyl_node, geo_grp)

            # 6. Verifica normali: cv[6][0] vs cv[6][1] in Y
            try:
                pos_a = cmds.xform(
                    "{}.cv[6][0]".format(cyl_node), query=True, worldSpace=True, translation=True
                )
                pos_b = cmds.xform(
                    "{}.cv[6][1]".format(cyl_node), query=True, worldSpace=True, translation=True
                )
                if pos_a[1] > pos_b[1]:
                    cmds.reverseSurface(
                        cyl_node, direction=0, constructionHistory=False, replaceOriginal=True
                    )
            except Exception:
                pass  # guard: curva corta o indici non validi

            # 7. Shading group
            sg = None
            if section.endswith("Line") or section in ("Pupil", "Iris"):
                # usa il parametro shading_group
                sg = shading_group if shading_group else None
            elif section == "Tongue":
                # parita' letterale col MEL (ramo irraggiungibile in
                # pratica: Tongue esce prima dei cilindri)
                sg = "asRedSG"
            elif section == "EyeLidMain2":
                sg = "asGreenSG" if factor in ("upper", "") else "asGreen2SG"
            elif part in ("Inner", "Main", "Outer"):
                sg = "asGreenSG" if factor in ("upper", "") else "asGreen2SG"

            if sg and cmds.objExists(sg):
                cmds.sets(cyl_node, edit=True, forceElement=sg)

        return True

    def _create_tongue_fit(self, template_loc: str, scale: float) -> bool:
        """Crea curva e locator della Tongue (ramo Tongue di asCreateFaceFit).

        Curva a 5 CV pilotati dai locator Tongue0-4 (worldPosition ->
        controlPoints); autoplace dal bbox della geo dell'opzione Tongue
        se definita. I locator restano selezionati (come in MEL).
        """
        reserved = ["TongueCurve"] + ["Tongue{}".format(i) for i in range(5)]
        existing = [name for name in reserved if cmds.objExists(name)]
        if existing:
            cmds.warning("Tongue fit nodes already exist in scene: {}".format(", ".join(existing)))
            return False

        pos = cmds.xform(self.fit_skeleton_grp, query=True, worldSpace=True, translation=True)
        curve = cmds.curve(
            degree=1,
            point=[
                (0, pos[1] + scale / 10.0, 0),
                (0, pos[1] + scale / 5.0, scale / 5.0),
                (0, pos[1] + scale / 5.0, scale / 3.0),
                (0, pos[1] + scale / 5.5, scale / 2.5),
                (0, pos[1] + scale / 7.0, scale / 2.2),
            ],
        )
        cmds.rename(curve, "TongueCurve")
        cmds.parent("TongueCurve", "FaceFitTongueCurve")
        cmds.setAttr("TongueCurve.inheritsTransform", 0)
        cmds.setAttr("TongueCurveShape.overrideEnabled", 1)
        cmds.setAttr("TongueCurveShape.overrideColor", 13)

        for i in range(5):
            cmds.duplicate(template_loc, name="Tongue{}".format(i))
            cmds.parent("Tongue{}".format(i), "FaceFitTongueLoc")
            cv_pos = cmds.xform(
                "TongueCurve.cv[{}]".format(i), query=True, worldSpace=True, translation=True
            )
            cmds.xform("Tongue{}".format(i), worldSpace=True, translation=cv_pos)
            cmds.connectAttr(
                "Tongue{}Shape.worldPosition[0]".format(i),
                "TongueCurveShape.controlPoints[{}]".format(i),
                force=True,
            )

        cmds.select(["Tongue{}".format(i) for i in range(5)])

        tongue_geo = get_fit_option("Tongue")
        if tongue_geo and cmds.objExists(tongue_geo):
            bb = cmds.xform(tongue_geo, query=True, worldSpace=True, boundingBox=True)
            # NOTA PARITA': il passo Z usa (zMin+zMax)/6 come nel MEL
            # originale (non zMax-zMin). Con geo tongue centrate sull'origine
            # il passo degenera a ~0: comportamento identico ad AS.
            for i in range(5):
                cmds.xform(
                    "Tongue{}".format(i),
                    worldSpace=True,
                    translation=(0, (bb[1] + bb[4]) / 2.0, bb[2] + ((bb[2] + bb[5]) / 6.0) * i),
                )
        return True

    def _create_upmidlo_fit(self, template_loc: str, scale: float) -> bool:
        """Crea i locator upper/middle/lowerFace (ramo UpMidLo).

        Richiede in scena JawPivot, lowerEyeLidOuterCurve e NoseUnder
        (prodotti dagli altri fit). Ritorna False se mancano: il chiamante
        fa il cleanup del gruppo FaceFitUpMidLo parziale.
        """
        reserved = ("upperFace", "middleFace", "lowerFace")
        existing = [name for name in reserved if cmds.objExists(name)]
        if existing:
            cmds.warning("UpMidLo fit nodes already exist in scene: {}".format(", ".join(existing)))
            return False

        required = ("JawPivot", "lowerEyeLidOuterCurve", "NoseUnder")
        missing = [name for name in required if not cmds.objExists(name)]
        if missing:
            cmds.warning("UpMidLo requires existing fits: missing {}".format(", ".join(missing)))
            return False

        cmds.duplicate(template_loc, name="upperFace")
        cmds.parent("upperFace", "FaceFitUpMidLoLoc")
        upper_shape = cmds.listRelatives("upperFace", shapes=True)[0]
        cmds.setAttr(upper_shape + ".localScale", scale / 2.0, 0, 0, type="float3")
        jaw_pos = cmds.xform("JawPivot", query=True, worldSpace=True, translation=True)
        bb = cmds.xform("lowerEyeLidOuterCurve", query=True, worldSpace=True, boundingBox=True)
        cmds.xform("upperFace", worldSpace=True, translation=(0, bb[1], jaw_pos[2]))
        _lock_main_attrs("upperFace")
        for attr in ("ty", "tz"):
            cmds.setAttr("upperFace." + attr, lock=False, keyable=True)

        cmds.duplicate("upperFace", name="middleFace")
        cmds.duplicate("upperFace", name="lowerFace")
        cmds.setAttr("lowerFace.ty", cmds.getAttr("NoseUnder.ty"))
        cmds.setAttr(
            "middleFace.ty", (cmds.getAttr("upperFace.ty") + cmds.getAttr("lowerFace.ty")) / 2.0
        )
        cmds.select(clear=True)
        return True

    def fit_region(self, region_name: str, left_side: bool = False, upper_lower: str = "") -> bool:
        """
        Fit a single region from current selection.

        Args:
            region_name: Name of the region to fit
            left_side: Whether to fit left side (for mirrored regions)
            upper_lower: "upper" or "lower" for split regions (eyelids, lips)

        Returns:
            True if fitting succeeded
        """
        if region_name not in self.REGIONS:
            cmds.warning(f"Unknown region: {region_name}")
            return False

        region = self.REGIONS[region_name]

        # Delega al percorso EyeBall (Fase 1d): asCreateFaceFit devia su
        # asBuildFitEyeBall, che non legge la selezione ma le opzioni
        # RightEye/LeftEye di FaceFitSkeleton.
        if region_name == "EyeBall":
            if left_side and get_left_suffix() != "Left":
                cmds.warning(
                    "Left-side fitting requires switch_side('Left') first (NonSymSide scene state)"
                )
                return False
            success = self.create_face_fit("EyeBall")
            if success and self._on_fit_complete:
                self._on_fit_complete(region_name + get_left_suffix())
            return success

        # Delega al percorso JawCurves (Fase 1e): proc MEL dedicata
        # (asFaceFitJawCurves), non passa da asCreateFaceFit.
        if region_name == "JawCurves":
            success = self.fit_jaw_curves()
            if success and self._on_fit_complete:
                self._on_fit_complete(region_name)
            return success

        # Delega al percorso ForeHead (Fase 1d): curva da 3 vertici via
        # asSelectLeastEdgesPath + AreaMesh.
        if region_name == "ForeHead":
            if left_side and get_left_suffix() != "Left":
                cmds.warning(
                    "Left-side fitting requires switch_side('Left') first (NonSymSide scene state)"
                )
                return False
            success = self.create_face_fit("ForeHead")
            if success and self._on_fit_complete:
                self._on_fit_complete(region_name + get_left_suffix())
            return success

        # Delega al percorso a parita' MEL (Fase 1b):
        # regioni sferiche e regioni senza selezione (Tongue, UpMidLo).
        if region.is_sphere or region.fit_type == FitType.NO_SELECTION:
            if left_side and not region.mirrored:
                cmds.warning(
                    "{} is not a mirrored region: left-side fitting not applicable".format(
                        region_name
                    )
                )
                return False
            if left_side and get_left_suffix() != "Left":
                cmds.warning(
                    "Left-side fitting requires switch_side('Left') first (NonSymSide scene state)"
                )
                return False
            success = self.create_face_fit(
                region_name, is_sphere=region.is_sphere, shading_group=region.shading_group
            )
            if success and self._on_fit_complete:
                self._on_fit_complete(region_name + get_left_suffix())
            return success

        # Delega al percorso loop MEL-parity (Fase 1c):
        # EyeLid*/Lip*/Pupil/Iris/EyeLidMain2.
        if region_name in self._LOOP_ROUTING:
            if left_side and not region.mirrored:
                cmds.warning(
                    "{} is not a mirrored region: left-side fitting not applicable".format(
                        region_name
                    )
                )
                return False
            if left_side and get_left_suffix() != "Left":
                cmds.warning(
                    "Left-side fitting requires switch_side('Left') first (NonSymSide scene state)"
                )
                return False
            if upper_lower:
                cmds.warning(
                    "upper/lower split is automatic in the MEL-parity path "
                    "(upper_lower={!r} ignored for {})".format(upper_lower, region_name)
                )
            section, part, up_and_lo = self._LOOP_ROUTING[region_name]
            success = self.create_face_fit(
                section, part=part, up_and_lo=up_and_lo, shading_group=region.shading_group
            )
            if success and self._on_fit_complete:
                self._on_fit_complete(region_name + get_left_suffix())
            return success

        suffix = "Left" if left_side else ""

        # Build full name
        if upper_lower and region.has_upper_lower:
            full_name = f"{upper_lower}{region_name}{suffix}"
        else:
            full_name = f"{region_name}{suffix}"

        # Get current selection
        selection = cmds.ls(selection=True, flatten=True)

        if not selection:
            cmds.warning(f"No selection for {region.display_name}")
            return False

        # Process based on fit type
        success = False

        if region.fit_type == FitType.VERTEX:
            success = self._store_vertex_fit(full_name, selection, region.color)

        elif region.fit_type == FitType.FACE_AREA:
            success = self._store_face_area_fit(full_name, selection, region.color)

        if success and self._on_fit_complete:
            self._on_fit_complete(full_name)

        return success

    def _store_vertex_fit(self, name: str, selection: List[str], color: int) -> bool:
        """Store a single vertex fit as a locator.

        Percorso legacy: usato solo da EyeBall finche' asBuildFitEyeBall
        non viene portato (Fase 1c/1d). Le regioni sferiche passano da
        create_face_fit.
        """
        # Validate single vertex
        vertices = self._ensure_vertices(selection)
        if len(vertices) != 1:
            cmds.warning(f"{name} requires exactly 1 vertex, got {len(vertices)}")
            return False

        vertex = vertices[0]
        pos = cmds.xform(vertex, query=True, worldSpace=True, translation=True)

        # Create fit locator
        loc_name = f"FaceFit{name}"
        if cmds.objExists(loc_name):
            cmds.delete(loc_name)

        loc = cmds.spaceLocator(name=loc_name)[0]
        cmds.xform(loc, worldSpace=True, translation=pos)
        cmds.parent(loc, self.fit_skeleton_grp)

        # Store selection attribute
        cmds.addAttr(loc, longName="selection", dataType="string")
        cmds.setAttr(f"{loc}.selection", vertex, type="string")

        # Set visual properties
        if not cmds.attributeQuery("faceScale", node=self.fit_skeleton_grp, exists=True):
            cmds.warning("faceScale not set: create the fit mask first (create_fit_mask)")
            return False
        face_scale = cmds.getAttr(f"{self.fit_skeleton_grp}.faceScale")
        scale = face_scale / 50.0

        shape = cmds.listRelatives(loc, shapes=True)[0]
        cmds.setAttr(f"{shape}.overrideEnabled", 1)
        cmds.setAttr(f"{shape}.overrideColor", color)
        cmds.setAttr(f"{shape}.localScale", scale, scale, scale, type="float3")

        # Store in fit data
        self.fit_data[name] = FitData(
            region_name=name,
            vertices=[vertex],
            positions=[tuple(pos)],
            locator=loc_name,
            selection_string=vertex,
        )

        print(f"// Fitted {name}")
        cmds.select(clear=True)
        return True

    # _store_loop_fit and _store_half_loop_fit were RETIRED in Task 5 (Fase 1c).
    # All EyeLid*/Lip*/Pupil/Iris/EyeLidMain2 regions now route through
    # create_face_fit (MEL-parity edge-walk path) via _LOOP_ROUTING in
    # fit_region.  _store_vertex_fit (EyeBall legacy) and
    # _store_face_area_fit (ForeHead legacy) are kept.

    def _store_face_area_fit(self, name: str, selection: List[str], color: int) -> bool:
        """Store a face area selection."""
        # Convert to vertices
        cmds.select(selection)
        cmds.ConvertSelectionToVertices()
        vertices = cmds.ls(selection=True, flatten=True)

        # Create group
        grp_name = f"FaceFit{name}Area"
        if cmds.objExists(grp_name):
            cmds.delete(grp_name)

        grp = cmds.createNode("transform", name=grp_name, parent=self.fit_skeleton_grp)

        # Store selection
        selection_str = " ".join(vertices)
        cmds.addAttr(grp, longName="selection", dataType="string")
        cmds.setAttr(f"{grp}.selection", selection_str, type="string")

        # Store in fit data
        self.fit_data[name] = FitData(
            region_name=name, vertices=vertices, selection_string=selection_str
        )

        print(f"// Fitted {name} area with {len(vertices)} vertices")
        cmds.select(clear=True)
        return True

    def _ensure_vertices(self, selection: List[str]) -> List[str]:
        """Ensure selection is converted to vertices."""
        cmds.select(selection)

        # Convert edges to vertices
        if any(".e[" in s for s in selection):
            cmds.ConvertSelectionToVertices()

        # Convert faces to vertices
        if any(".f[" in s for s in selection):
            cmds.ConvertSelectionToVertices()

        return cmds.ls(selection=True, flatten=True)

    def get_fit_selection(self, region_name: str, left_side: bool = False) -> str:
        """
        Get the stored selection string for a region.

        Args:
            region_name: Name of the region
            left_side: Whether to get left side

        Returns:
            Selection string
        """
        suffix = "Left" if left_side else ""
        fit_obj = f"FaceFit{region_name}{suffix}"

        if cmds.objExists(fit_obj):
            if cmds.attributeQuery("selection", node=fit_obj, exists=True):
                return cmds.getAttr(f"{fit_obj}.selection")

        # Check for curve directly
        curve = f"{region_name}Curve{suffix}"
        if cmds.objExists(curve):
            if cmds.attributeQuery("selection", node=curve, exists=True):
                return cmds.getAttr(f"{curve}.selection")

        return ""

    def get_fit_position(self, region_name: str, left_side: bool = False) -> Optional[List[float]]:
        """
        Get the world position of a fitted region.

        Args:
            region_name: Name of the region
            left_side: Whether to get left side

        Returns:
            Position [x, y, z] or None
        """
        suffix = "Left" if left_side else ""
        fit_obj = f"FaceFit{region_name}{suffix}"

        if cmds.objExists(fit_obj):
            return cmds.xform(fit_obj, query=True, worldSpace=True, translation=True)
        return None

    def validate_fitting(self, include_optional: bool = False) -> Tuple[List[str], List[str]]:
        """
        Validate that all required regions are fitted.

        Args:
            include_optional: Also check optional regions

        Returns:
            Tuple of (missing_required, missing_optional)
        """
        missing_required = []
        missing_optional = []

        for name, region in self.REGIONS.items():
            if region.has_upper_lower:
                # Check both upper and lower
                for ul in ["upper", "lower"]:
                    fit_name = f"{ul}{name}"
                    exists = cmds.objExists(f"FaceFit{name}") or cmds.objExists(f"{ul}{name}Curve")

                    if not exists:
                        if region.required:
                            missing_required.append(fit_name)
                        elif include_optional:
                            missing_optional.append(fit_name)
            else:
                fit_obj = f"FaceFit{name}"
                if not cmds.objExists(fit_obj):
                    if region.required:
                        missing_required.append(name)
                    elif include_optional:
                        missing_optional.append(name)

        return missing_required, missing_optional

    def mirror_fitting(self):
        """Mirror all fitted regions from right to left side."""
        for name, region in self.REGIONS.items():
            if not region.mirrored:
                continue

            # Handle upper/lower variants
            names_to_mirror = [name]
            if region.has_upper_lower:
                names_to_mirror = [f"upper{name}", f"lower{name}"]

            for fit_name in names_to_mirror:
                # Check for locator
                right_obj = f"FaceFit{fit_name}"
                left_obj = f"FaceFit{fit_name}Left"

                # Check for curve
                right_curve = f"{fit_name}Curve"
                left_curve = f"{fit_name}CurveLeft"

                if cmds.objExists(right_obj):
                    if cmds.objExists(left_obj):
                        cmds.delete(left_obj)

                    dup = cmds.duplicate(right_obj, name=left_obj)[0]
                    cmds.setAttr(f"{dup}.sx", -1 * abs(cmds.getAttr(f"{dup}.sx")))
                    print(f"// Mirrored {fit_name} to left side")

                elif cmds.objExists(right_curve):
                    if cmds.objExists(left_curve):
                        cmds.delete(left_curve)

                    # Get parent group
                    parent = cmds.listRelatives(right_curve, parent=True)
                    parent = parent[0] if parent else self.fit_skeleton_grp

                    dup = cmds.duplicate(right_curve, name=left_curve)[0]

                    # Mirror CVs
                    num_cvs = cmds.getAttr(f"{dup}.spans") + cmds.getAttr(f"{dup}.degree")
                    for i in range(num_cvs):
                        pos = cmds.xform(
                            f"{dup}.cv[{i}]", query=True, worldSpace=True, translation=True
                        )
                        cmds.xform(
                            f"{dup}.cv[{i}]", worldSpace=True, translation=[-pos[0], pos[1], pos[2]]
                        )

                    print(f"// Mirrored {fit_name} curve to left side")

    def get_ordered_regions(self) -> List[str]:
        """Get region names sorted by build order."""
        return sorted(self.REGIONS.keys(), key=lambda x: self.REGIONS[x].order)

    def get_regions_by_parent(self) -> Dict[str, List[str]]:
        """Get regions grouped by parent region."""
        groups = {}
        for name, region in self.REGIONS.items():
            parent = region.parent_region or "Other"
            if parent not in groups:
                groups[parent] = []
            groups[parent].append(name)
        return groups

    def set_callbacks(self, on_fit_complete: Optional[Callable] = None):
        """Set callback for when a fit completes."""
        self._on_fit_complete = on_fit_complete

    def reselect_fit(self, section: str, part: str = ""):
        """Seleziona i componenti salvati di una regione (parita'
        asFaceFitReSelect): delega alla funzione di modulo, il suffisso
        Left deriva da FaceFitSkeleton.NonSymSide."""
        face_fit_reselect(section, part)


class FittingUI:
    """
    Maya UI for interactive facial fitting.

    Provides a window with buttons for each facial region,
    color-coded status indicators, and fitting tools.
    """

    WINDOW_NAME = "facialFittingWindow"
    WINDOW_TITLE = "Facial Fitting"

    def __init__(self, geometry: str, non_symmetrical: bool = False):
        """
        Initialize the fitting UI.

        Args:
            geometry: Face mesh to fit
            non_symmetrical: Whether face is non-symmetrical
        """
        self.fitting = FacialFitting(geometry, non_symmetrical)
        self._region_buttons: Dict[str, Tuple[str, str]] = {}  # name: (button, status)
        self._current_upper_lower = "upper"

    def show(self):
        """Show the fitting UI window."""
        if cmds.window(self.WINDOW_NAME, exists=True):
            cmds.deleteUI(self.WINDOW_NAME)

        window = cmds.window(
            self.WINDOW_NAME, title=self.WINDOW_TITLE, widthHeight=(450, 700), sizeable=True
        )

        # Main scroll layout
        cmds.scrollLayout(childResizable=True)
        cmds.columnLayout(adjustableColumn=True, rowSpacing=5)

        # Header
        cmds.text(label="Facial Region Fitting", font="boldLabelFont", height=30)
        cmds.text(label=f"Geometry: {self.fitting.geometry}")
        cmds.separator(height=10)

        # Instructions frame
        cmds.frameLayout(label="Instructions", collapsable=True, collapse=True)
        cmds.columnLayout(adjustableColumn=True)
        cmds.text(
            label=(
                "1. Select vertices or edges on the face mesh\n"
                "2. Click the corresponding region button to store\n"
                "3. For loops (eyelids, lips): select from inner/center to outer/corner\n"
                "4. Use 'Upper'/'Lower' toggle for eyelids and lips\n\n"
                "Colors: Green=Complete, Yellow=Required, Gray=Optional"
            ),
            align="left",
            wordWrap=True,
        )
        cmds.setParent("..")
        cmds.setParent("..")

        cmds.separator(height=10)

        # Setup buttons
        cmds.rowLayout(numberOfColumns=2, adjustableColumn=True, columnWidth=[(1, 220), (2, 220)])
        cmds.button(
            label="1. Select Face Polygons → Create Mask",
            command=lambda x: self._create_fit_skeleton_from_selection(),
            backgroundColor=(0.3, 0.5, 0.3),
            annotation="Select face area polygons, then click to create fit skeleton",
        )
        cmds.button(
            label="Create Fit Skeleton (Auto)",
            command=lambda x: self._create_fit_skeleton_auto(),
            annotation="Create fit skeleton using full geometry bounds",
        )
        cmds.setParent("..")

        cmds.separator(height=10)

        # Upper/Lower toggle for loops
        cmds.frameLayout(label="Loop Type (for Eyelids & Lips)", collapsable=False)
        cmds.radioButtonGrp(
            "upperLowerRadio",
            labelArray2=["Upper", "Lower"],
            numberOfRadioButtons=2,
            select=1,
            onCommand1=lambda x: self._set_upper_lower("upper"),
            onCommand2=lambda x: self._set_upper_lower("lower"),
        )
        cmds.setParent("..")

        # Region sections
        groups = self.fitting.get_regions_by_parent()
        group_order = [
            "Eye",
            "EyeLid",
            "Lip",
            "EyeBrow",
            "Nose",
            "Jaw",
            "Cheek",
            "ForeHead",
            "Tongue",
            "Face",
        ]

        for group_name in group_order:
            if group_name in groups:
                regions = groups[group_name]
                self._create_region_section(group_name, regions)

        cmds.separator(height=10)

        # Action buttons
        cmds.frameLayout(label="Actions", collapsable=False)
        cmds.columnLayout(adjustableColumn=True, rowSpacing=3)

        cmds.button(
            label="Mirror Fitting → Left Side",
            command=lambda x: self._mirror_fitting(),
            annotation="Mirror all right side fits to left side",
        )

        cmds.button(
            label="Validate Fitting",
            command=lambda x: self._validate_fitting(),
            annotation="Check if all required regions are fitted",
        )

        cmds.button(
            label="Refresh Status",
            command=lambda x: self._refresh_all_status(),
            annotation="Update all button statuses",
        )

        cmds.setParent("..")
        cmds.setParent("..")

        cmds.showWindow(window)
        self._refresh_all_status()

    def _set_upper_lower(self, value: str):
        """Set current upper/lower mode."""
        self._current_upper_lower = value

    def _create_region_section(self, title: str, region_names: List[str]):
        """Create a collapsable section for a group of regions."""
        cmds.frameLayout(label=title, collapsable=True, collapse=False)
        cmds.columnLayout(adjustableColumn=True, rowSpacing=2)

        for region_name in sorted(
            region_names,
            key=lambda x: FacialFitting.REGIONS.get(x, FitRegion("", "", FitType.VERTEX, 0)).order,
        ):
            if region_name not in FacialFitting.REGIONS:
                continue

            region = FacialFitting.REGIONS[region_name]
            self._create_region_row(region)

        cmds.setParent("..")
        cmds.setParent("..")

    def _create_region_row(self, region: FitRegion):
        """Create a row for a single region with fit button and status."""
        cmds.rowLayout(
            numberOfColumns=5,
            adjustableColumn=2,
            columnWidth=[(1, 20), (2, 180), (3, 60), (4, 30), (5, 30)],
        )

        # Status indicator
        status_color = (0.4, 0.4, 0.4) if not region.required else (0.6, 0.6, 0.2)
        status = cmds.text(label="○", width=20, backgroundColor=status_color)

        # Description
        desc = f"{'* ' if region.required else ''}{region.display_name}"
        if region.has_upper_lower:
            desc += " (U/L)"

        # Main fit button
        btn = cmds.button(
            label=desc,
            command=lambda x, r=region.name: self._fit_region(r),
            annotation=region.description,
        )

        # Reselect button
        cmds.button(
            label="Sel",
            width=40,
            command=lambda x, r=region.name: self._reselect_region(r),
            annotation=f"Reselect vertices for {region.display_name}",
        )

        # Left side button (for mirrored regions)
        if region.mirrored:
            cmds.button(
                label="L",
                width=25,
                command=lambda x, r=region.name: self._fit_region(r, left_side=True),
                annotation=f"{region.display_name} (Left Side)",
            )
        else:
            cmds.text(label="", width=25)

        # Delete button
        cmds.button(
            label="X",
            width=25,
            command=lambda x, r=region.name: self._delete_fit(r),
            annotation=f"Delete {region.display_name} fit",
        )

        cmds.setParent("..")

        self._region_buttons[region.name] = (btn, status)

    def _create_fit_skeleton_from_selection(self):
        """Create fit skeleton and mask from current face selection."""
        sel = cmds.ls(selection=True, flatten=True)
        if not sel or ".f[" not in sel[0]:
            cmds.warning("Please select face polygons on the mesh first")
            return

        self.fitting.create_fit_skeleton()
        cmds.select(sel)
        self.fitting.create_fit_mask()
        print("// Created FaceFitSkeleton with mask from selection")

    def _create_fit_skeleton_auto(self):
        """Create fit skeleton only (mask must be added from face selection)."""
        self.fitting.create_fit_skeleton()
        print(
            "// Created FaceFitSkeleton (select face polygons and create the mask to set faceScale)"
        )

    def _fit_region(self, region_name: str, left_side: bool = False):
        """Fit a region from current selection."""
        region = FacialFitting.REGIONS.get(region_name)
        if not region:
            return

        upper_lower = ""
        if region.has_upper_lower:
            upper_lower = self._current_upper_lower

        success = self.fitting.fit_region(region_name, left_side, upper_lower)

        if success:
            self._update_status(region_name, completed=True)

    def _reselect_region(self, region_name: str):
        """Reselect the stored vertices for a region."""
        region = FacialFitting.REGIONS.get(region_name)
        if not region:
            return

        # le regioni loop sono salvate come FaceFit<section><part>
        routing = FacialFitting._LOOP_ROUTING.get(region_name)
        if routing:
            self.fitting.reselect_fit(routing[0], routing[1])
        else:
            self.fitting.reselect_fit(region_name)

    def _delete_fit(self, region_name: str):
        """Delete a region fit (parita' asFaceDeleteFromCheckBox; la
        conferma utente arrivera' con la UI PySide in Fase 4)."""
        region = FacialFitting.REGIONS.get(region_name)
        if not region:
            return

        face_fit_delete(region_name)
        self._update_status(region_name, completed=False)

    def _update_status(self, region_name: str, completed: bool):
        """Update visual status for a region button."""
        if region_name not in self._region_buttons:
            return

        btn, status = self._region_buttons[region_name]
        region = FacialFitting.REGIONS.get(region_name)

        if completed:
            cmds.text(status, edit=True, label="●", backgroundColor=(0.2, 0.6, 0.2))
        else:
            color = (0.6, 0.6, 0.2) if region and region.required else (0.4, 0.4, 0.4)
            cmds.text(status, edit=True, label="○", backgroundColor=color)

    def _refresh_all_status(self):
        """Refresh status indicators for all regions."""
        for region_name in self._region_buttons:
            region = FacialFitting.REGIONS.get(region_name)
            if not region:
                continue

            # Check if fitted
            fitted = False
            if region.has_upper_lower:
                # Check for curves
                upper_curve = f"upper{region_name}Curve"
                lower_curve = f"lower{region_name}Curve"
                fitted = cmds.objExists(upper_curve) or cmds.objExists(lower_curve)
            else:
                fit_obj = f"FaceFit{region_name}"
                fitted = cmds.objExists(fit_obj)

            self._update_status(region_name, completed=fitted)

    def _mirror_fitting(self):
        """Mirror all fits to left side."""
        self.fitting.mirror_fitting()
        self._refresh_all_status()
        print("// Mirrored all fitting to left side")

    def _validate_fitting(self):
        """Validate the fitting and report missing regions."""
        missing_required, missing_optional = self.fitting.validate_fitting(include_optional=True)

        if missing_required:
            cmds.warning(f"Missing REQUIRED regions: {', '.join(missing_required)}")
        else:
            print("// All required regions are fitted!")

        if missing_optional:
            print(f"// Missing optional regions: {', '.join(missing_optional)}")


def _legacy_show_fitting_ui(geometry: str, non_symmetrical: bool = False):
    """
    Show the facial fitting UI (legacy entry point).

    Deprecated: use ``facial_rig.show_fitting_ui`` (from core.ui.face_window)
    which accepts geometry as an optional arg and opens the new Face window.

    Args:
        geometry: Face mesh to fit
        non_symmetrical: Whether face is non-symmetrical

    Example:
        from facial_rig.core.fitting import _legacy_show_fitting_ui
        _legacy_show_fitting_ui("head_geo")
    """
    ui = FittingUI(geometry, non_symmetrical)
    ui.show()
    return ui

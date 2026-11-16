"""Build step LipFalloff (parita' asFaceLipFalloff, MEL:32567-32770).

Definisce l'area attorno alle labbra (`lipFalloffArea`) in cui il peso dei
joint delle labbra sfuma verso la testa: cresce la selezione dai loop Inner
e Outer, riporta l'area sull'HeadJoint e la passa al weight hammer. Salva i
pesi risultanti su `LipFalloffLayer` (copia di templateLayer) e lascia una
posa di prova sui controller del labbro superiore (frame 30), che lo step
successivo rimuove.

Divergenze (docs/gap-analysis.md §5j):
- i tre intField della UI MEL (Outside, Inside, Iterations) sono parametri
  della funzione: Outside e' `FaceFitSkeleton.vtxsFromLipToNose` (che la UI
  tiene sincronizzato col campo), Inside e Iterations hanno i default MEL;
- multiSkinClusters non portato;
- `$lipFalloffInsideMouthArea` nel MEL e' sempre vuoto: il secondo hammer
  non avviene mai ed e' omesso.
"""

import maya.cmds as cmds

from .face_ctrl_pp import weight_hammer_verts_ms
from .fit_options import FIT_SKELETON, get_fit_option
from .fitting import get_face_fit_selection

_INSIDE_DEFAULT = 2
_ITERATIONS_DEFAULT = 5


def _selected():
    return cmds.ls(selection=True, flatten=True) or []


def _grow():
    cmds.polySelectConstraint(propagate=1, type=0x0001)


def _select_fit(fit_object):
    text = get_face_fit_selection(fit_object)
    if text.strip():
        cmds.select(text.split())
    else:
        cmds.select(clear=True)
    return _selected()


def _lock_weights_except_lips(head_joint):
    """asFaceLockWeights 1, poi sblocca la testa e i joint delle labbra."""
    for joint in cmds.ls(type="joint"):
        if cmds.attributeQuery("lockInfluenceWeights", node=joint, exists=True):
            cmds.setAttr(joint + ".lockInfluenceWeights", 1)
    cmds.setAttr(head_joint + ".lockInfluenceWeights", 0)
    for joint in cmds.listRelatives("LipJoints_M", children=True, type="joint") or []:
        cmds.setAttr(joint + ".lockInfluenceWeights", 0)


def _count_vertices_from_lip_to_nose(vtx_lip, vtx_nose):
    """Quanti anelli di vertici separano il labbro superiore dal naso."""
    count = 0
    cmds.select(vtx_lip)
    for _ in range(25):
        if vtx_nose in _selected():
            break
        count += 1
        _grow()
    if vtx_lip == vtx_nose:  # caso del personaggio demo "max"
        count = 0
    return count


def _build_area(inner_outer, amount):
    """Aggiunge a lipFalloffArea i vertici entro `amount` anelli dal loop."""
    mirrored = []
    for upper_lower in ("upper", "lower"):
        curve = "{}Lip{}Curve".format(upper_lower, inner_outer)
        copy = cmds.duplicate(curve, name=curve + "_L")[0]
        cmds.setAttr(copy + ".sx", -1)
        mirrored.append(copy)

    vtxs = []
    for upper_lower in ("upper", "lower"):
        vtxs += _select_fit("{}Lip{}Curve".format(upper_lower, inner_outer))
    for upper_lower in ("upper", "lower"):  # lato sinistro: fit Left, o la copia specchiata
        curve = "{}Lip{}Curve".format(upper_lower, inner_outer)
        left = curve + "Left" if cmds.objExists(curve + "Left") else curve + "_L"
        vtxs += _select_fit(left)

    cmds.select(vtxs)
    for _ in range(amount):
        _grow()
        cmds.select("lipArea", deselect=True)
    cmds.select("lipArea", deselect=True)
    area = cmds.ls(selection=True) or []
    if area:
        cmds.sets(area, add="lipFalloffArea")
        cmds.sets(area, add="lipFalloffAreaMax")
    cmds.delete(mirrored)


def _store_on_layer(geometry, skin_cluster, head_joint):
    """Copia i pesi su LipFalloffLayer, dove la testa e' sostituita da
    lipOffJoint (MEL:32736-32755)."""
    if not cmds.objExists("lipOffJoint"):
        cmds.select(head_joint)
        cmds.joint(name="lipOffJoint")
        cmds.parent("lipOffJoint", "FaceBuildInProgressHidden")
    if cmds.objExists("LipFalloffLayer"):
        cmds.delete("LipFalloffLayer")
    cmds.duplicate("templateLayer", name="LipFalloffLayer")
    joints = []
    for joint in cmds.listConnections(skin_cluster, source=True, destination=False, type="joint"):
        if joint != head_joint and joint not in joints:
            joints.append(joint)
    joints.append("lipOffJoint")
    sc = cmds.skinCluster(
        joints,
        "LipFalloffLayer",
        toSelectedBones=True,
        maximumInfluences=3,
        dropoffRate=4,
        removeUnusedInfluence=False,
    )[0]
    cmds.rename(sc, "LipFalloffLayerSC")
    cmds.select(geometry, "LipFalloffLayer")
    cmds.copySkinWeights(
        noMirror=True, surfaceAssociation="closestPoint", influenceAssociation="closestJoint"
    )
    cmds.skinPercent("LipFalloffLayerSC", pruneWeights=0.01)


def face_lip_falloff(inside=_INSIDE_DEFAULT, iterations=_ITERATIONS_DEFAULT) -> bool:
    """Sfuma i pesi delle labbra verso la testa (asFaceLipFalloff).

    Args:
        inside: anelli di vertici di falloff verso l'interno della bocca
            (campo "Inside" della UI MEL, default 2).
        iterations: iterazioni del weight hammer (campo "Iterations", 5).

    Returns:
        True anche quando lo step e' saltato per assenza di
        `upperLipMainCurve` (gate MEL); False con warning se manca un
        prerequisito.
    """
    if not cmds.objExists("upperLipMainCurve"):
        return True
    geometry = get_fit_option("Face") or ""
    head_joint = get_fit_option("HeadJoint") or ""
    skin_cluster = get_fit_option("SkinCluster") or ""
    required = [geometry, head_joint, skin_cluster, "LipJoints_M", "lipArea", "FaceAreas"]
    required += ["FaceBuildingSets", "templateLayer", "FaceBuildInProgressHidden", "NoseUnder"]
    missing = [n for n in required if not n or not cmds.objExists(n)]
    if missing:
        cmds.warning("face_lip_falloff: missing {}".format(", ".join(missing) or "options"))
        return False
    if get_fit_option("MultiSkinClusters"):
        cmds.warning("face_lip_falloff: multiSkinClusters is not ported yet")

    test = cmds.objExists("asFaceLipFalloffTest")
    if test:
        cmds.delete("asFaceLipFalloffTest")
    update = cmds.objExists("asFaceLipFalloffUpdate")
    if update:
        cmds.delete("asFaceLipFalloffUpdate")

    # da leggere prima che la posa cambi
    vtx_lip = get_face_fit_selection("upperLipOuterCurve.cv[0]")
    vtx_nose = get_face_fit_selection("NoseUnder")

    cmds.currentTime(0)
    _lock_weights_except_lips(head_joint)

    attr = FIT_SKELETON + ".vtxsFromLipToNose"
    if test or update:
        outside = cmds.getAttr(attr)
    else:
        if not cmds.objExists(attr):
            cmds.addAttr(
                FIT_SKELETON, longName="vtxsFromLipToNose", attributeType="long", defaultValue=3
            )
        outside = _count_vertices_from_lip_to_nose(vtx_lip, vtx_nose)
        cmds.setAttr(attr, outside)
    cmds.select(clear=True)

    if not test:
        for ctrl in ("upperLipA_R", "upperLipB_R", "lowerLipA_R", "lowerLipB_R", "Lip_R"):
            if cmds.objExists(ctrl):
                cmds.xform(
                    ctrl,
                    objectSpace=True,
                    translation=(0, 0, 0),
                    rotation=(0, 0, 0),
                    scale=(1, 1, 1),
                )

    for area in ("lipFalloffArea", "lipFalloffInsideMouthArea"):
        if cmds.objExists(area):
            cmds.delete(area)
    cmds.createNode("objectSet", name="lipFalloffArea")
    cmds.sets("lipFalloffArea", add="FaceAreas")
    if not cmds.objExists("lipFalloffAreaMax"):
        cmds.createNode("objectSet", name="lipFalloffAreaMax")
        cmds.sets("lipFalloffAreaMax", add="FaceBuildingSets")

    _build_area("Inner", inside)
    _build_area("Outer", outside)
    cmds.select("lipFalloffArea")
    cmds.refresh()
    if test:
        cmds.currentTime(30)
        return True

    # prima tutto sulla testa: lo step puo' essere gia' passato con un
    # falloff piu' ampio
    cmds.select("lipFalloffAreaMax")
    try:
        cmds.skinPercent(skin_cluster, transformValue=(head_joint, 1))
    except RuntimeError:
        pass
    cmds.select("lipFalloffArea")
    weight_hammer_verts_ms(iterations, skin_cluster)
    cmds.select(clear=True)

    _store_on_layer(geometry, skin_cluster, head_joint)

    # posa di prova per l'utente: i controller B.. del labbro superiore
    lip_ctrls = int(get_fit_option("LipCtrls") or 12)
    for i in range(2, lip_ctrls // 4):
        plug = "upperLip{}_R.ty".format(chr(ord("A") + i - 1))
        cmds.setKeyframe(plug, time=0, value=0)
        cmds.setKeyframe(plug, time=30, value=1)
    cmds.currentTime(30)
    cmds.select(clear=True)
    return True

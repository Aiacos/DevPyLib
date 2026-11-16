"""Ponte fra il nodo di Arise Rigging System e il build facciale.

Il nodo Arise (`arise_node/io_modules_nodes/Adv_Face`) resta sottile:
raccoglie gli attributi impostati dall'utente e chiama queste funzioni, che
non dipendono da Arise e sono quindi provabili con mayapy.

Flusso di `rig_creation()` nel nodo:

    build_face(options)          # rig con i nomi ADV, come il port del MEL
    nodes = face_rig_nodes()     # da passare a tagging_utils.tag_nodes
    rename_to_arise(prefix)      # nomi secondo Arise (core/arise_naming)

Vedi docs/arise-node.md per il disegno e i limiti.
"""

import maya.cmds as cmds

from .fit_options import FIT_SKELETON, get_fit_option, set_fit_option

FACE_ROOT = "FaceGroup"


def apply_options(options):
    """Scrive su FaceFitSkeleton le opzioni date ({nome opzione: valore},
    es. {"Face": "head_geo", "ARKit": True}). I valori None sono ignorati.
    Ritorna False con un warning se FaceFitSkeleton manca."""
    if not cmds.objExists(FIT_SKELETON):
        cmds.warning("apply_options: FaceFitSkeleton not found (fit the face first)")
        return False
    ok = True
    for name, value in (options or {}).items():
        if value is None:
            continue
        ok = set_fit_option(name, value) and ok
    return ok


def build_face(options=None) -> bool:
    """Costruisce il rig facciale (i 30 step) leggendo il fitting dalla
    scena. `options` passa da `apply_options` prima del build."""
    from ..builder import FacialRigBuilder
    from .ui.build_frame import config_from_scene

    if options and not apply_options(options):
        return False
    if not cmds.objExists(FIT_SKELETON):
        cmds.warning("build_face: FaceFitSkeleton not found (fit the face first)")
        return False
    return bool(FacialRigBuilder(config_from_scene()).build())


def face_rig_nodes():
    """I nodi creati dal build (membri di FaceAllSet piu' la radice), per
    registrarli presso Arise con `tagging_utils.tag_nodes`. Lista vuota se
    il rig non c'e'."""
    nodes = []
    if cmds.objExists("FaceAllSet"):
        nodes = [n for n in cmds.sets("FaceAllSet", query=True) or [] if cmds.objExists(n)]
    if cmds.objExists(FACE_ROOT) and FACE_ROOT not in nodes:
        nodes.append(FACE_ROOT)
    return nodes


def _release_skin_influences(nodes):
    """Toglie i joint del rig dagli skinCluster che li usano, restituendo
    il loro peso al joint della testa (come fa asDeleteAdvancedFace,
    MEL: blocca tutte le influenze tranne HeadJoint e poi le rimuove).
    Cancellare un joint ancora influenza lascerebbe la mesh senza quei pesi."""
    head_joint = get_fit_option("HeadJoint") or ""
    rig_joints = set(cmds.ls(nodes, type="joint"))
    for skin in cmds.ls(type="skinCluster"):
        if skin in nodes:  # skinCluster creato dal build: se ne va col rig
            continue
        influences = cmds.skinCluster(skin, query=True, influence=True) or []
        ours = [j for j in influences if j in rig_joints]
        if not ours:
            continue
        keep = [j for j in influences if j not in rig_joints]
        if not keep:
            if not cmds.objExists(head_joint):
                continue
            cmds.skinCluster(skin, edit=True, addInfluence=head_joint, lockWeights=False, weight=1)
            keep = [head_joint]
        for joint in influences:
            if cmds.attributeQuery("lockInfluenceWeights", node=joint, exists=True):
                cmds.setAttr(joint + ".lockInfluenceWeights", joint != head_joint)
        for joint in ours:
            cmds.skinCluster(skin, edit=True, removeInfluence=joint)
        for joint in keep:
            if cmds.attributeQuery("lockInfluenceWeights", node=joint, exists=True):
                cmds.setAttr(joint + ".lockInfluenceWeights", 0)


def delete_face() -> bool:
    """Cancella il rig facciale lasciando il fitting e i pesi sul joint
    della testa. Serve al nodo Arise quando esce dalla modalita' Build: i
    nodi del build non nascono dalle API di Arise. Ritorna True se c'era
    qualcosa da cancellare."""
    fit_path = cmds.ls(FIT_SKELETON, long=True) or [""]
    nodes = []
    for node in face_rig_nodes():
        long_name = (cmds.ls(node, long=True) or [""])[0]
        if long_name and fit_path[0].startswith(long_name + "|"):
            continue  # antenato del fitting (FaceGroup): resta
        nodes.append(node)
    if not nodes:
        return False
    _release_skin_influences(nodes)
    for node in nodes:
        if cmds.objExists(node):  # un padre cancellato porta via i figli
            try:
                cmds.delete(node)
            except RuntimeError:
                pass
    return True

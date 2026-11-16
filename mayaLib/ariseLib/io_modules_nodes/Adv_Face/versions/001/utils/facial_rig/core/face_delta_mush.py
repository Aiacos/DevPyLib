"""Deformer DeltaMush di smoothing per il volto (parita' asFaceDeltaMush
MEL AdvancedSkeleton.mel:44350-44395, asConnectDeltaMushScale 66500,
asFacePaintDeltaMush 39443).

La geometria si legge dall'opzione Face di FaceFitSkeleton (equivalente del
textField asFaceFaceTextField). Divergenza intenzionale: usa cmds.deltaMush
diretto invece del wrapper MEL asDeformer (precedente: face_assist).
"""

import maya.cmds as cmds
import maya.mel as mel

from .fit_options import get_fit_option

_DM_NODE = "asFaceDeltaMush"
_DM_SET = "asFaceDeltaMushSet"


def _face_geometry():
    """Primo oggetto dell'opzione Face, o "" se assente/inesistente."""
    tokens = (get_fit_option("Face") or "").split()
    face = tokens[0] if tokens else ""
    return face if face and cmds.objExists(face) else ""


def connect_delta_mush_scale():
    """Connette MainScaleMultiplyDivide -> deltaMush.s (parita'
    asConnectDeltaMushScale, MEL:66500). No-op se Main non esiste."""
    if not cmds.objExists("Main"):
        return
    for node in cmds.ls(type="deltaMush") or []:
        if cmds.isConnected("MainScaleMultiplyDivide.outputX", node + ".sx"):
            continue
        for out, axis in (("outputX", "sx"), ("outputY", "sy"), ("outputZ", "sz")):
            cmds.connectAttr("MainScaleMultiplyDivide." + out, "{}.{}".format(node, axis))


def delta_mush_zero_weight():
    """Azzera la membership del deltaMush sulla selezione corrente
    (parita' asFaceDeltaMushZeroWeight, MEL:44381). Ritorna bool."""
    if cmds.objExists(_DM_NODE):
        cmds.percent(_DM_NODE, value=0)
        return True
    geometry = _face_geometry()
    if not geometry:
        cmds.warning("delta_mush_zero_weight: no DeltaMush and no Face geometry")
        return False
    history = cmds.listHistory(geometry, pruneDagObjects=True, interestLevel=2) or []
    found = False
    for node in history:
        if cmds.nodeType(node) == "deltaMush":
            cmds.percent(node, value=0)
            found = True
    if not found:
        cmds.warning("delta_mush_zero_weight: no deltaMush in history")
    return found


def create_delta_mush():
    """Crea il deformer DeltaMush sulla geometria Face (parita'
    asFaceDeltaMush, MEL:44350). Ritorna bool. Nessuna eccezione."""
    geometry = _face_geometry()
    if not geometry:
        cmds.warning("create_delta_mush: no Face geometry set")
        return False
    if not mel.eval("exists deltaMush"):
        cmds.warning("DeltaMush not available in this version of Maya")
        return False
    if cmds.objExists(_DM_NODE):
        cmds.warning("{} already exists".format(_DM_NODE))
        return False

    created = cmds.deltaMush(
        geometry, smoothingIterations=10, smoothingStep=0.5, pinBorderVertices=1, envelope=1
    )
    node = cmds.rename(created[0], _DM_NODE)

    # Cerca il set di deformazione reale creato da Maya (caso interattivo:
    # il wrapper MEL asDeformer lo crea; standalone potrebbe non farlo).
    existing_sets = [s for s in (cmds.listConnections(node, type="objectSet") or [])]
    existing_sets += [
        s
        for s in (cmds.listConnections(node + ".message", type="objectSet") or [])
        if s not in existing_sets
    ]
    set_found = False
    for s in existing_sets:
        try:
            cmds.rename(s, _DM_SET)
            set_found = True
            break
        except RuntimeError:
            pass
    if not set_found and not cmds.objExists(_DM_SET):
        # In Maya standalone cmds.deltaMush non crea un objectSet di deformazione
        # (a differenza del wrapper MEL asDeformer in sessione interattiva). Qui
        # creiamo un set segnaposto SOLO di naming (NON un set di membership del
        # deformer): il weighting passa comunque per `percent <deformer>`. In
        # interattivo il ramo sopra rinomina il set reale creato da Maya.
        _dm_set = cmds.sets(name=_DM_SET, empty=True)
        cmds.connectAttr(node + ".message", _dm_set + ".usedBy[0]", force=True)

    connect_delta_mush_scale()

    if cmds.objExists("eyeLidArea") and cmds.objExists("lipArea"):
        cmds.select("eyeLidArea", "lipArea")
        delta_mush_zero_weight()
        print("// Automatically zero weighting eyeLid and lip.")

    cmds.select(geometry)
    print("// DeltaMush applied")
    return True


def delete_delta_mush():
    """Elimina il nodo asFaceDeltaMush (parita' del callback inline del
    bottone Delete DeltaMush, MEL:1999). Ritorna bool."""
    if not cmds.objExists(_DM_NODE):
        cmds.warning("delete_delta_mush: {} not found".format(_DM_NODE))
        return False
    cmds.delete(_DM_NODE)
    print("// DeltaMush deleted")
    return True


def paint_delta_mush():
    """Apre il paint tool dei pesi DeltaMush (parita' asFacePaintDeltaMush,
    MEL:39443). Tool interattivo: inerte in batch."""
    if not cmds.objExists(_DM_NODE):
        cmds.warning("paint_delta_mush: {} non esiste (crea prima il DeltaMush)".format(_DM_NODE))
        return
    geometry = _face_geometry()
    if geometry:
        cmds.select(geometry)
    try:
        cmds.artAttrToolScript(4, "deltaMush")
    except (RuntimeError, TypeError):
        cmds.warning("paint_delta_mush: paint tool non disponibile in batch")

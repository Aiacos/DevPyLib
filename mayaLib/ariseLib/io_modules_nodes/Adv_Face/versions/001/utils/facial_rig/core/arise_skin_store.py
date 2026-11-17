"""Pesi del viso conservati fra un rebuild e l'altro (nodo Arise).

Uscendo da Build il rig viene cancellato e i pesi dei suoi joint tornano al
joint della testa; il build successivo li ricalcola da capo. Le correzioni
dipinte a mano andrebbero perse. Qui, prima della cancellazione, si salvano
i pesi dei vertici che i joint del viso deformano, e a build finito si
riapplicano.

I pesi stanno nella scena, in un nodo `network` del volto (ruolo `data`:
non si cancella col rig), compressi in un attributo stringa. I joint del rig
sono salvati col nome di AdvancedSkeleton, quindi si ritrovano dopo il
rebuild qualunque sia il prefisso del nodo.

I pesi salvati valgono solo se nulla e' cambiato sotto: stessa geometria con
lo stesso numero di vertici, e tutte le influenze salvate presenti nello
skinCluster ricostruito. Se il fitting o un'opzione cambiano i joint (per
esempio Lip Ctrls), il ripristino viene saltato con un warning e restano i
pesi appena calcolati dal build.

Divergenza dal MEL: AdvancedSkeleton conserva i pesi al rebuild leggendoli
dal rig precedente rinominato `prefix_*` ("keep Skin weights", in
asFaceRebuildRestore). Con Arise il rig precedente non c'e' piu' quando il
build riparte, quindi i pesi passano da questo deposito.
"""

import base64
import json
import zlib

import maya.api.OpenMaya as om
import maya.api.OpenMayaAnim as oma
import maya.cmds as cmds

from . import arise_faces

ROLE_DATA = "data"
STORE_NAME = "faceSkinWeights"
DATA_ATTR = "skinWeights"
_MIN_WEIGHT = 1e-6


def _skin_fn(skin):
    selection = om.MSelectionList()
    selection.add(skin)
    return oma.MFnSkinCluster(selection.getDependNode(0))


def _mesh_path(geometry):
    selection = om.MSelectionList()
    selection.add(geometry)
    path = selection.getDagPath(0)
    path.extendToShape()
    return path


def _components(indices):
    component = om.MFnSingleIndexedComponent()
    obj = component.create(om.MFn.kMeshVertComponent)
    component.addElements(indices)
    return obj


def _influence_names(skin_fn):
    return [path.partialPathName() for path in skin_fn.influenceObjects()]


def _store_node(owner):
    for node in arise_faces.face_nodes(owner, ROLE_DATA):
        if cmds.attributeQuery(DATA_ATTR, node=node, exists=True):
            return node
    return ""


def _user_skins(rig_nodes):
    """(skinCluster, geometria) degli skinCluster non creati dal build."""
    built = set(cmds.ls(rig_nodes, type="skinCluster") or [])
    pairs = []
    for skin in cmds.ls(type="skinCluster") or []:
        if skin in built:
            continue
        geometry = cmds.skinCluster(skin, query=True, geometry=True) or []
        if geometry and cmds.nodeType(geometry[0]) == "mesh":
            transform = cmds.listRelatives(geometry[0], parent=True, fullPath=True)[0]
            pairs.append((skin, transform))
    return pairs


def save_face_weights(owner, prefix="") -> bool:
    """Salva i pesi dei vertici deformati dai joint del volto `owner`. Da
    chiamare prima di cancellare il rig. Ritorna True se ha salvato qualcosa.
    Senza rig in scena non fa nulla e lascia il deposito precedente; con un
    rig i cui joint non deformano nulla, lo toglie."""
    rig = arise_faces.face_nodes(owner, arise_faces.ROLE_RIG)
    if not rig:  # Arise chiama la pulizia anche piu' volte: il deposito resta
        return False
    adv_names = {}
    for joint in cmds.ls(rig, type="joint", long=True) or []:
        adv_names[cmds.ls(joint)[0]] = cmds.getAttr(joint + "." + arise_faces.NAME_ATTR)

    entries = []
    for skin, geometry in _user_skins(rig):
        skin_fn = _skin_fn(skin)
        influences = _influence_names(skin_fn)
        ours = [index for index, name in enumerate(influences) if name in adv_names]
        if not ours:
            continue
        path = _mesh_path(geometry)
        vertex_count = om.MFnMesh(path).numVertices
        weights, count = skin_fn.getWeights(path, _components(list(range(vertex_count))))
        vertices, rows = [], []
        for vertex in range(vertex_count):
            row = weights[vertex * count : (vertex + 1) * count]
            if sum(row[index] for index in ours) <= _MIN_WEIGHT:
                continue
            vertices.append(vertex)
            rows.append([round(value, 6) for value in row])
        if not vertices:
            continue
        entries.append(
            {
                "geometry": cmds.ls(geometry)[0],
                "vertexCount": vertex_count,
                # i joint del rig col nome ADV, gli altri col proprio
                "influences": [adv_names.get(name, name) for name in influences],
                "rigInfluences": [adv_names[influences[index]] for index in ours],
                "vertices": vertices,
                "weights": rows,
            }
        )

    old = _store_node(owner)
    if old:
        cmds.delete(old)
    if not entries:
        return False
    packed = base64.b64encode(zlib.compress(json.dumps(entries).encode("utf-8"))).decode("ascii")
    node = cmds.createNode("network", name=STORE_NAME, skipSelect=True)
    cmds.addAttr(node, longName=DATA_ATTR, dataType="string")
    cmds.setAttr(node + "." + DATA_ATTR, packed, type="string")
    arise_faces.rename_face(prefix or owner[:8], owner, [node], role=ROLE_DATA)
    return True


def stored_face_weights(owner):
    """I pesi salvati per il volto `owner` (lista di dict), o lista vuota."""
    node = _store_node(owner)
    if not node:
        return []
    packed = cmds.getAttr(node + "." + DATA_ATTR) or ""
    try:
        return json.loads(zlib.decompress(base64.b64decode(packed)).decode("utf-8"))
    except (ValueError, zlib.error):
        cmds.warning("stored_face_weights: the stored skin weights cannot be read")
        return []


def discard_face_weights(owner) -> bool:
    """Butta i pesi salvati del volto `owner`. True se c'erano."""
    node = _store_node(owner)
    if node:
        cmds.delete(node)
    return bool(node)


def _current_skin(geometry):
    """Lo skinCluster che deforma `geometry` ("" se non c'e')."""
    shapes = set(cmds.listRelatives(geometry, shapes=True, fullPath=True) or [])
    for skin in cmds.ls(cmds.listHistory(geometry, pruneDagObjects=True) or [], type="skinCluster"):
        deformed = cmds.ls(cmds.skinCluster(skin, query=True, geometry=True) or [], long=True)
        if shapes & set(deformed):
            return skin
    return ""


def restore_face_weights(owner) -> bool:
    """Riapplica i pesi salvati del volto `owner`. Da chiamare a build
    finito, quando i joint del rig hanno ancora i nomi di AdvancedSkeleton
    (prima di `arise_faces.rename_face`).

    Ritorna True se ha ripristinato tutto cio' che era salvato. Una
    geometria i cui pesi non valgono piu' (vertici o influenze diversi)
    viene saltata con un warning."""
    entries = stored_face_weights(owner)
    if not entries:
        return False
    built_joints = set()
    if cmds.objExists("FaceAllSet"):
        built_joints = set(cmds.ls(cmds.sets("FaceAllSet", query=True) or [], type="joint"))
    ok = True
    for entry in entries:
        geometry = entry["geometry"]
        skin = _current_skin(geometry) if cmds.objExists(geometry) else ""
        if not skin:
            cmds.warning("restore_face_weights: no skinCluster on {}, skipped".format(geometry))
            ok = False
            continue
        skin_fn = _skin_fn(skin)
        path = _mesh_path(geometry)
        if om.MFnMesh(path).numVertices != entry["vertexCount"]:
            cmds.warning(
                "restore_face_weights: {} has a different vertex count, skipped".format(geometry)
            )
            ok = False
            continue
        current = _influence_names(skin_fn)
        missing = [name for name in entry["rigInfluences"] if name not in current]
        added = [
            name for name in current if name not in entry["influences"] and name in built_joints
        ]
        if missing or added:
            cmds.warning(
                "restore_face_weights: the face joints of {} changed ({} missing, {} new), "
                "keeping the weights of the new build".format(geometry, len(missing), len(added))
            )
            ok = False
            continue
        column = {name: index for index, name in enumerate(current)}
        stored = [(index, name) for index, name in enumerate(entry["influences"]) if name in column]
        values = om.MDoubleArray()
        for row in entry["weights"]:
            new_row = [0.0] * len(current)
            for index, name in stored:
                new_row[column[name]] = row[index]
            total = sum(new_row)
            if total > _MIN_WEIGHT:
                new_row = [value / total for value in new_row]
            for value in new_row:
                values.append(value)
        skin_fn.setWeights(
            path,
            _components(entry["vertices"]),
            om.MIntArray(list(range(len(current)))),
            values,
            False,
        )
    return ok

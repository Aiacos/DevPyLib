"""Piu' volti nella stessa scena: i nodi di ciascun volto portano nel nome
il nome del proprio nodo Arise, come fa Arise per i suoi moduli.

AdvancedSkeleton prevede un solo volto per scena: i nomi (`FaceFitSkeleton`,
`FaceGroup`, `Jaw_M`, `FaceAllSet`...) sono fissi e sono il contratto fra
fitting, build e confronto col MEL. Qui non si cambia quel contratto: il
build gira sempre con i nomi ADV, uno alla volta, e a build finito *tutti* i
nodi che ha creato vengono rinominati `<nodo>_<lato>_<nome>_<suffisso>`
(core/arise_naming). I nomi ADV tornano liberi per il volto successivo.

Ogni nodo rinominato porta tre attributi stringa:

- `advFace`: il proprietario (l'uuid del nodo Arise, stabile anche se
  l'utente rinomina il nodo);
- `advName`: il nome ADV originale, per poterlo ripristinare;
- `advRole`: `rig` (creato dal build) o `fit` (fitting messo da parte).

Il fitting di un volto ha due stati:

- *attivo*: con i nomi ADV (`FaceGroup|FaceFitSkeleton`), l'unico che la
  finestra di fitting e il build sanno leggere. `FaceFitSkeleton.ariseOwner`
  dice a chi appartiene;
- *messo da parte*: rinominato col prefisso del proprio nodo, quando serve
  attivare il fitting di un altro volto.

Un fitting attivo senza proprietario (fatto prima di creare il nodo Arise, o
fuori da Arise) viene preso dal primo nodo che lo usa; se pero' la finestra
di fitting era stata aperta da un nodo che non aveva ancora un fitting, quel
nodo e' annotato nella scena (`fileInfo advFacePendingOwner`) e il fitting
nato nel frattempo e' suo.

Divergenza dal MEL: nessuna procedura ADV corrisponde a questo modulo, e il
rig rinominato non e' piu' leggibile dagli strumenti di AdvancedSkeleton
(selector, picker, rebuild). Vedi docs/arise-node.md.
"""

import maya.cmds as cmds

from .arise_naming import arise_name
from .fit_options import FIT_SKELETON

OWNER_ATTR = "advFace"
NAME_ATTR = "advName"
ROLE_ATTR = "advRole"
ROLE_RIG = "rig"
ROLE_FIT = "fit"
FIT_OWNER_ATTR = "ariseOwner"  # su FaceFitSkeleton attivo
FIT_PREFIX_ATTR = "arisePrefix"
FIT_ROOT = "FaceGroup"


def scene_uuids():
    """Gli uuid di tutti i nodi della scena: da prendere prima del build."""
    return set(cmds.ls(uuid=True) or [])


def new_nodes(before):
    """I nodi nati dopo `scene_uuids()` (nomi lunghi dove servono)."""
    uuids = [uuid for uuid in cmds.ls(uuid=True) or [] if uuid not in before]
    return cmds.ls(uuids, long=True) if uuids else []


def _set_string(node, attr, value):
    if not cmds.attributeQuery(attr, node=node, exists=True):
        cmds.addAttr(node, longName=attr, dataType="string")
    cmds.setAttr("{}.{}".format(node, attr), value, type="string")


def _get_string(node, attr):
    if not cmds.attributeQuery(attr, node=node, exists=True):
        return ""
    return cmds.getAttr("{}.{}".format(node, attr)) or ""


def _by_uuid(uuid):
    found = cmds.ls(uuid, long=True)
    return found[0] if found else ""


def _short(node):
    return node.rsplit("|", 1)[-1]


def _rename_marked(uuid, adv_name, new_name, owner, role):
    """Marca il nodo e lo rinomina. False se il nodo non lo permette
    (bloccato, referenziato, di default)."""
    node = _by_uuid(uuid)
    if not node or cmds.referenceQuery(node, isNodeReferenced=True):
        return False
    if cmds.lockNode(node, query=True, lock=True)[0]:
        return False
    try:
        _set_string(node, NAME_ATTR, adv_name)
        _set_string(node, OWNER_ATTR, owner)
        _set_string(node, ROLE_ATTR, role)
        cmds.rename(node, new_name)
    except RuntimeError:
        return False
    return True


def rename_face(prefix, owner, nodes, role=ROLE_RIG):
    """Rinomina `nodes` secondo Arise e li assegna al volto `owner`.

    Le shape seguono il proprio transform (`<nuovo>Shape`); i nodi che non
    si possono rinominare restano come sono. I nomi si calcolano tutti prima
    di rinominare: il tipo di un nodo (controller o gruppo) si legge da
    FaceControlSet, che e' fra i nodi da rinominare, e Maya rinomina da se'
    la shape quando cambia nome il transform.

    Returns:
        dict {nome ADV corto: nome nuovo} dei nodi rinominati (shape escluse).
    """
    uuids = cmds.ls(nodes, uuid=True) if nodes else []
    listed = set(uuids)
    plan = []
    for uuid in uuids:
        node = _by_uuid(uuid)
        if not node:
            continue
        if cmds.ls(node, shapes=True):
            parent = cmds.listRelatives(node, parent=True, fullPath=True) or []
            if parent and cmds.ls(parent, uuid=True)[0] in listed:
                continue  # segue il transform
        shapes = cmds.listRelatives(node, shapes=True, fullPath=True) or []
        shape_plan = [(cmds.ls(shape, uuid=True)[0], _short(shape)) for shape in shapes]
        plan.append((uuid, _short(node), arise_name(node, prefix), shape_plan))

    renamed = {}
    for uuid, short, new_name, shape_plan in plan:
        if not _rename_marked(uuid, short, new_name, owner, role):
            continue
        final = _short(_by_uuid(uuid))
        for index, (shape_uuid, shape_short) in enumerate(shape_plan):
            suffix = "Shape" if index == 0 else "Shape{}".format(index)
            _rename_marked(shape_uuid, shape_short, final + suffix, owner, role)
        renamed[short] = final
    return renamed


def face_nodes(owner, role=None):
    """I nodi del volto `owner` (nomi lunghi), tutti o di un solo ruolo."""
    marked = cmds.ls("*." + OWNER_ATTR, "*:*." + OWNER_ATTR, objectsOnly=True, long=True) or []
    nodes = []
    for node in marked:
        if _get_string(node, OWNER_ATTR) != owner:
            continue
        if role and _get_string(node, ROLE_ATTR) != role:
            continue
        nodes.append(node)
    return nodes


def find_face_node(owner, adv_name):
    """Il nodo del volto `owner` che in origine si chiamava `adv_name`
    ("" se non c'e')."""
    for node in face_nodes(owner):
        if _get_string(node, NAME_ATTR) == adv_name:
            return node
    return ""


def active_fit_owner():
    """Il proprietario del fitting attivo; "" se e' libero, None se non c'e'
    nessun fitting attivo."""
    if not cmds.objExists(FIT_SKELETON):
        return None
    return _get_string(FIT_SKELETON, FIT_OWNER_ATTR)


def fit_skeleton(owner):
    """Il nodo FaceFitSkeleton del volto `owner`, attivo o messo da parte
    ("" se non c'e'). Serve a leggerne le opzioni con `get_fit_option(...,
    node=...)` senza attivarlo."""
    if active_fit_owner() == owner:
        return FIT_SKELETON
    return find_face_node(owner, FIT_SKELETON)


def _fit_nodes():
    """I nodi del fitting attivo: FaceGroup e cio' che contiene, esclusi i
    nodi gia' assegnati a un volto (il rig rinominato sta nello stesso
    gruppo)."""
    if not cmds.objExists(FIT_SKELETON):
        return []
    path = cmds.ls(FIT_SKELETON, long=True)[0]
    marker = "|" + FIT_ROOT + "|"
    root = path[: path.index(marker) + len(marker) - 1] if marker in path else path
    nodes = [root] + (cmds.listRelatives(root, allDescendents=True, fullPath=True) or [])
    return [n for n in nodes if not cmds.attributeQuery(OWNER_ATTR, node=n, exists=True)]


def stash_fitting():
    """Mette da parte il fitting attivo, rinominandolo col prefisso del
    proprio volto. False se non c'e' o non ha un proprietario."""
    owner = active_fit_owner()
    if not owner:
        return False
    prefix = _get_string(FIT_SKELETON, FIT_PREFIX_ATTR) or owner[:8]
    rename_face(prefix, owner, _fit_nodes(), role=ROLE_FIT)
    return True


def _restore_fitting(owner):
    """Ridà i nomi ADV al fitting messo da parte del volto `owner`."""
    uuids = cmds.ls(face_nodes(owner, ROLE_FIT), uuid=True) or []
    for uuid in uuids:
        node = _by_uuid(uuid)
        if not node:
            continue
        adv_name = _get_string(node, NAME_ATTR)
        for attr in (NAME_ATTR, OWNER_ATTR, ROLE_ATTR):
            cmds.deleteAttr("{}.{}".format(node, attr))
        cmds.rename(node, adv_name)
    return bool(uuids)


_PENDING_INFO = "advFacePendingOwner"


def _pending_owner():
    """(owner, prefix) del volto per cui si e' aperta la finestra di fitting
    senza che avesse ancora un fitting; ("", "") se non ce n'e'."""
    value = cmds.fileInfo(_PENDING_INFO, query=True)
    owner, _sep, prefix = (value[0] if value else "").partition("|")
    return owner, prefix


def _set_pending_owner(owner="", prefix=""):
    cmds.fileInfo(_PENDING_INFO, "{}|{}".format(owner, prefix) if owner else "")


def _claim(owner, prefix):
    _set_string(FIT_SKELETON, FIT_OWNER_ATTR, owner)
    _set_string(FIT_SKELETON, FIT_PREFIX_ATTR, prefix)


def activate_fitting(owner, prefix, allow_missing=False):
    """Rende attivo il fitting del volto `owner`.

    - attivo e gia' suo: niente da fare;
    - attivo ma di un altro volto: lo mette da parte e ripristina il proprio;
    - attivo e libero: e' del volto per cui si era aperta la finestra di
      fitting (vedi `allow_missing`), altrimenti di chi lo chiede.

    Returns:
        True se alla fine c'e' un fitting attivo di `owner`. Con
        `allow_missing` ritorna True anche se il volto non ha ancora un
        fitting: la scena e' pronta per crearne uno, e quello che nascera'
        sara' suo. Altrimenti False con un warning.
    """
    current = active_fit_owner()
    if current == "":
        pending, pending_prefix = _pending_owner()
        if pending and pending != owner:
            _claim(pending, pending_prefix)
            current = pending
    if current is not None and current not in ("", owner):
        stash_fitting()
        current = None
    if current is None and not _restore_fitting(owner):
        if cmds.objExists(FIT_SKELETON):
            cmds.warning("activate_fitting: another face fitting could not be put aside")
            return False
        if allow_missing:
            _set_pending_owner(owner, prefix)
        else:
            cmds.warning("activate_fitting: no face fitting for '{}' (fit it first)".format(prefix))
        return allow_missing
    _claim(owner, prefix)
    if _pending_owner()[0] == owner:
        _set_pending_owner()
    return True

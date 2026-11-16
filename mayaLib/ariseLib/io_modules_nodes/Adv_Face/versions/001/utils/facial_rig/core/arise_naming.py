"""Nomi del rig facciale secondo la convenzione di Arise Rigging System.

Il build produce il rig con i nomi di AdvancedSkeleton (`Jaw_M`,
`upperLipA_R`, `JawJoint_M`...), che sono il contratto fra i 30 step e la
base del confronto col MEL. Per l'uso dentro Arise i nodi vengono
rinominati a build finito, con una mappa deterministica:

    <nodo>_<lato>_<nome_snake_case>_<suffisso>

- il lato ADV in coda (`_R`, `_L`, `_M`) diventa un prefisso (`R_`, `L_`,
  `M_`), come nei nodi facciali inclusi in Arise (CA_Mouth:
  `L_lips_corner`, `M_upper_lip`);
- il nome passa da camelCase a snake_case;
- il suffisso dice il tipo: `ctrl` per i controller (membri di
  FaceControlSet), `jnt` per i joint, `grp` per gli altri transform. I
  gruppi ADV `<Name>Offset` e `SDK<Name>` diventano `<name>_offset_grp` e
  `<name>_sdk_grp`.

Esempi (nodo `face`): `Jaw_M` -> `face_M_jaw_ctrl`, `JawJoint_M` ->
`face_M_jaw_jnt`, `SDKupperLipA_R` -> `face_R_upper_lip_a_sdk_grp`.

I nodi che non sono transform (set, shading, nodi non-DAG) non hanno
suffisso: `FaceAllSet` -> `face_face_all_set`.

`rename_to_arise` rinomina un elenco di nodi (in origine mascella e denti,
JAW_SUBSET, per validare lo schema); la rinomina di tutto il rig, con il
proprietario di ogni nodo, e' in core/arise_faces.py. Vedi
docs/arise-node.md.
"""

import re

import maya.cmds as cmds

_SIDES = ("R", "L", "M")
# controller, joint e gruppi di mascella e denti (step JawWeighing)
JAW_SUBSET = (
    "Jaw_M", "SDKJaw_M", "JawOffset_M", "JawJoint_M", "JawMix_M",
    "upperTeeth_M", "SDKupperTeeth_M", "upperTeethOffset_M", "upperTeethJoint_M",
    "lowerTeeth_M", "SDKlowerTeeth_M", "lowerTeethOffset_M", "lowerTeethJoint_M",
    "lowerTeethFollow_M",
)  # fmt: skip


def _snake(name):
    """camelCase / PascalCase -> snake_case (`upperLipA` -> `upper_lip_a`)."""
    name = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", name)
    name = re.sub(r"(?<=[A-Z])(?=[A-Z][a-z])", "_", name)
    return name.lower()


def split_adv_name(adv_name):
    """(`nome`, `lato`) di un nome ADV: `upperLipA_R` -> (`upperLipA`, `R`).
    Senza lato riconoscibile il lato e' una stringa vuota."""
    base, sep, side = adv_name.rpartition("_")
    if sep and side in _SIDES:
        return base, side
    return adv_name, ""


def arise_base_name(adv_name, kind):
    """Il nome Arise senza prefisso del nodo.

    Args:
        adv_name: nome ADV corto (senza path).
        kind: "ctrl", "jnt", "grp", oppure "" per i nodi senza suffisso
            (set, nodi non-DAG): `FaceAllSet` -> `face_all_set`.
    """
    base, side = split_adv_name(adv_name)
    role = ""
    if kind == "jnt" and base.endswith("Joint"):
        base = base[: -len("Joint")]
    elif kind == "grp":
        if base.startswith("SDK"):
            base, role = base[len("SDK") :], "sdk"
        elif base.endswith("Offset"):
            base, role = base[: -len("Offset")], "offset"
    parts = [side] if side else []
    parts.append(_snake(base))
    if role:
        parts.append(role)
    if kind:
        parts.append(kind)
    return "_".join(parts)


def node_kind(node):
    """ "ctrl" (membro di FaceControlSet), "jnt", "grp" per gli altri
    transform, "" per tutto il resto (shape, set, nodi non-DAG)."""
    if cmds.objExists("FaceControlSet") and cmds.sets(node, isMember="FaceControlSet"):
        return "ctrl"
    node_type = cmds.nodeType(node)
    if node_type == "joint":
        return "jnt"
    return "grp" if node_type == "transform" else ""


def arise_name(node, prefix):
    """Il nome Arise completo di un nodo del rig: `<prefix>_<...>`."""
    short = node.rsplit("|", 1)[-1]
    base = arise_base_name(short, node_kind(node))
    return "{}_{}".format(prefix, base) if prefix else base


def rename_to_arise(prefix, nodes=JAW_SUBSET):
    """Rinomina i nodi dati secondo la convenzione Arise.

    Le shape seguono il transform (`<nuovo>Shape`). I nodi assenti sono
    saltati; un nome gia' occupato lascia il nodo com'e', con un warning.

    Returns:
        dict {nome ADV: nome Arise} dei nodi rinominati.
    """
    renamed = {}
    # prima i nomi, poi le rinomine: node_kind legge i set con i nomi ADV
    plan = [(node, arise_name(node, prefix)) for node in nodes if cmds.objExists(node)]
    for node, new_name in plan:
        if cmds.objExists(new_name):
            cmds.warning(
                "rename_to_arise: {} already exists, {} not renamed".format(new_name, node)
            )
            continue
        shapes = cmds.listRelatives(node, shapes=True, fullPath=True) or []
        new_name = cmds.rename(node, new_name)
        for index, shape in enumerate(
            cmds.listRelatives(new_name, shapes=True, fullPath=True) or []
        ):
            if index < len(shapes):
                suffix = "Shape" if index == 0 else "Shape{}".format(index)
                cmds.rename(shape, new_name + suffix)
        renamed[node] = new_name
    return renamed

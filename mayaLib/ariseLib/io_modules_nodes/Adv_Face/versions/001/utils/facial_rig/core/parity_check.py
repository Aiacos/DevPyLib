"""Utility di parita' scene-graph per la validazione MEL <-> Python.

Il modo rigoroso di validare un port e' confrontare il grafo della scena
prodotto dal MEL originale (`asBuildAdvancedFace`) con quello del port Python:
il CLAUDE.md stabilisce che i nomi dei nodi sono un contratto API, quindi due
rig "uguali" devono avere lo stesso grafo (nodi, tipi, gerarchia, connessioni,
attributi user-defined).

Workflow tipico nella fase Maya:

    from facial_rig.core.parity_check import snapshot, diff, format_report
    # 1) build col MEL originale su una copia dell'asset -> salva snapshot
    mel_snap = snapshot(["FaceGroup"])            # o i root rilevanti
    # 2) build col port Python su una copia pulita -> snapshot
    py_snap = snapshot(["FaceGroup"])
    # 3) confronta e leggi il report
    print(format_report(diff(mel_snap, py_snap)))

`snapshot` e' headless e non tocca la mesh: opera solo sul DAG. Salvare gli
snapshot (sono dict serializzabili) permette il confronto fra sessioni Maya
diverse (MEL e Python su scene separate).
"""

import maya.cmds as cmds

# scarto ammesso sugli elementi della matrice locale (unita' di scena / seno)
XFORM_TOLERANCE = 1e-3
# tolleranza relativa sui valori float degli attributi user-defined
FLOAT_TOLERANCE = 1e-6


def _node_attrs(node):
    """Valori degli attributi user-defined leggibili come scalari/vettori."""
    attrs = {}
    for attr in cmds.listAttr(node, userDefined=True) or []:
        plug = "{}.{}".format(node, attr)
        if not cmds.objExists(plug):
            continue
        try:
            value = cmds.getAttr(plug)
        except (RuntimeError, ValueError, TypeError):
            continue
        # i compound restituiscono [(x, y, z)] -> normalizza a tupla
        if isinstance(value, list) and len(value) == 1 and isinstance(value[0], (list, tuple)):
            value = tuple(value[0])
        attrs[attr] = value
    return attrs


def _node_inputs(node):
    """Connessioni in ingresso come 'destAttr<-srcNode.srcAttr' ordinate."""
    pairs = (
        cmds.listConnections(node, connections=True, plugs=True, source=True, destination=False)
        or []
    )
    inputs = []
    # listConnections -c -p restituisce [destPlug, srcPlug, destPlug, srcPlug...]
    for i in range(0, len(pairs) - 1, 2):
        dest_plug, src_plug = pairs[i], pairs[i + 1]
        # i groupId/groupParts (assegnazioni per-componente) hanno nomi
        # auto-numerati che dipendono dalla storia della scena: rumore
        if cmds.nodeType(src_plug.split(".", 1)[0]) in ("groupId", "groupParts"):
            continue
        dest_attr = dest_plug.split(".", 1)[1] if "." in dest_plug else dest_plug
        inputs.append("{}<-{}".format(dest_attr, src_plug))
    return sorted(inputs)


def snapshot(roots):
    """Snapshot del/i sotto-albero/i DAG sotto `roots`.

    Args:
        roots: nome nodo o lista di nomi (radici dei sotto-alberi).

    Returns:
        dict {node: {"type", "parent", "attrs", "inputs", "matrix"}}
        (matrix solo per i transform). I nomi nodo sono
        senza percorso (short name): se ci sono duplicati non univoci in scena
        l'ultimo vince — i rig facciali AS hanno nomi univoci per contratto.
    """
    if isinstance(roots, str):
        roots = [roots]
    nodes = set()
    for root in roots:
        if not cmds.objExists(root):
            continue
        nodes.add(root)
        for child in cmds.listRelatives(root, allDescendents=True, fullPath=False) or []:
            nodes.add(child)

    snap = {}
    for node in nodes:
        # i nomi non univoci non sono interrogabili per nome corto: saltati
        if not cmds.objExists(node) or len(cmds.ls(node)) != 1:
            continue
        # solo i nodi DAG hanno un parent (su un objectSet listRelatives
        # restituisce un membro a caso)
        parent = [None]
        if cmds.objectType(node, isAType="dagNode"):
            parent = cmds.listRelatives(node, parent=True) or [None]
        snap[node] = {
            "type": cmds.nodeType(node),
            "parent": parent[0],
            "attrs": _node_attrs(node),
            "inputs": _node_inputs(node),
        }
        # matrice locale: posizione/orientamento/scala rispetto al parent
        if cmds.objectType(node, isAType="transform"):
            matrix = cmds.xform(node, query=True, objectSpace=True, matrix=True)
            snap[node]["matrix"] = [round(v, 5) for v in matrix]
    return snap


def _same(a, b):
    """Uguaglianza con tolleranza sui float (anche dentro liste): due build
    identici differiscono di rumore numerico oltre la decima cifra."""
    if isinstance(a, (list, tuple)) and isinstance(b, (list, tuple)):
        return len(a) == len(b) and all(_same(x, y) for x, y in zip(a, b))
    if isinstance(a, float) or isinstance(b, float):
        try:
            return abs(a - b) <= FLOAT_TOLERANCE * max(1.0, abs(a), abs(b))
        except TypeError:
            return False
    return a == b


def _norm(value):
    """Tuple -> liste (ricorsivo): uno snapshot passato da JSON ha liste dove
    quello in memoria ha tuple."""
    if isinstance(value, (list, tuple)):
        return [_norm(v) for v in value]
    return value


def diff(a, b):
    """Confronta due snapshot. `a` = riferimento (MEL), `b` = port (Python).

    Returns:
        dict con liste: missing_in_b (in a non in b), missing_in_a (in b non
        in a), type_diffs, attr_diffs, conn_diffs, xform_diffs (matrice
        locale che differisce oltre XFORM_TOLERANCE).
    """
    a_nodes, b_nodes = set(a), set(b)
    result = {
        "missing_in_b": sorted(a_nodes - b_nodes),
        "missing_in_a": sorted(b_nodes - a_nodes),
        "type_diffs": [],
        "attr_diffs": [],
        "conn_diffs": [],
        "xform_diffs": [],
    }
    for node in sorted(a_nodes & b_nodes):
        na, nb = a[node], b[node]
        if na["type"] != nb["type"]:
            result["type_diffs"].append({"node": node, "a": na["type"], "b": nb["type"]})
        if na["parent"] != nb["parent"]:
            result["conn_diffs"].append(
                {"node": node, "kind": "parent", "a": na["parent"], "b": nb["parent"]}
            )
        # attributi
        for attr in sorted(set(na["attrs"]) | set(nb["attrs"])):
            va = na["attrs"].get(attr, "<assente>")
            vb = nb["attrs"].get(attr, "<assente>")
            if not _same(_norm(va), _norm(vb)):
                result["attr_diffs"].append({"node": node, "attr": attr, "a": va, "b": vb})
        # trasformazione locale (assente negli snapshot piu' vecchi)
        ma, mb = na.get("matrix"), nb.get("matrix")
        if ma and mb:
            delta = max(abs(x - y) for x, y in zip(ma, mb))
            if delta > XFORM_TOLERANCE:
                result["xform_diffs"].append({"node": node, "max_delta": round(delta, 5)})
        # connessioni in ingresso
        if na["inputs"] != nb["inputs"]:
            only_a = sorted(set(na["inputs"]) - set(nb["inputs"]))
            only_b = sorted(set(nb["inputs"]) - set(na["inputs"]))
            result["conn_diffs"].append(
                {"node": node, "kind": "inputs", "a_only": only_a, "b_only": only_b}
            )
    return result


def format_report(d):
    """Report leggibile del diff (a=MEL riferimento, b=Python port)."""
    lines = ["=== Parity diff (a=MEL, b=Python) ==="]

    if d["missing_in_b"]:
        lines.append("\nNodi nel MEL ma ASSENTI nel port ({}):".format(len(d["missing_in_b"])))
        lines += ["  - " + n for n in d["missing_in_b"]]
    if d["missing_in_a"]:
        lines.append("\nNodi nel port ma ASSENTI nel MEL ({}):".format(len(d["missing_in_a"])))
        lines += ["  + " + n for n in d["missing_in_a"]]
    for t in d["type_diffs"]:
        lines.append("\nTipo diverso {}: MEL={} Python={}".format(t["node"], t["a"], t["b"]))
    for a in d["attr_diffs"]:
        lines.append("Attr {}.{}: MEL={} Python={}".format(a["node"], a["attr"], a["a"], a["b"]))
    for c in d["conn_diffs"]:
        if c["kind"] == "parent":
            lines.append("Parent {}: MEL={} Python={}".format(c["node"], c["a"], c["b"]))
        else:
            lines.append(
                "Connessioni {}: solo-MEL={} solo-Python={}".format(
                    c["node"], c["a_only"], c["b_only"]
                )
            )

    for x in d.get("xform_diffs", []):
        lines.append("Trasformazione locale {}: scarto max {}".format(x["node"], x["max_delta"]))

    total = (
        len(d.get("xform_diffs", []))
        + len(d["missing_in_b"])
        + len(d["missing_in_a"])
        + len(d["type_diffs"])
        + len(d["attr_diffs"])
        + len(d["conn_diffs"])
    )
    if total == 0:
        lines.append("\nNessuna differenza: parita' del grafo verificata.")
    else:
        lines.append("\nTotale differenze: {}".format(total))
    return "\n".join(lines)

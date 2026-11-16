"""Validazione modello pre-rig (port minimo di asFaceModelCheck, MEL:68223).

Legge la geometria dall'opzione Face e controlla i transform di default
(T=0, R=0, S=1). Il symmetry-check completo di asModelChecker e' fuori scope
(divergenza registrata).
"""

import maya.cmds as cmds

from ..fit_options import get_fit_option


def model_check():
    """Controlla la geometria Face.

    Returns:
        (ok: bool, issues: list[str]). Nessuna eccezione: gli errori sono
        elencati in `issues` (e segnalati con cmds.warning).
    """
    issues = []
    face = get_fit_option("Face")
    first = face.split(" ")[0] if face else ""
    if not face or not cmds.objExists(first):
        issues.append("No geometry chosen for Face")
        cmds.warning(issues[-1])
        return False, issues

    for obj in face.split(" "):
        if not cmds.objExists(obj):
            continue
        for attr, expected in (
            ("translate", (0, 0, 0)),
            ("rotate", (0, 0, 0)),
            ("scale", (1, 1, 1)),
        ):
            val = cmds.getAttr("{}.{}".format(obj, attr))[0]
            if any(abs(v - e) > 1e-4 for v, e in zip(val, expected)):
                issues.append("{}.{} non e' al default: {}".format(obj, attr, val))

    ok = not issues
    if not ok:
        for i in issues:
            cmds.warning(i)
    return ok, issues

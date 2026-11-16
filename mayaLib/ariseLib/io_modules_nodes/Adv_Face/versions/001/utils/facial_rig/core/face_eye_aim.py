"""Build step EyeAim (parita' asFaceEyeAim MEL:35986).

Step di sola visibilita': nasconde i controller, spegne ctrlBox2 e i Region
control, accende l'Aim control e rende visibile il master AimEyeOffset_M.
Non ha procedura *Finish nel MEL. I guard objExists/attributeQuery rispettano
la politica no-exceptions (nel build reale i nodi esistono sempre, creati dagli
step CtrlBox/EyeBall).
"""

import maya.cmds as cmds

from .build_utils import as_face_hide_controllers


def face_eye_aim():
    """Rende visibile la rete di aim degli occhi (asFaceEyeAim).
    Ritorna bool. Nessuna eccezione."""
    if not cmds.objExists("ctrlBox"):
        cmds.warning("face_eye_aim: ctrlBox not found")
        return False

    as_face_hide_controllers(True)

    if cmds.objExists("ctrlBox2"):
        cmds.setAttr("ctrlBox2.v", 0)
    for attr, value in (("RegionsCtrlVis", 0), ("AimCtrlVis", 1)):
        if cmds.attributeQuery(attr, node="ctrlBox", exists=True):
            cmds.setAttr("ctrlBox." + attr, value)
    if cmds.objExists("AimEyeOffset_M"):
        cmds.setAttr("AimEyeOffset_M.v", 1)

    cmds.select(clear=True)
    print("// EyeAim applied")
    return True

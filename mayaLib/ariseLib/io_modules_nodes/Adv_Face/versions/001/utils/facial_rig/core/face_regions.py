"""Build step Regions (parita' asFaceRegions MEL:35949-35984).

Apre con asFaceTongueFinish (MEL:35956), mostra i controller di regione e
sposta nel quadro `ctrlBox2` le sagome indicatrici: ogni sagoma `<Name>1_<S>`
diventa una seconda shape del controller `<Name>_<S>` (asAddCtrlBox2Shape,
in ctrl_box.add_ctrl_box2_shape), cosi' il controller si seleziona anche dal
quadro. Le sagome senza controller sono nascoste.

Divergenze: nodi assenti saltati (il MEL usa catchQuiet per gli offset).
"""

import maya.cmds as cmds

from .build_utils import as_face_hide_controllers, as_show_layer
from .ctrl_box import add_ctrl_box2_shape
from .face_tongue import face_tongue_finish

_REGION_OFFSETS = (
    "EyeRegionOffset_R",
    "EyeRegionOffset_L",
    "EyeBrowRegionOffset_R",
    "EyeBrowRegionOffset_L",
    "EyeBrowRegionOffset_M",
    "NoseRegionOffset_M",
    "LipRegionOffset_M",
)


def face_regions() -> bool:
    """Mostra i controller di regione e aggancia le sagome di ctrlBox2
    (asFaceRegions). Salta (True) senza `upperLipMainCurve`."""
    if not cmds.objExists("upperLipMainCurve"):
        return True
    face_tongue_finish()
    if not cmds.objExists("ctrlBox2") or not cmds.objExists("ctrlBox"):
        cmds.warning("face_regions: ctrlBox / ctrlBox2 not found")
        return False

    as_face_hide_controllers(True)
    cmds.setAttr("ctrlBox2.v", 1)
    cmds.setAttr("ctrlBox.RegionsCtrlVis", 1)
    for offset in _REGION_OFFSETS:
        if cmds.objExists(offset):
            cmds.setAttr(offset + ".v", 1)

    for indicator in cmds.listRelatives("ctrlBox2", children=True, type="transform") or []:
        ctrl = indicator.replace("1", "", 1)
        if not cmds.objExists(ctrl):
            cmds.setAttr(indicator + ".v", 0)
            continue
        add_ctrl_box2_shape(ctrl)

    as_show_layer("Normal")
    cmds.select(clear=True)
    return True

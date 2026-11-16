"""Frame 'DeltaMush' della UI asFace (parita' MEL
AdvancedSkeleton.mel:1989-2022). Pilota il backend core/face_delta_mush.py;
qui si costruisce solo il layout.

Divergenza intenzionale: nel MEL il controllo "Paint DeltaMush" e' uno
`shelfButton` con icona, collocato in un `rowLayout` accanto a un'etichetta
testuale; nel port viene reso come un `cmds.button` standard collegato allo
stesso backend `paint_delta_mush`.
"""

import maya.cmds as cmds

from ..face_delta_mush import (
    create_delta_mush,
    delete_delta_mush,
    delta_mush_zero_weight,
    paint_delta_mush,
)


def _select_area(area):
    """Seleziona un set d'area (eyeLidArea/lipArea); warning se assente."""
    if cmds.objExists(area):
        cmds.select(area)
    else:
        cmds.warning("{} not found (DeltaMush areas exist after build)".format(area))


def build_delta_mush_frame(fitting):
    """Costruisce il frame DeltaMush. Returns il nome del frameLayout."""
    frame = cmds.frameLayout(label=" DeltaMush", collapsable=True, collapse=True)
    cmds.columnLayout(adjustableColumn=True, rowSpacing=4)

    cmds.button(label="Create DeltaMush", command=lambda *_: create_delta_mush())
    cmds.button(label="Delete DeltaMush", command=lambda *_: delete_delta_mush())
    cmds.button(label="Select eyeLidArea", command=lambda *_: _select_area("eyeLidArea"))
    cmds.button(label="Select lipArea", command=lambda *_: _select_area("lipArea"))
    cmds.button(label="zero weight selected", command=lambda *_: delta_mush_zero_weight())
    cmds.button(label="Paint DeltaMush", command=lambda *_: paint_delta_mush())

    cmds.setParent("..")
    cmds.setParent("..")
    return frame

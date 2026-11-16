"""Finestra Face (replica della sezione Face di AdvancedSkeletonWindow).

Pila di frame collassabili nell'ordine MEL (asFaceFrameLayout, MEL:1428).
In questo sub-progetto e' attivo solo il frame Pre; gli altri sono
placeholder collassati. Divergenza: finestra standalone (no body rig).
"""

import maya.cmds as cmds

from ..fitting import FacialFitting
from .build_frame import build_full_frame, build_steps_frame
from .delta_mush_frame import build_delta_mush_frame
from .fit_frame import build_fit_frame
from .prep_frame import build_prep_frame

__all__ = ["show_fitting_ui"]

_WINDOW = "facialFittingWindow"
_TITLE = "AdvancedSkeleton Face"

# Frame della sezione Face nell'ordine MEL; solo "Pre" attivo qui.
_PLACEHOLDER_FRAMES = [
    " Layers",
    " Tweaks",
    " HeadSquash",
    " WrinkleMap",
    " BlendShapes",
    " EditBlendShapes",
    " NewBlendShapes",
    " Custom Controllers",
]


def show_fitting_ui(geometry: str = "", non_symmetrical: bool = False):
    """Apre la finestra Face. geometry vuoto = scelta mesh dentro la UI."""
    fitting = FacialFitting(geometry, non_symmetrical)

    if cmds.window(_WINDOW, exists=True):
        cmds.deleteUI(_WINDOW)
    cmds.window(_WINDOW, title=_TITLE, widthHeight=(300, 700), sizeable=True)
    cmds.scrollLayout(childResizable=True)
    cmds.columnLayout(adjustableColumn=True, rowSpacing=2)

    build_prep_frame(fitting)
    build_fit_frame(fitting)
    build_full_frame(fitting)
    build_steps_frame(fitting)
    build_delta_mush_frame(fitting)

    for label in _PLACEHOLDER_FRAMES:
        cmds.frameLayout(label=label, collapsable=True, collapse=True, enable=False)
        cmds.setParent("..")

    cmds.setParent("..")
    cmds.showWindow(_WINDOW)
    return fitting

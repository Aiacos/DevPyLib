"""Frame 'Fit' della UI asFace (parita' MEL AdvancedSkeleton.mel:1565-1723).

Itera FacialFitting.REGIONS raggruppate per parent_region nell'ordine MEL e
costruisce una fit_row per ciascuna. La logica di fitting e' tutta delegata
al backend esistente (fit_region, face_fit_*, FacialFitting.face_assist);
qui si costruisce solo il layout. La selezione dei vertici/loop avviene in
viewport: la UI e' uno scheduler, non un selettore.
"""

import maya.cmds as cmds

from ..fit_options import get_fit_option
from ..fitting import face_fit_delete, face_fit_hide, face_fit_reselect, face_fit_swap_upper_lower
from .widgets import fit_row

# Ordine dei gruppi parent come nel loop MEL (1616-1720).
_PARENT_ORDER = ["Eye", "EyeLid", "Lip", "EyeBrow", "Nose", "Jaw", "Cheek", "ForeHead"]

# Region il cui nome immagine di help diverge da "fitFace<name>" nel MEL.
# JawCurves: il bottone ? del MEL usa fitFaceJawCurvesTweak (MEL:1875).
_HELP_REGION_OVERRIDE = {"JawCurves": "fitFaceJawCurvesTweak"}


def help_region_for(name):
    """Nome dell'immagine di help per una region (parita' asHelpImage MEL).

    Default "fitFace<name>"; alcune region usano un nome diverso nel MEL
    (vedi _HELP_REGION_OVERRIDE).
    """
    return _HELP_REGION_OVERRIDE.get(name, "fitFace" + name)


def grouped_regions(regions):
    """Raggruppa le REGIONS per parent_region nell'ordine MEL.

    Returns:
        Lista di (parent_region, [region_name...]) coprente TUTTE le region.
        I gruppi noti seguono _PARENT_ORDER; eventuali parent non elencati
        (o vuoti) vengono accodati in ordine alfabetico, cosi' la copertura
        resta totale anche se REGIONS aggiunge nuovi gruppi.
    """
    by_parent = {}
    for name, region in regions.items():
        by_parent.setdefault(region.parent_region or name, []).append(name)
    for parent in by_parent:
        by_parent[parent].sort(key=lambda n: regions[n].order)

    ordered = []
    for parent in _PARENT_ORDER:
        if parent in by_parent:
            ordered.append((parent, by_parent.pop(parent)))
    for parent in sorted(by_parent):
        ordered.append((parent, by_parent[parent]))
    return ordered


def _fit_node_exists(region_name):
    """True se il fit della region esiste in scena (per lo stato checkBox)."""
    suffix = "Left" if get_fit_option("NonSymSide") == "Left" else ""
    return cmds.objExists("FaceFit{}{}".format(region_name, suffix))


def build_fit_frame(fitting):
    """Costruisce il frame Fit. Returns il nome del frameLayout."""
    frame = cmds.frameLayout(label=" Fit", collapsable=True, collapse=True)
    cmds.columnLayout(adjustableColumn=True)

    # Blocco non-symmetrical (MEL: bottoni Right/Left/show both sides).
    cmds.rowLayout(numberOfColumns=3)
    cmds.button(label="Right", command=lambda *_: fitting.switch_side("Right"))
    cmds.button(label="Left", command=lambda *_: fitting.switch_side("Left"))
    cmds.button(label=" show both sides ", command=lambda *_: fitting.show_both_sides())
    cmds.setParent("..")
    cmds.separator(height=8)

    for parent, names in grouped_regions(fitting.REGIONS):
        cmds.text(label=parent + ":", align="left")
        for name in names:
            region = fitting.REGIONS[name]
            # assist e hide esistono nel MEL solo per part=="Inner" di
            # EyeLid/Lip (MEL:1712,1715-1716), piu' EyeBall/ForeHead per hide.
            is_inner = name.endswith("Inner") and region.parent_region in ("EyeLid", "Lip")
            is_lip = region.parent_region == "Lip"
            show_hide = is_inner or name in ("EyeBall", "ForeHead")
            # swap vuole (section, part) separati: il backend costruisce
            # upper<section>Cylinder<part> (es. upperLipCylinderOuter), quindi
            # per LipOuter serve ("Lip", "Outer"), non ("LipOuter", "").
            fit_row(
                label=name,
                on_fit=(lambda n=name: fitting.fit_region(n)),
                on_delete=(lambda n=name: face_fit_delete(n)),
                on_reselect=(lambda n=name: face_fit_reselect(n)),
                help_region=help_region_for(name),
                on_swap=(
                    (lambda part=name[3:]: face_fit_swap_upper_lower("Lip", part))
                    if is_lip
                    else None
                ),
                on_assist=(
                    (lambda p=region.parent_region: fitting.face_assist(p)) if is_inner else None
                ),
                on_hide=((lambda n=name: face_fit_hide(n)) if show_hide else None),
                checked=_fit_node_exists(name),
            )
        cmds.separator(height=6)

    cmds.setParent("..")
    cmds.setParent("..")
    return frame

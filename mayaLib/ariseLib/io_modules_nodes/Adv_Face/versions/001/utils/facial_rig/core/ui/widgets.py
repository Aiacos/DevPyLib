"""Righe UI riusabili del frame Pre (parita' layout MEL 1441-1535).

Ogni helper costruisce un rowLayout coerente con il MEL e ritorna i nomi
dei control creati. Le callback ricevono il nome dell'opzione fit.
"""

import maya.cmds as cmds

from .help_image import show_help_image


def help_button(region):
    """Bottone '?' che apre l'immagine di guida (parita' MEL:1446)."""
    return cmds.button(
        width=15,
        height=15,
        label="?",
        command=lambda *_: show_help_image(region),
        annotation="Guida: {}".format(region),
    )


def input_row(label, on_choose, on_reselect, region, enabled=True):
    """[button label][textField -ed 0][popup re-select][? ] (MEL 1441-1447).

    Returns (button, textField). La textField e' read-only (editable=False).
    """
    cmds.rowLayout(numberOfColumns=3, columnWidth3=(120, 100, 15))
    btn = cmds.button(width=120, label=label, enable=enabled, command=lambda *_: on_choose())
    cmds.popupMenu()
    cmds.menuItem(label="re-select", command=lambda *_: on_reselect())
    field = cmds.textField(width=100, editable=False)
    help_button(region)
    cmds.setParent("..")
    return btn, field


def option_row(label, items, region, on_change, default_index=0, enabled=True):
    """[optionMenu][? ] (parita' MEL 1456-1481). Returns optionMenu name."""
    cmds.rowLayout(numberOfColumns=2, columnWidth2=(222, 15))
    menu = cmds.optionMenu(label=label, enable=enabled, changeCommand=lambda *_: on_change(menu))
    for it in items:
        cmds.menuItem(label=it)
    cmds.optionMenu(menu, edit=True, select=default_index + 1)
    help_button(region)
    cmds.setParent("..")
    return menu


def checkbox_row(label, region, on_change, value=False, enabled=True):
    """[checkBox][? ] (parita' MEL 1483-1535). Returns checkBox name."""
    cmds.rowLayout(numberOfColumns=2, columnWidth2=(222, 15))
    box = cmds.checkBox(
        label=label, value=value, enable=enabled, changeCommand=lambda *_: on_change(box)
    )
    help_button(region)
    cmds.setParent("..")
    return box


def fit_row(
    label,
    on_fit,
    on_delete,
    on_reselect,
    help_region,
    on_swap=None,
    on_assist=None,
    on_hide=None,
    checked=False,
    enabled=True,
):
    """Riga region del frame Fit (parita' rowLayout MEL 1700-1717).

    [button label][checkBox stato][? help][popup re-select/(swap)]
    [assist?][-hide?]. Le callback ricevono 0 argomenti (gia' legate alla
    region dal chiamante). on_swap/on_assist/on_hide opzionali: se None il
    relativo controllo non viene creato. checkBox spento -> on_delete.

    Returns (button, checkBox).
    """
    cmds.rowLayout(numberOfColumns=6, columnWidth6=(100, 20, 15, 5, 35, 35), adjustableColumn=1)
    btn = cmds.button(width=100, label=label, enable=enabled, command=lambda *_: on_fit())
    cmds.popupMenu()
    cmds.menuItem(label="re-select", command=lambda *_: on_reselect())
    if on_swap is not None:
        cmds.menuItem(label="swap upper/lower", command=lambda *_: on_swap())
    box = cmds.checkBox(
        width=20, label="", value=checked, enable=enabled, offCommand=lambda *_: on_delete()
    )
    help_button(help_region)
    if on_assist is not None:
        cmds.button(width=35, label="assist", enable=enabled, command=lambda *_: on_assist())
    if on_hide is not None:
        cmds.button(width=35, label="-hide", enable=enabled, command=lambda *_: on_hide())
    cmds.setParent("..")
    return btn, box


def step_row(label, on_build, enabled=True, visible=True):
    """Riga di uno step del frame Build (parita' rowLayout MEL 1808-1817).

    [text "N : Nome"][button Build]. Il bottone e' abilitato solo per il
    prossimo step (gating); la riga puo' essere nascosta (visible=False).

    Returns (text, button).
    """
    cmds.rowLayout(numberOfColumns=2, columnWidth2=(159, 80), manage=visible)
    txt = cmds.text(label=label, align="left")
    btn = cmds.button(
        width=80, height=15, label="Build", enable=enabled, command=lambda *_: on_build()
    )
    cmds.setParent("..")
    return txt, btn

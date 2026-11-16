"""Popup immagine di guida (parita' asHelpImage, MEL AdvancedSkeleton.mel:43447).

Il MEL apre una window con un control `image` che carica
<scriptLocation>/AdvancedSkeletonFiles/div/images/help/<region>.jpg.
Qui le immagini sono versionate in docs/images/help/ (relative al package).
Divergenza intenzionale: nessun video-link.
"""

import os

import maya.cmds as cmds

_WINDOW = "facialHelpImageWindow"


def _help_dir():
    return os.path.normpath(
        os.path.join(os.path.dirname(__file__), "..", "..", "docs", "images", "help")
    )


def help_image_path(region):
    """Path assoluto dell'immagine <region>.jpg, o None se non esiste."""
    path = os.path.join(_help_dir(), region + ".jpg")
    return path if os.path.isfile(path) else None


def show_help_image(region):
    """Apre la finestra di help con l'immagine della regione.

    Gestione graceful: se l'immagine manca, mostra un dialog informativo
    invece di sollevare (parita' di intento con asHelpImage, senza crash).
    """
    path = help_image_path(region)
    if path is None:
        cmds.confirmDialog(
            title="AdvancedSkeleton Help",
            message="Immagine di guida non disponibile: {}".format(region),
            button=["OK"],
        )
        return None
    if cmds.window(_WINDOW, exists=True):
        cmds.deleteUI(_WINDOW)
    cmds.window(_WINDOW, title="AdvancedSkeleton Help")
    form = cmds.formLayout()
    img = cmds.image(image=path)
    cmds.formLayout(
        form,
        edit=True,
        attachForm=[(img, "top", 0), (img, "left", 0), (img, "right", 0), (img, "bottom", 0)],
    )
    cmds.showWindow(_WINDOW)
    return _WINDOW

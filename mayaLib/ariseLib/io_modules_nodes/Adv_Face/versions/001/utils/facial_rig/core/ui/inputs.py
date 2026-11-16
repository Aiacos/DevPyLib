"""Selezione/validazione input del frame Pre (parita' asChooseInput,
MEL AdvancedSkeleton.mel:42175; asSelectFromTextField MEL:9088).

choose_input contiene la logica testabile (validazione + persistenza
opzione); l'aggiornamento del textField della UI e' a carico del chiamante
(prep_frame), per mantenere la logica eseguibile headless.
"""

# NOTA: il ramo MEL per gli input *Joint* (validazione objectType == joint,
# asChooseInput:42217-42221) non e' ancora portato (fuori scope plan 1).
import maya.cmds as cmds

from ..fit_options import get_fit_option, set_fit_option

# Nomi riservati ai nodi creati dal rig (MEL asChooseInput:42184).
RESERVED_NAMES = ("Eye_R", "Eye_L", "upperTeeth_M", "lowerTeeth_M", "Tongue0_M", "Nose_M")

# Input che devono essere oggetti interi, non componenti.
# Divergenza intenzionale: il MEL verifica i componenti solo per Face/AllHead
# (MEL:42194); qui si estende a tutti gli input geometria per coerenza
# (gli altri input nel MEL sono comunque filtrati a mesh/nurbs).
_OBJECT_ONLY = (
    "Face",
    "AllHead",
    "RightEye",
    "LeftEye",
    "UpperTeeth",
    "LowerTeeth",
    "Tongue",
    "Eyebrow",
    "Eyelash",
    "Extras",
)


def choose_input(option_name, fitting):
    """Registra la selezione corrente come input `option_name`.

    Args:
        option_name: chiave fit option (es. "Face", "Mask", "RightEye").
        fitting: istanza FacialFitting (per create_fit_skeleton/create_fit_mask).

    Returns:
        La stringa salvata nell'opzione, oppure None se la selezione non e'
        valida (con cmds.warning, niente eccezioni).
    """
    selection = cmds.ls(selection=True, long=False)

    # FaceFitSkeleton deve esistere (parita' asChooseInput:42188).
    if not cmds.objExists(fitting.fit_skeleton_grp):
        fitting.create_fit_skeleton()

    if option_name == "Mask":
        fitting.create_fit_mask()
        return get_fit_option("Mask") or None

    if not selection:
        cmds.warning("Nothing selected for input '{}'".format(option_name))
        return None

    if option_name in _OBJECT_ONLY:
        for item in selection:
            if "." in item:
                cmds.warning("Only select Object, not vertices, edges or faces")
                return None

    for item in selection:
        if "|" in item:
            cmds.warning("'{}' does not have a unique name; rename it.".format(item))
            return None

    for item in selection:
        short = item.split("|")[-1]
        if short in RESERVED_NAMES:
            cmds.warning("'{}' is a reserved rig name".format(short))
            return None

    value = " ".join(selection)
    if not set_fit_option(option_name, value):
        return None

    # Per il Face: registra anche lo skinCluster trovato (parita' MEL:42300).
    if option_name == "Face":
        skin = fitting._get_skin_cluster(
            selection[0]
        )  # TODO: esporre helper pubblico se riusato altrove
        if not skin:
            cmds.warning(
                "No skinCluster found on '{}'; SkinCluster option left empty.".format(selection[0])
            )
        set_fit_option("SkinCluster", skin or "")
    return value


def reselect(option_name):
    """Riseleziona in viewport gli oggetti memorizzati nell'opzione
    (parita' asSelectFromTextField, MEL:9088)."""
    value = get_fit_option(option_name)
    objects = [o for o in (value or "").split() if o and cmds.objExists(o)]
    if objects:
        cmds.select(objects, replace=True)
        return objects
    cmds.warning("Nothing to re-select for '{}'".format(option_name))
    return []

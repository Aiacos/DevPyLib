"""Adv_Face: nodo Arise che costruisce il rig facciale di AdvancedSkeleton.

Il rig e' il port Python del MEL v6.661 (package `facial_rig`).

Segue la documentazione ufficiale di Arise ("How To Create Your Own Node",
https://ariserigging.com/docs/) con una deroga dichiarata: la
documentazione chiede di dichiarare joint e controller in `joints_creation`
/ `ctrls_creation` e di non crearli in `rig_creation`, ma nel rig ADV il
loro numero dipende dalla mesh e dal fitting. Qui li crea il build del
package; i nodi risultanti sono rinominati secondo la
convenzione di Arise con il nome del nodo come prefisso, cosi' piu' nodi
Adv_Face (piu' volti) convivono nella stessa scena.

Prerequisito: il viso deve essere gia' fittato (nodo `FaceFitSkeleton` in
scena, creato dalla UI di fitting del package).

Stato: provato dentro Arise su `chubby`. Vedi docs/arise-node.md nel repo adv-maya-facial-rig, che resta la sorgente
del package e dei suoi test.
"""

import importlib
import logging
import os
import sys

import maya.cmds as mc
from arise.data_types import node_data
from arise.utils import tagging_utils
from arise.utils.modules_utils import create_grps

MAYA_VERSION = 2022  # the version of maya from which this module supports.
AUTHOR = "Lorenzo Argentieri"  # name of person who created this module.
RIG_CATEGORY = "All"  # either 'Basic', 'Cartoon', 'Vfx', 'Game' or 'All'.
RIG_TYPE = "Biped"  # Biped, Car, Quadruped, ..., All.
TAGS = ["face", "facial", "advanced skeleton", "jaw", "lips", "eyes", "arkit"]
TOOL_TIP = "Facial rig built like the AdvancedSkeleton face (mesh-fitted, joint based)."

LOGGER = logging.getLogger("node_rig_logger")

# Il package del facciale sta nella cartella utils di questa versione del
# nodo (copia allineata dal repo adv-maya-facial-rig con
# tools/deploy_arise_node.py), cosi' il nodo non dipende da altro.
_UTILS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "utils")
_PACKAGE_NAMES = ("facial_rig",)
# opzioni scelte con il selettore di nodi di Arise
_PICKED_OPTIONS = ("Face", "HeadJoint")
# attributo che tagging_utils.tag_as_dont_tag aggiunge ai nodi
_DONT_TAG_ATTR = "io_dont_tag"


def _facial_rig():
    """Il package del facciale, dalla cartella utils del nodo."""
    if _UTILS_DIR not in sys.path:
        sys.path.insert(0, _UTILS_DIR)
    for name in _PACKAGE_NAMES:
        try:
            return importlib.import_module(name)
        except ImportError:
            continue
    return None


class Adv_Face(node_data.NodeData):  # noqa: N801 (Arise: classe = nome cartella)
    """Rig facciale AdvancedSkeleton come nodo Arise."""

    sort_priority = 1000

    def __init__(self, parent, docs, icon, module_dict):
        """Costruttore standard di un nodo Arise."""
        node_data.NodeData.__init__(
            self, parent=parent, icon=icon, docs=docs, module_dict=module_dict
        )

    def attributes_creation(self):
        """Opzioni del pannello Face di AdvancedSkeleton e collegamenti.

        L'elenco dei campi viene dal package (`arise_bridge.node_fields`),
        che e' la fonte unica delle opzioni; i default sono i valori gia'
        salvati dal fitting, se in scena.
        """
        self.option_attrs = {}
        self.option_defaults = {}
        package = _facial_rig()
        if package is None:
            LOGGER.error("[%s] facial_rig package not found (%s)", self.name, _PACKAGE_NAMES)
            fields = []
        else:
            bridge = importlib.import_module(package.__name__ + ".core.arise_bridge")
            fields = bridge.node_fields()

        # Il fitting (punti e loop di vertici su occhi, labbra, naso, guance...)
        # non sta negli attributi: si fa nella finestra Face del package.
        self.add_collapsible_layout(title="Fitting", shown=True)
        self.add_button(
            buttons=[
                (
                    self.open_face_fitting,
                    "resources/icons/guides_icon.png",
                    "Face Fitting",
                    "Open the face fitting window: select on the mesh the vertices and edge loops "
                    "of eyelids, lips, nose, cheeks... The result is stored in FaceFitSkeleton.",
                ),
            ],
        )
        self.close_layout()

        section = None
        for field in fields:
            if field["section"] != section:
                if section is not None:
                    self.close_layout()
                section = field["section"]
                self.add_collapsible_layout(title=section, shown=section in ("Geometry", "Rig"))
            attr = self._add_option_attr(field)
            if attr is not None:  # Arise scarta gli attributi dal nome non valido
                self.option_attrs[field["option"]] = attr
                picked = field["option"] in _PICKED_OPTIONS  # il selettore nasce vuoto
                self.option_defaults[field["option"]] = "" if picked else field["default"]
        if section is not None:
            self.close_layout()

        self.add_separator(title="Connections")
        self.driven_head_attr = self.add_driven_attribute(
            name="Head Input", annotation="The head the face follows."
        )
        self.driver_face_attr = self.add_driver_attribute(
            name="Face Output", annotation="Root of the face rig."
        )

    def open_face_fitting(self):
        """Apre la finestra di fitting del package sulla mesh del nodo."""
        package = _facial_rig()
        if package is None:
            LOGGER.error("[%s] facial_rig package not found (%s)", self.name, _PACKAGE_NAMES)
            return
        bridge = importlib.import_module(package.__name__ + ".core.arise_bridge")
        attr = self.option_attrs.get("Face")
        geometry = (attr.value or "").strip().rsplit("|", 1)[-1] if attr is not None else ""
        # con piu' volti in scena: attiva il fitting di questo nodo e mette
        # da parte quello degli altri
        bridge.open_fitting(self.uuid.hex, self.name, geometry)

    def _add_option_attr(self, field):
        """Crea l'attributo Arise adatto al tipo dell'opzione ADV."""
        note = "AdvancedSkeleton face option '{}'.".format(field["option"])
        if not field["ported"]:
            note += " Not supported yet by the Python port: it has no effect."
        if field["type"] == "bool":
            return self.add_boolean_attribute(
                name=field["title"], default_value=bool(field["default"]), annotation=note
            )
        if field["type"] == "enum":
            return self.add_drop_down_attribute(
                name=field["title"],
                items=field["items"],
                default_value=field["default"],
                annotation=note,
            )
        if field["type"] == "long":
            return self.add_integer_attribute(
                name=field["title"], default_value=int(field["default"]), annotation=note
            )
        if field["option"] in _PICKED_OPTIONS:
            return self.add_node_attribute(
                name=field["title"],
                annotation=note + " Leave empty to keep the value stored by the face fitting.",
            )
        return self.add_string_attribute(
            name=field["title"],
            default_value=field["default"] or "",
            annotation=note + " Space separated names for geometry lists.",
            set_str_validator=False,
        )

    def guides_creation(self):
        """Nessuna guida Arise.

        Il fitting e' quello di AdvancedSkeleton: punti e loop di vertici
        sulla mesh, salvati in FaceFitSkeleton.
        """

    def joints_creation(self):
        """Nessun joint dichiarato: li crea il build (vedi docstring del modulo)."""

    def ctrls_creation(self):
        """Nessun controller dichiarato: li crea il build."""

    def _options(self, bridge):
        """Ritorna {opzione: valore} dei soli campi cambiati dall'utente.

        I default del nodo sono una fotografia del fitting attivo alla
        creazione: un campo non toccato lascia il valore del fitting di
        questo volto (vedi `arise_bridge.changed_options`).
        """
        values = {}
        for option, attr in self.option_attrs.items():
            value = attr.value
            if isinstance(value, str) and option in _PICKED_OPTIONS:
                value = value.strip().rsplit("|", 1)[-1]  # il picker da' il nome lungo
            values[option] = value
        return bridge.changed_options(values, self.option_defaults)

    def on_delete_operation(self, silent=True):  # REIMPLEMENTED!
        """Cancella il rig facciale di questo nodo prima della pulizia di Arise.

        Arise conserva lo skin solo dei joint dichiarati in `joints_creation`
        (li sostituisce con dei placeholder). Quelli del facciale li crea il
        build: cancellati mentre sono ancora influenze, la mesh del viso
        perderebbe quei pesi. Qui tornano prima al joint della testa, come fa
        asDeleteAdvancedFace.

        Arise chiama questo metodo a ogni pulizia, anche senza rig in scena;
        il rig si riconosce dal proprietario scritto sui suoi nodi, quindi i
        volti degli altri nodi non vengono toccati.
        """
        package = _facial_rig()
        if package is None:
            return
        bridge = importlib.import_module(package.__name__ + ".core.arise_bridge")
        bridge.delete_face(self.uuid.hex)

    def rig_creation(self):
        """Costruisce il rig ADV e lo rinomina col nome di questo nodo."""
        package = _facial_rig()
        if package is None:
            LOGGER.error("[%s] facial_rig package not found (%s)", self.name, _PACKAGE_NAMES)
            return False
        bridge = importlib.import_module(package.__name__ + ".core.arise_bridge")

        input_grp, output_grp = create_grps(self, ["input_grp", "output_grp"])
        self.driven_head_attr.set_maya_object(input_grp)
        self.driver_face_attr.set_maya_object(output_grp)

        # Il build gira con i nomi di AdvancedSkeleton; a build finito tutto
        # cio' che ha creato prende il nome di questo nodo come prefisso,
        # cosi' piu' nodi Adv_Face (piu' volti) convivono nella stessa scena.
        # Arise tagga poi da solo i nodi nati qui dentro.
        is_built, kept = bridge.build_owned_face(self.uuid.hex, self.name, self._options(bridge))

        # Il build ricrea lo skinCluster del viso (rebind): per Arise e' un nodo
        # nuovo e lo cancellerebbe uscendo da Build. I nodi delle geometrie
        # dell'utente vanno esclusi dai tag automatici, come fanno i nodi
        # inclusi in Arise per cio' che deve restare (IK_Chain, HumanIK). Al
        # rebuild i sopravvissuti hanno gia' il tag: ripeterlo da' un warning.
        kept = [n for n in kept if not mc.attributeQuery(_DONT_TAG_ATTR, node=n, exists=True)]
        if kept:
            tagging_utils.tag_as_dont_tag(kept)

        if not is_built:
            LOGGER.error("[%s] the face build failed, see the Maya script editor", self.name)
            return False
        if mc.objExists(bridge.FACE_ROOT):
            output_grp.match_transformation_to(bridge.FACE_ROOT)
        return True

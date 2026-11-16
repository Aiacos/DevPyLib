"""Adv_Face: nodo Arise che costruisce il rig facciale di AdvancedSkeleton.

Il rig e' il port Python del MEL v6.661 (package `facial_rig`).

Segue la documentazione ufficiale di Arise ("How To Create Your Own Node",
https://ariserigging.com/docs/) con una deroga dichiarata: la
documentazione chiede di dichiarare joint e controller in `joints_creation`
/ `ctrls_creation` e di non crearli in `rig_creation`, ma nel rig ADV il
loro numero dipende dalla mesh e dal fitting. Qui li crea il build del
package; i nodi risultanti sono registrati presso Arise con
`tagging_utils.tag_nodes` (come fa CA_Mouth per i suoi nodi extra) e
rinominati secondo la convenzione di Arise.

Prerequisito: il viso deve essere gia' fittato (nodo `FaceFitSkeleton` in
scena, creato dalla UI di fitting del package).

Stato: scheletro, provato dentro Arise su `chubby`; la rinomina copre solo
mascella e denti. Vedi docs/arise-node.md nel repo adv-maya-facial-rig, che resta la sorgente
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
        attr = self.option_attrs.get("Face")
        geometry = (attr.value or "").strip().rsplit("|", 1)[-1] if attr is not None else ""
        package.show_fitting_ui(geometry)

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

    def _options(self):
        """Ritorna {opzione: valore} dagli attributi del nodo.

        Le stringhe vuote lasciano il valore gia' salvato dal fitting.
        """
        options = {}
        for option, attr in self.option_attrs.items():
            value = attr.value
            if isinstance(value, str):
                value = value.strip()
                if not value:
                    continue
                if option in _PICKED_OPTIONS:
                    value = value.rsplit("|", 1)[-1]  # il picker da' il nome lungo
            options[option] = value
        return options

    def on_delete_operation(self, silent=True):  # REIMPLEMENTED!
        """Cancella il rig facciale prima della pulizia di Arise.

        Arise conserva lo skin solo dei joint dichiarati in `joints_creation`
        (li sostituisce con dei placeholder). Quelli del facciale li crea il
        build: cancellati mentre sono ancora influenze, la mesh del viso
        perderebbe lo skinCluster. Qui i pesi tornano prima al joint della
        testa, come fa asDeleteAdvancedFace.

        Arise chiama questo metodo a ogni pulizia, anche senza rig in scena:
        si agisce solo se il rig presente porta il tag di questo nodo.
        """
        package = _facial_rig()
        if package is None:
            return
        bridge = importlib.import_module(package.__name__ + ".core.arise_bridge")
        rig_nodes = set(mc.ls(bridge.face_rig_nodes(), long=True) or [])
        tagged = set(tagging_utils.get_maya_nodes_with_tag(self.uuid.hex) or [])
        if not rig_nodes & tagged:
            return  # nessun rig, oppure un rig facciale non costruito da questo nodo
        if not bridge.delete_face() and not silent:
            LOGGER.warning("[%s] the face rig could not be deleted", self.name)

    def rig_creation(self):
        """Costruisce il rig ADV, lo registra presso Arise e lo rinomina."""
        package = _facial_rig()
        if package is None:
            LOGGER.error("[%s] facial_rig package not found (%s)", self.name, _PACKAGE_NAMES)
            return False
        bridge = importlib.import_module(package.__name__ + ".core.arise_bridge")
        naming = importlib.import_module(package.__name__ + ".core.arise_naming")

        input_grp, output_grp = create_grps(self, ["input_grp", "output_grp"])
        self.driven_head_attr.set_maya_object(input_grp)
        self.driver_face_attr.set_maya_object(output_grp)

        if not bridge.build_face(self._options()):
            LOGGER.error("[%s] the face build failed, see the Maya script editor", self.name)
            return False

        # Arise tagga da solo tutto cio' che nasce durante rig_creation():
        # taggare qui i nodi del rig darebbe un errore di attributo doppio
        # per ogni nodo.
        # Il build ricrea lo skinCluster del viso (rebind): per Arise e' un nodo
        # nuovo e lo cancellerebbe uscendo da Build. I nodi delle geometrie
        # dell'utente vanno esclusi dai tag automatici, come fanno i nodi
        # inclusi in Arise per cio' che deve restare (IK_Chain, HumanIK).
        # al rebuild i nodi sopravvissuti hanno gia' il tag: ripeterlo da' un warning
        kept = [
            node
            for node in bridge.geometry_nodes()
            if not mc.attributeQuery(_DONT_TAG_ATTR, node=node, exists=True)
        ]
        if kept:
            tagging_utils.tag_as_dont_tag(kept)

        if mc.objExists(bridge.FACE_ROOT):
            output_grp.match_transformation_to(bridge.FACE_ROOT)
        naming.rename_to_arise(self.name)
        return True

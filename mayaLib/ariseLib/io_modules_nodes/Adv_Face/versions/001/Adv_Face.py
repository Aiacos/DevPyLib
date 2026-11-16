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

Stato: scheletro. Non ancora provato dentro Arise; la rinomina copre solo
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
# (titolo nell'editor, opzione di FaceFitSkeleton)
_GEO_ATTRS = (
    ("Face Mesh", "Face"),
    ("Head Joint", "HeadJoint"),
)
_TEXT_ATTRS = (
    ("All Head Meshes", "AllHead"),
    ("Right Eye", "RightEye"),
    ("Left Eye", "LeftEye"),
    ("Upper Teeth", "UpperTeeth"),
    ("Lower Teeth", "LowerTeeth"),
    ("Tongue", "Tongue"),
)
_BOOL_ATTRS = (
    ("Eye Base", "EyeBase", False),
    ("Eye Socket", "EyeSocket", False),
    ("Long Snout", "LongSnout", False),
    ("Phonemes", "Phonemes", True),
    ("Emotions", "Emotions", True),
    ("ARKit", "ARKit", False),
)


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
        """Geometrie, opzioni del build e collegamenti verso gli altri nodi."""
        self.option_attrs = {}

        self.add_collapsible_layout(title="Geometry", shown=True)
        for title, option in _GEO_ATTRS:
            self.option_attrs[option] = self.add_node_attribute(
                name=title, annotation="Leave empty to keep the value stored by the face fitting."
            )
        for title, option in _TEXT_ATTRS:
            self.option_attrs[option] = self.add_string_attribute(
                name=title,
                default_value="",
                annotation="Space separated names. Leave empty to keep the fitted value.",
                set_str_validator=False,
            )
        self.close_layout()

        self.add_collapsible_layout(title="Options", shown=True)
        for title, option, default in _BOOL_ATTRS:
            self.option_attrs[option] = self.add_boolean_attribute(
                name=title, default_value=default, annotation="AdvancedSkeleton face option."
            )
        self.close_layout()

        self.add_separator(title="Connections")
        self.driven_head_attr = self.add_driven_attribute(
            name="Head Input", annotation="The head the face follows."
        )
        self.driver_face_attr = self.add_driver_attribute(
            name="Face Output", annotation="Root of the face rig."
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
                if option in ("Face", "HeadJoint"):
                    value = value.rsplit("|", 1)[-1]  # il picker da' il nome lungo
            options[option] = value
        return options

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

        # i nodi del build non nascono dalle API di Arise: vanno taggati
        # perche' la pulizia (uscita da Build, rebuild) li riconosca
        tagging_utils.tag_nodes(bridge.face_rig_nodes(), tag=self.uuid.hex)

        if mc.objExists(bridge.FACE_ROOT):
            output_grp.match_transformation_to(bridge.FACE_ROOT)
        naming.rename_to_arise(self.name)
        return True

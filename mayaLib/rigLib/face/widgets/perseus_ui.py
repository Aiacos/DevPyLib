"""Perseus UI main dialog for facial rigging.

Provides the main PerseusUI dialog class and CustomTabWidget for organizing
the facial rigging interface into tabbed panels.
"""

__author__ = "Lorenzo Argentieri"

import json
import sys

# Qt imports with PySide6/PySide2 fallback
try:
    from PySide6 import QtCore, QtWidgets
except (ImportError, ModuleNotFoundError):
    from PySide2 import QtCore, QtWidgets

# Maya imports - deferred to allow syntax checking
import maya.cmds as cmds
import pymel.all as pm
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin

from mayaLib.rigLib.face.utils import (
    get_short_license_string,
    maya_main_window,
)
from mayaLib.rigLib.face.widgets.head_geo_widget import HeadGeoWidget
from mayaLib.rigLib.face.widgets.settings_widget import SettingsWidget
from mayaLib.rigLib.face.widgets.skin_widget import SkinWidget


class CustomTabWidget(QtWidgets.QWidget):
    """Custom tab widget for organizing facial rig UI panels.

    A simplified tab widget implementation using QTabBar and QStackedWidget
    to provide a more customizable tab interface than QTabWidget.

    Attributes:
        tab_bar: The QTabBar for displaying tab labels.
        stacked_wdg: The QStackedWidget for displaying tab content.
    """

    def __init__(self):
        """Initialize CustomTabWidget with settings, skin, and exclude tabs."""
        super().__init__()
        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        """Create all child widgets for the tab widget."""
        self.tab_bar = QtWidgets.QTabBar()
        self.tab_bar.setObjectName("customTabBar")
        self.tab_bar.setStyleSheet("#customTabBar {background-color: #383838}")
        self.stacked_wdg = QtWidgets.QStackedWidget()
        self.stacked_wdg.setObjectName("tabBarStackedWidget")
        self.stacked_wdg.setStyleSheet("#tabBarStackedWidget {border: 1px solid #2e2e2e}")

    def create_layout(self):
        """Create and set the layout for the tab widget."""
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.tab_bar)
        main_layout.addWidget(self.stacked_wdg)

    def create_connections(self):
        """Create signal/slot connections for the tab widget."""
        self.tab_bar.currentChanged.connect(self.stacked_wdg.setCurrentIndex)

    def addTab(self, widget, label):
        """Add a new tab to the widget.

        Args:
            widget: Widget to add as tab content.
            label: Tab label text.
        """
        self.tab_bar.addTab(label)
        self.stacked_wdg.addWidget(widget)


class PerseusUI(MayaQWidgetDockableMixin, QtWidgets.QDialog):
    """Facial rig PerseusUI class.

    Main dialog window for the Perseus facial rigging system. Provides a
    dockable interface with tabs for geometry setup, rig settings, and
    skin tools.

    Attributes:
        WINDOW_TITLE: Static title for the window.
        UI_NAME: Static object name for the window.
        ui_instance: Class-level singleton instance reference.
        perseus_dic: Dictionary storing all facial rig data.
        headGeo_wdg: HeadGeoWidget instance for geometry selection.
        settings_wdg: SettingsWidget instance for rig settings.
        skin_wdg: SkinWidget instance for skin operations.
        tab_widget: CustomTabWidget containing all panels.
    """

    WINDOW_TITLE = "Perseus UI"
    UI_NAME = "PerseusUI"
    ui_instance = None
    perseus_dic = {}

    @classmethod
    def show_dialog(cls):
        """Show the facial rig UI dialog.

        Creates a new instance if one doesn't exist, otherwise raises
        the existing instance to the front.

        Returns:
            PerseusUI: The dialog instance.
        """
        version = str(cmds.about(v=1))
        if version != "2017":
            if not cls.ui_instance:
                cls.ui_instance = PerseusUI()
            if cls.ui_instance.isHidden():
                cls.ui_instance.show(dockable=True)
            else:
                cls.ui_instance.raise_()
                cls.ui_instance.activateWindow()
        if version == "2017":
            if not cls.ui_instance:
                cls.ui_instance = PerseusUI()
            if cls.ui_instance.isHidden():
                cls.ui_instance.show(dockable=True)
            else:
                cls.ui_instance.raise_()
                cls.ui_instance.activateWindow()
                cls.ui_instance.show(dockable=True)

    def __init__(self, parent=None):
        """Initialize PerseusUI main dialog window.

        Args:
            parent: Parent Qt widget, defaults to Maya main window if None.
        """
        if parent is None:
            parent = maya_main_window()
        super().__init__(parent)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        self.version = str(cmds.about(v=1))
        self.newExclusion = []
        self.setObjectName(self.__class__.UI_NAME)
        self.sizeHint()
        self.mainNameRig = get_short_license_string() + self.version
        self.setWindowTitle(self.mainNameRig)
        self.geometry = None
        self.create_widgets()
        self.create_layout()
        self.create_connections()
        return

    def showEvent(self, e):
        """Handle show event for the dialog.

        Args:
            e: Show event.
        """
        super().showEvent(e)
        if self.geometry:
            self.restoreGeometry(self.geometry)

    def closeEvent(self, e):
        """Handle close event for the dialog.

        Args:
            e: Close event.
        """
        if isinstance(self, PerseusUI):
            super().closeEvent(e)
            self.geometry = self.saveGeometry()

    def create_widgets(self):
        """Create all child widgets for the tab widget."""
        self.headGeo_wdg = HeadGeoWidget()
        self.settings_wdg = SettingsWidget()
        self.skin_wdg = SkinWidget()
        self.tab_widget = CustomTabWidget()
        self.tab_widget.addTab(self.headGeo_wdg, "Set Models and Components")
        self.tab_widget.addTab(self.settings_wdg, "Facial Settings")
        self.tab_widget.addTab(self.skin_wdg, "Skin Tools")

    def create_layout(self):
        """Create and set the layout for the tab widget."""
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.tab_widget)
        layout.addStretch()

    def create_connections(self):
        """Create signal/slot connections for the tab widget."""
        # Import operations module here to avoid circular imports
        from mayaLib.rigLib.face import operations
        from mayaLib.rigLib.face.skin import skin_export

        # HeadGeoWidget connections
        self.headGeo_wdg.geoBox.clicked.connect(self.LHeadGeoSelUI)
        self.headGeo_wdg.HeadGeoSelBut.clicked.connect(self.sl_headGeo_fn)
        self.headGeo_wdg.REyeGeo.clicked.connect(self.REyeGeoUI)
        self.headGeo_wdg.REyeGeoSelBut.clicked.connect(self.sl_rEyeGeo_fn)
        self.headGeo_wdg.LEyeGeo.clicked.connect(self.LEyeGeoUI)
        self.headGeo_wdg.LEyeGeoSelBut.clicked.connect(self.sl_lEyeGeo_fn)
        self.headGeo_wdg.TopTeethGeo.clicked.connect(self.UpTeethGeoUI)
        self.headGeo_wdg.TopTeethGeoSelBut.clicked.connect(self.sl_topTeethGeo_fn)
        self.headGeo_wdg.DownTeethGeo.clicked.connect(self.DownTeethGeoUI)
        self.headGeo_wdg.DownTeethGeoSelBut.clicked.connect(self.sl_downTeethGeo_fn)
        self.headGeo_wdg.TongueGeo.clicked.connect(self.TongueGeoUI)
        self.headGeo_wdg.TongueGeoSelBut.clicked.connect(self.sl_tongueGeo_fn)
        self.headGeo_wdg.ExtraGeo.clicked.connect(self.ExtraGeoUI)
        self.headGeo_wdg.ExtraGeoSelBut.clicked.connect(self.sl_extraGeo_fn)
        self.headGeo_wdg.REyeLidMainBoxButton.clicked.connect(self.REyeLidMainUI)
        self.headGeo_wdg.RTopDownEyeEdgeSelBut.clicked.connect(self.sl_rEyeLidMain_fn)
        self.headGeo_wdg.LEyeLidMainBoxButton.clicked.connect(self.LEyeLidMainUI)
        self.headGeo_wdg.LTopDownEyeEdgeSelBut.clicked.connect(self.sl_lEyeLidMain_fn)
        self.headGeo_wdg.LEyeLidTopBoxButton.clicked.connect(self.LTopEyeEdgeSelUI)
        self.headGeo_wdg.LEyeLidDownBoxButton.clicked.connect(self.LDownEyeEdgeSelUI)
        self.headGeo_wdg.REyeLidTopBoxButton.clicked.connect(self.RTopEyeEdgeSelUI)
        self.headGeo_wdg.REyeLidDownBoxButton.clicked.connect(self.RDownEyeEdgeSelUI)
        self.headGeo_wdg.LTopEyeEdgeSelBut.clicked.connect(self.sl_lTopEyeEdge_fn)
        self.headGeo_wdg.LDownEyeEdgeSelBut.clicked.connect(self.sl_lDownEyeEdge_fn)
        self.headGeo_wdg.RTopEyeEdgeSelBut.clicked.connect(self.sl_rTopEyeEdge_fn)
        self.headGeo_wdg.RDownEyeEdgeSelBut.clicked.connect(self.sl_rDownEyeEdge_fn)
        self.headGeo_wdg.REyeLidOuterBoxButton.clicked.connect(self.REyeLidOuterUI)
        self.headGeo_wdg.RTopDownEyeOuterEdgeSelBut.clicked.connect(self.sl_rEyeLidOuter_fn)
        self.headGeo_wdg.LEyeLidOuterBoxButton.clicked.connect(self.LEyeLidOuterUI)
        self.headGeo_wdg.LTopDownEyeOuterEdgeSelBut.clicked.connect(self.sl_lEyeLidOuter_fn)
        self.headGeo_wdg.LEyeLidOuterTopBoxButton.clicked.connect(self.LTopEyeOuterEdgeSelUI)
        self.headGeo_wdg.LTopEyeOuterEdgeSelBut.clicked.connect(self.sl_lTopEyeOuterEdge_fn)
        self.headGeo_wdg.LEyeLidOuterDownBoxButton.clicked.connect(self.LDownEyeOuterEdgeSelUI)
        self.headGeo_wdg.LDownEyeOuterEdgeSelBut.clicked.connect(self.sl_lDownEyeOuterEdge_fn)
        self.headGeo_wdg.REyeLidOuterTopBoxButton.clicked.connect(self.RTopEyeOuterEdgeSelUI)
        self.headGeo_wdg.RTopEyeOuterEdgeSelBut.clicked.connect(self.sl_rTopEyeOuterEdge_fn)
        self.headGeo_wdg.REyeLidOuterDownBoxButton.clicked.connect(self.RDownEyeOuterEdgeSelUI)
        self.headGeo_wdg.RDownEyeOuterEdgeSelBut.clicked.connect(self.sl_rDownEyeOuterEdge_fn)
        self.headGeo_wdg.LipBoxButton.clicked.connect(self.LipEdgeUI)
        self.headGeo_wdg.TopDownLipEdgeSelBut.clicked.connect(self.sl_lipTopDown_fn)
        self.headGeo_wdg.LipUpBoxButton.clicked.connect(self.TopLipEdgeSelUI)
        self.headGeo_wdg.TopLipEdgeSelBut.clicked.connect(self.sl_lipTop_fn)
        self.headGeo_wdg.LipDownBoxButton.clicked.connect(self.DownLipEdgeSelUI)
        self.headGeo_wdg.DownLipEdgeSelBut.clicked.connect(self.sl_lipDown_fn)
        self.headGeo_wdg.TongueBoxButton.clicked.connect(self.TongueEdgeUI)
        self.headGeo_wdg.TongueEdgeSelBut.clicked.connect(self.sl_tongueTopDown_fn)
        self.headGeo_wdg.TongueUpEdgeBoxButton.clicked.connect(self.TopTongueEdgeSelUI)
        self.headGeo_wdg.TopTongueEdgeSelBut.clicked.connect(self.sl_tongueTop_fn)
        self.headGeo_wdg.TongueDownEdgeBoxButton.clicked.connect(self.DownTongueEdgeSelUI)
        self.headGeo_wdg.DownTongueEdgeSelBut.clicked.connect(self.sl_tongueDown_fn)
        self.headGeo_wdg.NoseBoxButton.clicked.connect(self.NoseEdgeUI)
        self.headGeo_wdg.NoseEdgeSelBut.clicked.connect(self.sl_noseEdges_fn)
        self.headGeo_wdg.NoseUnderVertexBoxButton.clicked.connect(self.NoseUnderVrtxUI)
        self.headGeo_wdg.NoseUnderVertexSelBut.clicked.connect(self.sl_noseUnderVrtx_fn)
        self.headGeo_wdg.ForeheadBoxButton.clicked.connect(self.ForeheadFaceSelUI)
        self.headGeo_wdg.ForeheadFaceSelButton.clicked.connect(self.sl_foreheadFace_fn)
        self.headGeo_wdg.BackHeadNeckBoxButton.clicked.connect(self.BackHeadNeckFaceSelUI)
        self.headGeo_wdg.BackHeadNeckFaceSelButton.clicked.connect(self.sl_backHeadNeck_fn)
        self.headGeo_wdg.SquashStretchBoxButton.clicked.connect(self.SquashStretchFaceSelUI)
        self.headGeo_wdg.SquashStretchFaceSelButton.clicked.connect(self.sl_squashStretchFace_fn)
        self.headGeo_wdg.LPupilBoxButton.clicked.connect(self.LPupilUI)
        self.headGeo_wdg.LPupilSelButton.clicked.connect(self.sl_LPupil_fn)
        self.headGeo_wdg.RPupilBoxButton.clicked.connect(self.RPupilUI)
        self.headGeo_wdg.RPupilSelButton.clicked.connect(self.sl_RPupil_fn)
        self.headGeo_wdg.LIrisBoxButton.clicked.connect(self.LIrisUI)
        self.headGeo_wdg.LIrisSelButton.clicked.connect(self.sl_LIris_fn)
        self.headGeo_wdg.RIrisBoxButton.clicked.connect(self.RIrisUI)
        self.headGeo_wdg.RIrisSelButton.clicked.connect(self.sl_RIris_fn)
        self.headGeo_wdg.ComponentBut.clicked.connect(self.DuplicateUI)
        self.headGeo_wdg.selConstraintEdgeLoop.clicked.connect(self.EdgeLoopOn_fn)
        self.headGeo_wdg.AdjustmentBoxButton.clicked.connect(self.JawCurveUI)
        self.headGeo_wdg.AdjustmentBBoxButton.clicked.connect(self.FaceCurvesUI)
        self.headGeo_wdg.ProjectBoxButton.clicked.connect(self.projectCrv)

        # SettingsWidget connections
        self.settings_wdg.generateRig.clicked.connect(self.sl_generateRig_fn)
        self.settings_wdg.SaveSettingsBoxButton.clicked.connect(self.FacialSave)
        self.settings_wdg.LoadSettingsBoxButton.clicked.connect(self.FacialLoadUI)
        self.settings_wdg.ResetSettingsBoxButton.clicked.connect(self.FacialResetUI)
        self.settings_wdg.picker.clicked.connect(self.createMGPickerUI)
        self.settings_wdg.SaveCtlShapesBoxButton.clicked.connect(self.FacialSaveCtlShapes)
        self.settings_wdg.LoadCtlShapesBoxButton.clicked.connect(self.FacialLoadCtlShapes)

        # SkinWidget connections
        self.skin_wdg.DEFINE_large.clicked.connect(self.defineExclusionUI)
        self.skin_wdg.EXCLUDE_large.clicked.connect(self.wfexcludeSystem)
        self.skin_wdg.prExportSkin.clicked.connect(skin_export.prExportSkin)
        self.skin_wdg.prImpSkinAll.clicked.connect(skin_export.prImpSkinAll)
        self.skin_wdg.skinCopy.clicked.connect(self.skinCopy)
        self.skin_wdg.source_define.clicked.connect(self.source_define)
        self.skin_wdg.destination_define.clicked.connect(self.destination_define)
        self.skin_wdg.copySkinGlobal.clicked.connect(self.copySkinGlobal)
        self.skin_wdg.hammerSkinGlobal.clicked.connect(self.hammerSkinGlobal)
        self.skin_wdg.SaveFacialSkinSet.clicked.connect(self.SaveFacialSkinSet)
        self.skin_wdg.TransferFacialSkinSet.clicked.connect(self.TransferFacialSkinSet)
        self.skin_wdg.connectBlendShape.clicked.connect(self.connectBlendShape)
        self.skin_wdg.connectBlendShapeB.clicked.connect(self.connectBlendShapeB)
        self.skin_wdg.connectBlendShapeC.clicked.connect(self.connectBlendShapeC)
        self.skin_wdg.connectBlendShapeD.clicked.connect(self.connectBlendShapeD)
        self.skin_wdg.detachSkinJntConnection.clicked.connect(
            lambda: operations.detach_bind_joints()
        )
        self.skin_wdg.attachSkinJntConnection.clicked.connect(
            lambda: operations.attach_bind_joints()
        )

    # =========================================================================
    # Generate Rig Methods
    # =========================================================================

    def sl_generateRig_fn(self):
        """Generate facial rig from selected elements."""
        self.pre_generateRig_fn()
        response = pm.confirmDialog(
            title="Save Settings",
            cancelButton="No",
            defaultButton="Yes",
            button=["Yes", "No"],
            message="Would you like to save your settings?",
            dismissString="No",
        )
        if response == "Yes":
            self.FacialSave()
        self.generateRig_fn()

    def pre_generateRig_fn(self):
        """Pre-process and validate before generating rig."""
        name = self.headGeo_wdg.nameField.text()
        name = name.replace(" ", "")
        self.headGeo_wdg.nameField.setText(name)
        self.perseus_dic["FacialRigName"] = name
        skinJntSuffix = self.headGeo_wdg.skinJntSuffix.text()
        skinJntSuffix = skinJntSuffix.replace(" ", "")
        self.perseus_dic["skinJntSuffix"] = skinJntSuffix
        chkPrefix = int(self.headGeo_wdg.chkPrefix.isChecked())
        chkExtra = int(self.headGeo_wdg.chkExtra.isChecked())
        chkMaintainMaxInf = int(self.settings_wdg.chkMaintainMaxInf.isChecked())
        maxInfs = self.settings_wdg.maxInfs.value()
        relaxSk = self.settings_wdg.relaxSk.value()
        chkGame = int(self.settings_wdg.chkGame.isChecked())
        chkSoftMod = int(self.settings_wdg.chkSoftMod.isChecked())
        chkTweaker = int(self.settings_wdg.chkTweaker.isChecked())
        chkOptLip = int(self.settings_wdg.chkOptLip.isChecked())
        lipJnt = self.settings_wdg.lipJnt.value()
        chkOptEyelidJnt = int(self.settings_wdg.chkOptEyelidJnt.isChecked())
        eyelidJnt = self.settings_wdg.eyelidJnt.value()
        chkOptEye = int(self.settings_wdg.chkOptEye.isChecked())
        eyeCreaseJnt = self.settings_wdg.eyeCreaseJnt.value()
        self.perseus_dic["chkExtra"] = chkExtra
        self.perseus_dic["chkMaintainMaxInf"] = chkMaintainMaxInf
        self.perseus_dic["maxInfs"] = maxInfs
        self.perseus_dic["relaxSk"] = relaxSk
        self.perseus_dic["chkGame"] = chkGame
        self.perseus_dic["chkSoftMod"] = chkSoftMod
        self.perseus_dic["chkTweaker"] = chkTweaker
        self.perseus_dic["chkOptLip"] = chkOptLip
        self.perseus_dic["lipJnt"] = lipJnt
        self.perseus_dic["chkOptEyelidJnt"] = chkOptEyelidJnt
        self.perseus_dic["eyelidJnt"] = eyelidJnt
        self.perseus_dic["chkOptEye"] = chkOptEye
        self.perseus_dic["eyeCreaseJnt"] = eyeCreaseJnt
        self.perseus_dic["chkPrefix"] = chkPrefix

    def generateRig_fn(self):
        """Generate the complete facial rig."""
        pythonVersion = sys.version_info.major
        if pythonVersion == 3:
            from perseus_main_2022 import perseusRigging_facialRig
        else:
            from perseus_main import perseusRigging_facialRig
        prFacialRig = perseusRigging_facialRig()
        prFacialRig.checkCurveGuideExists(self.perseus_dic)

    # =========================================================================
    # Geometry Selection Slot Methods
    # =========================================================================

    def sl_headGeo_fn(self):
        """Store selected geometry in field."""
        cmds.select(self.perseus_dic["LHeadGeoSel"], r=1)

    def sl_rEyeGeo_fn(self):
        """Store selected geometry in field."""
        cmds.select(self.perseus_dic["REyeGeoSel"], r=1)

    def sl_lEyeGeo_fn(self):
        """Store selected geometry in field."""
        cmds.select(self.perseus_dic["LEyeGeoSel"], r=1)

    def sl_topTeethGeo_fn(self):
        """Store selected geometry in field."""
        cmds.select(self.perseus_dic["TopTeethGeoSel"], r=1)

    def sl_downTeethGeo_fn(self):
        """Store selected geometry in field."""
        cmds.select(self.perseus_dic["DownTeethGeoSel"], r=1)

    def sl_tongueGeo_fn(self):
        """Store selected geometry in field."""
        cmds.select(self.perseus_dic["TongueGeoSel"], r=1)

    def sl_extraGeo_fn(self):
        """Store selected geometry in field."""
        cmds.select(self.perseus_dic["ExtraGeoSel"], r=1)

    # =========================================================================
    # Eye Lid Edge Selection Slots
    # =========================================================================

    def sl_rEyeLidMain_fn(self):
        """Store selected main control in field."""
        self.checkVarExistsB(
            self.perseus_dic["RTopEyeEdgeSel"], self.perseus_dic["RDownEyeEdgeSel"], 0, 1
        )

    def sl_lEyeLidMain_fn(self):
        """Store selected main control in field."""
        self.checkVarExistsB(
            self.perseus_dic["LTopEyeEdgeSel"], self.perseus_dic["LDownEyeEdgeSel"], 0, 1
        )

    def sl_lTopEyeEdge_fn(self):
        """Store selected edges in field."""
        self.checkVarExists(self.perseus_dic["LTopEyeEdgeSel"], 0, 1)

    def sl_lDownEyeEdge_fn(self):
        """Store selected edges in field."""
        self.checkVarExists(self.perseus_dic["LDownEyeEdgeSel"], 0, 1)

    def sl_rTopEyeEdge_fn(self):
        """Store selected edges in field."""
        self.checkVarExists(self.perseus_dic["RTopEyeEdgeSel"], 0, 1)

    def sl_rDownEyeEdge_fn(self):
        """Store selected edges in field."""
        self.checkVarExists(self.perseus_dic["RDownEyeEdgeSel"], 0, 1)

    def sl_rEyeLidOuter_fn(self):
        """Store selected object from Maya selection."""
        self.checkVarExistsB(
            self.perseus_dic["RTopEyeOuterEdgeSel"],
            self.perseus_dic["RDownEyeOuterEdgeSel"],
            0,
            1,
        )

    def sl_lEyeLidOuter_fn(self):
        """Store selected object from Maya selection."""
        self.checkVarExistsB(
            self.perseus_dic["LTopEyeOuterEdgeSel"],
            self.perseus_dic["LDownEyeOuterEdgeSel"],
            0,
            1,
        )

    def sl_lTopEyeOuterEdge_fn(self):
        """Store selected edges in field."""
        self.checkVarExists(self.perseus_dic["LTopEyeOuterEdgeSel"], 0, 1)

    def sl_lDownEyeOuterEdge_fn(self):
        """Store selected edges in field."""
        self.checkVarExists(self.perseus_dic["LDownEyeOuterEdgeSel"], 0, 1)

    def sl_rTopEyeOuterEdge_fn(self):
        """Store selected edges in field."""
        self.checkVarExists(self.perseus_dic["RTopEyeOuterEdgeSel"], 0, 1)

    def sl_rDownEyeOuterEdge_fn(self):
        """Store selected edges in field."""
        self.checkVarExists(self.perseus_dic["RDownEyeOuterEdgeSel"], 0, 1)

    # =========================================================================
    # Lip Edge Selection Slots
    # =========================================================================

    def sl_lipTopDown_fn(self):
        """Store selected object from Maya selection."""
        self.checkVarExistsB(
            self.perseus_dic["DownLipEdgeSel"], self.perseus_dic["TopLipEdgeSel"], 0, 1
        )

    def sl_lipTop_fn(self):
        """Store selected object from Maya selection."""
        self.checkVarExists(self.perseus_dic["TopLipEdgeSel"], 0, 1)

    def sl_lipDown_fn(self):
        """Store selected object from Maya selection."""
        self.checkVarExists(self.perseus_dic["DownLipEdgeSel"], 0, 1)

    def sl_tongueTopDown_fn(self):
        """Store selected object from Maya selection."""
        self.checkVarExistsB(
            self.perseus_dic["DownTongueEdgeSel"],
            self.perseus_dic["TopTongueEdgeSel"],
            0,
            1,
        )

    def sl_tongueTop_fn(self):
        """Store selected object from Maya selection."""
        self.checkVarExists(self.perseus_dic["TopTongueEdgeSel"], 0, 1)

    def sl_tongueDown_fn(self):
        """Store selected object from Maya selection."""
        self.checkVarExists(self.perseus_dic["DownTongueEdgeSel"], 0, 1)

    def sl_noseEdges_fn(self):
        """Select and store edge loop from Maya selection."""
        self.checkVarExists(self.perseus_dic["NoseEdgeSel"], 0, 1)

    def sl_noseUnderVrtx_fn(self):
        """Store selected object from Maya selection."""
        self.checkVarExists(self.perseus_dic["NoseUnderVertexSel"], 0, 0)

    def sl_foreheadFace_fn(self):
        """Store selected object from Maya selection."""
        self.checkVarExists(self.perseus_dic["ForeheadFaceSel"], 1, 2)

    def sl_backHeadNeck_fn(self):
        """Store selected object from Maya selection."""
        self.checkVarExists(self.perseus_dic["BackHeadNeckFaceSel"], 0, 2)

    def sl_squashStretchFace_fn(self):
        """Store selected object from Maya selection."""
        self.checkVarExists(self.perseus_dic["SquashStretchFaceSel"], 0, 2)

    def sl_LPupil_fn(self):
        """Store selected object from Maya selection."""
        self.checkVarExists(self.perseus_dic["LPupilSel"], 0, 2)

    def sl_RPupil_fn(self):
        """Store selected object from Maya selection."""
        self.checkVarExists(self.perseus_dic["RPupilSel"], 0, 2)

    def sl_LIris_fn(self):
        """Store selected object from Maya selection."""
        self.checkVarExists(self.perseus_dic["LIrisSel"], 0, 2)

    def sl_RIris_fn(self):
        """Store selected object from Maya selection."""
        self.checkVarExists(self.perseus_dic["RIrisSel"], 0, 2)

    # =========================================================================
    # Geometry UI Selection Methods
    # =========================================================================

    def LHeadGeoSelUI(self):
        """Select head geometry from current Maya selection."""
        LHeadGeoSel = cmds.ls(sl=1)[0]
        chkNameSpace = int(len(LHeadGeoSel.split(":")))
        if chkNameSpace > 1:
            cmds.namespace(
                removeNamespace=":" + LHeadGeoSel.split(":")[0], mergeNamespaceWithParent=True
            )
        LHeadGeoSel = cmds.ls(sl=1)[0]
        self.perseus_dic["LHeadGeoSel"] = LHeadGeoSel
        self.headGeo_wdg.geoField.setText(LHeadGeoSel)

    def REyeGeoUI(self):
        """Select right eye geometry from current Maya selection."""
        REyeGeoSel = cmds.ls(sl=1)[0]
        chkNameSpace = int(len(REyeGeoSel.split(":")))
        if chkNameSpace > 1:
            cmds.namespace(
                removeNamespace=":" + REyeGeoSel.split(":")[0], mergeNamespaceWithParent=True
            )
        REyeGeoSel = cmds.ls(sl=1)[0]
        self.perseus_dic["REyeGeoSel"] = REyeGeoSel
        self.headGeo_wdg.REyeBox.setText(REyeGeoSel)

    def LEyeGeoUI(self):
        """Select left eye geometry from current Maya selection."""
        LEyeGeoSel = cmds.ls(sl=1)[0]
        chkNameSpace = int(len(LEyeGeoSel.split(":")))
        if chkNameSpace > 1:
            cmds.namespace(
                removeNamespace=":" + LEyeGeoSel.split(":")[0], mergeNamespaceWithParent=True
            )
        LEyeGeoSel = cmds.ls(sl=1)[0]
        self.perseus_dic["LEyeGeoSel"] = LEyeGeoSel
        self.headGeo_wdg.LEyeBox.setText(LEyeGeoSel)

    def UpTeethGeoUI(self):
        """Select upper teeth geometry from current Maya selection."""
        TopTeethGeoSel = cmds.ls(sl=1)[0]
        chkNameSpace = int(len(TopTeethGeoSel.split(":")))
        if chkNameSpace > 1:
            cmds.namespace(
                removeNamespace=":" + TopTeethGeoSel.split(":")[0], mergeNamespaceWithParent=True
            )
        TopTeethGeoSel = cmds.ls(sl=1)[0]
        self.perseus_dic["TopTeethGeoSel"] = TopTeethGeoSel
        self.headGeo_wdg.UpTeethBox.setText(TopTeethGeoSel)

    def DownTeethGeoUI(self):
        """Select lower teeth geometry from current Maya selection."""
        DownTeethGeoSel = cmds.ls(sl=1)[0]
        chkNameSpace = int(len(DownTeethGeoSel.split(":")))
        if chkNameSpace > 1:
            cmds.namespace(
                removeNamespace=":" + DownTeethGeoSel.split(":")[0],
                mergeNamespaceWithParent=True,
            )
        DownTeethGeoSel = cmds.ls(sl=1)[0]
        self.perseus_dic["DownTeethGeoSel"] = DownTeethGeoSel
        self.headGeo_wdg.DownTeethBox.setText(DownTeethGeoSel)

    def TongueGeoUI(self):
        """Select tongue geometry from current Maya selection."""
        TongueGeoSel = cmds.ls(sl=1)[0]
        chkNameSpace = int(len(TongueGeoSel.split(":")))
        if chkNameSpace > 1:
            cmds.namespace(
                removeNamespace=":" + TongueGeoSel.split(":")[0], mergeNamespaceWithParent=True
            )
        TongueGeoSel = cmds.ls(sl=1)[0]
        self.perseus_dic["TongueGeoSel"] = TongueGeoSel
        self.headGeo_wdg.TongueBox.setText(TongueGeoSel)

    def ExtraGeoUI(self):
        """Select extra geometry from current Maya selection."""
        ExtraGeoSel = cmds.ls(sl=1)
        self.perseus_dic["ExtraGeoSel"] = ExtraGeoSel
        self.headGeo_wdg.ExtraBox.setText(str(ExtraGeoSel))
        self.headGeo_wdg.chkExtra.setChecked(True)
        pm.parent(w=1)

    # =========================================================================
    # Eye Lid UI Methods
    # =========================================================================

    def REyeLidMainUI(self):
        """Select right eye lid edges and determine top/bottom automatically."""
        RTopEyeEdgeSel = self.findEdgeUpDown(0)
        RDownEyeEdgeSel = self.findEdgeUpDown(1)
        cmds.select(RDownEyeEdgeSel[int(int(len(RDownEyeEdgeSel) / 2))], r=1)
        downVV = cmds.xform(q=1, ws=1, t=1)
        cmds.select(RTopEyeEdgeSel[int(int(len(RTopEyeEdgeSel) / 2))], r=1)
        topVV = cmds.xform(q=1, ws=1, t=1)
        cmds.select(RTopEyeEdgeSel, r=1)
        if downVV[1] > topVV[1]:
            temp = RTopEyeEdgeSel
            RTopEyeEdgeSel = RDownEyeEdgeSel
            RDownEyeEdgeSel = temp
        self.perseus_dic["RTopEyeEdgeSel"] = RTopEyeEdgeSel
        self.perseus_dic["RDownEyeEdgeSel"] = RDownEyeEdgeSel
        self.headGeo_wdg.chkREyeLid.setChecked(True)

    def LEyeLidMainUI(self):
        """Select left eye lid edges and determine top/bottom automatically."""
        LTopEyeEdgeSel = self.findEdgeUpDown(0)
        LDownEyeEdgeSel = self.findEdgeUpDown(1)
        cmds.select(LDownEyeEdgeSel[int(int(len(LDownEyeEdgeSel) / 2))], r=1)
        downVV = cmds.xform(q=1, ws=1, t=1)
        cmds.select(LTopEyeEdgeSel[int(int(len(LTopEyeEdgeSel) / 2))], r=1)
        topVV = cmds.xform(q=1, ws=1, t=1)
        cmds.select(LTopEyeEdgeSel, r=1)
        if downVV[1] > topVV[1]:
            temp = LTopEyeEdgeSel
            LTopEyeEdgeSel = LDownEyeEdgeSel
            LDownEyeEdgeSel = temp
        self.perseus_dic["LTopEyeEdgeSel"] = LTopEyeEdgeSel
        self.perseus_dic["LDownEyeEdgeSel"] = LDownEyeEdgeSel
        self.headGeo_wdg.chkLEyeLid.setChecked(True)

    def REyeLidOuterUI(self):
        """Select right outer eye lid edges."""
        RTopEyeOuterEdgeSel = self.findEdgeUpDown(0)
        RDownEyeOuterEdgeSel = self.findEdgeUpDown(1)
        cmds.select(RDownEyeOuterEdgeSel[int(int(len(RDownEyeOuterEdgeSel) / 2))], r=1)
        downVV = cmds.xform(q=1, ws=1, t=1)
        cmds.select(RTopEyeOuterEdgeSel[int(int(len(RTopEyeOuterEdgeSel) / 2))], r=1)
        topVV = cmds.xform(q=1, ws=1, t=1)
        cmds.select(RTopEyeOuterEdgeSel, r=1)
        if downVV[1] > topVV[1]:
            temp = RTopEyeOuterEdgeSel
            RTopEyeOuterEdgeSel = RDownEyeOuterEdgeSel
            RDownEyeOuterEdgeSel = temp
        self.perseus_dic["RTopEyeOuterEdgeSel"] = RTopEyeOuterEdgeSel
        self.perseus_dic["RDownEyeOuterEdgeSel"] = RDownEyeOuterEdgeSel
        self.headGeo_wdg.chkREyeOuterLid.setChecked(True)

    def LEyeLidOuterUI(self):
        """Select left outer eye lid edges."""
        LTopEyeOuterEdgeSel = self.findEdgeUpDown(0)
        LDownEyeOuterEdgeSel = self.findEdgeUpDown(1)
        cmds.select(LDownEyeOuterEdgeSel[int(int(len(LDownEyeOuterEdgeSel) / 2))], r=1)
        downVV = cmds.xform(q=1, ws=1, t=1)
        cmds.select(LTopEyeOuterEdgeSel[int(int(len(LTopEyeOuterEdgeSel) / 2))], r=1)
        topVV = cmds.xform(q=1, ws=1, t=1)
        cmds.select(LTopEyeOuterEdgeSel, r=1)
        if downVV[1] > topVV[1]:
            temp = LTopEyeOuterEdgeSel
            LTopEyeOuterEdgeSel = LDownEyeOuterEdgeSel
            LDownEyeOuterEdgeSel = temp
        self.perseus_dic["LTopEyeOuterEdgeSel"] = LTopEyeOuterEdgeSel
        self.perseus_dic["LDownEyeOuterEdgeSel"] = LDownEyeOuterEdgeSel
        self.headGeo_wdg.chkLEyeOuterLid.setChecked(True)

    def LTopEyeEdgeSelUI(self):
        """Select left top eye edge from current selection."""
        LTopEyeEdgeSel = cmds.ls(sl=1)
        self.perseus_dic["LTopEyeEdgeSel"] = LTopEyeEdgeSel

    def LDownEyeEdgeSelUI(self):
        """Select left down eye edge from current selection."""
        LDownEyeEdgeSel = cmds.ls(sl=1)
        self.perseus_dic["LDownEyeEdgeSel"] = LDownEyeEdgeSel

    def RTopEyeEdgeSelUI(self):
        """Select right top eye edge from current selection."""
        RTopEyeEdgeSel = cmds.ls(sl=1)
        self.perseus_dic["RTopEyeEdgeSel"] = RTopEyeEdgeSel

    def RDownEyeEdgeSelUI(self):
        """Select right down eye edge from current selection."""
        RDownEyeEdgeSel = cmds.ls(sl=1)
        self.perseus_dic["RDownEyeEdgeSel"] = RDownEyeEdgeSel

    def LTopEyeOuterEdgeSelUI(self):
        """Select left top outer eye edge from current selection."""
        LTopEyeOuterEdgeSel = cmds.ls(sl=1)
        self.perseus_dic["LTopEyeOuterEdgeSel"] = LTopEyeOuterEdgeSel

    def LDownEyeOuterEdgeSelUI(self):
        """Select left down outer eye edge from current selection."""
        LDownEyeOuterEdgeSel = cmds.ls(sl=1)
        self.perseus_dic["LDownEyeOuterEdgeSel"] = LDownEyeOuterEdgeSel

    def RTopEyeOuterEdgeSelUI(self):
        """Select right top outer eye edge from current selection."""
        RTopEyeOuterEdgeSel = cmds.ls(sl=1)
        self.perseus_dic["RTopEyeOuterEdgeSel"] = RTopEyeOuterEdgeSel

    def RDownEyeOuterEdgeSelUI(self):
        """Select right down outer eye edge from current selection."""
        RDownEyeOuterEdgeSel = cmds.ls(sl=1)
        self.perseus_dic["RDownEyeOuterEdgeSel"] = RDownEyeOuterEdgeSel

    # =========================================================================
    # Lip and Tongue UI Methods
    # =========================================================================

    def LipEdgeUI(self):
        """Select lip edges and determine top/bottom automatically."""
        TopLipEdgeSel = self.findEdgeUpDown(0)
        DownLipEdgeSel = self.findEdgeUpDown(1)
        cmds.select(DownLipEdgeSel[int(int(len(DownLipEdgeSel) / 2))], r=1)
        downVV = cmds.xform(q=1, ws=1, t=1)
        cmds.select(TopLipEdgeSel[int(int(len(TopLipEdgeSel) / 2))], r=1)
        topVV = cmds.xform(q=1, ws=1, t=1)
        if downVV[1] > topVV[1]:
            temp = TopLipEdgeSel
            TopLipEdgeSel = DownLipEdgeSel
            DownLipEdgeSel = temp
        cmds.select(TopLipEdgeSel, r=1)
        self.perseus_dic["TopLipEdgeSel"] = TopLipEdgeSel
        self.perseus_dic["DownLipEdgeSel"] = DownLipEdgeSel
        self.headGeo_wdg.chkLip.setChecked(True)

    def TopLipEdgeSelUI(self):
        """Select top lip edge from current selection."""
        TopLipEdgeSel = cmds.ls(sl=1)
        self.perseus_dic["TopLipEdgeSel"] = TopLipEdgeSel

    def DownLipEdgeSelUI(self):
        """Select down lip edge from current selection."""
        DownLipEdgeSel = cmds.ls(sl=1)
        self.perseus_dic["DownLipEdgeSel"] = DownLipEdgeSel

    def TopTongueEdgeSelUI(self):
        """Select top tongue edge from current selection."""
        TopTongueEdgeSel = cmds.ls(sl=1)
        self.perseus_dic["TopTongueEdgeSel"] = TopTongueEdgeSel

    def DownTongueEdgeSelUI(self):
        """Select down tongue edge from current selection."""
        DownTongueEdgeSel = cmds.ls(sl=1)
        self.perseus_dic["DownTongueEdgeSel"] = DownTongueEdgeSel
        self.headGeo_wdg.chkTonque.setChecked(True)

    def TongueEdgeUI(self):
        """Select tongue edges and determine top/bottom automatically."""
        TopTongueEdgeSel = self.findEdgeUpDownTongue(0)
        DownTongueEdgeSel = self.findEdgeUpDownTongue(1)
        self.perseus_dic["TopTongueEdgeSel"] = TopTongueEdgeSel
        self.perseus_dic["DownTongueEdgeSel"] = DownTongueEdgeSel
        self.headGeo_wdg.chkTonque.setChecked(True)

    # =========================================================================
    # Nose, Forehead, and Face Selection Methods
    # =========================================================================

    def NoseEdgeUI(self):
        """Select nose edges from current selection."""
        cmds.ConvertSelectionToVertices()
        NoseEdgeSel = cmds.ls(fl=1, sl=1)
        cmds.ConvertSelectionToContainedEdges()
        self.perseus_dic["NoseEdgeSel"] = NoseEdgeSel
        self.headGeo_wdg.chkNoseEdge.setChecked(True)

    def NoseUnderVrtxUI(self):
        """Select nose under vertex from current selection."""
        cmds.ConvertSelectionToVertices()
        NoseUnderVertexSel = cmds.ls(fl=1, sl=1)
        self.perseus_dic["NoseUnderVertexSel"] = NoseUnderVertexSel
        self.headGeo_wdg.chkNoseUnderVertex.setChecked(True)

    def ForeheadFaceSelUI(self):
        """Select forehead faces from current selection."""
        LHeadGeoSel = self.perseus_dic["LHeadGeoSel"]
        cmds.ConvertSelectionToVertices()
        excludeJnt = cmds.ls(type="joint", sl=1)
        cmds.select(excludeJnt, d=1)
        ForeheadFaceSelEx = cmds.ls(fl=1, sl=1)
        headGeoName = LHeadGeoSel
        cmds.select(headGeoName + ".vtx[*]", r=1)
        cmds.select(ForeheadFaceSelEx, d=1)
        ForeheadFaceSel = cmds.ls(fl=1, sl=1)
        cmds.select(ForeheadFaceSelEx, r=1)
        self.perseus_dic["ForeheadFaceSel"] = ForeheadFaceSel
        self.headGeo_wdg.checkForeheadFace.setChecked(True)

    def BackHeadNeckFaceSelUI(self):
        """Select back head and neck faces from current selection."""
        cmds.ConvertSelectionToVertices()
        excludeJnt = cmds.ls(type="joint", sl=1)
        cmds.select(excludeJnt, d=1)
        BackHeadNeckFaceSel = cmds.ls(fl=1, sl=1)
        self.perseus_dic["BackHeadNeckFaceSel"] = BackHeadNeckFaceSel
        self.headGeo_wdg.chkBackFace.setChecked(True)

    def SquashStretchFaceSelUI(self):
        """Select squash/stretch faces from current selection."""
        cmds.ConvertSelectionToVertices()
        excludeJnt = cmds.ls(type="joint", sl=1)
        cmds.select(excludeJnt, d=1)
        SquashStretchFaceSel = cmds.ls(fl=1, sl=1)
        self.perseus_dic["SquashStretchFaceSel"] = SquashStretchFaceSel
        self.headGeo_wdg.checkSquashStretchFace.setChecked(True)

    # =========================================================================
    # Pupil and Iris Selection Methods
    # =========================================================================

    def LPupilUI(self):
        """Select left pupil from current selection."""
        cmds.ConvertSelectionToVertices()
        excludeJnt = cmds.ls(type="joint", sl=1)
        cmds.select(excludeJnt, d=1)
        LPupilSel = cmds.ls(fl=1, sl=1)
        self.perseus_dic["LPupilSel"] = LPupilSel
        self.headGeo_wdg.chkLPupil.setChecked(True)

    def RPupilUI(self):
        """Select right pupil from current selection."""
        cmds.ConvertSelectionToVertices()
        excludeJnt = cmds.ls(type="joint", sl=1)
        cmds.select(excludeJnt, d=1)
        LPupilSel = cmds.ls(fl=1, sl=1)
        self.perseus_dic["RPupilSel"] = LPupilSel
        self.headGeo_wdg.chkRPupil.setChecked(True)

    def LIrisUI(self):
        """Select left iris from current selection."""
        cmds.ConvertSelectionToVertices()
        excludeJnt = cmds.ls(type="joint", sl=1)
        cmds.select(excludeJnt, d=1)
        LPupilSel = cmds.ls(fl=1, sl=1)
        self.perseus_dic["LIrisSel"] = LPupilSel
        self.headGeo_wdg.chkLIris.setChecked(True)

    def RIrisUI(self):
        """Select right iris from current selection."""
        cmds.ConvertSelectionToVertices()
        excludeJnt = cmds.ls(type="joint", sl=1)
        cmds.select(excludeJnt, d=1)
        LPupilSel = cmds.ls(fl=1, sl=1)
        self.perseus_dic["RIrisSel"] = LPupilSel
        self.headGeo_wdg.chkRIris.setChecked(True)

    # =========================================================================
    # Edge Loop Methods
    # =========================================================================

    def EdgeLoopOn_fn(self):
        """Toggle edge loop selection constraint."""
        if not self.headGeo_wdg.edgeLoopToggle:
            pm.mel.dR_selConstraintEdgeLoop()
            self.headGeo_wdg.selConstraintEdgeLoop.setStyleSheet(
                self.headGeo_wdg.darkColorB
            )
            self.headGeo_wdg.selConstraintEdgeLoop.setText("Edge Loop On")
            self.headGeo_wdg.edgeLoopToggle = True
        else:
            pm.mel.dR_selConstraintOff()
            self.headGeo_wdg.selConstraintEdgeLoop.setStyleSheet(
                self.headGeo_wdg.defaultColor
            )
            self.headGeo_wdg.selConstraintEdgeLoop.setText("Edge Loop Off")
            self.headGeo_wdg.edgeLoopToggle = False

    def EdgeLoopOff_fn(self):
        """Turn off edge loop selection constraint."""
        pm.mel.dR_selConstraintOff()

    # =========================================================================
    # Duplicate and Adjustment Methods
    # =========================================================================

    def DuplicateUI(self):
        """Duplicate geometry for component setup."""
        cmds.select(cl=1)
        LHeadGeoSel = self.perseus_dic["LHeadGeoSel"]
        LEyeGeoSel = self.perseus_dic["LEyeGeoSel"]
        REyeGeoSel = self.perseus_dic["REyeGeoSel"]
        TopTeethGeoSel = self.perseus_dic["TopTeethGeoSel"]
        DownTeethGeoSel = self.perseus_dic["DownTeethGeoSel"]
        TongueGeoSel = self.perseus_dic["TongueGeoSel"]
        cmds.select(
            LHeadGeoSel,
            LEyeGeoSel,
            REyeGeoSel,
            TopTeethGeoSel,
            DownTeethGeoSel,
            TongueGeoSel,
            r=1,
        )
        self.wffacialDuplicate()
        self.headGeo_wdg.componentLayoutGrp.setChecked(True)

    def wffacialDuplicate(self):
        """Create facial geometry duplicate setup."""
        pm.displaySmoothness(
            pointsWire=4, polygonObject=1, pointsShaded=1, divisionsV=0, divisionsU=0
        )
        selected_objects = pm.ls(sl=1)
        pm.select(cl=1)
        if pm.objExists("curve1"):
            pm.rename("curve1", "curve1_temp_perseus")
        if pm.objExists("curve2"):
            pm.rename("curve2", "curve2_temp_perseus")
        if pm.objExists("facial_geo_grp"):
            pass
        else:
            pm.group(em=1, n="facial_geo_grp")
            pm.select(cl=1)
            for obj in selected_objects:
                pm.select(obj, r=1)
                pm.parent(obj, "facial_geo_grp")

        pm.select(selected_objects[0], r=1)
        if not self.headGeo_wdg.edgeLoopToggle:
            self.EdgeLoopOn_fn()

    def JawCurveUI(self):
        """Create jaw adjustment curves."""
        from mayaLib.rigLib.face.operations import adjustment

        adjustment.jaw_curve_ui(self)

    def FaceCurvesUI(self):
        """Create face adjustment curves."""
        from mayaLib.rigLib.face.operations import adjustment

        adjustment.face_curves_ui(self)

    def projectCrv(self):
        """Project curves onto geometry."""
        from mayaLib.rigLib.face.operations import adjustment

        adjustment.project_curves(self)

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def wflrRename(self):
        """Rename left side objects to right side."""
        sels = pm.ls(sl=1)
        s = len(sels) - 1
        while s >= 0:
            sel = sels[s]
            size = len(sel)
            last = sel[size - 1 : size]
            if last == "1" or last == "2":
                pm.rename(sel, "r_" + sel[2 : size - 1])
            else:
                pm.rename(sel, "r_" + sel[2:size])
            s -= 1

    def wflrConnect(self):
        """Connect left side transforms to right side."""
        sels = cmds.ls(transforms=1, sl=1)
        for sel in sels:
            size = len(sel)
            cmds.connectAttr(str(sel) + ".t", "r_" + sel[2:size] + ".t")
            cmds.connectAttr(str(sel) + ".r", "r_" + sel[2:size] + ".r")
            cmds.connectAttr(str(sel) + ".s", "r_" + sel[2:size] + ".s")
            cmds.setAttr("r_" + sel[2:size] + ".overrideColor", 1)

    def checkVarExists(self, new_list, invert, conversion_type):
        """Check if variable exists and select it.

        Args:
            new_list: List of components to select.
            invert: Whether to invert selection.
            conversion_type: Type of component conversion.
        """
        LHeadGeoSel = self.perseus_dic["LHeadGeoSel"]
        if len(new_list) != 0:
            pm.select(new_list, r=1)
            if invert == 1:
                cmds.ConvertSelectionToVertices()
                headGeoName = LHeadGeoSel
                pm.select(headGeoName + ".vtx[*]", r=1)
                pm.select(new_list, d=1)
            if len(new_list) != 1:
                if conversion_type == 0:
                    cmds.ConvertSelectionToVertices()
                if conversion_type == 1:
                    cmds.ConvertSelectionToVertices()
                if conversion_type == 2:
                    cmds.ConvertSelectionToVertices()
        else:
            pm.select(cl=1)

    def checkVarExistsB(self, new_list, new_list_b, invert, conversion_type):
        """Check if two variables exist and select them.

        Args:
            new_list: First list of components.
            new_list_b: Second list of components.
            invert: Whether to invert selection.
            conversion_type: Type of component conversion.
        """
        if len(new_list) != 0:
            pm.select(new_list, new_list_b, r=1)
            if invert == 1:
                pm.mel.invertSelection()
            if len(new_list) != 1:
                if conversion_type == 0:
                    cmds.ConvertSelectionToContainedEdges()
                if conversion_type == 1:
                    cmds.ConvertSelectionToContainedEdges()
                if conversion_type == 2:
                    cmds.ConvertSelectionToContainedEdges()
        else:
            pm.select(cl=1)

    def findEdgeUpDown(self, up_down):
        """Find edge loop vertices in up/down order.

        Args:
            up_down: 0 for top edges, 1 for bottom edges.

        Returns:
            list: Ordered list of vertex names.
        """
        LHeadGeoSel = self.perseus_dic["LHeadGeoSel"]
        vertexList = []
        name = LHeadGeoSel
        edgeSel = cmds.ls(fl=1, sl=1)
        cmds.ConvertSelectionToVertices()
        vertexList = cmds.ls(fl=1, sl=1)
        posX = []
        first = []
        end = []
        for i in range(0, len(vertexList)):
            pos = cmds.xform(vertexList[i], q=1, t=1)
            posX.append(pos[0])

        posSort = sorted(posX)
        for i in range(0, len(vertexList)):
            pos = cmds.xform(vertexList[i], q=1, t=1)
            if pos[0] == posSort[0]:
                cmds.select(vertexList[i], r=1)
                first = cmds.ls(sl=1)
            if pos[0] == posSort[(len(vertexList) - 1)]:
                cmds.select(vertexList[i], r=1)
                end = cmds.ls(sl=1)

        cmds.select(first, r=1)
        cmds.select(end, r=1)
        cmds.select(first, r=1)
        cmds.GrowPolygonSelectionRegion()
        cmds.select(first, end, d=1)
        selNew = cmds.ls(fl=1, sl=1)
        cmds.select(cl=1)
        for i in range(0, len(vertexList)):
            for j in range(0, len(selNew)):
                if selNew[j] == vertexList[i]:
                    cmds.select(selNew[j], tgl=1)

        upDownSel = cmds.ls(fl=1, sl=1)
        pos1 = cmds.xform(upDownSel[0], q=1, t=1)
        pos2 = cmds.xform(upDownSel[1], q=1, t=1)
        if up_down == 1:
            if pos1[1] < pos2[1]:
                cmds.select(upDownSel[0], r=1)
            else:
                cmds.select(upDownSel[1], r=1)
        else:
            if up_down == 0:
                if pos1[1] > pos2[1]:
                    cmds.select(upDownSel[0], r=1)
                else:
                    cmds.select(upDownSel[1], r=1)
            downVertex = []
            downVertex.append(first[0])
            second = cmds.ls(fl=1, sl=1)
            downVertex.append(second[0])
            for k in range(2, len(vertexList)):
                cmds.GrowPolygonSelectionRegion()
                cmds.select(downVertex[(k - 2)], downVertex[(k - 1)], d=1)
                selNew = cmds.ls(fl=1, sl=1)
                cmds.select(cl=1)
                for i in range(0, len(vertexList)):
                    for j in range(0, len(selNew)):
                        if selNew[j] == vertexList[i]:
                            cmds.select(selNew[j], add=1)

                self.wfFixEdgeLoopA(up_down)
                second = cmds.ls(fl=1, sl=1)
                pos1 = cmds.xform(second[0], q=1, t=1)
                pos2 = cmds.xform(end[0], q=1, t=1)
                if pos1[0] == pos2[0] and pos1[1] == pos2[1]:
                    break
                downVertex.append(second[0])

        downVertex.append(end[0])
        cmds.select(edgeSel, r=1)
        cmds.ConvertSelectionToContainedEdges()
        if not self.headGeo_wdg.edgeLoopToggle:
            self.EdgeLoopOn_fn()
        pm.catch(lambda: pm.mel.doMenuComponentSelection(name, "edge"))
        return downVertex

    def wfFixEdgeLoopA(self, up_down):
        """Fix edge loop selection ambiguity.

        Args:
            up_down: 0 for top, 1 for bottom.
        """
        upDownSel = cmds.ls(fl=1, sl=1)
        if len(upDownSel) == 2:
            upDownSel = cmds.ls(fl=1, sl=1)
            pos1 = cmds.xform(upDownSel[0], q=1, t=1)
            pos2 = cmds.xform(upDownSel[1], q=1, t=1)
            if up_down == 1:
                if pos1[1] < pos2[1]:
                    cmds.select(upDownSel[0], r=1)
                else:
                    cmds.select(upDownSel[1], r=1)
            elif up_down == 0:
                if pos1[1] > pos2[1]:
                    cmds.select(upDownSel[0], r=1)
                else:
                    cmds.select(upDownSel[1], r=1)

    def findEdgeUpDownTongue(self, up_down):
        """Find tongue edge vertices in up/down order.

        Args:
            up_down: 0 for top, 1 for bottom.

        Returns:
            list: Ordered list of vertex names.
        """
        self.perseus_dic["LHeadGeoSel"]
        vertexList = []
        edgeSel = cmds.ls(fl=1, sl=1)
        cmds.ConvertSelectionToVertices()
        vertexList = cmds.ls(fl=1, sl=1)
        posX = []
        first = []
        end = []
        for i in range(0, len(vertexList)):
            pos = cmds.xform(vertexList[i], q=1, t=1)
            posX.append(pos[2])

        posSort = sorted(posX)
        for i in range(0, len(vertexList)):
            pos = cmds.xform(vertexList[i], q=1, t=1)
            if pos[2] == posSort[0]:
                cmds.select(vertexList[i], r=1)
                first = cmds.ls(sl=1)
            if pos[2] == posSort[(len(vertexList) - 1)]:
                cmds.select(vertexList[i], r=1)
                end = cmds.ls(sl=1)

        cmds.select(first, r=1)
        cmds.select(end, r=1)
        cmds.select(first, r=1)
        cmds.GrowPolygonSelectionRegion()
        cmds.select(first, end, d=1)
        selNew = cmds.ls(fl=1, sl=1)
        cmds.select(cl=1)
        for i in range(0, len(vertexList)):
            for j in range(0, len(selNew)):
                if selNew[j] == vertexList[i]:
                    cmds.select(selNew[j], tgl=1)

        upDownSel = cmds.ls(fl=1, sl=1)
        pos1 = cmds.xform(upDownSel[0], q=1, t=1)
        pos2 = cmds.xform(upDownSel[1], q=1, t=1)
        if up_down == 1:
            if pos1[1] < pos2[1]:
                cmds.select(upDownSel[0], r=1)
            else:
                cmds.select(upDownSel[1], r=1)
        else:
            if up_down == 0:
                if pos1[1] > pos2[1]:
                    cmds.select(upDownSel[0], r=1)
                else:
                    cmds.select(upDownSel[1], r=1)
            downVertex = []
            downVertex = []
            downVertex.append(first[0])
            second = cmds.ls(fl=1, sl=1)
            downVertex.append(second[0])
            for k in range(2, len(vertexList)):
                cmds.GrowPolygonSelectionRegion()
                cmds.select(downVertex[(k - 2)], downVertex[(k - 1)], d=1)
                selNew = cmds.ls(fl=1, sl=1)
                for i in range(0, len(vertexList)):
                    for j in range(0, len(selNew)):
                        if selNew[j] == vertexList[i]:
                            cmds.select(selNew[j], r=1)

                second = cmds.ls(fl=1, sl=1)
                pos1 = cmds.xform(second[0], q=1, t=1)
                pos2 = cmds.xform(end[0], q=1, t=1)
                if pos1[0] == pos2[0] and pos1[1] == pos2[1]:
                    break
                downVertex.append(second[0])

        downVertex.append(end[0])
        cmds.select(edgeSel, r=1)
        cmds.ConvertSelectionToContainedEdges()
        if not self.headGeo_wdg.edgeLoopToggle:
            self.EdgeLoopOn_fn()
        return downVertex

    # =========================================================================
    # Save/Load Methods
    # =========================================================================

    def FacialSave(self):
        """Save facial rig settings to file."""
        from mayaLib.rigLib.face.io import facial_io

        facial_io.facial_save(self)

    def FacialLoad(self):
        """Load facial settings into UI checkboxes."""
        self.headGeo_wdg.chkLEyeLid.setChecked(True)
        self.headGeo_wdg.chkREyeLid.setChecked(True)
        self.headGeo_wdg.chkREyeOuterLid.setChecked(True)
        self.headGeo_wdg.chkLEyeOuterLid.setChecked(True)
        self.headGeo_wdg.chkNoseEdge.setChecked(True)
        self.headGeo_wdg.chkNoseUnderVertex.setChecked(True)
        self.headGeo_wdg.chkLip.setChecked(True)
        self.headGeo_wdg.chkTonque.setChecked(True)
        self.headGeo_wdg.chkBackFace.setChecked(True)
        self.headGeo_wdg.checkForeheadFace.setChecked(True)
        self.headGeo_wdg.checkSquashStretchFace.setChecked(True)
        self.headGeo_wdg.chkLPupil.setChecked(True)
        self.headGeo_wdg.chkRPupil.setChecked(True)
        self.headGeo_wdg.chkLIris.setChecked(True)
        self.headGeo_wdg.chkRIris.setChecked(True)
        self.headGeo_wdg.componentLayoutGrp.setChecked(True)
        pm.select(cl=1)

    def FacialLoadUI(self):
        """Open file dialog and load facial settings."""
        from mayaLib.rigLib.face.io import facial_io

        facial_io.facial_load_ui(self)

    def FacialResetUI(self):
        """Reset facial UI to default values."""
        self.perseus_dic = {}
        self.headGeo_wdg.chkExtra.setChecked(False)
        self.headGeo_wdg.chkLIris.setChecked(False)
        self.headGeo_wdg.chkLPupil.setChecked(False)
        self.headGeo_wdg.chkRIris.setChecked(False)
        self.headGeo_wdg.chkRPupil.setChecked(False)
        self.headGeo_wdg.chkLEyeLid.setChecked(False)
        self.headGeo_wdg.chkREyeLid.setChecked(False)
        self.headGeo_wdg.chkREyeOuterLid.setChecked(False)
        self.headGeo_wdg.chkLEyeOuterLid.setChecked(False)
        self.headGeo_wdg.chkNoseEdge.setChecked(False)
        self.headGeo_wdg.chkNoseUnderVertex.setChecked(False)
        self.headGeo_wdg.chkLip.setChecked(False)
        self.headGeo_wdg.chkTonque.setChecked(False)
        self.headGeo_wdg.chkBackFace.setChecked(False)
        self.headGeo_wdg.checkForeheadFace.setChecked(False)
        self.headGeo_wdg.checkSquashStretchFace.setChecked(False)
        self.headGeo_wdg.componentLayoutGrp.setChecked(False)
        self.settings_wdg.chkMaintainMaxInf.setChecked(True)
        self.settings_wdg.chkGame.setChecked(False)
        self.settings_wdg.chkSoftMod.setChecked(False)
        self.settings_wdg.chkTweaker.setChecked(False)
        self.settings_wdg.chkOptLip.setChecked(True)
        self.settings_wdg.chkOptEye.setChecked(True)
        self.settings_wdg.chkOptEyelidJnt.setChecked(False)
        self.settings_wdg.maxInfs.setProperty("value", 12)
        self.settings_wdg.relaxSk.setProperty("value", 2)
        self.settings_wdg.lipJnt.setProperty("value", 20)
        self.settings_wdg.eyelidJnt.setProperty("value", 20)
        self.settings_wdg.eyeCreaseJnt.setProperty("value", 8)
        self.headGeo_wdg.nameField.setText("name")
        self.headGeo_wdg.geoField.setText("")
        self.headGeo_wdg.LEyeBox.setText("")
        self.headGeo_wdg.REyeBox.setText("")
        self.headGeo_wdg.UpTeethBox.setText("")
        self.headGeo_wdg.DownTeethBox.setText("")
        self.headGeo_wdg.TongueBox.setText("")
        self.headGeo_wdg.ExtraBox.setText("")
        self.settings_wdg.progress.setValue(0)
        self.settings_wdg.progressText.setText("")

    def FacialLoadCtlShapesNoUI(self, ctrl_path, name_rig):
        """Load control shapes without UI dialog.

        Args:
            ctrl_path: Path to control shapes file.
            name_rig: Rig name prefix.
        """
        from mayaLib.rigLib.face.io import facial_io

        facial_io.facial_load_ctl_shapes_no_ui(ctrl_path, name_rig)

    def FacialLoadNoUI(self, json_path):
        """Load facial settings without UI dialog.

        Args:
            json_path: Path to JSON settings file.

        Returns:
            dict: Loaded settings data.
        """
        from mayaLib.rigLib.face.io import facial_io

        return facial_io.facial_load_no_ui(self, json_path)

    def to_json(self, dictionary, filename):
        """Save dictionary to JSON file.

        Args:
            dictionary: Data to save.
            filename: Output file path.
        """
        with open(filename, "w") as fp:
            json.dump(dictionary, fp, sort_keys=True, indent=4, ensure_ascii=False)

    def createMGPickerUI(self):
        """Create MG Picker UI file."""
        from mayaLib.rigLib.face.io import facial_io

        facial_io.create_mg_picker_ui(self)

    def FacialSaveCtlShapes(self):
        """Save facial control shapes to file."""
        from mayaLib.rigLib.face.io import facial_io

        facial_io.facial_save_ctl_shapes(self)

    def FacialSaveCtlShapesNoUI(self, name):
        """Save control shapes without UI dialog.

        Args:
            name: Rig name prefix.
        """
        from mayaLib.rigLib.face.io import facial_io

        facial_io.facial_save_ctl_shapes_no_ui(name)

    def FacialLoadCtlShapes(self):
        """Load facial control shapes from file."""
        from mayaLib.rigLib.face.io import facial_io

        facial_io.facial_load_ctl_shapes(self)

    # =========================================================================
    # Skin Methods
    # =========================================================================

    def defineExclusionUI(self):
        """Define exclusion set from selection."""
        self.newExclusion = self.wfdefineExclusionSet()
        pm.selectMode(object=1)

    def wfdefineExclusionSet(self):
        """Get exclusion vertices from selection.

        Returns:
            list: Selected vertices.
        """
        cmds.ConvertSelectionToVertices()
        selected_vertices = cmds.ls(fl=1, sl=1)
        return selected_vertices

    def wfexcludeSystem(self):
        """Apply exclusion system to skin weights."""
        from mayaLib.rigLib.face.skin import skin_ops

        skin_ops.wfexclude_system(self)

    def getSkinCluster(self, obj):
        """Get the skincluster of a given object.

        Args:
            obj: The object to get skincluster from.

        Returns:
            The skin cluster pynode object or None.
        """
        from mayaLib.rigLib.face.skin import skin_ops

        return skin_ops.get_skin_cluster(obj)

    def skinCopy(self, source_mesh=None, target_mesh=None, *args):
        """Copy skin weights from source to target meshes.

        Args:
            source_mesh: Source mesh with skin cluster.
            target_mesh: Target mesh(es) to copy weights to.
            *args: Additional arguments (unused, for Qt signal compatibility).
        """
        from mayaLib.rigLib.face.skin import skin_ops

        skin_ops.skin_copy(source_mesh, target_mesh, self)

    def source_define(self):
        """Define source vertices for skin copy."""
        from mayaLib.rigLib.face.skin import skin_ops

        skin_ops.source_define()

    def destination_define(self):
        """Define destination vertices for skin copy."""
        from mayaLib.rigLib.face.skin import skin_ops

        skin_ops.destination_define()

    def copySkinGlobal(self):
        """Copy skin weights globally."""
        from mayaLib.rigLib.face.skin import skin_ops

        skin_ops.copy_skin_global(self)

    def hammerSkinGlobal(self):
        """Hammer skin weights on selection."""
        pm.mel.weightHammerVerts()

    def copySkinMain(self):
        """Main skin copy operation."""
        from mayaLib.rigLib.face.skin import skin_ops

        skin_ops.copy_skin_main(self)

    def copyPivotF(self, source, dist):
        """Copy pivot from one object to another.

        Args:
            source: Source object.
            dist: Destination object.
        """
        pivotTranslate = cmds.xform(dist, q=True, ws=True, rotatePivot=True)
        cmds.xform(source, ws=True, pivots=pivotTranslate)

    def connectBlendShape(self):
        """Connect blendshape with parent constraint."""
        from mayaLib.rigLib.face.operations import blendshape_ops

        blendshape_ops.connect_blend_shape(self)

    def connectBlendShapeB(self):
        """Connect blendshape directly."""
        from mayaLib.rigLib.face.operations import blendshape_ops

        blendshape_ops.connect_blend_shape_b()

    def connectBlendShapeC(self):
        """Connect objects with wrap deformer."""
        from mayaLib.rigLib.face.operations import blendshape_ops

        blendshape_ops.connect_blend_shape_c()

    def connectBlendShapeD(self):
        """Connect blendshape with space switching."""
        from mayaLib.rigLib.face.operations import blendshape_ops

        blendshape_ops.connect_blend_shape_d(self)

    def detachSkinJntConnection(self):
        """Detach skin joint connections."""
        from mayaLib.rigLib.face import operations

        operations.detach_bind_joints()

    def attachSkinJntConnection(self):
        """Attach skin joint connections."""
        from mayaLib.rigLib.face import operations

        operations.attach_bind_joints()

    def SaveFacialSkinSet(self):
        """Save facial skin set."""
        from mayaLib.rigLib.face.skin import skin_ops

        skin_ops.save_facial_skin_set(self)

    def TransferFacialSkinSet(self):
        """Transfer facial skin set to another mesh."""
        from mayaLib.rigLib.face.skin import skin_ops

        skin_ops.transfer_facial_skin_set()


# Module-level exports
__all__ = [
    "CustomTabWidget",
    "PerseusUI",
]

"""Settings widget for facial rigging UI.

Provides the SettingsWidget class for configuring facial rig generation settings,
bind skin options, deformation layers, joint optimization, and data save/load operations.
"""

__author__ = "Lorenzo Argentieri"

# Qt imports with PySide6/PySide2 fallback
try:
    from PySide6 import QtWidgets
    from PySide6 import QtGui as QtG
except (ImportError, ModuleNotFoundError):
    from PySide2 import QtWidgets
    from PySide2 import QtGui as QtG

from mayaLib.rigLib.face.constants import (
    EDGE_COLOR,
    EDGE_INDEX_COLOR,
    PROGRESS_COLOR,
    SELECTION_COLOR,
)
from mayaLib.rigLib.face.utils import get_license_string


class SettingsWidget(QtWidgets.QWidget):
    """Widget for facial rig settings and configuration.

    Provides UI controls for:
    - Bind skin options (max influences, skin relax)
    - Deformation layers (game mode, soft mod, tweaker)
    - Joint optimization (lip, eyelid, eye crease joints)
    - Facial rig generation
    - Settings save/load
    - Picker creation
    - Control shape import/export

    Attributes:
        chkMaintainMaxInf: Checkbox for maintaining max influences.
        maxInfs: SpinBox for maximum influence count.
        relaxSk: SpinBox for skin relax steps.
        chkGame: Checkbox for game mode.
        chkSoftMod: Checkbox for soft mod deformation.
        chkTweaker: Checkbox for tweaker deformation.
        chkOptLip: Checkbox for lip joint optimization.
        lipJnt: SpinBox for lip joint count.
        chkOptEyelidJnt: Checkbox for eyelid joint optimization.
        eyelidJnt: SpinBox for eyelid joint count.
        chkOptEye: Checkbox for eye crease joint optimization.
        eyeCreaseJnt: SpinBox for eye crease joint count.
        generateRig: Button to create facial rig.
        progress: Progress bar for rig generation.
        progressText: Label for progress status.
        SaveSettingsBoxButton: Button to save settings.
        LoadSettingsBoxButton: Button to load settings.
        ResetSettingsBoxButton: Button to reset settings.
        picker: Button to create picker.
        SaveCtlShapesBoxButton: Button to export control shapes.
        LoadCtlShapesBoxButton: Button to import control shapes.
    """

    def __init__(self, parent=None):
        """Initialize SettingsWidget.

        Args:
            parent: Parent Qt widget.
        """
        super().__init__(parent)

        # Font setup
        self.font = QtG.QFont()
        self.font.setPointSize(10)
        self.font.setBold(True)

        # Color styles - use constants but also keep as instance attrs for compatibility
        self.edgeColor = EDGE_COLOR
        self.slColor = SELECTION_COLOR
        self.edgeIndColor = EDGE_INDEX_COLOR
        self.progressColor = PROGRESS_COLOR
        self.defineColor = "color : white;"
        self.defineColor2 = "color : black;"

        # Bind skin options
        self.chkMaintainMaxInf = QtWidgets.QCheckBox("Maintain Max Inf Jnts")
        self.chkMaintainMaxInf.setChecked(True)
        self.maxInfs = QtWidgets.QSpinBox()
        self.maxInfs.setProperty("value", 12)
        self.maxInfs.setRange(1, 14)

        self.relaxSkLabel = QtWidgets.QLabel(" Skin Relax Steps ")
        self.relaxSk = QtWidgets.QSpinBox()
        self.relaxSk.setProperty("value", 2)
        self.relaxSk.setRange(0, 5)

        # Deformation layer options
        self.chkGame = QtWidgets.QCheckBox("Game Mode")
        self.chkSoftMod = QtWidgets.QCheckBox("SoftMod")
        self.chkSoftMod.setChecked(False)
        self.chkTweaker = QtWidgets.QCheckBox("Tweaker")

        # Lip joint optimization
        self.chkOptLip = QtWidgets.QCheckBox("Optimize Lip Joints")
        self.chkOptLip.setChecked(True)
        self.lipJnt = QtWidgets.QSpinBox()
        self.lipJnt.setProperty("value", 20)
        self.lipJnt.setRange(4, 100)

        # Eyelid joint optimization
        self.chkOptEyelidJnt = QtWidgets.QCheckBox("Optimize Eyelid Joints")
        self.eyelidJnt = QtWidgets.QSpinBox()
        self.eyelidJnt.setProperty("value", 20)
        self.eyelidJnt.setRange(4, 100)

        # Eye crease joint optimization
        self.chkOptEye = QtWidgets.QCheckBox("Optimize EyeCrease Joints")
        self.chkOptEye.setChecked(True)
        self.eyeCreaseJnt = QtWidgets.QSpinBox()
        self.eyeCreaseJnt.setProperty("value", 8)
        self.eyeCreaseJnt.setRange(4, 100)

        # Create rig button and progress
        self.generateRig = QtWidgets.QPushButton("*   CREATE Facial Rig    ")
        self.generateRig.setStyleSheet(self.edgeColor)
        self.progress = QtWidgets.QProgressBar()
        self.progressText = QtWidgets.QLabel("           ")
        self.progressText.setStyleSheet(self.progressColor)
        self.progressText.setFixedSize(170, 25)

        # Save/Load buttons
        self.SaveSettingsBoxButton = QtWidgets.QPushButton(" Save Data ")
        self.SaveSettingsBoxButton.setFixedSize(150, 25)
        self.LoadSettingsBoxButton = QtWidgets.QPushButton(" Load Data ")
        self.LoadSettingsBoxButton.setFixedSize(150, 25)
        self.ResetSettingsBoxButton = QtWidgets.QPushButton(" Reset Data ")
        self.chkLoadData = QtWidgets.QCheckBox("")
        self.chkSaveData = QtWidgets.QCheckBox("")

        # Picker and shapes
        self.picker = QtWidgets.QPushButton("     CREATE PICKER     ")
        self.SaveCtlShapesBoxButton = QtWidgets.QPushButton(" Exp. Ctl. ")
        self.LoadCtlShapesBoxButton = QtWidgets.QPushButton(" Imp. Ctl. ")

        # Setup layouts
        self._setup_layouts()

    def _setup_layouts(self):
        """Configure all widget layouts."""
        # Bind Layout
        self.bindLayout = QtWidgets.QHBoxLayout()
        self.bindLayout.addWidget(self.chkMaintainMaxInf)
        self.bindLayout.addWidget(self.maxInfs)
        self.spacer = QtWidgets.QSpacerItem(50, 0)
        self.bindLayout.addSpacerItem(self.spacer)
        self.bindLayout.addWidget(self.relaxSkLabel)
        self.bindLayout.addWidget(self.relaxSk)
        self.bindLayout.addStretch()

        self.bindParentlayout = QtWidgets.QHBoxLayout(self)
        self.bindParentlayout.addLayout(self.bindLayout)
        self.bindParentlayout.addStretch()
        self.bindLayoutGrp = QtWidgets.QGroupBox("Bind Skin Option")
        self.bindLayoutGrp.setLayout(self.bindParentlayout)

        # Deformation Layout
        self.deformationLayout = QtWidgets.QHBoxLayout()
        self.deformationLayout.addWidget(self.chkGame)
        self.spacer = QtWidgets.QSpacerItem(50, 0)
        self.deformationLayout.addSpacerItem(self.spacer)
        self.deformationLayout.addWidget(self.chkSoftMod)
        self.spacer = QtWidgets.QSpacerItem(50, 0)
        self.deformationLayout.addSpacerItem(self.spacer)
        self.deformationLayout.addWidget(self.chkTweaker)
        self.deformationLayout.addStretch()

        self.deformationParentlayout = QtWidgets.QHBoxLayout(self)
        self.deformationParentlayout.addLayout(self.deformationLayout)
        self.deformationParentlayout.addStretch()
        self.deformationLayoutGrp = QtWidgets.QGroupBox("Deformation Layers ")
        self.deformationLayoutGrp.setLayout(self.deformationParentlayout)

        # Optimize Layout
        self.optimizeLayout = QtWidgets.QHBoxLayout()
        self.optimizeLayout.addWidget(self.chkOptLip)
        self.optimizeLayout.addWidget(self.lipJnt)
        self.spacer = QtWidgets.QSpacerItem(50, 0)
        self.optimizeLayout.addSpacerItem(self.spacer)
        self.optimizeLayout.addWidget(self.chkOptEyelidJnt)
        self.optimizeLayout.addWidget(self.eyelidJnt)
        self.spacer = QtWidgets.QSpacerItem(50, 0)
        self.optimizeLayout.addSpacerItem(self.spacer)
        self.optimizeLayout.addStretch()

        self.optimizeParentlayout = QtWidgets.QHBoxLayout(self)
        self.optimizeParentlayout.addLayout(self.optimizeLayout)
        self.optimizeParentlayout.addStretch()
        self.optimizeLayoutGrp = QtWidgets.QGroupBox("Deformation Layers ")
        self.optimizeLayoutGrp.setLayout(self.optimizeParentlayout)

        # Create Rig Layout
        self.createRigLayout = QtWidgets.QHBoxLayout()
        self.createRigLayoutB = QtWidgets.QHBoxLayout()
        self.createRigLayoutB.addWidget(self.generateRig)
        self.createRigLayoutB.addWidget(self.progressText)
        self.createRigLayoutB.addWidget(self.progress)

        self.createRigParentlayout = QtWidgets.QVBoxLayout(self)
        self.createRigParentlayout.addLayout(self.createRigLayoutB)
        self.createRigParentlayout.addLayout(self.createRigLayout)
        self.createRigParentlayoutGrp = QtWidgets.QGroupBox("Create Facial Rig")
        self.createRigParentlayoutGrp.setLayout(self.createRigParentlayout)

        # Save Layout
        self.saveLayout = QtWidgets.QHBoxLayout(self)
        self.saveLayout.addWidget(self.chkSaveData)
        self.saveLayout.addWidget(self.SaveSettingsBoxButton)
        self.spacer = QtWidgets.QSpacerItem(80, 0)
        self.saveLayout.addSpacerItem(self.spacer)
        self.saveLayout.addWidget(self.chkLoadData)
        self.saveLayout.addWidget(self.LoadSettingsBoxButton)
        self.saveLayout.addStretch()
        self.saveLayoutGrp = QtWidgets.QGroupBox("Save&Load Settings")
        self.saveLayoutGrp.setLayout(self.saveLayout)

        # Picker Layout
        self.pickerLayout = QtWidgets.QHBoxLayout(self)
        self.pickerLayout.addWidget(self.picker)
        self.pickerLayoutGrp = QtWidgets.QGroupBox("Picker")
        self.pickerLayoutGrp.setLayout(self.pickerLayout)

        # Shapes Layout
        self.shapesLayout = QtWidgets.QHBoxLayout(self)
        self.shapesLayout.addWidget(self.SaveCtlShapesBoxButton)
        self.shapesLayout.addWidget(self.LoadCtlShapesBoxButton)
        self.shapesLayoutGrp = QtWidgets.QGroupBox("Import/Export Shapes")
        self.shapesLayoutGrp.setLayout(self.shapesLayout)

        # License/Perseus layouts
        self.mainNameRig = get_license_string()
        self.perseusBLabelField = QtWidgets.QLabel(self.mainNameRig)
        self.perseusBLabelField.setStyleSheet(self.progressColor)
        self.perseusBLayout = QtWidgets.QHBoxLayout()
        self.perseusBLayout.addWidget(self.perseusBLabelField)
        self.perseusBLayoutGrp = QtWidgets.QGroupBox("")
        self.perseusBLayoutGrp.setLayout(self.perseusBLayout)

        self.perseusA = QtWidgets.QHBoxLayout(self)
        self.perseusA.addWidget(self.ResetSettingsBoxButton)
        self.perseusALayoutGrp = QtWidgets.QGroupBox("   Reset Settings   ")
        self.perseusALayoutGrp.setLayout(self.perseusA)

        self.perseusE = QtWidgets.QHBoxLayout(self)
        self.perseusELabelField = QtWidgets.QLabel("")
        self.perseusE.addWidget(self.perseusELabelField)
        self.perseusELayoutGrp = QtWidgets.QGroupBox("")
        self.perseusELayoutGrp.setLayout(self.perseusE)

        # Main Layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.bindLayoutGrp)
        layout.addWidget(self.deformationLayoutGrp)
        layout.addWidget(self.optimizeLayoutGrp)
        layout.addWidget(self.saveLayoutGrp)
        layout.addWidget(self.createRigParentlayoutGrp)
        layout.addWidget(self.pickerLayoutGrp)
        layout.addWidget(self.shapesLayoutGrp)
        layout.addWidget(self.perseusALayoutGrp)
        layout.addWidget(self.perseusELayoutGrp)
        layout.addWidget(self.perseusBLayoutGrp)

    def toggleGroup(self, ctrl):
        """Toggle visibility of a control group.

        Args:
            ctrl: Control widget to toggle.
        """
        state = ctrl.isChecked()
        if state:
            ctrl.setFixedHeight(ctrl.sizeHint().height())
        else:
            ctrl.setFixedHeight(30)


# Module-level exports
__all__ = ["SettingsWidget"]

"""Head geometry widget for facial rigging UI.

Provides the HeadGeoWidget class for selecting and configuring head geometry,
eyes, teeth, tongue, and other facial components for the facial rigging system.
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
    DEFAULT_COLOR,
    EDGE_COLOR,
    EDGE_INDEX_COLOR,
    PROGRESS_COLOR,
    SELECTION_COLOR,
)
from mayaLib.rigLib.face.utils import get_license_string


class HeadGeoWidget(QtWidgets.QWidget):
    """Widget for facial rig head geometry selection and configuration.

    Provides UI for selecting head, eyes, teeth, tongue, and extra geometry.
    Also includes component selection for eyelids, lips, nose, and tongue edges.

    Attributes:
        nameField: QLineEdit for character name input.
        geoField: QLineEdit for head geometry selection.
        LEyeBox: QLineEdit for left eye geometry.
        REyeBox: QLineEdit for right eye geometry.
        UpTeethBox: QLineEdit for upper teeth geometry.
        DownTeethBox: QLineEdit for lower teeth geometry.
        TongueBox: QLineEdit for tongue geometry.
        ExtraBox: QLineEdit for extra geometry.
        componentLayoutGrp: Collapsible group for component edge selections.
    """

    def __init__(self, parent=None):
        """Initialize the head geometry widget.

        Args:
            parent: Parent Qt widget.
        """
        super().__init__(parent)

        # Font setup
        self.font = QtG.QFont()
        self.font.setPointSize(10)
        self.font.setBold(False)

        # Color styles - use constants but also keep as instance attrs for compatibility
        self.edgeColor = EDGE_COLOR
        self.slColor = SELECTION_COLOR
        self.edgeIndColor = EDGE_INDEX_COLOR
        self.darkColorA = "background-color:rgb(70,70,70);color : white;"
        self.darkColorB = "background-color:rgb(50,50,50);color : white;"
        self.darkColorC = "background-color:rgb(30,30,30);color : white;"
        self.defaultColor = DEFAULT_COLOR
        self.progressColor = PROGRESS_COLOR
        self.defineColor = "color : white;"
        self.defineColor2 = "color : black;"

        # Edge loop toggle state
        self.edgeLoopToggle = False

        # Name section widgets
        self.nameLabelField = QtWidgets.QLabel("Name : ")
        self.nameField = QtWidgets.QLineEdit("name")
        self.nameField.setFixedSize(100, 25)
        self.mainNameRig = get_license_string()
        self.perseusLabelField = QtWidgets.QLabel(self.mainNameRig)
        self.perseusLabelField.setStyleSheet(self.progressColor)
        self.chkPrefix = QtWidgets.QCheckBox("Remove Prefix")
        self.skinJntSuffixLabel = QtWidgets.QLabel("Skin Joints Suffix : ")
        self.skinJntSuffix = QtWidgets.QLineEdit("skin")

        # Head Geometry Selection
        self.HeadGeoSelBut = QtWidgets.QPushButton("SL")
        self.HeadGeoSelBut.setFixedSize(30, 25)
        self.HeadGeoSelBut.setStyleSheet(self.slColor)
        self.HeadGeoSelBut.setFont(self.font)
        self.geoBox = QtWidgets.QPushButton("*     Head Geo     ")
        self.geoBox.setStyleSheet(self.edgeColor)
        self.geoField = QtWidgets.QLineEdit()
        self.geoField.setFixedSize(100, 25)

        # Left Eye Geometry
        self.LEyeGeoSelBut = QtWidgets.QPushButton("SL")
        self.LEyeGeoSelBut.setFixedSize(30, 25)
        self.LEyeGeoSelBut.setStyleSheet(self.slColor)
        self.LEyeGeoSelBut.setFont(self.font)
        self.LEyeGeo = QtWidgets.QPushButton("*    L Eye Geo     ")
        self.LEyeGeo.setStyleSheet(self.edgeColor)
        self.LEyeBox = QtWidgets.QLineEdit("")
        self.LEyeBox.setFixedSize(100, 25)

        # Right Eye Geometry
        self.REyeGeoSelBut = QtWidgets.QPushButton("SL")
        self.REyeGeoSelBut.setFixedSize(30, 25)
        self.REyeGeoSelBut.setStyleSheet(self.slColor)
        self.REyeGeoSelBut.setFont(self.font)
        self.REyeGeo = QtWidgets.QPushButton("*    R Eye Geo     ")
        self.REyeGeo.setStyleSheet(self.edgeColor)
        self.REyeBox = QtWidgets.QLineEdit("")
        self.REyeBox.setFixedSize(100, 25)

        # Top Teeth Geometry
        self.TopTeethGeoSelBut = QtWidgets.QPushButton("SL")
        self.TopTeethGeoSelBut.setFixedSize(30, 25)
        self.TopTeethGeoSelBut.setStyleSheet(self.slColor)
        self.TopTeethGeoSelBut.setFont(self.font)
        self.TopTeethGeo = QtWidgets.QPushButton("*  Up Teeth Geo  ")
        self.TopTeethGeo.setStyleSheet(self.edgeColor)
        self.UpTeethBox = QtWidgets.QLineEdit("")
        self.UpTeethBox.setFixedSize(100, 25)

        # Bottom Teeth Geometry
        self.DownTeethGeoSelBut = QtWidgets.QPushButton("SL")
        self.DownTeethGeoSelBut.setFixedSize(30, 25)
        self.DownTeethGeoSelBut.setStyleSheet(self.slColor)
        self.DownTeethGeoSelBut.setFont(self.font)
        self.DownTeethGeo = QtWidgets.QPushButton("*Down Teeth Geo")
        self.DownTeethGeo.setStyleSheet(self.edgeColor)
        self.DownTeethBox = QtWidgets.QLineEdit("")
        self.DownTeethBox.setFixedSize(100, 25)

        # Tongue Geometry
        self.TongueGeoSelBut = QtWidgets.QPushButton("SL")
        self.TongueGeoSelBut.setFixedSize(30, 25)
        self.TongueGeoSelBut.setStyleSheet(self.slColor)
        self.TongueGeoSelBut.setFont(self.font)
        self.TongueGeo = QtWidgets.QPushButton("*   Tongue Geo    ")
        self.TongueGeo.setStyleSheet(self.edgeColor)
        self.TongueBox = QtWidgets.QLineEdit("")
        self.TongueBox.setFixedSize(100, 25)

        # Extra Geometry
        self.ExtraGeoSelBut = QtWidgets.QPushButton("SL")
        self.ExtraGeoSelBut.setFixedSize(30, 25)
        self.ExtraGeoSelBut.setStyleSheet(self.slColor)
        self.ExtraGeoSelBut.setFont(self.font)
        self.ExtraGeo = QtWidgets.QPushButton("    Extra Geo    ")
        self.ExtraGeo.setStyleSheet(self.edgeColor)
        self.chkExtra = QtWidgets.QCheckBox("")
        self.chkExtra.setVisible(False)
        self.ExtraBox = QtWidgets.QLineEdit("")
        self.ExtraBox.setFixedSize(100, 25)

        # Component Mode and Edge Loop buttons
        self.ComponentBut = QtWidgets.QPushButton("*   Component Mode   ")
        self.selConstraintEdgeLoop = QtWidgets.QPushButton("Edge Loop Off")
        self.selConstraintEdgeLoop.setFixedSize(120, 25)
        self.selConstraintEdgeLoop.setStyleSheet(self.defaultColor)

        # Left Eyelid Main
        self.LEyeLidMainBoxButton = QtWidgets.QPushButton("*LEyeLidMain")
        self.LEyeLidMainBoxButton.setStyleSheet(self.edgeColor)
        self.LTopDownEyeEdgeSelBut = QtWidgets.QPushButton("SL")
        self.LTopDownEyeEdgeSelBut.setFixedSize(30, 25)
        self.LTopDownEyeEdgeSelBut.setStyleSheet(self.slColor)

        # Right Eyelid Main
        self.REyeLidMainBoxButton = QtWidgets.QPushButton("*REyeLidMain")
        self.REyeLidMainBoxButton.setStyleSheet(self.edgeColor)
        self.chkREyeLid = QtWidgets.QCheckBox("")
        self.RTopDownEyeEdgeSelBut = QtWidgets.QPushButton("SL")
        self.RTopDownEyeEdgeSelBut.setFixedSize(30, 25)
        self.RTopDownEyeEdgeSelBut.setStyleSheet(self.slColor)
        self.chkLEyeLid = QtWidgets.QCheckBox("")

        # Left Eyelid Up/Down
        self.LEyeLidTopBoxButton = QtWidgets.QPushButton("Up")
        self.LEyeLidTopBoxButton.setStyleSheet(self.edgeIndColor)
        self.LEyeLidDownBoxButton = QtWidgets.QPushButton("Down")
        self.LEyeLidDownBoxButton.setStyleSheet(self.edgeIndColor)
        self.LTopEyeEdgeSelBut = QtWidgets.QPushButton("SL")
        self.LTopEyeEdgeSelBut.setFixedSize(30, 25)
        self.LTopEyeEdgeSelBut.setStyleSheet(self.slColor)
        self.LDownEyeEdgeSelBut = QtWidgets.QPushButton("SL")
        self.LDownEyeEdgeSelBut.setFixedSize(30, 25)
        self.LDownEyeEdgeSelBut.setStyleSheet(self.slColor)

        # Right Eyelid Up/Down
        self.REyeLidTopBoxButton = QtWidgets.QPushButton("Up")
        self.REyeLidTopBoxButton.setStyleSheet(self.edgeIndColor)
        self.REyeLidDownBoxButton = QtWidgets.QPushButton("Down")
        self.REyeLidDownBoxButton.setStyleSheet(self.edgeIndColor)
        self.RTopEyeEdgeSelBut = QtWidgets.QPushButton("SL")
        self.RTopEyeEdgeSelBut.setFixedSize(30, 25)
        self.RTopEyeEdgeSelBut.setStyleSheet(self.slColor)
        self.RDownEyeEdgeSelBut = QtWidgets.QPushButton("SL")
        self.RDownEyeEdgeSelBut.setFixedSize(30, 25)
        self.RDownEyeEdgeSelBut.setStyleSheet(self.slColor)

        # Right Eyelid Outer
        self.REyeLidOuterBoxButton = QtWidgets.QPushButton("*REyeLidOuter")
        self.REyeLidOuterBoxButton.setStyleSheet(self.edgeColor)
        self.chkREyeOuterLid = QtWidgets.QCheckBox("")
        self.RTopDownEyeOuterEdgeSelBut = QtWidgets.QPushButton("SL")
        self.RTopDownEyeOuterEdgeSelBut.setFixedSize(30, 25)
        self.RTopDownEyeOuterEdgeSelBut.setStyleSheet(self.slColor)
        self.chkLEyeOuterLid = QtWidgets.QCheckBox("")
        self.REyeLidOuterTopBoxButton = QtWidgets.QPushButton("Up")
        self.REyeLidOuterTopBoxButton.setStyleSheet(self.edgeIndColor)
        self.REyeLidOuterDownBoxButton = QtWidgets.QPushButton("Down")
        self.REyeLidOuterDownBoxButton.setStyleSheet(self.edgeIndColor)
        self.RTopEyeOuterEdgeSelBut = QtWidgets.QPushButton("SL")
        self.RTopEyeOuterEdgeSelBut.setFixedSize(30, 25)
        self.RTopEyeOuterEdgeSelBut.setStyleSheet(self.slColor)
        self.RDownEyeOuterEdgeSelBut = QtWidgets.QPushButton("SL")
        self.RDownEyeOuterEdgeSelBut.setFixedSize(30, 25)
        self.RDownEyeOuterEdgeSelBut.setStyleSheet(self.slColor)

        # Left Eyelid Outer
        self.LEyeLidOuterBoxButton = QtWidgets.QPushButton("*LEyeLidOuter")
        self.LEyeLidOuterBoxButton.setStyleSheet(self.edgeColor)
        self.LTopDownEyeOuterEdgeSelBut = QtWidgets.QPushButton("SL")
        self.LTopDownEyeOuterEdgeSelBut.setFixedSize(30, 25)
        self.LTopDownEyeOuterEdgeSelBut.setStyleSheet(self.slColor)
        self.LEyeLidOuterTopBoxButton = QtWidgets.QPushButton("Up")
        self.LEyeLidOuterTopBoxButton.setStyleSheet(self.edgeIndColor)
        self.LEyeLidOuterDownBoxButton = QtWidgets.QPushButton("Down")
        self.LEyeLidOuterDownBoxButton.setStyleSheet(self.edgeIndColor)
        self.LTopEyeOuterEdgeSelBut = QtWidgets.QPushButton("SL")
        self.LTopEyeOuterEdgeSelBut.setFixedSize(30, 25)
        self.LTopEyeOuterEdgeSelBut.setStyleSheet(self.slColor)
        self.LDownEyeOuterEdgeSelBut = QtWidgets.QPushButton("SL")
        self.LDownEyeOuterEdgeSelBut.setFixedSize(30, 25)
        self.LDownEyeOuterEdgeSelBut.setStyleSheet(self.slColor)

        # Nose Edges
        self.NoseBoxButton = QtWidgets.QPushButton("* Nose Edges ")
        self.NoseBoxButton.setStyleSheet(self.edgeColor)
        self.NoseEdgeSelBut = QtWidgets.QPushButton("SL")
        self.NoseEdgeSelBut.setFixedSize(30, 25)
        self.NoseEdgeSelBut.setStyleSheet(self.slColor)
        self.NoseUnderVertexBoxButton = QtWidgets.QPushButton("*NoseUnderVtx")
        self.NoseUnderVertexBoxButton.setStyleSheet(self.edgeColor)
        self.chkNoseEdge = QtWidgets.QCheckBox("")
        self.NoseUnderVertexSelBut = QtWidgets.QPushButton("SL")
        self.NoseUnderVertexSelBut.setFixedSize(30, 25)
        self.NoseUnderVertexSelBut.setStyleSheet(self.slColor)
        self.chkNoseUnderVertex = QtWidgets.QCheckBox("")

        # Lip Edges
        self.LipBoxButton = QtWidgets.QPushButton("*   Lip Edge   ")
        self.LipBoxButton.setStyleSheet(self.edgeColor)
        self.chkLip = QtWidgets.QCheckBox("")
        self.TopDownLipEdgeSelBut = QtWidgets.QPushButton("SL")
        self.TopDownLipEdgeSelBut.setFixedSize(30, 25)
        self.TopDownLipEdgeSelBut.setStyleSheet(self.slColor)
        self.LipUpBoxButton = QtWidgets.QPushButton("Up")
        self.LipUpBoxButton.setStyleSheet(self.edgeIndColor)
        self.LipDownBoxButton = QtWidgets.QPushButton("Down")
        self.LipDownBoxButton.setStyleSheet(self.edgeIndColor)
        self.TopLipEdgeSelBut = QtWidgets.QPushButton("SL")
        self.TopLipEdgeSelBut.setFixedSize(30, 25)
        self.TopLipEdgeSelBut.setStyleSheet(self.slColor)
        self.DownLipEdgeSelBut = QtWidgets.QPushButton("SL")
        self.DownLipEdgeSelBut.setFixedSize(30, 25)
        self.DownLipEdgeSelBut.setStyleSheet(self.slColor)

        # Tongue Edges
        self.TongueBoxButton = QtWidgets.QPushButton("*Tongue Edge ")
        self.TongueBoxButton.setStyleSheet(self.edgeColor)
        self.chkTonque = QtWidgets.QCheckBox("")
        self.TongueEdgeSelBut = QtWidgets.QPushButton("SL")
        self.TongueEdgeSelBut.setFixedSize(30, 25)
        self.TongueEdgeSelBut.setStyleSheet(self.slColor)
        self.TongueUpEdgeBoxButton = QtWidgets.QPushButton("Up")
        self.TongueUpEdgeBoxButton.setStyleSheet(self.edgeIndColor)
        self.TongueDownEdgeBoxButton = QtWidgets.QPushButton("Down")
        self.TongueDownEdgeBoxButton.setStyleSheet(self.edgeIndColor)
        self.TopTongueEdgeSelBut = QtWidgets.QPushButton("SL")
        self.TopTongueEdgeSelBut.setFixedSize(30, 25)
        self.TopTongueEdgeSelBut.setStyleSheet(self.slColor)
        self.DownTongueEdgeSelBut = QtWidgets.QPushButton("SL")
        self.DownTongueEdgeSelBut.setFixedSize(30, 25)
        self.DownTongueEdgeSelBut.setStyleSheet(self.slColor)
        self.DownTongueEdgeSelBut.setFont(self.font)

        # Back Head/Neck Face Selection
        self.BackHeadNeckBoxButton = QtWidgets.QPushButton("*BackHead_Neck")
        self.BackHeadNeckBoxButton.setStyleSheet(self.edgeColor)
        self.chkBackFace = QtWidgets.QCheckBox("")
        self.BackHeadNeckFaceSelButton = QtWidgets.QPushButton("SL")
        self.BackHeadNeckFaceSelButton.setFixedSize(30, 25)
        self.BackHeadNeckFaceSelButton.setStyleSheet(self.slColor)

        # Forehead/Eyelid Mask
        self.ForeheadBoxButton = QtWidgets.QPushButton("* EyeLid_Mask  ")
        self.ForeheadBoxButton.setStyleSheet(self.edgeColor)
        self.checkForeheadFace = QtWidgets.QCheckBox("")
        self.ForeheadFaceSelButton = QtWidgets.QPushButton("SL")
        self.ForeheadFaceSelButton.setFixedSize(30, 25)
        self.ForeheadFaceSelButton.setStyleSheet(self.slColor)

        # Squash/Stretch Mask
        self.SquashStretchBoxButton = QtWidgets.QPushButton("*Squash_Stretch")
        self.SquashStretchBoxButton.setStyleSheet(self.edgeColor)
        self.checkSquashStretchFace = QtWidgets.QCheckBox("")
        self.SquashStretchFaceSelButton = QtWidgets.QPushButton("SL")
        self.SquashStretchFaceSelButton.setFixedSize(30, 25)
        self.SquashStretchFaceSelButton.setStyleSheet(self.slColor)

        # Pupil and Iris widgets
        self.LPupilBoxButton = QtWidgets.QPushButton("*LPupil")
        self.LPupilBoxButton.setStyleSheet(self.edgeColor)
        self.chkLPupil = QtWidgets.QCheckBox("")
        self.LPupilSelButton = QtWidgets.QPushButton("SL")
        self.LPupilSelButton.setFixedSize(30, 25)
        self.LPupilSelButton.setStyleSheet(self.slColor)
        self.RPupilBoxButton = QtWidgets.QPushButton("*RPupil")
        self.RPupilBoxButton.setStyleSheet(self.edgeColor)
        self.chkRPupil = QtWidgets.QCheckBox("")
        self.RPupilSelButton = QtWidgets.QPushButton("SL")
        self.RPupilSelButton.setFixedSize(30, 25)
        self.RPupilSelButton.setStyleSheet(self.slColor)
        self.LIrisBoxButton = QtWidgets.QPushButton("*LIris")
        self.LIrisBoxButton.setStyleSheet(self.edgeColor)
        self.chkLIris = QtWidgets.QCheckBox("")
        self.LIrisSelButton = QtWidgets.QPushButton("SL")
        self.LIrisSelButton.setFixedSize(30, 25)
        self.LIrisSelButton.setStyleSheet(self.slColor)
        self.RIrisBoxButton = QtWidgets.QPushButton("*RIris")
        self.RIrisBoxButton.setStyleSheet(self.edgeColor)
        self.chkRIris = QtWidgets.QCheckBox("")
        self.RIrisSelButton = QtWidgets.QPushButton("SL")
        self.RIrisSelButton.setFixedSize(30, 25)
        self.RIrisSelButton.setStyleSheet(self.slColor)

        # Curve guide buttons
        self.AdjustmentBoxButton = QtWidgets.QPushButton("Create Jaw Curve *")
        self.AdjustmentBBoxButton = QtWidgets.QPushButton(
            "Create Facial Curve Guide *"
        )
        self.ProjectBoxButton = QtWidgets.QPushButton(
            "Project Curves On face model *"
        )

        # Setup layouts
        self._setup_layouts()

    def _setup_layouts(self):
        """Configure all widget layouts."""
        # Model Layout - Head geometry selection
        self.modelLayout = QtWidgets.QGridLayout(self)
        self.modelLayout.setHorizontalSpacing(3)
        self.modelLayout.setContentsMargins(3, 3, 3, 3)
        self.modelLayout.addWidget(self.geoBox, 1, 1)
        self.modelLayout.addWidget(self.HeadGeoSelBut, 1, 0)
        self.modelLayout.addWidget(self.geoField, 2, 1)
        self.modelLayout.addWidget(self.REyeGeo, 1, 3)
        self.modelLayout.addWidget(self.REyeGeoSelBut, 1, 2)
        self.modelLayout.addWidget(self.REyeBox, 2, 3)
        self.modelLayout.addWidget(self.LEyeGeo, 1, 5)
        self.modelLayout.addWidget(self.LEyeGeoSelBut, 1, 4)
        self.modelLayout.addWidget(self.LEyeBox, 2, 5)
        self.modelLayout.addWidget(self.TongueGeo, 3, 5)
        self.modelLayout.addWidget(self.TongueGeoSelBut, 3, 4)
        self.modelLayout.addWidget(self.TongueBox, 4, 5)
        self.modelLayout.addWidget(self.TopTeethGeo, 3, 1)
        self.modelLayout.addWidget(self.TopTeethGeoSelBut, 3, 0)
        self.modelLayout.addWidget(self.UpTeethBox, 4, 1)
        self.modelLayout.addWidget(self.DownTeethGeo, 3, 3)
        self.modelLayout.addWidget(self.DownTeethGeoSelBut, 3, 2)
        self.modelLayout.addWidget(self.DownTeethBox, 4, 3)
        self.modelLayout.addWidget(self.ExtraGeo, 1, 7)
        self.modelLayout.addWidget(self.ExtraGeoSelBut, 1, 6)
        self.modelLayout.addWidget(self.ExtraBox, 2, 7)
        self.modelLayout.addWidget(self.chkExtra, 4, 6)
        self.modelLayoutGrp = QtWidgets.QGroupBox("Set Head Models")
        self.modelLayoutGrp.setLayout(self.modelLayout)

        # Component Layout - Edge selections
        self.componentLayout = QtWidgets.QGridLayout()
        self.componentLayout.setRowStretch(0, 0)
        self.componentLayout.setRowStretch(1, 0)
        self.componentLayout.setRowStretch(2, 0)

        # Right Eyelid Main
        self.componentLayout.addWidget(self.REyeLidMainBoxButton, 0, 1)
        self.componentLayout.addWidget(self.RTopDownEyeEdgeSelBut, 0, 0)
        self.componentLayout.addWidget(self.chkREyeLid, 0, 2)
        self.componentLayout.addWidget(self.REyeLidTopBoxButton, 1, 1)
        self.componentLayout.addWidget(self.RTopEyeEdgeSelBut, 1, 0)
        self.componentLayout.addWidget(self.REyeLidDownBoxButton, 2, 1)
        self.componentLayout.addWidget(self.RDownEyeEdgeSelBut, 2, 0)

        # Left Eyelid Main
        self.componentLayout.addWidget(self.LEyeLidMainBoxButton, 0, 4)
        self.componentLayout.addWidget(self.LTopDownEyeEdgeSelBut, 0, 3)
        self.componentLayout.addWidget(self.chkLEyeLid, 0, 5)
        self.componentLayout.addWidget(self.LEyeLidTopBoxButton, 1, 4)
        self.componentLayout.addWidget(self.LTopEyeEdgeSelBut, 1, 3)
        self.componentLayout.addWidget(self.LEyeLidDownBoxButton, 2, 4)
        self.componentLayout.addWidget(self.LDownEyeEdgeSelBut, 2, 3)

        # Right Eyelid Outer
        self.componentLayout.addWidget(self.REyeLidOuterBoxButton, 3, 1)
        self.componentLayout.addWidget(self.RTopDownEyeOuterEdgeSelBut, 3, 0)
        self.componentLayout.addWidget(self.chkREyeOuterLid, 3, 2)
        self.componentLayout.addWidget(self.REyeLidOuterTopBoxButton, 4, 1)
        self.componentLayout.addWidget(self.RTopEyeOuterEdgeSelBut, 4, 0)
        self.componentLayout.addWidget(self.REyeLidOuterDownBoxButton, 5, 1)
        self.componentLayout.addWidget(self.RDownEyeOuterEdgeSelBut, 5, 0)

        # Left Eyelid Outer
        self.componentLayout.addWidget(self.LEyeLidOuterBoxButton, 3, 4)
        self.componentLayout.addWidget(self.LTopDownEyeOuterEdgeSelBut, 3, 3)
        self.componentLayout.addWidget(self.chkLEyeOuterLid, 3, 5)
        self.componentLayout.addWidget(self.LEyeLidOuterTopBoxButton, 4, 4)
        self.componentLayout.addWidget(self.LTopEyeOuterEdgeSelBut, 4, 3)
        self.componentLayout.addWidget(self.LEyeLidOuterDownBoxButton, 5, 4)
        self.componentLayout.addWidget(self.LDownEyeOuterEdgeSelBut, 5, 3)

        # Lip edges
        self.componentLayout.addWidget(self.LipBoxButton, 0, 7)
        self.componentLayout.addWidget(self.TopDownLipEdgeSelBut, 0, 6)
        self.componentLayout.addWidget(self.chkLip, 0, 8)
        self.componentLayout.addWidget(self.LipUpBoxButton, 1, 7)
        self.componentLayout.addWidget(self.TopLipEdgeSelBut, 1, 6)
        self.componentLayout.addWidget(self.LipDownBoxButton, 2, 7)
        self.componentLayout.addWidget(self.DownLipEdgeSelBut, 2, 6)

        # Tongue edges
        self.componentLayout.addWidget(self.TongueBoxButton, 3, 7)
        self.componentLayout.addWidget(self.TongueEdgeSelBut, 3, 6)
        self.componentLayout.addWidget(self.chkTonque, 3, 8)
        self.componentLayout.addWidget(self.TongueUpEdgeBoxButton, 4, 7)
        self.componentLayout.addWidget(self.TopTongueEdgeSelBut, 4, 6)
        self.componentLayout.addWidget(self.TongueDownEdgeBoxButton, 5, 7)
        self.componentLayout.addWidget(self.DownTongueEdgeSelBut, 5, 6)

        # Nose edges
        self.componentLayout.addWidget(self.NoseBoxButton, 6, 7)
        self.componentLayout.addWidget(self.NoseEdgeSelBut, 6, 6)
        self.componentLayout.addWidget(self.chkNoseEdge, 6, 8)
        self.componentLayout.addWidget(self.NoseUnderVertexBoxButton, 7, 7)
        self.componentLayout.addWidget(self.NoseUnderVertexSelBut, 7, 6)
        self.componentLayout.addWidget(self.chkNoseUnderVertex, 7, 8)

        # Face mask selections
        self.componentLayout.addWidget(self.ForeheadBoxButton, 8, 1)
        self.componentLayout.addWidget(self.ForeheadFaceSelButton, 8, 0)
        self.componentLayout.addWidget(self.checkForeheadFace, 8, 2)
        self.componentLayout.addWidget(self.BackHeadNeckBoxButton, 8, 4)
        self.componentLayout.addWidget(self.BackHeadNeckFaceSelButton, 8, 3)
        self.componentLayout.addWidget(self.chkBackFace, 8, 5)
        self.componentLayout.addWidget(self.SquashStretchBoxButton, 8, 7)
        self.componentLayout.addWidget(self.SquashStretchFaceSelButton, 8, 6)
        self.componentLayout.addWidget(self.checkSquashStretchFace, 8, 8)

        # Pupil and Iris
        self.componentLayout.addWidget(self.LPupilBoxButton, 6, 4)
        self.componentLayout.addWidget(self.chkLPupil, 6, 5)
        self.componentLayout.addWidget(self.LPupilSelButton, 6, 3)
        self.componentLayout.addWidget(self.RPupilBoxButton, 6, 1)
        self.componentLayout.addWidget(self.chkRPupil, 6, 2)
        self.componentLayout.addWidget(self.RPupilSelButton, 6, 0)
        self.componentLayout.addWidget(self.LIrisBoxButton, 7, 4)
        self.componentLayout.addWidget(self.chkLIris, 7, 5)
        self.componentLayout.addWidget(self.LIrisSelButton, 7, 3)
        self.componentLayout.addWidget(self.RIrisBoxButton, 7, 1)
        self.componentLayout.addWidget(self.chkRIris, 7, 2)
        self.componentLayout.addWidget(self.RIrisSelButton, 7, 0)

        self.componentLayoutGrp = QtWidgets.QGroupBox("Set Components")
        self.componentLayoutGrp.setLayout(self.componentLayout)
        self.componentLayoutGrp.setCheckable(True)
        self.componentLayoutGrp.setChecked(False)

        # Settings Layout - Curve guides
        self.settingsLayout = QtWidgets.QHBoxLayout()
        self.settingsLayout.addWidget(self.AdjustmentBoxButton)
        self.settingsLayout.addWidget(self.AdjustmentBBoxButton)
        self.settingsLayout.addWidget(self.ProjectBoxButton)
        self.settingsLayoutGrp = QtWidgets.QGroupBox("Create Curve guides")
        self.settingsLayoutGrp.setLayout(self.settingsLayout)

        # Name Layout
        self.nameLayout = QtWidgets.QHBoxLayout()
        self.nameLayout.addWidget(self.nameLabelField)
        self.nameLayout.addWidget(self.nameField)
        self.nameLayout.addWidget(self.skinJntSuffixLabel)
        self.nameLayout.addWidget(self.skinJntSuffix)
        self.nameLayout.addWidget(self.chkPrefix)
        self.nameLayout.addStretch()
        self.nameLayoutGrp = QtWidgets.QGroupBox("Set Name")
        self.nameLayoutGrp.setLayout(self.nameLayout)

        # Perseus label layouts (license display)
        self.perseusLabelFieldE = QtWidgets.QLabel("")
        self.perseusLayoutE = QtWidgets.QHBoxLayout()
        self.perseusLayoutE.addWidget(self.perseusLabelFieldE)
        self.perseusLayoutGrpE = QtWidgets.QGroupBox("")
        self.perseusLayoutGrpE.setLayout(self.perseusLayoutE)

        self.perseusLabelFieldF = QtWidgets.QLabel("")
        self.perseusLayoutF = QtWidgets.QHBoxLayout()
        self.perseusLayoutF.addWidget(self.perseusLabelFieldF)
        self.perseusLayoutGrpF = QtWidgets.QGroupBox("")
        self.perseusLayoutGrpF.setLayout(self.perseusLayoutF)

        self.perseusLayout = QtWidgets.QHBoxLayout()
        self.perseusLayout.addWidget(self.perseusLabelField)
        self.perseusLayoutGrp = QtWidgets.QGroupBox("")
        self.perseusLayoutGrp.setLayout(self.perseusLayout)

        # Mode Layout - Component mode toggle
        self.modeLayout = QtWidgets.QHBoxLayout()
        self.modeLayout.addWidget(self.ComponentBut)
        self.spacer = QtWidgets.QSpacerItem(200, 0)
        self.modeLayout.addSpacerItem(self.spacer)
        self.modeLayout.addWidget(self.selConstraintEdgeLoop)
        self.modeLayoutGrp = QtWidgets.QGroupBox("")
        self.modeLayoutGrp.setLayout(self.modeLayout)

        # Main Layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.nameLayoutGrp)
        layout.addWidget(self.modelLayoutGrp)
        layout.addWidget(self.modeLayoutGrp)
        layout.addWidget(self.componentLayoutGrp)
        layout.addWidget(self.settingsLayoutGrp)
        layout.addWidget(self.perseusLayoutGrp)


# Module-level exports
__all__ = ["HeadGeoWidget"]

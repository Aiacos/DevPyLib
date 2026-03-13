"""Skin widget for facial rigging UI.

Provides the SkinWidget class for managing skin cluster operations,
including skin export/import, skin copying, component-based skin transfer,
and facial-to-body connection creation.
"""

__author__ = "Lorenzo Argentieri"

# Qt imports with PySide6/PySide2 fallback
try:
    from PySide6 import QtWidgets
except (ImportError, ModuleNotFoundError):
    from PySide2 import QtWidgets

from mayaLib.rigLib.face.constants import PROGRESS_COLOR
from mayaLib.rigLib.face.utils import get_license_string


class SkinWidget(QtWidgets.QWidget):
    """Widget for skin cluster setup and management.

    Provides UI controls for:
    - Skin export/import operations
    - Skin copying between meshes
    - Component-based skin weight transfer
    - Skin influence exclusion system
    - Facial-to-body rig connection creation
    - Detach/attach skin joint connections

    Attributes:
        prExportSkin: Button to export skin weights.
        prImpSkinAll: Button to import skin weights.
        skinCopy: Button to copy skin weights.
        source_define: Button to define source component for copy.
        destination_define: Button to define target component for copy.
        copySkinGlobal: Button to copy skin from source to target.
        hammerSkinGlobal: Button to hammer skin weights.
        progress: Progress bar for skin operations.
        DEFINE_large: Button to define skin exclusion set.
        EXCLUDE_large: Button to exclude system(s) from skin.
        SaveFacialSkinSet: Button to save facial skin set.
        TransferFacialSkinSet: Button to transfer skin for game mode.
        connectBlendShape: Button to create face-body joint connection.
        connectBlendShapeB: Button to create blendshape deformer.
        connectBlendShapeC: Button to create wrap deformer.
        connectBlendShapeD: Button to add eye aim space switch.
        detachSkinJntConnection: Button to detach skin joint connection.
        attachSkinJntConnection: Button to attach skin joint connection.
    """

    def __init__(self, parent=None):
        """Initialize SkinWidget.

        Args:
            parent: Parent Qt widget.
        """
        super().__init__(parent)

        # Color styles
        self.progressColor = PROGRESS_COLOR

        # Skin export/import/copy buttons
        self.prExportSkin = QtWidgets.QPushButton("Export Skin")
        self.prImpSkinAll = QtWidgets.QPushButton("Import Skin")
        self.skinCopy = QtWidgets.QPushButton("Copy Skin")
        self.perseusLabelField = QtWidgets.QLabel("")

        # Copy skin and influences layout
        self.perseusLayout = QtWidgets.QVBoxLayout()
        self.perseusLayout.addWidget(self.prExportSkin)
        self.perseusLayout.addWidget(self.prImpSkinAll)
        self.perseusLayout.addWidget(self.skinCopy)
        self.perseusLayoutGrp = QtWidgets.QGroupBox("Copy Skin and Influences")
        self.perseusLayoutGrp.setLayout(self.perseusLayout)

        # Component-based skin copy
        self.progress = QtWidgets.QProgressBar()
        self.source_define = QtWidgets.QPushButton("Source Component")
        self.destination_define = QtWidgets.QPushButton("Target Component")
        self.copySkinGlobal = QtWidgets.QPushButton("Copy Src. to Trg.")
        self.hammerSkinGlobal = QtWidgets.QPushButton("Hammer Skin Weight")
        self.perseusCLabelField = QtWidgets.QLabel("")

        # Copy skin components layout
        self.perseusCLayout = QtWidgets.QVBoxLayout()
        self.perseusCLayout.addWidget(self.source_define)
        self.perseusCLayout.addWidget(self.destination_define)
        self.perseusCLayout.addWidget(self.copySkinGlobal)
        self.perseusCLayout.addWidget(self.progress)
        self.perseusCLayout.addWidget(self.hammerSkinGlobal)
        self.perseusCLayoutGrp = QtWidgets.QGroupBox("Copy Skin Components")
        self.perseusCLayoutGrp.setLayout(self.perseusCLayout)

        # Skin exclusion system
        self.DEFINE_large = QtWidgets.QPushButton("Define Exclusion Set")
        self.EXCLUDE_large = QtWidgets.QPushButton("Exclude System(s)")
        self.excludeLayout = QtWidgets.QVBoxLayout(self)
        self.excludeLayout.addWidget(self.DEFINE_large)
        self.excludeLayout.addWidget(self.EXCLUDE_large)
        self.excludeLayoutGrp = QtWidgets.QGroupBox("Skin Exclusion System")
        self.excludeLayoutGrp.setLayout(self.excludeLayout)

        # Face to body connection buttons
        self.SaveFacialSkinSet = QtWidgets.QPushButton("Set A")
        self.TransferFacialSkinSet = QtWidgets.QPushButton(
            "A To B (Add influences and Cpy.Skin for Game Mode)"
        )
        self.connectBlendShape = QtWidgets.QPushButton(
            "Create Connection(Select body rig head jnt and facial grp)"
        )
        self.connectBlendShapeB = QtWidgets.QPushButton(
            "Create BlendShape (Select facial and body mesh) "
        )
        self.connectBlendShapeC = QtWidgets.QPushButton(
            "Create Wrap Deformer (Select facial and body mesh) "
        )
        self.connectBlendShapeD = QtWidgets.QPushButton(
            "Add Space Switch for Eye Aim Ctrl.(Select some Controllers from Body Rig)"
        )
        self.detachSkinJntConnection = QtWidgets.QPushButton("Detach Skin Joints Connection")
        self.attachSkinJntConnection = QtWidgets.QPushButton("Attach Skin Joints Connection")

        # Face to body connection layout
        self.perseusDLayout = QtWidgets.QVBoxLayout()
        self.perseusDLayout.addWidget(self.SaveFacialSkinSet)
        self.perseusDLayout.addWidget(self.TransferFacialSkinSet)
        self.perseusDLayout.addWidget(self.connectBlendShape)
        self.perseusDLayout.addWidget(self.connectBlendShapeB)
        self.perseusDLayout.addWidget(self.connectBlendShapeC)
        self.perseusDLayout.addWidget(self.connectBlendShapeD)
        self.perseusDLayout.addWidget(self.detachSkinJntConnection)
        self.perseusDLayout.addWidget(self.attachSkinJntConnection)
        self.perseusDLayoutGrp = QtWidgets.QGroupBox("Create Connection From Face --> Body")
        self.perseusDLayoutGrp.setLayout(self.perseusDLayout)

        # License/info label
        self.mainNameRig = get_license_string()
        self.perseusBLabelField = QtWidgets.QLabel(self.mainNameRig)
        self.perseusBLabelField.setStyleSheet(self.progressColor)
        self.perseusBLayout = QtWidgets.QHBoxLayout()
        self.perseusBLayout.addWidget(self.perseusBLabelField)
        self.perseusBLayoutGrp = QtWidgets.QGroupBox("")
        self.perseusBLayoutGrp.setLayout(self.perseusBLayout)

        # Empty spacer layouts
        self.perseusA = QtWidgets.QHBoxLayout(self)
        self.perseusALabelField = QtWidgets.QLabel("")
        self.perseusA.addWidget(self.perseusALabelField)
        self.perseusALayoutGrp = QtWidgets.QGroupBox("")
        self.perseusALayoutGrp.setLayout(self.perseusA)

        self.perseusE = QtWidgets.QHBoxLayout(self)
        self.perseusELabelField = QtWidgets.QLabel("")
        self.perseusE.addWidget(self.perseusELabelField)
        self.perseusELayoutGrp = QtWidgets.QGroupBox("")
        self.perseusELayoutGrp.setLayout(self.perseusE)

        # Main layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.excludeLayoutGrp)
        layout.addWidget(self.perseusLayoutGrp)
        layout.addWidget(self.perseusCLayoutGrp)
        layout.addWidget(self.perseusDLayoutGrp)
        layout.addWidget(self.perseusALayoutGrp)
        layout.addWidget(self.perseusBLayoutGrp)


# Module-level exports
__all__ = ["SkinWidget"]

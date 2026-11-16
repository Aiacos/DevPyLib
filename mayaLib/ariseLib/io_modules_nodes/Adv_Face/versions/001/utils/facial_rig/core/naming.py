"""
Naming convention module for consistent object naming.
"""

from enum import Enum
from typing import Optional


class Side(Enum):
    """Side enumeration for bilateral objects."""

    CENTER = "_M"
    RIGHT = "_R"
    LEFT = "_L"


class ControlType(Enum):
    """Control type enumeration."""

    PRIMARY = "primary"  # Type 2 - Green, larger
    SECONDARY = "secondary"  # Type 1 - Red, smaller
    DETAIL = "detail"  # Type 3 - Blue, smallest
    REGION = "region"  # Type 4 - Region controls
    CUSTOM = "custom"  # Type 5 - Custom controls


class NamingConvention:
    """
    Naming convention manager for facial rig elements.

    Provides consistent naming across all rig components.
    """

    # Prefixes
    PREFIX_SDK = "SDK"
    PREFIX_OFFSET = "Offset"
    PREFIX_JOINT = "Joint"
    PREFIX_CTRL = "ctrl"
    PREFIX_CTRL_BOX = "ctrlBox"
    PREFIX_FACE_FIT = "FaceFit"

    # Group names
    GRP_FACE = "FaceGroup"
    GRP_MOTION_SYSTEM = "FaceMotionSystem"
    GRP_DEFORMATION_SYSTEM = "FaceDeformationSystem"
    GRP_ON_FACE_CONTROLS = "OnFacecontrols"
    GRP_FIT_SKELETON = "FaceFitSkeleton"

    # Component prefixes
    COMP_EYELID = "EyeLid"
    COMP_LIP = "Lip"
    COMP_EYEBROW = "EyeBrow"
    COMP_EYE = "Eye"
    COMP_JAW = "Jaw"
    COMP_CHEEK = "Cheek"
    COMP_NOSE = "Nose"
    COMP_TONGUE = "Tongue"
    COMP_FOREHEAD = "ForeHead"

    @classmethod
    def controller(cls, name: str, side: Side) -> str:
        """
        Generate controller name.

        Args:
            name: Base name of the controller
            side: Side enum (CENTER, RIGHT, LEFT)

        Returns:
            Formatted controller name (e.g., "EyeBrowInner_R")
        """
        return f"{name}{side.value}"

    @classmethod
    def offset(cls, name: str, side: Side) -> str:
        """
        Generate offset group name.

        Args:
            name: Base name
            side: Side enum

        Returns:
            Formatted offset name (e.g., "EyeBrowInnerOffset_R")
        """
        return f"{name}{cls.PREFIX_OFFSET}{side.value}"

    @classmethod
    def sdk(cls, name: str, side: Side) -> str:
        """
        Generate SDK group name.

        Args:
            name: Base name
            side: Side enum

        Returns:
            Formatted SDK name (e.g., "SDKEyeBrowInner_R")
        """
        return f"{cls.PREFIX_SDK}{name}{side.value}"

    @classmethod
    def joint(cls, name: str, side: Side, index: Optional[int] = None) -> str:
        """
        Generate joint name.

        Args:
            name: Base name
            side: Side enum
            index: Optional index number

        Returns:
            Formatted joint name (e.g., "EyeLidJoint0_R")
        """
        if index is not None:
            return f"{name}{cls.PREFIX_JOINT}{index}{side.value}"
        return f"{name}{cls.PREFIX_JOINT}{side.value}"

    @classmethod
    def ctrl_box(cls, name: str, side: Side) -> str:
        """
        Generate control box name.

        Args:
            name: Base name (e.g., "Eye", "Brow")
            side: Side enum

        Returns:
            Formatted control box name (e.g., "ctrlBoxEye_R")
        """
        return f"{cls.PREFIX_CTRL_BOX}{name}{side.value}"

    @classmethod
    def ctrl(cls, name: str, side: Side) -> str:
        """
        Generate ctrl name for sliders.

        Args:
            name: Base name
            side: Side enum

        Returns:
            Formatted ctrl name (e.g., "ctrlBrow_R")
        """
        return f"{cls.PREFIX_CTRL}{name}{side.value}"

    @classmethod
    def face_fit(cls, name: str, left_suffix: str = "") -> str:
        """
        Generate FaceFit object name.

        Args:
            name: Base name (e.g., "EyeLidOuter")
            left_suffix: "Left" for left side objects, "" for right

        Returns:
            Formatted FaceFit name (e.g., "FaceFitEyeLidOuter", "FaceFitEyeLidOuterLeft")
        """
        return f"{cls.PREFIX_FACE_FIT}{name}{left_suffix}"

    @classmethod
    def curve(cls, prefix: str, curve_type: str, left_suffix: str = "") -> str:
        """
        Generate curve name.

        Args:
            prefix: Curve prefix (e.g., "upper", "lower")
            curve_type: Curve type (e.g., "EyeLidMainCurve", "LipOuterCurve")
            left_suffix: "Left" for left side, "" for right

        Returns:
            Formatted curve name (e.g., "upperEyeLidMainCurve")
        """
        return f"{prefix}{curve_type}{left_suffix}"

    @classmethod
    def get_opposite_side(cls, side: Side) -> Side:
        """
        Get the opposite side.

        Args:
            side: Current side

        Returns:
            Opposite side enum
        """
        if side == Side.RIGHT:
            return Side.LEFT
        elif side == Side.LEFT:
            return Side.RIGHT
        return Side.CENTER

    @classmethod
    def mirror_name(cls, name: str) -> str:
        """
        Get mirrored name (swap _R/_L suffixes).

        Args:
            name: Object name with side suffix

        Returns:
            Name with opposite side suffix
        """
        if name.endswith("_R"):
            return name[:-2] + "_L"
        elif name.endswith("_L"):
            return name[:-2] + "_R"
        return name

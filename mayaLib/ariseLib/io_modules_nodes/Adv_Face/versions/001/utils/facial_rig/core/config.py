"""
Configuration module for facial rig settings.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class ColorScheme:
    """Color scheme for controllers."""

    primary: int = 14  # Green - main controls
    secondary: int = 13  # Red - secondary controls
    tertiary: int = 6  # Blue - detail controls
    region: int = 14  # Region controls
    custom: int = 28  # Custom controls


@dataclass
class FacialRigConfig:
    """
    Configuration container for facial rig parameters.

    Attributes:
        geometry: The main face mesh name
        all_head_geo: List of all head geometry names
        head_joint: The head joint name
        skin_cluster: The skin cluster name

        right_eye: Right eye geometry
        left_eye: Left eye geometry
        upper_teeth: Upper teeth geometry
        lower_teeth: Lower teeth geometry
        tongue: Tongue geometry

        non_symmetrical: Whether the face is non-symmetrical
        game_engine: Optimize for game engine export
        simpler_eyelid: Use simplified eyelid setup
        eye_socket: Include eye socket controls
        long_snout: Character has elongated snout

        lip_controls: Number of lip controls (default 12)
        face_scale: Overall face scale factor

        colors: Color scheme for controllers
    """

    # Required geometry
    geometry: str = ""
    all_head_geo: List[str] = field(default_factory=list)
    head_joint: str = ""
    skin_cluster: str = ""

    # Optional geometry
    right_eye: str = ""
    left_eye: str = ""
    upper_teeth: str = ""
    lower_teeth: str = ""
    tongue: str = ""
    eyelash: str = ""
    eyebrow_geo: str = ""

    # Build options
    non_symmetrical: bool = False
    game_engine: bool = False
    simpler_eyelid: bool = False
    eye_socket: bool = False
    long_snout: bool = False
    multi_skin_clusters: bool = False
    arkit: bool = False  # Enable ARKit 52 blendshape creation
    snapchat: bool = False  # Enable SnapChat lens studio support

    # Parameters
    lip_controls: int = 12
    face_scale: float = 1.0
    ctrl_scale: float = 1.0

    # Color scheme
    colors: ColorScheme = field(default_factory=ColorScheme)

    # Build state
    build_step: int = 0

    # Fit data (populated from FaceFitSkeleton during build)
    fit_data: Optional["FitData"] = None

    def load_fit_data(self, fit_skeleton: str = "FaceFitSkeleton") -> bool:
        """
        Load fit data from FaceFitSkeleton in the scene.

        Args:
            fit_skeleton: Name of the fit skeleton group

        Returns:
            True if fit data loaded successfully
        """
        import maya.cmds as cmds

        if not cmds.objExists(fit_skeleton):
            return False

        self.fit_data = FitData.from_fit_skeleton(fit_skeleton)

        # Update face_scale from fit data
        if self.fit_data.face_scale > 0:
            self.face_scale = self.fit_data.face_scale

        return True

    def validate(self) -> List[str]:
        """
        Validate configuration and return list of errors.

        Returns:
            List of error messages, empty if valid.
        """
        errors = []

        if not self.geometry:
            errors.append("Face geometry not specified")
        if not self.all_head_geo:
            errors.append("All head geometry not specified")
        if not self.right_eye:
            errors.append("Right eye not specified")
        if not self.left_eye:
            errors.append("Left eye not specified")
        if not self.head_joint:
            errors.append("Head joint not specified")

        return errors

    def is_valid(self) -> bool:
        """Check if configuration is valid."""
        return len(self.validate()) == 0


@dataclass
class FitData:
    """
    Container for facial fit skeleton data.

    Stores positions and selections from the fitting process
    that are used during the build. This data is read from
    FaceFitSkeleton objects created by the fitting UI.
    """

    # Fit skeleton transforms
    fit_skeleton: str = "FaceFitSkeleton"

    # Face scale (calculated during fitting)
    face_scale: float = 1.0

    # Eye positions
    eye_ball_pos: Tuple[float, float, float] = (0, 0, 0)
    eye_ball_pos_left: Tuple[float, float, float] = (0, 0, 0)

    # Eyebrow positions
    eyebrow_center_pos: Tuple[float, float, float] = (0, 0, 0)
    eyebrow_inner_pos: Tuple[float, float, float] = (0, 0, 0)
    eyebrow_outer_pos: Tuple[float, float, float] = (0, 0, 0)

    # Nose positions
    nose_pos: Tuple[float, float, float] = (0, 0, 0)
    nose_under_pos: Tuple[float, float, float] = (0, 0, 0)
    nose_bridge_pos: Tuple[float, float, float] = (0, 0, 0)
    nose_corner_pos: Tuple[float, float, float] = (0, 0, 0)
    nostril_pos: Tuple[float, float, float] = (0, 0, 0)

    # Jaw positions
    jaw_pivot_pos: Tuple[float, float, float] = (0, 0, 0)
    jaw_corner_pos: Tuple[float, float, float] = (0, 0, 0)
    jaw_pos: Tuple[float, float, float] = (0, 0, 0)
    chin_crease_pos: Tuple[float, float, float] = (0, 0, 0)
    throat_pos: Tuple[float, float, float] = (0, 0, 0)

    # Cheek positions
    cheek_pos: Tuple[float, float, float] = (0, 0, 0)
    cheek_bone_pos: Tuple[float, float, float] = (0, 0, 0)
    smile_bulge_pos: Tuple[float, float, float] = (0, 0, 0)
    frown_bulge_pos: Tuple[float, float, float] = (0, 0, 0)

    # Forehead positions
    forehead_pos: Tuple[float, float, float] = (0, 0, 0)

    # Lip curves
    upper_lip_outer_curve: str = ""
    upper_lip_main_curve: str = ""
    upper_lip_inner_curve: str = ""
    lower_lip_outer_curve: str = ""
    lower_lip_main_curve: str = ""
    lower_lip_inner_curve: str = ""

    # Eyelid curves
    upper_eyelid_outer_curve: str = ""
    upper_eyelid_main_curve: str = ""
    upper_eyelid_inner_curve: str = ""
    lower_eyelid_outer_curve: str = ""
    lower_eyelid_main_curve: str = ""
    lower_eyelid_inner_curve: str = ""

    # Vertex selections stored as strings (region_name -> selection_string)
    selections: Dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_fit_skeleton(cls, fit_skeleton: str = "FaceFitSkeleton") -> "FitData":
        """
        Load FitData from an existing FaceFitSkeleton in the scene.

        Args:
            fit_skeleton: Name of the fit skeleton group

        Returns:
            FitData populated from scene objects
        """
        import maya.cmds as cmds

        if not cmds.objExists(fit_skeleton):
            raise ValueError(f"FaceFitSkeleton '{fit_skeleton}' not found")

        data = cls(fit_skeleton=fit_skeleton)

        # Get face scale
        if cmds.attributeQuery("faceScale", node=fit_skeleton, exists=True):
            data.face_scale = cmds.getAttr(f"{fit_skeleton}.faceScale")

        # Load positions from locators
        position_mappings = [
            ("FaceFitEyeBall", "eye_ball_pos"),
            ("FaceFitEyeBallLeft", "eye_ball_pos_left"),
            ("FaceFitEyeBrowCenter", "eyebrow_center_pos"),
            ("FaceFitEyeBrowInner", "eyebrow_inner_pos"),
            ("FaceFitEyeBrowOuter", "eyebrow_outer_pos"),
            ("FaceFitNose", "nose_pos"),
            ("FaceFitNoseUnder", "nose_under_pos"),
            ("FaceFitNoseBridge", "nose_bridge_pos"),
            ("FaceFitNoseCorner", "nose_corner_pos"),
            ("FaceFitNostril", "nostril_pos"),
            ("FaceFitJawPivot", "jaw_pivot_pos"),
            ("FaceFitJawCorner", "jaw_corner_pos"),
            ("FaceFitJaw", "jaw_pos"),
            ("FaceFitChinCrease", "chin_crease_pos"),
            ("FaceFitThroat", "throat_pos"),
            ("FaceFitCheek", "cheek_pos"),
            ("FaceFitCheekBone", "cheek_bone_pos"),
            ("FaceFitSmileBulge", "smile_bulge_pos"),
            ("FaceFitFrownBulge", "frown_bulge_pos"),
            ("FaceFitForeHead", "forehead_pos"),
        ]

        for obj_name, attr_name in position_mappings:
            if cmds.objExists(obj_name):
                pos = cmds.xform(obj_name, query=True, worldSpace=True, translation=True)
                setattr(data, attr_name, tuple(pos))

                # Also store selection if available
                if cmds.attributeQuery("selection", node=obj_name, exists=True):
                    sel = cmds.getAttr(f"{obj_name}.selection")
                    if sel:
                        region_name = obj_name.replace("FaceFit", "")
                        data.selections[region_name] = sel

        # Load curves
        curve_mappings = [
            ("upperLipOuterCurve", "upper_lip_outer_curve"),
            ("upperLipMainCurve", "upper_lip_main_curve"),
            ("upperLipInnerCurve", "upper_lip_inner_curve"),
            ("lowerLipOuterCurve", "lower_lip_outer_curve"),
            ("lowerLipMainCurve", "lower_lip_main_curve"),
            ("lowerLipInnerCurve", "lower_lip_inner_curve"),
            ("upperEyeLidOuterCurve", "upper_eyelid_outer_curve"),
            ("upperEyeLidMainCurve", "upper_eyelid_main_curve"),
            ("upperEyeLidInnerCurve", "upper_eyelid_inner_curve"),
            ("lowerEyeLidOuterCurve", "lower_eyelid_outer_curve"),
            ("lowerEyeLidMainCurve", "lower_eyelid_main_curve"),
            ("lowerEyeLidInnerCurve", "lower_eyelid_inner_curve"),
        ]

        for curve_name, attr_name in curve_mappings:
            if cmds.objExists(curve_name):
                setattr(data, attr_name, curve_name)
                # Store selection from curve attribute
                if cmds.attributeQuery("selection", node=curve_name, exists=True):
                    sel = cmds.getAttr(f"{curve_name}.selection")
                    if sel:
                        data.selections[curve_name] = sel

        return data

    def get_position(
        self, region_name: str, left_side: bool = False
    ) -> Optional[Tuple[float, float, float]]:
        """Get position for a region, mirroring X if left side requested."""
        suffix = "_left" if left_side else ""
        attr_name = f"{region_name.lower()}_pos{suffix}"

        # Try direct left side first
        pos = getattr(self, attr_name, None)
        if pos and pos != (0, 0, 0):
            return pos

        # If left side requested but no left pos, mirror right
        if left_side:
            right_attr = f"{region_name.lower()}_pos"
            right_pos = getattr(self, right_attr, None)
            if right_pos and right_pos != (0, 0, 0):
                return (-right_pos[0], right_pos[1], right_pos[2])

        return getattr(self, f"{region_name.lower()}_pos", None)

    def get_selection(self, region_name: str) -> str:
        """Get stored vertex selection for a region."""
        return self.selections.get(region_name, "")

"""
EyeBrow component for facial rig.

Handles the creation of eyebrow controls, joints, and deformation setup.
"""

from typing import Dict, List, Optional

import maya.cmds as cmds

from ..core.base import FacialComponent
from ..core.config import FacialRigConfig
from ..core.naming import Side
from ..utils.curves import CurveUtils
from ..utils.math_utils import MathUtils


class EyeBrowComponent(FacialComponent):
    """
    EyeBrow facial component.

    Creates the eyebrow rig including:
    - EyeBrow region controller
    - Inner, outer, and mid controllers
    - Center controller
    - Squeeze and outerUpDown functionality
    """

    INNER = "Inner"
    OUTER = "Outer"
    CENTER = "Center"
    MID = "Mid"

    def __init__(self, config: FacialRigConfig, side: Side = Side.RIGHT):
        """
        Initialize EyeBrow component.

        Args:
            config: Facial rig configuration
            side: Side to build
        """
        super().__init__(config, side)

        self._brow_controllers: Dict[str, str] = {}

    @property
    def name(self) -> str:
        return "EyeBrow"

    def build(self) -> bool:
        """
        Build the eyebrow component.

        Returns:
            True if build succeeded
        """
        if not self.pre_build():
            return False

        # Check if eyebrow fitting exists
        if not cmds.objExists("EyeBrowInner"):
            cmds.warning("EyeBrow fitting not found, skipping component")
            return False

        try:
            self._create_brow_region()
            self._create_brow_controllers()
            self._create_center_controller()
            self._setup_constrained_controls()
            self._setup_driving_system()
            self._setup_squeeze()
            self._setup_outer_up_down()

            self.post_build()
            return True

        except Exception as e:
            cmds.warning(f"EyeBrow build failed: {e}")
            return False

    def _create_brow_region(self):
        """Create the eyebrow region controller."""
        # Create region controller
        region_ctrl = self.create_controller("EyeBrowRegion", self.side, ctrl_type=4, radius=0.3)

        # Create half-moon shape
        self._create_half_moon_shape(region_ctrl, rotation=90)

        # Delete the joint created by region type
        region_joint = f"EyeBrowRegionJoint{self.side.value}"
        if cmds.objExists(region_joint):
            cmds.delete(region_joint)

        # Parent to SideReverse
        offset = f"EyeBrowRegionOffset{self.side.value}"
        side_reverse = f"SideReverse{self.side.value}"
        if cmds.objExists(side_reverse):
            cmds.parent(offset, side_reverse)
            cmds.xform(offset, objectSpace=True, rotation=(0, 0, 0), scale=(1, 1, 1))

        # Position at eyebrow center
        left_suffix = "Left" if self.side == Side.LEFT else ""
        inner_pos = self._get_fit_position(f"EyeBrowInner{left_suffix}")
        outer_pos = self._get_fit_position(f"EyeBrowOuter{left_suffix}")

        if inner_pos and outer_pos:
            center_pos = MathUtils.midpoint(inner_pos, outer_pos)
            if self.side == Side.RIGHT:
                center_pos[0] = abs(center_pos[0])
            else:
                center_pos[0] = -abs(center_pos[0])

            cmds.xform(offset, worldSpace=True, translation=center_pos)

            # Scale based on distance
            dist = MathUtils.distance(inner_pos, outer_pos)
            scale = self.config.face_scale / dist
            cmds.scale(
                scale, scale / 2, scale, f"{region_ctrl}.cv[0:7]", relative=True, pivot=center_pos
            )

        self._brow_controllers["region"] = region_ctrl

        # Create constraint target
        constrain_to = f"EyeBrowRegionConstrainTo{self.side.value}"
        cmds.createNode("transform", name=constrain_to, parent=region_ctrl)
        cmds.xform(constrain_to, objectSpace=True, translation=(0, 0, 0), scale=(1, 1, 1))

        if inner_pos:
            cmds.xform(constrain_to, worldSpace=True, translation=inner_pos)

    def _create_brow_controllers(self):
        """Create inner, outer, and mid controllers."""
        left_suffix = "Left" if self.side == Side.LEFT else ""

        # Inner controller
        inner_pos = self._get_fit_position(f"EyeBrowInner{left_suffix}")
        if inner_pos:
            inner_ctrl = self.create_controller("EyeBrowInner", self.side, ctrl_type=1)
            inner_offset = f"EyeBrowInnerOffset{self.side.value}"
            cmds.xform(inner_offset, worldSpace=True, translation=inner_pos)
            self._brow_controllers["inner"] = inner_ctrl

        # Outer controller
        outer_pos = self._get_fit_position(f"EyeBrowOuter{left_suffix}")
        if outer_pos:
            outer_ctrl = self.create_controller("EyeBrowOuter", self.side, ctrl_type=1)
            outer_offset = f"EyeBrowOuterOffset{self.side.value}"
            cmds.xform(outer_offset, worldSpace=True, translation=outer_pos)
            self._brow_controllers["outer"] = outer_ctrl

        # Mid controllers (1-3)
        for i in range(1, 4):
            mid_fit = f"EyeBrowMid{i}{left_suffix}"
            if cmds.objExists(mid_fit):
                mid_pos = self._get_fit_position(mid_fit)
                if mid_pos:
                    mid_ctrl = self.create_controller(f"EyeBrowMid{i}", self.side, ctrl_type=3)
                    mid_offset = f"EyeBrowMid{i}Offset{self.side.value}"
                    cmds.xform(mid_offset, worldSpace=True, translation=mid_pos)
                    self._brow_controllers[f"mid{i}"] = mid_ctrl

    def _create_center_controller(self):
        """Create the center eyebrow controller."""
        if self.side != Side.RIGHT:
            return  # Only create once from right side

        center_pos = self._get_fit_position("EyeBrowCenter")
        if not center_pos:
            return

        center_ctrl = self.create_controller("EyeBrowCenter", Side.CENTER, ctrl_type=1)

        offset = "EyeBrowCenterOffset_M"
        cmds.xform(offset, worldSpace=True, translation=center_pos)

        # Add follow attribute
        cmds.addAttr(
            center_ctrl,
            longName="follow",
            attributeType="double",
            minValue=0,
            maxValue=10,
            defaultValue=10,
            keyable=True,
        )

        # Create follow setup
        follow_grp = cmds.createNode("transform", name="EyeBrowCenterFollow_M", parent=offset)

        # Create unit conversion for follow
        unit_conv = cmds.createNode("unitConversion", name="EyeBrowCenterFollowUnitConversion")
        cmds.setAttr(f"{unit_conv}.conversionFactor", 0.1)
        cmds.connectAttr(f"{center_ctrl}.follow", f"{unit_conv}.input")

        # Parent SDK to follow
        sdk = "SDKEyeBrowCenter_M"
        if cmds.objExists(sdk):
            cmds.parent(sdk, follow_grp)

        self._brow_controllers["center"] = center_ctrl

    def _setup_constrained_controls(self):
        """Setup constrained mid controls."""
        region_ctrl = self._brow_controllers.get("region")
        inner_ctrl = self._brow_controllers.get("inner")
        outer_ctrl = self._brow_controllers.get("outer")

        if not all([region_ctrl, inner_ctrl]):
            return

        # Parent inner and outer to region
        inner_offset = f"EyeBrowInnerOffset{self.side.value}"
        outer_offset = f"EyeBrowOuterOffset{self.side.value}"

        if cmds.objExists(inner_offset):
            cmds.parent(inner_offset, region_ctrl)
            # Scale down inner controller
            inner_pos = cmds.xform(inner_ctrl, query=True, worldSpace=True, translation=True)
            cmds.scale(0.6, 0.6, 0.6, f"{inner_ctrl}.cv[0:99]", relative=True, pivot=inner_pos)

        if cmds.objExists(outer_offset):
            cmds.parent(outer_offset, region_ctrl)

        # Setup mid constraints
        for i in range(1, 4):
            mid_ctrl = self._brow_controllers.get(f"mid{i}")
            if mid_ctrl:
                # Constrain mids between inner/outer and region
                self._add_constrained_ctrl(
                    mid_ctrl,
                    inner_ctrl if i == 1 else outer_ctrl,
                    region_ctrl,
                    weight=3 if i in [1, 3] else 1,
                )

    def _add_constrained_ctrl(self, target: str, source_a: str, source_b: str, weight: float):
        """Add constraint between controllers."""
        # This creates a weighted blend between two source controllers
        offset = target.replace(target.split("_")[0], target.split("_")[0] + "Offset")

        if not cmds.objExists(offset):
            return

        # Create blend matrix setup
        blend_matrix = cmds.createNode("blendMatrix", name=f"{target}_blendMatrix")

        cmds.connectAttr(f"{source_a}.worldMatrix[0]", f"{blend_matrix}.target[0].targetMatrix")
        cmds.connectAttr(f"{source_b}.worldMatrix[0]", f"{blend_matrix}.target[1].targetMatrix")

        # Set blend weight
        cmds.setAttr(f"{blend_matrix}.target[0].weight", weight)
        cmds.setAttr(f"{blend_matrix}.target[1].weight", 10 - weight)

    def _setup_driving_system(self):
        """Setup driving system connections."""
        # Get distances for SDK values
        inner_pos = self._get_fit_position("EyeBrowInner")
        eye_pos = self._get_fit_position("FitEyeBall")

        if not inner_pos or not eye_pos:
            return

        dist = (inner_pos[1] - eye_pos[1]) / self.config.ctrl_scale / 2.0
        dist = max(0.25, min(dist, 1.0))

        # Create ctrl box slider
        ctrl_box = self.naming.ctrl_box("Brow", self.side)
        if not cmds.objExists(ctrl_box):
            cmds.createNode("transform", name=ctrl_box)

        slider_name = f"ctrlBrow{self.side.value}"
        if not cmds.objExists(slider_name):
            slider = cmds.circle(
                name=slider_name,
                center=(0, 0, 0),
                normal=(0, 0, 1),
                radius=0.15,
                degree=3,
                sections=8,
                constructionHistory=False,
            )[0]
            cmds.parent(slider, ctrl_box)

        # Setup SDK connections
        region_sdk = f"SDKEyeBrowRegion{self.side.value}"
        inner_sdk = f"SDKEyeBrowInner{self.side.value}"

        if cmds.objExists(region_sdk):
            self.create_sdk_setup(f"{slider_name}.ty", f"{region_sdk}.ty", 1, dist)
            self.create_sdk_setup(f"{slider_name}.ty", f"{region_sdk}.ty", -1, -dist)

        if cmds.objExists(inner_sdk):
            self.create_sdk_setup(f"{slider_name}.tx", f"{inner_sdk}.ty", 1, dist)
            self.create_sdk_setup(f"{slider_name}.tx", f"{inner_sdk}.ty", -1, -dist)

    def _setup_squeeze(self):
        """Setup squeeze functionality."""
        slider_name = f"ctrlBrow{self.side.value}"
        if not cmds.objExists(slider_name):
            return

        # Add squeeze attribute
        if not cmds.attributeQuery("squeeze", node=slider_name, exists=True):
            cmds.addAttr(
                slider_name,
                longName="squeeze",
                attributeType="double",
                keyable=True,
                softMinValue=0,
                softMaxValue=10,
            )

        # Get inner position for SDK values
        inner_pos = self._get_fit_position("EyeBrowInner")
        if not inner_pos:
            return

        # Setup squeeze SDKs for inner
        inner_sdk = f"SDKEyeBrowInner{self.side.value}"
        if cmds.objExists(inner_sdk):
            x_value = (inner_pos[0] / self.config.ctrl_scale) * 0.50
            y_value = (inner_pos[0] / self.config.ctrl_scale) * 0.25

            self.create_sdk_setup(f"{slider_name}.squeeze", f"{inner_sdk}.tx", 10, x_value)
            self.create_sdk_setup(f"{slider_name}.squeeze", f"{inner_sdk}.ty", 10, y_value)

    def _setup_outer_up_down(self):
        """Setup outerUpDown functionality."""
        slider_name = f"ctrlBrow{self.side.value}"
        if not cmds.objExists(slider_name):
            return

        # Add outerUpDown attribute
        if not cmds.attributeQuery("outerUpDown", node=slider_name, exists=True):
            cmds.addAttr(
                slider_name,
                longName="outerUpDown",
                attributeType="double",
                keyable=True,
                softMinValue=0,
                softMaxValue=10,
            )

        # Get forehead curve position for target
        if not cmds.objExists("ForeHeadTopToSideCurve"):
            return

        target_pos = CurveUtils.get_point_on_curve(
            "ForeHeadTopToSideCurve", 0.65, use_percentage=True
        )

        # Get outer position
        outer_pos = self._get_fit_position("EyeBrowOuter")
        if not outer_pos:
            return

        # Calculate offset for SDK
        offset = [
            target_pos[0] - outer_pos[0],
            target_pos[1] - outer_pos[1],
            target_pos[2] - outer_pos[2],
        ]

        # Setup SDKs for all brow controls
        controls = ["EyeBrowInner", "EyeBrowMid1", "EyeBrowMid2", "EyeBrowMid3", "EyeBrowOuter"]
        for i, ctrl_name in enumerate(controls):
            sdk = f"SDK{ctrl_name}{self.side.value}"
            if not cmds.objExists(sdk):
                continue

            percentage = MathUtils.smoothstep(0, 1, 0.2 * (i + 1))
            self.create_sdk_setup(
                f"{slider_name}.outerUpDown", f"{sdk}.tx", 10, offset[0] * percentage
            )
            self.create_sdk_setup(
                f"{slider_name}.outerUpDown", f"{sdk}.ty", 10, offset[1] * percentage
            )
            self.create_sdk_setup(
                f"{slider_name}.outerUpDown", f"{sdk}.tz", 10, offset[2] * percentage
            )

    def _get_fit_position(self, fit_object: str) -> Optional[List[float]]:
        """Get position from fit object."""
        if cmds.objExists(fit_object):
            return cmds.xform(fit_object, query=True, worldSpace=True, translation=True)
        return None

    def _create_half_moon_shape(self, ctrl: str, rotation: float = 0):
        """Create half-moon controller shape."""
        # Delete existing shape
        shapes = cmds.listRelatives(ctrl, shapes=True) or []

        # Create arc
        arc = cmds.circle(
            center=(0, 0, 0),
            normal=(0, 0, 1),
            sweep=180,
            radius=0.3,
            degree=3,
            sections=8,
            constructionHistory=False,
        )[0]

        if rotation:
            cmds.rotate(0, 0, rotation, f"{arc}.cv[0:99]", relative=True)

        # Parent shape to controller
        arc_shape = cmds.listRelatives(arc, shapes=True)[0]
        cmds.parent(arc_shape, ctrl, shape=True, relative=True)
        cmds.delete(arc)

        # Delete original shapes
        for shape in shapes:
            cmds.delete(shape)

"""
EyeLid component for facial rig.

Handles the creation of eyelid controls, joints, and deformation setup.
"""

from typing import Dict, List

import maya.cmds as cmds

from ..core.base import FacialComponent
from ..core.config import FacialRigConfig
from ..core.naming import Side
from ..utils.curves import CurveUtils
from ..utils.skinning import SkinningUtils


class EyeLidComponent(FacialComponent):
    """
    EyeLid facial component.

    Creates the eyelid rig including:
    - Upper and lower lid curves
    - Lid joints driven by curves
    - Blink and fleshy eye functionality
    - Lid controllers
    """

    UPPER = "upper"
    LOWER = "lower"
    MAIN = "Main"
    OUTER = "Outer"
    INNER = "Inner"

    def __init__(self, config: FacialRigConfig, side: Side = Side.RIGHT):
        """
        Initialize EyeLid component.

        Args:
            config: Facial rig configuration
            side: Side to build
        """
        super().__init__(config, side)

        self._lid_curves: Dict[str, str] = {}
        self._lid_locators: List[str] = []
        self._lid_setup_group: str = ""

    @property
    def name(self) -> str:
        return "EyeLid"

    def build(self) -> bool:
        """
        Build the eyelid component.

        Returns:
            True if build succeeded
        """
        if not self.pre_build():
            return False

        try:
            self._create_lid_hierarchy()
            self._create_lid_curves()
            self._create_lid_joints()
            self._setup_lid_deformation()
            self._create_lid_controls()
            self._setup_blink()

            self.post_build()
            return True

        except Exception as e:
            cmds.warning(f"EyeLid build failed: {e}")
            return False

    def _create_lid_hierarchy(self):
        """Create the lid setup hierarchy."""
        deform_system = self.hierarchy.DEFORMATION_SYSTEM

        self._lid_setup_group = self.hierarchy.create_component_group("LidSetup", deform_system)

        self.hierarchy.create_component_group("LidJoints", self._lid_setup_group)

        # Create side-specific groups
        side_group = f"LidSetup{self.side.value}"
        cmds.createNode("transform", name=side_group)
        cmds.parent(side_group, self._lid_setup_group)

        # Create curves group
        curves_group = f"LidCurves{self.side.value}"
        cmds.createNode("transform", name=curves_group, parent=deform_system)

        # Create locators group
        locs_group = f"LidLocs{self.side.value}"
        cmds.createNode("transform", name=locs_group, parent=self._lid_setup_group)
        cmds.setAttr(f"{locs_group}.inheritsTransform", 0)

    def _create_lid_curves(self):
        """Create lid curves from fit data."""
        left_suffix = "Left" if self.side == Side.LEFT else ""

        for upper_lower in [self.UPPER, self.LOWER]:
            for curve_type in [self.MAIN, self.OUTER]:
                fit_curve = f"{upper_lower}EyeLid{curve_type}Curve{left_suffix}"

                if not cmds.objExists(fit_curve):
                    continue

                # Duplicate and rebuild curve
                curve_name = f"{upper_lower}Lid{curve_type}Curve{self.side.value}"
                curve = cmds.duplicate(fit_curve, name=curve_name)[0]

                CurveUtils.rebuild_curve(curve, spans=5, degree=3)

                # Parent to curves group
                curves_group = f"LidCurves{self.side.value}"
                cmds.parent(curve, curves_group)

                self._lid_curves[f"{upper_lower}{curve_type}"] = curve

                # Create tweak curve
                tweak_curve = cmds.duplicate(
                    curve, name=f"{upper_lower}Lid{curve_type}CurveTweak{self.side.value}"
                )[0]
                self._lid_curves[f"{upper_lower}{curve_type}Tweak"] = tweak_curve

        # Create blink and fleshy curves for main curves
        for upper_lower in [self.UPPER, self.LOWER]:
            main_curve = self._lid_curves.get(f"{upper_lower}{self.MAIN}")
            if main_curve:
                # Fleshy curve
                fleshy = cmds.duplicate(
                    main_curve, name=f"{upper_lower}LidCurveFleshy{self.side.value}"
                )[0]
                self._lid_curves[f"{upper_lower}Fleshy"] = fleshy

                # Blink curve
                blink = cmds.duplicate(
                    main_curve, name=f"{upper_lower}LidCurveBlink{self.side.value}"
                )[0]
                self._lid_curves[f"{upper_lower}Blink"] = blink

    def _create_lid_joints(self):
        """Create joints for lid deformation."""
        left_suffix = "Left" if self.side == Side.LEFT else ""

        # Create main lid joint parent
        lid_joints_parent = "EyeLidJoints_M"
        if not cmds.objExists(lid_joints_parent):
            cmds.select(self.hierarchy.FACE_JOINT)
            cmds.joint(name=lid_joints_parent)
            cmds.setAttr(f"{lid_joints_parent}.drawStyle", 2)

        for upper_lower in [self.UPPER, self.LOWER]:
            for curve_type in [self.MAIN, self.OUTER]:
                if self.config.simpler_eyelid and curve_type == self.OUTER:
                    continue

                fit_curve = f"{upper_lower}EyeLid{curve_type}Curve{left_suffix}"
                if not cmds.objExists(fit_curve):
                    continue

                num_cvs = cmds.getAttr(f"{fit_curve}.spans") + 1

                for i in range(num_cvs):
                    # Skip overlapping corners for lower lid
                    if upper_lower == self.LOWER and (i == 0 or i == num_cvs - 1):
                        continue

                    # Get position from fit curve
                    pos = cmds.xform(
                        f"{fit_curve}.cv[{i}]", query=True, worldSpace=True, translation=True
                    )

                    # Create joint
                    joint_name = f"{upper_lower}Lid{curve_type}{i}{self.side.value}"
                    cmds.select(clear=True)
                    joint = cmds.joint(name=joint_name, position=pos)
                    cmds.setAttr(f"{joint}.segmentScaleCompensate", 0)
                    cmds.setAttr(f"{joint}.radius", 0.1)
                    cmds.parent(joint, lid_joints_parent)

                    self._joints.append(joint)

                    # Create locator for curve attachment
                    loc_name = f"{upper_lower}Lid{curve_type}Loc{i}{self.side.value}"
                    loc = cmds.spaceLocator(name=loc_name)[0]
                    scale = self.config.face_scale / 100.0
                    cmds.setAttr(f"{loc}.localScale", scale, scale, scale, type="float3")

                    locs_group = f"LidLocs{self.side.value}"
                    cmds.parent(loc, locs_group)
                    self._lid_locators.append(loc)

                    # Create pointOnCurveInfo to drive locator
                    poci = cmds.createNode(
                        "pointOnCurveInfo",
                        name=f"{upper_lower}Lid{curve_type}Poci{i}{self.side.value}",
                    )

                    curve = self._lid_curves.get(f"{upper_lower}{curve_type}")
                    if curve:
                        cmds.connectAttr(f"{curve}Shape.worldSpace[0]", f"{poci}.inputCurve")
                        # Set parameter based on CV position
                        param = i / (num_cvs - 1) if num_cvs > 1 else 0.5
                        cmds.setAttr(f"{poci}.parameter", param * (num_cvs - 1))

                        cmds.connectAttr(f"{poci}.position", f"{loc}.translate")

    def _setup_lid_deformation(self):
        """Setup lid deformation including skinning."""
        skin_cluster = self.config.skin_cluster

        # Add lid joints to skin cluster
        for joint in self._joints:
            if cmds.objExists(joint):
                SkinningUtils.add_influence(skin_cluster, joint)

        # Skin curves to eye region joint
        eye_region_joint = f"EyeRegionJoint{self.side.value}"

        for key, curve in self._lid_curves.items():
            if "Main" in key and "Tweak" not in key:
                if cmds.objExists(curve) and cmds.objExists(eye_region_joint):
                    sc_name = f"{curve}SC"
                    cmds.select(eye_region_joint, curve)
                    result = cmds.skinCluster(
                        toSelectedBones=True, maximumInfluences=3, dropoffRate=4
                    )
                    if result:
                        cmds.rename(result[0], sc_name)

    def _create_lid_controls(self):
        """Create lid controllers."""
        # Create eye control box
        ctrl_box = self.naming.ctrl_box("Eye", self.side)
        if not cmds.objExists(ctrl_box):
            cmds.createNode("transform", name=ctrl_box)

        # Create main lid controller
        ctrl_name = f"ctrlEye{self.side.value}"
        if not cmds.objExists(ctrl_name):
            ctrl = cmds.circle(
                name=ctrl_name,
                center=(0, 0, 0),
                normal=(0, 0, 1),
                radius=0.3,
                degree=3,
                sections=8,
                constructionHistory=False,
            )[0]

            # Add attributes for lid control
            cmds.addAttr(
                ctrl,
                longName="upperLidFollow",
                attributeType="double",
                minValue=0,
                maxValue=10,
                defaultValue=5,
                keyable=True,
            )
            cmds.addAttr(
                ctrl,
                longName="lowerLidFollow",
                attributeType="double",
                minValue=0,
                maxValue=10,
                defaultValue=2,
                keyable=True,
            )
            cmds.addAttr(
                ctrl,
                longName="blink",
                attributeType="double",
                minValue=0,
                maxValue=10,
                defaultValue=0,
                keyable=True,
            )

            self._controllers.append(ctrl)

    def _setup_blink(self):
        """Setup blink functionality."""
        # Create closed lid target curves
        upper_main = self._lid_curves.get(f"{self.UPPER}{self.MAIN}")
        lower_main = self._lid_curves.get(f"{self.LOWER}{self.MAIN}")

        if not upper_main or not lower_main:
            return

        # Create blend between open and closed positions
        upper_closed = f"upperClosedLidCurve{self.side.value}"
        if not cmds.objExists(upper_closed):
            cmds.duplicate(upper_main, name=upper_closed)

        lower_closed = f"lowerClosedLidCurve{self.side.value}"
        if not cmds.objExists(lower_closed):
            cmds.duplicate(lower_main, name=lower_closed)

    def create_eyelid_area_set(self) -> str:
        """
        Create the eyelid vertex area set.

        Returns:
            Set name
        """
        left_suffix = "Left" if self.side == Side.LEFT else ""
        set_name = f"eyeLidArea{left_suffix}"

        if cmds.objExists(set_name):
            return set_name

        # Get vertices from fit curves
        outer_selection = self._get_fit_selection(f"FaceFitEyeLidOuterCurve{left_suffix}")
        main_selection = self._get_fit_selection(f"FaceFitEyeLidMainCurve{left_suffix}")
        inner_selection = self._get_fit_selection(f"FaceFitEyeLidInnerCurve{left_suffix}")

        if main_selection:
            cmds.select(main_selection)

            # Grow selection
            for _ in range(20):
                cmds.polySelectConstraint(pp=1, type=0x0001)
                if outer_selection:
                    cmds.select(outer_selection, deselect=True)
                if inner_selection:
                    cmds.select(inner_selection, deselect=True)

            cmds.select(main_selection, add=True)

            # Create set
            cmds.sets(name=set_name)
            cmds.sets(set_name, add="FaceAreas")

        return set_name

    def _get_fit_selection(self, fit_object: str) -> str:
        """Get selection from fit object (ricampionata, parita'
        asGetFaceFitSelection)."""
        return self.get_fit_selection(fit_object)

    def setup_fleshy_eye(self, eye_joint: str):
        """
        Setup fleshy eye - lids follow eye rotation.

        Args:
            eye_joint: Eye joint name
        """
        ctrl = f"ctrlEye{self.side.value}"
        if not cmds.objExists(ctrl):
            return

        upper_follow = cmds.getAttr(f"{ctrl}.upperLidFollow") / 10.0
        lower_follow = cmds.getAttr(f"{ctrl}.lowerLidFollow") / 10.0

        # Connect eye rotation to lid curves
        for upper_lower, follow in [(self.UPPER, upper_follow), (self.LOWER, lower_follow)]:
            fleshy_curve = self._lid_curves.get(f"{upper_lower}Fleshy")
            if fleshy_curve and cmds.objExists(eye_joint):
                # Create multiply node for follow amount
                mult = cmds.createNode(
                    "multiplyDivide", name=f"{upper_lower}LidFleshyMult{self.side.value}"
                )
                cmds.setAttr(f"{mult}.input2X", follow)
                cmds.setAttr(f"{mult}.input2Y", follow)

                cmds.connectAttr(f"{eye_joint}.rotateX", f"{mult}.input1X")
                cmds.connectAttr(f"{eye_joint}.rotateY", f"{mult}.input1Y")

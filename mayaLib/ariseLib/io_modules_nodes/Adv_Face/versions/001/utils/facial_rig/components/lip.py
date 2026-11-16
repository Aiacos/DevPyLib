"""
Lip component for facial rig.

Handles the creation of lip controls, joints, and deformation setup.
"""

from typing import Dict, List

import maya.cmds as cmds

from ..core.base import FacialComponent
from ..core.config import FacialRigConfig
from ..core.naming import Side
from ..utils.curves import CurveUtils


class LipComponent(FacialComponent):
    """
    Lip facial component.

    Creates the lip rig including:
    - Upper and lower lip curves
    - Lip ribbon surface
    - Lip joints and follicles
    - Lip controllers with roll, press, and pucker
    - Corner controls
    """

    UPPER = "upper"
    LOWER = "lower"
    MAIN = "Main"
    OUTER = "Outer"
    INNER = "Inner"

    def __init__(self, config: FacialRigConfig, side: Side = Side.CENTER):
        """
        Initialize Lip component.

        Args:
            config: Facial rig configuration
            side: Side to build (usually CENTER for lips)
        """
        super().__init__(config, side)

        self._lip_curves: Dict[str, str] = {}
        self._ribbon_surfaces: Dict[str, str] = {}
        self._follicles: List[str] = []
        self._lip_setup_group: str = ""

    @property
    def name(self) -> str:
        return "Lip"

    def build(self) -> bool:
        """
        Build the lip component.

        Returns:
            True if build succeeded
        """
        if not self.pre_build():
            return False

        try:
            self._create_lip_hierarchy()
            self._create_lip_curves()
            self._create_lip_joints()
            self._create_ribbon_surface()
            self._create_follicles()
            self._create_lip_controls()
            self._setup_lip_attributes()

            self.post_build()
            return True

        except Exception as e:
            cmds.warning(f"Lip build failed: {e}")
            return False

    def _create_lip_hierarchy(self):
        """Create the lip setup hierarchy."""
        deform_system = self.hierarchy.DEFORMATION_SYSTEM

        self._lip_setup_group = self.hierarchy.create_component_group("LipSetup", deform_system)

        # Sub-groups
        for grp_name in [
            "LipRibbon",
            "LipFollicles",
            "LipRibbonJoints",
            "LipRibbonLocs",
            "LipRibbonFleshy",
            "LipSlider",
        ]:
            self.hierarchy.create_component_group(grp_name, self._lip_setup_group)

        # LipFollowHead setup
        follow_head = cmds.createNode(
            "transform", name="LipFollowHead", parent=self._lip_setup_group
        )

        # Constrain to head joint
        if cmds.objExists(self.config.head_joint):
            cmds.parentConstraint(self.config.head_joint, follow_head, maintainOffset=True)

    def _create_lip_curves(self):
        """Create lip curves from fit data."""
        for upper_lower in [self.UPPER, self.LOWER]:
            for curve_type in [self.INNER, self.OUTER, self.MAIN]:
                for left_suffix in ["", "Left"]:
                    fit_curve = f"{upper_lower}Lip{curve_type}Curve{left_suffix}"

                    if not cmds.objExists(fit_curve):
                        continue

                    # Store reference
                    key = f"{upper_lower}{curve_type}{left_suffix}"
                    self._lip_curves[key] = fit_curve

        # Create build curves from vertex selections
        self._create_build_curves()

    def _create_build_curves(self):
        """Create build curves from ordered vertex selections."""
        for side_suffix in ["", "Left"]:
            for upper_lower in [self.UPPER, self.LOWER]:
                for curve_type in [self.INNER, self.OUTER, self.MAIN]:
                    fit_curve = f"{upper_lower}Lip{curve_type}Curve{side_suffix}"

                    if not cmds.objExists(fit_curve):
                        continue

                    # Get vertex positions from fit curve
                    num_cvs = cmds.getAttr(f"{fit_curve}.spans") + 1
                    positions = []

                    for i in range(num_cvs):
                        pos = cmds.xform(
                            f"{fit_curve}.cv[{i}]", query=True, worldSpace=True, translation=True
                        )
                        positions.append(pos)

                    # Create build curve
                    curve_name = f"{upper_lower}Lip{curve_type}BuildCurve{side_suffix}"
                    if positions:
                        curve = cmds.curve(name=curve_name, degree=1, point=positions)
                        cmds.parent(curve, "LipSetup")
                        self._lip_curves[f"{upper_lower}{curve_type}Build{side_suffix}"] = curve

    def _create_lip_joints(self):
        """Create joints for lip deformation."""
        # Create main lip joint parent
        cmds.select(self.hierarchy.FACE_JOINT)
        lip_joints_parent = cmds.joint(name="LipJoints_M")
        cmds.setAttr(f"{lip_joints_parent}.segmentScaleCompensate", 0)
        cmds.setAttr(f"{lip_joints_parent}.drawStyle", 2)

        # Position at lip center
        upper_curve = self._lip_curves.get(f"{self.UPPER}{self.OUTER}")
        if upper_curve:
            pos = cmds.xform(f"{upper_curve}.cv[0]", query=True, worldSpace=True, translation=True)
            lower_curve = self._lip_curves.get(f"{self.LOWER}{self.OUTER}")
            if lower_curve:
                lower_pos = cmds.xform(
                    f"{lower_curve}.cv[0]", query=True, worldSpace=True, translation=True
                )
                pos[1] = (pos[1] + lower_pos[1]) / 2
                pos[2] = max(pos[2], lower_pos[2])

            cmds.xform(lip_joints_parent, worldSpace=True, translation=[0, pos[1], pos[2]])

        # Create joints for each side
        for side_suffix in ["", "Left"]:
            build_curve = self._lip_curves.get(f"{self.UPPER}{self.MAIN}Build{side_suffix}")
            if not build_curve:
                continue

            num_cvs = cmds.getAttr(f"{build_curve}.spans") + 1

            for upper_lower in [self.UPPER, self.LOWER]:
                for i in range(num_cvs):
                    side_value = "_R" if not side_suffix else "_L"
                    if i == 0:
                        side_value = "_M"  # Center joints

                    joint_name = f"{upper_lower}LipJoint{i}{side_value}"

                    # Skip if already exists (center shared)
                    if cmds.objExists(joint_name):
                        continue

                    # Get position
                    curve = self._lip_curves.get(f"{upper_lower}{self.MAIN}Build{side_suffix}")
                    if not curve:
                        continue

                    pos = cmds.xform(
                        f"{curve}.cv[{i}]", query=True, worldSpace=True, translation=True
                    )

                    cmds.select(lip_joints_parent)
                    joint = cmds.joint(name=joint_name, position=pos)
                    cmds.setAttr(f"{joint}.segmentScaleCompensate", 0)
                    cmds.setAttr(f"{joint}.radius", 0.1)

                    self._joints.append(joint)

    def _create_ribbon_surface(self):
        """Create ribbon surfaces for lip deformation."""
        # Get lip positions for ribbon shape
        upper_curve = self._lip_curves.get(f"{self.UPPER}{self.MAIN}")
        if not upper_curve or not cmds.objExists(upper_curve):
            return

        pos_a = cmds.xform(f"{upper_curve}.cv[0]", query=True, worldSpace=True, translation=True)
        num_cvs = cmds.getAttr(f"{upper_curve}.spans") + 1
        pos_b = cmds.xform(
            f"{upper_curve}.cv[{num_cvs - 1}]", query=True, worldSpace=True, translation=True
        )

        # Create profile curve for loft
        temp_profile = cmds.curve(
            name="tempLoftProfile",
            degree=1,
            point=[
                (pos_b[0], pos_a[1], pos_b[2]),
                (0, pos_a[1], pos_a[2]),
                (-pos_b[0], pos_a[1], pos_b[2]),
            ],
        )

        CurveUtils.rebuild_curve(temp_profile, spans=5, degree=3)

        # Extrude to create ribbon
        face_scale = self.config.face_scale
        for upper_lower in [self.UPPER, self.LOWER]:
            ribbon_name = f"{upper_lower}LipRibbon"
            direction = 1 if upper_lower == self.UPPER else -1

            ribbon = cmds.extrude(
                temp_profile,
                name=ribbon_name,
                constructionHistory=False,
                rn=False,
                po=0,
                et=0,
                upn=0,
                direction=(0, direction, 0),
                length=face_scale / 200.0,
                rotation=0,
                scale=1,
                dl=3,
            )[0]

            cmds.parent(ribbon, "LipRibbon")
            self._ribbon_surfaces[upper_lower] = ribbon

        cmds.delete(temp_profile)

    def _create_follicles(self):
        """Create follicles on ribbon surface."""
        for upper_lower in [self.UPPER, self.LOWER]:
            ribbon = self._ribbon_surfaces.get(upper_lower)
            if not ribbon:
                continue

            build_curve = self._lip_curves.get(f"{upper_lower}{self.MAIN}Build")
            if not build_curve:
                continue

            num_cvs = cmds.getAttr(f"{build_curve}.spans") + 1

            # Create closestPointOnSurface for UV lookup
            cpos = cmds.createNode("closestPointOnSurface", name="tempCPOS")
            cmds.connectAttr(f"{ribbon}Shape.worldSpace[0]", f"{cpos}.inputSurface")

            for side_suffix in ["", "Left"]:
                for i in range(num_cvs):
                    side_value = "_R" if not side_suffix else "_L"
                    if i == 0:
                        side_value = "_M"

                    # Skip if lower corner (shared with upper)
                    if upper_lower == self.LOWER and i == num_cvs - 1:
                        continue

                    follicle_name = f"{upper_lower}follicle{i}{side_value}"
                    if cmds.objExists(follicle_name):
                        continue

                    # Create follicle
                    follicle_shape = cmds.createNode("follicle")
                    follicle = cmds.listRelatives(follicle_shape, parent=True)[0]
                    follicle = cmds.rename(follicle, follicle_name)

                    cmds.parent(follicle, "LipFollicles")
                    cmds.setAttr(f"{follicle}.collide", 0)

                    # Connect follicle to ribbon
                    cmds.connectAttr(
                        f"{ribbon}Shape.worldSpace[0]", f"{follicle}Shape.inputSurface"
                    )
                    cmds.connectAttr(
                        f"{ribbon}Shape.worldMatrix[0]", f"{follicle}Shape.inputWorldMatrix"
                    )
                    cmds.connectAttr(f"{follicle}Shape.outTranslate", f"{follicle}.translate")
                    cmds.connectAttr(f"{follicle}Shape.outRotate", f"{follicle}.rotate")

                    # Set UV parameters using closestPointOnSurface
                    joint = f"{upper_lower}LipJoint{i}{side_value}"
                    if cmds.objExists(joint):
                        pos = cmds.xform(joint, query=True, worldSpace=True, translation=True)
                        cmds.setAttr(f"{cpos}.inPosition", *pos, type="float3")
                        u = cmds.getAttr(f"{cpos}.parameterU")
                        v = cmds.getAttr(f"{cpos}.parameterV")
                        cmds.setAttr(f"{follicle}Shape.parameterU", u)
                        cmds.setAttr(f"{follicle}Shape.parameterV", v)

                    self._follicles.append(follicle)

            cmds.delete(cpos)

    def _create_lip_controls(self):
        """Create lip controllers."""
        # Create main lips controller
        ctrl_name = "ctrlLips_M"
        if not cmds.objExists(ctrl_name):
            ctrl = cmds.circle(
                name=ctrl_name,
                center=(0, 0, 0),
                normal=(0, 0, 1),
                radius=0.4,
                degree=3,
                sections=8,
                constructionHistory=False,
            )[0]

            # Position at lip center
            upper_curve = self._lip_curves.get(f"{self.UPPER}{self.MAIN}")
            if upper_curve:
                pos = cmds.xform(
                    f"{upper_curve}.cv[0]", query=True, worldSpace=True, translation=True
                )
                lower_curve = self._lip_curves.get(f"{self.LOWER}{self.MAIN}")
                if lower_curve:
                    lower_pos = cmds.xform(
                        f"{lower_curve}.cv[0]", query=True, worldSpace=True, translation=True
                    )
                    pos[1] = (pos[1] + lower_pos[1]) / 2

                offset_name = "ctrlLipsOffset_M"
                offset = cmds.createNode("transform", name=offset_name)
                cmds.parent(ctrl, offset)
                cmds.xform(offset, worldSpace=True, translation=[0, pos[1], pos[2]])

            self._controllers.append(ctrl)

        # Create corner controls
        for side in [Side.RIGHT, Side.LEFT]:
            corner_name = f"cornerLip{side.value}"
            if not cmds.objExists(corner_name):
                corner = cmds.circle(
                    name=corner_name,
                    center=(0, 0, 0),
                    normal=(0, 0, 1),
                    radius=0.15,
                    degree=3,
                    sections=8,
                    constructionHistory=False,
                )[0]

                # Position at lip corner
                upper_curve = self._lip_curves.get(f"{self.UPPER}{self.MAIN}")
                if upper_curve:
                    num_cvs = cmds.getAttr(f"{upper_curve}.spans") + 1
                    cv_index = num_cvs - 1
                    pos = cmds.xform(
                        f"{upper_curve}.cv[{cv_index}]",
                        query=True,
                        worldSpace=True,
                        translation=True,
                    )

                    if side == Side.LEFT:
                        pos[0] *= -1

                    offset_name = f"cornerLipOffset{side.value}"
                    offset = cmds.createNode("transform", name=offset_name)
                    cmds.parent(corner, offset)
                    cmds.xform(offset, worldSpace=True, translation=pos)

                self._controllers.append(corner)

    def _setup_lip_attributes(self):
        """Setup lip control attributes."""
        ctrl = "ctrlLips_M"
        if not cmds.objExists(ctrl):
            return

        # Add attributes for lip controls
        for upper_lower in [self.UPPER, self.LOWER]:
            # Press attribute
            attr_name = f"{upper_lower}Press"
            if not cmds.attributeQuery(attr_name, node=ctrl, exists=True):
                cmds.addAttr(
                    ctrl,
                    longName=attr_name,
                    attributeType="double",
                    keyable=True,
                    softMinValue=-10,
                    softMaxValue=10,
                )

            # Squeeze attribute
            attr_name = f"{upper_lower}Squeeze"
            if not cmds.attributeQuery(attr_name, node=ctrl, exists=True):
                cmds.addAttr(
                    ctrl,
                    longName=attr_name,
                    attributeType="double",
                    keyable=True,
                    softMinValue=-10,
                    softMaxValue=10,
                )

            # Roll attribute
            attr_name = f"{upper_lower}Roll"
            if not cmds.attributeQuery(attr_name, node=ctrl, exists=True):
                cmds.addAttr(
                    ctrl,
                    longName=attr_name,
                    attributeType="double",
                    keyable=True,
                    softMinValue=-10,
                    softMaxValue=10,
                )

            # Pucker attribute
            attr_name = f"{upper_lower}Pucker"
            if not cmds.attributeQuery(attr_name, node=ctrl, exists=True):
                cmds.addAttr(
                    ctrl,
                    longName=attr_name,
                    attributeType="double",
                    keyable=True,
                    softMinValue=-10,
                    softMaxValue=10,
                )

        # Corner sticky attribute
        for side in [Side.RIGHT, Side.LEFT]:
            corner = f"cornerLip{side.value}"
            if cmds.objExists(corner):
                if not cmds.attributeQuery("sticky", node=corner, exists=True):
                    cmds.addAttr(
                        corner,
                        longName="sticky",
                        attributeType="double",
                        keyable=True,
                        minValue=0,
                        maxValue=10,
                        defaultValue=0,
                    )

    def create_lip_area_set(self) -> str:
        """
        Create the lip vertex area set.

        Returns:
            Set name
        """
        set_name = "lipArea"

        if cmds.objExists(set_name):
            return set_name

        # Get vertices from lip inner area
        inner_selection = self._get_fit_selection("LipInnerAreaMesh")
        if inner_selection:
            cmds.select(inner_selection)
            cmds.sets(name=set_name)
            cmds.sets(set_name, add="FaceAreas")

        return set_name

    def _get_fit_selection(self, fit_object: str) -> str:
        """Get selection from fit object (ricampionata, parita'
        asGetFaceFitSelection)."""
        return self.get_fit_selection(fit_object)

"""
Jaw component for facial rig.

Handles jaw joint and jaw weight curves for deformation.
"""

import maya.cmds as cmds

from ..core.base import FacialComponent
from ..core.config import FacialRigConfig
from ..core.naming import Side
from ..utils.curves import CurveUtils


class JawComponent(FacialComponent):
    """
    Jaw facial component.

    Creates:
    - Jaw joint
    - Jaw weight curves (JawCurve, JawCurveMid, JawCurveTop)
    - Jaw open/close controls
    """

    def __init__(self, config: FacialRigConfig, side: Side = Side.CENTER):
        super().__init__(config, side)
        self._jaw_curves = {}

    @property
    def name(self) -> str:
        return "Jaw"

    def build(self) -> bool:
        if not self.pre_build():
            return False

        try:
            self._create_jaw_joint()
            self._create_jaw_curves()
            self._create_jaw_controller()
            self._setup_jaw_weighting()

            self.post_build()
            return True
        except Exception as e:
            cmds.warning(f"Jaw build failed: {e}")
            return False

    def _create_jaw_joint(self):
        """Create the jaw joint."""
        if not cmds.objExists("JawPivot"):
            return

        pos = cmds.xform("JawPivot", query=True, worldSpace=True, translation=True)

        cmds.select(self.hierarchy.FACE_JOINT)
        jaw_joint = cmds.joint(name="Jaw_M", position=pos)
        cmds.setAttr(f"{jaw_joint}.segmentScaleCompensate", 0)

        self._joints.append(jaw_joint)

    def _create_jaw_curves(self):
        """Create jaw weight influence curves."""
        if not all(cmds.objExists(obj) for obj in ["JawPivot", "JawCorner", "Jaw"]):
            return

        # Main jaw curve
        pivot_pos = cmds.xform("JawPivot", query=True, worldSpace=True, translation=True)
        corner_pos = cmds.xform("JawCorner", query=True, worldSpace=True, translation=True)
        jaw_pos = cmds.xform("Jaw", query=True, worldSpace=True, translation=True)

        jaw_curve = cmds.curve(name="JawCurve", degree=1, point=[pivot_pos, corner_pos, jaw_pos])
        CurveUtils.rebuild_curve(jaw_curve, spans=3, degree=3)

        # Set display color
        cmds.setAttr(f"{jaw_curve}Shape.overrideEnabled", 1)
        cmds.setAttr(f"{jaw_curve}Shape.overrideColor", 14)

        self._jaw_curves["main"] = jaw_curve

        # Create JawCurveMid and JawCurveTop similarly
        if cmds.objExists("Cheek") and cmds.objExists("upperLipOuterCurve"):
            cheek_pos = cmds.xform("Cheek", query=True, worldSpace=True, translation=True)
            num_cvs = cmds.getAttr("upperLipOuterCurve.spans") + 1
            lip_corner_pos = cmds.xform(
                f"upperLipOuterCurve.cv[{num_cvs}]", query=True, worldSpace=True, translation=True
            )

            jaw_mid = cmds.curve(
                name="JawCurveMid", degree=1, point=[pivot_pos, cheek_pos, lip_corner_pos]
            )
            CurveUtils.rebuild_curve(jaw_mid, spans=2, degree=3)
            cmds.setAttr(f"{jaw_mid}Shape.overrideEnabled", 1)
            cmds.setAttr(f"{jaw_mid}Shape.overrideColor", 13)

            self._jaw_curves["mid"] = jaw_mid

        # Create parent group
        if not cmds.objExists("FaceFitJawCurves"):
            grp = cmds.createNode("transform", name="FaceFitJawCurves")
            cmds.parent(grp, "FaceFitSkeleton")
            for curve in self._jaw_curves.values():
                cmds.parent(curve, grp)

    def _create_jaw_controller(self):
        """Create jaw controller."""
        jaw_joint = "Jaw_M"
        if not cmds.objExists(jaw_joint):
            return

        ctrl = cmds.circle(
            name="Jaw_M",
            center=(0, 0, 0),
            normal=(0, 0, 1),
            radius=0.3,
            degree=3,
            sections=8,
            constructionHistory=False,
        )[0]

        pos = cmds.xform(jaw_joint, query=True, worldSpace=True, translation=True)
        offset = cmds.createNode("transform", name="ctrlJawOffset_M")
        cmds.parent(ctrl, offset)
        cmds.xform(offset, worldSpace=True, translation=pos)

        # Add jaw attributes
        cmds.addAttr(
            ctrl,
            longName="jawOpen",
            attributeType="double",
            minValue=0,
            maxValue=10,
            defaultValue=0,
            keyable=True,
        )
        cmds.addAttr(
            ctrl,
            longName="jawSide",
            attributeType="double",
            minValue=-10,
            maxValue=10,
            defaultValue=0,
            keyable=True,
        )
        cmds.addAttr(
            ctrl,
            longName="jawForward",
            attributeType="double",
            minValue=-10,
            maxValue=10,
            defaultValue=0,
            keyable=True,
        )

        self._controllers.append(ctrl)

    def _setup_jaw_weighting(self):
        """Setup jaw skin weighting based on curves."""
        # This would use the jaw curves to weight vertices
        # based on their distance to the curves
        pass

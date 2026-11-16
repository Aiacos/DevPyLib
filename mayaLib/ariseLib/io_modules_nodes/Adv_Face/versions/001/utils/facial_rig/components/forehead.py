"""
Forehead component for facial rig.

Handles forehead curves and skin cage.
"""

import maya.cmds as cmds

from ..core.base import FacialComponent
from ..core.config import FacialRigConfig
from ..core.naming import Side
from ..utils.curves import CurveUtils


class ForeheadComponent(FacialComponent):
    """
    Forehead facial component.

    Creates:
    - Forehead curves for deformation
    - Skin cage setup
    - Forehead joint
    """

    def __init__(self, config: FacialRigConfig, side: Side = Side.CENTER):
        super().__init__(config, side)
        self._forehead_curves = {}

    @property
    def name(self) -> str:
        return "Forehead"

    def build(self) -> bool:
        if not self.pre_build():
            return False

        try:
            self._create_forehead_curves()
            self._create_forehead_joint()
            self._setup_forehead_area()

            self.post_build()
            return True
        except Exception as e:
            cmds.warning(f"Forehead build failed: {e}")
            return False

    def _create_forehead_curves(self):
        """Create forehead deformation curves."""
        if not cmds.objExists("ForeHead"):
            return

        # Get forehead fitting positions
        forehead_pos = cmds.xform("ForeHead", query=True, worldSpace=True, translation=True)

        for left_suffix in ["", "Left"]:
            fit_curve = f"FaceFitForeHead{left_suffix}"
            if not cmds.objExists(fit_curve):
                continue

            # Get curve CVs
            num_cvs = CurveUtils.get_curve_cv_count(fit_curve)
            positions = []

            for i in range(num_cvs):
                pos = cmds.xform(
                    f"{fit_curve}.cv[{i}]", query=True, worldSpace=True, translation=True
                )
                positions.append(pos)

            # Create curve
            curve_name = f"ForeHeadCurve{left_suffix}"
            curve = cmds.curve(name=curve_name, degree=3, point=positions)
            CurveUtils.rebuild_curve(curve, spans=5, degree=3)

            self._forehead_curves[left_suffix or "Right"] = curve

        # Create top-to-side curve for region boundaries
        if cmds.objExists("ForeHead") and cmds.objExists("EyeBrowOuter"):
            forehead_pos = cmds.xform("ForeHead", query=True, worldSpace=True, translation=True)
            outer_pos = cmds.xform("EyeBrowOuter", query=True, worldSpace=True, translation=True)

            curve = cmds.curve(
                name="ForeHeadTopToSideCurve",
                degree=3,
                point=[
                    [0, forehead_pos[1], forehead_pos[2]],
                    [outer_pos[0] * 0.5, forehead_pos[1], forehead_pos[2]],
                    outer_pos,
                ],
            )
            CurveUtils.rebuild_curve(curve, spans=3, degree=3)
            self._forehead_curves["topToSide"] = curve

    def _create_forehead_joint(self):
        """Create forehead joint."""
        if not cmds.objExists("ForeHead"):
            return

        pos = cmds.xform("ForeHead", query=True, worldSpace=True, translation=True)

        cmds.select(self.hierarchy.FACE_JOINT)
        joint = cmds.joint(name="ForeHeadJoint_M")
        cmds.xform(joint, worldSpace=True, translation=[0, pos[1], pos[2]])
        cmds.setAttr(f"{joint}.segmentScaleCompensate", 0)

        self._joints.append(joint)

    def _setup_forehead_area(self):
        """Setup forehead vertex area set."""
        set_name = "ForeHeadArea"

        if cmds.objExists(set_name):
            return

        # Get vertices from forehead fit
        if cmds.objExists("ForeHeadAreaMesh"):
            selection = self._get_fit_selection("ForeHeadAreaMesh")
            if selection:
                cmds.select(selection)
                cmds.sets(name=set_name)
                cmds.sets(set_name, add="FaceAreas")

    def _get_fit_selection(self, fit_object: str) -> str:
        """Get selection from fit object (ricampionata, parita'
        asGetFaceFitSelection)."""
        return self.get_fit_selection(fit_object)

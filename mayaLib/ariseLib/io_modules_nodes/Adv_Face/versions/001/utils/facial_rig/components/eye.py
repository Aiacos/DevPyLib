"""
Eye component for facial rig.

Handles eye joints, aim controls, and pupil/iris setup.
"""

import maya.cmds as cmds

from ..core.base import FacialComponent
from ..core.config import FacialRigConfig
from ..core.naming import Side


class EyeComponent(FacialComponent):
    """
    Eye facial component.

    Creates:
    - Eye joints
    - Eye aim controls
    - Pupil and iris controls
    - Eye region controls
    """

    def __init__(self, config: FacialRigConfig, side: Side = Side.RIGHT):
        super().__init__(config, side)

    @property
    def name(self) -> str:
        return "Eye"

    def build(self) -> bool:
        if not self.pre_build():
            return False

        try:
            self._create_eye_joint()
            self._create_eye_aim()
            self._create_eye_region()
            self._setup_pupil_iris()

            self.post_build()
            return True
        except Exception as e:
            cmds.warning(f"Eye build failed: {e}")
            return False

    def _create_eye_joint(self):
        """Create the eye joint."""
        left_suffix = "Left" if self.side == Side.LEFT else ""
        fit_eye = f"FitEyeBall{left_suffix}"

        if not cmds.objExists(fit_eye):
            return

        pos = cmds.xform(fit_eye, query=True, worldSpace=True, translation=True)

        # Create joint
        cmds.select(self.hierarchy.FACE_JOINT)
        eye_joint = cmds.joint(name=f"Eye{self.side.value}", position=pos)
        cmds.setAttr(f"{eye_joint}.segmentScaleCompensate", 0)

        # Create child joint for proper rotation
        cmds.select(eye_joint)
        eye1_joint = cmds.joint(name=f"EyeEnd{self.side.value}")
        cmds.setAttr(f"{eye1_joint}.translateX", self.config.face_scale / 50)

        self._joints.extend([eye_joint, eye1_joint])

    def _create_eye_aim(self):
        """Create eye aim controller."""
        eye_joint = f"Eye{self.side.value}"
        if not cmds.objExists(eye_joint):
            return

        pos = cmds.xform(eye_joint, query=True, worldSpace=True, translation=True)

        # Create aim controller
        aim_ctrl = cmds.circle(
            name=f"AimEye{self.side.value}",
            center=(0, 0, 0),
            normal=(0, 0, 1),
            radius=self.config.face_scale / 20,
            degree=3,
            sections=8,
            constructionHistory=False,
        )[0]

        # Position in front of eye
        aim_offset = cmds.createNode("transform", name=f"AimEyeOffset{self.side.value}")
        cmds.parent(aim_ctrl, aim_offset)
        cmds.xform(
            aim_offset,
            worldSpace=True,
            translation=[pos[0], pos[1], pos[2] + self.config.face_scale / 2],
        )

        # Create aim constraint
        cmds.aimConstraint(
            aim_ctrl,
            eye_joint,
            maintainOffset=True,
            aimVector=(1, 0, 0),
            upVector=(0, 1, 0),
            worldUpType="objectrotation",
            worldUpObject=self.config.head_joint,
        )

        self._controllers.append(aim_ctrl)

    def _create_eye_region(self):
        """Create eye region controller."""
        eye_joint = f"Eye{self.side.value}"
        if not cmds.objExists(eye_joint):
            return

        region_ctrl = self.create_controller("EyeRegion", self.side, ctrl_type=4)
        self.align_to(f"EyeRegionOffset{self.side.value}", eye_joint)
        self._controllers.append(region_ctrl)

    def _setup_pupil_iris(self):
        """Setup pupil and iris if geometry exists."""
        # This would handle pupil/iris dilation controls
        pass

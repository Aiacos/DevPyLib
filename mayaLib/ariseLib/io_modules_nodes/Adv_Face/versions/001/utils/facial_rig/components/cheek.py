"""
Cheek component for facial rig.

Handles cheek, cheekbone, smile, and frown controls.
"""

import maya.cmds as cmds

from ..core.base import FacialComponent
from ..core.config import FacialRigConfig
from ..core.naming import Side


class CheekComponent(FacialComponent):
    """
    Cheek facial component.

    Creates:
    - Cheek controller
    - Cheekbone controller
    - Smile pull controller
    - Frown pull controller
    - Cheek raiser functionality
    """

    def __init__(self, config: FacialRigConfig, side: Side = Side.RIGHT):
        super().__init__(config, side)

    @property
    def name(self) -> str:
        return "Cheek"

    def build(self) -> bool:
        if not self.pre_build():
            return False

        try:
            self._create_cheek_controller()
            self._create_cheekbone_controller()
            self._create_smile_pull()
            self._create_frown_pull()
            self._create_cheek_raiser()

            self.post_build()
            return True
        except Exception as e:
            cmds.warning(f"Cheek build failed: {e}")
            return False

    def _create_cheek_controller(self):
        """Create cheek on-face controller."""
        left_suffix = "Left" if self.side == Side.LEFT else ""
        fit_cheek = f"Cheek{left_suffix}"

        if not cmds.objExists(fit_cheek):
            return

        pos = cmds.xform(fit_cheek, query=True, worldSpace=True, translation=True)

        ctrl = self.create_controller("Cheek", self.side, ctrl_type=1)
        offset = f"CheekOffset{self.side.value}"
        cmds.xform(offset, worldSpace=True, translation=pos)

        # Create joint
        cmds.select(clear=True)
        joint = cmds.joint(name=f"CheekJoint{self.side.value}")
        cmds.xform(joint, worldSpace=True, translation=pos)

        self._joints.append(joint)
        self._controllers.append(ctrl)

    def _create_cheekbone_controller(self):
        """Create cheekbone controller."""
        left_suffix = "Left" if self.side == Side.LEFT else ""
        fit_cheekbone = f"CheekBone{left_suffix}"

        if not cmds.objExists(fit_cheekbone):
            return

        pos = cmds.xform(fit_cheekbone, query=True, worldSpace=True, translation=True)

        ctrl = self.create_controller("CheekBone", self.side, ctrl_type=3)
        offset = f"CheekBoneOffset{self.side.value}"
        cmds.xform(offset, worldSpace=True, translation=pos)

        self._controllers.append(ctrl)

    def _create_smile_pull(self):
        """Create smile pull controller."""
        left_suffix = "Left" if self.side == Side.LEFT else ""
        fit_smile = f"SmileBulge{left_suffix}"

        if not cmds.objExists(fit_smile):
            return

        pos = cmds.xform(fit_smile, query=True, worldSpace=True, translation=True)

        ctrl = self.create_controller("SmileBulge", self.side, ctrl_type=2)
        offset = f"SmileBulgeOffset{self.side.value}"
        cmds.xform(offset, worldSpace=True, translation=pos)

        # Add narrow attribute
        cmds.addAttr(
            ctrl,
            longName="narrow",
            attributeType="double",
            minValue=0,
            maxValue=10,
            defaultValue=0,
            keyable=True,
        )

        self._controllers.append(ctrl)

    def _create_frown_pull(self):
        """Create frown pull controller."""
        left_suffix = "Left" if self.side == Side.LEFT else ""
        fit_frown = f"FrownBulge{left_suffix}"

        if not cmds.objExists(fit_frown):
            return

        pos = cmds.xform(fit_frown, query=True, worldSpace=True, translation=True)

        ctrl = self.create_controller("FrownBulge", self.side, ctrl_type=2)
        offset = f"FrownBulgeOffset{self.side.value}"
        cmds.xform(offset, worldSpace=True, translation=pos)

        # Add narrow attribute
        cmds.addAttr(
            ctrl,
            longName="narrow",
            attributeType="double",
            minValue=0,
            maxValue=10,
            defaultValue=0,
            keyable=True,
        )

        self._controllers.append(ctrl)

    def _create_cheek_raiser(self):
        """Create cheek raiser functionality."""
        # Links cheek raise to squint and smile
        pass

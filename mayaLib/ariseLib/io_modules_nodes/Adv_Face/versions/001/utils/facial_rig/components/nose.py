"""
Nose component for facial rig.

Handles nose and nostril controls.
"""

import maya.cmds as cmds

from ..core.base import FacialComponent
from ..core.config import FacialRigConfig
from ..core.naming import Side


class NoseComponent(FacialComponent):
    """
    Nose facial component.

    Creates:
    - Nose tip controller
    - Nostril controllers
    - Nose bridge controller
    - Nose crease controller
    - Snarl functionality
    """

    def __init__(self, config: FacialRigConfig, side: Side = Side.CENTER):
        super().__init__(config, side)

    @property
    def name(self) -> str:
        return "Nose"

    def build(self) -> bool:
        if not self.pre_build():
            return False

        try:
            self._create_nose_controller()
            self._create_nostril_controllers()
            self._create_nose_bridge()
            self._create_nose_crease()
            self._create_snarl()

            self.post_build()
            return True
        except Exception as e:
            cmds.warning(f"Nose build failed: {e}")
            return False

    def _create_nose_controller(self):
        """Create main nose controller."""
        if not cmds.objExists("Nose"):
            return

        pos = cmds.xform("Nose", query=True, worldSpace=True, translation=True)

        ctrl = self.create_controller("Nose", Side.CENTER, ctrl_type=2)
        offset = "NoseOffset_M"
        cmds.xform(offset, worldSpace=True, translation=[0, pos[1], pos[2]])

        # Create joint
        cmds.select(clear=True)
        joint = cmds.joint(name="NoseJoint_M")
        cmds.xform(joint, worldSpace=True, translation=[0, pos[1], pos[2]])

        self._joints.append(joint)
        self._controllers.append(ctrl)

    def _create_nostril_controllers(self):
        """Create nostril controllers."""
        for side in [Side.RIGHT, Side.LEFT]:
            left_suffix = "Left" if side == Side.LEFT else ""
            fit_nostril = f"Nostril{left_suffix}"

            if not cmds.objExists(fit_nostril):
                continue

            pos = cmds.xform(fit_nostril, query=True, worldSpace=True, translation=True)

            ctrl = self.create_controller("Nostril", side, ctrl_type=3)
            offset = f"NostrilOffset{side.value}"
            cmds.xform(offset, worldSpace=True, translation=pos)

            # Add flare attribute
            cmds.addAttr(
                ctrl,
                longName="flare",
                attributeType="double",
                minValue=-10,
                maxValue=10,
                defaultValue=0,
                keyable=True,
            )

            self._controllers.append(ctrl)

    def _create_nose_bridge(self):
        """Create nose bridge controller."""
        if not cmds.objExists("NoseBridge"):
            return

        pos = cmds.xform("NoseBridge", query=True, worldSpace=True, translation=True)

        ctrl = self.create_controller("NoseBridge", Side.CENTER, ctrl_type=3)
        offset = "NoseBridgeOffset_M"
        cmds.xform(offset, worldSpace=True, translation=[0, pos[1], pos[2]])

        self._controllers.append(ctrl)

    def _create_nose_crease(self):
        """Create nose crease controller."""
        if not cmds.objExists("NoseCrease"):
            return

        pos = cmds.xform("NoseCrease", query=True, worldSpace=True, translation=True)

        ctrl = self.create_controller("NoseCrease", Side.CENTER, ctrl_type=3)
        offset = "NoseCreaseOffset_M"
        cmds.xform(offset, worldSpace=True, translation=[0, pos[1], pos[2]])

        self._controllers.append(ctrl)

    def _create_snarl(self):
        """Create snarl functionality."""
        # Snarl connects nose side movement to sneer expression
        for side in [Side.RIGHT, Side.LEFT]:
            left_suffix = "Left" if side == Side.LEFT else ""
            fit_side = f"NoseSide{left_suffix}"

            if not cmds.objExists(fit_side):
                continue

            pos = cmds.xform(fit_side, query=True, worldSpace=True, translation=True)

            ctrl = self.create_controller("NoseSide", side, ctrl_type=3)
            offset = f"NoseSideOffset{side.value}"
            cmds.xform(offset, worldSpace=True, translation=pos)

            self._controllers.append(ctrl)

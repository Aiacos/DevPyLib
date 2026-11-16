"""
Tongue component for facial rig.

Handles tongue joint chain and controls.
"""

import maya.cmds as cmds

from ..core.base import FacialComponent
from ..core.config import FacialRigConfig
from ..core.naming import Side


class TongueComponent(FacialComponent):
    """
    Tongue facial component.

    Creates:
    - Tongue joint chain
    - Tongue FK controls
    - Tongue tip controller
    """

    def __init__(self, config: FacialRigConfig):
        super().__init__(config, Side.CENTER)
        self._num_joints = 5

    @property
    def name(self) -> str:
        return "Tongue"

    def build(self) -> bool:
        if not self.pre_build():
            return False

        # Check if tongue geometry specified
        if not self.config.tongue:
            cmds.warning("Tongue geometry not specified, skipping component")
            return False

        try:
            self._create_tongue_joints()
            self._create_tongue_controls()
            self._setup_tongue_skinning()

            self.post_build()
            return True
        except Exception as e:
            cmds.warning(f"Tongue build failed: {e}")
            return False

    def _create_tongue_joints(self):
        """Create tongue joint chain."""
        # Check for tongue locators
        if not cmds.objExists("Tongue0"):
            self._create_default_tongue_locators()

        jaw_joint = "Jaw_M"
        parent = jaw_joint if cmds.objExists(jaw_joint) else self.hierarchy.FACE_JOINT

        for i in range(self._num_joints):
            loc_name = f"Tongue{i}"
            if not cmds.objExists(loc_name):
                continue

            pos = cmds.xform(loc_name, query=True, worldSpace=True, translation=True)

            cmds.select(parent)
            joint = cmds.joint(name=f"TongueJoint{i}_M", position=pos)
            cmds.setAttr(f"{joint}.segmentScaleCompensate", 0)

            self._joints.append(joint)
            parent = joint

        # Orient joints
        if self._joints:
            cmds.joint(
                self._joints[0],
                edit=True,
                orientJoint="xyz",
                secondaryAxisOrient="yup",
                children=True,
            )

    def _create_tongue_controls(self):
        """Create tongue FK controls."""
        for i, joint in enumerate(self._joints):
            ctrl_name = f"Tongue{i}_M"

            ctrl = cmds.circle(
                name=ctrl_name,
                center=(0, 0, 0),
                normal=(1, 0, 0),
                radius=self.config.face_scale / 30,
                degree=3,
                sections=8,
                constructionHistory=False,
            )[0]

            pos = cmds.xform(joint, query=True, worldSpace=True, translation=True)
            rot = cmds.xform(joint, query=True, worldSpace=True, rotation=True)

            offset = cmds.createNode("transform", name=f"Tongue{i}Offset_M")
            cmds.parent(ctrl, offset)
            cmds.xform(offset, worldSpace=True, translation=pos, rotation=rot)

            # Connect control to joint
            cmds.connectAttr(f"{ctrl}.rotate", f"{joint}.rotate")

            self._controllers.append(ctrl)

    def _setup_tongue_skinning(self):
        """Setup tongue skinning."""
        if not self.config.tongue or not self._joints:
            return

        # Bind tongue geometry to joints
        cmds.select(self._joints, self.config.tongue)
        cmds.skinCluster(toSelectedBones=True, maximumInfluences=2, dropoffRate=4, name="TongueSC")

    def _create_default_tongue_locators(self):
        """Create default tongue locators if not present."""
        # Get jaw position for reference
        if not cmds.objExists("Jaw"):
            return

        jaw_pos = cmds.xform("Jaw", query=True, worldSpace=True, translation=True)

        # Create locator chain
        spacing = self.config.face_scale / 25

        for i in range(self._num_joints):
            loc = cmds.spaceLocator(name=f"Tongue{i}")[0]
            pos = [0, jaw_pos[1] - spacing * 0.5, jaw_pos[2] - spacing * i]
            cmds.xform(loc, worldSpace=True, translation=pos)

"""MEL interface for HumanIK commands.

This module provides a clean Python wrapper around Maya's HumanIK MEL commands,
isolating all MEL dependencies in a single location for easier maintenance and testing.
"""

from __future__ import annotations

import pymel.core as pm
from maya import mel


class MelInterface:
    """Wrapper class for HumanIK MEL command interface.

    This class encapsulates all MEL command calls used by the HumanIK system,
    providing a clean Python API and centralizing MEL dependencies.

    Attributes:
        character_name (str): The name of the HumanIK character.
    """

    def __init__(self, character_name: str):
        """Initialize the MEL interface for a HumanIK character.

        Args:
            character_name: The name of the HumanIK character to work with.
        """
        self.character_name = str(character_name)

    def open_character_controls_tool(self) -> None:
        """Open the HumanIK Character Controls Tool window.

        This MEL command opens the main HumanIK UI in Maya.
        """
        mel.eval("HIKCharacterControlsTool;")

    def create_character(self) -> None:
        """Create a new HumanIK character.

        Creates a HumanIK character definition with the name specified during
        initialization. This must be called before joints can be mapped.
        """
        mel.eval(f'hikCreateCharacter("{self.character_name}")')

    def set_character_object(self, joint: str, joint_id: int) -> None:
        """Assign a Maya joint to a HumanIK character slot.

        This is the core mapping function that connects Maya joints to HumanIK's
        skeleton definition. The joint_id corresponds to indices in the HumanIK
        bone system (see constants.HUMAN_IK_JOINT_MAP).

        Args:
            joint: The name of the Maya joint to assign.
            joint_id: The HumanIK character object ID (bone index).
        """
        if pm.objExists(joint):
            joint_name = str(pm.ls(joint)[-1].name())
            mel.eval(
                f'setCharacterObject("{joint_name}", "{self.character_name}", "{joint_id}", 0);'
            )

    def load_custom_rig_ui_configuration(self) -> None:
        """Load the custom rig UI configuration.

        Opens the HumanIK custom rig UI panel. This is typically called before
        creating custom rig mappings to set up the UI state.
        """
        mel.eval("hikLoadCustomRigUIConfiguration();")

    def create_custom_rig(self) -> None:
        """Create custom rig mapping for the current character.

        Initializes the custom rig system for the currently active HumanIK character.
        This must be called after skeleton definition and before control mapping.
        """
        mel.eval("hikCreateCustomRig( hikGetCurrentCharacter() );")

    def assign_custom_rig_effector(self, ctrl: str, ctrl_id: int) -> None:
        """Assign a control to a custom rig effector.

        Maps a Maya control to a HumanIK custom rig effector slot. The control
        must exist and be selected in the scene.

        Args:
            ctrl: Name of the Maya control to assign.
            ctrl_id: ID of the HumanIK control effector (see constants.HUMAN_IK_CTRL_MAP).
        """
        if pm.objExists(ctrl):
            pm.select(ctrl)
            mel.eval(f"hikCustomRigAssignEffector {ctrl_id};")

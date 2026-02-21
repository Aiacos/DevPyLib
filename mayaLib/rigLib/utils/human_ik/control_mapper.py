"""Control mapper for HumanIK custom rig control mapping.

This module provides the ControlMapper class which handles all custom control definition
and mapping operations for HumanIK custom rigs. It maps Maya controls to HumanIK's
custom rig effectors and provides convenience methods for different body parts.
"""

from __future__ import annotations

import pymel.core as pm
from maya import mel

from mayaLib.rigLib.utils.human_ik.constants import HUMAN_IK_CTRL_MAP


class ControlMapper:
    """Handles custom control definition and mapping for HumanIK custom rigs.

    This class provides methods to map Maya controls to HumanIK's custom rig effectors.
    It wraps the MEL interface and provides semantic methods for each body part,
    making it easy to define complete custom control rigs.

    Attributes:
        character_name (str): The name of the HumanIK character.
    """

    def __init__(self, character_name: str):
        """Initialize the control mapper for a HumanIK character.

        Args:
            character_name: The name of the HumanIK character to work with.
        """
        self.character_name = str(character_name)

    def load_custom_rig_template(self) -> None:
        """Load the custom rig UI configuration using MEL."""
        mel.eval("hikLoadCustomRigUIConfiguration();")

    def create_custom_rig_mapping(self) -> None:
        """Create custom rig mapping for the current character using MEL."""
        mel.eval("hikCreateCustomRig( hikGetCurrentCharacter() );")

    def add_ctrl(self, ctrl: str, ctrl_id: int) -> None:
        """Assign a control to a custom rig effector.

        This is the core mapping function for controls. All other control mapping
        methods use this internally.

        Args:
            ctrl: Name of the control.
            ctrl_id: ID of the control effector.
        """
        if pm.objExists(ctrl):
            pm.select(ctrl)
            mel.eval(f"hikCustomRigAssignEffector {ctrl_id};")

    def add_hip_ctrl(self, ctrl: str, ctrl_id: int = HUMAN_IK_CTRL_MAP["Hip"]) -> None:
        """Add the hip control to the rig.

        Args:
            ctrl: Name of the hip control.
            ctrl_id: ID of the hip control effector.
        """
        self.add_ctrl(ctrl, ctrl_id)

    def add_spine_ctrl(
        self, ctrl_list: list[str], ctrl_id_list: tuple[int, ...] = HUMAN_IK_CTRL_MAP["Spine"]
    ) -> None:
        """Add spine controls to the rig.

        Args:
            ctrl_list: List of spine control names.
            ctrl_id_list: Tuple of spine control effector IDs.
        """
        for i, ctrl in enumerate(ctrl_list):
            self.add_ctrl(ctrl, ctrl_id_list[i])

    def add_chest_ctrl(self, ctrl: str, ctrl_id: int = HUMAN_IK_CTRL_MAP["Chest"]) -> None:
        """Add the chest control to the rig.

        Args:
            ctrl: Name of the chest control.
            ctrl_id: ID of the chest control effector.
        """
        self.add_ctrl(ctrl, ctrl_id)

    def add_neck_ctrl(self, ctrl: str, ctrl_id: int = HUMAN_IK_CTRL_MAP["Neck"]) -> None:
        """Add the neck control to the rig.

        Args:
            ctrl: Name of the neck control.
            ctrl_id: ID of the neck control effector.
        """
        self.add_ctrl(ctrl, ctrl_id)

    def add_head_ctrl(self, ctrl: str, ctrl_id: int = HUMAN_IK_CTRL_MAP["Head"]) -> None:
        """Add the head control to the rig.

        Args:
            ctrl: Name of the head control.
            ctrl_id: ID of the head control effector.
        """
        self.add_ctrl(ctrl, ctrl_id)

    def add_left_clavicle_ctrl(
        self, ctrl: str, ctrl_id: int = HUMAN_IK_CTRL_MAP["LeftClavicle"]
    ) -> None:
        """Add the left clavicle control to the rig.

        Args:
            ctrl: Name of the left clavicle control.
            ctrl_id: ID of the left clavicle control effector.
        """
        self.add_ctrl(ctrl, ctrl_id)

    def add_left_shoulder_ctrl(
        self, ctrl: str, ctrl_id: int = HUMAN_IK_CTRL_MAP["LeftShoulder"]
    ) -> None:
        """Add the left shoulder control to the rig.

        Args:
            ctrl: Name of the left shoulder control.
            ctrl_id: ID of the left shoulder control effector.
        """
        self.add_ctrl(ctrl, ctrl_id)

    def add_left_elbow_ctrl(
        self, ctrl: str, ctrl_id: int = HUMAN_IK_CTRL_MAP["LeftElbow"]
    ) -> None:
        """Add the left elbow control to the rig.

        Args:
            ctrl: Name of the left elbow control.
            ctrl_id: ID of the left elbow control effector.
        """
        self.add_ctrl(ctrl, ctrl_id)

    def add_left_hand_ctrl(
        self, ctrl: str, ctrl_id: int = HUMAN_IK_CTRL_MAP["LeftHand"]
    ) -> None:
        """Add the left hand control to the rig.

        Args:
            ctrl: Name of the left hand control.
            ctrl_id: ID of the left hand control effector.
        """
        self.add_ctrl(ctrl, ctrl_id)

    def add_left_hip_ctrl(
        self, ctrl: str, ctrl_id: int = HUMAN_IK_CTRL_MAP["LeftUpLeg"]
    ) -> None:
        """Add the left hip control to the rig.

        Args:
            ctrl: Name of the left hip control.
            ctrl_id: ID of the left hip control effector.
        """
        self.add_ctrl(ctrl, ctrl_id)

    def add_left_knee_ctrl(
        self, ctrl: str, ctrl_id: int = HUMAN_IK_CTRL_MAP["LeftKnee"]
    ) -> None:
        """Add the left knee control to the rig.

        Args:
            ctrl: Name of the left knee control.
            ctrl_id: ID of the left knee control effector.
        """
        self.add_ctrl(ctrl, ctrl_id)

    def add_left_ankle_ctrl(
        self, ctrl: str, ctrl_id: int = HUMAN_IK_CTRL_MAP["LeftAnkle"]
    ) -> None:
        """Add the left ankle control to the rig.

        Args:
            ctrl: Name of the left ankle control.
            ctrl_id: ID of the left ankle control effector.
        """
        self.add_ctrl(ctrl, ctrl_id)

    def add_right_clavicle_ctrl(
        self, ctrl: str, ctrl_id: int = HUMAN_IK_CTRL_MAP["RightClavicle"]
    ) -> None:
        """Add the right clavicle control to the rig.

        Args:
            ctrl: Name of the right clavicle control.
            ctrl_id: ID of the right clavicle control effector.
        """
        self.add_ctrl(ctrl, ctrl_id)

    def add_right_shoulder_ctrl(
        self, ctrl: str, ctrl_id: int = HUMAN_IK_CTRL_MAP["RightShoulder"]
    ) -> None:
        """Add the right shoulder control to the rig.

        Args:
            ctrl: Name of the right shoulder control.
            ctrl_id: ID of the right shoulder control effector.
        """
        self.add_ctrl(ctrl, ctrl_id)

    def add_right_elbow_ctrl(
        self, ctrl: str, ctrl_id: int = HUMAN_IK_CTRL_MAP["RightElbow"]
    ) -> None:
        """Add the right elbow control to the rig.

        Args:
            ctrl: Name of the right elbow control.
            ctrl_id: ID of the right elbow control effector.
        """
        self.add_ctrl(ctrl, ctrl_id)

    def add_right_hand_ctrl(
        self, ctrl: str, ctrl_id: int = HUMAN_IK_CTRL_MAP["RightHand"]
    ) -> None:
        """Add the right hand control to the rig.

        Args:
            ctrl: Name of the right hand control.
            ctrl_id: ID of the right hand control effector.
        """
        self.add_ctrl(ctrl, ctrl_id)

    def add_right_hip_ctrl(
        self, ctrl: str, ctrl_id: int = HUMAN_IK_CTRL_MAP["RightUpLeg"]
    ) -> None:
        """Add the right hip control to the rig.

        Args:
            ctrl: Name of the right hip control.
            ctrl_id: ID of the right hip control effector.
        """
        self.add_ctrl(ctrl, ctrl_id)

    def add_right_knee_ctrl(
        self, ctrl: str, ctrl_id: int = HUMAN_IK_CTRL_MAP["RightKnee"]
    ) -> None:
        """Add the right knee control to the rig.

        Args:
            ctrl: Name of the right knee control.
            ctrl_id: ID of the right knee control effector.
        """
        self.add_ctrl(ctrl, ctrl_id)

    def add_right_ankle_ctrl(
        self, ctrl: str, ctrl_id: int = HUMAN_IK_CTRL_MAP["RightAnkle"]
    ) -> None:
        """Add the right ankle control to the rig.

        Args:
            ctrl: Name of the right ankle control.
            ctrl_id: ID of the right ankle control effector.
        """
        self.add_ctrl(ctrl, ctrl_id)

    def add_left_hand_thumb_ctrl(
        self,
        ctrl_list: list[str],
        ctrl_id_list: tuple[int, ...] = HUMAN_IK_CTRL_MAP["LeftHandThumb"],
    ) -> None:
        """Add left hand thumb controls to the rig.

        Args:
            ctrl_list: List of left hand thumb control names.
            ctrl_id_list: Tuple of left hand thumb control effector IDs.
        """
        for i, ctrl in enumerate(ctrl_list):
            self.add_ctrl(ctrl, ctrl_id_list[i])

    def add_left_hand_index_ctrl(
        self,
        ctrl_list: list[str],
        ctrl_id_list: tuple[int, ...] = HUMAN_IK_CTRL_MAP["LeftHandIndex"],
    ) -> None:
        """Add left hand index controls to the rig.

        Args:
            ctrl_list: List of left hand index control names.
            ctrl_id_list: Tuple of left hand index control effector IDs.
        """
        for i, ctrl in enumerate(ctrl_list):
            self.add_ctrl(ctrl, ctrl_id_list[i])

    def add_left_hand_middle_ctrl(
        self,
        ctrl_list: list[str],
        ctrl_id_list: tuple[int, ...] = HUMAN_IK_CTRL_MAP["LeftHandMiddle"],
    ) -> None:
        """Add left hand middle controls to the rig.

        Args:
            ctrl_list: List of left hand middle control names.
            ctrl_id_list: Tuple of left hand middle control effector IDs.
        """
        for i, ctrl in enumerate(ctrl_list):
            self.add_ctrl(ctrl, ctrl_id_list[i])

    def add_left_hand_ring_ctrl(
        self,
        ctrl_list: list[str],
        ctrl_id_list: tuple[int, ...] = HUMAN_IK_CTRL_MAP["LeftHandRing"],
    ) -> None:
        """Add left hand ring controls to the rig.

        Args:
            ctrl_list: List of left hand ring control names.
            ctrl_id_list: Tuple of left hand ring control effector IDs.
        """
        for i, ctrl in enumerate(ctrl_list):
            self.add_ctrl(ctrl, ctrl_id_list[i])

    def add_left_hand_pinky_ctrl(
        self,
        ctrl_list: list[str],
        ctrl_id_list: tuple[int, ...] = HUMAN_IK_CTRL_MAP["LeftHandPinky"],
    ) -> None:
        """Add left hand pinky controls to the rig.

        Args:
            ctrl_list: List of left hand pinky control names.
            ctrl_id_list: Tuple of left hand pinky control effector IDs.
        """
        for i, ctrl in enumerate(ctrl_list):
            self.add_ctrl(ctrl, ctrl_id_list[i])

    def add_right_hand_thumb_ctrl(
        self,
        ctrl_list: list[str],
        ctrl_id_list: tuple[int, ...] = HUMAN_IK_CTRL_MAP["RightHandThumb"],
    ) -> None:
        """Add right hand thumb controls to the rig.

        Args:
            ctrl_list: List of right hand thumb control names.
            ctrl_id_list: Tuple of right hand thumb control effector IDs.
        """
        for i, ctrl in enumerate(ctrl_list):
            self.add_ctrl(ctrl, ctrl_id_list[i])

    def add_right_hand_index_ctrl(
        self,
        ctrl_list: list[str],
        ctrl_id_list: tuple[int, ...] = HUMAN_IK_CTRL_MAP["RightHandIndex"],
    ) -> None:
        """Add right hand index controls to the rig.

        Args:
            ctrl_list: List of right hand index control names.
            ctrl_id_list: Tuple of right hand index control effector IDs.
        """
        for i, ctrl in enumerate(ctrl_list):
            self.add_ctrl(ctrl, ctrl_id_list[i])

    def add_right_hand_middle_ctrl(
        self,
        ctrl_list: list[str],
        ctrl_id_list: tuple[int, ...] = HUMAN_IK_CTRL_MAP["RightHandMiddle"],
    ) -> None:
        """Add right hand middle controls to the rig.

        Args:
            ctrl_list: List of right hand middle control names.
            ctrl_id_list: Tuple of right hand middle control effector IDs.
        """
        for i, ctrl in enumerate(ctrl_list):
            self.add_ctrl(ctrl, ctrl_id_list[i])

    def add_right_hand_ring_ctrl(
        self,
        ctrl_list: list[str],
        ctrl_id_list: tuple[int, ...] = HUMAN_IK_CTRL_MAP["RightHandRing"],
    ) -> None:
        """Add right hand ring controls to the rig.

        Args:
            ctrl_list: List of right hand ring control names.
            ctrl_id_list: Tuple of right hand ring control effector IDs.
        """
        for i, ctrl in enumerate(ctrl_list):
            self.add_ctrl(ctrl, ctrl_id_list[i])

    def add_right_hand_pinky_ctrl(
        self,
        ctrl_list: list[str],
        ctrl_id_list: tuple[int, ...] = HUMAN_IK_CTRL_MAP["RightHandPinky"],
    ) -> None:
        """Add right hand pinky controls to the rig.

        Args:
            ctrl_list: List of right hand pinky control names.
            ctrl_id_list: Tuple of right hand pinky control effector IDs.
        """
        for i, ctrl in enumerate(ctrl_list):
            self.add_ctrl(ctrl, ctrl_id_list[i])

    def define_custom_ctrls(
        self, rig_data: dict, use_ik: bool = True, use_hybrid: bool = True
    ) -> None:
        """Define custom controls for the HumanIK rig.

        This is the main entry point for custom control definition. It processes
        the rig_data dictionary and calls the appropriate mapping methods for
        each control based on the IK/FK mode.

        Args:
            rig_data: Dictionary containing control mappings in ['ctrls'] key.
            use_ik: Whether to use IK controls.
            use_hybrid: Whether to use hybrid IK controls.
        """
        self.create_custom_rig_mapping()

        # Add hip control
        if rig_data["ctrls"]["Hip"]:
            self.add_hip_ctrl(rig_data["ctrls"]["Hip"])

        # Add spine control
        if rig_data["ctrls"]["Spine"]:
            self.add_spine_ctrl(rig_data["ctrls"]["Spine"])

        # Add chest control
        if rig_data["ctrls"]["Chest"]:
            self.add_chest_ctrl(rig_data["ctrls"]["Chest"])

        # Add neck control
        if rig_data["ctrls"]["Neck"]:
            self.add_neck_ctrl(rig_data["ctrls"]["Neck"])

        # Add head control
        if rig_data["ctrls"]["Head"]:
            self.add_head_ctrl(rig_data["ctrls"]["Head"])

        # Add left clavicle control
        if rig_data["ctrls"]["LeftClavicle"]:
            self.add_left_clavicle_ctrl(rig_data["ctrls"]["LeftClavicle"])

        # Add right clavicle control
        if rig_data["ctrls"]["RightClavicle"]:
            self.add_right_clavicle_ctrl(rig_data["ctrls"]["RightClavicle"])

        # Add left and right limb controls
        if not use_ik and not use_hybrid:
            # Add left and right shoulder controls
            if rig_data["ctrls"]["LeftShoulder"]:
                self.add_left_shoulder_ctrl(rig_data["ctrls"]["LeftShoulder"])
            if rig_data["ctrls"]["RightShoulder"]:
                self.add_right_shoulder_ctrl(rig_data["ctrls"]["RightShoulder"])

            # Add left and right elbow controls
            if rig_data["ctrls"]["LeftElbow"]:
                self.add_left_elbow_ctrl(rig_data["ctrls"]["LeftElbow"])
            if rig_data["ctrls"]["RightElbow"]:
                self.add_right_elbow_ctrl(rig_data["ctrls"]["RightElbow"])

            # Add left and right hand controls
            if rig_data["ctrls"]["LeftHand"][0]:
                self.add_left_hand_ctrl(rig_data["ctrls"]["LeftHand"][0])
            if rig_data["ctrls"]["RightHand"][0]:
                self.add_right_hand_ctrl(rig_data["ctrls"]["RightHand"][0])

            # Add left and right leg controls
            if rig_data["ctrls"]["LeftUpLeg"]:
                self.add_left_hip_ctrl(rig_data["ctrls"]["LeftUpLeg"])
            if rig_data["ctrls"]["LeftKnee"]:
                self.add_left_knee_ctrl(rig_data["ctrls"]["LeftKnee"])
            if rig_data["ctrls"]["LeftAnkle"][0]:
                self.add_left_ankle_ctrl(rig_data["ctrls"]["LeftAnkle"][0])

            if rig_data["ctrls"]["RightUpLeg"]:
                self.add_right_hip_ctrl(rig_data["ctrls"]["RightUpLeg"])
            if rig_data["ctrls"]["RightKnee"]:
                self.add_right_knee_ctrl(rig_data["ctrls"]["RightKnee"])
            if rig_data["ctrls"]["RightAnkle"][0]:
                self.add_right_ankle_ctrl(rig_data["ctrls"]["RightAnkle"][0])

        if use_ik and not use_hybrid:
            # Add left and right hand IK controls
            if rig_data["ctrls"]["LeftHand"][1]:
                self.add_left_hand_ctrl(rig_data["ctrls"]["LeftHand"][1])
            if rig_data["ctrls"]["RightHand"][1]:
                self.add_right_hand_ctrl(rig_data["ctrls"]["RightHand"][1])

            if rig_data["ctrls"]["LeftAnkle"][1]:
                self.add_left_ankle_ctrl(rig_data["ctrls"]["LeftAnkle"][1])
            if rig_data["ctrls"]["RightAnkle"][1]:
                self.add_right_ankle_ctrl(rig_data["ctrls"]["RightAnkle"][1])

        if use_hybrid:
            # Add left and right limb controls
            if rig_data["ctrls"]["LeftShoulder"]:
                self.add_left_shoulder_ctrl(rig_data["ctrls"]["LeftShoulder"])
            if rig_data["ctrls"]["RightShoulder"]:
                self.add_right_shoulder_ctrl(rig_data["ctrls"]["RightShoulder"])

            if rig_data["ctrls"]["LeftElbow"]:
                self.add_left_elbow_ctrl(rig_data["ctrls"]["LeftElbow"])
            if rig_data["ctrls"]["RightElbow"]:
                self.add_right_elbow_ctrl(rig_data["ctrls"]["RightElbow"])

            if rig_data["ctrls"]["LeftHand"][0]:
                self.add_left_hand_ctrl(rig_data["ctrls"]["LeftHand"][0])
            if rig_data["ctrls"]["RightHand"][0]:
                self.add_right_hand_ctrl(rig_data["ctrls"]["RightHand"][0])

            if rig_data["ctrls"]["LeftAnkle"][1]:
                self.add_left_ankle_ctrl(rig_data["ctrls"]["LeftAnkle"][1])

            if rig_data["ctrls"]["RightAnkle"][1]:
                self.add_right_ankle_ctrl(rig_data["ctrls"]["RightAnkle"][1])

        if rig_data["ctrls"]["LeftHandThumb"]:
            self.add_left_hand_thumb_ctrl(rig_data["ctrls"]["LeftHandThumb"])
        if rig_data["ctrls"]["RightHandThumb"]:
            self.add_right_hand_thumb_ctrl(rig_data["ctrls"]["RightHandThumb"])

        # Add left and right hand index controls
        if rig_data["ctrls"]["LeftHandIndex"]:
            self.add_left_hand_index_ctrl(rig_data["ctrls"]["LeftHandIndex"])
        if rig_data["ctrls"]["RightHandIndex"]:
            self.add_right_hand_index_ctrl(rig_data["ctrls"]["RightHandIndex"])

        # Add left and right hand middle controls
        if rig_data["ctrls"]["LeftHandMiddle"]:
            self.add_left_hand_middle_ctrl(rig_data["ctrls"]["LeftHandMiddle"])
        if rig_data["ctrls"]["RightHandMiddle"]:
            self.add_right_hand_middle_ctrl(rig_data["ctrls"]["RightHandMiddle"])

        # Add left and right hand ring controls
        if rig_data["ctrls"]["LeftHandRing"]:
            self.add_left_hand_ring_ctrl(rig_data["ctrls"]["LeftHandRing"])
        if rig_data["ctrls"]["RightHandRing"]:
            self.add_right_hand_ring_ctrl(rig_data["ctrls"]["RightHandRing"])

        # Add left and right hand pinky controls
        if rig_data["ctrls"]["LeftHandPinky"]:
            self.add_left_hand_pinky_ctrl(rig_data["ctrls"]["LeftHandPinky"])
        if rig_data["ctrls"]["RightHandPinky"]:
            self.add_right_hand_pinky_ctrl(rig_data["ctrls"]["RightHandPinky"])

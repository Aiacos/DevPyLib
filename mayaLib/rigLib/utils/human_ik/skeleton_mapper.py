"""Skeleton mapper for HumanIK joint mapping.

This module provides the SkeletonMapper class which handles all skeleton definition
and joint mapping operations for HumanIK characters. It maps Maya joints to HumanIK's
bone indices and provides convenience methods for common joint chains.
"""

from __future__ import annotations

from mayaLib.rigLib.utils.human_ik.constants import HUMAN_IK_JOINT_MAP
from mayaLib.rigLib.utils.human_ik.mel_interface import MelInterface


class SkeletonMapper:
    """Handles skeleton definition and joint mapping for HumanIK characters.

    This class provides methods to map Maya joints to HumanIK's skeleton definition.
    It wraps the MEL interface and provides semantic methods for each body part,
    making it easy to define complete character skeletons.

    Attributes:
        character_name (str): The name of the HumanIK character.
        mel_interface (MelInterface): MEL command wrapper for HumanIK operations.
    """

    def __init__(self, character_name: str):
        """Initialize the skeleton mapper for a HumanIK character.

        Args:
            character_name: The name of the HumanIK character to work with.
        """
        self.character_name = str(character_name)
        self.mel_interface = MelInterface(character_name)

    def set_character_object(self, joint: str, joint_id: int) -> None:
        """Assign a Maya joint to a HumanIK character slot.

        This is the core mapping function that delegates to the MEL interface.
        All other mapping methods use this internally.

        Args:
            joint: The name of the Maya joint.
            joint_id: The character object ID (HumanIK bone index).
        """
        self.mel_interface.set_character_object(joint, joint_id)

    def add_reference(self, joint: str, joint_id: int = HUMAN_IK_JOINT_MAP["Reference"]) -> None:
        """Add a reference joint to the character.

        The reference joint is the root of the HumanIK skeleton hierarchy.

        Args:
            joint: The name of the Maya joint.
            joint_id: The character object ID for the reference joint.
        """
        self.set_character_object(joint, joint_id)

    def add_hip(self, joint: str, joint_id: int = HUMAN_IK_JOINT_MAP["Hips"]) -> None:
        """Add a hip joint to the character.

        The hip joint is the pelvis/root of the character's center mass.

        Args:
            joint: The name of the Maya joint.
            joint_id: The character object ID for the hip joint.
        """
        self.set_character_object(joint, joint_id)

    def add_spine(
        self, joint_list: list[str], joint_id_list: tuple[int, ...] = HUMAN_IK_JOINT_MAP["Spine"]
    ) -> None:
        """Add a spine to the character.

        The spine is a chain of joints from pelvis to chest.

        Args:
            joint_list: A list of Maya joints that make up the spine.
            joint_id_list: A tuple of character object IDs, one for each joint in the spine.
        """
        for i, joint in enumerate(joint_list):
            self.set_character_object(joint, joint_id_list[i])

    def add_neck(
        self, joint_list: list[str], joint_id_list: tuple[int, ...] = HUMAN_IK_JOINT_MAP["Neck"]
    ) -> None:
        """Add a neck to the character.

        The neck is a chain of joints from the top of the spine to the head.

        Args:
            joint_list: A list of Maya joints that make up the neck.
            joint_id_list: A tuple of character object IDs, one for each joint in the neck.
        """
        for i, joint in enumerate(joint_list):
            self.set_character_object(joint, joint_id_list[i])

    def add_head(self, joint: str, joint_id: int = HUMAN_IK_JOINT_MAP["Head"]) -> None:
        """Add a head to the character.

        The head joint is the terminal joint of the neck chain.

        Args:
            joint: The name of the Maya joint.
            joint_id: The character object ID for the head joint.
        """
        self.set_character_object(joint, joint_id)

    def add_left_up_leg(self, joint: str, joint_id: int = HUMAN_IK_JOINT_MAP["LeftUpLeg"]) -> None:
        """Add left up leg to the character.

        The up leg is the thigh/femur joint.

        Args:
            joint: The name of the Maya joint.
            joint_id: The character object ID for the left up leg joint.
        """
        self.set_character_object(joint, joint_id)

    def add_left_leg_joint(self, joint: str, joint_id: int = HUMAN_IK_JOINT_MAP["LeftLeg"]) -> None:
        """Add a left leg to the character.

        The leg joint is the knee/shin joint.

        Args:
            joint: The name of the Maya joint.
            joint_id: The character object ID for the left leg joint.
        """
        self.set_character_object(joint, joint_id)

    def add_left_foot(self, joint: str, joint_id: int = HUMAN_IK_JOINT_MAP["LeftFoot"]) -> None:
        """Add the left foot joint to the character.

        The foot joint is the ankle joint.

        Args:
            joint: The name of the Maya joint.
            joint_id: The character object ID for the left foot joint.
        """
        self.set_character_object(joint, joint_id)

    def add_left_shoulder(
        self, joint: str, joint_id: int = HUMAN_IK_JOINT_MAP["LeftShoulder"]
    ) -> None:
        """Add the left shoulder joint to the character.

        The shoulder joint is the clavicle joint.

        Args:
            joint: The name of the Maya joint.
            joint_id: The character object ID for the left shoulder joint.
        """
        self.set_character_object(joint, joint_id)

    def add_left_arm_joint(self, joint: str, joint_id: int = HUMAN_IK_JOINT_MAP["LeftArm"]) -> None:
        """Add the left arm joint to the character.

        The arm joint is the upper arm/humerus joint.

        Args:
            joint: The name of the Maya joint.
            joint_id: The character object ID for the left arm joint.
        """
        self.set_character_object(joint, joint_id)

    def add_left_fore_arm(
        self, joint: str, joint_id: int = HUMAN_IK_JOINT_MAP["LeftForeArm"]
    ) -> None:
        """Add the left forearm joint to the character.

        The forearm joint is the elbow/lower arm joint.

        Args:
            joint: The name of the Maya joint.
            joint_id: The character object ID for the left forearm joint.
        """
        self.set_character_object(joint, joint_id)

    def add_left_hand_joint(
        self, joint: str, joint_id: int = HUMAN_IK_JOINT_MAP["LeftHand"]
    ) -> None:
        """Add the left hand joint to the character.

        The hand joint is the wrist joint.

        Args:
            joint: The name of the Maya joint.
            joint_id: The character object ID for the left hand joint.
        """
        self.set_character_object(joint, joint_id)

    def add_right_up_leg(
        self, joint: str, joint_id: int = HUMAN_IK_JOINT_MAP["RightUpLeg"]
    ) -> None:
        """Add the right up leg joint to the character.

        The up leg is the thigh/femur joint.

        Args:
            joint: The name of the Maya joint.
            joint_id: The character object ID for the right up leg joint.
        """
        self.set_character_object(joint, joint_id)

    def add_right_leg_joint(
        self, joint: str, joint_id: int = HUMAN_IK_JOINT_MAP["RightLeg"]
    ) -> None:
        """Add the right leg joint to the character.

        The leg joint is the knee/shin joint.

        Args:
            joint: The name of the Maya joint.
            joint_id: The character object ID for the right leg joint.
        """
        self.set_character_object(joint, joint_id)

    def add_right_foot(self, joint: str, joint_id: int = HUMAN_IK_JOINT_MAP["RightFoot"]) -> None:
        """Add the right foot joint to the character.

        The foot joint is the ankle joint.

        Args:
            joint: The name of the Maya joint.
            joint_id: The character object ID for the right foot joint.
        """
        self.set_character_object(joint, joint_id)

    def add_right_shoulder(
        self, joint: str, joint_id: int = HUMAN_IK_JOINT_MAP["RightShoulder"]
    ) -> None:
        """Add the right shoulder joint to the character.

        The shoulder joint is the clavicle joint.

        Args:
            joint: The name of the Maya joint.
            joint_id: The character object ID for the right shoulder joint.
        """
        self.set_character_object(joint, joint_id)

    def add_right_arm_joint(
        self, joint: str, joint_id: int = HUMAN_IK_JOINT_MAP["RightArm"]
    ) -> None:
        """Add the right arm joint to the character.

        The arm joint is the upper arm/humerus joint.

        Args:
            joint: The name of the Maya joint.
            joint_id: The character object ID for the right arm joint.
        """
        self.set_character_object(joint, joint_id)

    def add_right_fore_arm(
        self, joint: str, joint_id: int = HUMAN_IK_JOINT_MAP["RightForeArm"]
    ) -> None:
        """Add the right forearm joint to the character.

        The forearm joint is the elbow/lower arm joint.

        Args:
            joint: The name of the Maya joint.
            joint_id: The character object ID for the right forearm joint.
        """
        self.set_character_object(joint, joint_id)

    def add_right_hand(self, joint: str, joint_id: int = HUMAN_IK_JOINT_MAP["RightHand"]) -> None:
        """Add the right hand joint to the character.

        The hand joint is the wrist joint.

        Args:
            joint: The name of the Maya joint.
            joint_id: The character object ID for the right hand joint.
        """
        self.set_character_object(joint, joint_id)

    def add_left_toe_base(
        self, joint: str, joint_id: int = HUMAN_IK_JOINT_MAP["LeftToeBase"]
    ) -> None:
        """Add the left toe base joint to the character.

        The toe base is the ball of the foot joint.

        Args:
            joint: The name of the Maya joint.
            joint_id: The character object ID for the left toe base joint.
        """
        self.set_character_object(joint, joint_id)

    def add_right_toe_base(
        self, joint: str, joint_id: int = HUMAN_IK_JOINT_MAP["RightToeBase"]
    ) -> None:
        """Add the right toe base joint to the character.

        The toe base is the ball of the foot joint.

        Args:
            joint: The name of the Maya joint.
            joint_id: The character object ID for the right toe base joint.
        """
        self.set_character_object(joint, joint_id)

    def add_left_hand_thumb(
        self,
        joint_list: list[str],
        joint_id_list: tuple[int, ...] = HUMAN_IK_JOINT_MAP["LeftHandThumb"],
    ) -> None:
        """Add the left hand thumb joints to the character.

        Args:
            joint_list: Maya joints that form the left hand thumb.
            joint_id_list: HumanIK IDs for the left hand thumb joints.
        """
        for i, joint in enumerate(joint_list):
            self.set_character_object(joint, joint_id_list[i])

    def add_left_hand_index(
        self,
        joint_list: list[str],
        joint_id_list: tuple[int, ...] = HUMAN_IK_JOINT_MAP["LeftHandIndex"],
    ) -> None:
        """Add the left hand index joints to the character.

        Args:
            joint_list: Maya joints that form the left hand index finger.
            joint_id_list: HumanIK IDs for the left hand index joints.
        """
        for i, joint in enumerate(joint_list):
            self.set_character_object(joint, joint_id_list[i])

    def add_left_hand_middle(
        self,
        joint_list: list[str],
        joint_id_list: tuple[int, ...] = HUMAN_IK_JOINT_MAP["LeftHandMiddle"],
    ) -> None:
        """Add the left hand middle joints to the character.

        Args:
            joint_list: Maya joints that form the left hand middle finger.
            joint_id_list: HumanIK IDs for the left hand middle joints.
        """
        for i, joint in enumerate(joint_list):
            self.set_character_object(joint, joint_id_list[i])

    def add_left_hand_ring(
        self,
        joint_list: list[str],
        joint_id_list: tuple[int, ...] = HUMAN_IK_JOINT_MAP["LeftHandRing"],
    ) -> None:
        """Add the left hand ring joints to the character.

        Args:
            joint_list: Maya joints that form the left hand ring finger.
            joint_id_list: HumanIK IDs for the left hand ring joints.
        """
        for i, joint in enumerate(joint_list):
            self.set_character_object(joint, joint_id_list[i])

    def add_left_hand_pinky(
        self,
        joint_list: list[str],
        joint_id_list: tuple[int, ...] = HUMAN_IK_JOINT_MAP["LeftHandPinky"],
    ) -> None:
        """Add the left hand pinky joints to the character.

        Args:
            joint_list: Maya joints that form the left hand pinky finger.
            joint_id_list: HumanIK IDs for the left hand pinky joints.
        """
        for i, joint in enumerate(joint_list):
            self.set_character_object(joint, joint_id_list[i])

    def add_right_hand_thumb(
        self,
        joint_list: list[str],
        joint_id_list: tuple[int, ...] = HUMAN_IK_JOINT_MAP["RightHandThumb"],
    ) -> None:
        """Add the right hand thumb joints to the character.

        Args:
            joint_list: Maya joints that form the right hand thumb.
            joint_id_list: HumanIK IDs for the right hand thumb joints.
        """
        for i, joint in enumerate(joint_list):
            self.set_character_object(joint, joint_id_list[i])

    def add_right_hand_index(
        self,
        joint_list: list[str],
        joint_id_list: tuple[int, ...] = HUMAN_IK_JOINT_MAP["RightHandIndex"],
    ) -> None:
        """Add the right hand index joints to the character.

        Args:
            joint_list: Maya joints that form the right hand index finger.
            joint_id_list: HumanIK IDs for the right hand index joints.
        """
        for i, joint in enumerate(joint_list):
            self.set_character_object(joint, joint_id_list[i])

    def add_right_hand_middle(
        self,
        joint_list: list[str],
        joint_id_list: tuple[int, ...] = HUMAN_IK_JOINT_MAP["RightHandMiddle"],
    ) -> None:
        """Add the right hand middle joints to the character.

        Args:
            joint_list: Maya joints that form the right hand middle finger.
            joint_id_list: HumanIK IDs for the right hand middle joints.
        """
        for i, joint in enumerate(joint_list):
            self.set_character_object(joint, joint_id_list[i])

    def add_right_hand_ring(
        self,
        joint_list: list[str],
        joint_id_list: tuple[int, ...] = HUMAN_IK_JOINT_MAP["RightHandRing"],
    ) -> None:
        """Add the right hand ring joints to the character.

        Args:
            joint_list: Maya joints that form the right hand ring finger.
            joint_id_list: HumanIK IDs for the right hand ring joints.
        """
        for i, joint in enumerate(joint_list):
            self.set_character_object(joint, joint_id_list[i])

    def add_right_hand_pinky(
        self,
        joint_list: list[str],
        joint_id_list: tuple[int, ...] = HUMAN_IK_JOINT_MAP["RightHandPinky"],
    ) -> None:
        """Add the right hand pinky joints to the character.

        Args:
            joint_list: A list of Maya joints for the right hand pinky.
            joint_id_list: A tuple of character object IDs for the right hand pinky joints.
        """
        for i, joint in enumerate(joint_list):
            self.set_character_object(joint, joint_id_list[i])

    def add_left_arm(
        self,
        clavicle: str | None = None,
        shoulder: str | None = None,
        forearm: str | None = None,
        hand: str | None = None,
    ) -> None:
        """Add the left arm components to the character.

        Convenience method to add all left arm joints at once.

        Args:
            clavicle: The clavicle joint name.
            shoulder: The shoulder joint name.
            forearm: The forearm joint name.
            hand: The hand joint name.
        """
        if clavicle:
            self.add_left_shoulder(clavicle)
        if shoulder:
            self.add_left_arm_joint(shoulder)
        if forearm:
            self.add_left_fore_arm(forearm)
        if hand:
            self.add_left_hand_joint(hand)

    def add_right_arm(
        self,
        clavicle: str | None = None,
        shoulder: str | None = None,
        forearm: str | None = None,
        hand: str | None = None,
    ) -> None:
        """Add the right arm components to the character.

        Convenience method to add all right arm joints at once.

        Args:
            clavicle: The clavicle joint name.
            shoulder: The shoulder joint name.
            forearm: The forearm joint name.
            hand: The hand joint name.
        """
        if clavicle:
            self.add_right_shoulder(clavicle)
        if shoulder:
            self.add_right_arm_joint(shoulder)
        if forearm:
            self.add_right_fore_arm(forearm)
        if hand:
            self.add_right_hand(hand)

    def add_left_leg(
        self,
        upper_leg: str | None = None,
        leg: str | None = None,
        foot: str | None = None,
        ball: str | None = None,
    ) -> None:
        """Add the left leg components to the character.

        Convenience method to add all left leg joints at once.

        Args:
            upper_leg: The upper leg joint name.
            leg: The leg joint name.
            foot: The foot joint name.
            ball: The ball joint name.
        """
        if upper_leg:
            self.add_left_up_leg(upper_leg)
        if leg:
            self.add_left_leg_joint(leg)
        if foot:
            self.add_left_foot(foot)
        if ball:
            self.add_left_toe_base(ball)

    def add_right_leg(
        self,
        upper_leg: str | None = None,
        leg: str | None = None,
        foot: str | None = None,
        ball: str | None = None,
    ) -> None:
        """Add the right leg components to the character.

        Convenience method to add all right leg joints at once.

        Args:
            upper_leg: The upper leg joint name.
            leg: The leg joint name.
            foot: The foot joint name.
            ball: The ball joint name.
        """
        if upper_leg:
            self.add_right_up_leg(upper_leg)
        if leg:
            self.add_right_leg_joint(leg)
        if foot:
            self.add_right_foot(foot)
        if ball:
            self.add_right_toe_base(ball)

    def define_skeleton(self, rig_data: dict, skip_reference_joint: bool = True) -> None:
        """Define the skeleton with the given rig data.

        This is the main entry point for skeleton definition. It processes the rig_data
        dictionary and calls the appropriate mapping methods for each joint.

        Args:
            rig_data: The rig data dictionary containing joint mappings.
            skip_reference_joint: Whether to skip the reference joint.
        """
        # Add reference joint if it exists
        if rig_data["joints"]["Reference"] and not skip_reference_joint:
            self.add_reference(rig_data["joints"]["Reference"])

        # Add hip joint
        if rig_data["joints"]["Hips"]:
            self.add_hip(rig_data["joints"]["Hips"])

        # Add spine joints
        if rig_data["joints"]["Spine"]:
            self.add_spine(rig_data["joints"]["Spine"])

        # Add neck joint
        if rig_data["joints"]["Neck"]:
            self.add_neck(rig_data["joints"]["Neck"])

        # Add head joint
        if rig_data["joints"]["Head"]:
            self.add_head(rig_data["joints"]["Head"])

        # Add left arm joints
        if rig_data["joints"]["LeftArm"]:
            self.add_left_arm(*rig_data["joints"]["LeftArm"])

        # Add left leg joints
        if rig_data["joints"]["LeftLeg"]:
            self.add_left_leg(*rig_data["joints"]["LeftLeg"])

        # Add right arm joints
        if rig_data["joints"]["RightArm"]:
            self.add_right_arm(*rig_data["joints"]["RightArm"])

        # Add right leg joints
        if rig_data["joints"]["RightLeg"]:
            self.add_right_leg(*rig_data["joints"]["RightLeg"])

        # Add left hand thumb joints
        if rig_data["joints"]["LeftHandThumb"]:
            self.add_left_hand_thumb(rig_data["joints"]["LeftHandThumb"])

        # Add left hand index joints
        if rig_data["joints"]["LeftHandIndex"]:
            self.add_left_hand_index(rig_data["joints"]["LeftHandIndex"])

        # Add left hand middle joints
        if rig_data["joints"]["LeftHandMiddle"]:
            self.add_left_hand_middle(rig_data["joints"]["LeftHandMiddle"])

        # Add left hand ring joints
        if rig_data["joints"]["LeftHandRing"]:
            self.add_left_hand_ring(rig_data["joints"]["LeftHandRing"])

        # Add left hand pinky joints
        if rig_data["joints"]["LeftHandPinky"]:
            self.add_left_hand_pinky(rig_data["joints"]["LeftHandPinky"])

        # Add right hand thumb joints
        if rig_data["joints"]["RightHandThumb"]:
            self.add_right_hand_thumb(rig_data["joints"]["RightHandThumb"])

        # Add right hand index joints
        if rig_data["joints"]["RightHandIndex"]:
            self.add_right_hand_index(rig_data["joints"]["RightHandIndex"])

        # Add right hand middle joints
        if rig_data["joints"]["RightHandMiddle"]:
            self.add_right_hand_middle(rig_data["joints"]["RightHandMiddle"])

        # Add right hand ring joints
        if rig_data["joints"]["RightHandRing"]:
            self.add_right_hand_ring(rig_data["joints"]["RightHandRing"])

        # Add right hand pinky joints
        if rig_data["joints"]["RightHandPinky"]:
            self.add_right_hand_pinky(rig_data["joints"]["RightHandPinky"])

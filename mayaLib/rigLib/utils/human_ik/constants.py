"""Constants for HumanIK rigging system.

This module contains joint and control name defaults, HumanIK mapping indices,
and rig template data used throughout the HumanIK framework.
"""

# =============================================================================
# Default Joint Names
# =============================================================================

REFERENCE_JOINT_DEFAULT = "Base_main_FS_jnt"
"""Default reference joint name for HumanIK skeleton definition."""

HIP_JOINT_DEFAULT = "M_Spine_pelvis_FS_jnt"
"""Default hip joint name."""

SPINE_JOINT_LIST_DEFAULT = [
    "M_Spine_ribbon_driven_0_FS_jnt",
    "M_Spine_ribbon_driven_1_FS_jnt",
    "M_Spine_ribbon_driven_2_FS_jnt",
    "M_Spine_chest_FS_jnt",
]
"""Default spine joint chain."""

NECK_JOINT_LIST_DEFAULT = [
    "M_Head_neck_root_FS_jnt",
    "M_Head_ribbon_driven_0_FS_jnt",
    "M_Head_ribbon_driven_1_FS_jnt",
    "M_Head_ribbon_driven_2_FS_jnt",
]
"""Default neck joint chain."""

HEAD_JOINT_DEFAULT = "M_Head_head_FS_jnt"
"""Default head joint name."""

LEFT_ARM_JOINT_LIST_DEFAULT = [
    "L_Arm_base_FS_jnt",
    "L_Arm_upper_ribbon_driven_0_FS_jnt",
    "L_Arm_lower_ribbon_driven_0_FS_jnt",
    "L_Arm_tip_FS_jnt",
]
"""Default left arm joint chain."""

LEFT_LEG_JOINT_LIST_DEFAULT = [
    "L_Leg_upper_ribbon_driven_0_FS_jnt",
    "L_Leg_lower_ribbon_driven_0_FS_jnt",
    "L_Leg_tip_FS_jnt",
    "L_Leg_toes_root_FS_jnt",
]
"""Default left leg joint chain."""

RIGHT_ARM_JOINT_LIST_DEFAULT = [
    "R_Arm_base_FS_jnt",
    "R_Arm_upper_ribbon_driven_0_FS_jnt",
    "R_Arm_lower_ribbon_driven_0_FS_jnt",
    "R_Arm_tip_FS_jnt",
]
"""Default right arm joint chain."""

RIGHT_LEG_JOINT_LIST_DEFAULT = [
    "R_Leg_upper_ribbon_driven_0_FS_jnt",
    "R_Leg_lower_ribbon_driven_0_FS_jnt",
    "R_Leg_tip_FS_jnt",
    "R_Leg_toes_root_FS_jnt",
]
"""Default right leg joint chain."""

LEFT_HAND_THUMB_JOINT_LIST_DEFAULT = [
    "L_Fingers_thumb_0_0_FS_jnt",
    "L_Fingers_thumb_0_1_FS_jnt",
    "L_Fingers_thumb_0_2_FS_jnt",
]
"""Default left thumb joint chain."""

LEFT_HAND_INDEX_JOINT_LIST_DEFAULT = [
    "L_Fingers_finger_0_0_FS_jnt",
    "L_Fingers_finger_0_1_FS_jnt",
    "L_Fingers_finger_0_2_FS_jnt",
    "L_Fingers_finger_0_3_FS_jnt",
]
"""Default left index finger joint chain."""

LEFT_HAND_MIDDLE_JOINT_LIST_DEFAULT = [
    "L_Fingers_finger_1_0_FS_jnt",
    "L_Fingers_finger_1_1_FS_jnt",
    "L_Fingers_finger_1_2_FS_jnt",
    "L_Fingers_finger_1_3_FS_jnt",
]
"""Default left middle finger joint chain."""

LEFT_HAND_RING_JOINT_LIST_DEFAULT = [
    "L_Fingers_finger_2_0_FS_jnt",
    "L_Fingers_finger_2_1_FS_jnt",
    "L_Fingers_finger_2_2_FS_jnt",
    "L_Fingers_finger_2_3_FS_jnt",
]
"""Default left ring finger joint chain."""

LEFT_HAND_PINKY_JOINT_LIST_DEFAULT = [
    "L_Fingers_finger_3_0_FS_jnt",
    "L_Fingers_finger_3_1_FS_jnt",
    "L_Fingers_finger_3_2_FS_jnt",
    "L_Fingers_finger_3_3_FS_jnt",
]
"""Default left pinky finger joint chain."""

RIGHT_HAND_THUMB_JOINT_LIST_DEFAULT = [
    "R_Fingers_thumb_0_0_FS_jnt",
    "R_Fingers_thumb_0_1_FS_jnt",
    "R_Fingers_thumb_0_2_FS_jnt",
]
"""Default right thumb joint chain."""

RIGHT_HAND_INDEX_JOINT_LIST_DEFAULT = [
    "R_Fingers_finger_0_0_FS_jnt",
    "R_Fingers_finger_0_1_FS_jnt",
    "R_Fingers_finger_0_2_FS_jnt",
    "R_Fingers_finger_0_3_FS_jnt",
]
"""Default right index finger joint chain."""

RIGHT_HAND_MIDDLE_JOINT_LIST_DEFAULT = [
    "R_Fingers_finger_1_0_FS_jnt",
    "R_Fingers_finger_1_1_FS_jnt",
    "R_Fingers_finger_1_2_FS_jnt",
    "R_Fingers_finger_1_3_FS_jnt",
]
"""Default right middle finger joint chain."""

RIGHT_HAND_RING_JOINT_LIST_DEFAULT = [
    "R_Fingers_finger_2_0_FS_jnt",
    "R_Fingers_finger_2_1_FS_jnt",
    "R_Fingers_finger_2_2_FS_jnt",
    "R_Fingers_finger_2_3_FS_jnt",
]
"""Default right ring finger joint chain."""

RIGHT_HAND_PINKY_JOINT_LIST_DEFAULT = [
    "R_Fingers_finger_3_0_FS_jnt",
    "R_Fingers_finger_3_1_FS_jnt",
    "R_Fingers_finger_3_2_FS_jnt",
    "R_Fingers_finger_3_3_FS_jnt",
]
"""Default right pinky finger joint chain."""


# =============================================================================
# Default Control Names
# =============================================================================

HIP_CTRL_DEFAULT = "M_Spine_cog_ctrl"
"""Default hip control name."""

SPINE_CTRL_LIST_DEFAULT = ["M_Spine_base_ctrl", "M_Spine_ik_0_ctrl"]
"""Default spine control chain."""

CHEST_CTRL_DEFAULT = "M_Spine_ik_chest_ctrl"
"""Default chest control name."""

NECK_CTRL_DEFAULT = "M_Head_neck_root_ctrl"
"""Default neck control name."""

HEAD_CTRL_DEFAULT = "M_Head_head_ctrl"
"""Default head control name."""

LEFT_CLAVICLE_CTRL_DEFAULT = "L_Arm_base_ctrl"
"""Default left clavicle control name."""

LEFT_SHOULDER_CTRL_DEFAULT = "L_Arm_fk_root_ctrl"
"""Default left shoulder control name."""

LEFT_ELBOW_CTRL_DEFAULT = "L_Arm_fk_mid_ctrl"
"""Default left elbow control name."""

LEFT_HAND_FK_CTRL_DEFAULT = "L_Arm_fk_tip_ctrl"
"""Default left hand FK control name."""

LEFT_HAND_IK_CTRL_DEFAULT = "L_Arm_ik_tip_ctrl"
"""Default left hand IK control name."""

RIGHT_CLAVICLE_CTRL_DEFAULT = "R_Arm_base_ctrl"
"""Default right clavicle control name."""

RIGHT_SHOULDER_CTRL_DEFAULT = "R_Arm_fk_root_ctrl"
"""Default right shoulder control name."""

RIGHT_ELBOW_CTRL_DEFAULT = "R_Arm_fk_mid_ctrl"
"""Default right elbow control name."""

RIGHT_HAND_FK_CTRL_DEFAULT = "R_Arm_fk_tip_ctrl"
"""Default right hand FK control name."""

RIGHT_HAND_IK_CTRL_DEFAULT = "R_Arm_ik_tip_ctrl"
"""Default right hand IK control name."""

LEFT_HIP_CTRL_DEFAULT = "L_Leg_fk_root_ctrl"
"""Default left hip control name."""

LEFT_KNEE_CTRL_DEFAULT = "L_Leg_fk_mid_ctrl"
"""Default left knee control name."""

LEFT_ANKLE_FK_CTRL_DEFAULT = "L_Leg_fk_tip_ctrl"
"""Default left ankle FK control name."""

LEFT_ANKLE_IK_CTRL_DEFAULT = "L_Leg_ik_tip_ctrl"
"""Default left ankle IK control name."""

RIGHT_HIP_CTRL_DEFAULT = "R_Leg_fk_root_ctrl"
"""Default right hip control name."""

RIGHT_KNEE_CTRL_DEFAULT = "R_Leg_fk_mid_ctrl"
"""Default right knee control name."""

RIGHT_ANKLE_FK_CTRL_DEFAULT = "R_Leg_fk_tip_ctrl"
"""Default right ankle FK control name."""

RIGHT_ANKLE_IK_CTRL_DEFAULT = "R_Leg_ik_tip_ctrl"
"""Default right ankle IK control name."""

LEFT_HAND_THUMB_CTRL_LIST_DEFAULT = [
    "L_Fingers_thumb_0_0_ctrl",
    "L_Fingers_thumb_0_1_ctrl",
    "L_Fingers_thumb_0_2_ctrl",
]
"""Default left thumb control chain."""

LEFT_HAND_INDEX_CTRL_LIST_DEFAULT = [
    "L_Fingers_finger_0_0_ctrl",
    "L_Fingers_finger_0_1_ctrl",
    "L_Fingers_finger_0_2_ctrl",
    "L_Fingers_finger_0_3_ctrl",
]
"""Default left index finger control chain."""

LEFT_HAND_MIDDLE_CTRL_LIST_DEFAULT = [
    "L_Fingers_finger_1_0_ctrl",
    "L_Fingers_finger_1_1_ctrl",
    "L_Fingers_finger_1_2_ctrl",
    "L_Fingers_finger_1_3_ctrl",
]
"""Default left middle finger control chain."""

LEFT_HAND_RING_CTRL_LIST_DEFAULT = [
    "L_Fingers_finger_2_0_ctrl",
    "L_Fingers_finger_2_1_ctrl",
    "L_Fingers_finger_2_2_ctrl",
    "L_Fingers_finger_2_3_ctrl",
]
"""Default left ring finger control chain."""

LEFT_HAND_PINKY_CTRL_LIST_DEFAULT = [
    "L_Fingers_finger_3_0_ctrl",
    "L_Fingers_finger_3_1_ctrl",
    "L_Fingers_finger_3_2_ctrl",
    "L_Fingers_finger_3_3_ctrl",
]
"""Default left pinky finger control chain."""

RIGHT_HAND_THUMB_CTRL_LIST_DEFAULT = [
    "R_Fingers_thumb_0_0_ctrl",
    "R_Fingers_thumb_0_1_ctrl",
    "R_Fingers_thumb_0_2_ctrl",
]
"""Default right thumb control chain."""

RIGHT_HAND_INDEX_CTRL_LIST_DEFAULT = [
    "R_Fingers_finger_0_0_ctrl",
    "R_Fingers_finger_0_1_ctrl",
    "R_Fingers_finger_0_2_ctrl",
    "R_Fingers_finger_0_3_ctrl",
]
"""Default right index finger control chain."""

RIGHT_HAND_MIDDLE_CTRL_LIST_DEFAULT = [
    "R_Fingers_finger_1_0_ctrl",
    "R_Fingers_finger_1_1_ctrl",
    "R_Fingers_finger_1_2_ctrl",
    "R_Fingers_finger_1_3_ctrl",
]
"""Default right middle finger control chain."""

RIGHT_HAND_RING_CTRL_LIST_DEFAULT = [
    "R_Fingers_finger_2_0_ctrl",
    "R_Fingers_finger_2_1_ctrl",
    "R_Fingers_finger_2_2_ctrl",
    "R_Fingers_finger_2_3_ctrl",
]
"""Default right ring finger control chain."""

RIGHT_HAND_PINKY_CTRL_LIST_DEFAULT = [
    "R_Fingers_finger_3_0_ctrl",
    "R_Fingers_finger_3_1_ctrl",
    "R_Fingers_finger_3_2_ctrl",
    "R_Fingers_finger_3_3_ctrl",
]
"""Default right pinky finger control chain."""


# =============================================================================
# HumanIK Mapping Indices
# =============================================================================

HUMAN_IK_JOINT_MAP = {
    "Reference": 0,
    "Hips": 1,
    "Spine": (8, 23, 24, 25, 26, 27, 28, 29, 30, 31),
    "Neck": (20, 32, 33, 34, 35, 36, 37, 38, 39, 40),
    "Head": 15,
    "LeftUpLeg": 2,
    "LeftLeg": 3,
    "LeftFoot": 4,
    "LeftToeBase": 16,
    "RightUpLeg": 5,
    "RightLeg": 6,
    "RightFoot": 7,
    "RightToeBase": 17,
    "LeftShoulder": 18,
    "LeftArm": 9,
    "LeftForeArm": 10,
    "LeftHand": 11,
    "RightShoulder": 19,
    "RightArm": 12,
    "RightForeArm": 13,
    "RightHand": 14,
    "LeftHandThumb": (50, 51, 52),
    "LeftHandIndex": (147, 54, 55, 56),
    "LeftHandMiddle": (148, 58, 59, 60),
    "LeftHandRing": (149, 62, 63, 64),
    "LeftHandPinky": (150, 66, 67, 68),
    "RightHandThumb": (74, 75, 76),
    "RightHandIndex": (153, 78, 79, 80),
    "RightHandMiddle": (154, 82, 83, 84),
    "RightHandRing": (155, 86, 87, 88),
    "RightHandPinky": (156, 90, 91, 92),
}
"""Mapping of HumanIK bone names to Maya's HumanIK joint indices.

Each key represents a bone/joint name in HumanIK nomenclature, and the value
is either a single integer index or a tuple of indices for chains (spine, fingers, etc.).
"""

HUMAN_IK_CTRL_MAP = {
    "Hip": 1,
    "Spine": (8, 23, 24, 25, 26),
    "Chest": 1000,
    "Neck": 20,
    "Head": 15,
    "LeftClavicle": 18,
    "LeftShoulder": 9,
    "LeftElbow": 10,
    "LeftHand": 11,
    "RightClavicle": 19,
    "RightShoulder": 12,
    "RightElbow": 13,
    "RightHand": 14,
    "LeftUpLeg": 2,
    "LeftKnee": 3,
    "LeftAnkle": 4,
    "RightUpLeg": 5,
    "RightKnee": 6,
    "RightAnkle": 7,
    "LeftHandThumb": (50, 51, 52),
    "LeftHandIndex": (147, 54, 55, 56),
    "LeftHandMiddle": (148, 58, 59, 60),
    "LeftHandRing": (149, 62, 63, 64),
    "LeftHandPinky": (150, 66, 67, 68),
    "RightHandThumb": (74, 75, 76),
    "RightHandIndex": (153, 78, 79, 80),
    "RightHandMiddle": (154, 82, 83, 84),
    "RightHandRing": (155, 86, 87, 88),
    "RightHandPinky": (156, 90, 91, 92),
}
"""Mapping of HumanIK control names to Maya's HumanIK control indices.

Similar to HUMAN_IK_JOINT_MAP but for control rig mapping.
Note: Chest uses index 1000 as a special marker for custom handling.
"""

"""Rig template data for HumanIK system.

This module contains predefined joint and control mappings for different
rig systems (Arise, Rokoko, Advanced Skeleton) to HumanIK skeleton.
These templates define the relationship between rig-specific naming
conventions and HumanIK's standardized bone structure.
"""

from .constants import (
    # Joint name constants
    REFERENCE_JOINT_DEFAULT,
    HIP_JOINT_DEFAULT,
    SPINE_JOINT_LIST_DEFAULT,
    NECK_JOINT_LIST_DEFAULT,
    HEAD_JOINT_DEFAULT,
    LEFT_LEG_JOINT_LIST_DEFAULT,
    RIGHT_LEG_JOINT_LIST_DEFAULT,
    LEFT_ARM_JOINT_LIST_DEFAULT,
    RIGHT_ARM_JOINT_LIST_DEFAULT,
    LEFT_HAND_THUMB_JOINT_LIST_DEFAULT,
    LEFT_HAND_INDEX_JOINT_LIST_DEFAULT,
    LEFT_HAND_MIDDLE_JOINT_LIST_DEFAULT,
    LEFT_HAND_RING_JOINT_LIST_DEFAULT,
    LEFT_HAND_PINKY_JOINT_LIST_DEFAULT,
    RIGHT_HAND_THUMB_JOINT_LIST_DEFAULT,
    RIGHT_HAND_INDEX_JOINT_LIST_DEFAULT,
    RIGHT_HAND_MIDDLE_JOINT_LIST_DEFAULT,
    RIGHT_HAND_RING_JOINT_LIST_DEFAULT,
    RIGHT_HAND_PINKY_JOINT_LIST_DEFAULT,
    # Control name constants
    HIP_CTRL_DEFAULT,
    SPINE_CTRL_LIST_DEFAULT,
    CHEST_CTRL_DEFAULT,
    NECK_CTRL_DEFAULT,
    HEAD_CTRL_DEFAULT,
    LEFT_CLAVICLE_CTRL_DEFAULT,
    LEFT_SHOULDER_CTRL_DEFAULT,
    LEFT_ELBOW_CTRL_DEFAULT,
    LEFT_HAND_FK_CTRL_DEFAULT,
    LEFT_HAND_IK_CTRL_DEFAULT,
    RIGHT_CLAVICLE_CTRL_DEFAULT,
    RIGHT_SHOULDER_CTRL_DEFAULT,
    RIGHT_ELBOW_CTRL_DEFAULT,
    RIGHT_HAND_FK_CTRL_DEFAULT,
    RIGHT_HAND_IK_CTRL_DEFAULT,
    LEFT_HIP_CTRL_DEFAULT,
    LEFT_KNEE_CTRL_DEFAULT,
    LEFT_ANKLE_FK_CTRL_DEFAULT,
    LEFT_ANKLE_IK_CTRL_DEFAULT,
    RIGHT_HIP_CTRL_DEFAULT,
    RIGHT_KNEE_CTRL_DEFAULT,
    RIGHT_ANKLE_FK_CTRL_DEFAULT,
    RIGHT_ANKLE_IK_CTRL_DEFAULT,
    LEFT_HAND_THUMB_CTRL_LIST_DEFAULT,
    LEFT_HAND_INDEX_CTRL_LIST_DEFAULT,
    LEFT_HAND_MIDDLE_CTRL_LIST_DEFAULT,
    LEFT_HAND_RING_CTRL_LIST_DEFAULT,
    LEFT_HAND_PINKY_CTRL_LIST_DEFAULT,
    RIGHT_HAND_THUMB_CTRL_LIST_DEFAULT,
    RIGHT_HAND_INDEX_CTRL_LIST_DEFAULT,
    RIGHT_HAND_MIDDLE_CTRL_LIST_DEFAULT,
    RIGHT_HAND_RING_CTRL_LIST_DEFAULT,
    RIGHT_HAND_PINKY_CTRL_LIST_DEFAULT,
)


# =============================================================================
# Arise Rig Template
# =============================================================================

ARISE_HIK_DATA = {
    "joints": {
        "Reference": REFERENCE_JOINT_DEFAULT,
        "Hips": HIP_JOINT_DEFAULT,
        "Spine": SPINE_JOINT_LIST_DEFAULT,
        "Neck": NECK_JOINT_LIST_DEFAULT,
        "Head": HEAD_JOINT_DEFAULT,
        "LeftLeg": LEFT_LEG_JOINT_LIST_DEFAULT,
        "RightLeg": RIGHT_LEG_JOINT_LIST_DEFAULT,
        "LeftArm": LEFT_ARM_JOINT_LIST_DEFAULT,
        "RightArm": RIGHT_ARM_JOINT_LIST_DEFAULT,
        "LeftHandThumb": LEFT_HAND_THUMB_JOINT_LIST_DEFAULT,
        "LeftHandIndex": LEFT_HAND_INDEX_JOINT_LIST_DEFAULT,
        "LeftHandMiddle": LEFT_HAND_MIDDLE_JOINT_LIST_DEFAULT,
        "LeftHandRing": LEFT_HAND_RING_JOINT_LIST_DEFAULT,
        "LeftHandPinky": LEFT_HAND_PINKY_JOINT_LIST_DEFAULT,
        "RightHandThumb": RIGHT_HAND_THUMB_JOINT_LIST_DEFAULT,
        "RightHandIndex": RIGHT_HAND_INDEX_JOINT_LIST_DEFAULT,
        "RightHandMiddle": RIGHT_HAND_MIDDLE_JOINT_LIST_DEFAULT,
        "RightHandRing": RIGHT_HAND_RING_JOINT_LIST_DEFAULT,
        "RightHandPinky": RIGHT_HAND_PINKY_JOINT_LIST_DEFAULT,
    },
    "ctrls": {
        "Hip": HIP_CTRL_DEFAULT,
        "Spine": SPINE_CTRL_LIST_DEFAULT,
        "Chest": CHEST_CTRL_DEFAULT,
        "Neck": NECK_CTRL_DEFAULT,
        "Head": HEAD_CTRL_DEFAULT,
        "LeftClavicle": LEFT_CLAVICLE_CTRL_DEFAULT,
        "LeftShoulder": LEFT_SHOULDER_CTRL_DEFAULT,
        "LeftElbow": LEFT_ELBOW_CTRL_DEFAULT,
        "LeftHand": [
            LEFT_HAND_FK_CTRL_DEFAULT,
            LEFT_HAND_IK_CTRL_DEFAULT,
        ],
        "RightClavicle": RIGHT_CLAVICLE_CTRL_DEFAULT,
        "RightShoulder": RIGHT_SHOULDER_CTRL_DEFAULT,
        "RightElbow": RIGHT_ELBOW_CTRL_DEFAULT,
        "RightHand": [
            RIGHT_HAND_FK_CTRL_DEFAULT,
            RIGHT_HAND_IK_CTRL_DEFAULT,
        ],
        "LeftUpLeg": LEFT_HIP_CTRL_DEFAULT,
        "LeftKnee": LEFT_KNEE_CTRL_DEFAULT,
        "LeftAnkle": [
            LEFT_ANKLE_FK_CTRL_DEFAULT,
            LEFT_ANKLE_IK_CTRL_DEFAULT,
        ],
        "RightUpLeg": RIGHT_HIP_CTRL_DEFAULT,
        "RightKnee": RIGHT_KNEE_CTRL_DEFAULT,
        "RightAnkle": [
            RIGHT_ANKLE_FK_CTRL_DEFAULT,
            RIGHT_ANKLE_IK_CTRL_DEFAULT,
        ],
        "LeftHandThumb": LEFT_HAND_THUMB_CTRL_LIST_DEFAULT,
        "LeftHandIndex": LEFT_HAND_INDEX_CTRL_LIST_DEFAULT,
        "LeftHandMiddle": LEFT_HAND_MIDDLE_CTRL_LIST_DEFAULT,
        "LeftHandRing": LEFT_HAND_RING_CTRL_LIST_DEFAULT,
        "LeftHandPinky": LEFT_HAND_PINKY_CTRL_LIST_DEFAULT,
        "RightHandThumb": RIGHT_HAND_THUMB_CTRL_LIST_DEFAULT,
        "RightHandIndex": RIGHT_HAND_INDEX_CTRL_LIST_DEFAULT,
        "RightHandMiddle": RIGHT_HAND_MIDDLE_CTRL_LIST_DEFAULT,
        "RightHandRing": RIGHT_HAND_RING_CTRL_LIST_DEFAULT,
        "RightHandPinky": RIGHT_HAND_PINKY_CTRL_LIST_DEFAULT,
    },
}
"""Template data for Arise rig system.

Maps Arise rig's joint and control naming conventions to HumanIK skeleton.
Contains two sections:
- 'joints': Mapping of HumanIK bone names to Arise joint names
- 'ctrls': Mapping of HumanIK bone names to Arise control names

Some controls (hands, ankles) have both FK and IK variants represented as lists.
"""


# =============================================================================
# Rokoko Rig Template
# =============================================================================

ROKOKO_HIK_DATA = {
    "joints": {
        "Reference": "",
        "Hips": "Hips",
        "Spine": ["Spine1", "Spine2", "Spine3", "Spine4"],
        "Neck": ["Neck"],
        "Head": "Head",
        "LeftLeg": ["LeftThigh", "LeftShin", "LeftFoot", "LeftToe"],
        "RightLeg": ["RightThigh", "RightShin", "RightFoot", "RightToe"],
        "LeftArm": ["LeftShoulder", "LeftArm", "LeftForeArm", "LeftHand"],
        "RightArm": ["RightShoulder", "RightArm", "RightForeArm", "RightHand"],
        "LeftHandThumb": [
            "LeftFinger1Metacarpal",
            "LeftFinger1Proximal",
            "LeftFinger1Distal",
        ],
        "LeftHandIndex": [
            "",
            "LeftFinger2Proximal",
            "LeftFinger2Medial",
            "LeftFinger2Distal",
        ],
        "LeftHandMiddle": [
            "",
            "LeftFinger3Proximal",
            "LeftFinger3Medial",
            "LeftFinger3Distal",
        ],
        "LeftHandRing": [
            "",
            "LeftFinger4Proximal",
            "LeftFinger4Medial",
            "LeftFinger4Distal",
        ],
        "LeftHandPinky": [
            "",
            "LeftFinger5Proximal",
            "LeftFinger5Medial",
            "LeftFinger5Distal",
        ],
        "RightHandThumb": [
            "RightFinger1Metacarpal",
            "RightFinger1Proximal",
            "RightFinger1Distal",
        ],
        "RightHandIndex": [
            "",
            "RightFinger2Proximal",
            "RightFinger2Medial",
            "RightFinger2Distal",
        ],
        "RightHandMiddle": [
            "",
            "RightFinger3Proximal",
            "RightFinger3Medial",
            "RightFinger3Distal",
        ],
        "RightHandRing": [
            "",
            "RightFinger4Proximal",
            "RightFinger4Medial",
            "RightFinger4Distal",
        ],
        "RightHandPinky": [
            "",
            "RightFinger5Proximal",
            "RightFinger5Medial",
            "RightFinger5Distal",
        ],
    },
}
"""Template data for Rokoko mocap rig system.

Maps Rokoko's joint naming conventions to HumanIK skeleton.
Only contains joint mappings (no controls) as Rokoko is primarily
a motion capture system.

Note: Empty strings ("") indicate optional/missing joints in the hierarchy.
"""


# =============================================================================
# Advanced Skeleton Rig Template
# =============================================================================

ADVANCED_SKELETON_DATA = {
    "joints": {
        "Reference": "",
        "Hips": "Hips",
        "Spine": ["Spine1", "Spine2", "Spine3", "Spine4"],
        "Neck": ["Neck"],
        "Head": "Head",
        "LeftLeg": ["LeftThigh", "LeftShin", "LeftFoot", "LeftToe"],
        "RightLeg": ["RightThigh", "RightShin", "RightFoot", "RightToe"],
        "LeftArm": ["LeftShoulder", "LeftArm", "LeftForeArm", "LeftHand"],
        "RightArm": ["RightShoulder", "RightArm", "RightForeArm", "RightHand"],
        "LeftHandThumb": [
            "LeftFinger1Metacarpal",
            "LeftFinger1Proximal",
            "LeftFinger1Distal",
        ],
        "LeftHandIndex": [
            "",
            "LeftFinger2Proximal",
            "LeftFinger2Medial",
            "LeftFinger2Distal",
        ],
        "LeftHandMiddle": [
            "",
            "LeftFinger3Proximal",
            "LeftFinger3Medial",
            "LeftFinger3Distal",
        ],
        "LeftHandRing": [
            "",
            "LeftFinger4Proximal",
            "LeftFinger4Medial",
            "LeftFinger4Distal",
        ],
        "LeftHandPinky": [
            "",
            "LeftFinger5Proximal",
            "LeftFinger5Medial",
            "LeftFinger5Distal",
        ],
        "RightHandThumb": [
            "RightFinger1Metacarpal",
            "RightFinger1Proximal",
            "RightFinger1Distal",
        ],
        "RightHandIndex": [
            "",
            "RightFinger2Proximal",
            "RightFinger2Medial",
            "RightFinger2Distal",
        ],
        "RightHandMiddle": [
            "",
            "RightFinger3Proximal",
            "RightFinger3Medial",
            "RightFinger3Distal",
        ],
        "RightHandRing": [
            "",
            "RightFinger4Proximal",
            "RightFinger4Medial",
            "RightFinger4Distal",
        ],
        "RightHandPinky": [
            "",
            "RightFinger5Proximal",
            "RightFinger5Medial",
            "RightFinger5Distal",
        ],
    },
}
"""Template data for Advanced Skeleton rig system.

Maps Advanced Skeleton's joint naming conventions to HumanIK skeleton.
Only contains joint mappings (no controls).

Note: Empty strings ("") indicate optional/missing joints in the hierarchy.
The naming convention matches Rokoko as both use similar standardized joint names.
"""

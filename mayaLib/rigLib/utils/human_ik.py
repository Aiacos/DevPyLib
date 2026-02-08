"""HumanIK helper for mapping joints and controls to Maya's HumanIK system."""

from __future__ import annotations

import importlib
import os
import platform
import sys
from pathlib import Path

import pymel.core as pm
from maya import mel

from mayaLib.rigLib.utils import joint as joint_utils

# pylint: disable=too-many-instance-attributes,too-many-arguments,too-many-positional-arguments
# pylint: disable=too-many-locals,too-many-branches,too-many-lines

REFERENCE_JOINT_DEFAULT = "Base_main_FS_jnt"
HIP_JOINT_DEFAULT = "M_Spine_pelvis_FS_jnt"
SPINE_JOINT_LIST_DEFAULT = [
    "M_Spine_ribbon_driven_0_FS_jnt",
    "M_Spine_ribbon_driven_1_FS_jnt",
    "M_Spine_ribbon_driven_2_FS_jnt",
    "M_Spine_chest_FS_jnt",
]
NECK_JOINT_LIST_DEFAULT = [
    "M_Head_neck_root_FS_jnt",
    "M_Head_ribbon_driven_0_FS_jnt",
    "M_Head_ribbon_driven_1_FS_jnt",
    "M_Head_ribbon_driven_2_FS_jnt",
]
HEAD_JOINT_DEFAULT = "M_Head_head_FS_jnt"
LEFT_ARM_JOINT_LIST_DEFAULT = [
    "L_Arm_base_FS_jnt",
    "L_Arm_upper_ribbon_driven_0_FS_jnt",
    "L_Arm_lower_ribbon_driven_0_FS_jnt",
    "L_Arm_tip_FS_jnt",
]
LEFT_LEG_JOINT_LIST_DEFAULT = [
    "L_Leg_upper_ribbon_driven_0_FS_jnt",
    "L_Leg_lower_ribbon_driven_0_FS_jnt",
    "L_Leg_tip_FS_jnt",
    "L_Leg_toes_root_FS_jnt",
]
RIGHT_ARM_JOINT_LIST_DEFAULT = [
    "R_Arm_base_FS_jnt",
    "R_Arm_upper_ribbon_driven_0_FS_jnt",
    "R_Arm_lower_ribbon_driven_0_FS_jnt",
    "R_Arm_tip_FS_jnt",
]
RIGHT_LEG_JOINT_LIST_DEFAULT = [
    "R_Leg_upper_ribbon_driven_0_FS_jnt",
    "R_Leg_lower_ribbon_driven_0_FS_jnt",
    "R_Leg_tip_FS_jnt",
    "R_Leg_toes_root_FS_jnt",
]
LEFT_HAND_THUMB_JOINT_LIST_DEFAULT = [
    "L_Fingers_thumb_0_0_FS_jnt",
    "L_Fingers_thumb_0_1_FS_jnt",
    "L_Fingers_thumb_0_2_FS_jnt",
]
LEFT_HAND_INDEX_JOINT_LIST_DEFAULT = [
    "L_Fingers_finger_0_0_FS_jnt",
    "L_Fingers_finger_0_1_FS_jnt",
    "L_Fingers_finger_0_2_FS_jnt",
    "L_Fingers_finger_0_3_FS_jnt",
]
LEFT_HAND_MIDDLE_JOINT_LIST_DEFAULT = [
    "L_Fingers_finger_1_0_FS_jnt",
    "L_Fingers_finger_1_1_FS_jnt",
    "L_Fingers_finger_1_2_FS_jnt",
    "L_Fingers_finger_1_3_FS_jnt",
]
LEFT_HAND_RING_JOINT_LIST_DEFAULT = [
    "L_Fingers_finger_2_0_FS_jnt",
    "L_Fingers_finger_2_1_FS_jnt",
    "L_Fingers_finger_2_2_FS_jnt",
    "L_Fingers_finger_2_3_FS_jnt",
]
LEFT_HAND_PINKY_JOINT_LIST_DEFAULT = [
    "L_Fingers_finger_3_0_FS_jnt",
    "L_Fingers_finger_3_1_FS_jnt",
    "L_Fingers_finger_3_2_FS_jnt",
    "L_Fingers_finger_3_3_FS_jnt",
]

RIGHT_HAND_THUMB_JOINT_LIST_DEFAULT = [
    "R_Fingers_thumb_0_0_FS_jnt",
    "R_Fingers_thumb_0_1_FS_jnt",
    "R_Fingers_thumb_0_2_FS_jnt",
]
RIGHT_HAND_INDEX_JOINT_LIST_DEFAULT = [
    "R_Fingers_finger_0_0_FS_jnt",
    "R_Fingers_finger_0_1_FS_jnt",
    "R_Fingers_finger_0_2_FS_jnt",
    "R_Fingers_finger_0_3_FS_jnt",
]
RIGHT_HAND_MIDDLE_JOINT_LIST_DEFAULT = [
    "R_Fingers_finger_1_0_FS_jnt",
    "R_Fingers_finger_1_1_FS_jnt",
    "R_Fingers_finger_1_2_FS_jnt",
    "R_Fingers_finger_1_3_FS_jnt",
]
RIGHT_HAND_RING_JOINT_LIST_DEFAULT = [
    "R_Fingers_finger_2_0_FS_jnt",
    "R_Fingers_finger_2_1_FS_jnt",
    "R_Fingers_finger_2_2_FS_jnt",
    "R_Fingers_finger_2_3_FS_jnt",
]
RIGHT_HAND_PINKY_JOINT_LIST_DEFAULT = [
    "R_Fingers_finger_3_0_FS_jnt",
    "R_Fingers_finger_3_1_FS_jnt",
    "R_Fingers_finger_3_2_FS_jnt",
    "R_Fingers_finger_3_3_FS_jnt",
]

HIP_CTRL_DEFAULT = "M_Spine_cog_ctrl"
SPINE_CTRL_LIST_DEFAULT = ["M_Spine_base_ctrl", "M_Spine_ik_0_ctrl"]
CHEST_CTRL_DEFAULT = "M_Spine_ik_chest_ctrl"
NECK_CTRL_DEFAULT = "M_Head_neck_root_ctrl"
HEAD_CTRL_DEFAULT = "M_Head_head_ctrl"
LEFT_CLAVICLE_CTRL_DEFAULT = "L_Arm_base_ctrl"
LEFT_SHOULDER_CTRL_DEFAULT = "L_Arm_fk_root_ctrl"
LEFT_ELBOW_CTRL_DEFAULT = "L_Arm_fk_mid_ctrl"
LEFT_HAND_FK_CTRL_DEFAULT = "L_Arm_fk_tip_ctrl"
LEFT_HAND_IK_CTRL_DEFAULT = "L_Arm_ik_tip_ctrl"
RIGHT_CLAVICLE_CTRL_DEFAULT = "R_Arm_base_ctrl"
RIGHT_SHOULDER_CTRL_DEFAULT = "R_Arm_fk_root_ctrl"
RIGHT_ELBOW_CTRL_DEFAULT = "R_Arm_fk_mid_ctrl"
RIGHT_HAND_FK_CTRL_DEFAULT = "R_Arm_fk_tip_ctrl"
RIGHT_HAND_IK_CTRL_DEFAULT = "R_Arm_ik_tip_ctrl"
LEFT_HIP_CTRL_DEFAULT = "L_Leg_fk_root_ctrl"
LEFT_KNEE_CTRL_DEFAULT = "L_Leg_fk_mid_ctrl"
LEFT_ANKLE_FK_CTRL_DEFAULT = "L_Leg_fk_tip_ctrl"
LEFT_ANKLE_IK_CTRL_DEFAULT = "L_Leg_ik_tip_ctrl"
RIGHT_HIP_CTRL_DEFAULT = "R_Leg_fk_root_ctrl"
RIGHT_KNEE_CTRL_DEFAULT = "R_Leg_fk_mid_ctrl"
RIGHT_ANKLE_FK_CTRL_DEFAULT = "R_Leg_fk_tip_ctrl"
RIGHT_ANKLE_IK_CTRL_DEFAULT = "R_Leg_ik_tip_ctrl"

LEFT_HAND_THUMB_CTRL_LIST_DEFAULT = [
    "L_Fingers_thumb_0_0_ctrl",
    "L_Fingers_thumb_0_1_ctrl",
    "L_Fingers_thumb_0_2_ctrl",
]
LEFT_HAND_INDEX_CTRL_LIST_DEFAULT = [
    "L_Fingers_finger_0_0_ctrl",
    "L_Fingers_finger_0_1_ctrl",
    "L_Fingers_finger_0_2_ctrl",
    "L_Fingers_finger_0_3_ctrl",
]
LEFT_HAND_MIDDLE_CTRL_LIST_DEFAULT = [
    "L_Fingers_finger_1_0_ctrl",
    "L_Fingers_finger_1_1_ctrl",
    "L_Fingers_finger_1_2_ctrl",
    "L_Fingers_finger_1_3_ctrl",
]
LEFT_HAND_RING_CTRL_LIST_DEFAULT = [
    "L_Fingers_finger_2_0_ctrl",
    "L_Fingers_finger_2_1_ctrl",
    "L_Fingers_finger_2_2_ctrl",
    "L_Fingers_finger_2_3_ctrl",
]
LEFT_HAND_PINKY_CTRL_LIST_DEFAULT = [
    "L_Fingers_finger_3_0_ctrl",
    "L_Fingers_finger_3_1_ctrl",
    "L_Fingers_finger_3_2_ctrl",
    "L_Fingers_finger_3_3_ctrl",
]

RIGHT_HAND_THUMB_CTRL_LIST_DEFAULT = [
    "R_Fingers_thumb_0_0_ctrl",
    "R_Fingers_thumb_0_1_ctrl",
    "R_Fingers_thumb_0_2_ctrl",
]
RIGHT_HAND_INDEX_CTRL_LIST_DEFAULT = [
    "R_Fingers_finger_0_0_ctrl",
    "R_Fingers_finger_0_1_ctrl",
    "R_Fingers_finger_0_2_ctrl",
    "R_Fingers_finger_0_3_ctrl",
]
RIGHT_HAND_MIDDLE_CTRL_LIST_DEFAULT = [
    "R_Fingers_finger_1_0_ctrl",
    "R_Fingers_finger_1_1_ctrl",
    "R_Fingers_finger_1_2_ctrl",
    "R_Fingers_finger_1_3_ctrl",
]
RIGHT_HAND_RING_CTRL_LIST_DEFAULT = [
    "R_Fingers_finger_2_0_ctrl",
    "R_Fingers_finger_2_1_ctrl",
    "R_Fingers_finger_2_2_ctrl",
    "R_Fingers_finger_2_3_ctrl",
]
RIGHT_HAND_PINKY_CTRL_LIST_DEFAULT = [
    "R_Fingers_finger_3_0_ctrl",
    "R_Fingers_finger_3_1_ctrl",
    "R_Fingers_finger_3_2_ctrl",
    "R_Fingers_finger_3_3_ctrl",
]

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


class HumanIK:
    """Manage HumanIK mapping between Maya rigs and HumanIK."""

    # pylint: disable=too-many-public-methods

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

    RIG_DEFINITION = {
        "arise": ARISE_HIK_DATA,
        "rokoko": ROKOKO_HIK_DATA,
    }

    def __init__(
        self,
        character_name,
        rig_template="arise",
        auto_t_pose=True,
        custom_ctrl_definition=True,
        use_ik=True,
        use_hybrid=True,
        skip_reference_joint=True,
    ):
        """Initialize the HumanIK class.

        Args:
            character_name (str): The name of the character to be created.
            rig_template (str): The template of the rig data to be used. Available
                templates are 'arise' and 'rokoko'. Defaults to 'arise'.
            auto_t_pose (bool): Whether to go to T pose after initialization. Defaults to True.
            custom_ctrl_definition (bool): Whether to define custom controls. Defaults to True.
            use_ik (bool): Whether to use IK. Defaults to True.
            use_hybrid (bool): Whether to use hybrid IK. Defaults to True.
            skip_reference_joint (bool): Whether to skip the reference joint. Defaults to True.
        """
        self.character_name = str(character_name)

        # Set T Pose
        if auto_t_pose:
            self.go_to_t_pose(rig_template)

        # Init HumanIK Window
        mel.eval("HIKCharacterControlsTool;")

        # Create Character
        mel.eval(f'hikCreateCharacter("{self.character_name}")')

        # Select Rig Data
        self.rig_data = self.RIG_DEFINITION[rig_template]

        self.define_skeleton(self.rig_data, skip_reference_joint)

        if custom_ctrl_definition:
            self.define_custom_ctrls(self.rig_data, use_ik, use_hybrid)

    def _arise_t_pose(self) -> None:
        """Set the character to a T pose using the Arise plug-in utilities.

        Returns:
            None
        """
        # Get Maya plug-ins directory based on platform
        system = platform.system()
        if system == "Windows":
            maya_base = Path.home() / "Documents" / "maya"
        elif system == "Darwin":  # macOS
            maya_base = Path.home() / "Library" / "Preferences" / "Autodesk" / "maya"
        else:  # Linux
            maya_base = Path.home() / "maya"

        base_plugin_path = maya_base / "Plug-ins" / "arise_main"
        version_folder = f"py_{sys.version_info.major}_{sys.version_info.minor}"
        plugin_path = str(base_plugin_path / version_folder)

        if plugin_path not in sys.path:
            sys.path.append(plugin_path)

        try:
            arise_utils = importlib.import_module("arise.utils.ctrls_utils")
        except ImportError:
            pm.warning("Arise zero pose utilities not available; skipping T pose alignment.")
            return

        arise_utils.apply_zero_pose_all(silent=True)

    def _arms_parallel_to_grid(
        self,
        left_arm_transforms: list[str] | None = None,
        right_arm_transforms: list[str] | None = None,
    ) -> None:
        """Align arms parallel to the grid by adjusting their transforms.

        Args:
            left_arm_transforms: Optional sequence of transforms for the left arm.
            right_arm_transforms: Optional sequence of transforms for the right arm.

        Returns:
            None
        """
        left_arm_transforms = left_arm_transforms or [
            LEFT_CLAVICLE_CTRL_DEFAULT,
            LEFT_SHOULDER_CTRL_DEFAULT,
            LEFT_ELBOW_CTRL_DEFAULT,
            LEFT_HAND_FK_CTRL_DEFAULT,
        ]
        right_arm_transforms = right_arm_transforms or [
            RIGHT_CLAVICLE_CTRL_DEFAULT,
            RIGHT_SHOULDER_CTRL_DEFAULT,
            RIGHT_ELBOW_CTRL_DEFAULT,
            RIGHT_HAND_FK_CTRL_DEFAULT,
        ]
        joint_utils.set_arm_parallel_to_grid(left_arm_transforms)
        joint_utils.set_arm_parallel_to_grid(right_arm_transforms)

    def go_to_t_pose(self, template):
        """Sets the character to the T pose.

        Depending on the template provided, this function sets the character
        to the T pose using either the Arise plugin utilities or by aligning
        the arms parallel to the grid.

        Args:
            template (str): The name of the template used to determine the method
                for setting the T pose. Options are 'arise' or any other value
                to use the grid alignment method.

        Returns:
            None
        """
        if template == "arise":
            # Use Arise plugin utilities to set T pose
            self._arise_t_pose()
        else:
            # Set arms parallel to the grid
            self._arms_parallel_to_grid()

    def define_skeleton(self, rig_data=None, skip_reference_joint=True):
        """Define the skeleton with the given rig data.

        Args:
            rig_data (dict): The rig data to be used. Defaults to None.
            skip_reference_joint (bool): Whether to skip the reference joint. Defaults to True.
        """
        if not rig_data:
            rig_data = self.rig_data

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

    def define_custom_ctrls(self, rig_data, use_ik=True, use_hybrid=True):  # pylint: disable=too-many-statements
        """Define custom controls for the HumanIK rig.

        Args:
            rig_data (dict): A dictionary containing the rig data.
            use_ik (bool): Whether to use IK controls. Defaults to True.
            use_hybrid (bool): Whether to use hybrid IK controls. Defaults to True.

        """
        if not rig_data:
            rig_data = self.rig_data

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

    def set_character_object(self, joint, joint_id):
        """Assign a Maya joint to a HumanIK character slot.

        Args:
            joint (str): The name of the Maya joint.
            joint_id (int): The character object ID.

        Returns:
            None
        """
        if pm.objExists(joint):
            joint_name = str(pm.ls(joint)[-1].name())
            mel.eval(
                f'setCharacterObject("{joint_name}", "{self.character_name}", "{joint_id}", 0);'
            )

    def add_reference(self, joint, joint_id=HUMAN_IK_JOINT_MAP["Reference"]):
        """Add a reference joint to the character.

        Args:
            joint (str): The name of the Maya joint.
            joint_id (int): The character object ID for the reference joint.
        """
        # Set the character object for the reference joint
        self.set_character_object(joint, joint_id)

    def add_hip(self, joint, joint_id=HUMAN_IK_JOINT_MAP["Hips"]):
        """Add a hip joint to the character.

        Args:
            joint (str): The name of the Maya joint.
            joint_id (int): The character object ID for the hip joint.
        """
        # Set the character object for the hip joint
        self.set_character_object(joint, joint_id)

    def add_spine(self, joint_list, joint_id_list=HUMAN_IK_JOINT_MAP["Spine"]):
        """Add a spine to the character.

        Args:
            joint_list (list): A list of Maya joints that make up the spine.
            joint_id_list (list): A list of character object IDs, one for each joint in the spine.
        """
        # Iterate over the joint list and add each joint to the character
        for i, joint in enumerate(joint_list):
            # Set the character object for each joint in the spine
            self.set_character_object(joint, joint_id_list[i])

    def add_neck(self, joint_list, joint_id_list=HUMAN_IK_JOINT_MAP["Neck"]):
        """Add a neck to the character.

        Args:
            joint_list (list): A list of Maya joints that make up the neck.
            joint_id_list (list): A list of character object IDs, one for each joint in the neck.
        """
        # Iterate over the joint list and add each joint to the character
        for i, joint in enumerate(joint_list):
            # Set the character object for each joint in the neck
            self.set_character_object(joint, joint_id_list[i])

    def add_head(self, joint, joint_id=HUMAN_IK_JOINT_MAP["Head"]):
        """Add a head to the character.

        Args:
            joint (str): The name of the Maya joint.
            joint_id (int): The character object ID for the head joint.
        """
        # Set the character object for the head joint
        self.set_character_object(joint, joint_id)

    def add_left_up_leg(self, joint, joint_id=HUMAN_IK_JOINT_MAP["LeftUpLeg"]):
        """Add left up leg to the character.

        Args:
            joint (str): The name of the Maya joint.
            joint_id (int): The character object ID for the left up leg joint.

        Returns:
            None
        """
        # Set the character object for the left up leg joint
        self.set_character_object(joint, joint_id)

    def add_left_leg_joint(self, joint, joint_id=HUMAN_IK_JOINT_MAP["LeftLeg"]):
        """Add a left leg to the character.

        Args:
            joint (str): The name of the Maya joint.
            joint_id (int): The character object ID for the left leg joint.

        Returns:
            None
        """
        # Set the character object for the left leg joint
        self.set_character_object(joint, joint_id)

    def add_left_foot(self, joint, joint_id=HUMAN_IK_JOINT_MAP["LeftFoot"]):
        """Add the left foot joint to the character.

        Args:
            joint (str): The name of the Maya joint.
            joint_id (int): The character object ID for the left foot joint.

        Returns:
            None
        """
        self.set_character_object(joint, joint_id)

    def add_left_shoulder(self, joint, joint_id=HUMAN_IK_JOINT_MAP["LeftShoulder"]):
        """Add the left shoulder joint to the character.

        Args:
            joint (str): The name of the Maya joint.
            joint_id (int): The character object ID for the left shoulder joint.

        Returns:
            None
        """
        self.set_character_object(joint, joint_id)

    def add_left_arm_joint(self, joint, joint_id=HUMAN_IK_JOINT_MAP["LeftArm"]):
        """Add the left arm joint to the character.

        Args:
            joint (str): The name of the Maya joint.
            joint_id (int): The character object ID for the left arm joint.

        Returns:
            None
        """
        self.set_character_object(joint, joint_id)

    def add_left_fore_arm(self, joint, joint_id=HUMAN_IK_JOINT_MAP["LeftForeArm"]):
        """Add the left forearm joint to the character.

        Args:
            joint (str): The name of the Maya joint.
            joint_id (int): The character object ID for the left forearm joint.

        Returns:
            None
        """
        self.set_character_object(joint, joint_id)

    def add_left_hand_joint(self, joint, joint_id=HUMAN_IK_JOINT_MAP["LeftHand"]):
        """Add the left hand joint to the character.

        Args:
            joint (str): The name of the Maya joint.
            joint_id (int): The character object ID for the left hand joint.

        Returns:
            None
        """
        self.set_character_object(joint, joint_id)

    def add_right_up_leg(self, joint, joint_id=HUMAN_IK_JOINT_MAP["RightUpLeg"]):
        """Add the right up leg joint to the character.

        Args:
            joint (str): The name of the Maya joint.
            joint_id (int): The character object ID for the right up leg joint.

        Returns:
            None
        """
        self.set_character_object(joint, joint_id)

    def add_right_leg_joint(self, joint, joint_id=HUMAN_IK_JOINT_MAP["RightLeg"]):
        """Add the right leg joint to the character.

        Args:
            joint (str): The name of the Maya joint.
            joint_id (int): The character object ID for the right leg joint.

        Returns:
            None
        """
        self.set_character_object(joint, joint_id)

    def add_right_foot(self, joint, joint_id=HUMAN_IK_JOINT_MAP["RightFoot"]):
        """Add the right foot joint to the character.

        Args:
            joint (str): The name of the Maya joint.
            joint_id (int): The character object ID for the right foot joint.

        Returns:
            None
        """
        self.set_character_object(joint, joint_id)

    def add_right_shoulder(self, joint, joint_id=HUMAN_IK_JOINT_MAP["RightShoulder"]):
        """Add the right shoulder joint to the character.

        Args:
            joint (str): The name of the Maya joint.
            joint_id (int): The character object ID for the right shoulder joint.

        Returns:
            None
        """
        self.set_character_object(joint, joint_id)

    def add_right_arm_joint(self, joint, joint_id=HUMAN_IK_JOINT_MAP["RightArm"]):
        """Add the right arm joint to the character.

        Args:
            joint (str): The name of the Maya joint.
            joint_id (int): The character object ID for the right arm joint.

        Returns:
            None
        """
        self.set_character_object(joint, joint_id)

    def add_right_fore_arm(self, joint, joint_id=HUMAN_IK_JOINT_MAP["RightForeArm"]):
        """Add the right forearm joint to the character.

        Args:
            joint (str): The name of the Maya joint.
            joint_id (int): The character object ID for the right forearm joint.

        Returns:
            None
        """
        self.set_character_object(joint, joint_id)

    def add_right_hand(self, joint, joint_id=HUMAN_IK_JOINT_MAP["RightHand"]):
        """Add the right hand joint to the character.

        Args:
            joint (str): The name of the Maya joint.
            joint_id (int): The character object ID for the right hand joint.

        Returns:
            None
        """
        self.set_character_object(joint, joint_id)

    def add_left_toe_base(self, joint, joint_id=HUMAN_IK_JOINT_MAP["LeftToeBase"]):
        """Add the left toe base joint to the character.

        Args:
            joint (str): The name of the Maya joint.
            joint_id (int): The character object ID for the left toe base joint.

        Returns:
            None
        """
        self.set_character_object(joint, joint_id)

    def add_right_toe_base(self, joint, joint_id=HUMAN_IK_JOINT_MAP["RightToeBase"]):
        """Add the right toe base joint to the character.

        Args:
            joint (str): The name of the Maya joint.
            joint_id (int): The character object ID for the right toe base joint.

        Returns:
            None
        """
        self.set_character_object(joint, joint_id)

    def add_left_hand_thumb(self, joint_list, joint_id_list=HUMAN_IK_JOINT_MAP["LeftHandThumb"]):
        """Add the left hand thumb joints to the character.

        Args:
            joint_list (list): Maya joints that form the left hand thumb.
            joint_id_list (list): HumanIK IDs for the left hand thumb joints.

        Returns:
            None
        """
        for i, joint in enumerate(joint_list):
            self.set_character_object(joint, joint_id_list[i])

    def add_left_hand_index(self, joint_list, joint_id_list=HUMAN_IK_JOINT_MAP["LeftHandIndex"]):
        """Add the left hand index joints to the character.

        Args:
            joint_list (list): Maya joints that form the left hand index finger.
            joint_id_list (list): HumanIK IDs for the left hand index joints.

        Returns:
            None
        """
        for i, joint in enumerate(joint_list):
            self.set_character_object(joint, joint_id_list[i])

    def add_left_hand_middle(self, joint_list, joint_id_list=HUMAN_IK_JOINT_MAP["LeftHandMiddle"]):
        """Add the left hand middle joints to the character.

        Args:
            joint_list (list): Maya joints that form the left hand middle finger.
            joint_id_list (list): HumanIK IDs for the left hand middle joints.

        Returns:
            None
        """
        for i, joint in enumerate(joint_list):
            self.set_character_object(joint, joint_id_list[i])

    def add_left_hand_ring(self, joint_list, joint_id_list=HUMAN_IK_JOINT_MAP["LeftHandRing"]):
        """Add the left hand ring joints to the character.

        Args:
            joint_list (list): Maya joints that form the left hand ring finger.
            joint_id_list (list): HumanIK IDs for the left hand ring joints.

        Returns:
            None
        """
        for i, joint in enumerate(joint_list):
            self.set_character_object(joint, joint_id_list[i])

    def add_left_hand_pinky(self, joint_list, joint_id_list=HUMAN_IK_JOINT_MAP["LeftHandPinky"]):
        """Add the left hand pinky joints to the character.

        Args:
            joint_list (list): Maya joints that form the left hand pinky finger.
            joint_id_list (list): HumanIK IDs for the left hand pinky joints.

        Returns:
            None
        """
        for i, joint in enumerate(joint_list):
            self.set_character_object(joint, joint_id_list[i])

    def add_right_hand_thumb(self, joint_list, joint_id_list=HUMAN_IK_JOINT_MAP["RightHandThumb"]):
        """Add the right hand thumb joints to the character.

        Args:
            joint_list (list): Maya joints that form the right hand thumb.
            joint_id_list (list): HumanIK IDs for the right hand thumb joints.

        Returns:
            None
        """
        for i, joint in enumerate(joint_list):
            self.set_character_object(joint, joint_id_list[i])

    def add_right_hand_index(self, joint_list, joint_id_list=HUMAN_IK_JOINT_MAP["RightHandIndex"]):
        """Add the right hand index joints to the character.

        Args:
            joint_list (list): Maya joints that form the right hand index finger.
            joint_id_list (list): HumanIK IDs for the right hand index joints.

        Returns:
            None
        """
        for i, joint in enumerate(joint_list):
            self.set_character_object(joint, joint_id_list[i])

    def add_right_hand_middle(
        self,
        joint_list,
        joint_id_list=HUMAN_IK_JOINT_MAP["RightHandMiddle"],
    ):
        """Add the right hand middle joints to the character.

        Args:
            joint_list (list): Maya joints that form the right hand middle finger.
            joint_id_list (list): HumanIK IDs for the right hand middle joints.

        Returns:
            None
        """
        # Iterate over the joint list and assign character objects
        for i, joint in enumerate(joint_list):
            self.set_character_object(joint, joint_id_list[i])

    def add_right_hand_ring(self, joint_list, joint_id_list=HUMAN_IK_JOINT_MAP["RightHandRing"]):
        """Add the right hand ring joints to the character.

        Args:
            joint_list (list): Maya joints that form the right hand ring finger.
            joint_id_list (list): HumanIK IDs for the right hand ring joints.

        Returns:
            None
        """
        # Iterate over the joint list and assign character objects
        for i, joint in enumerate(joint_list):
            self.set_character_object(joint, joint_id_list[i])

    def add_right_hand_pinky(self, joint_list, joint_id_list=HUMAN_IK_JOINT_MAP["RightHandPinky"]):
        """Add the right hand pinky joints to the character.

        Args:
            joint_list (list): A list of Maya joints for the right hand pinky.
            joint_id_list (list): A list of character object IDs for the right hand pinky joints.
        """
        for i, joint in enumerate(joint_list):
            self.set_character_object(joint, joint_id_list[i])

    def add_left_arm(self, clavicle=None, shoulder=None, forearm=None, hand=None):
        """Add the left arm components to the character.

        Args:
            clavicle (str, optional): The clavicle joint name.
            shoulder (str, optional): The shoulder joint name.
            forearm (str, optional): The forearm joint name.
            hand (str, optional): The hand joint name.

        Returns:
            None
        """
        if clavicle:
            self.add_left_shoulder(clavicle)
        if shoulder:
            self.add_left_arm_joint(shoulder)
        if forearm:
            self.add_left_fore_arm(forearm)
        if hand:
            self.add_left_hand_joint(hand)

    def add_right_arm(self, clavicle=None, shoulder=None, forearm=None, hand=None):
        """Add the right arm components to the character.

        Args:
            clavicle (str, optional): The clavicle joint name.
            shoulder (str, optional): The shoulder joint name.
            forearm (str, optional): The forearm joint name.
            hand (str, optional): The hand joint name.

        Returns:
            None
        """
        if clavicle:
            self.add_right_shoulder(clavicle)
        if shoulder:
            self.add_right_arm_joint(shoulder)
        if forearm:
            self.add_right_fore_arm(forearm)
        if hand:
            self.add_right_hand(hand)

    def add_left_leg(self, upper_leg=None, leg=None, foot=None, ball=None):
        """Add the left leg components to the character.

        Args:
            upper_leg (str, optional): The upper leg joint name.
            leg (str, optional): The leg joint name.
            foot (str, optional): The foot joint name.
            ball (str, optional): The ball joint name.

        Returns:
            None
        """
        if upper_leg:
            self.add_left_up_leg(upper_leg)
        if leg:
            self.add_left_leg_joint(leg)
        if foot:
            self.add_left_foot(foot)
        if ball:
            self.add_left_toe_base(ball)

    def add_right_leg(self, upper_leg=None, leg=None, foot=None, ball=None):
        """Add the right leg components to the character.

        Args:
            upper_leg (str, optional): The upper leg joint name.
            leg (str, optional): The leg joint name.
            foot (str, optional): The foot joint name.
            ball (str, optional): The ball joint name.

        Returns:
            None
        """
        if upper_leg:
            self.add_right_up_leg(upper_leg)
        if leg:
            self.add_right_leg_joint(leg)
        if foot:
            self.add_right_foot(foot)
        if ball:
            self.add_right_toe_base(ball)

    def load_custom_rig_template(self):
        """Load the custom rig UI configuration using MEL."""
        mel.eval("hikLoadCustomRigUIConfiguration();")

    def create_custom_rig_mapping(self):
        """Create custom rig mapping for the current character using MEL."""
        mel.eval("hikCreateCustomRig( hikGetCurrentCharacter() );")

    def add_remove_custom_rig_mapping(self):
        """Add or remove custom rig mapping configuration.

        hikCustomRigAddRemoveMapping("R", `iconTextCheckBox - q - v hikCustomRigRotateButton` );

        import maya.app.hik.retargeter as r
        temporary = r.HIKRetargeter.createDefaultMapping(
            'HIKState2GlobalSK1',
            'Test',
            'RightInHandMiddle',
            'R_Fingers_finger_1_0_ctrl',
            'R',
            154,
            0,
        )
        # r.DefaultRetargeter.toGraph(temporary, 'HIKState2GlobalSK1')
        # del temporary
        """

    def add_ctrl(self, ctrl, ctrl_id):
        """Assigns a control to a custom rig effector.

        Args:
            ctrl (str): Name of the control.
            ctrl_id (int): ID of the control effector.
        """
        if pm.objExists(ctrl):
            pm.select(ctrl)
            mel.eval(f"hikCustomRigAssignEffector {ctrl_id};")

    def add_hip_ctrl(self, ctrl, ctrl_id=HUMAN_IK_CTRL_MAP["Hip"]):
        """Adds the hip control to the rig.

        Args:
            ctrl (str): Name of the hip control.
            ctrl_id (int): ID of the hip control effector.
        """
        self.add_ctrl(ctrl, ctrl_id)

    def add_spine_ctrl(self, ctrl_list, ctrl_id_list=HUMAN_IK_CTRL_MAP["Spine"]):
        """Adds spine controls to the rig.

        Args:
            ctrl_list (list): List of spine control names.
            ctrl_id_list (list): List of spine control effector IDs.
        """
        for i, ctrl in enumerate(ctrl_list):
            self.add_ctrl(ctrl, ctrl_id_list[i])

    def add_chest_ctrl(self, ctrl, ctrl_id=HUMAN_IK_CTRL_MAP["Chest"]):
        """Adds the chest control to the rig.

        Args:
            ctrl (str): Name of the chest control.
            ctrl_id (int): ID of the chest control effector.
        """
        self.add_ctrl(ctrl, ctrl_id)

    def add_neck_ctrl(self, ctrl, ctrl_id=HUMAN_IK_CTRL_MAP["Neck"]):
        """Adds the neck control to the rig.

        Args:
            ctrl (str): Name of the neck control.
            ctrl_id (int): ID of the neck control effector.
        """
        self.add_ctrl(ctrl, ctrl_id)

    def add_head_ctrl(self, ctrl, ctrl_id=HUMAN_IK_CTRL_MAP["Head"]):
        """Adds the head control to the rig.

        Args:
            ctrl (str): Name of the head control.
            ctrl_id (int): ID of the head control effector.
        """
        self.add_ctrl(ctrl, ctrl_id)

    def add_left_clavicle_ctrl(self, ctrl, ctrl_id=HUMAN_IK_CTRL_MAP["LeftClavicle"]):
        """Adds the left clavicle control to the rig.

        Args:
            ctrl (str): Name of the left clavicle control.
            ctrl_id (int): ID of the left clavicle control effector.
        """
        self.add_ctrl(ctrl, ctrl_id)

    def add_left_shoulder_ctrl(self, ctrl, ctrl_id=HUMAN_IK_CTRL_MAP["LeftShoulder"]):
        """Adds the left shoulder control to the rig.

        Args:
            ctrl (str): Name of the left shoulder control.
            ctrl_id (int): ID of the left shoulder control effector.
        """
        self.add_ctrl(ctrl, ctrl_id)

    def add_left_elbow_ctrl(self, ctrl, ctrl_id=HUMAN_IK_CTRL_MAP["LeftElbow"]):
        """Adds the left elbow control to the rig.

        Args:
            ctrl (str): Name of the left elbow control.
            ctrl_id (int): ID of the left elbow control effector.
        """
        self.add_ctrl(ctrl, ctrl_id)

    def add_left_hand_ctrl(self, ctrl, ctrl_id=HUMAN_IK_CTRL_MAP["LeftHand"]):
        """Adds the left hand control to the rig.

        Args:
            ctrl (str): Name of the left hand control.
            ctrl_id (int): ID of the left hand control effector.
        """
        self.add_ctrl(ctrl, ctrl_id)

    def add_left_hip_ctrl(self, ctrl, ctrl_id=HUMAN_IK_CTRL_MAP["LeftUpLeg"]):
        """Adds the left hip control to the rig.

        Args:
            ctrl (str): Name of the left hip control.
            ctrl_id (int): ID of the left hip control effector.
        """
        self.add_ctrl(ctrl, ctrl_id)

    def add_left_knee_ctrl(self, ctrl, ctrl_id=HUMAN_IK_CTRL_MAP["LeftKnee"]):
        """Adds the left knee control to the rig.

        Args:
            ctrl (str): Name of the left knee control.
            ctrl_id (int): ID of the left knee control effector.
        """
        self.add_ctrl(ctrl, ctrl_id)

    def add_left_ankle_ctrl(self, ctrl, ctrl_id=HUMAN_IK_CTRL_MAP["LeftAnkle"]):
        """Adds the left ankle control to the rig.

        Args:
            ctrl (str): Name of the left ankle control.
            ctrl_id (int): ID of the left ankle control effector.
        """
        self.add_ctrl(ctrl, ctrl_id)

    def add_right_clavicle_ctrl(self, ctrl, ctrl_id=HUMAN_IK_CTRL_MAP["RightClavicle"]):
        """Adds the right clavicle control to the rig.

        Args:
            ctrl (str): Name of the right clavicle control.
            ctrl_id (int): ID of the right clavicle control effector.
        """
        self.add_ctrl(ctrl, ctrl_id)

    def add_right_shoulder_ctrl(self, ctrl, ctrl_id=HUMAN_IK_CTRL_MAP["RightShoulder"]):
        """Adds the right shoulder control to the rig.

        Args:
            ctrl (str): Name of the right shoulder control.
            ctrl_id (int): ID of the right shoulder control effector.
        """
        self.add_ctrl(ctrl, ctrl_id)

    def add_right_elbow_ctrl(self, ctrl, ctrl_id=HUMAN_IK_CTRL_MAP["RightElbow"]):
        """Adds the right elbow control to the rig.

        Args:
            ctrl (str): Name of the right elbow control.
            ctrl_id (int): ID of the right elbow control effector.
        """
        self.add_ctrl(ctrl, ctrl_id)

    def add_right_hand_ctrl(self, ctrl, ctrl_id=HUMAN_IK_CTRL_MAP["RightHand"]):
        """Adds the right hand control to the rig.

        Args:
            ctrl (str): Name of the right hand control.
            ctrl_id (int): ID of the right hand control effector.
        """
        self.add_ctrl(ctrl, ctrl_id)

    def add_right_hip_ctrl(self, ctrl, ctrl_id=HUMAN_IK_CTRL_MAP["RightUpLeg"]):
        """Adds the right hip control to the rig.

        Args:
            ctrl (str): Name of the right hip control.
            ctrl_id (int): ID of the right hip control effector.
        """
        self.add_ctrl(ctrl, ctrl_id)

    def add_right_knee_ctrl(self, ctrl, ctrl_id=HUMAN_IK_CTRL_MAP["RightKnee"]):
        """Adds the right knee control to the rig.

        Args:
            ctrl (str): Name of the right knee control.
            ctrl_id (int): ID of the right knee control effector.
        """
        self.add_ctrl(ctrl, ctrl_id)

    def add_right_ankle_ctrl(self, ctrl, ctrl_id=HUMAN_IK_CTRL_MAP["RightAnkle"]):
        """Adds the right ankle control to the rig.

        Args:
            ctrl (str): Name of the right ankle control.
            ctrl_id (int): ID of the right ankle control effector.
        """
        self.add_ctrl(ctrl, ctrl_id)

    def add_left_hand_thumb_ctrl(self, ctrl_list, ctrl_id_list=HUMAN_IK_CTRL_MAP["LeftHandThumb"]):
        """Adds left hand thumb controls to the rig.

        Args:
            ctrl_list (list): List of left hand thumb control names.
            ctrl_id_list (list): List of left hand thumb control effector IDs.
        """
        for i, ctrl in enumerate(ctrl_list):
            self.add_ctrl(ctrl, ctrl_id_list[i])

    def add_left_hand_index_ctrl(
        self,
        ctrl_list,
        ctrl_id_list=HUMAN_IK_CTRL_MAP["LeftHandIndex"],
    ):
        """Adds left hand index controls to the rig.

        Args:
            ctrl_list (list): List of left hand index control names.
            ctrl_id_list (list): List of left hand index control effector IDs.
        """
        for i, ctrl in enumerate(ctrl_list):
            self.add_ctrl(ctrl, ctrl_id_list[i])

    def add_left_hand_middle_ctrl(
        self,
        ctrl_list,
        ctrl_id_list=HUMAN_IK_CTRL_MAP["LeftHandMiddle"],
    ):
        """Adds left hand middle controls to the rig.

        Args:
            ctrl_list (list): List of left hand middle control names.
            ctrl_id_list (list): List of left hand middle control effector IDs.
        """
        for i, ctrl in enumerate(ctrl_list):
            self.add_ctrl(ctrl, ctrl_id_list[i])

    def add_left_hand_ring_ctrl(
        self,
        ctrl_list,
        ctrl_id_list=HUMAN_IK_CTRL_MAP["LeftHandRing"],
    ):
        """Adds left hand ring controls to the rig.

        Args:
            ctrl_list (list): List of left hand ring control names.
            ctrl_id_list (list): List of left hand ring control effector IDs.
        """
        for i, ctrl in enumerate(ctrl_list):
            self.add_ctrl(ctrl, ctrl_id_list[i])

    def add_left_hand_pinky_ctrl(
        self,
        ctrl_list,
        ctrl_id_list=HUMAN_IK_CTRL_MAP["LeftHandPinky"],
    ):
        """Adds left hand pinky controls to the rig.

        Args:
            ctrl_list (list): List of left hand pinky control names.
            ctrl_id_list (list): List of left hand pinky control effector IDs.
        """
        for i, ctrl in enumerate(ctrl_list):
            self.add_ctrl(ctrl, ctrl_id_list[i])

    def add_right_hand_thumb_ctrl(
        self,
        ctrl_list,
        ctrl_id_list=HUMAN_IK_CTRL_MAP["RightHandThumb"],
    ):
        """Adds right hand thumb controls to the rig.

        Args:
            ctrl_list (list): List of right hand thumb control names.
            ctrl_id_list (list): List of right hand thumb control effector IDs.
        """
        for i, ctrl in enumerate(ctrl_list):
            self.add_ctrl(ctrl, ctrl_id_list[i])

    def add_right_hand_index_ctrl(
        self,
        ctrl_list,
        ctrl_id_list=HUMAN_IK_CTRL_MAP["RightHandIndex"],
    ):
        """Adds right hand index controls to the rig.

        Args:
            ctrl_list (list): List of right hand index control names.
            ctrl_id_list (list): List of right hand index control effector IDs.
        """
        for i, ctrl in enumerate(ctrl_list):
            self.add_ctrl(ctrl, ctrl_id_list[i])

    def add_right_hand_middle_ctrl(
        self,
        ctrl_list,
        ctrl_id_list=HUMAN_IK_CTRL_MAP["RightHandMiddle"],
    ):
        """Adds right hand middle controls to the rig.

        Args:
            ctrl_list (list): List of right hand middle control names.
            ctrl_id_list (list): List of right hand middle control effector IDs.
        """
        for i, ctrl in enumerate(ctrl_list):
            self.add_ctrl(ctrl, ctrl_id_list[i])

    def add_right_hand_ring_ctrl(
        self,
        ctrl_list,
        ctrl_id_list=HUMAN_IK_CTRL_MAP["RightHandRing"],
    ):
        """Adds right hand ring controls to the rig.

        Args:
            ctrl_list (list): List of right hand ring control names.
            ctrl_id_list (list): List of right hand ring control effector IDs.
        """
        for i, ctrl in enumerate(ctrl_list):
            self.add_ctrl(ctrl, ctrl_id_list[i])

    def add_right_hand_pinky_ctrl(
        self,
        ctrl_list,
        ctrl_id_list=HUMAN_IK_CTRL_MAP["RightHandPinky"],
    ):
        """Adds right hand pinky controls to the rig.

        Args:
            ctrl_list (list): List of right hand pinky control names.
            ctrl_id_list (list): List of right hand pinky control effector IDs.
        """
        for i, ctrl in enumerate(ctrl_list):
            self.add_ctrl(ctrl, ctrl_id_list[i])


def _demo() -> None:
    """Run a quick smoke test when executed as a script."""
    char_name = "Sylvanas"
    HumanIK(
        f"{char_name}_FK",
        custom_ctrl_definition=True,
        use_ik=False,
        skip_reference_joint=True,
    )
    HumanIK(
        f"{char_name}_IK",
        custom_ctrl_definition=True,
        use_ik=True,
        skip_reference_joint=True,
    )
    HumanIK(
        f"{char_name}_Hybrid",
        custom_ctrl_definition=True,
        use_ik=False,
        use_hybrid=True,
        skip_reference_joint=True,
    )


if __name__ == "__main__":
    _demo()

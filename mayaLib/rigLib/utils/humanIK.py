__author__ = 'Lorenzo Argentieri'

import maya.mel as mel
import pymel.core as pm

reference_joint_default = 'Base_main_FS_jnt'
hip_joint_joint_default = 'M_Spine_pelvis_FS_jnt'
spine_joint_list_default = ['M_Spine_ribbon_driven_0_FS_jnt', 'M_Spine_ribbon_driven_1_FS_jnt',
                            'M_Spine_ribbon_driven_2_FS_jnt', 'M_Spine_chest_FS_jnt', ]
neck_joint_list_default = ['M_Head_neck_root_FS_jnt', 'M_Head_ribbon_driven_0_FS_jnt', 'M_Head_ribbon_driven_1_FS_jnt',
                           'M_Head_ribbon_driven_2_FS_jnt']
head_joint_joint_default = 'M_Head_head_FS_jnt'
left_arm_joint_list_default = ['L_Arm_base_FS_jnt', 'L_Arm_upper_ribbon_driven_0_FS_jnt',
                               'L_Arm_lower_ribbon_driven_0_FS_jnt', 'L_Arm_tip_FS_jnt']
left_leg_joint_list_default = ['L_Leg_upper_ribbon_driven_0_FS_jnt', 'L_Leg_lower_ribbon_driven_0_FS_jnt',
                               'L_Leg_tip_FS_jnt', 'L_Leg_toes_root_FS_jnt']
right_arm_joint_list_default = ['R_Arm_base_FS_jnt', 'R_Arm_upper_ribbon_driven_0_FS_jnt',
                                'R_Arm_lower_ribbon_driven_0_FS_jnt', 'R_Arm_tip_FS_jnt']
right_leg_joint_list_default = ['R_Leg_upper_ribbon_driven_0_FS_jnt', 'R_Leg_lower_ribbon_driven_0_FS_jnt',
                                'R_Leg_tip_FS_jnt', 'R_Leg_toes_root_FS_jnt']
left_hand_thumb_joint_list_default = ['L_Fingers_thumb_0_0_FS_jnt', 'L_Fingers_thumb_0_1_FS_jnt',
                                      'L_Fingers_thumb_0_2_FS_jnt']
left_hand_index_joint_list_default = ['L_Fingers_finger_0_0_FS_jnt', 'L_Fingers_finger_0_1_FS_jnt',
                                      'L_Fingers_finger_0_2_FS_jnt', 'L_Fingers_finger_0_3_FS_jnt']
left_hand_middle_joint_list_default = ['L_Fingers_finger_1_0_FS_jnt', 'L_Fingers_finger_1_1_FS_jnt',
                                       'L_Fingers_finger_1_2_FS_jnt', 'L_Fingers_finger_1_3_FS_jnt']
left_hand_ring_joint_list_default = ['L_Fingers_finger_2_0_FS_jnt', 'L_Fingers_finger_2_1_FS_jnt',
                                     'L_Fingers_finger_2_2_FS_jnt', 'L_Fingers_finger_2_3_FS_jnt']
left_hand_pinky_joint_list_default = ['L_Fingers_finger_3_0_FS_jnt', 'L_Fingers_finger_3_1_FS_jnt',
                                      'L_Fingers_finger_3_2_FS_jnt', 'L_Fingers_finger_3_3_FS_jnt']

right_hand_thumb_joint_list_default = ['R_Fingers_thumb_0_0_FS_jnt', 'R_Fingers_thumb_0_1_FS_jnt',
                                       'R_Fingers_thumb_0_2_FS_jnt']
right_hand_index_joint_list_default = ['R_Fingers_finger_0_0_FS_jnt', 'R_Fingers_finger_0_1_FS_jnt',
                                       'R_Fingers_finger_0_2_FS_jnt', 'R_Fingers_finger_0_3_FS_jnt']
right_hand_middle_joint_list_default = ['R_Fingers_finger_1_0_FS_jnt', 'R_Fingers_finger_1_1_FS_jnt',
                                        'R_Fingers_finger_1_2_FS_jnt', 'R_Fingers_finger_1_3_FS_jnt']
right_hand_ring_joint_list_default = ['R_Fingers_finger_2_0_FS_jnt', 'R_Fingers_finger_2_1_FS_jnt',
                                      'R_Fingers_finger_2_2_FS_jnt', 'R_Fingers_finger_2_3_FS_jnt']
right_hand_pinky_joint_list_default = ['R_Fingers_finger_3_0_FS_jnt', 'R_Fingers_finger_3_1_FS_jnt',
                                       'R_Fingers_finger_3_2_FS_jnt', 'R_Fingers_finger_3_3_FS_jnt']

hip_ctrl_default = 'M_Spine_cog_ctrl'
spine_ctrl_list_default = ['M_Spine_base_ctrl', 'M_Spine_ik_0_ctrl']
chest_ctrl_default = 'M_Spine_ik_chest_ctrl'
neck_ctrl_default = 'M_Head_neck_root_ctrl'
head_ctrl_default = 'M_Head_head_ctrl'
left_clavicle_ctrl_default = 'L_Arm_base_ctrl'
left_shoulder_ctrl_default = 'L_Arm_fk_root_ctrl'
left_elbow_ctrl_default = 'L_Arm_fk_mid_ctrl'
left_hand_fk_ctrl_default = 'L_Arm_fk_tip_ctrl'
left_hand_ik_ctrl_default = 'L_Arm_ik_tip_ctrl'
right_clavicle_ctrl_default = 'R_Arm_base_ctrl'
right_shoulder_ctrl_default = 'R_Arm_fk_root_ctrl'
right_elbow_ctrl_default = 'R_Arm_fk_mid_ctrl'
right_hand_fk_ctrl_default = 'R_Arm_fk_tip_ctrl'
right_hand_ik_ctrl_default = 'R_Arm_ik_tip_ctrl'
left_hip_ctrl_default = 'L_Leg_fk_root_ctrl'
left_knee_ctrl_default = 'L_Leg_fk_mid_ctrl'
left_ankle_fk_ctrl_default = 'L_Leg_fk_tip_ctrl'
left_ankle_ik_ctrl_default = 'L_Leg_ik_tip_ctrl'
right_hip_ctrl_default = 'R_Leg_fk_root_ctrl'
right_knee_ctrl_default = 'R_Leg_fk_mid_ctrl'
right_ankle_fk_ctrl_default = 'R_Leg_fk_tip_ctrl'
right_ankle_ik_ctrl_default = 'R_Leg_ik_tip_ctrl'

left_hand_thumb_ctrl_list_default = ['L_Fingers_thumb_0_0_ctrl', 'L_Fingers_thumb_0_1_ctrl', 'L_Fingers_thumb_0_2_ctrl']
left_hand_index_ctrl_list_default = ['L_Fingers_finger_0_0_ctrl', 'L_Fingers_finger_0_1_ctrl',
                                     'L_Fingers_finger_0_2_ctrl', 'L_Fingers_finger_0_3_ctrl']
left_hand_middle_ctrl_list_default = ['L_Fingers_finger_1_0_ctrl', 'L_Fingers_finger_1_1_ctrl',
                                      'L_Fingers_finger_1_2_ctrl', 'L_Fingers_finger_1_3_ctrl']
left_hand_ring_ctrl_list_default = ['L_Fingers_finger_2_0_ctrl', 'L_Fingers_finger_2_1_ctrl',
                                    'L_Fingers_finger_2_2_ctrl', 'L_Fingers_finger_2_3_ctrl']
left_hand_pinky_ctrl_list_default = ['L_Fingers_finger_3_0_ctrl', 'L_Fingers_finger_3_1_ctrl',
                                     'L_Fingers_finger_3_2_ctrl', 'L_Fingers_finger_3_3_ctrl']

right_hand_thumb_ctrl_list_default = ['R_Fingers_thumb_0_0_ctrl', 'R_Fingers_thumb_0_1_ctrl',
                                      'R_Fingers_thumb_0_2_ctrl']
right_hand_index_ctrl_list_default = ['R_Fingers_finger_0_0_ctrl', 'R_Fingers_finger_0_1_ctrl',
                                      'R_Fingers_finger_0_2_ctrl', 'R_Fingers_finger_0_3_ctrl']
right_hand_middle_ctrl_list_default = ['R_Fingers_finger_1_0_ctrl', 'R_Fingers_finger_1_1_ctrl',
                                       'R_Fingers_finger_1_2_ctrl', 'R_Fingers_finger_1_3_ctrl']
right_hand_ring_ctrl_list_default = ['R_Fingers_finger_2_0_ctrl', 'R_Fingers_finger_2_1_ctrl',
                                     'R_Fingers_finger_2_2_ctrl', 'R_Fingers_finger_2_3_ctrl']
right_hand_pinky_ctrl_list_default = ['R_Fingers_finger_3_0_ctrl', 'R_Fingers_finger_3_1_ctrl',
                                      'R_Fingers_finger_3_2_ctrl', 'R_Fingers_finger_3_3_ctrl']

arise_hik_data = {'joints': {'Reference': reference_joint_default,
                             'Hips': hip_joint_joint_default,
                             'Spine': spine_joint_list_default,
                             'Neck': neck_joint_list_default,
                             'Head': head_joint_joint_default,
                             'LeftLeg': left_leg_joint_list_default,
                             'RightLeg': right_leg_joint_list_default,
                             'LeftArm': left_arm_joint_list_default,
                             'RightArm': right_arm_joint_list_default,
                             'LeftHandThumb': left_hand_thumb_joint_list_default,
                             'LeftHandIndex': left_hand_index_joint_list_default,
                             'LeftHandMiddle': left_hand_middle_joint_list_default,
                             'LeftHandRing': left_hand_ring_joint_list_default,
                             'LeftHandPinky': left_hand_pinky_joint_list_default,
                             'RightHandThumb': right_hand_thumb_joint_list_default,
                             'RightHandIndex': right_hand_index_joint_list_default,
                             'RightHandMiddle': right_hand_middle_joint_list_default,
                             'RightHandRing': right_hand_ring_joint_list_default,
                             'RightHandPinky': right_hand_pinky_joint_list_default
                             },
                  'ctrls': {'Hip': hip_ctrl_default,
                            'Spine': spine_ctrl_list_default,
                            'Chest': chest_ctrl_default,
                            'Neck': neck_ctrl_default,
                            'Head': head_ctrl_default,
                            'LeftClavicle': left_clavicle_ctrl_default,
                            'LeftShoulder': left_shoulder_ctrl_default,
                            'LeftElbow': left_elbow_ctrl_default,
                            'LeftHand': [left_hand_fk_ctrl_default, left_hand_ik_ctrl_default],
                            'RightClavicle': right_clavicle_ctrl_default,
                            'RightShoulder': right_shoulder_ctrl_default,
                            'RightElbow': right_elbow_ctrl_default,
                            'RightHand': [right_hand_fk_ctrl_default, right_hand_ik_ctrl_default],
                            'LeftUpLeg': left_hip_ctrl_default,
                            'LeftKnee': left_knee_ctrl_default,
                            'LeftAnkle': [left_ankle_fk_ctrl_default, left_ankle_ik_ctrl_default],
                            'RightUpLeg': right_hip_ctrl_default,
                            'RightKnee': right_knee_ctrl_default,
                            'RightAnkle': [right_ankle_fk_ctrl_default, right_ankle_ik_ctrl_default],
                            'LeftHandThumb': left_hand_thumb_ctrl_list_default,
                            'LeftHandIndex': left_hand_index_ctrl_list_default,
                            'LeftHandMiddle': left_hand_middle_ctrl_list_default,
                            'LeftHandRing': left_hand_ring_ctrl_list_default,
                            'LeftHandPinky': left_hand_pinky_ctrl_list_default,
                            'RightHandThumb': right_hand_thumb_ctrl_list_default,
                            'RightHandIndex': right_hand_index_ctrl_list_default,
                            'RightHandMiddle': right_hand_middle_ctrl_list_default,
                            'RightHandRing': right_hand_ring_ctrl_list_default,
                            'RightHandPinky': right_hand_pinky_ctrl_list_default
                            }
                  }

rokoko_hik_data = {'joints': {'Reference': '',
                             'Hips': 'Hips',
                             'Spine': ['Spine1', 'Spine2', 'Spine3', 'Spine4'],
                             'Neck': ['Neck'],
                             'Head': 'Head',
                             'LeftLeg': ['LeftThigh', 'LeftShin', 'LeftFoot', 'LeftToe'],
                             'RightLeg': ['RightThigh', 'RightShin', 'RightFoot', 'RightToe'],
                             'LeftArm': ['LeftShoulder', 'LeftArm', 'LeftForeArm', 'LeftHand'],
                             'RightArm': ['RightShoulder', 'RightArm', 'RightForeArm', 'RightHand'],
                             'LeftHandThumb': ['LeftFinger1Metacarpal', 'LeftFinger1Proximal', 'LeftFinger1Distal'],
                             'LeftHandIndex': ['', 'LeftFinger2Proximal', 'LeftFinger2Medial', 'LeftFinger2Distal'],
                             'LeftHandMiddle': ['', 'LeftFinger3Proximal', 'LeftFinger3Medial', 'LeftFinger3Distal'],
                             'LeftHandRing': ['', 'LeftFinger4Proximal', 'LeftFinger4Medial', 'LeftFinger4Distal'],
                             'LeftHandPinky': ['', 'LeftFinger5Proximal', 'LeftFinger5Medial', 'LeftFinger5Distal'],
                             'RightHandThumb': ['RightFinger1Metacarpal', 'RightFinger1Proximal', 'RightFinger1Distal'],
                             'RightHandIndex': ['', 'RightFinger2Proximal', 'RightFinger2Medial', 'RightFinger2Distal'],
                             'RightHandMiddle': ['', 'RightFinger3Proximal', 'RightFinger3Medial', 'RightFinger3Distal'],
                             'RightHandRing': ['', 'RightFinger4Proximal', 'RightFinger4Medial', 'RightFinger4Distal'],
                             'RightHandPinky': ['', 'RightFinger5Proximal', 'RightFinger5Medial', 'RightFinger5Distal']
                             }
                  }

advanced_skeleton_data = {'joints': {'Reference': '',
                             'Hips': 'Hips',
                             'Spine': ['Spine1', 'Spine2', 'Spine3', 'Spine4'],
                             'Neck': ['Neck'],
                             'Head': 'Head',
                             'LeftLeg': ['LeftThigh', 'LeftShin', 'LeftFoot', 'LeftToe'],
                             'RightLeg': ['RightThigh', 'RightShin', 'RightFoot', 'RightToe'],
                             'LeftArm': ['LeftShoulder', 'LeftArm', 'LeftForeArm', 'LeftHand'],
                             'RightArm': ['RightShoulder', 'RightArm', 'RightForeArm', 'RightHand'],
                             'LeftHandThumb': ['LeftFinger1Metacarpal', 'LeftFinger1Proximal', 'LeftFinger1Distal'],
                             'LeftHandIndex': ['', 'LeftFinger2Proximal', 'LeftFinger2Medial', 'LeftFinger2Distal'],
                             'LeftHandMiddle': ['', 'LeftFinger3Proximal', 'LeftFinger3Medial', 'LeftFinger3Distal'],
                             'LeftHandRing': ['', 'LeftFinger4Proximal', 'LeftFinger4Medial', 'LeftFinger4Distal'],
                             'LeftHandPinky': ['', 'LeftFinger5Proximal', 'LeftFinger5Medial', 'LeftFinger5Distal'],
                             'RightHandThumb': ['RightFinger1Metacarpal', 'RightFinger1Proximal', 'RightFinger1Distal'],
                             'RightHandIndex': ['', 'RightFinger2Proximal', 'RightFinger2Medial', 'RightFinger2Distal'],
                             'RightHandMiddle': ['', 'RightFinger3Proximal', 'RightFinger3Medial', 'RightFinger3Distal'],
                             'RightHandRing': ['', 'RightFinger4Proximal', 'RightFinger4Medial', 'RightFinger4Distal'],
                             'RightHandPinky': ['', 'RightFinger5Proximal', 'RightFinger5Medial', 'RightFinger5Distal']
                             }
                  }

class HumanIK(object):
    humanIK_joint_dict = {
        'Reference': 0,
        'Hips': 1,
        'Spine': (8, 23, 24, 25, 26, 27, 28, 29, 30, 31),
        'Neck': (20, 32, 33, 34, 35, 36, 37, 38, 39, 40),
        'Head': 15,
        'LeftUpLeg': 2,
        'LeftLeg': 3,
        'LeftFoot': 4,
        'LeftToeBase': 16,
        'RightUpLeg': 5,
        'RightLeg': 6,
        'RightFoot': 7,
        'RightToeBase': 17,
        'LeftShoulder': 18,
        'LeftArm': 9,
        'LeftForeArm': 10,
        'LeftHand': 11,
        'RightShoulder': 19,
        'RightArm': 12,
        'RightForeArm': 13,
        'RightHand': 14,
        'LeftHandThumb': (50, 51, 52),
        'LeftHandIndex': (147, 54, 55, 56),
        'LeftHandMiddle': (148, 58, 59, 60),
        'LeftHandRing': (149, 62, 63, 64),
        'LeftHandPinky': (150, 66, 67, 68),
        'RightHandThumb': (74, 75, 76),
        'RightHandIndex': (153, 78, 79, 80),
        'RightHandMiddle': (154, 82, 83, 84),
        'RightHandRing': (155, 86, 87, 88),
        'RightHandPinky': (156, 90, 91, 92),
    }

    humanIK_ctrl_dict = {
        'Hip': 1,
        'Spine': (8, 23, 24, 25, 26),
        'Chest': 1000,
        'Neck': 20,
        'Head': 15,
        'LeftClavicle': 18,
        'LeftShoulder': 9,
        'LeftElbow': 10,
        'LeftHand': 11,
        'RightClavicle': 19,
        'RightShoulder': 12,
        'RightElbow': 13,
        'RightHand': 14,
        'LeftUpLeg': 2,
        'LeftKnee': 3,
        'LeftAnkle': 4,
        'RightUpLeg': 5,
        'RightKnee': 6,
        'RightAnkle': 7,
        'LeftHandThumb': (50, 51, 52),
        'LeftHandIndex': (147, 54, 55, 56),
        'LeftHandMiddle': (148, 58, 59, 60),
        'LeftHandRing': (149, 62, 63, 64),
        'LeftHandPinky': (150, 66, 67, 68),
        'RightHandThumb': (74, 75, 76),
        'RightHandIndex': (153, 78, 79, 80),
        'RightHandMiddle': (154, 82, 83, 84),
        'RightHandRing': (155, 86, 87, 88),
        'RightHandPinky': (156, 90, 91, 92),
    }

    rig_definition = {'arise': arise_hik_data, 'rokoko': rokoko_hik_data}

    def __init__(self, character_name, rig_template='arise', auto_T_pose=True, custom_ctrl_definition=True, use_ik=True, use_hybrid=True, skip_reference_joint=True):
        """Initialize the HumanIK class.

        Args:
            character_name (str): The name of the character to be created.
            rig_template (str): The template of the rig data to be used. Available
                templates are 'arise' and 'rokoko'. Defaults to 'arise'.
            auto_T_pose (bool): Whether to go to T pose after initialization. Defaults to True.
            custom_ctrl_definition (bool): Whether to define custom controls. Defaults to True.
            use_ik (bool): Whether to use IK. Defaults to True.
            use_hybrid (bool): Whether to use hybrid IK. Defaults to True.
            skip_reference_joint (bool): Whether to skip the reference joint. Defaults to True.
        """
        self.charecter_name = str(character_name)

        # Set T Pose
        if auto_T_pose:
            self.go_to_T_pose(rig_template)

        # Init HumanIK Window
        mel.eval('HIKCharacterControlsTool;')

        # Create Character
        mel.eval('hikCreateCharacter("' + self.charecter_name + '")')

        # Select Rig Data
        self.rig_data = self.rig_definition[rig_template]

        self.define_skeleton(self.rig_data, skip_reference_joint)

        if custom_ctrl_definition:
            self.define_custom_ctrls(self.rig_data, use_ik, use_hybrid)

    def _arise_T_pose(self):
        """Set the character to the T pose using the Arise plugin utilities.

        This function appends the appropriate version-specific path of the 
        Arise plugin to the system path (if not already present) and applies 
        the zero pose to all controls using the Arise utilities.
        """
        import sys
        import os

        # Construct the local path to the Arise plugin based on the current user's Documents folder
        LOCAL_PATH = r"C:/Users/" + os.getlogin() + "/Documents/maya/Plug-ins/arise_main"
        
        # Determine the version folder based on the Python version
        version_folder = 'py_' + str(sys.version_info.major) + '_' + str(sys.version_info.minor)
        path = os.path.join(LOCAL_PATH, version_folder)

        # Append the path to sys.path if it's not already included
        if path not in sys.path:
            sys.path.append(path)

        # Import the apply_zero_pose_all function from the Arise utilities
        from arise.utils.ctrls_utils import apply_zero_pose_all

        # Apply the zero pose to all controls silently
        apply_zero_pose_all(silent=True)

    def _arms_parallel_to_grid(self, left_arm_transforms=[left_clavicle_ctrl_default, left_shoulder_ctrl_default, left_elbow_ctrl_default, left_hand_fk_ctrl_default], 
                               right_arm_transforms=[right_clavicle_ctrl_default, right_shoulder_ctrl_default, right_elbow_ctrl_default, right_hand_fk_ctrl_default]):
        """
        Set the arms parallel to the grid by aligning the upperarm bone to the grid.

        Args:
            left_arm_transforms (list): List of transforms for the left arm.
            right_arm_transforms (list): List of transforms for the right arm.  
        """

        from mayaLib.rigLib.utils import joint
        joint.setArmParallelToGrid(left_arm_transforms)
        joint.setArmParallelToGrid(right_arm_transforms)

    def go_to_T_pose(self, template):
        """Sets the character to the T pose.

        Depending on the template provided, this function sets the character
        to the T pose using either the Arise plugin utilities or by aligning
        the arms parallel to the grid.

        Args:
            template (str): The name of the template used to determine the method
                for setting the T pose. Options are 'arise' or any other value
                to use the grid alignment method.
        """
        if template == 'arise':
            # Use Arise plugin utilities to set T pose
            self._arise_T_pose()
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
        if rig_data['joints']['Reference'] and not skip_reference_joint:
            self.add_reference(rig_data['joints']['Reference'])

        # Add hip joint
        if rig_data['joints']['Hips']:
            self.add_hip(rig_data['joints']['Hips'])

        # Add spine joints
        if rig_data['joints']['Spine']:
            self.add_spine(rig_data['joints']['Spine'])

        # Add neck joint
        if rig_data['joints']['Neck']:
            self.add_neck(rig_data['joints']['Neck'])

        # Add head joint
        if rig_data['joints']['Head']:
            self.add_head(rig_data['joints']['Head'])

        # Add left arm joints
        if rig_data['joints']['LeftArm']:
            self.add_left_arm(*rig_data['joints']['LeftArm'])

        # Add left leg joints
        if rig_data['joints']['LeftLeg']:
            self.add_left_leg(*rig_data['joints']['LeftLeg'])

        # Add right arm joints
        if rig_data['joints']['RightArm']:
            self.add_right_arm(*rig_data['joints']['RightArm'])

        # Add right leg joints
        if rig_data['joints']['RightLeg']:
            self.add_right_leg(*rig_data['joints']['RightLeg'])

        # Add left hand thumb joints
        if rig_data['joints']['LeftHandThumb']:
            self.add_leftHandThumb(rig_data['joints']['LeftHandThumb'])

        # Add left hand index joints
        if rig_data['joints']['LeftHandIndex']:
            self.add_leftHandIndex(rig_data['joints']['LeftHandIndex'])

        # Add left hand middle joints
        if rig_data['joints']['LeftHandMiddle']:
            self.add_leftHandMiddle(rig_data['joints']['LeftHandMiddle'])

        # Add left hand ring joints
        if rig_data['joints']['LeftHandRing']:
            self.add_leftHandRing(rig_data['joints']['LeftHandRing'])

        # Add left hand pinky joints
        if rig_data['joints']['LeftHandPinky']:
            self.add_leftHandPinky(rig_data['joints']['LeftHandPinky'])

        # Add right hand thumb joints
        if rig_data['joints']['RightHandThumb']:
            self.add_rightHandThumb(rig_data['joints']['RightHandThumb'])

        # Add right hand index joints
        if rig_data['joints']['RightHandIndex']:
            self.add_rightHandIndex(rig_data['joints']['RightHandIndex'])

        # Add right hand middle joints
        if rig_data['joints']['RightHandMiddle']:
            self.add_rightHandMiddle(rig_data['joints']['RightHandMiddle'])

        # Add right hand ring joints
        if rig_data['joints']['RightHandRing']:
            self.add_rightHandRing(rig_data['joints']['RightHandRing'])

        # Add right hand pinky joints
        if rig_data['joints']['RightHandPinky']:
            self.add_rightHandPinky(rig_data['joints']['RightHandPinky'])

    def define_custom_ctrls(self, rig_data, use_ik=True, use_hybrid=True):
        """Define custom controls for the HumanIK rig.

        Args:
            rig_data (dict): A dictionary containing the rig data.
            use_ik (bool): Whether to use IK controls. Defaults to True.
            use_hybrid (bool): Whether to use hybrid IK controls. Defaults to True.

        """
        if not rig_data:
            rig_data = self.rig_data

        self.createCustomRigMapping()

        # Add hip control
        if rig_data['ctrls']['Hip']:
            self.add_hip_ctrl(rig_data['ctrls']['Hip'])

        # Add spine control
        if rig_data['ctrls']['Spine']:
            self.add_spine_ctrl(rig_data['ctrls']['Spine'])

        # Add chest control
        if rig_data['ctrls']['Chest']:
            self.add_chest_ctrl(rig_data['ctrls']['Chest'])

        # Add neck control
        if rig_data['ctrls']['Neck']:
            self.add_neck_ctrl(rig_data['ctrls']['Neck'])

        # Add head control
        if rig_data['ctrls']['Head']:
            self.add_head_ctrl(rig_data['ctrls']['Head'])

        # Add left clavicle control
        if rig_data['ctrls']['LeftClavicle']:
            self.add_leftClavicle_ctrl(rig_data['ctrls']['LeftClavicle'])

        # Add right clavicle control
        if rig_data['ctrls']['RightClavicle']:
            self.add_rightClavicle_ctrl(rig_data['ctrls']['RightClavicle'])

        # Add left and right limb controls
        if not use_ik and not use_hybrid:
            # Add left and right shoulder controls
            if rig_data['ctrls']['LeftShoulder']:
                self.add_leftShoulder_ctrl(rig_data['ctrls']['LeftShoulder'])
            if rig_data['ctrls']['RightShoulder']:
                self.add_rightShoulder_ctrl(rig_data['ctrls']['RightShoulder'])

            # Add left and right elbow controls
            if rig_data['ctrls']['LeftElbow']:
                self.add_leftElbow_ctrl(rig_data['ctrls']['LeftElbow'])
            if rig_data['ctrls']['RightElbow']:
                self.add_rightElbow_ctrl(rig_data['ctrls']['RightElbow'])

            # Add left and right hand controls
            if rig_data['ctrls']['LeftHand'][0]:
                self.add_leftHand_ctrl(rig_data['ctrls']['LeftHand'][0])
            if rig_data['ctrls']['RightHand'][0]:
                self.add_rightHand_ctrl(rig_data['ctrls']['RightHand'][0])

            # Add left and right leg controls
            if rig_data['ctrls']['LeftUpLeg']:
                self.add_leftHip_ctrl(rig_data['ctrls']['LeftUpLeg'])
            if rig_data['ctrls']['LeftKnee']:
                self.add_leftKnee_ctrl(rig_data['ctrls']['LeftKnee'])
            if rig_data['ctrls']['LeftAnkle'][0]:
                self.add_leftAnkle_ctrl(rig_data['ctrls']['LeftAnkle'][0])

            if rig_data['ctrls']['RightUpLeg']:
                self.add_rightHip_ctrl(rig_data['ctrls']['RightUpLeg'])
            if rig_data['ctrls']['RightKnee']:
                self.add_rightKnee_ctrl(rig_data['ctrls']['RightKnee'])
            if rig_data['ctrls']['RightAnkle'][0]:
                self.add_rightAnkle_ctrl(rig_data['ctrls']['RightAnkle'][0])

        if use_ik and not use_hybrid:
            # Add left and right hand IK controls
            if rig_data['ctrls']['LeftHand'][1]:
                self.add_leftHand_ctrl(rig_data['ctrls']['LeftHand'][1])
            if rig_data['ctrls']['RightHand'][1]:
                self.add_rightHand_ctrl(rig_data['ctrls']['RightHand'][1])

            if rig_data['ctrls']['LeftAnkle'][1]:
                self.add_leftAnkle_ctrl(rig_data['ctrls']['LeftAnkle'][1])
            if rig_data['ctrls']['RightAnkle'][1]:
                self.add_rightAnkle_ctrl(rig_data['ctrls']['RightAnkle'][1])

        if use_hybrid:
            # Add left and right limb controls
            if rig_data['ctrls']['LeftShoulder']:
                self.add_leftShoulder_ctrl(rig_data['ctrls']['LeftShoulder'])
            if rig_data['ctrls']['RightShoulder']:
                self.add_rightShoulder_ctrl(rig_data['ctrls']['RightShoulder'])

            if rig_data['ctrls']['LeftElbow']:
                self.add_leftElbow_ctrl(rig_data['ctrls']['LeftElbow'])
            if rig_data['ctrls']['RightElbow']:
                self.add_rightElbow_ctrl(rig_data['ctrls']['RightElbow'])

            if rig_data['ctrls']['LeftHand'][0]:
                self.add_leftHand_ctrl(rig_data['ctrls']['LeftHand'][0])
            if rig_data['ctrls']['RightHand'][0]:
                self.add_rightHand_ctrl(rig_data['ctrls']['RightHand'][0])

            if rig_data['ctrls']['LeftAnkle'][1]:
                self.add_leftAnkle_ctrl(rig_data['ctrls']['LeftAnkle'][1])

            if rig_data['ctrls']['RightAnkle'][1]:
                self.add_rightAnkle_ctrl(rig_data['ctrls']['RightAnkle'][1])

        if rig_data['ctrls']['LeftHandThumb']:
            self.add_leftHandThumb_ctrl(rig_data['ctrls']['LeftHandThumb'])
        if rig_data['ctrls']['RightHandThumb']:
            self.add_rightHandThumb_ctrl(rig_data['ctrls']['RightHandThumb'])

        # Add left and right hand index controls
        if rig_data['ctrls']['LeftHandIndex']:
            self.add_leftHandIndex_ctrl(rig_data['ctrls']['LeftHandIndex'])
        if rig_data['ctrls']['RightHandIndex']:
            self.add_rightHandIndex_ctrl(rig_data['ctrls']['RightHandIndex'])

        # Add left and right hand middle controls
        if rig_data['ctrls']['LeftHandMiddle']:
            self.add_leftHandMiddle_ctrl(rig_data['ctrls']['LeftHandMiddle'])
        if rig_data['ctrls']['RightHandMiddle']:
            self.add_rightHandMiddle_ctrl(rig_data['ctrls']['RightHandMiddle'])

        # Add left and right hand ring controls
        if rig_data['ctrls']['LeftHandRing']:
            self.add_leftHandRing_ctrl(rig_data['ctrls']['LeftHandRing'])
        if rig_data['ctrls']['RightHandRing']:
            self.add_rightHandRing_ctrl(rig_data['ctrls']['RightHandRing'])

        # Add left and right hand pinky controls
        if rig_data['ctrls']['LeftHandPinky']:
            self.add_leftHandPinky_ctrl(rig_data['ctrls']['LeftHandPinky'])
        if rig_data['ctrls']['RightHandPinky']:
            self.add_rightHandPinky_ctrl(rig_data['ctrls']['RightHandPinky'])

    def setCharacterObject(self, joint, joint_id):
        """
        Set a character object attribute on a Maya joint.

        Args:
            joint (str): The name of the Maya joint.
            joint_id (int): The character object ID.

        Returns:
            None
        """
        if pm.objExists(joint):
            joint = str(pm.ls(joint)[-1].name())
            mel.eval('setCharacterObject("' + joint + '", "' + self.charecter_name + '", "' + str(joint_id) + '", 0);')

    def add_reference(self, joint, joint_id=humanIK_joint_dict['Reference']):
        """Add a reference joint to the character.

        Args:
            joint (str): The name of the Maya joint.
            joint_id (int): The character object ID for the reference joint.
        """
        # Set the character object for the reference joint
        self.setCharacterObject(joint, joint_id)

    def add_hip(self, joint, joint_id=humanIK_joint_dict['Hips']):
        """Add a hip joint to the character.

        Args:
            joint (str): The name of the Maya joint.
            joint_id (int): The character object ID for the hip joint.
        """
        # Set the character object for the hip joint
        self.setCharacterObject(joint, joint_id)

    def add_spine(self, joint_list, joint_id_list=humanIK_joint_dict['Spine']):
        """Add a spine to the character.

        Args:
            joint_list (list): A list of Maya joints that make up the spine.
            joint_id_list (list): A list of character object IDs, one for each joint in the spine.
        """
        # Iterate over the joint list and add each joint to the character
        for i, joint in enumerate(joint_list):
            # Set the character object for each joint in the spine
            self.setCharacterObject(joint, joint_id_list[i])

    def add_neck(self, joint_list, joint_id_list=humanIK_joint_dict['Neck']):
        """Add a neck to the character.

        Args:
            joint_list (list): A list of Maya joints that make up the neck.
            joint_id_list (list): A list of character object IDs, one for each joint in the neck.
        """
        # Iterate over the joint list and add each joint to the character
        for i, joint in enumerate(joint_list):
            # Set the character object for each joint in the neck
            self.setCharacterObject(joint, joint_id_list[i])

    def add_head(self, joint, joint_id=humanIK_joint_dict['Head']):
        """Add a head to the character.

        Args:
            joint (str): The name of the Maya joint.
            joint_id (int): The character object ID for the head joint.
        """
        # Set the character object for the head joint
        self.setCharacterObject(joint, joint_id)

    def add_leftUpLeg(self, joint, joint_id=humanIK_joint_dict['LeftUpLeg']):
        """Add left up leg to the character.

        Args:
            joint (str): The name of the Maya joint.
            joint_id (int): The character object ID for the left up leg joint.

        Returns:
            None
        """
        # Set the character object for the left up leg joint
        self.setCharacterObject(joint, joint_id)

    def add_leftLeg(self, joint, joint_id=humanIK_joint_dict['LeftLeg']):
        """Add a left leg to the character.

        Args:
            joint (str): The name of the Maya joint.
            joint_id (int): The character object ID for the left leg joint.

        Returns:
            None
        """
        # Set the character object for the left leg joint
        self.setCharacterObject(joint, joint_id)

    def add_leftFoot(self, joint, joint_id=humanIK_joint_dict['LeftFoot']):
        """Add the left foot joint to the character.

        Args:
            joint (str): The name of the Maya joint.
            joint_id (int): The character object ID for the left foot joint.

        Returns:
            None
        """
        self.setCharacterObject(joint, joint_id)

    def add_leftShoulder(self, joint, joint_id=humanIK_joint_dict['LeftShoulder']):
        """Add the left shoulder joint to the character.

        Args:
            joint (str): The name of the Maya joint.
            joint_id (int): The character object ID for the left shoulder joint.

        Returns:
            None
        """
        self.setCharacterObject(joint, joint_id)

    def add_leftArm(self, joint, joint_id=humanIK_joint_dict['LeftArm']):
        """Add the left arm joint to the character.

        Args:
            joint (str): The name of the Maya joint.
            joint_id (int): The character object ID for the left arm joint.

        Returns:
            None
        """
        self.setCharacterObject(joint, joint_id)

    def add_leftForeArm(self, joint, joint_id=humanIK_joint_dict['LeftForeArm']):
        """Add the left forearm joint to the character.

        Args:
            joint (str): The name of the Maya joint.
            joint_id (int): The character object ID for the left forearm joint.

        Returns:
            None
        """
        self.setCharacterObject(joint, joint_id)

    def add_leftHand(self, joint, joint_id=humanIK_joint_dict['LeftHand']):
        """Add the left hand joint to the character.

        Args:
            joint (str): The name of the Maya joint.
            joint_id (int): The character object ID for the left hand joint.

        Returns:
            None
        """
        self.setCharacterObject(joint, joint_id)

    def add_rightUpLeg(self, joint, joint_id=humanIK_joint_dict['RightUpLeg']):
        """Add the right up leg joint to the character.

        Args:
            joint (str): The name of the Maya joint.
            joint_id (int): The character object ID for the right up leg joint.

        Returns:
            None
        """
        self.setCharacterObject(joint, joint_id)

    def add_rightLeg(self, joint, joint_id=humanIK_joint_dict['RightLeg']):
        """Add the right leg joint to the character.

        Args:
            joint (str): The name of the Maya joint.
            joint_id (int): The character object ID for the right leg joint.

        Returns:
            None
        """
        self.setCharacterObject(joint, joint_id)

    def add_rightFoot(self, joint, joint_id=humanIK_joint_dict['RightFoot']):
        """Add the right foot joint to the character.

        Args:
            joint (str): The name of the Maya joint.
            joint_id (int): The character object ID for the right foot joint.

        Returns:
            None
        """
        self.setCharacterObject(joint, joint_id)

    def add_rightShoulder(self, joint, joint_id=humanIK_joint_dict['RightShoulder']):
        """Add the right shoulder joint to the character.

        Args:
            joint (str): The name of the Maya joint.
            joint_id (int): The character object ID for the right shoulder joint.

        Returns:
            None
        """
        self.setCharacterObject(joint, joint_id)

    def add_rightArm(self, joint, joint_id=humanIK_joint_dict['RightArm']):
        """Add the right arm joint to the character.

        Args:
            joint (str): The name of the Maya joint.
            joint_id (int): The character object ID for the right arm joint.

        Returns:
            None
        """
        self.setCharacterObject(joint, joint_id)

    def add_rightForeArm(self, joint, joint_id=humanIK_joint_dict['RightForeArm']):
        """Add the right forearm joint to the character.

        Args:
            joint (str): The name of the Maya joint.
            joint_id (int): The character object ID for the right forearm joint.

        Returns:
            None
        """
        self.setCharacterObject(joint, joint_id)

    def add_rightHand(self, joint, joint_id=humanIK_joint_dict['RightHand']):
        """Add the right hand joint to the character.

        Args:
            joint (str): The name of the Maya joint.
            joint_id (int): The character object ID for the right hand joint.

        Returns:
            None
        """
        self.setCharacterObject(joint, joint_id)

    def add_leftToeBase(self, joint, joint_id=humanIK_joint_dict['LeftToeBase']):
        """Add the left toe base joint to the character.

        Args:
            joint (str): The name of the Maya joint.
            joint_id (int): The character object ID for the left toe base joint.

        Returns:
            None
        """
        self.setCharacterObject(joint, joint_id)

    def add_rightToeBase(self, joint, joint_id=humanIK_joint_dict['RightToeBase']):
        """Add the right toe base joint to the character.

        Args:
            joint (str): The name of the Maya joint.
            joint_id (int): The character object ID for the right toe base joint.

        Returns:
            None
        """
        self.setCharacterObject(joint, joint_id)

    def add_leftHandThumb(self, joint_list, joint_id_list=humanIK_joint_dict['LeftHandThumb']):
        """Add the left hand thumb joints to the character.

        Args:
            joint_list (list): A list of Maya joints that make up the left hand thumb.
            joint_id_list (list): A list of character object IDs, one for each joint in the left hand thumb.

        Returns:
            None
        """
        for i, joint in enumerate(joint_list):
            self.setCharacterObject(joint, joint_id_list[i])

    def add_leftHandIndex(self, joint_list, joint_id_list=humanIK_joint_dict['LeftHandIndex']):
        """Add the left hand index joints to the character.

        Args:
            joint_list (list): A list of Maya joints that make up the left hand index.
            joint_id_list (list): A list of character object IDs, one for each joint in the left hand index.

        Returns:
            None
        """
        for i, joint in enumerate(joint_list):
            self.setCharacterObject(joint, joint_id_list[i])

    def add_leftHandMiddle(self, joint_list, joint_id_list=humanIK_joint_dict['LeftHandMiddle']):
        """Add the left hand middle joints to the character.

        Args:
            joint_list (list): A list of Maya joints that make up the left hand middle.
            joint_id_list (list): A list of character object IDs, one for each joint in the left hand middle.

        Returns:
            None
        """
        for i, joint in enumerate(joint_list):
            self.setCharacterObject(joint, joint_id_list[i])

    def add_leftHandRing(self, joint_list, joint_id_list=humanIK_joint_dict['LeftHandRing']):
        """Add the left hand ring joints to the character.

        Args:
            joint_list (list): A list of Maya joints that make up the left hand ring.
            joint_id_list (list): A list of character object IDs, one for each joint in the left hand ring.

        Returns:
            None
        """
        for i, joint in enumerate(joint_list):
            self.setCharacterObject(joint, joint_id_list[i])

    def add_leftHandPinky(self, joint_list, joint_id_list=humanIK_joint_dict['LeftHandPinky']):
        """Add the left hand pinky joints to the character.

        Args:
            joint_list (list): A list of Maya joints that make up the left hand pinky.
            joint_id_list (list): A list of character object IDs, one for each joint in the left hand pinky.

        Returns:
            None
        """
        for i, joint in enumerate(joint_list):
            self.setCharacterObject(joint, joint_id_list[i])

    def add_rightHandThumb(self, joint_list, joint_id_list=humanIK_joint_dict['RightHandThumb']):
        """Add the right hand thumb joints to the character.

        Args:
            joint_list (list): A list of Maya joints that make up the right hand thumb.
            joint_id_list (list): A list of character object IDs, one for each joint in the right hand thumb.

        Returns:
            None
        """
        for i, joint in enumerate(joint_list):
            self.setCharacterObject(joint, joint_id_list[i])

    def add_rightHandIndex(self, joint_list, joint_id_list=humanIK_joint_dict['RightHandIndex']):
        """Add the right hand index joints to the character.

        Args:
            joint_list (list): A list of Maya joints that make up the right hand index.
            joint_id_list (list): A list of character object IDs, one for each joint in the right hand index.

        Returns:
            None
        """
        for i, joint in enumerate(joint_list):
            self.setCharacterObject(joint, joint_id_list[i])

    def add_rightHandMiddle(self, joint_list, joint_id_list=humanIK_joint_dict['RightHandMiddle']):
        """Add the right hand middle joints to the character.

        Args:
            joint_list (list): A list of Maya joints that make up the right hand middle.
            joint_id_list (list): A list of character object IDs, one for each joint in the right hand middle.

        Returns:
            None
        """
        # Iterate over the joint list and assign character objects
        for i, joint in enumerate(joint_list):
            self.setCharacterObject(joint, joint_id_list[i])

    def add_rightHandRing(self, joint_list, joint_id_list=humanIK_joint_dict['RightHandRing']):
        """Add the right hand ring joints to the character.

        Args:
            joint_list (list): A list of Maya joints that make up the right hand ring.
            joint_id_list (list): A list of character object IDs, one for each joint in the right hand ring.

        Returns:
            None
        """
        # Iterate over the joint list and assign character objects
        for i, joint in enumerate(joint_list):
            self.setCharacterObject(joint, joint_id_list[i])

    def add_rightHandPinky(self, joint_list, joint_id_list=humanIK_joint_dict['RightHandPinky']):
        """Add the right hand pinky joints to the character.

        Args:
            joint_list (list): A list of Maya joints for the right hand pinky.
            joint_id_list (list): A list of character object IDs for the right hand pinky joints.
        """
        for i, joint in enumerate(joint_list):
            self.setCharacterObject(joint, joint_id_list[i])

    def add_left_arm(self, clavicle=None, shoulder=None, forearm=None, hand=None):
        """Add the left arm components to the character.

        Args:
            clavicle (str, optional): The clavicle joint name.
            shoulder (str, optional): The shoulder joint name.
            forearm (str, optional): The forearm joint name.
            hand (str, optional): The hand joint name.
        """
        if clavicle:
            self.add_leftShoulder(clavicle)
        if shoulder:
            self.add_leftArm(shoulder)
        if forearm:
            self.add_leftForeArm(forearm)
        if hand:
            self.add_leftHand(hand)

    def add_right_arm(self, clavicle=None, shoulder=None, forearm=None, hand=None):
        """Add the right arm components to the character.

        Args:
            clavicle (str, optional): The clavicle joint name.
            shoulder (str, optional): The shoulder joint name.
            forearm (str, optional): The forearm joint name.
            hand (str, optional): The hand joint name.
        """
        if clavicle:
            self.add_rightShoulder(clavicle)
        if shoulder:
            self.add_rightArm(shoulder)
        if forearm:
            self.add_rightForeArm(forearm)
        if hand:
            self.add_rightHand(hand)

    def add_left_leg(self, upper_leg=None, leg=None, foot=None, ball=None):
        """Add the left leg components to the character.

        Args:
            upper_leg (str, optional): The upper leg joint name.
            leg (str, optional): The leg joint name.
            foot (str, optional): The foot joint name.
            ball (str, optional): The ball joint name.
        """
        if upper_leg:
            self.add_leftUpLeg(upper_leg)
        if leg:
            self.add_leftLeg(leg)
        if foot:
            self.add_leftFoot(foot)
        if ball:
            self.add_leftToeBase(ball)

    def add_right_leg(self, upper_leg=None, leg=None, foot=None, ball=None):
        """Add the right leg components to the character.

        Args:
            upper_leg (str, optional): The upper leg joint name.
            leg (str, optional): The leg joint name.
            foot (str, optional): The foot joint name.
            ball (str, optional): The ball joint name.
        """
        if upper_leg:
            self.add_rightUpLeg(upper_leg)
        if leg:
            self.add_rightLeg(leg)
        if foot:
            self.add_rightFoot(foot)
        if ball:
            self.add_rightToeBase(ball)

    def loadCustomRigTemplate(self):
        """Load the custom rig UI configuration using MEL."""
        mel.eval('hikLoadCustomRigUIConfiguration();')

    def createCustomRigMapping(self):
        """Create custom rig mapping for the current character using MEL."""
        mel.eval('hikCreateCustomRig( hikGetCurrentCharacter() );')

    def add_remove_custom_rig_mapping(self):
        """
        hikCustomRigAddRemoveMapping("R", `iconTextCheckBox - q - v hikCustomRigRotateButton` );

        import maya.app.hik.retargeter as r
        temporary = r.HIKRetargeter.createDefaultMapping('HIKState2GlobalSK1', 'Test', 'RightInHandMiddle', 'R_Fingers_finger_1_0_ctrl', 'R', 154, 0)
        #r.DefaultRetargeter.toGraph(temporary, 'HIKState2GlobalSK1')
        #del temporary
        """

    def add_ctrl(self, ctrl, ctrl_id):
        """Assigns a control to a custom rig effector.

        Args:
            ctrl (str): Name of the control.
            ctrl_id (int): ID of the control effector.
        """
        if pm.objExists(ctrl):
            pm.select(ctrl)
            mel.eval('hikCustomRigAssignEffector ' + str(ctrl_id) + ';')

    def add_hip_ctrl(self, ctrl, ctrl_id=humanIK_ctrl_dict['Hip']):
        """Adds the hip control to the rig.

        Args:
            ctrl (str): Name of the hip control.
            ctrl_id (int): ID of the hip control effector.
        """
        self.add_ctrl(ctrl, ctrl_id)

    def add_spine_ctrl(self, ctrl_list, ctrl_id_list=humanIK_ctrl_dict['Spine']):
        """Adds spine controls to the rig.

        Args:
            ctrl_list (list): List of spine control names.
            ctrl_id_list (list): List of spine control effector IDs.
        """
        for i, ctrl in enumerate(ctrl_list):
            self.add_ctrl(ctrl, ctrl_id_list[i])

    def add_chest_ctrl(self, ctrl, ctrl_id=humanIK_ctrl_dict['Chest']):
        """Adds the chest control to the rig.

        Args:
            ctrl (str): Name of the chest control.
            ctrl_id (int): ID of the chest control effector.
        """
        self.add_ctrl(ctrl, ctrl_id)

    def add_neck_ctrl(self, ctrl, ctrl_id=humanIK_ctrl_dict['Neck']):
        """Adds the neck control to the rig.

        Args:
            ctrl (str): Name of the neck control.
            ctrl_id (int): ID of the neck control effector.
        """
        self.add_ctrl(ctrl, ctrl_id)

    def add_head_ctrl(self, ctrl, ctrl_id=humanIK_ctrl_dict['Head']):
        """Adds the head control to the rig.

        Args:
            ctrl (str): Name of the head control.
            ctrl_id (int): ID of the head control effector.
        """
        self.add_ctrl(ctrl, ctrl_id)

    def add_leftClavicle_ctrl(self, ctrl, ctrl_id=humanIK_ctrl_dict['LeftClavicle']):
        """Adds the left clavicle control to the rig.

        Args:
            ctrl (str): Name of the left clavicle control.
            ctrl_id (int): ID of the left clavicle control effector.
        """
        self.add_ctrl(ctrl, ctrl_id)

    def add_leftShoulder_ctrl(self, ctrl, ctrl_id=humanIK_ctrl_dict['LeftShoulder']):
        """Adds the left shoulder control to the rig.

        Args:
            ctrl (str): Name of the left shoulder control.
            ctrl_id (int): ID of the left shoulder control effector.
        """
        self.add_ctrl(ctrl, ctrl_id)

    def add_leftElbow_ctrl(self, ctrl, ctrl_id=humanIK_ctrl_dict['LeftElbow']):
        """Adds the left elbow control to the rig.

        Args:
            ctrl (str): Name of the left elbow control.
            ctrl_id (int): ID of the left elbow control effector.
        """
        self.add_ctrl(ctrl, ctrl_id)

    def add_leftHand_ctrl(self, ctrl, ctrl_id=humanIK_ctrl_dict['LeftHand']):
        """Adds the left hand control to the rig.

        Args:
            ctrl (str): Name of the left hand control.
            ctrl_id (int): ID of the left hand control effector.
        """
        self.add_ctrl(ctrl, ctrl_id)

    def add_leftHip_ctrl(self, ctrl, ctrl_id=humanIK_ctrl_dict['LeftUpLeg']):
        """Adds the left hip control to the rig.

        Args:
            ctrl (str): Name of the left hip control.
            ctrl_id (int): ID of the left hip control effector.
        """
        self.add_ctrl(ctrl, ctrl_id)

    def add_leftKnee_ctrl(self, ctrl, ctrl_id=humanIK_ctrl_dict['LeftKnee']):
        """Adds the left knee control to the rig.

        Args:
            ctrl (str): Name of the left knee control.
            ctrl_id (int): ID of the left knee control effector.
        """
        self.add_ctrl(ctrl, ctrl_id)

    def add_leftAnkle_ctrl(self, ctrl, ctrl_id=humanIK_ctrl_dict['LeftAnkle']):
        """Adds the left ankle control to the rig.

        Args:
            ctrl (str): Name of the left ankle control.
            ctrl_id (int): ID of the left ankle control effector.
        """
        self.add_ctrl(ctrl, ctrl_id)

    def add_rightClavicle_ctrl(self, ctrl, ctrl_id=humanIK_ctrl_dict['RightClavicle']):
        """Adds the right clavicle control to the rig.

        Args:
            ctrl (str): Name of the right clavicle control.
            ctrl_id (int): ID of the right clavicle control effector.
        """
        self.add_ctrl(ctrl, ctrl_id)

    def add_rightShoulder_ctrl(self, ctrl, ctrl_id=humanIK_ctrl_dict['RightShoulder']):
        """Adds the right shoulder control to the rig.

        Args:
            ctrl (str): Name of the right shoulder control.
            ctrl_id (int): ID of the right shoulder control effector.
        """
        self.add_ctrl(ctrl, ctrl_id)

    def add_rightElbow_ctrl(self, ctrl, ctrl_id=humanIK_ctrl_dict['RightElbow']):
        """Adds the right elbow control to the rig.

        Args:
            ctrl (str): Name of the right elbow control.
            ctrl_id (int): ID of the right elbow control effector.
        """
        self.add_ctrl(ctrl, ctrl_id)

    def add_rightHand_ctrl(self, ctrl, ctrl_id=humanIK_ctrl_dict['RightHand']):
        """Adds the right hand control to the rig.

        Args:
            ctrl (str): Name of the right hand control.
            ctrl_id (int): ID of the right hand control effector.
        """
        self.add_ctrl(ctrl, ctrl_id)

    def add_rightHip_ctrl(self, ctrl, ctrl_id=humanIK_ctrl_dict['RightUpLeg']):
        """Adds the right hip control to the rig.

        Args:
            ctrl (str): Name of the right hip control.
            ctrl_id (int): ID of the right hip control effector.
        """
        self.add_ctrl(ctrl, ctrl_id)

    def add_rightKnee_ctrl(self, ctrl, ctrl_id=humanIK_ctrl_dict['RightKnee']):
        """Adds the right knee control to the rig.

        Args:
            ctrl (str): Name of the right knee control.
            ctrl_id (int): ID of the right knee control effector.
        """
        self.add_ctrl(ctrl, ctrl_id)

    def add_rightAnkle_ctrl(self, ctrl, ctrl_id=humanIK_ctrl_dict['RightAnkle']):
        """Adds the right ankle control to the rig.

        Args:
            ctrl (str): Name of the right ankle control.
            ctrl_id (int): ID of the right ankle control effector.
        """
        self.add_ctrl(ctrl, ctrl_id)

    def add_leftHandThumb_ctrl(self, ctrl_list, ctrl_id_list=humanIK_ctrl_dict['LeftHandThumb']):
        """Adds left hand thumb controls to the rig.

        Args:
            ctrl_list (list): List of left hand thumb control names.
            ctrl_id_list (list): List of left hand thumb control effector IDs.
        """
        for i, ctrl in enumerate(ctrl_list):
            self.add_ctrl(ctrl, ctrl_id_list[i])

    def add_leftHandIndex_ctrl(self, ctrl_list, ctrl_id_list=humanIK_ctrl_dict['LeftHandIndex']):
        """Adds left hand index controls to the rig.

        Args:
            ctrl_list (list): List of left hand index control names.
            ctrl_id_list (list): List of left hand index control effector IDs.
        """
        for i, ctrl in enumerate(ctrl_list):
            self.add_ctrl(ctrl, ctrl_id_list[i])

    def add_leftHandMiddle_ctrl(self, ctrl_list, ctrl_id_list=humanIK_ctrl_dict['LeftHandMiddle']):
        """Adds left hand middle controls to the rig.

        Args:
            ctrl_list (list): List of left hand middle control names.
            ctrl_id_list (list): List of left hand middle control effector IDs.
        """
        for i, ctrl in enumerate(ctrl_list):
            self.add_ctrl(ctrl, ctrl_id_list[i])

    def add_leftHandRing_ctrl(self, ctrl_list, ctrl_id_list=humanIK_ctrl_dict['LeftHandRing']):
        """Adds left hand ring controls to the rig.

        Args:
            ctrl_list (list): List of left hand ring control names.
            ctrl_id_list (list): List of left hand ring control effector IDs.
        """
        for i, ctrl in enumerate(ctrl_list):
            self.add_ctrl(ctrl, ctrl_id_list[i])

    def add_leftHandPinky_ctrl(self, ctrl_list, ctrl_id_list=humanIK_ctrl_dict['LeftHandPinky']):
        """Adds left hand pinky controls to the rig.

        Args:
            ctrl_list (list): List of left hand pinky control names.
            ctrl_id_list (list): List of left hand pinky control effector IDs.
        """
        for i, ctrl in enumerate(ctrl_list):
            self.add_ctrl(ctrl, ctrl_id_list[i])

    def add_rightHandThumb_ctrl(self, ctrl_list, ctrl_id_list=humanIK_ctrl_dict['RightHandThumb']):
        """Adds right hand thumb controls to the rig.

        Args:
            ctrl_list (list): List of right hand thumb control names.
            ctrl_id_list (list): List of right hand thumb control effector IDs.
        """
        for i, ctrl in enumerate(ctrl_list):
            self.add_ctrl(ctrl, ctrl_id_list[i])

    def add_rightHandIndex_ctrl(self, ctrl_list, ctrl_id_list=humanIK_ctrl_dict['RightHandIndex']):
        """Adds right hand index controls to the rig.

        Args:
            ctrl_list (list): List of right hand index control names.
            ctrl_id_list (list): List of right hand index control effector IDs.
        """
        for i, ctrl in enumerate(ctrl_list):
            self.add_ctrl(ctrl, ctrl_id_list[i])

    def add_rightHandMiddle_ctrl(self, ctrl_list, ctrl_id_list=humanIK_ctrl_dict['RightHandMiddle']):
        """Adds right hand middle controls to the rig.

        Args:
            ctrl_list (list): List of right hand middle control names.
            ctrl_id_list (list): List of right hand middle control effector IDs.
        """
        for i, ctrl in enumerate(ctrl_list):
            self.add_ctrl(ctrl, ctrl_id_list[i])

    def add_rightHandRing_ctrl(self, ctrl_list, ctrl_id_list=humanIK_ctrl_dict['RightHandRing']):
        """Adds right hand ring controls to the rig.

        Args:
            ctrl_list (list): List of right hand ring control names.
            ctrl_id_list (list): List of right hand ring control effector IDs.
        """
        for i, ctrl in enumerate(ctrl_list):
            self.add_ctrl(ctrl, ctrl_id_list[i])

    def add_rightHandPinky_ctrl(self, ctrl_list, ctrl_id_list=humanIK_ctrl_dict['RightHandPinky']):
        """Adds right hand pinky controls to the rig.

        Args:
            ctrl_list (list): List of right hand pinky control names.
            ctrl_id_list (list): List of right hand pinky control effector IDs.
        """
        for i, ctrl in enumerate(ctrl_list):
            self.add_ctrl(ctrl, ctrl_id_list[i])




if __name__ == "__main__":
    char_name = 'Sylvanas'
    humanIk = HumanIK(char_name + '_FK', custom_ctrl_definition=True, use_ik=False, skip_reference_joint=True)
    humanIk = HumanIK(char_name + '_IK', custom_ctrl_definition=True, use_ik=True, skip_reference_joint=True)
    humanIk = HumanIK(char_name + '_Hybrid', custom_ctrl_definition=True, use_ik=False, use_hybrid=True,
                      skip_reference_joint=True)

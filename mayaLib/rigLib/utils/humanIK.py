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
        import sys
        import os

        LOCAL_PATH = r"C:/Users/" + os.getlogin() + "/Documents/maya/Plug-ins/arise_main"
        version_folder = 'py_' + str(sys.version_info.major) + '_' + str(sys.version_info.minor)
        path = os.path.join(LOCAL_PATH, version_folder)

        if path not in sys.path:
            sys.path.append(path)

        from arise.utils.ctrls_utils import apply_zero_pose_all

        apply_zero_pose_all(silent=True)

    def _arms_parallel_to_grid(self):
        pass

    def go_to_T_pose(self, template):
        if template == 'arise':
            self._arise_T_pose()
        else:
            self._arms_parallel_to_grid()


    def define_skeleton(self, rig_data=None, skip_reference_joint=True):
        if not rig_data:
            rig_data = self.rig_data

        if rig_data['joints']['Reference'] and not skip_reference_joint:
            self.add_reference(rig_data['joints']['Reference'])
        if rig_data['joints']['Hips']:
            self.add_hip(rig_data['joints']['Hips'])
        if rig_data['joints']['Spine']:
            self.add_spine(rig_data['joints']['Spine'])
        if rig_data['joints']['Neck']:
            self.add_neck(rig_data['joints']['Neck'])
        if rig_data['joints']['Head']:
            self.add_head(rig_data['joints']['Head'])
        if rig_data['joints']['LeftArm']:
            self.add_left_arm(*rig_data['joints']['LeftArm'])
        if rig_data['joints']['LeftLeg']:
            self.add_left_leg(*rig_data['joints']['LeftLeg'])
        if rig_data['joints']['RightArm']:
            self.add_right_arm(*rig_data['joints']['RightArm'])
        if rig_data['joints']['RightLeg']:
            self.add_right_leg(*rig_data['joints']['RightLeg'])

        if rig_data['joints']['LeftHandThumb']:
            self.add_leftHandThumb(rig_data['joints']['LeftHandThumb'])
        if rig_data['joints']['LeftHandIndex']:
            self.add_leftHandIndex(rig_data['joints']['LeftHandIndex'])
        if rig_data['joints']['LeftHandMiddle']:
            self.add_leftHandMiddle(rig_data['joints']['LeftHandMiddle'])
        if rig_data['joints']['LeftHandRing']:
            self.add_leftHandRing(rig_data['joints']['LeftHandRing'])
        if rig_data['joints']['LeftHandPinky']:
            self.add_leftHandPinky(rig_data['joints']['LeftHandPinky'])
        if rig_data['joints']['RightHandThumb']:
            self.add_rightHandThumb(rig_data['joints']['RightHandThumb'])
        if rig_data['joints']['RightHandIndex']:
            self.add_rightHandIndex(rig_data['joints']['RightHandIndex'])
        if rig_data['joints']['RightHandMiddle']:
            self.add_rightHandMiddle(rig_data['joints']['RightHandMiddle'])
        if rig_data['joints']['RightHandRing']:
            self.add_rightHandRing(rig_data['joints']['RightHandRing'])
        if rig_data['joints']['RightHandPinky']:
            self.add_rightHandPinky(rig_data['joints']['RightHandPinky'])

    def define_custom_ctrls(self, rig_data, use_ik=True, use_hybrid=True):
        if not rig_data:
            rig_data = self.rig_data

        self.createCustomRigMapping()

        if rig_data['ctrls']['Hip']:
            self.add_hip_ctrl(rig_data['ctrls']['Hip'])
        if rig_data['ctrls']['Spine']:
            self.add_spine_ctrl(rig_data['ctrls']['Spine'])
        if rig_data['ctrls']['Chest']:
            self.add_chest_ctrl(rig_data['ctrls']['Chest'])
        if rig_data['ctrls']['Neck']:
            self.add_neck_ctrl(rig_data['ctrls']['Neck'])
        if rig_data['ctrls']['Head']:
            self.add_head_ctrl(rig_data['ctrls']['Head'])
        if rig_data['ctrls']['LeftClavicle']:
            self.add_leftClavicle_ctrl(rig_data['ctrls']['LeftClavicle'])
        if rig_data['ctrls']['RightClavicle']:
            self.add_rightClavicle_ctrl(rig_data['ctrls']['RightClavicle'])

        if not use_ik and not use_hybrid:
            if rig_data['ctrls']['LeftShoulder']:
                self.add_leftShoulder_ctrl(rig_data['ctrls']['LeftShoulder'])
            if rig_data['ctrls']['LeftElbow']:
                self.add_leftElbow_ctrl(rig_data['ctrls']['LeftElbow'])
            if rig_data['ctrls']['LeftHand'][0]:
                self.add_leftHand_ctrl(rig_data['ctrls']['LeftHand'][0])

            if rig_data['ctrls']['LeftUpLeg']:
                self.add_leftHip_ctrl(rig_data['ctrls']['LeftUpLeg'])
            if rig_data['ctrls']['LeftKnee']:
                self.add_leftKnee_ctrl(rig_data['ctrls']['LeftKnee'])
            if rig_data['ctrls']['LeftAnkle'][0]:
                self.add_leftAnkle_ctrl(rig_data['ctrls']['LeftAnkle'][0])

            if rig_data['ctrls']['RightShoulder']:
                self.add_rightShoulder_ctrl(rig_data['ctrls']['RightShoulder'])
            if rig_data['ctrls']['RightElbow']:
                self.add_rightElbow_ctrl(rig_data['ctrls']['RightElbow'])
            if rig_data['ctrls']['RightHand'][0]:
                self.add_rightHand_ctrl(rig_data['ctrls']['RightHand'][0])

            if rig_data['ctrls']['RightUpLeg']:
                self.add_rightHip_ctrl(rig_data['ctrls']['RightUpLeg'])
            if rig_data['ctrls']['RightKnee']:
                self.add_rightKnee_ctrl(rig_data['ctrls']['RightKnee'])
            if rig_data['ctrls']['RightAnkle'][0]:
                self.add_rightAnkle_ctrl(rig_data['ctrls']['RightAnkle'][0])

        if use_ik and not use_hybrid:
            if rig_data['ctrls']['LeftHand'][1]:
                self.add_leftHand_ctrl(rig_data['ctrls']['LeftHand'][1])

            if rig_data['ctrls']['LeftAnkle'][1]:
                self.add_leftAnkle_ctrl(rig_data['ctrls']['LeftAnkle'][1])

            if rig_data['ctrls']['RightHand'][1]:
                self.add_rightHand_ctrl(rig_data['ctrls']['RightHand'][1])

            if rig_data['ctrls']['RightAnkle'][1]:
                self.add_rightAnkle_ctrl(rig_data['ctrls']['RightAnkle'][1])

        if use_hybrid:
            if rig_data['ctrls']['LeftShoulder']:
                self.add_leftShoulder_ctrl(rig_data['ctrls']['LeftShoulder'])
            if rig_data['ctrls']['LeftElbow']:
                self.add_leftElbow_ctrl(rig_data['ctrls']['LeftElbow'])
            if rig_data['ctrls']['LeftHand'][0]:
                self.add_leftHand_ctrl(rig_data['ctrls']['LeftHand'][0])

            if rig_data['ctrls']['RightShoulder']:
                self.add_rightShoulder_ctrl(rig_data['ctrls']['RightShoulder'])
            if rig_data['ctrls']['RightElbow']:
                self.add_rightElbow_ctrl(rig_data['ctrls']['RightElbow'])
            if rig_data['ctrls']['RightHand'][0]:
                self.add_rightHand_ctrl(rig_data['ctrls']['RightHand'][0])

            if rig_data['ctrls']['LeftAnkle'][1]:
                self.add_leftAnkle_ctrl(rig_data['ctrls']['LeftAnkle'][1])

            if rig_data['ctrls']['RightAnkle'][1]:
                self.add_rightAnkle_ctrl(rig_data['ctrls']['RightAnkle'][1])

        if rig_data['ctrls']['LeftHandThumb']:
            self.add_leftHandThumb_ctrl(rig_data['ctrls']['LeftHandThumb'])
        if rig_data['ctrls']['LeftHandIndex']:
            self.add_leftHandIndex_ctrl(rig_data['ctrls']['LeftHandIndex'])
        if rig_data['ctrls']['LeftHandMiddle']:
            self.add_leftHandMiddle_ctrl(rig_data['ctrls']['LeftHandMiddle'])
        if rig_data['ctrls']['LeftHandRing']:
            self.add_leftHandRing_ctrl(rig_data['ctrls']['LeftHandRing'])
        if rig_data['ctrls']['LeftHandPinky']:
            self.add_leftHandPinky_ctrl(rig_data['ctrls']['LeftHandPinky'])

        if rig_data['ctrls']['RightHandThumb']:
            self.add_rightHandThumb_ctrl(rig_data['ctrls']['RightHandThumb'])
        if rig_data['ctrls']['RightHandIndex']:
            self.add_rightHandIndex_ctrl(rig_data['ctrls']['RightHandIndex'])
        if rig_data['ctrls']['RightHandMiddle']:
            self.add_rightHandMiddle_ctrl(rig_data['ctrls']['RightHandMiddle'])
        if rig_data['ctrls']['RightHandRing']:
            self.add_rightHandRing_ctrl(rig_data['ctrls']['RightHandRing'])
        if rig_data['ctrls']['RightHandPinky']:
            self.add_rightHandPinky_ctrl(rig_data['ctrls']['RightHandPinky'])

    def setCharacterObject(self, joint, joint_id):
        if pm.objExists(joint):
            joint = str(pm.ls(joint)[-1].name())
            mel.eval('setCharacterObject("' + joint + '", "' + self.charecter_name + '", "' + str(joint_id) + '", 0);')

    def add_reference(self, joint, joint_id=humanIK_joint_dict['Reference']):
        self.setCharacterObject(joint, joint_id)

    def add_hip(self, joint, joint_id=humanIK_joint_dict['Hips']):
        self.setCharacterObject(joint, joint_id)

    def add_spine(self, joint_list, joint_id_list=humanIK_joint_dict['Spine']):
        for i, joint in enumerate(joint_list):
            self.setCharacterObject(joint, joint_id_list[i])

    def add_neck(self, joint_list, joint_id_list=humanIK_joint_dict['Neck']):
        for i, joint in enumerate(joint_list):
            self.setCharacterObject(joint, joint_id_list[i])

    def add_head(self, joint, joint_id=humanIK_joint_dict['Head']):
        self.setCharacterObject(joint, joint_id)

    def add_leftUpLeg(self, joint, joint_id=humanIK_joint_dict['LeftUpLeg']):
        self.setCharacterObject(joint, joint_id)

    def add_leftLeg(self, joint, joint_id=humanIK_joint_dict['LeftLeg']):
        self.setCharacterObject(joint, joint_id)

    def add_leftFoot(self, joint, joint_id=humanIK_joint_dict['LeftFoot']):
        self.setCharacterObject(joint, joint_id)

    def add_leftShoulder(self, joint, joint_id=humanIK_joint_dict['LeftShoulder']):
        self.setCharacterObject(joint, joint_id)

    def add_leftArm(self, joint, joint_id=humanIK_joint_dict['LeftArm']):
        self.setCharacterObject(joint, joint_id)

    def add_leftForeArm(self, joint, joint_id=humanIK_joint_dict['LeftForeArm']):
        self.setCharacterObject(joint, joint_id)

    def add_leftHand(self, joint, joint_id=humanIK_joint_dict['LeftHand']):
        self.setCharacterObject(joint, joint_id)

    def add_rightUpLeg(self, joint, joint_id=humanIK_joint_dict['RightUpLeg']):
        self.setCharacterObject(joint, joint_id)

    def add_rightLeg(self, joint, joint_id=humanIK_joint_dict['RightLeg']):
        self.setCharacterObject(joint, joint_id)

    def add_rightFoot(self, joint, joint_id=humanIK_joint_dict['RightFoot']):
        self.setCharacterObject(joint, joint_id)

    def add_rightShoulder(self, joint, joint_id=humanIK_joint_dict['RightShoulder']):
        self.setCharacterObject(joint, joint_id)

    def add_rightArm(self, joint, joint_id=humanIK_joint_dict['RightArm']):
        self.setCharacterObject(joint, joint_id)

    def add_rightForeArm(self, joint, joint_id=humanIK_joint_dict['RightForeArm']):
        self.setCharacterObject(joint, joint_id)

    def add_rightHand(self, joint, joint_id=humanIK_joint_dict['RightHand']):
        self.setCharacterObject(joint, joint_id)

    def add_leftToeBase(self, joint, joint_id=humanIK_joint_dict['LeftToeBase']):
        self.setCharacterObject(joint, joint_id)

    def add_rightToeBase(self, joint, joint_id=humanIK_joint_dict['RightToeBase']):
        self.setCharacterObject(joint, joint_id)

    def add_leftHandThumb(self, joint_list, joint_id_list=humanIK_joint_dict['LeftHandThumb']):
        for i, joint in enumerate(joint_list):
            self.setCharacterObject(joint, joint_id_list[i])

    def add_leftHandIndex(self, joint_list, joint_id_list=humanIK_joint_dict['LeftHandIndex']):
        for i, joint in enumerate(joint_list):
            self.setCharacterObject(joint, joint_id_list[i])

    def add_leftHandMiddle(self, joint_list, joint_id_list=humanIK_joint_dict['LeftHandMiddle']):
        for i, joint in enumerate(joint_list):
            self.setCharacterObject(joint, joint_id_list[i])

    def add_leftHandRing(self, joint_list, joint_id_list=humanIK_joint_dict['LeftHandRing']):
        for i, joint in enumerate(joint_list):
            self.setCharacterObject(joint, joint_id_list[i])

    def add_leftHandPinky(self, joint_list, joint_id_list=humanIK_joint_dict['LeftHandPinky']):
        for i, joint in enumerate(joint_list):
            self.setCharacterObject(joint, joint_id_list[i])

    def add_rightHandThumb(self, joint_list, joint_id_list=humanIK_joint_dict['RightHandThumb']):
        for i, joint in enumerate(joint_list):
            self.setCharacterObject(joint, joint_id_list[i])

    def add_rightHandIndex(self, joint_list, joint_id_list=humanIK_joint_dict['RightHandIndex']):
        for i, joint in enumerate(joint_list):
            self.setCharacterObject(joint, joint_id_list[i])

    def add_rightHandMiddle(self, joint_list, joint_id_list=humanIK_joint_dict['RightHandMiddle']):
        for i, joint in enumerate(joint_list):
            self.setCharacterObject(joint, joint_id_list[i])

    def add_rightHandRing(self, joint_list, joint_id_list=humanIK_joint_dict['RightHandRing']):
        for i, joint in enumerate(joint_list):
            self.setCharacterObject(joint, joint_id_list[i])

    def add_rightHandPinky(self, joint_list, joint_id_list=humanIK_joint_dict['RightHandPinky']):
        for i, joint in enumerate(joint_list):
            self.setCharacterObject(joint, joint_id_list[i])

    def add_left_arm(self, clavicle=None, shoulder=None, forearm=None, hand=None):
        if clavicle:
            self.add_leftShoulder(clavicle)
        if shoulder:
            self.add_leftArm(shoulder)
        if forearm:
            self.add_leftForeArm(forearm)
        if hand:
            self.add_leftHand(hand)

    def add_right_arm(self, clavicle=None, shoulder=None, forearm=None, hand=None):
        if clavicle:
            self.add_rightShoulder(clavicle)
        if shoulder:
            self.add_rightArm(shoulder)
        if forearm:
            self.add_rightForeArm(forearm)
        if hand:
            self.add_rightHand(hand)

    def add_left_leg(self, upper_leg=None, leg=None, foot=None, ball=None):
        if upper_leg:
            self.add_leftUpLeg(upper_leg)
        if leg:
            self.add_leftLeg(leg)
        if foot:
            self.add_leftFoot(foot)
        if ball:
            self.add_leftToeBase(ball)

    def add_right_leg(self, upper_leg=None, leg=None, foot=None, ball=None):
        if upper_leg:
            self.add_rightUpLeg(upper_leg)
        if leg:
            self.add_rightLeg(leg)
        if foot:
            self.add_rightFoot(foot)
        if ball:
            self.add_rightToeBase(ball)

    def loadCustomRigTemplate(self):
        mel.eval('hikLoadCustomRigUIConfiguration();')

    def createCustomRigMapping(self):
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
        if pm.objExists(ctrl):
            pm.select(ctrl)
            mel.eval('hikCustomRigAssignEffector ' + str(ctrl_id) + ';')

    def add_hip_ctrl(self, ctrl, ctrl_id=humanIK_ctrl_dict['Hip']):
        self.add_ctrl(ctrl, ctrl_id)

    def add_spine_ctrl(self, ctrl_list, ctrl_id_list=humanIK_ctrl_dict['Spine']):
        for i, ctrl in enumerate(ctrl_list):
            self.add_ctrl(ctrl, ctrl_id_list[i])

    def add_chest_ctrl(self, ctrl, ctrl_id=humanIK_ctrl_dict['Chest']):
        self.add_ctrl(ctrl, ctrl_id)

    def add_neck_ctrl(self, ctrl, ctrl_id=humanIK_ctrl_dict['Neck']):
        self.add_ctrl(ctrl, ctrl_id)

    def add_head_ctrl(self, ctrl, ctrl_id=humanIK_ctrl_dict['Head']):
        self.add_ctrl(ctrl, ctrl_id)

    def add_leftClavicle_ctrl(self, ctrl, ctrl_id=humanIK_ctrl_dict['LeftClavicle']):
        self.add_ctrl(ctrl, ctrl_id)

    def add_leftShoulder_ctrl(self, ctrl, ctrl_id=humanIK_ctrl_dict['LeftShoulder']):
        self.add_ctrl(ctrl, ctrl_id)

    def add_leftElbow_ctrl(self, ctrl, ctrl_id=humanIK_ctrl_dict['LeftElbow']):
        self.add_ctrl(ctrl, ctrl_id)

    def add_leftHand_ctrl(self, ctrl, ctrl_id=humanIK_ctrl_dict['LeftHand']):
        self.add_ctrl(ctrl, ctrl_id)

    def add_leftHip_ctrl(self, ctrl, ctrl_id=humanIK_ctrl_dict['LeftUpLeg']):
        self.add_ctrl(ctrl, ctrl_id)

    def add_leftKnee_ctrl(self, ctrl, ctrl_id=humanIK_ctrl_dict['LeftKnee']):
        self.add_ctrl(ctrl, ctrl_id)

    def add_leftAnkle_ctrl(self, ctrl, ctrl_id=humanIK_ctrl_dict['LeftAnkle']):
        self.add_ctrl(ctrl, ctrl_id)

    def add_rightClavicle_ctrl(self, ctrl, ctrl_id=humanIK_ctrl_dict['RightClavicle']):
        self.add_ctrl(ctrl, ctrl_id)

    def add_rightShoulder_ctrl(self, ctrl, ctrl_id=humanIK_ctrl_dict['RightShoulder']):
        self.add_ctrl(ctrl, ctrl_id)

    def add_rightElbow_ctrl(self, ctrl, ctrl_id=humanIK_ctrl_dict['RightElbow']):
        self.add_ctrl(ctrl, ctrl_id)

    def add_rightHand_ctrl(self, ctrl, ctrl_id=humanIK_ctrl_dict['RightHand']):
        self.add_ctrl(ctrl, ctrl_id)

    def add_rightHip_ctrl(self, ctrl, ctrl_id=humanIK_ctrl_dict['RightUpLeg']):
        self.add_ctrl(ctrl, ctrl_id)

    def add_rightKnee_ctrl(self, ctrl, ctrl_id=humanIK_ctrl_dict['RightKnee']):
        self.add_ctrl(ctrl, ctrl_id)

    def add_rightAnkle_ctrl(self, ctrl, ctrl_id=humanIK_ctrl_dict['RightAnkle']):
        self.add_ctrl(ctrl, ctrl_id)

    def add_leftHandThumb_ctrl(self, ctrl_list, ctrl_id_list=humanIK_ctrl_dict['LeftHandThumb']):
        for i, ctrl in enumerate(ctrl_list):
            self.add_ctrl(ctrl, ctrl_id_list[i])

    def add_leftHandIndex_ctrl(self, ctrl_list, ctrl_id_list=humanIK_ctrl_dict['LeftHandIndex']):
        for i, ctrl in enumerate(ctrl_list):
            self.add_ctrl(ctrl, ctrl_id_list[i])

    def add_leftHandMiddle_ctrl(self, ctrl_list, ctrl_id_list=humanIK_ctrl_dict['LeftHandMiddle']):
        for i, ctrl in enumerate(ctrl_list):
            self.add_ctrl(ctrl, ctrl_id_list[i])

    def add_leftHandRing_ctrl(self, ctrl_list, ctrl_id_list=humanIK_ctrl_dict['LeftHandRing']):
        for i, ctrl in enumerate(ctrl_list):
            self.add_ctrl(ctrl, ctrl_id_list[i])

    def add_leftHandPinky_ctrl(self, ctrl_list, ctrl_id_list=humanIK_ctrl_dict['LeftHandPinky']):
        for i, ctrl in enumerate(ctrl_list):
            self.add_ctrl(ctrl, ctrl_id_list[i])

    def add_rightHandThumb_ctrl(self, ctrl_list, ctrl_id_list=humanIK_ctrl_dict['RightHandThumb']):
        for i, ctrl in enumerate(ctrl_list):
            self.add_ctrl(ctrl, ctrl_id_list[i])

    def add_rightHandIndex_ctrl(self, ctrl_list, ctrl_id_list=humanIK_ctrl_dict['RightHandIndex']):
        for i, ctrl in enumerate(ctrl_list):
            self.add_ctrl(ctrl, ctrl_id_list[i])

    def add_rightHandMiddle_ctrl(self, ctrl_list, ctrl_id_list=humanIK_ctrl_dict['RightHandMiddle']):
        for i, ctrl in enumerate(ctrl_list):
            self.add_ctrl(ctrl, ctrl_id_list[i])

    def add_rightHandRing_ctrl(self, ctrl_list, ctrl_id_list=humanIK_ctrl_dict['RightHandRing']):
        for i, ctrl in enumerate(ctrl_list):
            self.add_ctrl(ctrl, ctrl_id_list[i])

    def add_rightHandPinky_ctrl(self, ctrl_list, ctrl_id_list=humanIK_ctrl_dict['RightHandPinky']):
        for i, ctrl in enumerate(ctrl_list):
            self.add_ctrl(ctrl, ctrl_id_list[i])




if __name__ == "__main__":
    char_name = 'Sylvanas'
    humanIk = HumanIK(char_name + '_FK', custom_ctrl_definition=True, use_ik=False, skip_reference_joint=True)
    humanIk = HumanIK(char_name + '_IK', custom_ctrl_definition=True, use_ik=True, skip_reference_joint=True)
    humanIk = HumanIK(char_name + '_Hybrid', custom_ctrl_definition=True, use_ik=False, use_hybrid=True,
                      skip_reference_joint=True)

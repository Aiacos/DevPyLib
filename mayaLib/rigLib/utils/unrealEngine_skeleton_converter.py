import pymel.core as pm

reference_joint_default = 'Base_main_FS_jnt'
hip_joint_joint_default = 'M_Spine_pelvis_FS_jnt'
spine_joint_list_default = ['M_Spine_spine_ribbon_0_driven_FS_jnt', 'M_Spine_spine_ribbon_1_driven_FS_jnt', 'M_Spine_spine_ribbon_2_driven_FS_jnt', 'M_Spine_spine_ribbon_3_driven_FS_jnt', 'M_Spine_spine_ribbon_4_driven_FS_jnt', 'M_Spine_chest_FS_jnt']
neck_joint_list_default = ['M_Head_neck_root_FS_jnt', 'M_Head_ribbon_driven_0_FS_jnt', 'M_Head_ribbon_driven_1_FS_jnt', 'M_Head_ribbon_driven_2_FS_jnt', 'M_Head_ribbon_driven_3_FS_jnt']
head_joint_joint_default = 'M_Head_head_FS_jnt'
left_arm_joint_list_default = ['L_Arm_base_FS_jnt', 'L_Arm_ribbon_upper_driven_0_FS_jnt', 'L_Arm_ribbon_lower_driven_0_FS_jnt', 'L_Arm_tip_FS_jnt']
left_leg_joint_list_default = ['L_Leg_ribbon_upper_driven_0_FS_jnt', 'L_Leg_ribbon_lower_driven_0_FS_jnt', 'L_Leg_tip_FS_jnt', 'L_Leg_toes_root_FS_jnt']
right_arm_joint_list_default = ['R_Arm_base_FS_jnt', 'R_Arm_ribbon_upper_driven_0_FS_jnt', 'R_Arm_ribbon_lower_driven_0_FS_jnt', 'R_Arm_tip_FS_jnt']
right_leg_joint_list_default = ['R_Leg_ribbon_upper_driven_0_FS_jnt', 'R_Leg_ribbon_lower_driven_0_FS_jnt', 'R_Leg_tip_FS_jnt', 'R_Leg_toes_root_FS_jnt']

left_hand_thumb_joint_list_default = ['L_Fingers_thumb_0_0_FS_jnt', 'L_Fingers_thumb_0_1_FS_jnt', 'L_Fingers_thumb_0_2_FS_jnt']
left_hand_index_joint_list_default = ['L_Fingers_finger_0_0_FS_jnt', 'L_Fingers_finger_0_1_FS_jnt', 'L_Fingers_finger_0_2_FS_jnt', 'L_Fingers_finger_0_3_FS_jnt']
left_hand_middle_joint_list_default = ['L_Fingers_finger_1_0_FS_jnt', 'L_Fingers_finger_1_1_FS_jnt', 'L_Fingers_finger_1_2_FS_jnt', 'L_Fingers_finger_1_3_FS_jnt']
left_hand_ring_joint_list_default = ['L_Fingers_finger_2_0_FS_jnt', 'L_Fingers_finger_2_1_FS_jnt', 'L_Fingers_finger_2_2_FS_jnt', 'L_Fingers_finger_2_3_FS_jnt']
left_hand_pinky_joint_list_default = ['L_Fingers_finger_3_0_FS_jnt', 'L_Fingers_finger_3_1_FS_jnt', 'L_Fingers_finger_3_2_FS_jnt', 'L_Fingers_finger_3_3_FS_jnt']

right_hand_thumb_joint_list_default = ['L_Fingers_thumb_0_0_FS_jnt', 'L_Fingers_thumb_0_1_FS_jnt', 'L_Fingers_thumb_0_2_FS_jnt']
right_hand_index_joint_list_default = ['L_Fingers_finger_0_0_FS_jnt', 'L_Fingers_finger_0_1_FS_jnt', 'L_Fingers_finger_0_2_FS_jnt', 'L_Fingers_finger_0_3_FS_jnt']
right_hand_middle_joint_list_default = ['L_Fingers_finger_1_0_FS_jnt', 'L_Fingers_finger_1_1_FS_jnt', 'L_Fingers_finger_1_2_FS_jnt', 'L_Fingers_finger_1_3_FS_jnt']
right_hand_ring_joint_list_default = ['L_Fingers_finger_2_0_FS_jnt', 'L_Fingers_finger_2_1_FS_jnt', 'L_Fingers_finger_2_2_FS_jnt', 'L_Fingers_finger_2_3_FS_jnt']
right_hand_pinky_joint_list_default = ['L_Fingers_finger_3_0_FS_jnt', 'L_Fingers_finger_3_1_FS_jnt', 'L_Fingers_finger_3_2_FS_jnt', 'L_Fingers_finger_3_3_FS_jnt']

class UnrealEngine_Skeleton(object):
    
    humanIK_joint_dict = {
        'Reference': 'root',
        'Hips': 'pelvis',
        'Spine': ('spine_01', 'spine_02', 'spine_03', 'spine_04', 'spine_05'),
        'Neck': ('neck_01', 'neck_02'),
        'Head': 'head',
        'LeftUpLeg': 'thigh_l',
        'LeftLeg': 'calf_l',
        'LeftFoot': 'foot_l',
        'LeftToeBase': 'ball_l',
        'RightUpLeg': 'thigh_r',
        'RightLeg': 'calf_r',
        'RightFoot': 'foor_r',
        'RightToeBase': 'ball_r',
        'LeftShoulder': 'clavicle_l',
        'LeftArm': 'upperarm_l',
        'LeftForeArm': 'lowerarm_l',
        'LeftHand': 'hand_l',
        'RightShoulder': 'clavicle_r',
        'RightArm': 'upperarm_r',
        'RightForeArm': 'lowerarm_r',
        'RightHand': 'hand_r',
        'LeftHandThumb': ('thumb_01_l', 'thumb_02_l', 'thumb_03_l'),
        'LeftHandIndex': ('index_metacarpal_l', 'index_01_l', 'index_02_l', 'index_03_l'),
        'LeftHandMiddle': ('middle_metacarpal_l', 'middle_01_l', 'middle_02_l', 'middle_03_l'),
        'LeftHandRing': ('ring_metacarpal_l', 'ring_01_l', 'ring_02_l', 'ring_03_l'),
        'LeftHandPinky': ('pinky_metacarpal_l', 'pinky_01_l', 'pinky_02_l', 'pinky_03_l'),
        'RightHandThumb': ('thumb_01_r', 'thumb_02_r', 'thumb_03_r'),
        'RightHandIndex': ('index_metacarpal_r', 'index_01_r', 'index_02_r', 'index_03_r'),
        'RightHandMiddle': ('middle_metacarpal_r', 'middle_01_r', 'middle_02_r', 'middle_03_r'),
        'RightHandRing': ('ring_metacarpal_r', 'ring_01_r', 'ring_02_r', 'ring_03_r'),
        'RightHandPinky': ('pinky_metacarpal_r', 'pinky_01_r', 'pinky_02_r', 'pinky_03_r'),
    }
    def __init__(self, reference_joint=reference_joint_default,
                 hip_joint=hip_joint_joint_default,
                 spine_joint_list=spine_joint_list_default,
                 neck_joint_list=neck_joint_list_default,
                 head_joint=head_joint_joint_default,
                 left_arm_joint_list=left_arm_joint_list_default,
                 left_leg_joint_list=left_leg_joint_list_default,
                 right_arm_joint_list=right_arm_joint_list_default,
                 right_leg_joint_list=right_leg_joint_list_default,
                 left_hand_thumb_joint_list=left_hand_thumb_joint_list_default,
                 left_hand_index_joint_list=left_hand_index_joint_list_default,
                 left_hand_middle_joint_list=left_hand_middle_joint_list_default,
                 left_hand_ring_joint_list=left_hand_ring_joint_list_default,
                 left_hand_pinky_joint_list=left_hand_pinky_joint_list_default,
                 right_hand_thumb_joint_list=right_hand_thumb_joint_list_default,
                 right_hand_index_joint_list=right_hand_index_joint_list_default,
                 right_hand_middle_joint_list=right_hand_middle_joint_list_default,
                 right_hand_ring_joint_list=right_hand_ring_joint_list_default,
                 right_hand_pinky_joint_list=right_hand_pinky_joint_list_default):
        
        # Root
        pm.rename(reference_joint, self.humanIK_joint_dict['Reference'])
        
        # Hip
        pm.rename(hip_joint, self.humanIK_joint_dict['Hips'])
        
        # Spine
        for jnt, name in zip(spine_joint_list, self.humanIK_joint_dict['Spine']): # more joint in Arise rig
            pm.rename(jnt, name)
        
        # Neck
        for jnt, name in zip(neck_joint_list, self.humanIK_joint_dict['Neck']): # more joint in Arise rig
            pm.rename(jnt, name)
        
        # Head
        pm.rename(head_joint, self.humanIK_joint_dict['Head'])
        
        # Leg
        for jnt, name in zip(left_leg_joint_list, (self.humanIK_joint_dict['LeftUpLeg'], self.humanIK_joint_dict['LeftLeg'], self.humanIK_joint_dict['LeftFoot'], self.humanIK_joint_dict['LeftToeBase'])):
            pm.rename(jnt, name)
        for jnt, name in zip(right_leg_joint_list, (self.humanIK_joint_dict['RightUpLeg'], self.humanIK_joint_dict['RightLeg'], self.humanIK_joint_dict['RightFoot'], self.humanIK_joint_dict['RightToeBase'])):
            pm.rename(jnt, name)
            
        # Arm
        for jnt, name in zip(left_arm_joint_list, (self.humanIK_joint_dict['LeftShoulder'], self.humanIK_joint_dict['LeftArm'], self.humanIK_joint_dict['LeftForeArm'], self.humanIK_joint_dict['LeftHand'])):
            pm.rename(jnt, name)
        for jnt, name in zip(right_arm_joint_list, (self.humanIK_joint_dict['RightShoulder'], self.humanIK_joint_dict['RightArm'], self.humanIK_joint_dict['RightForeArm'], self.humanIK_joint_dict['RightHand'])):
            pm.rename(jnt, name)
            
        # Finger
        for jnt, name in zip(left_hand_thumb_joint_list, self.humanIK_joint_dict['LeftHandThumb']):
            pm.rename(jnt, name)
        for jnt, name in zip(left_hand_index_joint_list, self.humanIK_joint_dict['LeftHandIndex']):
            pm.rename(jnt, name)
        for jnt, name in zip(left_hand_middle_joint_list, self.humanIK_joint_dict['LeftHandMiddle']):
            pm.rename(jnt, name)
        for jnt, name in zip(left_hand_ring_joint_list, self.humanIK_joint_dict['LeftHandRing']):
            pm.rename(jnt, name)
        for jnt, name in zip(left_hand_pinky_joint_list, self.humanIK_joint_dict['LeftHandPinky']):
            pm.rename(jnt, name)
            
        for jnt, name in zip(right_hand_thumb_joint_list, self.humanIK_joint_dict['RightHandThumb']):
            pm.rename(jnt, name)
        for jnt, name in zip(right_hand_index_joint_list, self.humanIK_joint_dict['RightHandIndex']):
            pm.rename(jnt, name)
        for jnt, name in zip(right_hand_middle_joint_list, self.humanIK_joint_dict['RightHandMiddle']):
            pm.rename(jnt, name)
        for jnt, name in zip(right_hand_ring_joint_list, self.humanIK_joint_dict['RightHandRing']):
            pm.rename(jnt, name)
        for jnt, name in zip(right_hand_pinky_joint_list, self.humanIK_joint_dict['RightHandPinky']):
            pm.rename(jnt, name)
            

if __name__ == "__main__":
    UE_rename = UnrealEngine_Skeleton()
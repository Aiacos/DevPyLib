__author__ = 'Lorenzo Argentieri'

import maya.mel as mel
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

hip_ctrl_default = 'M_Spine_cog_ctrl'
spine_ctrl_list_default = ['M_Spine_spine_base_ctrl', 'M_Spine_ik_0_ctrl']
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
    }

    def __init__(self, character_name, custom_ctrl_definition=True, use_ik=False, skip_reference_joint=False,
                 reference_joint=reference_joint_default,
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
                 right_hand_pinky_joint_list=right_hand_pinky_joint_list_default,
                 hip_ctrl=hip_ctrl_default,
                 spine_ctrl_list=spine_ctrl_list_default,
                 chest_ctrl=chest_ctrl_default,
                 neck_ctrl=neck_ctrl_default,
                 head_ctrl=head_ctrl_default,
                 left_clavicle_ctrl=left_clavicle_ctrl_default,
                 left_shoulder_ctrl=left_shoulder_ctrl_default,
                 left_elbow_ctrl=left_elbow_ctrl_default,
                 left_hand_fk_ctrl=left_hand_fk_ctrl_default,
                 left_hand_ik_ctrl=left_hand_ik_ctrl_default,
                 right_clavicle_ctrl=right_clavicle_ctrl_default,
                 right_shoulder_ctrl=right_shoulder_ctrl_default,
                 right_elbow_ctrl=right_elbow_ctrl_default,
                 right_hand_fk_ctrl=right_hand_fk_ctrl_default,
                 right_hand_ik_ctrl=right_hand_ik_ctrl_default,
                 left_hip_ctrl=left_hip_ctrl_default,
                 left_knee_ctrl=left_knee_ctrl_default,
                 left_ankle_fk_ctrl=left_ankle_fk_ctrl_default,
                 left_ankle_ik_ctrl=left_ankle_ik_ctrl_default,
                 right_hip_ctrl=right_hip_ctrl_default,
                 right_knee_ctrl=right_knee_ctrl_default,
                 right_ankle_fk_ctrl=right_ankle_fk_ctrl_default,
                 right_ankle_ik_ctrl=right_ankle_ik_ctrl_default
                 ):
        self.charecter_name = str(character_name)

        mel.eval('hikCreateCharacter("' + self.charecter_name + '")')

        if reference_joint and not skip_reference_joint:
            self.add_reference(reference_joint)
        if hip_joint:
            self.add_hip(hip_joint)
        if spine_joint_list:
            self.add_spine(spine_joint_list)
        if neck_joint_list:
            self.add_neck(neck_joint_list)
        if head_joint:
            self.add_head(head_joint)
        if left_arm_joint_list:
            self.add_left_arm(*left_arm_joint_list)
        if left_leg_joint_list:
            self.add_left_leg(*left_leg_joint_list)
        if right_arm_joint_list:
            self.add_right_arm(*right_arm_joint_list)
        if right_leg_joint_list:
            self.add_right_leg(*right_leg_joint_list)
            
        if left_hand_thumb_joint_list:
            self.add_leftHandThumb(left_hand_thumb_joint_list)
        if left_hand_index_joint_list:
            self.add_leftHandIndex(left_hand_index_joint_list)
        if left_hand_middle_joint_list:
            self.add_leftHandMiddle(left_hand_middle_joint_list)
        if left_hand_ring_joint_list:
            self.add_leftHandRing(left_hand_ring_joint_list)
        if left_hand_pinky_joint_list:
            self.add_leftHandPinky(left_hand_pinky_joint_list)
        if right_hand_thumb_joint_list:
            self.add_rightHandThumb(right_hand_thumb_joint_list)
        if right_hand_index_joint_list:
            self.add_rightHandIndex(right_hand_index_joint_list)
        if right_hand_middle_joint_list:
            self.add_rightHandMiddle(right_hand_middle_joint_list)
        if right_hand_ring_joint_list:
            self.add_rightHandRing(right_hand_ring_joint_list)
        if right_hand_pinky_joint_list:
            self.add_rightHandPinky(right_hand_pinky_joint_list)

        if custom_ctrl_definition:
            self.createCustomRigMapping()
            
            if hip_ctrl:
                self.add_hip_ctrl(hip_ctrl)
            if spine_ctrl_list:
                self.add_spine_ctrl(spine_ctrl_list)
            if chest_ctrl:
                self.add_chest_ctrl(chest_ctrl)
            if neck_ctrl:
                self.add_neck_ctrl(neck_ctrl)
            if head_ctrl:
                self.add_head_ctrl(head_ctrl)
            if left_clavicle_ctrl:
                self.add_leftClavicle_ctrl(left_clavicle_ctrl)
            if right_clavicle_ctrl:
                self.add_rightClavicle_ctrl(right_clavicle_ctrl)
                
            if use_ik and left_hand_ik_ctrl:
                self.add_leftHand_ctrl(left_hand_ik_ctrl)
            if not use_ik and left_shoulder_ctrl:
                self.add_leftShoulder_ctrl(left_shoulder_ctrl)
            if not use_ik and left_elbow_ctrl:
                self.add_leftElbow_ctrl(left_elbow_ctrl)
            if not use_ik and left_hand_fk_ctrl:
                self.add_leftHand_ctrl(left_hand_fk_ctrl)
            if use_ik and left_ankle_ik_ctrl:
                self.add_leftAnkle_ctrl(left_ankle_ik_ctrl)
            if not use_ik and left_hip_ctrl:
                self.add_leftHip_ctrl(left_hip_ctrl)
            if not use_ik and left_knee_ctrl:
                self.add_leftKnee_ctrl(left_knee_ctrl)
            if not use_ik and left_ankle_ik_ctrl:
                self.add_leftAnkle_ctrl(left_ankle_fk_ctrl)

            if use_ik and right_hand_ik_ctrl:
                self.add_rightHand_ctrl(right_hand_ik_ctrl)
            if not use_ik and right_shoulder_ctrl:
                self.add_rightShoulder_ctrl(right_shoulder_ctrl)
            if not use_ik and right_elbow_ctrl:
                self.add_rightElbow_ctrl(right_elbow_ctrl)
            if not use_ik and right_hand_fk_ctrl:
                self.add_rightHand_ctrl(right_hand_fk_ctrl)
            if use_ik and right_ankle_ik_ctrl:
                self.add_rightAnkle_ctrl(right_ankle_ik_ctrl)
            if not use_ik and right_hip_ctrl:
                self.add_rightHip_ctrl(right_hip_ctrl)
            if not use_ik and right_knee_ctrl:
                self.add_rightKnee_ctrl(right_knee_ctrl)
            if not use_ik and right_ankle_ik_ctrl:
                self.add_rightAnkle_ctrl(right_ankle_fk_ctrl)
                

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

    def unlock_and_unhide_all(self, node):
        """
        unlock and unhide all transform attributes of selected node
        :param node: node to be affected
        """
        nodeList = pm.ls(node)

        for node in nodeList:
            node.tx.set(l=0, k=1, cb=0)
            node.ty.set(l=0, k=1, cb=0)
            node.tz.set(l=0, k=1, cb=0)
            node.rx.set(l=0, k=1, cb=0)
            node.ry.set(l=0, k=1, cb=0)
            node.rz.set(l=0, k=1, cb=0)
            node.sx.set(l=0, k=1, cb=0)
            node.sy.set(l=0, k=1, cb=0)
            node.sz.set(l=0, k=1, cb=0)

    def createCustomRigMapping(self):
        # Unlock drawstyle
        joint_list = pm.listRelatives(reference_joint_default, ad=True, type='joint')
        reference_joint_default_pm = pm.ls(reference_joint_default)[-1]
        joint_top_grp = pm.ls('skeleton_grp')[-1]
        self.unlock_and_unhide_all(joint_top_grp)
        pm.connectAttr('Base_main_ctrl.joints_visibility', joint_top_grp.visibility)

        source_connection = pm.listConnections(reference_joint_default_pm.drawStyle, p=True, s=True)[-1]
        reverse_node = pm.listConnections(reference_joint_default_pm.drawStyle, s=True)[-1]
        #reverse_node.outputMin.set(0)
        #reverse_node.outputMin.set(1)
        pm.disconnectAttr(source_connection, reference_joint_default_pm.drawStyle)
        pm.connectAttr(source_connection, reference_joint_default_pm.visibility)

        connections_translateX = pm.listConnections(reference_joint_default_pm.translateX, p=True, s=True)[-1]
        connections_translateY = pm.listConnections(reference_joint_default_pm.translateY, p=True, s=True)[-1]
        connections_translateZ = pm.listConnections(reference_joint_default_pm.translateZ, p=True, s=True)[-1]

        pm.disconnectAttr(connections_translateX, reference_joint_default_pm.translateX)
        pm.disconnectAttr(connections_translateY, reference_joint_default_pm.translateY)
        pm.disconnectAttr(connections_translateZ, reference_joint_default_pm.translateZ)

        pm.connectAttr(connections_translateX, joint_top_grp.translateX)
        pm.connectAttr(connections_translateY, joint_top_grp.translateY)
        pm.connectAttr(connections_translateZ, joint_top_grp.translateZ)

        connections_rotateX = pm.listConnections(reference_joint_default_pm.rotateX, p=True, s=True)[-1]
        connections_rotateY = pm.listConnections(reference_joint_default_pm.rotateY, p=True, s=True)[-1]
        connections_rotateZ = pm.listConnections(reference_joint_default_pm.rotateZ, p=True, s=True)[-1]

        pm.disconnectAttr(connections_rotateX, reference_joint_default_pm.rotateX)
        pm.disconnectAttr(connections_rotateY, reference_joint_default_pm.rotateY)
        pm.disconnectAttr(connections_rotateZ, reference_joint_default_pm.rotateZ)

        pm.connectAttr(connections_rotateX, joint_top_grp.rotateX)
        pm.connectAttr(connections_rotateY, joint_top_grp.rotateY)
        pm.connectAttr(connections_rotateZ, joint_top_grp.rotateZ)

        for jnt in joint_list:
            try:
                source_connection = pm.listConnections(jnt.drawStyle, p=True, s=True)[-1]
                reverse_node = pm.listConnections(jnt.drawStyle, s=True)[-1]
                #reverse_node.outputMin.set(0)
                #reverse_node.outputMin.set(1)
                pm.disconnectAttr(source_connection, jnt.drawStyle)

                reverse_node = pm.shadingNode('reverse', asUtility=True)

                pm.connectAttr(source_connection, reverse_node.inputX)
                pm.connectAttr(reverse_node.outputX, jnt.visibility)

                self.unlock_and_unhide_all(jnt)
            except:
                pass


        mel.eval('hikCreateCustomRig( hikGetCurrentCharacter() );')

    def add_ctrl(self, ctrl, ctrl_id):
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
        
        
if __name__ == "__main__":
    humanIk = HumanIK('Test', custom_ctrl_definition=True, use_ik=True, skip_reference_joint=False)

__author__ = 'Lorenzo Argentieri'

import maya.mel as mel
import pymel.core as pm


reference_joint_joint_default = 'god_M:godnode_srt'
hip_joint_joint_default = 'spine_M:fk00'
spine_joint_list_default = ['spine_M:fk01', 'spine_M:fk02', 'spine_M:fk03', 'spine_M:fk04', 'spine_M:fk05']
neck_joint_list_default = ['head_joint_M:neck_srt']
head_joint_joint_default = 'head_joint_M:head_joint_srt'
left_arm_joint_list_default = ['clavicle_L:fk00', 'arm_L:upr_srt', 'arm_L:mid_srt', 'arm_L:end_srt']
left_leg_joint_list_default = ['leg_L:upr_srt', 'leg_L:mid_srt', 'leg_L:end_srt', 'leg_L:ball_srt']
right_arm_joint_list_default = ['clavicle_R:fk00', 'arm_R:upr_srt', 'arm_R:mid_srt', 'arm_R:end_srt']
right_leg_joint_list_default = ['leg_R:upr_srt', 'leg_R:mid_srt', 'leg_R:end_srt', 'leg_R:ball_srt']

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
        'RightHand': 14
    }

    def __init__(self, character_name, reference_joint=reference_joint_joint_default,
                 hip_joint=hip_joint_joint_default,
                 spine_joint_list=spine_joint_list_default,
                 neck_joint_list=neck_joint_list_default,
                 head_joint=head_joint_joint_default,
                 left_arm_joint_list=left_arm_joint_list_default,
                 left_leg_joint_list=left_leg_joint_list_default,
                 right_arm_joint_list=right_arm_joint_list_default,
                 right_leg_joint_list=right_leg_joint_list_default):
        self.charecter_name = str(character_name)

        mel.eval('hikCreateCharacter("' + self.charecter_name + '")')

        if reference_joint:
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

    def setCharacterObject(self, joint, joint_id):
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

if __name__ == "__main__":
    humanIk = HumanIK('Test', reference_joint='god_M:godnode_srt',
                    hip_joint='spine_M:fk00',
                    spine_joint_list=['spine_M:fk01', 'spine_M:fk02', 'spine_M:fk03', 'spine_M:fk04', 'spine_M:fk05'],
                    neck_joint_list=['head_joint_M:neck_srt'],
                    head_joint='head_joint_M:head_joint_srt',
                    left_arm_joint_list=['clavicle_L:fk00', 'arm_L:upr_srt', 'arm_L:mid_srt', 'arm_L:end_srt'],
                    left_leg_joint_list=['leg_L:upr_srt', 'leg_L:mid_srt', 'leg_L:end_srt', 'leg_L:ball_srt'],
                    right_arm_joint_list=['clavicle_R:fk00', 'arm_R:upr_srt', 'arm_R:mid_srt', 'arm_R:end_srt'],
                    right_leg_joint_list=['leg_R:upr_srt', 'leg_R:mid_srt', 'leg_R:end_srt', 'leg_R:ball_srt'])

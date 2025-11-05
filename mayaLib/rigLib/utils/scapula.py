"""Scapula IK rig setup utilities for shoulder mechanics.

Provides the Scapula class for creating automated scapula (shoulder blade)
IK setups with proper constraints between spine, shoulder, and scapula joints.
"""

__author__ = 'Lorenzo Argentieri'

import pymel.core as pm

from mayaLib.rigLib.utils import name


class Scapula():
    def __init__(self, spine_jnt, shoulder_jnt, scapula_shoulder_jnt):
        """
        Create scapula IK
        :param spine_jnt: str
        :param shoulder_jnt: str
        :param scapula_shoulder_jnt: str
        """
        # get side and name
        side = name.get_side(scapula_shoulder_jnt)

        # get childern of shoulder
        scapula_jnt = pm.listRelatives(scapula_shoulder_jnt, type='joint')[0]

        # create ik
        ikhandle = pm.ikHandle(n=side + 'scapula_IKH', sj=scapula_shoulder_jnt, ee=scapula_jnt)
        effector = pm.listConnections(ikhandle[0].endEffector, source=True)

        # group ik
        grp_name = name.remove_suffix(side + 'scapula_GRP')
        self.scapulaGrp = pm.group(ikhandle, n=grp_name)

        # parent constraint group
        pm.parentConstraint(spine_jnt, self.scapulaGrp, mo=True)

        # parent constraint only transform
        pm.parentConstraint(shoulder_jnt, scapula_shoulder_jnt, skipRotate=['x', 'y', 'z'], mo=True)

        # parent effector
        pm.parent(effector, scapula_shoulder_jnt)

    def get_scapula_grp(self):
        """Get the created scapula IK group.

        Returns:
            PyNode: The group containing scapula IK handle and related nodes
        """
        return self.scapulaGrp


if __name__ == "__main__":
    Scapula()
    # classeProva = IKFKSwitch('ikHandle1', forearmMidJnt=True)
    # classeProva.toIK()
    # classeProva.toFK()

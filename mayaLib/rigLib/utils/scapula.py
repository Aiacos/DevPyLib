__author__ = 'Lorenzo Argentieri'

import pymel.core as pm
from mayaLib.rigLib.utils import util
from mayaLib.rigLib.utils import name


class Scapula():
    def __init__(self, spine_jnt, shoulder_jnt, scapulaShoulder_jnt):
        """
        Create scapula IK
        :param spine_jnt: str
        :param shoulder_jnt: str
        :param scapulaShoulder_jnt: str
        """
        # get side and name
        side = name.getSide(scapulaShoulder_jnt)

        # get childern of shoulder
        scapula_jnt = pm.listRelatives(scapulaShoulder_jnt, type='joint')[0]

        # create ik
        ikhandle = pm.ikHandle(n=side+'scapula_IKH', sj=scapulaShoulder_jnt, ee=scapula_jnt)

        # group ik
        grpName = name.removeSuffix(side+'scapula_GRP')
        self.scapulaGrp = pm.group(ikhandle, n=grpName)

        # parent constraint group
        pm.parentConstraint(spine_jnt, self.scapulaGrp)

        # parent constraint only transform
        pm.parentConstraint(shoulder_jnt, scapulaShoulder_jnt, skipRotate=['x', 'y', 'z'])

    def getScapulaGrp(self):
        return self.getScapulaGrp()


if __name__ == "__main__":
    Scapula()
    # classeProva = IKFKSwitch('ikHandle1', forearmMidJnt=True)
    # classeProva.toIK()
    # classeProva.toFK()


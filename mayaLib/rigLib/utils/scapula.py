__author__ = 'Lorenzo Argentieri'

import pymel.core as pm
from mayaLib.rigLib.utils import util


class Scapula():
    def __init__(self, spine_jnt, scapulaShoulder_jnt):
        # get childern of shoulder
        scapula_jnt = pm.listRelatives(scapulaShoulder_jnt, type='joint')[0]
        # create ik
        ikhandle = pm.ikHandle(n=name, sj=scapulaShoulder_jnt, ee=scapula_jnt)
        # group ik
        # parent constraint group
        pass


if __name__ == "__main__":
    Scapula()
    # classeProva = IKFKSwitch('ikHandle1', forearmMidJnt=True)
    # classeProva.toIK()
    # classeProva.toFK()


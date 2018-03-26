__author__ = 'Lorenzo Argentieri'

import inspect
import pymel.core as pm
from mayaLib.pipelineLib.utility import type


class Convention():
    def __init__(self, uppercase=True,
                 separator='_',
                 left='l',
                 right='r',
                 grp='GRP',
                 loc='LOC',
                 geo='GEO',
                 proxyGeo='PRX',
                 cv='CRV',
                 joint='JNT',
                 ikHandle='IKH',
                 control='CTRL'
                 ):

        # general
        self.separator = '_'

        # side
        self.left = 'l'
        self.right = 'r'

        # group
        self.grp = 'GRP'

        # locator
        self.loc = 'LOC'

        # mesh
        self.geo = 'GEO'
        self.proxyGeo = 'PRX'

        # curve
        self.cv = 'CRV'

        # jont
        self.joint = 'JNT'

        # IK handle
        self.ikHandle = 'IKH'

        # control
        self.control = 'CTRL'

        self.conventionDict = {'separator': separator,
                               'left': left,
                               'right': right,
                               'group': grp,
                               'locator': loc,
                               'geometry': geo,
                               'proxyGeo': proxyGeo,
                               'curve': cv,
                               'joint': joint,
                               'ikHandle': ikHandle,
                               'control': control}


    def toLower(self, s):
        return s.lower()

    def toUpper(self, s):
        return s.upper()

    def convertAllToDefault(self):
        pass

    def convertAllToScene(self):
        pass


if __name__ == "__main__":
    c = Convention()
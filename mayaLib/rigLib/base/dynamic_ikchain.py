__author__ = 'Lorenzo Argentieri'

import pymel.core as pm
from mayaLib.rigLib.utils import util


class IkDynamicChain():
    def __init__(self, startJnt, curve, name='ikChain'):
        # get childern of shoulder
        tipJnt = pm.listRelatives(startJnt, type='joint', children=True, allDescendents=True)[0]
        # make curve dinamic
        dynamicCurve, self.systemGrp, follicleGrp = util.makeCurvesDynamic(curve)
        # create ik
        ikhandle = pm.ikHandle(n=name, sj=startJnt, ee=tipJnt, c=dynamicCurve, sol='ikSplineSolver', ccv=False,
                               roc=False, pcv=False, snc=True)
        # create control locator
        self.ctrlLocator = pm.spaceLocator(n=name + 'Ctrl_LOC')
        # group ik and dynamicSystem
        self.chainGrp = pm.group(self.ctrlLocator, ikhandle[0], self.systemGrp, n=name + '_GRP')
        util.centerPivot(self.chainGrp, startJnt)

        pm.parent(startJnt, self.chainGrp)
        # return ctrlLocator, chainGrp


if __name__ == "__main__":
    IkDynamicChain('joint1', 'curve1')
    # print pm.objectType( 'follicle1' )
    # classeProva = IKFKSwitch('ikHandle1', forearmMidJnt=True)
    # classeProva.toIK()
    # classeProva.toFK()
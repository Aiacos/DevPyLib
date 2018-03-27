__author__ = 'Lorenzo Argentieri'

import pymel.core as pm
from mayaLib.rigLib.utils import common
from mayaLib.rigLib.utils import name


class FootRoll():
    def __init__(self, hipJnt, ankleJnt, ballJntList, toeJntList):
        """
        Build footRoll on selected joints
        :param hipJnt: str
        :param ankleJnt: str
        :param ballJntList: list
        :param toeJntList: list
        """
        self.side = name.getSide(hipJnt)

        self.ballIkHandleList = []
        self.toeIkHandleList= []
        self.prefixJnt1 = name.removeSuffix(hipJnt)
        self.prefixJnt2 = name.removeSuffix(ankleJnt)
        self.ankleIkHandle = pm.ikHandle( n=self.prefixJnt1+'_IKH', sj=hipJnt, ee=ankleJnt)[0]

        for ballJnt in ballJntList:
            prefix = name.removeSuffix(ballJnt)
            tmpBallIkHandle = pm.ikHandle( n=prefix+'_IKH', sj=ankleJnt, ee=ballJnt)[0]
            self.ballIkHandleList.append(tmpBallIkHandle)

        for toeJnt, ballJnt in zip(toeJntList, ballJntList):
            prefix = name.removeSuffix(toeJnt)
            tmpToeIkHandle = pm.ikHandle(n=prefix+'_IKH', sj=ballJnt, ee=toeJnt)[0]
            self.toeIkHandleList.append(tmpToeIkHandle)

        # set temporarily ON Sticky
        self.setSticky(1)

        self.peelHeel()
        self.toeTap()
        self.tippyToe()
        self.moveGrp()

        # set OFF Sticky
        self.setSticky(0)


    def setSticky(self, val=0):
        self.ankleIkHandle.stickiness.set(val)
        for ballIkHandle in self.ballIkHandleList:
            ballIkHandle.stickiness.set(val)
        for toeIkHandle in self.toeIkHandleList:
            toeIkHandle.stickiness.set(val)

    def peelHeel(self):
        self.peelHeelGrp = pm.group(self.ankleIkHandle, n=self.prefixJnt2+'PeelHeel_GRP')

        # move Peel Heel Group Pivot to Middle Ball
        index = int(round(len(self.ballIkHandleList)/2.0))-1
        midBallJnt = self.ballIkHandleList[index]
        common.centerPivot(self.peelHeelGrp, midBallJnt)

    def toeTap(self):
        self.toeTapGrp = pm.group(self.ballIkHandleList, self.toeIkHandleList, n=self.prefixJnt2+'ToeTap_GRP')

        # move Toe Tap Group Pivot to Middle Ball
        index = int(round(len(self.ballIkHandleList)/2.0))-1
        midBallJnt = self.ballIkHandleList[index]
        common.centerPivot(self.toeTapGrp, midBallJnt)

    def tippyToe(self):
        self.tippyToeGrp = pm.group(self.toeTapGrp, self.peelHeelGrp, n=self.prefixJnt2+'TippyToe_GRP')

        # move Toe Tap Group Pivot to Middle Ball
        index = int(round(len(self.toeIkHandleList)/2.0))-1
        midToeJnt = self.toeIkHandleList[index]
        common.centerPivot(self.tippyToeGrp, midToeJnt)

    def moveGrp(self):
        self.moveGrp = pm.group(self.tippyToeGrp, n=self.prefixJnt2+'Move_GRP')

    def getGroupList(self):
        return self.peelHeelGrp, self.toeTapGrp, self.tippyToeGrp, self.moveGrp

    def getIkFingerList(self):
        return self.toeIkHandleList

    def getLimbIK(self):
        return self.ankleIkHandle


if __name__ == "__main__":
    FootRoll('joint1_JNT', 'joint3_JNT', ['joint4_JNT'], ['joint5_JNT'])
    # classeProva = IKFKSwitch('ikHandle1', forearmMidJnt=True)
    # classeProva.toIK()
    # classeProva.toFK()
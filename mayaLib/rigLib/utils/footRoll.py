__author__ = 'Lorenzo Argentieri'

import pymel.core as pm
from mayaLib.rigLib.utils import common


class FootRool():
    def __init__(self, hipJnt, ankleJnt, ballJntList, toeJntList):
        self.side = hipJnt[0:2]

        self.ballIkHandleList = []
        self.toeIkHandleList= []
        self.ankleIkHandle = pm.ikHandle( n=self.side+'ankle', sj=hipJnt, ee=ankleJnt)[0]

        for ballJnt in ballJntList:
            tmpBallIkHandle = pm.ikHandle( n=self.side+'ball', sj=ankleJnt, ee=ballJnt)[0]
            self.ballIkHandleList.append(tmpBallIkHandle)

        for toeJnt, ballJnt in zip(toeJntList, ballJntList):
            tmpToeIkHandle = pm.ikHandle(n=self.side+'toe', sj=ballJnt, ee=toeJnt)[0]
            self.toeIkHandleList.append(tmpToeIkHandle)

        # set temporarily ON Sticky
        self.setSticky(1)

        self.peelHeel()
        self.toeTap()
        self.tippyToe()

        # set OFF Sticky
        self.setSticky(0)


    def setSticky(self, val=0):
        self.ankleIkHandle.stickiness.set(val)
        for ballIkHandle in self.ballIkHandleList:
            ballIkHandle.stickiness.set(val)
        for toeIkHandle in self.toeIkHandleList:
            toeIkHandle.stickiness.set(val)

    def peelHeel(self):
        self.peelHeelGrp = pm.group(self.ankleIkHandle, n=self.side+'peelHeel_GRP')

        # move Peel Heel Group Pivot to Middle Ball
        index = int(round(len(self.ballIkHandleList)/2.0))-1
        midBallJnt = self.ballIkHandleList[index]
        common.centerPivot(self.peelHeelGrp, midBallJnt)

    def toeTap(self):
        self.toeTapGrp = pm.group(self.ballIkHandleList, self.toeIkHandleList, n=self.side+'toeTap_GRP')

        # move Toe Tap Group Pivot to Middle Ball
        index = int(round(len(self.ballIkHandleList)/2.0))-1
        midBallJnt = self.ballIkHandleList[index]
        common.centerPivot(self.toeTapGrp, midBallJnt)

    def tippyToe(self):
        self.tippyToeGrp = pm.group(self.toeTapGrp, self.peelHeelGrp, n=self.side+'tippyToe_GRP')

        # move Toe Tap Group Pivot to Middle Ball
        index = int(round(len(self.toeIkHandleList)/2.0))-1
        midBallJnt = self.toeIkHandleList[index]
        common.centerPivot(self.tippyToeGrp, midBallJnt)


if __name__ == "__main__":
    FootRool('joint1_JNT', 'joint3_JNT', ['joint4_JNT'], ['joint5_JNT'])
    # classeProva = IKFKSwitch('ikHandle1', forearmMidJnt=True)
    # classeProva.toIK()
    # classeProva.toFK()
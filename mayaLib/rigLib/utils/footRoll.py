__author__ = 'Lorenzo Argentieri'

import pymel.core as pm

from mayaLib.rigLib.utils import common
from mayaLib.rigLib.utils import name


class FootRoll():
    def __init__(self, hipJnt, ankleJnt, ballJntList, toeEndJntList, doSmartFootRoll=True):
        """
        Build footRoll on selected joints
        :param hipJnt: str
        :param ankleJnt: str
        :param ballJntList: list
        :param toeEndJntList: list
        :param doSmartFootRoll: bool
        """
        self.side = name.getSide(hipJnt)

        self.ballIkHandleList = []
        self.toeIkHandleList = []
        self.prefixJnt1 = name.removeSuffix(hipJnt)
        self.prefixJnt2 = name.removeSuffix(ankleJnt)
        self.ankleIkHandle = pm.ikHandle(n=self.prefixJnt1 + '_IKH', sj=hipJnt, ee=ankleJnt)[0]

        for ballJnt in ballJntList:
            ballJntParent = pm.ls(ballJnt)[0].getParent()
            prefix = name.removeSuffix(ballJnt)
            tmpBallIkHandle = pm.ikHandle(n=prefix + 'Ball_IKH', sj=ballJntParent, ee=ballJnt)[0]
            self.ballIkHandleList.append(tmpBallIkHandle)

        for toeJnt, ballJnt in zip(toeEndJntList, ballJntList):
            prefix = name.removeSuffix(toeJnt)
            tmpToeIkHandle = pm.ikHandle(n=prefix + 'Fng_IKH', sj=ballJnt, ee=toeJnt)[0]
            self.toeIkHandleList.append(tmpToeIkHandle)

        # set temporarily ON Sticky
        self.setSticky(1)

        self.peelHeel()
        self.toeTap()
        self.tippyToe()

        if doSmartFootRoll:
            frontRollLoc = self.prefixJnt2 + '_frontRoll_LOC'
            backRollLoc = self.prefixJnt2 + '_backRoll_LOC'
            innerRollLoc = self.prefixJnt2 + '_innerRoll_LOC'
            outerRollLoc = self.prefixJnt2 + '_outerRoll_LOC'
            self.frontRollGrp, self.backRollGrp, self.innerRollGrp, self.outerRollGrp = self.rollGroups(frontRollLoc,
                                                                                                        backRollLoc,
                                                                                                        innerRollLoc,
                                                                                                        outerRollLoc)
        else:
            self.frontRollGrp, self.backRollGrp, self.innerRollGrp, self.outerRollGrp = [None, None, None, None]

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
        self.peelHeelGrp = pm.group(self.ankleIkHandle, n=self.prefixJnt2 + 'PeelHeel_GRP')

        # move Peel Heel Group Pivot to Middle Ball
        index = int(round(len(self.ballIkHandleList) / 2.0)) - 1
        midBallJnt = self.ballIkHandleList[index]
        common.centerPivot(self.peelHeelGrp, midBallJnt)

    def toeTap(self):
        self.toeTapGrp = pm.group(self.ballIkHandleList, self.toeIkHandleList, n=self.prefixJnt2 + 'ToeTap_GRP')

        # move Toe Tap Group Pivot to Middle Ball
        index = int(round(len(self.ballIkHandleList) / 2.0)) - 1
        midBallJnt = self.ballIkHandleList[index]
        common.centerPivot(self.toeTapGrp, midBallJnt)

    def tippyToe(self):
        self.tippyToeGrp = pm.group(self.toeTapGrp, self.peelHeelGrp, n=self.prefixJnt2 + 'TippyToe_GRP')

        # move Toe Tap Group Pivot to Middle Ball
        index = int(round(len(self.toeIkHandleList) / 2.0)) - 1
        midToeJnt = self.toeIkHandleList[index]
        common.centerPivot(self.tippyToeGrp, midToeJnt)

    def rollGroups(self, frontRollLoc, backRollLoc, innerRollLoc, outerRollLoc):
        frontRollGrp, backRollGrp, innerRollGrp, outerRollGrp = [None, None, None, None]
        if pm.objExists(frontRollLoc) and pm.objExists(backRollLoc) and pm.objExists(innerRollLoc) and pm.objExists(
                outerRollLoc):
            frontLoc = pm.ls(frontRollLoc)[0]
            backLoc = pm.ls(backRollLoc)[0]
            innerLoc = pm.ls(innerRollLoc)[0]
            outerLoc = pm.ls(outerRollLoc)[0]

            frontRollGrp = pm.group(self.tippyToeGrp, n=name.removeSuffix(frontLoc) + '_GRP')
            backRollGrp = pm.group(frontRollGrp, n=name.removeSuffix(backLoc) + '_GRP')
            innerRollGrp = pm.group(backRollGrp, n=name.removeSuffix(innerLoc) + '_GRP')
            outerRollGrp = pm.group(innerRollGrp, n=name.removeSuffix(outerLoc) + '_GRP')

            common.centerPivot(frontRollGrp, frontLoc)
            common.centerPivot(backRollGrp, backLoc)
            common.centerPivot(innerRollGrp, innerLoc)
            common.centerPivot(outerRollGrp, outerLoc)

        return frontRollGrp, backRollGrp, innerRollGrp, outerRollGrp

    def moveGrp(self):
        if self.outerRollGrp:
            self.moveGrp = pm.group(self.outerRollGrp, n=self.prefixJnt2 + 'Move_GRP')
        else:
            self.moveGrp = pm.group(self.tippyToeGrp, n=self.prefixJnt2 + 'Move_GRP')

        common.centerPivot(self.moveGrp, self.ankleIkHandle)

    def getGroupList(self):
        return self.peelHeelGrp, self.toeTapGrp, self.tippyToeGrp, self.frontRollGrp, self.backRollGrp, self.innerRollGrp, self.outerRollGrp, self.moveGrp

    def getIkFingerList(self):
        return self.toeIkHandleList

    def getIkBallList(self):
        return self.ballIkHandleList

    def getLimbIK(self):
        return self.ankleIkHandle


def createLimbFootRollLocatorsReference(ankleJnt):
    prefix = name.removeSuffix(ankleJnt)
    frontLoc = pm.spaceLocator(n=prefix + '_frontRoll_LOC')
    backLoc = pm.spaceLocator(n=prefix + '_backRoll_LOC')
    innerLoc = pm.spaceLocator(n=prefix + '_innerRoll_LOC')
    outerLoc = pm.spaceLocator(n=prefix + '_outerRoll_LOC')
    locGrp = pm.group(frontLoc, backLoc, innerLoc, outerLoc, n=prefix + 'FootRollLocators_GRP')

    return locGrp


def mirrorFootRollGrp(footRollLocatorGrp):
    locGrp = pm.ls(footRollLocatorGrp)[0]
    newGrpName = locGrp.name().replace('l_', 'r_', 1)
    dupliLocGrp = pm.duplicate(locGrp, n=newGrpName)

    locList = pm.listRelatives(dupliLocGrp[0], c=True)
    for obj in locList:
        newName = obj.name().replace('l_', 'r_', 1)
        pm.rename(obj, newName)

    dupliLocGrp[0].scaleX.set(-1)
    common.freezeTranform(dupliLocGrp[0])

    return dupliLocGrp[0]


if __name__ == "__main__":
    FootRoll('joint1_JNT', 'joint3_JNT', ['joint4_JNT'], ['joint5_JNT'])
    # classeProva = IKFKSwitch('ikHandle1', forearmMidJnt=True)
    # classeProva.toIK()
    # classeProva.toFK()

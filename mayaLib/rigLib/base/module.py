"""
module for making top rig structure and rig module 
"""

import pymel.core as pm
from mayaLib.rigLib.base import control
from mayaLib.rigLib.utils import common
from mayaLib.rigLib.utils import util

class Base():
    """
    class for building top rig structure
    """

    sceneObjectType = 'rig'

    def __init__(
            self,
            characterName='new',
            scale=1.0,
            mainCtrlAttachObj=''
    ):

        """
        :param characterName: str, character name
        :param scale: float, general scale of the rig
        :return: None
        """

        # top group
        self.topGrp = pm.group(n=characterName + '_rig_GRP', em=1)

        characterNameAt = 'characterName'
        sceneObjectTypeAt = 'sceneObjectType'

        for at in [characterNameAt, sceneObjectTypeAt]:
            pm.addAttr(self.topGrp, ln=at, dt='string')

        pm.setAttr(self.topGrp + '.' + characterNameAt, characterName, type='string', l=1)
        pm.setAttr(self.topGrp + '.' + sceneObjectTypeAt, self.sceneObjectType, type='string', l=1)

        # make global control
        self.globalCtrl = control.Control(
            prefix='global',
            scale=scale * 1,
            parent=self.topGrp,
            lockChannels=['t', 'r', 'v'],
            shape='circleY',
            doModify=False,
            doOffset=False
        )

        self.mainCtrl = control.Control(
            prefix='main',
            scale=scale * 1,
            parent=self.globalCtrl.getControl(),
            lockChannels=['s', 'v'],
            shape='move',
            doModify=False,
            doOffset=False
        )

        # model group
        self.modelGrp = pm.group(n='model_GRP', em=1, p=self.topGrp)
        self.fastModelGrp = pm.group(n='fastModel_GRP', em=1, p=self.modelGrp)
        self.mediumModelGrp = pm.group(n='mediumModel_GRP', em=1, p=self.modelGrp)
        self.mediumSlowGrp = pm.group(n='mediumSlowModel_GRP', em=1, p=self.modelGrp)
        self.slowModelGrp = pm.group(n='slowModel_GRP', em=1, p=self.modelGrp)
        self.allModelGrp = pm.group(n='allModel_GRP', em=1, p=self.modelGrp)
        self.rigModelGrp = pm.group(n='rigModel_GRP', em=1, p=self.modelGrp)
        pm.hide(self.rigModelGrp)

        # rig group
        self.rigGrp = pm.group(n='rig_GRP', em=1, p=self.mainCtrl.getControl())

        # World Scale
        self.scaleLocator = pm.spaceLocator(n='scale_LOC')
        self.scaleLocator.inheritsTransform.set(0)
        self.scaleLocator.visibility.set(0)
        pm.connectAttr(self.globalCtrl.getControl().scale, self.scaleLocator.scale)
        pm.parent(self.scaleLocator, self.rigGrp)

        # make more groups
        self.jointsGrp = pm.group(n='skeleton_GRP', em=1, p=self.mainCtrl.getControl())
        self.modulesGrp = pm.group(n='modules_GRP', em=1, p=self.mainCtrl.getControl())
        self.rigCtrlGrp = pm.group(n='rigctrl_GRP', em=1, p=self.globalCtrl.getControl())
        util.lock_and_hide_all(self.rigCtrlGrp)

        self.partGrp = pm.group(n='parts_GRP', em=1, p=self.rigGrp)
        pm.setAttr(self.partGrp + '.it', 0, l=1)

        # make halo
        self.haloCtrl = control.Control(
            prefix='halo',
            scale=1,
            parent=self.rigCtrlGrp,
            translateTo=mainCtrlAttachObj,
            lockChannels=['s'],
            shape='circleX',
            doOffset=True,
            doModify=True,
            objBBox=mainCtrlAttachObj
        )
        self.haloCtrl.getOffsetGrp().visibility.set(0)
        self.createHalo(mainCtrlAttachObj, 1)

        mainVisAts = ['modelVis', 'jointsVis']
        mainDispAts = ['modelDisp', 'jointsDisp']
        mainObjList = [self.modelGrp, self.jointsGrp]
        mainObjVisDvList = [1, 0]

        # add rig visibility connections
        for at, obj, dfVal in zip(mainVisAts, mainObjList, mainObjVisDvList):
            pm.addAttr(self.globalCtrl.getControl(), ln=at, at='enum', enumName='off:on', k=1, dv=dfVal)
            pm.setAttr(self.globalCtrl.getControl() + '.' + at, cb=1)
            pm.connectAttr(self.globalCtrl.getControl() + '.' + at, obj + '.v')

        # add rig display type connections
        for at, obj in zip(mainDispAts, mainObjList):
            pm.addAttr(self.globalCtrl.getControl(), ln=at, at='enum', enumName='normal:template:reference', k=1, dv=2)
            pm.setAttr(self.globalCtrl.getControl() + '.' + at, cb=1)
            pm.setAttr(obj + '.ove', 1)
            pm.connectAttr(self.globalCtrl.getControl() + '.' + at, obj + '.ovdt')

        # add rig display level connection
        displayLevel = 'displayLevel'
        levelGrp = [self.fastModelGrp, self.mediumModelGrp, self.slowModelGrp]
        pm.addAttr(self.globalCtrl.getControl(), ln=displayLevel, at='enum', enumName='fast:medium:slow', k=1, dv=1)
        pm.setAttr(self.globalCtrl.getControl() + '.' + displayLevel, cb=1)
        common.setDrivenKey(self.globalCtrl.getControl() + '.' + displayLevel, [0, 1, 2], levelGrp[0] + '.v', [1, 0, 0])
        common.setDrivenKey(self.globalCtrl.getControl() + '.' + displayLevel, [0, 1, 2], levelGrp[1] + '.v', [0, 1, 0])
        common.setDrivenKey(self.globalCtrl.getControl() + '.' + displayLevel, [0, 1, 2], levelGrp[2] + '.v', [0, 0, 1])
        common.setDrivenKey(self.globalCtrl.getControl() + '.' + displayLevel, [0, 1, 2], self.mediumSlowGrp + '.v', [0, 1, 1])

        # create display control
        self.displayCtrl = self.createDisplay(mainCtrlAttachObj, 1)
        self.ikfkCtrl = self.createIKFK(mainCtrlAttachObj, 1)


    def getScaleLocator(self):
        return self.scaleLocator

    def getDisplayControl(self):
        return self.displayCtrl

    def createHalo(self, mainCtrlAttachObj, scale):
        if pm.objExists(mainCtrlAttachObj):
            haloDupliCtrl = pm.duplicate(self.haloCtrl.getControl(), n='halo')[0]
            haloDupliShape = haloDupliCtrl.getShape()

            # parent shape under globalControl
            pm.parent(haloDupliShape, self.globalCtrl.getControl(), r=1, s=1)
            pm.delete(haloDupliCtrl)

            # blendshape control with halo shape
            pm.blendShape(self.haloCtrl.getControl(), haloDupliShape, n='halo_blendShape', origin='world')
            pm.setAttr('halo_blendShape.halo_CTRL', 1)

            # constraint haloCtrl
            pm.parentConstraint(mainCtrlAttachObj, self.haloCtrl.getOffsetGrp())
            self.haloCtrl.getModifyGrp().translateY.set(12 * self.haloCtrl.getCtrlScale())

    def createDisplay(self, mainCtrlAttachObj, scale):
        # make Display
        displayCtrl = control.Control(
            prefix='display',
            scale=scale,
            parent=self.rigCtrlGrp,
            translateTo=mainCtrlAttachObj,
            lockChannels=['t', 'r', 's'],
            shape='display',
            doOffset=True,
            doModify=True,
            objBBox = mainCtrlAttachObj
        )

        if pm.objExists(mainCtrlAttachObj):
            # constraint displayCtrl
            common.centerPivot(displayCtrl.getOffsetGrp())
            common.centerPivot(displayCtrl.getControl())
            pm.parentConstraint(mainCtrlAttachObj, displayCtrl.getOffsetGrp())
            displayCtrl.getModifyGrp().translateY.set(4 * displayCtrl.getCtrlScale())

        return displayCtrl

    def createIKFK(self, mainCtrlAttachObj, scale):
        # make Display
        ikfkCtrl = control.Control(
            prefix='ikfk',
            scale=scale,
            parent=self.rigCtrlGrp,
            translateTo=mainCtrlAttachObj,
            lockChannels=['t', 'r', 's'],
            shape='ikfk',
            doOffset=True,
            doModify=True,
            objBBox=mainCtrlAttachObj
        )

        if pm.objExists(mainCtrlAttachObj):
            # constraint displayCtrl
            common.centerPivot(ikfkCtrl.getOffsetGrp())
            common.centerPivot(ikfkCtrl.getControl())
            pm.parentConstraint(mainCtrlAttachObj, ikfkCtrl.getOffsetGrp())
            ikfkCtrl.getModifyGrp().translateY.set(3 * ikfkCtrl.getCtrlScale())

        return ikfkCtrl

class Module():
    """
    class for building module rig structure
    """

    def __init__(
            self,
            prefix='new',
            baseObj=None
    ):
        """
        :param prefix: str, prefix to name new objects
        :param baseObj: instance of base.module.Base class
        :return: None
        """

        self.topGrp = pm.group(n=prefix + 'Module_GRP', em=1)

        self.controlsGrp = pm.group(n=prefix + 'Controls_GRP', em=1, p=self.topGrp)
        self.jointsGrp = pm.group(n=prefix + 'Joints_GRP', em=1, p=self.topGrp)
        self.partsGrp = pm.group(n=prefix + 'Parts_GRP', em=1, p=self.topGrp)
        self.partsNoTransGrp = pm.group(n=prefix + 'PartsNoTrans_GRP', em=1, p=self.topGrp)

        pm.hide(self.partsGrp, self.partsNoTransGrp)

        pm.setAttr(self.partsNoTransGrp + '.it', 0, l=1)

        # parent module

        if baseObj:
            pm.parent(self.topGrp, baseObj.modulesGrp)

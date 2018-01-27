"""
module for making top rig structure and rig module 
"""

import pymel.core as pm
from mayaLib.rigLib.base import control


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
            scale=scale * 20,
            parent=self.topGrp,
            lockChannels=['t', 'r', 'v'],
            shape='circleY',
            doModify=False,
            doOffset=False
        )

        self.mainCtrl = control.Control(
            prefix='main',
            scale=scale * 18,
            parent=self.globalCtrl.getControl(),
            lockChannels=['s', 'v'],
            shape='circleY', # ToDo: replae with arrow
            doModify=False,
            doOffset=False
        )

        # model group
        self.modelGrp = pm.group(n='model_GRP', em=1, p=self.topGrp)

        # rig group
        self.rigGrp = pm.group(n='rig_GRP', em=1, p=self.mainCtrl.getControl())

        # Wolrd Scale
        self.scaleLocator = pm.spaceLocator(n='scale_LOC')
        self.scaleLocator.inheritsTransform.set(0)
        self.scaleLocator.visibility.set(0)
        pm.connectAttr(self.globalCtrl.getControl().scale, self.scaleLocator.scale)
        pm.parent(self.scaleLocator, self.rigGrp)

        # make more groups
        self.jointsGrp = pm.group(n='skeleton_GRP', em=1, p=self.mainCtrl.getControl())
        self.modulesGrp = pm.group(n='modules_GRP', em=1, p=self.mainCtrl.getControl())

        self.partGrp = pm.group(n='parts_GRP', em=1, p=self.rigGrp)
        pm.setAttr(self.partGrp + '.it', 0, l=1)

        # make halo
        haloCtrl = control.Control(
            prefix='halo',
            scale=scale * 1,
            parent=self.mainCtrl.getControl(),
            translateTo=mainCtrlAttachObj,
            lockChannels=['t', 'r', 's', 'v'],
            shape='circleZ',
            doOffset=False,
            doModify=False
        )
        pm.parent(haloCtrl.getControl().getShape(), self.globalCtrl.getControl(), r=1, s=1)
        pm.delete(haloCtrl.getControl())

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


    def getScaleLocator(self):
        return self.scaleLocator


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

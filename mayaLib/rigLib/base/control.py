"""
module for making rig controls 
"""

import maya.cmds as pm
import pymel.core as pm
import mayaLib.pipelineLib.utility.nameCheck as nc

class Control():
    """
    class for building rig control
    """

    def __init__(
            self,
            prefix='new',
            scale=1.0,
            translateTo='',
            rotateTo='',
            parent='',
            shape='circle',
            lockChannels=['s', 'v'],
            doOffset=True,
            doModify=False
    ):

        """
        :param prefix: str, prefix to name new objects
        :param scale: float, scale value for size of control shapes
        :param translateTo: str, reference object for control position
        :param rotateTo: str, reference object for control orientation
        :param parent: str, object to be parent of new control
        :param shape: str, control shape type (normal direction)
        :param lockChannels: list( str ), list of channels on control to be locked and non-keyable
        :return: None
        """

        # name handle
        if '*' in prefix:
            prefix = nc.nameCheck(prefix + '_CTRL').split('_')[0]

        ctrlObject = None
        circleNormal = [1, 0, 0]

        if shape in ['circle', 'circleX']:

            circleNormal = [1, 0, 0]

        elif shape == 'circleY':

            circleNormal = [0, 1, 0]

        elif shape == 'circleZ':

            circleNormal = [0, 0, 1]

        elif shape == 'sphere':

            ctrlObject = pm.circle(n=prefix + '_CTRL', ch=False, normal=[1, 0, 0], radius=scale)[0]
            addShape = pm.circle(n=prefix + '_CTRL', ch=False, normal=[0, 0, 1], radius=scale)[0]
            pm.parent(pm.listRelatives(addShape, s=1), ctrlObject, r=1, s=1)
            pm.delete(addShape)

        if not ctrlObject:
            ctrlObject = pm.circle(n=prefix + '_CTRL', ch=False, normal=circleNormal, radius=scale)[0]

        if doModify:
            ctrlModify = pm.group(n=prefix + 'Modify_GRP', em=1)
            pm.parent(ctrlObject, ctrlModify)

        if doOffset:
            ctrlOffset = pm.group(n=prefix + 'Offset_GRP', em=1)
            if doModify:
                pm.parent(ctrlModify, ctrlOffset)
            else:
                pm.parent(ctrlObject, ctrlOffset)

        # color control
        ctrlShapes = ctrlObject.getShape()
        ctrlShapes.ove.set(1)
        #[pm.setAttr(s + '.ove', 1) for s in ctrlShapes]

        if prefix.startswith('l_'):
            #[pm.setAttr(s + '.ovc', 6) for s in ctrlShapes]
            ctrlShapes.ovc.set(6)

        elif prefix.startswith('r_'):
            #[pm.setAttr(s + '.ovc', 13) for s in ctrlShapes]
            ctrlShapes.ovc.set(13)

        else:
            #[pm.setAttr(s + '.ovc', 22) for s in ctrlShapes]
            ctrlShapes.ovc.set(22)

        # translate control
        if translateTo != None and translateTo != '':
            if pm.objExists(translateTo):
                pm.delete(pm.pointConstraint(translateTo, ctrlOffset))

        # rotate control
        if rotateTo != None and rotateTo != '':
            if pm.objExists(rotateTo):
                pm.delete(pm.orientConstraint(rotateTo, ctrlOffset))

        # parent control
        if parent != None and parent != '':
            if pm.objExists(parent):
                pm.parent(ctrlOffset, parent)

        # lock control channels

        singleAttributeLockList = []

        for lockChannel in lockChannels:

            if lockChannel in ['t', 'r', 's']:

                for axis in ['x', 'y', 'z']:
                    at = lockChannel + axis
                    singleAttributeLockList.append(at)

            else:

                singleAttributeLockList.append(lockChannel)

        for at in singleAttributeLockList:
            pm.setAttr(ctrlObject + '.' + at, l=1, k=0)

        # add public members

        self.C = ctrlObject
        self.Modify = None
        self.Off = None

        if doOffset:
            self.Off = ctrlOffset
        if doModify:
            self.Modify = ctrlModify

    def getControl(self):
        return self.C

    def getOffsetGrp(self):
        if self.Off:
            return self.Off

    def getModifyGrp(self):
        if self.Modify:
            return self.Modify

"""
module for making rig controls 
"""

import pymel.core as pm

import mayaLib.pipelineLib.utility.nameCheck as nc
from mayaLib.rigLib.utils import common
from mayaLib.rigLib.utils import ctrlShape
from mayaLib.rigLib.utils import name
from mayaLib.rigLib.utils import util


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
            doModify=False,
            doDynamicPivot=False,
            objBBox=''
    ):

        """
        class for building rig control
        :param prefix: str, prefix to name new objects
        :param scale: float, scale value for size of control shapes
        :param translateTo: str, reference object for control position
        :param rotateTo: str, reference object for control orientation
        :param parent: str, object to be parent of new control
        :param shape: str, control shape type (normal direction)
        :param lockChannels: list( str ), list of channels on control to be locked and non-keyable
        :param objBBox: str, object to calculate ctrl scale
        :param autoBBox: bool, auto find scale value from Proxy Geo if exist
        :return: None
        """

        # name handle
        if '*' in prefix:
            prefix = nc.nameCheck(prefix + '_CTRL').split('_')[0]

        ctrlObject = None
        circleNormal = [1, 0, 0]

        scale = self.calculateScale(scale, translateTo=translateTo, objBBox=objBBox)

        # custom shape
        if shape in ['circle', 'circleX']:
            circleNormal = [1, 0, 0]

        elif shape == 'circleY':
            circleNormal = [0, 1, 0]

        elif shape == 'circleZ':
            circleNormal = [0, 0, 1]

        elif shape == 'sphere':
            ctrlObject = ctrlShape.sphereCtrlShape(name=prefix + '_CTRL', scale=scale)

        elif shape == 'move':
            ctrlObject = ctrlShape.moveCtrlShape(name=prefix + '_CTRL', scale=scale)

        elif shape == 'spine':
            ctrlObject = ctrlShape.trapeziumCtrlShape(name=prefix + '_CTRL', scale=scale)
            ctrlObject.translateY.set(3 * scale)
            common.freezeTranform(ctrlObject)

        elif shape == 'chest':
            ctrlObject = ctrlShape.chestCtrlShape(name=prefix + '_CTRL', scale=scale)

        elif shape == 'hip':
            ctrlObject = ctrlShape.hipCtrlShape(name=prefix + '_CTRL', scale=scale)

        elif shape == 'head':
            ctrlObject = ctrlShape.headCtrlShape(name=prefix + '_CTRL', scale=scale)

        elif shape == 'display':
            ctrlObject = ctrlShape.displayCtrlShape(name=prefix + '_CTRL', scale=scale)

        elif shape == 'ikfk':
            ctrlObject = ctrlShape.ikfkCtrlShape(name=prefix + '_CTRL', scale=scale)

        # default ctrl
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
        ctrlShapes = ctrlObject.getShapes()
        for ctrl_shape in ctrlShapes:
            ctrl_shape.ove.set(1)

            if prefix.startswith('l_'):
                ctrl_shape.ovc.set(6)

            elif prefix.startswith('r_'):
                ctrl_shape.ovc.set(13)

            else:
                ctrl_shape.ovc.set(22)

        # translate control
        if translateTo != None and translateTo != '':
            if pm.objExists(translateTo):
                pm.delete(pm.pointConstraint(translateTo, ctrlOffset))

        # rotate control
        if rotateTo != None and rotateTo != '':
            if pm.objExists(rotateTo):
                pm.delete(pm.orientConstraint(rotateTo, ctrlOffset))

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
        self.scale = scale
        self.C = ctrlObject
        self.Modify = None
        self.Off = None

        if doOffset:
            self.Off = ctrlOffset
        if doModify:
            self.Modify = ctrlModify

        # parent control
        if parent != None and parent != '':
            if pm.objExists(parent):
                pm.parent(self.getTop(), parent)

        self.dynamicPivot = None
        if doDynamicPivot:
            self.dynamicPivot = self.makeDynamicPivot(prefix, scale, translateTo, rotateTo)

    def ctrlRadiusFromJoint(self, jnt, useSphere=True):
        childJnt = jnt.getChildren()

        if len(childJnt) > 0:
            radius = util.get_distance(jnt, childJnt[0])

            if useSphere:
                sphere = pm.polySphere(r=radius, sx=20, sy=20, ch=False)[0]
                radius = util.getPlanarRadiusBBOXFromTransform(sphere, radiusFactor=3)['3D']
                pm.delete(sphere)

        else:
            return 1

        return radius

    def calculateScale(self, scale, translateTo='', objBBox='', useBBox=False, useMean=False):
        """
        Calculate scale value
        :param scale: float
        :param objBBox: str, object where to calculate bounding box
        :param autoBBox: bool, auto find proxy geo for bbox
        :param translateTo: str, object where to search proxy geo
        :return: float, scale
        """
        if scale == 1:
            if useBBox and pm.objExists(objBBox):  # customGeo
                objBBox = pm.ls(objBBox)[0]
                scale = util.getPlanarRadiusBBOXFromTransform(objBBox, radiusFactor=3)['3D']

            elif pm.objExists(translateTo):
                translateTo = pm.ls(translateTo)[0]

                proxyGeoName = name.removeSuffix(translateTo.name()) + '_PRX'
                if useBBox and pm.objExists(proxyGeoName):
                    objBBox = pm.ls(proxyGeoName)[0]
                    scale = util.getPlanarRadiusBBOXFromTransform(objBBox, radiusFactor=3)['3D']

                elif useMean and pm.objExists(proxyGeoName):
                    objBBox = pm.ls(proxyGeoName)[0]
                    bboxValues = util.getPlanarRadiusBBOXFromTransform(objBBox, radiusFactor=3)
                    scale = (bboxValues['planarX'] + bboxValues['planarY'] + bboxValues['planarZ']) / 3

                elif isinstance(translateTo, pm.nodetypes.Joint):
                    scale = self.ctrlRadiusFromJoint(translateTo)
                    if scale < 1 or (scale / 3) < 0.01:
                        scale = 1
                    else:
                        scale = scale / 3

        return scale

    def getCtrlScale(self):
        return self.scale

    def makeDynamicPivot(self, prefix, scale, translateTo, rotateTo):
        pivotCtrl = Control(prefix=prefix + 'Pivot', scale=scale / 5, translateTo=translateTo, rotateTo=rotateTo,
                            parent=self.C,
                            shape='sphere', doOffset=True, doDynamicPivot=False)
        pm.connectAttr(pivotCtrl.getControl().translate, self.C.rotatePivot, f=True)
        control = pm.group(n=prefix + 'Con_GRP', p=self.getControl(), em=True)

        # add visibility Attribute on CTRL
        pm.addAttr(self.C, ln='PivotVisibility', at='enum', enumName='off:on', k=1, dv=0)
        pm.connectAttr(self.C.PivotVisibility, pivotCtrl.getOffsetGrp().visibility, f=True)
        control.visibility.set(0)

        return control

    def getControl(self):
        """
        Return Control
        :return:
        """

        if self.dynamicPivot:
            return self.dynamicPivot

        return self.C

    def getOffsetGrp(self):
        """
        Return Offset Grp if exist or None
        :return:
        """
        if self.Off:
            return self.Off
        return None

    def getModifyGrp(self):
        """
        Return Modify Grp if exist or None
        :return:
        """
        if self.Modify:
            return self.Modify
        return None

    def getTop(self):
        """
        Return control's top Grp or Control
        :return:
        """
        if self.Off:
            return self.Off
        elif self.Modify:
            return self.Modify
        else:
            return self.C

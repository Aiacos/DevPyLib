"""
face @ rig
"""

import pymel.core as pm

from mayaLib.rigLib.base import module
from mayaLib.rigLib.base import control
from mayaLib.rigLib.utils import deform
from mayaLib.rigLib.utils import followCtrl


class Face():
    def __init__(self,
                 cvList,
                 skinGeo,
                 faceGeo='face_GEO',
                 prefix='face',
                 headJnt='head_JNT',
                 jawJnt='jaw_JNT',
                 pointsNumber=5,
                 baseRig=None
                 ):
        """
        Build Facial Setup
        :param cvList: list of facial curves
        :param prefix: str, prefix to name new objects
        :param rigScale: float, scale factor for size of controls
        :param baseRig: instance of base.module.Base class
        """

        cvList = pm.ls(cvList)
        skinGeo = pm.ls(skinGeo)[0]
        faceGeo = pm.ls(faceGeo)[0]
        headJnt = pm.ls(headJnt)[0]
        jawJnt = pm.ls(jawJnt)[0]

        # make rig module
        self.rigmodule = module.Module(prefix=prefix, baseObj=baseRig)

        # attributes
        self.spacing = 1.0 / (pointsNumber - 1)

        # setup deformation
        # geo setup
        faceBaseGeo = pm.duplicate(faceGeo)[0]
        pm.parent(faceBaseGeo, self.rigmodule.partsNoTransGrp)
        #pm.parent(faceGeo, baseRig.baseModule.modelGrp)
        faceWrapNode = deform.wrapDeformer(skinGeo, faceGeo)
        faceWrapBaseGeo = pm.ls(str(faceGeo.name()) + 'Base')[0]
        pm.parent([faceGeo, faceWrapBaseGeo], self.rigmodule.partsNoTransGrp)

        # joints setup
        headFaceJnt = pm.duplicate(headJnt, renameChildren=True)[0]
        jointsDuplicates = pm.listRelatives(headFaceJnt, c=True, ad=True)

        for jnt in jointsDuplicates:
            pm.rename(jnt, str(jnt.name()).replace('_JNT1', 'Face_JNT'))
        pm.parent(jointsDuplicates[0], self.rigmodule.jointsGrp)

        baseJawJnt = pm.ls(str(jawJnt.name()).replace('_JNT', 'Face_JNT'))[0]
        pm.connectAttr(jawJnt.rotate, baseJawJnt.rotate)

        pm.skinCluster(skinGeo, edit=True, ai=cvList)

        for cv in pm.ls(cvList):
            pm.rebuildCurve(cv, ch=0, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=4, d=3, tol=0.01)
            pm.parent(cv, self.rigmodule.partsNoTransGrp)
            locList = self.setupCurve(cv, pointsNumber)

    def setupCurve(self, cv, pointsNumber, sphereSize=0.1, offsetActive=False, locSize=0.1, jointRadius=0.1, follow=False):
        cvName = str(cv.name()).replace('_CRV', '')

        locatorList = []
        for p in range(0, pointsNumber):
            # place locator
            locator = pm.spaceLocator(n=cvName + str(p + 1) + '_LOC')
            locator.localScaleX.set(locSize)
            locator.localScaleY.set(locSize)
            locator.localScaleZ.set(locSize)

            motionPath = pm.ls(pm.pathAnimation(locator, c=cv, f=follow))[0]
            self.deleteConnection(motionPath.u)
            motionPath.uValue.set(self.spacing * p)
            locatorList.append(locator)

            # place joint
            if offsetActive:
                jointOffset = pm.joint(n=cvName + 'Offset' + str(p + 1) + '_JNT', r=jointRadius)
                jointOffset.radius.set(jointRadius)

            joint = pm.joint(n=cvName + str(p + 1) + '_JNT', r=jointRadius)
            joint.radius.set(jointRadius)

            #sphereObj = pm.sphere(r=sphereSize, axis=(0, 1, 0))
            #sphereShape = pm.listRelatives(sphereObj, children=True, shapes=True)
            #pm.parent(sphereShape, joint, r=True, s=True)
            #pm.delete(sphereObj)

        locGrp = pm.group(locatorList, n=cvName + 'loc_GRP', p=self.rigmodule.partsNoTransGrp)

        return locatorList


    def deleteConnection(self, plug):
        # """ Equivalent of MEL: CBdeleteConnection """

        if pm.connectionInfo(plug, isDestination=True):
            plug = pm.connectionInfo(plug, getExactDestination=True)
            readOnly = pm.ls(plug, ro=True)
            # delete -icn doesn't work if destination attr is readOnly
            if readOnly:
                source = pm.connectionInfo(plug, sourceFromDestination=True)
                pm.disconnectAttr(source, plug)
            else:
                pm.delete(plug, icn=True)


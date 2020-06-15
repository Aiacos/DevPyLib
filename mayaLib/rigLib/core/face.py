"""
face @ rig
"""

import pymel.core as pm

from mayaLib.rigLib.base import module
from mayaLib.rigLib.base import control
from mayaLib.rigLib.utils import deform
from mayaLib.rigLib.utils import skin
from mayaLib.rigLib.utils import followCtrl


class Face():
    def __init__(self,
                 cvList,
                 skinGeo,
                 prefix='face',
                 headJnt='head_JNT',
                 pointsNumber=5,
                 scale=0.1,
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
        headJnt = pm.ls(headJnt)[0]

        # make rig module
        self.rigmodule = module.Module(prefix=prefix, baseObj=baseRig)

        # attributes
        self.spacing = 1.0 / (pointsNumber - 1)

        # setup deformation
        # geo setup
        faceGeo = pm.duplicate(skinGeo, n=prefix + '_GEO')[0]
        pm.parent(faceGeo, self.rigmodule.partsNoTransGrp)
        deform.blendShapeDeformer(skinGeo, [faceGeo], 'face_BS', frontOfChain=True)

        # joints setup
        headFaceJnt = pm.duplicate(headJnt, renameChildren=True)[0]
        jointsDuplicates = pm.listRelatives(headFaceJnt, c=True, ad=True)
        jointsDuplicates.append(headFaceJnt)

        for jnt in jointsDuplicates:
            pm.rename(jnt, str(jnt.name()).replace('_JNT1', 'Face_JNT'))
        pm.parent(jointsDuplicates[-1], self.rigmodule.jointsGrp)

        pm.skinCluster(faceGeo, headFaceJnt)

        faceGeoSkincluster = skin.findRelatedSkinCluster(faceGeo)
        pm.skinCluster(faceGeo, edit=True, ai=cvList, ug=True)
        faceGeoSkincluster.useComponents.set(1)

        pm.parent(pm.ls('*_CRVBase'), self.rigmodule.partsNoTransGrp)

        fullLocList = []
        fullClusterList = []
        for cv in pm.ls(cvList):
            pm.rebuildCurve(cv, ch=0, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=0, s=4, d=1, tol=0.01)
            pm.rebuildCurve(cv, ch=0, rpo=1, rt=0, end=1, kr=0, kcp=1, kep=1, kt=0, s=4, d=3, tol=0.01)

            pm.parent(cv, self.rigmodule.partsNoTransGrp)
            locList = self.setupCurve(cv, pointsNumber)
            fullLocList.extend(locList)

            # cluster
            chainCurveCVs = pm.ls(cv + '.cv[*]', fl=1)
            numChainCVs = len(chainCurveCVs)

            curveClusters = []
            for i in range(numChainCVs):
                cls = pm.cluster(chainCurveCVs[i], n=str(cv.name()) + 'Cluster%d' % (i + 1))[1]
                curveClusters.append(cls)

            fullClusterList.extend(curveClusters)

        clusterGrp = pm.group(fullClusterList, n='faceCluster_GRP', p=self.rigmodule.partsNoTransGrp)

        follicleList = []
        for loc, cls in zip(fullLocList, fullClusterList):
            ctrl = control.Control(str(loc.name()).replace('_LOC', ''),
                                   translateTo=loc,
                                   shape='sphere',
                                   parent=self.rigmodule.controlsGrp,
                                   doModify=True,
                                   scale=scale)

            follicle = followCtrl.makeControlFollowSkin(skinGeo, ctrl.getControl(), cls)[-1]
            follicleList.extend([follicle])
        follicleGrp = pm.group(follicleList, n='faceFollicle_GRP', p=self.rigmodule.partsNoTransGrp)

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
                pm.delete(pm.pointConstraint(locator, jointOffset))

            joint = pm.joint(n=cvName + str(p + 1) + '_JNT', r=jointRadius)
            joint.radius.set(jointRadius)
            if not offsetActive:
                pm.delete(pm.pointConstraint(locator, joint))


            #sphereObj = pm.sphere(r=sphereSize, axis=(0, 1, 0))
            #sphereShape = pm.listRelatives(sphereObj, children=True, shapes=True)
            #pm.parent(sphereShape, joint, r=True, s=True)
            #pm.delete(sphereObj)

        locGrp = pm.group(locatorList, n=cvName + 'Loc_GRP', p=self.rigmodule.partsNoTransGrp)

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


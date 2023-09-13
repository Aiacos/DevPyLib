__author__ = 'Lorenzo Argentieri'

import pymel.core as pm

from mayaLib.rigLib.utils import common
from mayaLib.rigLib.utils import deform
from mayaLib.rigLib.utils import name
from mayaLib.rigLib.utils import skin


class SlidingCloth():
    def __init__(self, mainSkinGeo, mainClothGeo_list=[], proxySkinGeo='', proxyClothGeo='', rigModelGrp=None, proximityWrap=True, copy_skincluster_to_cloth_proxy=False):
        """
        Setup Sliding Cloth deformation
        :param mainSkinGeo: str
        :param mainClothGeo_list: list of str
        :param proxySkinGeo: str
        :param proxyClothGeo: str
        """
        if mainSkinGeo and mainClothGeo_list:
            self.mainSkinGeo = pm.ls(mainSkinGeo)[0]
            self.mainClothGeo_list = pm.ls(mainClothGeo_list)
            self.mainClothGeo = pm.ls(mainClothGeo_list)[0]
        else:
            print('No valid Geo!')

        if proxySkinGeo:
            self.proxySkinGeo = pm.ls(proxySkinGeo)[0]
        else:
            self.proxySkinGeo = self.makeProxyGeo(self.mainSkinGeo)

        if proxyClothGeo:
            self.proxyClothGeo = pm.ls(proxyClothGeo)[0]
        else:
            self.proxyClothGeo = self.makeProxyGeo(self.mainClothGeo)

        # setup skin proxy geo
        if not skin.findRelatedSkinCluster(self.mainSkinGeo):
            skin.copyBind(self.mainSkinGeo, self.proxySkinGeo)

        # setup cloth proxy geo
        if copy_skincluster_to_cloth_proxy or not skin.findRelatedSkinCluster(self.proxyClothGeo):
            skin.copyBind(self.mainSkinGeo, self.proxyClothGeo)

        cMuscleDeformer = deform.cMuscleSystemDeformer(self.proxyClothGeo)
        cMuscleDeformer.enableRelax.set(1)
        cMuscleDeformer.relaxCompress.set(10)
        cMuscleDeformer.enableSmooth.set(1)

        shrinkWrapDeformer = deform.shrinkWrapDeformer(self.proxyClothGeo, self.proxySkinGeo)
        shrinkWrapDeformer.shapePreservationEnable.set(1)
        shrinkWrapDeformer.projection.set(4)
        shrinkWrapDeformer.targetInflation.set(0.01)

        polySmoothDeformer = pm.polySmooth(self.proxyClothGeo)[0]

        # wrap main Cloth Geo
        if proximityWrap:
            wrapDeformer = deform.createProximityWrap(self.proxyClothGeo, self.mainClothGeo_list)
            baseObj = []
        else:
            wrapDeformer = deform.wrapDeformer(self.mainClothGeo, self.proxyClothGeo)
            baseObj = pm.listConnections(wrapDeformer.basePoints, source=True)[0]

        # regroup
        grpName = name.removeSuffix(self.mainClothGeo.name()) + 'Cloth_GRP'
        clothGrp = pm.group(self.proxySkinGeo, self.proxyClothGeo, baseObj, n=grpName)
        if rigModelGrp:
            pm.parent(clothGrp, rigModelGrp)

        # save attribute
        self.baseObj = baseObj
        self.wrapDeformer = wrapDeformer
        self.shrinkWrapDeformer = shrinkWrapDeformer
        self.cMuscleDeformer = cMuscleDeformer

    def getWrapBaseObj(self):
        return self.baseObj

    def getWrapDeformer(self):
        return self.wrapDeformer

    def getShrinkWrapDeformer(self):
        return self.shrinkWrapDeformer

    def getCMuscleDeformer(self):
        return self.cMuscleDeformer

    def makeProxyGeo(self, geo, percentage=50):
        proxyName = name.removeSuffix(geo.name()) + 'Proxy_GEO'
        proxyGeo = pm.duplicate(geo, n=proxyName)[0]
        pm.polyReduce(proxyGeo, p=percentage,
                      ver=1, trm=0, shp=0, keepBorder=1, keepMapBorder=1, keepColorBorder=1, keepFaceGroupBorder=1,
                      keepHardEdge=1, keepCreaseEdge=1, keepBorderWeight=0.5, keepMapBorderWeight=0.5,
                      keepColorBorderWeight=0.5, keepFaceGroupBorderWeight=0.5, keepHardEdgeWeight=0.5,
                      keepCreaseEdgeWeight=0.5, useVirtualSymmetry=0, symmetryTolerance=0.01, sx=0, sy=1, sz=0, sw=0,
                      preserveTopology=1, keepQuadsWeight=1, vertexMapName='', cachingReduce=1, ch=1, vct=0, tct=0,
                      replaceOriginal=1)
        common.deleteHistory(proxyGeo)

        return proxyGeo

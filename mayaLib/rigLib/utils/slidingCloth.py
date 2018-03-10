__author__ = 'Lorenzo Argentieri'

import pymel.core as pm
from mayaLib.rigLib.utils import skin
from mayaLib.rigLib.utils import deform


class SlidingCloth():
    def __init__(self, mainSkinGeo, proxySkinGeo, mainClothGeo, proxyClothGeo):
        """
        Setup Sliding Cloth deformation
        :param mainSkinGeo: str
        :param proxySkinGeo: str
        :param mainClothGeo: str
        :param proxyClothGeo: str
        """
        if mainSkinGeo and mainClothGeo:
            self.mainSkinGeo = pm.ls(mainSkinGeo)[0]
            self.mainClothGeo = pm.ls(mainClothGeo)[0]
        else:
            print 'No valid Geo!'

        if proxySkinGeo:
            self.proxySkinGeo = pm.ls(proxySkinGeo)[0]
        else:
            print 'Make Skin proxy Geo!'

        if proxyClothGeo:
            self.proxyClothGeo = pm.ls(proxyClothGeo)[0]
        else:
            print 'Make Cloth proxy GEO!'

        # setup skin proxy geo
        skin.copyBind(self.mainSkinGeo, self.proxySkinGeo)

        # setup cloth proxy geo
        skin.copyBind(self.mainClothGeo, self.proxyClothGeo)

        cMuscleDeformer = deform.cMuscleSystemDeformer(self.proxyClothGeo)
        cMuscleDeformer.enableRelax.set(1)
        cMuscleDeformer.relaxCompress.set(10)
        cMuscleDeformer.enableSmooth.set(1)

        shrinkWrapDeformer = deform.shrinkWrapDeformer(self.proxyClothGeo, self.proxySkinGeo)
        shrinkWrapDeformer.shapePreservationEnable.set(1)

        polySmoothDeformer = pm.polySmooth(self.proxyClothGeo)[0]

        # wrap main Cloth Geo
        wrapDeformer = deform.wrapDeformer(self.mainClothGeo, self.proxyClothGeo)
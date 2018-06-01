__author__ = 'Lorenzo Argentieri'

import pymel.core as pm
from mayaLib.rigLib.utils import deform


class MuscleConnect():
    def __init__(self, mainSkinGeo, muscleGeo, muscleList=pm.ls('*_MUS'), rigModelGrp=None):
        if mainSkinGeo and muscleGeo:
            self.mainSkinGeo = pm.ls(mainSkinGeo)[0]
            self.mainMuscleGeo = pm.ls(muscleGeo)[0]
        else:
            print 'No valid Geo!'

        # apply Muscle Deformer
        self.cMuscleDeformer = deform.cMuscleSystemDeformer(self.mainMuscleGeo)

        # connect muscle
        deform.cMuscleConnectMuscle(self.mainMuscleGeo, muscleList)

        # duplicate Main Body
        muscleSkinBSGeo = pm.duplicate(self.mainSkinGeo, n='body_wrapped_GEO')
        # group and parent muscle mesh
        self.muscleDeformGrp = pm.group(self.mainMuscleGeo, muscleSkinBSGeo, n='muscleDeform_GRP', p=rigModelGrp)
        # Wrap main body with Muscle Body
        deform.wrapDeformer(muscleSkinBSGeo, self.mainMuscleGeo)

        # apply BlendShape
        deform.blendShapeDeformer(self.mainSkinGeo, muscleSkinBSGeo, 'muscleBS', frontOfChain=False)

        # set Attr for Muscle Deformer
        self.cMuscleDeformer.enableSmooth.set(1)
        self.cMuscleDeformer.smoothStrength.set(0)
        self.cMuscleDeformer.smoothExpand.set(10)
        self.cMuscleDeformer.smoothCompress.set(10)
        self.cMuscleDeformer.smoothHold.set(1)

        # ToDO:
        # generate wheights


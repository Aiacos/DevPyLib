import pymel.core as pm

from mayaLib.rigLib.utils import util as util
from mayaLib.rigLib.Ziva import ziva_fiber_tools as fiber
from mayaLib.rigLib.Ziva import ziva_attachments_tools as attachment
from mayaLib.rigLib.Ziva import ziva_tools as tool

class ZivaBase():
    def __init__(self, name='Muscle_rig_grp'):
        self.rig_grp = pm.group(n='Muscle_rig_grp', em=True)

class ZivaMuscle(ZivaBase):
    def __init__(self, skeleton_grp, muscle_grp):
        super().__init__(name='Muscle_rig_grp')

        self.skeleton = util.getAllObjectUnderGroup(skeleton_grp)
        self.muscles = util.getAllObjectUnderGroup(muscle_grp)

        # make bone
        self.ziva_bone = tool.addBone(skeleton_grp)

        # make tissue
        self.ziva_tissue_muscles = []
        for geo in self.muscles:
            muscle = tool.addTissue(geo)
            self.ziva_tissue_muscles.append(muscle)

        # attachment
        # - bone to muscle
        for geo in self.muscles:
            attachment.addAttachment(self.skeleton, geo, value=0.25)

        # - muscle to muscle

        # fiber
        for geo in self.muscles:
            fiber.createLineOfAction(geo, self.skeleton)

class ZivaSkin(ZivaBase):
    def __init__(self, skeleton_grp, muscle_grp, fascia_geo, fat_geo, skin_geo):
        super().__init__(name='Skin_rig_grp')

        self.skeleton = util.getAllObjectUnderGroup(skeleton_grp)
        self.muscles = util.getAllObjectUnderGroup(muscle_grp)
        self.fascia = pm.ls(fascia_geo)[-1]
        self.fat = pm.ls(fat_geo)[-1]
        self.skin = pm.ls(skin_geo)[-1]

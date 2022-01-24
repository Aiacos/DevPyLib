from pathlib import Path
import pymel.core as pm
import maya.mel as mel

from mayaLib.rigLib.utils import util as util
from mayaLib.rigLib.Ziva import ziva_fiber_tools as fiber
from mayaLib.rigLib.Ziva import ziva_attachments_tools as attachment
from mayaLib.rigLib.Ziva import ziva_tools as tool
import zBuilder.utils as zutils


def addTissue(obj):
    pm.select(obj)
    mel.eval('ziva -t;')

    nodes = pm.listRelatives(obj, type='')
    return None

def addBone(obj):
    pm.select(obj)
    mel.eval('ziva -b;')

def addCloth(obj):
    pm.select(obj)
    mel.eval('ziva -c;')


class ZivaBase():
    def __init__(self, character, rig_type='ziva'):
        self.character_name = character
        self.rig_type = rig_type
        self.rig_grp = pm.group(n=character + '_' + rig_type + '_rig_grp', em=True)
        self.zSolver = pm.ls(type='zSolverTransform')[-1]

        self.save_zBuilder('lol')

    def save_zBuilder(self, file_name=None):
        workspace_dir = Path(pm.workspace(q=True, dir=True, rd=True)) / 'scenes' / 'zBuilder'
        workspace_dir.mkdir(parents=True, exist_ok=True)

        if file_name:
            zutils.save_rig(file_name, solver_name=str(self.zSolver.name()))
        else:
            file_name = str(workspace_dir) + self.character_name + '_' + self.rig_type
            zutils.save_rig(file_name, solver_name=str(self.zSolver.name()))

    def load_zBuilder(self, file_name=None):
        workspace_dir = Path(pm.workspace(q=True, dir=True, rd=True)) / 'scenes' / 'zBuilder'
        workspace_dir.mkdir(parents=True, exist_ok=True)

        if file_name:
            zutils.load_rig(file_name, solver_name=str(self.zSolver.name()))
        else:
            file_name = str(workspace_dir) + self.character_name + '_' + self.rig_type
            zutils.load_rig(file_name, solver_name=str(self.zSolver.name()))


class ZivaMuscle(ZivaBase):
    def __init__(self, skeleton_grp, muscle_grp):
        super().__init__(rig_type='muscle')

        self.skeleton = util.getAllObjectUnderGroup(skeleton_grp)
        self.muscles = util.getAllObjectUnderGroup(muscle_grp)

        # make bone
        self.ziva_bone = addBone(skeleton_grp)

        # make tissue
        self.ziva_tissue_muscles = []
        for geo in self.muscles:
            muscle = addTissue(geo)
            self.ziva_tissue_muscles.append(muscle)

        # attachment
        # - bone to muscle
        for geo in self.muscles:
            attachment.addAttachment(self.skeleton, geo, value=0.25)

        # - muscle to muscle
        self.muscle_to_muscle_attachemnt()

        # fiber
        for geo in self.muscles:
            fiber.createLineOfAction(geo, self.skeleton)

    def muscle_to_muscle_attachemnt(self):
        for geo1 in self.muscles:
            for geo2 in self.muscles:
                intersecting_geos = pm.ls(tool.ziva_check_intersection(geo1, geo2), o=True)
                if intersecting_geos:
                    attachment.addAttachment(intersecting_geos[0], intersecting_geos[1], value=0.1, fixed=False)

class ZivaSkin(ZivaBase):
    def __init__(self, skeleton_grp, muscle_grp, fascia_geo, fat_geo, skin_geo):
        super().__init__(rig_type='skin')

        self.skeleton = util.getAllObjectUnderGroup(skeleton_grp)
        self.muscles = util.getAllObjectUnderGroup(muscle_grp)
        self.fascia = pm.ls(fascia_geo)[-1]
        self.fat = pm.ls(fat_geo)[-1]
        self.skin = pm.ls(skin_geo)[-1]


if __name__ == "__main__":
    zBase = ZivaBase()

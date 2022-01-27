from pathlib import Path
import pymel.core as pm
import maya.mel as mel

from mayaLib.rigLib.utils import util as util
from mayaLib.rigLib.Ziva import ziva_fiber_tools as fiber
from mayaLib.rigLib.Ziva import ziva_attachments_tools as attachment
from mayaLib.rigLib.Ziva import ziva_tools as tool
import zBuilder.utils as zutils


def addTissue(obj, tet_size=1):
    pm.select(obj)
    nodes = pm.ls(mel.eval('ziva -t;'))

    #zEmbedder = pm.ls(nodes, type='zEmbedder')[-1]
    zGeo = pm.ls(nodes, type='zGeo')[-1]
    zTissue = pm.ls(nodes, type='zTissue')[-1]
    zTet = pm.ls(nodes, type='zTet')[-1]
    zMaterial = pm.ls(nodes, type='zMaterial')[-1]

    zTet.tetSize.set(tet_size)
    zTet.maxResolution.set(512)

    return zGeo, zTissue, zTet, zMaterial


def addBone(obj):
    pm.select(obj)
    nodes = pm.ls(mel.eval('ziva -b;'))

    #zEmbedder = pm.ls(nodes, type='zEmbedder')[-1]
    zGeo = pm.ls(nodes, type='zGeo')[-1]
    zBone = pm.ls(nodes, type='zBone')[-1]

    return zGeo, zBone


def addCloth(obj):
    pm.select(obj)
    nodes = pm.ls(mel.eval('ziva -c;'))

    #zEmbedder = pm.ls(nodes, type='zEmbedder')[-1]
    zGeo = pm.ls(nodes, type='zGeo')[-1]
    zCloth = pm.ls(nodes, type='zCloth')[-1]
    zMaterial = pm.ls(nodes, type='zMaterial')[-1]

    return zGeo, zCloth, zMaterial


class ZivaBase():
    def __init__(self, character, rig_type='ziva', ziva_cache=True):
        self.character_name = character
        self.rig_type = rig_type
        self.rig_grp = pm.group(n=character + '_' + rig_type + '_rig_grp', em=True)
        self.zSolver = pm.ls(type='zSolverTransform')[-1] if len(pm.ls(type='zSolverTransform')) > 0 else None

        if self.zSolver:
            pm.group(self.zSolver, n='zSolver_grp', p=self.rig_grp)

        if ziva_cache:
            self.add_zivaCache()

        self.clean_up()

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

    def add_zivaCache(self, zSolver=None):
        if zSolver:
            pm.select(zSolver)
        else:
            pm.select(self.zSolver)

        mel.eval('ziva -acn;')

    def clean_up(self):
        tool.zivaRenameAll()


class ZivaMuscle(ZivaBase):
    def __init__(self, character='Warewolf', skeleton_grp='Skeleton_GRP', muscle_grp='Muscle_GRP', tet_size=6, attachment_radius=2):
        self.skeleton = util.getAllObjectUnderGroup(skeleton_grp)
        self.muscles = util.getAllObjectUnderGroup(muscle_grp)

        # make bone
        self.ziva_bone = addBone(self.skeleton)

        # make tissue
        self.ziva_tissue_muscles = []
        for geo in self.muscles:
            muscle = addTissue(geo, tet_size=tet_size)
            self.ziva_tissue_muscles.append(muscle)

        # attachment
        # - bone to muscle
        for geo in self.muscles:
            attachment.addAttachment(self.skeleton, geo, value=attachment_radius)

        # - muscle to muscle
        self.muscle_to_muscle_attachemnt(value=attachment_radius)

        # fiber
        self.curve_list = []
        self.rivets_list = []

        self.loa_grp = pm.group(n='loa_grp', em=True)
        self.curve_grp = pm.group(n='curve_grp', em=True, p=self.loa_grp)
        self.rivet_grp = pm.group(n='rivet_grp', em=True, p=self.loa_grp)

        for geo in self.muscles:
            curve, rivets = fiber.createLineOfAction(geo, self.skeleton)
            self.curve_list.append(curve)
            self.rivets_list.extend(rivets)
            print(curve, rivets)

        pm.parent(self.curve_list, self.curve_grp)
        pm.parent(self.rivets_list, self.rivet_grp)

        # CleanUp
        super().__init__(character, rig_type='muscle')
        self.clean_muscle()

    def clean_muscle(self):
        pm.parent(self.loa_grp, self.rig_grp)

    def muscle_to_muscle_attachemnt(self, value=1):
        for geo1 in self.muscles:
            for geo2 in self.muscles:
                intersecting_geos = pm.ls(tool.ziva_check_intersection(geo1, geo2), o=True)
                if len(intersecting_geos) == 2:
                    attachment.addAttachment(intersecting_geos[0], intersecting_geos[1], value=value, fixed=False)

class ZivaSkin(ZivaBase):
    def __init__(self, character, skeleton_grp, muscle_grp, fascia_geo, fat_geo, skin_geo):
        self.skeleton = util.getAllObjectUnderGroup(skeleton_grp)
        self.muscles = util.getAllObjectUnderGroup(muscle_grp)
        self.fascia = pm.ls(fascia_geo)[-1]
        self.fat = pm.ls(fat_geo)[-1]
        self.skin = pm.ls(skin_geo)[-1]

        super().__init__(character, rig_type='skin')
        self.clean_skin()

    def clean_skin(self):
        pass


if __name__ == "__main__":
    zBase = ZivaBase()

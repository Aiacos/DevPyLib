"""Ziva VFX rig building utilities.

Provides tools for building complete Ziva muscle and tissue
simulation systems.
"""

from pathlib import Path

import maya.mel as mel
import pymel.core as pm

try:
    import zBuilder.builders.ziva as zva
except ImportError:
    zva = None  # type: ignore[assignment]

from mayaLib.rigLib.utils import deform
from mayaLib.rigLib.utils import util as util
from mayaLib.rigLib.Ziva import ziva_attachments_tools as attachment
from mayaLib.rigLib.Ziva import ziva_fiber_tools as fiber
from mayaLib.rigLib.Ziva import ziva_tools as tool


def add_tissue(obj, tet_size=1, max_tet_resolution=512):
    """Adds a tissue to the given object using Ziva's command.

    Args:
        obj: The object to add tissue to.
        tet_size (int): The tetrahedral size.
        max_tet_resolution (int): The maximum tetrahedral resolution.

    Returns:
        tuple: A tuple containing zGeo, zTissue, zTet, and zMaterial nodes.
    """
    pm.select(obj)
    nodes = pm.ls(mel.eval("ziva -t;"))

    z_geo = pm.ls(nodes, type="zGeo")[-1]
    z_tissue = pm.ls(nodes, type="zTissue")[-1]
    z_tet = pm.ls(nodes, type="zTet")[-1]
    z_material = pm.ls(nodes, type="zMaterial")[-1]

    z_tet.tetSize.set(tet_size)
    z_tet.maxResolution.set(max_tet_resolution)

    return z_geo, z_tissue, z_tet, z_material


def add_bone(obj):
    """Adds a bone to the given object using Ziva's command.

    Args:
        obj: The object to add bone to.

    Returns:
        tuple: A tuple containing zGeo and zBone nodes.
    """
    pm.select(obj)
    nodes = pm.ls(mel.eval("ziva -b;"))

    z_geo = pm.ls(nodes, type="zGeo")[-1]
    z_bone = pm.ls(nodes, type="zBone")[-1]

    return z_geo, z_bone


def add_cloth(obj):
    """Adds a cloth to the given object using Ziva's command.

    Args:
        obj: The object to add cloth to.

    Returns:
        tuple: A tuple containing zGeo, zCloth, and zMaterial nodes.
    """
    pm.select(obj)
    nodes = pm.ls(mel.eval("ziva -c;"))

    z_geo = pm.ls(nodes, type="zGeo")[-1]
    z_cloth = pm.ls(nodes, type="zCloth")[-1]
    z_material = pm.ls(nodes, type="zMaterial")[-1]

    return z_geo, z_cloth, z_material


def add_material(obj):
    """Adds a material to the given object using Ziva's command.

    Args:
        obj: The object to add material to.

    Returns:
        The zMaterial node.
    """
    pm.select(obj)
    nodes = pm.ls(mel.eval("ziva -m;"))

    z_material = pm.ls(nodes, type="zMaterial")[-1]

    return z_material


class ZivaBase:
    """Base class for handling Ziva dynamics."""

    def __init__(
        self,
        character,
        rig_type="ziva",
        ziva_cache=True,
        solver_scale=100,
        use_gpu=True,
        skip_build=False,
    ):
        """Initializes the ZivaBase class.

        Args:
            character (str): The character name.
            rig_type (str): The type of rig.
            ziva_cache (bool): Whether to add Ziva cache.
            solver_scale (int): The solver scale.
            use_gpu (bool): Whether to use GPU.
            skip_build (bool): Whether to skip the build process.
        """
        self.character_name = character
        self.rig_type = rig_type
        self.rig_grp = pm.group(n=character + "_" + rig_type + "_rig_grp", em=True)
        self.z_solver = (
            pm.ls(type="zSolverTransform")[-1]
            if len(pm.ls(type="zSolverTransform")) > 0
            else None
        )

        if self.z_solver:
            pm.group(self.z_solver, n="zSolver_grp", p=self.rig_grp)
            self.z_solver.scale.set(solver_scale, solver_scale, solver_scale)
            self.z_solver.getShape().affectSolverGravity.set(1)
            self.z_solver.getShape().affectInertialDamping.set(1)
            self.z_solver.getShape().affectRestScaleEnvelope.set(1)
            self.z_solver.getShape().affectPressureEnvelope.set(1)
            self.z_solver.getShape().affectSurfaceTensionEnvelope.set(1)
            self.z_solver.getShape().affectFiberExcitation.set(1)
            self.z_solver.getShape().affectRestShapeEnvelope.set(1)
            self.z_solver.getShape().collisionDetection.set(1)

            if use_gpu:
                self.z_solver.getShape().solver.set(2)

        if ziva_cache:
            self.add_ziva_cache()

        self.clean_up()

    def save_z_builder(self, file_name=None):
        """Saves the Ziva builder state to a file.

        Args:
            file_name (str, optional): The name of the file to save.
        """
        workspace_dir = (
            Path(pm.workspace(q=True, dir=True, rd=True)) / "scenes" / "zBuilder"
        )
        workspace_dir.mkdir(parents=True, exist_ok=True)

        pm.select(self.z_solver)
        z = zva.Ziva()
        z.retrieve_from_scene()

        if file_name:
            z.write(file_name)
        else:
            file_name = (
                str(workspace_dir)
                + "/"
                + self.character_name
                + "_"
                + self.rig_type
                + ".zBuilder"
            )
            z.write(file_name)

    def load_z_builder(self, file_name=None):
        """Loads the Ziva builder state from a file.

        Args:
            file_name (str, optional): The name of the file to load.
        """
        workspace_dir = (
            Path(pm.workspace(q=True, dir=True, rd=True)) / "scenes" / "zBuilder"
        )
        workspace_dir.mkdir(parents=True, exist_ok=True)

        z = zva.Ziva()

        if file_name:
            z.retrieve_from_file(file_name)
        else:
            file_name = (
                str(workspace_dir)
                + "/"
                + self.character_name
                + "_"
                + self.rig_type
                + ".zBuilder"
            )
            z.retrieve_from_file(file_name)

        z.build()

    def add_ziva_cache(self, z_solver=None):
        """Adds a Ziva cache to the solver.

        Args:
            z_solver: The Ziva solver to add cache to.
        """
        if z_solver:
            pm.select(z_solver)
        else:
            pm.select(self.z_solver)

        mel.eval("ziva -acn;")

    def clean_up(self):
        """Performs cleanup operations."""
        tool.ziva_rename_all()


class ZivaMuscle(ZivaBase):
    """Handles muscle-related operations for Ziva dynamics."""

    def __init__(
        self,
        character="name",
        skeleton_grp="Skeleton_GRP",
        muscle_grp="Muscle_GRP",
        tet_size=2,
        attachment_radius=1,
        solver_scale=100,
        combine_skeleton=True,
        use_gpu=True,
    ):
        """Initializes the ZivaMuscle class.

        Args:
            character (str): The character name.
            skeleton_grp (str): The skeleton group.
            muscle_grp (str): The muscle group.
            tet_size (int): The tetrahedral size.
            attachment_radius (int): The attachment radius.
            solver_scale (int): The solver scale.
            combine_skeleton (bool): Whether to combine the skeleton.
            use_gpu (bool): Whether to use GPU.
        """
        self.skeleton_grp = skeleton_grp
        self.muscle_grp = muscle_grp
        self.skeleton = util.list_objects_under_group(skeleton_grp)
        self.muscles = util.list_objects_under_group(muscle_grp)

        # Prepare skeleton
        if len(skeleton_grp) > 1 and combine_skeleton:
            self.skeleton = tool.z_poly_combine(self.skeleton)
            pm.rename(self.skeleton, "combined_skeleton_geo")
            self.skeleton = pm.ls("combined_skeleton_geo")[-1]
            pm.parent(self.skeleton, self.skeleton_grp)

        # Make bone
        self.ziva_bone = add_bone(self.skeleton)

        # Make tissue
        self.ziva_tissue_muscles = []
        for geo in self.muscles:
            muscle = add_tissue(geo, tet_size=tet_size)
            self.ziva_tissue_muscles.append(muscle)

        # Attachment
        # - Bone to muscle
        for geo in self.muscles:
            attachment.add_attachment(self.skeleton, geo, value=attachment_radius)

        # - Muscle to muscle
        self.muscle_to_muscle_attachemnt(value=attachment_radius)

        # Fiber
        self.curve_list = []
        self.rivets_list = []

        self.loa_grp = pm.group(n="loa_grp", em=True)
        self.curve_grp = pm.group(n="curve_grp", em=True, p=self.loa_grp)
        self.rivet_grp = pm.group(n="rivet_grp", em=True, p=self.loa_grp)

        for geo in self.muscles:
            curve, rivets = fiber.create_line_of_action(geo, self.skeleton)
            self.curve_list.append(curve)
            self.rivets_list.extend(rivets)

        pm.parent(self.curve_list, self.curve_grp)
        pm.parent(self.rivets_list, self.rivet_grp)

        # zOut
        self.z_muscle_combined = tool.z_poly_combine(self.muscles)
        self.z_out_grp = pm.group(self.z_muscle_combined, n="zOut_grp")

        # CleanUp
        super().__init__(
            character, rig_type="muscle", solver_scale=solver_scale, use_gpu=use_gpu
        )
        self.clean_muscle()

    def clean_muscle(self):
        """Cleans up muscle-related groups."""
        pm.parent(self.skeleton_grp, self.rig_grp)
        pm.parent(self.muscle_grp, self.rig_grp)
        pm.parent(self.loa_grp, self.rig_grp)
        pm.parent(self.z_out_grp, self.rig_grp)
        pm.rename(self.z_muscle_combined, "zMuscleCombined_geo")

    def muscle_to_muscle_attachemnt(self, value=1):
        """Creates muscle-to-muscle attachments.

        Args:
            value (int): The attachment value.
        """
        for geo1 in self.muscles:
            for geo2 in self.muscles:
                intersecting_geos = pm.ls(
                    tool.ziva_check_intersection(geo1, geo2), o=True
                )
                if len(intersecting_geos) == 2:
                    attachment.add_attachment(
                        intersecting_geos[0],
                        intersecting_geos[1],
                        value=value,
                        fixed=False,
                    )


class ZivaSkin(ZivaBase):
    """Handles skin-related operations for Ziva dynamics."""

    def __init__(
        self,
        character="",
        fascia_grp="Fascia_grp",
        fat_grp="Fat_grp",
        skin_geo="",
        skeleton_grp="skeleton_grp",
        muscle_grp="muscle_grp",
        tet_size=1,
        attachment_radius=1,
        solver_scale=100,
        combine_skeleton=True,
        max_tet_resolution=512,
        skip_build=False,
        use_gpu=False,
    ):
        """Initializes the ZivaSkin class.

        Args:
            character (str): The character name.
            fascia_grp (str): The fascia group.
            fat_grp (str): The fat group.
            skin_geo (str): The skin geometry.
            skeleton_grp (str): The skeleton group.
            muscle_grp (str): The muscle group.
            tet_size (int): The tetrahedral size.
            attachment_radius (int): The attachment radius.
            solver_scale (int): The solver scale.
            combine_skeleton (bool): Whether to combine the skeleton.
            max_tet_resolution (int): The maximum tetrahedral resolution.
            skip_build (bool): Whether to skip the build process.
            use_gpu (bool): Whether to use GPU.
        """
        self.skeleton_grp = pm.ls(skeleton_grp)[-1]
        self.muscle_grp = pm.ls(muscle_grp)[-1]
        self.fascia_grp = pm.ls(fascia_grp)[-1]
        self.fat_grp = pm.ls(fat_grp)[-1]
        self.skeleton = util.list_objects_under_group(skeleton_grp)
        self.muscles = util.list_objects_under_group(muscle_grp)
        self.fascia_list = util.list_objects_under_group(fascia_grp)
        self.fat_list = util.list_objects_under_group(fat_grp)
        self.skin_list = pm.ls(skin_geo)

        self.z_in_grp = pm.group(n="zIn", em=True)

        # Prepare skeleton
        if len(self.skeleton) > 1:
            self.skeleton = tool.z_poly_combine(self.skeleton)
            pm.parent(self.skeleton, self.z_in_grp)
            pm.rename(self.skeleton, "skeleton_combined_msh")
            self.skeleton = pm.ls("skeleton_combined_msh")[-1]

        # Prepare muscle
        if len(self.muscles) > 1:
            self.muscle_combined = tool.z_poly_combine(self.muscles)
            pm.parent(self.muscle_combined, self.z_in_grp)
            pm.rename(self.muscle_combined, "muscle_combined_msh")
            self.muscle_combined = pm.ls("muscle_combined_msh")[-1]

        if not skip_build:
            self.ziva_skeleton_bone = add_bone(self.skeleton)
            self.ziva_muscle_bone = add_bone(self.muscle_combined)

            # Fascia
            for fascia_geo in self.fascia_list:
                self.fascia_tissue = add_tissue(
                    fascia_geo, tet_size=tet_size, max_tet_resolution=max_tet_resolution
                )

            # Fat
            for fat_geo in self.fat_list:
                self.fat_tissue = add_tissue(
                    fat_geo, tet_size=tet_size, max_tet_resolution=max_tet_resolution
                )

            # Attachment
            for fascia_geo in self.fascia_list:
                attachment.add_attachment(
                    self.skeleton, fascia_geo, value=attachment_radius, fixed=False
                )
                attachment.add_attachment(
                    self.muscle_combined,
                    fascia_geo,
                    value=attachment_radius,
                    fixed=True,
                )

            for fascia_geo, fat_geo in zip(self.fascia_list, self.fat_list):
                attachment.add_attachment(
                    fascia_geo, fat_geo, value=attachment_radius, fixed=True
                )

        # Wrap geo
        wrap_geo_list = []
        for fat_geo, skin_geo in zip(self.fat_list, self.skin_list):
            wrap_geo = pm.duplicate(
                skin_geo, n=str(skin_geo.name()).replace("_geo", "wrap_msh")
            )[-1]
            deform.wrap_deformer(wrap_geo, fat_geo)
            deform.blend_shape_deformer(
                skin_geo, [wrap_geo], str(skin_geo.name()).replace("_geo", "_wrap_BS")
            )

            wrap_geo_list.append(wrap_geo)

        self.wrap_grp = pm.group(wrap_geo_list, n="wrap_grp")

        super(ZivaSkin, self).__init__(
            character,
            rig_type="skin",
            solver_scale=solver_scale,
            skip_build=skip_build,
            use_gpu=use_gpu,
        )
        self.clean_skin()

    def clean_skin(self):
        """Cleans up skin-related groups."""
        pm.parent(self.wrap_grp, self.rig_grp)
        pm.parent(self.skeleton_grp, self.rig_grp)
        pm.parent(self.muscle_grp, self.rig_grp)
        pm.parent(self.fascia_grp, self.rig_grp)
        pm.parent(self.fat_grp, self.rig_grp)
        pm.parent(self.z_in_grp, self.rig_grp)


if __name__ == "__main__":
    z_base = ZivaBase("test_Character")

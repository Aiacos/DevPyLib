"""nCloth setup utilities for muscle deformations."""

from __future__ import annotations

import pymel.core as pm
from maya import mel

from . import dynamic


class ClothMuscle:
    """Helper that wires nCloth systems for muscle simulations."""
    def __init__(self, geo_list, collision_geo_list):
        """Initialise the cloth system and setup colliders.

        Args:
            geo_list: Iterable of meshes to convert to nCloth.
            collision_geo_list: Meshes to turn into nRigid colliders.
        """
        self.cloth_system_grp = pm.group(n='ClothSystem_grp', em=True)
        self.cloth_geo_grp = pm.group(n='cloth_geo_grp', em=True, p=self.cloth_system_grp)

        self.cloth_data_list, self.nucleus = self.create_ncloth(geo_list)
        self.cloth_shape_list = [entry[3] for entry in self.cloth_data_list]

        # setup Nucleus
        pm.rename(self.nucleus, 'clothSystem_nucleus')
        pm.parent(self.nucleus, self.cloth_system_grp)

        # self.nucleus.enable.set(0)

        # setup Colliders
        self.collision_setup(collision_geo_list)

        # sim_geo_list = util.list_objects_under_group(pm.ls('clothOut_grp')[-1])
        # deform.deltaMushDeformer(sim_geo_list)

    def create_ncloth(self, geo_list):
        """Create nCloth nodes for each geometry in `geo_list`.

        Args:
            geo_list: Collection of geometry transforms to convert to nCloth.

        Returns:
            tuple: (cloth_data_list, nucleus)
        """
        cloth_data_list = []
        nucleus = None

        for geo in geo_list:
            (
                cloth_geo,
                geo_cloth_shape,
                cloth_shape,
                nucleus,
            ) = dynamic.setup_nCloth(geo, rest_mesh=geo)
            pm.parent(cloth_geo, self.cloth_geo_grp)
            cloth_data_list.append([geo, cloth_geo, geo_cloth_shape, cloth_shape])

        return cloth_data_list, nucleus

    def collision_setup(self, collision_geo_list):
        """Create colliders for the provided geometry list.

        Args:
            collision_geo_list: Geometry transforms to turn into nRigid colliders.

        Returns:
            list: Pairs of original geometry and collider nodes.
        """
        collision_data_list = []

        for geo in collision_geo_list:
            collider = dynamic.create_collider(geo, self.nucleus)

            collision_data_list.append([geo, collider])

        return collision_data_list

    def paint_input_attract(self, cloth_node, grow_selection=5):
        """Paint input attract values on the cloth by growing a selection.

        Args:
            cloth_node: nCloth node to modify.
            grow_selection: Number of grow iterations for the vertex selection.
        """
        geo = pm.listConnections(cloth_node.inputMesh, s=True)[0]
        print(('PAINT: ', geo))

        # paint middle
        pm.select(geo)
        mel.eval('changeSelectMode -component;')
        mel.eval('SelectAll;')
        mel.eval('polySelectConstraint -pp 3;')
        pm.ls(sl=True)
        # mel.eval('polySelectContraint -dis;')

        for _ in range(grow_selection):
            mel.eval('select `ls -sl`;PolySelectTraverse 1;select `ls -sl`;')

        mel.eval('invertSelection;')

        vtx_list = pm.ls(sl=True)

        dynamic.paint_cloth_input_attract(cloth_node, vtx_list, 0.4, smooth_iterations=3)

    def update_settings(self):
        """Apply default cloth solver settings.

        Returns:
            None
        """
        # setup nCloth
        for data in self.cloth_data_list:
            cloth = data[0]
            # Set Default Value
            # Collision
            cloth.thickness.set(0.01)
            cloth.selfCollideWidthScale.set(1)

            # Dynamic Properties
            cloth.stretchResistance.set(10)
            cloth.bendResistance.set(5)
            cloth.inputMeshAttract.set(1)
            cloth.inputAttractMethod.set(0)

            # Pressure
            cloth.pressureMethod.set(1)

            # Collision
            cloth.thickness.set(0.01)
            cloth.selfCollideWidthScale.set(1)

            # Quality Settings
            cloth.collideLastThreshold.set(0.2)
            cloth.sortLinks.set(1)

            # cloth_shape.evaluationOrder.set(1)
            cloth.bendSolver.set(2)

            # trap checked
            cloth.trappedCheck.set(1)
            cloth.selfTrappedCheck.set(1)

            cloth.pushOut.set(0.05)
            cloth.pushOutRadius.set(1)

            cloth.isDynamic.set(1)

        self.nucleus.enable.set(1)

    def select_vtx(self, geo, vertices):
        """Select a list of vertices on `geo`.

        Args:
            geo: Geometry transform name.
            vertices: Iterable of vertex indices.
        """
        vertex_select_list = []
        for vertex in vertices:
            try:
                vertex_select_list.append(f'{geo}.vtx[{vertex}]')
            except RuntimeError as exc:
                pm.warning(f"Skip vertex {vertex}: {exc}")

        pm.select(vertex_select_list)

    def run_solve(self):
        """Execute the cloth solve using the configured settings.

        Returns:
            None
        """
        # setup nCloth
        for cloth_shape in self.cloth_shape_list:
            # Collisions
            cloth_shape.collisionFlag.set(3)
            cloth_shape.selfCollisionFlag.set(4)
            cloth_shape.thickness.set(0.001)

            # Dynamic Properties
            cloth_shape.inputMeshAttract.set(1)

            # Paint Dynmaic
            self.paint_input_attract(cloth_shape)

            # Pressure
            # setPressure(cloth_shape)

            # Quality Settings
            cloth_shape.collideLastThreshold.set(1)

            cloth_shape.evaluationOrder.set(1)
            cloth_shape.bendSolver.set(2)

            cloth_shape.trappedCheck.set(1)
            cloth_shape.selfTrappedCheck.set(1)

            cloth_shape.pushOut.set(0.05)
            cloth_shape.pushOutRadius.set(1)

        # for muscleGeo in muscleList:
        #    deltaMushSetup(muscleGeo)

        # setupCollider
        # collisionSetup('skeleton_grp')

        self.nucleus.enable.set(1)


if __name__ == "__main__":
    raise SystemExit('Run inside Maya to use cloth muscle utilities.')

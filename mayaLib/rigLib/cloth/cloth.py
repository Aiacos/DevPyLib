import maya.mel as mel
import pymel.core as pm

from mayaLib.rigLib.utils import util
from mayaLib.rigLib.utils import deform
from mayaLib.rigLib.utils import dynamic


class Cloth(object):
    """Cloth simulation setup class.

    Attributes:
        geo_list (list): List of geometry to simulate as cloth.
        collision_geo_list (list): List of geometry to act as collision targets.
        cloth_system_grp (pm.PyNode): The group containing the cloth simulation nodes.
        cloth_geo_grp (pm.PyNode): The group containing the cloth simulation geometry.
        cloth_data_list (list): List of lists containing the following:
            - original geo (pm.PyNode)
            - cloth geo (pm.PyNode)
            - geo cloth shape (pm.PyNode)
            - cloth shape (pm.PyNode)
        nucleus (pm.PyNode): The nucleus node for the cloth simulation.
    """

    def __init__(self, geo_list, collision_geo_list):
        """Initialize the Cloth object.

        Args:
            geo_list (list): List of geometry to simulate as cloth.
            collision_geo_list (list): List of geometry to act as collision targets.
        """
        self.cloth_system_grp = pm.group(n="ClothSystem_grp", em=True)
        self.cloth_geo_grp = pm.group(
            n="cloth_geo_grp", em=True, p=self.cloth_system_grp
        )

        self.cloth_data_list, self.nucleus = self.createNCloth(geo_list)

        # setup Nucleus
        pm.rename(self.nucleus, "clothSystem_nucleus")
        pm.parent(self.nucleus, self.cloth_system_grp)

        # self.nucleus.enable.set(0)

        # setup Colliders
        collision_data_list = self.collisionSetup(collision_geo_list)

        # sim_geo_list = util.getAllObjectUnderGroup(pm.ls('clothOut_grp')[-1])
        # deform.deltaMushDeformer(sim_geo_list)

    def createNCloth(self, geo_list):
        """
        Create nCloth for each geometry in the provided list.

        Args:
            geo_list (list): List of geometries to convert to nCloth.

        Returns:
            tuple: A tuple containing the list of cloth data and the nucleus node.
                   The cloth data list consists of:
                   - original geo (pm.PyNode)
                   - cloth geo (pm.PyNode)
                   - geo cloth shape (pm.PyNode)
                   - cloth shape (pm.PyNode)
        """
        cloth_data_list = []
        nucleus = None

        for geo in geo_list:
            # Set up nCloth for each geometry
            cloth_geo, geo_cloth_shape, clothShape, nucleus = dynamic.setup_nCloth(geo)

            # Parent the cloth geometry to the cloth geometry group
            pm.parent(cloth_geo, self.cloth_geo_grp)

            # Append the cloth data to the list
            cloth_data_list.append([geo, cloth_geo, geo_cloth_shape, clothShape])

        return cloth_data_list, nucleus

    def collisionSetup(self, collision_geo_list):
        """
        Set up colliders for the provided geometries.

        Args:
            collision_geo_list (list): List of geometries to set up as collision targets.

        Returns:
            list: List of lists containing the original geo and the collider node.
        """
        collision_data_list = []

        for geo in collision_geo_list:
            # Create a collider for each geometry
            collider = dynamic.create_collider(geo, self.nucleus)

            # Append the collider data to the list
            collision_data_list.append([geo, collider])

        return collision_data_list

    def paintInputAttract(self, clothNode, growSelection=5):
        """
        Paint the input attract weights of the provided cloth node.

        This method selects the geometry connected to the cloth node,
        selects all its edges, grows the selection by a specified amount,
        inverts the selection, and paints the input attract weights of the
        cloth node.

        Args:
            clothNode (pm.PyNode): The cloth node to paint.
            growSelection (int): The number of times to grow the selection.
        """
        geo = pm.listConnections(clothNode.inputMesh, s=True)[0]
        print(("PAINT: ", geo))

        # Select the geometry connected to the cloth node
        pm.select(geo)

        # Set the select mode to component select
        mel.eval("changeSelectMode -component;")

        # Select all edges
        mel.eval("SelectAll;")
        mel.eval("polySelectConstraint -pp 3;")
        edges = pm.ls(sl=True)
        # mel.eval('polySelectContraint -dis;')

        # Grow the selection by a specified amount
        for i in range(growSelection):
            mel.eval("select `ls -sl`;PolySelectTraverse 1;select `ls -sl`;")

        # Invert the selection
        mel.eval("invertSelection;")

        # Get the list of vertices to paint
        vtxList = pm.ls(sl=True)

        # Paint the input attract weights of the cloth node
        dynamic.clothPaintInputAttract(clothNode, vtxList, 0.4, smoothIteration=3)

    def updateSettings(self):
        """
        Update the settings of the cloth node.

        This method sets the collision, dynamic properties, quality settings,
        and solver settings of the cloth node.
        """
        # setup nCloth
        for cloth_items in self.cloth_data_list:
            clothShape = cloth_items

            # Collision
            clothShape.thickness.set(0.1)
            clothShape.selfCollideWidthScale.set(0)

            # Dynamic Properties
            # clothShape.stretchResistance.set(10)
            # clothShape.bendResistance.set(5)
            clothShape.inputMeshAttract.set(1)
            clothShape.inputAttractMethod.set(0)

            # Quality Settings
            clothShape.collideLastThreshold.set(0.2)
            clothShape.sortLinks.set(1)

            # clothShape.evaluationOrder.set(1)
            clothShape.bendSolver.set(2)

            clothShape.trappedCheck.set(1)
            clothShape.selfTrappedCheck.set(1)

            clothShape.pushOut.set(0.05)
            clothShape.pushOutRadius.set(1)

            clothShape.isDynamic.set(1)

        self.nucleus.enable.set(1)

    def selectVtx(self, geo, vertices):
        """
        Selects a list of vertices on a given geometry.

        Args:
            geo (str): The name of the geometry to select vertices on.
            vertices (list): A list of vertex indices to select.
        """
        vertex_select_list = []
        for vertex in vertices:
            try:
                # Construct the selection string
                vertex_select_list.append("{0}.vtx[{1}]".format(geo, vertex))
            except:
                print("Skip vtx: ", vertex)

        # Select the vertices
        pm.select(vertex_select_list)


#### main
if __name__ == "__main__":
    pass

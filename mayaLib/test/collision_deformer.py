"""Collision deformer test script.

Demonstrates usage of mesh collision deformer plugin
and setup.
"""

import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx


class CollisionDeformer(OpenMayaMPx.MPxDeformerNode):
    """Collision deformer node for mesh-based collision detection.

    Deforms a mesh to prevent intersection with a collider mesh
    using ray intersection and closest point calculations.
    """

    k_plugin_node_id = OpenMaya.MTypeId(0x00000012)
    k_plugin_node_type_name = "collisionDeformer"

    def __init__(self):
        """Initialize the collision deformer node."""
        OpenMayaMPx.MPxDeformerNode.__init__(self)
        self.accel_params = OpenMaya.MMeshIsectAccelParams()  # speeds up intersect calculation
        self.intersector = OpenMaya.MMeshIntersector()  # contains methods for efficiently finding the closest point to a mesh, required for collider

    def deform(self, block, geo_itr, matrix, index):
        """Compute the deformation on the input mesh.

        Args:
            block: Data block containing attribute values.
            geo_itr: Geometry iterator for the input mesh.
            matrix: World matrix of the mesh.
            index: Geometry index in the data block.
        """

        # get ENVELOPE
        envelope = OpenMayaMPx.cvar.MPxGeometryFilter_envelope
        envelope_handle = block.inputValue(envelope)
        envelope_val = envelope_handle.asFloat()

        if envelope_val != 0:

            # get COLLIDER MESH (as worldMesh)
            collider_handle = block.inputValue(self.collider)
            in_collider_mesh = collider_handle.asMesh()

            if not in_collider_mesh.isNull():

                # get collider fn mesh
                in_collider_fn = OpenMaya.MFnMesh(in_collider_mesh)

                # get DEFORMED MESH
                in_mesh = self.get_input_geom(block, index)

                # get COLLIDER WORLD MATRIX to convert the bounding box to world space
                collider_matrix_handle = block.inputValue(self.colliderMatrix)
                collider_matrix_val = collider_matrix_handle.asMatrix()

                # get BOUNDING BOX MIN VALUES
                collider_bounding_box_min_handle = block.inputValue(self.colliderBoundingBoxMin)
                collider_bounding_box_min_val = collider_bounding_box_min_handle.asFloat3()

                # get BOUNDING BOX MAX VALUES
                collider_bounding_box_max_handle = block.inputValue(self.colliderBoundingBoxMax)
                collider_bounding_box_max_val = collider_bounding_box_max_handle.asFloat3()

                # build new bounding box based on given values
                bbox = OpenMaya.MBoundingBox()
                bbox.expand(OpenMaya.MPoint(collider_bounding_box_min_val[0], collider_bounding_box_min_val[1],
                                            collider_bounding_box_min_val[2]))
                bbox.expand(OpenMaya.MPoint(collider_bounding_box_max_val[0], collider_bounding_box_max_val[1],
                                            collider_bounding_box_max_val[2]))

                # set up point on mesh and intersector for returning closest point and accel_params if required
                OpenMaya.MPointOnMesh()
                self.intersector.create(in_collider_mesh, collider_matrix_val)

                # set up constants for allIntersections
                face_ids = None
                tri_ids = None
                ids_sorted = False
                space = OpenMaya.MSpace.kWorld
                max_param = 100000
                test_both_dirs = False
                accel_params = None
                sort_hits = False
                hit_ray_params = None
                hit_faces = None
                hit_triangles = None
                hit_bary1 = None
                hit_bary2 = None
                tolerance = 0.0001
                float_vec = OpenMaya.MFloatVector(0, 1,
                                                 0)  # set up arbitrary vector n.b this is fine for what we want here but anything more complex may require vector obtained from vertex

                # deal with main mesh
                in_mesh_fn = OpenMaya.MFnMesh(in_mesh)
                in_point_array = OpenMaya.MPointArray()
                in_mesh_fn.getPoints(in_point_array, OpenMaya.MSpace.kWorld)

                # create array to store final points and set to correct length
                length = in_point_array.length()
                final_position_array = OpenMaya.MPointArray()
                final_position_array.setLength(length)

                # loop through all points. could also be done with geoItr
                for num in range(length):
                    point = in_point_array[num]

                    # if point is within collider bounding box then consider it
                    if bbox.contains(point):
                        ##-- allIntersections variables --##
                        float_point = OpenMaya.MFloatPoint(point)
                        hit_points = OpenMaya.MFloatPointArray()

                        in_collider_fn.allIntersections(float_point, float_vec, face_ids, tri_ids, ids_sorted, space, max_param,
                                                      test_both_dirs, accel_params, sort_hits, hit_points, hit_ray_params,
                                                      hit_faces, hit_triangles, hit_bary1, hit_bary2, tolerance)

                        if hit_points.length() % 2 == 1:
                            # work out closest point
                            closest_point = OpenMaya.MPoint()
                            in_collider_fn.getClosestPoint(point, closest_point, OpenMaya.MSpace.kWorld, None)

                            # calculate delta and add to array
                            delta = point - closest_point
                            final_position_array.set(point - delta, num)

                        else:
                            final_position_array.set(point, num)

                            # if point is not in bounding box simply add the position to the final array
                    else:
                        final_position_array.set(point, num)

                in_mesh_fn.setPoints(final_position_array, OpenMaya.MSpace.kWorld)

    def get_input_geom(self, block, index):
        """Get the input geometry mesh from the data block.

        Args:
            block: Data block containing geometry data.
            index: Geometry index to retrieve.

        Returns:
            MObject: Input mesh object.
        """
        input_attr = OpenMayaMPx.cvar.MPxGeometryFilter_input
        input_geom_attr = OpenMayaMPx.cvar.MPxGeometryFilter_inputGeom
        input_handle = block.outputArrayValue(input_attr)
        input_handle.jumpToElement(index)
        input_geom_obj = input_handle.outputValue().child(input_geom_attr).asMesh()
        return input_geom_obj


def creator():
    """Create and return a new instance of the deformer node.

    Returns:
        MPxPtr: Pointer to new CollisionDeformer instance.
    """
    return OpenMayaMPx.asMPxPtr(CollisionDeformer())


def initialize():
    """Initialize node attributes for the collision deformer."""
    g_attr = OpenMaya.MFnGenericAttribute()
    m_attr = OpenMaya.MFnMatrixAttribute()
    n_attr = OpenMaya.MFnNumericAttribute()

    CollisionDeformer.collider = g_attr.create("colliderTarget", "col")
    g_attr.addDataAccept(OpenMaya.MFnData.kMesh)

    CollisionDeformer.colliderBoundingBoxMin = n_attr.createPoint("colliderBoundingBoxMin", "cbbmin")

    CollisionDeformer.colliderBoundingBoxMax = n_attr.createPoint("colliderBoundingBoxMax", "cbbmax")

    CollisionDeformer.colliderMatrix = m_attr.create("colliderMatrix", "collMatr", OpenMaya.MFnNumericData.kFloat)
    m_attr.setHidden(True)

    CollisionDeformer.multiplier = n_attr.create("multiplier", "mult", OpenMaya.MFnNumericData.kFloat, 1)

    CollisionDeformer.addAttribute(CollisionDeformer.collider)
    CollisionDeformer.addAttribute(CollisionDeformer.colliderMatrix)
    CollisionDeformer.addAttribute(CollisionDeformer.colliderBoundingBoxMin)
    CollisionDeformer.addAttribute(CollisionDeformer.colliderBoundingBoxMax)
    CollisionDeformer.addAttribute(CollisionDeformer.multiplier)

    out_mesh = OpenMayaMPx.cvar.MPxGeometryFilter_outputGeom

    CollisionDeformer.attributeAffects(CollisionDeformer.collider, out_mesh)
    CollisionDeformer.attributeAffects(CollisionDeformer.colliderBoundingBoxMin, out_mesh)
    CollisionDeformer.attributeAffects(CollisionDeformer.colliderBoundingBoxMax, out_mesh)
    CollisionDeformer.attributeAffects(CollisionDeformer.colliderMatrix, out_mesh)
    CollisionDeformer.attributeAffects(CollisionDeformer.multiplier, out_mesh)


def initializePlugin(obj):
    """Initialize and register the collision deformer plugin.

    Args:
        obj: Maya plugin object.
    """
    plugin = OpenMayaMPx.MFnPlugin(obj, 'Grover', '1.0', 'Any')
    try:
        plugin.registerNode('collisionDeformer', CollisionDeformer.k_plugin_node_id, creator, initialize,
                            OpenMayaMPx.MPxNode.kDeformerNode)
    except RuntimeError:
        raise RuntimeError('Failed to register node')


def uninitializePlugin(obj):
    """Uninitialize and deregister the collision deformer plugin.

    Args:
        obj: Maya plugin object.
    """
    plugin = OpenMayaMPx.MFnPlugin(obj)
    try:
        plugin.deregisterNode(CollisionDeformer.k_plugin_node_id)
    except RuntimeError:
        raise RuntimeError('Failed to deregister node')


if __name__ == "__main__":
    # simply create two polygon spheres. Move the second away from the first, select the first and run the code below.
    import maya.cmds as cmds

    cmds.delete(cmds.ls(type='collisionDeformer'))
    cmds.flushUndo()
    cmds.unloadPlugin('collisionDeformer.py')
    cmds.loadPlugin('collisionDeformer.py')
    cmds.deformer(type='collisionDeformer')
    cmds.connectAttr('pSphere2.worldMesh', 'collisionDeformer1.colliderTarget')
    cmds.connectAttr('pSphere2.matrix', 'collisionDeformer1.colliderMatrix')
    cmds.connectAttr('pSphere2.boundingBox.boundingBoxSize.boundingBoxSizeX',
                     'collisionDeformer1.colliderBoundingBox.colliderBoundingBoxX')
    cmds.connectAttr('pSphere2.boundingBox.boundingBoxSize.boundingBoxSizeY',
                     'collisionDeformer1.colliderBoundingBox.colliderBoundingBoxY')
    cmds.connectAttr('pSphere2.boundingBox.boundingBoxSize.boundingBoxSizeZ',
                     'collisionDeformer1.colliderBoundingBox.colliderBoundingBoxZ')

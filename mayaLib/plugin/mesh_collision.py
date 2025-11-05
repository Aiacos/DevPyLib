"""Maya collision deformer plugin with bulge effect.

This deformer plugin pushes mesh vertices away from a collider mesh with support
for indirect bulge deformation. Vertices inside the collider are pushed to its
surface, while nearby vertices outside can bulge outward for organic deformation.

Installation:
    Copy this file to your Maya plugins directory and load via the Plug-in Manager.

    Windows: Program Files\\Autodesk\\MayaXXXX\\bin\\plug-ins\\
    macOS: Users/Shared/Autodesk/maya/XXXX/plug-ins

Usage:
    1. Load the plugin via Window->Settings/Prefs->Plug-in Manager
    2. Select the collider mesh, then the target mesh
    3. Execute MEL command: collisionDeformer()

Attributes:
    collider (mesh): Collider mesh that pushes vertices
    offset (float): Expand/contract collider surface (0.0-1.0)
    bulge (float): Bulge strength multiplier (0.0-10.0)
    bulgeextend (float): Maximum bulge range (0.0-10.0)
    bulgeshape (ramp): Falloff curve for bulge effect
    backface_culling (enum): Toggle backface collision detection
    sculpt_mode (enum): Lock deformation for sculpting

Author: Jan Lachauer (janlachauer@googlemail.com)
Support: https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=7KFXBVDNNMWHW
"""

import copy
import sys

import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
from maya.mel import eval as meval
import maya.cmds as cmds

K_PLUGIN_NODE_TYPE_NAME = "collisionDeformer"

COLLISION_DEFORMER_ID = OpenMaya.MTypeId(0x0010A52B)

# Some global variables were moved from MPxDeformerNode to MPxGeometryFilter.
# Set some constants to the proper C++ cvars based on the API version.

K_API_VERSION = cmds.about(apiVersion=True)
if K_API_VERSION < 201600:
    K_INPUT = OpenMayaMPx.cvar.MPxDeformerNode_input
    K_INPUT_GEOM = OpenMayaMPx.cvar.MPxDeformerNode_inputGeom
    K_OUTPUT_GEOM = OpenMayaMPx.cvar.MPxDeformerNode_outputGeom
    K_ENVELOPE = OpenMayaMPx.cvar.MPxDeformerNode_envelope
    K_GROUP_ID = OpenMayaMPx.cvar.MPxDeformerNode_groupId
else:
    K_INPUT = OpenMayaMPx.cvar.MPxGeometryFilter_input
    K_INPUT_GEOM = OpenMayaMPx.cvar.MPxGeometryFilter_inputGeom
    K_OUTPUT_GEOM = OpenMayaMPx.cvar.MPxGeometryFilter_outputGeom
    K_ENVELOPE = OpenMayaMPx.cvar.MPxGeometryFilter_envelope
    K_GROUP_ID = OpenMayaMPx.cvar.MPxGeometryFilter_groupId


# Node definition
class CollisionDeformer(OpenMayaMPx.MPxDeformerNode):
    # class variables
    mm_accel_params = OpenMaya.MMeshIsectAccelParams()
    intersector = OpenMaya.MMeshIntersector()
    new_points = OpenMaya.MFloatPointArray()
    max_dist = 0
    base_collider_points = OpenMaya.MFloatPointArray()

    def __init__(self):
        OpenMayaMPx.MPxDeformerNode.__init__(self)

    def _get_input_mesh_data(self, data_block, plug):
        """Retrieve input mesh geometry data.

        Args:
            data_block: Maya data block containing node attributes
            plug: The plug being computed

        Returns:
            tuple: (multi_index, in_mesh_fn, in_points, h_input_geom, sculpt_value)
                - multi_index: Logical index of the plug
                - in_mesh_fn: MFnMesh function set for input mesh
                - in_points: MFloatPointArray of input mesh points in world space
                - h_input_geom: Handle to input geometry
                - sculpt_value: Sculpt mode attribute value
        """
        multi_index = plug.logicalIndex()

        # Get sculpt mode
        sculpt_handle = data_block.inputValue(self.sculptmode)
        sculpt_value = sculpt_handle.asShort()

        # Get input geometry data
        input_attr = K_INPUT
        h_input = data_block.inputArrayValue(input_attr)
        h_input.jumpToArrayElement(multi_index)

        input_geom = K_INPUT_GEOM
        h_input_element = h_input.inputValue()
        h_input_geom = h_input_element.child(input_geom)

        in_mesh = h_input_geom.asMesh()
        in_mesh_fn = OpenMaya.MFnMesh(in_mesh)

        in_points = OpenMaya.MFloatPointArray()
        in_mesh_fn.getPoints(in_points, OpenMaya.MSpace.kWorld)

        # Copy points into array to set them later
        if self.new_points.length() == 0 or sculpt_value == 0:
            self.new_points = copy.copy(in_points)

        return multi_index, in_mesh_fn, in_points, h_input_geom, sculpt_value

    def _get_collider_data(self, data_block):
        """Retrieve and process collider mesh data.

        Args:
            data_block: Maya data block containing node attributes

        Returns:
            tuple: (collider_fn, collider_object, collider_points, collider_matrix_value,
                    threshold_value, pcounts, pconnect, polycount)
                Returns None values if collider mesh cannot be retrieved.
        """
        # Initialize return values
        collider_fn = None
        collider_object = None
        collider_points = OpenMaya.MFloatPointArray()
        pcounts = OpenMaya.MIntArray()
        pconnect = OpenMaya.MIntArray()
        polycount = 0

        # Get collider mesh
        collider_handle = data_block.inputValue(self.collider)
        try:
            collider_object = collider_handle.asMesh()
            collider_fn = OpenMaya.MFnMesh(collider_object)
            polycount = collider_fn.numPolygons()
            collider_fn.getVertices(pcounts, pconnect)
            collider_fn.getPoints(collider_points, OpenMaya.MSpace.kObject)
        except (RuntimeError, TypeError):
            # Can't get collidermesh - check connection to deformer node
            return None, None, None, None, None, None, None, None

        # Get collider transform matrix
        collider_matrix_handle = data_block.inputValue(self.colliderMatrix)
        collider_matrix_value = float_m_matrix_to_m_matrix(collider_matrix_handle.asFloatMatrix())

        # Get collider bounding box for threshold calculation
        collider_bb_size_handle = data_block.inputValue(self.colliderBBoxSize)
        collider_bb_size_value = collider_bb_size_handle.asDouble3()
        collider_bb_vector = OpenMaya.MVector(
            collider_bb_size_value[0],
            collider_bb_size_value[1],
            collider_bb_size_value[2]
        )
        collider_bb_size = collider_bb_vector.length()
        threshold_value = collider_bb_size * 2

        return (collider_fn, collider_object, collider_points, collider_matrix_value,
                threshold_value, pcounts, pconnect, polycount)

    def _apply_collider_offset(self, collider_fn, collider_points, offset_value, pcounts, pconnect, polycount):
        """Apply offset to collider mesh by moving vertices along their normals.

        Args:
            collider_fn: MFnMesh function set for collider mesh
            collider_points: Original collider mesh points
            offset_value: Distance to offset along normals
            pcounts: Polygon vertex counts array
            pconnect: Polygon vertex connection array
            polycount: Number of polygons in collider mesh

        Returns:
            MFloatPointArray: Base collider points before offset (for restoration)
        """
        base_collider_points = copy.copy(collider_points)
        new_collider_points = OpenMaya.MFloatPointArray()
        collider_point_normal = OpenMaya.MVector()

        for i in range(collider_points.length()):
            collider_fn.getVertexNormal(i, collider_point_normal, OpenMaya.MSpace.kObject)
            new_collider_point = OpenMaya.MFloatPoint(
                collider_points[i].x + collider_point_normal.x * offset_value,
                collider_points[i].y + collider_point_normal.y * offset_value,
                collider_points[i].z + collider_point_normal.z * offset_value
            )
            new_collider_points.append(new_collider_point)

        try:
            collider_fn.createInPlace(collider_points.length(), polycount, new_collider_points, pcounts, pconnect)
        except RuntimeError:
            # Can't create offset copy
            pass

        return base_collider_points

    def _process_direct_collision(self, in_mesh_fn, collider_fn, collider_object, collider_matrix_value,
                                   threshold_value, backface_value, in_points, data_block, multi_index,
                                   envelope_value):
        """Process direct collision detection and deformation.

        Args:
            in_mesh_fn: MFnMesh function set for input mesh
            collider_fn: MFnMesh function set for collider mesh
            collider_object: Collider mesh object
            collider_matrix_value: Collider transform matrix
            threshold_value: Maximum distance threshold for collision detection
            backface_value: Backface culling setting (0=off, 1=on)
            in_points: Original input mesh points
            data_block: Maya data block for accessing weights
            multi_index: Logical index of the deformer
            envelope_value: Overall deformer envelope value

        Returns:
            tuple: (check_collision, max_deformation, deformed_points_indices)
                - check_collision: Number of points with collision
                - max_deformation: Maximum deformation distance
                - deformed_points_indices: List of point indices that were deformed
        """
        check_collision = 0
        max_deformation = 0.0
        deformed_points_indices = []

        point_normal = OpenMaya.MVector()
        point_info = OpenMaya.MPointOnMesh()
        empty_float_array = OpenMaya.MFloatArray()

        # Create intersector
        try:
            self.intersector.create(collider_object, collider_matrix_value)
            self.mm_accel_params = collider_fn.autoUniformGridParams()
        except RuntimeError:
            # Can't create intersector
            return check_collision, max_deformation, deformed_points_indices

        # Process each vertex for direct collision
        for k in range(self.new_points.length()):
            in_mesh_fn.getVertexNormal(k, point_normal, OpenMaya.MSpace.kWorld)

            # Define intersection ray from the mesh vertex
            ray_source = OpenMaya.MFloatPoint(self.new_points[k].x, self.new_points[k].y, self.new_points[k].z)
            ray_direction = OpenMaya.MFloatVector(point_normal)
            point = OpenMaya.MPoint(self.new_points[k])

            # MeshFn.allIntersections variables
            face_ids = None
            tri_ids = None
            ids_sorted = True
            space = OpenMaya.MSpace.kWorld
            max_param = threshold_value
            test_both_dirs = True
            accel_params = self.mm_accel_params
            sort_hits = True
            hit_points_1 = OpenMaya.MFloatPointArray()
            hit_ray_params = OpenMaya.MFloatArray(empty_float_array)
            hit_faces = None
            hit_triangles = None
            hit_bary_1s = None
            hit_bary_2s = None

            try:
                got_hit = collider_fn.allIntersections(
                    ray_source, ray_direction, face_ids, tri_ids, ids_sorted, space,
                    max_param, test_both_dirs, accel_params, sort_hits, hit_points_1,
                    hit_ray_params, hit_faces, hit_triangles, hit_bary_1s, hit_bary_2s
                )
            except RuntimeError:
                break

            if not got_hit:
                continue

            # Check if collider is in range for collision
            hit_count = hit_points_1.length()
            sign_change = -1000

            for i in range(hit_count - 1):
                if hit_ray_params[i] * hit_ray_params[i + 1] < 0:
                    sign_change = i
                    break

            collision = 0
            if hit_count == 2 and sign_change + 1 == 1 and sign_change != -1000:
                collision = 1
            elif hit_count > 2 and hit_count / (sign_change + 1) != 2 and sign_change != -1000:
                collision = 1

            # Process collision if detected
            if collision == 1:
                check_collision += 1
                deformed_points_indices.append(k)

                # Get closest point on collider mesh
                self.intersector.getClosestPoint(point, point_info)
                close_point = OpenMaya.MPoint(point_info.getPoint())
                close_point_normal = OpenMaya.MFloatVector(point_info.getNormal())

                # Check backface culling
                angle = close_point_normal * ray_direction
                if angle > 0 and backface_value == 1:
                    # Ignore backfaces
                    world_point = OpenMaya.MPoint(hit_points_1[sign_change])
                else:
                    world_point = close_point
                    world_point = world_point * collider_matrix_value

                # Update maximum deformation distance
                deformation_distance = point.distanceTo(world_point)
                if max_deformation < deformation_distance:
                    max_deformation = deformation_distance

                # Apply deformation with weight
                weight = self.weightValue(data_block, multi_index, k)
                self.new_points[k].x += (world_point.x - in_points[k].x) * envelope_value * weight
                self.new_points[k].y += (world_point.y - in_points[k].y) * envelope_value * weight
                self.new_points[k].z += (world_point.z - in_points[k].z) * envelope_value * weight

        return check_collision, max_deformation, deformed_points_indices

    def _process_indirect_collision(self, in_mesh_fn, collider_matrix_value, bulge_extend_value,
                                     bulge_value, max_deformation, data_block, multi_index,
                                     envelope_value, this_node):
        """Process indirect collision (bulge) deformation.

        Args:
            in_mesh_fn: MFnMesh function set for input mesh
            collider_matrix_value: Collider transform matrix
            bulge_extend_value: Maximum bulge range
            bulge_value: Bulge strength multiplier
            max_deformation: Maximum deformation distance from direct collision
            data_block: Maya data block for accessing weights
            multi_index: Logical index of the deformer
            envelope_value: Overall deformer envelope value
            this_node: This node's MObject
        """
        in_mesh_normal = OpenMaya.MVector()
        indir_point_info = OpenMaya.MPointOnMesh()
        bulgeshape_value_util = OpenMaya.MScriptUtil()
        bulgeshape_value = bulgeshape_value_util.asFloatPtr()
        bulgeshape_handle = OpenMaya.MRampAttribute(this_node, self.bulgeshape)

        for i in range(self.new_points.length()):
            in_mesh_fn.getVertexNormal(i, in_mesh_normal, OpenMaya.MSpace.kWorld)

            indir_point = OpenMaya.MPoint(self.new_points[i])
            self.intersector.getClosestPoint(indir_point, indir_point_info)
            indir_close_point = OpenMaya.MPoint(indir_point_info.getPoint())

            indir_world_point = indir_close_point * collider_matrix_value
            bulge_pnts_dist = indir_point.distanceTo(indir_world_point)

            weight = self.weightValue(data_block, multi_index, i)

            # Calculate relative distance based on maximum bulge range
            relative_distance = bulge_pnts_dist / (bulge_extend_value + 0.00001)

            # Get bulge curve value
            bulgeshape_handle.getValueAtPosition(float(relative_distance), bulgeshape_value)
            bulge_amount = OpenMaya.MScriptUtil().getFloat(bulgeshape_value)

            # Apply bulge deformation
            bulge_scale = bulge_extend_value * (bulge_value / 5) * envelope_value * bulge_amount * max_deformation * weight
            self.new_points[i].x += in_mesh_normal.x * bulge_scale
            self.new_points[i].y += in_mesh_normal.y * bulge_scale
            self.new_points[i].z += in_mesh_normal.z * bulge_scale

    def compute(self, plug, data_block):
        """Main compute method for collision deformer.

        This method orchestrates the collision deformation by:
        1. Retrieving input mesh and collider data
        2. Processing direct collision (vertices inside collider)
        3. Processing indirect collision (bulge effect)
        4. Updating output mesh geometry
        """
        # Get this node reference
        this_node = self.thisMObject()

        # Get deformer attributes
        envelope = K_ENVELOPE
        envelope_handle = data_block.inputValue(envelope)
        envelope_value = envelope_handle.asFloat()

        offset_handle = data_block.inputValue(self.offset)
        offset_value = offset_handle.asDouble()

        bulge_extend_handle = data_block.inputValue(self.bulgeextend)
        bulge_extend_value = bulge_extend_handle.asDouble()

        bulge_handle = data_block.inputValue(self.bulge)
        bulge_value = bulge_handle.asDouble()

        backface_handle = data_block.inputValue(self.backface)
        backface_value = backface_handle.asShort()

        # Get input mesh data
        multi_index, in_mesh_fn, in_points, h_input_geom, sculpt_value = self._get_input_mesh_data(data_block, plug)

        # Set output geometry
        h_output = data_block.outputValue(plug)
        h_output.copy(h_input_geom)
        out_mesh = h_input_geom.asMesh()
        out_mesh_fn = OpenMaya.MFnMesh(out_mesh)

        # Get collider data
        collider_data = self._get_collider_data(data_block)
        (collider_fn, collider_object, collider_points, collider_matrix_value,
         threshold_value, pcounts, pconnect, polycount) = collider_data

        # Early exit if no valid collider or envelope is zero
        if collider_fn is None or envelope_value == 0:
            return

        # Apply offset to collider if needed
        base_collider_points = None
        if offset_value != 0:
            base_collider_points = self._apply_collider_offset(
                collider_fn, collider_points, offset_value, pcounts, pconnect, polycount
            )

        # Process direct collision detection and deformation
        check_collision, max_deformation, deformed_points_indices = self._process_direct_collision(
            in_mesh_fn, collider_fn, collider_object, collider_matrix_value,
            threshold_value, backface_value, in_points, data_block, multi_index, envelope_value
        )

        # Process indirect collision (bulge) if any direct collision occurred
        if check_collision != 0:
            self._process_indirect_collision(
                in_mesh_fn, collider_matrix_value, bulge_extend_value,
                bulge_value, max_deformation, data_block, multi_index,
                envelope_value, this_node
            )

        # Update output mesh with deformed points
        out_mesh_fn.setPoints(self.new_points, OpenMaya.MSpace.kWorld)
        data_block.setClean(self.outputGeom)

        # Restore collider to original position if offset was applied
        if offset_value != 0 and base_collider_points is not None:
            try:
                collider_fn.createInPlace(collider_points.length(), polycount, base_collider_points, pcounts, pconnect)
            except RuntimeError:
                # Can't reset offset copy
                pass

    # accessoryNodeSetup used to initialize the ramp attributes
    def accessoryNodeSetup(self, cmd):
        this_node = self.thisMObject()

        bulgeshape_handle = OpenMaya.MRampAttribute(this_node, self.bulgeshape)

        a1 = OpenMaya.MFloatArray()
        b1 = OpenMaya.MFloatArray()
        c1 = OpenMaya.MIntArray()

        a1.append(float(0.0))
        a1.append(float(0.2))
        a1.append(float(1.0))

        b1.append(float(0.0))
        b1.append(float(1.0))
        b1.append(float(0.0))

        c1.append(OpenMaya.MRampAttribute.kSpline)
        c1.append(OpenMaya.MRampAttribute.kSpline)
        c1.append(OpenMaya.MRampAttribute.kSpline)

        bulgeshape_handle.addEntries(a1, b1, c1)


def float_m_matrix_to_m_matrix(fm):
    mat = OpenMaya.MMatrix()
    OpenMaya.MScriptUtil.createMatrixFromList([
        fm(0, 0), fm(0, 1), fm(0, 2), fm(0, 3),
        fm(1, 0), fm(1, 1), fm(1, 2), fm(1, 3),
        fm(2, 0), fm(2, 1), fm(2, 2), fm(2, 3),
        fm(3, 0), fm(3, 1), fm(3, 2), fm(3, 3)], mat)
    return mat


def node_creator():
    return OpenMayaMPx.asMPxPtr(CollisionDeformer())


# initializer
def node_initializer():
    g_attr = OpenMaya.MFnGenericAttribute()

    CollisionDeformer.collider = g_attr.create("collider", "coll")
    g_attr.addDataAccept(OpenMaya.MFnData.kMesh)
    g_attr.setHidden(True)

    n_attr = OpenMaya.MFnNumericAttribute()

    CollisionDeformer.bulgeextend = n_attr.create("bulgeextend", "bex", OpenMaya.MFnNumericData.kDouble, 0.0)
    n_attr.setKeyable(True)
    n_attr.setStorable(True)
    n_attr.setSoftMin(0)
    n_attr.setSoftMax(10)

    CollisionDeformer.bulge = n_attr.create("bulge", "blg", OpenMaya.MFnNumericData.kDouble, 1.0)
    n_attr.setKeyable(True)
    n_attr.setStorable(True)
    n_attr.setSoftMin(0)
    n_attr.setSoftMax(10)

    CollisionDeformer.offset = n_attr.create("offset", "off", OpenMaya.MFnNumericData.kDouble, 0.0)
    n_attr.setKeyable(True)
    n_attr.setStorable(True)
    n_attr.setSoftMin(0)
    n_attr.setSoftMax(1)

    CollisionDeformer.colliderBBoxX = n_attr.create("colliderBBoxX", "cbbX", OpenMaya.MFnNumericData.kDouble, 0.0)
    CollisionDeformer.colliderBBoxY = n_attr.create("colliderBBoxY", "cbbY", OpenMaya.MFnNumericData.kDouble, 0.0)
    CollisionDeformer.colliderBBoxZ = n_attr.create("colliderBBoxZ", "cbbZ", OpenMaya.MFnNumericData.kDouble, 0.0)

    c_attr = OpenMaya.MFnCompoundAttribute()
    CollisionDeformer.colliderBBoxSize = c_attr.create("colliderBBoxSize", "cbb")

    c_attr.addChild(CollisionDeformer.colliderBBoxX)
    c_attr.addChild(CollisionDeformer.colliderBBoxY)
    c_attr.addChild(CollisionDeformer.colliderBBoxZ)

    m_attr = OpenMaya.MFnMatrixAttribute()

    CollisionDeformer.colliderMatrix = m_attr.create("colliderMatrix", "collMatr", OpenMaya.MFnNumericData.kFloat)
    m_attr.setHidden(True)

    r_attr = OpenMaya.MRampAttribute()

    CollisionDeformer.bulgeshape = r_attr.createCurveRamp("bulgeshape", "blgshp")

    e_attr = OpenMaya.MFnEnumAttribute()

    CollisionDeformer.backface = e_attr.create("backface_culling", "bkcul", 0)
    e_attr.addField("off", 0)
    e_attr.addField("on", 1)
    e_attr.setHidden(False)
    e_attr.setKeyable(True)
    e_attr.setStorable(True)

    CollisionDeformer.sculptmode = e_attr.create("sculpt_mode", "snmd", 0)
    e_attr.addField("off", 0)
    e_attr.addField("on", 1)
    e_attr.setHidden(False)
    e_attr.setKeyable(True)
    e_attr.setStorable(True)

    # add attribute
    try:
        CollisionDeformer.addAttribute(CollisionDeformer.collider)
        CollisionDeformer.addAttribute(CollisionDeformer.bulge)
        CollisionDeformer.addAttribute(CollisionDeformer.bulgeextend)
        CollisionDeformer.addAttribute(CollisionDeformer.colliderMatrix)
        CollisionDeformer.addAttribute(CollisionDeformer.backface)
        CollisionDeformer.addAttribute(CollisionDeformer.sculptmode)
        CollisionDeformer.addAttribute(CollisionDeformer.bulgeshape)
        CollisionDeformer.addAttribute(CollisionDeformer.offset)
        CollisionDeformer.addAttribute(CollisionDeformer.colliderBBoxSize)
        output_geom = K_OUTPUT_GEOM
        CollisionDeformer.attributeAffects(CollisionDeformer.collider, output_geom)
        CollisionDeformer.attributeAffects(CollisionDeformer.offset, output_geom)
        CollisionDeformer.attributeAffects(CollisionDeformer.colliderBBoxSize, output_geom)
        CollisionDeformer.attributeAffects(CollisionDeformer.bulge, output_geom)
        CollisionDeformer.attributeAffects(CollisionDeformer.bulgeextend, output_geom)
        CollisionDeformer.attributeAffects(CollisionDeformer.colliderMatrix, output_geom)
        CollisionDeformer.attributeAffects(CollisionDeformer.backface, output_geom)
        CollisionDeformer.attributeAffects(CollisionDeformer.sculptmode, output_geom)
        CollisionDeformer.attributeAffects(CollisionDeformer.bulgeshape, output_geom)
    except RuntimeError:
        sys.stderr.write("Failed to create attributes of %s node\n" % K_PLUGIN_NODE_TYPE_NAME)


# initialize the script plug-in
def initialize_plugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject, "Lorenzo Argentieri", "0.1")
    try:
        mplugin.registerNode(K_PLUGIN_NODE_TYPE_NAME, COLLISION_DEFORMER_ID, node_creator, node_initializer,
                             OpenMayaMPx.MPxNode.kDeformerNode)
    except RuntimeError:
        sys.stderr.write("Failed to register node: %s\n" % K_PLUGIN_NODE_TYPE_NAME)


# uninitialize the script plug-in
def uninitialize_plugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.deregisterNode(COLLISION_DEFORMER_ID)
    except RuntimeError:
        sys.stderr.write("Failed to unregister node: %s\n" % K_PLUGIN_NODE_TYPE_NAME)


mel = '''
global proc collisionDeformer()
{
    string $sel[] = `ls -sl -tr`;
    if (size($sel)==2)
    {
        string $collider = $sel[0];
        string $target = $sel[1];
        string $collidershape[] = `listRelatives -s $collider`;
        string $collisiondeformer[] = `deformer -typ "collisionDeformer" -n "collisionDeformer" $target`;
        connectAttr -f ($collidershape[0]+".worldMesh[0]") ($collisiondeformer[0]+".collider");
        connectAttr -f ($collider+".matrix") ($collisiondeformer[0]+".colliderMatrix");
        connectAttr -f ($collider+".boundingBox.boundingBoxSize") ($collisiondeformer[0]+".colliderBBoxSize");
    }
    else
    {
        error "please select two meshes: first the collider mesh then the mesh that should be deformed.";
    }
}


    global proc AEcollisionDeformerNew( string $attributeName1, string $attributeName2) {
        checkBoxGrp -numberOfCheckBoxes 1 -label "Backface Culling" culling;
        checkBoxGrp -numberOfCheckBoxes 1 -label "Sculpt Mode" sculpt;

        connectControl -index 2 culling ($attributeName1);
        connectControl -index 2 sculpt ($attributeName2);
    }

    global proc AEcollisionDeformerReplace( string $attributeName1, string $attributeName2) {
        connectControl -index 2 culling ($attributeName1);
        connectControl -index 2 sculpt ($attributeName2);
    }

    global proc AEcollisionDeformerTemplate( string $nodeName )
    {
        // the following controls will be in a scrollable layout
        editorTemplate -beginScrollLayout;

            // add a bunch of common properties
            editorTemplate -beginLayout "Collision Deformer Attributes" -collapse 0;
                editorTemplate -callCustom "AEcollisionDeformerNew" "AEcollisionDeformerReplace" "backface_culling" "sculpt_mode";
                editorTemplate -addSeparator;
                editorTemplate -addControl  "bulge" ;
                editorTemplate -addControl  "bulgeextend" ;
                editorTemplate -addControl  "offset" ;
                editorTemplate -addControl  "envelope" ;
                AEaddRampControl "bulgeshape" ;

            editorTemplate -endLayout;

            // include/call base class/node attributes
            AEdependNodeTemplate $nodeName;

            // add any extra attributes that have been added
            editorTemplate -addExtraControls;

        editorTemplate -endScrollLayout;
    }
'''
meval(mel)

# Maya plugin entry points (must use exact names)
initializePlugin = initialize_plugin
uninitializePlugin = uninitialize_plugin

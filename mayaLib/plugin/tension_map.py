"""Maya plugin for mesh tension visualization via vertex colors.

This plugin was ported to Python from C++ by Anno Schachner.
Original C++ implementation: https://github.com/wiremas/tension

The tensionMap node compares original and deformed mesh geometry to calculate
edge length changes, then applies color ramps to visualize areas of compression
(green) and stretching (red) on the mesh surface. Useful for skin weight painting
and deformation quality control.

Attributes:
    orig (mesh): Original undeformed mesh geometry
    deform (mesh): Deformed mesh geometry
    out (mesh): Output mesh with vertex colors applied
    color (ramp): Color ramp for tension visualization (green=compression, red=stretch)
"""

import sys

import maya.api.OpenMaya as om2
import maya.OpenMaya as om

K_PLUGIN_NODE_NAME = "tensionMap"
ORIG_ATTR_NAME = "orig"
DEFORMED_ATTR_NAME = "deform"
K_PLUGIN_NODE_CLASSIFY = "utility/general"
K_PLUGIN_NODE_ID = om2.MTypeId(0x86018)


def maya_use_new_api():
    """Marker function to indicate Maya Python API 2.0 usage.

    This function must be present for Maya to load the plugin
    using the API 2.0 interface.
    """
    pass


class TensionMap(om2.MPxNode):
    """Maya plugin node for visualizing mesh deformation tension via vertex colors.

    Compares original and deformed mesh geometry to calculate edge length changes,
    then applies a color ramp to visualize areas of compression (green) and stretching
    (red) on the mesh surface. Useful for skin weight evaluation and deformation quality control.

    Attributes:
        a_orig_shape: Original undeformed mesh geometry input
        a_deformed_shape: Deformed mesh geometry input
        a_out_shape: Output mesh with vertex colors applied
        a_color_ramp: Color ramp for tension visualization

    Notes:
        This is a Maya Python API 2.0 node. Requires maya_useNewAPI() declaration.
        Color ramp is automatically initialized with green (0.0), black (0.5), red (1.0).
    """

    a_orig_shape = om2.MObject()
    a_deformed_shape = om2.MObject()
    a_out_shape = om2.MObject()
    a_color_ramp = om2.MObject()

    is_deformed_dirty = True
    is_orig_dirty = True
    orig_edge_len_array = []
    deformed_edge_len_array = []

    def __init__(self):
        """Initialize TensionMap node.

        Calls parent class constructor to set up MPxNode.
        """
        om2.MPxNode.__init__(self)

    def initialize_ramp(self, parent_node, ramp_obj, index, position, value, interpolation):
        """Initialize a color ramp attribute with a specific value and position.

        Args:
            parent_node (MObject): Parent node containing the ramp attribute.
            ramp_obj (MObject): Ramp attribute object.
            index (int): Index of the ramp entry.
            position (float): Position along the ramp (0.0-1.0).
            value (list): RGB color value as [r, g, b].
            interpolation (int): Interpolation type (1 for linear).
        """
        ramp_plug = om2.MPlug(parent_node, ramp_obj)
        element_plug = ramp_plug.elementByLogicalIndex(index)
        position_plug = element_plug.child(0)
        position_plug.setFloat(position)
        value_plug = element_plug.child(1)
        value_plug.child(0).setFloat(value[0])
        value_plug.child(1).setFloat(value[1])
        value_plug.child(2).setFloat(value[2])

        interp_plug = element_plug.child(2)
        interp_plug.setInt(interpolation)

    def postConstructor(self):  # noqa: N802
        """Initialize color ramp with green-black-red gradient.

        Sets up the default color ramp for tension visualization:
        - Green at 0.0 (compression)
        - Black at 0.5 (neutral)
        - Red at 1.0 (stretching)
        """
        self.initialize_ramp(
            self.thisMObject(), self.a_color_ramp, 0, 0.0, om2.MColor((0, 1, 0, 1)), 1
        )
        self.initialize_ramp(
            self.thisMObject(), self.a_color_ramp, 1, 0.5, om2.MColor((0, 0, 0, 1)), 1
        )
        self.initialize_ramp(
            self.thisMObject(), self.a_color_ramp, 2, 1.0, om2.MColor((1, 0, 0, 1)), 1
        )

    def setDependentsDirty(self, dirty_plug, affected_plugs):  # noqa: N802
        """Mark geometry plugs dirty when input meshes change.

        Args:
            dirty_plug (MPlug): The plug that was dirtied.
            affected_plugs (MPlugArray): Array of plugs affected by the change.
        """
        if dirty_plug.partialName() == DEFORMED_ATTR_NAME:
            self.is_deformed_dirty = True
        else:
            self.is_deformed_dirty = False

        if dirty_plug.partialName() == ORIG_ATTR_NAME:
            self.is_orig_dirty = True
        else:
            self.is_orig_dirty = False

    def compute(self, plug, data):
        """Main compute method for tension map visualization.

        Calculates edge length changes between original and deformed meshes,
        then applies color ramp to visualize tension as vertex colors.

        Args:
            plug (MPlug): The output plug being computed.
            data (MDataBlock): Data block containing input and output values.
        """
        if plug == self.a_out_shape:
            this_obj = self.thisMObject()
            orig_handle = data.inputValue(self.a_orig_shape)
            deformed_handle = data.inputValue(self.a_deformed_shape)
            out_handle = data.outputValue(self.a_out_shape)
            color_attribute = om2.MRampAttribute(this_obj, self.a_color_ramp)

            if self.is_orig_dirty:
                self.orig_edge_len_array = self.get_edge_len(orig_handle)
            if self.is_deformed_dirty:
                self.deformed_edge_len_array = self.get_edge_len(deformed_handle)

            out_handle.copy(deformed_handle)
            out_handle.setMObject(deformed_handle.asMesh())

            out_mesh = out_handle.asMesh()
            mesh_fn = om2.MFnMesh(out_mesh)
            num_verts = mesh_fn.numVertices
            vert_colors = om2.MColorArray()
            vert_ids = om2.MIntArray()
            vert_colors.setLength(num_verts)
            vert_ids.setLength(num_verts)

            for i in range(num_verts):
                delta = 0
                vert_color = om2.MColor()
                if len(self.orig_edge_len_array) == len(self.deformed_edge_len_array):
                    delta = (
                        (self.orig_edge_len_array[i] - self.deformed_edge_len_array[i])
                        / self.orig_edge_len_array[i]
                    ) + 0.5
                else:
                    delta = 0.5
                vert_color = color_attribute.getValueAtPosition(delta)
                vert_colors.__setitem__(i, vert_color)
                vert_ids.__setitem__(i, i)
            mesh_fn.setVertexColors(vert_colors, vert_ids)
        data.setClean(plug)

    def get_edge_len(self, mesh_handle):
        """Calculate average edge length for each vertex.

        Args:
            mesh_handle (MDataHandle): Handle to mesh geometry.

        Returns:
            list: Average edge length for each vertex in the mesh.
        """
        edge_len_array = []

        mesh_obj = mesh_handle.asMesh()
        edge_iter = om2.MItMeshEdge(mesh_obj)
        vert_iter = om2.MItMeshVertex(mesh_obj)
        while not vert_iter.isDone():
            length_sum = 0.0
            connected_edges = om2.MIntArray()
            connected_edges = vert_iter.getConnectedEdges()
            for i in range(connected_edges.__len__()):
                edge_iter.setIndex(connected_edges[i])
                length = edge_iter.length(om2.MSpace.kWorld)
                length_sum += length * 1.0

            length_sum = length_sum / connected_edges.__len__()
            edge_len_array.append(length_sum)
            vert_iter.next()
        return edge_len_array


def node_creator():
    """Create and return a new TensionMap node instance.

    Returns:
        TensionMap: New instance of the TensionMap node.
    """
    return TensionMap()


def initialize():
    """Initialize TensionMap node attributes.

    Creates and registers the input/output attributes for the node.
    """
    t_attr = om2.MFnTypedAttribute()

    TensionMap.a_orig_shape = t_attr.create(ORIG_ATTR_NAME, ORIG_ATTR_NAME, om2.MFnMeshData.kMesh)
    t_attr.storable = True

    TensionMap.a_deformed_shape = t_attr.create(
        DEFORMED_ATTR_NAME, DEFORMED_ATTR_NAME, om2.MFnMeshData.kMesh
    )
    t_attr.storable = True

    TensionMap.a_out_shape = t_attr.create("out", "out", om2.MFnMeshData.kMesh)
    t_attr.writable = False
    t_attr.storable = False

    TensionMap.a_color_ramp = om2.MRampAttribute().createColorRamp("color", "color")
    TensionMap.addAttribute(TensionMap.a_orig_shape)
    TensionMap.addAttribute(TensionMap.a_deformed_shape)
    TensionMap.addAttribute(TensionMap.a_out_shape)
    TensionMap.addAttribute(TensionMap.a_color_ramp)
    TensionMap.attributeAffects(TensionMap.a_orig_shape, TensionMap.a_out_shape)
    TensionMap.attributeAffects(TensionMap.a_deformed_shape, TensionMap.a_out_shape)
    TensionMap.attributeAffects(TensionMap.a_color_ramp, TensionMap.a_out_shape)


# AE template that put the main attributes into the main attribute section
# @staticmethod
def ae_template_string(node_name):
    """Generate Attribute Editor template MEL code for TensionMap node.

    Args:
        node_name (str): Name of the node to create template for.

    Returns:
        str: MEL procedure code for the Attribute Editor template.
    """
    templ_str = ""
    templ_str += f"global proc AE{node_name}Template(string $nodeName)\n"
    templ_str += "{\n"
    templ_str += "editorTemplate -beginScrollLayout;\n"
    templ_str += '    editorTemplate -beginLayout "Color Remaping" -collapse 0;\n'
    templ_str += '        AEaddRampControl( $nodeName + ".color" );\n'
    templ_str += "    editorTemplate -endLayout;\n"

    templ_str += "editorTemplate -addExtraControls; // add any other attributes\n"
    templ_str += "editorTemplate -endScrollLayout;\n"
    templ_str += "}\n"

    return templ_str


def initialize_plugin(mobject):
    """Register the TensionMap plugin with Maya.

    Args:
        mobject (MObject): The plugin's MObject passed by Maya.

    Raises:
        RuntimeError: If node registration fails.
    """
    mplugin = om2.MFnPlugin(mobject)
    try:
        mplugin.registerNode(K_PLUGIN_NODE_NAME, K_PLUGIN_NODE_ID, node_creator, initialize)
        om.MGlobal.executeCommand(ae_template_string(K_PLUGIN_NODE_NAME))
    except RuntimeError:
        sys.stderr.write("Failed to register node: " + K_PLUGIN_NODE_NAME)
        raise


def uninitialize_plugin(mobject):
    """Unregister the TensionMap plugin from Maya.

    Args:
        mobject (MObject): The plugin's MObject passed by Maya.

    Raises:
        RuntimeError: If node deregistration fails.
    """
    mplugin = om2.MFnPlugin(mobject)
    try:
        mplugin.deregisterNode(K_PLUGIN_NODE_ID)
    except RuntimeError:
        sys.stderr.write("Failed to deregister node: " + K_PLUGIN_NODE_NAME)
        raise


# Maya plugin entry points (must use exact names)
initializePlugin = initialize_plugin  # noqa: N816
uninitializePlugin = uninitialize_plugin  # noqa: N816

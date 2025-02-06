import maya.cmds as cmds

from mayaLib.bifrostLib import bifrost_api as bifrost
from mayaLib.bifrostLib import bifrost_util_nodes


def getAllObjectUnderGroup(group, type='mesh', full_path=True):
    """
    Return all object of given type under group
    Args:
        group (string): group name
        type (string): object type

    Returns:
        (string[]): object list

    """

    objList = None

    if type == 'mesh':
        objList = [cmds.listRelatives(o, p=1, fullPath=full_path)[0] for o in
                   cmds.listRelatives(group, ad=1, type=type, fullPath=full_path)]

    if type == 'nurbsSurface':
        objList = [cmds.listRelatives(o, p=1, fullPath=full_path)[0] for o in
                   cmds.listRelatives(group, ad=1, type=type, fullPath=full_path)]

    if type == 'transform':
        geoList = [cmds.listRelatives(o, p=1, fullPath=full_path)[0] for o in
                   cmds.listRelatives(group, ad=1, type='mesh', fullPath=full_path)]
        objList = [o for o in cmds.listRelatives(group, ad=1, type=type, fullPath=full_path) if o not in geoList]

    objList = list(set(objList))
    objList.sort()

    return objList


def get_all_deformed_and_constrained(group):
    """
    Get all mesh deformed and constrained under a group
    Args:
        group (string): root group name

    Returns:
        (string[]): list of mesh with deformer
        (string[]): list of mesh without deformer

    """
    mesh_list = getAllObjectUnderGroup(group, type='mesh')

    deformed_list = []
    undeformed_list = []
    for mesh in mesh_list:
        history = [s for s in cmds.listHistory(mesh)]

        if len(history) > 1:
            deformed_list.append(mesh)
        else:
            undeformed_list.append(mesh)

    return deformed_list, undeformed_list


class USDCharacterBuild(object):
    """
    Build Bifrost nodes to manage usd
    """

    def __init__(self, name='', root_node='geo', save_usd_file='tmp', file_ext='usdc', single_usd=False, connect_output=True, debug=False):
        """
        Constructor
        Args:
            geo_list (string[]): list of geos
            name (string): name of the bifrost graph
            root_node (string): default top search group
            save_usd_file (string): filename to save
            file_ext (string): USD file extension
            connect_output (bool):
            debug (bool):
        """

        self.file_ext = file_ext
        self.single_usd = single_usd
        self.root_node = self.get_name_dict(cmds.ls(root_node, long=True)[-1])
        self.bifrost_shape, self.bifrost_transform = self.create_bifrost_graph(name)

        self.create_usd_stage_node = bifrost.bf_create_node(self.bifrost_shape, "BifrostGraph,USD::Stage,create_usd_stage")
        self.time_node = bifrost.bf_create_node(self.bifrost_shape, "BifrostGraph,Core::Time,time")

        bifrost.bf_add_output_port(self.bifrost_shape, 'input', 'start_frame', 'float')
        bifrost.bf_add_output_port(self.bifrost_shape, 'input', 'end_frame', 'float')
        bifrost.bf_add_output_port(self.bifrost_shape, 'input', 'layer_index', 'int')

        external_usd_input = bifrost.bf_add_output_port(self.bifrost_shape, '/input', "external_usd", "string")
        self.file_ext_input = bifrost.bf_add_output_port(self.bifrost_shape, '/input', "file_extension", "string")

        self.type_manager_compound = bifrost_util_nodes.file_type_manager(self.bifrost_shape, self.create_usd_stage_node)

        # Create Preview Compound
        self.preview_compound = bifrost_util_nodes.build_preview_compound(self.bifrost_shape)

        # Make external usd file available
        bifrost.bf_connect(self.bifrost_shape, external_usd_input, self.preview_compound + '.file')

        # Set Bifrost initial values
        self.set_start_frame(0)
        self.set_end_frame(0)
        #cmds.setAttr(self.bifrost_shape + '.layer', save_usd_file, type='string')
        cmds.setAttr(self.bifrost_shape + '.file_extension', file_ext, type='string')

        if connect_output:
            self.id_array_node, self.layer_array_node = self.connect_output()

        # Set USD Stage Sharable
        self.maya_usd_stage = bifrost.get_maya_usd_stage()
        bifrost.set_maya_usd_stage_shareable(self.maya_usd_stage)

        if not debug:
            #cmds.delete(cmds.listRelatives(maya_usd_stage, p=True))

            # Close Bifrost Windows
            from PySide2.QtWidgets import QApplication
            # close graph editor
            for widget in QApplication.allWidgets():
                try:
                    if widget.windowTitle() == "Bifrost Graph Editor":
                        widget.close()
                        break
                except:
                    pass

    def get_name_dict(self, full_path):
        """
        Return Long Name and Short Name of objects in a dict
        Args:
            long_name (string): long name

        Returns:
            (dict)

        """
        short_name = full_path.split('|')[-1]
        long_name = full_path.replace('|', '_')[1:]
        name_dict = {'full_path': full_path, 'long_name': long_name, 'short_name': short_name}

        return name_dict

    def create_bifrost_graph(self, name='usd'):
        """
        Create bifrost Graph
        Args:
            name (string): Name of the Graph

        Returns:
            (string): bifrost shape node
            (string): bifrost transform node

        """
        bifrost_shape = bifrost.create_bifrost_graph(name)
        bifrost_transform = cmds.listRelatives(bifrost_shape, p=True)[-1]

        return bifrost_shape, bifrost_transform

    def get_maya_usd_stage_shape(self):
        """
        Get Maya USD Stage Shape
        Returns:
            (string): USD Stage shape node
        """
        return self.maya_usd_stage

    def get_maya_usd_stage(self):
        """
        Get Maya USD Stage Transform
        Returns:
            (string): USD Stage node
        """
        return cmds.listRelatives(self.maya_usd_stage, p=True)[-1]

    def get_bifrost_transform(self):
        """
        Get Maya bifrost transform
        Returns:
            (string): Maya bifrost transform

        """
        return self.bifrost_transform

    def get_bifrost_shape(self):
        """
        Get Maya bifrost transform
        Returns:
            (string): Maya bifrost shape
        """

        return self.bifrost_shape

    def connect_output(self):
        """
        Connect bifrost output node
        Returns:

        """
        id_array_node = bifrost.bf_create_node(self.bifrost_shape, "BifrostGraph,Core::Array,build_array")
        id_array_node = bifrost.bf_rename_node(self.bifrost_shape, id_array_node, 'id_build_array')

        layer_array_node = bifrost.bf_create_node(self.bifrost_shape, "BifrostGraph,Core::Array,build_array")
        layer_array_node = bifrost.bf_rename_node(self.bifrost_shape, layer_array_node, 'layer_build_array')

        bifrost.bf_add_input_port(self.bifrost_shape, 'output', 'out_stage', 'BifrostUsd::Stage')
        try:
            id_array_output = bifrost.bf_add_input_port(self.bifrost_shape, 'output', 'id_array', 'array<long>')
        except:
            pass

        bifrost.bf_connect(self.bifrost_shape, self.preview_compound + '.out_stage', 'output.out_stage')
        bifrost.bf_connect(self.bifrost_shape, id_array_node + '.array', 'output.id_array')# "/build_array1.array" ".id_array"
        bifrost.bf_connect(self.bifrost_shape, layer_array_node + '.array', self.preview_compound + '.sublayers')#"/layer_build_array.array" "/Preview_Compound.sublayers"

        return id_array_node, layer_array_node

    def set_start_frame(self, frame):
        """
        Set Start Frame in the bifrost input
        Args:
            frame (float): start frame

        Returns:

        """
        cmds.setAttr(self.bifrost_shape + ".start_frame", frame)

    def set_end_frame(self, frame):
        """
        Set End Frame in the bifrost input
        Args:
            frame (float): end frame

        Returns:

        """
        cmds.setAttr(self.bifrost_shape + ".end_frame", frame)

    def add_stage_custom_layer_data(self, data, product):
        add_custom_layer_data_node = bifrost.bf_create_node(self.bifrost_shape, "BifrostGraph,USD::Stage,set_stage_custom_layer_data")
        bifrost.bf_connect(self.bifrost_shape, self.create_usd_stage_node + '.stage', add_custom_layer_data_node + '.stage')

        custom_layer_data_compound = bifrost_util_nodes.add_custom_layer_data(self.bifrost_shape, data, add_custom_layer_data_node, product=product)
        #bifrost.bf_connect(self.bifrost_shape, self.create_usd_stage_node + '.stage', add_custom_layer_data_node + '.stage')

        return add_custom_layer_data_node

    def add_product(self, deformed_geo_list=[], undeformed_geo_list=[], product_name='product', custom_layer_data={}):
        node_list = []

        # Publish Structure
        add_to_stage_node, save_usd_stage_node, set_stage_time_code_node, add_custom_layer_data_node = self.create_default_usd_stage(product_name, data=custom_layer_data)
        node_list.extend([add_to_stage_node, save_usd_stage_node, set_stage_time_code_node, add_custom_layer_data_node])

        if self.single_usd:
            add_to_stage_compound = bifrost.bf_create_compound(self.bifrost_shape, [self.add_to_stage_node])
            bifrost.bf_feedback_port(self.bifrost_shape, add_to_stage_compound, 'out_stage', 'stage')
            node_list.append(add_to_stage_compound)
        else:
            string_join_node, build_array_node, extension_value_node = bifrost_util_nodes.build_name(self.bifrost_shape, self.time_node, product=product_name, extension_format=self.file_ext, skip_frame=False)
            bifrost.bf_connect(self.bifrost_shape, string_join_node + '.joined', save_usd_stage_node + '.file')
            bifrost.bf_connect(self.bifrost_shape, self.file_ext_input, extension_value_node + ".value")
            node_list.extend([string_join_node, build_array_node, extension_value_node])

        # Create Prims
        for geo in deformed_geo_list:
            self.add_mesh(geo)
        for geo in undeformed_geo_list:
            self.add_undeformed_mesh(geo)

        ###############

        # Block unwanted data
        iterator_node = self.create_block_loop(add_to_stage_node, set_stage_time_code_node)
        node_list.append(iterator_node)
        ################

        # Create Payload and Reference Compound
        reference_compound = bifrost_util_nodes.build_referece_peyload(self.bifrost_shape, layer_name=product_name, is_payload="0")
        payload_compound = bifrost_util_nodes.build_referece_peyload(self.bifrost_shape, layer_name=product_name, is_payload="1")
        bifrost.bf_connect(self.bifrost_shape, save_usd_stage_node + '.out_stage',payload_compound + '.stage')
        bifrost.bf_connect(self.bifrost_shape, payload_compound + '.out_stage', reference_compound + '.stage')
        #bifrost.bf_connect(self.bifrost_shape, reference_compound + '.out_stage', self.preview_compound + '.stage')
        node_list.extend([reference_compound.replace('/', ''), payload_compound.replace('/', '')])

        array_node = bifrost.bf_create_node(self.bifrost_shape, "BifrostGraph,Core::Array,build_array")
        node_list.append(array_node)

        id_payload_output = bifrost.bf_add_input_port(self.bifrost_shape, array_node, 'id', 'long')
        id_reference_output = bifrost.bf_add_input_port(self.bifrost_shape, array_node, 'id', 'long')

        bifrost.bf_connect(self.bifrost_shape, payload_compound + '.id', id_payload_output)
        bifrost.bf_connect(self.bifrost_shape, reference_compound + '.id', id_reference_output)

        # Converto to layer
        get_root_layer_node = bifrost.bf_create_node(self.bifrost_shape, "BifrostGraph,USD::Layer,get_root_layer")
        node_list.append(get_root_layer_node)
        bifrost.bf_connect(self.bifrost_shape, reference_compound + '.out_stage', get_root_layer_node + '.stage')

        product_compound = bifrost.bf_create_compound(self.bifrost_shape, compound_node_list=node_list, compound_name=product_name + '_compound')
        product_layer_output = bifrost.bf_add_input_port(self.bifrost_shape, product_compound + '/output', 'layer', "auto")
        bifrost.bf_connect(self.bifrost_shape, product_compound + '/' + get_root_layer_node + '.layer', product_compound + '/' + product_layer_output)

        id_array_output = bifrost.bf_add_input_port(self.bifrost_shape, product_compound + '/output', product_name + '_id_array', "array<long>")
        bifrost.bf_connect(self.bifrost_shape, product_compound + '/' + array_node + '.array', product_compound + '.' + product_name + '_id_array')

        product_id_output = bifrost.bf_add_input_port(self.bifrost_shape, self.id_array_node, product_name + '_id_array', "array<long>")
        bifrost.bf_connect(self.bifrost_shape, product_compound + '.' + product_name + '_id_array', product_id_output)

        array_layer_output = bifrost.bf_add_input_port(self.bifrost_shape, self.layer_array_node, product_name + '_layer_array', "BifrostUsd::Layer")
        bifrost.bf_connect(self.bifrost_shape, product_compound + '.' + 'layer', array_layer_output)


    def create_default_usd_stage(self, product, data):
        """
        Create default Bifrost USD stage
        Returns:
            (string): bifrost Add to Stage node name
            (string): bifrost Time node name
            (string): bifrost Save Stage node name

        """
        # Add Input Port
        bifrost.bf_add_output_port(self.bifrost_shape, 'input', product + '_file', 'string')  # node, port_name, port_type
        bifrost.bf_add_output_port(self.bifrost_shape, 'input', 'save_' + product + '_to_file', 'bool')

        # Nodes Creation
        add_to_stage_node = bifrost.bf_create_node(self.bifrost_shape, "BifrostGraph,USD::Stage,add_to_stage")
        stage_time_code_node = bifrost.bf_create_node(self.bifrost_shape, "BifrostGraph,USD::Stage,set_stage_time_code")
        save_usd_stage_node = bifrost.bf_create_node(self.bifrost_shape, "BifrostGraph,USD::Stage,save_usd_stage")

        add_custom_layer_data_node = self.add_stage_custom_layer_data(data, product=product)

        # Nodes Connections
        bifrost.bf_connect(self.bifrost_shape, self.create_usd_stage_node + '.stage', add_to_stage_node + '.stage')
        bifrost.bf_connect(self.bifrost_shape, add_to_stage_node + '.out_stage', stage_time_code_node + '.stage')
        bifrost.bf_connect(self.bifrost_shape, stage_time_code_node + '.out_stage', save_usd_stage_node + '.stage')

        bifrost.bf_connect(self.bifrost_shape, stage_time_code_node + '.out_stage', add_custom_layer_data_node + '.stage')
        bifrost.bf_connect(self.bifrost_shape, add_custom_layer_data_node + '.out_stage', save_usd_stage_node + '.stage')

        bifrost.bf_connect(self.bifrost_shape, 'input.' + 'save_' + product + '_to_file', save_usd_stage_node + '.enable')

        bifrost.bf_connect(self.bifrost_shape, 'input.start_frame', stage_time_code_node + '.start')
        bifrost.bf_connect(self.bifrost_shape, 'input.end_frame', stage_time_code_node + '.end')
        bifrost.bf_connect(self.bifrost_shape, 'input.layer_index', add_to_stage_node + '.layer_index')

        bifrost.bf_connect(self.bifrost_shape, 'input.' + product + '_file', save_usd_stage_node + '.file')

        return add_to_stage_node, save_usd_stage_node, stage_time_code_node, add_custom_layer_data_node

    def create_prim(self, name_dict, prim_type="Xform", specifier_over=False):
        """
        Create bifrost prim from Maya object
        Args:
            obj (string): Maya object name
            prim_type (string): type of the prim

        Returns:
            (string): bifrost node name of the prim

        """
        # List all Nodes in the Grpah
        graph_node_list = cmds.vnnCompound(self.bifrost_shape, "/", listNodes=True)

        node_name = name_dict['long_name'] + '_define_usd_prim'
        if node_name in graph_node_list:

            node = node_name
        else:
            new_node = bifrost.bf_create_node(self.bifrost_shape, "BifrostGraph,USD::Prim,define_usd_prim")
            bifrost.bf_set_node_property(self.bifrost_shape, new_node, "path", '/' + name_dict['short_name'])
            new_node = bifrost.bf_rename_node(self.bifrost_shape, new_node, name_dict['long_name'] + '_define_usd_prim')

            bifrost.bf_set_node_property(self.bifrost_shape, node_name, "type", prim_type)

            if specifier_over:
                bifrost.bf_set_node_property(self.bifrost_shape, node_name, "specifier", "1")  # Set Over

            node = node_name

        return node

    def add_undeformed_mesh_transform(self, mesh_name):
        """
        Add Mesh shape to bifrost and relative mesh prim definition
        Args:
            mesh_name (string): Maya mesh name

        Returns:

        """
        # Add define_usd_transform
        define_usd_transform_node = bifrost.bf_create_node(self.bifrost_shape,
                                                           "BifrostGraph,USD::Attribute,define_usd_transform")
        cmds.vnnCompound(self.bifrost_shape, "/" + define_usd_transform_node, setIsReferenced=False)

        bifrost.bf_add_output_port(self.bifrost_shape, define_usd_transform_node + '/input', "frame", "float")
        bifrost.bf_add_output_port(self.bifrost_shape, define_usd_transform_node + '/input', "use_frame", "bool")

        bifrost.bf_connect(self.bifrost_shape, define_usd_transform_node + '.frame',
                           define_usd_transform_node + '/define_usd_attribute2' + '.frame')
        bifrost.bf_connect(self.bifrost_shape, define_usd_transform_node + '.use_frame',
                           define_usd_transform_node + '/define_usd_attribute2' + '.use_frame')

        bifrost.bf_connect(self.bifrost_shape, define_usd_transform_node + '.frame',
                           define_usd_transform_node + '/define_usd_attribute1' + '.frame')
        bifrost.bf_connect(self.bifrost_shape, define_usd_transform_node + '.use_frame',
                           define_usd_transform_node + '/define_usd_attribute1' + '.use_frame')

        bifrost.bf_connect(self.bifrost_shape, define_usd_transform_node + '.frame',
                           define_usd_transform_node + '/define_usd_attribute3' + '.frame')
        bifrost.bf_connect(self.bifrost_shape, define_usd_transform_node + '.use_frame',
                           define_usd_transform_node + '/define_usd_attribute3' + '.use_frame')

        # Rename node
        node_name = mesh_name + "_define_usd_attribute"
        define_usd_transform_node = bifrost.bf_rename_node(self.bifrost_shape, define_usd_transform_node, node_name)

        return node_name

    def add_undeformed_mesh(self, mesh_name):
        """
        Add Mesh shape to bifrost and relative mesh prim definition
        Args:
            mesh_name (string): Maya mesh name

        Returns:

        """
        name_dict = self.get_name_dict(mesh_name)

        # Create nodes
        define_mesh_node = bifrost.bf_create_node(self.bifrost_shape, "BifrostGraph,USD::Prim,define_usd_mesh")

        bifrost.bf_set_node_property(self.bifrost_shape, define_mesh_node, "path", '/' + name_dict['short_name'])
        define_mesh_node = bifrost.bf_rename_node(self.bifrost_shape, define_mesh_node,
                                                  name_dict['long_name'] + '_define_usd_mesh')

        self.recursive_build_usd_graph(name_dict, define_mesh_node)

    def add_xform(self, obj, obj_node=None):
        """
        Add xfrom attribute to a Mesh or Prim defintion
        Args:
            obj (string): maya object to connect
            obj_node (string): prim to connect attribute

        Returns:

        """
        name_dict = self.get_name_dict(obj)

        node = name_dict['long_name'] + "_define_usd_attribute"
        connected_node_list = cmds.vnnNode(self.bifrost_shape, '/' + obj_node, listConnectedNodes=1)
        if connected_node_list == None or not (node in connected_node_list):
            # Create input port
            bifrost.bf_add_output_port(self.bifrost_shape, 'input', name_dict['short_name'] + '_translate',
                                       "Math::float3")
            bifrost.bf_add_output_port(self.bifrost_shape, 'input', name_dict['short_name'] + '_rotate', "Math::float3")
            bifrost.bf_add_output_port(self.bifrost_shape, 'input', name_dict['short_name'] + '_scale', "Math::float3")

            # Create nodes
            define_attribute_node = self.add_undeformed_mesh_transform(name_dict['long_name'])
            bifrost.bf_set_node_property(self.bifrost_shape, define_attribute_node, "use_frame", "1")

            # Connect
            bifrost.bf_connect(self.bifrost_shape, self.time_node + '.frame', define_attribute_node + '.frame')

            bifrost.bf_connect(self.bifrost_shape, 'input.' + name_dict['short_name'] + '_translate',
                               define_attribute_node + '.translation')
            bifrost.bf_connect(self.bifrost_shape, 'input.' + name_dict['short_name'] + '_rotate',
                               define_attribute_node + '.rotation')
            bifrost.bf_connect(self.bifrost_shape, 'input.' + name_dict['short_name'] + '_scale',
                               define_attribute_node + '.scale')

            input_port = bifrost.bf_add_input_port(self.bifrost_shape, obj_node,
                                                   "attribute_definitions.attribute_definition", "auto",
                                                   'attribute_definitions')
            bifrost.bf_connect(self.bifrost_shape, define_attribute_node + '.attribute_definitions', input_port)

    def add_mesh(self, mesh_name, add_to_stage_node):
        """
        Add Mesh shape to bifrost and relative mesh prim definition
        Args:
            mesh_name (string): Maya mesh name

        Returns:

        """
        # Manage names
        name_dict = self.get_name_dict(mesh_name)
        node_list = []

        # Creaci una classe
        input_mesh_node = bifrost.bf_add_mesh(self.bifrost_shape, mesh_name)
        define_mesh_node = bifrost.bf_create_node(self.bifrost_shape, "BifrostGraph,USD::Prim,define_usd_mesh")

        mesh_out_port = \
        bifrost.bf_list_all_port(self.bifrost_shape, input_mesh_node, input_port=False, output_port=True)[-1]

        bifrost.bf_connect(self.bifrost_shape, mesh_out_port, define_mesh_node + '.mesh')
        bifrost.bf_connect(self.bifrost_shape, self.time_node + '.frame', define_mesh_node + '.frame')

        bifrost.bf_set_node_property(self.bifrost_shape, define_mesh_node, "path", '/' + name_dict['short_name'])
        define_mesh_node = bifrost.bf_rename_node(self.bifrost_shape, define_mesh_node,
                                                  name_dict['long_name'] + '_define_usd_mesh')

        self.recursive_node_list = []
        self.recursive_build_usd_graph(name_dict, define_mesh_node, add_to_stage_node)

        node_list.append(input_mesh_node)
        node_list.append(define_mesh_node)
        node_list.extend(self.recursive_node_list)

        return node_list

    def recursive_build_usd_graph(self, obj_data, node, add_to_stage_node):
        """
        Recursive build and connect Prims
        Args:
            obj_data (dict): current Maya object, contains 'long_name' and 'short_name'
            node (string): current Bifrost prim node

        Returns:
            None

        """

        # Check if maya object exists
        if cmds.objExists(obj_data['full_path']):
            # get the object parent
            parent = cmds.listRelatives(obj_data['full_path'], p=True, fullPath=True)[-1]
            parent_obj = self.get_name_dict(parent)

            # Check if there is a trnasform connection
            connection_check = cmds.connectionInfo(obj_data['full_path'] + '.tx',
                                                   isDestination=True) or cmds.connectionInfo(
                obj_data['full_path'] + '.ty', isDestination=True) or cmds.connectionInfo(
                obj_data['full_path'] + '.tz',
                isDestination=True) or cmds.connectionInfo(
                obj_data['full_path'] + '.rx', isDestination=True) or cmds.connectionInfo(
                obj_data['full_path'] + '.ry',
                isDestination=True) or cmds.connectionInfo(
                obj_data['full_path'] + '.rz', isDestination=True) or cmds.connectionInfo(
                obj_data['full_path'] + '.sx',
                isDestination=True) or cmds.connectionInfo(
                obj_data['full_path'] + '.sy', isDestination=True) or cmds.connectionInfo(
                obj_data['full_path'] + '.sz', isDestination=True)

            if connection_check:
                self.add_xform(obj_data['full_path'], node)

            # if the current node is the highest in hierarchy
            if parent_obj['short_name'] == self.root_node['short_name']:
                new_node = self.create_prim(parent_obj)

                # Check if there is a trnasform connection
                connection_check = cmds.connectionInfo(parent_obj['full_path'] + '.tx',
                                                       isDestination=True) or cmds.connectionInfo(
                    obj_data['full_path'] + '.ty', isDestination=True) or cmds.connectionInfo(
                    obj_data['full_path'] + '.tz',
                    isDestination=True) or cmds.connectionInfo(
                    obj_data['full_path'] + '.rx', isDestination=True) or cmds.connectionInfo(
                    obj_data['full_path'] + '.ry',
                    isDestination=True) or cmds.connectionInfo(
                    obj_data['full_path'] + '.rz', isDestination=True) or cmds.connectionInfo(
                    obj_data['full_path'] + '.sx',
                    isDestination=True) or cmds.connectionInfo(
                    obj_data['full_path'] + '.sy', isDestination=True) or cmds.connectionInfo(
                    obj_data['full_path'] + '.sz', isDestination=True)

                if connection_check:
                    self.add_xform(parent_obj['full_path'], new_node)

                # Check if the root is already created and connected to the create stage
                connected_node_list = cmds.vnnNode(self.bifrost_shape, '/' + new_node, listConnectedNodes=1)
                if connected_node_list == None or not (node in connected_node_list):
                    input_port = bifrost.bf_add_input_port(self.bifrost_shape, new_node, "children.prim_definition",
                                                           "auto", 'children')
                    bifrost.bf_connect(self.bifrost_shape, node + '.prim_definition', input_port)

                connected_node_list = cmds.vnnNode(self.bifrost_shape, '/' + add_to_stage_node,
                                                   listConnectedNodes=1)
                if not (self.root_node['long_name'] + '_define_usd_prim' in connected_node_list):
                    stage_input_port = bifrost.bf_add_input_port(self.bifrost_shape, add_to_stage_node,
                                                                 "prim_definitions.prim_definition", "auto",
                                                                 'prim_definitions')
                    bifrost.bf_connect(self.bifrost_shape, new_node + '.prim_definition', stage_input_port)

                self.recursive_node_list.append(new_node)

                return None

            else:
                new_node = self.create_prim(parent_obj)
                connected_node_list = cmds.vnnNode(self.bifrost_shape, '/' + new_node, listConnectedNodes=1)

                # Check if the node is already created
                if connected_node_list == None or not (node in connected_node_list):
                    # Check the type of the prim (Transform or Mesh)
                    if bifrost.bf_get_node_type(self.bifrost_shape, node) == "BifrostGraph,USD::Prim,define_usd_mesh":
                        input_port = bifrost.bf_add_input_port(self.bifrost_shape, new_node, "children.mesh_definition",
                                                               "auto", 'children')
                        bifrost.bf_connect(self.bifrost_shape, node + '.mesh_definition', input_port)
                    else:
                        input_port = bifrost.bf_add_input_port(self.bifrost_shape, new_node, "children.prim_definition",
                                                               "auto", 'children')
                        bifrost.bf_connect(self.bifrost_shape, node + '.prim_definition', input_port)

                    self.recursive_build_usd_graph(parent_obj, new_node, add_to_stage_node)
                    self.recursive_node_list.append(new_node)

                else:
                    return None

    def add_block_attribute(self, attr_name, node_name='', prim_path='', parent=''):
        """
        Add Block attribute
        Args:
            attr_name (string): attribute name
            node_name (string): node name
            prim_path (string): path of the prim to block
            parent (string): parent node to connect

        Returns:
            (string): bifrost attribute node
        """
        block_attribute_node = bifrost.bf_create_node(self.bifrost_shape, "BifrostGraph,USD::Attribute,block_attribute",
                                                      parent)
        bifrost.bf_set_node_property(self.bifrost_shape, parent + '/' + block_attribute_node, "name", attr_name)

        if prim_path != '':
            bifrost.bf_set_node_property(self.bifrost_shape, parent + '/' + block_attribute_node, "prim_path",
                                         prim_path)

        # block_attribute_node = bifrost.bf_rename_node(self.bifrost_shape, parent + '/' + block_attribute_node, node_name + '_block_attribute')

        return block_attribute_node

        # vnnConnect
        # "|rig_grp|test_bifrostGraph|test_bifrostGraphShape" "/set_stage_time_code.out_stage" "/block_attribute1.stage";

        # vnnConnect
        # "|rig_grp|test_bifrostGraph|test_bifrostGraphShape" "/block_attribute1.out_stage" "/save_usd_stage.stage";

    def create_block_loop(self, add_to_stage_node, set_stage_time_code_node):
        """
        Create the iterator to block same attribute on multiple prim
        Returns:
            (string): iterator node

        """
        # Create nodes
        get_prim_children_node = bifrost.bf_create_node(self.bifrost_shape, "BifrostGraph,USD::Prim,get_prim_children")
        get_prim_path_node = bifrost.bf_create_node(self.bifrost_shape, "BifrostGraph,USD::Prim,get_prim_path")
        array_size_node = bifrost.bf_create_node(self.bifrost_shape, "BifrostGraph,Core::Array,array_size")
        iterator_node = bifrost.bf_create_node(self.bifrost_shape, "BifrostGraph,Core::Iterators,iterate")

        get_from_array_node = bifrost.bf_create_node(self.bifrost_shape, "BifrostGraph,Core::Array,get_from_array",
                                                     parent='/' + iterator_node)
        face_vertex_counts_block_node = self.add_block_attribute('faceVertexCounts', 'faceVertexCounts',
                                                                 parent='/' + iterator_node)
        face_vertex_indices_block_node = self.add_block_attribute('faceVertexIndices', 'faceVertexIndices',
                                                                  parent='/' + iterator_node)
        primvars_st_block_node = self.add_block_attribute('primvars:st', 'primvars_st', parent='/' + iterator_node)
        primvars_st_indices_block_node = self.add_block_attribute('primvars:st:indices', 'primvars_st_indices',
                                                                  parent='/' + iterator_node)

        # Add ports
        bifrost.bf_add_output_port(self.bifrost_shape, iterator_node + '/input', 'out_stage', 'auto')
        bifrost.bf_add_output_port(self.bifrost_shape, iterator_node + '/input', 'path', 'auto')
        bifrost.bf_add_input_port(self.bifrost_shape, iterator_node + '/output', "out_stage1", "auto")

        # Connects nodes
        bifrost.bf_connect(self.bifrost_shape, add_to_stage_node + '.out_stage', get_prim_children_node + '.stage')
        bifrost.bf_connect(self.bifrost_shape, get_prim_children_node + '.children', get_prim_path_node + '.prim')
        bifrost.bf_connect(self.bifrost_shape, get_prim_path_node + '.path', array_size_node + '.array')
        bifrost.bf_connect(self.bifrost_shape, array_size_node + '.size', iterator_node + '.max_iterations')

        bifrost.bf_connect(self.bifrost_shape, add_to_stage_node + '.out_stage', iterator_node + '.out_stage')
        bifrost.bf_connect(self.bifrost_shape, get_prim_path_node + '.path', iterator_node + '.path')

        ## Connections inside loop
        bifrost.bf_connect(self.bifrost_shape, iterator_node + '.path',
                           iterator_node + '/' + get_from_array_node + '.array')
        bifrost.bf_connect(self.bifrost_shape, iterator_node + '.current_index',
                           iterator_node + '/' + get_from_array_node + '.index')

        bifrost.bf_connect(self.bifrost_shape, iterator_node + '.out_stage',
                           iterator_node + '/' + face_vertex_counts_block_node + '.stage')
        bifrost.bf_connect(self.bifrost_shape, iterator_node + '/' + face_vertex_counts_block_node + '.out_stage',
                           iterator_node + '/' + face_vertex_indices_block_node + '.stage')
        bifrost.bf_connect(self.bifrost_shape, iterator_node + '/' + face_vertex_indices_block_node + '.out_stage',
                           iterator_node + '/' + primvars_st_block_node + '.stage')
        bifrost.bf_connect(self.bifrost_shape, iterator_node + '/' + primvars_st_block_node + '.out_stage',
                           iterator_node + '/' + primvars_st_indices_block_node + '.stage')
        bifrost.bf_connect(self.bifrost_shape, iterator_node + '/' + primvars_st_indices_block_node + '.out_stage',
                           iterator_node + '.out_stage1')

        bifrost.bf_connect(self.bifrost_shape, iterator_node + '/' + get_from_array_node + '.value',
                           iterator_node + '/' + face_vertex_counts_block_node + '.prim_path')
        bifrost.bf_connect(self.bifrost_shape, iterator_node + '/' + get_from_array_node + '.value',
                           iterator_node + '/' + face_vertex_indices_block_node + '.prim_path')
        bifrost.bf_connect(self.bifrost_shape, iterator_node + '/' + get_from_array_node + '.value',
                           iterator_node + '/' + primvars_st_block_node + '.prim_path')
        bifrost.bf_connect(self.bifrost_shape, iterator_node + '/' + get_from_array_node + '.value',
                           iterator_node + '/' + primvars_st_indices_block_node + '.prim_path')

        # Connect output
        bifrost.bf_connect(self.bifrost_shape, iterator_node + '.out_stage1', set_stage_time_code_node + '.stage')

        # Settings
        bifrost.bf_sequence_port(self.bifrost_shape, '/' + iterator_node, "out_stage", "out_stage1")
        bifrost.bf_set_node_property(self.bifrost_shape, get_prim_children_node, "prim_path",
                                     '/' + self.root_node['short_name'])
        bifrost.bf_set_node_property(self.bifrost_shape, get_prim_children_node, "descendant_mode", "3")

        return iterator_node


if __name__ == "__main__":
    ## Use case
    to_delete = cmds.ls('*_bifrostGraph', '*_bifrostGraph?' 'mayaUsdProxy*')
    cmds.delete(to_delete)
    geo_list = getAllObjectUnderGroup('geo')
    print('Geo list: ', geo_list)
    usd_character_manager = USDCharacterBuild(geo_list, name='test', root_node='root', file_ext='usdc', debug=True)
    bifrost_transform = usd_character_manager.get_bifrost_transform()
    bifrost_shape = usd_character_manager.get_bifrost_shape()

    output_path = 'temp_file'
    cmds.setAttr(bifrost_shape + ".layer", output_path, type="string")


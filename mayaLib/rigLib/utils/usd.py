import maya.cmds as cmds
from mayaLib.rigLib.bifrost import bifrost
from mayaLib.rigLib.bifrost import bifrost_util_nodes


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
        objList = [cmds.listRelatives(o, p=1, fullPath=full_path)[0] for o in cmds.listRelatives(group, ad=1, type=type, fullPath=full_path)]

    if type == 'nurbsSurface':
        objList = [cmds.listRelatives(o, p=1, fullPath=full_path)[0] for o in cmds.listRelatives(group, ad=1, type=type, fullPath=full_path)]

    if type == 'transform':
        geoList = [cmds.listRelatives(o, p=1, fullPath=full_path)[0] for o in cmds.listRelatives(group, ad=1, type='mesh', fullPath=full_path)]
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

    def __init__(self, deformed_geo_list=[], undeformed_geo_list=[], name='', root_node='geo', save_usd_file='tmp', connect_output=True, debug=False, single_usd=False):
        """
        Constructor
        Args:
            deformed_geo_list (string[]): list of geos with deformers
            undeformed_geo_list (string[]): list of geos without deformers
            name (string): name of the bifrost graph
            root_node (string): default top search group
            connect_output (bool):
            debug (bool):
            single_usd (bool): if False use the Value Clips workflow
        """

        self.root_node = root_node
        self.bifrost_shape, self.bifrost_transform = self.create_bifrost_graph(name)
        self.add_to_stage_node, self.time_node, self.save_usd_stage_node, self.set_stage_time_code_node = self.create_default_usd_stage(single_usd)
        
        for geo in deformed_geo_list:
            self.add_mesh(geo)
        for geo in undeformed_geo_list:
            self.add_undeformed_mesh(geo)

        if single_usd:
            add_to_stage_compound = bifrost.bf_create_compound(self.bifrost_shape, [self.add_to_stage_node])
            bifrost.bf_feedback_port(self.bifrost_shape, add_to_stage_compound, 'out_stage', 'stage')
        else:
            string_join_node = bifrost_util_nodes.build_name(self.bifrost_shape, self.time_node, extension_format='usdc')
            bifrost.bf_connect(self.bifrost_shape, string_join_node + '.joined', self.save_usd_stage_node + '.file')

        # Block unwanted data
        self.create_block_loop()

        # Set Bifrost initial values
        self.set_start_frame(0)
        self.set_end_frame(1)
        cmds.setAttr(self.bifrost_shape + '.layer', save_usd_file, type='string')
        
        if connect_output:
            self.connect_output()
        
        # Set USD Stage Sharable
        maya_usd_stage = bifrost.get_maya_usd_stage()
        bifrost.set_maya_usd_stage_shareable(maya_usd_stage)
        
        if not debug:
            cmds.delete(cmds.listRelatives(maya_usd_stage, p=True))
        

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
        
    def get_bifrost_transform(self):
        """
        Get Maya bifrost transform
        Returns:
            (string): Maya bifrost transform

        """
        return self.bifrost_transform
        
    def connect_output(self):
        """
        Connect bifrost output node
        Returns:

        """
        bifrost.bf_add_input_port(self.bifrost_shape, 'output', 'out_stage', 'BifrostUsd::Stage')
        bifrost.bf_connect(self.bifrost_shape, self.save_usd_stage_node + '.out_stage', 'output.out_stage')
        
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
                
    def create_default_usd_stage(self, single_usd=False):
        """
        Create default Bifrost USD stage
        Returns:
            (string): bifrost Add to Stage node name
            (string): bifrost Time node name
            (string): bifrost Save Stage node name

        """
        # Add Input Port
        bifrost.bf_add_output_port(self.bifrost_shape, 'input', 'layer', 'string') # node, port_name, port_type
        bifrost.bf_add_output_port(self.bifrost_shape, 'input', 'start_frame', 'float')
        bifrost.bf_add_output_port(self.bifrost_shape, 'input', 'end_frame', 'float')
        bifrost.bf_add_output_port(self.bifrost_shape, 'input', 'layer_index', 'int')
        bifrost.bf_add_output_port(self.bifrost_shape, 'input', 'publish', 'bool')
        
        # Nodes Creation
        time_node = bifrost.bf_create_node(self.bifrost_shape, "BifrostGraph,Core::Time,time")
        create_usd_stage_node = bifrost.bf_create_node(self.bifrost_shape, "BifrostGraph,USD::Stage,create_usd_stage")
        add_to_stage_node = bifrost.bf_create_node(self.bifrost_shape, "BifrostGraph,USD::Stage,add_to_stage")
        stage_time_code_node = bifrost.bf_create_node(self.bifrost_shape, "BifrostGraph,USD::Stage,set_stage_time_code")
        save_usd_stage_node = bifrost.bf_create_node(self.bifrost_shape, "BifrostGraph,USD::Stage,save_usd_stage")

        if single_usd:
            equal_node = bifrost.bf_create_node(self.bifrost_shape, "BifrostGraph,Core::Logic,equal")
            and_node = bifrost.bf_create_node(self.bifrost_shape, "BifrostGraph,Core::Logic,and")
        
        # Nodes Connections
        bifrost.bf_connect(self.bifrost_shape, create_usd_stage_node + '.stage', add_to_stage_node + '.stage')
        bifrost.bf_connect(self.bifrost_shape, add_to_stage_node + '.out_stage', stage_time_code_node + '.stage')
        bifrost.bf_connect(self.bifrost_shape, stage_time_code_node + '.out_stage', save_usd_stage_node + '.stage')

        if single_usd:
            bifrost.bf_connect(self.bifrost_shape, time_node + '.frame', equal_node + '.first')
            bifrost.bf_connect(self.bifrost_shape, equal_node + '.output', and_node + '.first')
            bifrost.bf_connect(self.bifrost_shape, 'input.end_frame', equal_node + '.second')
            bifrost.bf_connect(self.bifrost_shape, 'input.publish', and_node + '.second')
            bifrost.bf_connect(self.bifrost_shape, and_node + '.output', save_usd_stage_node + '.enable')
        else:
            bifrost.bf_connect(self.bifrost_shape, 'input.publish', save_usd_stage_node + '.enable')

        bifrost.bf_connect(self.bifrost_shape, 'input.start_frame', stage_time_code_node + '.start')
        bifrost.bf_connect(self.bifrost_shape, 'input.end_frame', stage_time_code_node + '.end')
        bifrost.bf_connect(self.bifrost_shape, 'input.layer_index', add_to_stage_node + '.layer_index')
            
        #bifrost.bf_connect(self.bifrost_shape, 'input.layer', create_usd_stage_node + '.layer')
        bifrost.bf_connect(self.bifrost_shape, 'input.layer', save_usd_stage_node + '.file')
        
        return add_to_stage_node, time_node, save_usd_stage_node, stage_time_code_node
        
    def create_prim(self, obj, prim_type="Xform"):
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
        
        node_name = obj + '_define_usd_prim'
        node = ''
        if node_name in graph_node_list:
            
            node = node_name
        else:
            new_node = bifrost.bf_create_node(self.bifrost_shape, "BifrostGraph,USD::Prim,define_usd_prim")
            bifrost.bf_set_node_property(self.bifrost_shape, new_node, "path", '/' + obj)
            bifrost.bf_rename_node(self.bifrost_shape, new_node, obj + '_define_usd_prim')
            
            bifrost.bf_set_node_property(self.bifrost_shape, node_name, "type", prim_type)
            
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
        define_usd_transform_node = bifrost.bf_create_node(self.bifrost_shape, "BifrostGraph,USD::Attribute,define_usd_transform")
        cmds.vnnCompound(self.bifrost_shape, "/" + define_usd_transform_node, setIsReferenced=False)
        
        bifrost.bf_add_output_port(self.bifrost_shape, define_usd_transform_node + '/input', "frame", "float")
        bifrost.bf_add_output_port(self.bifrost_shape, define_usd_transform_node + '/input', "use_frame", "bool")
        
        bifrost.bf_connect(self.bifrost_shape, define_usd_transform_node + '.frame', define_usd_transform_node + '/define_usd_attribute2' + '.frame')
        bifrost.bf_connect(self.bifrost_shape, define_usd_transform_node + '.use_frame', define_usd_transform_node + '/define_usd_attribute2' + '.use_frame')
        
        bifrost.bf_connect(self.bifrost_shape, define_usd_transform_node + '.frame', define_usd_transform_node + '/define_usd_attribute1' + '.frame')
        bifrost.bf_connect(self.bifrost_shape, define_usd_transform_node + '.use_frame', define_usd_transform_node + '/define_usd_attribute1' + '.use_frame')

        bifrost.bf_connect(self.bifrost_shape, define_usd_transform_node + '.frame', define_usd_transform_node + '/define_usd_attribute3' + '.frame')
        bifrost.bf_connect(self.bifrost_shape, define_usd_transform_node + '.use_frame', define_usd_transform_node + '/define_usd_attribute3' + '.use_frame')
        
        # Rename node
        node_name = mesh_name + "_define_usd_attribute"
        bifrost.bf_rename_node(self.bifrost_shape, define_usd_transform_node, node_name)
        
        return node_name


    def add_undeformed_mesh(self, mesh_name):
        """
        Add Mesh shape to bifrost and relative mesh prim definition
        Args:
            mesh_name (string): Maya mesh name

        Returns:

        """
        # Create input port
        bifrost.bf_add_output_port(self.bifrost_shape, 'input', mesh_name + '_translate', "Math::float3")
        bifrost.bf_add_output_port(self.bifrost_shape, 'input', mesh_name + '_rotate', "Math::float3")
        bifrost.bf_add_output_port(self.bifrost_shape, 'input', mesh_name + '_scale', "Math::float3")

        # Create nodes
        define_attribute_node = self.add_undeformed_mesh_transform(mesh_name)
        define_mesh_node = bifrost.bf_create_node(self.bifrost_shape, "BifrostGraph,USD::Prim,define_usd_mesh")

        bifrost.bf_set_node_property(self.bifrost_shape, define_attribute_node, "use_frame", "1")

        bifrost.bf_set_node_property(self.bifrost_shape, define_mesh_node, "path", '/' + mesh_name)

        # Connect
        bifrost.bf_connect(self.bifrost_shape, self.time_node + '.frame', define_attribute_node + '.frame')
        
        bifrost.bf_connect(self.bifrost_shape, 'input.' + mesh_name + '_translate', define_attribute_node + '.translation')
        bifrost.bf_connect(self.bifrost_shape, 'input.' + mesh_name + '_rotate', define_attribute_node + '.rotation')
        bifrost.bf_connect(self.bifrost_shape, 'input.' + mesh_name + '_scale', define_attribute_node + '.scale')

        input_port = bifrost.bf_add_input_port(self.bifrost_shape, define_mesh_node, "attribute_definitions.attribute_definition", "auto", 'attribute_definitions')
        bifrost.bf_connect(self.bifrost_shape, define_attribute_node + '.attribute_definitions', input_port)

        self.recursive_build_usd_graph(mesh_name, define_mesh_node)

    def add_mesh(self, mesh_name):
        """
        Add Mesh shape to bifrost and relative mesh prim definition
        Args:
            mesh_name (string): Maya mesh name

        Returns:

        """
        # Creaci una classe
        input_mesh_node = bifrost.bf_add_mesh(self.bifrost_shape, mesh_name)
        define_mesh_node = bifrost.bf_create_node(self.bifrost_shape, "BifrostGraph,USD::Prim,define_usd_mesh")
        
        mesh_out_port = bifrost.bf_list_all_port(self.bifrost_shape, input_mesh_node, input_port=False, output_port=True)[-1]
        
        bifrost.bf_connect(self.bifrost_shape, mesh_out_port, define_mesh_node + '.mesh')
        bifrost.bf_connect(self.bifrost_shape, self.time_node + '.frame', define_mesh_node + '.frame')
        
        bifrost.bf_set_node_property(self.bifrost_shape, define_mesh_node, "path", '/' + mesh_name)
        
        self.recursive_build_usd_graph(mesh_name, define_mesh_node)
        
    def recursive_build_usd_graph(self, obj, node):
        """
        Recursive build and connect Prims
        Args:
            obj (string): current Maya object
            node (string): current Bifrost prim node

        Returns:
            None

        """
        if obj:
            parent = cmds.listRelatives(obj, p=True)[-1]
            
            if parent == self.root_node:
                new_node = self.create_prim(parent)

                connected_node_list = cmds.vnnNode(self.bifrost_shape, '/' + new_node, listConnectedNodes=1)
                if connected_node_list == None or not (node in connected_node_list):
                    input_port = bifrost.bf_add_input_port(self.bifrost_shape, new_node, "children.prim_definition", "auto", 'children')
                    bifrost.bf_connect(self.bifrost_shape, node + '.prim_definition', input_port)

                connected_node_list = cmds.vnnNode(self.bifrost_shape, '/' + self.add_to_stage_node, listConnectedNodes=1)
                if not ('root_define_usd_prim' in connected_node_list):
                    stage_input_port = bifrost.bf_add_input_port(self.bifrost_shape, self.add_to_stage_node, "prim_definitions.prim_definition", "auto", 'prim_definitions')
                    bifrost.bf_connect(self.bifrost_shape, new_node + '.prim_definition', stage_input_port)
                
                return None

            else:
                new_node = self.create_prim(parent)
                connected_node_list = cmds.vnnNode(self.bifrost_shape, '/' + new_node, listConnectedNodes=1)

                if connected_node_list == None or not (new_node in connected_node_list):
                    if bifrost.bf_get_node_type(self.bifrost_shape, node) == "BifrostGraph,USD::Prim,define_usd_mesh":
                        input_port = bifrost.bf_add_input_port(self.bifrost_shape, new_node, "children.mesh_definition", "auto", 'children')
                        bifrost.bf_connect(self.bifrost_shape, node + '.mesh_definition', input_port)
                    else:
                        input_port = bifrost.bf_add_input_port(self.bifrost_shape, new_node, "children.prim_definition", "auto", 'children')
                        bifrost.bf_connect(self.bifrost_shape, node + '.prim_definition', input_port)

                    self.recursive_build_usd_graph(parent, new_node)

                else:
                    return None

    def add_block_attribute(self, attr_name, node_name='', prim_path='', parent=''):
        block_attribute_node = bifrost.bf_create_node(self.bifrost_shape, "BifrostGraph,USD::Attribute,block_attribute", parent)
        bifrost.bf_set_node_property(self.bifrost_shape, parent + '/' + block_attribute_node, "name", attr_name)

        if prim_path != '':
            bifrost.bf_set_node_property(self.bifrost_shape, parent + '/' + block_attribute_node, "prim_path", prim_path)
        
        #block_attribute_node = bifrost.bf_rename_node(self.bifrost_shape, parent + '/' + block_attribute_node, node_name + '_block_attribute')

        return block_attribute_node

        #vnnConnect
        #"|rig_grp|test_bifrostGraph|test_bifrostGraphShape" "/set_stage_time_code.out_stage" "/block_attribute1.stage";

        #vnnConnect
        #"|rig_grp|test_bifrostGraph|test_bifrostGraphShape" "/block_attribute1.out_stage" "/save_usd_stage.stage";

    def create_block_loop(self):
        # Create nodes
        get_prim_children_node = bifrost.bf_create_node(self.bifrost_shape, "BifrostGraph,USD::Prim,get_prim_children")
        get_prim_path_node = bifrost.bf_create_node(self.bifrost_shape, "BifrostGraph,USD::Prim,get_prim_path")
        array_size_node = bifrost.bf_create_node(self.bifrost_shape, "BifrostGraph,Core::Array,array_size")
        iterator_node = bifrost.bf_create_node(self.bifrost_shape, "BifrostGraph,Core::Iterators,iterate")

        get_from_array_node = bifrost.bf_create_node(self.bifrost_shape, "BifrostGraph,Core::Array,get_from_array", parent='/' + iterator_node)
        face_vertex_counts_block_node = self.add_block_attribute('faceVertexCounts', 'faceVertexCounts', parent='/' + iterator_node)
        face_vertex_indices_block_node = self.add_block_attribute('faceVertexIndices', 'faceVertexIndices', parent='/' + iterator_node)
        primvars_st_block_node = self.add_block_attribute('primvars:st', 'primvars_st', parent='/' + iterator_node)
        primvars_st_indices_block_node = self.add_block_attribute('primvars:st:indices', 'primvars_st_indices', parent='/' + iterator_node)

        # Add ports
        bifrost.bf_add_output_port(self.bifrost_shape, iterator_node + '/input', 'out_stage', 'auto')
        bifrost.bf_add_output_port(self.bifrost_shape, iterator_node + '/input', 'path', 'auto')
        bifrost.bf_add_input_port(self.bifrost_shape, iterator_node + '/output', "out_stage1", "auto")

        # Connects nodes
        bifrost.bf_connect(self.bifrost_shape, self.add_to_stage_node + '.out_stage', get_prim_children_node + '.stage')
        bifrost.bf_connect(self.bifrost_shape, get_prim_children_node + '.children', get_prim_path_node + '.prim')
        bifrost.bf_connect(self.bifrost_shape, get_prim_path_node + '.path', array_size_node + '.array')
        bifrost.bf_connect(self.bifrost_shape, array_size_node + '.size', iterator_node + '.max_iterations')

        bifrost.bf_connect(self.bifrost_shape, self.add_to_stage_node + '.out_stage', iterator_node + '.out_stage')
        bifrost.bf_connect(self.bifrost_shape, get_prim_path_node + '.path', iterator_node + '.path')

        ## Connections inside loop
        bifrost.bf_connect(self.bifrost_shape, iterator_node + '.path', iterator_node + '/' + get_from_array_node + '.array')
        bifrost.bf_connect(self.bifrost_shape, iterator_node + '.current_index', iterator_node + '/' + get_from_array_node + '.index')

        bifrost.bf_connect(self.bifrost_shape, iterator_node + '.out_stage', iterator_node + '/' + face_vertex_counts_block_node + '.stage')
        bifrost.bf_connect(self.bifrost_shape, iterator_node + '/' + face_vertex_counts_block_node + '.out_stage', iterator_node + '/' + face_vertex_indices_block_node + '.stage')
        bifrost.bf_connect(self.bifrost_shape, iterator_node + '/' + face_vertex_indices_block_node + '.out_stage', iterator_node + '/' + primvars_st_block_node + '.stage')
        bifrost.bf_connect(self.bifrost_shape, iterator_node + '/' + primvars_st_block_node + '.out_stage', iterator_node + '/' + primvars_st_indices_block_node + '.stage')
        bifrost.bf_connect(self.bifrost_shape, iterator_node + '/' + primvars_st_indices_block_node + '.out_stage', iterator_node + '.out_stage1')

        bifrost.bf_connect(self.bifrost_shape, iterator_node + '/' + get_from_array_node + '.value', iterator_node + '/' + face_vertex_counts_block_node + '.prim_path')
        bifrost.bf_connect(self.bifrost_shape, iterator_node + '/' + get_from_array_node + '.value', iterator_node + '/' + face_vertex_indices_block_node + '.prim_path')
        bifrost.bf_connect(self.bifrost_shape, iterator_node + '/' + get_from_array_node + '.value', iterator_node + '/' + primvars_st_block_node + '.prim_path')
        bifrost.bf_connect(self.bifrost_shape, iterator_node + '/' + get_from_array_node + '.value', iterator_node + '/' + primvars_st_indices_block_node + '.prim_path')

        # Connect output
        bifrost.bf_connect(self.bifrost_shape, iterator_node + '.out_stage1', self.set_stage_time_code_node + '.stage')

        # Settings
        bifrost.bf_sequence_port(self.bifrost_shape, '/' + iterator_node, "out_stage", "out_stage1")
        bifrost.bf_set_node_property(self.bifrost_shape, get_prim_children_node, "prim_path", "/root")
        bifrost.bf_set_node_property(self.bifrost_shape, get_prim_children_node, "descendant_mode", "3")

        return iterator_node

if __name__ == "__main__":
    to_delete = cmds.ls('*_bifrostGraph', '*_bifrostGraph?' 'mayaUsdProxy*')
    cmds.delete(to_delete)
    deformed_list, undeformed_list = get_all_deformed_and_constrained('geo')
    print('Deformed list: ', deformed_list)
    print('Undeformed list: ', undeformed_list)
    usd_character_manager = USDCharacterBuild(deformed_list, undeformed_list, name='test', root_node='geo', debug=True)
    bifrost_transform = usd_character_manager.get_bifrost_transform()
    cmds.parent(bifrost_transform, 'rig_grp')

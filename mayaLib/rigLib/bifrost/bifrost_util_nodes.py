from mayaLib.rigLib.bifrost import bifrost

# Convert Degree to Radiants
pass

# Euler to Quaternions and convert to Matrix
pass

# Multiply Inverse Matrix
pass

# Get/Set point position
pass

def file_type_manager(bifrost_shape, create_stage_node):
    # Create Nodes
    binary_value_node = bifrost.bf_create_node(bifrost_shape, "BifrostGraph,Core::Constants,string")
    ascii_value_node = bifrost.bf_create_node(bifrost_shape, "BifrostGraph,Core::Constants,string")
    equal_node = bifrost.bf_create_node(bifrost_shape, "BifrostGraph,Core::Logic,equal")
    if_node = bifrost.bf_create_node(bifrost_shape, "BifrostGraph,Core::Logic,if")

    # Connect
    bifrost.bf_connect(bifrost_shape, 'input.file_extension', equal_node + '.first')
    bifrost.bf_connect(bifrost_shape, equal_node + '.output', if_node + '.condition')

    bifrost.bf_connect(bifrost_shape, binary_value_node + '.output', if_node + '.true_case')
    bifrost.bf_connect(bifrost_shape, ascii_value_node + '.output', if_node + '.false_case')

    bifrost.bf_connect(bifrost_shape, if_node + '.output', create_stage_node + '.file_format')

    # Set Prperty
    bifrost.bf_set_node_property(bifrost_shape, equal_node, "second", "usdc")
    bifrost.bf_set_node_property(bifrost_shape, binary_value_node, "value", "Binary")
    bifrost.bf_set_node_property(bifrost_shape, ascii_value_node, "value", "ASCII")

    node_list = [binary_value_node, ascii_value_node, equal_node, if_node]
    type_manager_compund = bifrost.bf_create_compound(bifrost_shape, compound_node_list=node_list, compound_name='extension_Compound', parent='/')

    return type_manager_compund

def add_custom_layer_data(bifrost_shape, data, custom_layer_data_node, product=''):
    node_list = []
    source = None
    for key, value in data.items():
        if node_list:
            source = node_list[-1]
        nodes = set_stage_property(bifrost_shape, key, value, source)
        node_list.extend(nodes)

    bifrost.bf_connect(bifrost_shape, node_list[-1] + '.out_object', custom_layer_data_node + '.value')
    custom_layer_data_compund = bifrost.bf_create_compound(bifrost_shape, compound_node_list=node_list, compound_name=product+'_custom_layer_data_Compound', parent='/')

    return custom_layer_data_compund

def set_stage_property(bifrost_shape, key, value='', source=None):
    node_list = []

    # Create nodes
    set_property_node = bifrost.bf_create_node(bifrost_shape, "BifrostGraph,Core::Object,set_property")
    key_value_node = bifrost.bf_create_node(bifrost_shape, "BifrostGraph,Core::Constants,string")


    if value != '' and value != source:
        if isinstance(value, int):
            value_value_node = bifrost.bf_create_node(bifrost_shape, "BifrostGraph,Core::Constants,int")
        else:
            value_value_node = bifrost.bf_create_node(bifrost_shape, "BifrostGraph,Core::Constants,string")
        node_list.append(value_value_node)

    # Set Property
    bifrost.bf_set_node_property(bifrost_shape, key_value_node, "value", key)

    if value != '' and value != source:
        bifrost.bf_set_node_property(bifrost_shape, value_value_node, "value", value)

    # Connect
    bifrost.bf_connect(bifrost_shape, key_value_node + '.output', set_property_node + '.key')

    if value != '' and value != source:
        bifrost.bf_connect(bifrost_shape, value_value_node + '.output', set_property_node + '.value')
    else:
        bifrost.bf_connect(bifrost_shape, source + '.out_object', set_property_node + '.value')

    if source:
        bifrost.bf_connect(bifrost_shape, source + '.out_object', set_property_node + '.object')

    node_list.extend([key_value_node, set_property_node])
    return node_list



# Build Name with frame number
def build_name(bifrost_shape, time_node, product='', extension_format='usdc', skip_frame=False):
    string_join_node = bifrost.bf_create_node(bifrost_shape, "BifrostGraph,Core::String,string_join")
    build_array_node = bifrost.bf_create_node(bifrost_shape, "BifrostGraph,Core::Array,build_array")
    extension_value_node = bifrost.bf_create_node(bifrost_shape, "BifrostGraph,Core::Constants,string")
    if not skip_frame:
        number_to_string_node = bifrost.bf_create_node(bifrost_shape, "BifrostGraph,Core::String,number_to_string")
        frame_value_node = bifrost.bf_create_node(bifrost_shape, "BifrostGraph,Core::Constants,string")

    # Create Ports
    bifrost.bf_add_input_port(bifrost_shape, build_array_node, product + '_file', 'string')
    bifrost.bf_add_input_port(bifrost_shape, build_array_node, 'output', 'string')
    bifrost.bf_add_input_port(bifrost_shape, build_array_node, 'output1', 'string')

    # Set property
    bifrost.bf_set_node_property(bifrost_shape, string_join_node, "separator", ".")
    bifrost.bf_set_node_property(bifrost_shape, extension_value_node, "value", extension_format)

    # Connections
    if not skip_frame:
        bifrost.bf_connect(bifrost_shape, time_node + '.frame', number_to_string_node + '.number')
        bifrost.bf_connect(bifrost_shape, number_to_string_node + '.string', frame_value_node + '.value')

    bifrost.bf_connect(bifrost_shape, 'input.' + product + '_file', build_array_node + '.' + product + '_file')
    if not skip_frame:
        bifrost.bf_connect(bifrost_shape, frame_value_node + '.output', build_array_node + '.output')
    bifrost.bf_connect(bifrost_shape, extension_value_node + '.output', build_array_node + '.output1')

    bifrost.bf_connect(bifrost_shape, build_array_node + '.array', string_join_node + '.strings')

    # Rename Nodes
    extension_value_node = bifrost.bf_rename_node(bifrost_shape, extension_value_node, "extension_value")

    if not skip_frame:
        frame_value_node = bifrost.bf_rename_node(bifrost_shape, frame_value_node, "frame_value")

    # vnnConnect "|rig_grp|test_bifrostGraph|test_bifrostGraphShape" "/string_join.joined" "/save_usd_stage.file";
    return string_join_node, build_array_node, extension_value_node

# Build Reference / Payload Compound
def build_referece_peyload(bifrost_shape, layer_name='Reference_layer', is_payload="0"):
    # Create compound
    name = 'Reference_Payload'
    if 'Reference' in layer_name:
        name = 'Reference'
    else:
        name = 'Payload'

    compound = bifrost.bf_create_compound(bifrost_shape, compound_node_list=[],
                                          compound_name=name + '_Compound', parent='/')

    # Create nodes
    create_stage_node = bifrost.bf_create_node(bifrost_shape, "BifrostGraph,USD::Stage,create_usd_stage", compound)
    add_to_stage_node = bifrost.bf_create_node(bifrost_shape, "BifrostGraph,USD::Stage,add_to_stage", compound)
    get_root_layer_node = bifrost.bf_create_node(bifrost_shape, "BifrostGraph,USD::Layer,get_root_layer", compound)
    add_payload_prim_node = bifrost.bf_create_node(bifrost_shape, "BifrostGraph,USD::Prim,add_payload_prim", compound)
    add_reference_prim_node = bifrost.bf_create_node(bifrost_shape, "BifrostGraph,USD::Prim,add_reference_prim",
                                                     compound)
    if_node = bifrost.bf_create_node(bifrost_shape, "BifrostGraph,Core::Logic,if", compound)
    define_usd_prim_node = bifrost.bf_create_node(bifrost_shape, "BifrostGraph,USD::Prim,define_usd_prim", compound)
    send_stage_to_cache_node = bifrost.bf_create_node(bifrost_shape, "BifrostGraph,USD::Stage,send_stage_to_cache", compound)

    # Set Property
    bifrost.bf_set_node_property(bifrost_shape, compound + "/" + create_stage_node, "layer", layer_name)
    bifrost.bf_set_node_property(bifrost_shape, compound + "/" + define_usd_prim_node, "path", "/root")
    bifrost.bf_set_node_property(bifrost_shape, compound + "/" + add_payload_prim_node, "prim_path", "/root")
    bifrost.bf_set_node_property(bifrost_shape, compound + "/" + add_payload_prim_node, "payload_prim_path", "/root")

    bifrost.bf_set_node_property(bifrost_shape, compound + "/" + add_reference_prim_node, "prim_path", "/root")
    bifrost.bf_set_node_property(bifrost_shape, compound + "/" + add_reference_prim_node, "reference_prim_path",
                                 "/root")
    bifrost.bf_set_node_property(bifrost_shape, compound + "/" + if_node, "condition", is_payload)

    # Create Ports
    compound = compound.replace('/', '')
    prim_definition_input_port = bifrost.bf_add_input_port(bifrost_shape, compound + "/" + add_to_stage_node,
                                                           "prim_definitions.prim_definition", "auto",
                                                           'prim_definitions')

    compound_stage_input = bifrost.bf_add_output_port(bifrost_shape, compound + '/input', "stage", "BifrostUsd::Stage")
    compound_variant_set_name_input = bifrost.bf_add_output_port(bifrost_shape, compound + '/input', "variant_set_name",
                                                                 "string")
    compound_variant_name_input = bifrost.bf_add_output_port(bifrost_shape, compound + '/input', "variant_name",
                                                             "string")
    compound_payload_input = bifrost.bf_add_output_port(bifrost_shape, compound + '/input', "Payload", "bool")

    compound_stage_output = bifrost.bf_add_input_port(bifrost_shape, compound + '/output', "out_stage",
                                                      "BifrostUsd::Stage")
    bifrost.bf_set_node_property(bifrost_shape, compound, "Payload", is_payload)
    id_output = bifrost.bf_add_input_port(bifrost_shape, compound + '/output', "id", "auto")

    # Connections
    bifrost.bf_connect(bifrost_shape, compound + "/" + create_stage_node + '.stage',
                       compound + "/" + add_to_stage_node + '.stage')
    bifrost.bf_connect(bifrost_shape, compound + "/" + define_usd_prim_node + '.prim_definition',
                       prim_definition_input_port)
    bifrost.bf_connect(bifrost_shape, compound + "/" + add_to_stage_node + '.out_stage',
                       compound + "/" + add_payload_prim_node + '.stage')
    bifrost.bf_connect(bifrost_shape, compound + "/" + add_to_stage_node + '.out_stage',
                       compound + "/" + add_reference_prim_node + '.stage')
    bifrost.bf_connect(bifrost_shape, compound + "/" + get_root_layer_node + '.layer',
                       compound + "/" + add_payload_prim_node + '.payload_layer')
    bifrost.bf_connect(bifrost_shape, compound + "/" + get_root_layer_node + '.layer',
                       compound + "/" + add_reference_prim_node + '.reference_layer')

    bifrost.bf_connect(bifrost_shape, compound + "/" + compound_stage_input,
                       compound + "/" + get_root_layer_node + '.stage')
    bifrost.bf_connect(bifrost_shape, compound + "/" + compound_variant_set_name_input,
                       compound + "/" + define_usd_prim_node + '.variant_set_name')
    bifrost.bf_connect(bifrost_shape, compound + "/" + compound_variant_name_input,
                       compound + "/" + define_usd_prim_node + '.variant_name')
    bifrost.bf_connect(bifrost_shape, compound + "/" + compound_payload_input, compound + "/" + if_node + '.condition')

    bifrost.bf_connect(bifrost_shape, compound + "/" + add_payload_prim_node + '.out_stage',
                       compound + "/" + if_node + '.true_case')
    bifrost.bf_connect(bifrost_shape, compound + "/" + add_reference_prim_node + '.out_stage',
                       compound + "/" + if_node + '.false_case')

    bifrost.bf_connect(bifrost_shape, compound + "/" + if_node + '.output', compound + "/" + compound_stage_output)

    bifrost.bf_connect(bifrost_shape, compound + "/" + if_node + '.output', compound + "/" + send_stage_to_cache_node + '.stage')
    bifrost.bf_connect(bifrost_shape, compound + "/" + send_stage_to_cache_node + '.id', compound + "/" + id_output)

    return '/' + compound


def build_preview_compound(bifrost_shape, working_layer_name='WORKING_MODELING'):
    # Create compound
    compound = bifrost.bf_create_compound(bifrost_shape, compound_node_list=[], compound_name='Preview_Compound',
                                          parent='/')

    # Create nodes
    create_stage_node = bifrost.bf_create_node(bifrost_shape, "BifrostGraph,USD::Stage,create_usd_stage", compound)
    open_layer_node = bifrost.bf_create_node(bifrost_shape, "BifrostGraph,USD::Layer,open_layer", compound)
    #get_root_layer_node = bifrost.bf_create_node(bifrost_shape, "BifrostGraph,USD::Layer,get_root_layer", compound)
    create_layer_node = bifrost.bf_create_node(bifrost_shape, "BifrostGraph,USD::Layer,create_usd_layer", compound)
    send_stage_to_cache_node = bifrost.bf_create_node(bifrost_shape, "BifrostGraph,USD::Stage,send_stage_to_cache", compound)

    # Set Property
    bifrost.bf_set_node_property(bifrost_shape, compound + "/" + create_layer_node, "layer", working_layer_name) # "Preview_layer"
    bifrost.bf_set_node_property(bifrost_shape, compound + "/" + create_stage_node, "layer", "Preview_Stage")

    # Create Ports
    compound = compound.replace('/', '')
    compound_layers_input = bifrost.bf_add_output_port(bifrost_shape, compound + '/input', "sublayers", "array<BifrostUsd::Layer>")
    compound_file_input = bifrost.bf_add_output_port(bifrost_shape, compound + '/input', "file", "string")



    stage_layer_input = bifrost.bf_add_input_port(bifrost_shape, compound + '/' + create_layer_node, "sublayers.sublayers", "array<BifrostUsd::Layer>")
    file_layer_input = bifrost.bf_add_input_port(bifrost_shape, compound + '/' + create_stage_node, "sublayers.layer", "auto")

    try:
        create_stage_layer_input = bifrost.bf_add_input_port(bifrost_shape, compound + '/' + create_stage_node,
                                                             "sublayers.new_layer", "auto")
    except:
        pass

    compound_stage_output = bifrost.bf_add_input_port(bifrost_shape, compound + '/output', "out_stage",
                                                      "BifrostUsd::Stage")
    id_output = bifrost.bf_add_input_port(bifrost_shape, compound + '/output', "id", "auto")

    # Connections
    bifrost.bf_connect(bifrost_shape, compound + ".sublayers", compound + "/" + create_layer_node + '.sublayers.sublayers')
    bifrost.bf_connect(bifrost_shape, compound + "/" + compound_file_input, compound + "/" + open_layer_node + '.file')

    bifrost.bf_connect(bifrost_shape, compound + "/" + open_layer_node + '.layer', compound + "/" + create_stage_node + ".sublayers.layer")

    bifrost.bf_connect(bifrost_shape, compound + "/" + create_layer_node + '.new_layer', compound + "/" + create_stage_node + ".sublayers.new_layer")

    bifrost.bf_connect(bifrost_shape, compound + "/" + create_stage_node + '.stage', compound + "/" + compound_stage_output)

    bifrost.bf_connect(bifrost_shape, compound + "/" + create_stage_node + '.stage', compound + "/" + send_stage_to_cache_node + '.stage')
    bifrost.bf_connect(bifrost_shape, compound + "/" + send_stage_to_cache_node + '.id', compound + "/" + id_output)

    "sublayers.sublayers" "array<BifrostUsd::Layer>"

    return '/' + compound






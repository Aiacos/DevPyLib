import importlib as imp

from mayaLib.bifrostLib import bifrost_api as bifrost

imp.reload(bifrost)

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
    """
    Creates a compound which sets the file format of the USD stage depending on the file extension.

    Args:
        bifrost_shape (str): The shape of the Bifrost graph.
        create_stage_node (str): The node which creates the USD stage.

    Returns:
        tuple: A tuple containing the compound node created during the process.
    """
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
    """
    Adds a set of custom data to a Bifrost graph node.

    Args:
        bifrost_shape (str): The shape of the Bifrost graph.
        data (dict): A dictionary of key-value pairs to add as custom data.
        custom_layer_data_node (str): The node to which the custom data should be added.
        product (str, optional): The product name to use when creating the compound.

    Returns:
        str: The name of the compound created to hold the custom data.
    """
    node_list = []
    source = None
    for key, value in data.items():
        if node_list:
            source = node_list[-1]
        nodes = set_stage_property(bifrost_shape, key, value, source)
        node_list.extend(nodes)

    bifrost.bf_connect(bifrost_shape, node_list[-1] + '.out_object', custom_layer_data_node + '.value')
    custom_layer_data_compound = bifrost.bf_create_compound(bifrost_shape, compound_node_list=node_list, compound_name=product+'_custom_layer_data_Compound', parent='/')
    custom_layer_data_compound = custom_layer_data_compound.strip("/")

    return custom_layer_data_compound

def set_stage_property(bifrost_shape, key, value='', source=None):
    """
    Sets a property on a Bifrost graph node by creating and connecting
    nodes as needed.

    Args:
        bifrost_shape (str): The shape of the Bifrost graph.
        key (str): The key of the property to set.
        value (str, optional): The value of the property. Defaults to an empty string.
        source (str, optional): The source node to connect if no value is provided. Defaults to None.

    Returns:
        list: A list of nodes created during the process.
    """
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
    """
    Build a compound which creates a string from a base name and a frame number.

    Args:
        bifrost_shape (str): The shape of the bifrost graph.
        time_node (str): The node which outputs the frame number.
        product (str): The base name of the file.
        extension_format (str): The file extension.
        skip_frame (bool): Whether to include the frame number in the file name.

    Returns:
        tuple: A tuple containing the string join node, build array node, extension value node,
            number to string node and frame value node.
    """
    number_to_string_node = None
    frame_value_node = None

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
    return string_join_node, build_array_node, extension_value_node, number_to_string_node, frame_value_node

# Build Reference / Payload Compound
def build_referece_peyload(bifrost_shape, layer_name='Reference_layer', is_payload="0", use_variant=False, use_reference=True):
    """
    Create a reference or payload compound node based on the input parameters.

    Args:
        bifrost_shape (str): The Bifrost shape name.
        layer_name (str): The name of the USD layer. Defaults to 'Reference_layer'.
        is_payload (str): A boolean string indicating whether to build a payload or reference compound. Defaults to '0'.
        use_variant (bool): A boolean indicating whether to use a variant set. Defaults to False.
        use_reference (bool): A boolean indicating whether to use a reference compound. Defaults to True.

    Returns:
        str: The path to the created compound node.
    """
    if use_reference:
        if is_payload == "0":
            compound = bifrost.bf_create_node(bifrost_shape, "BifrostGraph,EDI::Compounds,Reference_Compound")
        else:
            compound = bifrost.bf_create_node(bifrost_shape, "BifrostGraph,EDI::Compounds,Payload_Compound")
        bifrost.bf_set_node_property(bifrost_shape, compound, "layer_name", layer_name)
    else:
        # Create compound
        name = 'Reference_Payload'
        if is_payload == "0":
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

        if use_variant:
            variant_selector_node = bifrost.bf_create_node(bifrost_shape, "BifrostGraph,USD::VariantSet,define_usd_variant_set", compound)

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

        if use_variant:
            bifrost.bf_set_node_property(bifrost_shape, compound + "/" + variant_selector_node, 'variant_set_name', 'modeling')
            bifrost.bf_set_node_property(bifrost_shape, compound + "/" + variant_selector_node, 'selection', 'default')

            variant_set_port = bifrost.bf_add_input_port(bifrost_shape, compound + "/" + define_usd_prim_node, 'variant_set_definitions.variant_set_definition', 'auto')
            bifrost.bf_connect(bifrost_shape, compound + "/" + variant_selector_node + '.variant_set_definition', compound + "/" + define_usd_prim_node + '.variant_set_definitions.variant_set_definition')

    return '/' + compound


    # Create compound
def build_preview_compound(bifrost_shape, working_layer_name='WORKING_MODELING', placeholder='PLACEHOLDER'):
    """
    Builds a compound which creates a new USD stage and adds a new layer
    to it. The layer is named after the incoming step and is set as the
    root of the stage. The stage is then sent to the cache.

    The compound takes three inputs:
    - sublayers: an array of USD layers
    - file: a string representing the file path of the incoming USD file
    - step: a string representing the current step
    - custom_data: a dictionary of custom data to be added to the stage

    The compound output is a USD stage.
    """

    compound = bifrost.bf_create_compound(bifrost_shape, compound_node_list=[], compound_name='Preview_Compound',
                                          parent='/')

    # Create nodes
    create_stage_node = bifrost.bf_create_node(bifrost_shape, "BifrostGraph,USD::Stage,create_usd_stage", compound)
    #open_layer_node = bifrost.bf_create_node(bifrost_shape, "BifrostGraph,USD::Layer,open_layer", compound)
    #get_root_layer_node = bifrost.bf_create_node(bifrost_shape, "BifrostGraph,USD::Layer,get_root_layer", compound)
    create_layer_node = bifrost.bf_create_node(bifrost_shape, "BifrostGraph,USD::Stage,create_usd_stage", compound)
    send_stage_to_cache_node = bifrost.bf_create_node(bifrost_shape, "BifrostGraph,USD::Stage,send_stage_to_cache", compound)

    working_value_node = bifrost.bf_create_node(bifrost_shape, "BifrostGraph,Core::Constants,string", compound)
    step_buffer_value_node = bifrost.bf_create_node(bifrost_shape, "BifrostGraph,Core::Constants,string", compound)
    build_string_node = bifrost.bf_create_node(bifrost_shape, "BifrostGraph,Core::String,build_string", compound)
    custom_layer_data_node = bifrost.bf_create_node(bifrost_shape, "BifrostGraph,USD::Stage,set_stage_custom_layer_data", compound)
    get_root_layer_node = bifrost.bf_create_node(bifrost_shape, "BifrostGraph,USD::Layer,get_root_layer", compound)

    split_string_node = bifrost.bf_create_node(bifrost_shape, "BifrostGraph,Core::String,split_string", compound)
    array_size_node = bifrost.bf_create_node(bifrost_shape, "BifrostGraph,Core::Array,array_size", compound)
    for_each_node = bifrost.bf_create_node(bifrost_shape, "BifrostGraph,Core::Iterators,for_each", compound)

    get_from_array_node = bifrost.bf_create_node(bifrost_shape, "BifrostGraph,Core::Array,get_from_array", compound + "/" + for_each_node)
    open_layer_node = bifrost.bf_create_node(bifrost_shape, "BifrostGraph,USD::Layer,open_layer", compound + "/" + for_each_node)

    equal_layer_node = bifrost.bf_create_node(bifrost_shape, "BifrostGraph,Core::Logic,equal", compound + "/" + for_each_node)
    if_layer_node = bifrost.bf_create_node(bifrost_shape, "BifrostGraph,Core::Logic,if", compound + "/" + for_each_node)

    ## Custom layer Data
    layer_type_property_node = bifrost.bf_create_node(bifrost_shape, "BifrostGraph,Core::Object,set_property", compound)
    layer_type_value_node = bifrost.bf_create_node(bifrost_shape, "BifrostGraph,Core::Constants,string", compound)

    step_property_node = bifrost.bf_create_node(bifrost_shape, "BifrostGraph,Core::Object,set_property", compound)
    step_value_node = bifrost.bf_create_node(bifrost_shape, "BifrostGraph,Core::String,string_upper", compound)

    usd_products_node = bifrost.bf_create_node(bifrost_shape, "BifrostGraph,Core::Object,set_property", compound)


    #layer_type_node_list = set_stage_property(bifrost_shape, 'layer_type', 'Step')
    #step_node_list = set_stage_property(bifrost_shape, 'step', 'Modelling', layer_type_node_list[-1])
    #usd_products_node_list = set_stage_property(bifrost_shape, 'usd_products', 'Modelling', step_node_list[-1])

    # Set Property
    bifrost.bf_set_node_property(bifrost_shape, compound + "/" + for_each_node + "/" + open_layer_node, "read_only", '1')
    bifrost.bf_set_node_property(bifrost_shape, compound + "/" + layer_type_property_node, "key", 'layer_type')
    bifrost.bf_set_node_property(bifrost_shape, compound + "/" + layer_type_value_node, "value", 'Step')

    bifrost.bf_set_node_property(bifrost_shape, compound + "/" + step_property_node, "key", 'step')
    #bifrost.bf_set_node_property(bifrost_shape, compound + "/" + step_value_node, "value", 'Modeling')

    bifrost.bf_set_node_property(bifrost_shape, compound + "/" + usd_products_node, "key", 'usd_products')



    bifrost.bf_set_node_property(bifrost_shape, compound + "/" + create_layer_node, "layer", working_layer_name) # "Preview_layer"
    bifrost.bf_set_node_property(bifrost_shape, compound + "/" + create_stage_node, "layer", "Preview_Stage")

    bifrost.bf_set_node_property(bifrost_shape, compound + "/" + working_value_node, "value", "WORKING_")

    bifrost.bf_set_node_property(bifrost_shape, compound + "/" + split_string_node, "separator", ";")

    # Create Ports
    compound = compound.replace('/', '')
    compound_layers_input = bifrost.bf_add_output_port(bifrost_shape, compound + '/input', "sublayers", "array<BifrostUsd::Layer>")
    compound_file_input = bifrost.bf_add_output_port(bifrost_shape, compound + '/input', "file", "string")
    step_input = bifrost.bf_add_output_port(bifrost_shape, compound + '/input', "step", "string")
    custom_data_input = bifrost.bf_add_output_port(bifrost_shape, compound + '/input', "custom_data", "auto")

    try:
        working_buildstring_input = bifrost.bf_add_input_port(bifrost_shape, compound + '/' + build_string_node, "strings.output", "string")
    except:
        pass

    try:
        step_buffer_input = bifrost.bf_add_input_port(bifrost_shape, compound + '/' + build_string_node, "strings.output1", "string")
    except:
        pass

    stage_layer_input = bifrost.bf_add_input_port(bifrost_shape, compound + '/' + create_layer_node, "sublayers.sublayers", "array<BifrostUsd::Layer>")
    file_layer_input = bifrost.bf_add_input_port(bifrost_shape, compound + '/' + create_stage_node, "sublayers.layer", "auto")

    try:
        sublayers_array_input = bifrost.bf_add_input_port(bifrost_shape, compound + "/" + create_stage_node, "sublayers.external_layers", "auto")
    except:
        pass

    compound_stage_output = bifrost.bf_add_input_port(bifrost_shape, compound + '/output', "out_stage", "BifrostUsd::Stage")
    id_output = bifrost.bf_add_input_port(bifrost_shape, compound + '/output', "id", "auto")

    foreach_split_input = bifrost.bf_add_output_port(bifrost_shape, compound + '/' + for_each_node + '/input', "split", "auto")
    foreach_layer_output = bifrost.bf_add_input_port(bifrost_shape, compound + '/' + for_each_node + '/output', "layer", "auto")

    try:
        working_layer_input = bifrost.bf_add_output_port(bifrost_shape, compound + '/' + for_each_node + '/input', "working_layer", "auto")
    except:
        pass

    # Connections
    bifrost.bf_connect(bifrost_shape, compound + ".sublayers", compound + "/" + create_layer_node + '.sublayers.sublayers')
    bifrost.bf_connect(bifrost_shape, compound + "/" + get_root_layer_node + ".layer", compound + "/" + for_each_node + '.working_layer')
    bifrost.bf_connect(bifrost_shape, compound + "/" + custom_layer_data_node + ".out_stage", compound + "/" + get_root_layer_node + '.stage')
    bifrost.bf_connect(bifrost_shape, compound + "/" + create_layer_node + '.stage', compound + "/" + custom_layer_data_node + '.stage')

    bifrost.bf_connect(bifrost_shape, compound + ".step", compound + "/" + step_buffer_value_node + '.value')
    bifrost.bf_connect(bifrost_shape, compound + "/" + step_buffer_value_node + '.output', compound + "/" + build_string_node + '.strings.output1')
    bifrost.bf_connect(bifrost_shape, compound + "/" + working_value_node + '.output', compound + "/" + build_string_node + '.strings.output')
    bifrost.bf_connect(bifrost_shape, compound + "/" + build_string_node + '.joined', compound + "/" + create_layer_node + '.layer')

    ## Custom Data
    bifrost.bf_connect(bifrost_shape, compound + ".custom_data", compound + "/" + usd_products_node + '.value')
    bifrost.bf_connect(bifrost_shape, compound + "/" + layer_type_property_node + '.out_object', compound + "/" + step_property_node + '.object')
    bifrost.bf_connect(bifrost_shape, compound + "/" + step_property_node + '.out_object', compound + "/" + usd_products_node + '.object')
    bifrost.bf_connect(bifrost_shape, compound + "/" + usd_products_node + '.out_object', compound + "/" + custom_layer_data_node + '.value')
    bifrost.bf_connect(bifrost_shape, compound + "/" + layer_type_value_node + '.output', compound + "/" + layer_type_property_node + '.value')
    bifrost.bf_connect(bifrost_shape, compound + '.step', compound + "/" + step_value_node + '.string')
    bifrost.bf_connect(bifrost_shape, compound + '.step', compound + "/" + step_property_node + '.value')
    bifrost.bf_connect(bifrost_shape, compound + "/" + step_value_node + '.upper_case', compound + "/" + step_buffer_value_node + '.value')

    #bifrost.bf_connect(bifrost_shape, compound + "/" + open_layer_node + '.layer', compound + "/" + create_stage_node + ".sublayers.layer")

    #bifrost.bf_connect(bifrost_shape, compound + "/" + create_layer_node + '.new_layer', compound + "/" + create_stage_node + ".sublayers.new_layer")

    bifrost.bf_connect(bifrost_shape, compound + "/" + create_stage_node + '.stage', compound + "/" + compound_stage_output)

    bifrost.bf_connect(bifrost_shape, compound + "/" + create_stage_node + '.stage', compound + "/" + send_stage_to_cache_node + '.stage')
    bifrost.bf_connect(bifrost_shape, compound + "/" + send_stage_to_cache_node + '.id', compound + "/" + id_output)

    # Open Layers

    bifrost.bf_connect(bifrost_shape, compound + "/" + compound_file_input, compound + "/" + split_string_node + '.string')
    bifrost.bf_connect(bifrost_shape, compound + "/" + split_string_node + '.split', compound + "/" + array_size_node + '.array')
    bifrost.bf_connect(bifrost_shape, compound + "/" + array_size_node + '.size', compound + "/" + for_each_node + '.max_iterations')
    bifrost.bf_connect(bifrost_shape, compound + "/" + split_string_node + '.split', compound + "/" + for_each_node + '.split')

    bifrost.bf_connect(bifrost_shape, compound + "/" + for_each_node + '.split', compound + "/" + for_each_node + "/" + get_from_array_node + '.array')
    bifrost.bf_connect(bifrost_shape, compound + "/" + for_each_node + '.current_index', compound + "/" + for_each_node + "/" + get_from_array_node + '.index')
    bifrost.bf_connect(bifrost_shape, compound + "/" + for_each_node + "/" + get_from_array_node + '.value', compound + "/" + for_each_node + "/" + open_layer_node + '.file')
    bifrost.bf_connect(bifrost_shape, compound + "/" + for_each_node + "/" + if_layer_node + '.output', compound + "/" + for_each_node + '.layer')
    bifrost.bf_connect(bifrost_shape, compound + "/" + for_each_node + "/" + get_from_array_node + '.value', compound + "/" + for_each_node + "/" + equal_layer_node + '.first')
    bifrost.bf_connect(bifrost_shape, compound + "/" + for_each_node + "/" + equal_layer_node + '.output', compound + "/" + for_each_node +  "/" + if_layer_node + '.condition')

    bifrost.bf_connect(bifrost_shape, compound + "/" + for_each_node + '.working_layer', compound + "/" + for_each_node + "/" + if_layer_node + '.true_case')
    bifrost.bf_connect(bifrost_shape, compound + "/" + for_each_node + "/" + open_layer_node + '.layer', compound + "/" + for_each_node + "/" + if_layer_node + '.false_case')

    bifrost.bf_connect(bifrost_shape, compound + "/" + for_each_node + '.layer', compound + "/" + create_stage_node + '.sublayers.external_layers')

    bifrost.bf_set_node_property(bifrost_shape, compound + "/" + for_each_node + "/" + equal_layer_node, "second", placeholder)

    return '/' + compound


def get_data_from_layer(bifrost_shape, layer_node, product_name):
    # Create Nodes
    get_layer_id_node = bifrost.bf_create_node(bifrost_shape, "BifrostGraph,USD::Layer,get_layer_identifier")
    layer_file_path_node = bifrost.bf_create_node(bifrost_shape, "BifrostGraph,USD::Layer,get_layer_file_path")
    split_file_path_node = bifrost.bf_create_node(bifrost_shape, "BifrostGraph,Core::String,split_string")
    get_from_array_node = bifrost.bf_create_node(bifrost_shape, "BifrostGraph,Core::Array,get_from_array")

    product_dict_property = bifrost.bf_create_node(bifrost_shape, "BifrostGraph,Core::Object,set_property")
    name_property = bifrost.bf_create_node(bifrost_shape, "BifrostGraph,Core::Object,set_property")
    path_property = bifrost.bf_create_node(bifrost_shape, "BifrostGraph,Core::Object,set_property")

    # Set Property
    bifrost.bf_set_node_property(bifrost_shape, split_file_path_node, "separator", ".")
    bifrost.bf_set_node_property(bifrost_shape, name_property, "key", "name")
    bifrost.bf_set_node_property(bifrost_shape, path_property, "key", "path")

    # Connection
    bifrost.bf_connect(bifrost_shape, layer_node + '.layer', get_layer_id_node + '.layer')
    bifrost.bf_connect(bifrost_shape, layer_node + '.layer', layer_file_path_node + '.layer')
    bifrost.bf_connect(bifrost_shape, layer_file_path_node + '.file', split_file_path_node + '.string')
    bifrost.bf_connect(bifrost_shape, split_file_path_node + '.split', get_from_array_node + '.array')
    bifrost.bf_connect(bifrost_shape, get_from_array_node + '.value', name_property + '.value')
    bifrost.bf_connect(bifrost_shape, get_layer_id_node + '.identifier', path_property + '.value')

    bifrost.bf_connect(bifrost_shape, name_property + '.out_object', path_property + '.object')
    bifrost.bf_connect(bifrost_shape, get_from_array_node + '.value', product_dict_property + '.key')
    bifrost.bf_connect(bifrost_shape, path_property + '.out_object', product_dict_property + '.value')

    node_list = [get_layer_id_node, layer_file_path_node, split_file_path_node, get_from_array_node, product_dict_property, name_property, path_property]
    compound = bifrost.bf_create_compound(bifrost_shape, compound_node_list=node_list, compound_name=product_name + '_data_compound')

    # Complete compound
    compound_stage_output = bifrost.bf_add_input_port(bifrost_shape, compound + '/output', "out_data", "auto")
    bifrost.bf_connect(bifrost_shape, compound + "/" + product_dict_property + '.out_object', compound + '.out_data')

    compound_stage_input = bifrost.bf_add_output_port(bifrost_shape, compound + '/input', "in_data", "auto")
    bifrost.bf_connect(bifrost_shape, compound + '.in_data', compound + "/" + product_dict_property + '.object')

    return compound



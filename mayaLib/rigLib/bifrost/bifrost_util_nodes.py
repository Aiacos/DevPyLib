from mayaLib.rigLib.bifrost import bifrost

# Convert Degree to Radiants
pass

# Euler to Quaternions and convert to Matrix
pass

# Multiply Inverse Matrix
pass

# Get/Set point position
pass

# Build Name with frame number
def build_name(bifrost_shape, time_node, extension_format='usdc'):
    string_join_node = bifrost.bf_create_node(bifrost_shape, "BifrostGraph,Core::String,string_join")
    build_array_node = bifrost.bf_create_node(bifrost_shape, "BifrostGraph,Core::Array,build_array")
    frame_value_node = bifrost.bf_create_node(bifrost_shape, "BifrostGraph,Core::Constants,string")
    extension_value_node = bifrost.bf_create_node(bifrost_shape, "BifrostGraph,Core::Constants,string")
    number_to_string_node = bifrost.bf_create_node(bifrost_shape, "BifrostGraph,Core::String,number_to_string")

    # Create Ports
    bifrost.bf_add_input_port(bifrost_shape, build_array_node, 'layer', 'string')
    bifrost.bf_add_input_port(bifrost_shape, build_array_node, 'output', 'string')
    bifrost.bf_add_input_port(bifrost_shape, build_array_node, 'output1', 'string')

    # Set property
    bifrost.bf_set_node_property(bifrost_shape, string_join_node, "separator", ".")
    bifrost.bf_set_node_property(bifrost_shape, extension_value_node, "value", extension_format)

    # Connections
    bifrost.bf_connect(bifrost_shape, time_node + '.frame', number_to_string_node + '.number')
    bifrost.bf_connect(bifrost_shape, number_to_string_node + '.string', frame_value_node + '.value')

    bifrost.bf_connect(bifrost_shape, 'input.layer', build_array_node + '.layer')
    bifrost.bf_connect(bifrost_shape, frame_value_node + '.output', build_array_node + '.output')
    bifrost.bf_connect(bifrost_shape, extension_value_node + '.output', build_array_node + '.output1')

    bifrost.bf_connect(bifrost_shape, build_array_node + '.array', string_join_node + '.strings')

    # Rename Nodes
    extension_value_node = bifrost.bf_rename_node(bifrost_shape, extension_value_node, "extension_value")
    frame_value_node = bifrost.bf_rename_node(bifrost_shape, frame_value_node, "frame_value")

    # vnnConnect "|rig_grp|test_bifrostGraph|test_bifrostGraphShape" "/string_join.joined" "/save_usd_stage.file";
    return string_join_node

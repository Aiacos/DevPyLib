import maya.mel as mel
import maya.cmds as cmds
import pymel.core as pm


## USD Utility
def get_maya_usd_stage(stage_name='mayaUsdProxy1'):
    """
    Get Stage node from a Maya scene
    Args:
        stage_name (string): Name of the Stage

    Returns:
        (string): Stage shape node name

    """

    stage_node = cmds.ls(stage_name)[-1]
    stage_shape = cmds.listRelatives(stage_node, s=True)[-1]
    
    return stage_shape
    
def set_maya_usd_stage_shareable(stage_shape, default_value=True):
    """
    Set Maya Stage Sharable
    Args:
        stage_shape (string): Stage shape node name
        default_value (bool): Default value to set

    Returns:
        None

    """

    cmds.setAttr(stage_shape + '.shareStage', default_value)
    
## Bifrost low level
def create_bifrost_graph(name=''):
    """
    Create Maya Bifrost Graph
    Args:
        name (string): Name of Maya Bifrost node

    Returns:
        (string): Bifrost Maya Node

    """

    mel.eval('CreateNewBifrostGraph;')
    
    bifrost_node = cmds.ls('bifrostGraph1')[-1]
    cmds.rename(bifrost_node, name + '_bifrostGraph')
    bifrost_node = cmds.ls(name + '_bifrostGraph')[-1]

    return cmds.listRelatives(bifrost_node, s=True)[-1]

def create_bifrost_maya_shape(name='bifrost_geo'):
    """
    Create Maya Transform and Shape to connect to Bifrost output
    Args:
        name (string): Geo Name

    Returns:
        (string): Geo Shape Node

    """

    sphere = cmds.polySphere(n=name)
    sphere_shape = cmds.listRelatives(sphere, s=True)
    
    return sphere_shape

def create_bifrostGeoToMaya_node():
    """
    Create conversion node from Bifrost to Maya shape
    Returns:
        (string): Bifrost to Maya Geo Node

    """

    bifrostGeoToMaya_node = cmds.createNode('bifrostGeoToMaya')
    
    return bifrostGeoToMaya_node
    
def bf_create_node(bifrost_shape, node, parent='/'):
    """
    Create Bifrost Graph Node
    Args:
        bifrost_shape (string): Bifrost Graph Shape
        node (string): Node to create in the format "BifrostGraph,<category>::<sub_category>,<node_name>" ex:"BifrostGraph,USD::Stage,create_usd_stage"
        parent (string): Parent of the node

    Returns:
        (string): Bifrost Graph Node

    """

    bf_node = cmds.vnnCompound(bifrost_shape, parent, addNode=node)[-1]
    
    return bf_node

def bf_get_port_type(bifrost_shape, node, port_name):
    """
    Get Bifrost Graph node Type
    Args:
        bifrost_shape (string): Bifrost Graph Shape
        node (string): Node to query
        port_name: Port to query

    Returns:
        (string): port type

    """

    port_type = cmds.vnnNode(bifrost_shape, '/' + node, queryPortDataType=port_name)
    
    return port_type
    
def bf_list_all_port(bifrost_shape, node, input_port=True, output_port=True):
    """
    List all ports on a Bifrost Graph Node
    Args:
        bifrost_shape (string): Bifrost Graph Shape
        node (string): Node to query
        input_port (bool): Flag to enable listing input ports
        output_port (bool): Flag to enable listing output ports

    Returns:
        (string[]): list of port as string

    """

    port_list = cmds.vnnNode(bifrost_shape, node, listPorts=True, inputPort=input_port, outputPort=output_port)
    
    return port_list

def bf_add_input_port(bifrost_shape, node, port_name, port_type):
    """
    Add input port to Bifrost Graph Node
    Args:
        bifrost_shape (string): Bifrost Graph Shape
        node (string): Node to add port to
        port_name (string): Name of the port
        port_type (string): Type of the port in the format "BifrostUsd::Stage"

    Returns:
        None

    """

    cmds.vnnNode(bifrost_shape, '/' + node, createInputPort=(port_name, port_type))
    
def bf_add_output_port(bifrost_shape, node, port_name, port_type):
    """
    Add output port to Bifrost Graph Node
    Args:
        bifrost_shape (string): Bifrost Graph Shape
        node (string): Node to add port to
        port_name (string): Name of the port
        port_type (string): Type of the port in the format "BifrostUsd::Stage"

    Returns:
        None

    """

    cmds.vnnNode(bifrost_shape, '/' + node, createOutputPort=(port_name, port_type))
    
def bf_connect(bifrost_shape, source_port, destination_port):
    """
    Connect to nodes on the specified ports
    Args:
        bifrost_shape (string): Bifrost Graph Shape
        source_port (string): Node and Port name in the format "node.port"
        destination_port (string): Node and Port name in the format "node.port"

    Returns:
        None

    """

    cmds.vnnConnect(bifrost_shape, '/' + source_port, '/' + destination_port)
    
def bf_create_compound(bifrost_shape, compound_node_list=[] ,compound_name='compound', parent='/'):
    """
    Create Bifrost Graph Compound node from specified nodes
    Args:
        bifrost_shape (string): Bifrost Graph Shape
        compound_node_list (string[]): List of nodes to include in the Compound
        compound_name (string): Compound name
        parent (string): parent of the Compound node

    Returns:
        None

    """

    value_node_list = {'moveNodeIn': compound_node_list}
    bf_compound = cmds.vnnCompound(bifrost_shape, parent, create=compound_name, **value_node_list)
    
    return bf_compound

def bf_feedback_port(bifrost_shape, node, source_port, destination_port):
    """
    Enable Feedback beetween ports inside a Compound
    Args:
        bifrost_shape (string): Bifrost Graph Shape
        node (string): Compound Node name
        source_port (string): Name of the port
        destination_port (string): Name of the port

    Returns:
        None

    """

    cmds.vnnCompound(bifrost_shape, node,  setPortMetaDataValue=[source_port, "feedbackPort", destination_port])

def bf_set_node_property(bifrost_shape, node, property, value):
    """
    Set Property on a Bifrost node
    Args:
        bifrost_shape (string): Bifrost Graph Shape
        node (string): Node name
        property (string): Property name
        value (string[]): Values as list of string

    Returns:
        None

    """
    cmds.vnnNode(bifrost_shape, '/' + node, setPortDefaultValues=[property, value])

def bf_auto_layout():
    """
    Layout Bifrost Graph nodes
    Returns:
        None

    """

    mel.eval('undoInfo -openChunk -chunkName "Auto-Layout_Selected\tL";')



## Bifrost Deformer Connection
def connect_bifrostwgt_to_deformerwgt(bifrost_wgt_attribute, deformer_wgt_attribute):
    """
    Connect Bifrost Maya Node weight output to a deformer Attribute
    Args:
        bifrost_wgt_attribute (string): Node and Port in the format "bifrost_node.attribute"
        deformer_wgt_attribute (string): Node and Port in the format "deformer.attribute"

    Returns:
        None

    """

    cmds.connectAttr(bifrost_wgt_attribute, deformer_wgt_attribute, f=True)
    
def connect_bifrost_attribute_to_blendshape(bifrost_node, blendshape_targhet):
    """
    Connect Bifrost Maya Node weight attribute to a blendshape deformer
    Args:
        bifrost_node (string): Maya Bifrost Node
        blendshape_targhet (string): Blendshape deformer targhet

    Returns:
        None

    """

    connect_bifrostwgt_to_deformerwgt(bifrost_node.out_weights, blendshape_targhet.inputTargetGroup[0].targetWeights)


####### Tests
if __name__ == "__main__":
    mel.eval('file -f -new;')
    bifrost_shape = create_bifrost_graph('usd')
    
    # Create Stage
    create_usd_stage_node = bf_create_node(bifrost_shape, "BifrostGraph,USD::Stage,create_usd_stage")
    add_to_stage_node = bf_create_node(bifrost_shape, "BifrostGraph,USD::Stage,add_to_stage")
    bf_connect(bifrost_shape, create_usd_stage_node + '.stage', add_to_stage_node + '.stage')
    
    save_usd_stage_node = bf_create_node(bifrost_shape, "BifrostGraph,USD::Stage,save_usd_stage")
    print('bf_node: ', save_usd_stage_node, ' - ', type(save_usd_stage_node))
    bf_add_input_port(bifrost_shape, 'output', 'out_stage', 'BifrostUsd::Stage')
    bf_connect(bifrost_shape, save_usd_stage_node + '.out_stage', 'output.out_stage')
    bf_connect(bifrost_shape, add_to_stage_node + '.out_stage', save_usd_stage_node + '.stage')

    compound_node = bf_create_compound(bifrost_shape, compound_node_list=[add_to_stage_node], compound_name='test_compound')
    bf_feedback_port(bifrost_shape, compound_node, 'out_stage', 'stage')
    
    stage = get_maya_usd_stage()
    set_maya_usd_stage_shareable(stage)
    
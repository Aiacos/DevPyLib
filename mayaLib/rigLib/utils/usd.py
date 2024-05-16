import maya.cmds as cmds
import pymel.core as pm

from mayaLib.rigLib.utils import bifrost


def getAllObjectUnderGroup(group, type='mesh'):
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
        objList = [cmds.listRelatives(o, p=1)[0] for o in cmds.listRelatives(group, ad=1, type=type)]

    if type == 'nurbsSurface':
        objList = [cmds.listRelatives(o, p=1)[0] for o in cmds.listRelatives(group, ad=1, type=type)]

    if type == 'transform':
        geoList = [cmds.listRelatives(o, p=1)[0] for o in cmds.listRelatives(group, ad=1, type='mesh')]
        objList = [o for o in cmds.listRelatives(group, ad=1, type=type) if o not in geoList]

    objList = list(set(objList))
    objList.sort()

    return objList

class USDCharacterBuild(object):
    """
    Build Bifrost nodes to manage usd
    """

    def __init__(self, geo_list=[], name='', root_node=''):
        self.bifrost_shape = self.create_bifrost_graph(name)
        add_to_stage_node, time_node = self.create_default_usd_stage()
        
        add_to_stage_compound = bifrost.bf_create_compound(self.bifrost_shape, [add_to_stage_node])
        bifrost.bf_feedback_port(self.bifrost_shape, add_to_stage_compound, 'out_stage', 'stage')
        
        bifrost.bf_add_mesh(self.bifrost_shape, "platonic_body")
        

    def create_bifrost_graph(self, name='usd'):
        bifrost_shape = bifrost.create_bifrost_graph(name)

        return bifrost_shape

    def create_default_usd_stage(self, connect_output=True):
        # Add Input Port
        bifrost.bf_add_output_port(self.bifrost_shape, 'input', 'layer', 'string') # node, port_name, port_type
        bifrost.bf_add_output_port(self.bifrost_shape, 'input', 'start_frame', 'float')
        bifrost.bf_add_output_port(self.bifrost_shape, 'input', 'end_frame', 'float')
        bifrost.bf_add_output_port(self.bifrost_shape, 'input', 'layer_index', 'int')
        
        # Nodes Creation
        time_node = bifrost.bf_create_node(self.bifrost_shape, "BifrostGraph,Core::Time,time")
        create_usd_stage_node = bifrost.bf_create_node(self.bifrost_shape, "BifrostGraph,USD::Stage,create_usd_stage")
        add_to_stage_node = bifrost.bf_create_node(self.bifrost_shape, "BifrostGraph,USD::Stage,add_to_stage")
        stage_time_code_node = bifrost.bf_create_node(self.bifrost_shape, "BifrostGraph,USD::Stage,set_stage_time_code")
        save_usd_stage_node = bifrost.bf_create_node(self.bifrost_shape, "BifrostGraph,USD::Stage,save_usd_stage")
        equal_node = bifrost.bf_create_node(self.bifrost_shape, "BifrostGraph,Core::Logic,equal")
        
        # Nodes Connections
        bifrost.bf_connect(self.bifrost_shape, create_usd_stage_node + '.stage', add_to_stage_node + '.stage')
        bifrost.bf_connect(self.bifrost_shape, add_to_stage_node + '.out_stage', stage_time_code_node + '.stage')
        bifrost.bf_connect(self.bifrost_shape, stage_time_code_node + '.out_stage', save_usd_stage_node + '.stage')
        bifrost.bf_connect(self.bifrost_shape, equal_node + '.output', save_usd_stage_node + '.enable')
        bifrost.bf_connect(self.bifrost_shape, time_node + '.frame', equal_node + '.first')
        bifrost.bf_connect(self.bifrost_shape, 'input.start_frame', stage_time_code_node + '.start')
        bifrost.bf_connect(self.bifrost_shape, 'input.end_frame', stage_time_code_node + '.end')
        bifrost.bf_connect(self.bifrost_shape, 'input.layer_index', add_to_stage_node + '.layer_index')
        bifrost.bf_connect(self.bifrost_shape, 'input.end_frame', equal_node + '.second')
        
        if connect_output:
            bifrost.bf_add_input_port(self.bifrost_shape, 'output', 'out_stage', 'BifrostUsd::Stage')
            bifrost.bf_connect(self.bifrost_shape, save_usd_stage_node + '.out_stage', 'output.out_stage')
            
        bifrost.bf_connect(self.bifrost_shape, 'input.layer', create_usd_stage_node + '.layer')
        
        return add_to_stage_node, time_node


if __name__ == "__main__":
    usd_character_manager = USDCharacterBuild()
    """
    # Create Stage
    create_usd_stage_node = bf_create_node(bifrost_shape, "BifrostGraph,USD::Stage,create_usd_stage")
    add_to_stage_node = bf_create_node(bifrost_shape, "BifrostGraph,USD::Stage,add_to_stage")
    bf_connect(bifrost_shape, create_usd_stage_node + '.stage', add_to_stage_node + '.stage')

    save_usd_stage_node = bf_create_node(bifrost_shape, "BifrostGraph,USD::Stage,save_usd_stage")
    print('bf_node: ', save_usd_stage_node, ' - ', type(save_usd_stage_node))
    bf_add_input_port(bifrost_shape, 'output', 'out_stage', 'BifrostUsd::Stage')
    bf_connect(bifrost_shape, save_usd_stage_node + '.out_stage', 'output.out_stage')
    bf_connect(bifrost_shape, add_to_stage_node + '.out_stage', save_usd_stage_node + '.stage')

    compound_node = bf_create_compound(bifrost_shape, compound_node_list=[add_to_stage_node],
                                       compound_name='test_compound')
    bf_feedback_port(bifrost_shape, compound_node, 'out_stage', 'stage')

    stage = get_maya_usd_stage()
    set_maya_usd_stage_shareable(stage)
    """
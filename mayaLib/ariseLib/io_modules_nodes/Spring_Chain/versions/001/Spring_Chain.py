"""Spring_Chain creates a chain that trails behind a single 'lead' ctrl with a cascading spring.

Made for dragged ropes and dragon/snake bodies, after the Control Rig "dynamic chain": every joint is
pulled by a spring towards where it would be if the chain was rigid from the joint before it, so the
delay grows towards the tip. Bones keep their length and the twist travels down the chain the same way.

The springs live in 'springChainSolver' nodes, from the DevPyLib plugin
'mayaLib/plugin/spring_chain_solver.py', which keep their own state like mGear's spring node does:
the chain reacts while a ctrl is dragged, and it has to be played from a frame to be correct (jumping
in time resets it on its rigid pose).

'spring_network' is injected in this module namespace by Arise ('utils' folder).
"""

from pathlib import Path

import maya.cmds as mc
from arise.data_types import node_data
from arise.utils.io_nodes.io_transform import IoTransform
from arise.utils.math_utils import distance_between
from arise.utils.matrix_utils import matrix_constraint
from arise.utils.modules_utils import create_grps, update_ctrls

MAYA_VERSION = 2022  # the version of maya from which this module supports.
AUTHOR = "Lorenzo Argentieri"  # name of person who created this module.
RIG_CATEGORY = "All"  # either 'Basic', 'Cartoon', 'Vfx', 'Game' or 'All'.
RIG_TYPE = "All"  # Biped, Car, Quadruped, ..., All.
TAGS = ["chain", "spring", "lag", "trail", "dragon", "rope", "tail", "dynamic", "overlap"]
TOOL_TIP = (
    "Chain that trails behind a lead ctrl with a cascading spring, like a dragon body or a rope."
)

SPACE_ITEMS = ["World", "Root Input"]
GUIDES_OFFSET = 5.0
MAX_LAG = 100
MIN_DAMPING = 0.05
# .../mayaLib/ariseLib/io_modules_nodes/Spring_Chain/versions/001/Spring_Chain.py -> .../mayaLib/plugin
SOLVER_PLUGIN = Path(__file__).resolve().parents[5] / "plugin" / "spring_chain_solver.py"

node_data.NodeData.update_ctrls = update_ctrls


def load_solver_plugin():
    """Load the 'springChainSolver' plugin if it is not loaded yet."""
    if mc.pluginInfo(SOLVER_PLUGIN.name, query=True, loaded=True):
        return

    mc.loadPlugin(str(SOLVER_PLUGIN), quiet=True)


class Spring_Chain(node_data.NodeData):  # noqa: N801 (Arise: class, module and folder share the name)
    """Chain that trails behind a lead ctrl with a cascading spring."""

    sort_priority = 1000

    def __init__(self, parent, docs, icon, module_dict):
        """Initialize the node data (called by Arise)."""
        node_data.NodeData.__init__(
            self, parent=parent, icon=icon, docs=docs, module_dict=module_dict
        )

    def attributes_creation(self):
        """Here you add the module attributes."""
        self.add_collapsible_layout(title="Settings", shown=True)
        self.ctrls_scale_attr = self.add_float_attribute(
            name="Ctrls Scale",
            default_value=1.0,
            min_value=0.01,
            max_value=100,
            annotation="Scale all the node's ctrls.",
            button=[
                self.update_ctrls,
                "Update",
                "resources/icons/sync_icon.png",
                "If the ctrls exist in the Maya scene, their shapes will update without requiring a rebuild.",
            ],
        )
        self.joint_count_attr = self.add_integer_attribute(
            name="Joints",
            default_value=10,
            min_value=3,
            max_value=200,
            annotation="Number of joints/guides to create; modifying this attribute requires a 're-template'.",
        )
        self.is_skinning_attr = self.add_boolean_attribute(
            name="Skinning Joints",
            default_value=True,
            annotation="Tag the chain joints as skinning joints.",
        )
        self.close_layout()

        self.add_collapsible_layout(title="Spring", shown=True)
        self.lag_attr = self.add_float_attribute(
            name="Lag Per Joint",
            default_value=2.0,
            min_value=0.0,
            max_value=MAX_LAG,
            annotation=(
                "Default value of the 'lag' attr on the lead ctrl: frames of delay each joint adds on top "
                "of the joint before it.\nAnimators can change and key it on the ctrl."
            ),
        )
        self.damping_attr = self.add_float_attribute(
            name="Damping",
            default_value=1.0,
            min_value=MIN_DAMPING,
            max_value=1.0,
            annotation=(
                "Default value of the 'damping' attr on the lead ctrl.\n"
                "1.0 = the chain settles without overshooting. Lower values overshoot and bounce."
            ),
        )
        self.delayed_twist_attr = self.add_boolean_attribute(
            name="Delayed Twist",
            default_value=True,
            annotation=(
                "Checked: the twist of the lead travels down the chain with the same delay as the position.\n"
                "Unchecked: the twist follows the lead immediately (one solver node less)."
            ),
        )
        self.space_attr = self.add_radio_attribute(
            name="Space",
            items=SPACE_ITEMS,
            default_value=0,
            annotation=(
                "World: any motion of the lead in the world is delayed.\n"
                "Root Input: the motion of whatever drives 'Root Input' is not delayed, only the lead "
                "motion relative to it."
            ),
        )
        self.close_layout()

        self.add_separator(title="Connections")
        self.driven_root_attr = self.add_driven_attribute(
            name="Root Input", annotation="Space of the 'lead' ctrl."
        )
        self.driver_root_attr = self.add_driver_attribute(
            name="Root Output", annotation="First joint."
        )
        self.driver_tip_attr = self.add_driver_attribute(
            name="Tip Output", annotation="Last joint."
        )

    def guides_creation(self):
        """Create a chain of aim guides along +Y. Each guide aims at the next one."""
        self.guides_list = []
        parent = None
        for index in range(self.joint_count_attr.value):
            guide = self.add_aim_guide(
                name=str(index).zfill(4),
                translation=[0, GUIDES_OFFSET * index, 0],
                parent=parent,
                side_pin_rotation=(0, 0, 0),
                side_pin_guide=self.guides_list[0] if self.guides_list else None,
            )
            self.guides_list.append(guide)
            parent = guide

        for guide, next_guide in zip(self.guides_list[:-1], self.guides_list[1:]):  # noqa: B905
            guide.aim_at = next_guide

        self.guides_list[-1].aim_at = self.guides_list[-2]
        self.guides_list[-1].aim_rotation_offset = (180, 0, 0)

    def joints_creation(self):
        """Declare the chain joints."""
        self.joints_list = []
        parent = None
        for index in range(self.joint_count_attr.value):
            joint = self.add_joint(
                name=f"chain_{index}",
                skinning_jnt=self.is_skinning_attr.value,
                tag_parent_jnt=parent,
                radius=0.5,
            )
            self.joints_list.append(joint)
            parent = joint

    def ctrls_creation(self):
        """Declare the single 'lead' ctrl."""
        self.lead_ctrl = self.add_ctrl(
            name="lead", shape="circle", up_orient="+Y", size=3.0 * self.ctrls_scale_attr.value
        )
        for attr in ["scaleY", "scaleZ"]:
            self.lead_ctrl.add_locked_hidden_attr(attr)

    def maya_attrs_creation(self):
        """Declare the spring attrs so 'AttributesSettings' can set them (Arise 1.09+)."""
        if not hasattr(self.lead_ctrl, "add_maya_attr"):
            return

        self.lead_ctrl.add_maya_attr(
            name="spring_weight", attr_type="float", default_value=1, min=0, max=1
        )
        self.lead_ctrl.add_maya_attr(
            name="lag", attr_type="float", default_value=self.lag_attr.value, min=0, max=MAX_LAG
        )
        self.lead_ctrl.add_maya_attr(
            name="damping",
            attr_type="float",
            default_value=self.damping_attr.value,
            min=MIN_DAMPING,
            max=1,
        )

    def rig_creation(self):
        """Using the attributes values, guides, joints, and ctrls, build the rig."""
        load_solver_plugin()

        if self.is_mirrored:
            self.module_grp.set_attr("scaleX", -1)

        input_root_grp, output_root_grp, output_tip_grp, jnts_grp, ctrls_grp = create_grps(
            self, ["input_root_grp", "output_root_grp", "output_tip_grp", "jnts_grp", "ctrls_grp"]
        )
        self.driven_root_attr.set_maya_object(input_root_grp)
        self.driver_root_attr.set_maya_object(output_root_grp)
        self.driver_tip_attr.set_maya_object(output_tip_grp)

        matrices = [guide.world_transformations["matrix"] for guide in self.guides_list]
        positions = [guide.world_transformations["translate"] for guide in self.guides_list]

        # --- lead ctrl at the first guide, with the spring attrs animators can key.
        lead = self.lead_ctrl.pointer
        ctrls_grp.set_matrix(matrices[0])
        ctrls_grp.set_scale([1, 1, 1])
        lead.offset_grp.parent_relative(ctrls_grp)
        lead.scale_attrs_connect()
        weight_attr = lead.add_attr(
            "spring_weight", attributeType="float", min=0, max=1, dv=1, keyable=True
        )
        lag_attr = lead.add_attr(
            "lag", attributeType="float", min=0, max=MAX_LAG, dv=self.lag_attr.value, keyable=True
        )
        damping_attr = lead.add_attr(
            "damping",
            attributeType="float",
            min=MIN_DAMPING,
            max=1,
            dv=self.damping_attr.value,
            keyable=True,
        )

        # --- rest points: where each joint would be if the chain was rigid. Up points drive the twist.
        lengths = [
            distance_between(positions[index], positions[index + 1])
            for index in range(len(positions) - 1)
        ]
        up_offset = sum(lengths) / len(lengths)
        rest_points, up_points = [], []
        for index, matrix in enumerate(matrices):
            rest = IoTransform(f"{self.name}_rest_{index}_grp")
            rest.parent_relative(lead)
            rest.set_matrix(matrix)
            rest.set_scale([1, 1, 1])
            rest_points.append(rest)

            if self.delayed_twist_attr.value:
                up_point = IoTransform(f"{self.name}_up_{index}_grp")
                up_point.parent_relative(rest)
                up_point.set_translation([up_offset, 0, 0], space="object")
                up_points.append(up_point)

        # --- joints hierarchy. Their transformations are driven by the spring network.
        joints = [joint.pointer for joint in self.joints_list]
        joints[0].parent_relative(jnts_grp)
        for index in range(1, len(joints)):
            joints[index].parent_relative(joints[index - 1])

        spring_network.build_spring_chain(  # noqa: F821
            prefix=self.name,
            rest_points=[str(point) for point in rest_points],
            up_points=[str(point) for point in up_points] if up_points else None,
            joints=[str(joint) for joint in joints],
            lead=str(lead),
            lag_attr=lag_attr,
            damping_attr=damping_attr,
            weight_attr=weight_attr,
            space=str(input_root_grp) if self.space_attr.value == 1 else None,
        )

        # --- connections.
        input_root_grp.match_transformation_to(ctrls_grp)
        matrix_constraint(input_root_grp, ctrls_grp, maintain_offset=True)
        matrix_constraint(joints[0], output_root_grp, maintain_offset=False)
        matrix_constraint(joints[-1], output_tip_grp, maintain_offset=False)
        return True

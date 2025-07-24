import pymel.core as pm
from mayaLib.rigLib.utils.common import setDrivenKey
from mayaLib.rigLib.utils import humanIK
from mayaLib.rigLib.utils import joint
from mayaLib.rigLib.utils.util import getAllObjectUnderGroup


class BaseRig:
    """
    A base class for rigging operations in Maya.

    This class provides methods for setting up display layers, connecting controls,
    and managing rig components like HumanIK and facial rigs.
    """

    def __init__(
        self, character_name="Male_Human", do_human_ik=True, auto_t_pose=False
    ):
        """Initialize the BaseRig class with character settings.

        Args:
            character_name (str): Name of the character for rigging.
            do_human_ik (bool): Whether to set up HumanIK.
            auto_t_pose (bool): Whether to automatically set T-pose for HumanIK.
        """
        self.character_name = character_name
        self.do_human_ik = do_human_ik
        self.auto_t_pose = auto_t_pose

        # Init
        self.main_set = None

        # Connect purpose
        self.connect_purpose("Base_main_ctrl")

        # Set up geometry display overrides
        self._setup_geometry_display()

        # Set up selection sets
        self._create_selection_sets()

        # Set up display layers
        self._setup_display_layers()

        # Set up delta mush nodes
        self._setup_delta_mush()

        # Set up advanced advanced skeleton face rig
        self._setup_face_rig()

        # Rename SkinCluster
        self._rename_skin_cluster()

        # Set up HumanIK if enabled
        if self.do_human_ik:
            self._setup_human_ik()

    def _setup_geometry_display(self):
        """Set up geometry display overrides.

        This method sets up the override display type of the geometry group
        based on the value of the geometry_display attribute of the main control.
        """
        if pm.objExists("geo"):
            pm.setAttr("geo.overrideEnabled", 1)
            # Connect the geometry_display attribute to the overrideDisplayType
            # attribute of the geometry group if it's not already connected.
            if not pm.isConnected(
                "Base_main_ctrl.geometry_display", "geo.overrideDisplayType"
            ):
                pm.connectAttr(
                    "Base_main_ctrl.geometry_display", "geo.overrideDisplayType", f=True
                )

    def connect_purpose(self, source, destination_list=None):
        """Connect purpose attribute to visibility of destination objects.

        Args:
            source (str): Source object with purpose attribute.
            destination_list (list): List of destination objects for visibility control.
                                  Defaults to ["render", "proxy", "guide"].
        """
        if destination_list is None:
            destination_list = ["render", "proxy", "guide"]

        if not pm.objExists(source):
            pm.warning(f"Source object {source} does not exist.")
            return

        for dest in destination_list:
            if not pm.objExists(dest):
                pm.warning(f"Destination object {dest} does not exist.")
                continue

        setDrivenKey(
            f"{source}.purpose",
            [0, 1, 2],
            f"{destination_list[0]}.visibility",
            [0, 1, 0],
        )
        setDrivenKey(
            f"{source}.purpose",
            [0, 1, 2],
            f"{destination_list[1]}.visibility",
            [1, 0, 0],
        )
        setDrivenKey(
            f"{source}.purpose",
            [0, 1, 2],
            f"{destination_list[2]}.visibility",
            [0, 0, 1],
        )

    def create_display_layer(self, obj_list, layer_name, idx=0):
        """Create a display layer with the given name and objects.

        Args:
            obj_list (list): List of objects to add to the layer.
            layer_name (str): Name of the display layer.
            idx (int): Display layer index.

        Returns:
            PyNode: The created display layer.
        """
        if not obj_list:
            pm.warning("No objects provided for display layer creation.")
            return None

        if "_layer" not in layer_name:
            layer_name = f"{layer_name}_layer"

        # Check if layer already exists
        existing_layer = pm.ls(layer_name, type="displayLayer")
        if existing_layer:
            return existing_layer[0]

        pm.select(obj_list)
        layer = pm.createDisplayLayer(name=layer_name, nr=True, number=idx)

        # Set layer color and visibility based on name
        color_mapping = {
            "skeleton": (25, 1),
            "muscle": (4, 0),
            "organs": (24, 0),
            "lymphatic": (28, 0),
            "ligaments": (30, 0),
            "heart": (12, 0),
            "veins": (8, 0),
            "arteries": (12, 0),
            "nervous_system": (29, 0),
            "hair": (0, 0),
        }

        for key, (color, visibility) in color_mapping.items():
            if key in layer_name.lower():
                pm.setAttr(f"{layer}.color", color)
                pm.setAttr(f"{layer}.visibility", visibility)
                break

        return layer

    def _create_selection_sets(self):
        """Create selection sets for controls and meshes.

        Create selection sets for different component types like controls,
        meshes, joints and skeletal system.
        """
        # Create selection sets for different component types
        root_jnt = "Base_main_FS_jnt"

        joint_list = pm.listRelatives(root_jnt, ad=True, type="joint")
        joint_list.insert(0, pm.ls(root_jnt)[-1])

        # Delete sets if they already exist
        sets_to_delete = pm.ls("*_set")
        for set_name in sets_to_delete:
            if pm.objExists(set_name):
                pm.delete(set_name)

        # Create sets
        # Ctrls
        body_ctrl_set = pm.sets(pm.ls("*_ctrl"), n="body_ctrls_set")
        face_ctrl_set = pm.sets(empty=True, n="face_ctrls_set")
        ctrl_set = pm.sets(pm.ls(body_ctrl_set, face_ctrl_set), n="ctrls_set")

        # Meshes
        render_geo_list = getAllObjectUnderGroup("render")
        proxy_geo_list = getAllObjectUnderGroup("proxy")
        guide_geo_list = getAllObjectUnderGroup("guide")

        render_model_set = pm.sets(render_geo_list, n="render_model_set")
        proxy_model_set = pm.sets(proxy_geo_list, n="proxy_model_set")
        guide_model_set = pm.sets(guide_geo_list, n="guide_model_set")
        model_set = pm.sets(
            [render_model_set, proxy_model_set, guide_model_set], n="model_set"
        )

        # Joints
        body_joint_set = pm.sets(joint_list, n="body_joint_set")
        face_joint_set = pm.sets(empty=True, n="face_joint_set")
        joint_set = pm.sets([body_joint_set, face_joint_set], n="joint_set")

        # Skeletal
        skeletal_set = pm.sets(pm.ls(render_geo_list, joint_list), n="skeletalMesh_set")

        # Main
        self.main_set = self._create_selection_set(
            self.character_name + "_character_set",
            pm.ls(ctrl_set, model_set, joint_set, skeletal_set),
        )

    def _create_selection_set(self, name, members, parent=None):
        """Create a selection set if it doesn't already exist.

        Args:
            name (str): Name of the selection set.
            members (list): List of objects to add to the set.

        Returns:
            PyNode: The created or existing object set.
        """
        if not pm.objExists(name):
            obj_set = pm.sets(name=name, empty=True)
            if members:
                pm.sets(obj_set, add=members)

            if self.main_set and pm.objExists(self.main_set):
                pm.sets(self.main_set, add=obj_set)
            elif parent and pm.objExists(parent):
                pm.sets(parent, add=obj_set)
            else:
                pass

            return obj_set
        return pm.PyNode(name)

    def _setup_display_layers(self):
        """Set up display layers for guide components.

        This function iterates over predefined group names under the 'guide'
        node, checks for their existence, and creates a display layer for
        each existing group using its name.

        Returns:
            None
        """
        if not pm.objExists("guide"):
            return

        # List of guide children group names to process
        guide_children_list = [
            "guide|skeleton_grp",
            "guide|muscle_grp",
            "guide|secondary_muscle_grp",
            "guide|ligaments_grp",
            "guide|heart_grp",
            "guide|organs_grp",
            "guide|arteries_grp",
            "guide|veins_grp",
            "guide|lymphatic_grp",
            "guide|nervous_system_grp",
            "guide|hair_grp",
        ]

        for grp_name in guide_children_list:
            if pm.objExists(grp_name):
                grp = pm.PyNode(grp_name)
                # Extract and format the group name for the display layer
                layer_name = str(grp.name()).split("|")[-1].replace("_grp", "")
                self.create_display_layer(grp, layer_name)

    def _setup_delta_mush(self):
        """Set up delta mush nodes if they exist.

        Connects the Base_main_ctrl scale to the delta mush node's scale
        attribute if it's not already connected.

        Args:
            None

        Returns:
            None

        """
        # Get list of delta mush nodes
        deltamush_node_list = pm.ls(type="deltaMush")

        # Iterate over each delta mush node
        for dm_node in deltamush_node_list:
            dm_node_name = dm_node.name()

            # Check if the scale attribute of the delta mush node is connected
            # to the scale attribute of the Base_main_ctrl
            if not pm.isConnected("Base_main_ctrl.scale", f"{dm_node_name}.scale"):
                # Connect the attributes
                pm.connectAttr("Base_main_ctrl.scale", f"{dm_node_name}.scale", f=True)

    def _setup_face_rig(self):
        """Set up Advanced Skeleton face rig components.

        Connects control objects for eye aim and face joint setup.
        Also establishes scale connections for the main face rig components.
        """
        # Eye aim setup
        if pm.objExists("AimEye_M"):
            # Connect middle eye aim control
            if pm.objExists("M_Eyes_Aim_01_ctrl"):
                pm.parentConstraint("M_Eyes_Aim_01_ctrl", "AimEye_M", mo=True)
            # Connect left eye aim control
            if pm.objExists("L_Eye_eye_aim_at_ctrl"):
                pm.parentConstraint("L_Eye_eye_aim_at_ctrl", "AimEye_L", mo=True)
            # Connect right eye aim control
            if pm.objExists("R_Eye_eye_aim_at_ctrl"):
                pm.parentConstraint("R_Eye_eye_aim_at_ctrl", "AimEye_R", mo=True)

            # Hide specified controls if they exist
            hide_ctrl_list = [
                ctrl for ctrl in ["AimEye_M", "FKHead_M"] if pm.objExists(ctrl)
            ]
            if hide_ctrl_list:
                pm.hide(hide_ctrl_list)

        # Face joint setup
        if pm.objExists("FaceJoint_M") and pm.objExists("M_Head_head_FS_jnt"):
            # Parent face joint under head joint
            pm.parent("FaceJoint_M", "M_Head_head_FS_jnt")

            # Parent constraint face motion targets to the head joint
            for target in [
                "FaceMotionSystem",
                "FaceDeformationFollowHead",
                "LipFollowHead",
            ]:
                if pm.objExists(target):
                    pm.parentConstraint("M_Head_head_FS_jnt", target, mo=True)

            # Set up scale connection if not already connected
            if not pm.isConnected(
                "Base_main_ctrl.worldMatrix", "MainAndHeadScaleMultiplyDivide.input1"
            ):
                decompose_matrix = pm.shadingNode("decomposeMatrix", asUtility=True)
                pm.connectAttr(
                    "Base_main_ctrl.worldMatrix", decompose_matrix.inputMatrix, f=True
                )
                pm.connectAttr(
                    decompose_matrix.outputScale,
                    "MainAndHeadScaleMultiplyDivide.input1",
                    f=True,
                )

    def _setup_human_ik(self):
        """Set up HumanIK for the character.

        This function sets up the character for HumanIK, using the character's
        name as the name of the HumanIK character. It also sets the T-pose of
        the character if enabled.

        Args:
            auto_t_pose (bool): Whether to go to T-pose after initialization.
        """

        # Define the control lists for the arms
        l_arms_ctrl_list = [
            "L_Arm_base_ctrl",
            "L_Arm_fk_root_ctrl",
            "L_Arm_fk_mid_ctrl",
            "L_Arm_fk_tip_ctrl",
        ]
        r_arms_ctrl_list = [
            "R_Arm_base_ctrl",
            "R_Arm_fk_root_ctrl",
            "R_Arm_fk_mid_ctrl",
            "R_Arm_fk_tip_ctrl",
        ]

        # Set T-pose if enabled
        if self.auto_t_pose:
            # Check if all left arm controls exist
            if all(pm.objExists(ctrl) for ctrl in l_arms_ctrl_list):
                joint.setArmParallelToGrid(l_arms_ctrl_list)
            # Check if all right arm controls exist
            if all(pm.objExists(ctrl) for ctrl in r_arms_ctrl_list):
                joint.setArmParallelToGrid(r_arms_ctrl_list)

        # Initialize HumanIK
        human_ik_name = f"{self.character_name}_HIK"
        humanIK.HumanIK(human_ik_name, auto_T_pose=self.auto_t_pose)

    def _rename_skin_cluster(self):
        """Rename skin clusters for each geometry to be more descriptive.

        The new name is based on the name of the geometry with "_skinCluster"
        appended to the end. This is useful for debugging and finding the
        correct skin cluster to use in a script.

        Returns:
            None
        """

        object_skincluster_dict = {}
        skin_cluster_list = pm.ls(type="skinCluster")
        for skin_cluster in skin_cluster_list:
            # Get the geometry that the skin cluster is connected to
            obj_shape = pm.skinCluster(skin_cluster, q=True, geometry=True)
            obj = pm.listRelatives(obj_shape, p=True)[0]
            object_skincluster_dict[obj] = skin_cluster

        for obj, skin_cluster in object_skincluster_dict.items():
            geo_name = str(obj.name()).replace("_geo", "")
            new_name = f"{geo_name}_skinCluster"
            pm.rename(skin_cluster, new_name)


# Example usage:
if __name__ == "__main__":
    # Create an instance of BaseRig with default settings
    rig = BaseRig(character_name="Male_Human", do_human_ik=True, auto_t_pose=False)

"""Base utilities for Arise rig system.

Provides foundational classes and functions for the Arise character
rigging framework.
"""

import pymel.core as pm

from mayaLib.rigLib.utils import human_ik, joint
from mayaLib.rigLib.utils.common import set_driven_key
from mayaLib.rigLib.utils.util import list_objects_under_group


class BaseRig:
    """A base class for rigging operations in Maya.

    This class provides methods for setting up display layers, connecting controls,
    and managing rig components like HumanIK and facial rigs.
    """

    def __init__(self, character_name="Male_Human", do_human_ik=True, auto_t_pose=False):
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
        try:
            self.connect_purpose("Base_main_ctrl")
        except Exception:
            print("No purpose found for the character.")

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
            if not pm.isConnected("Base_main_ctrl.geometry_display", "geo.overrideDisplayType"):
                pm.connectAttr("Base_main_ctrl.geometry_display", "geo.overrideDisplayType", f=True)

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

        set_driven_key(
            f"{source}.purpose",
            [0, 1, 2],
            f"{destination_list[0]}.visibility",
            [0, 1, 0],
        )
        set_driven_key(
            f"{source}.purpose",
            [0, 1, 2],
            f"{destination_list[1]}.visibility",
            [1, 0, 0],
        )
        set_driven_key(
            f"{source}.purpose",
            [0, 1, 2],
            f"{destination_list[2]}.visibility",
            [0, 0, 1],
        )

    def create_display_layer(self, obj_list, layer_name):
        """Create a display layer with the given name and objects.

        Args:
            obj_list (list): List of objects to add to the layer.
            layer_name (str): Name of the display layer.

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
        layer = pm.createDisplayLayer(name=layer_name, nr=True)

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
        render_geo_list = list_objects_under_group("render") if pm.objExists("render") else []
        proxy_geo_list = list_objects_under_group("proxy") if pm.objExists("proxy") else []
        guide_geo_list = list_objects_under_group("guide") if pm.objExists("guide") else []

        model_sets = []
        if render_geo_list:
            render_model_set = pm.sets(render_geo_list, n="render_model_set")
            model_sets.append(render_model_set)
        if proxy_geo_list:
            proxy_model_set = pm.sets(proxy_geo_list, n="proxy_model_set")
            model_sets.append(proxy_model_set)
        if guide_geo_list:
            guide_model_set = pm.sets(guide_geo_list, n="guide_model_set")
            model_sets.append(guide_model_set)

        # Fallback to geometry_grp if render/proxy/guide don't exist
        if not model_sets and pm.objExists("geometry_grp"):
            geometry_geo_list = list_objects_under_group("geometry_grp")
            if geometry_geo_list:
                geometry_model_set = pm.sets(geometry_geo_list, n="geometry_model_set")
                model_sets.append(geometry_model_set)

        model_set = (
            pm.sets(model_sets, n="model_set") if model_sets else pm.sets(empty=True, n="model_set")
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
            parent (str | None): Optional parent set to add this set to.
                If None and main_set exists, uses main_set. Defaults to None.

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

        Parents ``FaceJoint_M`` under the head joint, rebuilds the eye-aim
        follow system (multMatrix + parentConstraint + setRange), connects
        Arise eye-aim controls (L/M/R) via multiplyDivide nodes for
        translation, rotation and scale, and wires the main-ctrl scale
        into the face motion system.

        Prerequisites:
            The scene must contain the Advanced Skeleton face rig hierarchy
            (``FaceJoint_M``, ``AimEye_*``, ``AimEyeFollow_M``, etc.) and
            the Arise eye-aim controls (``L_Eye_eye_aim_at_ctrl``,
            ``M_Eyes_Aim_01_ctrl``, ``R_Eye_eye_aim_at_ctrl``).
        """
        # Advanced Skeleton face connection
        if pm.objExists("FaceJoint_M"):
            pm.parent("FaceJoint_M", "M_Head_head_FS_jnt")
            pm.parent("FaceGroup", "rig_root_grp")

            # delete AimEyeFollowMMStatic_M if exist
            if pm.objExists("AimEyeFollowMMStatic_M"):
                pm.delete("AimEyeFollowMMStatic_M")

            mult_matrix = pm.shadingNode(
                "multMatrix", asUtility=True, name="AimEyeFollowMMStatic_M"
            )
            pm.connectAttr("M_Head_head_FS_jnt.worldMatrix", mult_matrix.matrixIn[1], f=True)
            pm.connectAttr(mult_matrix.matrixSum, "AimEyeFollowBM_M.inputMatrix", f=True)

            # Rebuild eye-aim follow constraint and setRange blend
            if pm.objExists("eyeAimFollowSetRange"):
                pm.delete("eyeAimFollowSetRange")
            if pm.objExists("AimEyeFollow_M_parentConstraint1"):
                pm.delete("AimEyeFollow_M_parentConstraint1")
            pm.parentConstraint("EyeAimStatic", "M_Head_head_FS_jnt", "AimEyeFollow_M", mo=True)
            pm.shadingNode("setRange", asUtility=True, name="eyeAimFollowSetRange")
            pm.connectAttr("AimEye_M.follow", "eyeAimFollowSetRange.value.valueX", f=True)
            pm.connectAttr("AimEye_M.follow", "eyeAimFollowSetRange.value.valueY", f=True)
            pm.connectAttr(
                "eyeAimFollowSetRange.outValue.outValueX",
                "AimEyeFollow_M_parentConstraint1.M_Head_head_FS_jntW1",
                f=True,
            )
            pm.connectAttr(
                "eyeAimFollowSetRange.outValue.outValueY",
                "AimEyeFollow_M_parentConstraint1.EyeAimStaticW0",
                f=True,
            )
            pm.setAttr("eyeAimFollowSetRange.minY", 1)
            pm.setAttr("eyeAimFollowSetRange.maxX", 1)
            pm.setAttr("eyeAimFollowSetRange.oldMaxY", 10)
            pm.setAttr("eyeAimFollowSetRange.oldMaxX", 10)

            pm.connectAttr(
                "M_Head_head_FS_jnt.worldMatrix[0]",
                "EyeAimFollowHeadMM_EyeAimFollowHead.matrixIn[0]",
                f=True,
            )

            pm.connectAttr(
                "M_Head_head_FS_jnt.worldMatrix[0]",
                "FaceMotionSystemMM_FaceMotionSystem.matrixIn[1]",
                f=True,
            )

            pm.connectAttr(
                "M_Head_head_FS_jnt.worldMatrix[0]",
                "LipFollowHeadMM_LipFollowHead.matrixIn[0]",
                f=True,
            )

            pm.connectAttr(
                "M_Head_head_FS_jnt.worldMatrix[0]",
                "FaceDeformationFollowHeadMM_FaceDeformationFollowHead.matrixIn[1]",
                f=True,
            )

            # Connect to Arise Eye Aim Ctrls
            if (
                pm.objExists("R_EyeTranslation")
                and pm.objExists("M_EyeTranslation")
                and pm.objExists("L_EyeTranslation")
                and pm.objExists("R_EyeRotation")
            ):
                pm.delete(
                    "R_EyeTranslation",
                    "M_EyeTranslation",
                    "L_EyeTranslation",
                    "R_EyeRotation",
                )

            multiply_translate_node_r = pm.shadingNode(
                "multiplyDivide", asUtility=True, n="R_EyeTranslation"
            )
            multiply_translate_node_m = pm.shadingNode(
                "multiplyDivide", asUtility=True, n="M_EyeTranslation"
            )
            multiply_translate_node_l = pm.shadingNode(
                "multiplyDivide", asUtility=True, n="L_EyeTranslation"
            )

            aim_eye_offset = pm.ls("AimEyeOffset_M")[-1]
            scale_value = aim_eye_offset.scaleX.get()

            # Translation connections (Arise eye ctrls -> ADV AimEye targets)
            pm.connectAttr(
                "R_Eye_eye_aim_at_ctrl.translate",
                multiply_translate_node_r.input1,
                f=True,
            )
            pm.connectAttr(multiply_translate_node_r.output, "AimEye_R.translate", f=True)
            pm.setAttr(multiply_translate_node_r.input2X, (1 / scale_value) * -1)
            pm.setAttr(multiply_translate_node_r.input2Y, (1 / scale_value))
            pm.setAttr(multiply_translate_node_r.input2Z, (1 / scale_value))

            pm.connectAttr(
                "M_Eyes_Aim_01_ctrl.translate",
                multiply_translate_node_m.input1,
                f=True,
            )
            pm.connectAttr(multiply_translate_node_m.output, "AimEye_M.translate", f=True)
            pm.setAttr(multiply_translate_node_m.input2X, (1 / scale_value))
            pm.setAttr(multiply_translate_node_m.input2Y, (1 / scale_value))
            pm.setAttr(multiply_translate_node_m.input2Z, (1 / scale_value))

            pm.connectAttr(
                "L_Eye_eye_aim_at_ctrl.translate",
                multiply_translate_node_l.input1,
                f=True,
            )
            pm.connectAttr(multiply_translate_node_l.output, "AimEye_L.translate", f=True)
            pm.setAttr(multiply_translate_node_l.input2X, (1 / scale_value))
            pm.setAttr(multiply_translate_node_l.input2Y, (1 / scale_value))
            pm.setAttr(multiply_translate_node_l.input2Z, (1 / scale_value))

            # Rotation connections
            pm.connectAttr("L_Eye_eye_aim_at_ctrl.rotate", "AimEye_L.rotate", f=True)
            pm.connectAttr("M_Eyes_Aim_01_ctrl.rotate", "AimEye_M.rotate", f=True)

            multiply_rotate_node_r = pm.shadingNode(
                "multiplyDivide", asUtility=True, n="R_EyeRotation"
            )
            pm.connectAttr(
                "R_Eye_eye_aim_at_ctrl.rotate",
                multiply_rotate_node_r.input1,
                f=True,
            )
            pm.connectAttr(multiply_rotate_node_r.output, "AimEye_R.rotate", f=True)
            pm.setAttr(multiply_rotate_node_r.input2Z, -1)

            # Scale connections
            pm.connectAttr("L_Eye_eye_aim_at_ctrl.scale", "AimEye_L.scale", f=True)
            pm.connectAttr("M_Eyes_Aim_01_ctrl.scale", "AimEye_M.scale", f=True)
            pm.connectAttr("R_Eye_eye_aim_at_ctrl.scale", "AimEye_R.scale", f=True)

            hide_ctrl_list = pm.ls("AimEye_M")
            pm.hide(hide_ctrl_list)

            # Disconnect and reset scale to 1 first, otherwise the rig collapses
            if pm.isConnected("Base_main_ctrl.scale", "MainAndHeadScaleMultiplyDivide.input1"):
                pm.disconnectAttr("Base_main_ctrl.scale", "MainAndHeadScaleMultiplyDivide.input1")
                pm.setAttr("MainAndHeadScaleMultiplyDivide.input1X", 1)
                pm.setAttr("MainAndHeadScaleMultiplyDivide.input1Y", 1)
                pm.setAttr("MainAndHeadScaleMultiplyDivide.input1Z", 1)

            pm.connectAttr(
                "Base_main_ctrl.scale",
                "MainAndHeadScaleMultiplyDivide.input1",
                f=True,
            )

    def _setup_human_ik(self):
        """Set up HumanIK for the character.

        This function sets up the character for HumanIK, using the character's
        name as the name of the HumanIK character. It also sets the T-pose of
        the character if enabled (via self.auto_t_pose attribute).
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
                joint.set_arm_parallel_to_grid(l_arms_ctrl_list)
            # Check if all right arm controls exist
            if all(pm.objExists(ctrl) for ctrl in r_arms_ctrl_list):
                joint.set_arm_parallel_to_grid(r_arms_ctrl_list)

        # Initialize HumanIK
        human_ik_name = f"{self.character_name}_HIK"
        human_ik.HumanIK(human_ik_name, auto_t_pose=self.auto_t_pose)

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
